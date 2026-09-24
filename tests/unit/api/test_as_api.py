"""Task 24.8: FastAPI TestClient tests for the AS calculation route.

Mirrors `test_wff_api.py`'s Task 21 scope, adapted for AS's single-component
response shape. Unlike WFF's Case 1 (a fully `calculated` result against
the real approved policy), the real approved AS `policy.yaml` does not yet
declare the claimant-category base rates (Task 22's deliberate, documented
gap -- see `accommodation_supplement.py`'s `_param_value()` docstring), so
there is no request that legitimately produces `calculated` against the
*real deployed* policy yet. The "ordinary request" case here therefore
checks the real policy's actual current behaviour -- a clear `needs_review`
naming the undeclared parameter, never a crash and never a guessed number
-- and a second case demonstrates a real, fully-resolved `unsupported`
outcome (the r 15 asset ceiling, whose parameters *are* declared in the
real policy) end-to-end through the API.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

import poltika.api.accommodation_supplement as as_api
from poltika.api.accommodation_supplement import _as_policy_dir
from poltika.api.main import app
from poltika.engines.simulator.wff import ComponentResult
from tests.conftest import AS_POLICY_DIR, load_as_cases

client = TestClient(app)

MODELLED_DATE = "2026-06-01"
# A test week containing MODELLED_DATE -- not Task 28.2's selected week,
# which Pete has not chosen yet.
ASSESSMENT_WEEK_START = "2026-06-01"
ASSESSMENT_WEEK_END = "2026-06-08"


def _request_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "modelled_date": MODELLED_DATE,
        "assessment_week_start": ASSESSMENT_WEEK_START,
        "assessment_week_end": ASSESSMENT_WEEK_END,
        "requested_policy_version": "0.1.1",
        "household_eligibility": "verified",
        "claimant_category": "jobseeker_support",
        "tenure_type": "rent_contributions_or_board",
        "partner_status": "single",
        "statistical_area_unit": "area1",
        "weekly_accommodation_costs": "200",
        "dependent_children_count": 0,
        "cash_assets": "1000",
        "exempt_cash_asset_status": "verified",
        "ordinary_rate_status": "verified",
    }
    payload.update(overrides)
    return payload


def test_policy_dir_env_var_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR-0011's deploy-time mount convention: POLTIKA_POLICY_SPECS_DIR,
    when set, wins over the source-checkout-relative default -- same
    convention as WFF's `_wff_policy_dir()`."""
    monkeypatch.setenv("POLTIKA_POLICY_SPECS_DIR", str(tmp_path))

    resolved = _as_policy_dir()

    assert resolved == tmp_path / "accommodation_supplement"


def test_policy_dir_defaults_without_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset: falls back to the source-checkout-relative path."""
    monkeypatch.delenv("POLTIKA_POLICY_SPECS_DIR", raising=False)

    resolved = _as_policy_dir()

    assert resolved.name == "accommodation_supplement"
    assert resolved.parent.name == "policy_specs"


def test_calculate_real_policy_uses_the_published_threshold() -> None:
    """End-to-end against the real approved policy (0.1.1), which declares
    the published thresholds since Task 26a.2. The request matches the
    `real_policy_jobseeker_single_published_threshold` spec case, whose
    independently hand-calculated value is the expectation -- loaded from
    the protected YAML, not restated here."""
    case = next(
        c
        for c in load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")
        if c["id"] == "real_policy_jobseeker_single_published_threshold"
    )
    response = client.post("/accommodation-supplement/calculate", json=_request_payload())

    assert response.status_code == 200
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == "calculated"
    assert component["value"] == case["expected"]["accommodation_supplement"]["value"]


def test_calculate_real_policy_asset_ceiling_is_unsupported() -> None:
    """A real, fully-resolved `unsupported` outcome end-to-end: the r 15
    asset-ceiling parameters *are* declared in the real approved policy
    (unlike the base rates above), so cash_assets at/above the ceiling
    ($8,100 for a single claimant with no dependent children) resolves
    without any test-only parameter assumption."""
    response = client.post(
        "/accommodation-supplement/calculate",
        json=_request_payload(cash_assets="8100"),
    )

    assert response.status_code == 200
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == "unsupported"
    assert component["value"] is None
    assert "r 15" in (component["reason"] or "")


def test_calculate_serializes_fractional_decimal_value_as_json_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PR #33 review finding: no request against the real deployed policy
    yet produces a `calculated` outcome (see this module's docstring), so
    nothing exercised this module's own docstring claim that a fractional
    `Decimal` `value` serializes as a JSON string, never a JSON number
    that risks float rounding. Stubs `run_as_module()` at the route
    boundary -- the claim under test is Pydantic's serialization of the
    response model, not the calculator's arithmetic, so this does not
    need a real policy.yaml capable of a `calculated` result."""
    monkeypatch.setattr(
        as_api,
        "run_as_module",
        lambda *args, **kwargs: ComponentResult(outcome="calculated", value=Decimal("129.5500")),
    )

    response = client.post("/accommodation-supplement/calculate", json=_request_payload())

    assert response.status_code == 200
    raw_value = response.json()["accommodation_supplement"]["value"]
    assert isinstance(raw_value, str), (
        "value must be a JSON string, not a JSON number -- a JSON number "
        "would have been parsed back as a float/int here, not a str"
    )
    assert Decimal(raw_value) == Decimal("129.5500")
    assert '"value":"129.5500"' in response.text.replace(" ", "")


