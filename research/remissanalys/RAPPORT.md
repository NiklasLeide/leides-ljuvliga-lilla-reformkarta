# Spike: Remissvar mot beslut — rapport

**Datum:** 2026-11-10 · **Status:** avslutad spike, inga ändringar i publik data eller UI
**Filer:** `kedjor.json` (Del A, sju reformer), `pilot-betyg.json` (Del B, djupextraktion), `skript/` (extraktionsskripten, se avvikelser)

---

## 1. Sammanfattning

- **Alla sju kedjor är kompletta ända till rskr.** Riksdagens dokumentstatus för varje utskottsbetänkande visar att beslutsaktiviteten (BES) har status "inträffat" och refererar till en rskr.
- **Pilot: `betyg`** (SOU 2025:18 → prop. 2025/26:197 → bet. 2025/26:UbU26 → rskr. 2025/26:335). Den har komplett kedja och flest remissvar från fokusgrupperna (35, mot 33 för tid).
- **Endast 7 av 80 utredningsförslag (8,75 %) fick `utfall_prop` utan tolkning.** Propositionen skriver nästan alltid "stämmer **i huvudsak** överens" eller "stämmer **delvis** överens". Det går inte att mappa till överensstämmer/avviker utan egen tolkning.
- **`utfall_riksdag` sattes till "bifall" för 17 av 80.** Inget förslag fick "ändrat". Riksdagen antog utskottets lagtekniskt samordnade lagförslag. Enligt utskottet hade ändringarna "inte någon betydelse i sak", och riksdagen gjorde inga tillkännagivanden.
- **Största fyndet om remissvaren:** regeringen.se publicerar bara svar från inbjudna remissinstanser. Därför syns inga enskilda huvudmän på remissidorna: de svarar alltid självmant, i alla sju reformer. Propositionens bilaga ("Förteckning över remissinstanserna") är den enda källan som räknar alla.
- **research/ hamnar i produktion vid nästa deploy** (se avsnitt 11).

## 2. Kedjestatus (Del A)

| Reform (brief) | id i reforms.json | Utredningsbetänkande | Remiss dnr | Proposition | Utskottsbet. | Rskr | Beslut |
|---|---|---|---|---|---|---|---|
| Kunskap för alla | laroplaner | SOU 2025:19 | U2025/00630 | Prop. 2025/26:194 | 2025/26:UbU23 | 2025/26:327 | 2026-06-03 |
| Betygsuppdraget | betyg ⚠️ | SOU 2025:18 | U2025/00401 | Prop. 2025/26:197 | 2025/26:UbU26 | 2025/26:335 | 2026-06-09 |
| Förbättrat stöd | stod | SOU 2025:44 | U2025/01067 | Prop. 2025/26:195 | 2025/26:UbU24 | 2025/26:328 | 2026-06-03 |
| På språklig grund | — (saknas) | SOU 2025:9 | U2025/00233 | Prop. 2025/26:194 (avsnitt 8) | 2025/26:UbU23 | 2025/26:327 | 2026-06-03 |
| Trygghet och studiero | studiero | SOU 2025:8 | U2025/00202 | Prop. 2025/26:193 | 2025/26:UbU22 | 2025/26:308 | 2026-06-03 |
| Tid för undervisningsuppdraget | tid | SOU 2025:26 | U2025/00740 | Prop. 2025/26:196 | 2025/26:UbU25 | 2025/26:332 | 2026-06-09 |
| Tioårig grundskola | tioarig | SOU 2021:33 | U2021/02645 | Prop. 2024/25:143 | 2024/25:UbU17 | 2024/25:289 | 2025-06-18 |

