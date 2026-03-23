# Troubleshooting — leides-ljuvliga-lilla-reformkarta

Known issues and solutions. Check here before debugging. Add here when you fix something.

---

## Format
```
### Issue title
**Symptom:** What you observed
**Cause:** Why it happened
**Solution:** What fixed it
```

---

## WSL2 / Environment

### WSL2: permission errors on /mnt/c/
**Symptom:** Permission errors running scripts or tools on files under `/mnt/c/`.
**Cause:** Windows filesystem mounted at `/mnt/c/` doesn't support Linux permissions.
**Solution:** Keep the project on the native WSL filesystem (`~/projects/`). Only use `/mnt/c/` for dropping files from Windows.

### git init fails or behaves unexpectedly
**Symptom:** `git init` or git operations fail on `/mnt/c/`.
**Cause:** Same filesystem permission issue as above.
**Solution:** Keep the git repo on native WSL: `~/projects/leides-ljuvliga-lilla-reformkarta`.

### Python venv fails
**Symptom:** `python -m venv` fails or venv doesn't work.
**Cause:** Symlinks and permissions broken on mounted Windows filesystem.
**Solution:** Create venv on native WSL: `python3 -m venv ~/venv-leides-ljuvliga-lilla-reformkarta`

---

## Claude Code

### Claude Code auto-update fails on startup
**Symptom:** Warning on startup that Claude Code failed to auto-update.
**Cause:** Global npm packages need sudo; auto-updater doesn't use it.
**Solution:** `sudo npm install -g @anthropic-ai/claude-code`
Not critical — Claude Code still works, it's just a warning.

### Claude Code forgets to update PROJECT_STATUS.md
**Symptom:** Tasks get done but PROJECT_STATUS.md stays stale.
**Cause:** Prompt-based rules in CLAUDE.md get missed when Claude is focused on code.
**Solution:** Don't rely on prompts — enforce with tooling. Use a `commit.sh` script
or git hooks that check documentation is updated before pushing.
**General principle:** If something needs to happen every time, automate it. Never rely on Claude remembering.

---

## Git / GitHub

### npm global install needs sudo
**Symptom:** `npm install -g` fails with permission errors.
**Solution:** `sudo npm install -g <package>`

---
## Build / Deploy

### commit.sh kräver manuell git add för rotfiler
**Symptom:** `./commit.sh` säger "no changes added to commit" trots att filer ändrats.
**Cause:** Skriptet kör `git add docs/ src/ .claude/` och `git add *.json *.ts *.js *.sh *.md` — men glob-mönster i bash matchar bara redan stagade eller trackade filer om de inte redan finns i index. Ibland behöver filer stagas manuellt först.
**Solution:** Kör `git add <fil>` innan `./commit.sh "msg"`.

### CSS media query ordning: generella regler skriver över media queries
**Symptom:** Mobil listvy (`display: block` i portrait media query) syntes inte.
**Cause:** `.list-view { display: none; }` definierades *efter* portrait-mediaqueryns `.list-view { display: block }`. Samma specificitet → sista regeln vinner.
**Solution:** Flytta generella `display: none`-regler till *före* alla media queries. Media queries som sätter `display: block` måste komma efteråt för att få företräde.

### Touch swipe-to-close triggas av scroll i panel
**Symptom:** Sidopanelen stängs när man scrollar uppåt i den och når toppen.
**Cause:** Swipe-hanteraren kollade `dy > 60` (vertikalt) utöver `dx > 60` (horisontellt). Scroll som nådde toppen registrerades som vertikal svep.
**Solution:** Stäng bara vid horisontell svep: `dx > 60 && Math.abs(dx) > Math.abs(dy) * 2`.

### Zoom/pan hoppar vid start på touch
**Symptom:** Kartan hoppar till en annan position när man börjar zooma eller panorera.
**Cause:** Första fingret startade pan, sedan landade andra fingret (pinch) med en offset. Pan-state överfördes inte korrekt till pinch.
**Solution:** Dead zone (5px) innan pan startar. Vid pinch: nollställ pan-state med pinch-mittpunkt. Vid finger-release från 2→1: starta inte ny pan.

---
## TBD / App

_Add issues here as you encounter them._

---
