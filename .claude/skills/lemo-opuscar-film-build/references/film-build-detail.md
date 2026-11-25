# lemo-opuscar film build: stage order and costs

Run from the repo root with `PYTHONPATH=. .venv/bin/python`:

1. write_preprod.py (research reuse and proposal)
2. approve_and_script.py
3. gen_narration.py or voice_loop.py
4. opuscar stages, run from the lemo-opuscar checkout with `LIB` set to its path and its own py3.12 venv: still.mjs sheet, still.mjs range plus sheet.py, events.mjs, readcheck.mjs, music/score.py, mix.py, video.mjs, mux.sh, tools/subs.py
5. write_artifacts.py
6. compose_publish.py

Notes:
- The OpenMontage venv is py3.10. Run Whisper through the opuscar python, not the project venv.
- Measured cost for one 82 s film: about $0.03 of Deepgram narration. Everything else ran locally.
- Rendered frames are JPEG temp files; expect tens of GB during a render.
