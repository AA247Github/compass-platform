"""Configuration loading and validation.

WHAT THIS FILE IS FOR
---------------------
This is the heart of the "configuration-driven" design your scoping form
promises. The idea in one sentence: anything that differs between Integrated
Care Boards lives in a YAML text file, never in the code.

Why that matters: your scoping form claims a fourth ICB could be added in under
one working day. That claim is only true if adding an ICB means editing
config/icbs.yml and nothing else. This file is what makes it true, and
tests/test_config.py is what stops anyone quietly breaking it later.

WHAT PYDANTIC DOES
------------------
Pydantic reads your YAML and checks it before the pipeline runs. Without it, a
typo like `engine: pyspork` would sail through and blow up forty minutes into a
Spark job with a confusing error. With it, you get an instant, readable message
naming the file, the field and the problem. That is worth the one extra library.
"""

from __future__ import annotations

# `Path` is Python's modern way of handling file locations. It works on Windows,
# Mac and Linux without you worrying about backslashes versus forward slashes.
from pathlib import Path

# PyYAML reads .yml files and turns them into ordinary Python dicts and lists.
import yaml

# From pydantic we need three things:
#   BaseModel       - the class we inherit from to describe a shape of data
#   Field           - lets us attach a description and rules to one field
#   field_validator - lets us write a custom rule for one field
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# WORKING OUT WHERE THE PROJECT LIVES
#
# `__file__` is a built-in variable: the path of THIS file.
# `.resolve()` turns it into a full absolute path.
# `.parents[2]` climbs up two folders:
#     this file      = <repo>/src/compass/config.py
#     parents[0]     = <repo>/src/compass
#     parents[1]     = <repo>/src
#     parents[2]     = <repo>            <- the repository root
#
# Doing it this way means the code finds the config folder no matter which
# directory you happen to run it from. Hardcoding "C:/Users/Alex/..." would
# work on your laptop and nowhere else, including in CI.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

# The `/` operator joins paths together. It is cleaner than gluing strings.
CONFIG_DIR = REPO_ROOT / "config"


# ---------------------------------------------------------------------------
# SHAPE 1: one Integrated Care Board
#
# `class IcbConfig(BaseModel)` means: define a new kind of thing called
# IcbConfig, and give it all the abilities of a pydantic BaseModel (validation,
# helpful errors, conversion to and from dicts).
# ---------------------------------------------------------------------------
class IcbConfig(BaseModel):
    """One Integrated Care Board, and everything that differs about it."""

    # Each line below declares a field: its name, its type, and its default.
    #
    # `Field(...)` with three dots means REQUIRED: the config must supply it.
    # The description is documentation that pydantic keeps with the field.
    code: str = Field(..., description="ODS code, e.g. QHL")

    # No Field() at all, just a type: also required, but with nothing extra.
    name: str

    # `= True` gives a DEFAULT. If the YAML omits `enabled`, it becomes True.
    # This is the switch that turns one ICB into three in month 5.
    enabled: bool = True

    # For a list default we must use `default_factory=list`, not `= []`.
    # Reason: a plain `= []` would create ONE list shared by every ICB, so
    # adding a peer to one ICB would add it to all of them. A classic Python
    # trap, and pydantic makes the safe version explicit.
    peer_codes: list[str] = Field(
        default_factory=list,
        description="ICB codes used as the peer comparison group for benchmarking.",
    )

    # ----- A CUSTOM RULE -----------------------------------------------
    # `@field_validator("code")` is a "decorator": it attaches the function
    # below to the `code` field, so pydantic runs it whenever a code is loaded.
    # `@classmethod` is required boilerplate for pydantic validators.
    # -------------------------------------------------------------------
    @field_validator("code")
    @classmethod
    def code_must_be_uppercase(cls, v: str) -> str:
        """Force ODS codes to uppercase as they are loaded.

        Source files are inconsistent about capitalisation. Normalising here,
        at the single point of entry, is far safer than scattering `.upper()`
        calls through the pipeline and hoping you remembered them all.
        """
        if not v.strip():
            raise ValueError("ICB code must not be empty")
        # Whatever this returns becomes the stored value.
        return v.strip().upper()


