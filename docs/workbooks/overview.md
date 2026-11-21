# Workbook: Essential Eight maturity overview

The overview workbook ([EssentialEight-Overview.json](../../Solution/Workbooks/EssentialEight-Overview.json)) aggregates telemetry across all eight mitigation strategies into an indicative ML0 to ML3 scorecard, lists recent Essential Eight regression alerts, verifies required Sentinel data connector health and provides drill-down links to every per-strategy workbook.

## Important caveat

Telemetry-based maturity scores are **indicative operational indicators only**. They do **not** represent a formal ASD Essential Eight assessment or compliance attestation.

- Formal assessments must follow the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide).
- Strategies with procedural or offline requirements (such as `Regular backups`, `Application control` ruleset reviews and `Configure Microsoft Office macro settings` code vetting) are intentionally capped in the automated scorecard and flagged with manual evidence reminders so teams do not overstate coverage.
- Under the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model), overall maturity is determined by the weakest-link strategy.

## Drill-down workbooks

| Strategy | Drill-down workbook |
| :--- | :--- |
| 1. Application control | [EssentialEight-ApplicationControl.json](../../Solution/Workbooks/EssentialEight-ApplicationControl.json) |
| 2. Patch applications | [EssentialEight-PatchApplicationsAndOS.json](../../Solution/Workbooks/EssentialEight-PatchApplicationsAndOS.json) |
| 3. Configure Microsoft Office macro settings | [EssentialEight-OfficeMacros.json](../../Solution/Workbooks/EssentialEight-OfficeMacros.json) |
| 4. User application hardening | [EssentialEight-UserApplicationHardening.json](../../Solution/Workbooks/EssentialEight-UserApplicationHardening.json) |
| 5. Restrict administrative privileges | [EssentialEight-RestrictAdminPrivileges.json](../../Solution/Workbooks/EssentialEight-RestrictAdminPrivileges.json) |
| 6. Patch operating systems | [EssentialEight-PatchApplicationsAndOS.json](../../Solution/Workbooks/EssentialEight-PatchApplicationsAndOS.json) |
| 7. Multi-factor authentication | [EssentialEight-MultiFactorAuthentication.json](../../Solution/Workbooks/EssentialEight-MultiFactorAuthentication.json) |
| 8. Regular backups | `EssentialEight-RegularBackups.json` (tracked in Issue #10) |

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by ASD, ACSC or Microsoft.
