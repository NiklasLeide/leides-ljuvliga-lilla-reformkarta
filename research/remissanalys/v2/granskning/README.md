# Granskning av Utmaningskartan, pilot betyg

Tack för att du granskar! Det här är en instruktion till dig som granskar. Du behöver inga tekniska förkunskaper.

## Vad sidan visar

Pilotsidan finns på **https://reformer.leide.se/dev/utmaningar-pilot/**. Den visar vilka utmaningar kommuner, SKR, Almega och Idéburna skolors riksförbund lyfte i sina remissvar på betänkandet *Ett likvärdigt betygssystem* (SOU 2025:18). Den visar också vad propositionen och den beslutade lagen säger om de förslag som utmaningarna gällde.

**Citaten är ordagranna** ur de publicerade remissvaren, med sida och länk till remissvaret. Enskilda huvudmäns remissvar saknas, eftersom regeringen inte publicerar dem.

## Vad som är maskinell tolkning

En språkmodell har gjort tre saker:

1. **Valt ut utmaningarna** i remissvaren. En "utmaning" är något som huvudmannen pekar ut som svårt, kostsamt, oklart eller riskabelt att genomföra.
2. **Satt utmaningstyp** på varje utmaning, till exempel *Kostnader och finansiering* eller *Otydlighet i förslaget*. Definitionerna finns längst ner på pilotsidan.
3. **Kopplat utmaningar till utredningens förslag** när remissvaret inte själv hänvisar till ett avsnitt i betänkandet. Sådana kopplingar är märkta "Tolkad koppling" på sidan och står som "tolkad" i filen.

Ingenting av detta är kvalitetssäkrat. Det är det din granskning ska ge underlag för.

## Filen granskning-betyg.csv

Öppna filen i Excel. Den är semikolonseparerad och sparad så att å, ä och ö visas rätt. Filen har två delar.

### Del 1: Träffsäkerhet (40 utmaningar)

Det är fem utmaningar per utmaningstyp, slumpvis valda. 16 av dem har en tolkad koppling. Läs citatet. Öppna gärna länken till remissvaret eller till vyn på pilotsidan. Fyll sedan i:

| Kolumn | Fyll i |
|---|---|
| Är det en utmaning? | **ja** om citatet beskriver något som är svårt, kostsamt, oklart eller riskabelt för huvudmannen, annars **nej** |
| Rätt utmaningstyp? | **ja** om typen i kolumnen *utmaningstyp* stämmer, annars **nej** |
| Rätt koppling? | **ja** om sakområdet och kopplingen stämmer med vad citatet handlar om, **nej** om de inte stämmer, **går ej att bedöma** om det inte går att avgöra. Om kopplingsnivån är "ingen koppling" bedömer du om det är rätt att citatet saknar koppling. |
| Kommentar | Valfritt, till exempel vilken typ som hade varit rätt |

### Del 2: Missade utmaningar (20 passager)

Det här är slumpvis valda textstycken ur remissvaren som modellen **inte** valde ut som utmaningar. Fyll i:

| Kolumn | Fyll i |
|---|---|
| Innehåller passagen en utmaning som borde ha kommit med? | **ja** eller **nej** |
| Kommentar | Valfritt |

## Annat du ser

Skriv gärna ner annat du lägger märke till på sidan, till exempel om något är svårt att förstå, ser fel ut eller saknas. Det kan stå i kommentarskolumnen eller i ett eget meddelande.

## För den som räknar ihop

`python3 rakna-granskning.py granskning-betyg.csv` skriver ut andelen "ja" per fråga i del 1, uppdelat på utmaningstyp och kopplingsnivå, samt andelen missade utmaningar i del 2.

Filen byggs av `research/remissanalys/skript/v2/bygg-granskning.py` med det fasta **slumpfröet 20261112**:
- **Del 1:** två tolkade och tre övriga utmaningar per typ.
- **Del 2:** urval bland de 169 passager som inte kodades som utmaning, är minst 200 tecken långa och inte bara återger utredningens förslag.
