---
name: site-saglik-kontrolu
description: Ücretsiz barındırmadaki (Render free tier) bir web uygulamasının ayakta olup olmadığını uyanma süresini ayırarak ölçer, GitHub commit API'siyle haftalık ilerlemeyi okur ve önceki ölçümlerle karşılaştırır. Voltyol bekçisi kullanır.
kaynak: Ajan Köyü'nün kendi üretimi — dış kaynak yok
lisans: MIT
uyarlayan: Ajan Köyü (2026-10-31)
takimlar: [voltyol-bekci]
---

# Site sağlık kontrolü

## Ne zaman
Haftalık Voltyol kontrolünde ve patron "site" / "voltyol" diye sorduğunda.

## Ölçüm
```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}\n" --max-time 90 https://ev-rota.onrender.com
```
- Render free tier 15 dk hareketsizlikte uyur; ilk istek 30–60 sn sürebilir. Bu **normaldir**.
- İlk ölçüm 30 sn'den uzunsa ya da zaman aşımına uğradıysa ikinci `curl`'ü hemen at ve **bir kez daha** ölç
  (ilk istek siteyi uyandırmıştır; `Bash(curl *)` dışında komut iznin yok).
- Tabloya ikisini de yaz: `uyanma` (ilk) ve `sıcak` (ikinci).

## Eşikler
| Durum | Koşul | Özette |
|---|---|---|
| Sağlıklı | sıcak yanıt 2xx/3xx ve < 3 sn | "Site ayakta, sıcak yanıt <x> sn." |
| Yavaş | sıcak yanıt 2xx/3xx ama ≥ 3 sn | "Site ayakta ama yavaş." |
| Sorunlu | iki ölçüm de 4xx/5xx ya da zaman aşımı | "Site açılmıyor — Render panosuna bakman gerekebilir." |

## Repo okuma
```bash
curl -s "https://api.github.com/repos/durukatre12/EV-rota/commits?since=<YYYY-MM-DDT00:00:00Z>&per_page=30"
```
- Cevap JSON listesi: her öğede `commit.message` ve `commit.author.date`. Mesajın yalnız ilk satırını yaz.
- `{"message": "Not Found"}` → repo private ya da adı farklı: "repo okunamadı" yaz, tahmin etme.
- Saatlik 60 istek sınırı var (anahtarsız); haftada bir istek için sorun değil.

## Karşılaştırma
`veri/olcumler.md` satırlarından son 4 ölçümü al: sıcak süre artıyor mu, commit sıklığı nasıl.
İlk koşuda "ilk ölçüm — karşılaştırma gelecek hafta" yaz.

## Sıradaki adım önerisi
Commit mesajlarına ve önceki önerilere bak; bir oturumda bitecek **tek** somut iş öner. Havuz (repo durumuna göre seç):
gerçek şarj istasyonu verisi (açık kaynak/OpenChargeMap) · mobil görünüm · maliyet hesabında tarife güncelleme ·
README'ye ekran görüntüsü ve "nasıl çalışır" · Render uyanma süresi için hafif bir ping · basit kullanım ölçümü.

## Öğrenilenler
Bu skill koşuda aldığı veriyle **kendini geliştirir**: ölçümde neyin yanılttığını (ör. uyanma süresi,
API sınırı) `takimlar/<takim>/defter.md`'ye tek ders olarak yaz. Aynı ders üç koşuda tekrar ediyorsa koşu
kaydına "yetenek önerisi: `site-saglik-kontrolu` → ## Öğrenilenler'e şu satır eklensin" yaz; kararı patron
verir, skill'i kendi başına değiştirme.

- (henüz ders yok)
