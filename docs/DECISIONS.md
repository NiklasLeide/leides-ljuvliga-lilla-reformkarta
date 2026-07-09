# Decision Log — leides-ljuvliga-lilla-reformkarta

Record of key decisions made during the project. **Newest first.**

> The alternatives you *rejected* are as important as what you chose.
> Future sessions will read this — make the reasoning explicit.

---

## Format
```
### DEC-NNN: Title
**Date:** YYYY-MM-DD
**Decision:** What we chose
**Reasoning:** Why this option over the others
**Alternatives considered:** What was rejected and why
```

---

### DEC-015: Läsårshjulet ersätter listan som guidens förstasida
**Date:** 2026-06-12
**Decision:** (T5.4) guide.html är ett läsårshjul: SVG med månaderna aug–jul i läsårsordning, händelsemånader tonade, verksamhetsdatum som klickbara punkter på fälgen, centrum med antal + kort deskriptiv mening; detaljkort under hjulet (datum + relativ tid + klartext + påverkan + länkrad där "Mer hos Skolverket" bara visas när en verifierad Skolverket-länk finns i reforms.json — inga fabricerade länkar); horisontcirklar (mini-hjul per framtida läsår + streckad "på g") byter visat läsår. Mockupen lasarshjul-mockup.html är specen — konceptet återskapat med repots designtokens, datadrivet ur guide.json (DEC-010-händelsemodellen oförändrad). Den fullständiga listan (nivå 1–3, sammanfattning, piller, deeplinks) FLYTTAD i sin helhet till undersidan guide-alla.html, länkad "Alla datum och fullständiga underlag →"; ?reform=-deeplinks till guide.html vidarebefordras dit. Tillgänglighet: hjulets punkter är tabbara (tabindex, role=button, aria-label med datum/status/klartext, synlig fokusring, Enter/Space), detaljkortet aria-live, och en skärmläsarnotis hänvisar till undersidan som fullvärdigt listalternativ.
**Reasoning:** Niklas mockup definierar formen: hjulet är överblicken (startkortet utgick), målgruppen tänker i läsår, och en graf med max ~7 punkter per läsår skannas snabbare än 19 listrader. Listan försvinner inte — den blir fördjupningssidan och det tillgängliga alternativet, vilket löser SVG-grafikens skärmläsarproblem utan parallell DOM.
**Alternatives considered:** Hjul + lista på samma sida (dubblerad kognitiv last, mobilen oändligt lång); kalenderår i hjulet (målgruppen planerar per läsår — mockupen är explicit); tillgänglighet via osynlig parallellista i guide.html (underhållsdubblering — undersidan finns redan och är komplett).

**Komplettering (T5.5, 2026-06-13 — Niklas beslut efter UX-granskning):**
(1) MÅNADER ÄR KNAPPARNA, PUNKTER ÄR MARKÖRER. T5.4:s klickbara fälgpunkter (~22px cirklar) var för små träffytor och konkurrerade med segmentytorna om samma interaktion — punkterna avklickbarades helt (pointer-events:none, aria-hidden, inga handlers) och månadssegment MED datum blev knapparna ([data-test=manad], role=button, tabbara, aria-label "September — 1 nytt datum", hover-/fokus-/vald-affordance i fyllnad). Månader utan datum är inerta. Geometrin ger segmenten >44px träffyta. Hjulet har därmed EN interaktionsmodell.
(2) Verksamhetsvalet är en alltid synlig chiprad under sidhuvudet, samma mönster mobil/desktop ([data-test=val-synlig]) — T5.4:s headerknapp+panel utgick (dolde valet bakom ett extra steg); rensning med ett tryck via Rensa-chip.
(3) Detaljkortet fick föregående/nästa-pilar ([data-test=detalj-nav], 44px) som primär navigering + piltangenter + touch-svep med riktningströskel (|dx|>|dy| och |dx|>30px — vertikal scroll kapas aldrig) + klickbara bläddringsprickar.
(4) Detaljytan har stabil min-höjd per visat läge (uppmätt mot största kortet) så bläddring/läsårsbyte inte flyttar innehållet under; horisontcirklarnas etiketter utskrivna (siffra + "nya datum" + "läsåret YYYY/YY" resp. "på g / ej beslutat" — läsårsformen vald även för 2030/31 i st.f. uppgiftsexemplets "2031", konsekvent vokabulär); på g-kortet listar samtliga poster med namn och bläddras som övriga.
(5) Läsårsspannet uttalat i rubriken ("Läsåret 2025/26 · augusti–juli"); ordet terminsstart förekommer inte i UI (skolor startar olika); datum placeras strikt kalendariskt.

