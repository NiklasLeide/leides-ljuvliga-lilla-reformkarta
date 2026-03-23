I am parking this project. Do all of these before I close:

1. Run: git status
   If uncommitted changes exist — commit them first with a descriptive message.

2. Update @docs/PROJECT_STATUS.md:
   - Set all 🔄 in-progress tasks to accurate status
   - Add a "Parked on [date]:" note at the very top with:
     what is working, what was next, any gotchas to remember on return
   - Update "Last updated" date

3. Update @docs/CHANGELOG.md with today's changes

4. Check @docs/TROUBLESHOOTING.md — any new issues hit this session? Add them now.

5. Check @docs/DECISIONS.md — any architectural choices made? Log them now.

6. Update @docs/MAINTENANCE.md "Last parked" section with today's date and one-line state summary.

7. Final commit:
   ./commit.sh "docs: park project — [one line summary]"

8. Tell me the exact commands to resume next time:
   cd [project dir] && code .
   then in VS Code terminal: claude
   then: /resume

Do not skip steps. This is what makes returning in 3 months painless.
