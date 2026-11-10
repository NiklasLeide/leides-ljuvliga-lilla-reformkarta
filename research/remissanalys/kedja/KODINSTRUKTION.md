# Kodinstruktion: Utmaningskartan (alla reformer)

En instruktion för alla reformer (Sprint 17 T1). Den samlar de instruktioner som användes för betyg i förstudie 2 och Sprint 16:
- den öppna kodningen
- den tolkade kopplingen
- `skript/v2/INSTRUKTION.md`
- `skript/v2/INSTRUKTION-regel.md`

Metoden är låst. Taxonomin, den avgörande regeln och stoppreglerna står i `kedja/gemensamt.json`, och den filen gäller om något i den här instruktionen skiljer sig från den.

Platshållare: `{reform}` är reformens id, `{sou}` utredningens nummer och titel ur `reformer/{reform}.json` (`sou.nr`, `namn`), och `{mapp}` är `research/remissanalys/reformer/{reform}`.

Modellkodningen ger fem filer som checkas in under `{mapp}/kodning/`. Den redaktionella förslagsmatchningen R1 ger `{mapp}/forslag-propositionsavsnitt.json`. Allt efter kodningen körs deterministiskt med `kedja/kor.py {reform}`, se `KEDJA.md`.

Allmänt för alla moment:
- Bedöm aldrig om en utmaning är rimlig, löst eller bemött.
- Orden "löst", "kvarstår" och "bemött tillräckligt" får inte stå i motiveringar. `bygg.py` stoppar om de gör det, om det inte finns en loggad omformulering i `korrigeringar.motivering_omformulerad`.
- Skriv filerna med python `json.dump(..., ensure_ascii=False)` och kontrollera med python att formatet stämmer innan filen checkas in.
- Varje fil har ett `_meta`-objekt med `steg` (moment, antal kodare, datum) och `tolkning: true`.

---

## M1 Identifiering av utmaningar → `kodning/utmaningar.json`

**Indata:** `{mapp}/passager.json` (steg K6), passagerna `{id, avsandare, sida, rubrik, text}`. Dela upp dem i batcher med en kodare per batch. Varje kodare läser hela sin batch.

**Uppgift:** avgör för varje passage om den beskriver en **utmaning för huvudmannen**, det vill säga för kommunen eller den enskilda huvudmannen. En utmaning är något som blir svårt, kostsamt, betungande, riskabelt eller oklart för huvudmannen att genomföra eller leva med. Exempel:
- genomförande och organisation
- kostnader och finansiering
- personalens kompetens och lärarförsörjning
- tidplan och ikraftträdande
- IT och administrativa system
- otydliga regler
- effekter på huvudmannens verksamhet, som små skolor, komvux, introduktionsprogram och planering

Regler:
1. **Koda bara avsändarens egna synpunkter.** Text där avsändaren återger utredningens förslag kodas inte, till exempel under rubriken "Utredningens förslag" eller i ett referat av förslaget.
2. Koda inte allmänna ställningstaganden som "tillstyrker" eller "avstyrker".
3. Koda inte effekter bara för elever eller samhällsfrågor, utom när passagen beskriver dem som något huvudmannen, skolorna eller kommunen måste hantera eller inte klarar.
4. En passage kan innehålla noll, en eller flera utmaningar.
5. **Citatet ska vara en ordagrann delsträng av passagens `text`**, oftast 1–3 meningar.
   - Rätta inte stavfel och korta inte med "…". Slå inte ihop passager.
   - Citatet kontrolleras maskinellt i K7 mot källsidans text, där blanksteg och bindestreck normaliseras.

**Utdata:**
```json
{"_meta": {"steg": "M1 identifiering av utmaningar (...)", "tolkning": true, "falt": {...}},
 "utmaningar": [{"uid": "U001", "id": "<passage-id>", "citat": "<ordagrann delsträng>",
                 "oppen_kod": "<2–6 ord, fri etikett>", "beskrivning": "<en mening: vad utmaningen är för huvudmannen>"}]}
```

Om `uid` och ordningen:
- `uid` numreras i passagernas ordning.
- `oppen_kod` och `beskrivning` finns bara för spårbarhet och visas aldrig.
- Dubbletter inom samma avsändare (minst 90 % likhet) markeras mekaniskt i K7 och ska inte tas bort för hand.

## M2 Utmaningstyp → `kodning/utmaningstyp.json`

**Indata:**
- alla utmaningar utom de dubbletter som K7 markerar, med `id`, `citat` och `sammanhang`, där sammanhanget är passagens text
- fördelade på flera kodare med samma instruktion

Sammanhanget får bara användas för att förstå citatet. Koda det som citatet säger.

**Utmaningstyper.** Använd exakt dessa namn, i den här ordningen; källan är `gemensamt.json` `utmaningstyper`.

| Typ | Definition |
|---|---|
| Kostnader och finansiering | utgifter, ersättning, finansieringsprincipen, resursbehov i pengar |
| Tidplan och reformtakt | ikraftträdande, förberedelsetid, samtidiga reformer |
| Personal, kompetens och arbetsbelastning | bemanning, kompetensutveckling, lärares och rektorers arbetsbörda |
| System och teknik | digitala system, provplattform, infrastruktur, utrustning |
| Organisation och planering | schemaläggning, lokaler, genomförande i verksamheten, samordning mellan enheter |
| Otydlighet i förslaget | oklara begrepp, oklart ansvar, oklar tillämpning |
| Likvärdighet och konsekvenser för elever | effekter för elevgrupper, rättssäkerhet, likvärdig bedömning |
| Övrigt | inget av ovanstående |

