# Projeyi anlama ve gösterme rehberi

Bu rehber kodu, testleri ve raporu kontrol ederek kendi anlatımını hazırlaman için yazıldı. Kod, test tasarımı ve rapor OpenAI Codex desteğiyle oluşturuldu; hocanın istediği şekilde bu yardımı belirtmelisin. Hocanın konu onayı geldiği iddia edilmiyor.

## Projenin tek cümlelik açıklaması

Kampüsteki bir ekipman masasının, öğrencinin veya personelin yeni bir ekipman ödünç alıp alamayacağını belirleyen, teslim tarihini hesaplayan ve gecikmiş iade ücretini bulan küçük bir Java konsol uygulaması.

## Kuralların mantığı

Öğrencinin en fazla 3, personelin en fazla 5 aktif ödüncü olabilir. Yeni isteğin kabulü için mevcut sayı bu sınırın altında olmalı. Öğrencinin 2 ödüncü varsa yenisi değerlendirilebilir; 3 varsa reddedilir. Üyelik de aktif ve borç tam sıfır olmalı. Üç şartın hepsi birlikte gerekli.

Borç kuruş olarak tutulur. `0` borçsuzdur, `1` bir kuruş borçtur ve reddedilir. `100` bir TL'dir. Ondalıklı `double` kullanmadığımız için para karşılaştırmalarında kayan nokta yuvarlama problemi oluşmaz.

Öğrenci 1–7, personel 1–14 gün isteyebilir. 23 Kasım'da 7 günlük isteğin son günü 30 Kasım'dır. Hafta sonları da takvim günüdür. Sistem bugünün tarihini kendiliğinden almaz; tarih açıkça verilir, böylece aynı test yarın da aynı sonucu verir.

Son günde veya daha önce iade ücretsizdir. 1 gün gecikme 100 kuruş, 49 gün 4.900 kuruş, 50 ve daha fazla gün en fazla 5.000 kuruştur. Ekipmanı ödünç almadan önce iade etmek geçersizdir; ödünç aldığı gün geri vermek geçerlidir.

## Sınıflar nasıl ayrılıyor

| Sınıf | Görevi |
| --- | --- |
| `Role` | Öğrenci/personel için sayı ve gün sınırlarını tutar. |
| `Borrower` | Kişinin rol, üyelik, aktif ödünç sayısı ve borç bilgisinin değişmez bir anlık görüntüsüdür; negatif veriyi reddeder. |
| `LoanService` | İsteği doğrular, üç uygunluk şartını ayrı ayrı kontrol eder, sonucu döndürür. |
| `RejectionReason` | Üç ret nedeninin sabit adlarıdır. |
| `LoanDecision` | Kabul/ret, nedenler ve varsa son tarihi taşır. Ret halinde son tarih yoktur. |
| `OverdueFeeService` | Tarih sırasını kontrol eder, gecikme gününü ve tavanlı ücreti hesaplar. |
| `ConsoleApp` | Komut satırını okur, servisleri çağırır, kullanıcıya sonucu gösterir. |

Bu servisler ekipman kaydı oluşturmaz, sayıyı artırmaz, borç tahsil etmez. Proposal kapsamı bir değerlendirme servisidir; veri tabanı ve stok sistemi yoktur. Bu yüzden aynı girdiyi tekrar değerlendirmek aynı sonucu verir.

## Ret ile hata arasındaki fark

Aktif olmayan üyelik, 1 kuruş borç veya dolu kontenjan geçerli bilgidir; cevap `REJECTED` olur. Üçü aynı anda varsa üç neden de listelenir. Buna karşılık negatif ödünç sayısı, eksik tarih veya 8 günlük öğrenci isteği geçersiz girdidir ve servis `IllegalArgumentException` üretir. Konsol bunu anlaşılır mesaj ve 2 çıkış koduyla gösterir.

## Test tekniklerini bu projeyle anlatma

**Equivalence Partitioning:** Borcu sıfır, pozitif ve negatif olarak sınıflandırdık. Pozitif sınıftan birkaç örnek, bu sınıfın anlamını test eder; her TL miktarını denemek gerekmez.

**Boundary Value Analysis:** Öğrenci için 2, 3 ve 4 aktif ödünç; süre için 0, 1, 6, 7, 8 gün; ücret tavanı için 49, 50 ve 51 gecikme günü özellikle seçildi. Karşılaştırma hataları çoğunlukla tam bu noktalarda görünür.

**Decision Table:** Aktif mi, borç sıfır mı, yer var mı şeklindeki üç evet/hayır sorusunun 2³ = 8 kombinasyonu var. Sekizini de öğrenci ve personel için çalıştırdık; toplam 16 karar tablosu senaryosu. Bu, tüm uygulamanın her olası girdisini tükettiğimiz anlamına gelmez.

