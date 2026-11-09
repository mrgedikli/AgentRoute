# Sunucuda Claude Code'a verilecek prompt: AgentRoute'a Sionna radyo katmanı eklemek

Bu dosya, sunucuda repoyu klonladıktan sonra Claude Code'a yapıştıracağın prompt'tur.
Aşağıdaki `=== PROMPT BAŞLANGICI ===` ile `=== PROMPT SONU ===` arasını olduğu gibi kopyala.

Sunucuya geçmeden önce (bu bilgisayarda):

1. `main` şu an `origin/main`'den bir commit ileride. Sunucu klonu düzeltmeleri görsün diye push etmen gerekir.
   `origin` şu an `https://github.com/mrgedikli/AgentRoute.git`. Bu senin hesabın (BemreSTR) değil, push yetkin var mı kontrol et.
2. Sunucu HuggingFace'e erişemiyorsa MiniLM önbelleğini kopyala (yaklaşık 1,2 MB, internet yerine scp):
   `scp -r results/cache <kullanici>@<sunucu>:<klon-yolu>/results/`
   Önbellek anahtarı metnin hash'i olduğu için sunucuda aynı metinlerle aynı dosya adları çıkar.

---

=== PROMPT BAŞLANGICI ===

Sen bir yazılım mühendisisin ve bir üniversite dönem projesine yeni bir özellik ekleyeceksin. Kullanıcıyla Türkçe konuş. Kod, değişken adları, commit mesajları ve teknik terimler İngilizce olsun. Kısa ve doğrudan yaz, gereksiz özet ve tekrar yapma. Emin olmadığın bir şeyi uydurma, doğrulayamadığını açıkça söyle. Bir şeyin çalıştığını ancak çalıştırıp gördüysen söyle.

# 1. Proje nedir

Proje **AgentRoute**: CSE 476/575 Mobile Communication Networks dersinin dönem projesi. Üç kişilik ekip. Ağ katmanında, paketleri bir host adresine değil bir **yeteneğe (capability)** yönlendiriyor.
- Her ajanın adresi, yetenek cümlelerinin MiniLM (all-MiniLM-L6-v2, 384 boyut) embedding'idir.
- Her router, komşu başına k-means özetli bir **Semantic FIB (S-FIB)** tutar. Tablolar R hop ile sınırlı duyurularla dolar.
- Görev paketi bir intent embedding taşır. Her hop'ta bir sonraki komşuyu paylaşımlı bir Double DQN (ve bir GNN varyantı) seçer.
- Karşılaştırma: merkezi registry, TTL'li flooding, Chord (exact match), greedy semantik forwarding.
- Simülatör Python + SimPy + NetworkX. Kod `agentroute/` altında, deneyler `experiments/`, sonuçlar `results/`, belgeler `docs/`.

Önce şunları oku (kodlamadan önce): `README.md`, `docs/report/FINAL_REPORT.md` (özellikle §4.1 Simulator, §6 Limitations), `docs/NASIL_YAPTIK.md`, `docs/KULLANIM_KILAVUZU.md`, `configs/default.yaml`, `agentroute/sim/simulator.py`, `agentroute/sim/topology.py`, `agentroute/sim/mobility.py`, `agentroute/baselines/*.py`, `tests/*.py`, `experiments/common.py`.

# 2. Neden bu iş

Hoca, dönem projelerinde ücretsiz **NVIDIA Sionna** simülatörünü kullanmayı önerdi. Sionna ile kod/simülasyon geliştirenlere +30 puan vereceğini yazdı. Proje toplamı 100 puan. Ekip, Sionna'yı **küçük ama gerçek** bir şekilde projeye eklemeye karar verdi ve hoca bunun yeterli olacağını söyledi.

Sionna fiziksel katman ve kanal modelleme kütüphanesidir. Ağ katmanı yönlendirmesi içermez. Bu yüzden AgentRoute'un yerine geçmeyecek. Sadece radyo bağlantısını besleyecek.

