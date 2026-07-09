# leides-ljuvliga-lilla-reformkarta

En reformkarta över de senaste skolreformerna

**Stack:** Vanilla HTML/CSS/JS, inga ramverk, inga byggsteg. Varje vy är en self-contained .html-fil. Data i JSON (data/). Hostad via GitHub Pages. Cloudflare Web Analytics.
**Started:** 2026-03-23
**GitHub:** github.com/niklasleide/leides-ljuvliga-lilla-reformkarta

## Session Start — ALWAYS do this first
1. Read `@docs/PROJECT_STATUS.md` — understand current state
2. Read `@docs/DECISIONS.md` — don't propose changes that contradict past decisions
3. Check `@docs/TROUBLESHOOTING.md` before proposing solutions to errors

These files ARE Claude's memory between sessions. Keep them accurate.

## Commands
```bash
# Öppna lokalt (ingen server behövs — bara statiska filer):
open index.html             # eller öppna i webbläsare
# Live: https://reformer.leide.se
# Dev-preview: https://reformer.leide.se/dev/

./commit.sh "message"       # ALWAYS use this to commit — never bare git commit
# commit.sh: stages docs/, data/, *.html, *.json, *.sh etc, pushes to dev,
# syncs ALL .html + data/ to master:dev/ for preview

# Deploy till produktion (interaktiv — bara Niklas kör):
./deploy.sh                 # mergar dev → master, kräver bekräftelse
# Alternativt manuellt:
# git checkout master && git merge dev --no-edit && git push origin master && git checkout dev

# Det finns inga byggsystem, tester eller type-checks.
# Verifiering sker manuellt i webbläsaren.
```

## Architecture
See `@docs/DECISIONS.md` for all architectural decisions and reasoning.
**Do not make architectural choices without consulting this file first.**

## Directory Structure
```
leides-ljuvliga-lilla-reformkarta/
├── CLAUDE.md              ← you are here (keep under 150 lines)
├── index.html             ← reformkarta (noder + kopplingar, drag-and-drop)
├── reformer.html          ← reformtabell (sorterings/filterbar, sidebar)
├── uppdrag.html           ← uppdragsöversikt (tidsgrupperad, deeplinks)
├── tidslinje.html         ← Gantt-tidslinje (expanderbara reformbars)
├── utredningar.html       ← utredningslistvy (filter, sök, expanderbara kort)
├── guide.html             ← huvudmannaguide (läsårshjul); guide-alla.html = fullista
├── andringar.html         ← senaste ändringar (bevakningen synlig; data/andringar.json)
├── assets/og-image.png    ← delningsbild (Open Graph, 1200×630)
├── data/
│   ├── reforms.json       ← reformdata (namn, status, kategorier, länkar)
│   ├── connections.json   ← kopplingar mellan reformer
│   ├── uppdrag.json       ← Skolverkets uppdragsstatus per reform (med titel)
│   ├── utredningar.json   ← utredningar (direktiv, betänkanden, prop-koppling)
│   ├── guide.json         ← huvudmannaguidens per-reform-lager
│   ├── andringar.json     ← ändringslogg (datum, text, reform_ids, kalla)
│   ├── meta.json          ← { senast_uppdaterad } — driver färskhetsstämpeln
│   └── tidslinje.json     ← 30 händelser (ikraftträdanden, redovisningar, milstolpar)
├── _config.yml            ← Jekyll: exkluderar docs/mockups ur Pages-bygget
├── commit.sh              ← commit + push till dev + synka dev-preview
├── deploy.sh              ← merga dev → master (interaktiv)
├── docs/
│   ├── DECISIONS.md       ← decision log — WHY choices were made
│   ├── PROJECT_STATUS.md  ← sprint tasks, blockers, what's working
│   ├── TROUBLESHOOTING.md ← known issues grouped by category
│   ├── CHANGELOG.md       ← what changed and when
│   ├── ROADMAP.md         ← sprints and feature backlog
│   └── BEVAKNING.md       ← URL:er att bevaka per reform
└── .claude/commands/      ← custom slash commands
```

## Commit Rule (non-negotiable)
**Always use `./commit.sh "message"` — never bare `git commit`.**
Använd commit.sh för att committa och pusha — det går alltid till dev.
**Använd ALDRIG git push till master direkt.**
Dev-versionen testas på reformer.leide.se/dev/ — commit.sh synkar dit automatiskt.
Deploy till produktion görs av Niklas via `./deploy.sh`.

The script auto-stages docs/, src/, config files and blocks commits if CHANGELOG.md
isn't updated when src/ changed. It refuses to run on master.