**Avgörande regel**, ordagrant ur `gemensamt.json` `avgorande_regel`:

> Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som Otydlighet i förslaget, även när elever eller vårdnadshavare nämns som de som ska förstå. Likvärdighet och konsekvenser för elever kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän.

Regler:
1. Ange exakt **en primär** typ, den som citatet främst handlar om.
2. Ange **en sekundär** typ bara om citatet tydligt också handlar om en annan typ. Annars null.
3. Hitta inte på nya typer. Använd "Övrigt" bara när ingen typ passar.
4. Skolform och sakområde är inte typer. Välj typ efter vad utmaningen består i. Exempel:
   - provtillfällen i komvux som inte passar verksamheten blir Organisation och planering
   - en provplattform som saknas blir System och teknik

**Utdata:**
```json
{"_meta": {"steg": "M2 utmaningstyp (...)", "tolkning": true},
 "kodning": [{"id": "U001", "primar": "<typ>", "sekundar": "<typ>" | null, "motivering": "<högst 12 ord>", "kodare": 1}]}
```

## M2b Dubbelkodning → `kodning/dubbelkodning.json`

- Dra ett stickprov på 40 utmaningar slumpvis med en seed som anges i `_meta`. En **oberoende** kodare med M2-instruktionen kodar dem utan att se M2-resultatet.
- Format som M2 men utan `kodare`: `{"_meta": {...}, "kodning": [{"id", "primar", "sekundar", "motivering"}]}`.
- Samstämmigheten är andelen av stickprovet där den oberoende kodarens primära typ är densamma som i M2. K11 (`stoppregler.py`) räknar ut den.

## M2c Regelprövning → `kodning/regelprovning.json`

- En kodare prövar alla utmaningar med primär typ Otydlighet i förslaget eller Likvärdighet och konsekvenser för elever mot den avgörande regeln, genom att läsa citatet.
- Kodaren får bara byta mellan de två typerna.
- **Utdata:**

```json
{"_meta": {"steg": "...", "regel": "<avgörande regel>", "antal_provade": 0, "antal_andrade": 0, "tolkning": true},
 "provade_id": ["U004", "..."],
 "andringar": [{"id": "U024", "gammal": "<typ i M2>", "ny": "<typ>", "motivering": "<högst 15 ord>"}]}
```

`bygg.py` tillämpar ändringarna (`regelprovad` och `andrad_vid_regelprovning` i datafilen).

## M3 Tolkad koppling → `kodning/tolkad-koppling.json`

**Indata:**
- utredningens förslag `{mapp}/sou-forslag.json` (`id`, `avsnitt`, `avsnittsrubrik`, `text`)
- de utmaningar vars passage saknar egen hänvisning till utredningen, det vill säga där `hanvisningar_egna`, `hanvisningar_rubrik` och paragrafhänvisningar är tomma
- två kodare som tar varsin halva

**Uppgift:** detta är ett tolkande steg, så var försiktig. Ange 1–3 förslags-id när citatet eller passagen tydligt gäller det ett visst förslag reglerar. Ange null när utmaningen är generell, till exempel många samtidiga reformer, kostnader i allmänhet eller behov av information, och inget enskilt förslag är ett rimligt mål. **Välj null hellre än en svag gissning.**

**Utdata:**
```json
{"_meta": {"steg": "M3 tolkad koppling (...)", "tolkning": true},
 "kopplingar": [{"uid": "U001", "forslag": ["F02"] | null, "motivering": "<högst 15 ord>"}]}
```

K7 använder den tolkade kopplingen bara när remissvaret saknar egen hänvisning. Kopplingen får då nivån `tolkad` och `tolkning: true`.

## R1 Redaktionell koppling förslag → propositionsavsnitt → `forslag-propositionsavsnitt.json`

Detta är inte modellkodning av remissvar. Det är en redaktionell ämnesmatchning, och den görs en gång per reform.

- Varje utredningsförslag kopplas till de propositionsavsnitt (`"<kort>:<avsnitt>"`, till exempel `"197:6.2"`) som behandlar det.
- Underlag är `prop-avsnitt.json` och `propositioner-innehall.json`.

**Utdata:**
```json
{"_meta": {"steg": "R1 ...", "redaktionell": true, "matchningstyper": ["förslagsruta", "avsnittsnivå", "osäker ämnesmatchning", "övergripande avsnitt, detalj ej behandlad", "ingen"]},
 "forslag": [{"id": "F01", "propositionsavsnitt": ["197:6.2"], "matchning": "förslagsruta", "grund": "<kort motivering>"}]}
```

`matchning` ska vara en av de fem typerna. `ingen` betyder tom lista.

## Stoppregler

Stoppreglerna kontrolleras av K11 (`kedja/stoppregler.py {reform}`). En reform stoppas och rapporteras om något av följande gäller:
- **Övrigt** överstiger 10 % av utmaningarna, räknat på primär typ efter regelprövning och utan dubbletter.
- **Samstämmigheten** i M2b understiger 80 %.
- Ett typnamn avviker från de åtta.

Gör ingen omkodning för att klara gränserna. Rapportera i stället.
