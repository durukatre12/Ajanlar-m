"""`haber.ek_haberler`: çıktıdaki `## LinkedIn mesajları` bölümü patrona ayrı mesaj olarak gider."""
import sys
import tempfile
import time
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "bin"))
import haber  # noqa: E402

CIKTI = """# Başvuru — Trendyol

Trendyol Operations Data Analyst satırı açıldı.

## Tablo
| # | Şirket |
|---|---|

## LinkedIn mesajları
Trendyol — Operations Data Analyst · başvuru 2026-11-03

1) Bağlantı notu (≤200 karakter):
Merhaba [ad], İTÜ mezunuyum.
"""


class EkHaberTesti(unittest.TestCase):
    def _kok(self, d, metin):
        dizin = Path(d) / "takimlar" / "basvuru-takip" / "cikti"
        dizin.mkdir(parents=True)
        (dizin / "2026-11-03-bv-1.md").write_text(metin, encoding="utf-8")
        return Path(d)

    def test_linkedin_bolumu_ayri_gider(self):
        with tempfile.TemporaryDirectory() as d:
            ekler = haber.ek_haberler("basvuru-takip", time.time() - 5, kok=self._kok(d, CIKTI))
        self.assertEqual(len(ekler), 1)
        self.assertTrue(ekler[0].startswith("📮 LinkedIn mesajları"))
        self.assertIn("Merhaba [ad]", ekler[0])
        self.assertNotIn("| # |", ekler[0])

    def test_bolum_yoksa_ek_yok(self):
        with tempfile.TemporaryDirectory() as d:
            kok = self._kok(d, CIKTI.split("## LinkedIn")[0])
            self.assertEqual(haber.ek_haberler("basvuru-takip", time.time() - 5, kok=kok), [])


if __name__ == "__main__":
    unittest.main()
