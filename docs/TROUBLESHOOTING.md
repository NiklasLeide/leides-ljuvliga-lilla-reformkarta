# Troubleshooting — leides-ljuvliga-lilla-reformkarta

Known issues and solutions. Check here before debugging. Add here when you fix something.

---

## Format
```
### Issue title
**Symptom:** What you observed
**Cause:** Why it happened
**Solution:** What fixed it
```

---

## WSL2 / Environment

### WSL2: permission errors on /mnt/c/
**Symptom:** Permission errors running scripts or tools on files under `/mnt/c/`.
**Cause:** Windows filesystem mounted at `/mnt/c/` doesn't support Linux permissions.
**Solution:** Keep the project on the native WSL filesystem (`~/projects/`). Only use `/mnt/c/` for dropping files from Windows.

### git init fails or behaves unexpectedly
**Symptom:** `git init` or git operations fail on `/mnt/c/`.
**Cause:** Same filesystem permission issue as above.
**Solution:** Keep the git repo on native WSL: `~/projects/leides-ljuvliga-lilla-reformkarta`.

### Python venv fails
**Symptom:** `python -m venv` fails or venv doesn't work.
**Cause:** Symlinks and permissions broken on mounted Windows filesystem.
**Solution:** Create venv on native WSL: `python3 -m venv ~/venv-leides-ljuvliga-lilla-reformkarta`

---

## Claude Code

### Claude Code auto-update fails on startup
**Symptom:** Warning on startup that Claude Code failed to auto-update.
**Cause:** Global npm packages need sudo; auto-updater doesn't use it.
**Solution:** `sudo npm install -g @anthropic-ai/claude-code`
Not critical — Claude Code still works, it's just a warning.

### Claude Code forgets to update PROJECT_STATUS.md
**Symptom:** Tasks get done but PROJECT_STATUS.md stays stale.
**Cause:** Prompt-based rules in CLAUDE.md get missed when Claude is focused on code.
**Solution:** Don't rely on prompts — enforce with tooling. Use a `commit.sh` script
or git hooks that check documentation is updated before pushing.
**General principle:** If something needs to happen every time, automate it. Never rely on Claude remembering.

---

## Git / GitHub

### npm global install needs sudo
**Symptom:** `npm install -g` fails with permission errors.
**Solution:** `sudo npm install -g <package>`

---
## Bevakning (scripts/bevakning/)

### Mockar mot ANTAGNA API-format gav 8/8 grönt medan jobb B var dött
**Symptom:** Riksdagen-watchern (T2) hade 8 gröna enhetstester men jobb B (nya
Utbildningsdep.-direktiv) hittade aldrig något mot live API. Jobb A:s `relaterade`
var alltid tom, och rapporterade dir-beteckningar var oanvändbara ("7" utan årtal).
**Cause:** Testmockarna fabricerade svarsformer ur antaganden istället för riktiga
svar. De antog: dir-`departement` = fullt namn (i verkligheten `undefined`; bara
`organ`-kortkod "U-dep" finns, även i detalj-svaret), dir-`beteckning` = "Dir.
2099:100" (i verkligheten bart löpnummer "100" + årtal i `rm`), relaterade bet/rskr
i `dokuppgift.uppgift` (i verkligheten i `dokreferens.referens` med referenstyp
`behandlas_i`). Mockarna validerade koden mot sina egna fel → grönt på dött jobb.
**Solution:** T2-fix (2026-06-10): spara skarpa API-svar som fixtures i
`scripts/bevakning/fixtures/` och driv testerna från dem. Lärdom inbakad i
kodkommentarer (riksdagen.js "VERIFIERAT MOT LIVE API"). **Princip:** mocka aldrig
ett externt format du inte har sett — fånga ett riktigt svar och frys det som fixture.

### Riksdagens API: fältformer som lätt antas fel
**Symptom:** Felaktiga slutsatser om data.riksdagen.se-svaren.
**Cause/fakta (verifierat 2026-06-10):**
- Prop-list: `beteckning` = bart löpnummer ("20"), årtal i `rm` ("2023/24"); `organ`
  = fullt departementsnamn; `dokument.departement` saknas.
- Dir-list: `beteckning`/`nummer` = bart löpnummer; `organ` = KORTKOD ("U-dep",
  "Ju-dep", "UD-dep"=Utrikes); `dokument.departement` saknas även i detalj-svaret.
- Relaterade bet/rskr: `dokumentstatus.dokreferens.referens`, referenstyp `behandlas_i`.
- `dokument_url_html` kan vara protokoll-relativ ("//data.riksdagen.se/..."). Måste
  prefixas med `https:` innan den används som klickbar länk (T4-rapporten).
