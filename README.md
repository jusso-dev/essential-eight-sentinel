# essential-eight-sentinel

Microsoft Sentinel Content hub style solution for the ASD Essential Eight and ISM: workbooks, analytics rules and hunting queries on Defender XDR, Entra and Intune data.

> **Status:** `v1.0.0` released. See [CHANGELOG.md](CHANGELOG.md), [docs/architecture.md](docs/architecture.md), [docs/ism-coverage.md](docs/ism-coverage.md) and [issues](https://github.com/jusso-dev/essential-eight-sentinel/issues).

## Goal

Microsoft's existing Essential Eight workbook dates from 2023 and mainly covers Azure VMs. This repo builds a modern solution in the Sentinel Content hub format that measures and monitors all eight mitigation strategies at maturity levels one to three, using the data most Australian organisations already have: Defender XDR (advanced hunting tables), Entra ID, Intune and Defender Vulnerability Management.

It ships:

- A workbook per strategy plus an overview with maturity scoring
- Analytics rules that alert when a control regresses (for example MFA excluded, macros allowed from the internet, admin account used for email)
- Hunting queries for evidence collection
- A mapping of every rule and query to Essential Eight requirements and ISM controls
- A packaged solution (Content hub format) with Deploy to Azure buttons

## Deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fessential-eight-sentinel%2Fmain%2FSolution%2FPackage%2FcreateUiDefinition.json)

See [docs/install-guide.md](docs/install-guide.md) for Azure Portal, Azure CLI and post-deployment verification steps.

## Layout

```text
Solution/        Content hub package (data, workbooks, analytic rules, hunting queries)
mappings/        Essential Eight requirement and ISM control mappings (CSV/YAML)
docs/            Guides and architecture
tests/           KQL and schema validation
```

## Related projects

- [microsoft-security-logging-guide](https://github.com/jusso-dev/microsoft-security-logging-guide): which Microsoft security logs matter and how to get them into Sentinel
- [soc-ready-logging](https://github.com/jusso-dev/soc-ready-logging)
- [junction](https://github.com/jusso-dev/junction): Microsoft API runtime (Graph, Defender, Sentinel)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft. References to ASD publications, the ISM and the Essential Eight point to the official sources; always check the current release.

## Licence

Code and content are released under the [MIT License](LICENSE).
