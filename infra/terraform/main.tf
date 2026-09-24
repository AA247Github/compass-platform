# =============================================================================
# WHAT TERRAFORM IS DOING HERE
# =============================================================================
# This file describes the cloud resources you want to exist. Terraform reads it,
# compares it with what already exists in Azure, and makes reality match.
#
# The big idea: you never click in the Azure portal to create things. You edit
# this file, run `terraform apply`, and the change is recorded in git alongside
# your code. That is "Infrastructure as Code" (KSB K13, S4).
#
# HOW TO READ TERRAFORM
#   resource "azurerm_storage_account" "lake" { ... }
#            ^ the TYPE of thing         ^ YOUR name for it, used to refer
#                                          to it elsewhere in this file
#
# Reference other resources with TYPE.NAME.ATTRIBUTE, for example
# `azurerm_resource_group.this.name`. Terraform reads those references and
# works out the correct creation order by itself - you never specify it.
# =============================================================================


# -----------------------------------------------------------------------------
# LOCALS: values calculated once and reused, so a change happens in one place.
# -----------------------------------------------------------------------------
locals {
  # Produces "compass-dev". Used to build every resource name below, so all
  # your resources are named consistently and are obviously related.
  suffix = "${var.project}-${var.environment}"

  # Tags are labels attached to resources in Azure. They matter more than they
  # look: they let you filter the bill by project, and prove which resources
  # are managed by Terraform rather than created by hand.
  common_tags = {
    project     = var.project
    environment = var.environment
    managed_by  = "terraform"
    owner       = "alex adeniyi"
  }
}


# -----------------------------------------------------------------------------
# RESOURCE GROUP
# A folder that holds everything else. Deleting the group deletes its contents,
# which is your cost safety net: one command stops all billing.
# -----------------------------------------------------------------------------
resource "azurerm_resource_group" "this" {
  name     = "rg-${local.suffix}" # -> rg-compass-dev
  location = var.location
  tags     = local.common_tags
}


# -----------------------------------------------------------------------------
# THE DATA LAKE (Azure Data Lake Storage Gen2)
# This is where bronze, silver and gold data physically live.
# -----------------------------------------------------------------------------
resource "azurerm_storage_account" "lake" {
  # Storage account names must be globally unique across ALL of Azure, and
  # allow only lowercase letters and numbers - no hyphens. That is why your
  # initials are appended via a variable.
  name                = "st${var.project}${var.environment}${var.storage_account_suffix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location

  account_tier = "Standard" # Standard is fine; Premium is for very
  # low-latency workloads and costs more.
  account_replication_type = "LRS" # LRS keeps 3 copies in one datacentre.
  # Cheapest, and correct here because
  # every file can be re-downloaded from
  # the original public source.

  # THE MOST IMPORTANT LINE IN THIS BLOCK.
  # "hns" = hierarchical namespace. It gives the storage account real folders,
  # which is what turns ordinary blob storage into a DATA LAKE.
  is_hns_enabled = true

  # Security defaults. Encryption at rest is always on in Azure and cannot be
  # disabled; these two lines add transport security and block public access - K13

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  tags = local.common_tags
}

# --- The three medallion layers ---------------------------------------------
# `for_each` creates one copy of this resource per item in the list, so three
# containers are created from one block. Adding a fourth layer means adding a
# word to the variable, not copying and pasting this block.
# `toset()` converts the list to a set, which is the type for_each expects.
# `each.value` is the current item: "bronze", then "silver", then "gold".
resource "azurerm_storage_container" "layers" {
  for_each           = toset(var.medallion_layers)
  name               = each.value
  storage_account_id = azurerm_storage_account.lake.id
}


# -----------------------------------------------------------------------------
# KEY VAULT: the safe for passwords, tokens and connection strings.
# Nothing sensitive ever goes in git. Code fetches secrets from here at runtime.
# -----------------------------------------------------------------------------

# A `data` block READS something that already exists, rather than creating it.
# This one asks Azure "who am I logged in as?", which we need for the tenant ID.
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "this" {
  name                = "kv-${local.suffix}-${var.storage_account_suffix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # Deleted vaults are recoverable for this many days. Kept short and with
  # purge protection off so that during learning you can fully delete and
  # recreate. In a real production system you would want the opposite.
  purge_protection_enabled   = false
  soft_delete_retention_days = 7

  # Manage access with Azure roles rather than old-style vault access policies.
  # This is the modern, recommended approach.
  enable_rbac_authorization = true

  tags = local.common_tags
}


# -----------------------------------------------------------------------------
# DATABRICKS WORKSPACE: where notebooks, jobs and Spark clusters live.
# -----------------------------------------------------------------------------
resource "azurerm_databricks_workspace" "this" {
  name                = "dbw-${local.suffix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location

  # "premium" is REQUIRED for Unity Catalog and role-based access control.
  # The cheaper "standard" tier cannot do the governance your scoping form
  # promises, so this line is a requirement, not a luxury.
  sku = "premium"

  tags = local.common_tags
}


# =============================================================================
# UNITY CATALOG - LEAVE COMMENTED OUT ON YOUR FIRST RUN
# =============================================================================
# WHY: these resources talk to the Databricks workspace, which does not exist
# until the block above has finished creating it. On a personal Azure account
# you must also attach a "metastore" once, by hand, in the Databricks account
# console at accounts.azuredatabricks.net.
#
# So the order is:
#   1. terraform apply            (creates the workspace)
#   2. attach a metastore by hand (one time, in the account console)
#   3. delete the # from the lines below
#   4. terraform apply again      (creates the catalog and schemas)
#
# Applying infrastructure in two passes like this is completely normal. Saying
# so in your report shows you understand provider dependencies rather than
# treating Terraform as magic.
# =============================================================================

# resource "databricks_catalog" "compass" {
#   name    = var.project
#   comment = "CardioMetabolic Compass - managed by Terraform"
#   properties = {
#     purpose = "cardiometabolic-inequalities"
#   }
# }
#
# # One schema per medallion layer, created from the same variable as the
# # storage containers above - so the lake and the catalog can never drift apart.
# resource "databricks_schema" "layers" {
#   for_each     = toset(var.medallion_layers)
#   catalog_name = databricks_catalog.compass.name
#   name         = each.value
#   comment      = "${each.value} layer of the medallion architecture"
# }
