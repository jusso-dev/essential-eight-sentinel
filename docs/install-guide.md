# Installation guide

This guide explains how to deploy the `essential-eight-sentinel` Content hub style package into an existing [Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/overview) workspace.

> **Read-only monitoring design:** The workbooks, analytics rule templates and hunting queries in this solution only read log telemetry from your Log Analytics workspace. They do not modify Entra ID, Intune, Defender or Azure Backup configurations.

## Prerequisites

1. An Azure subscription with a [Microsoft Sentinel-enabled Log Analytics workspace](https://learn.microsoft.com/en-us/azure/sentinel/quickstart-onboard).
2. `Microsoft Sentinel Contributor` and `Workbook Contributor` permissions on the target resource group to deploy the ARM template.
3. Recommended [Microsoft Sentinel data connectors](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference) enabled:
   - **Microsoft Defender XDR** (`DeviceInfo`, `DeviceEvents`, `DeviceProcessEvents`, `DeviceRegistryEvents`, `DeviceLogonEvents`, `DeviceTvmSoftwareVulnerabilities`, `DeviceTvmSoftwareVulnerabilitiesKB`, `DeviceTvmSoftwareInventory`, `DeviceTvmSecureConfigurationAssessment`)
   - **Microsoft Entra ID** (`SigninLogs`, `AADNonInteractiveUserSignInLogs`, `AuditLogs`)
   - **Microsoft Sentinel UEBA** (`IdentityInfo`)
   - **Microsoft Intune** diagnostic settings (`IntuneDevices`, `IntuneDeviceComplianceOrg`)
   - **Azure Backup** diagnostic settings (`AddonAzureBackupJobs`, `AddonAzureBackupProtectedInstance`)

## Option 1: Deploy to Azure Portal

Select a button below to launch the Azure Portal custom deployment wizard using `Solution/Package/mainTemplate.json` and `Solution/Package/createUiDefinition.json`:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FcreateUiDefinition.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FcreateUiDefinition.json)

1. Choose your target **Subscription** and **Resource group** containing your Sentinel workspace.
2. Enter your existing **Log Analytics Workspace Name**.
3. Review the summary and select **Create**.

## Option 2: Deploy with Azure CLI

Using the [Azure CLI `az deployment group create`](https://learn.microsoft.com/en-us/cli/azure/deployment/group?view=azure-cli-latest) command (replace placeholder values with your own):

```bash
az account set --subscription "00000000-0000-0000-0000-000000000000"

az deployment group create \
  --resource-group "rg-sentinel-prod" \
  --template-file "Solution/Package/mainTemplate.json" \
  --parameters workspace="law-sentinel-prod" workspace-location="australiaeast"
```

To validate the template without deploying resources, run `az deployment group what-if`:

```bash
az deployment group what-if \
  --resource-group "rg-sentinel-prod" \
  --template-file "Solution/Package/mainTemplate.json" \
  --parameters workspace="law-sentinel-prod" workspace-location="australiaeast"
```

## Option 3: Rebuild the package locally

To regenerate `Solution/Package/mainTemplate.json`, `Solution/Package/createUiDefinition.json` and a release zip archive after customising rules or workbooks:

```bash
python3 scripts/build_solution_package.py --zip dist/essential-eight-sentinel-1.0.0.zip
```

## Post-deployment verification

1. Open **Microsoft Sentinel** -> **Workbooks** -> **My workbooks** and open **Essential Eight - Overview**.
2. Inspect the **Required Sentinel data connector telemetry health** table at the bottom of the overview workbook to confirm your connectors are ingesting data.
3. Open **Analytics** -> **Rule templates**, search for `Essential Eight`, and enable the scheduled rules relevant to your environment.
4. Open **Hunting**, filter by `Essential Eight`, and follow [docs/assessment-evidence-export.md](assessment-evidence-export.md) to export evidence.

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft.
