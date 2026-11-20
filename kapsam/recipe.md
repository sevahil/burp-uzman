# Kapsam kabul reçetesi

Tarama bitti demek uygulama tam test edildi demek degildir. Asagidaki maddeler kapanmadan rapor "tamamlandi" olarak sunulmaz.

## A. Yuzey

- [ ] Musteriden beklenen ekran, endpoint, HTTP metodu ve onemli parametre listesi alindi.
- [ ] Target > Site map ile liste karsilastirildi; eksikler isaretlendi.
- [ ] Eksik istekler tarayicidan/Proxy'den yakalanip "Scan" ile hedefli tarandi (Burp manual scanner testing is akisi); gerekirse insertion point elle belirlendi.
- [ ] API icin OpenAPI/Swagger/GraphQL semasi alindi; her operasyon icin en az bir gecerli istek Proxy'den gecirildi.
- [ ] SPA/JS agirlikli yuzeyde gezinti tarayici ile elle yapildi.

## B. Kimlik ve rol

- [ ] Anonim kullanici icin ayri tarama gorevi.
- [ ] Her rol ve her tenant icin ayri Application login ile ayri tarama gorevi (`auth/recipe.md`).
- [ ] Roller arasi erisim karsilastirmasi: dusuk yetkili oturumla yuksek yetkili isteklerin tekrari (Autorize veya elle Repeater).
- [ ] Tarama boyunca oturum acik kaldi (Dashboard'da login hatasi/401 yigilmasi yok).

## C. Manuel kapsam (tarayicinin yapisal olarak goremedigi)

- [ ] Is mantigi: fiyat/miktar/durum manipulasyonu, adim atlama, tekrar oynatma.
- [ ] IDOR/BOLA: nesne kimlikleri baska kullanici ve baska tenant ile denendi.
- [ ] Yetki yukseltme: istemci tarafi rol alanlari, gizli yonetici endpoint'leri.
- [ ] Yaris kosulu: tek kullanimlik kod, kupon, bakiye islemleri.
- [ ] Cok adimli akislar: kayit, sifre sifirlama, odeme, dosya yukleme.
- [ ] Dosya yukleme ve indirme: tur/boyut/yol kontrolleri.

## D. Calisma durumu

- [ ] Dashboard'da gorev hatalari, atlanan istekler, zaman asimi ve baglanti hatalari incelendi.
- [ ] Crawl'in tamamlandigi ve limit nedeniyle kesilmedigi dogrulandi.
- [ ] Hata veren kisimlar yeniden tarandi veya raporda kapsam disi olarak belirtildi.

## E. Bulgu kaniti

- [ ] Her bulgu icin istek/yanit kaniti saklandi.
- [ ] `tentative` guvenli bulgular elle dogrulandi veya raporda belirsiz olarak isaretlendi.
- [ ] BCheck sinyalleri (yansima, DNS etkilesimi, surum ifsasi) tek basina etki olarak raporlanmadi.
- [ ] Raporda test edilen ve edilemeyen alanlar acikca yazildi.