**Komplettering (T5.6, 2026-06-13 — Niklas desktopgranskning):**
(A) KURERAT VÄLJARLAGER ersätter berors-råvärdena i chipraden (14 råa chips → 7 kurerade: Förskola, Grundskola, Anpassad grundskola, Gymnasieskola, Anpassad gymnasieskola, Fritidshem, Komvux). Mappningstabell i koden (KURERADE_VAL): Förskola ⊇ fristående förskolor; Grundskola ⊇ grundskolan, fristående skolor, förskoleklassen, sameskolan, specialskolan; Anpassad grundskola ⊇ anpassade grundskolan, fristående skolor; Gymnasieskola ⊇ gymnasieskolan, fristående skolor; Anpassad gymnasieskola ⊇ anpassade gymnasieskolan, fristående skolor; Fritidshem ⊇ fritidshemmet, fristående fritidshem, öppen fritidsverksamhet; Komvux ⊇ kommunal vuxenutbildning. Bedömningar: "fristående skolor" (offentlighetsposten) träffar alla fyra skol-valen eftersom fristående skolor finns i alla skolformer; specialskolan och sameskolan ingår i Grundskola — posternas reglering är gemensam med grundskolans och hellre överinkludering än tyst filtermiss (specialskolan har statlig huvudman men förekommer aldrig ensam i datat); förskoleklassen ingår i Grundskola (upphör 2028, följer grundskoleposterna). Poster med berors=null visas ALLTID — "ej specificerat" är inget valbart chip längre. Runtime-vakt loggar berors-värden som mappningen inte täcker.
(B) Hjulet städat: fälgpunkterna har inga textetiketter (r=6-markörer, kollisionsförskjutna med 6°-minimiseparation — två reformer 1 aug överlappar inte längre); månadsetiketten bär antalsbadge ("JULI · 2", [data-test=manad-antal]). Månadsklick öppnar MÅNADSKONTEXT: nav/prickar förfiltrerade till månadens samtliga poster (åtgärdar julibuggen där bara en av två visades) med "Visa hela läsåret"-knapp som behåller aktuell post vid återgång.
(C) Tvåspalt ≥1100px ([data-test=layout-tvaspalt]): hjul + horisont vänster, detaljkortet sticky höger — kärnvyn ryms utan scroll på 1440p (uppmätt 828/654px). T5.5:s fasta min-höjd UTGICK; ersatt av mjuk höjdtransition (0.18s) på kortet vid innehållsbyte — inget reserverat tomrum.
(D) Innevarande läsår borttaget ur horisontcirklarna (hjulet ÄR det; diskret "‹ tillbaka till läsåret X"-länk visas i hjulhuvudet när annat läsår visas); etiketter utskrivna med "ändringar" ("5 / ändringar / läsåret 2026/27", på g: "3 / på g / ej beslutat").
(E) Rubriken "Läsårshjul" utan possessiv; spann-underrubriken kvar.

**Komplettering (T5.7, 2026-06-16 — Niklas granskning, omkast av T5.6 D):**
KOMPLETT LÄSÅRSRAD ersätter framtidscirklarna. T5.6 (D) dolde innevarande läsår ur horisontcirklarna (hjulet ÄR det) och döpte raden "Längre fram". Det skapade förvirring om hur raden fungerar — "längre fram" antydde enbart framtid, och att innevarande saknades gjorde att raden inte lästes som en fullständig läsårsväljare. Beslut: raden visar nu EN cirkel per läsår i datat INKLUSIVE innevarande ([data-test=lasarsrad]; lasarKnappar = allaLasar ∪ {innevarande}, sorterat), plus "på g"-cirkeln (streckad) sist. Det aktiva läsåret är visuellt markerat med samma fyllda .aktiv-stil som tidigare. Klick byter visat hjul; klick på den redan aktiva cirkeln (på läsårsnivå) är en tyst no-op — ingen omritning, inget flimmer (från månadskontext zoomar klicket i stället ut till hela läsåret). Rubriken "Längre fram" → "Läsår". Etiketternas T5.6-form ("N ändringar läsåret X", "på g / ej beslutat") och verksamhetsfiltrets synkrona antal är orörda. Motivering att markera snarare än dölja innevarande: en komplett, självförklarande rad där nuet syns som en av cirklarna är mer begriplig än en dold-och-omdöpt delmängd. Headless-verifierat (Playwright, 1440p+375): 15/15, inkl. no-op bevisad via oförändrad hjul-/rad-DOM. Endast guide.html ändrades funktionellt; guide-alla.html rördes bara av en inert kodkommentar-omformulering (språkregel-hygien).

