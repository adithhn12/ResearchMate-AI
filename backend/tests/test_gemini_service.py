import time
from types import SimpleNamespace
import pytest
from app.services.gemini_service import GeminiService


def test_gemini_bounded_retry_on_transient_503(monkeypatch):
    """Verify bounded exponential backoff (max 3 attempts) on transient 503/429/500 errors."""
    svc = GeminiService()
    svc.api_key = "test-key"
    svc.model_name = "gemini-3.5-flash-lite"

    sleep_calls = []
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))

    attempts = {"count": 0}

    class FakeModels:
        def generate_content(self, model, contents, config):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError("503 UNAVAILABLE: high demand")
            return SimpleNamespace(text="OK")

    svc.genai_client = SimpleNamespace(models=FakeModels())
    result = svc._call_model("Reply with OK", temperature=0.0)

    assert result == "OK"
    assert attempts["count"] == 3
    assert sleep_calls == [1.0, 2.0]


def test_gemini_skips_404_immediately_and_falls_back(monkeypatch):
    """Verify 404 NOT_FOUND skips retries immediately and falls back to working model."""
    svc = GeminiService()
    svc.api_key = "test-key"
    svc.model_name = "gemini-flash-lite-latest"

    sleep_calls = []
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))

    called_models = []

    class FakeModels:
        def generate_content(self, model, contents, config):
            called_models.append(model)
            if model == "gemini-flash-lite-latest":
                raise RuntimeError("404 NOT_FOUND: model not found")
            return SimpleNamespace(text="OK")

    svc.genai_client = SimpleNamespace(models=FakeModels())
    result = svc._call_model("Reply with OK", temperature=0.0)

    assert result == "OK"
    assert called_models == ["gemini-flash-lite-latest", "gemini-3.5-flash-lite"]
    assert sleep_calls == []


def test_gemini_live_minimal_generation():
    """Verify live Gemini generation succeeds with the updated default/fallback configuration."""
    svc = GeminiService()
    if not svc.api_key:
        pytest.skip("GEMINI_API_KEY not configured")
    resp = svc._call_model("Reply with OK", temperature=0.0)
    assert "OK" in resp.upper()
