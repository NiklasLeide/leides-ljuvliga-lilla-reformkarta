#!/bin/bash
# synka-dev.sh — för dev ikapp master utan force (Sprint 15). Används av automat-publicera.sh och av
# arbetsflödet synka-dev.yml efter att en PR mergats till master.
#   scripts/revision/synka-dev.sh <master-sha>
# Är dev en förfader till master → dev snabbspolas. Har dev egna commits → master mergas in i dev.
# Konflikt → exit 4, dev orörd. Mappen dev/ hanteras som vanliga filer (ingen särbehandling, inget raderas).
set -euo pipefail
NY="${1:?master-sha saknas}"
cd "$(git rev-parse --show-toplevel)"
git config user.name >/dev/null || git config user.name "github-actions[bot]"
git config user.email >/dev/null || git config user.email "41898273+github-actions[bot]@users.noreply.github.com"
git fetch -q origin dev
DEV=$(git rev-parse origin/dev)
if [ "$DEV" = "$NY" ]; then
  echo "[synka-dev] dev redan = master ($NY)"
elif git merge-base --is-ancestor "$DEV" "$NY"; then
  git push -q origin "$NY:refs/heads/dev"
  echo "[synka-dev] dev snabbspolad till $NY"
else
  git checkout -q -B automat-dev-synk origin/dev
  if ! git merge -q --no-edit "$NY"; then
    git merge --abort || true
    echo "[synka-dev] STOPP: konflikt när master mergades in i dev — dev orörd" >&2
    exit 4
  fi
  git push -q origin HEAD:dev
  echo "[synka-dev] master mergad in i dev ($(git rev-parse --short HEAD))"
fi
