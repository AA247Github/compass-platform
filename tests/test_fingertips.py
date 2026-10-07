# =============================================================================
# SPECIFICATION for Month 2 Step 5b: src/compass/extractors/fingertips.py (after Step 3)
# These tests describe what your code must do. They are skipped for now.
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# Red -> green is your test-first evidence (screenshot both).
# =============================================================================
from __future__ import annotations

import pandas as pd
import pytest

from compass.config import load_settings
from compass.extractors import fingertips

pytestmark = pytest.mark.skip(reason="Month 2 Step 5b: delete this line when you start")

SAMPLE_CSV = (
    "\ufeffIndicator ID,Area Code,Parent Code,Time period,Value,Count,Denominator\n"
    "219,M85001,E54000055,2024/25,17.2,1720,10000\n"
    "241,M85001,E54000055,2024/25,9.1,720,7900\n"
)


class FakeResponse:
    status_code = 200

    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        pass


class RecordingSession:
    def __init__(self, text: str) -> None:
        self.text = text
        self.requests: list[tuple[str, dict[str, object]]] = []

    def get(self, url: str, params: dict[str, object] | None = None, **_: object) -> FakeResponse:
        self.requests.append((url, params or {}))
        return FakeResponse(self.text)


def test_request_is_built_from_config_only() -> None:
    url, params = fingertips.build_request(load_settings())
    assert url == "https://fingertips.phe.org.uk/api/all_data/csv/by_indicator_id"
    assert params == {
        "indicator_ids": "219,241",
        "child_area_type_id": 7,
        "parent_area_type_id": 221,
    }


def test_fetch_returns_text_columns_and_lineage() -> None:
    session = RecordingSession(SAMPLE_CSV)
    df = fingertips.fetch_indicators(load_settings(), session=session)  # type: ignore[arg-type]
    assert len(session.requests) == 1
    assert list(df.columns[:2]) == ["Indicator ID", "Area Code"]  # BOM stripped
    assert df["Value"].tolist() == ["17.2", "9.1"]  # kept as text in bronze
    assert set(df["_source"]) == {"fingertips_indicators"}
    assert df["_extracted_at"].str.len().gt(0).all()


def test_html_error_page_is_rejected() -> None:
    with pytest.raises(ValueError, match="HTML"):
        fingertips.parse_csv("<html><body>Service unavailable</body></html>")


def test_empty_values_stay_empty_strings_not_nan() -> None:
    df = fingertips.parse_csv("Area Code,Value\nM85001,\n")
    assert df.loc[0, "Value"] == ""
    assert not df.isna().any().any()
    assert isinstance(df, pd.DataFrame)
