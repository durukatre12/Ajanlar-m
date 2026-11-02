"""`bin/posta.py`: e-posta dosyası → Gmail taslağı → patron onayıyla gönderim. Ağ yok; sahte Gmail."""
import base64
import sys
import tempfile
import unittest
from email import message_from_bytes, policy
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "bin"))
import posta  # noqa: E402
import telegram_dinle  # noqa: E402

ORTAM = {"GMAIL_CLIENT_ID": "i", "GMAIL_CLIENT_SECRET": "s", "GMAIL_REFRESH_TOKEN": "r"}


class SahteIstek:
    """Gmail API'yi taklit eder: taslakları bellekte tutar, gönderilenleri sayar."""

    def __init__(self):
        self.taslaklar, self.gonderilen, self.silinen, self.cagri = {}, [], [], []

    def __call__(self, yontem, url, govde=None, basliklar=None, form=False):
        self.cagri.append((yontem, url))
        if url == posta.TOKEN_URL:
            return {"access_token": "erisim"}
        if yontem == "POST" and url.endswith("/drafts"):
            draft_id = f"d{len(self.taslaklar) + 1}"
            self.taslaklar[draft_id] = govde["message"]["raw"]
            return {"id": draft_id}
        if yontem == "GET" and "/drafts/" in url:
            return {"message": {"raw": self.taslaklar[url.split("/drafts/")[1].split("?")[0]]}}
        if url.endswith("/drafts/send"):
            self.gonderilen.append(govde["id"])
            return {"id": "m1"}
        if yontem == "DELETE":
            self.silinen.append(url.rsplit("/", 1)[1])
            return {}
        raise AssertionError(url)

    def duzelt(self, draft_id, eski, yeni):
        """Patron Gmail'de taslağı düzeltti."""
        ham = base64.urlsafe_b64decode(self.taslaklar[draft_id] + "==")
        mesaj = message_from_bytes(ham, policy=policy.default)
        mesaj.set_content(mesaj.get_body(("plain",)).get_content().replace(eski, yeni))
        self.taslaklar[draft_id] = base64.urlsafe_b64encode(mesaj.as_bytes()).decode()


def dosya(kok, ad, kime="ik@ornek.com", konu="Data Analyst başvurusu", tur="on-yazi", ek="yok",
          govde="Merhaba,\n\nBaşvurumu iletiyorum.\n\nDuru Katre Sarnıç"):
    dizin = posta.eposta_dizini(kok)
    dizin.mkdir(parents=True, exist_ok=True)
    (dizin / ad).write_text(f"---\nkime: {kime}\nkonu: {konu}\ntur: {tur}\nek: {ek}\n---\n{govde}\n",
                            encoding="utf-8")


