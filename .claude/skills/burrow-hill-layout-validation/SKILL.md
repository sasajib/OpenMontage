---
name: burrow-hill-layout-validation
description: Use before rendering or handing over any Burrow Hill DSA video, or when the user reports text cut off, a label under a line, or something blocking the doors.
---

# Burrow Hill layout validation

Validate a built Burrow Hill piece by measurement before any render. The user found three layout defects by eye on 2026-11-19 that
HyperFrames' own check (9 samples) had passed; this check seeks the timeline every 0.4 s and would have caught all three.

## Run

```bash
P=~/Desktop/workspaces/OpenMontage/projects/dsa-burrow-pilot
node $P/scripts/build.mjs <ids>            # the check reads hyperframes/<id>/index.html, so build first
node $P/scripts/validate_layout.mjs <ids>  # exit 0 = every piece clean, 1 = problems
```

No render is needed. A 100 s piece takes about 20 s. `render.py` runs the same check and skips a failing piece unless `--force`.
Needs the global `playwright` package (`npm root -g`); a backup of the script is in `~/.claude/skills/burrow-hill-dsa-chapter/engine/`.

## What it reports

Each line is `start-end s | CHECK | element | other element`. Only problems lasting 0.8 s or more are listed.

| Check | Meaning | Usual fix |
|---|---|---|
| `OFFSCREEN` | a label leaves the 1920x1080 frame | move it left, shorten the text, or lower the font size |
| `TEXT/TEXT` | two labels overlap | give each its own row or zone; hide the old one first |
| `LINE/TEXT` | a bar or bracket runs through a label | put the bar at least 12 px below the label |
| `ITEM/DOOR` | a parcel sits across a door it does not live in | park waiting items left of the row (x < 300) or right of it (x > 1610) |
| `ITEM/TEXT` | a parcel covers a label | move the label to the top band |
| `ACTOR/TEXT` | a character covers a label | raise or shift the chip, lower the hop height, or hide the chip before the character arrives |

## Rules it enforces

1. Text stays fully on screen for its whole life.
2. Nothing overlaps a label: not another label, a line, an item or a character.
3. Items wait beside the structure, never in front of doors, even for a few seconds.

## What it does not check

- Whether the picture explains the idea, or whether something blocks an unlabelled thing the narration is pointing at. After the check passes, still read a contact sheet (`npx --yes hyperframes snapshot --frames 18`) and ask of each frame: is anything in front of what is being explained right now?
- Top-down scenes with arrows (linked lists): arrows are SVG lines and are not measured.
- Problems shorter than 0.8 s.

## Adding a new kind of element

The script classifies by CSS class: text (`card chip stampb title kicker big who stepc tbl code nb glab cmp rnd`), items (`pc pk m2 stone`),
lines (`seg wbar brace stem`, plus any coloured `.abs` box with an id), doors (`df d2`), characters (`.actor svg`).
A new class must be added to the matching list at the top of the page-side function, or it is not checked.
A strike-through drawn on purpose gets an id ending in `-x`.