**Negative Testing:** Eksik tarih, negatif para, yanlış rol, geçersiz takvim günü ve sayı taşmasını denedik. Sadece kabul senaryolarını test etmedik.

**Regression Testing:** Kontrollü hataları ayrı kopyalarda denedikten sonra orijinal projenin bütün testlerini tekrar çalıştırdık. Ayrıca önceki çağrının bir sonraki karar veya ücrete etki etmediğini test ettik.

## Hata deneylerini doğru anlatma

Üç hata bilerek, geçici kopyalara eklendi. Bunları geliştirme sırasında kazara yaptığın hatalar gibi anlatma.

1. `>=` yerine `>` kullanıldığında sınırdaki kişi yanlış kabul edildi; CAP-03 ve CAP-07 bunu yakaladı.
2. Gecikmeye fazladan 1 gün eklendiğinde zamanında iadeye ücret çıktı; FEE-03 ve başka sınır testleri başarısız oldu.
3. Ücret tavanı kaldırıldığında 51 gün için 50 yerine 51 TL çıktı; FEE-08 ve FEE-09 bunu yakaladı.

Gerçek başarısız çalıştırmalar `evidence/fault-injection` içinde. Asıl kod bu deneylerde değiştirilmedi; deneylerden sonra tam test paketi tekrar geçti.

## Coverage hakkında ne söylemelisin

Coverage bir satırın veya dalın çalıştığını gösterir. Beklenen sonucun doğru seçildiğini ya da gereksinimlerin eksiksiz olduğunu kanıtlamaz. Örneğin yanlış bir ücret formülü de bütün satırları çalıştırabilir. Bu yüzden karar tablosu, bağımsız beklenen sonuçlar ve hata deneyleri de var.

Rapor bütün üretim sınıflarını kapsıyor; konsolu dışarı çıkarıp oran yükseltmedik. Konsolun ayrı JVM'deki `main` çalışmaları gerçek uçtan uca kanıt sağlar, fakat bu süreçler JUnit'in JaCoCo ajanıyla ölçülmez. Tam sayılar `evidence/summary.json` ve İngilizce raporda bulunur.

## Kısa gösterim sırası

Proje klasöründe terminal aç:

```sh
./scripts/build.sh clean verify
./scripts/run.sh --demo
./scripts/run.sh loan STUDENT true 2 0 2026-11-23 7
./scripts/run.sh loan STUDENT true 3 0 2026-11-23 7
./scripts/run.sh loan STAFF false 5 1 2026-11-23 14
./scripts/run.sh fee 2026-11-23 2026-11-30 2026-11-30
./scripts/run.sh fee 2026-11-23 2026-11-30 2026-12-01
./scripts/run.sh fee 2026-11-23 2026-11-30 2027-03-01
./scripts/run.sh loan STUDENT true -1 0 2026-11-23 7
```

Sırasıyla testler, demo, kabul, kapasite reddi, üç nedenli ret, sıfır ücret, 1 TL, 50 TL tavanı ve giriş hatası görünür. Son olarak `evidence/test-cases.html` ile girdileri/sonuçları, `evidence/jacoco/index.html` ile coverage'ı göster.

## Hocaya açıklayabilmen gereken noktalar

`>=` neden gerekli, 7 günlük istekte tarihe neden 7 ekleniyor, geçersiz girdinin normal retten farkı ne, neden `long` ve `LocalDate` seçildi, neden bütün ret nedenleri dönüyor, 100% coverage neden tek başına yeterli değil ve JUnit 4 örnekleri yerine neden JUnit 5 kullanıldı. Cevaplar specification, kod ve testlerle birbirini tutmalı. Rapordaki tartışmayı okuyup kendi gerçekten karşılaştığın öğrenme deneyimlerini ekle; yazılmamış kişisel deneyim uydurulmadı.

## Yönergenin 7 ve 9. maddeleri için çalışma

7. madde bireysel çalışma ve öğrenmeyi, 9. madde kendi çalışmanı temsil etme, kullanılan yardımı bildirme ve kararları açıklayabilmeyi istiyor. AI kullanımının belirtilmesi bu koşulların tümünün karşılandığını tek başına göstermez. Hazır kodu okuyabilmek de kodun başlangıçta nasıl üretildiğini değiştirmez. Kendi yaptığın katkıları ve öğrendiğin noktaları doğru biçimde kaydet; hocanın izin verdiği yardım kapsamına göre değerlendir.

### Gerçek katkı ve inceleme kaydı

Bu kayıt, 24 Kasım 2026 tarihli konuşmadaki yanıtlar ve öğrencinin ChatGPT ile yaptığı ek çalışmaya ilişkin beyanı kullanılarak güncellendi. Kişisel katkı ve öğrenme açıklaması İngilizce raporun 7. bölümüne eklendi.

