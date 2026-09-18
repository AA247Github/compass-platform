# dbt project (built in Month 3)

This folder is a placeholder in Month 1. In Month 3 you will run
`dbt init` here and build the silver and gold models in SQL.

Planned structure:
- `models/staging/` - one model per source, cleaning and renaming only
- `models/marts/` - the gold star schema (facts and dimensions)
- `macros/` - reusable SQL such as the prevalence calculation
- `tests/` - custom singular tests, e.g. register_count <= list_size
