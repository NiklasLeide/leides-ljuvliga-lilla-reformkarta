# Bevakning — reformer.leide.se

Detta dokument är källan för hur bevakningen fungerar och vilka regler som
gäller vid triage. `/bevakning`-kommandot (.claude/commands/bevakning.md)
följer rutinen härifrån — reglerna definieras HÄR och dupliceras inte.

---

## Arkitektur — vad körs var

**GitHub Action** (`.github/workflows/bevakning.yml`)
- Cron måndagar 06:00 UTC — körs bara på master, så ändringar i workflowet/
  skripten aktiveras först efter deploy. `workflow_dispatch` kan köras
  manuellt från Actions-UI:t med valfritt `from`/`tom`-fönster (backdaterade
  testkörningar). OBS: dispatch fungerar först när filen finns på master.
- Permissions: exakt `contents: read` + `issues: write`.
- Finns deltan → issue **"Bevakningsrapport v.\<ISO-vecka\> \<år\>"** med label
  `bevakning`. Tom körning → grönt jobb, ingen issue. Skriptfel → rött jobb,
  ingen issue (fail loud — en saknad rapport ska synas, aldrig se ut som en
  tom vecka).

**Skripten** (`scripts/bevakning/`, zero-dependency Node 20, CJS)
- `extract.js` — runtime-manifest ur datafilerna (props/SOU/dir/utredningar).
  Ingen committad bevakningslista; manifestet beräknas vid varje körning.
- `riksdagen.js` — fem jobb mot data.riksdagen.se:
  **A** prop-status (betänkandebeslut för icke-terminala manifest-props),
  **B** nya U-dep-direktiv i fönstret, **B2** nya U-dep-propositioner i
  fönstret, **B3** SOU-publiceringar i fönstret (spårade → sou-levererad,
  okända → ny-sou), **C** tilläggsdir till spårade utredningar (alla
  departement). Kända API-beteenden (publiceringsstatus "Klar" utan
  signalvärde, BES-aktivitet "planerat" vs "inträffat", organ-kortkoder,
  SOU helt utan departementsdata → ny-sou listar alla departement)
  dokumenteras i filens huvudkommentar — läs den innan du ändrar något.
- `rss.js` — lagrådsremisser via regeringen.se:s RSS (U-dep-filtrerad feed;
  riksdagens API täcker inte lagrådsremisser). Flaggar när fönstret sträcker
  sig bakom flödets äldsta post.
- `rapport.js` — bygger issue-bodyn ur de två rapporterna. Okända delta-typer
  hamnar i "Övrigt", aldrig tyst tappade.
- Tester: `node --test scripts/bevakning/<fil>.test.js` (en fil i taget).
  Testerna drivs av RIKTIGA fångade API-/feedsvar i `fixtures/`.

**Människan** (du + `/bevakning`)
- All triage är manuell. Automationen skriver ALDRIG i datafiler — den
  rapporterar bara. Varje delta i issuet har en kryssruta som bockas när
  punkten är hanterad.

**Viktigt om jobb A:** A diffar API mot datafil oavsett datumfönster — samma
deltan återkommer varje vecka tills reforms.json är uppdaterad. En "tom
vecka" (ingen issue) kräver alltså både tomt fönster OCH triagerad A-backlog.

---

## Täckningskarta — vad bevakas automatiskt

Denna tabell ska matcha deltatyperna i rapport.js SEKTIONER exakt —
kontrolleras vid sprintens DoD. Lägger du till ett jobb: uppdatera tabellen,
rapport.js och (vid behov) /bevakning-kommandots triage-instruktioner i
samma commit.

| Deltatyp | Jobb | Källa | Täckning |
|---|---|---|---|
| `prop-status` | A | data.riksdagen.se | Betänkandebeslut för manifest-props (fönsteroberoende) |
| `nytt-direktiv` | B | data.riksdagen.se | Nya U-dep-direktiv i fönstret |
| `ny-proposition` | B2 | data.riksdagen.se | Nya U-dep-props i fönstret, ej i manifestet |
| `sou-levererad` | B3 | data.riksdagen.se | SOU i fönstret som matchar spårat betankanden[].nr |
| `ny-sou` | B3 | data.riksdagen.se | Okända SOU i fönstret — ALLA departement (SOU saknar departementsdata) |
| `tillaggsdir-till-tracked-utredning` | C | data.riksdagen.se | Tilläggsdir till spårade utredningar, alla departement |
| `lagradsremiss` | rss.js | regeringen.se RSS | Nya U-dep-lagrådsremisser i fönstret |

---

## Verifieringsregler (fullständig form)

Gäller varje ändring i datafilerna, oavsett om den görs via `/bevakning`
eller för hand:

1. **Officiella namn och formuleringar** ur originaldokumenten — aldrig
   egenpåhittad eller "förbättrad" terminologi. Propositionens titel är den
   som står på regeringen.se/riksdagen.se, inte en omskrivning.
2. **Beslutsdatum, inte publiceringsdatum.** Datum i datafilerna avser när
   beslutet fattades (regeringssammanträde för prop/dir/lagrådsremiss,
   kammarbeslut för riksdagsbeslut) — inte när dokumentet lades ut på webben.
   I bevakningsrapporten är "beslut YYYY-MM-DD" kammarbeslutsdatumet.
