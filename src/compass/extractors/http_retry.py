"""One HTTP helper shared by every extractor.            [SCAFFOLD - Month 2 Step 5a]

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
    """GET a URL, retrying timeouts, dropped connections, 429 and 5xx.

    `session` and `sleep` are parameters so tests can pass fakes: no network
    and no real waiting. This is called dependency injection.

    TODO (write this yourself, in this order):
      1. Use the session you were given, or make a new requests.Session().
      2. Loop `for attempt in range(1, attempts + 1):`
      3. Inside a try: call session.get(url, params=..., timeout=..., stream=...).
         - status NOT in RETRY_STATUS -> response.raise_for_status() (fails fast
           on 4xx), log at INFO, and return the response.
         - status IN RETRY_STATUS -> remember the reason, e.g. "HTTP 503".
      4. except (requests.Timeout, requests.ConnectionError) -> remember the
         exception's class name as the reason.
      5. On the last attempt raise RuntimeError(f"GET {url} failed after
         {attempts} attempts ({reason})").
      6. Otherwise wait = backoff * 2 ** (attempt - 1); log a WARNING that
         contains "retry {attempt}/{attempts - 1}"; then sleep(wait).
    """
    raise NotImplementedError("Month 2 Step 5a: write get_with_retry (see the guide)")