Şu an simülatör radyoyu **sabit** modelliyor (`configs/default.yaml`: `topology.delay_ms.radio: 5.0`, `topology.loss.radio: 0.002`). Final rapor bunu bir sınırlılık olarak yazıyor ("The radio is modelled by delay and loss only"). Amaç: radyo kaybını ve ek gecikmeyi, UE'nin hizmet veren gNB'ye olan **mesafesine** bağlı, **Sionna ile hesaplanmış** değerlerle değiştirmek. Böylece hücre kenarındaki mobil ajanların bağlantısı gerçekten kötüleşir.

# 3. Değişmez kurallar

Bunlar pazarlık konusu değil.

1. **`main` dalına commit atma.** `feature/sionna-radio` adlı bir dal aç. Küçük, anlamlı commit'ler at. **Push etme**, ben söylemeden. Commit mesajları İngilizce ve açıklayıcı olsun.
2. **Mevcut sonuçlar bozulmayacak.** `results/raw/*.csv`, `results/summary.json`, `results/tables.md`, `results/models/*.pt`, `results/tau.json`, `results/figures/*` dosyalarını **değiştirme, silme, yeniden üretme.** Yeni çıktılar yeni dosya adlarıyla yazılsın (`radio*.csv` gibi).
3. **Varsayılan davranış aynı kalacak.** `configs/default.yaml` içine `radio.model: constant` varsayılanıyla yeni bir bölüm ekle. `constant` modunda simülatör, bugünkü kodla **bire bir aynı** rastgele sayı çekimlerini ve zaman aşımlarını üretmeli. Bunu kanıtla (bkz. §6 adım 3).
4. **Sionna yalnızca tablo üretirken gerekecek.** Simülatör, hesaplanmış bir tabloyu (`results/radio_lut.npz`) okur. Böylece repoyu klonlayan biri Sionna kurmadan her şeyi çalıştırabilir. `requirements.txt`'e Sionna'yı **ekleme**. Ayrı bir `requirements-radio.txt` yaz.
5. **Mevcut kod stilini koru.** Yeni bir kalıp getirmeden önce mevcut kalıbı incele. Gereksiz hata yakalama (`try/except`), kullanılmayan import ve yorum satırı bırakma. Ekibin özel yapılarını "standart" diye değiştirme.
6. **Sır, token, parola içeren dosyalara dokunma.** `.env` ve anahtar dosyalarını okuma.
7. **Büyük deneyleri sormadan başlatma.** `experiments/run_all.py` yaklaşık bir saat sürer ve eğitim içerir. **Çalıştırma.** DQN'i yeniden eğitme (bu iş için gerekmiyor, bkz. §5).
8. **Uydurma.** Sionna'nın API'sini ezbere yazma. Kurduğun sürümün kaynak kodunu ve dokümanını oku, sonra yaz. Aşağıda verdiğim modül adları hafızadan, doğrula.

# 4. Aşama 0: Ortam ve fizibilite (sonra DUR ve bana raporla)

