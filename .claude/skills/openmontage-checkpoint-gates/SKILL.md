---
name: openmontage-checkpoint-gates
description: Use when writing a gate PASS to an OpenMontage checkpoint.
category: video-production
---

# OpenMontage checkpoint gates

A gate verdict (G1–G6 and similar) must come from re-running that stage's review after the change. Never write `PASS` into checkpoint metadata by hand.

- If a fix changes an artifact, re-run the gate for that stage and record what it actually returned.
- Keep `metadata.review` for real review output. Put a note about a manual fix in a separate `notes` field.
- Before writing a checkpoint, validate each artifact with jsonschema against its file in `schemas/artifacts/` (for example `schemas/artifacts/render_report.schema.json`). Build artifacts only from fields the schema declares, and drop extras. A render report failed validation on one enum field and had to be fixed and rewritten.
- Do not fix validation errors one at a time. First dump the schema's enums, `required` lists, and `additionalProperties` for the artifact (one script pass), then write the artifact once. A research brief and a proposal packet each took 3–4 failed runs because the author guessed field names. Known traps:
  - research_brief `expert_voices`: `contrarian` (bool), not `stance`.
  - research_brief `data_points`: `usable_as`, not `use_as`; `credibility` must be `primary_source` / `secondary_source` / `anecdotal`.
  - research_brief `trending.recent_developments`: `headline`, `date`, `relevance` are required; `event` and bare `url` fail.
  - proposal_packet `decision_log` `decisions[].category`: must be one of the schema enum (e.g. `music_source`, not `music_selection`).
- When the user says "approve" and asks you to work autonomously, carry the remaining stages straight through without pausing at each one. Stop only for a real deviation from the approved plan, or for spend the user has not approved.
- Decision-log `category` must be a value the schema accepts. A `quality_gate` category was rejected at finalize and had to be replaced with `visual_accuracy_check` before the publish checkpoint could be written. Check the allowed values in the schema before writing decisions.
- If the change moves away from what the user approved (values, scenes, voice, runtime), stop and tell the user before continuing.
