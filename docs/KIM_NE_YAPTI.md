# AgentRoute: Kim Ne Yaptı

Bu belge, proposal'daki iş paketi bölüşümüne göre projenin hangi kısmından kimin sorumlu olduğunu gösterir. Her Python modülünün başındaki docstring'de de sorumlu kişi yazar (`Responsible: ...`).

## Özet

| Kişi | Öğrenci no | Sorumlu olduğu kod | Sunumdaki kısmı (~5 dk) |
|---|---|---|---|
| Ömer Faruk Gedikli | 220104004103 | Simülatör, topoloji, mobilite modeli, olay logu, üç baseline (registry, flooding, Chord) | Problem, motivasyon, ilgili çalışmalar, Figure 1 ile genel bakış |
| Bekir Emre Sarıpınar | 220104004039 | Yetenek dataset'i, embedding'ler, τ ayarı, S-FIB, yetenek duyuruları, greedy semantik forwarding | Capability address, S-FIB, duyurular, greedy ve sınırları |
| Bekir Göktepe | 220104004018 | DQN next-hop policy, GNN varyantı, replay buffer, eğitim | DQN, mobilite, değerlendirme (baseline'lar, metrikler, sonuçlar), kapanış |
| Hep birlikte | | Deneyler, grafikler, testler, final rapor, slaytlar | |

## Ömer Faruk Gedikli: simülatör ve baseline'lar

| Dosya | Ne yapıyor |
|---|---|
| `agentroute/sim/topology.py` | Hücresel/edge topoloji: hücre ızgarasında gNB+edge router'lar, Xn linkleri, core router ızgarası, backhaul, cloud düğümü, gecikme ve kayıp değerleri, bozuk linkler. Hücre sayısı agent sayısıyla büyür. |
| `agentroute/sim/mobility.py` | Random-waypoint mobilite (vektörleştirilmiş), en yakın hücre seçimi, histerezisli handover kararı |
| `agentroute/sim/simulator.py` | SimPy simülatörü: router kuyrukları, arka plan trafiği ve hotspot'lar, link gecikme/kaybı, agent'lar, handover (withdraw/announce yayılımı), node failure ve algılama, istek üretimi, sonuç metrikleri. Her rastgelelik türü için ayrı random stream, böylece her yöntem aynı senaryoyu görür. |
| `agentroute/sim/events.py` | JSONL olay logu ve `topology.json` snapshot'ı |
| `agentroute/baselines/registry.py` | Merkezi (DNS benzeri) registry: kayıt, periyodik yenileme, handover güncellemesi, tek kuyruklu sunucu, sorgu → cevap → görev |
| `agentroute/baselines/flooding.py` | TTL-limited flooding, kopya tekrarını önleme, en benzer cevabı seçme |
| `agentroute/baselines/chord.py` | Chord halkası (SHA-1, finger table, O(log N) lookup), exact-match anahtarlar |
| `agentroute/config.py`, `configs/default.yaml` | YAML ayar yükleme, seed |

## Bekir Emre Sarıpınar: adresleme, S-FIB ve greedy forwarding

| Dosya | Ne yapıyor |
|---|---|
| `agentroute/data/capabilities.py` | 50 yetenek sınıfı: sınıf başına 2 yetenek açıklaması, 3 örnek istek (yetenek kartı) ve 10 parafraz intent. Train/test bölmesi (7/3). |
| `agentroute/embeddings.py` | MiniLM encoder, `.npy` cache, yetenek kartından prototip vektör, header sıkıştırma (int8 / binary) |
| `experiments/tune_tau.py` | Kabul eşiği τ'nun F1 ile ayarlanması → `results/tau.json` |
| `agentroute/sfib.py` | S-FIB: komşu başına sayaç tablosu, k-means / mean / exact özet, R-hop sınırlı duyuru, artımlı withdraw/announce, failure sonrası yeniden kurma, kontrol mesajı sayımı |
| `agentroute/forwarding.py` | Simülatörden bağımsız forwarding arayüzü: `Packet`, `NodeView`, kabul kuralı, DQN'in kullandığı 14 komşu özelliği, `GreedyPolicy` |

## Bekir Göktepe: öğrenen next hop

| Dosya | Ne yapıyor |
|---|---|
| `agentroute/dqn/model.py` | Tüm router'ların paylaştığı Q-ağı: her komşuyu ayrı skorlayan MLP |
| `agentroute/dqn/gnn.py` | GNN varyantı: komşu embedding'lerinden bağlam vektörü (yerel yıldız grafiğinde mesaj geçişi) |
| `agentroute/dqn/replay.py` | Değişken komşu sayısını maskeyle tutan replay buffer |
| `agentroute/dqn/policy.py` | DQN next-hop policy: ε-greedy seçim, reward hesabı, geçişlerin learner'a verilmesi |
| `agentroute/dqn/train.py` | Double DQN eğitimi, target network, rastgele eğitim senaryoları, doğrulama ve en iyi modelin seçimi |
| `experiments/run_train.py` | Eğitimi başlatan script → `results/models/*.pt`, `results/raw/train_*.csv` |

## Sionna radyo katmanı (sorumlu: Bekir Emre Sarıpınar)

Bu parça yapay zeka desteğiyle yazıldı. Sorumlu Bekir Emre Sarıpınar: modülün tamamını (tablo üretimi, simülatöre bağlanışı, varsayımlar, sonuçlar) anlatabilmeli. Modül başlıklarında `Responsible: Bekir Emre Sarıpınar` yazıyor.

| Dosya | Ne yapıyor |
|---|---|
| `configs/radio.yaml` | Radyo varsayımları (frekans, güç, MCS, HARQ) tek yerde |
| `experiments/build_radio_lut.py` | Sionna ile TR 38.901 kanalı, EESM ve NR LDPC BLER eğrisinden mesafeye bağlı tablo üretir |
| `results/radio_lut.npz`, `results/radio_lut_plus10db.npz` | Üretilen tablolar (Sionna kurmadan simülasyon çalışsın diye repoda) |
| `agentroute/radio/lut.py` | Tabloyu okuyan küçük sınıf (`RadioLUT`, yalnızca numpy) |
| `agentroute/sim/simulator.py` | `radio(agent)`: `radio.model: constant\|sionna` ayarına göre sabit ya da mesafeye bağlı kayıp ve HARQ gecikmesi |
| `experiments/run_radio.py`, `viz/plot_radio.py` | Radyo deneyleri ve grafikleri |
| `tests/test_radio.py` | Tablo, determinizm ve `constant` modunun eski sonuçlarla birebir aynı olduğu testi |

## Hep birlikte

| Dosya / iş | Ne |
|---|---|
| `tests/test_core.py`, `tests/test_sim.py` | Dataset, S-FIB, forwarding, simülatör, baseline ve DQN testleri |
| `experiments/run_*.py`, `experiments/common.py`, `experiments/run_all.py` | Deney taramaları (yapay zeka desteğiyle, aşağıya bakın) |
| `viz/plots.py` | Rapor ve sunum grafikleri (yapay zeka desteğiyle) |
| `docs/report/FINAL_REPORT.md` | Final rapor |
| `docs/slides/AgentRoute.pptx` | Sunum slaytları |

## Görselleştirme işlerinin dağılımı

CLAUDE.md'de görselleştirme "hep birlikte" olarak geçiyor. Takip ve anlatım kolay olsun diye her parçanın bir sahibi var:

| Parça | Sahibi | Neden |
|---|---|---|
| `viz/animate.py` (iki animasyon videosu) | Ömer | Simülatörün olay logunu en iyi bilen kişi |
| `viz/app_streamlit.py` (interaktif simülatör) | Bekir Emre | S-FIB ve R gibi parametreleri en iyi anlatabilecek kişi |
| `viz/web/` (React + D3 log oynatıcı) | Bekir Göktepe | React bildiği için |

## Yapay zeka desteğiyle yapılanlar

Projenin asıl işi (dataset, embedding'ler, S-FIB, forwarding, DQN/GNN, simülatör ve baseline'lar) yukarıdaki kişilere aittir. Aşağıdaki destekleyici kısımlar bir yapay zeka kodlama aracı (Claude) desteğiyle yazılmıştır:

| Kısım | Dosyalar |
|---|---|
| Deney script'leri ve ek deneyler (yük, S-FIB özeti, header sıkıştırma) | `experiments/common.py`, `experiments/run_scale.py`, `run_mobility.py`, `run_failure.py`, `run_radius.py`, `run_load.py`, `run_ablation.py`, `run_handover_cost.py`, `run_demo.py`, `run_all.py` |
| Grafikler | `viz/plots.py` |
| Animasyonlar | `viz/animate.py` |
| Streamlit uygulaması | `viz/app_streamlit.py` |
| React + D3 log oynatıcı | `viz/web/`, `viz/export_web_data.py` |
| PDF ve slayt üretimi | `docs/build_pdfs.py`, `docs/slides/` |

Final raporun "Use of AI Tools" bölümü aynı listeyi İngilizce verir.

## Sunumdan önce kontrol listesi

Hoca soruyu herhangi birimize sorabilir. Bu yüzden:

- [ ] Herkes kendi modüllerini baştan sona okudu ve bir arkadaşına anlattı.
- [ ] Herkes `docs/NASIL_YAPTIK.md` dosyasının tamamını okudu (diğer iki kişinin kısımları dahil).
- [ ] Herkes `docs/SUNUM_HAZIRLIK.md` dosyasındaki olası soruları en az bir kere sesli cevapladı.
- [ ] Bir prova yapıldı, her kısım 5 dakikanın altında.
