"""Task 11.5: valid, missing, overlapping, unapproved, and unresolved-rate cases.

Uses synthetic policy.yaml/sources.yaml fixtures (via tmp_path), not the real
WFF files -- this tests the loader's own logic in isolation, independent of
whatever WFF's spec currently says. WFF-specific behaviour (e.g. that
in_work_base is needs_review today) is exercised separately in
test_loader_against_wff.py against the real, approved files.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from poltika.common.errors import (
    PolicyNotApprovedError,
    PolicyVersionMismatchError,
    UnresolvedSourceIdError,
    UnsupportedSchemaVersionError,
)
from poltika.policy.loader import load_policy_parameters

MODELLED_DATE = date(2026, 6, 1)  # inside the fixtures' 2026-04-01..2027-04-01 interval


def _base_policy(**overrides: object) -> dict:
    policy = {
        "schema_version": "0.1",
        "policy_id": "test_policy",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            {
                "id": "rate",
                "value_type": "money",
                "unit": "NZD_per_tax_year",
                "values": [
                    {
                        "effective_from": "2026-04-01",
                        "effective_to": "2027-04-01",
                        "value": 100,
                        "source_id": "test-source",
                        "locator": "s 1",
                        "review_status": "approved",
                    }
                ],
            }
        ],
        "components": [],
        "outputs": {},
    }
    policy.update(overrides)
    return policy


def _write_policy(policy_dir: Path, policy: dict, sources: dict | None = None) -> None:
    policy_dir.mkdir(parents=True, exist_ok=True)
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump(sources or {"sources": [{"id": "test-source", "kind": "legislation"}]})
    )


def test_valid_parameter_resolves(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy())

    result = load_policy_parameters(tmp_path, MODELLED_DATE)

    resolution = result.get("rate")
    assert resolution.outcome == "resolved"
    assert resolution.value == 100
    assert resolution.unit == "NZD_per_tax_year"
    assert resolution.reason is None


def test_missing_interval_is_unsupported_not_zero(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy())

    # A date entirely outside the parameter's only interval.
    result = load_policy_parameters(tmp_path, date(2030, 1, 1))

    resolution = result.get("rate")
    assert resolution.outcome == "unsupported"
    assert resolution.value is None
    assert "no effective interval covers" in resolution.reason


def test_overlapping_intervals_rejected_at_load_time(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["values"].append(
        {
            "effective_from": "2026-06-01",  # overlaps the first interval
            "effective_to": "2027-06-01",
            "value": 200,
            "source_id": "test-source",
            "locator": "s 2",
            "review_status": "approved",
        }
    )
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="overlapping effective intervals"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_unapproved_policy_status_rejected(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy(status="draft_pending_review"))

    with pytest.raises(PolicyNotApprovedError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_unresolved_rate_returns_needs_review_not_a_value(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["values"][0]["review_status"] = "needs_review"
    _write_policy(tmp_path, policy)

    result = load_policy_parameters(tmp_path, MODELLED_DATE)

    resolution = result.get("rate")
    assert resolution.outcome == "needs_review"
    assert resolution.value is None
    assert "not 'approved'" in resolution.reason


def test_unsupported_schema_version_rejected(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy(schema_version="99.0"))

    with pytest.raises(UnsupportedSchemaVersionError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_policy_version_mismatch_rejected(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy())

    with pytest.raises(PolicyVersionMismatchError):
        load_policy_parameters(
            tmp_path, MODELLED_DATE, requested_policy_version="9.9.9"
        )


def test_unknown_source_id_rejected(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["values"][0]["source_id"] = "no-such-source"
    _write_policy(tmp_path, policy)

    with pytest.raises(UnresolvedSourceIdError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_approved_policy_with_no_policy_version_rejected(tmp_path: Path) -> None:
    # Should be unreachable per SCHEMA.md's Version axes, but the loader must
    # not silently trust that invariant.
    _write_policy(tmp_path, _base_policy(policy_version=None))

    with pytest.raises(PolicyNotApprovedError):
        load_policy_parameters(tmp_path, MODELLED_DATE)
