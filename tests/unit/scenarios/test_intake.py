"""v0.3 Task 1b.4 (ADR-0016): the intake planner.

The main test removes each fact a golden household supplies, then answers
the planner's questions from the golden household itself. The planner must
reach the golden household's own step with its exact result, so its
questions are enough and its answers are typed as the engine expects."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from enum import Enum
from typing import Any

import pytest

from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import BestStartCohort, PartnerStatus, VerifiedIncome
from poltika.scenarios.conditional import COMPONENTS, MissingFact, Slot, resolve
from poltika.scenarios.intake import IntakeStep, apply_answer, next_step
from poltika.scenarios.record import ScenarioRecord, result_payload
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_conditional import FACTS, G0, GOLDEN, _as, _run, _wff


def _step(record: ScenarioRecord, **kw: Any) -> IntakeStep:
    return next_step(record, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS, **kw)


def _target(record: ScenarioRecord, slot: Slot) -> Any:
    h = record.household
    if slot.scope == "household":
        return h
    if slot.scope == "accommodation_supplement":
        return h.accommodation_supplement
    return h.wff if slot.child is None else h.wff.children[slot.child]


def _value(record: ScenarioRecord, slot: Slot) -> Any:
    if slot.field == "family_scheme_income.partner_amount":
        income = record.household.wff.family_scheme_income
        return None if income is None else income.partner_amount
    value = getattr(_target(record, slot), slot.field)
    return value.claimant_amount if isinstance(value, VerifiedIncome) else value


def _answer(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _cleared(value: Any) -> Any:
    if isinstance(value, FactStatus):
        return FactStatus.UNKNOWN
    if isinstance(value, PartnerStatus):
        return PartnerStatus.UNKNOWN
    if isinstance(value, BestStartCohort):
        return BestStartCohort.UNKNOWN
    if isinstance(value, bool):
        return False
    return None


def _clear(record: ScenarioRecord, slot: Slot) -> ScenarioRecord:
    h = record.household
    target = _target(record, slot)
    cleared = replace(target, **{slot.field: _cleared(getattr(target, slot.field))})
    if slot.scope == "household":
        return replace(record, household=cleared)
    if slot.scope == "accommodation_supplement":
        return replace(record, household=replace(h, accommodation_supplement=cleared))
    if slot.child is None:
        return replace(record, household=replace(h, wff=cleared))
    children = list(h.wff.children)
    children[slot.child] = cleared
    return replace(record, household=replace(h, wff=replace(h.wff, children=children)))


def _removable(record: ScenarioRecord) -> list[Slot]:
    """Every catalogued fact the household supplies, one slot each."""
    slots = []
    for scope, fact_id in FACTS:
        if fact_id == "family_scheme_income.partner_amount":
            continue  # cleared with the claimant amount it belongs to
        if fact_id.startswith("children."):
            name = fact_id.removeprefix("children.")
            slots += [Slot(scope, name, i) for i in range(len(record.household.wff.children))]
        else:
            slots.append(Slot(scope, fact_id))
    return [
        s
        for s in slots
        if _value(record, s) not in (None, False)
        and _cleared(getattr(_target(record, s), s.field)) != getattr(_target(record, s), s.field)
    ]


def _drive(record: ScenarioRecord, golden: ScenarioRecord) -> tuple[ScenarioRecord, IntakeStep]:
    asked: list[str] = []
    for _ in range(40):
        step = _step(record)
        if step.status != "ask":
            return record, step
        assert step.question is not None
        value = _value(golden, step.question.slot)
        if value is None:
            return record, step  # the golden household doesn't know it either
        label = step.question.slot.label
        assert label not in asked, f"asked {label} twice"
        asked.append(label)
        record = apply_answer(record, step.question, _answer(value))
    raise AssertionError("the planner did not stop")


def _cases() -> list[Any]:
    """Each catalogued fact once, removed from the first golden household
    that supplies it (the first child, for a child-level fact). Every
    golden household is also driven back from its first removable fact."""
    seen: set[tuple[str, str]] = set()
    cases = []
    for i, g in enumerate(GOLDEN):
        for n, slot in enumerate(_removable(g)):
            key = (slot.scope, slot.fact_id)
            if key in seen and n > 0:
                continue
            seen.add(key)
            cases.append(pytest.param(i, slot, id=f"g{i}-{slot.label}"))
    return cases


CASES = _cases()


@pytest.mark.parametrize(("index", "slot"), CASES)
def test_answering_the_planner_restores_the_golden_result(index: int, slot: Slot) -> None:
    golden = GOLDEN[index]
    restored, step = _drive(_clear(golden, slot), golden)
    assert step == _step(golden)
    assert result_payload(_run(restored)) == result_payload(_run(golden))


def test_every_golden_household_has_removable_facts() -> None:
    assert all(_removable(g) for g in GOLDEN)


def test_cases_cover_every_catalogued_fact_a_golden_household_supplies() -> None:
    supplied = {(s.scope, s.fact_id) for g in GOLDEN for s in _removable(g)}
    covered = {(p.values[1].scope, p.values[1].fact_id) for p in CASES}
    assert covered == supplied


def test_complete_golden_household_is_ready_or_blocked_only_by_parameters() -> None:
    step = _step(G0)
    assert step.status == "ready" and step.question is None and step.remaining == ()


def test_question_order_is_deterministic() -> None:
    record = _as(_wff(G0, household_eligibility=FactStatus.UNKNOWN), claimant_category=None)
    first = _step(record)
    assert first.status == "ask"
    assert all(_step(record) == first for _ in range(3))


def test_finite_fact_that_unblocks_comes_before_numeric_facts() -> None:
    record = _as(_wff(G0, household_eligibility=FactStatus.UNKNOWN), weekly_income=None)
    step = _step(record)
    assert step.question is not None and step.question.branchable
    labels = {m.slot.label for m in step.remaining}
    assert {"wff.household_eligibility", "accommodation_supplement.weekly_income"} <= labels


def test_asked_components_limit_the_questions() -> None:
    record = _as(_wff(G0, household_eligibility=FactStatus.UNKNOWN), claimant_category=None)
    step = _step(record, asked=("accommodation_supplement",))
    assert step.question is not None
    assert step.question.slot.label == "accommodation_supplement.claimant_category"
    assert all("accommodation_supplement" in m.blocks for m in step.remaining)


def test_impact_counts_only_asked_components() -> None:
    record = _as(
        _wff(G0, household_eligibility=FactStatus.UNKNOWN), statistical_area_unit=None
    )
    # Both facts unblock one asked component. Only area changes a calculated
    # amount across answers; the unasked WFF components must not break the tie.
    step = _step(record, asked=("family_tax_credit", "accommodation_supplement"))
    assert step.question is not None
    assert step.question.slot.label == "accommodation_supplement.statistical_area_unit"
    # Asking for all components gives WFF eligibility its full impact again.
    all_components = _step(record)
    assert all_components.question is not None
    assert all_components.question.slot.label == "wff.household_eligibility"


def test_numeric_questions_follow_catalogue_order() -> None:
    record = _as(_wff(G0, family_scheme_income=None), weekly_accommodation_costs=None)
    step = _step(record, asked=("family_tax_credit", "accommodation_supplement"))
    assert step.question is not None
    assert step.question.slot.label == "wff.family_scheme_income"
    # The index supplied by the caller defines catalogue order, not AS/WFF rule prefixes.
    reversed_step = next_step(
        record, WFF_POLICY_DIR, AS_POLICY_DIR, dict(reversed(tuple(FACTS.items()))),
        asked=("family_tax_credit", "accommodation_supplement"),
    )
    assert reversed_step.question is not None
    assert reversed_step.question.slot.label == "accommodation_supplement.weekly_accommodation_costs"


def test_declined_fact_is_not_asked_again_and_gives_incomplete() -> None:
    record = _wff(G0, household_eligibility=FactStatus.UNKNOWN)
    step = _step(record, declined=("wff.household_eligibility",))
    assert step.status == "incomplete" and step.question is None
    assert [m.slot.label for m in step.remaining] == ["wff.household_eligibility"]
    # the caller's conditional answer is the resolver's, unchanged
    res = resolve(record, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS)
    assert {m.slot.label for m in res.missing} >= {"wff.household_eligibility"}
    assert len(res.branches) == 2


def test_declining_one_fact_still_asks_the_others() -> None:
    record = _as(_wff(G0, household_eligibility=FactStatus.UNKNOWN), claimant_category=None)
    step = _step(record, declined=("wff.household_eligibility",))
    assert step.status == "ask" and step.question is not None
    assert step.question.slot.label == "accommodation_supplement.claimant_category"


def test_unknown_component_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown or empty"):
        _step(G0, asked=("no_such_component",))
    with pytest.raises(ValueError, match="unknown or empty"):
        _step(G0, asked=())
    assert set(COMPONENTS)


def _question(record: ScenarioRecord, label: str) -> MissingFact:
    step = _step(record)
    fact = next(m for m in step.remaining if m.slot.label == label)
    return fact


@pytest.mark.parametrize(
    ("changes", "label", "answer", "message"),
    [
        (
            {"household_eligibility": FactStatus.UNKNOWN},
            "wff.household_eligibility",
            "maybe",
            "admissible",
        ),
        ({"family_scheme_income": None}, "wff.family_scheme_income", "lots", "amount"),
        ({"family_scheme_income": None}, "wff.family_scheme_income", "-1", "non-negative"),
        ({"family_scheme_income": None}, "wff.family_scheme_income", "NaN", "non-negative"),
    ],
)
def test_inadmissible_wff_answers_are_refused(
    changes: dict[str, Any], label: str, answer: str, message: str
) -> None:
    record = _wff(G0, **changes)
    with pytest.raises(ValueError, match=message):
        apply_answer(record, _question(record, label), answer)


@pytest.mark.parametrize(
    ("changes", "label", "answer", "message"),
    [
        (
            {"dependent_children_count": None},
            "accommodation_supplement.dependent_children_count",
            "1.5",
            "whole number",
        ),
        (
            {"dependent_children_count": None},
            "accommodation_supplement.dependent_children_count",
            "-1",
            "whole number",
        ),
        (
            {"claimant_category": None},
            "accommodation_supplement.claimant_category",
            "retired",
            "admissible",
        ),
    ],
)
def test_inadmissible_as_answers_are_refused(
    changes: dict[str, Any], label: str, answer: str, message: str
) -> None:
    record = _as(G0, **changes)
    with pytest.raises(ValueError, match=message):
        apply_answer(record, _question(record, label), answer)


def test_count_refuses_non_ascii_digits() -> None:
    record = _as(G0, dependent_children_count=None)
    fact = _question(record, "accommodation_supplement.dependent_children_count")
    with pytest.raises(ValueError, match="whole number"):
        apply_answer(record, fact, "\u00b2")


def test_attestation_takes_only_yes() -> None:
    fact = MissingFact(
        Slot("wff", "net_family_scheme_income_me3_attested"),
        FACTS[("wff", "net_family_scheme_income_me3_attested")],
        ("minimum_family_tax_credit",),
    )
    assert apply_answer(G0, fact, "yes").household.wff.net_family_scheme_income_me3_attested
    with pytest.raises(ValueError, match="decline"):
        apply_answer(G0, fact, "no")


def test_partner_income_needs_the_claimant_amount_first() -> None:
    fact = MissingFact(
        Slot("wff", "family_scheme_income.partner_amount"),
        FACTS[("wff", "family_scheme_income.partner_amount")],
        ("family_tax_credit",),
    )
    with pytest.raises(ValueError, match="claimant"):
        apply_answer(_wff(G0, family_scheme_income=None), fact, "1000")


def test_money_answer_keeps_the_partner_amount() -> None:
    income = G0.household.wff.family_scheme_income
    assert income is not None
    fact = MissingFact(
        Slot("wff", "family_scheme_income"),
        FACTS[("wff", "family_scheme_income")],
        ("family_tax_credit",),
    )
    updated = apply_answer(G0, fact, "50000.50")
    assert updated.household.wff.family_scheme_income == VerifiedIncome(
        Decimal("50000.50"), income.partner_amount
    )
