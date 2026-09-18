# ADR 001: Configuration-driven, multi-ICB architecture

- **Status:** Accepted
- **Date:** Month 1
- **Deciders:** Apprentice, mentor, line manager

## Context

The project must serve three Integrated Care Boards (Birmingham and Solihull,
Greater Manchester, South East London) within seven months, and the scoping form
claims a fourth ICB could be added in under one working day. A naive approach
would copy the pipeline per ICB, which triples maintenance and makes that claim
false.

## Options considered

1. **One pipeline per ICB.** Simple to start; three codebases to maintain; a bug
   fix must be applied three times. Rejected.
2. **Hardcoded ICB list inside the transformation code.** Marginally better, but
   adding an ICB is still a code change, a pull request and a release. Rejected.
3. **Configuration-driven single codebase.** The ICB is a parameter read from
   `config/icbs.yml`, validated by pydantic, and passed through to dbt as a
   variable. Adding an ICB means editing YAML. **Chosen.**

## Decision

One codebase. All ICB-specific values live in `config/icbs.yml`; all source
definitions live in `config/sources.yml`. National extracts are ingested once and
filtered per ICB, rather than downloaded per ICB, which also reduces compute and
supports the net-zero requirement (K12, K7).

## Consequences

- Positive: the reusability KPI becomes measurable and testable. `tests/test_config.py`
  fails if anyone hardcodes an ICB.
- Positive: deploying ICBs two and three in month 5 is a configuration change, which
  is the evidence for the S1/S3 distinction descriptor.
- Negative: slightly more upfront design effort in month 1 before any data moves.
- Negative: config validation errors must be clear, or debugging gets harder for a
  future maintainer. Mitigated with pydantic validators and tests.
