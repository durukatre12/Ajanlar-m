---
name: sicak-temas
description: İlan açan şirkette benzer rolde çalışan, patronla ortak geçmişi olan kişilere ulaşmak için hazır LinkedIn kişi araması bağlantıları ve kısa bağlantı notu taslağı üretir; isim toplamaz, giriş yapmaz, mesaj göndermez. İlan avcısı günlük taramada öne çıkan ilanlar için kullanır.
kaynak: Ajan Köyü'nün kendi üretimi — dış kaynak yok
lisans: MIT
uyarlayan: Ajan Köyü (2026-11-03)
takimlar: [ilan-avcisi]
---

# Sıcak temas

**Soğuk başvuruyu sıcak tanıştırmaya çeviren şey ortak geçmiştir; ajan kapıyı gösterir, kapıyı patron çalar.**

## Ne zaman
Günlük taramada listeye giren her **öne çıkan** ilan (puan 8+) ve puanı 7 olan en fazla 3 ilan için.
Patron Telegram'dan "temas <no>" yazarsa o numaralı ilan için de.

## Pazarlıksız kurallar (ANAYASA §1, §2)
- LinkedIn'e giriş yapılmaz, profil sayfası açılmaz/kazınmaz, kişi adı toplanmaz ya da çıktıya yazılmaz.
- Ajanın ürettiği şey **arama bağlantısı**dır; aramayı patron kendi oturumuyla açar.
- Bağlantı notu taslaktır, gönderilmez. İşe alımcıya değil, **benzer rolde çalışana** yazılır.
- Not, profilde olmayan bir iddia taşımaz; proje sayıları `sirket/PROFIL.md`'den birebir alınır.

## Adımlar
1. İlandan **şirket adı** (LinkedIn'deki yazılışıyla, ör. "Trendyol", "QNB Finansbank") ve **rol anahtarı**
   çıkar: data analyst · fraud analyst · risk analyst · business intelligence · analytics engineer.
2. Her ilan için şu üç aramayı kur. Anahtar kelimeleri boşlukla birleştir, URL'de `%20` ile kodla:
   - **İTÜ mezunu (en sıcak):**
     `https://www.linkedin.com/search/results/people/?keywords=<şirket>%20<rol>%20İstanbul%20Teknik%20Üniversitesi`
   - **Workintech mezunu:**
     `https://www.linkedin.com/search/results/people/?keywords=<şirket>%20<rol>%20Workintech`
   - **2. derece bağlantı (ortak tanıdık üzerinden):**
     `https://www.linkedin.com/search/results/people/?keywords=<şirket>%20<rol>&network=%5B%22S%22%5D`
   Türkçe karakterler URL'de kalabilir; tarayıcı kodlar.
3. Bir bağlantı notu taslağı yaz (aşağıdaki şablon), **en fazla 200 karakter** (LinkedIn not sınırı için güvenli pay).
   Ortak geçmiş satırını aramaya göre seç: İTÜ → "İTÜ Şehir ve Bölge Planlama mezunuyum",
   Workintech → "Workintech veri analitiği programını yeni bitirdim", 2. derece → ortak tanıdığı patron yazar: `[ortak bağlantı]`.
4. Çıktıda ilanın altına `Sıcak temas` bloğunu ekle (şablon aşağıda).

## Not şablonu
```
Merhaba [ad], <ortak geçmiş>. <Şirket>'teki <rol> ilanına başvuruyorum; ekipte bu rolün
gündelik işini sizden iki dakika dinleyebilir miyim?
```
Rol → tek kanıt eklemek gerekirse (karakter kalırsa): fraud/risk → "IEEE-CIS fraud projemde
LightGBM ile 0.9134 ROC-AUC aldım"; BI → "dbt + Power BI ile transfer analitiği kurdum".

## Çıktı şablonu (ilanın altına)
```
   **Sıcak temas** · [İTÜ](<url>) · [Workintech](<url>) · [2. derece](<url>)
   Not: "<200 karakterlik taslak>"
```

## Kalite kontrol listesi
- [ ] Çıktıda hiçbir kişi adı yok (yer tutucu `[ad]`)
- [ ] Üç bağlantı da `linkedin.com/search/results/people/` ile başlıyor
- [ ] Not ≤ 200 karakter ve işe alımcıya değil çalışana hitap ediyor
- [ ] Notta profilde olmayan iddia yok

## Öğrenilenler
Bu skill koşuda aldığı veriyle **kendini geliştirir**: patron Telegram'dan bir temasın cevap verdiğini ya da
bir aramanın boş döndüğünü yazarsa bunu `takimlar/ilan-avcisi/defter.md`'ye tek ders olarak yaz. Aynı ders
üç koşuda tekrar ediyorsa koşu kaydına "yetenek önerisi: `sicak-temas` → ## Öğrenilenler'e şu satır eklensin"
yaz; kararı patron verir, skill'i kendi başına değiştirme.

- (henüz ders yok)
