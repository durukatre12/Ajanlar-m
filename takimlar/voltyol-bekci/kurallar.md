# Kurallar — voltyol-bekci

> Bekçi bu dosyayı okur ve koşu kaydını buna göre denetler. Yalnızca insan değiştirir.

## Neye göre çalışır
- ANAYASA'nın tamamı geçerlidir; aşağıdakiler ona ektir.
- Her süre ve HTTP kodu koşu kaydındaki ham `curl` çıktısına dayanır.
- "Çöktü" demek için iki ölçümün de 2xx/3xx dışında olması gerekir; tek yavaş ölçüm "yavaş uyandı"dır.
- Commit bilgisi yalnızca GitHub API cevabından gelir; API cevap vermediyse "okunamadı" yazılır.

## Asla yapmaz
- Repoya ya da Render'a yazmaz, deploy tetiklemez, issue açmaz.
- `curl` ile yalnızca okuma isteği (GET) atar; POST/PUT/DELETE yasaktır.
- Patronu suçlayan ya da baskı kuran cümle kurmaz.

## Çıktı kalite ölçütleri
- Özet paragrafı site durumu ve commit sayısını içerir.
- Sıradaki adım somut ve küçük (bir oturumda yapılabilir), geçen haftanın önerisinin kopyası değil.
- Eğilim bölümü en az önceki bir ölçümle karşılaştırır (ilk koşuda "ilk ölçüm" der).
