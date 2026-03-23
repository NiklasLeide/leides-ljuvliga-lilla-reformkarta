Cold project restart. I have been away for weeks or months. Work through these steps in order.

## Step 1 — Orient (read silently, do not output full files)
Read these files:
- @docs/PROJECT_STATUS.md
- @docs/DECISIONS.md (last 3 entries only)
- @docs/CHANGELOG.md (last 5 entries only)
- @docs/MAINTENANCE.md

Then tell me in plain language:
- What was the last thing completed
- What was I about to do next
- Any known blockers or open questions left behind
- How long ago the last commit was (run: git log -1 --format="%ar")

## Step 2 — Environment check
Run these and report what fails:
1. Check for the start command in MAINTENANCE.md or CLAUDE.md — try running it
2. Check outdated dependencies (Python: pip list --outdated | head -10 / Node: npm outdated)
3. Run: git status — any uncommitted changes left behind?
4. Check .env exists and is not empty

Report failures before touching any code.

## Step 3 — Triage
Ask me: "What brings you back — new feature, bug fix, or maintenance?"
Wait for my answer. Do not start coding until I confirm.
