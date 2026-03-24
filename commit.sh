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

git add docs/ src/ .claude/ data/ 2>/dev/null || true
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

# Create dev/ folder if needed
mkdir -p dev

# Copy site files from dev branch into dev/ folder
# Use a temp dir to avoid overwriting master root files
TMPDIR=$(mktemp -d)
git show dev:index.html > "$TMPDIR/index.html" 2>/dev/null || true
git show dev:reformkarta.html > "$TMPDIR/reformkarta.html" 2>/dev/null || true
cp "$TMPDIR/index.html" dev/index.html 2>/dev/null || true
cp "$TMPDIR/reformkarta.html" dev/reformkarta.html 2>/dev/null || true
rm -rf "$TMPDIR"

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
