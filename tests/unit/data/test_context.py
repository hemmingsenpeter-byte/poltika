from __future__ import annotations

import csv
import io
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from poltika.data.context import DataContext, DataContextError, NoObservationError
from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, Transformation
from poltika.semantics.variables import CanonicalContext
from tests.unit.data.conftest import RAW_CSV, VARIABLE, manifest_for


def _rows(raw: bytes, manifest: DatasetManifest, unit: str = "index") -> list[Row]:
    return [
        Row(
            variable_id=manifest.canonical_variable_mapping[0],
            period_start=date.fromisoformat(r["period_start"]),
            period_end=date.fromisoformat(r["period_end"]),
            value=Decimal(r["value"]),
            unit=unit,
        )
        for r in csv.DictReader(io.StringIO(raw.decode()))
    ]


def _registry(
    fn: Callable[[bytes, DatasetManifest], list[Row]] = _rows, version: int = 1
) -> dict[str, Transformation]:
    return {"synthetic_csv": Transformation("synthetic_csv", version, fn)}


def test_repository_data_builds() -> None:
    DataContext(Path(__file__).resolve().parents[3] / "data")


def test_get_returns_value_with_full_lineage(data_root: Callable[..., Path]) -> None:
    ctx: CanonicalContext = DataContext(data_root((RAW_CSV, manifest_for(RAW_CSV))), _registry())
    obs = ctx.get("test.synthetic.level", date(2021, 6, 30))
    assert obs.value == Decimal(105)
    assert (obs.period_start, obs.period_end) == (date(2021, 1, 1), date(2022, 1, 1))
    lin = obs.lineage
    assert (lin.transformation_id, lin.transformation_version) == ("synthetic_csv", 1)
    assert (lin.dataset_id, lin.vintage, lin.raw_snapshot_version) == (
        "synthetic_series",
        "synthetic-release-1",
        1,
    )
    assert lin.source_organisation == "Synthetic test organisation"
    assert lin.publication == "Synthetic test series"
    assert lin.retrieval_date == date(2026, 9, 26)
    assert len(lin.raw_sha256) == 64


def test_no_observation_for_date_or_variable(data_root: Callable[..., Path]) -> None:
    ctx = DataContext(data_root((RAW_CSV, manifest_for(RAW_CSV))), _registry())
    with pytest.raises(NoObservationError, match="no observation covering"):
        ctx.get("test.synthetic.level", date(2022, 1, 1))  # periods are [start, end)
    with pytest.raises(NoObservationError, match="no dataset provides"):
        ctx.get("test.synthetic.other", date(2021, 1, 1))


def test_vintage_selects_the_snapshot(data_root: Callable[..., Path]) -> None:
    revised = RAW_CSV.replace(b",105", b",106")
    root = data_root(
        (RAW_CSV, manifest_for(RAW_CSV)),
        (
            revised,
            manifest_for(
                revised,
                raw_file="test_org/synthetic_series/v2/series.csv",
                raw_snapshot_version=2,
                vintage="synthetic-release-2",
            ),
        ),
    )
    ctx = DataContext(root, _registry())
    assert ctx.get("test.synthetic.level", date(2021, 1, 1)).value == Decimal(106)
    old = ctx.get("test.synthetic.level", date(2021, 1, 1), vintage="synthetic-release-1")
    assert old.value == Decimal(105)


def _bad(**kwargs: Any) -> Callable[[bytes, DatasetManifest], list[Row]]:
    def fn(raw: bytes, manifest: DatasetManifest) -> list[Row]:
        rows = _rows(raw, manifest)
        return [Row(**{**row.__dict__, **kwargs}) for row in rows]

    return fn


@pytest.mark.parametrize(
    ("transformations", "match"),
    [
        ({}, "no transformation"),
        (_registry(version=2), "registered version is 2"),
        (_registry(_bad(unit="NZD")), "the dictionary says"),
        (_registry(_bad(variable_id="test.synthetic.other")), "not in the manifest's mapping"),
        (_registry(_bad(period_end=date(2020, 1, 1))), "empty period|overlapping"),
        (_registry(_bad(period_start=date(1999, 1, 1))), "valid period"),
        (
            _registry(_bad(period_start=date(2020, 6, 1), period_end=date(2021, 6, 1))),
            "overlapping",
        ),
    ],
)
def test_contract_violations(
    data_root: Callable[..., Path], transformations: dict[str, Transformation], match: str
) -> None:
    ctx = DataContext(data_root((RAW_CSV, manifest_for(RAW_CSV))), transformations)
    with pytest.raises(DataContextError, match=match):
        ctx.get("test.synthetic.level", date(2021, 1, 1))


def test_unmapped_dictionary_variable_fails(data_root: Callable[..., Path]) -> None:
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)), variables=[])
    with pytest.raises(DataContextError, match="not in the data dictionary"):
        DataContext(root, _registry())


def test_two_datasets_for_one_variable_fail(data_root: Callable[..., Path]) -> None:
    other = manifest_for(
        RAW_CSV, dataset_id="other_series", raw_file="test_org/other/v1/series.csv"
    )
    root = data_root((RAW_CSV, manifest_for(RAW_CSV)), (RAW_CSV, other))
    with pytest.raises(DataContextError, match="mapped by both"):
        DataContext(root, _registry())


def test_real_series_needs_a_price_base(data_root: Callable[..., Path]) -> None:
    root = data_root(
        (RAW_CSV, manifest_for(RAW_CSV)), variables=[{**VARIABLE, "price_basis": "real"}]
    )
    with pytest.raises(ValueError, match="price_base"):
        DataContext(root, _registry())
