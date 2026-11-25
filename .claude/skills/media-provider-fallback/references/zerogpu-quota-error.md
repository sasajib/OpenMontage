# Observed on 2026-11-03

Space: ResembleAI/Chatterbox (gradio_client, api_name /generate_tts_audio).

- First call: succeeded, produced a 20.4 s wav.
- Second call seconds later: failed with "You have exceeded your ZeroGPU runs limit. Authenticate with a Hugging Face token for more quota".

The error is a quota message, not a bad input. Retrying in the same window does not help. A Hugging Face token raises the quota, but only add one if the user has provided it.
