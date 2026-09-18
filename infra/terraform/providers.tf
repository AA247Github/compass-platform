# =============================================================================
# PROVIDERS: the plugins Terraform uses to talk to each platform.
# =============================================================================

terraform {
  # The minimum Terraform version this configuration needs.
  required_version = ">= 1.6"

  required_providers {
    # "azurerm" is the Azure Resource Manager provider: it creates storage,
    # Key Vault, the Databricks workspace, and so on.
    azurerm = {
      source = "hashicorp/azurerm"
      # `~> 4.0` means "any 4.x version, but not 5.0". so a major provider release cannot silently 
      #change what the infrastructure looks like overnight.
      version = "~> 4.0"
    }

    # The Databricks provider configures things INSIDE the workspace, such as
    # catalogs and schemas. Different provider, different job.
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.50"
    }
  }

  # ---------------------------------------------------------------------------
  # REMOTE STATE
  # ---------------------------------------------------------------------------
  # Terraform's "state file" is its memory of what it has already created.
  # It contains secrets, so it must NEVER be committed to git.
  #
  # Keeping state in Azure rather than on your laptop means: it is backed up,
  # it is locked so two runs cannot corrupt it, and CI can use it too.
  #
  # Create the storage account once by hand (SETUP.md step 6), then delete the
  # # from the lines below and run: terraform init -migrate-state
  # ---------------------------------------------------------------------------
  # backend "azurerm" {
  #   resource_group_name  = "rg-compass-tfstate"
  #   storage_account_name = "stcompasstfstate<yourinitials>"
  #   container_name       = "tfstate"
  #   key                  = "compass.terraform.tfstate"
  # }
}

# Configure the Azure provider. The empty `features {}` block is required by
# the provider even when you are not changing any of its behaviour.
provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Point the Databricks provider at the workspace created in main.tf.
# Because this references azurerm_databricks_workspace, Terraform knows the
# workspace must be created first. This reference is also why Unity Catalog
# resources are applied on a second pass - see the note at the end of main.tf.
provider "databricks" {
  host = azurerm_databricks_workspace.this.workspace_url
}
