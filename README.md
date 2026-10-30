# Ajan Köyü

Dört Claude Code ajanı, bir bekçi, bir dağıtıcı ve hepsini izleyebildiğin pikselli bir köy.
İlan avcısı her sabah yeni veri analisti ilanlarını tarar. Postacı başvurularını takip edip taslak yazar.
Kâşif haftalık proje fikri araştırır. Bekçi Voltyol'u kontrol eder. Sonuçlar Telegram'a özet olarak düşer.
**Gönder düğmesi insanda:** hiçbir ajan başvurmaz, e-posta göndermez, kimseye yazmaz.

Bu repo [selmakcby/a-sirketi](https://github.com/selmakcby/a-sirketi) (MIT) iskeletinden uyarlandı:
dört dosyalı takım yapısı, bekçi, dağıtıcı, tavanlar ve Telegram dinleyicisi oradan gelir.
Takımlar, yetenekler, köy arayüzü, Telegram özetleri ve Windows (WSL) zamanlayıcısı bu repoya özgüdür.

## Dört takım

| Bina | Takım | Ne zaman | Ne çıkar |
|---|---|---|---|
| 🔭 Gözetleme kulesi | `ilan-avcisi` | hafta içi 09:00 · Telegram'dan "ilan bak" ya da ilan linki | `cikti/<tarih>-ilanlar.md` — numaralı, puanlı, bağlantılı yeni ilanlar |
| 📮 Postane | `basvuru-takip` | Telegram'dan "başvurdum 3", "mülakat geldi" · pazartesi · zincirden | başvuru tablosu, takip e-postası / ön yazı / mülakat kartı **taslakları** |
| 💡 Fikir atölyesi | `fikir-atolyesi` | cumartesi · Telegram'dan "fikir: tarım" | `cikti/<tarih>-fikirler.md` — 3–4 kaynaklı fikir + haftanın favorisi |
| ⚡ Şarj istasyonu | `voltyol-bekci` | pazar · Telegram'dan "voltyol site nasıl" | `cikti/<tarih>-voltyol.md` — site ölçümü, haftalık commit'ler, sıradaki adım |

Her takım `takimlar/<takim>/` altında aynı dört dosyayla yaşar: `takim.md` (ne yapar), `kurallar.md`
(neye göre), `defter.md` (ne öğrendi), `durum.json` (nerede). Profilin `sirket/PROFIL.md`'de.

## Döngü

```
 sen (Telegram)  "başvurdum 3"                  Görev Zamanlayıcı 09:00 (hafta içi il-<tarih> ...)
        │                                                   │
 bin/telegram_dinle.py ── takım seç ──► kuyruk ◄── bin/gunluk.py --sabah
        │                                  │
        └──────────── bin/kos.py <takim> ◄─┘  (mesai 09–23 · koşu 2 USD / 15 dk · günde 4 koşu · köy 10 USD)
                           │ claude -p
                           ▼
                 takimlar/<takim>/cikti/*.md ── Stop hook ──► bin/bekci.py (kabul / red)
                           │
            bin/haber.py ──┴──► Telegram özeti        bin/dagitici.py ── 8+ puanlı ilan ──► basvuru-takip (ön yazı)
                           │
                    http://localhost:8765  (bin/koy.py — pikselli köy)
```

## Kurulum — 6 adım

Windows için komut komut ayrıntılı hâli: **[KURULUM.md](KURULUM.md)**. Windows'ta her şey **WSL (Ubuntu)** içinde çalışır;
`bin/kos.py` koşu kilidini POSIX `fcntl` ile kurar. macOS'ta `bin/zamanla.py` (launchd), Linux'ta cron kullanılır.

1. WSL'de `git clone … ~/ajan-koyu && cd ~/ajan-koyu` · `cp .env.example .env` — Telegram anahtarlarını doldur
2. `python3 bin/ayar.py` ve `python3 -m unittest discover -s tests` — iskelet ayakta mı
3. `ANAYASA.md` ve `sirket/PROFIL.md`'yi oku — profil güncel değilse düzelt
4. `python3 bin/agents_uret.py` ile `.claude/agents/<takim>.md` dosyalarını üret
5. Döngüyü kapat: `python3 bin/kos.py ilan-avcisi --kuru` → `python3 bin/kos.py ilan-avcisi --zorla` → `python3 bin/koy.py` ile köyü aç
6. Sürekli çalıştır: `python3 bin/zamanla_windows.py --kur` (Windows) · `python3 bin/zamanla.py --kur` (macOS) · Linux'ta cron

## Anahtarlar (`.env`)

| Anahtar | Ne için | Yoksa ne olur |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot gelen kutusu ve özetler (@BotFather) | dinleyici açılmaz, özet gitmez; takımlar yine saatinde koşar, çıktı köyde görünür |
| `TELEGRAM_CHAT_ID` | Yalnızca senin mesajların işlensin, özet yalnız sana gitsin | aynı |
| `OPENAI_API_KEY` | Bekçi — ayrı model ailesi (ANAYASA §3) | **yoksa ya da geçersizse** yedek yol `claude -p --model haiku`; karar "bekçi aynı aileden — uyarı" notuyla kaydedilir |
| `NVIDIA_API_KEY` | Ajanı Anthropic yerine NVIDIA'nın bedava modeliyle koşturmak ([docs/07](docs/07-farkli-model.md)) | hiçbir şey değişmez |
| `NIM_MODEL` | Koşacak NIM modeli (tool-use desteklemeli) | `saglayici: nim` koşusu atlanır |

Ajanlar `claude -p` ile, yani **Claude aboneliğinle** koşar; ayrıca API anahtarı gerekmez.

## Telegram'dan konuşmak

| Yazarsın | Ne olur |
|---|---|
| `ilan bak` · `fintech ilanı var mı` | İlan avcısı o an tarar (mesai içindeyse) |
| bir ilan linki | İlan avcısı ilanı CV'nle karşılaştırır: puan, eksikler, öne çıkarılacaklar |
| `başvurdum 3` | Postacı son ilan listesindeki 3 numarayı başvuru tablosuna ekler |
| `Getir'den mülakat geldi perşembe 14:00` | Postacı satırı günceller, mülakat hazırlık kartı yazar |
| `fikir: deprem` | Kâşif o konuda araştırma yapar |
| `voltyol site nasıl` | Bekçi siteyi ve repoyu kontrol eder |

## Komutlar

```bash
python3 bin/ayar.py                          # mesai, tavanlar, telegram hazır mı, .env var mı
python3 bin/kos.py <takim> [--kuru] [--zorla]   # bir takımı bir kez koştur (--kuru: hiçbir şeye dokunma)
python3 bin/dagitici.py [--kuru]             # zinciri kur, sırada bekleyen takımları koştur
python3 bin/gunluk.py --sabah | --aksam [--kuru]
python3 bin/telegram_oku.py --chat-id-bul    # TELEGRAM_CHAT_ID'yi bul
python3 bin/telegram_dinle.py                # olay tetiği
python3 bin/haber.py "deneme"                # Telegram'a deneme mesajı
python3 bin/koy.py                           # köy → http://localhost:8765
python3 bin/zamanla_windows.py --kuru | --kur | --durum | --kaldir | --simdi servis
python3 bin/zamanla.py --kur                 # macOS launchd
python3 bin/agents_uret.py [--check]
bin/takim-olustur.sh <yeni-takim>
python3 -m unittest discover -s tests
```

## Belgeler

| Dosya | Ne anlatır |
|---|---|
| [KURULUM.md](KURULUM.md) | Windows + WSL kurulumu, adım adım |
| [docs/01-nasil-calisir.md](docs/01-nasil-calisir.md) | Mimari: dört dosya, okuma sırası, `bin/kos.py` |
| [docs/02-dongu.md](docs/02-dongu.md) | Tetikler, dağıtıcı ve zincir, tavanlar |
| [docs/03-bekci.md](docs/03-bekci.md) | Bekçi: ön kontrol, ayrı kafa, red akışı |
| [docs/04-yetenekler.md](docs/04-yetenekler.md) | `skills/` |
| [docs/05-yeni-takim.md](docs/05-yeni-takim.md) | Yeni takım (yeni bina) açmak |
| [docs/06-sorun-giderme.md](docs/06-sorun-giderme.md) | Sık çıkan hatalar |
| [docs/07-farkli-model.md](docs/07-farkli-model.md) | NVIDIA NIM ile koşturmak |

> `docs/01`–`07` A Şirketi'nden geldi; mimari aynı olduğu için geçerlidir ama örneklerinde
> eski takım adları (`x-icerik`, `youtube-analiz`) geçebilir.

## Lisans

MIT — bkz. [LICENSE](LICENSE). Orijinal iskelet © A Şirketi (selmakcby), MIT.
