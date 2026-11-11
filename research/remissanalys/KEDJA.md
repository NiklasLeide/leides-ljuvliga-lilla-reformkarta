# Utmaningskartans kedja: per reform, parametrisk (Sprint 17)

Kedjan går från utredningsbetänkande och remissvar till datafilen `pilot/utmaningar/data/utmaningar-<id>.json`. Den används för sju reformer: `betyg`, `studiero`, `stod`, `tid`, `laroplaner`, `spraklig` och `tioarig`. Metoden beskrivs i `docs/utmaningskartan-metod.md` och datamodellen i `pilot/utmaningar/README.md`.

- Alla steg körs från repo-roten med reformens id som argument: `python3 research/remissanalys/kedja/<steg>.py <id>`.
- Inget steg läser filer utanför repot.
- Källstegen hämtar källor från nätet till `reformer/<id>/kallor/`. Den katalogen är en cache och checkas inte in (`.gitignore`). Samma sak gäller modellkodningens underlag och råsvar i `kallor/kodning/`.
- Alla andra mellanfiler och den sammanslagna modellkodningen checkas in under `reformer/<id>/`. Därför går allt efter kodningen att köra deterministiskt från en ren utcheckning.

## Filer

| Fil | Innehåll |
|---|---|
| `reformer/<id>.json` | Reformens konfiguration: kedjan med källor, PDF-adresser, sidintervall, delrubriker, lagar med egna ändrings-SFS och belägg, förordningar, fokusorganisationer, remissidekontroll, begränsningskoder, korrigeringar. Ett steg som behöver ett null-värde stoppar med fel. |
| `kedja/gemensamt.json` | Låst metod för alla reformer: utmaningstyper, avgörande regel, kopplingsnivåer, fokusgrupper, klassningslistor, stoppregler, förbjudna ord. |
| `kedja/KODINSTRUKTION.md` | Den enda kodinstruktionen (M1–M3, R1) med utdataformat. |
| `reformer/<id>/` | Mellanfiler (incheckade). `kodning/` innehåller den sammanslagna modellkodningen. |
| `reformer/<id>/kallor/` | Nedladdade PDF:er, sidtext, OCR-bilder och kodningens underlag och råsvar (cache, inte incheckad). |

## Stegen i ordning

Typer av steg:
- **N** = källsteg, kräver nät
- **D** = deterministiskt
- **M** = modellkodat (tolkning, incheckat)
- **R** = redaktionellt (manuellt, incheckat)

