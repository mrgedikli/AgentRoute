# AgentRoute — Sunum Hazırlığı (11 Kasım 2026)

Toplam ~15 dakika, kişi başı en fazla 5 dakika. Slaytlar İngilizce, konuşma ve konuşmacı notları Türkçe. Canlı demo yok, kaydedilmiş animasyon videosu kullanılacak.

**Tek cümle:** "Paketleri bir adrese değil bir yeteneğe yönlendiriyoruz ve router'ların bu kararı öğrenmesinin işe yarayıp yaramadığını ölçüyoruz."

**Slaytlar:** `docs/slides/AgentRoute.pptx` (PDF gerekirse PowerPoint'ten Dosya → Dışa Aktar ile alın). Her slaytın konuşmacı notlarında söylenecekler ve gerçek rakamlar var. Rakamlar `results/summary.json` dosyasından otomatik geliyor.

| Slaytlar | Konuşmacı | İçerik |
|---|---|---|
| 1–5 | Ömer | Başlık, "nerede" vs "kim yapabilir", iki klasik çözüm ve mobilite, ilgili çalışmalar, tek resimde AgentRoute |
| 6–10 | Bekir Emre | Capability address, S-FIB, duyuru yarıçapı R, mobilite ve handover maliyeti, sorun çoğunlukla eşleşmede (kapanış sorusu) |
| 11–19 | Bekir Göktepe | DQN, doğrulama eğrisi, deney düzeni, ölçek, istek hızı, dayanıklılık, iki video, takeaways |
| 20 | (yedek) | S-FIB içeriği ve header boyutu, soru gelirse |

**Önemli:** Çekirdek modüllerin v2 hali yapay zeka aracıyla yazıldı (`docs/KIM_NE_YAPTI.md`). Herkes kendi modülünün v2 halini okuyup anlatabilmeli. Hoca sorarsa bunu saklamayın, ama kodu da açıklayabilin.

---

## 1. Ömer (~5 dk): Sorun ve büyük resim

- Bugünkü internet **"nerede?"** sorusuna göre çalışıyor: IP adresi + DNS ile zaten bilinen isimler. Posta benzetmesi: postacı kime gittiğini bilmez, adrese götürür.
- AI agent'lar **"bu işi kim yapabilir?"** diye soruyor, kim olduğunu ve nerede olduğunu bilmeden, makine hızında, büyük ve sürekli değişen bir kalabalıkta.
- Bugünkü iki seçenek (1.000 agent, 10 istek/s):
  - Merkezi kayıt (DNS benzeri): 60 ms, tek sunucu. Trafiği çok az, ama sunucu ölürse keşif biter. **Replika bunu büyük ölçüde çözer**, bunu saklamayın.
  - Flooding: durum tutmuyor, ama istek başına 174 kB trafik ve cevap bekleme penceresi kadar gecikme.
- Üstüne mobilite: agent'ların çoğu telefonda, arabada, dronda; bağlı oldukları baz istasyonu sürekli değişiyor.
- Literatür: agent'a özel katmanlar HTTP'nin üstünde [1], discovery servisleri [3], [4]. SPFR [2] ve bir IETF taslağı [14] da yönlendirmeyi semantik yapıyor. **Bizim sorumuz: kuralı öğrenmek, sıkıştırılmış tabloda ve mobil ağda işe yarıyor mu?**
- INS (1999), Siena (2001), pSearch (2003): fikir yeni değil. Bunu kendiniz söyleyin.
- Figure 1 ile genel bakış, ayrıntıya girmeden: duyurular tabloları dolduruyor, görev paketi hop hop yetenekli agent'a gidiyor.

## 2. Bekir Emre (~5 dk): Adresleme, semantik tablo ve mobilite

- **Capability address:** her agent'ın kendi vektörü var. Sınıfın 5 cümlesinin MiniLM vektörlerinin rastgele ağırlıklı karışımı. Aynı işi yapan iki sağlayıcı yakın ama aynı değil.
- **Örnek çift:** "find the cars in this photo" ↔ "object detection in images" (cos 0.517).
- **τ = 0.355:** Doğru kabul +1, yanlış kabul −1, kabul etmeme 0 olacak şekilde seçildi. Yanlış teslim ile kaçırılan istek arasında bir takas. Eşiği 0.5'e çıkarmak 21 puan başarı kaybettiriyor.
- **S-FIB:** normal router "şu IP aralığı için şu kapıdan çık" der. Bizim router "bu komşumun tarafında şu tür yetenekler var" der. AVM benzetmesi: koridor başındaki tabela.
- **İki katman:** bir hop ötedeki agent'lar için tek tek satır, daha uzak için k = 8 temsilci vektör. Mesaj boyutu agent sayısıyla büyümez.
- **Duyuru yarıçapı:** R = 2 yeterli. R arttıkça kontrol trafiği neredeyse sabit (485 → 506 kB/s), çünkü her hop yeniden özetliyor.
- **Encoder:** altı encoder denedik, test doğruluğu 0.73–0.77. n = 150 ile aralarındaki fark gürültü. Encoder değiştirmek çare değil.
- **Mobilite:** eski hücre withdraw, yeni hücre announce, yalnızca R hop içinde. Handover başına 20 mesaj, ağ büyüse de sabit.
- Bitiriş sorusu (sözü Bekir Göktepe'ye bağlar): **"En benzer komşu tıkalıysa ya da bir hop ötede daha iyisi varsa, burada teslim mi edelim, yoksa devam mı?"**

## 3. Bekir Göktepe (~5 dk): Öğrenen karar ve değerlendirme

- **DQN:**
  - Aksiyonlar: komşular + "burada teslim et".
  - Durum (her aksiyon için 15 özellik): benzerlik, kuyruk, link kalitesi, handover bayrağı, TTL, tür.
  - Ödül: −gecikme, teslimde +1, düşerse −1. Aynı ödülü greedy için de ölçüyoruz.
  - Tüm router'lar tek ağı paylaşıyor, her aksiyonu ayrı skorluyor.
- **Sonuçlar (10 seed, görülmemiş parafrazlar, 1.000 agent):**
  - Eşleşme tavanı %69.3. Bu bir üst sınır değil, referans çizgisi.
  - DQN %62.9. Aynı tabloda greedy %60.4, yük duyarlı greedy %59.4.
  - **DQN − greedy = +2.5 puan (GA 1.4–3.7), DQN − yük duyarlı = +3.5 puan (GA 2.6–4.4).**
  - SPFR tarzı kural %64.1 ama tam tablo ile, kontrol trafiği 3.6 kat. DQN − SPFR tarzı = −1.2 puan (GA −2.2 ile −0.2). Aynı tam tabloda DQN, SPFR tarzından 2.2 puan iyi.
  - Flooding %65.4 ama 234 ms ve istek başına 174 kB.
  - Registry %63.0, kontrol trafiği 11 kat az, 60 ms.
  - Gecikme: eşleştirilmiş isteklerde greedy'ye karşı yalnızca 0.2–0.5 ms kazanç. **Eski "daha hızlı" iddiasını artık yapmayın.**
- **Üç dürüst cümle (kendiniz söyleyin):**
  1. Registry bayt olarak her zaman daha ucuz.
  2. Mobilite başarıyı değil maliyeti etkiliyor, hiçbir yöntemin başarısı hızla değişmiyor.
  3. Asıl tavan yönlendirme değil eşleşme.
- İki video: `agentroute_demo.mp4` (duyuru → istek → handover) ve `greedy_vs_agentroute.mp4` (**seçilmiş** tek istek, ortalama değil. Bunu videoda da yazıyor, sözlü de söyleyin.)
- Kapanış: tek cümle + gelecek iş.

---

## Hocanın sorabileceği zor sorular

Üçünüz de bunların hepsine 2–3 cümleyle cevap verebilmelisiniz.

**1. Registry aynı başarıyı 11 kat daha az trafikle veriyorsa bu protokole neden ihtiyaç var?**
Haklı bir soru, verimiz de bunu söylüyor. 1.000 agent'ta registry başarıda DQN'le aynı (fark −0.1, GA −1.1 ile 1.0) ve bayt olarak her istek hızında daha ucuz. Bizim tarafta üç şey var: gecikme (21 ms'ye karşı 60 ms), 10.000 agent'ta başarı (+4.2 puan, çünkü sunucuya gidiş-dönüş 12 hop ve isteklerin %12'si yolda kayboluyor) ve işletilecek bir sunucu olmaması. Trafik her şeyden önemliyse registry seçilmeli.

**2. Tek hata noktası diyorsunuz ama üç replika bunu çözmüyor mu?**
Büyük ölçüde çözüyor: %20 router çökmesinde 3 replikayla %60.0, tek sunucuda sunucu ayaktaysa %60.7, çöktüyse %18. Replika kontrol trafiğini 1.000 agent'ta %21, 10.000 agent'ta %40 artırıyor. Bu yüzden tek sunucu kıyaslamasını koşullu raporladık ve 3 replikayı ayrı baseline yaptık.

**3. DQN'in katkısı gerçekten öğrenmeden mi, yoksa ek bilgiden mi?**
Aynı tabloyu kullanan iki sezgisel kurala karşı ölçtük, ek kontrol trafiği yok. Aynı istek dizisi ve aynı seed'lerle eşleştirilmiş farklar: +2.5 ve +3.5 puan. Greedy'ye göre kazancın kaynağı: kuyruk taşmaları 2.3 puan, yanlış teslim 1.6 puan azalıyor, TTL bitmesi 1.5 puan artıyor.

**4. 2.5 puan için derin öğrenme değer mi?**
Küçük ama güven aralığı sıfırı dışlıyor, üç senaryoda da tekrarlanıyor. Ama şunu da söyleyin: tam tablonun getirdiği kazanç öğrenmeninkinden büyük. Doğru okuma: öğrenilen politika, sıkıştırılmış tabloda tam tablolu kuralın 1–2 puan yakınına, onun kontrol trafiğinin dörtte birine geliyor.

**5. SPFR'yi kendiniz yazdınız, adil mi?**
Yeniden uyarlama, orijinal kod değil ve bunu raporda yazdık. Yük ve fiyat terimleri simülatörümüzde olmadığı için fayda = benzerlik. Parametre ω = 0.08 SPFR'nin değeri, ufuk R = 2. Yani "SPFR'yi yendik" demiyoruz, zaten yenmiyoruz.

**6. Başarı neden %63? Eşleşme tavanı nasıl %69?**
Tavan: ağdaki en benzer agent doğru sınıftan ve τ'yu geçiyorsa başarılı. İsteklerin ~%14–16'sında τ'yu geçen kimse yok, ~%15'inde en iyi eşleşme yanlış sınıftan. Bu encoder + veri + τ'nun sınırı. Yönlendirme en fazla kalan 6 puanı kapatabilir.

**7. Flooding için 200 ms pencere seçmişsiniz, kasıtlı yavaşlatma değil mi?**
Pencereyi 20 ms ile 1 s arasında taradık: 50 ms'de %63.4 ve 79 ms, 100 ms'de %65.8 ve 134 ms. 20 ms'de %35.9'a düşüyor. "Flooding 10 kat yavaş" demeyin, "en iyisine yaklaşmak için en az ~80 ms gerekiyor" deyin.

**8. Chord %0, kasıtlı zayıf baseline değil mi?**
%0 tanım gereği: parafraz başka anahtara hash'leniyor. Bu yüzden Chord'u rakip saymıyoruz, sadece referans. Semantik DHT ayrı bir baseline, bu da %56'da kalıyor.

**9. Mobil ağ diyorsunuz ama mobilite sonucu etkilemiyor.**
Doğru, başarı 0–30 m/s arasında düz, 150 m hücrelerde bile. Modelimizde handover 50 ms kesinti, güncellemeler milisaniyeler içinde yayılıyor. Etki maliyette: 150 m hücrede 30 m/s'de kontrol trafiği 445'ten 1.336 kB/s'ye çıkıyor. Keşfi zorlayan bir mobilite modeli için görev süresi boyunca handover ve handover hataları eklenmeli, gelecek iş.

**10. Periyodik yenileme bu kadar pahalıysa neden var?**
Handover kontrol trafiğinin küçük kısmı (10.000 agent'ta 423 kB/s), yenileme 2.866 kB/s. Soft state basitlik veriyor ve hataları kendiliğinden düzeltiyor. Yalnızca değişen satırları göndermeyi (artımlı yenileme) ayrıca denedik: 1.000 agent'ta sürekli kontrol trafiği 380'den 64 kB/s'ye iniyor, DQN'in başarısı %62.9'da kalıyor. 10.000 agent'ta (5 seed) trafik 3.453'ten 549 kB/s'ye iniyor, başarı değişmiyor (%66.7 ve %67.0). Bu ayrı bir deney (`experiments/run_refresh.py`), rapordaki ve slaytlardaki bütün sayılar tam yenilemeyle. Yenileme süresini uzatmayı denemedik.

**11. R = 1'de DQN neden 54 ms oluyor?**
Eğitim R = 2–4 arasındaydı, R = 1'de tablo görmediği bir biçimde ve hop sayısı 6.4'e çıkıyor. GNN 21 ms'de kalıyor. Dürüst sonuç: politika eğitim aralığı dışına otomatik taşınmıyor. Ortalama vektörlü tabloda da DQN greedy'nin altında (%44.6'ya karşı %51.0), aynı neden.

**12. Bu gerçekten ağ katmanı mı?**
Tasarım ağ katmanında: adresleme, yönlendirme tablosu, hop hop iletme. Gerçek dünyada ilk aşamada IP üzerinde overlay olarak kurulabilir, IPv6'nın başta IPv4 üzerinden tünellenmesi gibi. Bugün çalışan bir yığın göstermiyoruz, simülasyon sonucu gösteriyoruz.

**13. Veri setini kendiniz yazmışsınız, test seti 150 istek. Sonuçlara güvenilir mi?**
Sınırlılık olarak raporda var. Encoder karşılaştırmasında aynı nedenle 7 puandan küçük farkı gürültü sayıyoruz. Yöntem karşılaştırmaları istek düzeyinde eşleştirilmiş olduğundan daha duyarlı, ama hepsi aynı 150 cümleye bağlı.

**14. Bu kodu siz mi yazdınız?**
v1'in çekirdeğini ekip yazdı. v2 revizyonunu, eleştirel bir değerlendirmeden sonra yapay zeka aracıyla yaptık ve raporun 9. bölümünde dosya dosya yazıyor. Ne yaptığını anlatabiliriz (bunun için gerçekten okuyun).

**15. Sionna'yı nasıl kullandınız? Simülatör Sionna mı?**
Hayır, simülatör SimPy ile yazılı kaldı. Sionna yalnızca radyo hop'unu hesaplıyor: 3GPP TR 38.901 kanalı, 5G NR blok hata oranı ve HARQ ile "UE–gNB mesafesi → kayıp olasılığı ve tekrar gönderim gecikmesi" tablosu üretiyor (`results/radio_lut.npz`). Simülatör bu tabloyu okuyor (`radio.model: sionna`). Varsayılan ayar sabit radyo olduğu için diğer tüm sonuçlar değişmedi. Bölüm 5.13'teki bulgu: radyo gerçekçi olunca başarı 8–21 puan düşüyor, en çok radyoyu 4 kez geçen registry'ler düşüyor (%63.0 → %44.2, 3 replika %64.0 → %43.2). DQN %62.9 → %52.3 oluyor ve greedy'ye karşı farkını koruyor (+2.4 puan, GA ±1.5). DQN'i yeni radyoyla yeniden eğitmedik. Girişim, link adaptation ve Doppler yok, "hız modellendi" deme.

---

## Teknik kısa cevaplar

**NDN / Information-Centric Networking'den farkı ne?** NDN isimleri birebir ya da prefix ile eşleştiriyor. Biz anlam benzerliğiyle eşleştiriyoruz. Farklı kelimelerle sorulan istek NDN'de bulunamaz.

**Vektör paketin içinde, header büyümez mi?** float32 1.536 B, int8 388 B ve başarı aynı (%62.7'ye karşı %62.9), binary 48 B ama başarı %51.1. int8 kullanıyoruz.

**Komşunun arkasındaki yüzlerce yeteneği nasıl özetliyorsunuz?** Tek ortalama bulanıklaştırıyor (greedy %51). k = 8 temsilci + bir hop için tek tek satır %60.4. Tam tablo %64.1 ama 3.6 kat trafik.

**Komşu sayısı değişken, DQN'in çıktısı nasıl sabit?** DQN her aksiyonu ayrı skorluyor (girdi = 15 özellik, çıktı = tek Q-değeri).

**Eğitim nerede yapılıyor?** Simülasyonda offline. Ağırlıklar tüm düğümlere dağıtılıyor. Sahada lokal fine-tune gelecek iş.

**Eğitim ile test karışıyor mu?** Hayır. Eğitim ve model seçimi 350 train parafrazıyla, bütün sonuçlar 150 test parafrazıyla ve başka seed'lerle.

**Döngü olursa? Yetenekli kimse yoksa?** TTL var, paket geldiği komşuya geri gönderilmiyor. Kimse τ'yu geçmiyorsa TTL biter ve başarısız sayılır. "Burada kimse yok" sinyali bu tasarımda yok, bu yüzden boşa 16 hop harcanabiliyor.

**Sahte yetenek duyuran kötü niyetli agent?** Kapsam dışı. Gelecek iş: imzalı duyurular ya da itibar puanı.

**Yük duyarlı greedy neden greedy'den iyi değil?** Başarıda iyi değil (−0.9 puan), yaklaşık 1 ms hızlı. Kuyruktan kaçınmak daha çok agent bulmak demek değil.

---

## Söylememeniz gerekenler (v1'den kalma, artık doğru değil)

- ~~"AgentRoute en hızlısı, %7–14 daha hızlı"~~ → Eşleştirilmiş isteklerde gecikme farkı 0.2–0.5 ms, yük duyarlı kurala karşı biraz daha yavaş.
- ~~"Flooding'in dörtte biri mesaj"~~ → Sayı yerine bayt kullanıyoruz, cevap isteğin hızına bağlı.
- ~~"DQN başarıyı artırmıyor, gecikmeyi azaltıyor"~~ → v2'de tam tersi: başarıyı artırıyor, gecikmede fark yok.
- ~~"Registry 10.000 agent'ta 202 ms"~~ → O rakam her kaydın 1 ms sürdüğü varsayımından geliyordu. Şimdi 83 ms.
- ~~"En yüksek yükte DQN greedy'nin gerisinde"~~ → v2'de 2.4 puan önünde.
- ~~"Eğitim eğrisi yükseliyor, öğreniyor"~~ → ε düştüğü için zaten yükselir, doğrulama eğrisini gösteriyoruz.

---

## Hakimiyet için

- Her biriniz bir kere diğer iki kişinin kısmını anlatmayı deneyin.
- Bir prova yapın ve süre tutun: 5 dakikayı geçen kısım kısaltılmalı.