**Komplettering (T6-städning, 2026-06-16):**
Hjulhuvudets "‹ tillbaka till läsåret X"-länk (T5.6 D, behållen i T5.7) TOGS BORT i T6-städningen. Klickytan var fullt redundant med innevarande-cirkeln i den kompletta läsårsraden — båda gjorde exakt samma sak (kontext='lasar', visatLasar=INNEVARANDE, uppdateraAllt). Två klickytor för samma åtgärd är brus, inte robusthet. Borttagna delar: `.hjulhuvud .nu-lank`-CSS, `<button id="nuLank">`-elementet i hjulhuvudet, `nu`-uppdateringen i `ritaHjul()`, och click-handlern. Nu finns precis EN väg tillbaka till innevarande: klicka på dess cirkel i läsårsraden.

**Komplettering (T5.8, 2026-06-17 — Niklas granskning):**
(1) AKTIV PUNKT MARKERAS. Punkten vars post visas i detaljkortet markeras visuellt i hjulet ([data-test=punkt-aktiv]): accentfärg (--kunskap) + r=9 (vs månadens övriga r=6) + tjockare vit ring. Synkas av `markeraHjul()` vid varje postbyte (pil/svep/prickklick) och månadsbyte. Den valda månadens övriga punkter får `.manad` (accent, r=6); aktiv jämförs robust via `eventKey` (datum|reform_id), inte objektreferens.
(2) KARUSELLEN ÄR MÅNADSAVGRÄNSAD MED WRAP. Detaljkortets pilar/piltangenter/svep/prickar bläddrar ENBART den valda månadens punkter, med wrap (`pos = ((i % n) + n) % n` — sista→första, första→sista); prickantalet = månadens punkter. Detta innebar att den läsårsvida navigeringskontexten ('lasar') ELIMINERADES: `kontext ∈ {'manad','pag'}`, och inom ett läsår väljs default-månaden via `defaultManadSlot` (slot för nästa kommande datum, annars första). Konsekvens: "Visa hela läsåret"-knappen (kontextTillbaka, T5.5/T5.6) togs bort — den återgick till den läsårsvida karusellen som inte längre finns. **Motivering**: läsårsvida pilar krockade med månadsklickets filterlogik (klicka en månad → se bara den månaden, men pilarna tog dig ändå ut ur månaden), och navigeringen kunde "ta slut" mitt i ett läsår. En månadsavgränsad karusell med wrap ger en sluten, förutsägbar loop per månad; månadsbyte sker via segmenten (oförändrat) och nollställer till månadens första punkt. Headless-verifierat (Playwright 1440p+375): aktiv punkt distinkt (r 9 vs 6, accent), wrap fram/bak inom JULI·2, prickantal=månadens, månadsbyte nollställer, svep på 375. Kurerad väljare, läsårsrad, tvåspaltslayout, månadsbadgar och rubriker orörda.

---

### DEC-014: T5.3-avvikelsen — målvillkor är golv, briefen är specifikationen
**Date:** 2026-06-12
**Decision:** T5.3:s första leverans uppfyllde /goal-villkoret ("[data-test=oversikt] med minst fyra tidsgrupper som uppdateras vid verksamhetsval") med enbart räknarpiller — men briefens kärna var en skummbar textsammanfattning: grupperade en-radare per reform (datum + klartextens första mening + berörda-chips, radlänk till posten) och en "På g"-grupp för ej beslutade reformer. Kompletterat i T5.3-fix. Processlärdom inskriven: ett maskinverifierbart målvillkor är ett GOLV (minsta verifierbara bevis), inte hela leveransen — när brief och målvillkor skiljer sig i omfattning är briefen specifikationen, och tolkningar som "minsta uppfyllande" ska flaggas innan leverans, inte upptäckas efteråt.
**Reasoning:** Målvillkor formuleras medvetet kompakta och testbara; att optimera mot dem bokstavligt producerar tekniskt gröna men innehållsligt tomma leveranser — samma felklass som rapporteringsregeln i CLAUDE.md adresserar för rapporter, här för byggval.
**Alternatives considered:** Behandla målvillkoret som hela specen (gjordes — gav denna avvikelse); be om förtydligande före bygge (rätt när briefen saknas — här FANNS briefen i tidigare T5.2-uppgifter och mönstret "sammanfattning" var etablerat).

