from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from poltika.common.errors import (
    IncompatibleUnitsError,
    MissingConversionRuleError,
    PoltikaError,
    UnitConversionError,
    UnknownUnitError,
)
from poltika.semantics import units, variables
from poltika.semantics.units import (
    ConversionRegistry,
    Dimension,
    PriceBasis,
    Unit,
    UnitConversion,
    convert,
    get_unit,
    rescale,
)

DICTIONARY = Path(__file__).resolve().parents[3] / "data/metadata/variables/dictionary.yaml"

# dictionary unit string -> (unit id, entity part, period part), for Task 2.1.
DICTIONARY_UNITS = {
    "NZD million per tax year": "nzd_million",
    "NZD per household per week": "nzd",
    "NZD per household per year": "nzd",
    "NZD thousands per household": "nzd_thousand",
    "households": "households",
    "live births registered": "live_births",
    "recipients": "recipients",
    "thousands of children": "children_thousand",
    "thousands of families": "families_thousand",
    "thousands of households": "households_thousand",
    "thousands of people": "persons_thousand",
    # engine outputs (scenarios/microsim/runner.py UNITS)
    "NZD per tax year": "nzd",
    "NZD per week": "nzd",
}
D = date(2026, 7, 1)


def test_registry_ids_unique_and_keyed() -> None:
    assert len(units._UNITS) == len(units.UNITS)
    assert all(k == u.id for k, u in units.UNITS.items())
    with pytest.raises(ValueError, match="duplicate unit id"):
        units._build((units._UNITS[0], units._UNITS[0]))


def test_every_dictionary_unit_string_maps() -> None:
    data = yaml.safe_load(DICTIONARY.read_text())
    strings = {v["unit"] for v in data["variables"]}
    assert strings <= set(DICTIONARY_UNITS), strings - set(DICTIONARY_UNITS)
    for unit_id in DICTIONARY_UNITS.values():
        get_unit(unit_id)


def test_unknown_unit() -> None:
    with pytest.raises(UnknownUnitError):
        get_unit("euro")


def test_unit_validation() -> None:
    with pytest.raises(ValidationError):
        Unit(
            id="x",
            dimension=Dimension.MONEY,
            scale=Decimal(1),
            price_basis=PriceBasis.NOMINAL,
            label="x",
        )
    with pytest.raises(ValidationError):
        Unit(
            id="x",
            dimension=Dimension.PERSONS,
            scale=Decimal(1),
            price_basis=PriceBasis.NOMINAL,
            label="x",
        )
    with pytest.raises(ValidationError):
        Unit(
            id="x",
            dimension=Dimension.PERSONS,
            scale=Decimal(0),
            price_basis=PriceBasis.NOT_APPLICABLE,
            label="x",
        )


def test_rescale_round_trip_exact() -> None:
    thousand, one = get_unit("persons_thousand"), get_unit("persons")
    v = Decimal("1234.567")
    assert rescale(v, thousand, one) == Decimal(1234567)
    assert rescale(rescale(v, thousand, one), one, thousand) == v
    m = rescale(Decimal("2.5"), get_unit("nzd_million"), get_unit("nzd_thousand"))
    assert m == Decimal(2500)


@pytest.mark.parametrize(
    ("a", "b"),
    [("nzd", "persons"), ("persons", "children"), ("households", "families"), ("ratio", "percent")],
)
def test_rescale_refuses_other_dimensions(a: str, b: str) -> None:
    with pytest.raises(IncompatibleUnitsError):
        rescale(Decimal(1), get_unit(a), get_unit(b))


def test_rescale_refuses_price_basis_and_currency() -> None:
    real = Unit(
        id="nzd_real",
        dimension=Dimension.MONEY,
        scale=Decimal(1),
        price_basis=PriceBasis.REAL,
        currency="NZD",
        label="r",
    )
    aud = Unit(
        id="aud",
        dimension=Dimension.MONEY,
        scale=Decimal(1),
        price_basis=PriceBasis.NOMINAL,
        currency="AUD",
        label="a",
    )
    with pytest.raises(IncompatibleUnitsError):
        rescale(Decimal(1), get_unit("nzd"), real)
    with pytest.raises(IncompatibleUnitsError):
        rescale(Decimal(1), get_unit("nzd"), aud)


def test_convert_refuses_without_rule() -> None:
    with pytest.raises(MissingConversionRuleError):
        convert(Decimal(1), get_unit("nzd"), get_unit("nzd_million"), D)
    assert units.CONVERSIONS.find("nzd", "nzd_million", D) is None
    assert issubclass(MissingConversionRuleError, PoltikaError)


def _rule(**kw: object) -> UnitConversion:
    base: dict[str, object] = {
        "id": "r",
        "from_unit": "nzd",
        "to_unit": "nzd_thousand",
        "deflator_variable_id": "price.cpi.all_groups",
        "method": "m",
        "source": "x.yaml:1",
        "valid_from": D,
    }
    base.update(kw)
    return UnitConversion(**base)  # type: ignore[arg-type]


def test_rule_needs_deflator_and_source() -> None:
    for bad in (
        {"deflator_variable_id": ""},
        {"deflator_variable_id": "nodots"},
        {"source": ""},
        {"source": "  "},
        {"method": ""},
    ):
        with pytest.raises(ValidationError):
            _rule(**bad)
    with pytest.raises(ValidationError):
        UnitConversion(  # type: ignore[call-arg]
            id="r", from_unit="nzd", to_unit="nzd_thousand", method="m", source="x:1", valid_from=D
        )


def test_registered_rule_found_but_no_method_implemented() -> None:
    reg = ConversionRegistry((_rule(),))
    assert reg.find("nzd", "nzd_thousand", D) is not None
    assert reg.find("nzd", "nzd_thousand", date(2020, 1, 1)) is None
    with pytest.raises(UnitConversionError):
        convert(Decimal(1), get_unit("nzd"), get_unit("nzd_thousand"), D, reg)
    with pytest.raises(ValueError, match="duplicate"):
        ConversionRegistry((_rule(), _rule()))
    with pytest.raises(UnknownUnitError):
        ConversionRegistry((_rule(to_unit="euro"),))


def test_price_basis_reexported_from_variables() -> None:
    assert variables.PriceBasis is units.PriceBasis