1. Sunucuyu incele ve raporla: işletim sistemi, Python sürümü (Sionna 2.x için resmi dokümana göre **Python 3.11+ ve PyTorch 2.9+** gerekiyor, doğrula), CPU/GPU, boş disk, PyPI ve HuggingFace'e erişim.
2. Repo için sanal ortam kur ve `requirements.txt`'i kur. `python -m pytest -q` çalıştır. **Beklenen: 15 test geçer.** HuggingFace'e erişim yoksa 7 test `OSError` ile başarısız olur, bu kod hatası değil (modeli indirmek ya da `results/cache` kopyalamak gerekir). Sonucu olduğu gibi raporla.
3. **Ayrı bir sanal ortamda** Sionna'yı kur: PHY ve SYS için `sionna-no-rt` paketi. **Sionna RT'yi (Mitsuba/Dr.Jit) kurma**, kapsam dışı. Bir Mac'te yapılan çözümleme `sionna-no-rt 2.2.0` ve `torch 2.15.0` seçti (yaklaşık 197 MB). Sunucuda GPU'lu bir Linux'ta torch CUDA tekerleği çok daha büyük olabilir. **Kurmadan önce `pip install --dry-run` ile ne ineceğini ve boyutunu bana göster.**
4. Kurulumu doğrula: `import sionna.phy`, sürümü yaz. Küçük bir link-seviyesi deneme çalıştır (örneğin 5G NR LDPC kodlu AWGN üzerinden birkaç yüz blok, BLER ölç). Hafızadan olası adlar (**doğrula**): `sionna.phy.fec.ldpc` (LDPC5GEncoder/Decoder), `sionna.phy.mapping`, `sionna.phy.channel` ve `sionna.phy.channel.tr38901` (UMi/UMa/RMa, PanelArray), `sionna.phy.utils`. Sistem seviyesi modülde (`sionna.sys`) SINR'dan BLER veren bir **PHY abstraction** olup olmadığına bak. Varsa BLER eğrisini Monte Carlo olmadan, çok daha hızlı alabiliriz. Hangi yolun mümkün olduğunu raporla.
5. Lisansı ve atıf bilgisini bul (Sionna makalesi: Hoydis ve ark., "Sionna: An Open-Source Library for Next-Generation Physical Layer Research", arXiv:2203.11854, **atıf vermeden önce doğrula**).

**Burada dur.** Şunları içeren kısa bir rapor yaz: ortam bilgisi, testlerin sonucu, Sionna'nın kurulup kurulmadığı, hangi sürüm, hangi yolun (LDPC Monte Carlo mu, SYS PHY abstraction mı) uygulanabilir olduğu, tahmini süre. Ben onaylamadan Aşama 1'e geçme.

# 5. Aşama 1: Radyo tablosu (onaydan sonra)

**Tasarım.** `radio_lut.npz`, UE–gNB mesafesine göre **ilk iletimin blok hata olasılığını (BLER)** tutar. Simülatör bundan HARQ ile deneme sayısını örnekler:
- n. denemede başarı olasılığı `1 - BLER(d)` (denemeler bağımsız kabul edilir, HARQ birleştirme kazancı yok. Bu bir basitleştirmedir, raporda yaz).
- En fazla `max_tx` denemede (öneri: 4) hiç başarı yoksa paket `"link"` nedeniyle düşer.
- Başarılı olursa ek gecikme = `(deneme sayısı - 1) × harq_rtt` olur, taban gecikme mevcut 5 ms'de kalır.

**Zincir:** mesafe → yol kaybı (TR 38.901, UMi street canyon: hücre aralığı 500 m olduğundan uygun) → SNR (Tx gücü, bant genişliği, gürültü katsayısı) → BLER (sabit bir MCS için LDPC + fading).

**Varsayımlar.** Aşağıdaki değerler **önerilerdir**. Hepsini **tek bir yerde** (örneğin `configs/radio.yaml`) tut, kodun içine gömme, ve her birini raporda tablo olarak yaz. Bunları seçmeden önce **bana bir tablo olarak göster ve onay iste**:
- Taşıyıcı frekansı 3,5 GHz, bant genişliği 20 MHz, gNB Tx gücü ~ 40 dBm, UE gürültü katsayısı ~ 9 dB
- gNB yüksekliği 10 m, UE yüksekliği 1,5 m
- Sabit MCS (bir NR MCS tablosu girdisi), paket boyutu mevcut intent başlığına uygun (float32 1536 B, int8 388 B)
- `max_tx = 4`, `harq_rtt` (öneri 4 ms, slot süresi ve 5G NR HARQ zamanlamasıyla gerekçelendir)
- Hızın etkisi (Doppler): 0–30 m/s mobilite deneyi var. **Önce mesafeye bağlı tabloyla başla.** Hız boyutunu yalnızca ucuza eklenebiliyorsa ekle. Eklemezsen bunu açıkça yaz, "hız modellendi" deme.

