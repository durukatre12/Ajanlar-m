#!/usr/bin/env python3
"""Postane → Gmail köprüsü. Ajan değil, sürücü (ANAYASA §1 istisnası, patron kararı 2026-11-03).

Akış:
  1. `basvuru-takip` e-postayı **dosya** olarak yazar: `takimlar/basvuru-takip/cikti/eposta/*.md`
     (frontmatter: kime, konu, tur, ek). Ajan Gmail'e erişemez.
  2. `yukle()` yeni dosyaları Gmail **taslağı** yapar, her birine bir numara verir ve patrona
     Telegram'dan sorar. (`bin/kos.py`, basvuru-takip koşusu bitince çağırır.)
  3. Patron Telegram'dan `gönder <no>` yazınca `gonder()` Gmail'deki taslağı — patron Gmail'de
     düzelttiyse düzeltilmiş hâliyle — gönderir. `iptal <no>` taslağı siler. `taslaklar` listeler.

Anahtarlar `.env`'den: GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN (bir kez:
`python3 bin/gmail_yetki.py`). İsteğe bağlı GMAIL_CV_YOLU: `ek: cv` olan taslağa eklenecek PDF.

Kullanım:
  python3 bin/posta.py yukle | taslaklar | gonder <no> | iptal <no>
"""
import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from email import message_from_bytes, policy
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402

KOK = ayar.KOK
TAKIM = "basvuru-takip"
GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ANAHTARLAR = ("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN")
EPOSTA = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$")
# Doldurulmamış yer tutucu: [ad], [telefon], [ortak bağlantı] … — markdown bağlantısı [x](y) sayılmaz.
YER_TUTUCU = re.compile(r"\[[^\]\n]{1,40}\](?!\()")
TURLER = ("on-yazi", "tanistirma", "takip")


class PostaHatasi(Exception):
    pass


# --- dosyalar --------------------------------------------------------------

def eposta_dizini(kok=None):
    return Path(kok or KOK) / "takimlar" / TAKIM / "cikti" / "eposta"


def defter_yolu(kok=None):
    return Path(kok or KOK) / "takimlar" / TAKIM / "veri" / "eposta.json"


def defter_oku(kok=None):
    try:
        return json.loads(defter_yolu(kok).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"sayac": 0, "taslaklar": {}}


def defter_yaz(defter, kok=None):
    yol = defter_yolu(kok)
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(defter, ensure_ascii=False, indent=2), encoding="utf-8")


def taslak_oku(yol):
    """Ajanın yazdığı dosyayı çözer: {kime, konu, tur, ek, govde}. Bozuksa PostaHatasi."""
    metin = Path(yol).read_text(encoding="utf-8")
    fm, govde = ayar.frontmatter(metin)
    govde = govde.strip()
    kime = str(fm.get("kime") or "").strip()
    konu = str(fm.get("konu") or "").strip()
    tur = str(fm.get("tur") or "").strip()
    if not EPOSTA.match(kime):
        raise PostaHatasi(f"geçersiz alıcı: {kime or '(boş)'}")
    if not konu:
        raise PostaHatasi("konu boş")
    if not govde:
        raise PostaHatasi("gövde boş")
    if tur not in TURLER:
        raise PostaHatasi(f"bilinmeyen tür: {tur or '(boş)'}")
    return {"kime": kime, "konu": konu, "tur": tur,
            "ek": str(fm.get("ek") or "yok").strip().lower(), "govde": govde}


def mime_ham(taslak, cv_yolu=None):
    """Gmail API'nin istediği base64url RFC 2822 mesaj. Gönderen Gmail hesabının kendisidir."""
    mesaj = EmailMessage()
    mesaj["To"] = taslak["kime"]
    mesaj["Subject"] = taslak["konu"]
    mesaj.set_content(taslak["govde"])
    if taslak["ek"] == "cv":
        if not cv_yolu or not Path(cv_yolu).is_file():
            raise PostaHatasi("ek: cv istendi ama GMAIL_CV_YOLU yok ya da dosya bulunamadı")
        tip = (mimetypes.guess_type(str(cv_yolu))[0] or "application/pdf").split("/")
        mesaj.add_attachment(Path(cv_yolu).read_bytes(), maintype=tip[0], subtype=tip[1],
                             filename=Path(cv_yolu).name)
    return base64.urlsafe_b64encode(mesaj.as_bytes()).decode("ascii")


def govde_metni(ham_bayt):
    """Ham RFC 2822 mesajın düz metin gövdesi (ekli, base64 ya da QP kodlu olsa da)."""
    mesaj = message_from_bytes(ham_bayt, policy=policy.default)
    parca = mesaj.get_body(preferencelist=("plain",))
    return parca.get_content() if parca else ""


def yer_tutucular(metin):
    return sorted(set(YER_TUTUCU.findall(metin)))


# --- Gmail API (yalnız standart kütüphane) ---------------------------------

