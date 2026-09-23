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

from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from poltika.api.accommodation_supplement import _as_policy_dir
from poltika.api.main import app

client = TestClient(app)

MODELLED_DATE = "2026-06-01"


def _request_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "modelled_date": MODELLED_DATE,
        "requested_policy_version": "0.1.0",
        "household_eligibility": "verified",
        "claimant_category": "jobseeker_support",
        "tenure_type": "rent_contributions_or_board",
        "partner_status": "single",
        "statistical_area_unit": "area1",
        "weekly_accommodation_costs": "200",
        "dependent_children_count": 0,
        "cash_assets": "1000",
        "exempt_cash_asset_status": "verified",
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


def test_calculate_real_policy_undeclared_base_rate_is_needs_review() -> None:
    """The real, approved policy.yaml does not yet declare
    as_base_rate_jobseeker_support (Task 22's documented gap, pending
    Task 25's parameter-shape fix) -- must serialize as a clear
    `needs_review`, never a crash and never a guessed number."""
    response = client.post("/accommodation-supplement/calculate", json=_request_payload())

    assert response.status_code == 200
    component = response.json()["accommodation_supplement"]
    assert component["outcome"] == "needs_review"
    assert component["value"] is None
    assert "as_base_rate_jobseeker_support" in (component["reason"] or "")


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
    filesystem paths, which must never reach an untrusted caller."""
    broken_policy_dir = tmp_path / "policy"
    broken_policy_dir.mkdir()
    (broken_policy_dir / "policy.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "99.9",  # unsupported -- triggers UnsupportedSchemaVersionError
                "policy_id": "accommodation_supplement",
                "policy_version": "0.1.0",
                "status": "approved",
                "reference_period": {"from": "2026-03-02", "to": "2027-04-01"},
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
    monkeypatch.setattr("poltika.api.accommodation_supplement.AS_POLICY_DIR", broken_policy_dir)

    response = client.post("/accommodation-supplement/calculate", json=_request_payload())

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail == "Internal server error: the deployed policy configuration is invalid."
    assert "99.9" not in detail
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
