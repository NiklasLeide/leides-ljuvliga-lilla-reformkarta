# Omprövning av utmaningstyp: Otydlighet i förslaget eller Likvärdighet och konsekvenser för elever

Utmaningarna kommer från huvudmäns och deras organisationers remissvar på SOU 2025:18 "Ett likvärdigt betygssystem". Varje utmaning har i dag primär typ **Otydlighet i förslaget** eller **Likvärdighet och konsekvenser för elever**. Pröva varje utmaning mot den avgörande regeln nedan, genom att läsa citatet (sammanhanget får bara användas för att förstå citatet).

## Definitioner
- **Otydlighet i förslaget**: oklara begrepp, oklart ansvar, oklar tillämpning.
- **Likvärdighet och konsekvenser för elever**: effekter för elevgrupper, rättssäkerhet, likvärdig bedömning.

## Avgörande regel
Citat vars huvudpoäng är att modellen, regleringen eller begreppen är svåra att förstå eller förklara kodas som **Otydlighet i förslaget**, även när elever eller vårdnadshavare nämns som de som ska förstå. **Likvärdighet och konsekvenser för elever** kräver att citatet beskriver en effekt för elever eller skilda utfall mellan elevgrupper, skolor eller huvudmän.

## Uppgift
För varje utmaning: ange vilken av de två typerna som är rätt primär typ enligt regeln. Byt bara mellan dessa två typer; inga andra typer. Bedöm inte om utmaningen är rimlig eller bemött.

## Utdata
JSON-lista, ett objekt per id: `{"id": "...", "primar": "Otydlighet i förslaget" | "Likvärdighet och konsekvenser för elever", "motivering": "<högst 15 ord>"}`. Skriv med python `json.dump(..., ensure_ascii=False)`. Kontrollera att alla id finns exakt en gång.