**Solution:** Se fixtures + DEC-007. Bygg full beteckning via `dirBetFromEntry`.

---
## Build / Deploy

### commit.sh kräver manuell git add för rotfiler
**Symptom:** `./commit.sh` säger "no changes added to commit" trots att filer ändrats.
**Cause:** Skriptet kör `git add docs/ src/ .claude/` och `git add *.json *.ts *.js *.sh *.md` — men glob-mönster i bash matchar bara redan stagade eller trackade filer om de inte redan finns i index. Ibland behöver filer stagas manuellt först.
**Solution:** Kör `git add <fil>` innan `./commit.sh "msg"`.

### commit.sh stagear inte allt vid saknad katalog i listan
**Symptom:** `./commit.sh` rapporterar inte allt staged trots att flera kataloger ändrats. Tidigare: `data/` och allt efter `src/` (som inte finns i repot) ignorerades tyst pga `|| true`-suppression.
**Cause:** `git add docs/ src/ .claude/ data/ ...` aborterar HELA kommandot vid första saknade pathspec — efterföljande kataloger nås aldrig.
**Solution:** Sprint 10 T1-fix: stage-listan kör nu en loop som hoppar över saknade kataloger individuellt (`for d in ...; do [ -d "$d" ] || continue; git add "$d"; done`). Verifierat med dry-run att `scripts/` och `.github/` fångas.

### CSS media query ordning: generella regler skriver över media queries
**Symptom:** Mobil listvy (`display: block` i portrait media query) syntes inte.
**Cause:** `.list-view { display: none; }` definierades *efter* portrait-mediaqueryns `.list-view { display: block }`. Samma specificitet → sista regeln vinner.
**Solution:** Flytta generella `display: none`-regler till *före* alla media queries. Media queries som sätter `display: block` måste komma efteråt för att få företräde.

### Touch swipe-to-close triggas av scroll i panel
**Symptom:** Sidopanelen stängs när man scrollar uppåt i den och når toppen.
**Cause:** Swipe-hanteraren kollade `dy > 60` (vertikalt) utöver `dx > 60` (horisontellt). Scroll som nådde toppen registrerades som vertikal svep.
**Solution:** Stäng bara vid horisontell svep: `dx > 60 && Math.abs(dx) > Math.abs(dy) * 2`.

### Zoom/pan hoppar vid start på touch
**Symptom:** Kartan hoppar till en annan position när man börjar zooma eller panorera.
**Cause:** Första fingret startade pan, sedan landade andra fingret (pinch) med en offset. Pan-state överfördes inte korrekt till pinch.
**Solution:** Dead zone (5px) innan pan startar. Vid pinch: nollställ pan-state med pinch-mittpunkt. Vid finger-release från 2→1: starta inte ny pan.

---
## CSS / Layout

### overflow-x:auto tvingar overflow-y:auto (CSS-spec)
**Symptom:** Gantt-tidslinjen klippte vertikalt — rader försvann och gick inte att scrolla till.
**Cause:** CSS-specen säger att om en overflow-axel sätts till något annat än `visible`, sätts den andra axeln automatiskt till `auto`. Så `overflow-x:auto; overflow-y:visible` renderar som `overflow-x:auto; overflow-y:auto` — en scroll-container som fångar vertikal scroll.
**Solution:** Ta bort all overflow från scroll-containern. Låt sidans body hantera all scroll (vertikal + horisontell). Bröt tidslinjen tre gånger innan orsaken hittades.

### height:100% på flex-child med absolut-positionerade barn → 0px
**Symptom:** Gantt-bars och markörer osynliga trots korrekt HTML.
**Cause:** `.gantt-row-chart { height: 100% }` i en flex-container med `align-items: center` resolvar till 0px. Absolut-positionerade barn (bars, markörer med `top:50%`) renderas utanför synligt område.
**Solution:** Använd alltid explicit pixelhöjd (t.ex. `height: 30px`) på element som har absolut-positionerade barn.

### innerHTML-byte förstör DOM-element som andra funktioner förväntar sig
**Symptom:** `clearDetail()` kraschade tyst — mobile sidebar stängdes aldrig.
**Cause:** `selectEvent()` bytte ut `detailPanel.innerHTML` helt. `clearDetail()` kallade `renderDefaultSidebar()` som letade efter `#detailDefault` — ett element som inte längre fanns i DOM.
**Solution:** Återskapa elementet innan: `detailPanel.innerHTML='<div id="detailDefault"></div>'` före `renderDefaultSidebar()`.

---
