# =============================================================================
# VARIABLES: the inputs to your infrastructure.
# =============================================================================
# Anything that differs between people or environments belongs here, not
# hardcoded in main.tf. You supply real values in terraform.tfvars, which is
# gitignored because it identifies your Azure subscription.
#
# Each block has three useful parts:
#   description - shown in errors and docs. Always write one.
#   type        - string, number, bool, list(string), and so on.
#   default     - if present the variable is optional; if absent it is required.
# =============================================================================

variable "subscription_id" {
  description = "Azure subscription ID. Find it with: az account show --query id -o tsv"
  type        = string
  # No default, so Terraform will refuse to run until you provide it. That is
  # deliberate: deploying into the wrong subscription is an expensive mistake.
}

variable "project" {
  description = "Short project name used in every resource name."
  type        = string
  default     = "compass"
}

variable "environment" {
  description = "Deployment environment: dev, test or prod."
  type        = string
  default     = "dev"

  # A validation block rejects bad values before anything is created.
  # `contains(list, value)` checks membership. Without this, a typo like
  # "prd" would happily create a whole parallel set of resources.
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, prod."
  }
}

variable "location" {
  description = "Azure region. UK South keeps data in the UK and has strong renewable commitments (K7/K12 evidence)."
  type        = string
  default     = "uksouth"
}

variable "medallion_layers" {
  description = "Data lake containers. Driven by a list so adding a layer is a config change."
  type        = list(string)
  default     = ["bronze", "silver", "gold"]
  # This one variable creates BOTH the storage containers and (later) the Unity
  # Catalog schemas, so the lake and the catalog cannot drift out of step.
}

variable "storage_account_suffix" {
  description = "Globally unique suffix for the storage account name, e.g. your initials."
  type        = string
  # Required, because storage account names must be unique across the whole of
  # Azure. If `terraform apply` complains the name is taken, change this value.
}