Before every commit, update:
- `docs/CHANGELOG.md` — always, for every code change
- `docs/PROJECT_STATUS.md` — if any task changed state
- `docs/DECISIONS.md` — if an architectural decision was made
- `docs/TROUBLESHOOTING.md` — if a bug was hit and fixed

## Coding Conventions
- Prefer simple and readable over clever
- Add comments for non-obvious logic — future sessions have no memory
- All errors logged, never silently swallowed
- Environment variables via `.env` (never committed — use `.env.example`)
- When a pattern exists in the codebase, follow it; ask before deviating

## Design System
CSS-variabler i :root i varje HTML-fil (inget delat stylesheet). Kopiera exakt vid nya sidor:
- Färger: --kunskap (#1d4ed8), --trygghet (#b91c1c), --larare (#15803d), --styrning (#6d28d9)
- Bakgrund: --bg (#f7f6f3), --card (#fff), --border (#e5e2dc)
- Typsnitt: DM Sans (body), Source Serif 4 (rubriker)
- Fliknavigation: Reformkarta / Reformer / Uppdrag / Tidslinje (Målbild dold)
- Cloudflare Web Analytics-snippet före </body> i alla sidor

## Claude's Role
You are a **critical friend**, not a yes-machine.

- Challenge architectural decisions before implementing — ask "is there a simpler way?"
- Flag scope creep: "do we actually need this in the current sprint?"
- Point out technical debt being introduced
- Don't rely on reminding me to do things — if something must happen every time, suggest we automate or enforce it with tooling (lesson from a past project: prompts get forgotten, hooks don't)
- Be direct. Skip flattery. If something is wrong, say so.
- If context window is >70% full, say so and suggest /compact before continuing
- Scope each session to ONE feature or ONE bug — push back if asked to do more

## Rapporteringsregel (alla tasks)
Innan du rapporterar utfall: granska varje påstående mot ett faktiskt
verktygsresultat från denna session. Rapportera endast det du kan peka
på belägg för. Om något inte är verifierat eller hoppades över — säg det
uttryckligen. Misslyckade tester rapporteras med output, inte omskrivning.

## /goal-reglerna
- **Villkor och brief skickas i samma paste.** Villkoret är ett
  maskinverifierbart GOLV (minsta testbara bevis), inte hela leveransen.
  Briefen är FACIT — den beskriver vad som faktiskt ska byggas. När de
  skiljer sig i omfattning är briefen specifikationen. Tolkar du "minsta
  uppfyllande" — flagga det FÖRE leverans, inte efteråt (DEC-014).
- **/goal är bara för byggtasks** med flera verifierbara villkor. Inte
  för enstegs-frågor, research eller dokuppdateringar.

## Vid sessionsstart
**Kör `git fetch origin --prune` först om någon refererar till commits eller
filer som "redan finns".** Lokala klonen kan ligga commits efter origin —
tidigare sessioner pushar, men din klon vet inte om det förrän du fetchar.
Lärdom (Sprint 11 T5.7): klonen låg 34 commits efter origin/dev, vilket
fick mig att felaktigt avbryta med "förutsättning ej uppfylld" när allt
redan fanns på origin. Kontrollera ALDRIG existens enbart med lokala kommandon.

## What Claude Gets Wrong on This Project
<!-- Update this as you discover patterns — highest-value section -->
- **overflow-x/overflow-y-fällan**: CSS-specen tvingar overflow-y till auto om overflow-x sätts till auto. Använd ALDRIG overflow-x:auto på ett element som ska scrolla vertikalt med sidan. Tidslinjen bröts tre gånger av detta.
- **height:100% i flex/grid**: Absolut-positionerade barn (bars, markörer) syns inte om föräldern har height:100% i en flex-container — resolvar till 0. Använd alltid explicit pixelhöjd.
- **commit.sh kräver ibland manuell git add**: Glob-mönster i bash matchar inte alltid nya filer. Kör `git add <fil>` innan `./commit.sh` om det klagar.
- **Glömmer att varje HTML-fil är self-contained**: Alla CSS/JS dupliceras per sida. Ändra design tokens/nav → uppdatera ALLA .html-filer.
- **Mobilproblem upptäcks inte förrän användaren testar**: Testa alltid mental modell mot 375px viewport. Touch-targets minst 44px. overflow-klippning syns inte i kodgranskning.
- **clearDetail()/renderDefault() kraschar efter innerHTML-byte**: Om en funktion förväntar sig ett DOM-element som en annan funktion bytt ut, kraschar den tyst. Återskapa elementet innan.
- **Burns tokens on planning when task is already scoped** — just execute
- **Forgets to update docs** — enforced by commit.sh, but verify before committing