**Matchningsproblem som rapporteras i stället för att gissas:**
- **"Betygsuppdraget"** finns inte som namn någonstans i datan. Jag matchade det på sakinnehåll till `betyg` (SOU 2025:18 "Ett likvärdigt betygssystem"). **Bekräfta att detta avses.**
- **3 och 4 är två olika reformer.** "Förbättrat stöd" är SOU 2025:44 med prop. 195. "På språklig grund" är SOU 2025:9, och dess avsnitt 8 (grundläggande svenska som andraspråk) behandlas i prop. 194, alltså samma proposition som läroplanerna. SOU 2025:9 har ingen egen post i reforms.json. I utredningar.json (`utr-grundlaggande-svenska`) står `prop: null`, trots att prop. 2025/26:194 s. 44 uttryckligen behandlar betänkandet.
- **Utredningar delas mellan propositioner.** SOU 2025:18 delas mellan prop. 197 och prop. 194, SOU 2025:19 mellan prop. 194, 195 och 196, och SOU 2025:8 mellan prop. 193 och 194. En matris per reform måste alltså kunna hämta rader från flera propositioner.

## 3. Remissvar per kategori (Del A)

Källa: varje propositions bilaga "Förteckning över remissinstanserna". Antalen omfattar både inbjudna remissinstanser och spontana yttranden. De som avstått räknas inte.

| Reform | Kommuner | Enskilda huvudmän | SKR | Almega | Idéburna | Regioner | Myndigheter | Övriga org. | Övriga | **Totalt** | **Fokus** | Avstått/ej svarat | På remisslistan | Publicerade PDF (text/inskannad) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kunskap för alla | 22 | 4 | 1 | 1 | 1 | 1 | 29 | 71 | 0¹ | 130 | 29 | 14 | 71 | 58 (57/1) |
| Betygsuppdraget | 26 | 5 | 1 | 2² | 1 | 1 | 28 | 34 | 7 | 105 | 35 | 24 | 93 | 77 (75/2) |
| Förbättrat stöd | 18 | 2 | 1 | 1 | 1 | 0 | 17 | 33 | 0 | 73 | 23 | 20 | 71 | 58 (58/0) |
| På språklig grund | 19 | 2 | 1 | 0 | 0 | 0 | 19 | 9 | 0 | 50 | 22 | 26 | 64 | 44 (44/0) |
| Trygghet och studiero | 22 | 2 | 1 | 1 | 1 | 0 | 22 | 30 | 0 | 79 | 27 | 15 | 68 | 54 (54/0) |
| Tid för undervisningsuppdraget | 26 | 4 | 1 | 1 | 1 | 0 | 15 | 20 | 1 | 69 | 33 | 13 | 62 | 52 (51/1) |
| Tioårig grundskola | 21 | 0 | 1 | 0 | 1 | 0 | 19 | 10 | 0 | 52 | 23 | 22 | 64 | 47 (47/0) |

¹ Prop. 194 skriver "privatpersoner" i uppräkningen men anger inget antal. Därför är värdet 0 med anmärkning, inte en uppskattning.
² Almega räknas två gånger, eftersom förteckningen har två namn: "Almega Utbildning" (remissinstans) och "Almega utbildningsföretagen" (spontant yttrande).

**Status för huvudmannaorganisationerna** (källa per reform: remisslistans PDF + propositionens förteckning + remissvaret på regeringen.se):

| Reform | SKR | Almega | Idéburna skolors riksförbund |
|---|---|---|---|
| Kunskap för alla | svarat | svarat ("Almega utbildning" på listan) | svarat |
| Betygsuppdraget | svarat | svarat ("Almega Utbildning" + spontant "Almega utbildningsföretagen") | svarat |
| Förbättrat stöd | svarat | svarat | svarat |
| På språklig grund | svarat | på remisslistan men ej svarat³ | på remisslistan men ej svarat |
| Trygghet och studiero | svarat | svarat | svarat |
| Tid för undervisningsuppdraget | svarat | svarat | svarat |
| Tioårig grundskola | svarat | **ej på remisslistan**⁴ | svarat |

³ Regeringen.se publicerar under "Remissvar" ett e-postmeddelande där Almega Utbildning meddelar att organisationen avstår. Propositionen listar Almega Utbildning bland dem som avstått eller inte yttrat sig.
⁴ Remisslistan från 2021 har "Friskolornas riksförbund", som avstod eller inte svarade. Inget samband antas mellan namnen.

