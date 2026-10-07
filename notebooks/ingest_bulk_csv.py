# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest one bulk CSV source into bronze            [SCAFFOLD - Month 2 Step 6c]
# MAGIC Parameters: `source` (a name from config/sources.yml) and `extract_date`.
# MAGIC Steps: download -> unzip -> read as text -> clean names + lineage -> replace this
# MAGIC extract date's partition. ONE notebook serves every bulk source: the job passes
# MAGIC a different `source` to each task (resources/pipeline_job.yml).

# COMMAND ----------

# "# COMMAND ----------" lines split this .py file into notebook cells.
# "# MAGIC %pip ..." runs a notebook magic: here, install packages for this run.
# MAGIC %pip install -q "pydantic>=2" pyyaml

# COMMAND ----------

import os
import sys
from datetime import date

# The bundle uploads src/ next to notebooks/, so this makes `import compass` work.
sys.path.append(os.path.abspath("../src"))

from compass.config import load_settings

# Widgets = notebook parameters. The job fills them; when you run by hand,
# the default value is used.
dbutils.widgets.text("source", "qof_prevalence")
dbutils.widgets.text("extract_date", date.today().isoformat())
SOURCE = dbutils.widgets.get("source")
EXTRACT_DATE = date.fromisoformat(dbutils.widgets.get("extract_date"))
RAW_ROOT = "/Volumes/compass/bronze/raw"  # the volume you created in landing.tf

settings = load_settings()

# TODO (Step 6c), cell by cell:
#   src = settings.source(SOURCE); encoding = src.options.get("encoding", "utf-8")
#   target_dir = landing_dir(RAW_ROOT, SOURCE, EXTRACT_DATE)

# COMMAND ----------

# TODO 1. Download every file in src.download_urls with download_file().
#         If it is a .zip, unzip() only the files named in options.tables
#         (or all files when tables is empty). Collect the CSV paths.
#         No download_urls (iod_2025, landed by ADF)? Use landed_csvs(target_dir).
#         print() how many CSVs were found: it shows in the job log.

# COMMAND ----------

# TODO 2. For each CSV path:
#   - engine == "pandas":  pd.read_csv(path, dtype=str, keep_default_na=False,
#                                       encoding=encoding) -> spark.createDataFrame(pdf)
#   - engine == "pyspark": spark.read.option("header", True)
#                                    .option("encoding", encoding).csv(str(path))
#   - table = table_for_file(SOURCE, path.name, len(paths), src.options.get("tables", {}))
#   - write_bronze(to_bronze_frame(df, EXTRACT_DATE, path.name), table, EXTRACT_DATE)
#   - count the rows for this extract_date and print them (evidence).

# COMMAND ----------

# TODO 3. dbutils.notebook.exit(str(results))  # the job run page shows this text
