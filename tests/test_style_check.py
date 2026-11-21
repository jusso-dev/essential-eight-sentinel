"""Unit tests for the repository style checker."""

from tests.validators.style_check import check_text


def test_clean_text_passes() -> None:
    sample = (
        "This independent community project measures Essential Eight controls. "
        "It is not produced, endorsed or supported by ASD, ACSC or Microsoft. "
        'Use placeholder tenantId: "00000000-0000-0000-0000-000000000000".'
    )
    assert check_text(sample, "sample.md") == []


def test_rejects_em_dash() -> None:
    sample = "Essential Eight \u2014 maturity model"
    violations = check_text(sample, "sample.md")
    assert any("em dash" in v for v in violations)


def test_rejects_emoji() -> None:
    sample = "Build passed \U0001F680"
    violations = check_text(sample, "sample.md")
    assert any("emoji" in v for v in violations)


def test_rejects_non_placeholder_tenant_id() -> None:
    fake_guid = "12345678-" + "1234-1234-1234-123456789abc"
    sample = f'tenantId: "{fake_guid}"'
    violations = check_text(sample, "config.yaml")
    assert any("non-placeholder" in v for v in violations)

    kql_sample = f'SigninLogs | where TenantId == "{fake_guid}"'
    kql_violations = check_text(kql_sample, "rule.kql")
    assert any("non-placeholder" in v for v in kql_violations)


def test_rejects_endorsement_claim() -> None:
    phrase = "official " + "ASD solution"
    sample = f"This is an {phrase} " + "endorsed " + "by Microsoft."
    violations = check_text(sample, "readme.md")
    assert any("endorsement" in v for v in violations)

    mixed = "This is not " + "endorsed " + "by ASD, but " + "endorsed " + "by Microsoft."
    mixed_violations = check_text(mixed, "readme.md")
    assert any("endorsement" in v for v in mixed_violations)
