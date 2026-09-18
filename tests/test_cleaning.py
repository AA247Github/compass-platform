"""Tests for compass.cleaning.

HOW TO READ A TEST FILE
-----------------------
A test is just a function whose name starts with `test_`. pytest finds every
such function automatically and runs it. If the function finishes without
error, the test passes. If an `assert` inside it is False, the test fails and
pytest prints exactly which values did not match.

You never call these functions yourself. You run `pytest` in the terminal.

WHY THIS FILE IS LONGER THAN THE CODE IT TESTS
That is normal and healthy. The code handles the expected case; the tests pin
down all the awkward ones (blanks, capitals, impossible numbers) so that a
future change cannot quietly break them.
"""

from __future__ import annotations

from datetime import date

import pytest

# Import the functions we want to test. Because the package is installed
# (`pip install -e .`), Python finds `compass` from anywhere in the project.
from compass.cleaning import (
    is_valid_register,
    normalise_ods_code,
    parse_mixed_date,
    prevalence_percent,
    standardise_sex,
)


# ---------------------------------------------------------------------------
# PARAMETRISED TESTS
#
# `@pytest.mark.parametrize` runs the SAME test body once per row of data.
# The first argument names the variables; the second is a list of tuples, one
# tuple per run.
#
# So the test below actually runs seven separate times, and pytest reports
# seven results. This is the difference between "I tested it" and "I tested
# seven inputs including the awkward ones" - which is what an assessor is
# listening for when they ask about testing.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Male", "Male"),  # already clean
        ("male", "Male"),  # lowercase
        ("M", "Male"),  # single-letter code
        ("  f  ", "Female"),  # spaces AND lowercase
        ("FEMALE", "Female"),  # shouting
        ("", "Unknown"),  # empty string
        (None, "Unknown"),  # no value supplied at all
    ],
)
def test_standardise_sex(raw: str | None, expected: str) -> None:
    # `assert X == Y` means "X must equal Y". If it does not, the test fails
    # and pytest shows you both values side by side.
    assert standardise_sex(raw) == expected


def test_standardise_sex_rejects_unknown_value() -> None:
    """Unrecognised values must fail loudly, not be quietly binned as Unknown.

    `pytest.raises` inverts the usual logic: this test PASSES only if the code
    inside the `with` block raises the error we expect. It is how you test that
    something fails correctly.

    `match=` also checks the error message contains that text, so a different
    ValueError from an unrelated bug would not accidentally satisfy the test.
    """
    with pytest.raises(ValueError, match="Unrecognised sex value"):
        standardise_sex("nonbinary-typo-xyz")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2024-03-31", date(2024, 3, 31)),  # ISO format
        ("31/03/2024", date(2024, 3, 31)),  # UK format, same date
        ("31-03-2024", date(2024, 3, 31)),  # UK format with dashes
        ("", None),  # blank means "we do not know"
        (None, None),
    ],
)
def test_parse_mixed_date(raw: str | None, expected: date | None) -> None:
    assert parse_mixed_date(raw) == expected


def test_parse_mixed_date_rejects_nonsense() -> None:
    """A format we did not plan for must raise, not silently return None."""
    with pytest.raises(ValueError, match="Unrecognised date format"):
        parse_mixed_date("31st March 2024")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("qhl", "QHL"),  # the 2% of rows that break joins
        (" P00123 ", "P00123"),  # stray spaces from a CSV export
        ("", None),
        (None, None),
    ],
)
def test_normalise_ods_code(raw: str | None, expected: str | None) -> None:
    assert normalise_ods_code(raw) == expected


# ---------------------------------------------------------------------------
# EDGE CASES ARE THE POINT
#
# The rows below are chosen deliberately. Zero, equal values, negatives and
# None are exactly where naive code breaks, and exactly what an assessor will
# probe. Each comment explains WHY that row is in the list.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("register", "list_size", "expected"),
    [
        (1200, 10000, True),  # ordinary, sensible values
        (0, 10000, True),  # zero is valid: a real, if unusual, register
        (10000, 10000, True),  # equal is valid, if wildly implausible
        (10001, 10000, False),  # register cannot exceed list size
        (-5, 10000, False),  # negatives are impossible
        (100, 0, False),  # guards against dividing by zero later
        (None, 10000, False),  # missing data is not valid data
        (100, None, False),
    ],
)
def test_is_valid_register(register: int | None, list_size: int | None, expected: bool) -> None:
    # `is expected` rather than `== expected`: for True/False, `is` checks it
    # really is the boolean, not merely something that behaves like one.
    assert is_valid_register(register, list_size) is expected


def test_prevalence_percent_happy_path() -> None:
    """The "happy path" is the normal case where everything is well behaved."""
    assert prevalence_percent(1450, 10000) == 14.5


def test_prevalence_percent_returns_none_when_invalid() -> None:
    """None means "cannot be computed". It must never silently become 0.0.

    This is the single most important test in the file. If missing data became
    zero, a practice with a broken feed would appear as the healthiest practice
    in the ICB, and someone might act on that.
    """
    assert prevalence_percent(None, 10000) is None
    assert prevalence_percent(10001, 10000) is None