| Başlık | Kaydedilen katkı veya çalışma |
| --- | --- |
| Konu ve kapsam | Öğrenci mevcut konuyu ve küçük Java konsol kapsamını bu çalışmaya taşıdı; proposal ile gönderdiği onay e-postasını paylaştı. |
| Sınır örneği | Personelin 5 mevcut ödünçte reddedileceğini ve `>=` yerine `>` hatasını yakalayan değerin 5 olduğunu belirledi. |
| Geçersiz girdi | Pozitif borcun normal ret; negatif borcun ve öğrencinin 8 günlük isteğinin geçersiz girdi hatası ürettiğini belirledi. |
| Ücret örneği | 60 gün gecikmede tavanın 50 TL olduğunu söyledi; 8 Aralık son tarih ve 11 Aralık gerçek iade için 300 kuruşu doğru hesapladı. |
| JUnit kontrolü | Öğrenci beklenen ve gerçek sonuç ayrımını öğrendiğini belirtti. Doğru sonuç 300 iken testin 400 beklemesi durumunda yanlış test beklentisinin düzeltilmesi gerektiği öğrenme bölümüne eklendi. |
| Ek öğrenme beyanı | Öğrenci Java ve JUnit kavramlarını, test tekniklerini ve coverage konularını ChatGPT ile çalışıp öğrendiğini belirtti. Bu beyan rapora yansıtıldı. |
| Kullanılan yardım | Uygulama, test tasarımı, çalıştırma, analiz ve raporda Codex; kavramları öğrenmede ChatGPT desteği belirtildi. |

Öğrencinin kendi bilgisayarında bağımsız derleme, test çalıştırma veya kod değişikliği yaptığına ilişkin bir kayıt eklenmedi. Korunan çalıştırma kanıtları proje araçlarıyla alınan gerçek sonuçlardır.

### Öğrenilen JUnit kontrolü

Öğrenci, `assertEquals(300L, actual)` kontrolündeki beklenen değer ile programın gerçek sonucu arasındaki ayrımı öğrendiğini belirtti. Üç günlük gecikme için doğru sonuç 300 kuruştur. Program 300 döndürürken test 400 bekliyorsa gereksinime uymayan test beklentisi 300 olarak düzeltilir. Bir testin başarısız olması incelenirken hem uygulama hem de beklenen sonucun gereksinimlere uygunluğu kontrol edilir. Bu konu öğrenilmiş olarak kaydedildi.

### Sonucu önce kendin tahmin et

Aşağıdaki sorular tekrar ve gösterim hazırlığı içindir. Konuşmada yanıtlanan örneklerle birlikte kullanılabilir; resmi bir sınav veya bağımsız uygulama değerlendirmesi değildir.

1. Aktif bir öğrencinin 2 ödüncü ve 1 kuruş borcu var. 24 Kasım 2026'da 7 gün istiyor. Sonuç ne olur, hangi neden döner ve teslim tarihi bulunur mu? Bu örnek hangi girdi sınıfını sınar?
2. Borçsuz, aktif bir öğrencinin mevcut ödünç sayısı 3. Karşılaştırmayı `>=` yerine `>` yapmak neyi değiştirir? Bu yanlışı yakalayacak iki komşu sınır değeri seç.
3. Öğrenci 24 Kasım 2026'da 7 günlük geçerli bir istek yapıyor. Son tarihi hesapla; o tarihte, ertesi gün ve 51 gün sonra iade ücretlerini kuruş ve TL olarak söyle. Kullanılacak test tekniğini gerekçelendir.
4. Aynı öğrencinin üyeliği pasif ve istediği süre 8 gün olursa normal ret mi, geçersiz girdi hatası mı beklenir? İşlem sırasını hangi gereksinim belirliyor?
5. Öğrenci için 7 yerine 6 gün ekleyen bir uygulama düşün. Bütün satırlar yine çalışabilir mi? Hangi beklenen-sonuç kontrolü yanlışı ortaya çıkarır?

Soruların ardından kendin bir ek senaryo seç, beklenen sonucu kurallardan çıkar ve mevcut testlerden hangisinin bunu kapsadığını bul. Kapsanmıyorsa yeni testin neyi farklı doğrulayacağını açıkla. Yeni test eklemeden önce senaryonun amacını netleştir.

### Gösterim için öz değerlendirme

- İncelediğin kod ve testleri kendi cümlelerinle açıkla.
- Bir sınır senaryosunun beklenen sonucunu kodu çalıştırmadan çıkar.
- Kontrol amacıyla eklenen üç hatayı gerçek geliştirme hatalarından ayır.
- Kendi katkını ve kullanılan yardımı rapordaki açıklamayla tutarlı anlat.
- Teknik testlerin geçmesi ile gereksinimlerin doğru ve eksiksiz olması arasındaki farkı açıkla.
