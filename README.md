# AgentRoute

**Paketleri bir host adresine değil bir yeteneğe (capability) yönlendiriyoruz. Router'lar bir sonraki hop'u deep reinforcement learning ile öğreniyor.**

CSE 476/575 Mobile Communication Networks dönem projesi.
Ekip: Ömer Faruk Gedikli, Bekir Emre Sarıpınar, Bekir Göktepe.

- **Capability address:** agent'ın yetenek kartı MiniLM ile 384 boyutlu bir vektöre çevrilir.
- **Semantic FIB (S-FIB):** her router, komşu başına o komşunun arkasındaki yeteneklerin k-means özetini tutar. Tablolar R hop ile sınırlı duyurularla dolar.
- **Intent-based forwarding:** görev paketi bir intent embedding taşır ve en iyi eşleşen komşuya iletilir.
- **Learned next hop:** tüm router'ların paylaştığı bir Double DQN (ve bir GNN varyantı) komşuları benzerlik, kuyruk, link kalitesi ve handover bilgisine göre puanlar.
- **Mobilite:** handover'da sadece eski ve yeni hücrenin R-hop çevresi güncellenir.
- **Karşılaştırma:** merkezi registry, TTL-limited flooding, Chord (exact match) ve greedy semantic forwarding ile.

## Hızlı başlangıç

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
```

```bash
source .venv/bin/activate && python -m pytest -q
```

```bash
python experiments/run_all.py --quick
```

```bash
streamlit run viz/app_streamlit.py
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
