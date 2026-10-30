# KURULUM — Windows'ta sıfırdan altı adım

Ajan Köyü Windows'ta **WSL (Ubuntu)** içinde çalışır: ajanları koşturan `bin/kos.py` POSIX `fcntl`
kilidi kullanır ve betikler Linux kabuğu bekler. Görev Zamanlayıcı (Windows) saat gelince WSL'i
kendisi açar; senin her sabah terminal açman gerekmez. macOS'taysan adım 0'ı atla, adım 6'da
`python3 bin/zamanla.py --kur` kullan.

## Adım 0 · WSL, Python, Claude Code (bir kez, ~15 dk)

**PowerShell'i yönetici olarak aç** ve:

```powershell
wsl --install -d Ubuntu
```

Bilgisayarı yeniden başlat. Başlat menüsünden **Ubuntu**'yu aç, kullanıcı adı ve parola belirle.
Bundan sonraki her komut bu **Ubuntu terminalinde** yazılır.

```bash
sudo apt update && sudo apt install -y python3 git curl
python3 --version        # 3.9 ve üstü
```

**Claude Code'u WSL'in içine kur.** Windows'a kurduğun Claude Code buradan görünmez; WSL kendi
Linux'udur ve `claude` komutunu kendi içinde arar:

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
claude                   # bir kez aç, hesabınla giriş yap, sonra /exit
```

Kurulum komutu değiştiyse güncel hâli: [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code).
Giriş yapılmamış bir `claude` ile her koşu ilk adımda ölür.

---

## Adım 1 · Klon ve anahtarlar

Repoyu **Linux tarafına** (`~`) klonla, `C:\` altına (`/mnt/c/...`) değil — orada dosya işlemleri
çok yavaştır ve kilit güvenilir çalışmaz.

```bash
cd ~
git clone https://github.com/durukatre12/ajan-koyu.git
cd ajan-koyu
cp .env.example .env
head -1 .gitignore     # ".env" — anahtar dosyası hiçbir zaman commit'e girmez
nano .env              # ya da: code .   (VS Code + "WSL" eklentisi)
```

5 anahtar var, hiçbiri zorunlu değil:

| Anahtar | Nereden alınır | Boşsa |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram'da @BotFather → `/newbot` | Telegram'dan iş veremezsin, özet gelmez; plan yine saatinde koşar |
| `TELEGRAM_CHAT_ID` | aşağıdaki `--chat-id-bul` | aynı |
| `OPENAI_API_KEY` | platform.openai.com | **yoksa ya da geçersizse** bekçi Haiku'ya düşer, kararına "bekçi aynı aileden — uyarı" notu eklenir |
| `NVIDIA_API_KEY` | build.nvidia.com → model kartı → Get API Key | hiçbir şey değişmez ([docs/07](docs/07-farkli-model.md)) |
| `NIM_MODEL` | tool-use destekleyen bir NIM modeli | `saglayici: nim` koşusu atlanır |

**Telegram botu 30 saniyede:** @BotFather → `/newbot` → bota bir ad ver (ör. "Duru Köy Botu") → verdiği
token'ı `TELEGRAM_BOT_TOKEN`'a yaz. Sonra kendi botuna herhangi bir mesaj at ve:

```bash
python3 bin/telegram_oku.py --chat-id-bul
python3 bin/haber.py "Ajan Köyü kuruldu"     # telefonuna bu mesaj gelmeli
```

Çıkan sayıyı `TELEGRAM_CHAT_ID`'ye yaz. Bu filtre olmadan bota yazan herkesin mesajı işlenirdi;
bu yüzden yalnız o chat id'den gelen mesajlar okunur ve özetler yalnız oraya gider.

> **`.env` her zaman kabuğu ezer.** Kabuğunda aynı adla eski bir değer duruyorsa bile koşu
> `.env`'deki değeri kullanır (`bin/ayar.py` → `ortam_yukle`).

---

## Adım 2 · Ayakta mı

```bash
python3 bin/ayar.py
python3 -m unittest discover -s tests
```

Birinci komut mesai penceresini, tavanları ve Telegram'ın hazır olup olmadığını basar. Sayılar tek
yerdedir: `bin/ayar.py`. İkinci komut reponun kendi testleridir (ağ yok, `claude` çağrısı yok, para yok).
Hepsi geçmeden devam etme.

---

## Adım 3 · ANAYASA ve PROFİL

```bash
cat ANAYASA.md
cat sirket/PROFIL.md
```

ANAYASA beş madde: gönder düğmesi insanın · kaynaksız iddia yok · bekçi ayrı kafa · her koşunun tavanı var ·
defter ajanın, kural insanın. `sirket/PROFIL.md` ajanların seni tanıdığı tek yerdir — CV'n değişince
burayı güncelle (iletişim bilgilerini buraya yazma). İkisi de **insanındır**: ajan okur, değiştiremez.

---

## Adım 4 · Ajan dosyalarını üret

```bash
python3 bin/agents_uret.py            # .claude/agents/<takim>.md + .claude/settings.json (bekçi hook) yazılır
head -8 .claude/agents/ilan-avcisi.md # ilk satır ajanın kimliğidir
```

İlk satır: **"Sen `ilan-avcisi` ajanısın. Ajan Köyü'nde bir çalışansın ve bir yapay zekâ ajanısın. Mesleğin: …"**

Yeni bir bina (takım) açmak istersen:

```bash
bin/takim-olustur.sh <yeni-takim>
```

> Yeni takım `skills: []` ile gelir. **`takim.md`'de `skills:` alanını doldur (en az bir
> yetenek), yoksa testler kırmızı** — `tests/test_skills.py` her takımdan en az bir yetenek
> bekler. Sonra `python3 bin/agents_uret.py` koş. Telegram yönlendirmesi için `bin/telegram_dinle.py`
> içindeki `YONLENDIRME` tablosuna, sabah planı için `bin/gunluk.py` içindeki `HAFTALIK` listesine bir satır ekle.

---

## Adım 5 · İlk koşu ve köy

Önce kuru koşu — `claude` çağrılmaz, hiçbir dosyaya yazılmaz:

```bash
python3 bin/kos.py ilan-avcisi --kuru
```

Sonra gerçeği (`--zorla` mesai dışında da koşturur; birkaç dakika sürer):

```bash
python3 bin/kos.py voltyol-bekci --zorla      # en hızlı ve en ucuz takım — ilk deneme için ideal
python3 bin/kos.py ilan-avcisi --zorla
```

Köyü aç ve Windows tarayıcında **http://localhost:8765** adresine git:

```bash
python3 bin/koy.py
```

Tarayıcı açamazsa: `KOY_HOST=0.0.0.0 python3 bin/koy.py`.

Telegram'dan dene (dinleyici açıkken: `python3 bin/telegram_dinle.py`): bota `voltyol site nasıl` yaz.

---

## Adım 6 · Sürekli çalıştır (Windows Görev Zamanlayıcı)

```bash
python3 bin/zamanla_windows.py --kuru     # ne kurulacağını gör
python3 bin/zamanla_windows.py --kur      # dört görev: sabah, saatlik, aksam, servis
python3 bin/zamanla_windows.py --simdi servis   # köyü ve dinleyiciyi şimdi aç
python3 bin/zamanla_windows.py --durum
```

| Görev | Ne zaman | Ne yapar |
|---|---|---|
| `\AjanKoyu\sabah` | her gün 09:00 | günün planını kuyruğa düşürür (hafta içi ilan, pzt başvuru, cmt fikir, paz Voltyol) + dağıtıcı |
| `\AjanKoyu\saatlik` | 10:05–22:05 saatte bir | sırada bekleyen işleri alır |
| `\AjanKoyu\aksam` | her gün 22:00 | günün denetim raporu (`sirket-log/rapor/`) |
| `\AjanKoyu\servis` | Windows'a giriş yapınca | köy (localhost:8765) + Telegram dinleyici |

Bilgisayar 09:00'da uykudaysa görev açılınca koşar. Görevler pencere açmadan (`conhost --headless`)
çalışır. Kaldırmak için: `python3 bin/zamanla_windows.py --kaldir`.

---

## GitHub'a göndermeden önce

Koşular `takimlar/*/durum.json` dosyalarını günceller. Kendi kopyanı push'lamadan önce bu değişiklikleri
commit'e katmak istemiyorsan:

```bash
git restore takimlar/*/durum.json
```

`kosu/`, `cikti/`, `veri/` (başvuru tablon dahil) zaten `.gitignore`'da — yalnız bu bilgisayarda kalır.
