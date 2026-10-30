#!/usr/bin/env python3
"""Köy — ajanların pikselli görünümü. Yerel bir web sayfası; yalnız bu bilgisayardan açılır.

Kullanım:
  python3 bin/koy.py             # http://localhost:8765 — tarayıcıda aç
  KOY_PORT=9000 python3 bin/koy.py

Köy yalnızca OKUR: `takimlar/*/durum.json`, `takimlar/*/cikti/*.md`, `takimlar/*/.calisiyor`,
bugünkü koşu kayıtlarındaki maliyet. Tek yazma işi "şimdi çalıştır" düğmesidir: takımın kuyruğuna
`el-<zaman>` maddesi düşürür ve ANAYASA §4 izin veriyorsa (`dagitici.tetik_karari`) takımı başlatır —
yani terminalde `python3 bin/kos.py <takim>` yazmakla aynı yoldan geçer, tavanları aşamaz.

Sunucu varsayılan olarak 127.0.0.1'e bağlanır; ağdaki başka cihazlar köyü göremez.
WSL'de Windows tarayıcısı açamazsa: KOY_HOST=0.0.0.0 python3 bin/koy.py
"""
import json
import os
import re
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402
import dagitici  # noqa: E402
import gunluk  # noqa: E402
import haber  # noqa: E402

KOK = ayar.KOK
SAYFA = KOK / "koy" / "index.html"
GUNLER = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
BINA = {"ilan-avcisi": "Gözetleme kulesi", "basvuru-takip": "Postane",
        "fikir-atolyesi": "Fikir atölyesi", "voltyol-bekci": "Şarj istasyonu"}
DOSYA_ADI = re.compile(r"^[\w.\-]+\.md$")
CIKTI_SINIRI = 12


def plan_metni(takim):
    """gunluk.HAFTALIK'tan insan okuyacağı plan: "Pzt–Cum 09:00" gibi."""
    for madde in gunluk.HAFTALIK:
        if madde["takim"] == takim:
            gunler = madde["gunler"]
            if gunler == [0, 1, 2, 3, 4]:
                metin = "Hafta içi"
            else:
                metin = ", ".join(GUNLER[g] for g in gunler)
            return f"{metin} · sabah {ayar.MESAI_BASLANGIC:02d}:00 · {madde['not']}"
    return "yalnızca Telegram'dan ya da elle"


def _ciktilar(takim):
    dizin = KOK / "takimlar" / takim / "cikti"
    if not dizin.is_dir():
        return []
    dosyalar = sorted(dizin.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:CIKTI_SINIRI]
    return [{"dosya": p.name, "zaman": datetime.fromtimestamp(p.stat().st_mtime).astimezone()
             .isoformat(timespec="seconds"), "ozet": haber.ozet_paragrafi(p)[:400]} for p in dosyalar]


def takim_durumu(takim, simdi):
    fm = ayar.takim_bilgisi(takim) or {}
    durum = ayar.durum_oku(takim)
    kuyruk = [o for o in (durum.get("kuyruk") or []) if isinstance(o, dict)]
    kossun, sebep = dagitici.tetik_karari(KOK, takim, simdi)
    calisiyor = (KOK / "takimlar" / takim / ".calisiyor").exists()
    return {"id": takim, "ad": haber.AD.get(takim, takim), "bina": BINA.get(takim, takim),
            "rozet": haber.ROZET.get(takim, "•"), "gorev": fm.get("description", ""),
            "plan": plan_metni(takim), "son_kosu": durum.get("son_kosu"),
            "son_sonuc": durum.get("son_sonuc"), "calisiyor": calisiyor,
            "bekleyen": [o for o in kuyruk if o.get("durum") == "bekliyor"][-5:],
            "bekci": (durum.get("bekci") or {}).get("son_karar"),
            "bugun": dagitici.bugunku_kosu_sayisi(KOK, takim, simdi.strftime("%Y-%m-%d")),
            "tetik": {"kossun": kossun, "sebep": sebep}, "ciktilar": _ciktilar(takim)}


