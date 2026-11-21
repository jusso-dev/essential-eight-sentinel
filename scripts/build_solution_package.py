"""Build and verify Microsoft Sentinel Content hub solution package artefacts.

Compiles Solution/Data/Solution_EssentialEight.json, Solution/SolutionMetadata.json,
Workbooks, Analytic Rules and Hunting Queries into:
- Solution/Package/mainTemplate.json
- Solution/Package/createUiDefinition.json
- Optional zip archive (--zip dist/essential-eight-sentinel-<version>.zip)

Usage:
    python scripts/build_solution_package.py          # write Package files
    python scripts/build_solution_package.py --check  # exit 1 if out of date
    python scripts/build_solution_package.py --zip dist/essential-eight-sentinel-1.0.0.zip
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SOLUTION_DIR = REPO_ROOT / "Solution"
MANIFEST_PATH = SOLUTION_DIR / "Data" / "Solution_EssentialEight.json"
METADATA_PATH = SOLUTION_DIR / "SolutionMetadata.json"
PACKAGE_DIR = SOLUTION_DIR / "Package"

PKG_NS = uuid.UUID("7e4c910a-5b1f-4d8a-9c22-000000000013")

ISO_DURATION_MAP = {
    "m": ("PT", "M"),
    "h": ("PT", "H"),
    "d": ("P", "D"),
}


def to_iso8601_duration(value: str) -> str:
    """Convert Sentinel shorthand durations (e.g. 1h, 14d) to ISO-8601 (PT1H, P14D)."""
    if value.startswith("P"):
        return value
    unit = value[-1].lower()
    qty = value[:-1]
    prefix, suffix = ISO_DURATION_MAP.get(unit, ("PT", "H"))
    return f"{prefix}{qty}{suffix}"


def to_arm_trigger_operator(op: str) -> str:
    mapping = {
        "gt": "GreaterThan",
        "lt": "LessThan",
        "eq": "Equal",
        "ne": "NotEqual",
    }
    return mapping.get(op.lower(), op)


def build_main_template(manifest: dict, metadata: dict) -> dict:
    version = manifest.get("Version", "1.0.0")
    solution_id = f"{metadata['publisherId']}.{metadata['offerId']}"
    package_uid = str(uuid.uuid5(PKG_NS, f"package/{solution_id}"))

    resources: list[dict] = []
    dependencies_criteria: list[dict] = []

    # 1. Workbooks
    for rel_path in manifest.get("Workbooks", []):
        wb_path = SOLUTION_DIR / rel_path
        wb_json = json.loads(wb_path.read_text(encoding="utf-8"))
        wb_stem = wb_path.stem
        wb_guid = str(uuid.uuid5(PKG_NS, f"workbook/{wb_stem}"))
        template_id = f"{solution_id}-wb-{wb_stem.lower()}"
        display_name = wb_stem.replace("EssentialEight-", "Essential Eight - ")

        resources.append(
            {
                "type": "Microsoft.Insights/workbooks",
                "apiVersion": "2022-04-01",
                "name": wb_guid,
                "location": "[parameters('workspace-location')]",
                "kind": "shared",
                "properties": {
                    "displayName": display_name,
                    "serializedData": json.dumps(wb_json, separators=(",", ":")),
                    "version": "1.0",
                    "sourceId": "[variables('workspaceResourceId')]",
                    "category": "sentinel",
                },
            }
        )
        resources.append(
            {
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                "apiVersion": "2023-04-01-preview",
                "name": f"[concat(parameters('workspace'), '/Microsoft.SecurityInsights/{template_id}')]",
                "location": "[parameters('workspace-location')]",
                "properties": {
                    "contentId": wb_guid,
                    "displayName": display_name,
                    "contentKind": "Workbook",
                    "version": version,
                    "contentSchemaVersion": "3.0.0",
                    "packageId": solution_id,
                    "packageVersion": version,
                    "packageKind": "Solution",
                    "packageName": manifest["Name"],
                    "mainTemplate": {
                        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                        "contentVersion": f"{version}.0",
                        "resources": [],
                    },
                },
            }
        )
        dependencies_criteria.append(
            {"kind": "Workbook", "contentId": wb_guid, "version": version}
        )

    # 2. Analytic Rules
    for rel_path in manifest.get("Analytic Rules", []):
        rule_path = SOLUTION_DIR / rel_path
        rule = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
        content_id = rule["id"]
        template_name = f"{solution_id}-ar-{content_id}"

        rule_props: dict = {
            "displayName": rule["name"],
            "description": rule["description"].strip(),
            "severity": rule["severity"],
            "status": rule["status"],
            "query": rule["query"],
            "tactics": rule["tactics"],
            "techniques": rule["relevantTechniques"],
            "requiredDataConnectors": rule["requiredDataConnectors"],
            "version": rule["version"],
        }
        if rule.get("kind") == "Scheduled":
            rule_props["queryFrequency"] = to_iso8601_duration(rule["queryFrequency"])
            rule_props["queryPeriod"] = to_iso8601_duration(rule["queryPeriod"])
            rule_props["triggerOperator"] = to_arm_trigger_operator(rule["triggerOperator"])
            rule_props["triggerThreshold"] = rule["triggerThreshold"]
        if rule.get("entityMappings"):
            rule_props["entityMappings"] = rule["entityMappings"]
        if rule.get("customDetails"):
            rule_props["customDetails"] = rule["customDetails"]

        resources.append(
            {
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                "apiVersion": "2023-04-01-preview",
                "name": f"[concat(parameters('workspace'), '/Microsoft.SecurityInsights/{template_name}')]",
                "location": "[parameters('workspace-location')]",
                "properties": {
                    "contentId": content_id,
                    "displayName": rule["name"],
                    "contentKind": "AnalyticsRule",
                    "version": rule["version"],
                    "contentSchemaVersion": "3.0.0",
                    "packageId": solution_id,
                    "packageVersion": version,
                    "packageKind": "Solution",
                    "packageName": manifest["Name"],
                    "mainTemplate": {
                        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                        "contentVersion": f"{rule['version']}.0",
                        "resources": [
                            {
                                "type": "Microsoft.SecurityInsights/AlertRuleTemplates",
                                "apiVersion": "2023-02-01-preview",
                                "name": content_id,
                                "kind": rule["kind"],
                                "properties": rule_props,
                            }
                        ],
                    },
                },
            }
        )
        dependencies_criteria.append(
            {"kind": "AnalyticsRule", "contentId": content_id, "version": rule["version"]}
        )

    # 3. Hunting Queries
    for rel_path in manifest.get("Hunting Queries", []):
        hq_path = SOLUTION_DIR / rel_path
        hq = yaml.safe_load(hq_path.read_text(encoding="utf-8"))
        content_id = hq["id"]
        template_name = f"{solution_id}-hq-{content_id}"
        saved_search_tags = [
            {"name": "description", "value": hq["description"].strip()},
            {"name": "tactics", "value": ",".join(hq["tactics"])},
            {"name": "relevantTechniques", "value": ",".join(hq["relevantTechniques"])},
        ]

        resources.append(
            {
                "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
                "apiVersion": "2020-08-01",
                "name": f"[concat(parameters('workspace'), '/{content_id}')]",
                "properties": {
                    "eTag": "*",
                    "displayName": hq["name"],
                    "category": "Hunting Queries",
                    "query": hq["query"],
                    "version": 2,
                    "tags": saved_search_tags,
                },
            }
        )
        resources.append(
            {
                "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                "apiVersion": "2023-04-01-preview",
                "name": f"[concat(parameters('workspace'), '/Microsoft.SecurityInsights/{template_name}')]",
                "location": "[parameters('workspace-location')]",
                "properties": {
                    "contentId": content_id,
                    "displayName": hq["name"],
                    "contentKind": "HuntingQuery",
                    "version": hq["version"],
                    "contentSchemaVersion": "3.0.0",
                    "packageId": solution_id,
                    "packageVersion": version,
                    "packageKind": "Solution",
                    "packageName": manifest["Name"],
                    "mainTemplate": {
                        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                        "contentVersion": f"{hq['version']}.0",
                        "resources": [],
                    },
                },
            }
        )
        dependencies_criteria.append(
            {"kind": "HuntingQuery", "contentId": content_id, "version": hq["version"]}
        )

    # 4. Solution Content Package metadata resource
    resources.append(
        {
            "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
            "apiVersion": "2023-04-01-preview",
            "name": f"[concat(parameters('workspace'), '/Microsoft.SecurityInsights/{solution_id}')]",
            "location": "[parameters('workspace-location')]",
            "properties": {
                "version": version,
                "kind": "Solution",
                "contentSchemaVersion": "3.0.0",
                "displayName": manifest["Name"],
                "publisherDisplayName": metadata["author"]["name"],
                "descriptionHtml": manifest["Description"],
                "contentId": solution_id,
                "contentKind": "Solution",
                "contentProductId": package_uid,
                "id": f"[concat(variables('workspaceResourceId'), '/providers/Microsoft.SecurityInsights/contentPackages/{solution_id}')]",
                "author": metadata["author"],
                "support": metadata["support"],
                "providers": metadata["providers"],
                "categories": metadata["categories"],
                "firstPublishDate": metadata["firstPublishDate"],
                "dependencies": {
                    "operator": "AND",
                    "criteria": dependencies_criteria,
                },
            },
        }
    )

    return {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": f"{version}.0",
        "metadata": {
            "author": metadata["author"]["name"],
            "description": manifest["Description"],
            "solutionId": solution_id,
            "version": version,
        },
        "parameters": {
            "workspace-location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Azure region of the target Microsoft Sentinel Log Analytics workspace."
                },
            },
            "workspace": {
                "type": "string",
                "metadata": {
                    "description": "Name of the target Microsoft Sentinel Log Analytics workspace."
                },
            },
        },
        "variables": {
            "workspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace'))]"
        },
        "resources": resources,
        "outputs": {
            "solutionId": {
                "type": "string",
                "value": solution_id,
            },
            "workbooksDeployed": {
                "type": "int",
                "value": len(manifest.get("Workbooks", [])),
            },
            "analyticRuleTemplatesDeployed": {
                "type": "int",
                "value": len(manifest.get("Analytic Rules", [])),
            },
            "huntingQueriesDeployed": {
                "type": "int",
                "value": len(manifest.get("Hunting Queries", [])),
            },
        },
    }


def build_create_ui_definition(manifest: dict) -> dict:
    wb_count = len(manifest.get("Workbooks", []))
    ar_count = len(manifest.get("Analytic Rules", []))
    hq_count = len(manifest.get("Hunting Queries", []))

    return {
        "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
        "handler": "Microsoft.Azure.CreateUIDef",
        "version": "0.1.2-preview",
        "parameters": {
            "config": {
                "isWizard": False,
                "basics": {
                    "description": (
                        f"{manifest['Description']} Includes {wb_count} workbooks, "
                        f"{ar_count} analytics rule templates and {hq_count} hunting queries."
                    )
                },
            },
            "basics": [
                {
                    "name": "workspace",
                    "type": "Microsoft.Common.TextBox",
                    "label": "Log Analytics Workspace Name",
                    "toolTip": "Enter the name of an existing Microsoft Sentinel enabled Log Analytics workspace in the selected resource group.",
                    "constraints": {
                        "required": True,
                        "regex": "^[a-zA-Z0-9][a-zA-Z0-9-]{2,61}[a-zA-Z0-9]$",
                        "validationMessage": "Workspace name must be 4 to 63 alphanumeric characters or hyphens.",
                    },
                }
            ],
            "steps": [
                {
                    "name": "contentSummary",
                    "label": "Solution Content",
                    "elements": [
                        {
                            "name": "summaryText",
                            "type": "Microsoft.Common.TextBlock",
                            "options": {
                                "text": (
                                    f"This deployment installs {wb_count} Essential Eight workbooks, "
                                    f"{ar_count} scheduled analytics rule templates and {hq_count} read-only "
                                    "assessment evidence hunting queries into your Microsoft Sentinel workspace. "
                                    "No tenant settings or policies are modified."
                                )
                            },
                        }
                    ],
                }
            ],
            "outputs": {
                "workspace-location": "[location()]",
                "workspace": "[basics('workspace')]",
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify Content hub solution package")
    parser.add_argument("--check", action="store_true", help="Verify Package JSON files match source")
    parser.add_argument("--zip", type=str, default=None, help="Optional output path for solution zip artefact")
    args = parser.parse_args(argv)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    main_template_text = json.dumps(build_main_template(manifest, metadata), indent=2) + "\n"
    ui_def_text = json.dumps(build_create_ui_definition(manifest), indent=2) + "\n"

    main_path = PACKAGE_DIR / "mainTemplate.json"
    ui_path = PACKAGE_DIR / "createUiDefinition.json"

    if args.check:
        stale = []
        if not main_path.exists() or main_path.read_text(encoding="utf-8") != main_template_text:
            stale.append(str(main_path.relative_to(REPO_ROOT)))
        if not ui_path.exists() or ui_path.read_text(encoding="utf-8") != ui_def_text:
            stale.append(str(ui_path.relative_to(REPO_ROOT)))
        if stale:
            print(
                "Solution package is out of date (" + ", ".join(stale) + "). "
                "Run: python scripts/build_solution_package.py",
                file=sys.stderr,
            )
            return 1
        print("Solution package is up to date.")
    else:
        PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
        main_path.write_text(main_template_text, encoding="utf-8")
        ui_path.write_text(ui_def_text, encoding="utf-8")
        print(
            f"Built {main_path.relative_to(REPO_ROOT)} and {ui_path.relative_to(REPO_ROOT)} "
            f"({len(manifest['Workbooks'])} workbooks, {len(manifest['Analytic Rules'])} rules, "
            f"{len(manifest['Hunting Queries'])} hunting queries)."
        )

    if args.zip:
        zip_path = Path(args.zip)
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mainTemplate.json", main_template_text)
            zf.writestr("createUiDefinition.json", ui_def_text)
        print(f"Created package archive: {zip_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