# ---------------------------------------------------------------------------
# SHAPE 2: one upstream data source
# ---------------------------------------------------------------------------
class SourceConfig(BaseModel):
    """One upstream data source, such as QOF or the workforce file."""

    name: str
    kind: str = Field(..., description="One of: api, bulk_csv, lookup")
    url: str

    # This field records a real engineering decision as data. Large national
    # files get PySpark; small lookups stay in pandas. Writing it down here
    # means the choice is visible and reviewable, and it is your evidence for
    # KSB K12 and K7 (not burning more compute than the job needs).
    engine: str = Field(
        ...,
        description="pyspark for large national files, pandas for small lookups.",
    )
    refresh: str = Field("annual", description="annual, monthly or static")

    @field_validator("kind")
    @classmethod
    def known_kind(cls, v: str) -> str:
        """Reject any `kind` we do not have code to handle."""
        # A "set" is written with curly braces. Checking membership in a set is
        # very fast and reads naturally.
        allowed = {"api", "bulk_csv", "lookup"}
        if v not in allowed:
            # `sorted()` puts the options in a predictable order, so the error
            # message looks the same every time.
            raise ValueError(f"kind must be one of {sorted(allowed)}, got {v!r}")
        return v

    @field_validator("engine")
    @classmethod
    def known_engine(cls, v: str) -> str:
        """Catch typos like 'pyspork' immediately, at load time."""
        allowed = {"pyspark", "pandas"}
        if v not in allowed:
            raise ValueError(f"engine must be one of {sorted(allowed)}, got {v!r}")
        return v


# ---------------------------------------------------------------------------
# SHAPE 3: the whole configuration
# ---------------------------------------------------------------------------
class Settings(BaseModel):
    """Everything the pipeline needs to know before it starts."""

    # `list[IcbConfig]` means "a list where every item is an IcbConfig".
    # Pydantic validates every item, so one bad ICB fails the whole load.
    icbs: list[IcbConfig]
    sources: list[SourceConfig]

    # `@property` makes this behave like a stored value rather than a function.
    # You write `settings.enabled_icbs`, not `settings.enabled_icbs()`.
    @property
    def enabled_icbs(self) -> list[IcbConfig]:
        """The ICBs this run should process.

        Month 4 runs one ICB. Month 5 flips two flags in the YAML and runs
        three, with no code change. That is the reusability claim, working.
        """
        # This is a "list comprehension": build a new list by looping over
        # `self.icbs` and keeping only the items where `icb.enabled` is True.
        # Read it as: "give me icb, for each icb in icbs, if icb is enabled".
        return [icb for icb in self.icbs if icb.enabled]

    def icb_by_code(self, code: str) -> IcbConfig:
        """Find one ICB by its code, ignoring capitals and stray spaces."""
        for icb in self.icbs:
            if icb.code == code.strip().upper():
                return icb

        # Reached only if the loop finished without finding a match.
        # Raising KeyError is better than returning None, because the caller
        # cannot then accidentally carry on with nothing and fail later
        # somewhere far away from the actual mistake.
        raise KeyError(f"No ICB configured with code {code!r}")


# ---------------------------------------------------------------------------
# THE FUNCTION EVERYTHING ELSE CALLS
# ---------------------------------------------------------------------------
def load_settings(config_dir: Path | None = None) -> Settings:
    """Read config/icbs.yml and config/sources.yml, and validate both.

    The `config_dir` argument defaults to None, meaning "use the real config
    folder". Tests can pass a different folder to try deliberately broken
    config without touching the real files. Designing for testability like
    this, from the start, is what keeps a test suite easy to write.
    """
    # `A or B` again: use the folder we were given, or fall back to the default.
    directory = config_dir or CONFIG_DIR

    # `.read_text()` opens the file, reads all of it, and closes it again.
    # `yaml.safe_load` turns that text into Python dicts and lists.
    # Always use safe_load, never plain load: plain load can execute code
    # embedded in a YAML file, which is a genuine security risk.
    icbs_raw = yaml.safe_load((directory / "icbs.yml").read_text())
    sources_raw = yaml.safe_load((directory / "sources.yml").read_text())

    # Handing the raw dicts to Settings is the moment validation happens.
    # If anything is missing, misspelled or the wrong type, this line raises a
    # clear error naming exactly which field is wrong.
    return Settings(icbs=icbs_raw["icbs"], sources=sources_raw["sources"])
