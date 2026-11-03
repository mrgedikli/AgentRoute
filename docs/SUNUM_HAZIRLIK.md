# AgentRoute — Sunum Hazırlığı (11 Kasım 2026)

Toplam ~15 dakika, kişi başı ~5 dakika. Slaytlar İngilizce. Canlı demo yok, kaydedilmiş animasyon videosu kullanılacak.

**Tek cümle:** "Paketleri bir adrese değil bir yeteneğe yönlendiriyoruz, router'lar da en iyi yolu kendi kendine öğreniyor."

**Slaytlar:** `docs/slides/AgentRoute.pptx` (PDF: `docs/pdf/AgentRoute_Slides.pdf`). Her slaytın konuşmacı notlarında söylenecekler ve gerçek rakamlar var.

| Slaytlar | Konuşmacı | İçerik |
|---|---|---|
| 1–5 | Ömer | Başlık, "nerede" vs "kim yapabilir", iki klasik çözüm, ilgili çalışmalar, tek resimde AgentRoute |
| 6–9 | Bekir Emre | Capability address, S-FIB, duyuru yarıçapı R, greedy ve sınırı (kapanış sorusu) |
| 10–18 | Bekir Göktepe | DQN, eğitim eğrisi, handover, deney düzeni, ölçek, dayanıklılık, iki video, takeaways |
| 19 | (yedek) | S-FIB özeti ve header boyutu, soru gelirse |

---

## 1. Ömer (~5 dk): Sorun ve büyük resim

- Bugünkü internet **"nerede?"** sorusuna göre çalışıyor: IP adresi + DNS ile zaten bilinen isimler. Posta benzetmesi: postacı kime gittiğini bilmez, adrese götürür.
- AI agent'lar **"bu işi kim yapabilir?"** diye soruyor, kim olduğunu ve nerede olduğunu bilmeden, makine hızında, büyük ve sürekli değişen bir kalabalıkta.
- Bugünkü iki seçenek:
  - Merkezi kayıt (DNS benzeri): darboğaz ve tek hata noktası.
  - Flooding: küçük ağda çalışır, büyük ağda ortalığı mesajla doldurur.
- Üstüne mobilite: agent'ların çoğu telefonda, arabada, dronda; bağlı oldukları baz istasyonu sürekli değişiyor.
- Literatür: agent'a özel katmanlar HTTP'nin üstünde [1], discovery servisleri [3], [4]. **Biz ağ katmanının kendisini yeniden tasarlıyoruz.**
- Figure 1 ile genel bakış, ayrıntıya girmeden: duyurular tabloları dolduruyor, görev paketi hop hop yetenekli agent'a gidiyor.

## 2. Bekir Emre (~5 dk): Adresleme ve semantik tablo