**Format på remissvaren:** 386 av 390 publicerade PDF:er är text-PDF:er. 4 är inskannade utan textlager: Sametinget (Kunskap för alla), Norrköpings kommun och Uppsala universitet (Betygsuppdraget), Åre kommun (Tid). Metod: `pdftotext`, där fler än 200 tecken per sida räknas som text och 0 tecken utan inbäddade typsnitt räknas som inskannad.

## 4. Pilot: betyg (Del B)

**Varför betyg:** kedjan är komplett och reformen har flest fokusgruppssvar av de sju: 26 kommuner, 5 enskilda huvudmän, SKR, 2 Almega-namn och Idéburna, totalt 35. Den är också ett bra stresstest. SOU:n är på två volymer och 1 300 sidor, förslagen delas mellan två propositioner och utskottet ändrade lagtekniskt.

- **Remissvar från fokusgrupperna:** 35, varav 29 från inbjudna remissinstanser och 6 självmant (5 enskilda huvudmän + "Almega utbildningsföretagen"). De 6 självmant inkomna svaren saknar URL, eftersom regeringen.se inte publicerar spontana yttranden.
- **Utredningsförslag:** 80 förslagsrutor ur SOU 2025:18 volym 1, med sidhänvisning.
  - 24 matchar en förslags- eller bedömningsruta i prop. 197 eller 194.
  - 23 är detaljer som propositionen bara behandlar övergripande ("Den mer detaljerade regleringen om hur beräkningen ska gå till bör bestämmas på förordningsnivå", prop. 197 s. 62).
  - 4 matchar bara på avsnittsnivå.
  - 2 är osäkra ämnesmatchningar.
  - **27 tas inte upp alls** i någon förslags- eller bedömningsruta. De finns ändå med i filen.
- **Utskottsbetänkandet** (UbU26 s. 1, 3 och 29): det fanns inga tillkännagivanden, och alla motionsyrkanden avslogs. Riksdagen antog utskottets lagförslag i bilaga 3, alltså lagtekniska anpassningar och ändrade ikraftträdande- och övergångsbestämmelser, som enligt utskottet var "utan betydelse i sak". Formellt står det: "Därmed bifaller riksdagen […] 2025/26:197 punkterna 1–4".

### Andel förslag där `utfall_prop` kunde sättas utan tolkning

| | Antal |
|---|---|
| Alla utredningsförslag | **7 av 80 (8,75 %)**, alla "överensstämmer" |
| Förslag med uttrycklig ruta-matchning | 7 av 24 (29 %) |
| Propositionsavsnitt (19 st) där meningen är entydig | 6 av 19 (32 %) |
| "avviker" | 0. Propositionen använder aldrig ordet |
| "ej genomfört" | 0. Det finns aldrig ett uttryckligt källstöd. Att propositionen är tyst räcker inte |

De 7 förslagen är F11, F12, F21, F53, F63, F64 och F69. Fördelning över de 19 propositionsavsnitten:
- 6 "stämmer överens"
- 8 "stämmer i huvudsak överens"
- 5 "stämmer delvis överens"

`utfall_riksdag` blev "bifall" för 17 förslag och null för 63. Null betyder att propositionen bara lämnade en bedömning (riksdagen beslutar inte om sådana), att förslaget gäller ikraftträdande (som utskottet ändrade) eller att det inte fanns något propositionsförslag.

### Exempel på formuleringar som inte gick att mappa till kontrollerad vokabulär

