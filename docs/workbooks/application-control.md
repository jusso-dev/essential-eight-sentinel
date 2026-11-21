# Workbook and rules: Application control

Measures App Control for Business (formerly Windows Defender Application Control / WDAC) enforcement coverage, audit-only endpoints, blocked executions and policy weakening events against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-ApplicationControl.json](../../Solution/Workbooks/EssentialEight-ApplicationControl.json)
- **Analytics rules:**
  - [E8-AppControl-PolicyRemovedOrDeleted.yaml](../../Solution/Analytic%20Rules/E8-AppControl-PolicyRemovedOrDeleted.yaml)
  - [E8-AppControl-PolicySwitchedToAuditMode.yaml](../../Solution/Analytic%20Rules/E8-AppControl-PolicySwitchedToAuditMode.yaml)
  - [E8-AppControl-VulnerableDriverOrBypassAttempt.yaml](../../Solution/Analytic%20Rules/E8-AppControl-VulnerableDriverOrBypassAttempt.yaml)

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [Query App Control events with advanced hunting](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/querying-application-control-events-centrally-using-advanced-hunting)
- [Understanding App Control event IDs](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/event-id-explanations)
- [Microsoft recommended block rules](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/design/microsoft-recommended-block-rules)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
