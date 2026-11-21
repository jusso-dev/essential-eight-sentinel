# Workbook and rules: Regular backups

Tracks observable Azure Backup telemetry and documents the explicit boundaries between Sentinel log visibility and required manual evidence against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-RegularBackups.json](../../Solution/Workbooks/EssentialEight-RegularBackups.json)
- **Analytics rule:** [E8-Backups-VaultDeleteOrImmutabilityWeakened.yaml](../../Solution/Analytic%20Rules/E8-Backups-VaultDeleteOrImmutabilityWeakened.yaml)

## What is observable from Microsoft telemetry

| Source | Sentinel table | Observable signals | Official reference |
| :--- | :--- | :--- | :--- |
| Azure Backup (Recovery Services / Backup vaults) | `AddonAzureBackupJobs` | Scheduled and ad-hoc backup job status, duration, failure codes and restore job executions (`JobOperation == 'Restore'`) | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/addonazurebackupjobs) |
| Azure Backup protected workloads | `AddonAzureBackupProtectedInstance` | Protected instance counts, vault types and storage replication type (`LRS`, `GRS`, `ZRS`) | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/addonazurebackupprotectedinstance) |
| Azure control plane | `AzureActivity` | Vault deletion, stop-backup, soft-delete changes, Resource Guard proxy removal and backup policy edits | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/backup/backup-azure-immutable-vault-concept) |

## Clear limits and required manual evidence

This workbook does **not** prove Essential Eight compliance for Regular backups on its own. Organisations and assessors must gather supplementary manual evidence for the following gaps:

1. **Microsoft 365 Backup** ([Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/backup/backup-overview)): Microsoft 365 Backup protects SharePoint, OneDrive and Exchange Online inside the Microsoft 365 trust boundary, but does not emit dedicated `AddonAzureBackup*` tables to Sentinel. Export policy coverage, retention windows and restore test logs from the Microsoft 365 admin centre and Microsoft Purview audit logs.
2. **Vault immutability lock state and Multi-User Authorization (MUA)**: While `AzureActivity` logs changes to vault settings, confirming that immutability is actively enabled and **locked** (cannot be reversed even by backup administrators at ML3) requires Azure Resource Graph or Azure CLI read-only configuration exports (`az backup vault show`).
3. **Privilege boundary enforcement (ML1/ML2)**: Confirming that unprivileged accounts and non-backup administrators cannot access, modify or delete backups requires Azure RBAC and Entra ID role reviews across every vault and storage account.
4. **Offline / air-gapped copies and full disaster recovery drills (ML2/ML3)**: Verifying offline media custody, restored application integrity, business RPO/RTO compliance and bare-metal or identity recovery exercises requires formal DR test reports under the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide).
5. **Non-Azure backup platforms**: Third-party SaaS and on-premises backup solutions are out of scope of native Azure Backup tables unless custom connectors are onboarded.

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft.