**Çıktılar (yeni dosyalar):**
- `agentroute/radio/` paketi: tabloyu okuyan küçük bir sınıf (`RadioLUT`: `bler(distance_m)` vb., numpy interpolasyonu). **Sionna'yı import etme.**
- `experiments/build_radio_lut.py` (veya `tools/`): Sionna ile tabloyu üreten betik. Sionna'yı yalnızca burada import et. Tohum sabit olsun, aynı komut aynı tabloyu üretsin.
- `results/radio_lut.npz` (küçük, repoya girecek). Tablonun meta verisine (parametreler, Sionna sürümü, tohum) bir not göm.
- `requirements-radio.txt`
- Tabloyu gösteren bir kontrol grafiği (`results/figures/radio_bler.png`: mesafeye karşı BLER ve kayıp). BLER mesafeyle **azalmamalı**. Azalıyorsa hata var, nedenini bul.

# 6. Aşama 2: Simülatöre bağlama

`radio()` çağrı yerleri (satır numaraları değişmiş olabilir, `grep -n "radio()"` ile bul):
- `agentroute/sim/simulator.py`: `def radio` (yaklaşık 243), `deliver_to` içinde (yaklaşık 317), `semantic_query` başında (yaklaşık 329)
- `agentroute/baselines/flooding.py:21` ve cevap varış gecikmesi (yaklaşık 49'da `delay_ms["radio"]` doğrudan okunuyor)
- `agentroute/baselines/registry.py:89` ve `:111` (iki radyo hop'u: cevap aşağı, görev yukarı)
- `agentroute/baselines/chord.py:118`

**Değişecek şey:** `radio()` hangi ajan ve hangi gNB arasındaki hop olduğunu bilmeli (`agent_xy` ve `cell_xy` mevcut, mesafe hesaplanabilir). Mobil ajanların konumu `mobility()` içinde saniyede bir güncelleniyor. **Bulut ajanlarının** (cloud düğümüne bağlı) radyo hop'u yok, mevcut kod onlara da radyo ücreti yazıyor. `model: sionna` modunda bunu doğru yap, `constant` modunda mevcut davranışı **aynen koru**.

Adımlar:
1. **Önce referans al.** Kodu değiştirmeden, `constant` modunda şu betiği çalıştır ve çıktıyı bir JSON olarak kaydet: `greedy`, `flooding`, `registry`, `chord`, `agentroute` yöntemleri, seed 1 ve 2, `n_agents=100`, `sim.duration_s=8`. (`Simulator(cfg, method, seed=...).run()` özet sözlüğünü kaydet.)
2. Değişikliği yap. Yeni rastgele çekimleri yalnızca `sionna` modunda yap.
3. **Regresyon kanıtı:** aynı betiği tekrar çalıştır ve özet sözlüklerin **bire bir eşit** olduğunu göster (`==`). Eşit değilse ilerleme, nedenini bul.
4. `sionna` modunda çalıştığını göster ve mobil ajan hücre kenarına yaklaşınca kaybın arttığını bir ölçümle doğrula.

**Testler** (`tests/test_radio.py`, mevcut stile uy):
- `RadioLUT`: BLER mesafeyle azalmaz, sınır değerleri (0 m ve çok uzak) tanımlı.
- `constant` modu, referansla bire bir aynı.
- `sionna` modu çalışır ve belirli tohumda deterministik.
- Testler **Sionna'ya bağlı olmamalı**, yalnızca `.npz` dosyasına.
- Tüm test takımı (`python -m pytest -q`) geçmeli (mevcut 15 + yeni).

# 7. Aşama 3: Deneyler (başlamadan önce bana süreyi söyle)

`experiments/common.py` içindeki `sweep()` yardımcısını kullan, yeni bir `experiments/run_radio.py` yaz. Mevcut `run_*.py` dosyalarının biçimini koru. Çıktılar `results/raw/radio.csv` gibi **yeni** dosyalara yazılsın. 5 seed kullan (mevcut deneylerle aynı).

1. **Sabit radyo ile Sionna radyosu karşılaştırması**: varsayılan senaryo (1000 ajan), tüm yöntemler. Metrikler: başarı, tamamlanma süresi, hop sayısı, düşme nedenleri.
2. **Mobilite taraması** (hız 0, 2, 5, 10, 20, 30 m/s) Sionna radyosuyla.
3. Mümkünse **ölçek** deneyinin küçük bir alt kümesi (100, 1000, 10000).

**DQN'i yeniden eğitme.** Gerekmediğini düşünüyorum, çünkü radyo yalnızca ilk ve son hop'ta kullanılıyor ve DQN'in girdisindeki `link_quality` yalnızca router–router linklerini kapsıyor. Bu varsayımı doğrula (özellikleri `agentroute/forwarding.py` içinde `neighbor_features` ile kontrol et) ve mevcut modeli (`results/models/dqn.pt`) olduğu gibi kullan.

**Dürüst beklenti:** Sionna radyosu büyük ihtimalle tüm yöntemlerin başarısını **benzer oranda** düşürür ve yöntem sıralaması pek değişmez. Sonucu **olduğu gibi** raporla. Ters bir hikaye çıkarmak için parametreleri ayarlama. İlginç bir bulgu çıkarsa (örneğin yüksek hızda belirgin bir fark) onu da olduğu gibi yaz.

`viz/plots.py` bütün şekilleri ve `results/tables.md` ile `summary.json` dosyalarını yeniden üretiyor. **Bunu çalıştırma**, çünkü mevcut sonuç dosyalarının üzerine yazar. Yeni deneyin grafiklerini ayrı bir betikle (`viz/plot_radio.py`) yaz.

# 8. Aşama 4: Belgeler

- `docs/report/FINAL_REPORT.md` (İngilizce): yeni bir bölüm (radyo modeli: zincir, parametre tablosu, basitleştirmeler, sonuçlar), §6 Limitations güncellemesi, §9 "Use of AI Tools" bölümüne bu işin eklenmesi (yapay zeka desteğiyle yazılan dosyaların başlığına da "Written with AI assistance" notu), Sionna atfı ve referans listesi. Mevcut bölüm numaralarını ve biçimi koru.
- `docs/KIM_NE_YAPTI.md`: yeni modülün **sorumlusunu bana sor**, tahmin etme. `Responsible:` satırını buna göre yaz.
- `README.md`: radyo tablosunu nasıl yeniden üreteceğini ve `radio.model` ayarını anlatan kısa bir not.
- `docs/KULLANIM_KILAVUZU.md`: yeni ayar ve betikler (Türkçe, mevcut stile uy).
- PDF'leri `docs/build_pdfs.py` ile yeniden üretmek Chrome gerektirir. Sunucuda Chrome yoksa **atla ve söyle**.
- Sunum slaytlarına dokunma (`docs/slides/`). Sunum 11 Kasım'da, bu iş ondan sonra.

# 9. Rapor biçimi

Her aşamanın sonunda şunu ver:
- **Yapılanlar** (dosya adlarıyla), **çalıştırılan komutlar ve gerçek çıktıları** (test sonuçları, regresyon karşılaştırması).
- **Doğrulananlar ve doğrulanamayanlar.** Sionna API'sinden emin olmadığın yerleri açıkça işaretle.
- **Sorular ve kararlar** (parametre tablosu, sorumlu kişi vb.).
- `git status` ve `git log --oneline` çıktısı.

# 10. Bitti sayılması için

- `python -m pytest -q` tamamen geçiyor (yeni testler dahil).
- `constant` modunun mevcut çıktılarla bire bir aynı olduğu kanıtlandı.
- `results/radio_lut.npz` repoda ve Sionna kurmadan simülasyon çalışıyor.
- Sabit ve Sionna radyosunun karşılaştırması olduğu gibi raporlandı (varsayımlar dahil).
- Rapor ve belgeler güncel, mevcut sonuç dosyalarına dokunulmadı (`git diff --stat -- results/raw results/summary.json results/tables.md results/figures` boş olmalı, yeni dosyalar hariç).
- Her şey `feature/sionna-radio` dalında, `main` değişmedi, push yapılmadı.

Şimdi **Aşama 0**'dan başla ve orada dur.

=== PROMPT SONU ===
