"""Reusable cleaning functions.

WHAT THIS FILE IS FOR
---------------------
Real NHS data arrives messy. The same idea is written five different ways
("Male", "male", "M", "F", ""), dates arrive in two formats in the SAME column,
and some rows are simply impossible (more people on a diabetes register than
are registered at the practice at all).

This file holds one small function per family of mess. Each function takes
something messy in and hands something clean back.

WHY SMALL FUNCTIONS
-------------------
Each function here is "pure": you give it a value, it returns a value, and it
changes nothing else in the world. Pure functions are extremely easy to test,
which is why tests/test_cleaning.py can check dozens of inputs in a fraction of
a second. That test suite is the evidence for KSB K6 (debugging, version
control and testing).
"""

# ---------------------------------------------------------------------------
# IMPORTS: pulling in code other people already wrote, so we don't rewrite it.
# ---------------------------------------------------------------------------

# A compatibility switch. It lets us write modern type hints (like `str | None`)
# even on slightly older Python versions. Put it at the top of every file and
# then forget about it.
from __future__ import annotations

# Python's built-in tools for handling dates.
# `datetime` can READ a date out of text; `date` is the clean result we keep.
from datetime import date, datetime
import 
x=1
# ---------------------------------------------------------------------------
# A LOOKUP TABLE
#
# This is a "dictionary" (Python calls it a dict). A dict stores pairs:
# a KEY on the left, a VALUE on the right. Here the key is the messy version
# and the value is the clean version we want.
#
# The leading underscore in `_SEX_LOOKUP` is a convention meaning "internal to
# this file". The CAPITALS are a convention meaning "a constant: set once,
# never changed while the program runs".
# ---------------------------------------------------------------------------
_SEX_LOOKUP = {
    "male": "Male",  # key "male" -> value "Male"
    "m": "Male",  # key "m"    -> value "Male"
    "female": "Female",
    "f": "Female",
}

# A "tuple" is an ordered list that cannot be changed after it is created.
# Round brackets make a tuple; square brackets would make a list.
# These are the date formats we know how to read:
#   %Y = 4-digit year, %m = 2-digit month, %d = 2-digit day
# So "%Y-%m-%d" reads "2024-03-31", and "%d/%m/%Y" reads "31/03/2024".
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


# ---------------------------------------------------------------------------
# FUNCTION 1: standardise_sex
#
# Reading the function signature, piece by piece:
#   def                  -> "I am defining a function"
#   standardise_sex      -> the function's name
#   (value: str | None)  -> ONE input called `value`, which is either text (str)
#                           or nothing at all (None)
#   -> str               -> it always hands back text
#
# The type hints do not change how the code runs. They are documentation that
# VS Code and mypy can check for you automatically.
# ---------------------------------------------------------------------------
def standardise_sex(value: str | None) -> str:
    """Turn any spelling of sex into 'Male', 'Female' or 'Unknown'.

    This text between triple quotes is a "docstring". Hover over the function
    name anywhere in VS Code and this is what pops up.

    The `>>>` lines below are real, runnable examples:

    >>> standardise_sex("F")
    'Female'
    >>> standardise_sex("  female ")
    'Female'
    >>> standardise_sex("")
    'Unknown'
    """
    # `is None` checks for the complete absence of a value. That is different
    # from an empty string "": None means "no data was supplied at all".
    if value is None:
        return "Unknown"  # `return` = hand this answer back and stop here

    # `.strip()` removes spaces from both ends: "  female " -> "female".
    # `.lower()` makes everything lowercase: "FEMALE" -> "female".
    # Chaining them means we need only ONE entry per spelling in our lookup,
    # instead of an entry for every combination of capitals and spaces.
    cleaned = value.strip().lower()

    # An empty string is "falsy" in Python, so `not cleaned` is True when the
    # string is empty. This reads better than `if cleaned == ""`.
    if not cleaned:
        return "Unknown"

    # `in` asks: is this key present in the dictionary?
    # If we do NOT recognise the value we raise an error rather than guess.
    # Deliberate choice: silently turning unknown values into "Unknown" would
    # hide data problems, and hidden problems end up on dashboards.
    if cleaned not in _SEX_LOOKUP:
        # The `f` before the quotes makes this an "f-string", which drops a
        # variable into text using {curly braces}.
        # `!r` shows the value with its quote marks, so an invisible trailing
        # space is actually visible in the error message.
        raise ValueError(f"Unrecognised sex value: {value!r}")

    # Square brackets look up a key in the dictionary and return its value.
    return _SEX_LOOKUP[cleaned]


