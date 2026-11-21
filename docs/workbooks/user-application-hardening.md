# Workbook and rules: User application hardening

Measures browser hardening, Internet Explorer 11 elimination, .NET Framework 3.5 and older presence, PowerShell 2.0 downgrade attempts, PowerShell Constrained Language Mode and logging, and Attack Surface Reduction (ASR) rule coverage against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-UserApplicationHardening.json](../../Solution/Workbooks/EssentialEight-UserApplicationHardening.json)
- **Analytics rules:**
  - [E8-Hardening-PowerShellV2DowngradeOrCLMBypass.yaml](../../Solution/Analytic%20Rules/E8-Hardening-PowerShellV2DowngradeOrCLMBypass.yaml)
  - [E8-Hardening-LegacyBrowserOrScriptEngineExecution.yaml](../../Solution/Analytic%20Rules/E8-Hardening-LegacyBrowserOrScriptEngineExecution.yaml)
- **Hunting query:**
  - [E8-Hardening-Hunt-ASRCoverage.yaml](../../Solution/Hunting%20Queries/E8-Hardening-Hunt-ASRCoverage.yaml)

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [Attack surface reduction rules reference](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference)
- [PowerShell language modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes)
- [Internet Explorer 11 end of support](https://learn.microsoft.com/en-us/lifecycle/announcements/internet-explorer-11-end-of-support)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
