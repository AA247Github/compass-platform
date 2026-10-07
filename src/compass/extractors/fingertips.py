"""Fingertips API extractor (OHID public health indicators). [SCAFFOLD - Month 2 Step 5b]

WHAT YOU ARE BUILDING
    build_request()     -> URL + query parameters, built ONLY from config
    parse_csv()         -> the API's CSV text -> a DataFrame of text columns
    fetch_indicators()  -> the two above plus get_with_retry, plus lineage columns

WHY
    Fingertips publishes the official practice prevalence. In Month 4 you check
    your own numbers against it (the 0.1 percentage-point Quality KPI).
    Fingertips is being replaced ("Find public health data"), so every
    Fingertips detail lives in config/sources.yml and this one module.

DEPENDS ON Month 2 Step 3: Settings.source() and SourceConfig.options.

Spec: tests/test_fingertips.py. Guide: 03-month2-ingestion.md, Step 5b.
"""

from __future__ import annotations

import io  # noqa: F401  (io.StringIO turns text into a "file" pandas can read)
import time
from collections.abc import Callable
from typing import Any

import pandas as pd
import requests

from compass.config import Settings

SOURCE_NAME = "fingertips_indicators"  # must match the `name:` in sources.yml


def build_request(settings: Settings) -> tuple[str, dict[str, Any]]:
    """Return (url, params) for the all-data CSV endpoint.

    url    = <source url without trailing slash> + "/all_data/csv/by_indicator_id"
    params = {"indicator_ids": "219,241", "child_area_type_id": 7, "parent_area_type_id": 221}
             with every value read from the source's `options` in sources.yml.
    Hint: ",".join(str(i) for i in [219, 241]) -> "219,241"
    """
    raise NotImplementedError("Month 2 Step 5b: build_request")


def parse_csv(text: str) -> pd.DataFrame:
    """Read the API's CSV as TEXT columns. Bronze keeps data exactly as sent.

    Rules:
      - If the text starts with "<" (after stripping spaces) it is an HTML
        error page sent with status 200: raise ValueError mentioning HTML.
      - Strip the byte-order mark "\\ufeff" from the start.
      - pd.read_csv(io.StringIO(...), dtype=str, keep_default_na=False) so
        "NA" stays "NA" and "007" stays "007".
    """
    raise NotImplementedError("Month 2 Step 5b: parse_csv")


def fetch_indicators(
    settings: Settings,
    *,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> pd.DataFrame:
    """All practice rows for the configured indicators, plus `_source` and
    `_extracted_at` (UTC ISO timestamp) lineage columns.

    Use get_with_retry(url, params, session=..., sleep=..., timeout=120).
    """
    raise NotImplementedError("Month 2 Step 5b: fetch_indicators")
