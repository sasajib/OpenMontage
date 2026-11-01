GEMINI TTS: True  {"provider": "gemini", "model": "gemini-3.8-flash-tts", "output": "projects/why-the-sky-is-blue/assets/narration/sample_s4.wav", "format": "wav", "cost_status": "unquoted"}
TTS: False Google TTS failed: 403 Client Error: Forbidden for url: https://texttospeech.googleapis.com/v1beta1/text:synthesize
IMAGE: False Imagen on the Gemini API has retired. Select gemini-nano-banana-2.1 explicitly, or configure Vertex AI for Imagen.
IMAGE: False Gemini image generation failed: 429 RESOURCE_EXHAUSTED. ... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.5-flash-preview-image
GEMINI TTS: False This adapter requests WAV; output_path must end in .wav