def _http(yontem, url, govde=None, basliklar=None, form=False):
    veri = None
    basliklar = dict(basliklar or {})
    if govde is not None:
        if form:
            veri = urllib.parse.urlencode(govde).encode()
            basliklar["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            veri = json.dumps(govde).encode()
            basliklar["Content-Type"] = "application/json"
    istek = urllib.request.Request(url, data=veri, headers=basliklar, method=yontem)
    try:
        with urllib.request.urlopen(istek, timeout=30) as yanit:
            ham = yanit.read()
    except urllib.error.HTTPError as exc:
        ayrinti = exc.read()[:200].decode(errors="ignore")
        if "invalid_grant" in ayrinti:
            raise PostaHatasi("Gmail izni düşmüş — python3 bin/gmail_yetki.py ile yenile "
                              "(uygulama 'Testing'deyse 'In production'a al)") from None
        raise PostaHatasi(f"Gmail {exc.code}: {ayrinti}") from None
    except urllib.error.URLError as exc:
        raise PostaHatasi(f"ağ hatası: {exc.reason}") from None
    return json.loads(ham) if ham else {}


class Gmail:
    """Küçük Gmail istemcisi. Testler `istek` yerine sahte bir fonksiyon verir."""

    def __init__(self, ortam=None, istek=_http):
        ortam = ortam if ortam is not None else os.environ
        eksik = [a for a in ANAHTARLAR if not ortam.get(a)]
        if eksik:
            raise PostaHatasi("Gmail bağlı değil — eksik: " + ", ".join(eksik)
                              + " (python3 bin/gmail_yetki.py)")
        self._ortam = ortam
        self._istek = istek
        self._erisim = None

    def _yetki(self):
        if not self._erisim:
            yanit = self._istek("POST", TOKEN_URL, {
                "client_id": self._ortam["GMAIL_CLIENT_ID"],
                "client_secret": self._ortam["GMAIL_CLIENT_SECRET"],
                "refresh_token": self._ortam["GMAIL_REFRESH_TOKEN"],
                "grant_type": "refresh_token"}, form=True)
            self._erisim = yanit.get("access_token")
            if not self._erisim:
                raise PostaHatasi("Gmail erişim jetonu alınamadı — gmail_yetki.py'yi yeniden çalıştır")
        return {"Authorization": f"Bearer {self._erisim}"}

    def taslak_ac(self, ham):
        return self._istek("POST", f"{GMAIL}/drafts", {"message": {"raw": ham}}, self._yetki())["id"]

    def taslak_metni(self, draft_id):
        yanit = self._istek("GET", f"{GMAIL}/drafts/{draft_id}?format=raw", None, self._yetki())
        ham = (yanit.get("message") or {}).get("raw") or ""
        return govde_metni(base64.urlsafe_b64decode(ham + "=" * (-len(ham) % 4)))

    def taslak_gonder(self, draft_id):
        return self._istek("POST", f"{GMAIL}/drafts/send", {"id": draft_id}, self._yetki())

    def taslak_sil(self, draft_id):
        self._istek("DELETE", f"{GMAIL}/drafts/{draft_id}", None, self._yetki())


def _gmail():
    ayar.ortam_yukle()
    return Gmail()


# --- işler -----------------------------------------------------------------

def _duyuru(no, kayit, uyari=""):
    tur = {"on-yazi": "ön yazılı başvuru", "tanistirma": "tanıştırma ricası", "takip": "takip"}
    satirlar = [f"✉️ Taslak #{no} · {tur.get(kayit['tur'], kayit['tur'])}",
                f"Kime: {kayit['kime']}", f"Konu: {kayit['konu']}"]
    if kayit.get("ek") == "cv":
        satirlar.append("Ek: CV")
    satirlar.append("")
    satirlar.append(kayit.get("onizleme", ""))
    if uyari:
        satirlar += ["", uyari]
    satirlar += ["", f"Gmail › Taslaklar'da duruyor; istersen orada düzelt.",
                 f"Göndermek için: gönder {no} · Silmek için: iptal {no}"]
    return "\n".join(satirlar)


def yukle(kok=None, gmail=None, haber=None):
    """Yeni taslak dosyalarını Gmail'e koyar ve patrona sorar. Yüklenen numaraların listesi döner."""
    dizin = eposta_dizini(kok)
    if not dizin.is_dir():
        return []
    defter = defter_oku(kok)
    yeniler = [y for y in sorted(dizin.glob("*.md")) if y.name not in defter["taslaklar"]]
    if not yeniler:
        return []
    try:
        gmail = gmail or _gmail()
    except PostaHatasi as exc:
        if haber:
            haber(f"📮 {len(yeniler)} e-posta taslağı hazır ama Gmail'e konamadı: {exc}")
        return []
    ayar.ortam_yukle()
    cv = os.environ.get("GMAIL_CV_YOLU")
    yuklenen = []
    for yol in yeniler:
        try:
            taslak = taslak_oku(yol)
            draft_id = gmail.taslak_ac(mime_ham(taslak, cv))
        except PostaHatasi as exc:
            defter["taslaklar"][yol.name] = {"durum": "hatali", "hata": str(exc)}
            if haber:
                haber(f"⚠️ {yol.name} Gmail'e konmadı: {exc}")
            continue
        defter["sayac"] += 1
        no = defter["sayac"]
        kayit = {"no": no, "draft_id": draft_id, "durum": "taslak", "kime": taslak["kime"],
                 "konu": taslak["konu"], "tur": taslak["tur"], "ek": taslak["ek"],
                 "onizleme": taslak["govde"][:400], "zaman": ayar.simdi_iso()}
        defter["taslaklar"][yol.name] = kayit
        yuklenen.append(no)
        if haber:
            eksik = yer_tutucular(taslak["govde"])
            uyari = (f"⚠️ Doldurulmamış yer: {', '.join(eksik)} — Gmail'de düzeltmeden gönderemezsin."
                     if eksik else "")
            haber(_duyuru(no, kayit, uyari))
    defter_yaz(defter, kok)
    return yuklenen


def _bul(defter, no):
    for ad, kayit in defter["taslaklar"].items():
        if kayit.get("no") == no:
            return ad, kayit
    return None, None


def gonder(no, kok=None, gmail=None):
    """Patron onayıyla gönderir. Gmail'deki **güncel** taslağı yer tutucuya karşı denetler."""
    defter = defter_oku(kok)
    ad, kayit = _bul(defter, no)
    if not kayit:
        return f"#{no} diye bir taslak yok. \"taslaklar\" yazarak listeyi görebilirsin."
    if kayit["durum"] != "taslak":
        return f"#{no} zaten {kayit['durum']}."
    try:
        gmail = gmail or _gmail()
        metin = gmail.taslak_metni(kayit["draft_id"])
        eksik = yer_tutucular(metin)
        if eksik:
            return f"#{no} gönderilmedi: doldurulmamış yer var ({', '.join(eksik)}). Gmail'de düzelt, sonra yine \"gönder {no}\"."
        gmail.taslak_gonder(kayit["draft_id"])
    except PostaHatasi as exc:
        return f"#{no} gönderilemedi: {exc}"
    kayit.update({"durum": "gönderildi", "gonderim": ayar.simdi_iso()})
    defter_yaz(defter, kok)
    return f"✅ #{no} gönderildi → {kayit['kime']} · {kayit['konu']}"


def iptal(no, kok=None, gmail=None):
    defter = defter_oku(kok)
    ad, kayit = _bul(defter, no)
    if not kayit:
        return f"#{no} diye bir taslak yok."
    if kayit["durum"] != "taslak":
        return f"#{no} zaten {kayit['durum']}."
    try:
        (gmail or _gmail()).taslak_sil(kayit["draft_id"])
    except PostaHatasi as exc:
        if "404" not in str(exc):        # Gmail'den elle silinmişse yine iptal say
            return f"#{no} silinemedi: {exc}"
    kayit["durum"] = "iptal"
    defter_yaz(defter, kok)
    return f"🗑 #{no} silindi."


def liste(kok=None):
    bekleyen = [k for k in defter_oku(kok)["taslaklar"].values() if k.get("durum") == "taslak"]
    if not bekleyen:
        return "Bekleyen e-posta taslağı yok."
    return "Bekleyen taslaklar:\n" + "\n".join(
        f"#{k['no']} · {k['kime']} · {k['konu']}" for k in sorted(bekleyen, key=lambda k: k["no"]))


KOMUT = re.compile(r"^\s*(g[öo]nder|iptal)\s+#?(\d+)\s*$|^\s*taslaklar\s*$", re.IGNORECASE)


def komut_mu(metin):
    """Telegram mesajı posta komutu mu? (komut, no) ya da None. Ajan çağrılmaz; sürücü yanıtlar."""
    eslesme = KOMUT.match(metin or "")
    if not eslesme:
        return None
    if eslesme.group(1) is None:
        return ("taslaklar", None)
    komut = "gonder" if eslesme.group(1).lower().startswith("g") else "iptal"
    return (komut, int(eslesme.group(2)))


def komutu_isle(metin, kok=None, gmail=None):
    komut, no = komut_mu(metin)
    if komut == "taslaklar":
        return liste(kok)
    return (gonder if komut == "gonder" else iptal)(no, kok=kok, gmail=gmail)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "yukle":
        import haber
        print("yüklendi:", yukle(haber=haber.gonder) or "yeni taslak yok")
    elif argv[0] == "taslaklar":
        print(liste())
    elif argv[0] in ("gonder", "iptal") and len(argv) == 2 and argv[1].isdigit():
        print((gonder if argv[0] == "gonder" else iptal)(int(argv[1])))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