| Formulering (ordagrant) | Källa | Problem |
|---|---|---|
| "Förslagen från utredningen stämmer i huvudsak överens med regeringens förslag." | Prop. 197 s. 73 (6.3) och 7 andra avsnitt | Varken överensstämmer eller avviker. Avvikelsen beskrivs i nästa mening, i fritext |
| "Förslagen från utredningen stämmer delvis överens med regeringens förslag." | Prop. 197 s. 88, 90, 102, 113, 127 | Samma problem |
| "Förslaget om att fokus inte ska vara att uppfylla kriterier utan elevens tillgodogörande av kunskap stämmer också i huvudsak överens med regeringens förslag." | Prop. 194 s. 147 (6.7) | Samma problem. Dessutom ligger förslaget i en annan proposition |
| "Den mer detaljerade regleringen om hur beräkningen ska gå till bör bestämmas på förordningsnivå." | Prop. 197 s. 62 (6.1) | Hänskjutet till förordning. Ingen kategori i vokabulären |
| "Utredningen föreslår inte någon ändring av den tidigare riksdagsbindningen." | Prop. 197 s. 109 (6.11) | Regeringen går längre än utredningen. Vokabulären saknar "utvidgat" |
| "Förslaget från utredningen stämmer överens med regeringens förslag." (6.8) | Prop. 197 s. 101 | Mappas till överensstämmer, men SOU-förslaget F11 omfattar även komvuxarbetet, som inte nämns i regeringens ruta. Entydig text kan alltså dölja en skillnad i omfattning |
| "Riksdagen a) godtar det som utskottet anför om regeringens förslag …" | Bet. UbU23 punkt 1 | "godtar" är varken bifall eller ändrat |
| "antar utskottets förslag i bilaga 3 …" + "inte någon betydelse i sak" | Bet. UbU26 s. 3, 29 | Formellt ändrat, i sak bifall |

### Hur ofta propositionen namnger fokusgrupperna jämfört med andra

Underlaget är 18 avsnitt med rubriken "Remissinstanserna" (prop. 197 och prop. 194, den del som gäller SOU 2025:18). Avsnitt 6.11 saknar rubriken.

| Kategori | Namngivna | Svarande | Omnämnanden | Avsnitt där kategorin förekommer |
|---|---|---|---|---|
| Kommuner | 24 | 26 | 72 | 17 av 18 |
| Enskilda huvudmän | 3 | 5 (Academedia AB, IES i Sverige AB, Kunskapsskolan i Sverige AB) | 5 | 4 |
| SKR | 1 | 1 | 9 | 9 |
| Almega | 1 | 2 (bara "Almega Utbildning") | 3 | 3 |
| Idéburna | 1 | 1 | 4 | 4 |
| Myndigheter | 18 | 28 | 64 | 15 |
| Övriga organisationer | 18 | 34 | 57 | 14 |

Fokusgrupperna står för 93 av 217 omnämnanden (43 %), och de är 35 av 105 svarande (33 %). De namnges alltså ungefär i proportion till sin andel eller något mer. Kommunerna dominerar genom samordnade uppräkningar som "Falu, Motala och Söderhamns kommuner". Utöver namnen innehåller texten 30 generiska hänvisningar, till exempel "Flera remissinstanser" (8), "Flera kommuner" (5) och "Några remissinstanser" (3). Dessa kan inte knytas till en avsändare.

## 5. Namnbyten och namnvarianter mellan reformerna

Här rapporteras bara vad som står. Inga samband antas.

- **Almega:** "Almega utbildning" och "Almega Utbildning" (skiftläge) förekommer i remisslistorna 2025. "Almega utbildningsföretagen" förekommer som spontant yttrande i betyg, i samma förteckning som "Almega Utbildning". Almega finns inte med i tioårig (2021), där listan i stället har "Friskolornas riksförbund".
- **Idéburna:** "Idéburna skolors riksförbund" och "Idéburna Skolors Riksförbund" (skiftläge). Annars stabilt.
- **SKR:** "Sveriges Kommuner och Regioner" används oförändrat i alla sju.
- **Övriga, utanför fokus men relevanta för matchningen:**
  - 2021 har "Lärarförbundet", "Lärarnas Riksförbund", "Lärarförbundet Skolledare" och "Sveriges Skolledarförbund". 2025 har "Sveriges Lärare" och "Sveriges Skolledare".
  - På språklig grund: remisslistan har "Sveriges Skolledarförbund" medan propositionens förteckning har "Sveriges Skolledare".
  - Tid: remisslistan har "Svenska kommunalarbetareförbundet" medan förteckningen har "Kommunal".
  - Stavningsvarianter mellan lista och förteckning: "Karlstad kommun"/"Karlstads kommun", "Friends"/"Stiftelsen Friends", "Göteborg kommun"/"Göteborgs kommun".

## 6. Datakvalitet

