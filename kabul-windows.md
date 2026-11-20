# Windows VM kabul listesi (Burp Suite Professional 2026.2.1)

Bu liste Linux tarafindaki `kur.sh` kontrolunden ayridir. Linux kontrolu dosyalarin statik gecerliligini kanitlar; asagidakiler Burp'te elle yapilir ve sonuclari isaretlenir. Isaretlenmemis madde "dogrulanmadi" demektir.

## 1. Surum

- [x] Help > About: v2026.2.1. (2026-11-20 ekran goruntusu: Burp Suite Professional v2026.2.1)
- [ ] Aktif oturumda Burp AI kullanilmiyor.

## 2. BCheck import

- [x] Extensions > Custom scan checks > Import: Burp alt klasorlere inmiyor; her alt klasorun ICINE girip dosyalar secilir (passive 3, host-path 5, oob 1, active 1). Ayni dosyayi tekrar import etmek tabloda kopya satir uretir.
- [x] 10 dosyanin 10'u hatasiz yuklendi (2026-11-20). Ilk turda 2 dosya reddedildi: actuator regex `[[]` Java'da gecersiz; `matches` sagindaki backtick kabul edilmedi. Ikisi duzeltildi, linter kurali eklendi. Hatalar Event log'a degil tabloda kirmizi ucgene ve dosya duzenleyicisinin Errors alanina yazilir.
- [ ] Tum kontroller scan baslatma diyalogunda secilebilir gorunuyor.

## 3. BCheck calisma testi (kontrol basina pozitif ve negatif)

Kontrol listesi 10 dosyadir; her biri icin kendi test hedefinde:

- [ ] csp-missing-or-weak: CSP'siz HTML sayfada tetikler; CSP'li sayfada tetiklemez.
- [ ] debug-mode-exposed: bilinen debug sayfasi imzasinda tetikler; normal sayfada tetiklemez.
- [ ] js-source-map-referenced: sourceMappingURL iceren JS'de tetikler; icermeyende tetiklemez.
- [ ] exposed-env-file, exposed-git-repository, exposed-actuator-env, exposed-phpinfo, exposed-apache-server-status: hedefte dosya varken tetikler; yoksa, soft-404 donen hedefte ve giris sayfasi donen hedefte tetiklemez.
- [ ] header-ssrf-collaborator: kendi kontrol ettigin zayif test uygulamasinda HTTP ve DNS etkilesimi dogru derecelenir; Collaborator erisilebilir.
- [ ] special-characters-reflected: yansitan ve kodlayan sayfalarda dogru davranir.
- [ ] Her kontrolun yaptigi istekler Logger veya Dashboard'dan incelendi. Host kontrolleri yalnizca GET, govdesiz ve Cookie/Authorization basliksiz gider; beklenmeyen yikici istek yok.
- [ ] Insertion point kontrolleri (header-ssrf-collaborator, special-characters-reflected) Burp'un yerlesik aktif taramasi gibi tabani yeniden gonderir; DSL'de metoda gore kosullanamaz. Taban istek POST/DELETE olan yollar crawl kapsaminin disinda tutulur (`configs/recipe.md`) ve bu kontrollerin istekleri Logger'dan incelenir.
- [x] `status_code is "200"` kabul edildi; `matches` sagindaki backtick reddedildi ve `in` ile degistirildi (`in`'in solunda backtick kabul edildi).
- [ ] Istek yuku olculdu: host basina yaklasik 5, her genel insertion point icin 1, her header insertion point icin 1 ek istek.
- [ ] Ayni bulgularda Burp'un kendi kontrolleriyle ortusme gozlendi; gereksiz olan kontrol repodan cikarilir.

## 4. Scan yapilandirmasi

- [ ] `configs/recipe.md` siralamasi kuruldu; etkin ayarlar okundu ve kayda gecirildi.
- [ ] Export edilen JSON Import ile geri yuklendi, ayarlar ayni geldi.

## 5. Kimlik dogrulama

- [ ] `auth/recipe.md` dogrulama maddeleri test hesabiyla kapatildi.

## 6. BApp'ler

- [ ] Kullanilacak her BApp 2026.2.1'de yuklendi, hata gunlugu temiz.
- [ ] `bapps.md` kayit alanlari dolduruldu.

## 7. Argus aktarimi

- [ ] Kucuk bir test taramasi Burp raporu olarak (XML) disa aktarildi.
- [ ] Argus'ta `import-scan <rapor.xml> --tool burp-pro` hatasiz calisti ve bulgular beklenen sayida geldi.
- [ ] Rapor dosyasi musteri verisi iceriyorsa repoya veya Codex'e verilmedi.