---

### DEC-013: Guidens startnivå — konkret nästa deadline, klartext som ansikte, hopfällt val på mobil
**Date:** 2026-06-12
**Decision:** (T5.2b-omtag) Startöverblicken är ETT konkret kort: nästa verksamhetsdatum för vald verksamhet (utan val: alla) med absolut datum + klientberäknad relativ tid, klartext som rubrik och påverkan som enda stycke — plus 12-månadersräknare och en tydlig väg till hela tidslinjen. Aldrig grind, aldrig tomt: utan kommande datum för valet visas nästa datum över alla verksamheter med ärlig etikett. Klartext leder överallt: nivå 1-raderna bär klartext som rubrik (utan kicker); officiell beslutsrubrik + omfattning + påverkan utgör nivå 2:s topp; krav + ordagranna övergångsbestämmelser + SFS + korslänkar ligger i nivå 3. All citerad beslutstext får enhetlig citatstil (markerad vänsterkant + indrag + §) så klarspråk och författningstext aldrig kan förväxlas (DEC-012-villkoret). På mobil komprimeras skolformsvalet till en hopfälld "Välj verksamhet"-knapp så startkortet ligger ovanför fold (uppmätt: topp 315px/botten 637px vid 375×812).
**Reasoning:** T5.2b:s första utförande lade tre herokort + räknarrad överst — informativt men abstrakt; målgruppen behöver se ETT verkligt datum med en verklig mening om verklig påverkan inom en sekund. Valet före hero åt upp mobilens första skärm (~700px chips) — hopfällningen löser foldproblemet utan att gömma funktionen.
**Alternatives considered:** Tre herokort (första T5.2b — splittrar fokus, abstrakt); räknarrad som primärt element (siffror utan konkretion); skolformsval som egen sida/steg (grindning — förbjudet); auto-öppnad chips-panel vid första besök (trycker startkortet under fold igen).

---

### DEC-012: Klarspråkslager i guiden tillåtet — på Niklas villkor
**Date:** 2026-06-12
**Decision:** Principbeslut av Niklas (T5.2a): guideposterna får ett egenförfattat klarspråkslager — fälten `klartext` {text, kalla} (1–2 deskriptiva meningar om vad som ändras) och `paverkan` {text, kalla}|null (vad ändringen innebär för huvudmannen i drift, extraherad ur propositionens konsekvensavsnitt med källhänvisning till avsnittet). Villkor: strikt deskriptivt, varje mening spårbar till källa, visuellt åtskilt från citerad beslutstext i UI:t (T5.2b). Utökad språkregel för just dessa fält: bör/rekommenderar/råder/måste ni/se till att är förbjudna. Saknar propen huvudmannakonsekvenser sätts paverkan till null med notering — aldrig fabricerat. Befintliga krav/övergångsbestämmelser orörda (blir nivå 3).
**Reasoning:** T1-kontraktets rena citatlinje gav spårbarhet men 5-sekundersskanningen (DEC-011) behöver en mening på klarspråk per rad. Avgränsningen deskriptivt-spårbart-åtskilt behåller skiljelinjen mot rådgivning: guiden säger vad som gäller och vad det innebär enligt propositionen själv, aldrig vad huvudmannen borde göra.
**Alternatives considered:** Enbart officiella formuleringar (T1–T5-läget — skannbarhet lider, myndighetsprosa i listraderna); AI-genererad sammanfattning per sidvisning (out of scope: AI-anrop förbjudna i Sprint 10-beslutet och ospårbart); kravlistan som nivå 1-text (för lång och uppräknande för radformatet).

---

