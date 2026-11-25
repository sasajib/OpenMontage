# Runware serverless deploy sequence (LTX-2.5 app, openmontage-ltx25)

App dir: projects/runware/openmontage-ltx25 (container/ holds Dockerfile, container.yaml, server.py).

1. runware auth status
2. runware serverless gpus   (confirm the 96 GB pool has capacity)
3. printf '%s' "$HF_TOKEN" | runware serverless secrets set HF_TOKEN --value-file -
4. runware serverless deploy --id openmontage-ltx25 --gpu-type rtx-pro-6000 --container ./container --volume /weights --max-workers 1 --idle-ttl 60 --wait
5. runware serverless secrets attach openmontage-ltx25 HF_TOKEN
6. Invoke the generate endpoint async and poll until done; record cold start, clip time and cost.

## Fixed rules
- `--volume` and `--gpu-type` are create-time only; redeploy to change them.
- Ports 8000, 8888, 8889 and 9090 are reserved in the container.

## Billing
- Serverless draws from its own prepaid balance, separate from the balance inference calls use. The top-up page does not ask which one, so a top-up can land in inference and leave serverless unfunded.
- No documented transfer between the two balances. Purchases are described as non-refundable; refunds are at Runware's discretion, usually as credits. Ask Runware support in writing first, quoting the top-up date and amount. Do not assume a refund.
- The inference balance still works for hosted calls (for example hosted LTX-2.5 via `modelSearch` on `api.runware.ai`), so it is not wasted.

## First-run status (2026-11-05)
Blocked at step 2 by a 401 from the serverless API. Re-probe both APIs before retrying.
