Review the most recent code changes critically.

First run: `git diff HEAD~1 --name-only` to see what changed.

For each significant file changed:
1. Is there a simpler approach?
2. What technical debt is this introducing?
3. Missing error handling or edge cases?
4. Does this align with @docs/DECISIONS.md — are we drifting from agreed architecture?
5. Anything that should go in @docs/TROUBLESHOOTING.md?

Be specific. No filler. If something is fine, say so in one word and move on.
Flag scope creep if you see it.
