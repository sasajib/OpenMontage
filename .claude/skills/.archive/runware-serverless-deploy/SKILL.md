---
name: runware-serverless-deploy
description: Use when Runware serverless gives 401/403/402, needs deploying, or a Runware top-up landed in the wrong balance.
category: gpu-compute
---

# Runware serverless deploy

Read the exact status before acting. Runware's errors doc: `403` = credentials are fine but the org has no Serverless access (waiting on the "Request access" form approval, or revoked); `401` = the key itself is rejected, so re-check the key source; `402 insufficient-credit` = the serverless balance cannot cover the workers, and the `shortfall` field is the amount to add. Probe both APIs with the same key before touching anything (see step 1).

1. Probe both APIs with the same key: `/v1/gpu-types` on serverless, and the `authentication` task on the main API. Compare the results.
2. If only serverless fails, stop and ask the user to confirm the access request was approved. Do not create new keys or re-login the CLI.
3. Once access is live, run the deploy sequence in `references/deploy-sequence.md`.

Billing (check before topping up):
- Serverless draws from its own prepaid balance, separate from the balance inference calls use. The top-up page does not ask which one, so a top-up can land in inference and leave serverless unfunded.
- No documented transfer between the two balances, and purchases are described as non-refundable (refunds at Runware's discretion, usually as credits). Ask Runware support in writing first, quoting the top-up date and amount; do not assume a refund.
- The inference balance still works for hosted calls (for example hosted LTX-2.5 via `modelSearch` on `api.runware.ai`), so it is not wasted.

Fixed rules:
- `--volume` and `--gpu-type` are create-time only; redeploy to change them.
- Ports 8000, 8888, 8889 and 9090 are reserved in the container.
- Never print the API key or HF token; mask command output.

Command order and first-run status: `references/deploy-sequence.md`.