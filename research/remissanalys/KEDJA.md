# Utmaningskartans kedja: per reform, parametrisk (Sprint 17 T1)

Kedjan går från utredningsbetänkande och remissvar till datafilen `pilot/utmaningar/data/utmaningar-<id>.json`.

- Alla steg körs från repo-roten med reformens id som argument: `python3 research/remissanalys/kedja/<steg>.py <id>`.
- Inget steg läser filer utanför repot.
- Källstegen hämtar källor från nätet till `reformer/<id>/kallor/`. Den katalogen är en cache och checkas inte in (`.gitignore`).
- Alla andra mellanfiler och all modellkodning checkas in under `reformer/<id>/`. Därför går allt efter kodningen att köra deterministiskt från en ren utcheckning.

## Filer

| Fil | Innehåll |
|---|---|
| `reformer/<id>.json` | Reformens konfiguration: kedjan med källor, PDF-adresser, sidintervall, delrubriker, lagar och förordningar, korrigeringar. Mallar har `status: "mall …"` och null för okända värden; ett steg som behöver ett null-värde stoppar med fel. |
| `kedja/gemensamt.json` | Låst metod för alla reformer: utmaningstyper, avgörande regel, kopplingsnivåer, fokusgrupper, klassningslistor, stoppregler, förbjudna ord. |
| `kedja/KODINSTRUKTION.md` | Den enda kodinstruktionen (M1–M3, R1) med utdataformat. |
| `reformer/<id>/` | Mellanfiler (incheckade). `kodning/` innehåller modellkodningen. |
| `reformer/<id>/kallor/` | Nedladdade PDF:er, sidtext och OCR-bilder (cache, inte incheckad). |

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
| K4 | D¹ | `kedja/extrahera_sfs.py <id>` | `kallor/sfs/`, `sou-paragrafer.json` | `sfs.json` |
| K5 | D¹ N | `kedja/extrahera_remissvar.py <id>` | `kallor/prop/`, `kallor/remisssida.html` (hämtar remissvarens PDF:er om de saknas; OCR med tesseract för inskannade) | `remissvar.json` |
| K6 | D | `kedja/segmentera.py <id>` | `remissvar.json`, `sou-innehall.json`, `sou-forslag.json` | `passager.json` |
| M1 | M | enligt `KODINSTRUKTION.md` M1 | `passager.json` | `kodning/utmaningar.json` |
| M2 | M | M2 (+ M2b, M2c) | utmaningar (utan dubbletter, se K7) | `kodning/utmaningstyp.json`, `kodning/dubbelkodning.json`, `kodning/regelprovning.json` |
| M3 | M | M3 | `sou-forslag.json`, utmaningar utan egen hänvisning | `kodning/tolkad-koppling.json` |
| R1 | R | R1 | `sou-forslag.json`, `prop-avsnitt.json` | `forslag-propositionsavsnitt.json` |
| K7 | D | `kedja/utmaningar.py <id>` | K2, K5, K6, M1–M3 | `utmaningar.json` (citatkontroll, dubbletter, kopplingsnivå, skolform, typ) |
| K8 | D | `kedja/sfs_diff.py <id>` | K2, K3, K4, K6, M1, M3 | `sfs-diff.json` |
| K9 | D | `kedja/avvikelser.py <id>` | `prop-avsnitt.json`, R1 | `avvikelser.json` |
| K10 | D | `kedja/bygg.py <id>` | K2, K3, K5, K7–K9, M2c, R1, config, `gemensamt.json` | `pilot/utmaningar/data/utmaningar-<id>.json` |
| K11 | D | `kedja/stoppregler.py <id>` | K7, M2, M2b, M2c | (kod 1 = stopp) |
| K12 | D | `skript/validera-pilot.py` | datafilen | (kod 1 = fel) — **bara betyg** (antal 440/28 hårdkodade) tills vidare |
| K13 | D | `node skript/testa-pilotsida.js` | `pilot/utmaningar/index.html` + datafilen | (Playwright, headless) — **bara betyg** tills sidan blir reformväljande (Sprint 17 T8) |

¹ K2–K5 är deterministiska givet `kallor/`. Eftersom `kallor/` inte checkas in kräver de nät vid första körningen (K1). Deras utdata checkas in.

