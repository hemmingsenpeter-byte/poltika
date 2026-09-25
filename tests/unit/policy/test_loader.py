"""Task 11.5: valid, missing, overlapping, unapproved, and unresolved-rate cases.

Uses synthetic policy.yaml/sources.yaml fixtures (via tmp_path), not the real
WFF files -- this tests the loader's own logic in isolation, independent of
whatever WFF's spec currently says. WFF-specific behaviour (e.g. that
in_work_base is needs_review today) is exercised separately in
test_loader_against_wff.py against the real, approved files.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from poltika.common.errors import (
    InvalidSourceCatalogError,
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


# --- Task 11.6 review findings ------------------------------------------------


def test_rate_resolves_with_exact_decimal_precision(tmp_path: Path) -> None:
    """0.275 * 3 as float is 0.8250000000000001; as Decimal it's exactly 0.825.

    The approved WFF abatement rate is 27.5 cents per complete dollar, which
    the calculation sequence explicitly says can produce a half-cent annual
    result -- this only stays exact if the loader hands Task 12 a Decimal,
    not a float, per the reviewer's finding on PR #13.
    """
    policy = _base_policy()
    policy["parameters"][0]["values"][0]["value"] = 0.275
    _write_policy(tmp_path, policy)

    result = load_policy_parameters(tmp_path, MODELLED_DATE)

    resolution = result.get("rate")
    assert isinstance(resolution.value, Decimal)
    assert resolution.value == Decimal("0.275")
    assert resolution.value * 3 == Decimal("0.825")  # exact; float would not be


def test_duplicate_parameter_id_rejected(tmp_path: Path) -> None:
    policy = _base_policy()
    duplicate = dict(policy["parameters"][0])
    duplicate["values"] = [
        {
            "effective_from": "2026-04-01",
            "effective_to": "2027-04-01",
            "value": 200,  # different value -- would silently win if not rejected
            "source_id": "test-source",
            "locator": "s 2",
            "review_status": "approved",
        }
    ]
    policy["parameters"].append(duplicate)
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="duplicate parameter id"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_open_ended_final_interval_resolves(tmp_path: Path) -> None:
    """SCHEMA.md: effective_to is optional -- an open-ended final interval
    is a legitimate shape, not something to reject or crash on."""
    policy = _base_policy()
    del policy["parameters"][0]["values"][0]["effective_to"]
    _write_policy(tmp_path, policy)

    # Any date on/after effective_from, including well beyond the old
    # hardcoded 2027-04-01 boundary, resolves.
    result = load_policy_parameters(tmp_path, date(2030, 1, 1))

    resolution = result.get("rate")
    assert resolution.outcome == "resolved"
    assert resolution.value == 100


def test_open_ended_interval_must_be_last(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["values"] = [
        {
            "effective_from": "2020-04-01",
            # open-ended, but a later interval exists below -- invalid
            "value": 50,
            "source_id": "test-source",
            "locator": "s 1",
            "review_status": "approved",
        },
        {
            "effective_from": "2026-04-01",
            "effective_to": "2027-04-01",
            "value": 100,
            "source_id": "test-source",
            "locator": "s 2",
            "review_status": "approved",
        },
    ]
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="open-ended interval"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_declared_source_catalog_is_honoured(tmp_path: Path) -> None:
    """A policy naming a non-default catalogue file must actually use it,
    not silently validate against a hardcoded sources.yaml."""
    policy = _base_policy(source_catalog="alt_sources.yaml")
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "policy.yaml").write_text(yaml.safe_dump(policy))
    (tmp_path / "alt_sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    # A file literally named sources.yaml also exists, with a DIFFERENT set
    # of known IDs -- if the loader ignored source_catalog and fell back to
    # this file, resolution would incorrectly fail.
    (tmp_path / "sources.yaml").write_text(yaml.safe_dump({"sources": []}))

    result = load_policy_parameters(tmp_path, MODELLED_DATE)

    assert result.get("rate").outcome == "resolved"


def test_source_catalog_path_traversal_rejected(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy(source_catalog="../sources.yaml"))

    with pytest.raises(InvalidSourceCatalogError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_source_catalog_missing_file_rejected(tmp_path: Path) -> None:
    _write_policy(tmp_path, _base_policy(source_catalog="does_not_exist.yaml"))

    with pytest.raises(InvalidSourceCatalogError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_empty_values_list_rejected(tmp_path: Path) -> None:
    """A parameter with no effective-dated values is a malformed policy.yaml,
    not a legitimate always-unsupported parameter -- reject it at load time
    rather than let it pass quietly and resolve "unsupported" forever."""
    policy = _base_policy()
    policy["parameters"][0]["values"] = []
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="at least 1 item"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_unknown_value_type_rejected(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["value_type"] = "percentage"  # not a known dimension
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_unknown_unit_rejected(tmp_path: Path) -> None:
    policy = _base_policy()
    policy["parameters"][0]["unit"] = "USD_per_month"  # free text, not a known unit
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError):
        load_policy_parameters(tmp_path, MODELLED_DATE)


def test_value_type_unit_dimension_mismatch_rejected(tmp_path: Path) -> None:
    """Both value_type and unit are independently valid, but a "fraction"
    claiming a currency-per-year unit is the wrong dimension -- SCHEMA.md:
    "rates must state their dimension" -- and must be rejected as a
    combination, not just as independently-valid free text."""
    policy = _base_policy()
    policy["parameters"][0]["value_type"] = "fraction"
    policy["parameters"][0]["unit"] = "NZD_per_tax_year"  # a money unit, not a rate unit
    policy["parameters"][0]["values"][0]["value"] = 0.25  # a valid fraction: only the unit is wrong
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="not a valid unit for that dimension"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


@pytest.mark.parametrize(
    ("value_type", "unit"),
    [
        ("money", "NZD"),
        ("money", "NZD_per_week"),
        ("fraction", "fraction"),
    ],
)
def test_task_23_as_units_are_valid(tmp_path: Path, value_type: str, unit: str) -> None:
    """Task 23's narrow, additive ParameterUnit extension (NZD, NZD_per_week,
    fraction -- see the ParameterUnit docstring for why) must actually work,
    not just fail to break WFF. Confirms each new unit resolves normally
    for its correct value_type, independent of any AS-specific fixture."""
    policy = _base_policy()
    policy["parameters"][0]["value_type"] = value_type
    policy["parameters"][0]["unit"] = unit
    if value_type == "fraction":
        policy["parameters"][0]["values"][0]["value"] = 0.25  # fractions are range-checked (QS-1)
    _write_policy(tmp_path, policy)

    result = load_policy_parameters(tmp_path, MODELLED_DATE)

    resolution = result.get("rate")
    assert resolution.outcome == "resolved"
    assert resolution.unit == unit


def test_task_23_fraction_unit_still_rejects_wrong_value_type(tmp_path: Path) -> None:
    """The new bare `fraction` unit must still be dimension-checked like
    every other unit -- adding it must not accidentally widen `money`'s
    valid-unit set too."""
    policy = _base_policy()
    policy["parameters"][0]["value_type"] = "money"
    policy["parameters"][0]["unit"] = "fraction"
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="not a valid unit for that dimension"):
        load_policy_parameters(tmp_path, MODELLED_DATE)


@pytest.mark.parametrize("value", [27.5, -0.01, 1.01])
def test_fraction_outside_zero_to_one_is_refused(tmp_path: Path, value: float) -> None:
    """v0.1 question set QS-1: a rate stored as a percentage (27.5 for
    0.275) loaded and silently made FTC $0. It is now refused at load."""
    policy = _base_policy()
    policy["parameters"][0]["value_type"] = "fraction"
    policy["parameters"][0]["unit"] = "fraction"
    policy["parameters"][0]["values"][0]["value"] = value
    _write_policy(tmp_path, policy)

    with pytest.raises(ValueError, match="fractions must be between 0 and 1"):
        load_policy_parameters(tmp_path, MODELLED_DATE)
