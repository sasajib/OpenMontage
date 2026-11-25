---
name: openmontage-artifact-writing
description: Use when writing OpenMontage JSON artifacts or checkpoints.
category: video-production
---

# OpenMontage artifacts and checkpoints: validate every write, never hand-write a PASS

Build each artifact in a script from the fields its schema declares. Validate every object against `schemas/artifacts/` before writing, and write each file once. Never write a gate PASS by hand: re-run that stage's review and record what it actually returned.

## Validate before the first write

- Read the schema's `required`, `properties` and enums first. Do not guess field names.
- Collect every error at once with `jsonschema.Draft7Validator(schema).iter_errors(data)`. Plain `validate()` stops at the first error and costs a run per error.
- Run from the repository root with `.venv/bin/python`. The system python lacks jsonschema.
- Validate each asset before appending it, so one bad record fails loudly with its id.

## Asset manifest

- Each asset needs `id`, `type`, `path`, `source_tool` and `scene_id`.
- `type` must be one of: image, video, audio, narration, music, sfx, diagram, animation, 3d_asset, 3d_world, code_snippet, subtitle, font, lut. Put detail in `subtype` and `provider`.
- Asset entries reject unknown keys (`additionalProperties` is false). A `review`, `notes` or `reality_check` object fails. Put review text, verdict and take count in `generation_summary` (a string).
- Check allowed keys with `list(schema['properties']['assets']['items']['properties'])`.
- `cost_usd` is the generation-log execution time times the endpoint rate, or `0.0` for provided assets.

## Edit decisions

- Needs `version`, `cuts` and `render_runtime`. `overlays`, `audio`, `subtitles`, `music` and `transitions` are arrays or objects, as the schema says.

## Checkpoints

- Write them in pipeline order. `proposal` is rejected with `PREREQUISITE VIOLATION` until research is written. Run the research script, confirm `research ok`, then run the proposal script.
- If a fix changes an artifact, re-run that stage's gate and record its real output in `metadata.review`. Put manual-fix notes in a separate `notes` field.
- Decision log `category` must be a schema enum value. Do not add `timestamp` to `decisions[]`. Full list of known rejects: `references/checkpoint-field-traps.md`.
- `publish_log` chapters must be `{time, title}` objects, not strings. Mirror the same list into `exports/metadata.json`.
- After the user approves and asks for autonomy, carry the remaining stages straight through. Stop only for a real deviation from the approved plan, or for unapproved spend. If a change moves away from approved values, scenes, voice or runtime, stop and tell the user.
