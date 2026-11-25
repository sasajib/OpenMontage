# Checkpoint field traps

Schema rejections seen in OpenMontage runs. Check the schema before writing; these are the known misses.

## research_brief
- `expert_voices[]`: `contrarian` (bool), not `stance`. No `notable_quote`; fold it into `position`.
- `data_points[]`: `usable_as`, not `use_as`. `credibility` must be `primary_source`, `secondary_source` or `anecdotal`. `visual_potential` is rejected.
- `trending.recent_developments[]`: `headline`, `date`, `relevance` are required. `event` and bare `url` fail.
- `visual_references[]`: only `description`, `url`, `what_works`.
- `angles_discovered[]`: no `animation_fit`, `audio_direction`, `motion_commitment` or `visual_references`; fold them into `grounded_in` and `why_now`. Required: `name`, `hook`, `type`, `why_now`.

## proposal_packet
- `decision_log.decisions[].category` must be a schema enum value: `music_source`, not `music_selection`. `topic_selection` and `style_selection` are rejected; use `concept_selection` or `playbook_selection`.
- `decision_log.decisions[]`: no `timestamp` key. `options_considered[]` needs `option_id`, `label`, `score`, `reason` (not `option` or `rejected_because`).
- `concept_options[]`: no `animation_mode`, `audio_architecture`, `reuse_strategy`, `risks`. Use `grounded_in`, `key_points`, `why_this_works`.
- `cost_estimate`: no `provider_comparison` or `budget_cap_usd`; move them to `metadata`.
- `production_plan.quality_tradeoffs` is an array.
- `alternative_paths[]` needs `description`, `total_cost_usd`, `quality_level`; no `name`.
- `delivery_promise` requires `motion_required` and `tone_mode`.
- `voice_selection` has no `speed`, `tool` or `voice` keys; use `voice_id` and `pacing_policy`.

## publish_log
- `entries[0].metadata_used.chapters` must be objects `{time, title}`. The string form `0:00 The loop` fails `write_checkpoint` at publish.

## decision_log (any stage)
- `category` must be a schema value. `quality_gate` was rejected at finalize; `visual_accuracy_check` was accepted.
