# Changelog

All notable changes to `essential-eight-sentinel` are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-21

### Added

- **Content hub solution layout and CI validation** (#2): Microsoft Sentinel Content hub directory structure, JSON Schemas for analytics rules, hunting queries, workbooks and solution metadata, a custom KQL syntax validator (`tests/validators/kql_validator.py`), repository style checker (`tests/validators/style_check.py`), YAML lint and Markdown lint in GitHub Actions CI.
- **Essential Eight requirements and telemetry mapping** (#1): Machine-readable `mappings/e8-requirements.yaml` and `docs/requirements-and-data-sources.md` covering all eight mitigation strategies across Maturity Levels 1 to 3 from the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model), with honest observability classifications (`observable`, `partial`, `not_observable`).
- **Workbooks (8 total)**:
  - `EssentialEight-Overview.json` (#11): Indicative ML0 to ML3 scorecard across all eight strategies with explicit assessment caveats, regression alert summary, data connector health and drill-down links.
  - `EssentialEight-PatchApplicationsAndOS.json` (#4): Defender Vulnerability Management time-to-patch, exploited vulnerabilities (CISA KEV / vendor flags) and unsupported software/OS views with device group filters and synthetic fixture previews.
  - `EssentialEight-MultiFactorAuthentication.json` (#5): MFA coverage, phishing-resistant MFA adoption, legacy authentication and Conditional Access exclusions.
  - `EssentialEight-RestrictAdminPrivileges.json` (#6): Privileged email/web access, standing Global Administrators, Entra PIM activation justification, dormant privileged accounts and Credential Guard / LAPS posture.
  - `EssentialEight-ApplicationControl.json` (#7): App Control for Business (WDAC) enforcement coverage, audit-only devices, blocked executions and user-writable path executions.
  - `EssentialEight-OfficeMacros.json` (#8): Defender TVM and Intune macro compliance, Win32 API ASR blocks/audits and suspicious Office child processes.
  - `EssentialEight-UserApplicationHardening.json` (#9): Attack Surface Reduction (ASR) rule coverage, browser hardening, IE11 removal, .NET Framework 3.5 and older detection, PowerShell 2.0 and Constrained Language Mode logging.
  - `EssentialEight-RegularBackups.json` (#10): Azure Backup job health, restore job history, protected instances and vault modification tracking with an explicit telemetry limits and manual evidence section.
- **Scheduled analytics rules (18 total)**: Regression detections spanning Patch applications, Patch operating systems, Multi-factor authentication, Restrict administrative privileges, Application control, Microsoft Office macros, User application hardening and Regular backups.
- **Read-only hunting queries (38 total)** (#8, #9, #12): Dedicated assessment evidence export queries for all 35 `observable` requirements in `Solution/Hunting Queries/Evidence/` plus targeted macro and ASR operational hunts, alongside read-only Portal, Azure CLI and PowerShell export guidance in `docs/assessment-evidence-export.md`.
- **ISM control mapping** (#3): `mappings/ism.csv` mapping all 93 analytics rules, hunting queries and workbook tiles to ASD Information Security Manual (`ISM September 2026`) control IDs, with CI-verified Markdown generation (`scripts/generate_ism_coverage.py` -> `docs/ism-coverage.md`).
- **Content hub solution packaging and Deploy to Azure** (#13): `scripts/build_solution_package.py` generating `Solution/Package/mainTemplate.json`, `Solution/Package/createUiDefinition.json` and deployable `.zip` archives, Deploy to Azure buttons and `docs/install-guide.md`.
- **Architecture and data flow diagrams** (#14): GitHub-renderable Mermaid diagrams in `docs/architecture.md` showing data sources, connectors, indicative maturity scoring and evidence export flows.

### Known limitations

- Live end-to-end click verification of the **Deploy to Azure** button in a lab Microsoft Sentinel workspace remains tracked in issue #13 (manual test required; automated builds do not connect to any live tenant).
- Telemetry scores are indicative operational metrics only and do not replace a formal assessment under the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide).
