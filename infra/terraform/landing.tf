resource "databricks_external_location" "bronze" {
  name            = "${local.suffix}-bronze"
  url             = "abfss://${azurerm_storage_container.layers["bronze"].name}@${azurerm_storage_account.lake.name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.lake.name
  comment         = "Bronze landing zone - managed by Terraform"
  force_destroy   = true
  depends_on      = [azurerm_role_assignment.connector_lake]
}

resource "databricks_volume" "raw" {
  name             = "raw"
  catalog_name     = databricks_catalog.compass.name
  schema_name      = databricks_schema.layers["bronze"].name
  volume_type      = "EXTERNAL"
  storage_location = "${databricks_external_location.bronze.url}raw"
  comment          = "Raw files exactly as downloaded - never edited"
}
