# =============================================================================
# SPECIFICATION for Month 2 Step 5a: src/compass/extractors/http_retry.py
# These tests describe what your code must do. They are skipped for now.
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# Red -> green is your test-first evidence (screenshot both).
# =============================================================================
"""Tests for get_with_retry: no network, no real waiting.

FakeSession plays back a list of planned outcomes, so each test describes
exactly what the "server" does.
"""

from __future__ import annotations

import logging

import pytest
import requests

from compass.extractors.http_retry import get_with_retry

pytestmark = pytest.mark.skip(reason="Month 2 Step 5a: delete this line when you start")


class FakeResponse:
    def __init__(self, status: int, text: str = "ok") -> None:
        self.status_code = status
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class FakeSession:
    """Returns (or raises) the next planned outcome on every get() call."""

    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        assert isinstance(outcome, int)
        return FakeResponse(outcome)


def no_sleep(_: float) -> None:
    pass


def test_success_first_time() -> None:
    session = FakeSession([200])
    response = get_with_retry("https://x", session=session, sleep=no_sleep)  # type: ignore[arg-type]
    assert response.status_code == 200
    assert session.calls == 1


def test_timeout_then_503_then_success(caplog: pytest.LogCaptureFixture) -> None:
    waits: list[float] = []
    session = FakeSession([requests.Timeout(), 503, 200])
    with caplog.at_level(logging.WARNING):
        response = get_with_retry("https://x", session=session, sleep=waits.append)  # type: ignore[arg-type]
    assert response.status_code == 200
    assert waits == [2.0, 4.0]  # exponential backoff
    assert "retry 1/3" in caplog.text  # the evidence log line for SCRUM-33


def test_gives_up_after_max_attempts() -> None:
    session = FakeSession([requests.Timeout()] * 4)
    with pytest.raises(RuntimeError, match="after 4 attempts"):
        get_with_retry("https://x", session=session, sleep=no_sleep)  # type: ignore[arg-type]


def test_404_is_not_retried() -> None:
    session = FakeSession([404])
    with pytest.raises(requests.HTTPError):
        get_with_retry("https://x", session=session, sleep=no_sleep)  # type: ignore[arg-type]
    assert session.calls == 1
