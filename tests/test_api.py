"""Tests for FastAPI endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    # Patch orchestrator before importing app
    with patch("app.main.orchestrator") as mock_orch:
        mock_orch.start = AsyncMock()
        mock_orch.stop = AsyncMock()
        mock_orch.handle_new_call = AsyncMock(return_value="call-123")
        mock_orch.feed_audio = AsyncMock()
        mock_orch.end_call = AsyncMock()
        mock_orch._sessions = {}

        from app.main import app
        yield TestClient(app)


def test_health(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_webhook_invalid_json(test_client):
    resp = test_client.post(
        "/webhook/zadarma",
        content=b"not json",
        headers={"Content-Type": "application/json", "Sign": ""},
    )
    assert resp.status_code == 400


def test_webhook_valid_event(test_client):
    resp = test_client.post(
        "/webhook/zadarma",
        json={"event": "NOTIFY_START", "pbx_call_id": "call-1", "caller_id": "+7999"},
        headers={"Sign": ""},
    )
    assert resp.status_code == 200
