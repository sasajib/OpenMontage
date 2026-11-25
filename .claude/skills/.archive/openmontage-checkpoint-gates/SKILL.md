---
name: openmontage-checkpoint-gates
description: Use when writing a gate PASS to an OpenMontage checkpoint.
category: video-production
---

# OpenMontage checkpoint gates

A gate verdict (G1–G6 and similar) must come from re-running that stage's review after the change. Never write `PASS` into checkpoint metadata by hand.

- Write checkpoints in pipeline order. `proposal` is rejected with `PREREQUISITE VIOLATION: stage 'proposal' cannot advance; incomplete or missing: ['research']` if the research checkpoint is not written first. Run the research script and confirm `research ok` before the proposal script.
- If a fix changes an artifact, re-run the gate for that stage and record what it actually returned.
- Keep `metadata.review` for real review output. Put a note about a manual fix in a separate `notes` field.
- Before writing a checkpoint, validate each artifact with jsonschema against its file in `schemas/artifacts/` (for example `schemas/artifacts/render_report.schema.json`). Build artifacts only from fields the schema declares, and drop extras. A render report failed validation on one enum field and had to be fixed and rewritten.
- Do not fix validation errors one at a time. Before the first write, dump every artifact's `required`, enums, and `additionalProperties` in one script pass, and collect all errors at once with `jsonschema.Draft7Validator(schema).iter_errors(data)` (not `validate()`, which stops at the first error). Then write each artifact once. Run the script with `.venv/bin/python`, since the system python lacks jsonschema. A research brief and a proposal packet each took 3–4 failed runs because the author guessed field names. Known traps:
  - research_brief `expert_voices`: `contrarian` (bool), not `stance`.
  - research_brief `data_points`: `usable_as`, not `use_as`; `credibility` must be `primary_source` / `secondary_source` / `anecdotal`.
  - research_brief `trending.recent_developments`: `headline`, `date`, `relevance` are required; `event` and bare `url` fail.
  - proposal_packet `decision_log` `decisions[].category`: must be one of the schema enum (e.g. `music_source`, not `music_selection`). `topic_selection` and `style_selection` are rejected; use `concept_selection` and `playbook_selection`.
  - decision_log `decisions[]`: no `timestamp` key. `options_considered` items need `option_id`, `label`, `score`, `reason` (not `option` / `rejected_because`).
  - research_brief `visual_references[]`: only `description`, `url`, `what_works`. `data_points[]`: `visual_potential` is rejected (use `usable_as`). `angles_discovered[]`: no `animation_fit`, `audio_direction`, `motion_commitment`, or `visual_references` (fold them into `grounded_in` and `why_now`); required keys are `name`, `hook`, `type`, `why_now`. `expert_voices[]`: no `notable_quote` (fold it into `position`).
  - proposal_packet `concept_options[]`: no `animation_mode`, `audio_architecture`, `reuse_strategy`, `risks` (use `grounded_in`, `key_points`, `why_this_works`). `cost_estimate`: no `provider_comparison` or `budget_cap_usd` (move to `metadata`). `production_plan.quality_tradeoffs` is an array. `alternative_paths[]` needs `description`, `total_cost_usd`, `quality_level` (no `name`). `delivery_promise` requires `motion_required` and `tone_mode`. `voice_selection` has no `speed`, `tool`, or `voice` keys (use `voice_id`, `pacing_policy`).
- `publish_log` `entries[0].metadata_used.chapters` must be objects `{time, title}`, not `"0:00 The loop"` strings. The string form fails `write_checkpoint` at the publish stage with `'0:00 The loop' is not of type 'object'`. Convert the chapters before the first write, and mirror the same list into `exports/metadata.json`.
- When the user says "approve" and asks you to work autonomously, carry the remaining stages straight through without pausing at each one. Stop only for a real deviation from the approved plan, or for spend the user has not approved.
- Decision-log `category` must be a value the schema accepts. A `quality_gate` category was rejected at finalize and had to be replaced with `visual_accuracy_check` before the publish checkpoint could be written. Check the allowed values in the schema before writing decisions.
- If the change moves away from what the user approved (values, scenes, voice, runtime), stop and tell the user before continuing.
