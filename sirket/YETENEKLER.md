# YETENEKLER — Ajan Köyü

> Dört takımın kullandığı beş yeteneğin kataloğu.
> Bir yetenek, o işin nasıl yapılacağını adım adım, şablonuyla ve kontrol listesiyle anlatan tek dosyadır:
> `skills/<ad>/SKILL.md`. Ajan koşu adımında **yalnızca ilgili yeteneği** okur.

## Neden bu dosyalar var — üç gerekçe

1. **Token sorununu çözmek.** Bir işin nasıl yapılacağını her koşuda baştan anlatmak pahalıdır ve her
   seferinde biraz farklı çıkar. Yetenek dosyası bir kez yazılır, ajan koşuda sadece ilgili adımda okur.
2. **Ajanın hatırlaması.** Ajanın hafızası yok; oturum kapanınca her şey gider. `defter.md` dünü,
   `skills/` ise **nasıl yapıldığını** hatırlar. Yazmadığın şey olmamıştır.
3. **Ajanın gelişmesi.** Her yetenek dosyasının sonunda `## Öğrenilenler` bölümü var. Ajan koşuda aldığı
   veriyle **kendini geliştirir**: dersi `defter.md`'ye yazar, aynı ders üç koşuda tekrar ederse yeteneğin
   `## Öğrenilenler` bölümüne öneri bırakır. Kararı patron verir.

## Katalog

| Takım | Yetenek | Ne işe yarar | Kaynak | Lisans |
|---|---|---|---|---|
| `ilan-avcisi`, `basvuru-takip` | [`ilan-eslestirme`](../skills/ilan-eslestirme/SKILL.md) | Arama planı, 10 üzerinden puan tablosu, eleme kuralları, tek ilan analizi. | kendi üretimimiz | MIT |
| `ilan-avcisi`, `fikir-atolyesi` | [`kaynak-dogrulama`](../skills/kaynak-dogrulama/SKILL.md) | Her iddiayı birincil kaynağa açıp ✅/🟡/⛔ ile sınıflar. | A Şirketi'nden uyarlandı | MIT |
| `basvuru-takip` | [`basvuru-yazismasi`](../skills/basvuru-yazismasi/SKILL.md) | Takip e-postası, ön yazı ve mülakat kartı taslakları — gönderilmez. | kendi üretimimiz | MIT |
| `fikir-atolyesi` | [`pazar-arastirmasi`](../skills/pazar-arastirmasi/SKILL.md) | Türkiye ↔ global araştırma planı, fikir kartı, favori seçimi. | kendi üretimimiz | MIT |
| `voltyol-bekci` | [`site-saglik-kontrolu`](../skills/site-saglik-kontrolu/SKILL.md) | Uyanma süresini ayıran site ölçümü, commit API'si, eğilim. | kendi üretimimiz | MIT |

**Toplam 5 yetenek, 4 takım.**

## Nereden aldık
İskelet, sürücüler ve `kaynak-dogrulama` yeteneği [selmakcby/a-sirketi](https://github.com/selmakcby/a-sirketi)
(MIT) reposundan gelir. Diğer dört yetenek Ajan Köyü için yazıldı.

## Nasıl çalışır (teknik)
- Kaynak: `takimlar/<takim>/takim.md` frontmatter'ındaki `skills: [ad1, ad2]` alanı.
- `bin/agents_uret.py` bu alanı **şirket alanı** sayar (agent frontmatter'ına sızmaz) ve önsöze
  `Yeteneklerin: ...` satırını ekler.
- `bin/kos.py` `istem()` aynı satırı koşu istemine koyar — `python3 bin/kos.py <takim> --kuru` ile görülür.
- Bağın bütünlüğünü `tests/test_skills.py` denetler.
