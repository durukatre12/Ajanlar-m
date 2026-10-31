"""Ajan Köyü'ne özgü parçalar: haber (Telegram özeti), köy sunucusu, Windows zamanlayıcısı.

Ağ yok, claude çağrısı yok, schtasks çağrısı yok.
"""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "bin"))
import gunluk  # noqa: E402
import haber  # noqa: E402
import koy  # noqa: E402
import telegram_dinle  # noqa: E402
import zamanla_windows as zw  # noqa: E402

CIKTI = """# İlanlar — 2026-10-30

Bugün 6 yeni ilan var. En iyisi Örnek Fintech — Junior Risk Analyst.
İkinci satır da özete dahil.

## Bugünün öne çıkanları
1. ...
"""


class HaberTesti(unittest.TestCase):
    def test_ozet_paragrafi_basliktan_sonraki_ilk_paragraf(self):
        with tempfile.TemporaryDirectory() as d:
            yol = Path(d) / "a.md"
            yol.write_text(CIKTI, encoding="utf-8")
            self.assertEqual(haber.ozet_paragrafi(yol),
                             "Bugün 6 yeni ilan var. En iyisi Örnek Fintech — Junior Risk Analyst. "
                             "İkinci satır da özete dahil.")

    def test_kosu_haberi_yeni_ciktiyi_ozetler(self):
        with tempfile.TemporaryDirectory() as d:
            kok = Path(d)
            dizin = kok / "takimlar/ilan-avcisi/cikti"
            dizin.mkdir(parents=True)
            baslangic = time.time()
            (dizin / "2026-10-30-ilanlar.md").write_text(CIKTI, encoding="utf-8")
            metin = haber.kosu_haberi("ilan-avcisi", "tamam", baslangic, kok)
        self.assertIn("İlan Avcısı", metin)
        self.assertIn("Bugün 6 yeni ilan var", metin)
        self.assertIn("takimlar/ilan-avcisi/cikti/2026-10-30-ilanlar.md", metin)

    def test_red_haberi_ciktiyi_gondermez(self):
        metin = haber.kosu_haberi("ilan-avcisi", "red", time.time(), "/yok")
        self.assertIn("reddetti", metin)

    def test_anahtar_yoksa_gondermez_ve_cokmez(self):
        with mock.patch.object(haber.ayar, "ortam_yukle", return_value={}), \
             mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""}):
            self.assertFalse(haber.gonder("deneme"))


class KoyTesti(unittest.TestCase):
    def test_koy_durumu_dort_takimi_dondurur(self):
        veri = koy.koy_durumu()
        self.assertEqual(sorted(t["id"] for t in veri["takimlar"]),
                         ["basvuru-takip", "fikir-atolyesi", "ilan-avcisi", "voltyol-bekci"])
        json.dumps(veri, ensure_ascii=False)   # JSON'a çevrilebilir olmalı

    def test_plan_metni_gunluk_planla_ayni(self):
        self.assertTrue(koy.plan_metni("ilan-avcisi").startswith("Hafta içi"))
        self.assertTrue(koy.plan_metni("fikir-atolyesi").startswith("Cmt"))

    def test_bilinmeyen_takim_calistirilmaz(self):
        kod, _ = koy.simdi_calistir("olmayan-takim")
        self.assertEqual(kod, 404)

    def test_her_takimin_binasi_ve_plani_var(self):
        planli = {m["takim"] for m in gunluk.HAFTALIK}
        for takim in ("ilan-avcisi", "basvuru-takip", "fikir-atolyesi", "voltyol-bekci"):
            with self.subTest(takim=takim):
                self.assertIn(takim, koy.BINA)
                self.assertIn(takim, planli)
                self.assertIn(takim, telegram_dinle.KUYRUK_ONEKI)

    def test_sayfa_var(self):
        self.assertIn("Ajan Köyü", (KOK / "koy/index.html").read_text(encoding="utf-8"))


