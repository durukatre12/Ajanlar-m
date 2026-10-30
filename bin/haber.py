#!/usr/bin/env python3
"""Patrona Telegram'dan haber — köyün dışarıya açılan tek kapısı (ANAYASA §1).

Ajan mesaj atmaz; koşu bittikten sonra sürücü (`bin/kos.py`) bu modülle çıktının özet paragrafını
patronun kendi sohbetine gönderir. Başka hiçbir alıcı yoktur: chat id `.env`'deki TELEGRAM_CHAT_ID'dir.

Kullanım (elle deneme): python3 bin/haber.py "deneme mesajı"
Anahtarlar yoksa sessizce hiçbir şey yapmaz. Hata koşuyu asla düşürmez.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402

ROZET = {"ilan-avcisi": "🔭", "basvuru-takip": "📮", "fikir-atolyesi": "💡", "voltyol-bekci": "⚡"}
AD = {"ilan-avcisi": "İlan Avcısı", "basvuru-takip": "Postacı",
      "fikir-atolyesi": "Kâşif", "voltyol-bekci": "Bekçi"}
TELEGRAM_SINIRI = 3500


def gonder(metin):
    """Patronun sohbetine düz metin gönderir. Gönderildiyse True."""
    ayar.ortam_yukle()
    if not ayar.telegram_hazir_mi():
        return False
    import telegram_oku  # döngüsel içe aktarmayı önlemek için geç yüklenir
    try:
        telegram_oku._api(os.environ["TELEGRAM_BOT_TOKEN"], "sendMessage",
                          chat_id=os.environ["TELEGRAM_CHAT_ID"], text=metin[:TELEGRAM_SINIRI],
                          disable_web_page_preview="true")
        return True
    except Exception as exc:  # noqa: BLE001 — haber yolu koşuyu bağlamaz
        print(f"haber gitmedi: {type(exc).__name__}", file=sys.stderr)
        return False


def ozet_paragrafi(yol):
    """Çıktı dosyasında başlıktan sonraki ilk paragraf (ANAYASA/AJAN-KIMLIGI sözleşmesi)."""
    try:
        satirlar = Path(yol).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    paragraf, basladi = [], False
    for satir in satirlar:
        s = satir.strip()
        if not basladi:
            if s.startswith("#") or not s:
                continue
            basladi = True
        if basladi:
            if not s or s.startswith("#"):
                break
            paragraf.append(s)
    return " ".join(paragraf)


def yeni_cikti(takim, baslangic_ts, kok=None):
    """Koşu başladıktan sonra yazılmış en yeni çıktı dosyası; yoksa None."""
    dizin = Path(kok or ayar.KOK) / "takimlar" / takim / "cikti"
    adaylar = [p for p in dizin.glob("*.md") if p.stat().st_mtime >= baslangic_ts - 1] if dizin.is_dir() else []
    return max(adaylar, key=lambda p: p.stat().st_mtime) if adaylar else None


def kosu_haberi(takim, sonuc, baslangic_ts, kok=None):
    """Koşu sonu haberinin metni. Çıktı yoksa sonucu tek satırla söyler."""
    bas = f"{ROZET.get(takim, '•')} {AD.get(takim, takim)}"
    cikti = yeni_cikti(takim, baslangic_ts, kok)
    if sonuc == "red":
        return f"{bas} — bekçi bu koşuyu reddetti; çıktı önüne gelmeyecek. Sebep durum.json'da."
    if sonuc in ("hata", "atlandi") or cikti is None:
        return f"{bas} — koşu {sonuc}; yeni çıktı yok."
    ozet = ozet_paragrafi(cikti) or "(özet paragrafı yok)"
    goreli = cikti.relative_to(Path(kok or ayar.KOK))
    return f"{bas}\n{ozet}\n\n📄 {goreli}\n🏠 köyde aç: http://localhost:8765"


if __name__ == "__main__":
    print("gönderildi" if gonder(" ".join(sys.argv[1:]) or "Ajan Köyü: deneme") else
          "gönderilmedi — .env'de TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID var mı?")
