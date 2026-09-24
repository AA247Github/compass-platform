# =============================================================================
# OUTPUTS: values Terraform prints after a successful apply.
# =============================================================================
# Run `terraform output` at any time to see them again. They save you hunting
# through the Azure portal for names you need in later steps, and they are how
# other tools (like a deployment script) discover what was created.
# =============================================================================

output "resource_group_name" {
  description = "Resource group holding every project resource."
  value       = azurerm_resource_group.this.name
}

output "storage_account_name" {
  description = "ADLS Gen2 account holding the medallion layers."
  value       = azurerm_storage_account.lake.name
}

output "databricks_workspace_url" {
  description = "Open this URL in a browser to reach the Databricks workspace."
  value       = azurerm_databricks_workspace.this.workspace_url
}

output "key_vault_name" {
  description = "Key Vault used for pipeline secrets."
  value       = azurerm_key_vault.this.name
  sensitive   = true
}

# NOTE: if you ever output something sensitive, add `sensitive = true` so
# Terraform hides it from the console. Remember it is still stored in the state
# file, which is exactly why state lives in Azure and never in git.
