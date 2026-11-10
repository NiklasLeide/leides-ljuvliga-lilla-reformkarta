# Spike 2: Huvudmännens utmaningar mot beslut (pilot betyg) — rapport

**Datum:** 2026-11-10 · **Status:** avslutad spike, inga ändringar i publik data eller UI
**Kedja:** SOU 2025:18 → remiss U2025/00401 → Prop. 2025/26:197 (+ del av Prop. 2025/26:194) → bet. 2025/26:UbU26 → rskr. 2025/26:335 (2026-06-09)
**Filer:**
- `utmaningar-betyg.json` (steg 2, 3, 5)
- `sfs-diff-betyg.json` (steg 4)
- `granskning-urval.md` (steg 6)
- `skript/utmaningar/` (skript, den öppna kodningen och den tolkade kopplingen)

---

## 1. Sammanfattning

- **456 utmaningar** kodades i 29 publicerade remissvar. 440 räknas, efter att 16 dubbletter inom samma avsändare tagits bort.
  - Stockholms remissvar innehåller två tjänsteutlåtanden som upprepar varandra nästan ordagrant.
  - Utmaningarna kommer från 25 kommuner, SKR, Almega Utbildning och Idéburna skolors riksförbund.
- **Remissvar från enskilda huvudmän saknas helt, 6 st:** Academedia AB, Frida Utbildning AB, Internationella Engelska Skolan i Sverige AB, Kunskapsskolan i Sverige AB, Stiftelsen Viktor Rydberg skolor och Almega utbildningsföretagen. Alla är spontana yttranden, som regeringen.se inte publicerar. Fokusgruppen "enskilda huvudmän" har därför **0** utmaningar i datan. Det beror på hur källan publiceras, inte på vad de skrev.
- **Koppling till utredningsförslag:**
  - 38,6 % förankrade (remissvaret anger själv avsnitt, kapitel, rubrik eller paragraf)
  - 36,1 % tolkade
  - 25,2 % utan koppling
- **SFS-diff:** 36 av 93 unika paragrafer (39 %) matchade automatiskt, det vill säga på nummer och med minst 80 % textlikhet både i propositionen och i beslutad lydelse. 56 är flaggade `manuell_granskning`.
- **Avsändaren namnges i propositionens skäl** i det kopplade avsnittet för 92 av de 253 utmaningar där en sådan sökning var möjlig (36 %).
- **Största risken:** SFS-diffens status "ändrad" sätts på 92 av 93 paragrafer och skiljer inte mellan ändringar i sak och redaktionella ändringar eller samordning med andra propositioner. Status blir därmed nästan informationslös, utom genom den ordagranna diffen. Se avsnitt 10.

## 2. Kategorier och definitioner

Den öppna kodningen av hela korpusen gav 300 öppna koder. Jag slog ihop dem till åtta kategorier. Tilldelningen från öppen kod till kategori görs med ordnade nyckelordsregler, som finns i `kategorier[].regel` och i `skript/utmaningar/kategorier.py` så att de går att granska. Varje kategorisering har `tolkning: true`.

| Kategori | Definition | Antal |
|---|---|---|
| Provgenomförande och system | Utmaningar med att genomföra nationella slutprov och med de tekniska och administrativa system som krävs (provplattform, IT, lokaler, rättning, antagningssystem). | 75 |
| Tidplan och reformtakt | Utmaningar som gäller ikraftträdande, tid för införandet eller samtidighet och samordning med andra reformer och utredningar. | 71 |
| Otydlighet och kommunikation | Utmaningar som beror på otydliga regler, modeller eller ansvar, eller på behovet att förklara och informera om systemet och få stöd i god tid. | 65 |
| Planering och verksamhet | Utmaningar för huvudmannens planering och verksamhet i övrigt: gymnasieantagning och dimensionering, programutbud, introduktionsprogram, uppföljning och kvalitetsarbete. | 51 |
| Komvux | Utmaningar som huvudmannen pekar ut för kommunal vuxenutbildning: provtillfällen, flexibilitet, utbud, elevflöden och komvux uppdrag. | 50 |
| Kostnader och finansiering | Utmaningar som gäller kostnader för huvudmannen, finansiering, statsbidrag och resurser för genomförandet. | 48 |
| Bedömningssamråd och små enheter | Utmaningar med att organisera bedömningssamråd och kalibrering där skolenheter, program eller ämneslärargrupper är små. | 47 |
| Personal, arbetsbelastning och kompetens | Utmaningar som gäller lärares och annan personals tid, arbetsbelastning, kompetensutveckling och kompetensförsörjning. | 33 |
| **Summa** | | **440** |

