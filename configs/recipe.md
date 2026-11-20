# Tarama yapilandirmasi reçetesi

Burp 2026.2.1 Pro. Config adlari PortSwigger "built-in configurations" sayfasindan birebir alindi. Ayarlar GUI'de kurulur, JSON elle yazilmaz.

## Siralama (listede ustten alta; cakisan ayarda ALTTAKI kazanir)

1. `Crawl and Audit - Deep`
2. `Crawl strategy - most complete`
3. `Audit coverage - maximum`

Scan baslatma diyalogu > Scan configuration > Select from library > siralamayi bu sirayla kur.

## Hassas / uretim hedefi icin degisim

PortSwigger dokumanina gore `Audit checks - all except time-based detection methods` yalnizca zaman tabanli yontemleri kapatir, yikici olabilecek (intrusive) aktif kontrolleri kapatmaz. Intrusive aktif kontrolleri kapatanlar:

- `Audit checks - medium active`: intrusive aktif kontrolleri kapatir; medium aktif kontroller calisir.
- `Audit checks - light active`: medium ve intrusive aktif kontrolleri kapatir; pasif, light aktif ve JavaScript analizi kalir.
- `Audit checks - passive`: aktif kontrol yok.

Hassas hedef: 3. satir yerine `Audit checks - medium active`; cok hassas hedef: `Audit checks - light active`. Her ikisine ek olarak `Crawl limit - 60 minutes` ve gerekirse `Audit checks - all except time-based detection methods` eklenir. Ozel BCheck'ler bu config secimlerinden bagimsiz calisir; hassas hedefte BCheck sec/cikar karari scan diyalogunda ayrica verilir.

## Varsayilan ACIK OLMAYANLAR

- `Never stop crawl due to application errors`
- `Never stop audit due to application errors`

Yalnizca hedef sahibi hata altinda tarama surmesini yazili onayladiysa eklenir.

## Butce ve durdurma (her hedefte once belirlenir)

- Scan diyalogundaki Resource pool: eszamanli istek ve istekler arasi gecikme, hedef sahibinin kabul ettigi degerlere gore (menu adi GUI'de dogrulanacak).
- Durdurma kosulu: hedefte 5xx orani artisi, yavaslama veya hedef sahibinin istegi; gorev Dashboard'dan duraklatilir.
- Yikici islev iceren yollar (silme, odeme, e-posta gonderme, kayit olusturma) crawl kapsamindan cikarilir.

## Efektif ayar kontrolu

1. Uc config scan diyalogunda yukaridaki sirayla secilir.
2. Cakisan ayarlar her config Settings > Configuration library'de acilarak elle karsilastirilir; etkin birlesik degerleri gosteren bir GUI yolu dokumanda yoktur ve 2026.2.1'de aranir. Bulunamazsa karsilastirma elle yapilir.
3. Birlesimi "en genis kapsam" sayma; gozlenen degerler kabul listesine (`kabul-windows.md`) yazilir.

## Export

1. Settings > Configuration library > export edilecek config'leri sec > Export > `configs/exported/` altina `.json` olarak kaydet.
2. Export edilen dosyada kullanici adi, parola, token veya cerez yok olmali; `python3 -I dogrula.py` sir kontrolu yapar.
3. Export edilen dosya 2026.2.1'de yeniden Import edilip ayarlarin ayni geldigi dogrulanir.
4. `python3 -I dogrula.py --manifest-yaz` ile manifest guncellenir.

Kimlik bilgisi iceren config'ler `configs/private/` altinda tutulur; bu dizin versiyonlanmaz.
