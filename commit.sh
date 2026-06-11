#!/bin/bash
# commit.sh — enforced commit workflow (always pushes to dev)
# Usage: ./commit.sh "your commit message"
# Auto-stages docs/, src/, config files. Blocks commit if CHANGELOG not updated with src/ changes.
# NEVER pushes to master root — use deploy.sh for that.
# After pushing dev, syncs site files to dev/ folder on master for preview at reformer.leide.se/dev/

set -e

if [ -z "$1" ]; then
  echo 'Usage: ./commit.sh "commit message"' && exit 1
fi

# Safety: refuse to run on master
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "master" ]; then
  echo "ERROR: Du är på master. Byt till dev först: git checkout dev"
  exit 1
fi

# Stagea varje katalog för sig — git add aborterar hela kommandot vid första
# saknade pathspec, så en saknad katalog (t.ex. src/) skulle annars hindra
# senare i listan från att fångas.
for d in docs/ src/ .claude/ data/ scripts/ .github/; do
  [ -d "$d" ] || continue
  git add "$d" 2>/dev/null || true
done
git add *.json *.ts *.js *.sh *.md *.toml *.py *.html 2>/dev/null || true

SRC_CHANGED=$(git diff --cached --name-only | grep "^src/" || true)
CHANGELOG_CHANGED=$(git diff --cached --name-only | grep "CHANGELOG.md" || true)

if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
  echo "ERROR: src/ changed but CHANGELOG.md was not updated. Update it first."
  exit 1
fi

git commit -m "$1"
git push -u origin dev

# --- Sync dev site files to dev/ folder on master for preview ---
echo ""
echo "Synkar dev-version till master:dev/ för preview..."

# Save current state
STASH_NEEDED=false
if ! git diff --quiet 2>/dev/null; then
  STASH_NEEDED=true
  git stash --quiet
fi

# Switch to master, update dev/ folder
git checkout master --quiet

# Defensiv kontroll: kör ALDRIG reset --hard om vi inte faktiskt står på master.
# En misslyckad checkout (t.ex. ostagade ändringar) får inte leda till att en
# efterföljande reset träffar fel gren och kastar arbete.
if [ "$(git branch --show-current)" != "master" ]; then
  echo "ERROR: kunde inte växla till master för preview-sync; avbryter (ingen reset)."
  [ "$STASH_NEEDED" = true ] && git stash pop --quiet
  exit 1
fi

# Härda preview-syncen: lokala master driver lätt isär från origin/master
# (commit.sh committar bara sync-commits här, deploy.sh mergar dev→master).
# Hämta senaste origin och rikta in lokala master mot den FÖRE sync — annars
# committas sync-commiten på en föråldrad bas och push:en avvisas (non-fast-forward),
# vilket vid en tidigare körning lämnade arbetsträdet kvar på master.
git fetch origin --quiet
# Säkerhet: har lokala master commits som INTE finns på origin/master är det
# (potentiellt) riktigt arbete — reset --hard skulle kasta det. Abortera istället.
UNPUSHED=$(git rev-list origin/master..master 2>/dev/null)
if [ -n "$UNPUSHED" ]; then
  echo "ERROR: lokala master har commits som inte finns på origin/master:"
  git log origin/master..master --oneline
  echo ""
  echo "Preview-syncen avbruten för att inte kasta lokalt arbete med reset --hard."
  echo "Om detta bara är gamla preview-sync-commits, kör:"
  echo "  git checkout master && git reset --hard origin/master && git checkout dev"
  echo "Annars: säkra arbetet (t.ex. via deploy.sh) innan du kör commit.sh igen."
  git checkout dev --quiet
  [ "$STASH_NEEDED" = true ] && git stash pop --quiet
  exit 1
fi
# Inga lokala-only commits → tryggt att rikta in lokala master mot origin.
git reset --hard origin/master --quiet

# Create dev/ folder if needed
mkdir -p dev

# Copy all HTML files from dev branch into dev/ folder
for f in $(git ls-tree --name-only dev: 2>/dev/null | grep '\.html$'); do
  git show "dev:$f" > "dev/$f" 2>/dev/null || true
done

# Copy data/ folder from dev
mkdir -p dev/data
for f in $(git ls-tree --name-only dev:data/ 2>/dev/null); do
  git show "dev:data/$f" > "dev/data/$f" 2>/dev/null || true
done

# Stage and commit dev/ changes
git add dev/ 2>/dev/null || true
if ! git diff --cached --quiet 2>/dev/null; then
  git commit -m "sync: dev preview → dev/" --quiet
  git push origin master --quiet
  echo "✓ Dev-preview uppdaterad på reformer.leide.se/dev/"
else
  echo "· Dev-preview redan i synk."
fi

# Back to dev
git checkout dev --quiet

# Restore stash if needed
if [ "$STASH_NEEDED" = true ]; then
  git stash pop --quiet
fi
