# Ajan Köyü

> Duru'nun iş arama ve ürün geliştirme işlerini yapan dört ajanlık küçük köy. Gönder düğmesi insanda.
> İskelet: [selmakcby/a-sirketi](https://github.com/selmakcby/a-sirketi) (MIT).

## Ne bu
- **ilan-avcisi** (Gözetleme kulesi) — hafta içi her sabah yeni junior veri analisti ilanlarını tarar, puanlar;
  Telegram'dan gelen tek ilan linkini CV ile karşılaştırır.
- **basvuru-takip** (Postane) — başvuru tablosunu tutar; "başvurdum 3", "mülakat geldi" haberlerini işler;
  takip e-postası, ön yazı ve mülakat kartı **taslağı** yazar.
- **fikir-atolyesi** (Fikir atölyesi) — cumartesi Türkiye ↔ global pazar araştırması, 3–4 proje fikri.
- **voltyol-bekci** (Şarj istasyonu) — pazar Voltyol sitesini ve EV-rota reposunu kontrol eder.
- **bekçi** (`bin/bekci.py`) — Stop hook'ta her koşuyu denetler; red verirse ajan aynı oturumda düzeltir.
- **dağıtıcı** (`bin/dagitici.py`) — zinciri kurar (ilan-avcisi 8+ puanlı ilan → basvuru-takip ön yazı).
- **dinleyici** (`bin/telegram_dinle.py`) — bota düşen mesajı ilgili takıma yönlendirir ve o an koşturur.
- **günlük** (`bin/gunluk.py`) — 09:00 günün planı, saatlik dağıtıcı, 22:00 denetim.
- **köy** (`bin/koy.py`) — http://localhost:8765 pikselli köy; durum, çıktılar, "şimdi çalıştır".
- **haber** (`bin/haber.py`) — koşu bitince çıktının özet paragrafını patronun Telegram'ına yollar.

## Okuma sırası (her ajan, her koşuda)
1. `ANAYASA.md` — değişmez çerçeve
2. `sirket/AJAN-KIMLIGI.md` — kimsin, nasıl çalışırsın
3. `takimlar/<takim>/kurallar.md` — takımın sınırları
4. `takimlar/<takim>/takim.md` — koşu adımları ve çıktı sözleşmesi
5. `sirket/PROFIL.md` ve `skills/` — işi karşılayan yetenek varsa

## Klasör yapısı
```
bin/                  kos.py · bekci.py · dagitici.py · telegram_dinle.py · gunluk.py · haber.py · koy.py
                      zamanla.py (macOS) · zamanla_windows.py + wsl-tetik.sh (Windows/WSL)
koy/index.html        pikselli köy arayüzü
sirket/               AJAN-KIMLIGI.md · PROFIL.md · YETENEKLER.md
takimlar/<takim>/     takim.md · kurallar.md · defter.md · durum.json · kosu/ · cikti/ · veri/
skills/<ad>/SKILL.md  yetenekler
.env                  anahtarlar — asla commit'e girmez
```
`kosu/`, `cikti/`, `veri/` (başvuru tablosu dahil) git'e girmez; yalnız bu bilgisayarda kalır.

## Yasaklar
- `.env` okuma, açma, ekrana basma — anahtar yalnız süreç ortamından gelir
- Başvurma, e-posta gönderme, form doldurma, hesaba giriş, mesaj atma
- Para harcama — abonelik, satın alma, tavan dışı ücretli çağrı
- `ANAYASA.md`, `kurallar.md` ve `sirket/PROFIL.md` değiştirme — üçü de insanındır
