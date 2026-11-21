# Workbook and rules: Restrict administrative privileges

Monitors privileged account separation, standing Global Administrator assignments, Microsoft Entra Privileged Identity Management (PIM) activation justifications, dormant privileged accounts and endpoint credential protection against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-RestrictAdminPrivileges.json](../../Solution/Workbooks/EssentialEight-RestrictAdminPrivileges.json)
- **Analytics rules:**
  - [E8-Admin-PrivilegedAccountEmailOrWebAccess.yaml](../../Solution/Analytic%20Rules/E8-Admin-PrivilegedAccountEmailOrWebAccess.yaml)
  - [E8-Admin-StandingGlobalAdminAssigned.yaml](../../Solution/Analytic%20Rules/E8-Admin-StandingGlobalAdminAssigned.yaml)
  - [E8-Admin-PIMActivationWithoutJustification.yaml](../../Solution/Analytic%20Rules/E8-Admin-PIMActivationWithoutJustification.yaml)
  - [E8-Admin-DormantPrivilegedAccountActivity.yaml](../../Solution/Analytic%20Rules/E8-Admin-DormantPrivilegedAccountActivity.yaml)

Note: Phishing-resistant MFA enforcement for privileged accounts is also monitored by [E8-MFA-PrivilegedNonPhishingResistantSignIn.yaml](../../Solution/Analytic%20Rules/E8-MFA-PrivilegedNonPhishingResistantSignIn.yaml) and surfaced in this workbook's KPI summary.

## Mapping to Essential Eight requirements

| Requirement ID | Maturity Level | Artefact | Microsoft Sentinel tables |
| :--- | :--- | :--- | :--- |
| `E8-RAP-ML1-02` | ML1 | `E8-Admin-PrivilegedAccountEmailOrWebAccess.yaml`, workbook email/web panel | `SigninLogs`, `IdentityInfo` |
| `E8-RAP-ML2-01` | ML2 | `E8-Admin-DormantPrivilegedAccountActivity.yaml`, workbook dormant panel | `SigninLogs`, `IdentityInfo` |
| `E8-RAP-ML2-02` | ML2 | `E8-Admin-StandingGlobalAdminAssigned.yaml`, workbook PIM panel | `AuditLogs`, `IdentityInfo` |
| `E8-RAP-ML2-03` | ML2 | Workbook Credential Guard and LAPS posture panel | `DeviceTvmSecureConfigurationAssessment` |
| `E8-RAP-ML3-01` | ML3 | `E8-Admin-PIMActivationWithoutJustification.yaml`, workbook PIM panel | `AuditLogs` |
| `E8-RAP-ML3-02` | ML3 | Workbook phishing-resistant MFA KPI and HVCI panel | `SigninLogs`, `IdentityInfo`, `DeviceTvmSecureConfigurationAssessment` |

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [Microsoft Entra Privileged Identity Management](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Securing privileged access](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-devices)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
