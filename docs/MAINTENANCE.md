# Maintenance — leides-ljuvliga-lilla-reformkarta

> Statisk sajt: ren HTML/CSS/JS, inga byggsteg. "Kör" = öppna en .html-fil i
> webbläsaren, eller servera repo-roten statiskt. Deploy = `./deploy.sh` (dev→master).
> Nedanstående boilerplate-sektioner (venv/npm/API_KEY) är mallrester och gäller INTE.

## Datamaintenance — färskhetsstämpel (Sprint 12 T3)

Alla publika sidor visar "Senast uppdaterad <datum>" läst ur **`data/meta.json`**
(`{ "senast_uppdaterad": "YYYY-MM-DD" }`). Sidorna parsar strängen manuellt till
svenskt datum — ingen `new Date()`-lokaltolkning. Kan filen inte läsas visas ingen
stämpel (tyst fallback).

**Regel för VARJE datapatch (manuell eller via `/bevakning`):** ändrar du en fil
i `data/`, sätt i samma commit `data/meta.json` `senast_uppdaterad` till patchens
datum (beslutsdatum om ett enda styrande beslut, annars dagens patchdatum — var
konsekvent). En datapatch utan bump gör att sajten ljuger om sin aktualitet, vilket
är precis den förtroendebrist Sprint 12 åtgärdade. `/bevakning`-kommandot gör detta
automatiskt; vid manuella patchar är det ditt ansvar.

---

> Fill this in THE MOMENT you get the project running. Not later. Now.
> If you can't run the project from these instructions alone, they're not done yet.
> Run /project:resume when returning — it reads this file first.

## How to run this project

```bash
# 1. Navigate to project
cd /home/niklas/projects/leides-ljuvliga-lilla-reformkarta

# 2. Activate environment (if applicable)
# source ~/venv-leides-ljuvliga-lilla-reformkarta/bin/activate   ← Python venv
# nvm use 18                        ← Node version

# 3. Set up environment variables
cp .env.example .env
# Edit .env and fill in real values

# 4. Install dependencies
# pip install -r requirements.txt   ← Python
# npm install                        ← Node

# 5. Start the app
# [fill in your start command]
```

## Environment variables needed
| Variable | Where to get it | Required? |
|----------|----------------|-----------|
| `API_KEY` | [service dashboard] | Yes |

## Dependencies and versions
| Tool/Library | Version | Notes |
|-------------|---------|-------|
| Python/Node | [version] | |

## Data file locations
<!-- Where does this app store its data? -->
- _Fill in: e.g., %APPDATA%/com.myapp/data.json, ~/.config/myapp/, sqlite.db_

## Known environment quirks
<!-- Things that will bite you when setting up fresh -->
- [Fill in as you discover them]

## How to update dependencies safely
```bash
# Python:
pip list --outdated
pip install --upgrade [package]  # upgrade one at a time, test after each

# Node:
npm outdated
npm update [package]
```

## Last parked
<!-- Updated automatically by /project:parkhere -->
_Not yet parked_

---
> Update the "How to run" section the moment you figure out the setup.
> Do it while it's fresh — not when you're returning cold in 3 months.

## Revisionsskriptet (Sprint 14 T2)

```bash
node scripts/revision/revision.js --datum YYYY-MM-DD   # diffrapport → docs/revision/revision-<datum>.{json,md}
node --test scripts/revision/*.test.js scripts/bevakning/*.test.js   # hela testsviten
node scripts/revision/remiss-e2e.js   # Remissläge i webbläsaren (Playwright), skärmbilder → docs/revision/skarmbilder/
```
Skriptet läser riksdagens öppna data och jämför mot `data/reforms.json` och
`data/utredningar.json`. Det ändrar aldrig datafiler. Fynd klassas RUTIN/BEDÖMNING
i en ändringslista (DEC-018) innan något patchas. Exit 2 = rapport skriven men
minst ett API-anrop misslyckades (se avsnittet Fel i rapporten).

## Remissläge (Sprint 14 T5, DEC-021)

Ny remiss = ny post i `data/remisser.json` (verifiera datum och nästa steg mot remissidan).
Status räknas i klienten och ska aldrig skrivas in i datafilen. `<remiss-lib>`-blocket finns i fyra
sidor och måste vara byte-identiskt — `remiss.test.js` fäller annars. Ändra blocket i alla fyra.

## Automatfilen (Sprint 15 T2, DEC-022)

```bash
node scripts/revision/automat.js                               # torrkörning (standard) — skriver inget
node scripts/revision/automat.js --tillampa --rapport ut.json  # tillämpar regel 1a–1d (används av arbetsflödet)
```
Tillåtna ändringar: beslut + rskr för spårad proposition vid fullt bifall, tilläggsdirektiv när
kommittébeteckning OCH namn stämmer, nytt betänkande, följdändringar (andringar, meta). Allt annat går
till veckorutinen. Vakten stoppar körningen om något annat ändras. Exit 3 = STOPP (ingenting skrivet).