- **Capability address:** yetenek cümlesi → MiniLM ile 384 boyutlu vektör. Anlamca yakın cümlelerin vektörleri de yakın. Örnek çift göster: "find the cars in this photo" ↔ "object detection in images".
- **S-FIB:** normal router "şu IP aralığı için şu kapıdan çık" der. Bizim router "bu komşumun tarafında şu tür yetenekler var" der. AVM benzetmesi: koridor başındaki "bu tarafta elektronik ve kitapçı var" tabelası.
- **Sınırlı yarıçaplı duyurular:** agent'lar yeteneklerini R hop uzağa kadar duyurur, bütün ağa değil.
- **Greedy iletme:** her hop'ta en benzer komşuya gönder.
- Bitiriş sorusu (sözü Bekir Göktepe'ye bağlar): **"Peki en benzer komşu o an tıkalıysa ya da cihaz tam hücre değiştiriyorsa?"**

## 3. Bekir Göktepe (~5 dk): Öğrenen router, mobilite, değerlendirme

- **DQN:**
  - State (her komşu için): benzerlik skoru, kuyruk doluluğu, link kalitesi, handover bayrağı.
  - Action: paketi hangi komşuya göndereceği.
  - Reward: −gecikme, ulaşırsa +bonus, düşerse −ceza.
  - Tüm router'lar tek bir ağı paylaşıyor ve her komşuyu ayrı skorluyor, bu yüzden komşu sayısı fark etmiyor.
  - Navigasyon benzetmesi: kuş uçuşu en kısa yol ile trafiğe göre en hızlı yol farklı şeyler.
- **Mobilite:** handover'da bütün ağ yeniden flood edilmiyor. Eski taraf withdraw ediyor, yeni taraf yakın çevreye duyuruyor.
- **Değerlendirme:**
  - Ortam: gNB + edge, core, sabit ve mobil (random-waypoint) agent'lar. ~50 yetenek sınıfı, parafraz istekler.
  - 4 baseline: merkezi registry, flooding, Chord (exact match), greedy (öğrenmesiz).
  - Metrikler: başarı oranı, tamamlanma süresi, hop sayısı, kontrol mesajı yükü, 100 → 10.000 agent, mobilite ve düğüm çökmesi altında dayanıklılık.
  - **Gerçek sonuçlar** (5 seed):
    - Chord parafraz isteklerin hiçbirini bulamıyor.
    - Flooding en yüksek başarıyı alıyor (%61.5), ama istek başına 1.230 mesajla.
    - Registry 10.000 agent'ta 202 ms'ye çıkıyor ve kendi router'ı çökünce başarı %14–17'ye düşüyor.
    - AgentRoute en hızlısı (21 ms), mesajda flooding'in dörtte biri.
    - DQN başarıda greedy ile aynı, %7–14 daha hızlı, ama en yüksek yükte greedy'nin 3.7 puan gerisinde.
  - Beklentiden farkı dürüstçe söyle: DQN başarıyı artırmadı, gecikmeyi azalttı. Başarıyı sınırlayan şey eşleşme kalitesi.
- İki video: `agentroute_demo.mp4` (duyuru → istek → handover) ve `greedy_vs_agentroute.mp4` (aynı istek, iki yöntem).
- Kapanış: tek cümle + gelecek iş.

---

## Olası sorular ve kısa cevaplar

Üçünüz de bunların hepsine 2–3 cümleyle cevap verebilmelisiniz.

**NDN / Information-Centric Networking'den farkı ne?** (En olası soru)
NDN de isimle yönlendiriyor ama isimler birebir ya da prefix eşleşmesiyle aranıyor. Biz anlam benzerliğiyle eşleştiriyoruz. Farklı kelimelerle sorulan istek NDN'de bulunamaz, bizde bulunur.

**Bu gerçekten ağ katmanı mı?**
Tasarım ağ katmanında: adresleme, yönlendirme tablosu, hop hop iletme. Gerçek dünyada ilk aşamada IP üzerinde overlay olarak kurulabilir, IPv6'nın başta IPv4 üzerinden tünellenmesi gibi.

**Vektör paketin içinde, header büyümez mi?**
384 × float32 ≈ 1.5 KB. int8 ile 384 byte, binary ile 48 byte. Maliyeti kabul edip sıkıştırmayla çözülebileceğini söyle.

**Komşunun arkasındaki yüzlerce yeteneği tek vektörde nasıl özetliyorsunuz?**
Ortalama farklı yetenekleri bulanıklaştırır. Komşu başına birkaç temsilci vektör (küme merkezi) tutuyoruz, komşu skoru en yüksek benzerlik.

**Komşu sayısı değişken, DQN'in çıktısı nasıl sabit?**
DQN her komşuyu ayrı skorluyor (girdi = komşunun özellikleri, çıktı = tek Q-değeri), en yüksek skorlu komşu seçiliyor.

**Eğitim nerede yapılıyor?**
Simülasyonda offline. Ağırlıklar tüm düğümlere dağıtılıyor. Sahada lokal fine-tune gelecek iş.

**Döngü olursa? Yetenekli kimse yoksa?**
TTL var, paket geldiği komşuya geri gönderilmiyor. Agent benzerlik eşiği τ'nun üstündeyse işi kabul ediyor. TTL biterse başarısız sayılıyor ve success rate'e yansıyor.

**Duyuru yarıçapı neden sınırlı?**
Takas: yarıçap büyüdükçe bilgi iyileşir ama kontrol mesajı yükü artar. Bunu deneyle ölçüyoruz.

**SPFR'den farkınız?**
SPFR kuralı elle tasarlıyor (heuristic), biz öğreniyoruz. Ayrıca mobil/hücresel topolojide değerlendiriyoruz.

**Chord neden bu kadar kötü, kasıtlı zayıf bir baseline mı?**
Chord bugünkü exact-match discovery'nin temsilcisi. Anlamsal eşleşmenin neden gerekli olduğunu gösteren bir referans noktası. Asıl rakibimiz greedy semantik forwarding.

**Neden greedy yetmiyor?**
Greedy sadece benzerliğe bakıyor, tıkanıklığı, link kalitesini ve handover'ı bilmiyor. DQN bunları da tartıyor. Ölçtüğümüz etki: kuyruk taşmaları %4.3'ten %0.4'e iniyor ve istekler %7–14 daha hızlı ulaşıyor. Başarı oranı ise aynı kalıyor.

**Flooding sizden daha başarılı, neden onu kullanmayalım?**
Flooding bütün adaylara soruyor ve en iyisini seçiyor, bu yüzden %61.5. Ama 10.000 agent'ta istek başına 1.230 mesaj harcıyor (bizde 315) ve iki kat yavaş (52 ms, bizde 21 ms). Bizim yöntem yolda τ'yu geçen ilk agent'a teslim ediyor, o agent isteklerin %14–15'inde yanlış sınıftan oluyor. Bu hop hop teslimin bedeli. Agent tarafında doğrulama ile azaltılabilir.

**Başarı neden %50 civarında?**
İsteklerin yaklaşık %28–30'u için ağda τ'yu geçen hiçbir agent yok: MiniLM bu parafrazları yeteneklere yeterince yakın bulmuyor. Global bilgiye sahip registry bile %56'da kalıyor. Yani sınır yönlendirme değil, eşleşme kalitesi. Daha iyi bir encoder ya da fine-tuning gelecek iş.

**DQN yük altında neden greedy'nin gerisinde?**
En yüksek yükte neredeyse her yoğun router taşıyor. DQN'in bunlardan kaçan yolları uzuyor ve daha çok paketin TTL'i bitiyor. Eğitimde yüklü senaryolara daha çok ağırlık vermek ya da reward'a TTL'e duyarlı bir ceza eklemek çözüm adayları. Bunu açık sorun olarak raporda yazdık.

**Sahte yetenek duyuran kötü niyetli agent?**
Kapsam dışı, limitation. Gelecek iş: imzalı duyurular ya da itibar puanı.

**10.000 agent'ı gerçekten simüle edebiliyor musunuz?**
Benzerlik hesapları numpy ile vektörleştiriliyor. Sunumda küçük ölçek, ölçeklenebilirlik deneyi final raporda.

---

## Hakimiyet için

- Her biriniz bir kere diğer iki kişinin kısmını anlatmayı deneyin.
- Bir prova yapın ve süre tutun: 5 dakikayı geçen kısım kısaltılmalı.
