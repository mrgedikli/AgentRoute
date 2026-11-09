# AgentRoute

**Paketleri bir host adresine değil bir yeteneğe (capability) yönlendiriyoruz. Router'lar bir sonraki hop'u deep reinforcement learning ile öğreniyor.**

CSE 476/575 Mobile Communication Networks dönem projesi.
Ekip: Ömer Faruk Gedikli, Bekir Emre Sarıpınar, Bekir Göktepe.

Bu **v2** sürümüdür. İlk sürüm git'te `v1` etiketiyle duruyor. v2'de neyin neden değiştiği: [docs/NASIL_YAPTIK.md](docs/NASIL_YAPTIK.md), bölüm 7.

- **Capability address:** her agent'ın kendi yetenek vektörü vardır (MiniLM, 384 boyut, kendi cümle karışımı).
- **Semantic FIB (S-FIB):** router'lar birbirine sadece özet gönderir (distance-vector). Yakındaki agent'lar kendi satırını tutar, uzaktakiler k = 8 temsilciye sıkıştırılır. Duyurular R hop ile sınırlı.
- **Intent-based forwarding:** görev paketi bir intent embedding taşır. Router, daha iyi bir aday bilmiyorsa işi yerel agent'a verir, biliyorsa en iyi eşleşen komşuya iletir.
- **Learned next hop:** tüm router'ların paylaştığı bir Double DQN (ve bir GNN varyantı) "burada teslim et" ya da "şu komşuya ilet" kararını verir.
- **Mobilite:** handover'da eski ve yeni hücre R hop içinde güncelleme gönderir, ve bir router güncellemeyi sadece özeti gerçekten değiştiyse iletir.
- **Karşılaştırma:** greedy, yük duyarlı greedy, SPFR tarzı kural, TTL-limited flooding, tek sunuculu ve üç replikalı registry, semantik DHT ve Chord (exact match).

## Hızlı başlangıç

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
```

```bash
source .venv/bin/activate && python -m pytest -q
```

> **İlk çalıştırma internet ister.** MiniLM modeli (`all-MiniLM-L6-v2`, yaklaşık 90 MB) ilk seferde HuggingFace'ten indirilir ve embedding'ler `results/cache/` altına kaydedilir (`.gitignore`'da). Test ve simülasyon, model indirilene kadar çalışmaz; bu yüzden 7 test internetsiz ortamda başarısız olur. Sonraki çalıştırmalar önbellekten okur.

```bash
python experiments/run_all.py --quick
```

```bash
streamlit run viz/app_streamlit.py
```

## Sionna radyo modeli

Radyo bağlantısı iki modda çalışır (`configs/default.yaml` içinde `radio.model`): `constant` (sabit 5 ms ve %0,2 kayıp, varsayılan, eski sonuçlarla birebir aynı) ve `sionna` (UE-gNB mesafesine bağlı kayıp ve HARQ gecikmesi). Tablolar repoda (`results/radio_lut*.npz`), simülasyon için Sionna gerekmez. Tabloyu yeniden üretmek için ayrı bir ortamda:

```bash
pip install -r requirements-radio.txt && python experiments/build_radio_lut.py
```

```bash
python experiments/run_radio.py compare && python experiments/run_radio.py mobility && python viz/plot_radio.py
```

## Belgeler

| Belge | İçerik |
|---|---|
| [docs/KULLANIM_KILAVUZU.md](docs/KULLANIM_KILAVUZU.md) | Kurulum, her script, animasyon, Streamlit, React oynatıcı, ayarlar, log formatı |
| [docs/KIM_NE_YAPTI.md](docs/KIM_NE_YAPTI.md) | Ekipte kim hangi kısımdan sorumluydu |
| [docs/NASIL_YAPTIK.md](docs/NASIL_YAPTIK.md) | Her parçanın nasıl tasarlanıp yapıldığı |
| [docs/report/FINAL_REPORT.md](docs/report/FINAL_REPORT.md) | Final rapor (İngilizce) |
| [docs/SUNUM_HAZIRLIK.md](docs/SUNUM_HAZIRLIK.md) | Sunum akışı ve olası sorular |
| `docs/pdf/` | Belgelerin PDF sürümleri |
| `docs/slides/AgentRoute.pptx` | Sunum slaytları |

## Klasörler

```
agentroute/   çekirdek kod        experiments/  deney script'leri
configs/      YAML ayarları       viz/          grafikler, animasyon, Streamlit, React oynatıcı
results/      sonuçlar            docs/         belgeler        tests/  testler
```
