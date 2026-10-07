# =============================================================================
# SPECIFICATION for Month 2 Step 6a: src/compass/extractors/download.py
# These tests describe what your code must do. They are skipped for now.
# 1. Delete the `pytestmark = ...` line below, then run `ruff format tests`.
# 2. Run pytest: watch them FAIL (red).
# 3. Write the code until they PASS (green).  4. Add one test of your own.
# Red -> green is your test-first evidence (screenshot both).
# =============================================================================
from __future__ import annotations

import io
import zipfile
from datetime import date
from pathlib import Path

import pytest

from compass.extractors.download import download_file, landing_dir, unzip

pytestmark = pytest.mark.skip(reason="Month 2 Step 6a: delete this line when you start")


class FakeStreamResponse:
    status_code = 200

    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        pass

    def iter_content(self, chunk_size: int) -> list[bytes]:
        return [self.payload[i : i + chunk_size] for i in range(0, len(self.payload), chunk_size)]


class FakeSession:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def get(self, url: str, **_: object) -> FakeStreamResponse:
        return FakeStreamResponse(self.payload)


def make_zip(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buffer.getvalue()


def test_landing_dir_uses_hive_partition_style(tmp_path: Path) -> None:
    path = landing_dir(tmp_path, "qof_prevalence", date(2026, 10, 6))
    assert path == tmp_path / "qof_prevalence" / "extract_date=2026-10-06"


def test_download_keeps_published_name_and_bytes(tmp_path: Path) -> None:
    payload = b"x" * 3000
    saved = download_file(
        "https://files.example/QOF_2526_v2.zip",
        tmp_path,
        session=FakeSession(payload),  # type: ignore[arg-type]
        chunk_size=1024,
    )
    assert saved.name == "QOF_2526_v2.zip"
    assert saved.read_bytes() == payload


def test_unzip_extracts_only_requested_files(tmp_path: Path) -> None:
    archive = tmp_path / "q.zip"
    archive.write_bytes(make_zip({"PREVALENCE_2526.csv": "a,b\n1,2\n", "OTHER.csv": "z\n"}))
    paths = unzip(archive, tmp_path, ["PREVALENCE_2526.csv"])
    assert [p.name for p in paths] == ["PREVALENCE_2526.csv"]
    assert not (tmp_path / "OTHER.csv").exists()


def test_unzip_fails_loudly_when_a_file_is_renamed(tmp_path: Path) -> None:
    archive = tmp_path / "q.zip"
    archive.write_bytes(make_zip({"PREVALENCE_2627.csv": "a\n"}))
    with pytest.raises(FileNotFoundError, match="PREVALENCE_2526.csv"):
        unzip(archive, tmp_path, ["PREVALENCE_2526.csv"])


def test_landed_csvs_finds_files_and_fails_loudly_when_empty(tmp_path):
    from compass.extractors.download import landed_csvs

    with pytest.raises(FileNotFoundError, match="ADF"):
        landed_csvs(tmp_path)
    (tmp_path / "b.csv").write_text("x")
    (tmp_path / "a.CSV").write_text("x")
    (tmp_path / "notes.txt").write_text("x")
    assert [p.name for p in landed_csvs(tmp_path)] == ["a.CSV", "b.csv"]
