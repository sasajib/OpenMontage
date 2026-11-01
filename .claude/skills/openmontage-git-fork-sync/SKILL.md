---
name: openmontage-git-fork-sync
description: Use when syncing OpenMontage fork or upstream remotes.
category: git-workflow
---

# OpenMontage fork and upstream sync

Remotes: `origin` = https://github.com/sasajib/OpenMontage.git (the user's fork, the only push target). `upstream` = https://github.com/calesthio/OpenMontage.git (original project, never push).

- Pull upstream changes: `git fetch upstream && git pull --rebase --autostash upstream main`.
- Publish to the fork: `git push origin main`, only when the user asks for a push in that turn.
- If the rebase conflicts, stop, list the conflicting files, and ask before resolving.
- Stage explicit paths only. Never `git add -A` here, because `AGENT_GUIDE.md` can carry an unrelated uncommitted line that must stay out of commits.
- In this shell `cp` prompts before overwriting. Write files with `cat src > dst` or `command cp -f src dst`.
