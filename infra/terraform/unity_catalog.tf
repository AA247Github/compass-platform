# =============================================================================
# UNITY CATALOG: the compass catalog and its bronze/silver/gold schemas
# =============================================================================
# WHY THIS FILE EXISTS
# Azure now switches new workspaces on for Unity Catalog automatically, with a
# metastore that has NO storage of its own. So a catalog cannot be created
# unless we tell it where its managed tables will physically live.
#
# We point it at our own data lake (azurerm_storage_account.lake in main.tf),
# which keeps every byte of project data in one account we control, in UK
# South, managed by Terraform. The chain is:
#
#   access connector (a managed identity Databricks can use)
#     -> role assignment (that identity may read/write the lake)
#       -> storage credential (Unity Catalog's name for that identity)
#         -> external location (a lake path Unity Catalog is allowed to use)
#           -> catalog (stores its managed tables under that path)
#             -> schemas (bronze, silver, gold)
#
# Terraform works out the creation order from the references below.
# =============================================================================


# -----------------------------------------------------------------------------
# ACCESS CONNECTOR: an Azure managed identity for Databricks.
# No passwords or keys anywhere: Azure issues it tokens automatically.
# The connector itself is free.
# -----------------------------------------------------------------------------
resource "azurerm_databricks_access_connector" "this" {
  name                = "dbac-${local.suffix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

# Let that identity read and write data in the lake, and nothing else.
# Least privilege: "Storage Blob Data Contributor" on this one account only,
# not Owner and not the whole subscription.
resource "azurerm_role_assignment" "connector_lake" {
  scope                = azurerm_storage_account.lake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.this.identity[0].principal_id
}

# A dedicated container for Unity Catalog's managed tables, kept separate from
# the raw bronze/silver/gold landing folders.
resource "azurerm_storage_container" "catalog" {
  name               = "catalog"
  storage_account_id = azurerm_storage_account.lake.id
}


# -----------------------------------------------------------------------------
# UNITY CATALOG OBJECTS (databricks provider)
# -----------------------------------------------------------------------------
resource "databricks_storage_credential" "lake" {
  name    = "${local.suffix}-lake"
  comment = "Managed identity for the compass data lake - managed by Terraform"

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.this.id
  }
}

resource "databricks_external_location" "catalog" {
  name            = "${local.suffix}-catalog"
  url             = "abfss://${azurerm_storage_container.catalog.name}@${azurerm_storage_account.lake.name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.lake.name
  comment         = "Managed storage for the compass catalog - managed by Terraform"

  # Allows `terraform destroy` to remove it in Step 10.
  force_destroy = true

  # Databricks checks the identity can reach the path. The role assignment
  # must exist first, so wait for it explicitly.
  depends_on = [azurerm_role_assignment.connector_lake]
}

resource "databricks_catalog" "compass" {
  name         = var.project
  comment      = "CardioMetabolic Compass - managed by Terraform"
  storage_root = databricks_external_location.catalog.url

  properties = {
    purpose = "cardiometabolic-inequalities"
  }

  # Every new catalog gets an automatic `default` schema that Terraform does
  # not manage. Without this, `terraform destroy` fails with "catalog is not
  # empty".
  force_destroy = true
}

# One schema per medallion layer, created from the same variable as the
# storage containers in main.tf - so the lake and the catalog can never drift
# apart.
resource "databricks_schema" "layers" {
  for_each     = toset(var.medallion_layers)
  catalog_name = databricks_catalog.compass.name
  name         = each.value
  comment      = "${each.value} layer of the medallion architecture"
}