def koy_durumu():
    simdi = datetime.now().astimezone()
    return {"simdi": simdi.isoformat(timespec="seconds"), "mesai": ayar.mesaide_mi(simdi),
            "mesai_metni": ayar.MESAI_METNI,
            "maliyet": round(dagitici.gunluk_maliyet(KOK, simdi.strftime("%Y-%m-%d")), 3),
            "tavan": ayar.GUNLUK_MALIYET_TAVANI_USD, "kosu_tavani": ayar.GUNLUK_KOSU_TAVANI,
            "telegram": ayar.telegram_hazir_mi(),
            "takimlar": [takim_durumu(t, simdi) for t in dagitici.takimlar(KOK)]}


def simdi_calistir(takim):
    """Köydeki düğme: kuyruğa `el-<zaman>` yaz, §4 izin verirse başlat. (kod, mesaj)."""
    if takim not in dagitici.takimlar(KOK):
        return 404, "böyle bir takım yok"
    simdi = datetime.now().astimezone()
    id_ = f"el-{simdi:%Y%m%d-%H%M%S}"
    dagitici.kuyruga_yaz(KOK, takim, id_, "köydeki 'şimdi çalıştır' düğmesi")
    kossun, sebep = dagitici.tetik_karari(KOK, takim, simdi)
    if (KOK / "takimlar" / takim / ".calisiyor").exists():
        return 200, f"{id_} kuyruğa yazıldı; takım zaten çalışıyor, sıradaki koşuda alınır."
    if not kossun:
        return 200, f"{id_} kuyruğa yazıldı ama şimdi başlamadı: {sebep}"
    dagitici._kostur(KOK, takim)
    return 200, f"{id_} başladı — bitince Telegram'a özet gelir."


class Isleyici(BaseHTTPRequestHandler):
    def _yanit(self, kod, govde, tur="application/json; charset=utf-8"):
        veri = govde if isinstance(govde, bytes) else (
            json.dumps(govde, ensure_ascii=False).encode("utf-8") if not isinstance(govde, str)
            else govde.encode("utf-8"))
        self.send_response(kod)
        self.send_header("Content-Type", tur)
        self.send_header("Content-Length", str(len(veri)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(veri)

    def do_GET(self):  # noqa: N802
        yol = self.path.split("?", 1)[0]
        if yol in ("/", "/index.html"):
            return self._yanit(200, SAYFA.read_bytes(), "text/html; charset=utf-8")
        if yol == "/api/koy":
            return self._yanit(200, koy_durumu())
        eslesme = re.fullmatch(r"/api/cikti/([a-z0-9-]+)/([^/]+)", yol)
        if eslesme:
            takim, dosya = eslesme.groups()
            hedef = KOK / "takimlar" / takim / "cikti" / dosya
            if takim in dagitici.takimlar(KOK) and DOSYA_ADI.match(dosya) and hedef.is_file():
                return self._yanit(200, hedef.read_text(encoding="utf-8"), "text/plain; charset=utf-8")
            return self._yanit(404, {"hata": "dosya yok"})
        return self._yanit(404, {"hata": "yok"})

    def do_POST(self):  # noqa: N802
        eslesme = re.fullmatch(r"/api/kos/([a-z0-9-]+)", self.path)
        if not eslesme:
            return self._yanit(404, {"hata": "yok"})
        kod, mesaj = simdi_calistir(eslesme.group(1))
        return self._yanit(kod, {"mesaj": mesaj})

    def log_message(self, *_):  # sessiz — her 5 sn'lik yoklamayı loglamaya gerek yok
        return


def main(argv):
    ayar.ortam_yukle()
    host = os.environ.get("KOY_HOST", "127.0.0.1")
    port = int(os.environ.get("KOY_PORT", "8765"))
    sunucu = ThreadingHTTPServer((host, port), Isleyici)
    print(f"Ajan Köyü açık → http://localhost:{port}  (kapatmak için Ctrl-C)", flush=True)
    try:
        sunucu.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
