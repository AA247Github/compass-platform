"""The only module that needs Spark. Kept tiny.             [SCAFFOLD - Month 2 Step 6b]

WHAT YOU ARE BUILDING
    to_bronze_frame() clean column names + add lineage columns
                      (extract_date, _source_file, _ingested_at)
    write_bronze()    write to a Delta table, replacing ONLY this extract
                      date's partition, so reruns never duplicate rows

WHY IT IS SEPARATE
    CI has no Spark. Everything testable without Spark lives in bronze.py;
    this file is excluded from the coverage figure (pyproject.toml) and is
    tested by tests/test_spark_io.py only where PySpark is installed.

Guide: 03-month2-ingestion.md, Step 6b (the write-mode table explains why
overwrite + replaceWhere, and not append or plain overwrite).
"""

from __future__ import annotations

from datetime import date
from typing import Any  # Spark DataFrames are typed as Any: CI has no pyspark

from compass.bronze import clean_column_names  # noqa: F401  (use it in to_bronze_frame)


def to_bronze_frame(df: Any, extract_date: date, source_file: str) -> Any:
    """Return df with cleaned column names and three lineage columns.

    Hints (PySpark):
      from pyspark.sql import functions as F       # import INSIDE the function
      df.toDF(*new_names)                          # rename every column at once
      .withColumn("extract_date", F.lit("2026-10-06").cast("date"))
      .withColumn("_source_file", F.lit(source_file))
      .withColumn("_ingested_at", F.current_timestamp())
    """
    raise NotImplementedError("Month 2 Step 6b: to_bronze_frame")


def write_bronze(df: Any, table: str, extract_date: date) -> None:
    """Replace just this extract date's partition of a Delta table.

    df.write.format("delta").mode("overwrite")
      .option("replaceWhere", f"extract_date = '{...}'")
      .partitionBy("extract_date").saveAsTable(table)
    """
    raise NotImplementedError("Month 2 Step 6b: write_bronze")