class BekciCiktiTesti(unittest.TestCase):
    def test_bekci_kosudan_sonra_yazilan_ciktiyi_gorur(self):
        import bekci
        with tempfile.TemporaryDirectory() as d:
            kok = Path(d)
            (kok / "takimlar/fikir-atolyesi/cikti").mkdir(parents=True)
            (kok / "takimlar/fikir-atolyesi/kosu").mkdir(parents=True)
            from datetime import datetime, timedelta
            kosu = kok / "takimlar/fikir-atolyesi/kosu" / (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d-%H%M.md")
            kosu.write_text("kayıt", encoding="utf-8")
            eski = kok / "takimlar/fikir-atolyesi/cikti/eski.md"
            eski.write_text("ESKI", encoding="utf-8")
            os.utime(eski, (time.time() - 86400, time.time() - 86400))
            (kok / "takimlar/fikir-atolyesi/cikti/yeni.md").write_text("YENI çıktı", encoding="utf-8")
            metin = bekci.kosu_ciktilari(kok, "fikir-atolyesi", kosu)
        self.assertIn("YENI çıktı", metin)
        self.assertNotIn("ESKI", metin)

    def test_bekci_istemi_cikti_ve_baglanti_kuralini_tasir(self):
        import bekci
        istem = bekci._istem("A", "K", "kayıt", "### cikti/x.md\nmetin")
        self.assertIn("<ciktilar>", istem)
        self.assertIn("## Açılan bağlantılar", istem)


class WindowsZamanlayiciTesti(unittest.TestCase):
    def test_saatlik_gorev_tekrarlar_ve_kacani_telafi_eder(self):
        saatlik = next(g for g in zw.GOREVLER if g["ad"] == "saatlik")
        xml = zw.gorev_xml(saatlik)
        self.assertIn("<StartWhenAvailable>true</StartWhenAvailable>", xml)
        self.assertIn("<Interval>PT1H</Interval>", xml)
        self.assertIn("conhost.exe", xml)
        self.assertIn("--headless wsl.exe", xml)

    def test_servis_oturum_acilinca_baslar_ve_suresiz(self):
        servis = next(g for g in zw.GOREVLER if g["ad"] == "servis")
        xml = zw.gorev_xml(servis)
        self.assertIn("<LogonTrigger>", xml)
        self.assertIn("<ExecutionTimeLimit>PT0S</ExecutionTimeLimit>", xml)

    def test_oturum_tetigi_kullaniciya_baglanir(self):
        servis = next(g for g in zw.GOREVLER if g["ad"] == "servis")
        xml = zw.gorev_xml(servis, kullanici="desktop-x\\dell")
        self.assertIn("<LogonTrigger><Enabled>true</Enabled><UserId>desktop-x\\dell</UserId></LogonTrigger>", xml)
        self.assertIn('<Principal id="Author"><UserId>desktop-x\\dell</UserId>', xml)

    def test_servis_baslangic_betigi_gizli_calisir(self):
        vbs = zw.servis_vbs()
        self.assertIn("wsl-tetik.sh servis", vbs)
        self.assertTrue(vbs.rstrip().endswith(", 0, False"), "pencere açmamalı (0) ve beklememeli")
        self.assertNotIn("servis", [g["ad"] for g in zw.TAKVIM], "servis Görev Zamanlayıcı'ya yazılmaz")

    def test_tetik_betigi_var_ve_dort_komutu_bilir(self):
        betik = (KOK / "bin/wsl-tetik.sh").read_text(encoding="utf-8")
        for komut in ("sabah)", "saatlik)", "aksam)", "servis)"):
            self.assertIn(komut, betik)

    def test_wsl_disinda_kurulum_yapmaz(self):
        with mock.patch.object(zw, "wsl_mi", return_value=False), \
             mock.patch.object(zw, "_schtasks") as sahte:
            self.assertEqual(zw.main(["--kur"]), 1)
        sahte.assert_not_called()


if __name__ == "__main__":
    unittest.main()