## 3. Antal per kategori och fokusgrupp

| Kategori | Kommuner (25) | Enskilda huvudmän | SKR | Almega | Idéburna |
|---|---|---|---|---|---|
| Provgenomförande och system | 60 | — | 6 | 5 | 4 |
| Tidplan och reformtakt | 58 | — | 6 | 6 | 1 |
| Otydlighet och kommunikation | 58 | — | 4 | 3 | 0 |
| Planering och verksamhet | 45 | — | 6 | 0 | 0 |
| Komvux | 40 | — | 7 | 3 | 0 |
| Kostnader och finansiering | 40 | — | 5 | 2 | 1 |
| Bedömningssamråd och små enheter | 42 | — | 2 | 2 | 1 |
| Personal, arbetsbelastning och kompetens | 29 | — | 3 | 1 | 0 |
| **Summa** | **372** | **0 (6 svar ej publicerade)** | **39** | **22** | **7** |

Huvudmän (kommuner, enskilda huvudmän) och huvudmannaorganisationer (SKR, Almega, Idéburna) hålls isär i fältet `grupp`. Kommunerna står för 85 % av utmaningarna, bland annat för att de är 25 av 28 avsändare. Antalet speglar också hur långa remissvaren är: Gislaved har 55 sidor och 27 utmaningar.

## 4. Kopplingar till utredningsförslag

| Koppling | Antal | Andel |
|---|---|---|
| förankrad (remissvaret anger själv avsnitt, kapitel, rubrik eller paragraf) | 170 | 38,6 % |
| tolkad (`tolkning: true`, modellkodning med motivering per utmaning) | 159 | 36,1 % |
| null (ingen enskild rimlig koppling: allmän reformtakt, kostnader i allmänhet, informationsbehov, gymnasieantagningens tidpunkt) | 111 | 25,2 % |

- **Förankrad** bygger på att remissvaren ofta följer SOU:ns numrering, till exempel "13.3 Meritvärdering i komvux …" eller "Kapitel 16". Rubriken matchas mot SOU:ns innehållsförteckning, och en paragrafhänvisning ("16 kap. 29 §") matchas via SOU:ns författningskommentar.
- **Svaghet:** en hänvisning på kapitelnivå kopplar till *alla* förslag i kapitlet. Därför är 77 av 80 förslag kopplade till minst en utmaning.
- **Tolkad:** en första maskinell TF-IDF-variant gav för många felträffar (t.ex. "Till Regeringen Utbildningsdepartementet" → F52) och användes inte. Den tolkade kopplingen gjordes i stället av en modell med konservativ instruktion, och den väljer hellre null än en svag gissning. Motiveringen sparas per utmaning.

## 5. SFS-diff (steg 4)

**Källor:**
- **SOU:ns föreslagna lydelse:** författningskommentaren, avsnitt 22.1, som återger varje föreslagen paragraf i sin helhet och anger "Bestämmelsen behandlas i avsnitt …".
- **Propositionens lagförslag:** kapitel 2 i prop. 197 och 194, tvåspaltig layout som tolkats via ordkoordinater (`pdftotext -bbox`).
- **Beslutad lydelse:** skollagen i konsoliderad form från riksdagens öppna data ("Källa: Regeringskansliet / Lagrummet", ändrad t.o.m. SFS 2026:1636, hämtad 2026-11-10). Den innehåller de framtida lydelserna med markeringen "/Träder i kraft I:2028-07-02/" och "Lag (2026:1243)".
- **Avvikelse från briefen:** själva ändrings-SFS:en på svenskforfattningssamling.se gick inte att nå. **Host som behövs: `svenskforfattningssamling.se`.** I stället för att stoppa steg 4 använde jag riksdagens konsoliderade SFS-text, som är nåbar och innehåller de beslutade lydelserna. Om du kräver original-SFS: lägg till hosten i miljön och kör `sfs_diff.py` mot den.

**Paragrafmatchning:** 93 unika paragrafer, inklusive ikraftträdande- och övergångsbestämmelserna som egen enhet.

| | Antal | Andel |
|---|---|---|
| Matchade automatiskt både i propositionen och i SFS (samma nummer och likhet ≥ 0,80) | 36 | 39 % |
| Matchade automatiskt i SFS | 39 | 42 % |
| Matchade automatiskt i propositionen | 62 | 67 % |
| SFS-match bara via textlikhet (annat nummer) | 25 | 27 % |
| `manuell_granskning: true` | 56 | 60 % |

