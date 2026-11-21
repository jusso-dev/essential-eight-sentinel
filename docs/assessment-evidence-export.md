# Assessment evidence hunting queries and export guide

This guide explains how assessors and security engineers can run the Essential Eight hunting queries in `Solution/Hunting Queries/` and export repeatable, read-only evidence artefacts for each observable requirement in [mappings/e8-requirements.yaml](../mappings/e8-requirements.yaml).

> **Important caveat:** Exported telemetry is supporting technical evidence only. Formal Essential Eight maturity ratings must follow the [ASD Essential Eight Assessment Process Guide](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-assessment-process-guide), including sampling verification, configuration inspection and manual evidence for partially observable or non-observable controls.

## Query layout

Every `observable` requirement in `mappings/e8-requirements.yaml` has a dedicated evidence hunting query in `Solution/Hunting Queries/Evidence/` named `<RequirementID>-Evidence.yaml` (for example `E8-MFA-ML1-03-Evidence.yaml`), alongside targeted operational hunting queries in `Solution/Hunting Queries/`.

Each evidence query is:

- **Read-only**: Queries Log Analytics / Sentinel tables without modifying tenant state.
- **Deterministic**: Includes an explicit lookback window (`ago(14d)` or `ago(30d)`), clear summary columns and `EvidenceRequirement` tagging so exported CSV/JSON rows are self-describing.
- **CI validated**: Validated against `tests/schemas/hunting_query.schema.json` and the KQL syntax validator in `tests/validators/kql_validator.py`.

## Option 1: Export via the Microsoft Sentinel portal

1. Open **Microsoft Sentinel** -> **Threat management** -> **Hunting** ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/hunting)).
2. Filter queries by tag `EssentialEight` or search by requirement ID (for example `E8-PA-ML1-01`).
3. Select **Run Query** (or select multiple queries and choose **Run selected queries**).
4. Open **View Results**, verify the time range matches the assessment period, and select **Export** -> **Export to CSV - All columns**.
5. Record the query UTC execution timestamp, workspace resource ID (sanitised if shared externally) and SHA-256 hash of the exported CSV in the assessment workpapers.

## Option 2: Export via Azure CLI (read-only)

Using the official [Azure Monitor Log Analytics CLI extension](https://learn.microsoft.com/en-us/cli/azure/monitor/log-analytics?view=azure-cli-latest) with a Log Analytics Reader role:

```bash
# Replace with your workspace customer ID (placeholder shown)
WORKSPACE_ID="00000000-0000-0000-0000-000000000000"
QUERY=$(python3 -c "import yaml; print(yaml.safe_load(open('Solution/Hunting Queries/Evidence/E8-MFA-ML1-03-Evidence.yaml'))['query'])")

az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "$QUERY" \
  --timespan P14D \
  --output table
```

To save structured JSON evidence for archiving:

```bash
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query "$QUERY" \
  --timespan P14D \
  --output json > E8-MFA-ML1-03-evidence.json
```

## Option 3: Export via PowerShell (`Az.OperationalInsights`, read-only)

Using the official [`Invoke-AzOperationalInsightsQuery`](https://learn.microsoft.com/en-us/powershell/module/az.operationalinsights/invoke-azoperationalinsightsquery) cmdlet:

```powershell
$WorkspaceId = "00000000-0000-0000-0000-000000000000"
$Yaml = Get-Content "Solution/Hunting Queries/Evidence/E8-PA-ML1-01-Evidence.yaml" -Raw | ConvertFrom-Yaml
$Result = Invoke-AzOperationalInsightsQuery -WorkspaceId $WorkspaceId -Query $Yaml.query -Timespan (New-TimeSpan -Days 14)
$Result.Results | Export-Csv -Path "E8-PA-ML1-01-evidence.csv" -NoTypeInformation
```

## Evidence integrity checklist

- Run queries using a dedicated read-only account (`Log Analytics Reader` or `Microsoft Sentinel Reader`).
- Retain the exact query version (git commit SHA), execution timestamp (UTC) and exported row count alongside each CSV/JSON artefact.
- Pair telemetry exports with manual evidence for `partial` and `not_observable` requirements listed in [docs/requirements-and-data-sources.md](requirements-and-data-sources.md).

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft.
