"""Task 21: FastAPI TestClient tests for the WFF calculation route.

Four cases, per BUILD_PLAN.md's Task 21 entry -- the fourth (a
loader-raised exception's HTTP status mapping) gets its own explicit test
rather than being left as prose-only documentation, since that's exactly
the failure mode (an exception silently becoming a 200) this task's
doctrine is most worried about.

Request payloads reuse `spec_cases.yaml`'s own scenario blocks via
`tests.conftest.load_wff_spec_case()` rather than hand-authoring a new
scenario -- the field names and FactStatus/BestStartCohort/PartnerStatus
string vocabulary are already identical between the YAML fixtures and the
API's request model (this module wraps `WffScenario`'s own fields
directly), so no separate translation is needed beyond adding
`modelled_date`/`requested_policy_version`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.api.wff import _wff_policy_dir
from tests.conftest import load_wff_spec_case

client = TestClient(app)


def test_policy_dir_env_var_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR-0011's deploy-time mount convention: POLTIKA_POLICY_SPECS_DIR,
    when set, wins over the source-checkout-relative default."""
    monkeypatch.setenv("POLTIKA_POLICY_SPECS_DIR", str(tmp_path))

    resolved = _wff_policy_dir()

    assert resolved == tmp_path / "working_for_families"


def test_policy_dir_defaults_without_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset (the normal case for local development and existing
    deployments): falls back to Task 21's original source-checkout-
    relative path, unchanged."""
    monkeypatch.delenv("POLTIKA_POLICY_SPECS_DIR", raising=False)

    resolved = _wff_policy_dir()

    assert resolved.name == "working_for_families"
    assert resolved.parent.name == "policy_specs"


def _request_payload(case_id: str) -> dict[str, Any]:
    case = load_wff_spec_case(case_id)
    payload: dict[str, Any] = dict(case["scenario"])
    modelled_date = case["modelled_date"]
    if isinstance(modelled_date, date):
        modelled_date = modelled_date.isoformat()
    payload["modelled_date"] = modelled_date
    payload["requested_policy_version"] = case["policy_version"]
    return payload


def test_calculate_returns_calculated_result() -> None:
    """Case 1: a normal request producing a `calculated` result. Uses
    `single_ordinary_low_income`, an already-approved spec case, and
    checks the exact expected values from that case -- not just that the
    call succeeded.

    Compares by `Decimal` value, not raw string equality: `calculate_wff()`'s
    own Decimal arithmetic can legitimately produce trailing zeros (e.g.
    "7921.000" from a zero-abatement subtraction chain), which the API
    preserves rather than reformatting -- specification.md's "preserve the
    exact decimal annual result... do not introduce rounding" applies to
    the API response too, matching how every other test in this project
    compares `Decimal(actual) == Decimal(expected)`, never a literal string.
    """
    response = client.post("/wff/calculate", json=_request_payload("single_ordinary_low_income"))

    assert response.status_code == 200
    body = response.json()
    assert body["family_tax_credit"]["outcome"] == "calculated"
    assert Decimal(body["family_tax_credit"]["value"]) == Decimal(7921)
    assert body["family_tax_credit"]["reason"] is None
    assert body["minimum_family_tax_credit"]["outcome"] == "calculated"
    assert Decimal(body["minimum_family_tax_credit"]["value"]) == Decimal(6604)
    # No Best Start-eligible child: an evidenced zero, `ineligible` (ADR-0014).
    assert body["best_start"]["outcome"] == "ineligible"
    assert Decimal(body["best_start"]["value"]) == Decimal(0)
    assert body["best_start"]["reason_code"] is None


def test_calculate_returns_needs_review_without_a_collapsed_value() -> None:
    """Case 2: the same request's in_work_tax_credit resolves
    needs_review under the real approved policy.yaml (in_work_base's live
    rate-status gate, Task 10.2) -- must serialize as `{"outcome":
    "needs_review", "value": null, "reason": <non-empty>}`, never a
    collapsed zero or omitted field. It also says why and what resolves it
    (ADR-0014): the rate is unreviewed, which no caller input can fix."""
    response = client.post("/wff/calculate", json=_request_payload("single_ordinary_low_income"))

    assert response.status_code == 200
    component = response.json()["in_work_tax_credit"]
    assert component["outcome"] == "needs_review"
    assert component["value"] is None
    assert component["reason"]
    assert component["reason_code"] == "unresolved_rule"
    assert component["missing"] == []
    assert "in_work_base" in component["resolution"]


def test_calculate_rejects_malformed_request_body() -> None:
    """Case 3: a malformed request body (missing a required field, and an
    invalid enum value for another) must return a 4xx with a clear
    validation error, not a 500 or an unhandled exception."""
    payload = _request_payload("single_ordinary_low_income")
    del payload["household_eligibility"]
    payload["partner_status"] = "not_a_real_status"

    response = client.post("/wff/calculate", json=payload)

    assert 400 <= response.status_code < 500
    detail = response.json()["detail"]
    fields_with_errors = {tuple(error["loc"]) for error in detail}
    assert ("body", "household_eligibility") in fields_with_errors
    assert ("body", "partner_status") in fields_with_errors


def test_calculate_maps_policy_version_mismatch_to_409_not_200() -> None:
    """Case 4: a requested_policy_version mismatch raises
    PolicyVersionMismatchError inside run_wff_module() -- this is the
    failure mode most worth testing explicitly, since a loader-raised
    exception silently collapsing into a 200 (or an unhandled 500) is
    exactly what Task 20/21's "caller-level structural errors stay
    distinguishable from calculation outcomes" discipline exists to
    prevent."""
    payload = _request_payload("single_ordinary_low_income")
    payload["requested_policy_version"] = "9.9.9"

    response = client.post("/wff/calculate", json=payload)

    assert response.status_code == 409
    assert "9.9.9" in response.json()["detail"]


def test_500_handler_does_not_leak_exception_detail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Historical issue: PR #22's review finding. A `PoltikaError` other
    than `PolicyVersionMismatchError` (here, an unsupported
    schema_version) previously returned `str(exc)` verbatim as the 500
    response's `detail` -- and `InvalidSourceCatalogError` in particular
    embeds absolute resolved filesystem paths, which must never reach an
    untrusted caller. The response must now carry a fixed, generic
    message with no exception text."""
    broken_policy_dir = tmp_path / "policy"
    broken_policy_dir.mkdir()
    (broken_policy_dir / "policy.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "99.9",  # unsupported -- triggers UnsupportedSchemaVersionError
                "policy_id": "working_for_families",
                "policy_version": "0.1.0",
                "status": "approved",
                "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
                "source_catalog": "sources.yaml",
                "assessment": {},
                "inputs": [],
                "parameters": [],
                "components": [],
                "outputs": {},
            }
        )
    )
    (broken_policy_dir / "sources.yaml").write_text(yaml.safe_dump({"sources": []}))
    monkeypatch.setattr("poltika.api.wff.WFF_POLICY_DIR", broken_policy_dir)

    payload = _request_payload("single_ordinary_low_income")

    response = client.post("/wff/calculate", json=payload)

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail == "Internal server error: the deployed policy configuration is invalid."
    assert "99.9" not in detail
    assert str(broken_policy_dir) not in detail
    assert "/" not in detail  # no filesystem path fragment of any kind


def test_startup_fails_loudly_if_policy_directory_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The known packaging limitation (`poltika.api.main`'s module
    docstring, PR #22 review finding): `WFF_POLICY_DIR` only resolves
    inside a source checkout. If it's ever missing -- e.g. a `pip
    install`-ed deployment that doesn't carry `policy_specs/` -- the app
    must fail immediately at startup with a clear error, not confusingly
    on the first request."""
    monkeypatch.setattr("poltika.api.main.WFF_POLICY_DIR", tmp_path / "does_not_exist")

    with pytest.raises(RuntimeError, match="has no policy.yaml"), TestClient(app):
        pass