| # | Typ | Kommando | Läser | Skriver |
|---|---|---|---|---|
| K1 | N | `kedja/hamta.py <id> [--om]` | config | `kallor/` (SOU-, prop-PDF:er, remissida, SFS-text) |
| K2 | D¹ | `kedja/extrahera_sou.py <id>` | `kallor/sou/` | `sou-innehall.json`, `sou-forslag.json`, `sou-paragrafer.json` |
| K3 | D¹ | `kedja/extrahera_prop.py <id>` | `kallor/prop/` | `prop-avsnitt.json`, `propositionsavsnitt-text.json`, `propositioner-innehall.json`, `prop-lagtext.json` |
| K4 | D¹ | `kedja/extrahera_sfs.py <id>` | `kallor/sfs/`, `sou-paragrafer.json`, config `lagar[].andringar` | `sfs.json` (bara paragrafversioner med "Lag (…)" från reformens egna SFS-nummer, plus `paragrafer_i_lagen`) |
| K5 | D¹ N | `kedja/extrahera_remissvar.py <id>` | `kallor/prop/`, `kallor/remisssida.html` (hämtar remissvarens PDF:er om de saknas; OCR med tesseract för inskannade) | `remissvar.json` |
| K6 | D | `kedja/segmentera.py <id>` | `remissvar.json`, `sou-innehall.json`, `sou-forslag.json` | `passager.json` |
| M1 | M | enligt `KODINSTRUKTION.md` M1. `kedja/kodning.py <id> m1-underlag`, sedan `m1-ihop` | `passager.json` | `kodning/utmaningar.json`, `kodning/dubbelidentifiering.json` (M1b: 40 passager om minst 100 tecken, oberoende kodare) |
| M2 | M | M2, M2b och M2c. `kodning.py <id> m2-underlag`/`m2-ihop`, sedan `m2c-underlag`/`m2c-ihop` | utmaningar utan dubbletter (se K7) | `kodning/utmaningstyp.json`, `kodning/dubbelkodning.json` (M2b: 40 utmaningar), `kodning/regelprovning.json` |
| M2d | M | bara betyg (regel A4). `kodning.py <id> m2d-underlag`/`m2d-ihop`, efter M2c | utmaningar utan dubbletter, typ efter M2c | `kodning/dubbelkodning-efter-regelprovning.json` (80 utmaningar, oberoende typning jämförd med typ efter regelprövning) |
| M3 | M | M3. `kodning.py <id> m3-underlag`/`m3-ihop` | `sou-forslag.json`, utmaningar utan egen hänvisning | `kodning/tolkad-koppling.json` |
| R1 | R | R1 | `sou-forslag.json`, `prop-avsnitt.json` | `forslag-propositionsavsnitt.json` |
| K7 | D | `kedja/utmaningar.py <id>` | K2, K5, K6, M1–M3 | `utmaningar.json` (citatkontroll, dubbletter, kopplingsnivå, skolform, typ) |
| K8 | D | `kedja/sfs_diff.py <id>` | K2, K3, K4, K6, M1, M3 | `sfs-diff.json` |
| K9 | D | `kedja/avvikelser.py <id>` | `prop-avsnitt.json`, R1 | `avvikelser.json` (formuleringen om överensstämmelse som den står, A3) |
| K10 | D | `kedja/bygg.py <id>` | K2, K3, K5, K7–K9, `kodning/` (M2c; samstämmighet ur M1b, M2b, M2d), R1, config, `gemensamt.json` | `pilot/utmaningar/data/utmaningar-<id>.json` |
| K11 | D | `kedja/stoppregler.py <id>` | K7, K5, M1b, M2, M2b, M2c, M2d | (kod 1 = stopp) |
| K12 | D | `skript/validera-pilot.py <id>` | datafilen, `utmaningar.json`, `propositioner-innehall.json`, config | (kod 1 = fel). Antal kontrolleras mot mellanfilen, och varje citat ska ha `citatkontroll.ok = true`. |

¹ K2–K5 är deterministiska givet `kallor/`. Eftersom `kallor/` inte checkas in kräver de nät vid första körningen (K1). Deras utdata checkas in.

`kodning.py` skriver underlagen (`m1-batch-<n>.json`, `m1-dubbel.json`, `m2-batch-<n>.json`, `m2-dubbel.json`, `m2c-underlag.json`, `m2d-underlag.json`, `m3-batch-1/2.json`, `m3-forslag.json`) till `kallor/kodning/`. Där läser `*-ihop` kodarnas svar (`m1-resultat-<n>.json`, `m1-dubbel-resultat.json` och så vidare). Slumpfröna står i skriptet: `SEED_ID` 20261201, `SEED_TYP` 20261202 och `SEED_TYP_EFTER` 20261203.

**Kör alla deterministiska steg för en reform (K6–K10):** `python3 research/remissanalys/kedja/kor.py <id>`. För betyg gör `python3 research/remissanalys/skript/bygg-pilot.py` samma sak (omslag).

### Efter alla reformer

| # | Typ | Kommando | Läser | Skriver |
|---|---|---|---|---|
| Ö | D | `kedja/oversikt.py` (inget argument) | de sju datafilerna i fast ordning | `pilot/utmaningar/data/oversikt.json` (stoppar om `meta.reform.id` eller utmaningstyperna avviker) |
| K13 | D | `node skript/testa-pilotsida.js` | `pilot/utmaningar/index.html`, `oversikt.json` och alla sju datafiler | (Playwright, headless, 1280 och 375 px; alla förväntade värden härleds ur datafilerna; 323 kontroller 2026-11-11) |
| G | D | `kedja/granskning.py <id>` eller `alla` | datafilen, `passager.json`, `kodning/utmaningar.json` | `research/remissanalys/granskning/granskning-<id>.csv` (betyg 40 + 20, övriga 15 + 5 rader, fasta slumpfrön per reform) |

### Ordningsberoenden