**Kör alla deterministiska steg från repot (K6–K10):** `python3 research/remissanalys/kedja/kor.py <id>`.

För betyg gör `python3 research/remissanalys/skript/bygg-pilot.py` samma sak. Det är ett omslag och den sökväg som datafilens `meta.byggd_av` anger.

### Ordningsberoenden

- M2 kodar utmaningar utan dubbletter. Dubbletterna markeras mekaniskt i K7, så K7 körs en gång efter M1 för att få urvalet och igen efter M2–M3.
- M3 gäller utmaningar vars passage saknar egen hänvisning. Det framgår av `passager.json` från K6.
- K8 och K10 kräver att alla kodfiler finns.

## Stoppregler

1. **Övrigt > 10 %** av utmaningarna (primär typ efter regelprövning, utan dubbletter) leder till att reformen stoppas och rapporteras (K11).
2. **Samstämmighet < 80 %** i dubbelkodningen (M2b) leder till att reformen stoppas och rapporteras (K11).
3. **Citat utan automatisk träff** i källsidans text redovisas av K7. De märks `citatkontroll.metod: "manuell"`, `ok: null` och ska kontrolleras mot sidbilden innan publicering. OCR-citat som är manuellt kontrollerade listas i config `korrigeringar.ocr_citat_manuellt_kontrollerade`.
4. **Förbjudna ord** ("löst", "kvarstår", "bemött tillräckligt") i motiveringar gör att K10 stoppar, utom när en loggad omformulering finns i config `korrigeringar.motivering_omformulerad`. K12 kontrollerar hela datafilen.
5. **Saknat konfigurationsvärde** (null i mallen) gör att steget stoppar med namnet på värdet.
6. Ingen omkodning görs för att klara gränserna. Avvikelser rapporteras.

## Regressionstest (betyg)

```bash
git clone <repo> /tmp/ren && cd /tmp/ren && git checkout <commit>
rm research/remissanalys/reformer/betyg/{passager,utmaningar,sfs-diff,avvikelser}.json   # deterministiska utdata
python3 research/remissanalys/kedja/kor.py betyg
git diff --exit-code -- pilot/utmaningar/data/utmaningar-betyg.json research/remissanalys/reformer/betyg/
python3 research/remissanalys/kedja/stoppregler.py betyg
python3 research/remissanalys/skript/validera-pilot.py
node research/remissanalys/skript/testa-pilotsida.js
```

## Betygsspecifikt som inte är generaliserat

Följande är antingen lagt i config eller ännu inte generaliserat:

- **Urvalet till SFS-jämförelsen (K8)** följer Sprint 16:s regel: förslag som någon kodad utmaning pekar på via förstudie 2:s förankring, där ett avsnitt utan förslagsruta faller tillbaka på förälderavsnittet, eller via tolkad koppling. Regeln behålls för identisk betygsfil. För nya reformer bör urvalet vara alla förslag. Det beslutet tas när den första nya reformen körs.
- **En lag:** författningskommentaren och SFS-jämförelsen stöder bara en lag (`lagar[0]`, `sou.forfattningskommentar`). Om en reform ändrar flera lagar stoppar K8.
- **Lagförslagen i propositionen** antas ligga i kapitel 2 ("2.x Förslag till lag om ändring i …") och vara tvåspaltiga. Spaltförskjutning och y-intervall ligger i config `layout`.
- **Förordningsmarkören** (`forordning_markor`, "betyget 4") och dess beskrivning är reformspecifika och ligger i config.
- **R1** (förslag → propositionsavsnitt) är manuell ämnesmatchning, inte ett skript.
- **Manuellt kontrollerade OCR-citat och omformulerade motiveringar** är listor per reform i config.
- **Klassningslistorna** (enskilda huvudmän, myndigheter) i `gemensamt.json` är extern kunskap och kan behöva kompletteras per remiss.
- **Sökvägar i betygsfilen:** datafilens `belagg` och `byggd_av` pekar på `sfs-diff-betyg.json` och `skript/bygg-pilot.py` (config `legacy_sokvagar`). Nya reformer pekar på `reformer/<id>/sfs-diff.json` och `kedja/bygg.py`.
- **Validering och sidtest** (`validera-pilot.py`, `testa-pilotsida.js`) är skrivna för betyg och behöver parametriseras.
- **spraklig** saknar id i `data/reforms.json`.
