# Arkiverade mockups och legacy-vyer

Filer som en gång låg i repo-roten men flyttades hit i **Sprint 12 T6** för att de
inte längre är en del av den publicerade sajten. De ligger kvar för historik/referens
och exkluderas ur GitHub Pages-bygget via `_config.yml` (`exclude: [docs/mockups]`),
så de är **inte nåbara på reformer.leide.se**.

| Fil | Vad det är | Varför bevarad |
|-----|-----------|----------------|
| `lasarshjul-mockup.html` | Mockupen som var **specen** för läsårshjulet i guide.html | DEC-015 refererar den som spec; committades medvetet som referens (T5.4) |
| `malbild.html` | Sprint 3-vyn "målbild / infrastrukturberoenden" (6 pelare, SVG-bezierlinjer), var dold från nav | Verkligt byggd feature med historiskt värde; superseded men bevarad |
| `malbild.json` | Data för malbild.html (infrastrukturpelare + reformberoenden) | Användes bara av malbild.html; flyttad tillsammans med den |

**Kör-notis:** malbild.html hämtar `data/malbild.json` och `data/reforms.json` med
relativa sökvägar som gällde i repo-roten — den fungerar inte standalone härifrån.
Det är ett kodarkiv, inte en körbar sida.

`reformkarta.html` (en tidig, superseded prototyp av reformkartan) togs **bort** i samma
städning — index.html är den underhållna versionen och prototypen hade inget referensvärde
utöver git-historiken.
