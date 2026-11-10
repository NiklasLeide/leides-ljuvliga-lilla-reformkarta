# Backtest av automatfilen (Sprint 15 T3)

**Körning:** 2026-11-10, `node scripts/revision/automat.js --data <data ur commit 37c2616> --idag 2026-11-10`
(torrkörning) mot riksdagens öppna data live. 37c2616 är master före Sprint 14:s deploy, alltså datat
innan Sprint 14:s handpatchar. Rå rapport: [`backtest-rapport.json`](backtest-rapport.json).
Facit: Sprint 14:s ändringslista `docs/revision/2026-11-andringslista.md`.

## Utfall

| # | Regel | Post | Föreslagen ändring | Sprint 14-rad | Klass där | Jämfört med Sprint 14-patchen |
|---|---|---|---|---|---|---|
| 1 | 1c | utr-skolpeng | betänkande {SOU 2026:65, "Verktyg för en mer likvärdig resursfördelning", slut, 2026-10-29} | S2 | RUTIN | byte-identisk |
| 2 | 1b | utr-skolplikt | direktiv {Dir. 2026:117, 2026-09-03, tilläggs, "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten"} | D29 | RUTIN | byte-identisk |
| 3 | 1b | utr-aldersgrans-sociala-medier | direktiv {Dir. 2026:123, 2026-10-22, tilläggs, "Tilläggsdirektiv till Utredningen om en åldersgräns på sociala medier"} | D31 | RUTIN | byte-identisk |
| 4 | 1b | utr-barnungdomsvard-reform | direktiv {Dir. 2025:95, 2025-10-30, tilläggs, "Tilläggsdirektiv till utredningen En reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård"} | D33 | RUTIN | byte-identisk |
| 5 | 1b | utr-grundlaggande-svenska | direktiv {Dir. 2024:72, 2024-08-22, tilläggs, "Tilläggsdirektiv till Utredningen om införande av grundläggande svenska och översyn av modersmålsundervisningen"} | D35 | RUTIN | byte-identisk |

Till veckorutinen (inte tillämpat): **utr-vinst, SOU 2025:37** — utredningen har en betänkanderad utan
nummer (kan vara samma betänkande). I Sprint 14 var detta rad S1 (RUTIN, nr/titel ifyllda för hand) —
automatfilen fyller inte en befintlig rad utan lämnar det till människa. Försiktigare än facit, inte fel.

Följdändringar (1d): tre andringar-poster (2026-10-29, 2026-09-03, 2026-10-22), alla märkta "Hämtat
automatiskt från riksdagens öppna data."; ingen post för Dir. 2025:95 och 2024:72 (före loggens första
datum 2026-05-26 — samma val som Sprint 14 T6). meta.json `senast_uppdaterad` = körningsdatum.

## Kontroll mot acceptanskriterierna

| Kriterium | Belägg | Utfall |
|---|---|---|
| Varje föreslagen ändring finns som RUTIN-rad i Sprint 14-listan | tabellen ovan: S2, D29, D31, D33, D35 | **5/5** |
| Ingen BEDÖMNING-rad föreslås | inga statusbyten, inga nya poster, ingen fritext; S3 (skolpeng → avslutad, BEDÖMNING) föreslogs inte | **0 BEDÖMNING** |
| Inget ifyllt värde skrivs över | vakten godkände; tillämpning på en kopia gav en diff som bara består av tillagda rader i utredningar.json och 0 rader i reforms.json; alla fyra filer validerar | **0 överskrivningar** |

## Vad automatfilen medvetet inte tog (och varför)

Av ändringslistans 68 RUTIN-rader tog automatfilen 5. Resten faller utanför regel 1 med avsikt:
- **Rättelser av ifyllda värden** (D1–D14 direktivdatum, A1 datum, U4–U6 dnr): regel 3 — skrivs aldrig över.
- **Tomma fält i befintliga rader** (D17–D28 direktivtitlar, S4 SOU-datum): ingen tillåten ändringstyp.
- **Fritext och SFS** (R1–R5 transition, G1–G18 guide; rskr för vinst R1 där status redan var beslutad): regel 2.
- **Redovisningsdatum** efter tilläggsdirektiv (D30, D32, D34, L1): ingår inte i regel 1b (bara nr, titel, datum) → veckorutinen.

## Avvikelser och observationer

- Inga avvikelser mot kriterierna.
- **Regel 5 nåddes exakt (5 ändringar).** Backtestet motsvarar tio veckors eftersläpning; i daglig drift
  väntas 0–2 per körning. En sjätte ändring hade gett STOPP och en automat-stopp-issue — avsett beteende.
- Andringar-posternas text skiljer sig från Sprint 14:s handskrivna (fast mall, märkning); datum och källa är desamma.
