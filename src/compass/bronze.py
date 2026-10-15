"""Helpers for landing data in bronze. Pure Python, so unit tested. [SCAFFOLD - Step 6b]

WHAT YOU ARE BUILDING
    clean_column_name()  "LSOA code (2021)" -> "lsoa_code_2021"
    clean_column_names() the same for a list, making duplicates unique
    table_name_for()     "qof_prevalence"   -> "compass.bronze.qof_prevalence"
    table_for_file()     which bronze table a landed CSV goes to

WHY
    Delta tables reject spaces and brackets in column names; SQL rejects names
    starting with a digit. Cleaning once, here, means every source follows the
    same rule. The Spark write itself lives in compass.spark_io.

Spec: tests/test_bronze.py. Guide: 03-month2-ingestion.md, Step 6b.
"""

from __future__ import annotations

import re  # noqa: F401  (re.sub(r"[^0-9a-zA-Z]+", "_", text) replaces runs of symbols)


def clean_column_name(name: str) -> str:
    """Lower-case snake_case name, safe for Delta and SQL.

    Rules, in order: strip spaces and a leading "\\ufeff"; replace every run of
    non-alphanumeric characters with "_"; trim "_" from both ends; lower-case.
    Empty result -> raise ValueError. Starts with a digit -> prefix "c_".
    """
    raise NotImplementedError("Month 2 Step 6b: clean_column_name")


def clean_column_names(names: list[str]) -> list[str]:
    """Clean every name; repeated names become value, value_2, value_3.

    Hint: keep a dict counting how many times each cleaned name has been seen.
    """
    raise NotImplementedError("Month 2 Step 6b: clean_column_names")


def table_name_for(source: str) -> str:
    """Bronze table for a source, e.g. compass.bronze.qof_prevalence."""
    raise NotImplementedError("Month 2 Step 6b: table_name_for")


def table_for_file(source: str, file_name: str, n_files: int, tables: dict[str, str]) -> str:
    """Which bronze table a landed file goes to.

    1. file_name is a key in `tables` (options.tables in sources.yml) -> that table.
       This keeps next year's PREVALENCE_2627.csv in the same table.
    2. it is the only file for the source -> compass.bronze.<source>
    3. otherwise -> compass.bronze.<source>_<file name without extension>
    """
    raise NotImplementedError("Month 2 Step 6b: table_for_file")
