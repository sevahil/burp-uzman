# BApp listesi

BApp Store listesinde adlari ve son guncelleme tarihleri 2026-11-20'de dogrulandi. Hicbiri varsayilan acik degildir; hedefe gore secilir. Her eklenti Burp 2026.2.1'de yuklenip bir test hedefinde calistirilmadan musteri isinde kullanilmaz (`kabul-windows.md`).

## Aday cekirdek (guncel)

| BApp | Son guncelleme | Ne ekler | Dikkat |
|---|---|---|---|
| Active Scan++ | 2026-10-22 | Scanner'a ek aktif ve pasif kontroller | Ek istek uretir; Scanner'a otomatik katilir |
| Param Miner | 2026-08-05 | Gizli parametre ve header kesfi | Cok sayida istek; hiz ve kaynak sinirini ayarla |
| Collaborator Everywhere | 2025-08-29 | Proxy trafigine Collaborator header'lari ekler | Veri Collaborator sunucusuna cikabilir; musteri onayi sart |
| HTTP Request Smuggler | 2026-08-05 | Request smuggling/desync testi | Paylasimli altyapiyi bozabilir; yazili onay ve dusuk hiz |
| Backslash Powered Scanner | 2025-04-30 | Injection sinyalleri icin ek aktif tarama | Daha eski; yukleme kabulu sart |
| InQL - GraphQL Scanner | 2026-02-16 | GraphQL introspection ve tarama | Yalnizca GraphQL hedeflerde |
| JWT Editor | 2026-09-07 | JWT inceleme ve manipulasyon | Manuel arac |
| Autorize | 2026-02-24 | Roller arasi yetki kontrolu (IDOR/BOLA) | Manuel; `kapsam/recipe.md` B |

## Bayat (2021'den beri guncellenmemis)

J2EEScan (2021-08-25), Retire.js (2021-12-14), AuthMatrix (2021-10-15). Burp 2026.2.1'de yuklenip calistigi kanitlanmadikca kullanilmaz.

## Kayit

Her kullanilan BApp icin: surum, bagimlilik, Scanner'a otomatik katilim, bagimsiz trafik uretimi, Collaborator kullanimi ve alinan musteri onayi proje kaydina yazilir. Burp'un kaynak sinirinin tum eklenti trafigine uygulandigi varsayilmaz.

## Collaborator

Collaborator'a giden veri ve kullanimi musteriyle yazili netlestirilir. Musteri verisi payload'a konmaz. Public Collaborator yerine hassas isler icin private Collaborator sunucusu degerlendirilir.
