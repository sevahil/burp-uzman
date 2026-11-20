# Kimlik dogrulamali tarama reçetesi

Scanner icin birinci yol Application login'dir. Session handling rules ve makro, tarayici trafigine sinirli uygulanir: PortSwigger Sessions dokumani crawl ve crawl kaynakli audit isteklerinde yalnizca "Set a specific cookie or parameter value" ve "Invoke a Burp extension" eylemleri iceren kurallarin uygulandigini belirtir; bu kisit tum tarama turlerine genellenmez ve 2026.2.1 davranisi kabulde gozlenir. Makro tek basina taramayi kimlik dogrulamali yapmaz.

## Application login

1. Scan baslatma diyalogu > Application login.
2. Basit giris formu: kullanici adi ve parola ekle. Karmasik akis (cok adim, MFA yok, CSRF, JS): kaydedilmis login dizisi (recorded login sequence) ekle ve Burp tarayicisi ile kaydet.
3. Her rol ve her tenant icin ayri login tanimi olustur; adini rolle yaz.
4. Kimlik bilgileri yalnizca Burp project dosyasinda ve musteriden alinan test hesaplarinda tutulur; bu repoya, export edilen config'e veya rapora yazilmaz.

## Dogrulama

- [ ] Kaydedilmis login dizisi yeniden oynatildi ve korumali bir sayfaya erisildi.
- [ ] Taramanin ilk dakikalarinda ve ortasinda Dashboard'da login hatasi yok.
- [ ] Oturum suresi doldurularak (cikis veya bekleme) yeniden giris calistigi gozlendi.
- [ ] Logout, oturum sonlandirma veya yikici islem yollari crawl kapsamindan cikarildi.
- [ ] Giris yapilabilmesi yetkilendirmenin test edildigi anlamina gelmez; rol karsilastirmasi icin `kapsam/recipe.md` B bolumu.

## Makro (yalnizca dar durum)

Yalnizca sabit bir cerez veya parametre degerinin her istege yazilmasi gerekiyorsa: Settings > Sessions > Session handling rules > Add, eylem "Set a specific cookie or parameter value". Kapsam Burp tool scope ve suite scope ile sinirli tutulur.
