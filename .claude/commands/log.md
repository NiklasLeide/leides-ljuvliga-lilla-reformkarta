End-of-session update. Do all of these:

1. Run `git diff HEAD~1 --stat` to see what changed this session
2. Update @docs/CHANGELOG.md — add one line per logical change:
   Format: [YYYY-MM-DD] type: description
3. Update @docs/PROJECT_STATUS.md:
   - Change task statuses (⬜/🔄/✅) to reflect reality
   - Update "Last updated" date
   - Update "What's Working Now" if new things are runnable
4. If a new decision was made this session: remind me to run /project:decide before closing
5. If a new bug was hit and fixed: add it to @docs/TROUBLESHOOTING.md

4. Update @docs/ROADMAP.md — mark any completed items as done
5. If a new decision was made: remind me to run /project:decide
6. If a new bug was hit and fixed: add it to @docs/TROUBLESHOOTING.md

Then: `./commit.sh "docs: session update [date]"`
