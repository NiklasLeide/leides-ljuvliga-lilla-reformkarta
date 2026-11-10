# Utmaningskartan — metod (pilot betyg)

Sprint 16. Sidan heter `pilot/utmaningar/index.html` och data ligger i `pilot/utmaningar/data/utmaningar-betyg.json`. Datamodellen beskrivs i `pilot/utmaningar/README.md`.

Utmaningskartan visar vilka utmaningar huvudmännen och deras organisationer pekade ut i sina remissvar på en utredning. Den visar också vad proposition och lag säger om de förslag som utmaningarna gällde. Piloten avser reformen *Ett likvärdigt betygssystem*.

## 1. Källor och kedja

| Led | Dokument | Källa |
|---|---|---|
| Utredningsbetänkande | SOU 2025:18 *Ett likvärdigt betygssystem* (förslagsrutor, författningskommentar 22.1, innehållsförteckning) | regeringen.se |
| Remiss | U2025/00401 (remisslista och publicerade remissvar) | regeringen.se |
| Proposition | Prop. 2025/26:197 (avsnitt 6.1–6.13 och 8). Prop. 2025/26:194 avsnitt 6.7–6.8 behandlar SOU 2025:18 avsnitt 9.3–9.4 | regeringen.se |
| Remissförteckning | Prop. 2025/26:197 bilaga 3 (vilka som svarat, spontant eller inte) | regeringen.se |
| Utskottsbetänkande | Bet. 2025/26:UbU26 | data.riksdagen.se |
| Beslut | Rskr. 2025/26:335 (2026-06-09), beslutsaktivitet med status "inträffat" | data.riksdagen.se |
| Beslutad lydelse | Skollag (2010:800) i konsoliderad form med framtida lydelser enligt SFS 2026:1242, 2026:1243 och 2026:1245 | data.riksdagen.se (Regeringskansliet/Lagrummet) |

Allt hämtades 2026-11-10. Den ursprungliga ändrings-SFS:en på svenskforfattningssamling.se gick inte att nå från arbetsmiljön.

## 2. Korpus och vad som saknas

- **Fokusgrupper:** huvudmän (kommuner, enskilda huvudmän) och huvudmännens organisationer (SKR, Almega, Idéburna skolors riksförbund). De två kategorierna hålls isär i all data.
- **Publicerade remissvar:** 29 svar från fokusgrupperna finns på regeringen.se: 26 kommuner, SKR, Almega Utbildning och Idéburna skolors riksförbund. 28 av avsändarna har minst en kodad utmaning (Kils kommun har ingen).
- **Saknas:** 6 remissvar, alla spontana yttranden. Regeringen.se publicerar bara svar från inbjudna remissinstanser.
  - 5 från enskilda huvudmän: Academedia AB, Frida Utbildning AB, Internationella Engelska Skolan i Sverige AB, Kunskapsskolan i Sverige AB och Stiftelsen Viktor Rydberg skolor.
  - 1 från Almega utbildningsföretagen.
  - Enskilda huvudmän saknas därför helt bland avsändarna. De opublicerade svaren har inte hämtats från andra källor.
- **OCR:** ett remissvar (Norrköpings kommun) är inskannat och OCR-tolkat. Citat därifrån är märkta `ocr: true`.

## 3. Från remissvar till datafil

