"""Download published files and land them, untouched.     [SCAFFOLD - Month 2 Step 6a]

WHAT YOU ARE BUILDING
    Four small functions the bulk-CSV notebook calls in order:
      landing_dir()  -> where today's files go
      download_file()-> stream one file to disk, keeping its published name
      unzip()        -> pull the named CSVs out of a zip, failing loudly if absent
      landed_csvs()  -> list CSVs already landed (e.g. by Azure Data Factory)

WHY KEEP THE RAW FILE
    It is the audit trail. If a figure is questioned in Month 7, you can show
    exactly what NHS England published on the day you extracted it.

Spec: tests/test_download.py. Guide: 03-month2-ingestion.md, Step 6a.
"""

from __future__ import annotations

import logging
import time
import zipfile  # noqa: F401  (you will use zipfile.ZipFile in unzip)
from collections.abc import Callable
from datetime import date
from pathlib import Path

import requests

from compass.extractors.http_retry import get_with_retry  # noqa: F401  (use it in download_file)

log = logging.getLogger(__name__)


def landing_dir(root: str | Path, source: str, extract_date: date) -> Path:
    """Folder for a source's files, e.g. <root>/qof_prevalence/extract_date=2026-10-06.

    The `name=value` folder style is Hive partitioning: Spark reads
    extract_date back as a column. Hint: Path(root) / source / f"...".
    `date.isoformat()` gives "2026-10-06".
    """
    raise NotImplementedError("Month 2 Step 6a: landing_dir")


def download_file(
    url: str,
    dest_dir: Path,
    *,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
    chunk_size: int = 1024 * 1024,
) -> Path:
    """Stream a file to disk, keeping its published file name. Returns the path.

    TODO:
      1. dest_dir.mkdir(parents=True, exist_ok=True)
      2. File name = last part of the URL path. Hint: urllib.parse.urlparse(url).path,
         then Path(...).name.
      3. response = get_with_retry(url, session=..., sleep=..., stream=True, timeout=120)
      4. Open the target with "wb" (write bytes) and write each chunk from
         response.iter_content(chunk_size=chunk_size). Streaming = 1 MB at a
         time, so a 400 MB file never sits in memory.
      5. Log the size (target.stat().st_size) and return the path.
    """
    raise NotImplementedError("Month 2 Step 6a: download_file")


def unzip(archive: Path, dest_dir: Path, members: list[str] | None = None) -> list[Path]:
    """Extract named files (or all, if members is None). Return their paths.

    Must RAISE FileNotFoundError naming the missing file if a requested member
    is not in the zip, so next year's renamed file fails loudly.
    Hint: `with zipfile.ZipFile(archive) as zf:` then zf.namelist(), zf.extractall().
    """
    raise NotImplementedError("Month 2 Step 6a: unzip")


def landed_csvs(dest_dir: Path) -> list[Path]:
    """CSV files already in a landing folder (put there by ADF or by hand), sorted.

    Match .csv in any case (.CSV too). If none, raise FileNotFoundError with a
    message that mentions ADF, so the person reading the job log knows why.
    """
    raise NotImplementedError("Month 2 Step 6a: landed_csvs")
