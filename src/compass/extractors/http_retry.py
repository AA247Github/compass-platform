"""One HTTP helper shared by every extractor.

WHAT YOU ARE BUILDING
    get_with_retry(): fetch a URL, and if the failure is temporary (a timeout,
    a dropped connection, HTTP 429 "slow down", or a 5xx "server problem"),
    wait and try again, waiting twice as long each time (2s, 4s, 8s).

WHY ONE HELPER
    Timeouts, retries and logging are decided once, here. Every extractor calls
    get_with_retry(); none calls requests.get() directly.

HOW YOU KNOW IT WORKS
    tests/test_http_retry.py is the specification. Delete its `pytestmark`
    line, run `pytest tests/test_http_retry.py`, watch it fail, then make it pass.

Guide: SETUP/Distinction_Guide/03-month2-ingestion.md, Step 5a.
Answer key (look AFTER you have tried): SETUP/Compass_Build_Guide/reference/.
"""

# Lets type hints mention classes defined later and use `X | None` on 3.10.
from __future__ import annotations

import logging
import time
from collections.abc import Callable  # Callable[[float], None] = "a function taking a float"
from typing import Any

import requests

# One logger per module, named after it ("compass.extractors.http_retry"),
# so log lines say where they came from.
log = logging.getLogger(__name__)

# Worth retrying: rate limited (429) or a server-side problem (5xx).
# A 404 or 400 means OUR request is wrong, and retrying will not fix it.
RETRY_STATUS = {429, 500, 502, 503, 504}


def get_with_retry(
    url: str,
    params: dict[str, Any] | None = None,
    *,  # everything after * must be passed by name: get_with_retry(u, timeout=60)
    session: requests.Session | None = None,
    attempts: int = 4,
    backoff: float = 2.0,
    timeout: float = 30,
    stream: bool = False,
    sleep: Callable[[float], None] = time.sleep,
) -> requests.Response:
    """GET a URL, retrying timeouts, dropped connections, 429 and 5xx."""
    session = session or requests.Session()
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, params=params, timeout=timeout, stream=stream)

            if response.status_code not in RETRY_STATUS:
                response.raise_for_status()  # raises HTTPError if status is 4xx or 5xx
                log.info("GET %s -> %s", url, response.status_code)
                return response

            reason = f"HTTP {response.status_code}"

        except (requests.Timeout, requests.ConnectionError) as exc:
            reason = type(exc).__name__

        # Back at loop level (lined up with `try`): runs after try OR except.
        if attempt == attempts:
            raise RuntimeError(f"GET {url} failed after {attempts} attempts ({reason})")

        wait = backoff * 2 ** (attempt - 1)
        log.warning(
            "GET %s failed (%s), retry %d/%d in %.0fs", url, reason, attempt, attempts - 1, wait
        )
        sleep(wait)  # the injected `sleep`, so tests don't really wait

    raise AssertionError("unreachable")  # for mypy: the loop always returns or raises first
