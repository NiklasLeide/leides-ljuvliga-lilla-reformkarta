#!/bin/bash
# deploy.sh — merge dev to master and push to production
# Requires manual confirmation. Only Niklas runs this.

set -e

echo "=== Deploy till produktion ==="
echo ""

# Show commits in dev that aren't in master
AHEAD=$(git log master..dev --oneline 2>/dev/null)

if [ -z "$AHEAD" ]; then
  echo "Inget att deploya — dev och master är i synk."
  exit 0
fi

echo "Commits i dev som inte finns i master:"
echo "────────────────────────────────────────"
echo "$AHEAD"
echo "────────────────────────────────────────"
echo ""

read -p "Vill du merga dev till master och deploya? (ja/nej): " CONFIRM

if [ "$CONFIRM" != "ja" ]; then
  echo "Avbryter. Inget ändrat."
  exit 0
fi

echo ""
echo "Mergar dev → master..."
git checkout master
git merge dev --no-edit
echo "Pushar master..."
git push origin master
echo "Tillbaka till dev..."
git checkout dev

echo ""
echo "✓ Deploy klar. Master uppdaterad och pushad."
