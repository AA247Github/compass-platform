# =============================================================================
# SPECIFICATION for Month 2 Step 6b: src/compass/bronze.py
# These tests describe what your code must do. They are skipped for now.
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# Red -> green is your test-first evidence (screenshot both).
# =============================================================================
from __future__ import annotations

import pytest

from compass.bronze import clean_column_name, clean_column_names, table_name_for

pytestmark = pytest.mark.skip(reason="Month 2 Step 6b: delete this line when you start")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("LSOA code (2021)", "lsoa_code_2021"),
        ("Index of Multiple Deprivation (IMD) Rank", "index_of_multiple_deprivation_imd_rank"),
        ("\ufeffPRACTICE_CODE", "practice_code"),
        ("2021 population", "c_2021_population"),
    ],
)
def test_clean_column_name(raw: str, expected: str) -> None:
    assert clean_column_name(raw) == expected


def test_duplicates_are_made_unique() -> None:
    assert clean_column_names(["Value", "value", "VALUE "]) == ["value", "value_2", "value_3"]


def test_unusable_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        clean_column_name("()")


def test_table_name() -> None:
    assert table_name_for("qof_prevalence") == "compass.bronze.qof_prevalence"


def test_table_for_file_uses_config_mapping_first() -> None:
    from compass.bronze import table_for_file

    tables = {"PREVALENCE_2526.csv": "qof_prevalence"}
    assert (
        table_for_file("qof", "PREVALENCE_2526.csv", 2, tables) == "compass.bronze.qof_prevalence"
    )
    assert table_for_file("gp_workforce", "x.csv", 1, {}) == "compass.bronze.gp_workforce"
    assert table_for_file("reg", "Quin Age.csv", 2, {}) == "compass.bronze.reg_quin_age"
