# Essential Eight requirements and Microsoft Sentinel data sources

This document summarises how requirements from the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model) and the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide) map to Microsoft Sentinel, Microsoft Defender XDR, Microsoft Entra ID, Microsoft Intune and Azure Backup telemetry.

The machine-readable source of truth is [mappings/e8-requirements.yaml](../mappings/e8-requirements.yaml).

## Observability classification

Every requirement in `mappings/e8-requirements.yaml` is classified into one of three categories so organisations and assessors do not overstate what log telemetry can prove:

- `observable` - Primary technical evidence can be queried directly from Microsoft Sentinel and Defender XDR tables.
- `partial` - Telemetry provides useful continuous indicators, but a formal assessment still requires supplementary configuration exports, external scans or governance records.
- `not_observable` - Control is procedural or offline (such as code review before macro signing, initial access request approvals or bare-metal disaster recovery exercises) and must be evidenced manually.

## Core Microsoft Sentinel tables used

| Table | Source product | Essential Eight strategies supported | Official reference |
| :--- | :--- | :--- | :--- |
| `DeviceTvmSoftwareVulnerabilities` | Microsoft Defender Vulnerability Management | Patch applications, Patch operating systems | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicetvmsoftwarevulnerabilities-table) |
| `DeviceTvmSoftwareVulnerabilitiesKB` | Microsoft Defender Vulnerability Management | Patch applications, Patch operating systems | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicetvmsoftwarevulnerabilitieskb-table) |
| `DeviceTvmSoftwareInventory` | Microsoft Defender Vulnerability Management | Patch applications, User application hardening | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicetvmsoftwareinventory-table) |
| `DeviceTvmSecureConfigurationAssessment` | Microsoft Defender Vulnerability Management | Application control, Office macros, User application hardening, Restrict administrative privileges | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicetvmsecureconfigurationassessment-table) |
| `DeviceInfo` | Microsoft Defender for Endpoint | Application control, Patch applications, Patch operating systems, Restrict administrative privileges | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceinfo-table) |
| `DeviceEvents` | Microsoft Defender for Endpoint | Application control, Office macros, User application hardening | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceevents-table) |
| `DeviceProcessEvents` | Microsoft Defender for Endpoint | Application control, Office macros, User application hardening | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table) |
| `DeviceRegistryEvents` | Microsoft Defender for Endpoint | Office macros, User application hardening | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceregistryevents-table) |
| `DeviceLogonEvents` | Microsoft Defender for Endpoint | Restrict administrative privileges, Multi-factor authentication | [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicelogonevents-table) |
| `SigninLogs` / `AADNonInteractiveUserSignInLogs` | Microsoft Entra ID | Multi-factor authentication, Restrict administrative privileges | [Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins) |
| `AuditLogs` | Microsoft Entra ID | Multi-factor authentication, Restrict administrative privileges, Regular backups | [Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs) |
| `IdentityInfo` | Microsoft Sentinel UEBA / Entra ID | Multi-factor authentication, Restrict administrative privileges | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/ueba-reference) |
| `IntuneDevices` / `IntuneDeviceComplianceOrg` | Microsoft Intune | Application control, Office macros, Patch operating systems, Restrict administrative privileges | [Microsoft Learn](https://learn.microsoft.com/en-us/mem/intune/fundamentals/review-logs-using-azure-monitor) |
| `AddonAzureBackupJobs` / `AddonAzureBackupProtectedInstance` | Azure Backup | Regular backups | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/backup/backup-azure-monitoring-built-in-monitor) |
| `AzureActivity` | Azure Monitor | Regular backups, Application control | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log) |

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft. Telemetry measurements are indicative only and do not replace a formal Essential Eight assessment conducted under the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide).
