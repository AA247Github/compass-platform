# CardioMetabolic Compass

An automated, version-controlled, configuration-driven data platform for
hypertension and type 2 diabetes prevalence, benchmarking and workforce
allocation across three NHS Integrated Care Boards, aligned to Core20PLUS5.

Level 5 Data Engineer apprenticeship, AM1 project.

## What this repository contains

| Path                  | What it is                                                  | Status        |
| --------------------- | ----------------------------------------------------------- | ------------- |
| `config/`             | `icbs.yml`, `sources.yml`: the only files an ICB change touches | Month 1-2  |
| `src/compass/`        | Package: config, cleaning, extractors (analytics, quality later) | Month 1-2 |
| `tests/`              | pytest suite; runs on every pull request                    | Month 1-2     |
| `infra/terraform/`    | Azure, Key Vault, Databricks, Unity Catalog, landing volume | Month 1-2     |
| `notebooks/`          | Databricks notebooks: ingestion (quality checks in Month 6) | Month 2       |
| `databricks.yml`, `resources/` | The Databricks job, deployed as code (bundle)      | Month 2       |
| `dbt_compass/`        | dbt: staging, intermediate, marts, serving views            | Month 3-5     |
| `app/`                | Streamlit dashboard                                         | Month 5       |
| `docs/decisions/`     | Architecture Decision Records (template: `000-template.md`) | Ongoing       |
| `.github/`            | CI workflow and pull request template                       | Ongoing       |

## Quick start (no cloud, no cost)

```bash
python -m venv .venv                       # create it INSIDE this folder
source .venv/bin/activate                  # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                                     # all pass; Month 2 specs show as skipped
```

## Adding an ICB

Edit `config/icbs.yml` (add a block or set `enabled: true`). From Month 3,
also run `python -m compass.seeds` and commit both files. No Python or SQL
changes: that is the reusability claim the project is measured against.

## Full setup instructions

See `SETUP.md`.