**Statusfördelning**

| Nivå | ändrad | oförändrad | ej i SFS per 2026-11-10 | ej lagtext | ej med |
|---|---|---|---|---|---|
| Förslag med utmaning (77) | 36 | 2 | 31 | 8 | 0 |
| Unika paragrafer (93) | 92 | 1 | — | — | 0 |

- **"ej i SFS per 2026-11-10"** gäller förslag som ingen paragraf i skollagskommentaren hänvisar till, alltså förslag på förordningsnivå. Underlaget är konsoliderade texter av gymnasieförordningen, skolförordningen, högskoleförordningen, vuxenutbildningsförordningen och förordningen om fjärde tekniskt år, hämtade 2026-11-10. Ingen av dem innehåller den nya betygsskalan (0 träffar på "betyget 4").
- **"ej lagtext"** gäller uppdrag och myndighetsansvar.
- **"ändrad"** gäller nästan alla paragrafer. Ord-diffen sparas ordagrant (`diff_sou_mot_beslutad`). Exempel:
  - 11 kap. 20 §: "på en skala 1–10" → "på skalan 1-10".
  - Ikraftträdande: "1 januari 2027" i SOU → "2 juli 2028" i SFS 2026:1243.

## 6. Bemötande i propositionen (steg 5)

Jag sökte efter avsändarens namn i propositionernas avsnitt "Skälen för regeringens …". Sökningen omfattade alla avsnitt i prop. 197 och avsnitt 6.7–6.8 i prop. 194. Den hittar kortformer (SKR) och samordnade uppräkningar ("Falu, Motala och Söderhamns kommuner"). Totalt fick jag 50 namnträffar.

| `bemott_namngiven` | Antal | Förklaring |
|---|---|---|
| true | 92 | avsändaren namnges i skälen i ett propositionsavsnitt som utmaningens förslag hör till |
| false | 161 | inte namngiven där |
| null | 187 | utmaningen saknar koppling, eller förslaget behandlas inte i något propositionsavsnitt, så ingen avsnittsvis sökning är möjlig |

**Andel namngivna:** 92 av 253 sökbara utmaningar (36 %). Namnträffar i *andra* skäl-avsnitt sparas separat i `namngiven_i_ovriga_skal`. Fältet anger bara om namnet förekommer. Det säger ingenting om innehållet.

## 7. Citatkontroll

Alla **456 citat** kontrollerades **automatiskt**. Citatet, med blanksteg och bindestreck normaliserade, måste finnas i källsidans text för den angivna sidan:
- 444 kontrollerades mot pdftotext.
- 12 kontrollerades mot OCR-text (Norrköpings kommun, `ocr: true`).

Av OCR-citaten kontrollerades **10 även manuellt** mot sidbilden (s. 1–2). Alla stämde. 2 OCR-citat (s. 3) är bara kontrollerade mot OCR-texten.

Kodarna kontrollerade dessutom att varje citat är en exakt delsträng av sin passage. Citaten U296/U297 är delar av samma mening över en sidbrytning.

## 8. Saknade remissvar

6 svar saknas. Alla är spontana yttranden som inte publiceras på regeringen.se, och enligt briefen hämtades de inte från andra källor:
- 5 från enskilda huvudmän: Academedia AB, Frida Utbildning AB, Internationella Engelska Skolan i Sverige AB, Kunskapsskolan i Sverige AB och Stiftelsen Viktor Rydberg skolor.
- 1 från Almega utbildningsföretagen.

Alla 29 svar från inbjudna fokusgruppsinstanser fanns publicerade. Kristianstads kommun publiceras som "Kristianstad kommun", och URL:en löstes via remissidan.

## 9. Föreslagen datamodell för v1

En fil per reform, som laddas när användaren klickar. Utmaningen är minsta enhet och refererar till förslagsraderna i matrisen från spike 1 (`F01`…). Lagtextdiffen lagras per paragraf och refereras från förslagen.

