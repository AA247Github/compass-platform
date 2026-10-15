# =============================================================================
# AZURE DATA FACTORY                                    [SCAFFOLD - Month 2 Step 7]
# =============================================================================
# WHY: the scoping form promises a data integration platform with a graphical
# interface (K13/S4). This file will build a minimal, real ADF pipeline that
# copies IoD 2025 File 7 from gov.uk into bronze/raw/iod_2025/extract_date=.../
# where ingest_bulk_csv (source = iod_2025) picks it up.
#
# PATTERN TO USE: `count = var.enable_adf ? 1 : 0`
#   condition ? value_if_true : value_if_false   -> 1 copy or none
#   Refer to a counted resource with [0]: azurerm_data_factory.this[0].id
#
# TODO - write these resources (all with the count line above), in order:
#   1. azurerm_data_factory "this"            identity { type = "SystemAssigned" }
#   2. azurerm_role_assignment "adf_bronze"   Storage Blob Data Contributor,
#        scope = the BRONZE container only (least privilege), not the account
#   3. azurerm_data_factory_linked_service_web "govuk"   Anonymous, var.iod_base_url
#   4. azurerm_data_factory_linked_service_data_lake_storage_gen2 "lake"
#        url = azurerm_storage_account.lake.primary_dfs_endpoint, use_managed_identity = true
#   5. two azurerm_data_factory_dataset_delimited_text: "iod_source" (http) and
#        "iod_bronze" (lake), the sink path an ADF expression:
#        "@concat('raw/iod_2025/extract_date=', formatDateTime(utcNow(), 'yyyy-MM-dd'))"
#   6. azurerm_data_factory_pipeline "iod"    one Copy activity, retry = 3
#
# ...and add four variables to variables.tf: enable_adf (bool, default false),
# iod_base_url, iod_path, iod_filename.
#
# Tip: build the pipeline in ADF Studio first, then copy its JSON from the
# Code ({}) button into activities_json = jsonencode([...]).
# Check: terraform validate; plan shows 7 to add with enable_adf = true.
# =============================================================================
