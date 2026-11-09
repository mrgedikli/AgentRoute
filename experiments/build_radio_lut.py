"""Build results/radio_lut.npz: first-transmission BLER of the radio hop versus UE-gNB distance.

Chain (all from Sionna): TR 38.901 UMi channel (path loss, LoS probability,
shadow fading, small-scale fading) -> per-subcarrier SINR -> EESM effective
SINR -> calibrated 5G NR LDPC BLER curve (sionna.sys.PHYAbstraction).

Run in an environment with Sionna (requirements-radio.txt). The simulator
itself only reads the .npz and does not need Sionna.

Written with AI assistance (Claude).
Responsible: Bekir Emre Sarıpınar
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import yaml
import sionna
from sionna.phy.channel import cir_to_ofdm_channel, subcarrier_frequencies
from sionna.phy.channel.tr38901 import PanelArray, UMi
from sionna.sys import EESM, PHYAbstraction

ROOT = Path(__file__).resolve().parents[1]


def build(cfg: dict) -> dict:
    torch.manual_seed(cfg["seed"])
    sionna.phy.config.seed = cfg["seed"]  # Sionna draws from its own random generator
    fc = cfg["carrier_frequency_hz"]
    n_sc = cfg["num_subcarriers"]
    n_ut = cfg["drops_per_distance"]
    bs_array = PanelArray(num_rows_per_panel=1, num_cols_per_panel=1, polarization="dual",
                          polarization_type="cross", antenna_pattern="38.901", carrier_frequency=fc)
    ut_array = PanelArray(num_rows_per_panel=1, num_cols_per_panel=1, polarization="single",
                          polarization_type="V", antenna_pattern="omni", carrier_frequency=fc)
    channel = UMi(carrier_frequency=fc, o2i_model="low", ut_array=ut_array, bs_array=bs_array,
                  direction="downlink", enable_pathloss=True, enable_shadow_fading=True)
    phy = PHYAbstraction(sinr_effective_fun=EESM())
    freqs = subcarrier_frequencies(n_sc, cfg["subcarrier_spacing_hz"])
    # Power per resource element and thermal noise per resource element (linear, mW).
    tx_re_mw = 10 ** (cfg["tx_power_dbm"] / 10) / n_sc  # UE transmit power per resource element
    noise_mw = 10 ** ((-174 + 10 * np.log10(cfg["subcarrier_spacing_hz"]) + cfg["noise_figure_db"]) / 10)

    max_tx = cfg["max_tx"]
    bler, snr_db, pmf = [], [], []
    for d in cfg["distance_grid_m"]:
        # n_ut independent drops (batch entries), one UE each, at ground distance d inside the
        # serving 120-degree sector of a three-sector gNB (the 38.901 antenna pattern points its
        # boresight along +x). Separate batch entries keep shadow fading statistically independent;
        # UEs in one batch entry would share spatially correlated shadowing.
        ang = (torch.rand(n_ut, 1) - 0.5) * (2 * np.pi / 3)
        ut_loc = torch.stack([d * torch.cos(ang), d * torch.sin(ang),
                              torch.full((n_ut, 1), cfg["ut_height_m"])], dim=-1)
        bs_loc = torch.tensor([0.0, 0.0, cfg["bs_height_m"]]).repeat(n_ut, 1, 1)
        zeros = torch.zeros(n_ut, 1, 3)
        channel.set_topology(ut_loc, bs_loc, zeros, torch.zeros(n_ut, 1, 3), zeros,
                             torch.zeros(n_ut, 1, dtype=torch.bool), los="random")
        a, tau = channel(1, 1e6)
        h = cir_to_ofdm_channel(freqs, a, tau)  # [drop, 1, ut_ant, 1, bs_ant, 1, n_sc]
        gain = (h.abs() ** 2).sum(dim=(2, 4)).mean(dim=3)[:, 0, 0, :]  # [drop, n_sc], power summed over the 2 gNB ports
        sinr = tx_re_mw * gain * 10 ** (cfg["extra_gain_db"] / 10) / noise_mw  # uplink, maximum-ratio combining over the gNB ports
        sinr_ut = sinr.T.reshape(1, n_sc, n_ut, 1)  # [sym, sc, ut, stream]
        mcs = torch.full((n_ut,), cfg["mcs_index"], dtype=torch.int32)
        out = phy(mcs, sinr=sinr_ut, mcs_table_index=cfg["mcs_table_index"],
                  mcs_category=cfg["mcs_category"])
        # Per-UE first-transmission BLER. A UE keeps its LoS state and shadowing across HARQ
        # attempts, so attempts are independent only given the UE (not across UEs).
        p = out[3].clamp(max=1.0).double()
        # P(delivered at attempt k) = mean_ue p^(k-1) (1-p); last column = dropped after max_tx attempts.
        ok = torch.stack([(p ** (k - 1) * (1 - p)).mean() for k in range(1, max_tx + 1)])
        pmf.append(torch.cat([ok, (p ** max_tx).mean().reshape(1)]).numpy())
        bler.append(float(p.mean()))
        snr_db.append(float(10 * torch.log10(sinr.mean(dim=1)).mean()))
    pmf = np.array(pmf)
    # Sampling noise can make the curve wiggle; a farther UE is never better, so enforce that.
    drop = np.maximum.accumulate(pmf[:, -1])
    ok = pmf[:, :-1]
    ok = ok * ((1 - drop) / np.maximum(ok.sum(axis=1), 1e-12))[:, None]
    pmf = np.concatenate([ok, drop[:, None]], axis=1)
    return {"distance_m": np.array(cfg["distance_grid_m"], float), "bler": np.maximum.accumulate(bler),
            "snr_db": np.array(snr_db), "attempt_pmf": pmf}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "radio.yaml"))
    ap.add_argument("--out", default=str(ROOT / "results" / "radio_lut.npz"))
    ap.add_argument("--extra-gain-db", type=float, default=None, help="override extra_gain_db (sensitivity runs)")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    if args.extra_gain_db is not None:
        cfg["extra_gain_db"] = args.extra_gain_db
    res = build(cfg)
    meta = {"config": cfg, "sionna": __import__("importlib.metadata").metadata.version("sionna-no-rt"),
            "torch": torch.__version__}
    np.savez(args.out, **res, harq_rtt_ms=cfg["harq_rtt_ms"], meta=json.dumps(meta))
    for d, b, s, q in zip(res["distance_m"], res["bler"], res["snr_db"], res["attempt_pmf"]):
        print(f"{d:6.0f} m  snr {s:6.1f} dB  first-tx bler {b:.4f}  drop after {cfg['max_tx']} tx {q[-1]:.4f}")


if __name__ == "__main__":
    main()