1. **Regeringen.se publicerar ett urval av remissvaren.** Sidan säger själv "Här kan du ta del av svaren från dem som har ombetts att svara … Övriga yttranden finns tillgängliga i departementet".
   - Därför finns spontana yttranden aldrig online, och dit hör **alla enskilda huvudmän** i alla sju reformer.
   - För SOU 2025:8, SOU 2025:9 och SOU 2025:26 beskriver remissidans ingress bara remisslistan ("Här kan du ta del av till vilka instanser…"), men sidorna länkar ändå 44–54 remissvar under rubriken "Remissvar:". Ingressen går alltså inte att använda för att avgöra om svaren finns publicerade.
2. **Remissidans "Remissvar" omfattar även avstå-svar** (e-post eller korta brev, 39 st enligt en enkel heuristik: under 2 500 tecken och "avstår"/"inga synpunkter" i texten). Antalet PDF:er är alltså inte antalet yttranden. Propositionens förteckning är den auktoritativa källan.
3. **Remisslistan och propositionens förteckning stämmer inte alltid överens.** Strömsunds kommun står på remisslistan för SOU 2025:8 men saknas helt i propositionens förteckning.
4. **Tryckfel i källan:** i prop. 194 bilaga 12 saknas ett komma mellan "Dals-Eds kommun" och "Elevernas riksförbund". I prop. 143 står "arbetsmarknadsoch". Almega Utbildnings remissvar på SOU 2025:18 anger fel referensnummer (U2025/00740, som är dnr för SOU 2025:26).
5. **Diarienummer** står i propositionen för 4 av 7 reformer (193, 195, 197, 143). För 194 (SOU 2025:19 och 2025:9) och 196 finns det bara på remissidan.
6. **Kategorierna "myndigheter" och "enskilda huvudmän" bygger på extern kunskap,** inte på källtext. Källan anger inte organisationsform. Kommunalförbund (Göteborgsregionen, Lapplands Kommunalförbund) har lagts under övriga organisationer. Folkuniversitetet och OneSchool Global är osäkra. Allt detta är markerat med `klassning_anm` i datan. Före v1 behöver klassningen verifieras mot Skolverkets skolenhetsregister och myndighetsregistret.
7. **SOU-förslagen:** 3 förslagsrutor slutar med kolon följt av en tabell eller punktlista som inte extraherats (F02, F29, F30). F59 slutar mitt i en mening ("även avse krav på") och är troligen också avkortad. Detta är markerat med `textanm`.

## 7. Tidsåtgång

Tiderna bygger på filernas tidsstämplar i sessionen och är inte separat mätta per reform.
- **Del A, alla sju:** cirka 25 minuter (16:15–16:39). Själva kedjeuppslaget är snabbt, cirka 1 minut per reform. Det mesta av tiden gick åt till att hitta remissidorna, eftersom SOU-sidorna på regeringen.se inte länkar till dem (de hittas via regeringen.se-sökning på dnr eller SOU-nummer) och till att tolka propositionernas förteckningar.
- **Del B, betyg:** cirka 15 minuter maskinell extraktion plus manuell matchning av 80 förslag.
- Varje ny reform bör ta cirka 5 minuter för Del A med skripten, och 1–2 timmar för Del B inklusive manuell granskning av matchningarna.
- Nätverket var blockerat vid sessionsstart. En miljö med regeringen.se och riksdagen.se skapades under sessionen.

## 8. Föreslagen datamodell för v1 (matrisen)

Utgångspunkten är att matrisen är **en rad per utredningsförslag** men att källtexterna **lagras en gång per propositionsavsnitt**. Flera förslag delar samma avsnitt, och en reform kan hämta avsnitt från flera propositioner. Pilotfilen följer redan den här normaliseringen.

