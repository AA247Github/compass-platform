# ADR 002: Cloud and platform choice

- **Status:** Accepted
- **Date:** Month 1 (September 2026)
- **Deciders:** Apprentice; to be reviewed with mentor and line manager

## Context

The platform must ingest five national open NHS datasets, transform them
through bronze, silver and gold layers, govern access by ICB, and serve
Power BI and Streamlit. It must be buildable and destroyable from code, run
on a personal subscription with a small budget, and keep data in the UK.

## Decision

Azure Databricks (Premium tier, Unity Catalog) on Azure, in UK South,
provisioned with Terraform.

## Why Azure

- IQVIA and the NHS already run on Microsoft: Entra ID sign-in, Microsoft 365
  and Power BI. Azure fits that estate with no extra identity work.
- Azure Databricks is a first-party Azure service: billed through the
  subscription and signed in with Entra ID.
- Power BI connects natively to Databricks SQL warehouses.

**Rejected: AWS (EMR) and Google Cloud (Dataproc).** Both run Spark well, but
neither fits IQVIA's or the NHS's Microsoft estate: Power BI and Entra ID would
need cross-cloud identity and networking. Not priced in detail; costs for this
workload are of the same order.

## Why Databricks over Synapse

| Criterion            | Azure Databricks       | Azure Synapse                       |
| -------------------- | ---------------------- | ----------------------------------- |
| Product direction    | Actively developed     | Maintained; new work goes to Fabric |
| Governance           | Unity Catalog built in | Needs Microsoft Purview             |
| Table format         | Delta Lake native      | Delta via Spark pools               |
| dbt adapter          | Vendor-maintained      | Community-maintained                |
| Terraform coverage   | Workspace and catalog  | Workspace only                      |
| Serverless compute   | Jobs, notebooks, SQL   | SQL only                            |
| Runs on other clouds | Yes (AWS, GCP)         | No                                  |

- Synapse is maintained, but Microsoft directs new analytics work to Fabric,
  and some Synapse components have already been retired.
- Synapse serverless covers SQL only; its Spark pools are provisioned clusters.
- Synapse is slightly cheaper for this workload (see costs below). Databricks
  is chosen for governance, dbt support, serverless compute and product
  direction, not price.

**Rejected: Microsoft Fabric.** It fits Power BI well, but it prices by
capacity (F2 costs £0.318/hour, about £232/month if left running), ties
the platform to Microsoft only, and is a less established target for this
project's Terraform and dbt tooling. Kept as the documented alternative if
IQVIA standardises on Fabric.

## Why UK South

- Keeps all data in the UK, which NHS data-handling guidance expects, even for
  open aggregated data.
- Has availability zones; UK West has none.
- Supports every Databricks serverless feature, including default storage and
  Databricks Apps (a possible Streamlit host). UK West lacks both.
- Same prices as UK West for this workload, with the lowest latency from the UK.

**Rejected: UK West** (reasons above). **Rejected: EU regions**, which would
move data outside the UK for no benefit.

## Provisioning tool

| Criterion                    | Portal  | CLI script   | Bicep + SQL | Terraform |
| ---------------------------- | ------- | ------------ | ----------- | --------- |
| Learning curve               | Lowest  | Low          | Medium      | Medium    |
| Repeatable, identical builds | No      | Mostly       | Yes         | Yes       |
| Safe to re-run               | n/a     | Needs checks | Yes         | Yes       |
| Azure + Databricks, one tool | By hand | Partly       | No          | Yes       |
| Preview before applying      | No      | No           | Yes         | Yes       |
| One-command teardown         | No      | Write own    | Partial     | Yes       |
| Reviewed in PRs and CI       | No      | Partly       | Yes         | Yes       |
| State file to manage         | No      | No           | No          | Yes       |

- Bicep + SQL: Bicep builds the Azure resources; SQL or Asset Bundles create
  the Databricks objects. Teardown removes the resource group only.
- Terraform is the only option that builds and destroys Azure and Databricks
  together with one command. That makes the destroy-between-sessions cost
  control practical.

## Estimated monthly cost

UK South retail prices in GBP, September 2026. Assumes the workspace is
destroyed between sessions (about 40 hours a month running) and holds under
20 GB of data. Compute figures are estimates, to be replaced with Cost
Management actuals at the end of Month 2.

| Item                      | Assumption               | £/month    |
| ------------------------- | ------------------------ | ---------- |
| Data lake + state storage | Under 20 GB, hot LRS     | < 1        |
| Key Vault                 | A few hundred operations | < 0.10     |
| NAT gateway               | 40 h at ~0.035/h         | ~1.40      |
| Serverless jobs           | ~40 DBU at 0.3681        | ~15        |
| Serverless notebooks      | ~15 DBU at 0.7362        | ~11        |
| Serverless SQL (2X-Small) | 20 DBU at 0.6994         | ~14        |
| **Total**                 |                          | **~40-45** |

### Alternatives, same workload

| Option                                          | £/month (40 h use) | £/month (always on) |
| ----------------------------------------------- | ------------------ | ------------------- |
| Databricks, destroyed between sessions (chosen) | ~40-45             | n/a                 |
| Databricks, left running                        | n/a                | ~65-70              |
| Synapse serverless SQL + Spark pool             | ~30                | n/a (pools pause)   |
| Synapse dedicated SQL pool DW100c               | ~25 (20 h)         | ~918                |
| Microsoft Fabric F2                             | ~13                | ~232                |
| AWS EMR / Google Dataproc                       | Not priced         | Not priced          |

How the alternatives were costed:

- **Databricks, left running:** the NAT gateway bills around the clock
  (~£26/month) on top of the chosen setup.
- **Synapse Spark pool:** minimum 3 nodes of 4 vCores at £0.116 per
  vCore-hour = £1.39/hour, for 20 hours. Serverless SQL at £4.735 per TB
  scanned adds under £1.
- **Synapse dedicated pool:** £1.2576/hour.
- **Fabric F2:** 2 capacity units at £0.1591 per CU-hour, paused when idle.

## Consequences

- Positive: one tool (Terraform) builds and destroys the whole platform, so
  cost stays low by destroying it between sessions.
- Positive: Unity Catalog provides the governance the scoping form requires.
- Negative: the starter SQL warehouse is created at Small size (12 DBU/h, about
  £8.39/hour). It must be resized to 2X-Small before use.
- Negative: the £10 budget alert set in Month 1 will be exceeded once
  ingestion starts. Raise it to £50, keeping the 50% and 90% alerts.
- Negative: the platform depends on Databricks pricing; Fabric remains the
  documented fallback.

## Sources

- Azure Retail Prices API, UK South, GBP (Azure Databricks, Azure Synapse
  Analytics, Fabric Capacity), queried September 2026:
  <https://prices.azure.com/api/retail/prices>
- Azure Databricks feature availability by region:
  <https://learn.microsoft.com/en-us/azure/databricks/resources/feature-region-support>
- Future of Azure Synapse Analytics, Microsoft Q&A:
  <https://learn.microsoft.com/en-us/answers/questions/5828755/do-we-have-any-indication-that-azure-synapse-analy>
- NAT gateway: published list price of about USD 0.045/hour, converted. Confirm
  in the Azure pricing calculator.