- M2 kodar utmaningar utan dubbletter. Dubbletterna markeras mekaniskt i K7, så K7 körs en gång efter M1 för att få urvalet och igen efter M2–M3.
- M2d körs efter M2c, eftersom den jämför med typen efter regelprövning.
- M3 gäller utmaningar vars passage saknar egen hänvisning. Det framgår av `passager.json` från K6. `m3-underlag` kräver att M2 och K7 är körda.
- K8 och K10 kräver att alla kodfiler finns.
- `oversikt.py` körs när alla sju datafiler är byggda, och `testa-pilotsida.js` efter `oversikt.py`.

## Stoppregler

1. **Övrigt > 10 %** av utmaningarna (primär typ efter regelprövning, utan dubbletter) leder till att reformen stoppas och rapporteras (K11).
2. **Samstämmighet i typning < 80 %** i dubbelkodningen (M2b) leder till att reformen stoppas och rapporteras (K11). **Undantag för betyg (regel A4, Sprint 17):** när `kodning/dubbelkodning-efter-regelprovning.json` finns mäts typningen i stället på de 80 utmaningarna efter regelprövning, med gränsen 75 %. M2b-måttet skrivs då ut som information. Filen finns bara för betyg, där utfallet är 71/80, mot 31/40 i M2b.
3. **Typnamn** som inte är de åtta i `gemensamt.json` leder till stopp.
4. **Flaggas men stoppar inte:** samstämmighet för identifiering (M1b) under 80 %, och färre än fem publicerade remissvar från fokusgrupperna.
5. **Citat utan automatisk träff** i källsidans text redovisas av K7. De märks `citatkontroll.metod: "manuell"`, `ok: null` och ska kontrolleras mot sidbilden innan publicering. OCR-citat som är manuellt kontrollerade listas i config `korrigeringar.ocr_citat_manuellt_kontrollerade`. Listan är tom i alla sju reformer, eftersom alla citat har automatisk träff.
6. **Förbjudna ord** ("löst", "kvarstår", "bemött tillräckligt") i motiveringar gör att K10 stoppar, utom när en loggad omformulering finns i config `korrigeringar.motivering_omformulerad`. K12 kontrollerar hela datafilen, utom ordagrann källtext.
7. **Saknat konfigurationsvärde** (null) gör att steget stoppar med namnet på värdet.
8. Ingen omkodning görs för att klara gränserna. Avvikelser rapporteras.

## Regressionstest (alla sju reformer)

```bash
git clone <repo> /tmp/ren && cd /tmp/ren && git checkout <commit>
for r in betyg studiero stod tid laroplaner spraklig tioarig; do
  rm research/remissanalys/reformer/$r/{passager,utmaningar,sfs-diff,avvikelser}.json   # deterministiska utdata
  python3 research/remissanalys/kedja/kor.py $r || break
done
rm pilot/utmaningar/data/oversikt.json && python3 research/remissanalys/kedja/oversikt.py
git status --short && git diff --exit-code                       # inga ändrade eller saknade filer
for r in betyg studiero stod tid laroplaner spraklig tioarig; do
  python3 research/remissanalys/kedja/stoppregler.py $r
  python3 research/remissanalys/skript/validera-pilot.py $r
done
python3 research/remissanalys/kedja/granskning.py alla && git diff --exit-code -- research/remissanalys/granskning/
node research/remissanalys/skript/testa-pilotsida.js
```

Körning 2026-11-11 från en ren klon av `7cbd0c0`:
- Datafilerna, mellanfilerna, `oversikt.json` och granskningsfilerna blev byte-identiska.
- `validera-pilot.py` gick igenom för alla sju.
- `stoppregler.py` och `testa-pilotsida.js` kördes i arbetskatalogen, som var ren och lika med `7cbd0c0`. `stoppregler.py` gav OK utan flaggor för alla sju, och `testa-pilotsida.js` gav 323/323. I klonen hittade Node inte modulen `playwright`.

## Reformspecifikt och sådant som inte är generaliserat

