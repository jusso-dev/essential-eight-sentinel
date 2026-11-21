# Workbook and rules: Configure Microsoft Office macro settings

Measures Microsoft Office macro policy compliance via Defender Vulnerability Management (`DeviceTvmSecureConfigurationAssessment`) and Intune (`IntuneDeviceComplianceOrg`), alongside runtime macro execution, Win32 API blocking and registry tampering events against the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model).

## Artefacts

- **Workbook:** [EssentialEight-OfficeMacros.json](../../Solution/Workbooks/EssentialEight-OfficeMacros.json)
- **Analytics rules:**
  - [E8-Macros-InternetMacroPolicyWeakened.yaml](../../Solution/Analytic%20Rules/E8-Macros-InternetMacroPolicyWeakened.yaml)
  - [E8-Macros-OfficeMacroWin32ApiOrChildProcess.yaml](../../Solution/Analytic%20Rules/E8-Macros-OfficeMacroWin32ApiOrChildProcess.yaml)
- **Hunting queries:**
  - [E8-Macros-Hunt-InternetFileMacroExecution.yaml](../../Solution/Hunting%20Queries/E8-Macros-Hunt-InternetFileMacroExecution.yaml)
  - [E8-Macros-Hunt-PolicyComplianceAndWin32Api.yaml](../../Solution/Hunting%20Queries/E8-Macros-Hunt-PolicyComplianceAndWin32Api.yaml)

## Official references

- [ASD Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
- [Macros from the internet are blocked by default in Office](https://learn.microsoft.com/en-us/microsoft-365-apps/security/internet-macros-blocked)
- [Attack surface reduction rules reference](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