### DEC-011: Guiden följer "viktiga datum för företagare"-mönstret
**Date:** 2026-06-12
**Decision:** Guidevyn (T5.1) designas som genren "viktiga datum"-tjänst (Skatteverket-klassen): kronologisk datumlista med datumet visuellt primärt, hero "Närmast i tid" (tre närmaste verksamhetsdatumen, opåverkad av filter — sidan har aldrig tom yta), skolformsval överst med stora träffytor (sparas i URL-param + localStorage, URL vinner; rensas med ett tryck), GOV.UK task list-mikromönster per rad (hela raden klickbar, lugna gemena statusmarkeringar gäller redan/träder i kraft/tillämpas, max en stödtextrad), tre progressiva nivåer hopfällda som default (rad → krav med källor → ordagranna övergångsbestämmelser/SFS/korslänkar), caveat-rad i sidhuvudet enligt genrekonvention. Årsavdelare i stället för T4:s grupprubriker. Innehåll, datakontrakt och DEC-010:s händelsemodell oförändrade.
**Reasoning:** Målgruppen (småföretagare som driver fristående verksamheter) behärskar redan mönstret från myndigheternas datumtjänster — igenkänning sänker tröskeln mer än någon ny struktur. Datumet är det huvudmannen faktiskt planerar mot; allt annat är fördjupning. Tre hopfällda nivåer ger 5-sekunders skannbarhet utan att offra spårbarheten (källänk per kravrad kvarstår från kontraktet).
**Alternatives considered:** Step-by-step-/wizardmönster (GOV.UK "check what you need to do") — FÖRKASTAT: det guidar mot ett slutmål genom frågor, vilket är rådgivningssemantik ("vad ska jag göra?") och bryter mot sprintens grundregel överblick-aldrig-rådgivning; dessutom grindar det innehållet bakom val, vilket strider mot aldrig-grind-kravet. T4:s kortbaserade grupplayout (behölls en sprintdag) — informationstät men kändes som rapport, inte datumtjänst; allt innehåll synligt samtidigt motverkade skannbarhet.

---

### DEC-010: Guidevyns händelsemodell och gap-regel för tillämpningspivot
**Date:** 2026-06-12
**Decision:** Guidens tidslinje är händelsebaserad: varje post i `ikrafttradanden` blir en egen tidslinjehändelse (flerstegsreformer som tid syns i flera grupper). Pivotregeln preciseras med en gap-regel: en reform pivoterar på sina tillampning-poster — och dess ikraft-poster degraderas till sekundärtext på korten — ENDAST när största tillampning ligger >365 dagar efter första ikraft (tioarig: ikraft 2026-07-01, verksamhetsträff läsåret 2028/29). Vid kortare gap (brott: 6 månader, delbestämmelser) är ikraftträdandet en verklig verksamhetshändelse och båda stegen visas som händelser. Gruppetiketter härleds ur datum (Sommaren 2026, Läsåret 2028/29, …) — inga reformnamn i logiken.
**Reasoning:** T1-kontraktets enkla regel ("pivotera på tillampning när sådan finns") ger fel resultat för brott — sprintspecen placerar brott uttryckligen på sitt ikraftdatum 30/6 i Sommaren 2026, eftersom lagen då gäller och bara vissa bestämmelser har en senare tillämpningströskel. Gap-regeln skiljer maskinellt "hela lagen träffar verksamheten långt senare" (tioarig) från "delbestämmelser med kort tröskel" (brott) utan hårdkodade reformnamn.
**Alternatives considered:** Flagga i datat (per-post `pivot: true`) — mer explicit men kräver dataändring och en redaktionell bedömning per reform som gap-regeln ger gratis; textmatchning på "I övrigt tillämpas lagen" (skört mot formuleringsvariation); hårdkodade reform-id:n (förbjudet av sprintspecen).

---

### DEC-009: Guidelagret som separat data/guide.json, inte utökning av reforms.json
**Date:** 2026-06-11
**Decision:** Huvudmannaguidens data (Sprint 11) ligger i en egen fil `data/guide.json` — en post per reform, nycklad på `reform_id` mot reforms.json. Synk-risken mellan filerna hanteras med runtime-validering: guide-vyn loggar reform-id utan guidepost och guideposter utan reform till konsolen (fail loud, aldrig tyst), och bevakningsautomatiseringens extract.js kan utökas att inkludera guide-id:n i manifestet.
**Reasoning:** (1) Etablerat mönster — varje datadimension är redan en egen fil (connections, uppdrag, malbild, tidslinje, utredningar; se DEC-004 med samma resonemang: separata data uppdateras utan att röra reformdatan). (2) reforms.json laddas av ALLA fem sidor vid varje sidvisning; guide-innehållet är textmassivt (ordagranna övergångsbestämmelser, kravlistor med källor) och behövs bara i guide-vyn — inbakat skulle det blåsa upp varje sidladdning och varje render-loop som itererar reformer. (3) /bevakning-patchar rör reforms.json-statusar ofta; en separat guide-fil ger mindre diffar och lägre konfliktyta per patch.
**Alternatives considered:** Utökning av reformposterna i reforms.json (noll synk-risk men filstorlek/rendering enligt ovan, och varje guide-uppdatering skulle diffa mot kartans kärndata); separat fil per reform (överdriven granularitet för ~16 poster, fler fetch:ar).

