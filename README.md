# CardioMetabolic Compass

An automated, version-controlled, configuration-driven data platform for
hypertension and type 2 diabetes prevalence, benchmarking and workforce
allocation across three NHS Integrated Care Boards, aligned to Core20PLUS5.

Level 5 Data Engineer apprenticeship, AM1 project.

## What this repository contains

| Path | What it is |
|---|---|
| `src/compass/` | The Python package: config loading, cleaning, extractors |
| `tests/` | pytest suite; runs on every pull request |
| `config/` | `icbs.yml` and `sources.yml` - the only files that change per ICB |
| `infra/terraform/` | Infrastructure as code: ADLS, Key Vault, Databricks, Unity Catalog |
| `dbt_compass/` | SQL transformation models (silver and gold layers) |
| `docs/decisions/` | Architecture Decision Records |
| `.github/workflows/` | CI: lint, format, type check, tests, terraform validate |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                              # 36 tests should pass
```

## Adding a fourth ICB

Edit `config/icbs.yml`, add a block with the ODS code, name and peer codes, set
`enabled: true`, and rerun the pipeline. No Python or SQL changes are required.
This is the reusability claim the project is measured against.

## Full setup instructions

See `SETUP.md`.