1. **Kedja och korpus** (förstudie 1): remissida, remisslista och propositionens remissförteckning. Varje svar har klassats på avsändare. Se `research/remissanalys/kedjor.json` och `RAPPORT.md`.
2. **Utredningsförslag** (förstudie 1): de 80 förslagsrutorna i SOU 2025:18 med sida, matchade mot propositionens avsnitt. Matchningen är **redaktionell**, eftersom propositionen inte anger vilka SOU-förslag den avser. Se `pilot-betyg.json`.
3. **Segmentering** (förstudie 2): de 29 remissvaren delades i 714 passager. Varje passage har avsändare, sida och URL.
4. **Utmaningar** (förstudie 2): en språkmodell valde ut passager som beskriver en utmaning för huvudmannen och sparade ett ordagrant citat ur dem. Det gav 456 utmaningar, eller 440 efter att dubbletter inom samma avsändare tagits bort. Varje citat är kontrollerat mot källans text: 444 automatiskt mot pdftotext och 12 mot OCR-text, varav 10 även manuellt mot sidbilden. Se `utmaningar-betyg.json`.
5. **Omkodning** (Sprint 16 T2): utmaningstyp satt genom läsning mot åtta definitioner, kopplingsnivå, sakområde och skolform. Se `v2/`.
6. **Regelprövning** (T3): en och samma kodare prövade alla utmaningar med typen Otydlighet eller Likvärdighet mot den avgörande regeln. 11 utmaningar ändrades. Se `v2/andringslogg-utmaningstyp.json`.
7. **SFS-jämförelse**: SOU:ns föreslagna paragrafer (ur författningskommentaren) jämfördes med propositionens lagförslag och med beslutad lydelse. Jämförelsen anger textlikhet och ordagrann diff. Se `sfs-diff-betyg.json`.
8. **Namngivning**: för utmaningar som hör till ett propositionsavsnitt har avsändarens namn sökts i avsnittets text. Sökningen fångar fullt namn, kortform (SKR) och samordnade uppräkningar som "Falu, Motala och Söderhamns kommuner". I prop. 194 hoppas delarna om SOU 2025:19 över.
9. **Bygge**: `bygg-pilot.py` sätter ihop datafilen, och `validera-pilot.py` kontrollerar den.

## 4. Vad som är tolkning

| Fält | Hur det tagits fram | Märkning |
|---|---|---|
| Att en passage är en utmaning | Modellkodning | Hela korpusen. Granskas i `v2/granskning/` |
| Utmaningstyp (primär, sekundär) | Modellkodning genom läsning mot definitionerna | `tolkning: true` |
| Koppling med nivån `tolkad` | Modellkodning när remissvaret saknar egen hänvisning | `tolkning: true` |
| Koppling mellan utredningsförslag och propositionsavsnitt | Redaktionell matchning (förstudie 1) | `redaktionell: true`, visas som "Reformkartans koppling" |

Resten är mekaniskt härlett ur källtext:
- citat, sida och URL
- kopplingsnivåerna `förslag`, `avsnitt` och `kapitel` (remissvarets egen hänvisning)
- sakområde och skolform
- propositionens avvikelsetexter och deras exakta fras om överensstämmelse
- SFS-status och textlikhet
- namnträffar
- avsändarräkning

Kodarnas motiveringar finns i datafilen som spårbarhet men visas aldrig på sidan.

## 5. Taxonomi och avgörande regel

Utmaningstyper (exakt en primär, valfritt en sekundär):

| Utmaningstyp | Definition |
|---|---|
| Kostnader och finansiering | utgifter, ersättning, finansieringsprincipen, resursbehov i pengar |
| Tidplan och reformtakt | ikraftträdande, förberedelsetid, samtidiga reformer |
| Personal, kompetens och arbetsbelastning | bemanning, kompetensutveckling, lärares och rektorers arbetsbörda |
| System och teknik | digitala system, provplattform, infrastruktur, utrustning |
| Organisation och planering | schemaläggning, lokaler, genomförande i verksamheten, samordning mellan enheter |
| Otydlighet i förslaget | oklara begrepp, oklart ansvar, oklar tillämpning |
| Likvärdighet och konsekvenser för elever | effekter för elevgrupper, rättssäkerhet, likvärdig bedömning |
| Övrigt | inget av ovanstående (2,0 %) |

**Avgörande regel:** Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som Otydlighet i förslaget, även när elever eller vårdnadshavare nämns som de som ska förstå. Likvärdighet och konsekvenser för elever kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän.

**Kopplingsnivåer:**

| Nivå | Betydelse |
|---|---|
| `förslag` | Remissvarets hänvisning pekar ut exakt ett förslag |
| `avsnitt` | Hänvisningen pekar ut ett SOU-avsnitt med flera förslag |
| `kapitel` | Remissvaret anger bara kapitel. Ingen expansion till enskilda förslag |
| `tolkad` | Ingen egen hänvisning; koppling genom tolkning |
| `null` | Ingen koppling |

**Sakområde** är SOU-kapitlets rubrik, ordagrant ur innehållsförteckningen. Detaljer finns i `research/remissanalys/v2/taxonomi.md`.

## 6. Samstämmighet mellan kodare

