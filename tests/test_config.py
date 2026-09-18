"""Tests for compass.config.

WHAT THESE TESTS ARE REALLY PROTECTING
--------------------------------------
Not the code. The PROMISE.

Your scoping form claims a fourth ICB can be added in under one working day,
through configuration only. That promise quietly dies the first time somebody
writes an ICB code directly into a Python file or a SQL query, because from
then on adding an area means changing code.

These tests are the alarm on that door. If someone hardcodes an ICB, the test
below stops matching the config file and fails in CI, on the pull request,
before it reaches main.
"""

from __future__ import annotations

import pytest

# ValidationError is the error pydantic raises when config does not match the
# shape we declared. We import it so we can assert that it happens on purpose.
from pydantic import ValidationError

from compass.config import IcbConfig, SourceConfig, load_settings


def test_real_config_files_load_and_validate() -> None:
    """The simplest possible test: do the actual config files even load?

    This is worth writing first. It catches a broken indent in the YAML, a
    missing field, or a file accidentally deleted - all of which are easy
    mistakes and confusing to debug later.
    """
    settings = load_settings()
    assert len(settings.icbs) == 3  # len() = "how many items"
    assert len(settings.sources) == 5


def test_only_enabled_icbs_are_processed() -> None:
    """Month 4 runs one ICB; month 5 flips two flags and runs three."""
    settings = load_settings()
    enabled = settings.enabled_icbs

    # This is a list comprehension inside an assert: pull the `code` out of
    # each enabled ICB, then check the resulting list is exactly ["QHL"].
    assert [icb.code for icb in enabled] == ["QHL"]


def test_lookup_by_code_is_case_insensitive() -> None:
    """Passing 'qhl' must find the same ICB as 'QHL'.

    Users, URLs and spreadsheets will all supply codes in the wrong case at
    some point. Handling it here means no caller has to remember to.
    """
    settings = load_settings()
    assert settings.icb_by_code("qhl").name == "NHS Birmingham and Solihull ICB"


def test_lookup_by_unknown_code_raises() -> None:
    """Asking for an ICB that does not exist must fail immediately.

    The alternative - returning None - lets the pipeline carry on with nothing
    and crash somewhere far away, where the real cause is hard to see.
    """
    settings = load_settings()
    with pytest.raises(KeyError):
        settings.icb_by_code("ZZZ")


def test_icb_code_is_normalised_to_uppercase() -> None:
    """The custom validator in config.py should tidy codes as they load.

    Note we build an IcbConfig directly here rather than reading a file. Small,
    focused tests like this pinpoint exactly which piece is broken.
    """
    icb = IcbConfig(code=" qop ", name="Test ICB")
    assert icb.code == "QOP"


def test_invalid_source_kind_is_rejected_at_load_time() -> None:
    """A typo must fail instantly with a clear message.

    'csvv' instead of 'bulk_csv' is the kind of mistake everyone makes at
    11pm. Without validation it would surface forty minutes into a Spark job
    as something baffling. With it, you get told immediately.
    """
    with pytest.raises(ValidationError):
        SourceConfig(name="x", kind="csvv", url="http://e.com", engine="pandas")


def test_invalid_engine_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SourceConfig(name="x", kind="bulk_csv", url="http://e.com", engine="excel")


def test_every_source_declares_a_right_sized_engine() -> None:
    """Evidence for K12/K7: compute is matched to file size deliberately.

    `all(...)` returns True only if every item satisfies the condition. Read
    it as: "for every source, its engine is one of these two".
    """
    settings = load_settings()
    assert all(s.engine in {"pyspark", "pandas"} for s in settings.sources)
