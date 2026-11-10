# Ändringslista — revision november 2026 (Sprint 14 T3, fas A)

**Status:** Fas A (research) klar 2026-11-10. **Inga datapatchar är gjorda.** Patchar görs i T4
efter godkännande: alla RUTIN-rader appliceras, BEDÖMNING-rader bara efter beslut (se
separat lista sist). Arbetsordning enligt DEC-018.

**Klass:** RUTIN = nytt värde står ordagrant i källan för en redan spårad post.
BEDÖMNING = allt annat (ny post, relevans, struken post, egen text, val mellan källor).

**Underlag hämtat 2026-11-10 i molnmiljön:**
- Revisionsskriptet: `docs/revision/revision-2026-11-10.{md,json}` (62 fynd, 0 fel).
- Riksdagens öppna data (dokumentlista/dokumentstatus/dokumenttext, SFS-text `sfs-2010-800`).
- regeringen.se (RSS för U-dep: pressmeddelanden 1334, lagrådsremisser 2085, regeringsuppdrag 1342; direktiv- och uppdragssidor + PDF).
- skolverket.se (remissidan 2026-11-09, översiktssidan, pågående/rapporterade regeringsuppdrag, publikationer).
- lagen.nu/2010:800 (ändringsregister: förarbeten + ikraftträdande per ändrings-SFS).
- uppdrag.json och guide.json granskades post för post av två delegerade genomgångar. Deras
  högpåverkande fynd har kontrollerats igen i huvudsessionen (markerat **✓ omkontrollerat**).
- Ej nåbart/ej försökt: statskontoret.se (regleringsbrev → chatten), svenskforfattningssamling.se
  (403 Cloudflare), digital-strategy.ec.europa.eu (nekas av sandboxens nätpolicy).

Förkortningar för återkommande källor:
- **AUG** = https://www.regeringen.se/contentassets/65c4fc54d4dc43479794db0d196f83b6/andring-av-uppdraget-till-statens-skolverk-att-forbereda-inforandet-av-en-tioarig-grundskola-och-ta-fram-forslag-pa-nya-laroplaner.pdf
- **SFS800** = https://data.riksdagen.se/dokument/sfs-2010-800.text
- **LAGEN** = https://lagen.nu/2010:800
- **UBU30** = https://data.riksdagen.se/dokumentstatus/HD01UbU30.json
- **REMISS** = https://www.skolverket.se/om-skolverket/det-har-gor-skolverket/skolverkets-remisser/remisser/2026-11-09-remiss-forslag-pa-nya-laroplaner-och-kursplaner-for-grundskolan-anpassade-grundskolan-specialskolan-och-sameskolan
- **SVOV** = https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/nya-laroplaner-och-kursplaner

---

## Tvärgående fynd (påverkar flera filer)

