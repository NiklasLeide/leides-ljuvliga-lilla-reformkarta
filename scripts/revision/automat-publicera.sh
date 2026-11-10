#!/bin/bash
# automat-publicera.sh — publicerar automatfilens ändringar (Sprint 15 T4, regel 9 + synkregeln).
# Körs av .github/workflows/automat.yml EFTER att automat.js --tillampa, JSON-validering, testsviten
# och renderingstestet har gått gröna. Förutsätter att arbetskatalogen är en checkout av master.
#
#   scripts/revision/automat-publicera.sh <rapport.json>
#
# Gör: (1) commit "automat: …" med käll-URL:er i brödtexten (bara data/), (2) push till master
# (startar GitHub Pages), (3) synkar dev: är dev == master före körningen snabbspolas dev till nya
# master; har dev egna commits mergas master in i dev (aldrig force). Mappen dev/ på master rörs inte
# (bara data/ committas). Exit: 0 publicerat/inget att göra, 4 = push eller merge misslyckades.
set -euo pipefail

RAPPORT="${1:?rapportfil saknas}"
cd "$(git rev-parse --show-toplevel)"

if git diff --quiet -- data/; then
  echo "[publicera] inga ändringar i data/ — inget att publicera"
  exit 0
fi
# Säkerhet: bara data/ får vara ändrat (dev/ och allt annat orört).
ANDRAT=$(git status --porcelain --untracked-files=no | awk '{print $2}' | grep -v '^data/' || true)
if [ -n "$ANDRAT" ]; then
  echo "[publicera] STOPP: ändringar utanför data/: $ANDRAT" >&2
  exit 4
fi

RUBRIK=$(node -e "const r=require(require('path').resolve(process.argv[1]));process.stdout.write(r.commit||'automat: senast kontrollerad')" "$RAPPORT")
BROD=$(node -e "
const r=require(require('path').resolve(process.argv[1]));
const rader=(r.andringar||[]).map(a=>'- '+a.post+' ('+a.regel+'): '+(a.kalla_url||''));
process.stdout.write((rader.length?'Källor:\n'+rader.join('\n')+'\n\n':'')+'Hämtat automatiskt från riksdagens öppna data (scripts/revision/automat.js).');
" "$RAPPORT")

git config user.name "github-actions[bot]"
git config user.email "41898273+github-actions[bot]@users.noreply.github.com"

FORE=$(git rev-parse HEAD)
git add data/
git commit -q -m "$RUBRIK" -m "$BROD"
if ! git push -q origin HEAD:master; then
  echo "[publicera] STOPP: push till master misslyckades (master har flyttat sig?)" >&2
  exit 4
fi
NY=$(git rev-parse HEAD)
echo "[publicera] master: $FORE → $NY"

# --- Synka dev ---
git fetch -q origin dev
DEV=$(git rev-parse origin/dev)
if [ "$DEV" = "$FORE" ] || git merge-base --is-ancestor "$DEV" "$NY"; then
  git push -q origin "$NY:refs/heads/dev"
  echo "[publicera] dev snabbspolad till $NY"
else
  git checkout -q -B automat-dev-synk origin/dev
  if ! git merge -q --no-edit "$NY"; then
    git merge --abort || true
    echo "[publicera] STOPP: konflikt när master mergades in i dev — dev orörd" >&2
    exit 4
  fi
  git push -q origin HEAD:dev
  echo "[publicera] master mergad in i dev ($(git rev-parse --short HEAD))"
fi
echo "PUBLICERAD_SHA=$NY"
