# Runware serverless deploy sequence (LTX-2.5 app, openmontage-ltx25)

App dir: projects/runware/openmontage-ltx25 (container/ holds Dockerfile, container.yaml, server.py).

1. runware auth status
2. runware serverless gpus   (confirm the 96 GB pool has capacity)
3. printf '%s' "$HF_TOKEN" | runware serverless secrets set HF_TOKEN --value-file -
4. runware serverless deploy --id openmontage-ltx25 --gpu-type rtx-pro-6000 --container ./container --volume /weights --max-workers 1 --idle-ttl 60 --wait
5. runware serverless secrets attach openmontage-ltx25 HF_TOKEN
6. Invoke the generate endpoint async and poll until done; record cold start, clip time and cost.

Status of the first run (2026-11-05): blocked at step 2 by the 401 described in SKILL.md.
