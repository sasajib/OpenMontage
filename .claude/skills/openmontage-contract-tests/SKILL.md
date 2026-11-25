---
name: openmontage-contract-tests
description: Use when running OpenMontage pytest or tests/contracts.
category: testing
---

# OpenMontage contract tests

Run the contract suite through uv with pytest added for that run only. Do not install into `.venv`, which has no pytest.

- Suite: `uv run --no-project --python .venv/bin/python --with pytest python -m pytest tests/contracts -q 2>&1 | tail -6`, with a 400 s timeout. A full run took about 70 to 150 s.
- Quick manifest check: in `.venv/bin/python`, import `lib.pipeline_loader.load_pipeline` and load each pipeline name. Use this after editing `pipeline_defs/*.yaml`.
- Report the exact pass, fail and skip counts. Never call the suite green while failures remain.
- Before blaming new edits for a failure, check `git diff` for the failing file. Skill-pointer failures can come from earlier uncommitted skill work.

Last observed baseline: 3 failed, 1272 passed, 7 skipped, all in `tests/contracts/test_agent_skill_pointers.py`. Those were `reality_check` and `audio_check` pointers to video-reality-check and generated-visual-anatomy-qa.
