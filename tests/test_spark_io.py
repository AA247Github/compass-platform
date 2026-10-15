# =============================================================================
# SPECIFICATION for Month 2 Step 6b: src/compass/spark_io.py (runs only where PySpark is installed)
# These tests describe what your code must do. They are skipped for now.
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# Red -> green is your test-first evidence (screenshot both).
# =============================================================================
"""Runs only where PySpark is installed (Databricks, or a local install).

CI skips it: installing Spark there would add minutes to every run.
"""

from __future__ import annotations

from datetime import date

import pytest

pyspark = pytest.importorskip("pyspark")

pytestmark = pytest.mark.skip(reason="Month 2 Step 6b: delete this line when you start")


@pytest.fixture(scope="module")
def spark():  # type: ignore[no-untyped-def]
    from pyspark.sql import SparkSession

    session = SparkSession.builder.master("local[1]").appName("tests").getOrCreate()
    yield session
    session.stop()


def test_to_bronze_frame_cleans_names_and_adds_lineage(spark) -> None:  # type: ignore[no-untyped-def]
    from compass.spark_io import to_bronze_frame

    df = spark.createDataFrame([("E01000001", "5")], ["LSOA code (2021)", "IMD Decile"])
    out = to_bronze_frame(df, date(2026, 10, 6), "File_7.csv")
    assert out.columns == [
        "lsoa_code_2021",
        "imd_decile",
        "extract_date",
        "_source_file",
        "_ingested_at",
    ]
    row = out.collect()[0]
    assert str(row["extract_date"]) == "2026-10-06"
    assert row["_source_file"] == "File_7.csv"
