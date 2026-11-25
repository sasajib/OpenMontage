"""Kokoro-FastAPI text-to-speech provider tool.

Talks to a self-hosted Kokoro-FastAPI server (https://github.com/remsky/Kokoro-FastAPI),
which wraps the open Kokoro-82M model behind an OpenAI-compatible speech API.
Kokoro is free, runs well on CPU, and has 60+ natural voices across several
languages, but it has no voice cloning.

Configure with ``KOKORO_TTS_URL`` (e.g. ``http://127.0.0.1:8880`` or a tunnelled
public hostname). Optional ``KOKORO_TTS_API_KEY`` is sent as a bearer token if
the server sits behind an auth proxy.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class KokoroTTS(BaseTool):
    name = "kokoro_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "kokoro"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Point OpenMontage at a Kokoro-FastAPI server:\n"
        "  export KOKORO_TTS_URL=http://127.0.0.1:8880\n"
        "Run one with Docker:\n"
        "  docker run -d -p 127.0.0.1:8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:v0.2.4\n"
        "Optional: KOKORO_TTS_API_KEY if the server is behind an auth proxy."
    )
    fallback = "piper_tts"
    fallback_tools = ["edge_tts", "piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "voice_blending",
        "word_timestamps",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": True,  # self-hosted; no third-party service involved
        "native_audio": True,
    }
    best_for = [
        "free natural narration from a self-hosted server",
        "fast CPU synthesis with many stock voices",
        "word-level timing for captions at zero cost",
    ]
    not_good_for = [
        "voice cloning (use elevenlabs_tts or fish_audio_tts)",
        "expressive acting or emotion tags",
    ]

    # Curated picks from the 67 shipped voices. Any voice name or blend
    # such as "af_bella(2)+af_sky(1)" may be passed directly.
    RECOMMENDED_VOICES = {
        "heart": "af_heart",  # default, warm female
        "bella": "af_bella",  # bright female
        "sarah": "af_sarah",  # calm female
        "adam": "am_adam",  # deep male
        "michael": "am_michael",  # neutral male
        "emma": "bf_emma",  # British female
        "george": "bm_george",  # British male
    }
    DEFAULT_VOICE = "af_heart"

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to convert to speech"},
            "voice": {
                "type": "string",
                "description": (
                    "Kokoro voice id (e.g. 'af_heart', 'am_adam'), a blend like "
                    "'af_bella(2)+af_sky(1)', or an alias: heart, bella, sarah, adam, "
                    "michael, emma, george. Default af_heart."
                ),
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "description": "Speaking speed multiplier, 0.25 to 4.0.",
            },
            "lang_code": {
                "type": "string",
                "description": (
                    "Optional language override: a (US English), b (UK English), "
                    "e (Spanish), f (French), h (Hindi), i (Italian), j (Japanese), "
                    "p (Portuguese), z (Chinese). Defaults to the voice's own language."
                ),
            },
            "word_timestamps": {
                "type": "boolean",
                "default": False,
                "description": "Also write <output>.words.json with per-word start/end seconds.",
            },
            "output_path": {"type": "string"},
            "output_format": {
                "type": "string",
                "enum": ["mp3", "wav"],
                "default": "mp3",
            },
        },
    }

    output_schema = {
        "type": "object",
        "properties": {
            "provider": {"type": "string"},
            "voice": {"type": "string"},
            "output": {"type": "string"},
            "format": {"type": "string"},
            "text_length": {"type": "integer"},
            "word_timestamps_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=128, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(
        max_retries=2, retryable_errors=["ConnectionError", "Timeout", "502", "503"]
    )
    idempotency_key_fields = ["text", "voice", "speed", "lang_code", "output_format"]
    side_effects = ["writes audio file to output_path", "sends text to the Kokoro server"]
    user_visible_verification = ["Listen to generated audio for natural speech quality"]

    @staticmethod
    def _base_url() -> str:
        return os.environ.get("KOKORO_TTS_URL", "").strip().rstrip("/")

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if self._base_url() else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        # Roughly 2x real time on an 8-thread CPU, ~15 chars per second of speech.
        return max(2.0, len(inputs.get("text", "")) / 15 / 2)

    def _resolve_voice(self, inputs: dict[str, Any]) -> str:
        voice = (inputs.get("voice") or "").strip()
        if not voice:
            return self.DEFAULT_VOICE
        return self.RECOMMENDED_VOICES.get(voice.lower(), voice)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if not self._base_url():
            return ToolResult(
                success=False, error="Kokoro TTS is not configured. " + self.install_instructions
            )

        start = time.time()
        try:
            result = self._synthesize(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"TTS generation failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = 0.0
        return result

    def _synthesize(self, inputs: dict[str, Any]) -> ToolResult:
        import requests

        voice = self._resolve_voice(inputs)
        fmt = "wav" if inputs.get("output_format") == "wav" else "mp3"
        want_words = bool(inputs.get("word_timestamps", False))

        output_path = Path(inputs.get("output_path") or f"tts_output.{fmt}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload: dict[str, Any] = {
            "model": "kokoro",
            "input": inputs["text"],
            "voice": voice,
            "response_format": fmt,
            "speed": float(inputs.get("speed", 1.0)),
            "stream": False,
        }
        if inputs.get("lang_code"):
            payload["lang_code"] = inputs["lang_code"]

        headers = {"Content-Type": "application/json"}
        api_key = os.environ.get("KOKORO_TTS_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint = "/dev/captioned_speech" if want_words else "/v1/audio/speech"
        if want_words:
            payload["return_timestamps"] = True

        response = requests.post(
            f"{self._base_url()}{endpoint}", headers=headers, json=payload, timeout=300
        )
        if response.status_code != 200:
            return ToolResult(
                success=False,
                error=f"Kokoro server returned {response.status_code}: {response.text[:300]}",
            )

        data: dict[str, Any] = {
            "provider": self.provider,
            "voice": voice,
            "text_length": len(inputs["text"]),
            "output": str(output_path),
            "format": fmt,
        }
        artifacts = [str(output_path)]

        if want_words:
            # Captioned endpoint returns JSON with base64 audio + word timestamps.
            import base64

            body = response.json()
            output_path.write_bytes(base64.b64decode(body["audio"]))
            words = [
                {"word": w["word"], "start": round(float(w["start_time"]), 3),
                 "end": round(float(w["end_time"]), 3)}
                for w in body.get("timestamps", [])
            ]
            words_path = output_path.with_suffix(".words.json")
            words_path.write_text(json.dumps({"words": words}, indent=2), encoding="utf-8")
            data["word_timestamps_path"] = str(words_path)
            artifacts.append(str(words_path))
        else:
            output_path.write_bytes(response.content)

        if not output_path.exists() or output_path.stat().st_size == 0:
            return ToolResult(success=False, error="Kokoro server returned no audio")

        return ToolResult(success=True, data=data, artifacts=artifacts, model="kokoro")
