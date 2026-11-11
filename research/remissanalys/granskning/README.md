# Granskning av Utmaningskartan, alla sju reformer

Tack för att du granskar! Det här är en instruktion till dig som granskar. Du behöver inga tekniska förkunskaper.

## Vad sidan visar

Pilotsidan finns på **https://reformer.leide.se/dev/utmaningar-pilot/**. Startvyn jämför sju skolreformer. Välj en reform för att se vilka utmaningar kommuner och huvudmannaorganisationer (SKR, Almega, Idéburna skolors riksförbund och för den tioåriga grundskolan Friskolornas riksförbund) lyfte i sina remissvar på utredningens betänkande. Sidan visar också vad propositionen och den beslutade lagen säger om de förslag som utmaningarna gällde.

| Fil | Reform | Betänkande |
|---|---|---|
| `granskning-betyg.csv` | Ett likvärdigt betygssystem | SOU 2025:18 |
| `granskning-studiero.csv` | Trygghet och studiero | SOU 2025:8 |
| `granskning-stod.csv` | Förbättrat stöd i skolan | SOU 2025:44 |
| `granskning-tid.csv` | Tid för undervisningsuppdraget | SOU 2025:26 |
| `granskning-laroplaner.csv` | Kunskap för alla (nya läroplaner) | SOU 2025:19 |
| `granskning-spraklig.csv` | På språklig grund | SOU 2025:9 |
| `granskning-tioarig.csv` | En tioårig grundskola | SOU 2021:33 |

**Citaten är ordagranna** ur de publicerade remissvaren, med sida och länk till remissvaret. Enskilda huvudmäns remissvar saknas, eftersom regeringen inte publicerar spontana yttranden.

## Vad som är maskinell tolkning

En språkmodell har gjort tre saker, med samma instruktion för alla reformer:

1. **Valt ut utmaningarna** i remissvaren. En "utmaning" är något som huvudmannen pekar ut som svårt, kostsamt, oklart eller riskabelt att genomföra.
2. **Satt utmaningstyp** på varje utmaning, till exempel *Kostnader och finansiering* eller *Otydlighet i förslaget*. Definitionerna finns i metodrutan på pilotsidan.
3. **Kopplat utmaningar till utredningens förslag** när remissvaret inte själv hänvisar till ett avsnitt i betänkandet. Sådana kopplingar är märkta "Tolkad koppling" på sidan och står som "tolkad" i filen.

Ingenting av detta är kvalitetssäkrat. Det är det din granskning ska ge underlag för.

## Filerna

Öppna en fil i Excel. Den är semikolonseparerad och sparad så att å, ä och ö visas rätt. Varje fil har två delar. Betyg har 40 + 20 rader, övriga reformer 15 + 5.

### Del 1: Träffsäkerhet

Utmaningarna är slumpvis valda och jämnt fördelade över utmaningstyperna; ungefär fyra av tio har en tolkad koppling. Läs citatet. Öppna gärna länken till remissvaret eller till vyn på pilotsidan (länken öppnar rätt reform och typ). Fyll sedan i:

| Kolumn | Fyll i |
|---|---|
| Är det en utmaning? | **ja** om citatet beskriver något som är svårt, kostsamt, oklart eller riskabelt för huvudmannen, annars **nej** |
| Rätt utmaningstyp? | **ja** om typen i kolumnen *utmaningstyp* stämmer, annars **nej** |
| Rätt koppling? | **ja** om sakområdet och kopplingen stämmer med vad citatet handlar om, **nej** om de inte stämmer, **går ej att bedöma** om det inte går att avgöra. Om kopplingsnivån är "ingen koppling" bedömer du om det är rätt att citatet saknar koppling. |
| Kommentar | Valfritt, till exempel vilken typ som hade varit rätt |

### Del 2: Missade utmaningar

Slumpvis valda textstycken ur remissvaren som modellen **inte** valde ut som utmaningar. Fyll i:

| Kolumn | Fyll i |
|---|---|
| Innehåller passagen en utmaning som borde ha kommit med? | **ja** eller **nej** |
| Kommentar | Valfritt |

## Annat du ser

Skriv gärna ner annat du lägger märke till på sidan, till exempel om något är svårt att förstå, ser fel ut eller saknas.

## För den som räknar ihop

`python3 research/remissanalys/granskning/rakna-granskning.py` räknar alla ifyllda filer i mappen: andelen "ja" per fråga per reform och totalt (totalen även per reform, utmaningstyp och kopplingsnivå) samt andelen missade utmaningar i del 2. Enskilda filer kan anges som argument.

Filerna byggs av `research/remissanalys/kedja/granskning.py <reform-id|alla>` ur den aktuella datafilen `pilot/utmaningar/data/utmaningar-<id>.json` och reformens `passager.json`, med fasta slumpfrön (betyg 20261112, studiero 20261121, stod 20261122, tid 20261123, laroplaner 20261124, spraklig 20261125, tioarig 20261126).
- **Del 1:** jämn kvot per utmaningstyp (tak = antal i typen), inom typen cirka 40 % tolkade.
- **Del 2:** urval bland passager som inte kodades som utmaning, är minst 200 tecken långa och inte bara återger utredningens förslag (samma mekaniska regler som i Sprint 16).

Sprint 16:s granskningsfil för betyg (den gamla kodningen) ligger kvar i `research/remissanalys/v2/granskning/` som historik.
