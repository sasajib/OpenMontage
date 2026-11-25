"""Focused tests for the self-hosted Kokoro-FastAPI TTS tool (network mocked)."""

import base64
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.base_tool import BaseTool, ToolRuntime, ToolStatus, ToolTier
from tools.tool_registry import ToolRegistry
from tools.audio.kokoro_tts import KokoroTTS
from tools.audio.tts_selector import TTSSelector


FAKE_WAV = b"RIFF" + b"\x00" * 64


class _FakeResponse:
    def __init__(self, status_code=200, content=b"", body=None, text=""):
        self.status_code, self.content, self._body, self.text = status_code, content, body, text

    def json(self):
        return self._body


@pytest.fixture
def kokoro_env(monkeypatch):
    monkeypatch.setenv("KOKORO_TTS_URL", "http://kokoro.test:8880/")
    monkeypatch.delenv("KOKORO_TTS_API_KEY", raising=False)


@pytest.fixture
def fake_post(monkeypatch):
    calls = []

    def post(url, headers=None, json=None, timeout=None):
        calls.append({"url": url, "headers": headers, "json": json})
        if url.endswith("/dev/captioned_speech"):
            return _FakeResponse(body={
                "audio": base64.b64encode(FAKE_WAV).decode(),
                "audio_format": "wav",
                "timestamps": [{"word": "Hello", "start_time": 0.0245, "end_time": 0.312}],
            })
        return _FakeResponse(content=FAKE_WAV)

    import requests
    monkeypatch.setattr(requests, "post", post)
    return calls


class TestContract:
    def test_identity(self):
        t = KokoroTTS()
        assert issubclass(KokoroTTS, BaseTool)
        assert t.name == "kokoro_tts"
        assert t.capability == "tts"
        assert t.provider == "kokoro"
        assert t.runtime == ToolRuntime.API
        assert t.tier == ToolTier.VOICE
        assert t.estimate_cost({"text": "x" * 10_000}) == 0.0

    def test_discoverable(self):
        reg = ToolRegistry()
        reg.discover("tools")
        assert "kokoro_tts" in [t.name for t in reg.get_by_capability("tts")]

    def test_status_follows_env(self, monkeypatch):
        monkeypatch.delenv("KOKORO_TTS_URL", raising=False)
        assert KokoroTTS().get_status() == ToolStatus.UNAVAILABLE
        monkeypatch.setenv("KOKORO_TTS_URL", "http://x:8880")
        assert KokoroTTS().get_status() == ToolStatus.AVAILABLE


class TestExecute:
    def test_plain_speech(self, kokoro_env, fake_post, tmp_path):
        out = tmp_path / "line.mp3"
        res = KokoroTTS().execute({"text": "Hello", "voice": "adam", "speed": 1.1, "output_path": str(out)})
        assert res.success, res.error
        assert out.read_bytes() == FAKE_WAV
        assert res.data["voice"] == "am_adam"
        call = fake_post[-1]
        assert call["url"] == "http://kokoro.test:8880/v1/audio/speech"
        assert call["json"]["voice"] == "am_adam"
        assert call["json"]["speed"] == 1.1
        assert call["json"]["stream"] is False
        assert "Authorization" not in call["headers"]

    def test_blend_passthrough_and_api_key(self, kokoro_env, fake_post, tmp_path, monkeypatch):
        monkeypatch.setenv("KOKORO_TTS_API_KEY", "secret")
        res = KokoroTTS().execute({"text": "x", "voice": "af_bella(2)+af_sky(1)", "output_path": str(tmp_path / "a.mp3")})
        assert res.success
        assert fake_post[-1]["json"]["voice"] == "af_bella(2)+af_sky(1)"
        assert fake_post[-1]["headers"]["Authorization"] == "Bearer secret"

    def test_word_timestamps(self, kokoro_env, fake_post, tmp_path):
        out = tmp_path / "line.wav"
        res = KokoroTTS().execute({"text": "Hello", "word_timestamps": True, "output_format": "wav", "output_path": str(out)})
        assert res.success, res.error
        assert fake_post[-1]["url"].endswith("/dev/captioned_speech")
        assert out.read_bytes() == FAKE_WAV
        words = json.loads(Path(res.data["word_timestamps_path"]).read_text())["words"]
        assert words == [{"word": "Hello", "start": 0.025, "end": 0.312}]

    def test_server_error(self, kokoro_env, tmp_path, monkeypatch):
        import requests
        monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(status_code=503, text="busy"))
        res = KokoroTTS().execute({"text": "x", "output_path": str(tmp_path / "a.mp3")})
        assert not res.success and "503" in res.error

    def test_unconfigured(self, monkeypatch, tmp_path):
        monkeypatch.delenv("KOKORO_TTS_URL", raising=False)
        res = KokoroTTS().execute({"text": "x", "output_path": str(tmp_path / "a.mp3")})
        assert not res.success and "KOKORO_TTS_URL" in res.error


class TestSelectorAdaptation:
    def test_maps_capability_controls(self):
        adapted = TTSSelector._adapt_inputs(
            KokoroTTS(),
            {"text": "x", "voice_id": "bella", "speaking_rate": 0.9, "style": 0.4, "output_format": "wav_48000"},
        )
        assert adapted["voice"] == "bella"
        assert adapted["speed"] == 0.9
        assert "style" not in adapted
        assert adapted["output_format"] == "wav"
