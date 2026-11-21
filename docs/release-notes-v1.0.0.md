# Release notes: v1.0.0

First full release of `essential-eight-sentinel`, a community Microsoft Sentinel Content hub style solution for monitoring the [ASD Essential Eight Maturity Model (November 2023)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model) and mapped [ASD Information Security Manual (ISM)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism) controls (`ISM September 2026`).

## What is included in v1.0.0

- **8 Microsoft Sentinel workbooks**: Overview with indicative ML0 to ML3 scoring plus per-strategy workbooks for all eight Essential Eight mitigation strategies.
- **18 scheduled analytics rules**: Control regression detections across Defender XDR, Microsoft Entra ID and Azure Activity telemetry.
- **38 read-only hunting queries**: One dedicated evidence export query for every `observable` Essential Eight requirement (35 queries) plus targeted Office macro and ASR rule coverage queries.
- **Machine-readable mappings**: `mappings/e8-requirements.yaml` and `mappings/ism.csv` (93 mapped rules, queries and workbook tiles) with CI-verified `docs/ism-coverage.md`.
- **Content hub package**: `Solution/Package/mainTemplate.json`, `Solution/Package/createUiDefinition.json` and the attached `essential-eight-sentinel-1.0.0.zip` release artefact.
- **Documentation**: Installation guide ([docs/install-guide.md](install-guide.md)), Mermaid architecture diagrams ([docs/architecture.md](architecture.md)) and read-only evidence export guidance ([docs/assessment-evidence-export.md](assessment-evidence-export.md)).

## Important caveats

- Telemetry indicators are **indicative only** and do not constitute a formal Essential Eight assessment. Always pair technical telemetry with manual evidence required by the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide).
- Live lab workspace click testing of the Deploy to Azure button remains open in issue #13 for interactive verification in a target Azure tenant.

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft.
