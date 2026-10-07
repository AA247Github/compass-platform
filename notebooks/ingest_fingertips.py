# Databricks notebook source
# MAGIC %md
# MAGIC # Fingertips -> bronze                              [SCAFFOLD - Month 2 Step 5b]
# MAGIC National practice-level values for the indicators in config. Used in Month 4 to
# MAGIC validate your own QOF prevalence against published figures.

# COMMAND ----------

# MAGIC %pip install -q "pydantic>=2" pyyaml

# COMMAND ----------

import logging
import os
import sys
from datetime import date

sys.path.append(os.path.abspath("../src"))
# basicConfig makes the INFO/WARNING lines from http_retry appear in the job log:
# that log line showing a retry surviving a failure is Step 5 evidence.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

dbutils.widgets.text("extract_date", date.today().isoformat())
EXTRACT_DATE = date.fromisoformat(dbutils.widgets.get("extract_date"))

# TODO (Step 5b), once fingertips.py passes its tests:
#   1. pdf = fetch_indicators(load_settings())
#   2. Save the raw response as a CSV in the raw volume (audit trail):
#        raw_dir = landing_dir("/Volumes/compass/bronze/raw", SOURCE_NAME, EXTRACT_DATE)
#        raw_dir.mkdir(parents=True, exist_ok=True); pdf.to_csv(raw_dir / "...csv", index=False)
#   3. write_bronze(to_bronze_frame(spark.createDataFrame(pdf), EXTRACT_DATE, "fingertips API"),
#                   table_name_for(SOURCE_NAME), EXTRACT_DATE)
#   4. Count rows for EXTRACT_DATE and dbutils.notebook.exit(...) with the count.