class PostaTesti(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.kok = Path(self._tmp.name)
        self.istek = SahteIstek()
        self.gmail = posta.Gmail(ortam=ORTAM, istek=self.istek)
        self.haberler = []

    def tearDown(self):
        self._tmp.cleanup()

    def yukle(self):
        return posta.yukle(kok=self.kok, gmail=self.gmail, haber=self.haberler.append)

    def test_anahtar_yoksa_gmail_kurulmaz(self):
        with self.assertRaises(posta.PostaHatasi):
            posta.Gmail(ortam={}, istek=self.istek)

    def test_yeni_dosya_taslak_olur_numara_alir_ve_patrona_sorulur(self):
        dosya(self.kok, "a.md")
        self.assertEqual(self.yukle(), [1])
        self.assertEqual(len(self.istek.taslaklar), 1)
        self.assertIn("gönder 1", self.haberler[-1])
        self.assertEqual(self.istek.gonderilen, [], "onaysız gönderim olmamalı")

    def test_ayni_dosya_ikinci_kez_yuklenmez(self):
        dosya(self.kok, "a.md")
        self.yukle()
        self.assertEqual(self.yukle(), [])
        self.assertEqual(len(self.istek.taslaklar), 1)

    def test_gecersiz_alici_taslak_olmaz(self):
        dosya(self.kok, "a.md", kime="isim-yok")
        self.assertEqual(self.yukle(), [])
        self.assertIn("geçersiz alıcı", self.haberler[-1])

    def test_cv_eki_yolu_yoksa_taslak_olmaz(self):
        dosya(self.kok, "a.md", ek="cv")
        self.assertEqual(self.yukle(), [])

    def test_cv_eki_eklenir(self):
        cv = self.kok / "CV.pdf"
        cv.write_bytes(b"%PDF-1.4 sahte")
        ham = posta.mime_ham({"kime": "a@b.co", "konu": "k", "govde": "g", "ek": "cv"}, cv)
        mesaj = message_from_bytes(base64.urlsafe_b64decode(ham), policy=policy.default)
        self.assertEqual([p.get_filename() for p in mesaj.iter_attachments()], ["CV.pdf"])

    def test_gonder_onaylayinca_gider_ve_ikinci_kez_gitmez(self):
        dosya(self.kok, "a.md")
        self.yukle()
        self.assertIn("gönderildi", posta.gonder(1, kok=self.kok, gmail=self.gmail))
        self.assertEqual(self.istek.gonderilen, ["d1"])
        self.assertIn("zaten", posta.gonder(1, kok=self.kok, gmail=self.gmail))
        self.assertEqual(self.istek.gonderilen, ["d1"])

    def test_yer_tutuculu_taslak_gonderilmez_duzeltilince_gider(self):
        dosya(self.kok, "a.md", tur="tanistirma", govde="Merhaba [ad],\n\nBir rica…\n\nDuru")
        self.yukle()
        self.assertIn("Doldurulmamış", self.haberler[-1])
        self.assertIn("gönderilmedi", posta.gonder(1, kok=self.kok, gmail=self.gmail))
        self.assertEqual(self.istek.gonderilen, [])
        self.istek.duzelt("d1", "[ad]", "Senanur")          # patron Gmail'de düzeltti
        self.assertIn("gönderildi", posta.gonder(1, kok=self.kok, gmail=self.gmail))

    def test_markdown_baglantisi_yer_tutucu_sayilmaz(self):
        self.assertEqual(posta.yer_tutucular("Bkz. [GitHub](https://github.com/durukatre12)"), [])
        self.assertEqual(posta.yer_tutucular("Merhaba [ad], [telefon]"), ["[ad]", "[telefon]"])

    def test_iptal_taslagi_siler(self):
        dosya(self.kok, "a.md")
        self.yukle()
        self.assertIn("silindi", posta.iptal(1, kok=self.kok, gmail=self.gmail))
        self.assertEqual(self.istek.silinen, ["d1"])
        self.assertIn("zaten iptal", posta.gonder(1, kok=self.kok, gmail=self.gmail))

    def test_bilinmeyen_numara(self):
        self.assertIn("yok", posta.gonder(9, kok=self.kok, gmail=self.gmail))

    def test_liste(self):
        dosya(self.kok, "a.md")
        dosya(self.kok, "b.md", kime="x@y.com")
        self.yukle()
        posta.gonder(1, kok=self.kok, gmail=self.gmail)
        self.assertEqual(posta.liste(self.kok), "Bekleyen taslaklar:\n#2 · x@y.com · Data Analyst başvurusu")


class KomutTesti(unittest.TestCase):
    def test_komutlar(self):
        self.assertEqual(posta.komut_mu("gönder 3"), ("gonder", 3))
        self.assertEqual(posta.komut_mu("Gonder #12"), ("gonder", 12))
        self.assertEqual(posta.komut_mu("iptal 4"), ("iptal", 4))
        self.assertEqual(posta.komut_mu("taslaklar"), ("taslaklar", None))
        for metin in ("gönder", "başvurdum 3", "ilan bak", "bunu gönder 3 lütfen", ""):
            self.assertIsNone(posta.komut_mu(metin), metin)

    def test_tanistir_postaciya_gider(self):
        mesaj = {"metin": "tanıştır senanur@ornek.com 2", "linkler": []}
        self.assertEqual(telegram_dinle.takim_sec(mesaj), "basvuru-takip")

    def test_gonder_komutu_ajan_kosturmaz(self):
        with tempfile.TemporaryDirectory() as d:
            haberler = []
            etiket, _ = telegram_dinle.isle_mesaj(Path(d), {"metin": "gönder 5", "update_id": 1},
                                                  haber=haberler.append)
        self.assertEqual(etiket, "posta")
        self.assertIn("#5 diye bir taslak yok", haberler[0])


if __name__ == "__main__":
    unittest.main()