```jsonc
// data/remissanalys/<reform-id>.json  (en fil per reform; laddas lat vid klick)
{
  "reform_id": "betyg",
  "kedja": { "utredning": {"nr","titel","url"}, "remiss": {"dnr","url","svar_senast"},
             "propositioner": [{"nr","url"}], "betankanden": [{"bet","url"}], "rskr": {"nr","datum","url"} },
  "remissvar": {                        // källa: propositionens förteckning
    "kalla": {"text","url"},
    "antal": { "kommuner": {"remissinstans":0,"spontant":0}, "...": {} },  // 9 kategorier, se kedjor.json
    "avsandare": [ {"namn","kategori","grupp":"huvudman|huvudmannaorganisation|ovrigt",
                    "typ":"remissinstans|spontant","url": null} ],
    "fokusorganisationer": { "skr": {"status","namn_i_remisslistan","kallor":[]}, "almega": {}, "ideburna": {} }
  },
  "avsnitt": {                          // en gång per propositionsavsnitt
    "197:6.3": { "rubrik", "regeringens_rutor": {...},
                 "utredningens_forslag": {"text","kalla"},     // ordagrant
                 "remissinstanserna":   {"text","kalla"},     // ordagrant – öppnas vid klick
                 "namngivna": [{"namn_i_texten","namn_i_forteckningen","kategori"}] }
  },
  "rader": [                            // en per utredningsförslag
    { "id":"F61", "forslag":{"text","kalla"},          // kolumn Utredning
      "avsnitt":["197:6.3"], "matchning":"forslagsruta|avsnittsniva|detalj|ingen",
      "utfall_prop":"överensstämmer|avviker|ej genomfört|null", "utfall_prop_citat":[{"text","kalla"}],  // kolumn Proposition
      "utfall_riksdag":"bifall|ändrat|null", "utfall_riksdag_kalla":{},                                    // kolumn Riksdag
      "remissraknare": {"fokus":5, "ovriga":12, "generiska":3}  // härleds från avsnitt.namngivna
    }
  ]
}
```

**Rekommendationer för vokabulären,** så att fler celler kan få ett värde utan tolkning:
1. Lägg till `"i huvudsak överensstämmer"` och `"delvis överensstämmer"` som egna värden. De motsvarar propositionens fasta fraser ordagrant. Det skulle ge värde i **19 av 19** propositionsavsnitt (i stället för 6) och mappar mot texten, inte mot en tolkning.
2. Lägg till `"hänskjutet till förordning"`, men bara när propositionen säger det uttryckligen.
3. Låt `null` i Proposition-kolumnen visas som "tas inte upp i propositionen". Det gäller 27 av 80 förslag och är informativt i sig.
4. För Riksdag-kolumnen: visa "bifall" och ange lagtekniska ändringar som fotnot. "ändrat" bör bara användas för ändringar i sak.

Remissräknaren bör räkna **namngivna i propositionens remissavsnitt** och inte inkomna svar. Annars antyder den att propositionen redovisat alla svar. Totalantalet inkomna svar per kategori visas på reformnivå.

## 9. Automatisering kontra manuell verifiering

| Steg | Automatiserbart | Kräver manuell verifiering |
|---|---|---|
| Kedjan prop → bet → rskr → beslutsdatum | ~100 % (riksdagens API: dokreferens + BES "inträffat") | Nej |
| Hitta remissida och dnr | ~90 % (regeringen.se-sökning på dnr eller SOU-nummer; dnr ur propositionen) | Om dnr saknas i propositionen |
| Remisslista, förteckning, räkning per namn | ~90 % | Namnsplittring vid tryckfel, stavningsvarianter |
| Kategoriklassning | Kommuner, regioner, SKR/Almega/Idéburna ~100 % | Myndigheter och enskilda huvudmän: manuell lista, cirka 10 % osäkra |
| Text eller skannat | 100 % | Nej |
| SOU-förslagsrutor med sida | ~95 % | Rutor som fortsätter i tabell eller lista |
| Propositionens avsnitt, ordagranna citat, sidor | ~95 % (fasta rubriker; 239 av 241 citat verifierades automatiskt mot PDF-texten och 2 manuellt) | Varianter av rubriken ("Läroplansutredningens förslag" och liknande) |
| `utfall_prop` från fast fras | 100 % (regex på första meningen) | Nej, men regeln måste beslutas (se 8.1) |
| **Matchning utredningsförslag → propositionsavsnitt** | **~30 %** (bara de 24 uttryckliga ruta-matchningarna, och även de är ämnesmatchade av mig) | **Ja, alltid.** Propositionen hänvisar inte till SOU-avsnitt per förslag |
| Namngivna remissinstanser | ~90 % | Generiska hänvisningar, kortformer |

