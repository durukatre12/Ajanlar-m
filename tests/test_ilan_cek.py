"""`bin/ilan_cek.py`: Lever ilan servisinden çek, ayıkla, `veri/kaynak-ilanlar.md` yaz. Ağ yok."""
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "bin"))
import ilan_cek  # noqa: E402
import telegram_dinle  # noqa: E402


def ilan(baslik, konum="İstanbul, Turkey", ekip="Analytics", zaman=1793600000000):
    return {"text": baslik, "categories": {"location": konum, "team": ekip},
            "createdAt": zaman, "hostedUrl": f"https://jobs.lever.co/x/{abs(hash(baslik))}"}


ILANLAR = [ilan("Data Analyst"), ilan("Senior Data Analyst"), ilan("Fraud Analyst", ekip="Risk"),
           ilan("iOS Developer", ekip="Mobile"), ilan("Data Analyst", konum="Barcelona, Spain"),
           ilan("Jr. Business Intelligence Analyst", konum="Remote")]


def sahte_getir(url):
    if "/yok?" in url:
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    return ILANLAR


class IlanCekTesti(unittest.TestCase):
    def test_ayiklama(self):
        uygunlar, toplam, hata = ilan_cek.lever_cek("X", "x", sahte_getir)
        self.assertIsNone(hata)
        self.assertEqual(toplam, 6)
        self.assertEqual(sorted(u["baslik"] for u in uygunlar),
                         ["Data Analyst", "Fraud Analyst", "Jr. Business Intelligence Analyst"])
        self.assertTrue(all(u["tarih"].startswith("2026") for u in uygunlar))

    def test_yanlis_kimlik_raporlanir(self):
        self.assertEqual(ilan_cek.lever_cek("Y", "yok", sahte_getir)[2], "kimlik yanlış olabilir (404)")

    def test_rapor_yazilir(self):
        with tempfile.TemporaryDirectory() as d:
            kok = Path(d)
            yol = ilan_cek.kaynaklar_yolu(kok)
            yol.parent.mkdir(parents=True)
            yol.write_text(json.dumps({"lever": [{"sirket": "X", "kimlik": "x"}, {"sirket": "Y", "kimlik": "yok"}],
                                       "sayfalar": [{"sirket": "Gratis", "url": "https://ornek/gratis"}]}),
                           encoding="utf-8")
            self.assertEqual(ilan_cek.cek(kok, sahte_getir, datetime(2026, 11, 3, 9)), 3)
            metin = ilan_cek.cikti_yolu(kok).read_text(encoding="utf-8")
        self.assertIn("## Uygun ilanlar (3)", metin)
        self.assertIn("**X — Fraud Analyst**", metin)
        self.assertIn("Y (lever/yok): kimlik yanlış olabilir", metin)
        self.assertIn("- Gratis: https://ornek/gratis", metin)
        self.assertNotIn("Senior", metin)

    def test_repodaki_kaynaklar_gecerli(self):
        ayar = json.loads(ilan_cek.kaynaklar_yolu().read_text(encoding="utf-8"))
        self.assertTrue(all({"sirket", "kimlik"} <= set(k) for k in ayar["lever"]))
        self.assertTrue(all(s["url"].startswith("https://") for s in ayar["sayfalar"]))


class UzunMetinTesti(unittest.TestCase):
    def test_uzun_ilan_metni_kesilmeden_saklanir(self):
        metin = "ilan " + "Data Analyst aranıyor. SQL, Python, Power BI. " * 20
        with tempfile.TemporaryDirectory() as d:
            yol = telegram_dinle.ilan_metnini_sakla(Path(d), {"update_id": 7, "not": metin})
            kayit = (Path(d) / "takimlar/ilan-avcisi/veri/ilan-metni-7.txt").read_text(encoding="utf-8")
        self.assertEqual(yol, "tam metin: veri/ilan-metni-7.txt")
        self.assertEqual(kayit, metin)


if __name__ == "__main__":
    unittest.main()
