# =============================================================================
# SPECIFICATION for Month 2 Step 5c (adaptation A3): src/compass/extractors/metadata.py
# Semi-structured JSON + unstructured HTML text -> a tidy data dictionary (K19/S16).
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# =============================================================================
"""The sample below mimics the SHAPE of the Fingertips metadata response.

Before you trust it, open the real endpoint in a browser (guide Step 4) and
adjust SAMPLE so it matches what Fingertips actually returns. Keeping a saved
real response as a test fixture is even better.
"""

from __future__ import annotations

import pytest

from compass.config import load_settings
from compass.extractors import metadata

pytestmark = pytest.mark.skip(reason="Month 2 Step 5c: delete this line when you start")

SAMPLE = {
    "219": {
        "IID": 219,
        "Descriptive": {
            "Name": "Hypertension: QOF prevalence (all ages)",
            "Definition": "<p>The percentage of patients with established "
            "hypertension, as recorded on practice disease registers.</p>",
            "Caveats": "<p>Registers count <b>diagnosed</b> patients only&nbsp;"
            "&amp; depend on case-finding.</p><p>Not age-standardised.</p>",
            "Blank": "",
        },
        "Unit": {"Label": "%", "Value": 100},
    },
    "241": {"IID": 241, "Descriptive": {"Name": "Diabetes: QOF prevalence (17+)"}},
}


def test_flatten_json_turns_nesting_into_dotted_paths() -> None:
    flat = metadata.flatten_json({"a": {"b": 1, "c": [2, 3]}})
    assert flat == {"a.b": 1, "a.c[0]": 2, "a.c[1]": 3}


def test_html_to_text_strips_tags_and_decodes_entities() -> None:
    text = metadata.html_to_text(SAMPLE["219"]["Descriptive"]["Caveats"])  # type: ignore[index]
    assert "<" not in text and "&amp;" not in text and "&nbsp;" not in text
    assert text == (
        "Registers count diagnosed patients only & depend on case-finding.\nNot age-standardised."
    )


def test_html_to_text_handles_empty_and_none() -> None:
    assert metadata.html_to_text("") == ""
    assert metadata.html_to_text(None) == ""


def test_dictionary_has_one_row_per_indicator_and_text_field() -> None:
    df = metadata.metadata_to_dictionary(SAMPLE)
    assert list(df.columns) == ["indicator_id", "field", "text", "n_words"]
    assert set(df["indicator_id"]) == {219, 241}
    assert "Descriptive.Definition" in set(df["field"])
    assert "Unit.Value" not in set(df["field"])  # numbers are not dictionary text
    assert "Descriptive.Blank" not in set(df["field"])  # empty text is dropped
    assert not df["text"].str.contains("<").any()


def test_metadata_request_is_built_from_config() -> None:
    url, params = metadata.build_metadata_request(load_settings())
    assert url == "https://fingertips.phe.org.uk/api/indicator_metadata/by_indicator_id"
    assert params == {"indicator_ids": "219,241"}


class FakeJsonResponse:
    status_code = 200

    def __init__(self, payload: object) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def get(self, url: str, **_: object) -> FakeJsonResponse:
        return FakeJsonResponse(self.payload)


def test_fetch_returns_the_json_object() -> None:
    session = FakeSession(SAMPLE)
    assert metadata.fetch_metadata(load_settings(), session=session) == SAMPLE  # type: ignore[arg-type]


def test_fetch_rejects_json_that_is_not_an_object() -> None:
    with pytest.raises(ValueError):
        metadata.fetch_metadata(load_settings(), session=FakeSession([1, 2]))  # type: ignore[arg-type]