# ---------------------------------------------------------------------------
# FUNCTION 2: parse_mixed_date
# ---------------------------------------------------------------------------
def parse_mixed_date(value: str | None) -> date | None:
    """Read a date that might be written in several different formats.

    Returns a real date object, or None if the input was blank.

    WHY RETURN None FOR BLANKS BUT RAISE FOR RUBBISH?
    A blank might be legitimately missing data, and the caller should decide
    whether that is acceptable. Text like "31st March 2024" is a format we did
    not expect, and quietly ignoring it would lose real data.
    """
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    # A `for` loop repeats the indented block once for each item in the tuple.
    # Here we try each known format in turn until one works.
    for fmt in _DATE_FORMATS:
        # `try` means "attempt this, and if it fails do not crash".
        try:
            # strptime = "string parse time". It reads text using the given
            # format and returns a datetime. `.date()` drops the time part,
            # which we do not need.
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            # This format did not match. `continue` = go to the next loop item.
            continue

    # We only reach this line if the loop finished without ever returning,
    # meaning NONE of our known formats matched.
    raise ValueError(f"Unrecognised date format: {value!r}")


# ---------------------------------------------------------------------------
# FUNCTION 3: normalise_ods_code
# ---------------------------------------------------------------------------
def normalise_ods_code(value: str | None) -> str | None:
    """Tidy an NHS practice or ICB code, e.g. ' qhl ' becomes 'QHL'.

    WHY THIS MATTERS MORE THAN IT LOOKS
    About 2% of rows in real extracts carry lowercase codes. A computer treats
    "QHL" and "qhl" as two completely different things, so a join silently
    drops those rows and a group-by silently splits one ICB into two. Nothing
    errors. The numbers are just quietly wrong. Fixing this once, at the
    boundary, prevents that whole class of bug.
    """
    if value is None:
        return None

    cleaned = value.strip().upper()

    # `A or B` returns A if A is truthy, otherwise B.
    # So an empty string (falsy) becomes None, and anything else stays as-is.
    # This keeps "no value" represented one single way across the pipeline.
    return cleaned or None


# ---------------------------------------------------------------------------
# FUNCTION 4: is_valid_register
#
# This returns True or False. Functions like this are called "predicates",
# and naming them `is_...` is a widely used convention.
# ---------------------------------------------------------------------------
def is_valid_register(register_count: int | None, list_size: int | None) -> bool:
    """Check whether a condition register count is actually possible.

    A practice cannot have more people on its hypertension register than it has
    registered patients in total. Real extracts do contain such rows, because
    of coding errors upstream.

    The same rule is written again later as a dbt test in SQL. That is
    deliberate, not pointless duplication: Python checks single rows as data
    arrives, SQL checks the whole table once it is in the warehouse. Two
    layers, described in the scoping form under KSB K4 and S26.
    """
    # Guard clause 1: we cannot judge validity without both numbers.
    if register_count is None or list_size is None:
        return False

    # Guard clause 2: a negative register is impossible, and a list size of
    # zero or less would make the division below meaningless.
    if register_count < 0 or list_size <= 0:
        return False

    # `<=` produces True or False directly, so we return the comparison itself.
    # Writing `if x <= y: return True else: return False` is more typing for
    # exactly the same result.
    return register_count <= list_size


# ---------------------------------------------------------------------------
# FUNCTION 5: prevalence_percent
# ---------------------------------------------------------------------------
def prevalence_percent(register_count: int | None, list_size: int | None) -> float | None:
    """Work out what percentage of a practice's patients have a condition.

    Example: 1450 people on the hypertension register out of a list of 10000
    gives 14.5 percent.

    THE MOST IMPORTANT LINE IN THIS FILE IS THE `return None`.
    When we cannot calculate prevalence we return None ("we do not know"),
    NOT 0.0. Zero is a real clinical value meaning "nobody has this condition".
    If missing data silently became zero, a practice with a broken data feed
    would appear on your dashboard as the healthiest practice in the ICB.
    """
    # Reuse the function above rather than rewriting the rules. If the validity
    # rules ever change, they change in exactly one place.
    if not is_valid_register(register_count, list_size):
        return None

    # `assert` tells type checkers like mypy that by this point we definitely
    # have real numbers, because is_valid_register already ruled out None.
    # It is a note to the tooling, not a runtime safety check.
    assert register_count is not None and list_size is not None

    # `round(x, 4)` keeps four decimal places. We keep more precision than we
    # display, because rounding early and then aggregating introduces errors.
    return round(register_count / list_size * 100, 4)