- **Urvalet till SFS-jämförelsen (K8)** är alla förslag i alla sju reformer, även betyg (config `sfs_urval: "alla"` sedan omkodningen i A4). Koden har kvar Sprint 16:s regel för `sfs_urval: "kodade"`, men ingen reform använder den.
- **Flera lagar** stöds (tid, tioarig): `lagar` och `sou.forfattningskommentar` kan vara listor, och paragrafraderna får `lag`.
- **Layoutavvikelser** i SOU och propositioner ligger i config, bland annat `sou.ruta_rubriker`, `ruta_over_sidbrytning`, `ruta_slutrader`, `pdf_sidforskjutning`, `forfattningskommentar.radkorrigeringar/inline_rubriker/borja_vid_rubrik`, `propositioner[].lagforslag_rubrik`, `flerradiga_delrubriker`, `layout.vanstermarginal_pt` och `layout.lagtext_tolerant`. Se respektive skript för semantik.
- **Delade propositioner:** andra utredningars delar hoppas över vid namnsökningen (config `propositioner[].hoppa_delar_vid_namnsokning`, `hoppade_delar_beskrivning`).
- **Förordningsmarkören** (`forordning_markor`) och dess beskrivning är reformspecifika och ligger i config: "betyget 4" för betyg och "ogiltig frånvaro" för studiero; övriga har ingen.
- **R1** (förslag → propositionsavsnitt) är manuell ämnesmatchning, inte ett skript.
- **Manuellt kontrollerade OCR-citat och omformulerade motiveringar** är listor per reform i config. De är tomma i alla sju.
- **Klassningslistorna** (enskilda huvudmän, myndigheter) i `gemensamt.json` är extern kunskap och kan behöva kompletteras per remiss.
- **Sökvägar:** alla sju datafiler har `byggd_av` = `kedja/bygg.py` och `belagg` = `reformer/<id>/sfs-diff.json`. Config-nyckeln `legacy_sokvagar` används inte längre av någon reform, men `bygg.py` läser den fortfarande om den finns.
- **Extra fokusgrupper per reform** (tioarig: Friskolornas riksförbund) läggs i config `fokusorganisationer` och `extra_fokusgrupper`. `gemensamt.json` ändras inte. En organisation som inte hör till remissen är null i `fokusorganisationer` (tioarig: `almega`).
- **Egna ändrings-SFS (Sprint 17 A1):**
  - Config `lagar[].andringar` är de SFS-nummer som riksdagsbeslutet om reformens egna propositioner ledde till. Vart och ett är belagt i `lagar[].andringar_kalla` (`sfs`, `prop`, `text`, `url`). Ett nummer som inte kan beläggas tas inte med och förklaras i `lagar[].andringar_anm`.
  - Riksdagens dokumentstatus saknar SFS-nummer, så beläggen bygger på den konsoliderade texten ("Lag (…)", ikraftträdande, övergångsblock), betänkandets beslutstext och propositionen.
  - K4 sparar bara paragrafversioner från dessa nummer, plus `paragrafer_i_lagen` med bara beteckningar. K8 tar beslutad lydelse bara därifrån. En paragraf som finns i lagen men saknar version från egna SFS blir `ej med` med `status_kalla`. Textlikhet mot en annan paragraf används bara när paragrafnumret saknas helt i lagen.
- **SFS-status null med förklaring** ges i två fall: när förordningsförslag saknar avgörande textmarkör (eller markören har träffar), och när SOU:n inte återger paragraftexten (tioarig). Inget obelagt "ej i SFS" sätts.
- **Remissidekontroll (A2)** står i config `remissida_kontroll` (`datum`, `regel`, `tillagda_yttranden`, `ej_med_avstaenden`). K10 för över den till datafilens `meta.remissida_kontroll` och `meta.publicerade_avstaenden`, och `ej_med_avstaenden` ger status `avstått` i `meta.organisationer`.
- **Begränsningskoder** står i config `begransningar` och förs oförändrade till `meta.begransningar`. Texterna per kod står i `pilot/utmaningar/index.html`, och en okänd kod loggas som konsolfel.
- **Regel A4** (typning efter regelprövning, 80 utmaningar, 75 %) gäller bara betyg. Den styrs av att filen `kodning/dubbelkodning-efter-regelprovning.json` finns, inte av config.
- **Reformlistan** är hårdkodad i fast ordning i `oversikt.py`, `granskning.py` (med slumpfrön per reform) och `testa-pilotsida.js`. En ny reform kräver ändring i alla tre.
- **spraklig** saknar id i `data/reforms.json`.