**X1. Augustiändringen av läroplansuppdraget har fel dnr och fel datum i tre filer.** ✓ omkontrollerat.
Beslutet är daterat **2026-08-20** med dnr **U2026/01483** (AUG: "2026-08-20 / U2026/00988 (delvis) /
U2026/01483"). U2026/00888 är dnr för en *tidigare* ändring daterad 2026-04-23. Skolverket listar samma
datum (SVOV/REMISS: "(2026-04-23)", "(2026-08-20)"). 2026-08-24 är regeringen.se:s publiceringsdatum.
Felet kommer från Sprint 13 T8b. → rad U4–U6, T3, A1.

**X2. SFS 2026:1243 träder i kraft 2 juli 2028, inte 1 juli.** ✓ omkontrollerat (SFS800: "2026:1243 /
1. Denna lag träder i kraft den 2 juli 2028."). Utskottet samordnade prop. 194–198 i UbU26 till tre
lagar: 2026:1242 (1 juli 2028), 2026:1243 (2 juli 2028) och 2026:1245 (1 jan 2031). Påverkar *tid*
(tredje steget) och *betyg*. → rad G1–G3, R7–R8, A3–A4.

**X3. Prop. 2025/26:292 har rskr och SFS.** ✓ UBU30: BES "inträffat", rskr 2025/26:438, beslutsdatum
2026-08-13. LAGEN: "SFS 2026:1634 … Förarbeten Bet. 2025/26:UbU30, Prop. 2025/26:292, Rskr. 2025/26:438"
och övergångsbestämmelsen "1. Denna lag träder i kraft den 1 juli 2027." (även SFS 2026:1636, ändring i
2026:1242). → rad R1, A2.

---

## a) Revisionsskriptets diff (`revision-2026-11-10`)

### reforms.json

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| R1 | vinst | transition | "Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30; rskr ej publicerad 2026-08-25). …" | "Riksdagen beslutade 2026-08-13 (bet. 2025/26:UbU30, rskr. 2025/26:438). …" | UBU30 | RUTIN |
| R2 | vinst | transition (tillägg) | — | "… Ikraftträdande 1 juli 2027 (SFS 2026:1634)." | LAGEN | RUTIN |
| R3 | profession | transition | "I kraft 1 sep 2025." | "Riksdagen beslutade 2023-05-31 (bet. 2022/23:UbU13, rskr. 2022/23:206). I kraft 1 sep 2025." (standardformeln + befintlig text) | https://data.riksdagen.se/dokument/HA01UbU13.html | RUTIN |
| R4 | timplan | transition | "Beslutad. Tillämpas stegvis." | "Riksdagen beslutade 2023-12-20 (bet. 2023/24:UbU5, rskr. 2023/24:106). Tillämpas stegvis." | https://data.riksdagen.se/dokument/HB01UbU5.html | RUTIN |
| R5 | tioarig | transition | "Riksdagen har beslutat. Tillämpas fr.o.m. HT 2028." | "Riksdagen beslutade 2025-06-18 (bet. 2024/25:UbU17, rskr. 2024/25:289). Tillämpas fr.o.m. HT 2028." | https://data.riksdagen.se/dokument/HC01UbU17.html | RUTIN |
| R6 | laroplaner, stod, tid, yrkes | transition | nämner huvudbetänkandet | **Ingen ändring.** Skriptets "ytterligare-betankande" (UbU24/25/26) speglar att utskottet samordnade lagtexten i UbU26. Huvudbeslutet står redan korrekt. | riksdagen dokumentstatus | — (information) |

### utredningar.json — direktiv

Alla direktivdatum nedan är kontrollerade mot beslutsformeln i direktivtexten ("Beslut vid
regeringssammanträde den …"). Den stämmer i 14 av 14 fall med riksdagens datum.

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| D1 | utr-skolsakerhet | Dir. 2023:120.datum | 2023-08-14 | 2023-08-10 | https://data.riksdagen.se/dokument/HBB1120.html | RUTIN |
| D2 | utr-skolinformation | Dir. 2021:89.datum | 2021-10-21 | 2021-10-20 | https://data.riksdagen.se/dokument/H9B189.html | RUTIN |
| D3 | utr-skolinformation | Dir. 2023:34.datum | 2023-03-09 | 2023-03-02 | https://data.riksdagen.se/dokument/HBB134.html | RUTIN |
| D4 | utr-fler-vagar | Dir. 2023:31.datum | 2023-03-09 | 2023-02-23 | https://data.riksdagen.se/dokument/HBB131.html | RUTIN |
| D5 | utr-fler-vagar | Dir. 2023:114.datum | 2023-07-06 | 2023-07-13 | https://data.riksdagen.se/dokument/HBB1114.html | RUTIN |
| D6 | utr-vinst | Dir. 2024:85.datum | 2024-09-26 | 2024-09-19 | https://data.riksdagen.se/dokument/HCB185.html | RUTIN |
| D7 | utr-skolpeng | Dir. 2023:153.datum | 2023-10-19 | 2023-11-02 | https://data.riksdagen.se/dokument/HBB1153.html | RUTIN |
| D8 | utr-sprakforskola | Dir. 2025:102.datum | 2025-12-05 | 2025-11-27 | https://data.riksdagen.se/dokument/HDB1102.html | RUTIN |
| D9 | utr-amnesgymnasiet | Dir. 2025:98.datum | 2025-11-17 | 2025-11-13 | https://data.riksdagen.se/dokument/HDB198.html | RUTIN |
| D10 | utr-speciallarare | Dir. 2026:39.datum | 2026-05-29 | 2026-05-28 | https://data.riksdagen.se/dokument/HEB139.html | RUTIN |
| D11 | utr-skolplikt | Dir. 2025:111.datum | 2025-12-29 | 2025-12-18 | https://data.riksdagen.se/dokument/HDB1111.html | RUTIN |
| D12 | utr-barnungdomsvard-styrning | Dir. 2026:98.datum | 2026-08-28 | 2026-08-27 | https://data.riksdagen.se/dokument/HEB198.html | RUTIN |
| D13 | utr-barnungdomsvard-reform | Dir. 2025:39.datum | 2025-04-28 | 2025-04-16 | https://data.riksdagen.se/dokument/HDB139.html | RUTIN |
| D14 | utr-integritetsbevarande | Dir. 2025:64.datum | 2025-06-18 | 2025-06-19 | https://data.riksdagen.se/dokument/HDB164.html | RUTIN |
| D15 | utr-skolpeng | tillsatt | 2023-10-19 | 2023-11-02 (följer av D7: huvuddirektivets beslutsdatum) | https://data.riksdagen.se/dokument/HBB1153.html | BEDÖMNING |
| D16 | utr-skolinformation | tillsatt | 2021-10-21 | 2021-10-20 (följer av D2) | https://data.riksdagen.se/dokument/H9B189.html | BEDÖMNING |
| D17 | utr-elevhalsa | Dir. 2025:18.titel | null | "Tilläggsdirektiv till Utredningen om en förbättrad elevhälsa" | https://data.riksdagen.se/dokument/HDB118.html | RUTIN |
| D18 | utr-elevhalsa | Dir. 2025:62.titel | null | "Tilläggsdirektiv till Utredningen om en förbättrad elevhälsa" | https://data.riksdagen.se/dokument/HDB162.html | RUTIN |
| D19 | utr-studiero | Dir. 2024:79.titel | null | "Tilläggsdirektiv till utredningen Stärkt trygghet och studiero i skolan" | https://data.riksdagen.se/dokument/HCB179.html | RUTIN |
| D20 | utr-skolsakerhet | Dir. 2023:22.titel | null | "Tilläggsdirektiv till utredningen om att säkerheten i skolan ska förbättras" | https://data.riksdagen.se/dokument/HBB122.html | RUTIN |
| D21 | utr-skolinformation | Dir. 2022:10 / 2023:23 / 2023:34 .titel | null | "Tilläggsdirektiv till Skolinformationsutredningen" (alla tre) | https://data.riksdagen.se/dokument/HAB110.html, …/HBB123.html, …/HBB134.html | RUTIN |
| D22 | utr-fler-vagar | Dir. 2023:31 / 2023:114 .titel | null | "Tilläggsdirektiv till Utredningen om fler vägar till arbetslivet" | https://data.riksdagen.se/dokument/HBB131.html, …/HBB1114.html | RUTIN |
| D23 | utr-yrkesvux | Dir. 2023:110.titel | null | "Tilläggsdirektiv till Yrkesvuxutredningen" | https://data.riksdagen.se/dokument/HBB1110.html | RUTIN |
| D24 | utr-vinst | Dir. 2022:102.titel | null | "En skola utan vinstintresse" | https://data.riksdagen.se/dokument/HAB1102.html | RUTIN |
| D25 | utr-vinst | Dir. 2024:85.titel | null | "Tilläggsdirektiv till Utredningen om vinst i skolan" | https://data.riksdagen.se/dokument/HCB185.html | RUTIN |
| D26 | utr-barnungdomsvard-reform | Dir. 2025:39.titel | null | "Tilläggsdirektiv till Utredningen om en reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård" | https://data.riksdagen.se/dokument/HDB139.html | RUTIN |
| D27 | utr-rektor | Dir. 2024:48.titel | null | "Bättre förutsättningar för rektorerna inom skolväsendet" | https://data.riksdagen.se/dokument/HCB148.html | RUTIN |
| D28 | utr-rektor | Dir. 2025:50.titel | null | "Tilläggsdirektiv till Utredningen om bättre förutsättningar för rektorerna inom skolväsendet" | https://data.riksdagen.se/dokument/HDB150.html | RUTIN |
| D29 | utr-skolplikt | direktiv (ny rad) | — | {nr "Dir. 2026:117", datum "2026-09-03", typ "tilläggs", titel "Tilläggsdirektiv till Utredningen om tydligare regler vid undantag från skolplikten"} | https://data.riksdagen.se/dokument/HEB1117.html | RUTIN |
| D30 | utr-skolplikt | redovisning | 2026-11-18 | 2027-03-31 ("Uppdraget ska i stället redovisas senast den 31 mars 2027") | https://data.riksdagen.se/dokument/HEB1117.html | RUTIN |
| D31 | utr-aldersgrans-sociala-medier | direktiv (ny rad) | — | {nr "Dir. 2026:123", datum "2026-10-22", typ "tilläggs", titel "Tilläggsdirektiv till Utredningen om en åldersgräns på sociala medier"} | https://data.riksdagen.se/dokument/HEB1123.html | RUTIN |
| D32 | utr-aldersgrans-sociala-medier | redovisning | 2026-11-14 | 2026-12-31 ("ska i stället redovisas senast den 31 december 2026") | https://data.riksdagen.se/dokument/HEB1123.html | RUTIN |
| D33 | utr-barnungdomsvard-reform | direktiv (ny rad) | — | {nr "Dir. 2025:95", datum "2025-10-30", typ "tilläggs", titel "Tilläggsdirektiv till utredningen En reform av den statliga barn- och ungdomsvården för en trygg och kvalitativ vård"} | https://data.riksdagen.se/dokument/HDB195.html | RUTIN |
| D34 | utr-barnungdomsvard-reform | redovisning | 2026-03-02 | 2026-08-11 ("Uppdraget ska i stället redovisas senast den 11 augusti 2026", Dir. 2025:95) | https://data.riksdagen.se/dokument/HDB195.html | RUTIN |
| D35 | utr-grundlaggande-svenska | direktiv (ny rad) | — | {nr "Dir. 2024:72", datum "2024-08-22", typ "tilläggs", titel "Tilläggsdirektiv till Utredningen om införande av grundläggande svenska och översyn av modersmålsundervisningen"} | https://data.riksdagen.se/dokument/HCB172.html | RUTIN |
| D36 | utr-barnungdomsvard-styrning | Dir. 2026:98 — kommittékoppling | S 2025:08 | **Ingen ändring.** Riksdagens metadata anger "kommittébeteckning: S 2025:06", men direktivets titel anger "(S 2025:08)" och texten utvidgar dir. 2025:74 (= S 2025:08). Felet ligger i källans metadata. | https://data.riksdagen.se/dokument/HEB198.html | — (källfel noterat) |

### utredningar.json — betänkanden och status

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| S1 | utr-vinst | betankanden[0] (del) | {nr null, titel null, datum 2025-03-28} | {nr "SOU 2025:37", titel "Skärpta villkor för friskolesektorn", typ "del"}. Datum: riksdagen anger 2025-04-08; nuvärde 2025-03-28 behålls tills överlämningsdatum verifierats | https://data.riksdagen.se/dokument/HDB337.html | RUTIN (nr, titel) |
| S2 | utr-skolpeng | betankanden (ny rad) | — | {nr "SOU 2026:65", titel "Verktyg för en mer likvärdig resursfördelning", typ "slut", datum "2026-10-29"} (titelsidan: "Slutbetänkande av Utredningen om en nationell skolpengsnorm för ökad likvärdighet") | https://data.riksdagen.se/dokument/HEB365.html | RUTIN |
| S3 | utr-skolpeng | status | pagaende | avslutad (slutbetänkande lämnat) | https://www.regeringen.se/pressmeddelanden/2026/10/utredningen-om-en-nationell-skolpengsnorm-har-lamnat-sitt-slutbetankande/ | BEDÖMNING |
| S4 | utr-aldersgrans-sociala-medier | SOU 2026:35.datum | null | 2026-06-02 (regeringen.se "Publicerad 02 juni 2026"; SOU:n saknas i riksdagens data) | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2026/06/sou-202635/ | BEDÖMNING |
| S5 | utr-laroplan | SOU 2025:19.datum | 2024-12-20 | 2025-02-26 (regeringen.se "Publicerad 26 februari 2025"; riksdagen 2025-02-26) | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202519/ | BEDÖMNING |
| S6 | utr-skolinformation | SOU 2024:28.datum | 2024-03-28 | 2024-04-18 (regeringen.se; riksdagen 2024-04-19) | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2024/04/sou-202428/ | BEDÖMNING |
| S7 | utr-skolsakerhet | SOU 2024:17.datum | 2024-02-29 | 2024-03-06 (regeringen.se; riksdagen 2024-03-07) | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2024/03/sou-202417/ | BEDÖMNING |
| S8 | utr-rektor | SOU 2026:4.datum | 2026-01-14 | 2026-01-19 (regeringen.se; riksdagen 2026-01-20) | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2026/01/sou-20264/ | BEDÖMNING |
| S9 | övriga SOU-datum (elevhalsa 2025:113, studiero 2025:8, skolsakerhet 2023:28/2024:87, fler-vagar 2024:74, yrkesvux 2024:16, vinst 2025:123, ai 2025:101, skolpeng 2025:72, speciallarare 2026:50) | datum | — | **Ingen ändring.** Avvikelse 1–3 dagar mot riksdagens publiceringsdatum. Datafilens konvention är överlämningsdatum (Sprint 13). | revisionsrapporten | — |

---

## b) Triage av bevakningsissues #13–#20

Alla åtta rapporter är kontrollerade. v.40 (run 24) och v.44 (run 28) gick gröna utan issue (tom
körning enligt design).

| Issue | Punkt | Disposition | Rad |
|---|---|---|---|
| #13 v.37 | Dir. 2026:107 "En översyn av svenskämnenas indelning" (U-dep, 2026-09-03) | Skolrelevant nytt direktiv → kandidat för ny utredningspost | B1 |
| #14 v.38 | SOU 2026:57 Akademisk frihet | Avförs (högskola, utanför kartans scope) | — |
| #15 v.39 | SOU 2026:56 (Utredningen om företagsansvar) | Avförs (ej skolområdet) | — |
| #16 v.41 | SOU 2026:58 (×3 dok-id), 2026:59, 2026:60, 2026:62 | Avförs (ej skolområdet). Dubbletter av SOU 2026:58 = riksdagens delar d2/d3 | — |
| #17 v.42 | SOU 2026:61, SOU 2026:53 | Avförs (ej skolområdet) | — |
| #18 v.43 | SOU 2026:63, SOU 2026:64 | Avförs (ej skolområdet) | — |
| #19 v.45 | SOU 2026:65 | **Spårad utredning har levererat slutbetänkande** (skolpeng) | S2, S3, R9, A6 |
| #20 v.46 | SOU 2026:66 Lyssna på barnet! (familjerätt) | Avförs (ej skolområdet) | — |
| #13–#20 | "regleringsbrev kunde INTE hämtas" (alla åtta) | Känd DEC-008-degradering. Regleringsbrevskontroll → chatten (statskontoret.se ej nåbart härifrån) | — |

**Bevakningen missade (observation, ingen åtgärd i Sprint 14):**
- Dir. 2026:117 (tilläggsdir. till spårade U 2025:04, 2026-09-03) i v.37. Samma körning rapporterade Dir.
  2026:107 (samma dag, samma departement) men inte 2026:117 eller 2026:121, så fönsterlistan var ofullständig.
- Dir. 2026:123 (tilläggsdir. till spårade S 2025:11, 2026-10-22) i v.44, som gick tom.
- Departementsuppdrag utan Dir.-nummer (U2026/01547, 01569, 01571, 01573) syns inte i riksdagens data.
  Pressmeddelande-RSS (taxonomi 1334) bevakas inte.
- Revisionsskriptet (T2) fångar de två första via kommittébeteckning. Underlag för Sprint 15.

---

## c) Post för post

### uppdrag.json

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| U1 | laroplaner (huvudpost) | kort | "… Förslag till regeringen mars 2027." | "… Förslag till regeringen senast 14 maj 2027." | AUG ("senareläggs till den 14 maj") | RUTIN |
| U2 | laroplaner (huvudpost) | fulltext | "… senast den 31 mars 2027 redovisa förslagen …" | "… senast den 14 maj 2027 …" (ursprungligen 31 mars 2027; senarelagt genom U2026/01483, 20 augusti 2026) | AUG | RUTIN |
| U3 | laroplaner (huvudpost) | kort | "Uppdrag att ta fram förslag till nya kursplaner (U2025/02427)" | "Uppdrag att ta fram förslag på nya läroplaner (U2025/02427)" | https://www.regeringen.se/regeringsuppdrag/2025/12/uppdrag-till-statens-skolverk-att-forbereda-inforandet-av-en-tioarig-grundskola-och-ta-fram-forslag-pa-nya-laroplaner/ | BEDÖMNING |
| U4 | laroplaner + tioarig, relaterad "Ändring av uppdraget …" | kort | "(U2026/00888, 24 aug 2026)" | "(U2026/01483, 20 aug 2026)" | AUG ✓ | RUTIN |
| U5 | samma (båda noderna) | fulltext | "(U2025/02427, U2026/00888; 24 augusti 2026)" | "(U2026/01483; 20 augusti 2026). Beslutet ändrar uppdraget U2025/02427 och U2026/00888." | AUG ✓ | RUTIN |
| U6 | samma (båda noderna) | kallor[].text | "Regeringsuppdrag (U2026/00888)" | "Regeringsuppdrag (U2026/01483)" | AUG ✓ | RUTIN |
| U7 | laroplaner (+ ev. tioarig), relaterade | ny post | — | Apriländringen U2026/00888 (2026-04-23): förslagen utgår från prop. 2025/26:194, experter från U 2023:09 ges en central roll, samlad redovisning till Regeringskansliet senast 15 juni 2026 | https://www.regeringen.se/regeringsuppdrag/2026/04/andring-av-uppdraget-till-statens-skolverk-att-forbereda-inforandet-av-en-tioarig-grundskola-och-ta-fram-forslag-pa-nya-laroplaner/ | BEDÖMNING |
| U8 | införandestöd U2026/01265 (fem noder) | fulltext | "(U2026/01265, 23 juni 2026)" | "(U2026/01265, 18 juni 2026)". 23 juni är publiceringsdatum | https://www.regeringen.se/contentassets/5479deb87bc140128c4a767cda9d059e/uppdrag-till-statens-skolverk-att-genomfora-insatser-for-att-stodja-inforandet-av-skolreformer.pdf | RUTIN |
| U9 | betyg, relaterad "Uppdrag om digitala prov" | kort/fulltext/kallor.text | "24 juli 2026", inget dnr | "23 juli 2026", dnr U2026/01377 | https://www.regeringen.se/globalassets/regeringen/dokument/utbildningsdepartementet/u2026_01377-uppdrag-till-statens-skolverk-om-digitala-prov_webb.pdf | RUTIN |
| U10 | betyg, relaterad "Uppdrag om digitala prov" | kort/fulltext (innehåll) | "Uppdragets innehåll framgår av regeringsbeslutet — se källan." | Digitala nationella slutprov (gr, specialskola, gymnasial nivå). Ersätter bl.a. U2026/00283. Årlig redovisning 15 feb; delredovisning om central rättning senast 1 dec 2026 | samma | BEDÖMNING |
| U11 | betyg, relaterad U2026/00283 | kort | "Redovisas 8 maj 2026." | "Redovisad 8 maj 2026 (U2026/00976)." | samma + https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/redovisning-av-andring-av-uppdraget-att-digitalisera-de-nationella-proven | RUTIN |
| U12 | betyg, relaterad U2026/00283 | status | aktiv | ersatt av U2026/01377 (23 juli 2026) | samma | BEDÖMNING |
| U13 | betyg, relaterad U2026/00283 | kort/fulltext | "Central rättning fortgår — gymnasiet HT 2026, grundskolan VT 2028" | Stryk. Uppgiften saknar stöd i beslutet, och Skolverkets redovisning beskriver en annan plan | samma | BEDÖMNING |
| U14 | betyg, relaterade | ny post | — | U2026/01561 "Uppdrag till Statens skolverk om ett likvärdigt betygssystem" (2026-09-03): bedömningsstöd senast 15 jan 2027, slutprov och beräkning 15 feb 2028, kalibrering 15 feb 2030 | https://www.skolverket.se/download/18.359c24d31a0a86b47d62daf/1789566333305/U2026_01561_Uppdrag-om-ett-likvardigt-betygssystem.pdf | BEDÖMNING |
| U15 | betyg (huvudpost) | fulltext | "1 juli 2028: Ändringar i skollagen träder i kraft." | Följer beslutet om X2/A4 (SFS 2026:1243 = 2 juli 2028) | SFS800 ✓ | BEDÖMNING |
| U16 | betyg (huvudpost) | kallor[0] url/text | …/forandringar-inom-skolomradet/forberedelser-for-inforande-av-nytt-betygssystem | https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/nytt-betygssystem, "Skolverket: Nytt betygssystem" (gamla adressen redirectar hit) | samma | RUTIN |
| U17 | stod, standardiserade tester | relaterade | "Förbereda framtagande av standardiserade tester (RB 2025)" | Ny post U2026/01274 "Uppdrag om framtagning av standardiserade tester" (2026-06-18), ersätter U2025/02022; delredovisas 1 juni 2027, slutredovisas 1 juni 2028. Gamla posten markeras ersatt | https://www.skolverket.se/download/18.667f30a619ed441dc0c6bf20/1783341393618/U2026_01274_Framtagning-av-standardiserade-tester.pdf | BEDÖMNING |
| U18 | studiero, relaterad "Stödmaterial … sexualbrott" | kort | "Redovisas 18 feb 2026." | "Redovisad 12 feb 2026." | https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/stodmaterial-for-att-forebygga-sexualbrott-och-andra-grova-brott | RUTIN |
| U19 | studiero, situationell brottsprevention | fulltext | "… ska redovisas senast 29 maj 2026." | "… redovisades 29 maj 2026 ('Att förebygga på plats – situationell brottsprevention i skolan')." | https://www.skolverket.se/sok-publikationer/publikationsserier/ovrigt-material/2026/att-forebygga-pa-plats---situationell-brottsprevention-i-skolan | RUTIN |
| U20 | sprak | fulltext | "… Redovisas senast 5 juni 2026." | "… Redovisad 20 maj 2026." | https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/stod-for-uppfoljning-av-barns-sprakutveckling-i-forskolan | RUTIN |
| U21 | tioarig, relaterade | ny post | — | U2026/01202 "Förbereda fortbildning för förskollärare och lärare", redovisad 30 sep 2026 | https://www.skolverket.se/sok-publikationer/publikationsserier/regeringsuppdrag/2026/forbereda-fortbildning-for-forskollarare-och-larare | BEDÖMNING |
| U22 | brott + offentlighet, relaterade | ny post | — | U2026/00991 "Uppdrag till Statens skolverk om stöd i tillämpningen av nya regler om informationsutbyte" (2026-05-13): vägledning senast 25 juni 2027, slutredovisning 15 dec 2028 | https://www.regeringen.se/regeringsuppdrag/2026/05/uppdrag-till-statens-skolverk-om-stod-i-tillampningen-av-nya-regler-om-informationsutbyte/ | BEDÖMNING |
| U23 | gy25 | kallor[0].url | …/forandringar-inom-skolomradet/gy25----amnesbetyg-pa-gymnasial-niva | https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/tidigare-forandringar/gy25----amnesbetyg-pa-gymnasial-niva (redirect-mål) | samma | RUTIN |
| U24 | skolpeng | kort | "Utredning pågår. Inget uppdrag till Skolverket." | "Slutbetänkande lämnat (SOU 2026:65, 29 okt 2026)." Delen om Skolverksuppdrag ej verifierad | https://data.riksdagen.se/dokument/HEB365.html | BEDÖMNING |

Ej verifierbart i uppdrag.json: allt som bara bygger på regleringsbrev (belopp och RB-uppdrag, "Inget
uppdrag i regleringsbrevet för 2026") → chatten. Införandestödets utvärderingsförslag (frist 2 nov 2026):
ingen redovisning hittad. Apriländringens samlade redovisning (15 juni 2026): ingen publicerad redovisning hittad.

### tidslinje.json

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| T1 | laroplaner-remiss | hela posten | 2026-10-09 "Kursplaneremiss — öppen för synpunkter t.o.m. 11 december 2026" | **Stryk.** Motsägs av den faktiska remissen (9 nov 2026–20 jan 2027). Ersätts av remisshändelserna ur remisser.json i T5 | REMISS | BEDÖMNING |
| T2 | riksdag-q2-2026 | hela posten | 2026-Q2 "Riksdagsbeslut väntas för åtta propositioner (191–198)" | **Stryk** (inaktuell; besluten fattades 26 maj–9 juni 2026 och är egna rader i andringar.json) | riksdagens dokumentstatus UbU20–27 | BEDÖMNING |
| T3 | laroplaner-forslag | kalla | "U2025/02427, senarelagt U2026/00888" | "U2025/02427, senarelagt U2026/01483" | AUG ✓ | RUTIN |
| T4 | laroplaner-forslag | titel | "Förslag till nya kursplaner lämnas till regeringen" | "Omarbetade förslag till nya läro- och kursplaner lämnas till regeringen" | SVOV ("lämnas omarbetade förslag till nya läro- och kursplaner över till regeringen den 14 maj 2027") | BEDÖMNING |
| T5 | prov-genomforandeplan (2026-05-08) | — | redovisning | Oförändrad datumpost; redovisad 8 maj 2026 (U2026/00976) | se U11 | — (stämmer) |
| T6 | brottsprevention-kartlaggning (2026-05-29) | — | delredovisning | Stämmer: redovisad 29 maj 2026 | se U19 | — (stämmer) |
| T7 | studiero-delar-ikraft (2028-07-01) | hela posten | "Trygghet och studiero — resterande delar träder i kraft" | Prop. 2025/26:193 finns bara i SFS 2026:1198 (i kraft 2026-08-01) enligt lagen.nu:s förarbetesregister, så posten saknar belägg. Stryk eller verifiera mot prop. 193 | LAGEN | BEDÖMNING |
| T8 | (ny) vinst-ikraft | ny post | — | {datum 2027-07-01, typ ikraftträdande, titel "Skärpta villkor för friskolesektorn träder i kraft", reform vinst, kalla "SFS 2026:1634"} | LAGEN | BEDÖMNING |
| T9 | (ny) tid-steg 1 och 3 | ny post | — | 2026-08-01 (SFS 2026:1096) och 2028-07-02 (SFS 2026:1243); tidslinjen har i dag bara 2027-07-01 | LAGEN; SFS800 | BEDÖMNING |
| T10 | central-rattning-gy (2026-Q3) och central-rattning-grundskola (2028-Q1) | datum | 2026-Q3 / 2028-Q1 (kalla "RB 2024") | Skolverkets redovisning 8 maj 2026 beskriver pappersprov och lokal rättning i gymnasieskolan 2029–2030 och central rättning av vissa uppsatsdelar från 2031. Posterna är sannolikt inaktuella. Stryk eller ersätt efter beslut | se U13 | BEDÖMNING |
| T11 | laroplaner-samrad (2026-Q2) | — | milstolpe | Passerad, kalla "skolverket.se" utan URL. Ej verifierad, ingen ändring föreslås | — | — (ej verifierad) |

### guide.json

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| G1 | tid, 2028-07-01 | ikrafttradanden[2].datum | 2028-07-01 | 2028-07-02 | SFS800 ✓ ("2026:1243 / 1. Denna lag träder i kraft den 2 juli 2028.") | RUTIN |
| G2 | tid, 2028-07-01 | ikrafttradanden[2].omfattning | "… den 1 juli 2028 (SFS 2026:1243)" | "… den 2 juli 2028 (SFS 2026:1243)" | SFS800 ✓ | RUTIN |
| G3 | tid | overgangsbestammelser[2] | "Denna lag träder i kraft den 1 juli 2028." (prop.citat) | Ersätt med den antagna lagens text (SFS 2026:1243, 2 juli 2028). Utskottet: "Till följd av ett förbiseende saknades övergångsbestämmelser … i proposition 2025/26:196" | https://data.riksdagen.se/dokument/HD01UbU26.text; SFS800 | BEDÖMNING |
| G4 | betyg, 2028-07-01 | ikrafttradanden[0].datum + overgangsbestammelser[0] | 1 juli 2028 | 2 juli 2028 enligt SFS 2026:1243, vars övergångstext i övrigt är likalydande med guidens. UbU26 skriver "i huvudsak … 1 juli 2028" | SFS800 ✓; LAGEN | BEDÖMNING |
| G5 | betyg | ikrafttradanden (ny rad) | — | 2030-07-01, SFS 2026:1244 ("Denna lag träder i kraft den 1 juli 2030", tillämpas på utbildning som påbörjas efter 30 juni 2031) | SFS800 ✓ | BEDÖMNING |
| G6 | stod | sfs; noteringar | null; "ej kungjord" | "SFS 2026:1242"; ta bort "ej kungjord" | LAGEN ("Prop. 2025/26:195 … Rskr. 2025/26:328 … Ikraftträder 2028-07-01") | RUTIN |
| G7 | studiero | sfs; noteringar | null; "ej kungjord" | "SFS 2026:1198" | SFS800 + LAGEN ("Bet. 2025/26:UbU22, Prop. 2025/26:193, Rskr. 2025/26:308 … Ikraftträder 2026-08-01") | RUTIN |
| G8 | register | sfs; noteringar | null; "ej kungjord" | "SFS 2026:760" | LAGEN ("Prop. 2025/26:174, Rskr. 2025/26:300 … Ikraftträder 2026-07-15") | RUTIN |
| G9 | timplan | sfs; noteringar | null; "ej verifierat" | "SFS 2023:943" | SFS800 + LAGEN ("Bet. 2023/24:UbU5, Prop. 2023/24:20, Rskr. 2023/24:106") | RUTIN |
| G10 | tid | sfs; noteringar | null; "ej kungjord vid inmatning" | Tre lagar (2026:1096/1097/1243). Fältet är enkelvärt. Ta bort "ej kungjord"; behåll SFS i omfattning (Sprint 13-beslutet) | LAGEN | BEDÖMNING |
| G11 | betyg | sfs; noteringar | null; "ej kungjord" | 2026:1243 (även 2026:1244/1245); uppdatera noteringen | LAGEN | BEDÖMNING |
| G12 | laroplaner | sfs; noteringar | null; "ej kungjord" | 2026:1242 (prop. 194 ingår även i 1243/1245) | LAGEN | BEDÖMNING |
| G13 | brott | sfs; noteringar | null; "ej kungjord" | 2026:734 (guidens övergångstext är ordagrant dess); prop. 192 gav även 2026:735–737 | SFS800; LAGEN | BEDÖMNING |
| G14 | brott | ikrafttradanden (ny rad) | — | SFS 2026:737 (3 kap. 12 k §): i kraft 2026-07-01, tillämpas efter 31 december 2027 | SFS800 | BEDÖMNING |
| G15 | offentlighet | sfs; noteringar | null; "ej kungjord" | 2026:714 (OSL; guidens övergångstext är ordagrant dess). Skollagsdelen 2026:716 | https://data.riksdagen.se/dokument/sfs-2009-400.text; LAGEN | BEDÖMNING |
| G16 | yrkes | noteringar | "steg 2-lagens SFS-nummer ej verifierat" | Steg 2 = SFS 2026:1243 (2028-07-02). Prop. 198 ingår även i 2026:1245 (2031-01-01), som saknas som steg | LAGEN | BEDÖMNING |
| G17 | profession | noteringar | "senareläggningslagens SFS-nummer ej verifierat (propen anger '2024:000')" | SFS 2024:1074 (prop. 2023/24:166, rskr. 2024/25:40, ikraft 2025-09-01) | LAGEN | RUTIN |
| G18 | tioarig | noteringar | "lag (2025:1312) … ej verifierad mot SFS-kungörelsen" | Belagd (prop. 2025/26:10, rskr. 2025/26:49); övergångspunkt 3 får ny lydelse 2027-01-01 genom 2026:716 | LAGEN; SFS800 | BEDÖMNING |

Kontrollerat utan avvikelse: alla 13 riksdagsbeslut (BES inträffat + rskr) och ikraftträdandena för
laroplaner, stod, brott, register, offentlighet, yrkes, timplan, tioarig och profession. Alla 26 URL:er i guide.json ger 200.

### andringar.json

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| A1 | 2026-08-24 laroplaner/tioarig | datum; kalla.text | 2026-08-24; "Regeringsuppdrag (U2026/00888)" | 2026-08-20; "Regeringsuppdrag (U2026/01483)" | AUG ✓ | RUTIN |
| A2 | 2026-08-13 vinst | kalla.text | "Riksdagsbeslut — bet. 2025/26:UbU30" | "Riksdagsbeslut — bet. 2025/26:UbU30, rskr. 2025/26:438" | UBU30 ✓ | RUTIN |
| A3 | 2026-06-09 tid | text | "… 1 augusti 2026, 1 juli 2027 och 1 juli 2028." | "… 1 augusti 2026, 1 juli 2027 och 2 juli 2028." | SFS800 ✓ | RUTIN |
| A4 | 2026-06-09 betyg | text | "Skollagsändringarna träder i kraft 1 juli 2028; …" | Följer beslutet om G4 (2 juli 2028 enligt SFS 2026:1243) | SFS800 ✓ | BEDÖMNING |
| A5 | 2026-08-13 SOU 2026:50 | datum | 2026-08-13 | **Ingen ändring** (regeringen.se 08-13 och riksdagen 08-14 noterade i Sprint 13) | — | — |
| A6 | (ny) 2026-10-29 | ny post | — | "Slutbetänkandet SOU 2026:65 (Verktyg för en mer likvärdig resursfördelning) överlämnades till regeringen." reform_ids ["skolpeng"] (Sprint 13-konventionen: betänkanden → post) | https://data.riksdagen.se/dokument/HEB365.html | BEDÖMNING (görs i T6) |
| A7 | (ny) 2026-11-09 | ny post | — | Remiss öppnad (givet i briefen, T6) | REMISS | BEDÖMNING (görs i T6) |
| A8 | (ny) nya spårade utredningar | ny post | — | En post per utredning som godkänns under B2–B7 (Sprint 13-konventionen) | se B2–B7 | BEDÖMNING (görs i T6) |

Övriga 12 poster är kontrollerade mot riksdagens dokumentstatus (datum, bet., rskr) utan avvikelse.

### reforms.json (utöver skriptets diff)

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| R7 | tid | ikraft; transition | "1 aug 2026 / 1 juli 2027 / 1 juli 2028"; "… samordning 1 juli 2028 (SFS 2026:1243)" | "… / 2 juli 2028"; "… 2 juli 2028 (SFS 2026:1243)" | SFS800 ✓ | RUTIN |
| R8 | betyg | ikraft; transition | "1 juli 2028"; "Skollagen: 1 juli 2028" | Följer beslutet om G4 | SFS800 ✓ | BEDÖMNING |
| R9 | skolpeng | transition | "… Slutbetänkande (gymnasiet) väntas nov 2026." | "… Slutbetänkande (gymnasiet) SOU 2026:65 lämnat 29 oktober 2026." | https://data.riksdagen.se/dokument/HEB365.html | BEDÖMNING |
| R10 | sprak | transition | "Utredning pågår. Redovisning senast 11 juni 2026." | Slutbetänkande SOU 2026:37 överlämnat 17 juni 2026; ny utredning om obligatorisk förskola med språkutvecklande insatser (U2026/01573, 3 sep 2026) | https://data.riksdagen.se/dokument/HEB337.html; B2 | BEDÖMNING |
| R11 | studiero | transition | "… Vissa bestämmelser om stödundervisning träder i kraft 1 juli 2028." | Prop. 193 finns bara i SFS 2026:1198 (2026-08-01) enligt lagen.nu, och guiden säger "samtliga ändringar … samtidigt". Stryk meningen eller verifiera mot prop. 193 (samma fråga som T7) | LAGEN | BEDÖMNING |
| R12 | laroplaner, tioarig | links[Skolverket].u | …/forandringar-inom-skolomradet/tioarig-grundskola-och-nya-laroplaner (404) | https://www.skolverket.se/styrning-och-ansvar/en-skola-i-forandring/nya-laroplaner-och-kursplaner (200, "Nya läroplaner och kursplaner") | SVOV | BEDÖMNING |
| R13 | betyg | links[SOU 2025:18].u | …/statens-offentliga-utredningar/2025/03/sou-202518/ (404) | …/statens-offentliga-utredningar/2025/02/sou-202518/ (200, "Ett likvärdigt betygssystem") | https://www.regeringen.se/rattsliga-dokument/statens-offentliga-utredningar/2025/02/sou-202518/ | RUTIN |
| R14 | utredningar.json utr-vinst | kallor (Dir. 2022:102).url | https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2022/06/dir.-2022102 (404) | https://data.riksdagen.se/dokument/HAB1102.html (200, samma direktiv) | https://data.riksdagen.se/dokument/HAB1102.html | RUTIN |

---

## d) Efter 2026-09-05

**Valet och regeringsbildningen.** Riksdagsval 13 september 2026. Ny riksdag samlades vid uppropet
28 september. Riksdagen röstade 3 november nej till talmannens förslag Elisabeth Thand Ringqvist (C)
som statsminister. Talmannen gav samma dag Ulf Kristersson (M) sonderingsuppdrag, som har förlängts
(https://www.riksdagen.se/sv/aktuellt/valet-2026/, https://www.riksdagen.se/sv/aktuellt/). regeringen.se
listar 2026-11-10 oförändrade statsråd (Mohamsson utbildnings- och integrationsminister, Edholm gymnasie-,
högskole- och forskningsminister). **Inget formellt beslut påverkar reformernas status → inga rader.**
Sajten nämner inga statsråd i renderad text utöver aviseringskällor (historiska källhänvisningar, lämnas).

**Budgetpropositionen för 2027.** Prop. 2026/27:1 finns inte i riksdagens öppna data 2026-11-10
(dokumentlista doktyp=prop rm=2026/27 bet=1: 0 träffar). → Inga budgetändringar. `budget`-fälten
bygger på regleringsbrev/BP26 och är inte verifierbara härifrån (chatten).

**Propositioner.** Inga propositioner från Utbildningsdepartementet i riksmötet 2026/27 per 2026-11-10
(10 props totalt, inga U-dep). Inga återkallade eller ändrade ärenden hittade.

**Lagrådsremisser (U-dep).** Senaste: "Ett tydligare regelverk för barns och ungas utbildning i
kriminalvårdsanstalt" (2026-08-27, före fönstret och inte spårad) → B8.

**Nya direktiv och departementsuppdrag:**

| # | Ärende | Källa | Förslag | Klass |
|---|---|---|---|---|
| B1 | Dir. 2026:107 "En översyn av svenskämnenas indelning" (U-dep, beslut 2026-09-03) | https://data.riksdagen.se/dokument/HEB1107.html | Ny utredningspost, kopplad_reform laroplaner? | BEDÖMNING |
| B2 | U2026/01573 "Uppdrag att föreslå obligatorisk förskola med språkutvecklande insatser" (regeringskanslibeslut 2026-09-03, publ. 2026-09-04; redovisas senast 1 september 2027; utredare Camilla Mårtensen enligt pressmeddelandet) | https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601573/ + PDF | Ny utredningspost (departementsuppdrag, beteckning null), kopplad_reform sprak. **Löser lucka (e3).** | BEDÖMNING |
| B3 | U2026/01547 "Uppdrag att utreda vissa skärpta villkor för enskilda huvudmän inom skolväsendet" (2026-09-01; redovisas senast 30 september 2027) | https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601547/ | Ny utredningspost, kopplad_reform vinst | BEDÖMNING |
| B4 | Dir. 2026:105 "Åtgärder för att förebygga och förhindra allvarliga våldsdåd i skolmiljöer" (Ju-dep, 2026-09-03) | https://data.riksdagen.se/dokument/HEB1105.html | Ny utredningspost (trygghet), departementsöverskridande | BEDÖMNING |
| B5 | U2026/01569 "Uppdrag att utreda nationell yrkesutbildning" (2026-09-03; redovisas senast 31 mars 2027) | https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601569/ | Ny post eller avförs (pilotverksamhet, svag koppling till yrkes) | BEDÖMNING |
| B6 | U2026/01571 "Uppdrag att se över en utökning av målgruppen för särskild utbildning med judiska studier i grundskolan" (2026-09-03; redovisas senast 5 april 2027) | https://www.regeringen.se/rattsliga-dokument/kommittedirektiv/2026/09/u202601571/ | Förslag: avförs (ingen spårad reform) | BEDÖMNING |
| B7 | Dir. 2026:121 "Bättre insyn och kontroll i yrkeshögskolan" (U-dep, 2026-09-03) | https://data.riksdagen.se/dokument/HEB1121.html | Förslag: avförs (yrkeshögskolan ingår inte i skolväsendet) | BEDÖMNING |
| B8 | Lagrådsremiss om utbildning i kriminalvårdsanstalt (2026-08-27) | https://www.regeringen.se/rattsliga-dokument/lagradsremiss/2026/08/ett-tydligare-regelverk-for-barns-och-ungas-utbildning-i-kriminalvardsanstalt/ | Spåras eller avförs | BEDÖMNING |
| B9 | Statsbidrag för säkerhet i skolan förstärkt med 100 Mkr för 2026, totalt 400 Mkr (pressmeddelande 2026-09-03) | https://www.regeringen.se/pressmeddelanden/2026/09/regeringen-forstarker-statsbidrag-for-sakerhet-i-skolan-med-100-miljoner-kronor/ | studiero.budget säger "300 Mkr statsbidrag säkerhet". Pressmeddelande, inte beslutsdokument → ingen ändring förrän beslutet hittats | BEDÖMNING |
| B10 | Förordning (2026:1751) om statsbidrag för undervisning på entreprenad inom små och dyra yrkesområden (2026-09-03) | https://data.riksdagen.se/dokumentlista/?doktyp=sfs&rm=2026&sok=skollagen&utformat=json | Formellt beslut kopplat till yrkes (bygger på SOU 2024:74). Lägg till i yrkes.changes/links eller avförs | BEDÖMNING |
| B11 | Dir. 2026:117 och 2026:123 | se D29–D32 | Redan RUTIN-rader | — |

---

## e) Kända luckor

| Lucka | Utfall | Rad |
|---|---|---|
| rskr för prop. 2025/26:292 | **Löst:** rskr 2025/26:438 (BES inträffat, beslut 2026-08-13). SFS 2026:1634 + 2026:1636, ikraft 1 juli 2027 | R1, R2, A2 |
| Innehållet i Dir. 2026:98 | **Löst:** utvidgar S 2025:08 (dir. 2025:74) med kartläggning av hot och våld mot personal och förtroendevalda i barn- och unga-ärenden enligt SoL/LVU, behov av stöd och skydd, åtgärdsförslag och författningsförslag. Redovisning förlängd från 16 oktober 2026 till **30 november 2027**. Riksdagens "S 2025:06" är källfel (D36) | D12, nedan L1–L2 |
| Förskoledirektivet aviserat 2026-08-31 | **Löst:** blev departementsuppdraget U2026/01573 (2026-09-03), inte ett numrerat kommittédirektiv. Därför fanns det inte i riksdagens data | B2 |

| # | Post | Fält | Nuvärde | Nytt värde | Käll-URL | Klass |
|---|---|---|---|---|---|---|
| L1 | utr-barnungdomsvard-styrning | redovisning | 2026-10-16 | 2027-11-30 ("Uppdraget ska i stället redovisas senast den 30 november 2027") | https://data.riksdagen.se/dokument/HEB198.html | RUTIN |
| L2 | utr-barnungdomsvard-styrning | noteringar | "… Tilläggsdirektivets innehåll ej verifierat — kompletteras …" | Sammanfattning av uppdragsutvidgningen enligt ovan. Datumavvikelsen löst (2026-08-27) | https://data.riksdagen.se/dokument/HEB198.html | BEDÖMNING |

---

## f) Sajten

| # | Ärende | Fynd | Förslag | Klass |
|---|---|---|---|---|
| F1 | Sidtitel vs og-titel | `<title>` säger "Skolreformer 2025–2028" på alla 8 sidor (10 förekomster). index.html:s og:title och 3 andra ställen säger "2025–2031". Datat sträcker sig till 2031 (tidslinjen: betyg-komvux 2031-01-01, betyg-forsta-kullen 2031-06-01) | Enhetligt "2025–2031" i alla titlar (8 filer) | BEDÖMNING |
| F2 | Länkar som inte svarar | 95 externa URL:er i data/ + html kontrollerade: 90 × 200, 3 × 404 (R12, R13, R14), 1 timeout som gav 200 vid nytt försök (Dir. 2023:111), 1 nekad av sandboxens nätpolicy (digital-strategy.ec.europa.eu, *ai*-reformen; ej verifierbar härifrån, ej trasig) | R12–R14 | — |
| F3 | Sprint 10 T6 | Öppen sedan juni: "Run DoD review for this sprint — kontrollerar även att täckningskartan i BEVAKNING.md matchar deltatyperna rapport.js renderar". Sprint 10:s leveranser har gått i produktion och använts i 30 körningar | Stäng genom att köra täckningskartekontrollen som del av T9 (DoD) och markera Sprint 10 Completed där; alternativt stäng som överspelad | BEDÖMNING |
| F4 | Statsråd i aviseringskällor | `utr-aviserad-skolval.aviseringskalla` säger "skolminister Lotta Edholm". Edholms titel är i dag gymnasie-, högskole- och forskningsminister (regeringen.se) | Historisk källhänvisning, lämnas. Alternativt "dåvarande skolminister" | BEDÖMNING |

---

## Sammanställning: alla BEDÖMNING-rader (kräver beslut före T4)

| Rad | Kort | Föreslagen riktning |
|---|---|---|
| D15, D16 | `tillsatt` följer rättat huvuddirektivdatum (skolpeng, skolinformation) | Godkänn |
| S3 | skolpeng status → avslutad | Godkänn |
| S4 | SOU 2026:35 datum 2026-06-02 (publiceringsdatum) | Godkänn |
| S5–S8 | SOU-datum med stora avvikelser (2025:19, 2024:28, 2024:17, 2026:4) → regeringen.se publiceringsdatum | Godkänn S5 (data har utredningens deadline, inte SOU-datum); S6–S8 avgörs |
| U3 | laroplaner kort: "kursplaner" → "läroplaner" | Godkänn |
| U7 | Ny relaterad post: apriländringen U2026/00888 | Godkänn (förklarar varför U2026/00888 nämns i augustibeslutet) |
| U10 | Innehållssammanfattning för digitala prov | Godkänn |
| U12, U13 | U2026/00283 markeras ersatt; stryk "central rättning HT 2026/VT 2028" | Godkänn |
| U14 | Ny post: U2026/01561 likvärdigt betygssystem | Godkänn |
| U15, G4, A4, R8 | betyg: 1 juli → 2 juli 2028 (SFS 2026:1243) mot UbU26:s "i huvudsak 1 juli" | **Kräver beslut.** SFS är den antagna lagen; förordningen 2026:1242 (1 juli) kan bära delar |
| G3 | tid övergångsbestämmelse: prop.citat → antagen lag | Godkänn |
| G5 | betyg: nytt steg 2030-07-01 (SFS 2026:1244) | Godkänn |
| G10–G16, G18 | sfs/noteringar för tid, betyg, laroplaner, brott, offentlighet, yrkes, tioarig; nya steg brott 2026:737 | Godkänn noteringar; nya steg (G14, yrkes 2031) avgörs |
| U17 | Standardiserade tester: ny post U2026/01274, gammal ersatt | Godkänn |
| U21 | Ny post: fortbildning U2026/01202 (tioarig) | Godkänn |
| U22 | Ny post: informationsutbyte U2026/00991 (brott + offentlighet) | Godkänn |
| U24 | skolpeng kort: slutbetänkande lämnat | Godkänn |
| T1 | Stryk laroplaner-remiss (felaktig, ersätts av T5) | Godkänn |
| T2 | Stryk riksdag-q2-2026 (inaktuell) | Godkänn |
| T4 | laroplaner-forslag titel "läro- och kursplaner" | Godkänn |
| T7, R11 | studiero "resterande delar 1 juli 2028" saknar SFS-belägg | **Kräver beslut** (stryk eller verifiera mot prop. 193) |
| T8, T9 | Nya tidslinjeposter: vinst 2027-07-01, tid 2026-08-01 + 2028-07-02 | Godkänn |
| T10 | central-rattning-gy/-grundskola sannolikt inaktuella | **Kräver beslut** |
| A6, A7, A8 | Nya andringar-poster (SOU 2026:65, remiss, nya utredningar) | Görs i T6 |
| R9, R10 | skolpeng/sprak transition aktualiseras | Godkänn |
| R12 | Skolverket-länk laroplaner/tioarig → översiktssidan | Godkänn |
| L2 | Dir. 2026:98 innehåll i noteringar | Godkänn |
| B1 | Dir. 2026:107 svenskämnen → ny post (laroplaner) | **Kräver beslut** (relevans) |
| B2 | Förskoleuppdraget U2026/01573 → ny post (sprak) | Godkänn |
| B3 | Skärpta villkor enskilda huvudmän U2026/01547 → ny post (vinst) | Godkänn |
| B4 | Skoldådskommissionen Dir. 2026:105 → ny post | **Kräver beslut** (relevans) |
| B5 | Nationell yrkesutbildning U2026/01569 | **Kräver beslut** |
| B6 | Judiska studier U2026/01571 | Avförs |
| B7 | Yrkeshögskolan Dir. 2026:121 | Avförs |
| B8 | Lagrådsremiss kriminalvårdsanstalt | **Kräver beslut** |
| B9 | Säkerhetsstatsbidrag +100 Mkr (pressmeddelande) | Ingen ändring (inte beslutsdokument) |
| B10 | Förordning 2026:1751 (yrkes) | **Kräver beslut** |
| F1 | Titlar 2025–2028 → 2025–2031 | Godkänn |
| F3 | Sprint 10 T6 stängs via T9 | Godkänn |
| F4 | "skolminister Lotta Edholm" i aviseringskälla | Lämnas |

**Antal numrerade rader (räknat med grep i filen):** RUTIN 68, BEDÖMNING 60, ingen ändring/information 8.
D21 och D22 är sammanslagna rader (5 titlar). I sammanställningen ovan är 9 punkter märkta "Kräver beslut".
