#!/usr/bin/env python3
"""Şirketlerin kendi ilan sistemlerinden (Lever) açık ilanları çeker — sürücü, ajan değil.

LinkedIn giriş istiyor, Kariyer.net arama sayfası otomatik ziyaretçiye 403 veriyor. Lever ise
şirketlerin ilanlarını giriş istemeyen, herkese açık bir servisle yayınlıyor:
`https://api.lever.co/v0/postings/<kimlik>?mode=json`. Bu betik `takimlar/ilan-avcisi/kaynaklar.json`'daki
şirketleri çeker, Türkiye/remote + veri/analist/risk geçen ve kıdemli olmayan ilanları ayıklar ve
`takimlar/ilan-avcisi/veri/kaynak-ilanlar.md`'ye yazar. İlan avcısı koşusunun başında okunur.

Yapay zekâ çağrısı yok, ücretsiz. `bin/kos.py`, ilan-avcisi koşusundan hemen önce çağırır.

    python3 bin/ilan_cek.py          # çek ve yaz
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402

KOK = ayar.KOK
TAKIM = "ilan-avcisi"
LEVER = "https://api.lever.co/v0/postings/{kimlik}?mode=json"

KONUM = re.compile(r"t[üu]rk|istanbul|İstanbul|remote|uzaktan", re.IGNORECASE)
ROL = re.compile(r"\bdata\b|veri|analyst|analist|analytics|analitik|\bbi\b|business intelligence|"
                 r"insight|risk|fraud|dolandırıcılık|\bgis\b|reporting|raporlama", re.IGNORECASE)
KIDEMLI = re.compile(r"senior|\bsr\b|lead|manager|head|principal|staff|director|kıdemli|müdür|"
                     r"yönetici|\bvp\b|chief", re.IGNORECASE)


def kaynaklar_yolu(kok=None):
    return Path(kok or KOK) / "takimlar" / TAKIM / "kaynaklar.json"


def cikti_yolu(kok=None):
    return Path(kok or KOK) / "takimlar" / TAKIM / "veri" / "kaynak-ilanlar.md"


def _getir(url):
    istek = urllib.request.Request(url, headers={"User-Agent": "ajan-koyu/1.0"})
    with urllib.request.urlopen(istek, timeout=20) as yanit:
        return json.loads(yanit.read())


def _konum(ilan):
    kat = ilan.get("categories") or {}
    parcalar = [kat.get("location") or ""] + list(kat.get("allLocations") or [])
    parcalar.append(ilan.get("workplaceType") or "")
    return " / ".join(p for p in dict.fromkeys(parcalar) if p)


def uygun_mu(ilan):
    """(uygun, sebep). Türkiye/remote + veri-analist rolü + kıdemli değil."""
    baslik = ilan.get("text") or ""
    if not KONUM.search(_konum(ilan)):
        return False, "konum"
    if not ROL.search(baslik + " " + ((ilan.get("categories") or {}).get("team") or "")):
        return False, "rol"
    if KIDEMLI.search(baslik):
        return False, "kıdem"
    return True, ""


def lever_cek(sirket, kimlik, getir=_getir):
    """(uygunlar, toplam, hata). uygunlar: [{sirket, baslik, konum, tarih, link, ekip}]."""
    try:
        ilanlar = getir(LEVER.format(kimlik=kimlik))
    except urllib.error.HTTPError as exc:
        return [], 0, ("kimlik yanlış olabilir (404)" if exc.code == 404 else f"HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return [], 0, f"erişilemedi: {getattr(exc, 'reason', exc)}"
    if not isinstance(ilanlar, list):
        return [], 0, "beklenmeyen yanıt"
    uygunlar = []
    for ilan in ilanlar:
        if not uygun_mu(ilan)[0]:
            continue
        zaman = ilan.get("createdAt")
        tarih = (datetime.fromtimestamp(zaman / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                 if isinstance(zaman, (int, float)) else "tarih bilinmiyor")
        uygunlar.append({"sirket": sirket, "baslik": " ".join((ilan.get("text") or "").split()),
                         "konum": _konum(ilan), "tarih": tarih, "link": ilan.get("hostedUrl") or "",
                         "ekip": (ilan.get("categories") or {}).get("team") or ""})
    return uygunlar, len(ilanlar), None


def rapor(sonuclar, sayfalar, simdi):
    satirlar = [f"# Kaynak ilanlar — {simdi:%Y-%m-%d %H:%M}", "",
                "> `bin/ilan_cek.py` yazdı (sürücü). Lever ilanları şirketin kendi ilan servisinden çekildi: "
                "bağlantılar canlı, tarih ilanın yayın tarihidir. Ajan bunları açılmış sayar ('açıldı (API)').", ""]
    ilanlar = sorted((i for s in sonuclar for i in s["uygunlar"]), key=lambda i: i["tarih"], reverse=True)
    satirlar.append(f"## Uygun ilanlar ({len(ilanlar)})")
    satirlar += [f"- {i['tarih']} · **{i['sirket']} — {i['baslik']}** · {i['konum']}"
                 + (f" · {i['ekip']}" if i["ekip"] else "") + f" · {i['link']}" for i in ilanlar] or ["- (yok)"]
    satirlar += ["", "## Kaynak durumu"]
    for s in sonuclar:
        durum = s["hata"] or f"{s['toplam']} açık ilan, {len(s['uygunlar'])} uygun"
        satirlar.append(f"- {s['sirket']} (lever/{s['kimlik']}): {durum}")
    satirlar += ["", "## Ajanın açacağı sayfalar",
                 "Bu sayfaları WebFetch ile aç; veri/analist/risk ilanlarını bul, ilanın kendi bağlantısını aç."]
    satirlar += [f"- {p['sirket']}: {p['url']}" for p in sayfalar] or ["- (yok)"]
    return "\n".join(satirlar) + "\n"


def cek(kok=None, getir=_getir, simdi=None):
    """Kaynakları çekip `veri/kaynak-ilanlar.md`'yi yazar. Uygun ilan sayısını döner."""
    try:
        ayarlar = json.loads(kaynaklar_yolu(kok).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    sonuclar = []
    for kaynak in ayarlar.get("lever") or []:
        uygunlar, toplam, hata = lever_cek(kaynak["sirket"], kaynak["kimlik"], getir)
        sonuclar.append({**kaynak, "uygunlar": uygunlar, "toplam": toplam, "hata": hata})
    yol = cikti_yolu(kok)
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(rapor(sonuclar, ayarlar.get("sayfalar") or [], simdi or datetime.now()), encoding="utf-8")
    return sum(len(s["uygunlar"]) for s in sonuclar)


if __name__ == "__main__":
    adet = cek()
    print(f"{adet} uygun ilan → {cikti_yolu().relative_to(KOK)}")
