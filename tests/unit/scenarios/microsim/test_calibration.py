"""v0.2 Task 3.3: the real population spec is derived, not written by hand.

- The committed spec is exactly what `calibrate_cli.render()` derives from
  the committed snapshots, so no share can drift from its source.
- Assumption A9 (the open top rent band's upper bound doesn't matter) holds
  against the Accommodation Supplement policy's own caps and thresholds.
- The share and band rules behave as documented.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from poltika.scenarios.microsim.calibrate_cli import render
from poltika.scenarios.microsim.calibration import CalibrationError, _shares, _two_bands
from poltika.scenarios.microsim.synthetic import SyntheticSpec

ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "data" / "metadata" / "populations" / "nz_synthetic_development.v1.yaml"
AS_POLICY = ROOT / "policy_specs" / "accommodation_supplement" / "policy.yaml"
LOOKUP = date(2026, 6, 1)


def test_committed_spec_is_the_derivation() -> None:
    assert SPEC.read_text() == render(ROOT / "data")
    SyntheticSpec.model_validate(yaml.safe_load(SPEC.read_text()))


def _values(prefix: str) -> list[Decimal]:
    out = []
    for param in yaml.safe_load(AS_POLICY.read_text())["parameters"]:
        if param["id"].startswith(prefix):
            for v in param["values"]:
                if v["effective_from"] <= LOOKUP < v["effective_to"]:
                    out.append(Decimal(str(v["value"])))
    assert out, prefix
    return out


def test_a9_top_rent_band_starts_where_every_as_cap_binds() -> None:
    spec = yaml.safe_load(SPEC.read_text())
    top_start = Decimal(spec["weekly_housing_cost"][-1]["from"])
    (rate,) = _values("rent_board_subsidy_rate")
    binds_by = max(_values("area_cap_")) / rate + max(_values("as_entry_threshold_"))
    assert top_start >= binds_by


def test_shares_sum_to_exactly_one() -> None:
    shares = _shares({"a": Decimal(1), "b": Decimal(1), "c": Decimal(1)})
    assert sum(Decimal(v) for v in shares.values()) == 1
    assert sorted(shares.values()) == ["0.333333", "0.333333", "0.333334"]
    with pytest.raises(CalibrationError):
        _shares({"a": Decimal(0)})


def test_two_bands_reproduce_median_and_mean() -> None:
    low, high = _two_bands(Decimal(100), Decimal(150))
    assert (low["from"], low["to"], high["from"], high["to"]) == (0, 100, 100, 400)
    assert (Decimal(low["to"]) / 2 + Decimal(high["from"] + high["to"]) / 2) / 2 == 150
    with pytest.raises(CalibrationError):
        _two_bands(Decimal(100), Decimal(40))
