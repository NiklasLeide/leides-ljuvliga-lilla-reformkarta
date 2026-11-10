#!/bin/bash
# pilot-sync.sh — synkar Utmaningskartans pilot till förhandsvisningen reformer.leide.se/dev/utmaningar-pilot/
#
# Kopierar pilot/utmaningar/index.html och pilot/utmaningar/data/* från dev till master:dev/utmaningar-pilot/,
# committar och pushar till master. README.md kopieras inte. Inget annat på master än dev/utmaningar-pilot/ rörs.
# Körs av Niklas (Sprint 16 T4).
#
#   ./pilot-sync.sh            synka
#   ./pilot-sync.sh --dry-run  skriv ut vad som skulle kopieras/tas bort, ändra ingenting
#   ./pilot-sync.sh --remove   ta bort dev/utmaningar-pilot/ från master
#
# Säkerhet:
#  - avbryter om nuvarande gren inte är dev eller om arbetskatalogen har ocommittade ändringar
#  - avbryter om lokala dev inte är lika med origin/dev (opushat arbete publiceras inte)
#  - master hanteras i ett tillfälligt git worktree: arbetskatalogen lämnar aldrig dev, och worktree tas bort
#    även vid fel (trap). Därmed är man alltid kvar på dev efteråt.
#  - avbryter om något utanför dev/utmaningar-pilot/ skulle ändras på master
#  - push till master sker bara som fast-forward (aldrig --force)

set -euo pipefail

MAL="dev/utmaningar-pilot"
KALLA="pilot/utmaningar"
MODE="sync"
case "${1:-}" in
  "") ;;
  --dry-run) MODE="dry" ;;
  --remove) MODE="remove" ;;
  *) echo "Okänd flagga: $1 (använd --dry-run eller --remove)"; exit 2 ;;
esac

cd "$(git rev-parse --show-toplevel)"

GREN=$(git branch --show-current)
if [ "$GREN" != "dev" ]; then
  echo "AVBRYTER: du står på '$GREN'. Kör från dev."; exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "AVBRYTER: arbetskatalogen har ocommittade ändringar:"; git status --short; exit 1
fi

# Filer som ska kopieras (från committad dev, inte arbetskatalogen)
FILER=$(git ls-tree -r --name-only dev -- "$KALLA/index.html" "$KALLA/data/")
if [ -z "$FILER" ]; then
  echo "AVBRYTER: hittar inga filer under $KALLA/ på dev."; exit 1
fi

if [ "$MODE" = "dry" ]; then
  echo "TORRKÖRNING — ingenting ändras (ingen fetch, inget worktree, ingen commit, ingen push)."
  echo "Källa: dev ($(git rev-parse --short dev))"
  echo "Mål:   master:$MAL/  →  https://reformer.leide.se/$MAL/"
  echo ""
  echo "Skulle kopieras:"
  for f in $FILER; do echo "  $f  →  $MAL/${f#$KALLA/}"; done
  echo ""
  echo "Skulle tas bort först (befintligt innehåll i master:$MAL/ enligt lokal origin/master):"
  BEF=$(git ls-tree -r --name-only origin/master -- "$MAL/" 2>/dev/null || true)
  if [ -z "$BEF" ]; then echo "  (inget — katalogen finns inte på origin/master)"; else for f in $BEF; do echo "  $f"; done; fi
  echo ""
  echo "Kopieras inte: $KALLA/README.md"
  if [ "$(git rev-parse dev)" != "$(git rev-parse origin/dev 2>/dev/null || echo saknas)" ]; then
    echo ""; echo "OBS: lokala dev skiljer sig från origin/dev (enligt senaste fetch) — den riktiga synken skulle avbryta."
  fi
  exit 0
fi

git fetch origin --quiet
if [ "$(git rev-parse dev)" != "$(git rev-parse origin/dev)" ]; then
  echo "AVBRYTER: lokala dev ($(git rev-parse --short dev)) är inte lika med origin/dev ($(git rev-parse --short origin/dev)). Pusha eller pulla dev först."; exit 1
fi

WT=$(mktemp -d)
stada() {
  git worktree remove --force "$WT" >/dev/null 2>&1 || rm -rf "$WT"
  git worktree prune >/dev/null 2>&1 || true
  # Arbetskatalogen har aldrig lämnat dev; kontrollera ändå.
  [ "$(git branch --show-current)" = "dev" ] || git checkout dev --quiet
}
trap stada EXIT

git worktree add --detach --quiet "$WT" origin/master

if [ "$MODE" = "remove" ]; then
  if [ -z "$(git -C "$WT" ls-tree -r --name-only HEAD -- "$MAL/")" ]; then
    echo "Inget att ta bort: $MAL/ finns inte på master."; exit 0
  fi
  git -C "$WT" rm -r --quiet -- "$MAL"
  MEDD="pilot: ta bort förhandsvisning $MAL/"
else
  rm -rf "${WT:?}/$MAL"
  mkdir -p "$WT/$MAL"
  for f in $FILER; do
    mal="$WT/$MAL/${f#$KALLA/}"
    mkdir -p "$(dirname "$mal")"
    git show "dev:$f" > "$mal"
  done
  git -C "$WT" add -A -- "$MAL"
  MEDD="pilot: synka Utmaningskartan till $MAL/ från dev $(git rev-parse --short dev)"
fi

# Skyddsräcke: inget utanför dev/utmaningar-pilot/ får vara stageat
UTANFOR=$(git -C "$WT" diff --cached --name-only | grep -v "^$MAL/" || true)
if [ -n "$UTANFOR" ]; then
  echo "AVBRYTER: ändringar utanför $MAL/ skulle committas:"; echo "$UTANFOR"; exit 1
fi
if git -C "$WT" diff --cached --quiet; then
  echo "Inget att göra: master:$MAL/ är redan i synk."; exit 0
fi

git -C "$WT" diff --cached --stat
git -C "$WT" commit --quiet -m "$MEDD"
git -C "$WT" push origin HEAD:master
echo "Klart: https://reformer.leide.se/$MAL/  (GitHub Pages kan behöva någon minut)"
