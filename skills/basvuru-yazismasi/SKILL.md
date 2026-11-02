---
name: basvuru-yazismasi
description: Takip e-postası, ön yazı ve mülakat hazırlık kartı taslakları için şablon ve kontrol listesi; hepsi taslaktır, gönderilmez. Postacı kullanır.
kaynak: Ajan Köyü'nün kendi üretimi — dış kaynak yok
lisans: MIT
uyarlayan: Ajan Köyü (2026-10-31)
takimlar: [basvuru-takip]
---

# Başvuru yazışması

## Ne zaman
Haftalık takipte (7+ gün cevapsız başvuru), zincirden gelen ön yazı işinde, mülakat haberi geldiğinde.
**Hiçbiri gönderilmez.** Çıktı dosyaya yazılır; gönderen patrondur (ANAYASA §1).

## Dil ve ton
- İlan İngilizceyse İngilizce, Türkçeyse Türkçe. Emin değilsen ilanın dilini kullan.
- Kısa, saygılı, somut. Yalvarma, abartma, klişe ("tutkulu", "dinamik ekip") yok.
- Profilde olmayan deneyim, sertifika ya da sayı yazılmaz. Proje sayıları `sirket/PROFIL.md`'den birebir alınır.
- İşe alımcının adını bilmiyorsan "Merhaba," / "Hello," — isim uydurma.
- İletişim bilgisi yerine yer tutucu: `[telefon]`. E-posta imzası: ad soyad + LinkedIn + GitHub (profilde var).

## 1 · Takip e-postası (4–6 cümle)
```
Konu: <Pozisyon> başvurusu — Duru Katre Sarnıç
Merhaba,
<tarih>'te <Pozisyon> pozisyonuna başvurdum ve ilgimi yinelemek istedim.
<Role en uygun tek kanıt: proje ya da staj, bir sayıyla.>
<İlana özgü tek cümle: ilandaki bir sorumluluğa nasıl katkı vereceği.>
Sürecin hangi aşamada olduğunu öğrenebilirsem sevinirim; ek bilgi gerekirse memnuniyetle paylaşırım.
Saygılarımla,
Duru Katre Sarnıç
```
Rol → kanıt seçimi:
- risk / fraud / fintech → IEEE-CIS Fraud Risk Analytics (0.9134 ROC-AUC; en riskli %5 dilim vakaların %58.32'si)
- BI / raporlama → Futbolcu Transfer Analitiği (dbt mart modelleri + DAX'lı Power BI)
- analytics engineer → fraud projesindeki dbt testleri + GitHub Actions CI/CD
- GIS / şehir / mobilite → İmar Planlama stajı (Netcad, kadastro çakıştırma) ya da Voltyol

## 2 · Ön yazı (150–250 kelime)
Üç paragraf:
1. **Neden bu rol, neden bu şirket** — ilandan ya da şirket sayfasından somut bir şey (kaynağı açılmış).
2. **Kanıt** — role en uygun 1–2 proje/staj, ilandaki 2–3 gereksinimle birebir eşleştirerek.
   Şehir ve Bölge Planlama geçmişini artı olarak çerçevele: mekânsal düşünme, saha verisi, karar destek.
3. **Kapanış** — kısa, görüşme isteği. Klişe yok.
Altına "CV'de öne çıkar" 3 madde (`skills/ilan-eslestirme` tek ilan analizi adım 5).

## 3 · Mülakat hazırlık kartı
```
### <Şirket> — <Pozisyon> · <tarih/saat varsa>
- Şirket tek cümle: <ne yapıyor — kaynaklı>
- Rolün 3 ana işi: <ilandan>
- Anlatacağın 3 hikâye: <durum → ne yaptın → sonuç (profilden)>
- Teknik tekrar: <ilandaki araçlardan 3 konu: ör. SQL window functions, dbt testleri, A/B testi>
- Soracağın 2 soru: <role özgü>
```
İK görüşmesiyse teknik tekrar yerine: "kendini 60 sn'de anlat" iskeleti, maaş beklentisi sorusuna
hazırlık notu (rakam önerme — patron karar verir), neden bu şirket.

## 4 · Ön yazılı başvuru maili (`cikti/eposta/`, `tur: on-yazi`, `ek: cv`)
Yalnız ilan metninde bir başvuru e-postası varsa. Gövde = ön yazının e-posta hâli, 120–200 kelime:
selam → hangi pozisyon ve nerede gördüğün → 1–2 kanıt → "CV'mi ekte paylaşıyorum" → kapanış + imza
(ad soyad · LinkedIn · GitHub). Konu: `<Pozisyon> başvurusu — Duru Katre Sarnıç`.

## 5 · Tanıştırma ricası (`cikti/eposta/`, `tur: tanistirma`, `ek: yok`)
Ortak tanıdığa yazılır, işe alımcıya değil. 4–6 cümle, samimi ama kısa:
```
Konu: Küçük bir rica — <Şirket> <Pozisyon>
Merhaba <ad ya da boş>,
<Şirket>'teki <Pozisyon> ilanına başvuruyorum; LinkedIn'de <Şirket>'te <rol> ekibinde
bağlantıların olduğunu gördüm.
Uygun görürsen ekipten biriyle kısa bir tanışma ayarlayabilir misin? Rolü ilk elden dinlemek istiyorum.
<Tek kanıt: role en uygun proje, bir sayıyla.>
İstersen sana iletmen için iki satırlık bir özet ve CV'mi göndereyim. Şimdiden teşekkürler!
Duru
```
Çalışanın adını yazma (ANAYASA §2) — "ekipten biri" de; adı patron Gmail'de ekler.

## Kontrol listesi (her taslak)
- [ ] Konu satırı var
- [ ] İlana özgü en az bir cümle var
- [ ] Profilde olmayan iddia yok
- [ ] Telefon/adres yok, yer tutucu var — `cikti/eposta/` dosyasında yer tutucu bırakma: doldurulmamış `[...]`
      olan mail gönderilemez; bilmediğin şeyi cümleden çıkar
- [ ] Uzunluk sınırında

## Öğrenilenler
Bu skill koşuda aldığı veriyle **kendini geliştirir**: patron bir taslağı düzelttiyse ya da bir takip
e-postası cevap aldıysa (tablodan görürsün) bunu `takimlar/<takim>/defter.md`'ye tek ders olarak yaz.
Aynı ders üç koşuda tekrar ediyorsa koşu kaydına "yetenek önerisi: `basvuru-yazismasi` → ## Öğrenilenler'e
şu satır eklensin" yaz; kararı patron verir, skill'i kendi başına değiştirme.

- (henüz ders yok)
