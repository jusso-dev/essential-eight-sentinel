"""Unit tests for the KQL syntax validator."""

from tests.validators.kql_validator import extract_workbook_queries, validate_kql


def test_valid_simple_query() -> None:
    query = """
    // Count failed sign-ins using legacy authentication
    SigninLogs
    | where TimeGenerated > ago(7d)
    | where ResultType == "0"
    | where ClientAppUsed in ("IMAP4", "POP3", "SMTP")
    | summarize SignInCount = count() by UserPrincipalName, ClientAppUsed
    | order by SignInCount desc
    """
    assert validate_kql(query) == []


def test_valid_let_and_join_query() -> None:
    query = """
    let lookback = 14d;
    let exploited = DeviceTvmSoftwareVulnerabilitiesKB
        | where IsExploitAvailable == true
        | distinct CveId;
    DeviceTvmSoftwareVulnerabilities
    | where TimeGenerated > ago(lookback)
    | join kind=inner exploited on CveId
    | project DeviceName, SoftwareName, CveId, VulnerabilitySeverityLevel
    """
    assert validate_kql(query) == []


def test_valid_workbook_query_with_parameters() -> None:
    query = """
    DeviceTvmSoftwareVulnerabilities
    | where TimeGenerated > ago({TimeRange})
    | where VulnerabilitySeverityLevel in ({Severity})
    | summarize VulnCount = dcount(CveId) by DeviceName
    """
    assert validate_kql(query, is_workbook=True) == []


def test_rejects_empty_query() -> None:
    assert validate_kql("   // only a comment\n") != []


def test_rejects_sql_query() -> None:
    errors = validate_kql("SELECT * FROM SigninLogs WHERE ResultType = 0")
    assert any("SQL" in str(e) for e in errors)


def test_rejects_unbalanced_parentheses() -> None:
    errors = validate_kql("SigninLogs | where TimeGenerated > ago(7d")
    assert any("Unclosed" in str(e) for e in errors)


def test_rejects_unterminated_string() -> None:
    errors = validate_kql('SigninLogs | where AppDisplayName == "Portal')
    assert any("Unterminated" in str(e) for e in errors)


def test_rejects_unknown_pipe_operator() -> None:
    errors = validate_kql("SigninLogs | frobnicate TimeGenerated")
    assert any("Unknown or invalid KQL tabular operator" in str(e) for e in errors)


def test_rejects_single_equals_in_where() -> None:
    errors = validate_kql('SigninLogs | where ResultType = "0"')
    assert any("==" in str(e) for e in errors)


def test_rejects_trailing_pipe() -> None:
    errors = validate_kql("SigninLogs | where TimeGenerated > ago(1d) |")
    assert any("Empty pipe stage" in str(e) for e in errors)


def test_accepts_filter_alias_and_rejects_empty_where() -> None:
    assert validate_kql('SigninLogs | filter ResultType == "0"') == []
    assert validate_kql("SigninLogs | where") != []
    assert validate_kql("SigninLogs | filter") != []
    assert validate_kql('SigninLogs | filter ResultType = "0"') != []


def test_validates_inside_materialize_and_toscalar() -> None:
    assert validate_kql("let x = materialize(SigninLogs | take 5); x | count") == []
    assert validate_kql("let x = materialize(SigninLogs |); x") != []
    assert validate_kql("let c = toscalar(SigninLogs | where); SigninLogs | extend total = c") != []


def test_extracts_nested_workbook_queries() -> None:
    workbook = {
        "version": "Notebook/1.0",
        "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json",
        "items": [
            {
                "type": 9,
                "name": "params",
                "content": {
                    "parameters": [
                        {"name": "DeviceGroup", "query": "DeviceInfo | distinct MachineGroup"}
                    ]
                },
            },
            {
                "type": 12,
                "name": "group-1",
                "content": {
                    "items": [
                        {
                            "type": 3,
                            "name": "tile-1",
                            "content": {"query": "SigninLogs | take 5", "queryType": 0},
                        }
                    ]
                },
            },
        ],
    }
    extracted = list(extract_workbook_queries(workbook))
    assert len(extracted) == 2
    assert extracted[0][0] == "params.DeviceGroup"
    assert extracted[1][0] == "tile-1"
