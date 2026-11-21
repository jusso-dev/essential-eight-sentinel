# Workbook and rules: Multi-factor authentication

Monitors MFA coverage, phishing-resistant MFA adoption, legacy authentication usage and Conditional Access exclusions against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-MultiFactorAuthentication.json](../../Solution/Workbooks/EssentialEight-MultiFactorAuthentication.json)
- **Analytics rules:**
  - [E8-MFA-ConditionalAccessExclusionAdded.yaml](../../Solution/Analytic%20Rules/E8-MFA-ConditionalAccessExclusionAdded.yaml)
  - [E8-MFA-LegacyAuthSuccess.yaml](../../Solution/Analytic%20Rules/E8-MFA-LegacyAuthSuccess.yaml)
  - [E8-MFA-PrivilegedNonPhishingResistantSignIn.yaml](../../Solution/Analytic%20Rules/E8-MFA-PrivilegedNonPhishingResistantSignIn.yaml)
  - [E8-MFA-ConditionalAccessPolicyDisabledOrDeleted.yaml](../../Solution/Analytic%20Rules/E8-MFA-ConditionalAccessPolicyDisabledOrDeleted.yaml)

## Mapping to Essential Eight Maturity Level requirements

| Requirement ID | Maturity Level | Artefact | Microsoft Sentinel tables |
| :--- | :--- | :--- | :--- |
| `E8-MFA-ML1-01` | ML1 | Workbook KPI and strength breakdown | `SigninLogs`, `AADNonInteractiveUserSignInLogs` |
| `E8-MFA-ML1-03` | ML1 | `E8-MFA-LegacyAuthSuccess.yaml`, workbook legacy auth table | `SigninLogs`, `AADNonInteractiveUserSignInLogs` |
| `E8-MFA-ML2-01` | ML2 | Workbook phishing-resistant MFA KPI and pie chart | `SigninLogs` |
| `E8-MFA-ML2-02` | ML2 | `E8-MFA-PrivilegedNonPhishingResistantSignIn.yaml`, workbook privileged weak auth table | `SigninLogs`, `IdentityInfo` |
| `E8-MFA-ML2-03` | ML2 | `E8-MFA-ConditionalAccessExclusionAdded.yaml`, `E8-MFA-ConditionalAccessPolicyDisabledOrDeleted.yaml` | `AuditLogs` |
| `E8-MFA-ML3-01` | ML3 | Workbook phishing-resistant % all users, CA exclusion rules | `SigninLogs`, `AuditLogs` |

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [Microsoft Entra authentication strengths](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)
- [Block legacy authentication with Conditional Access](https://learn.microsoft.com/en-us/entra/identity/conditional-access/block-legacy-authentication)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