**Sammantaget kan cirka 70 % av arbetet automatiseras.** Kvar blir **matchningen förslag → propositionsavsnitt** och **kategoriklassningen**. Båda behöver granskas av en människa per reform.

## 10. Risker

1. **Matchningen är den svaga länken, och den är tolkning.** Propositionen säger "Förslagen från utredningen" utan att ange vilka SOU-förslag som avses. Varje rad i matrisen vilar därför på en redaktionell koppling. Den måste märkas som sådan och inte presenteras som officiell. *Detta är den största risken.*
2. **Ojämn bild av remisskritiken.** Spontana yttranden, bland annat alla enskilda huvudmän, publiceras inte. En klickbar räknare kan därför aldrig länka till deras text, och huvudmännens röst blir systematiskt mindre synlig än kommunernas.
3. **Fältet `utfall_prop` med nuvarande vokabulär blir nästan tomt** (91 % null). Matrisen ser då ofärdig ut, eller så frestas man att tolka. Vokabulären bör beslutas före v1 (se 8).
4. **Klassningen bygger på extern kunskap.** Att kalla något "enskild huvudman" eller "myndighet" står inte i källan. Det bryter mot datapricipen om det inte verifieras och dokumenteras.
5. **Utredningar delas mellan propositioner.** Det kräver att matrisen kan hämta rader från flera propositioner per reform, och reforms.json:s 1:1-antagande (en `ref` per reform) räcker inte.
6. **Underhåll:** remissidorna på regeringen.se länkas inte från SOU-sidorna, och regeringen.se-sökningen kan ändra format.

## 11. deploy.sh och research/

**Resultat: research/ HAMNAR i produktion vid nästa `./deploy.sh`.**
- `deploy.sh` kör `git merge dev` till master utan filter. Allt som finns på dev, inklusive research/, kommer till master.
- GitHub Pages bygger master med Jekyll: det finns ingen `.nojekyll`, och `_config.yml` exkluderar bara `docs/mockups`. Filer utan front matter (.json, .md) kopieras som statiska filer, så de blir nåbara på reformer.leide.se/research/remissanalys/…
- Belägg för att filer utanför data/ publiceras: Sprint 15 T0 hämtade en provfil under docs/automat/ live från reformer.leide.se (PROJECT_STATUS.md).
- `commit.sh` synkar bara *.html och data/ till dev-previewn, så research/ syns inte på /dev/.

**Inte åtgärdat** (briefen tillåter bara ändring i PROJECT_STATUS.md). Förslag på enradsfix i `_config.yml` före nästa deploy:
```yaml
exclude:
  - docs/mockups
  - research
```
Innehållet är bara offentliga uppgifter, så risken är låg. Men det är oavsiktlig publicering. Obs: docs/ är redan publikt på samma sätt.

## 12. Avvikelser från briefen

- **Commit-gren.** Commiten ligger på sessionsgrenen `claude/remissvar-beslut-spike-m7w3vd`, utgrenad från origin/dev (c3764fe), och inte direkt på dev. Sessionens regler tillåter bara push till den grenen. `commit.sh` användes inte, eftersom den pushar till dev och synkar master:dev/. Grenen kan snabbspolas in i dev.
- **`skript/`** har lagts till i research/remissanalys/ (finns inte i briefens fillista), så att extraktionen går att återskapa och automatiseringsbedömningen går att kontrollera. Skripten förutsätter nedladdade källfiler i en arbetskatalog och är inte produktionskod.
- **Förslagsenhet:** utredningsförslagen hämtades ur SOU:ns förslagsrutor ("Förslag:", 80 st, med sida) i stället för ur författningsförslag och sammanfattning. Förslagsrutorna är finare indelade och har entydig sidhänvisning. Bedömningsrutor (27) är inte med.
- **Part B täcker SOU 2025:18 volym 1.** Volym 2 innehåller inga förslagsrutor (kontrollerat: 0 träffar).
