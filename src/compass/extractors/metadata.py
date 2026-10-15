"""Indicator metadata -> data dictionary.          [SCAFFOLD - Month 2 Step 5c, adaptation A3]

WHAT YOU ARE BUILDING
    Fingertips also publishes METADATA about each indicator: its name,
    definition, caveats, method. It arrives as nested JSON (semi-structured)
    and several values are free text containing HTML (unstructured). You will
    turn it into a tidy table: one row per indicator x text field.

WHY (this closes a gap)
    Your scoping form promises "unstructured indicator definitions ... turned
    into a data dictionary" (K19, S16). Nothing in the reference build does
    that. This module is the evidence: a small extraction algorithm you
    designed, tested, and can evaluate.

TRANSFERABLE SKILL
    Flattening nested JSON and cleaning HTML text appear in almost every API
    integration you will ever build (CRMs, survey tools, web pages).

Spec: tests/test_metadata.py. Guide: 03-month2-ingestion.md, Step 5c.
Answer key (after you have tried): SETUP/Distinction_Guide/answer-keys/metadata.py
"""

from __future__ import annotations

import html  # noqa: F401  (html.unescape turns &amp; into &)
import re  # noqa: F401  (re.compile(r"<[^>]+>") matches an HTML tag)
import time
from collections.abc import Callable
from typing import Any

import pandas as pd
import requests

from compass.config import Settings

SOURCE_NAME = "fingertips_indicators"  # reuse the same config block as fingertips.py


def build_metadata_request(settings: Settings) -> tuple[str, dict[str, Any]]:
    """URL <api>/indicator_metadata/by_indicator_id, params {"indicator_ids": "219,241"}."""
    raise NotImplementedError("Month 2 Step 5c: build_metadata_request")


def fetch_metadata(
    settings: Settings,
    *,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """GET with get_with_retry, return response.json(). Raise ValueError if it is not a dict."""
    raise NotImplementedError("Month 2 Step 5c: fetch_metadata")


def flatten_json(obj: Any, prefix: str = "") -> dict[str, Any]:
    """{"a": {"b": 1, "c": [2, 3]}} -> {"a.b": 1, "a.c[0]": 2, "a.c[1]": 3}

    This is RECURSION: the function calls itself on each nested dict or list,
    and stops when it reaches a plain value (a "leaf").
    """
    raise NotImplementedError("Month 2 Step 5c: flatten_json")


def html_to_text(raw: str | None) -> str:
    """Free text with HTML -> clean plain text.

    Rules: None or "" -> "". <br>, </p>, </li>, </div> end a line; every other
    tag becomes a space; decode entities (&amp; -> &, &nbsp; -> space); collapse
    repeated spaces; strip each line; drop empty lines; join with "\\n".
    """
    raise NotImplementedError("Month 2 Step 5c: html_to_text")


def metadata_to_dictionary(payload: dict[str, Any], min_words: int = 1) -> pd.DataFrame:
    """One row per indicator x STRING field: indicator_id (int), field, text, n_words.

    Skip non-string values and text with fewer than min_words words.
    Sort by indicator_id, field.
    """
    raise NotImplementedError("Month 2 Step 5c: metadata_to_dictionary")