---

### DEC-008: Per-feed-degradering i RSS-watchern
**Date:** 2026-06-11
**Decision:** Ett RSS-flöde som inte går att hämta nollar inte övriga flödens täckning: felet fångas per feed och landar som `feed_fel` i rapportens floden[] → 🔴-varning i veckorapportens issue + "FEL" i footern. Exit 1 endast när ALLA flöden faller (då finns ingen RSS-täckning alls att rapportera).
**Reasoning:** statskontoret.se blockerar GitHub Actions-runners på nätverksnivå (fetch failed, persistent över flera körningar; lokalt fungerar flödet — trolig WAF/datacenter-IP-blockering, inte IPv6: domänen saknar AAAA). Med hård fail-loud per feed skulle ett permanent oåtkomligt externt värdskap göra HELA veckorapporten röd och utebliven — sämre än en rapport med explicit flaggad lucka. Fail loud-principen behålls i sak: felet är högljutt synligt i issuet, aldrig tyst.
**Alternatives considered:** Hård fail på första feed-felet (ursprungsdesign — ger permanent död veckorapport så länge statskontoret blockerar); retry/backoff (hjälper inte mot IP-blockering); proxy/spegel för statsliggaren (out of scope, ny infrastruktur). Regleringsbrev-deltan uteblir i CI tills blockeringen löses — fångas lokalt vid /bevakning-triage i stället.

---

### DEC-007: Riksdagen-watchern matchar på organ-kortkod + testas mot fångade API-svar
**Date:** 2026-06-10
**Decision:** Jobb B identifierar Utbildningsdepartementets direktiv via list-entryts `organ`-kortkod (`"U-dep"`), inte via fullständigt departementsnamn — och gör ingen detalj-fetch när `organ` redan finns på list-entryt. Full dir-beteckning byggs som `Dir. <rm>:<nummer>` (riksdagens list-API ger löpnumret och årtalet i skilda fält). Relaterade bet/rskr läses ur `dokumentstatus.dokreferens.referens` (referenstyp `behandlas_i`). Enhetstesterna drivs av RIKTIGA API-svar sparade som fixtures i `scripts/bevakning/fixtures/`.
**Reasoning:** Live-verifiering (T2-fix) visade att `dokument.departement` är `undefined` för direktiv även i detalj-svaret — bara `organ`-kortkoden finns. De tidigare mockarna antog fel format (fullt namn, beteckning med årtal, relaterade i dokuppgift) och gav 8/8 grönt medan jobb B i praktiken aldrig hittade något. Fixtures av skarpa svar gör att testerna fångar verkliga formatändringar istället för att cementera antaganden.
**Alternatives considered:** Matcha på fullt departementsnamn via detalj-fetch (omöjligt — fältet saknas för dir, och 1 extra anrop per dir/vecka i onödan); mappa organ-kortkod → fullt namn i rapporten (lätt tolkning, bryter mot principen att rapporten bara återger beskrivande faktapar); behålla syntetiska mockar (gav falskt grönsken — hela orsaken till T2-fix)

---

### DEC-006: SVG-overlay för kopplingslinjer i tidslinjen
**Date:** 2026-06-10
**Decision:** Kopplingslinjer utredning↔reform ritas i en enda SVG-overlay (`#ganttConnections`) inuti gantt-body, `pointer-events:none`, bezierkurvor beräknade från `getBoundingClientRect()`. Linjer ritas endast vid hover (tillfälligt) eller markering (pinned); aldrig vid load. Hover uppdaterar bara SVG-innehållet — ingen re-render av Gantt:en.
**Reasoning:** Gantt-body har variabel höjd (expanderbara rader) och staplar positionerade i procent. SVG ger exakta pixelkoordinater, rena diagonaler och skalar till multi-linjer (en reform → N utredningar) i ett enda lager som följer horisontell scroll automatiskt.
**Alternatives considered:** CSS-roterade divs (krångligt vid diagonaler, en div per linje, skalar dåligt), alltid-på-linjer (visuellt brus med 27 utredningar), Canvas (overkill för enstaka linjer)