```jsonc
// data/utmaningar/<reform-id>.json
{
  "reform_id": "betyg",
  "kategorier": [{"id": "prov_system", "namn": "...", "definition": "..."}],   // ≤ 8, fastställda manuellt
  "utmaningar": [{
    "id": "U0xx", "avsandare": "…",
    "grupp": "huvudmannaorganisation", "fokusgrupp": "skr",
    "citat": "...", "kalla": {"text": "Remissvar … s. 7", "url": "..."}, "ocr": false,
    "kategori": "prov_system", "tolkning": true,
    "koppling": {"typ": "förankrad|tolkad|null", "forslag": ["F64"], "grund": "..."},
    "namngiven_i_skal": {"varde": true, "citat": "...", "kalla": {"text": "Prop. … s. 82", "url": "..."}}
  }],
  "saknade_remissvar": [{"avsandare": "...", "grupp": "huvudman", "skal": "spontant yttrande, ej publicerat"}],
  "lagtext": {                       // per paragraf, refereras från förslagen
    "11 kap. 20 §": {"sou": {"text","kalla"}, "proposition": {"text","kalla"}, "beslutad": {"text","sfs","ikraft","kalla"},
                     "status": "ändrad", "diff": [{"op","fore","efter"}], "manuell_granskning": false}
  },
  "forslag_till_lagtext": {"F01": ["11 kap. 20 §", "…"]}
}
```

**Rekommendationer:**
1. **Visa SFS-status som diff, inte som etikett.** "ändrad" är för grov. Om en etikett behövs bör den skilja "redaktionell" från "i sak", men den skillnaden går inte att göra mekaniskt. Antingen granskas den manuellt (93 paragrafer per reform) eller så visas bara diffen.
2. **Räkna utmaningar per avsändare, inte per citat.** Annars väger långa remissvar tyngst.
3. **Visa saknade remissvar uttryckligen** ("5 enskilda huvudmän svarade, svaren är inte publicerade"), så att frånvaron inte läses som tystnad.
4. **Kapitelhänvisningar** bör ge koppling till kapitlet, inte till varje förslag i kapitlet.

## 10. Risker

1. **SFS-statusen är nästan tom på information.** 92 av 93 paragrafer blir "ändrad". Ordagrann jämförelse fångar också ordval ("en skala" → "skalan"), samordning med propositionerna 194, 195 och 198 (UbU26) och ändrade ikraftträdanden. Utan manuell klassning kan en läsare tro att alla förslag ändrades i sak. *Detta är den största risken.*
2. **Själva identifieringen och kategoriseringen av utmaningar är modelltolkning.** Fyra kodare, en per batch, kodade öppet utan gemensam kodbok. Gränsdragningen mellan "utmaning för huvudmannen" och "allmän synpunkt eller elevkonsekvens" kan därför skilja mellan batcherna. Granskningsurvalet (25) är till för att mäta detta, och det är inte gjort än.
3. **Systematisk lucka:** alla enskilda huvudmän saknas. En visualisering av "huvudmännens utmaningar" blir i praktiken kommunernas, SKR:s, Almegas och Idéburnas.
4. **Kopplingsgranularitet:** förslag knyts till paragrafer på avsnittsnivå, och kapitelhänvisningar knyter till alla förslag i kapitlet. Det blåser upp vilka förslag som "har utmaningar" (77 av 80).
5. **PDF-tolkningen av propositionens tvåspaltiga lagförslag är skör.** Paragrafrubriker som delas över rader gör att paragrafer slås ihop (t.ex. 29 kap. 19 c §). Dessa fångas av flaggan `manuell_granskning`, men propositionstexten för dem är opålitlig.
6. **Beslutad lydelse kommer från konsoliderad text** (riksdagen/Lagrummet) och inte från original-SFS (svenskforfattningssamling.se var inte nåbar).
7. **"bemott_namngiven" kan läsas som "bemött i sak".** Fältnamnet bör bytas i v1 (till exempel `namngiven_i_skal`) för att undvika feltolkning.

## 11. Avvikelser och process

- **Push till dev:** förutsättningen saknades först (research/ fanns inte på dev och var inte exkluderad). Med Niklas uttryckliga tillstånd gjordes commit `5a31e29` (`_config.yml` exkluderar `research`), med fast-forward-push `c3764fe..5a31e29` till dev. Spike 2 committas direkt på dev.
- **`commit.sh` användes inte.** Den pushar även en preview-synk till master, och instruktionen var "aldrig push till master". Jag använde bare `git commit` och `git push origin HEAD:dev`, med enbart fast-forward. CHANGELOG.md uppdaterades inte, eftersom briefen bara tillåter ändring i PROJECT_STATUS.md.
- **Steg 4** använde riksdagens konsoliderade SFS i stället för att stoppa (se avsnitt 5).
- **Arbetsfördelning:** den öppna kodningen (4 parallella modellagenter) och den tolkade kopplingen (2 agenter) är delegerade. Deras utdata ligger ordagrant i `skript/utmaningar/oppen-kodning.json` och `tolkad-koppling.json`.