def test_calculate_rejects_malformed_request_body() -> None:
    """A malformed request body (missing a required field, and an invalid
    enum value for another) must return a 4xx with a clear validation
    error, not a 500 or an unhandled exception."""
    payload = _request_payload()
    del payload["household_eligibility"]
    payload["partner_status"] = "not_a_real_status"

    response = client.post("/accommodation-supplement/calculate", json=payload)

    assert 400 <= response.status_code < 500
    detail = response.json()["detail"]
    fields_with_errors = {tuple(error["loc"]) for error in detail}
    assert ("body", "household_eligibility") in fields_with_errors
    assert ("body", "partner_status") in fields_with_errors


def test_calculate_rejects_negative_amount_as_422_not_500() -> None:
    """A structural contradiction Pydantic's own `ge=0` constraint
    rejects (a negative cash_assets) -- a caller input problem, so 422,
    not an unhandled 500."""
    response = client.post(
        "/accommodation-supplement/calculate",
        json=_request_payload(cash_assets="-1"),
    )

    assert response.status_code == 422


def test_calculate_maps_policy_version_mismatch_to_409_not_200() -> None:
    """A requested_policy_version mismatch raises
    PolicyVersionMismatchError inside run_as_module() -- must map to 409,
    not silently collapse into a 200 or an unhandled 500 (same discipline
    as WFF's equivalent test)."""
    response = client.post(
        "/accommodation-supplement/calculate",
        json=_request_payload(requested_policy_version="9.9.9"),
    )

    assert response.status_code == 409
    assert "9.9.9" in response.json()["detail"]


def test_500_handler_does_not_leak_exception_detail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Historical issue (PR #22's WFF review finding, same class of bug):
    a `PoltikaError` other than `PolicyVersionMismatchError` must never
    return `str(exc)` verbatim as the 500 response's `detail` --
    `InvalidSourceCatalogError` in particular embeds absolute resolved
    filesystem paths, which must never reach an untrusted caller.

    The fixture's `schema_version` is deliberately a supported one and its
    `source_catalog` deliberately names a file that does not exist --
    PR #33 review finding: a schema_version of "99.9" here raises
    `UnsupportedSchemaVersionError` first (`load_policy_parameters()`
    checks schema_version before resolving source_catalog), never
    reaching `InvalidSourceCatalogError` at all. This must actually
    exercise the path-bearing error the docstring describes."""
    broken_policy_dir = tmp_path / "policy"
    broken_policy_dir.mkdir()
    (broken_policy_dir / "policy.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "0.1",
                "policy_id": "accommodation_supplement",
                "policy_version": "0.1.1",
                "status": "approved",
                "reference_period": {"from": "2026-03-02", "to": "2027-04-01"},
                "source_catalog": "does_not_exist.yaml",  # triggers InvalidSourceCatalogError
                "assessment": {},
                "inputs": [],
                "parameters": [],
                "components": [],
                "outputs": {},
            }
        )
    )
    monkeypatch.setattr("poltika.api.accommodation_supplement.AS_POLICY_DIR", broken_policy_dir)

    response = client.post("/accommodation-supplement/calculate", json=_request_payload())

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail == "Internal server error: the deployed policy configuration is invalid."
    assert "does_not_exist.yaml" not in detail
    assert str(broken_policy_dir) not in detail
    assert "/" not in detail  # no filesystem path fragment of any kind


def test_startup_fails_loudly_if_as_policy_directory_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same known packaging limitation as WFF's equivalent test: if
    AS_POLICY_DIR is ever missing, the app must fail immediately at
    startup with a clear error, not confusingly on the first request."""
    monkeypatch.setattr("poltika.api.main.AS_POLICY_DIR", tmp_path / "does_not_exist")

    with pytest.raises(RuntimeError, match="has no policy.yaml"), TestClient(app):
        pass


def test_calculate_requires_an_assessment_week() -> None:
    """AS is assessed per week: the route must not fall back to a lookup
    date alone."""
    payload = _request_payload()
    del payload["assessment_week_start"]
    del payload["assessment_week_end"]
    response = client.post("/accommodation-supplement/calculate", json=payload)
    assert response.status_code == 422
    missing = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "assessment_week_start") in missing
    assert ("body", "assessment_week_end") in missing


def test_calculate_rejects_a_week_that_is_not_seven_days() -> None:
    response = client.post(
        "/accommodation-supplement/calculate",
        json=_request_payload(assessment_week_end="2026-06-09"),
    )
    assert response.status_code == 422
    assert "exactly 7 days" in response.json()["detail"]


@pytest.mark.parametrize("omitted", ["ordinary_rate_status", "eldest_dependent_child_under_16"])
def test_calculate_treats_an_omitted_new_fact_as_unverified(omitted: str) -> None:
    """Task 26a repair: the API must not default either fact to verified,
    and must pass each through to the scenario (PR #50 review, M22-M26)."""
    payload = _request_payload(
        partner_status="single",
        dependent_children_count=1,
        ordinary_rate_status="verified",
        eldest_dependent_child_under_16="verified",
    )
    del payload[omitted]
    response = client.post("/accommodation-supplement/calculate", json=payload)
    assert response.status_code == 200
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == "needs_review"
    assert omitted in (component["reason"] or "")


def test_calculate_passes_eldest_child_exclusion_through() -> None:
    response = client.post(
        "/accommodation-supplement/calculate",
        json=_request_payload(dependent_children_count=1, eldest_dependent_child_under_16="excluded"),
    )
    assert response.json()["accommodation_supplement"]["outcome"] == "unsupported"


def test_calculate_refuses_the_pre_repair_policy_version() -> None:
    """No old policy version may be silently interpreted as the new contract:
    requesting 0.1.0 against the 0.1.1 AS policy is a 409, not a result."""
    response = client.post(
        "/accommodation-supplement/calculate", json=_request_payload(requested_policy_version="0.1.0")
    )
    assert response.status_code == 409