- **Utmaningstyp:** fyra modellkodare med samma instruktion. 40 slumpvis valda utmaningar kodades av en femte, oberoende kodare. **35 av 40 fick samma primära typ, Cohens kappa 0,85.**
- **Systematisk skillnad:** en batchvis skillnad, där "svårt att förstå" hamnade under Likvärdighet i stället för Otydlighet, åtgärdades med den avgörande regeln i T3.
- **Urval och koppling:** att en passage är en utmaning, och den tolkade kopplingen, har inte dubbelkodats. Träffsäkerheten mäts i granskningen i `research/remissanalys/v2/granskning/`, där del 1 gäller träffsäkerhet och del 2 missade utmaningar.

## 7. Kända begränsningar

- **230 av 440 utmaningar saknar propositionsavsnitt.** De har ingen koppling, en koppling bara till kapitel, eller en koppling till förslag som propositionen inte behandlar i något avsnitt. De kan inte jämföras mot propositionen, och sidan anger antalet.
- **Förordningar är inte beslutade.** Förslag på förordningsnivå har status "ej i SFS per 2026-11-10". Regeringen beslutar förordningar och kan göra det senare.
- **Namngivning är inte bemötande.** "Avsändaren nämns i propositionens avsnitt" betyder bara att namnet förekommer i texten. Sidan bedömer inte om utmaningar är lösta eller om propositionen har tagit hänsyn till dem.
- **Textlikhet är inte saklig ändring.** Textlikhet i procent mellan SOU:ns och den beslutade lydelsen fångar också ordval och samordning med andra propositioner. Paragrafmatchningar med under 80 % likhet är flaggade för manuell granskning.
- **Avsnittsnivå:** 89 av 139 egna hänvisningar pekar på ett avsnitt med flera förslag.
- **Enskilda huvudmän saknas** (se avsnitt 2).

## 8. Bygga om datafilen

Kör från repo-roten:

```bash
python3 research/remissanalys/skript/bygg-pilot.py      # skriver pilot/utmaningar/data/utmaningar-betyg.json
python3 research/remissanalys/skript/validera-pilot.py  # 440 utmaningar, 28 avsändare, källor, rubriker, förbjudna ord
node research/remissanalys/skript/testa-pilotsida.js    # headless-test av sidan (Playwright), desktop och 380 px
```

- `bygg-pilot.py` läser bara incheckade filer, under `research/remissanalys/` och dess `arbetsfiler/`.
- Utdata är deterministisk, så ett bygge från en ren utcheckning ger en identisk fil.
- Arbetsfilerna (propositionsavsnittens text och innehållsförteckningar) togs fram en gång med `skript/v2/forbered_arbetsfiler.py` ur pdftotext-utdata av propositionerna.

## 9. Förhandsvisning: pilot-sync.sh

`pilot/` är exkluderad från GitHub Pages och når aldrig produktionsroten. Piloten visas bara under `https://reformer.leide.se/dev/utmaningar-pilot/`. Niklas kör synken.

```bash
./pilot-sync.sh --dry-run   # visar vad som skulle kopieras; ändrar ingenting
./pilot-sync.sh             # kopierar index.html och data/ till master:dev/utmaningar-pilot/, committar och pushar
./pilot-sync.sh --remove    # tar bort dev/utmaningar-pilot/ från master
```

Skriptet:
- kräver att man står på dev, med ren arbetskatalog och lokal dev lika med origin/dev
- arbetar mot master i ett tillfälligt worktree, så att man aldrig lämnar dev
- rör inget annat än `dev/utmaningar-pilot/`
- pushar bara som fast-forward

`commit.sh` tar aldrig bort något på master. Därför måste piloten tas bort med `--remove` när den inte längre ska visas.

## 10. Inför flytt till produktion

Flytt sker först efter Cecilias granskning. Piloten saknar medvetet två saker som ska läggas till vid flytt till produktion:

- **Cloudflare Web Analytics-snippet** före `</body>`, som alla produktionssidor har.
- **Webbtypsnitten** DM Sans och Source Serif 4 via Google Fonts. Piloten har inga externa beroenden och faller tillbaka på systemtypsnitt.

Dessutom: ta bort `noindex` och banderollen, lägg till sidan i fliknavigationen på alla sidor (varje HTML-fil är fristående) och ta bort förhandsvisningen med `./pilot-sync.sh --remove`.
