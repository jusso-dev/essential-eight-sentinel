"""End-to-end validation suite for Microsoft Sentinel Content hub artefacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from tests.validators.kql_validator import extract_workbook_queries, validate_kql
from tests.validators.style_check import check_repository

REPO_ROOT = Path(__file__).resolve().parents[1]
SOLUTION_DIR = REPO_ROOT / "Solution"
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _yaml_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(
        list(directory.rglob("*.yaml")) + list(directory.rglob("*.yml"))
    )


def _json_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.json"))


def test_solution_layout_exists() -> None:
    expected = [
        SOLUTION_DIR / "SolutionMetadata.json",
        SOLUTION_DIR / "Data" / "Solution_EssentialEight.json",
        SOLUTION_DIR / "Analytic Rules",
        SOLUTION_DIR / "Hunting Queries",
        SOLUTION_DIR / "Workbooks",
        SOLUTION_DIR / "Package",
    ]
    for path in expected:
        assert path.exists(), f"Missing required Sentinel solution path: {path.relative_to(REPO_ROOT)}"


def test_solution_metadata_schema() -> None:
    schema = _load_schema("solution_metadata.schema.json")
    data = json.loads((SOLUTION_DIR / "SolutionMetadata.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=data, schema=schema)


def test_solution_data_manifest() -> None:
    manifest_path = SOLUTION_DIR / "Data" / "Solution_EssentialEight.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("Name", "Author", "Description", "Workbooks", "Analytic Rules", "Hunting Queries", "Metadata"):
        assert key in manifest, f"Missing key {key!r} in Solution_EssentialEight.json"
    # Verify any referenced artefacts exist on disk
    for section in ("Workbooks", "Analytic Rules", "Hunting Queries"):
        for rel_path in manifest[section]:
            target = SOLUTION_DIR / rel_path
            assert target.exists(), f"Solution manifest references missing file: Solution/{rel_path}"


def test_analytic_rules_schema_and_kql() -> None:
    schema = _load_schema("analytic_rule.schema.json")
    seen_ids: dict[str, str] = {}
    for path in _yaml_files(SOLUTION_DIR / "Analytic Rules"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{rel} must contain a YAML mapping"
        jsonschema.validate(instance=data, schema=schema)

        rule_id = data["id"].lower()
        assert rule_id not in seen_ids, f"Duplicate rule id {rule_id} in {rel} and {seen_ids[rule_id]}"
        seen_ids[rule_id] = rel

        kql_errors = validate_kql(data["query"], is_workbook=False)
        assert not kql_errors, f"KQL errors in {rel}: " + "; ".join(str(e) for e in kql_errors)


def test_hunting_queries_schema_and_kql() -> None:
    schema = _load_schema("hunting_query.schema.json")
    seen_ids: dict[str, str] = {}
    for path in _yaml_files(SOLUTION_DIR / "Hunting Queries"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{rel} must contain a YAML mapping"
        jsonschema.validate(instance=data, schema=schema)

        query_id = data["id"].lower()
        assert query_id not in seen_ids, f"Duplicate hunting query id {query_id} in {rel} and {seen_ids[query_id]}"
        seen_ids[query_id] = rel

        kql_errors = validate_kql(data["query"], is_workbook=False)
        assert not kql_errors, f"KQL errors in {rel}: " + "; ".join(str(e) for e in kql_errors)


def test_workbooks_schema_and_kql() -> None:
    schema = _load_schema("workbook.schema.json")
    for path in _json_files(SOLUTION_DIR / "Workbooks"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)

        queries = list(extract_workbook_queries(data))
        assert queries, f"Workbook {rel} must contain at least one KQL query"
        for item_name, query in queries:
            kql_errors = validate_kql(query, is_workbook=True)
            assert not kql_errors, (
                f"KQL errors in {rel} ({item_name}): " + "; ".join(str(e) for e in kql_errors)
            )


def test_e8_requirements_mapping_when_present() -> None:
    req_path = REPO_ROOT / "mappings" / "e8-requirements.yaml"
    if not req_path.exists():
        pytest.skip("mappings/e8-requirements.yaml not yet created")
    data = yaml.safe_load(req_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "metadata" in data and "strategies" in data
    assert len(data["strategies"]) == 8
    seen_ids: set[str] = set()
    for strategy in data["strategies"]:
        assert strategy.get("id") and strategy.get("name")
        reqs = strategy.get("requirements", [])
        assert reqs, f"Strategy {strategy['id']} has no requirements"
        for req in reqs:
            rid = req["id"]
            assert rid not in seen_ids, f"Duplicate requirement id {rid}"
            seen_ids.add(rid)
            assert req["maturity_level"] in (1, 2, 3)
            assert req["observability"] in ("observable", "partial", "not_observable")
            assert isinstance(req.get("tables"), list)


def test_ism_mapping_when_present() -> None:
    ism_path = REPO_ROOT / "mappings" / "ism.csv"
    if not ism_path.exists():
        pytest.skip("mappings/ism.csv not yet created")
    with ism_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, "mappings/ism.csv must not be empty"
    required_cols = {
        "ism_control_id",
        "ism_release",
        "strategy",
        "e8_requirement_id",
        "maturity_level",
        "artefact_type",
        "artefact_path",
        "tile_or_rule_name",
        "control_summary",
    }
    assert required_cols.issubset(set(rows[0].keys()))
    mapped_rules: set[str] = set()
    mapped_hunts: set[str] = set()
    mapped_tiles: set[tuple[str, str]] = set()
    for row in rows:
        assert row["ism_control_id"].startswith("ISM-"), f"Invalid ISM control id: {row['ism_control_id']}"
        assert row["ism_release"].strip(), "ism_release must be populated"
        target = REPO_ROOT / row["artefact_path"]
        assert target.exists(), f"ISM mapping references missing artefact: {row['artefact_path']}"
        if row["artefact_type"] == "analytic_rule":
            mapped_rules.add(row["artefact_path"])
        elif row["artefact_type"] == "hunting_query":
            mapped_hunts.add(row["artefact_path"])
        elif row["artefact_type"] == "workbook_tile":
            mapped_tiles.add((row["artefact_path"], row["tile_or_rule_name"]))

    # Verify every analytics rule, hunting query and workbook tile is mapped
    for path in _yaml_files(SOLUTION_DIR / "Analytic Rules"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        assert rel in mapped_rules, f"Analytic rule missing from mappings/ism.csv: {rel}"
    for path in _yaml_files(SOLUTION_DIR / "Hunting Queries"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        assert rel in mapped_hunts, f"Hunting query missing from mappings/ism.csv: {rel}"
    for path in _json_files(SOLUTION_DIR / "Workbooks"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        wb = json.loads(path.read_text(encoding="utf-8"))
        for item in wb.get("items", []):
            if item.get("type") == 3:
                tile_name = item["name"]
                assert (rel, tile_name) in mapped_tiles, (
                    f"Workbook tile missing from mappings/ism.csv: {rel}::{tile_name}"
                )


def test_observable_requirements_have_hunting_queries() -> None:
    req_path = REPO_ROOT / "mappings" / "e8-requirements.yaml"
    evidence_dir = SOLUTION_DIR / "Hunting Queries" / "Evidence"
    if not req_path.exists() or not evidence_dir.exists():
        pytest.skip("Evidence hunting queries not yet created")
    data = yaml.safe_load(req_path.read_text(encoding="utf-8"))
    covered_reqs: set[str] = set()
    for path in _yaml_files(SOLUTION_DIR / "Hunting Queries"):
        q = yaml.safe_load(path.read_text(encoding="utf-8"))
        for tag in q.get("tags", []):
            if isinstance(tag, str) and tag.startswith("Requirement:"):
                covered_reqs.add(tag.split(":", 1)[1])
    missing = [
        req["id"]
        for strategy in data["strategies"]
        for req in strategy["requirements"]
        if req["observability"] == "observable" and req["id"] not in covered_reqs
    ]
    assert not missing, f"Observable requirements missing evidence hunting queries: {missing}"


def test_solution_package_arm_and_ui_templates() -> None:
    main_path = SOLUTION_DIR / "Package" / "mainTemplate.json"
    ui_path = SOLUTION_DIR / "Package" / "createUiDefinition.json"
    if not main_path.exists() or not ui_path.exists():
        pytest.skip("Solution package not yet built")

    main_tpl = json.loads(main_path.read_text(encoding="utf-8"))
    ui_def = json.loads(ui_path.read_text(encoding="utf-8"))

    assert main_tpl["$schema"].endswith("deploymentTemplate.json#")
    assert "workspace" in main_tpl["parameters"]
    assert "workspace-location" in main_tpl["parameters"]
    assert main_tpl["resources"], "mainTemplate.json must contain ARM resources"

    resource_types = {r["type"] for r in main_tpl["resources"]}
    assert "Microsoft.Insights/workbooks" in resource_types
    assert "Microsoft.OperationalInsights/workspaces/savedSearches" in resource_types
    assert "Microsoft.OperationalInsights/workspaces/providers/contentTemplates" in resource_types
    assert "Microsoft.OperationalInsights/workspaces/providers/contentPackages" in resource_types

    assert ui_def["handler"] == "Microsoft.Azure.CreateUIDef"
    ui_outputs = set(ui_def["parameters"]["outputs"].keys())
    assert {"workspace", "workspace-location"}.issubset(ui_outputs)


def test_repository_style_compliance() -> None:
    violations = check_repository(REPO_ROOT)
    assert not violations, "Style violations found:\n" + "\n".join(violations)
