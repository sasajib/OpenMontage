---
name: hyperframes-compose
description: Use when npx hyperframes or hyperframes_compose fails, or the check gate reports contrast or layout errors.
category: video-production
---

# HyperFrames composition in OpenMontage

Rename the workspace package before any `npx hyperframes` call. `init` writes `"name": "hyperframes"` into the workspace package.json, and npx then resolves the local package (no bin) instead of the CLI. Every check and render fails from that folder.

1. Scaffold non-interactively: `HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <dir> --example blank --resolution portrait --non-interactive --skip-skills`. There is no `--yes` flag. The npm package is `hyperframes`; `@hyperframes/cli` does not exist.
2. Immediately set `"name": "<project>-hf"` in `<dir>/package.json`.
3. Pin the CLI: `npx --yes hyperframes@0.8.223 --version` from `<dir>`, and use the same pin in any command you run.
4. Run `check` and `snapshot --at` before rendering. Fix lint and layout issues first. The snapshot output flag is `--output` (`--out` is rejected as an unknown flag). Snapshot the beats, tile them into one contact sheet with PIL, and look at the sheet once instead of opening each frame.
4a. A `<video>` lint error "references local file(s) not found" means the renderer will silently skip those clips. Generate or place the clips in `assets/` before the final check, or the render comes out without them.
5. Render through `video_compose` with the hyperframes runtime so OpenMontage's final review runs.
6. If compose fails, report the `steps.check` stderr to the user. Do not silently fall back to Remotion or FFmpeg; governance requires surfacing the failure first.

Authoring rules that passed `check`: one paused GSAP timeline on global time; captions as non-overlapping clips on one track (overlapping clips hide each other and fail the layout gate); chart labels must sit inside their column box.

## Contrast gate

`check` measures the text colour against the sampled background. `text-shadow` does not count, however heavy. When a photo or generated plate is lighter than the drawn scene it replaced (Z-Image skies, sunsets), give the text a backing: `background: rgba(7,26,58,0.6); padding: 10px 26px; border-radius: 18px`. For stacked hook lines use `display: table` on each line so every line gets its own shrink-to-fit pill; `display: inline` merges the lines into one paragraph. Re-run `check` and `snapshot --at` the flagged times; a passing gate is required, not a lower warning count.

## Caption and overlay fixes that held

- When suppressing captions around an insert or stamp, drop any caption that overlaps the window (`p.s < b and p.e > a`), not only ones that start inside it. A start-only test lets a caption that began earlier double up with the insert.
- Re-snapshot after moving a CTA or box: the last caption and the CTA collided at the bottom of the frame until the CTA was moved to the top.
- A `tl.set` on a hidden element before its `fromTo` silences the streak/baseline warning from `check`; keep the element's starting state explicit on the timeline.

## Stopping a render

Stop the background task by its task id, then kill leftover `hyperframes/dist/w*` node workers by PID from `pgrep -fl hyperframes`. Never `pkill -f "hyperframes.*render"`: the pattern matches the shell that runs it and kills your own command (exit 144).
