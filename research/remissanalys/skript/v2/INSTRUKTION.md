# Kodinstruktion: utmaningstyp (Utmaningskartan, pilot betyg)

Du kodar utmaningar som huvudmän (kommuner) och deras organisationer (SKR, Almega Utbildning, Idéburna skolors riksförbund) har pekat ut i sina remissvar på SOU 2025:18 "Ett likvärdigt betygssystem" (ny betygsskala 1–10, nationella slutprov som rättas centralt, kalibrering av meritvärden, bedömningssamråd, nya behörighetsregler m.m.).

Läs varje **citat** och avgör vilken utmaningstyp det beskriver. Fältet **sammanhang** är den omgivande texten och får bara användas för att förstå citatet; koda det som citatet säger.

## Utmaningstyper (använd exakt dessa namn)

- **Kostnader och finansiering**: utgifter, ersättning, finansieringsprincipen, resursbehov i pengar.
- **Tidplan och reformtakt**: ikraftträdande, förberedelsetid, samtidiga reformer.
- **Personal, kompetens och arbetsbelastning**: bemanning, kompetensutveckling, lärares och rektorers arbetsbörda.
- **System och teknik**: digitala system, provplattform, infrastruktur, utrustning.
- **Organisation och planering**: schemaläggning, lokaler, genomförande i verksamheten, samordning mellan enheter.
- **Otydlighet i förslaget**: oklara begrepp, oklart ansvar, oklar tillämpning.
- **Likvärdighet och konsekvenser för elever**: effekter för elevgrupper, rättssäkerhet, likvärdig bedömning.
- **Övrigt**: inget av ovanstående.

## Regler

1. Exakt **en primär** typ: den som citatet främst handlar om.
2. Valfritt **en sekundär** typ, bara om citatet tydligt också handlar om en annan typ. Annars null.
3. Hitta inte på nya typer. Använd "Övrigt" bara när ingen typ passar.
4. Skolform (t.ex. komvux) och sakområde (t.ex. slutprov, bedömningssamråd) är INTE typer – välj typ efter vad utmaningen består i (t.ex. komvux-provtillfällen som inte passar verksamheten = Organisation och planering; ingen provplattform = System och teknik).
5. Bedöm inte om utmaningen är rimlig, löst eller bemött.

## Utdata

En JSON-lista, ett objekt per utmaning i indatafilen:
`{"id": "U001", "primar": "<typ>", "sekundar": "<typ>" | null, "motivering": "<högst 12 ord på svenska>"}`
Skriv med python `json.dump(..., ensure_ascii=False)`. Kontrollera med python att alla id finns exakt en gång och att typnamnen är exakt de åtta ovan.
