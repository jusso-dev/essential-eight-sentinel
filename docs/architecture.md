# Architecture and data flow

This document illustrates the Microsoft security data sources, Microsoft Sentinel data connectors, indicative maturity scoring pipeline and read-only evidence export workflow used by `essential-eight-sentinel`.

## 1. Data sources, connectors and Sentinel artefacts

The solution relies on native [Microsoft Sentinel data connectors](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference) and [Microsoft Defender XDR advanced hunting tables](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables). All analytics rules, workbooks and hunting queries are read-only against the Log Analytics workspace.

```mermaid
flowchart LR
    subgraph Sources["Microsoft Security & Cloud Sources"]
        MDE["Microsoft Defender for Endpoint"]
        TVM["Microsoft Defender Vulnerability Management"]
        Entra["Microsoft Entra ID & PIM"]
        Intune["Microsoft Intune"]
        AzBackup["Azure Backup & Azure Monitor"]
    end

    subgraph Connectors["Sentinel Data Connectors & Diagnostics"]
        C_XDR["Microsoft Defender XDR Connector"]
        C_AAD["Microsoft Entra ID Connector"]
        C_UEBA["Microsoft Sentinel UEBA"]
        C_Intune["Intune Diagnostic Settings"]
        C_Az["Azure Activity & Vault Diagnostics"]
    end

    subgraph Tables["Log Analytics Workspace Tables"]
        T_MDE["DeviceInfo, DeviceEvents, DeviceProcessEvents, DeviceRegistryEvents, DeviceLogonEvents"]
        T_TVM["DeviceTvmSoftwareVulnerabilities, DeviceTvmSoftwareVulnerabilitiesKB, DeviceTvmSoftwareInventory, DeviceTvmSecureConfigurationAssessment"]
        T_AAD["SigninLogs, AADNonInteractiveUserSignInLogs, AuditLogs"]
        T_UEBA["IdentityInfo"]
        T_Intune["IntuneDevices, IntuneDeviceComplianceOrg"]
        T_Backup["AddonAzureBackupJobs, AddonAzureBackupProtectedInstance, AzureActivity"]
    end

    subgraph Content["Essential Eight Sentinel Solution"]
        WB["8 Workbooks (Overview + Per-Strategy)"]
        AR["18 Scheduled Analytics Rules"]
        HQ["38 Read-Only Hunting Queries"]
    end

    subgraph Outputs["Operational & Assessment Outputs"]
        SOC["SOC Regression Alerts & Incidents"]
        Dash["Indicative Maturity Dashboards"]
        Evid["Exported CSV/JSON Evidence Artefacts"]
    end

    MDE --> C_XDR --> T_MDE
    TVM --> C_XDR --> T_TVM
    Entra --> C_AAD --> T_AAD
    Entra --> C_UEBA --> T_UEBA
    Intune --> C_Intune --> T_Intune
    AzBackup --> C_Az --> T_Backup

    T_MDE --> WB & AR & HQ
    T_TVM --> WB & AR & HQ
    T_AAD --> WB & AR & HQ
    T_UEBA --> WB & AR & HQ
    T_Intune --> WB & HQ
    T_Backup --> WB & AR

    WB --> Dash
    AR --> SOC
    HQ --> Evid
```

## 2. How indicative maturity scores are calculated

The overview workbook ([EssentialEight-Overview.json](../Solution/Workbooks/EssentialEight-Overview.json)) evaluates each of the eight mitigation strategies against thresholds derived from the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

Strategies that depend on procedural or offline evidence (such as macro code vetting, annual WDAC ruleset reviews, initial privileged access approvals and offline backup restoration drills) are explicitly flagged and capped so telemetry scores are never mistaken for a formal assessment.

```mermaid
flowchart TD
    Start["Log Analytics Workspace Telemetry"] --> Eval["Evaluate Per-Strategy KQL Queries"]

    Eval --> S1["1. Application Control (WDAC Enforced vs Audit)"]
    Eval --> S2["2. Patch Applications (48h / 14d / 30d SLA & EOL)"]
    Eval --> S3["3. Office Macros (TVM Compliance & ASR Win32)"]
    Eval --> S4["4. User App Hardening (ASR, IE11, .NET <=3.5, PSv2)"]
    Eval --> S5["5. Restrict Admin Privileges (Email/Web, Standing GA, PIM)"]
    Eval --> S6["6. Patch Operating Systems (48h / 14d / 30d SLA & EOL)"]
    Eval --> S7["7. Multi-Factor Authentication (MFA %, Phishing-Resistant %, Legacy Auth)"]
    Eval --> S8["8. Regular Backups (Azure Backup Jobs & Restores)"]

    S1 & S2 & S3 & S4 & S5 & S6 & S7 & S8 --> Cap["Apply Observability Classification (observable / partial / not_observable)"]
    Cap --> Weakest["Indicative Strategy Ratings (ML0 to ML3) & Weakest-Link Summary"]
    Weakest --> Caveat["Display Mandatory Caveat Banner: Indicative Telemetry Only"]

    Manual["Manual Evidence (DR Reports, Vetting Records, RBAC Audits, External Scans)"] --> Formal["Formal Assessment under ASD Assessment Process Guide"]
    Caveat -.->|"Supporting technical evidence only"| Formal
```

## 3. Read-only assessment evidence and CI packaging flow

Assessors query the workspace with read-only permissions (`Log Analytics Reader`), while GitHub Actions validates schemas, KQL syntax, ISM mappings and Content hub package generation on every pull request.

```mermaid
sequenceDiagram
    participant Dev as Contributor
    participant CI as GitHub Actions CI
    participant Repo as Solution Package (mainTemplate.json)
    participant Law as Sentinel Log Analytics Workspace
    participant Assessor as Assessor (Read-Only)

    Dev->>CI: Open pull request with rules, workbooks or hunting queries
    CI->>CI: Validate JSON Schemas, KQL syntax, YAML, Markdown and style rules
    CI->>CI: Verify mappings/ism.csv and docs/ism-coverage.md
    CI->>Repo: Verify mainTemplate.json and createUiDefinition.json match source
    Repo-->>Law: Deployed via Deploy to Azure or Azure CLI
    Assessor->>Law: Run read-only Evidence hunting queries (Portal, CLI or PowerShell)
    Law-->>Assessor: Export CSV/JSON evidence artefacts with UTC timestamp and SHA-256
```

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide)
- [Microsoft Sentinel data connectors reference](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference)
- [Microsoft Defender XDR advanced hunting schema tables](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft.
