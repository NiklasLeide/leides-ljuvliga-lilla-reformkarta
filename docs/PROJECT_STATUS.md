# Project Status — leides-ljuvliga-lilla-reformkarta

> **Last updated:** 2026-08-25
> **Current sprint:** Sprint 13 — Aktualiseringssprinten (rev B)
> **Sprint dates:** augusti 2026

---

## Sprint 13 — Aktualiseringssprinten (rev B)

**Mål:** Sajtens innehåll aktuellt och källbelagt per 2026-08-25 — tio veckors
bevakningsskuld (v.25–v.35, issues #4–#11) avarbetad, friskolebeslutet infört,
SFS-avstämning av juni-reformernas ikraftträdanden, grunden städad. Färskhetsstämpeln
ska åter tala för sajten — 19 dagar före valet.

**Miljö (T0 GODKÄND m. avvikelser):** gh CLI saknas → GitHub-ops via MCP. Sandbox-proxy
blockerar svenska myndighetskällor (403) → alla live-uppslag lyfta ur tasklistan,
ersatta med verifierade värden i bilaga A rev B (research gjord i Claude chat-projektet,
se DEC-017). **Skärpt regel:** ingen task får kräva extern hämtning utanför GitHub;
saknas ett värde i bilagan → stoppa och rapportera, patcha aldrig ur minne.

**Out of scope:** guideposter gy25/ai; val26-koppling; tillgänglighet; CSS-refaktor;
exkludering av docs/ ur Pages; ombyggnad av regleringsbrevsflödet (DEC-008 består);
automatgenerering av andringar; ny funktionalitet/redesign.

**Stop condition:** dev och master samma SHA + strö-branch borttagen; luckveckorna
30/32/33 täckta via backdaterade dispatch; regleringsbrevskontroll dokumenterad (A.7);
bilaga A-patchar applicerade med källor; SFS-avstämning dokumenterad + guide/reforms
konsistenta; andringar+meta uppdaterade (stämpel=patchdatum); issues #4–#11 stängda;
deployad till master med Pages-success; DoD passerad.

| ID | Task | Filer | Status | Acceptance (rev B) |
|----|------|-------|--------|------------|
| T0 | Miljösmoketest desktop-appen | (ingen) | ✅ Done | GODKÄND m. avvikelser: gh saknas→MCP; proxy blockerar myndighetskällor→live-uppslag ur scope (bilaga A rev B). Repo/remote/git verifierade; testsvit 61/61; strö-branch-checkout upptäckt (→T1). |
| T1 | Sprintregistrering + git-hygien | PROJECT_STATUS.md, DECISIONS.md, CLAUDE.md, git | ✅ Done | Brief rev B + bilaga A registrerad; DEC-017; CLAUDE.md default-branch master. **Git-hygien:** master/dev hade divergerat vid 2608f1c (master = merge/preview-sync-commits, dev = 3 docs-commits, sajtinnehåll identiskt). Löst via merge dev→master (`f41bede`, bokföring bevarad) + ff dev→master → **rev-parse dev master IDENTISKA (f41bede)**. Lokal strö-branch raderad. **2 förbehåll:** (1) remote claude/brief-session-isyBT kunde EJ raderas härifrån — git-http-proxyn blockerar ref-radering ("remote hung up") och GitHub MCP saknar delete-branch → Niklas raderar via GitHub UI (github.com/…/branches, ett klick). Innehållet är fullt subsumerat (Sprint 9→13), säkert att radera. (2) Master:dev/ preview-mappen följde med in i dev-branchen som konsekvens av identisk-med-master — kosmetisk (dev serveras ej), återdivergerar naturligt vid nästa commit.sh. |
| T2 | Backdaterad bevakning luckveckorna | GitHub Actions (dispatch via MCP) | ✅ Done | Tre workflow_dispatch via MCP (ref master, f41bede) för luckfönstren: 07-13→07-20 (run 17), 07-27→08-03 (run 18), 08-03→08-10 (run 19). **Alla tre completed/success.** Inga nya issues skapade (öppna = oförändrat #4–#11) → 0 rapporterbara deltan i luckveckorna 30/32/33. Belägg (jobblogg run 19): "0 props i fönstret · 3 direktiv i fönstret · 0 SOU i fönstret", steget "Skapa issue" = skipped, "Tom körning" = success. Inga nya skolrelevanta deltan → inget att rapportera för patch. Not: loggen visar "regleringsbrev FEL" = känd DEC-008-degradering (feeden trasig på GitHub-runnern) → hanteras av manuell kontroll A.7/T3. |
| T3 | ~~Manuell regleringsbrevskontroll~~ | — | ✅ UTGÅR | Ersatt av bilaga A.7 (research-ledet). Regleringsbrevsvarningar i #4–#11 stängs i T9 m. hänvisning A.7 + Niklas okulärkontroll. |
| T4 | Datapatch utredningar.json | data/utredningar.json | ✅ Done | Fem poster per A.2 rev B: U 2024:04→SOU 2026:37 (2026-06-17), U 2025:05→SOU 2026:50 (2026-08-13, not: riksdagen anger 08-14), U 2025:02→SOU 2026:51 (2026-08-17), S 2024:01→SOU 2026:52 (2026-08-18, i tre delar), Fi 2025:07→SOU 2026:44 (2026-07-02) + namn→"Utredningen om integritetsfrämjande teknik i förvaltningen". Alla status→avslutad, betänkanden typ=slut, käll-URL i kallor per A.2. Alla fem hade nått sin redovisning-deadline och levererat slutbetänkande → avslutad (Fi explicit i rev B, U 2025:05 explicit slutbetänkande; övriga tre: slut härlett ur levererat betänkande + passerad deadline — flaggat i taskrapport). JSON validerar, manifest fångar alla 5 SOU, testsvit 61/61. |
| T5 | Datapatch reforms.json — vinst | data/reforms.json | ✅ Done | vinst→beslutad per A.1: ref Prop. 2025/26:292, ikraft 1 juli 2027, time ["2027"], 8 nyckelförändringar (ordagrant ur Beslut i korthet UbU30), transition m. bet. 2025/26:UbU30 + prop-datum 2026-06-25 + riksdagsbeslut 2026-08-13. **Rskr avvikelse:** ej publicerad 2026-08-25 → noterad i transition ("rskr ej publicerad"), inget rskr-fält finns i schemat. Länkar: prop + betänkande + pressmeddelande. JSON validerar, testsvit 61/61. **Konsekvens:** vinst är nu beslutad utan guidepost → guide.html console.warn (samma klass som gy25/ai, guidepost out of scope). |
| T6 | SFS-avstämning juni-reformerna (krympt) | data/guide.json, data/reforms.json | ✅ Done | A.6: (a) guide.json tid-postens tre ikrafttradanden kompletterade med SFS i omfattning: 2026-08-01→SFS 2026:1096, 2027-07-01→SFS 2026:1097, 2028-07-01→SFS 2026:1243. (b) reforms.json tid ikraft "Ej fastställt"→"1 aug 2026 / 1 juli 2027 / 1 juli 2028" (slash-format som yrkes). (d) övriga juni-reformer oförändrade (laroplaner/stod/betyg=1 juli 2028, yrkes=1 juli 2026/2 juli 2028). (c) andringar 2026-06-09-posten görs i T8 (andringar.json = T8:s filägo). Top-level guide `sfs`-fält lämnat null (reformen spänner 3 SFS, fältet enkelvärt; A.6 dirigerar SFS→omfattning). JSON validerar, testsvit 61/61. |
| T7 | Datapatch uppdrag.json | data/uppdrag.json | ✅ Done | **Digitala prov** (2026-07-24, `de81844`) infört under betyg.relaterade. **Införandestöd** (U2026/01265, 2026-06-23) infört per A.3 rev C under FEM noder (studiero, laroplaner, stod, tid, betyg) med per-nod prop-referens (193/194/195/196/197 + bet/rskr); uppdragstextens formuleringar (implementeringsinsatser, utvärderingsförslag 2 nov 2026, delredovisning 1 juni 2027, slutredovisning 15 juni 2029); formatering bevarad (64 insertions), uppdrag.html 0 konsolfel. **andringar-post: nej** (val rapporterat — implementeringsuppdrag hör i uppdragsvyn, inte andringar; konsekvent med digitala prov). **Statsbidrag yrkesvux**: AVFÖRD per rev B. JSON validerar, språkregel 0, testsvit 61/61. |
| T8 | andringar.json + meta.json + språkfix | data/andringar.json, data/meta.json | ✅ Done | 9→15 poster. Ny post 2026-08-13 vinst (prop 292, källa bet. UbU30 — rskr null). 5 betänkandeposter per A.2 (datum=överlämning: SOU 2026:37/44/50/51/52). Post 2026-06-09 tid: text→"propositionen Tid för undervisningsuppdraget" + stegvis ikraft 1 aug 2026/1 juli 2027/1 juli 2028 (SFS 1096/1097/1243) — uppfyller även T6(c). **reform_id-schemafråga (rapporterad före commit):** utredningsposter får reform_ids = utredningens kopplad_reform om giltig reform (SOU 2026:37→["sprak"]), annars [] (4 st) — fail-loud förblir grön, tomma id ger ingen tagg men renderar posten. meta.json=2026-08-25 (patchdatum, flera beslut → dagens datum). Språkregel 0. Headless: 15 poster, 9 datumgrupper desc, 15 källänkar, 0 app-konsolfel. Testsvit 61/61. |
| T8b | Ändring av läroplansuppdraget (fynd utanför bevakningen) | data/uppdrag.json, data/andringar.json, data/tidslinje.json, data/meta.json | ✅ Done | Ändring U2026/00888 (2026-08-24): läroplansförslagens redovisning senareläggs 31 mars→14 maj 2027; expertersättning om U 2023:09-expert avsäger sig. Införd som relaterade i uppdrag.json noderna laroplaner + tioarig; andringar.json ny post 2026-08-24 (reform_ids laroplaner+tioarig); **tidslinje.json posten laroplaner-forslag FANNS → datum 2027-03-31→2027-05-14** (kalla noterar senareläggningen). meta.json→2026-08-26. JSON validerar, språkregel 0, fail-loud grön, headless 16 poster/0 konsolfel, testsvit 61/61. **Backloggkandidat (ingen åtgärd):** bevakningens departementsfilter fångade inte detta trots U-dep som avsändare — deltatypen "ändring av regeringsuppdrag" saknas sannolikt i skriptet. |
| T8c | v.36-triage (issue #12) | data/utredningar.json, data/andringar.json, data/meta.json, .claude/commands/bevakning.md | ✅ Done | Ny utredning **U 2026:04** "Utredningen om åtgärder för lämpliga klasstorlekar" (Dir. 2026:96, tillsatt 2026-08-27, redovisas 2028-01-28, kopplad_reform `tid`, utredare null); direktivets uppdragsformuleringar i noteringar. **S 2025:08** fick tilläggsdirektiv Dir. 2026:98 (2026-08-28 per researchledet; riksdagen anger 08-27 — noterat; innehåll null, kompletteras nästa /bevakning). andringar.json ny post 2026-08-27 (17 poster). meta.json→2026-09-05. Konventionen "nya spårade utredningar → andringar-post" inskriven i /bevakning. Issue #12 disponerad + stängd. JSON validerar (7 filer, 30 utredningar), språkregel 0, testsvit 61/61. |
| T9 | Stäng issues #4–#11 | GitHub Issues (MCP) | ✅ Done | Alla 8 issues (#4 v.25 – #11 v.35) disponerade per punkt via MCP och **stängda** (state_reason=completed, 0 öppna bevakning-issues kvar). Dispositioner: prop-status-A → beslutade sedan v.24; prop 292 → T5+T8; utredningsbetänkanden (SOU 37/44/50/51/52) → T4+T8; digitala prov-uppdrag → T7; icke-skol-SOU/direktiv (34,36,38,39,41,42,43,46,47,48,54; Dir 2026:75/82) → avförda A.4; regleringsbrev → A.7. Läroplansändringen (T8b) noterad i #11 som departementsfilter-lucka. T2:s backdaterade körningar skapade inga nya issues. **Uppdatering (verifieringssteg):** A.7 regleringsbrevskontroll är GJORD i researchledet 2026-08-26 (inga ändringsbeslut för skolmyndigheterna sedan 2026-06-01) → ingen okulärkontroll krävs, issues förblir stängda. Issue-kommentarernas "okulärkontroll som acceptansgrind" är en kvarvarande överförsiktighet (issues stängda, ingen åtgärd behövs). |
| T10 | Deploy Sprint 13 | (deploy) | ✅ Done | dev→master via ./deploy.sh (normal merge, ingen force/reset). **Merge-SHA `10b3957`; föregående master-SHA `512ff63` (rollback-punkt).** Master-egna commits före deployen var 7 st preview-syncar som bara rörde dev/ — mappen dev/ behållen. GitHub Pages "build and deployment" för 10b3957 = **completed/success** (run 124, 2026-09-05T06:25Z). Master-roten verifierad: meta.json=2026-08-26 (stämpel), 16 andringar-poster, vinst=beslutad, tid ikraft stegvis. |
| T11 | DoD review | PROJECT_STATUS.md | ⬜ | dod-reviewer mot stop condition; avvikelser dokumenterade; Sprint 13→Completed. |

### Noteringar & avvikelser (Sprint 13, till T11)
- **A.7 regleringsbrevskontroll** utförd i researchledet 2026-08-26: grundbeslut för budgetåret 2026 daterade 2025-12-18; inga ändringsbeslut för Skolverket, Skolinspektionen, SPSM eller Skolforskningsinstitutet sedan 2026-06-01. Issues #4–#11 förblir stängda, ingen okulärkontroll krävs.
- **Backloggkandidater (ingen åtgärd i Sprint 13):** bevakningens departementsfilter missar (a) tvärdepartementala skoluppdrag (t.ex. Socialdep./Skolverket 2026-07-31) och (b) deltatypen "ändring av regeringsuppdrag" (t.ex. U2026/00888, 2026-08-24, T8b).
- **Accepterad avvikelse:** `vinst` är beslutad utan guidepost → console.warn i guide.html (samma klass som gy25/ai). Guidepost-backlogg: gy25, ai, vinst.
- **T7 införandestöd (U2026/01265):** infört under fem noder per A.3 rev C. Ingen andringar-post (implementeringsuppdrag hör i uppdragsvyn — val rapporterat).
- **T1 klart:** strö-branch claude/brief-session-isyBT raderad (av Niklas via GitHub UI), verifierat borta på origin.

---

## Completed: Sprint 12 — Trovärdighetssprinten

DoD-granskad och GODKÄND (T8, 2026-06-17) — alla 8 stop-condition-led verifierade
mot verktygsresultat: nav (Guide+Ändringar) på 8 sidor, färskhetsstämpel ur meta.json
(0 hårdkodade), andringar.html med 9 källbelagda poster, full meta/OG/canonical/og:image,
mockups ur produktion, /bevakning underhåller meta.json+andringar.json, 61/61 node-tester,
Pages-deploy f92b914 success. Deployad till produktion (T7).

### Kända avvikelser (dokumenterade, accepterade — åtgärdas inte i Sprint 12)
- **Live-URL-rendering + OG-delningspreview ej körd härifrån.** Sandboxen når inte
  reformer.leide.se (curl 000 / WebFetch 403). Beläggen är GitHub Pages deploy-success
  för exakt deploy-SHA + verifierat master-innehåll. Niklas slutkontroll i browser
  (rendrerad sida + t.ex. OG-debugger) återstår — acceptansgrind, ej blockerande.
- **gy25 + ai saknar guideposter** (känd sedan Sprint 11, uttalat out of scope här —
  kräver egen researchrunda).
- **Internt docs/ (utom docs/mockups) serveras fortfarande av GitHub Pages.**
  Pre-existerande, utanför T6-scope (T6 exkluderade bara det arkiverade mockup-materialet).
  Kandidat: exkludera hela docs/ ur Pages i en framtida städning (planeringsdokument
  behöver inte vara publikt nåbara).

## Sprint 12 — Trovärdighetssprinten

**Mål:** att en tjänsteman som landar på sajten, eller får en länk delad till sig,
omedelbart ser att sajten är aktuell, bevakad och delbar. Sajtens största brister
är inte innehållet utan förtroendesignalerna runt det: deploy-släp, en hårdkodad
"mars 2026"-stämpel som ljuger, osynlig bevakning, saknad delningsmetadata och
mockupfiler som läcker till produktion.

**Out of scope:** tillgänglighetsarbete (aria/tangentbord på SVG-kartan);
CSS-refaktor/delad stylesheet; guideposter för `gy25` och `ai` (egen researchsprint);
lagbeslutad-vs-utredning inför val26 (kräver scope-diskussion); self-hostade fonter,
print-CSS, notiser/prenumeration; automatgenerering av andringar-poster ur git-historik
(manuell/kommandodriven pipeline i v1); ny kartfunktionalitet och visuell redesign.

**Stop condition:** live-sajten visar komplett nav inkl. Guide och Ändringar;
färskhetsstämpel läses ur data/meta.json och ingen hårdkodad "mars 2026" finns kvar;
andringar.html är live med källbelagd seedad data; alla publika sidor har description
+ OG + canonical + og:image; mockupfiler är borta ur produktion; /bevakning-kommandot
underhåller både meta.json och andringar.json; DoD passerad.

| ID | Task | Filer | Status | Acceptance |
|----|------|-------|--------|------------|
| T1 | Sprintregistrering Sprint 12 | PROJECT_STATUS.md | ✅ Done | Mål, scope, stop condition och tasktabell registrerade |
| T2 | Deploy Sprint 11 till produktion | (deploy) | ✅ Done | dev→master merge `7654f5c` pushad; guide.html/guide-alla.html/utredningar.html på master-roten; Guide+Utredningar-nav på alla 7 publika sidor; guide.html laddar guide.json. GitHub Pages "build and deployment" för 7654f5c = completed/success. **Sandboxen når ej reformer.leide.se (curl 000/WebFetch 403) — rendrerad live-sida ej hämtbar härifrån; Pages-deploysuccess + verifierat master-innehåll är beläggen. Niklas bekräftar i browser.** |
| T3 | Dynamisk färskhetsstämpel | data/meta.json, alla publika .html, .claude/commands/bevakning, MAINTENANCE.md | ✅ Done | data/meta.json {senast_uppdaterad:"2026-06-12"} (= senaste data/-commit ef1cda6, verifierat i git). Alla 7 publika sidor: header-badge + footer-datum → `[data-fresh]`-span fylld av inline-script som parsar strängen manuellt (ingen new Date()-glidning), tyst fallback vid läsfel. grep "mars 2026"/"Sammanställd" = 0 i publika sidor (mockups malbild/reformkarta kvar → T6). Headless-verifierat (Playwright, 7 sidor): varje span fylld "12 juni 2026", 0 app-konsolfel. /bevakning steg 4 bumpar meta.json; MAINTENANCE.md dokumenterar regeln för manuella patchar. |
| T4 | Sidan Senaste ändringar | andringar.html, data/andringar.json, alla publika .html (nav), .claude/commands/bevakning | ✅ Done | data/andringar.json seedad med 9 källbelagda poster (de nio riksdagsbesluten från Bevakning v.24), genererade FAITHFULLY ur reforms.json:s transition-fält (beslutsdatum + bet./rskr.), kalla.url mot data.riksdagen.se/dokument/HD01UbUNN.html (verifierat schema). datum=beslutsdatum (DEC-016). andringar.html återanvänder befintligt sidskal, omvänt kronologisk grupperad per datum, reform-taggar (deeplink), källänkar. reform_ids runtime-validerade (fail-loud). "Ändringar" i nav på alla 8 sidor. Headless-verifierat: 9 poster, svenska datum nyast först, 9 källor, stämpel fylld, 0 app-konsolfel, 375px 0 overflow, fail-loud bevisad med medvetet fel-id (route-override, ej committat). /bevakning steg 4 lägger post per delta. |
| T5 | Meta/OG/canonical + og-bild | alla publika .html, assets/, commit.sh | ✅ Done | Alla 8 publika sidor: unik `<meta description>` (~150 tecken, deskriptiv, 0 rådgivande ord), canonical + og:type/locale/url/title/description/image (6 og:*-taggar) med absoluta https://reformer.leide.se/-URL:er. assets/og-image.png (1200×630, giltig PNG, textbaserad i sajtens formspråk — kategoriprickar + serif-titel "Reformkartan" + reformer.leide.se, genererad via Playwright-screenshot) refererad med absolut URL från alla sidor. commit.sh stageär nu assets/ (annars tyst utebliven binärfil). Källverifiering mot live sker vid T7 (sandboxen når ej reformer.leide.se; taggar verifierade i källan, Niklas delningspreview-kontroll efter deploy). |
| T6 | Städa repo-roten | reformkarta.html, docs/mockups/*, data/malbild.json, _config.yml, CLAUDE.md, commit.sh, CHANGELOG.md | ✅ Done | Grep: 0 skarpa sidor länkar till någon av de tre filerna. **Beslut per fil:** reformkarta.html → RADERAD (superseded prototyp, index.html är kanon, inget referensvärde utöver git). lasarshjul-mockup.html → FLYTTAD docs/mockups/ (DEC-015-spec för guide.html). malbild.html + data/malbild.json → FLYTTADE docs/mockups/ (verklig Sprint 3-feature, dold, superseded; json:en användes bara av den). docs/ serveras av GitHub Pages (default Jekyll, ingen .nojekyll) → nytt `_config.yml` med `exclude: [docs/mockups]` gör arkivet icke-serverat, så filerna är faktiskt ej nåbara på reformer.leide.se (inte bara olänkade). docs/mockups/README.md dokumenterar arkivet. CLAUDE.md-katalogstruktur uppdaterad (148 rader). commit.sh stageär nu *.yml (annars missas _config.yml). Roten har exakt de 8 publika sidorna. |
| T7 | Deploy Sprint 12 | (deploy) | ✅ Done | dev→master merge `f92b914` pushad. GitHub Pages "build and deployment" för f92b914 (inkl. nya _config.yml) = completed/success — Jekyll-configen bröt inget. Master-roten verifierad: 0 "mars 2026" på alla 8 publika sidor, meta/OG/canonical + og-image på plats, andringar.html + meta.json med, mockupfiler borta ur roten (i docs/mockups/, exkluderade ur Pages). **Sandboxen når ej reformer.leide.se — rendrerad live-sida + delningspreview (OG-debugger) är Niklas slutkontroll; Pages-deploysuccess + verifierat master-innehåll är beläggen härifrån.** |
| T8 | Run DoD review for this sprint | PROJECT_STATUS.md | ✅ Done | Subagent-DoD mot stop condition: alla 8 led GODKÄNDA med verktygsbelägg (nav 8 sidor, färskhetsstämpel headless-verifierad, andringar.json källbelagd + fail-loud, meta/OG/canonical/og:image komplett + unik, mockups ur master-roten, /bevakning+MAINTENANCE, 61/61 node-tester, Pages-deploy f92b914 success). Inga åtgärdskrävande avvikelser; 3 kända avvikelser accepterade och dokumenterade ovan. Sprint 12 → Completed. |

---

## Completed: Sprint 11 — Huvudmannaguiden

DoD-granskad 2026-06-16 (T6). **Stängd** — Niklas granskning 2K + mobil godkänd.
Deploy till produktion krävs: guide.html + guide-alla.html är live först efter `./deploy.sh` (master).

### Kända avvikelser (dokumenterade, åtgärdas inte i Sprint 11)
- **Täckning, 2 reformer utan guidepost:** `gy25` (Lag 2022:147, ikraft 1 juli 2025) och `ai` (EU 2024/1689, stegvis 2024–27) saknar guideposter i guide.json (12/14 beslutade reformer täckta). Båda kräver källverifierad klartext+paverkan-författande; datapatch utanför Sprint 11-scope. Kandidater för uppföljningssprint.
- **Användartest med målgrupp ej genomfört.** Niklas granskning är acceptansgrind (utförd 2026-06-16, 2K + mobil).
- **Läsårsgränsen delar sommarklustret 2026** (30/6 + 15/7 i läsåret 25/26, 1/8 i 26/27) — medvetet designval, läsårslogiken prioriterad. Spannet uttalat i hjulrubriken ("Läsåret 2025/26 · augusti–juli").
- **"T5.2c"-commiten omdöpt till T5.3 i PROJECT_STATUS** efter att den pushats — fryst historik, dokumenterat i DEC-014.
- **Startkortets aldrig-tomt-fallback** (numera hjulets tomläge) ej browser-triggbar med nuvarande data (alla nuvarande val ger ≥1 träff någonstans i framtida läsår). Logiken finns; bevisad endast via kodgranskning.
- **/goal-pilotens två felkonstruktioner** dokumenterade i DECISIONS.md (DEC-014 + processnotering i T5.7).

## Sprint 11 — Huvudmannaguiden

**Mål:** guide.html — skyldighetscentrerad tidslinje för enskilda huvudmän:
vad gäller, vem berörs, från när. Varje rad spårbar till författning/beslut.
Överblick, aldrig rådgivning.

**Out of scope:** prenumeration/notiser; rådgivande formuleringar; kommunala
huvudmän som egen anpassning; automatgenerering av guideposter ur bevakningen
(manuell pipeline i v1); val26-koppling.

**Stop condition:** guide.html på dev med batch 1–3-data; varje krav har källa
i {text, url}; språkregeln maskingranskad (inga bör/rekommenderar/råder i
guidetext); 375px manuellt verifierad; "på väg"-sektion skiljer beslutat från
kommande; DoD passerad.

**Överlappning:** Sprint 10 stängs med T6 (DoD-review) 2026-06-16 — körs parallellt
tills dess.

**Designbeslut (T1):**
- **Guidelagret = separat `data/guide.json`**, en post per reform nycklad på
  `reform_id` — INTE utökning av reforms.json. Fullt resonemang i **DEC-009**;
  kort: etablerat en-fil-per-dimension-mönster (DEC-004), reforms.json laddas av
  alla fem sidor medan guide-texten (ordagranna övergångsbestämmelser, kravlistor)
  bara behövs i guide-vyn, och /bevakning-patchar får mindre diffar. Synk-risken
  hanteras med runtime-validering i guide-vyn (id-mismatchar loggas, fail loud).
- **Språkregeln gäller modellen:** fältnamn och värden bär "gäller/berör/innebär"-
  semantik (ikrafttradanden, berors, krav = författningens krav), aldrig
  rekommendationssemantik (inga "bör"-fält, checklistor eller råd). Alla
  textvärden är officiella formuleringar ur författning/prop med källa.

**Datamodell per guidepost** (datakontrakt för researchen — inga datavärden ännu):

| Fält | Typ | Kontrakt |
|---|---|---|
| `reform_id` | sträng | Måste matcha `id` i reforms.json (runtime-validerad) |
| `ikrafttradanden` | lista av `{datum, typ, omfattning}` | FLERA per reform förekommer (tid-reformen har tre steg: 2026-08-01, 2027-07-01, 2028-07-01). `datum` ISO; `omfattning` = officiell formulering av vad som träder i kraft det datumet. `typ` (tillagd i T3): `"ikraft"` (författningens ikraftträdande) eller `"tillampning"` (författningsexakt "tillämpas första gången"-datum, t.ex. tioarig 2028-07-01). **Pivotregel för guidevyn (T4):** tidslinjen pivoterar på tillampning-posten när sådan finns — det datum som träffar verksamheten — med ikraft synligt sekundärt. Tillämpningsstart som INTE är författningsexakt ("höstterminen 2028") bärs i omfattningstexten, aldrig som eget datum |
| `overgangsbestammelser` | lista av `{text, kalla:{text,url}}` | `text` = ORDAGRANN författnings-/proptext, ingen parafras |
| `berors` | `{skolformer:[], huvudmannatyper:[]}` | Officiella skolformsbeteckningar; huvudmannatyper som explicit lista (kommunal/enskild/statlig — inget "alla"-specialvärde, det officiella beslutet anger vilka) |
| `krav` | lista av `{text, kalla:{text,url}}` | `text` = officiell formulering av kravet; källa till primärkälla (regeringen.se/riksdagen.se/SFS) |
| `sfs` | sträng eller null | SFS-nummer; null tills kungörelse skett (kungörelsen släpar efter färska beslut — null betyder "ej kungjord ännu", aldrig gissad) |
| `senast_andrad` | ISO-datum | Sätts/uppdateras av samma rutin som /bevakning-datapatcharna |
| `noteringar` | sträng eller null | Tillagd i T2 (krävs av regeln "overifierbart → null + notering"; precedens utredningar.json): redovisar null-orsaker, representationsbeslut och vad som medvetet lämnats i källan |
| `klartext` | `{text, kalla}` | Tillagd i T5.2a (DEC-012): 1–2 egenförfattade deskriptiva meningar om vad som ändras; spårbar källa; utökad språkregel (även "måste ni"/"se till att" förbjudna); visas visuellt åtskild från citat |
| `paverkan` | `{text, kalla}` eller null | Tillagd i T5.2a (DEC-012): vad ändringen innebär för huvudmannen i drift, klarspråkad ur propens konsekvensavsnitt med avsnittshänvisning; null + notering om propen saknar huvudmannakonsekvenser |

**Exempel-post — FIKTIV, illustrerar enbart formen (committas INTE i data/);
«…» markerar platshållare där researchen ska sätta verifierad officiell text:**

```json
{
  "reform_id": "exempel-reform",
  "ikrafttradanden": [
    { "datum": "2026-08-01", "omfattning": "«officiell formulering: vilka bestämmelser som träder i kraft detta datum»" },
    { "datum": "2028-07-01", "omfattning": "«officiell formulering för steg två»" }
  ],
  "overgangsbestammelser": [
    {
      "text": "«ordagrann övergångsbestämmelse ur författningen eller propositionens lagförslag»",
      "kalla": { "text": "Prop. 20XX/XX:NNN s. NN", "url": "https://www.regeringen.se/…" }
    }
  ],
  "berors": {
    "skolformer": ["grundskola", "anpassad grundskola"],
    "huvudmannatyper": ["kommunal", "enskild"]
  },
  "krav": [
    {
      "text": "«officiell formulering av vad huvudmannen ska göra enligt författningen»",
      "kalla": { "text": "Bet. 20XX/XX:UbUNN", "url": "https://www.riksdagen.se/…" }
    }
  ],
  "sfs": null,
  "senast_andrad": "2026-06-11"
}
```

| ID | Task | Filer | Status | Acceptance |
|----|------|-------|--------|------------|
| T1 | Sprintregistrering + datamodell guidelagret | PROJECT_STATUS.md, DECISIONS.md | ✅ Done | Modell dokumenterad med fiktiv exempel-post (ej i data/); fil-vs-utökning avgjort och motiverat (DEC-009); språkregeln inbakad i kontraktet; inga datavärden (7bfc805) |
| T2 | Ingestion batch 1+2 (9 reformer) + ordagrann extraktion övergångsbestämmelser | data/guide.json | ✅ Done | 9 poster, 40 krav samtliga källsatta {text,url} mot data.riksdagen.se; övergångsbestämmelser ordagrant ur prop-texterna (bilagornas utredningsförslag exkluderade); mobilfri-datum dubbelverifierat (lagförslag + UbU22 beslut i korthet); "mindre huvudman"-def + meritvärde-lägst-4 ordagrant; berors=null+notering där skolformslista ej verifierad (tid, brott, register-skolformer); noteringar-fält tillagt i kontraktet; språkregel-grep: 2 "bör"-träffar = citerad riksdagstext (citat-undantagsregel behövs i T6-granskningen). Diff godkänd av Niklas före commit. |
| T3 | Ingestion batch 3 (genomförda reformer) + SFS-komplettering | data/guide.json | ✅ Done | profession/timplan/tioarig inlagda (12 poster totalt, 49 källsatta krav). Professions ändringshistorik i overgangsbestammelser med båda källorna (2025-01-01→2025-09-01 via prop 2023/24:166/UbU4); gällande datum i ikrafttradanden. Representationsbeslut: typ-fält ikraft/tillampning infört på ALLA poster + pivotregel för T4 dokumenterad i kontraktet. SFS-komplettering via Skolverkets Aktuella regeländringar, varje nummer verifierat mot svenskforfattningssamling.se: tioarig 2025:729, profession 2023:393 (ursprungslagen, ur prop 166), yrkes 2026:960 (steg 1); timplan + T2-reformerna i övrigt ej kungjorda/ej belagda → null med notering. Diff godkänd av Niklas före commit. |
| T4 | Guidevyn | guide.html | ✅ Done | Händelsebaserad skyldighetstidslinje (19 händelser, 8 grupper inkl. Gäller redan + På väg), gap-regel för tillämpningspivot (DEC-010). Slutvillkor verifierade med Playwright/Chromium mot lokal server: 61 node-tester gröna, 0 orphans/0 källösa i valideringen, 0 konsolfel (Cloudflare-beacon CORS-blockeras på localhost — testartefakt, exkluderad), språkregel 0 träffar i guide.html-UI:t + exakt de 2 dokumenterade citat-undantagen i guide.json ("Proven bör rättas centralt" + dess notering). Filter (multi-select skolform, synlighet enbart), Ändrat nyligen (30d), null-berors renderas "Ej specificerat i beslutet", SFS-badges, senast_andrad synligt, På väg härledd ur status (3 utredningar, fast formulering utan kravspråk). /goal visade sig vara en sessionsbunden stop-grind (aktiverades efteråt och verifierade samma slutvillkor — alla höll). |
| T5 | Korslänkning karta↔guide + 375px | guide.html, index/tidslinje/övriga .html | ✅ Done | Guide-flik i nav på alla 6 sidor; Guiden-länk i kartans båda detaljpaneler + tidslinjens 4 detaljvyer (datadrivet via guideIds — reformer utan guidepost länkar inte); ?reform=-deeplinks åt båda håll verifierade i browser (guide→karta: selectNode+scroll; guide→tidslinje: selectReform; in till guiden: markerat kort + scroll). 375px: 0px horisontell overflow på alla sidor utom tidslinje (Gantt scrollar by design); touch-targets 44px (chips/summary/länkar uppmätta); fix: 6:e nav-fliken gav 67px overflow på uppdrag/reformer → overflow-x:auto på .tab-nav (utredningar-mönstret, säkert — naven sidscrollar inte vertikalt); aktiv flik scrollas in i synfältet. Vision-granskning utförd på viewport-skärmdumpar (375 + desktop) — Niklas gör slutlig manuell mobilkoll. |
| T5.1 | Designpass — "viktiga datum"-mönstret | guide.html | ✅ Done | Omdesign till datumtjänst-genren (DEC-011, inkl. förkastat step-by-step): hero "Närmast i tid" (3 närmaste, filteroberoende — aldrig tom yta), skolformsval med 44px-chips sparat i URL+localStorage (URL vinner, rensas med ett tryck, verifierat över reload), kronologisk lista med årsavdelare + datum primärt + GOV.UK-radmönster (hela raden klickbar, gemena statusar gäller redan/träder i kraft/tillämpas, en stödtextrad med ellipsis), tre hopfällda nivåer (rad→krav→ordagranna övergångsbestämmelser/SFS/korslänkar), caveat i sidhuvudet. På väg + Ändrat nyligen underordnade efter listan. Innehåll/kontrakt/DEC-010 orörda. Verifierat i browser: 0 konsolfel, 0px 375-overflow i alla tre lägena (fix: rad-stöd inline→block), 19 rader/6 årsavdelare/3 hero-kort, persistens + 0-träffsläge + deeplink ?reform= fungerar; vision-granskning av a/b/c-skärmdumpar 375+desktop utförd. Språkregel UI: 0 träffar. Niklas gör slutlig mobilkoll. |
| T5.1-fix | Sidfiler glob-buggen utelämnade + commit.sh-fix | commit.sh, guide.html | ✅ Done | Commit 1d2bd4b: glob-utelämnande i tidigare commit.sh stagade inte alla T5.1-sidfilerna; commit.sh-fix säkrar att alla guide-relaterade filer fångas (kompletterar Sprint 10 T1-fix:s glob-individuering). |
| T5.2a | Klarspråk + påverkan i guide.json | data/guide.json, DECISIONS.md | ✅ Done | klartext {text,kalla} + paverkan {text,kalla} i alla 12 poster (DEC-012 — Niklas principbeslut: deskriptivt, spårbart per mening, visuellt åtskilt i T5.2b). paverkan extraherad ur propparnas konsekvensavsnitt — alla 12 hade huvudmannakonsekvenser (10 explicita enskilda-avsnitt med verifierade nummer, betyg/register/yrkes via rubrikhänvisning), ingen null behövdes. Utökad språkregel verifierad: 0 träffar på bör/rekommenderar/råder/måste ni/se till att i nya fälten (propens "se till att" i professionskällan medvetet omskriven). senast_andrad → 2026-06-12. krav/övergångsbestämmelser orörda. Diff (108 rader) godkänd av Niklas. UI-rendering = T5.2b. |
| T5.2b | UI-rendering klarspråkslagret + startöverblick + relativ tid | guide.html | ✅ Done | Klartext som nivå 1-rubrik på alla 19 rader (maskinverifierat mot guide.json; reform.short som kicker, officiell omfattning som stödrad — visuellt åtskilt per DEC-012: klarspråk rak stil, citat kursiva på platta). Nivå 2 inleds med klartext-källa + paverkan-block ("För huvudmannen — ur propositionens konsekvensavsnitt", ramad rak stil). Startöverblick [data-test=start-overblick] med lägesräkning (2 gäller redan · 17 kommande · 3 på väg); relativ tid [data-test=relativ-tid] på hero + alla rader ("om 18 dagar"/"för 2 år sedan", 22 element). Verifierat: 0 konsolfel, 0px 375-overflow inkl. nivå 2 öppen, 4 testsviter gröna, vision-granskning desktop+375. **Språkregel-undantagen är nu TRE dokumenterade citat**: "Proven bör rättas centralt" (betyg, krav + notering) och "se till att sådana händelser hanteras" (tid, krav — UbU25:s ordagranna formulering, noterad i posten). |
| T5.2b-omtag | Konkret startnivå med klartext och påverkan | guide.html, DECISIONS.md | ✅ Done | DEC-013. Startkort: nästa deadline för vald verksamhet (30 juni 2026 — om 3 veckor vid verifiering) med klartext-rubrik + påverkan som enda stycke, 12-månadersräknare, tidslinjeväg; valstyrd och aldrig tom (fallback till alla med ärlig etikett — browser-verifierad med gymnasieskolan-val: 1 juli, 1 kommande/12 mån). Nivåflytt: officiell rubrik+omfattning+påverkan = nivå 2-topp; krav+övergångsbestämmelser+SFS+korslänkar = nivå 3; enhetlig citatstil (3px ink-vänsterkant, computed-verifierad). Mobil: valet hopfällt bakom Välj verksamhet-knapp — startkortet uppmätt HELT ovanför fold (topp 315/botten 637 vid 375×812), 0px overflow alla lägen, 0 konsolfel, 19/19 klartext-rubriker, 20 relativ-tid-element, sviterna gröna. Vision-granskning 375+desktop × utan val/med val/nivå 2+3: startkortet konkret (verkligt datum, verklig påverkansmening). |
| T5.3 | Tidsgruppsöversikt (första leverans — ofullständig mot brief) | guide.html | ✅ Done (kompletterad i T5.3-fix) | Byggde enbart räknarpillren: klickbara periodräknare som följer verksamhetsvalet, nollgrupper dämpade. **Avvikelse mot brief dokumenterad i DEC-014**: sammanfattningens en-radare och På g-gruppen utelämnades (målvillkoret formulerades som räknarbart element och jag levererade minsta uppfyllande tolkning). Beteckningen felskrevs dessutom T5.2c — rättad. |
| T5.3-fix | En-radare och På g-grupp enligt brief | guide.html, DECISIONS.md | ✅ Done | [data-test=oversikt] är nu en faktisk sammanfattning: räknarpillren kvar som navigering (scrollar till sin grupp, + ny "på g"-pill), därunder grupperade en-radare per reform — datum (relativ tid <12 mån), klartextens FÖRSTA mening, berörda-chips (max 3 + räknare; dolda på 375 där de finns i posten) — hela raden öppnar sin post (browser-verifierat: 2027-klick öppnade brott). På g-gruppen tillagd ur ej-beslutade reforms-statusar med fast formulering "inga skyldigheter gäller än" (ingen verksamhetskoppling → dämpas aldrig av valet). Val filtrerar en-radarna synkront (19→9 med grundskolan; tom 2027 dämpad). 0 konsolfel, 0 overflow desktop+375, sviterna gröna. Vision: hela läget skummbart som text grupp för grupp. |
| T5.3-fix-2 | Lägesrubrik per valläge | guide.html | ✅ Done | "Läget för din verksamhet" / "Läget — alla verksamheter" på översikten, synkron med valet — browser-verifierad i båda lägena + återställning vid Rensa val, inga konsolfel. |
| T5.4 | Läsårshjulet som förstasida, listan till undersida | guide.html, guide-alla.html, DECISIONS.md | ✅ Done | DEC-015; mockup = spec (OBS: filen heter lasarshjul-mockup.html, inte mockup-lasarshjul.html som uppgiften angav — namnavvikelse, innehållet fanns). Hjulet [data-test=lasarshjul]: 12 segment, 3 heta i läsåret 2025/26, 4 punkter alla tabbara med aria-label + Enter-stöd (browser-verifierat), centrum "4 datum / 3 kommande". Detaljkortet [data-test=hjul-detalj] byter vid punktklick (verifierat); länkrad Beslutet↗ + Fullständigt underlag→ + "Mer hos Skolverket" endast vid verifierad länk i reforms.json. Horisontcirklar [data-test=horisont-cirklar]: 25/26·4, 26/27·5, 27/28·7, 30/31·2 + på g·3 (streckad; klick → inga-skyldigheter-detalj); cirkelklick byter läsår (verifierat). Kompakt valknapp i sidhuvudet styr hjul+cirklar+detalj, persistens som tidigare; tomläge för val utan datum i läsåret (gymnasieskolan i 26/27 → 0 punkter + vägledningstext, aldrig tomt). Listan flyttad intakt till guide-alla.html (19 rader, 6 piller, data-test=oversikt/relativ-tid kvar, ?reform-deeplink fungerar; guide.html?reform= vidarebefordrar dit). 375: hjul ovanför fold (topp 293), 0 overflow. 0 konsolfel båda sidor, sviterna gröna, språkregel 0+0. Vision-jämförelse mot mockup-skärmdump utförd — konceptet troget, medvetna avvikelser: repots tokens, hela klartexten som detaljrubrik (uppgiftens fältlista), "datum" i st.f. "regler". |
| T5.5 | Hjuljusteringar efter granskning | guide.html, DECISIONS.md | ✅ Done | Alla sex besluten browser-verifierade: (1) 3 månadsknappar [data-test=manad] role=button/tabbara/aria ("September — 1 nytt datum"), 9 tomma segment inerta, punkter rena markörer (pointer-events none, aria-hidden) med månadshighlight; (2) synlig chiprad [data-test=val-synlig] mobil+desktop, 15 chips à 44px, Rensa-chip, persistens orörd; (3) [data-test=detalj-nav] 2 pilar 44px + ArrowLeft/Right + klickbara prickar + svep med riktningströskel (horisontellt bläddrar, vertikalt 200px-svep rör ingenting — touch-simulerat); (4) stabil detaljyta (456px→456px vid bläddring), utskrivna cirkeletiketter ("7 nya datum läsåret 2027/28", "3 på g ej beslutat"), på g listar samtliga 3 med namn+status+formulering och bläddras; (5) rubrik "Läsåret 2025/26 · augusti–juli", 0 terminsstart-förekomster; (6) aria-live + sr-notis kvar. 0 konsolfel båda sidor, 0px 375-overflow, sviterna gröna, språkregel 0+0. DEC-015 kompletterad (inkl. varför punkterna avklickbarades). Vision: EN interaktionsmodell bekräftad i skärmdumpar. |
| T5.6 | Hjulrevision efter desktopgranskning | guide.html, DECISIONS.md | ✅ Done | Alla fem besluten browser-verifierade: (A) kurerad väljare — 7 chips (Förskola…Komvux), mappningstabell KURERADE_VAL i kod + DEC-015 (inkl. fristående-skolor-till-alla-skolval och specialskole-/sameskole-bedömningen), ej-spec-poster visas alltid (Komvux-val → 4 datum: 1 träff + 3 ej spec), runtime-vakt för otäckta råvärden, persistens med kurerade namn; (B) punkter utan text (0 uppmätta), 6°-kollisionsseparation, månadsbadges "JULI · 2" [data-test=manad-antal], julibuggen åtgärdad — månadsklick ger månadskontex med 2 bläddringsbara juli-poster + "Visa hela läsåret" som bevarar position; (C) [data-test=layout-tvaspalt] grid 2 kolumner ≥1100px med sticky detaljkort, kärnvyn ryms på 1440p (828/654px), fasta min-höjden borta, mjuk höjdtransition i stället; (D) horisont utan innevarande läsår, etiketter "N ändringar läsåret X" + "på g ej beslutat", tillbaka-länk till innevarande läsår i hjulhuvudet; (E) rubrik "Läsårshjul". 375 staplad 0 overflow, 0 konsolfel båda sidor, sviterna gröna, språkregel 0+0. |
| T5.7 | Komplett läsårsrad med markerat innevarande | guide.html, guide-alla.html, DECISIONS.md | ✅ Done | Horisontcirklarna (enbart framtida) ersatta av komplett läsårsrad [data-test=lasarsrad]: EN cirkel per läsår inkl. innevarande (2023/24, **2025/26**, 2026/27, 2027/28, 2030/31) + på g (streckad) sist; aktiv cirkel markerad (.aktiv fylld). Klick på annan cirkel byter hjul; klick på redan aktiv cirkel = tyst no-op (hjul + rad oförändrade, verifierat byte-för-byte i DOM). Rubrik "Längre fram" → "Läsår" (0 förekomster kvar i guide.html, inkl. tomtext). Etikettform + verksamhetsfilter orörda. Headless-verifierat (Playwright/Chromium mot lokal server, 1440p+375): 15/15 checks gröna — 6 cirklar, innevarande med, en aktiv, på g streckad sist, byte fungerar, no-op bevisad, 0px 375-overflow, 0 applikationskonsolfel båda sidor (externa CDN-cert-fel = sandbox-artefakt, exkl. som i T5.4). Språkregel-grep: 0 i guide.html/guide-alla.html-UI (bonus: avlägsnade "se till att" ur ett pre-existerande JS-kodkommentar i båda filerna — inert, ingen feature rörd), guide.json oförändrad med sina 2 dokumenterade citat-undantag. nuLank-tillbakalänken behållen (del av hjulhuvudet, utanför scope) — nu delvis redundant med innevarande-cirkeln, kandidat för städning. |
| T6 | DoD-review + sprintstängning | docs/*, CLAUDE.md, guide.html | ✅ Done | Steg 0 (commit 54e94e6): T5.1-fix-raden införd i Sprint 11-tabellen + nuLank-länken borttagen (redundant med innevarande-cirkeln efter T5.7), DEC-015 T6-städningskomplettering. Steg 1 (subagent DoD): 12 punkter granskade. **Gröna**: 61 node-tester (extract 8/riksdagen 22/rss 21/rapport 10), språkregel UI 0+0, språkregel guide.json 4 träffar inom de 2 dokumenterade citatposterna, klartext/paverkan 0 förbjudna ord, källspårbarhet 0 orphans + 0 källösa, inga fabricerade Skolverket-länkar, commits matchar PS efter steg 0, T6-städning klar, DOM-kontraktet (alla data-test-attribut på rätt sida), DEC-010–015 + lasarshjul-mockup.html som spec-referens på plats, Playwright 15/15 ALLA GRÖNA. **Avvikelser hanterade i T6**: (1) Täckning — `gy25` + `ai` saknar guideposter (12/14 beslutade); dokumenterad som känd avvikelse, datapatch utanför scope. (2) CLAUDE.md saknade /goal-reglerna och git-fetch-vid-sessionsstart-lärdomen → tillagda i denna commit (141 rader, under 150-gränsen). |
| T5.8 | Aktiv punkt + månadskarusell (underhåll efter sprintstängning) | guide.html, DECISIONS.md | ✅ Done | Två granskningsbeslut (DEC-015-komplettering, 2026-06-17). (1) Aktiv punkt markerad [data-test=punkt-aktiv]: accent + r=9 (vs månadens övriga r=6) + tjock ring, synkad vid pil/svep/prick/månadsbyte. (2) Karusellen månadsavgränsad med wrap — pilar/piltangenter/svep/prickar bläddrar enbart vald månads punkter, wrap fram/bak; prickantal = månadens. Läsårsvid nav-kontext eliminerad (kontext ∈ {manad,pag}, default-månad = nästa kommande); "Visa hela läsåret"-knappen borttagen som konsekvens. Headless-verifierat (Playwright 1440p+375, ny harness test10.js): aktiv punkt distinkt (r 9 vs 6, fill rgb(29,78,216)), wrap inom JULI·2 (navNasta×2→dot0, navFore→sista), prickantal=2, månadsbyte→dot0, svep 375, tvåspalt grid orörd; 61 node-tester gröna; språkregel 0+0; 0 konsolfel båda sidor. Kurerad väljare/läsårsrad/tvåspalt/badgar/rubriker orörda. Ej deployad (master kräver ./deploy.sh). |

---

## Sprint 10 — Bevakningsautomatisering

**Mål:** Detektering av dataändringar flyttas till en schemalagd GitHub Action som
producerar en veckorapport som GitHub Issue. Människan verifierar, maskinen bevakar.
Noll automatiska skrivningar till datafiler.

**Designbeslut:**
- Runtime-manifest — ingen committad bevakningsfil; manifestet beräknas vid varje körning
- Stateless diff mot datafilerna (inga state-filer mellan körningar)
- Zero-dependency Node (inga npm-paket, node:test för tester)
- Tom vecka = ingen issue skapas
- Cron måndagar 06:00 UTC + workflow_dispatch för manuell körning

**Out of scope:** automatisk skrivning till datafiler; HTML-scraping av regeringen.se
(T9-scraping-undantaget STRUKET 2026-06-11 — det behövdes aldrig: statsliggaren
visade sig ha ett riktigt RSS-flöde hos Statskontoret, ingen sidskrapning krävdes);
bevakning av val26; notifiering utanför GitHub; AI-anrop.

**Stop condition (utökad i T7):** Action körs på schema och manuellt; korrekt rapport
mot känt testfall; tom vecka ger ingen issue; workflow-permissions contents:read +
issues:write; BEVAKNING.md följbar utan chatkontext; **täckningskartan i BEVAKNING.md
matchar deltatyperna rapport.js kan rendera (kontrolleras i T6-DoD); automationen
täcker SOU-publiceringar (T7), regeringsuppdrag (T8) och regleringsbrevet (T9) så att
manuella listan i BEVAKNING.md bara innehåller Skolverkets sidor**; DoD passerad.

**Dokumentregel (fr.o.m. T7):** varje task uppdaterar PROJECT_STATUS.md och
docs/BEVAKNING.md (täckningskarta + manuella listan) i samma commit som koden;
.claude/commands/bevakning.md endast när nya deltatyper kräver ny triage-instruktion.

| ID | Task | Filer | Status | Acceptance |
|----|------|-------|--------|------------|
| T1 | Sprintregistrering + identifierar-extraktion | PROJECT_STATUS.md, scripts/bevakning/extract.js | ✅ Done | Plan i PROJECT_STATUS; komplett manifest (12 props, 21 SOU, 49 dir, 27 utredningar), inga hårdkodade id:n, 8 tester med facit passerar |
| T1-fix | commit.sh stagear scripts/ och .github/ | commit.sh | ✅ Done | Loop över stage-listan; verifierad med dry-run |
| T2 | Riksdagen-watcher: status-diff API vs datafiler | scripts/bevakning/riksdagen.js | ✅ Done | 8 tester med mockad fetcher (omarbetade i T2-fix). |
| T2-fix | Live-verifiering + API-fältkorrigeringar | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | Live-verifiering avslöjade 3 buggar som mockarna dolde: (1) relaterade i fel fält (dokuppgift→dokreferens.behandlas_i), (2) jobb B matchade fullt dept-namn som inte finns för dir → organ-kortkod "U-dep", (3) dir-beteckning byggd fel → `Dir. <rm>:<nummer>`. Jobb C-regex \d{2}→\d{2,3}. Testerna drivs nu av fångade riktiga API-svar (scripts/bevakning/fixtures/). 20/20 gröna. Skarp körning verifierad: 12 prop-deltan med relaterade bet, 1 U-dep-direktiv (Dir. 2026:43). Se DEC-007. **OBS triage (T2 rapporterar bara, ej åtgärdat):** 8 av 12 props (2025/26:174,191–198) säger api=Klar medan reforms.json säger "proposition" — datafilen kan vara föråldrad. |
| T2-fix-3 | Signalregel jobb A: betänkandebeslut, inte dokumentstatus | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | Dokumentstatus "Klar"=publiceringsstatus, bär ingen signal. Regel 1: terminal datafil-status (beslutad) → ingen rapport, ingen fetch. Regel 2: delta endast när ≥1 kopplat betänkande fattat beslut; faktapar med statustext/beslutsdatum/rdbeslut/rskr ur bet-dokumentstatus. API-fynd: obeslutade bet HAR BES-aktivitet med status "planerat" → kriteriet är "inträffat" (fixture HD01UbU30). 16/16 tester; skarp körning = exakt 9 deltan (174, 191–198), 3 terminala skippade. Ej-funnen prop rapporteras fortfarande (anomali). |
| T2-fix-4 | Jobb B2: nya propositioner från U-dep | riksdagen.js, riksdagen.test.js, fixtures/ | ✅ Done | doktyp=prop i B-fönstret, organ-fullnamnsfilter, manifest-dedup. Delta typ "ny-proposition". 19/19 tester (fixture: 31 riktiga props, 1 U-dep). Skarp körning: Prop. 2025/26:260 (etikprövning) fångad — saknas i manifestet, triagepunkt. Fynd: friskole-propositionen efter lagrådsremissen 13 maj finns INTE i API:t ännu (bet UbU30 = placeholder, beredning planerad aug 2026). **T4-krav: rapport.js behöver sektion för typ ny-proposition.** |
| T3 | RSS-watcher: regeringen.se, Utbildningsdep., 7-dagarsfönster | scripts/bevakning/rss.js | ✅ Done | Feed-discovery verifierad (rk-main.js bygger /Filter/RssFeed?, taxonomi 2085=lagrådsremiss + 1294=U-dep, filtret biter server-side). Delta `{typ:"lagradsremiss",titel,datum,url}`; fonster_fullt_tackt-flagga; fail loud. 12 tester mot fångad riktig fixture (100 poster, djup till 2012-12-11). Live smoke OK: friskole-lagrådsremissen 2026-05-13 fångas. |
| T4 | GitHub Action: veckocron + dispatch + Issue "Bevakningsrapport v.X" | bevakning.yml, rapport.js | ✅ Done | rapport.js: sektioner A/B/B2/C/lagrådsremisser, triage-kryssrutor, Övrigt-sektion för okända typer, GITHUB_OUTPUT-kontrakt, 7/7 tester. Permissions exakt contents:read+issues:write. Live-verifierat efter deploy 2026-06-11 (workflow_dispatch registreras först när filen finns på master — dispatch från dev 404:ar innan dess): scenario 1 (maj-fönster) → issue #1 med friskole-lagrådsremissen 2026-05-13 + Dir. 2026:39; scenario 2 (jan-fönster) → grön körning, alla fönsterberoende sektioner tomma, MEN issue #2 skapades med de 9 fönsteroberoende A-deltana — äkta tom körning kräver att A-backloggen triagerats i reforms.json (by design). Test-issues stängda ("testkörning T4"). T4-fix: absUrl i alla jobb + actions v5/v6 (Node 24-deprecation före cron 22 juni). **Cronen är LIVE på master (deploy 2026-06-11, inkl. T4-fix) — första schemalagda körning måndag 15 juni 06:00 UTC.** |
| T5 | Bevakningsrutin som kommando (reviderad) | docs/BEVAKNING.md, .claude/commands/bevakning.md | ✅ Done | BEVAKNING.md omskriven: arkitektur (Action/skript/människa, jobb A-backlog-caveat), verifieringsregler i full form, triage-klassning (åtgärda/ignorera/eskalera, Prop. 260-exemplet), felsökning med fixture-förnyelse som första steg; manuella listan behållen för det automationen inte täcker (Skolverket, RB, SOU-publicering). /bevakning-kommandot kodifierar 6-stegsrutinen (gh-hämtning → källverifiering → klassning → datapatch → diff-godkännande FÖRE commit → issue-kommentar+stängning); hårda regler: overifierbart=eskalera, BEVAKNING.md är regelkällan (ingen duplicering). End-to-end-verifierad 2026-06-11 mot issue #3 (Bevakningsrapport v.24): 9 åtgärda + 1 ignorera + 1 noterat feed-fel, diff godkänd före commit, issue kommenterat och stängt. A-backloggen tömd — nästa veckorapport ska sakna A-sektion. |
| T7 | Jobb B3: SOU-publiceringar | riksdagen.js, rapport.js, fixtures/ | ✅ Done | **Empiri: SOU bär INGET departement i riksdagens data** (organ tom i list, departement+dokuppgift saknas i detalj — verifierat mot HDB39) → ingen dep-filtrering möjlig; alla okända SOU rapporteras (~0–3/vecka) med "Betänkande av..."-ledtråd ur summary. sou-levererad vid betankanden[].nr-match (faktapar med utrednings-id), annars ny-sou. 22/22 + 8/8 tester; skarp körning 2025-01-25→02-05: SOU 2025:9 → sou-levererad via utr-grundlaggande-svenska (facit) + SOU 2025:8 via utr-studiero; 3 ny-sou. Fönster-fetcharna konsoliderade till fetchDokumentWindow. |
| T8 | Uppdrag-RSS: regeringsuppdrag + multi-feed-refactor | rss.js, rapport.js, fixtures/ | ✅ Done | Feed-discovery (T3-metoden): Regeringsuppdrag=taxonomi 1342 + U-dep 1294, filtret biter server-side (100/100 items bär domain=1294), djup till maj 2019. rss.js refactorerad till multi-feed: FEEDS-konfig {namn, deltatyp, url} driver samma parser/fönster/täckningsflagga per feed; rapportform { floden[], deltan } — T3-testerna beteendeoförändrade via feeds-injektion. Delta typ "regeringsuppdrag" (ingen dedup behövs, 7d-fönster). 15/15 + 8/8 tester; skarp körning 2025-12-20→31: tioårig grundskola-uppdraget (2025-12-22) fångat exakt. Bonus-observation: ändringsbeslut flödar genom samma feed (Ändring av uppdraget... 2026-04-28 sedd i flödet). |
| T9 | Regleringsbrev via statsliggarens RSS | rss.js, rapport.js, fixtures/ | ✅ Done | Statsliggaren ESV→Statskontoret verifierad (kanonisk domän statskontoret.se; "esv--" i sökvägen är legacy). Itemstruktur: media:keywords="Myndighet,Departement,År" (filtrering), beslutsdatum i titeln (delta-datum — inte pubDate), rbid-länk. Tvåstegsfilter: U-dep + REGLERINGSBREV_MYNDIGHETER-konfig (5 skolmyndigheter; lärosätena = ~50 brev/december, fast scopegräns). Ändringsbeslut särskiljs i titeln → ingen egen typ. parseFeed fick extraTaggar; FEEDS fick transform-hook. 19/19 + 9/9 tester. **Flödesdjup bara ~3 mån (äldsta 2026-03-16)** → dec-facit (Skolverkets RB 2026) onåbart retroaktivt; skarp körning fångade i stället Skolverkets BÅDA vårändringsbeslut (2026-04-28, 2026-05-25) exakt. Scraping-undantaget struket — behövdes aldrig. |
| T6 | Run DoD review for this sprint (sist) | (dod-reviewer) | ⬜ Todo | Sprint godkänd; kontrollerar även att täckningskartan i BEVAKNING.md matchar deltatyperna rapport.js renderar |

**Testkommando:** `node --test scripts/bevakning/extract.test.js`,
`node --test scripts/bevakning/riksdagen.test.js` och
`node --test scripts/bevakning/rss.test.js` (kör filerna var för sig — inte
katalogformen `node --test scripts/bevakning/`, den snubblar på CLI-stdout).
CLI: `node scripts/bevakning/extract.js [dataDir]` skriver manifest som JSON till stdout;
`node scripts/bevakning/riksdagen.js --from YYYY-MM-DD --tom YYYY-MM-DD` kör skarp watcher;
`node scripts/bevakning/rss.js --from YYYY-MM-DD --tom YYYY-MM-DD` kör RSS-watchern skarpt.
riksdagen.test.js och rss.test.js använder fångade riktiga svar i `scripts/bevakning/fixtures/`.

---

## Completed: Sprint 9 — Utredningar på tidslinjen

DoD-granskad och GODKÄND (T5, 2026-06-10). T2-followup levererad samma dag — alla 27 icke-aviserade utredningar renderas nu.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 9.T2 | Bakåtförlängd axel (2021) + utredningsstaplar | ✅ Done | Modell A — gemensam axel. Efter T2-followup: 27/27 utredningar renderas. |
| 9.T3 | Bidirektionell navigering utredning↔reform | ✅ Done | Lookup utrByReform vid render. Reformdetaljvy med Utredningar-sektion (visas bara vid kopplingar); utredningsvyn länkar tillbaka. reforms.json oförändrad. |
| 9.T4 | Kopplingslinjer vid hover/markering | ✅ Done | SVG-overlay i gantt-body. Bezierlinje från utredningens slut till reformens start. Hover visar tillfälligt, klick pin:ar. Ingen full re-render vid hover. |
| 9.T5 | DoD-granskning + sprintstängning | ✅ Done | Alla T1–T4 maskinella kriterier uppfyllda. |
| 9.T2-followup | Datumkomplettering 6 utredningar | ✅ Done | utr-fler-vagar, utr-komvux, utr-heder, utr-grundlaggande-svenska, utr-undervisningstid, utr-lararutbildning — primärkällsverifierade datum. 0 skips. |

---

## Completed: Sprint 1 – Grundfunktion live

9/10 uppgifter klara. Kvar: 1.2 DNS (väntar propagering), 1.10 dela med kollegor.

---

## Completed: Sprint 2 – Innehåll, struktur och kopplingar

**Mål:** Separera data från gränssnitt, förbättra layout, verifiera innehåll.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Skolverkets uppdragsstatus per reform | ✅ Done | Data från RB 2025/2026, indikator + modal |
| 2.2 | Responsiv kartyta på desktop | ✅ Done | Full bredd, noder omplacerade med min 15% avstånd |
| 2.3 | dev/master-branching + deploy.sh | ✅ Done | commit.sh → dev, deploy.sh mergar till master |
| 2.4 | Separera data till JSON-filer | ✅ Done | data/reforms.json, connections.json, uppdrag.json — fetch() vid laddning |
| 2.5 | Granska alla 15 kopplingar | ⬜ Todo | Saknas/fel? |
| 2.6 | Verifiera rollfilter | ⬜ Todo | Stämmer rollerna per reform? |
| 2.7 | Uppdatera efter riksdagsbeslut | ⬜ Todo | Bevaka vårens voteringar |
| 2.8 | Komplettera ändrade timplaner | ⬜ Todo | Prop. 2023/24:20 |
| 2.9 | Verifiera budgetsiffra 95 Mkr studiero | ⬜ Todo | Källa: budgetprop, inte Prop. 193 |
| 2.10 | Feedback-runda #2 | ⬜ Todo | Bredare grupp |

---

## Completed: Sprint 3 – Målbild och infrastrukturberoenden

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | data/malbild.json med pelardefinitioner och kopplingar | ✅ Done | 6 pelare, 16 reformer, motiveringstext per koppling |
| 3.2 | malbild.html med chips, pelare, SVG-linjer, sidebar | ✅ Done | Samma designspråk som reformkartan |
| 3.3 | Fliknavigation mellan reformkarta och målbild | ✅ Done | Header-navigation i index.html och malbild.html |
| 3.4 | Klickbara kopplingar med bezier-kurvor | ✅ Done | Sorterade ankarpunkter, minimala korsningar |
| 3.5 | Sidebar med detaljer vid klick | ✅ Done | Reform- och pelardetaljer med motiveringstext |
| 3.6 | Sammanhållen visiontext | ✅ Done | Fällbar, första meningen synlig |
| 3.7 | Statistikrad | ✅ Done | Antal reformer med beroenden, pelare, totala kopplingar |
| 3.8 | Responsiv | ✅ Done | Mobilanpassad |
| 3.9 | Uppdatera infrastrukturberoenden | ✅ Done | Strategisk analys: betyg, läroplaner, tid, studiero |

---

## Completed: Sprint 5 – Listvy och uppdragsöversikt

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | Fliknavigation (Reformkarta/Reformer/Uppdrag) | ✅ Done | Målbild dold från nav, nås via direkt URL |
| 5.2 | Reformtabell (reformer.html) | ✅ Done | Sorterings- och filterbar, sidebar med detaljer |
| 5.3 | Filter: kategori, status, uppdragsstatus | ✅ Done | |
| 5.4 | Uppdragsöversikt (uppdrag.html) | ✅ Done | Individuella uppdrag, inkl. relaterade |
| 5.5 | Tidsgruppering per kvartal/år | ✅ Done | Q2–Q4 2026, 2027, 2028+ |
| 5.6 | Snart-markering (30 dagar) | ✅ Done | Orange kant + badge |
| 5.7 | Uppdragstitlar från regleringsbrevet | ✅ Done | Formella namn, visas som rubrik |
| 5.8 | Tvåvägslänkning reformer↔uppdrag | ✅ Done | Deeplinks med URL-parametrar |
| 5.9 | Responsiv | ✅ Done | Mobilanpassad med sidebar-overlay |

---

## Completed: Sprint 6 – Tidslinje

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.1 | data/tidslinje.json (30 händelser) | ✅ Done | Ikraftträdanden, redovisningar, milstolpar, riksdagsbeslut |
| 6.2 | Expanderbar Gantt-layout | ✅ Done | Reformbars med chevron expand/collapse |
| 6.3 | Händelsemarkörer på bars | ✅ Done | Diamant, cirklar, fyrkant — 10px med vit border |
| 6.4 | Filter (dämpar, döljer inte) | ✅ Done | Typ + kategori |
| 6.5 | Hoppa-till-knappar | ✅ Done | Ersätter minikarta |
| 6.6 | Klickbar sidebar (händelser + uppdrag) | ✅ Done | Deeplinks till reformer/uppdrag |
| 6.7 | Responsiv + mobil touch-targets | ✅ Done | 44px touch-areas, sidebar overlay |

---

## What's Working Now
Reformkartan finns som `index.html` i roten. GitHub Pages serverar sidan.
- 16 reformnoder med kategorifärgad bakgrund, uppdragsstatus-chip, drag-and-drop
- Kopplingslinjer bakom kort (2px, 0.5 opacity), aktiva linjer framhävda
- Multi-select filter (område, tid, roll) — checkbox-logik, inga valda = visa alla
- Klick på tom yta återställer vald reform
- Mobil portrait: listvy med accordion-kort; landscape: kartvy med zoom/pan
- **Målbildsvy** (malbild.html): 6 infrastrukturpelare, 16 reformer med beroendekopplingar, SVG-bezierlinjer, sidebar med motiveringstext, statistikrad, responsiv (dold från navigation, nås via direkt URL)
- **Reformtabell** (reformer.html): sorterings- och filterbar tabell, sidebar med detaljer, deeplinks till uppdragsvy
- **Uppdragsöversikt** (uppdrag.html): individuella uppdrag grupperade per tidsperiod, snart-markering, sidebar med fulltext, deeplinks till reformtabell
- **Tidslinje** (tidslinje.html): expanderbar Gantt med reformbars, uppdragsbars, händelsemarkörer, tooltips, klickbar sidebar, hoppa-knappar
- Fliknavigation: Reformkarta / Reformer / Uppdrag / Tidslinje
- Cloudflare Web Analytics på alla sidor

```bash
# Öppna lokalt:
open index.html
# Live: https://niklasleide.github.io/leides-ljuvliga-lilla-reformkarta/
# Planerad: https://reformer.leide.se
```

---

## Blockers
- DNS-propagering för reformer.leide.se (sprint 1.10 beror på detta)

---

## Osäkert — kontrollera vid tillfälle
- Budgetsiffran 95 Mkr för trygghet/studiero — hämtad från budgetproposition, inte Prop. 193
- Ändrade timplaner (Prop. 2023/24:20) — begränsade detaljer
- Uppdragsfulltext för betyg och standardiserade tester refererar till RB 2025 som inte laddats ner — nuvarande text baserad på Skolverkets sidor och pressmeddelanden

---
> Update this at the **end** of each Claude Code session, not the beginning.
> Move completed tasks to ✅ Done. Keep Blockers current.
