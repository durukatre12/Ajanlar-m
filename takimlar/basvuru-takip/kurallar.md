# Kurallar — basvuru-takip

> Bekçi bu dosyayı okur ve koşu kaydını buna göre denetler. Yalnızca insan değiştirir.

## Neye göre çalışır
- ANAYASA'nın tamamı geçerlidir; aşağıdakiler ona ektir.
- Tabloya yalnızca patronun "başvurdum" dediği başvurular girer. Durum değişikliği yalnızca patronun haberiyle olur;
  tek istisna 21+ gün cevapsız başvurunun `sessiz`e çekilmesidir.
- "Başvurdum <numara>" ilan listesinde bulunamazsa satır açılmaz, soru sorulur.
- Taslaklarda profildeki gerçek proje ve sayılar kullanılır; profilde olmayan deneyim, sertifika ya da sayı yazılmaz.
- Takip e-postası 4–6 cümle; ön yazı 150–250 kelime. İlan İngilizceyse taslak İngilizce, Türkçeyse Türkçe.

## Asla yapmaz
- E-posta göndermez, başvuru formu doldurmaz, LinkedIn'de mesaj atmaz. E-posta yalnız `cikti/eposta/` dosyası
  olarak yazılır (patron kararı 2026-11-03); Gmail'e koymak ve göndermek `bin/posta.py` + patron onayının işidir.
- Yeni başvuruda LinkedIn **mesaj taslağı** ve kişi **araması bağlantısı** yazılabilir (patron kararı 2026-11-03);
  kişi adı toplanmaz, `[ad]` yer tutucusu kalır, gönderen patrondur.
- `kime:` alanına yalnız ilan metninde yazan ya da patronun Telegram notunda verdiği adres girer.
- Başka takımın klasörüne yazmaz (ilan-avcisi çıktısını yalnızca okur).
- Telefon, adres gibi kişisel bilgiyi taslağa yazmaz.

## Çıktı kalite ölçütleri
- Özet paragrafı ne değiştiğini tek bakışta söyler ("Getir satırı mülakat'a çekildi, perşembe 14:00").
- Her taslakta konu satırı var ve ilana özgü en az bir cümle var (genel şablon kokan taslak red sebebidir).
- Tablo her çıktıda tutarlı: aynı şirket-pozisyon iki satırda görünmez.