3. **Allt overifierbart droppas eller nullas — aldrig uppskattas.** Saknas
   ett datum i primärkällan lämnas fältet null; vi fabricerar inte "troliga"
   värden. Hellre ett hål i kartan än en gissning.
4. **Varje faktauppgift spårbar till primärkälla**: regeringen.se,
   riksdagen.se, sou.gov.se. Nyhetsartiklar, pressmeddelanden och Skolverkets
   sammanfattningar kan peka mot källan men ÄR inte källan.

---

## Triage-klassning

Varje delta i rapporten klassas som ett av tre:

- **Åtgärda** — primärkällan bekräftar en ändring som datafilerna ska
  spegla. Exempel: kammarbeslut fattat → reforms.json-status uppdateras
  (+ ev. tidslinjehändelse).
- **Ignorera (med motivering)** — deltat är korrekt rapporterat men ska
  inte in i kartan. Bocka av kryssrutan och skriv motiveringen i
  issue-kommentaren. **Exempel: Prop. 2025/26:260 (etikprövning av
  forskning)** — U-dep, men utanför kartans skolscope → ignorera med
  motivering. INGEN kodfiltrering för sådana fall: watchern ska visa hela
  U-dep-bredden, scope-bedömningen är människans.
- **Eskalera** — allt som inte kan verifieras direkt ur den länkade
  primärkällan går till research-flödet (se RESEARCH_AGENT.md), inte till
  gissning. Exempel: ett delta antyder följdändringar i en annan reform,
  eller källsidan motsäger rapporten.

---

## Felsökning

**Första steg vid konstiga resultat: förnya fixtures.** Skripten är byggda
mot fångade API-svar; när API:t/feeden ändrar format ljuger gamla mockar
(lärdom från T2-fix: 8/8 gröna tester medan ett jobb var dött live).
Rutin: hämta om motsvarande svar (URL:erna står i respektive fixtures
ursprungskommentar/test), diffa mot gammal fixture, kör testsviten — faller
den har formatet ändrats och koden ska anpassas, inte testerna luckras upp.

- **Rött workflow** → läs job-loggen; skriptens FEL-rader går till stderr
  med exit 1. Ingen issue skapas vid fel — det är avsiktligt.
- **Ingen issue på måndag** → kolla om körningen var grön och tom (job-
  loggen visar "Inga deltan i fönstret") innan du misstänker fel. Kom ihåg
  jobb A-backloggen (se ovan) — med otriagerade A-deltan kommer issue varje
  vecka.
- **RSS-varningen "fönster ej fullt täckt"** → flödet innehåller bara
  senaste ~100 poster; en tom lagrådsremiss-sektion med den varningen är
  inte ett bevis på en tom period.
- **workflow_dispatch 404** → filen finns inte på master ännu (deploya).
- **Feed-URL:en slutar svara** → discovery-metoden står i rss.js
  huvudkommentar (filter-UI:ts data-attribut → /Filter/RssFeed-parametrar).

---

## Manuell bevakning — täcks INTE av automationen

Automationen täcker riksdagsdokument (prop/dir/bet/SOU) och lagrådsremisser
— se Täckningskartan. Följande källor kräver fortfarande manuell koll
(månadsvis, eller veckovis under voteringsperioden april–juni):

### Skolverket
- [ ] Aktuella regeländringar: https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/aktuella-regelandringar
- [ ] Pågående regeringsuppdrag: https://www.skolverket.se/om-oss/var-verksamhet/regeringsuppdrag-och-remisser/pagaende-regeringsuppdrag
- [ ] Nya läroplaner: https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/tioarig-grundskola-och-nya-laroplaner/sa-har-arbetar-skolverket-med-nya-laroplaner-och-tioarig-grundskola (kursplaneremiss okt–dec 2026)
- [ ] Betygssystem 1–10: https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/forberedelser-for-inforande-av-nytt-betygssystem
- [ ] Tioårig grundskola: https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/tioarig-grundskola-och-nya-laroplaner (fortbildning VT 2027)
- [ ] Gy25 (i drift, övergång t.o.m. 2030): https://www.skolverket.se/styrning-och-ansvar/forandringar-inom-skolomradet/gy25----amnesbetyg-pa-gymnasial-niva
- [ ] Professionsprogrammet (i drift): https://www.skolverket.se/skolutveckling/professionsutveckling/professionsprogrammet

### Regeringen (politik/uppdrag — ej rättsliga dokument)
- [ ] Skolprioriteringen: https://www.regeringen.se/regeringens-politik/regeringens-prioriteringar/skola/
- [ ] Nya regeringsuppdrag: https://www.regeringen.se/regeringsuppdrag/ (filtrera Utbildningsdepartementet)

### Regleringsbrev
- [ ] RB 2026: https://www.statskontoret.se/regleringsbrev/25940/pdf?Version=HelaBrevet

### Övrigt
- [ ] EU:s AI-förordning — bevaka om Skolverket får uppdrag (inget uppdrag ännu)
- [ ] Ändrade timplaner (Prop. 2023/24:20) — källa för detaljer saknas fortfarande