---

### DEC-005: Utredningar på gemensam tidsaxel (Modell A)
**Date:** 2026-06-10
**Decision:** Tidslinjens axel förlängdes bakåt till 2021-01-01 och utredningar renderas som staplar på samma axel som reformerna, grupperade inom befintliga kategoriblock (kunskap/trygghet/larare/styrning) efter reformraderna. Visuell åtskillnad via dashed border + diagonalt stripe-mönster i samma kategoripalett. Poster utan verifierbart start/slutdatum skippas med console.warn — datum fabriceras aldrig. Reverse-links reform→utredningar beräknas vid render-tid från `kopplad_reform` (reforms.json modifieras inte).
**Reasoning:** En gemensam axel visar det kausala flödet utredning→reform direkt — utredningens slut ligger ofta nära reformens start. Separat vy eller fil hade dubblerat renderingslogik och tappat den visuella kopplingen.
**Alternatives considered:** Separat spatial fil/vy för utredningar (tappar tidssambandet med reformerna, mer kod att underhålla), egen sektion under Gantt:en (samma problem), datum i reforms.json (bryter mot principen att utredningsdata ägs av utredningar.json)

---

### DEC-004: Skolverkets uppdragsstatus som eget datalager
**Date:** 2026-03-23
**Decision:** Separat `skolverketUppdrag`-objekt med typ/kort/fulltext/kallor per reform. Visas som indikator (6px dot) på noder, detaljsektion i panelen, och modal för fulltext. Data från RB 2025/2026 och regeringsuppdrag.
**Reasoning:** Uppdragsstatus är en annan dimension än reformstatus (proposition vs beslutad). Separata data gör det enkelt att uppdatera utan att röra reformdatan. Modal för fulltext håller detaljpanelen kompakt.
**Alternatives considered:** Inline fulltext i detaljpanelen (för långt, scrollar bort annan info), tooltip (för liten för dessa textmängder)

---

### DEC-003: Mobil listvy (portrait) + kartvy (landscape)
**Date:** 2026-03-23
**Decision:** Portrait (<800px): scrollbar listvy med accordion-expandering, grupperad per kategori. Kopplingar som klickbara länkar. Landscape (mobil): växla till kartvyn med glesare nodlayout (max ~10% överlapp). Desktop: oförändrad kartvy.
**Reasoning:** 16 noder med linjer är för tätt för portrait-mobil oavsett zoom. En lista är det naturliga mobilmönstret. Landscape ger tillräckligt med yta för kartan om noderna separeras. Zoom/pan behålls i landscape för att navigera den glesare kartan.
**Alternatives considered:** Enbart zoom/pan utan listvy (testat i portrait, för trångt), enbart listvy utan kartväxling (tappar kopplingarna visuellt i landscape)

---

### DEC-002: ~~Mobilanpassning via zoom/pan + bottom sheet~~ (ERSATT av DEC-003)
**Date:** 2026-03-23
**Decision:** Pinch-to-zoom/pan på kartområdet, bottom sheet för detaljpanel, kompakta noder under 600px
**Reasoning:** Kartan har 16 noder med kopplingslinjer — för tät för en liten skärm utan zoom. Bottom sheet behåller kartan synlig medan detaljer visas. Ingen extern lib behövs.
**Alternatives considered:** Separat listvy för mobil (tappar det visuella), viewport-skalning via meta-tag (för grovt), extern lib som Panzoom (onödig dependency för ~50 rader JS)
**Utfall:** Testat — för trångt, dålig navigering. Ersatt av DEC-003.

---

### DEC-001: Single-file HTML with no build step
**Date:** 2026-03-23
**Decision:** Enkel HTML/CSS/JS i en fil (index.html), hostad via GitHub Pages
**Reasoning:** Projektet är en statisk informationsvisualisering utan backend. Inget byggsystem behövs. En fil är enklast att underhålla och dela.
**Alternatives considered:** React/Vite (onödig komplexitet för en sida), SSG som Astro (onödigt för en fil)

---
