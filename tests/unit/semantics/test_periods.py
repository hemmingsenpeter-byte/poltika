"""Programme Task 2.3: periods, named relations and the D8 refusal."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

import pytest
from pydantic import ValidationError

from poltika.common.errors import (
    PeriodConversionRefusedError,
    PeriodRelationMismatchError,
    UnknownPeriodRelationError,
    UnknownPeriodTypeError,
)
from poltika.semantics import periods
from poltika.semantics.periods import (
    PERIOD_RELATIONS,
    PERIOD_TYPES,
    Period,
    PeriodRelation,
    PeriodType,
    RelationKind,
    check_containment,
    contains,
    convert_amount,
    get_period_relation,
    get_period_type,
)

WFF_YEAR = Period(type=PeriodType.TAX_YEAR, start=date(2026, 4, 1), end=date(2027, 4, 1))


def week(start: date, days: int = 7) -> Period:
    from datetime import timedelta

    return Period(type=PeriodType.ASSESSMENT_WEEK, start=start, end=start + timedelta(days=days))


@pytest.mark.parametrize("days", [6, 8])
def test_assessment_week_must_be_seven_days(days: int) -> None:
    with pytest.raises(ValidationError, match="7 days"):
        week(date(2026, 6, 1), days)


def test_assessment_week_has_no_weekday_convention() -> None:
    for offset in range(7):
        week(date(2026, 6, 1 + offset))


def test_point_in_time_has_no_end() -> None:
    Period(type=PeriodType.POINT_IN_TIME, start=date(2026, 6, 1))
    with pytest.raises(ValidationError):
        Period(type=PeriodType.POINT_IN_TIME, start=date(2026, 6, 1), end=date(2026, 6, 2))


def test_other_types_need_an_end_after_start() -> None:
    with pytest.raises(ValidationError, match="explicit end"):
        Period(type=PeriodType.QUARTER, start=date(2026, 4, 1))
    with pytest.raises(ValidationError, match="after start"):
        Period(type=PeriodType.CALENDAR_YEAR, start=date(2026, 1, 1), end=date(2026, 1, 1))


def test_no_anchor_date_is_enforced() -> None:
    Period(type=PeriodType.TAX_YEAR, start=date(2026, 5, 7), end=date(2027, 5, 7))


def test_period_is_frozen_and_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        WFF_YEAR.start = date(2020, 1, 1)  # type: ignore[misc]
    with pytest.raises(ValidationError):
        Period(type=PeriodType.TAX_YEAR, start=date(2026, 4, 1), end=date(2027, 4, 1), x=1)  # type: ignore[call-arg]


def test_containment_at_both_edges() -> None:
    assert contains(WFF_YEAR, week(date(2026, 4, 1)))  # starts on year start
    assert contains(WFF_YEAR, week(date(2027, 3, 25)))  # ends on year end (exclusive)
    assert not contains(WFF_YEAR, week(date(2026, 3, 31)))
    assert not contains(WFF_YEAR, week(date(2027, 3, 26)))  # one day over


def test_point_containment_is_half_open() -> None:
    def at(d: date) -> Period:
        return Period(type=PeriodType.POINT_IN_TIME, start=d)

    assert contains(WFF_YEAR, at(date(2026, 4, 1)))
    assert not contains(WFF_YEAR, at(date(2027, 4, 1)))
    assert not contains(at(date(2026, 6, 1)), at(date(2026, 6, 1)))


def test_registered_relation_applies() -> None:
    rel = get_period_relation("as_week_within_wff_year")
    assert rel.kind is RelationKind.CONTAINMENT and rel.source
    assert check_containment(rel.id, WFF_YEAR, week(date(2026, 6, 1)))
    assert not check_containment(rel.id, WFF_YEAR, week(date(2027, 3, 26)))
    with pytest.raises(PeriodRelationMismatchError):
        check_containment(rel.id, week(date(2026, 6, 1)), WFF_YEAR)


def test_unknown_ids_raise() -> None:
    with pytest.raises(UnknownPeriodTypeError):
        get_period_type("fortnight")
    with pytest.raises(UnknownPeriodRelationError):
        get_period_relation("nope")
    assert get_period_type("tax_year").id is PeriodType.TAX_YEAR


def test_registries_are_unique_complete_and_read_only() -> None:
    assert set(PERIOD_TYPES) == {t.value for t in PeriodType}
    assert all(r.id == k for k, r in PERIOD_RELATIONS.items())
    with pytest.raises(TypeError):
        PERIOD_TYPES["x"] = PERIOD_TYPES["tax_year"]  # type: ignore[index]


def test_d9_no_value_conversion_registered_and_refused() -> None:
    assert not [r for r in PERIOD_RELATIONS.values() if r.kind is RelationKind.VALUE_CONVERSION]
    with pytest.raises(PeriodConversionRefusedError, match="D8"):
        convert_amount(Decimal(52), PeriodType.TAX_YEAR, PeriodType.ASSESSMENT_WEEK)
    with pytest.raises(PeriodConversionRefusedError):
        convert_amount(Decimal(1), PeriodType.ASSESSMENT_WEEK, PeriodType.TAX_YEAR)


def test_registered_value_conversion_is_still_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    rule = PeriodRelation(
        id="annual_to_week_example",
        from_type=PeriodType.TAX_YEAR,
        to_type=PeriodType.ASSESSMENT_WEEK,
        kind=RelationKind.VALUE_CONVERSION,
        source="BUILD_PLAN.md:1",
        statement="test-only rule",
    )
    monkeypatch.setattr(periods, "PERIOD_RELATIONS", MappingProxyType({rule.id: rule}))
    with pytest.raises(PeriodConversionRefusedError, match=r"\(1 registered\)"):
        convert_amount(Decimal(52), PeriodType.TAX_YEAR, PeriodType.ASSESSMENT_WEEK)
    # A different direction has no registered rule.
    with pytest.raises(PeriodConversionRefusedError, match=r"\(0 registered\)"):
        convert_amount(Decimal(1), PeriodType.ASSESSMENT_WEEK, PeriodType.TAX_YEAR)


def test_source_citations_resolve_to_existing_lines() -> None:
    root = Path(__file__).resolve().parents[3]
    cited = [d.source for d in PERIOD_TYPES.values()] + [
        r.source for r in PERIOD_RELATIONS.values()
    ]
    pattern = re.compile(r"([\w/.-]+\.(?:md|py|yaml)):(\d+)")
    resolved = 0
    for source in cited:
        match = pattern.search(source)
        assert match, f"no file:line citation in {source!r}"
        name, line = match.group(1), int(match.group(2))
        # The variables dictionary is cited relative to the metadata folder.
        path = root / name if (root / name).exists() else root / "data" / name
        assert path.exists(), f"{name} does not exist"
        assert 1 <= line <= len(path.read_text(encoding="utf-8").splitlines()), (
            f"{source}: line out of range"
        )
        resolved += 1
    assert resolved == len(cited)
