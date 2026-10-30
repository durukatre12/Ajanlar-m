---
name: pazar-arastirmasi
description: Türkiye'deki gerçek sorunları kanıtla bulup global trendlerle eşleştiren araştırma planı, fikir kartı ve puanlama; tek kişinin 2–4 haftada MVP çıkarabileceği ölçekte fikir üretir. Kâşif kullanır.
kaynak: Ajan Köyü'nün kendi üretimi — dış kaynak yok
lisans: MIT
uyarlayan: Ajan Köyü (2026-10-31)
takimlar: [fikir-atolyesi]
---

# Pazar araştırması

## Ne zaman
Haftalık fikir koşusunda ve patron Telegram'dan bir konu attığında.

## Araştırma planı (8–15 arama, her biri ayrı)
**Türkiye — sorun var mı?**
1. Tema + "şikayet" / "sorun" (haber) — ör. "kira artışı şikayet 2026"
2. Şikayetvar'da temadaki kategori — sık geçen şikayet türleri
3. Ekşi Sözlük / Reddit r/Turkey — insanlar bunu nasıl anlatıyor (alıntı kısaltılmış, isimsiz)
4. TÜİK / ilgili bakanlık / düzenleyici (BDDK, EPDK, SPK …) — resmi sayı ya da yeni düzenleme
5. İBB Açık Veri / data.gov.tr / belediye portalları — kullanılabilir açık veri var mı
**Global — başkası çözüyor mu?**
6. Tema + "startup" / "Y Combinator" — yeni şirketler
7. Product Hunt — benzer ürünler
8. Sektör raporu (McKinsey, CB Insights, Dünya Bankası, OECD …) — trend
**Boşluk**
9. Türkiye'de aynı işi yapan yerel rakip var mı
10–15. Fikre özgü derinleştirme (veri kaynağının erişimi, API, lisans)

## Fikir kartı (her fikir)
```
## <n>. <Ad> — <tek cümle>
- **Problem ve kanıt:** kimin sorunu, ne kadar yaygın — <rozet> <kaynak>
- **Türkiye ↔ global:** <burada sorun / orada çözüm, ya da tersi>
- **Hedef kullanıcı:** <kim, kaç kişi — sayı varsa kaynaklı, yoksa "ölçülmedi">
- **Gelir modeli:** <abonelik / freemium / B2B lisans / reklam — tek cümle>
- **Rakipler ve fark:** <yerel + global, her biri bağlantılı>
- **Açık veri:** <kaynak adı + bağlantı + format>
- **MVP (2–4 hafta):** <hafta 1: veri · hafta 2: model/analiz · hafta 3: arayüz · hafta 4: yayın>
- **Patronun yetkinlikleri:** <hangileri kullanılıyor: SQL, dbt, GIS, FastAPI …>
- **Zorluk:** kolay / orta / zor · **Portföy değeri:** düşük / orta / yüksek · **Gelir şansı:** düşük / orta / yüksek
```

## Puanlama (favoriyi seçmek için)
| Ölçüt | 1–3 |
|---|---|
| Kanıtlı problem (✅ kaynak) | |
| Açık veriyle yapılabilir | |
| Patronun güçlü yanlarını kullanır (risk, GIS, veri hattı) | |
| 2–4 haftada MVP | |
| Türkiye'de boşluk + globalde karşılık | |
Toplamı en yüksek olan favoridir; eşitlikte portföy değeri yüksek olan.

## Tuzaklar
- "Yapay zekâ ile X" demek fikir değildir; problem yoksa fikir yoktur.
- Pazar büyüklüğü raporlarındaki dev sayılar fikri haklı çıkarmaz; kullanıcı ölçeğinde kanıt ara.
- Lisans/izin gerektiren alanlar (ödeme, kredi, sağlık verisi) → "zor" ve sebebini yaz.
- Rakibin gelir/kullanıcı sayısı: yalnız birincil kaynaktan (şirketin kendi açıklaması) ✅; haberden 🟡; gerisi ⛔.

## Öğrenilenler
Bu skill koşuda aldığı veriyle **kendini geliştirir**: hangi kaynak işe yaradı, hangisi boş döndü,
patron hangi fikri beğendi (Telegram'dan "fikir 2 güzel" gibi bir not gelirse) — `takimlar/<takim>/defter.md`'ye
tek ders olarak yaz. Aynı ders üç koşuda tekrar ediyorsa koşu kaydına "yetenek önerisi: `pazar-arastirmasi`
→ ## Öğrenilenler'e şu satır eklensin" yaz; kararı patron verir, skill'i kendi başına değiştirme.

- (henüz ders yok)
