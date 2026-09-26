"""v0.3 Tasks 1b.2-1b.3 (ADR-0016): conditional answers.

Households are golden households with facts made unknown. Every branch
must equal an ordinary engine run with its assignment filled in, and
nothing conditional is ever `calculated` in the base result."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from poltika.engines.assurance.explanation import explain, verify
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import BestStartCohort, PartnerStatus
from poltika.policy.facts import fact_index, load_fact_catalog
from poltika.scenarios.combined import run_combined_household
from poltika.scenarios.conditional import (
    COMPONENTS,
    WFF_TOTAL,
    IncompatibleAssignmentError,
    Resolution,
    Slot,
    UncataloguedFactError,
    assign,
    component,
    resolve,
)
from poltika.scenarios.record import ScenarioRecord, result_payload
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

POLICIES = Path(__file__).resolve().parents[3] / "policy_specs"
FACTS = fact_index(
    *(
        load_fact_catalog(POLICIES / d)
        for d in ("working_for_families", "accommodation_supplement", "wff_as_interaction")
    )
)
GOLDEN = [record_from_yaml(h) for h in yaml.safe_load(GOLDEN_PATH.read_text())["households"]]
G0 = GOLDEN[0]


def _run(record: ScenarioRecord):  # type: ignore[no-untyped-def]
    return run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )


def _as(record: ScenarioRecord, **changes: object) -> ScenarioRecord:
    h = record.household
    return replace(
        record,
        household=replace(
            h, accommodation_supplement=replace(h.accommodation_supplement, **changes)
        ),
    )


def _wff(record: ScenarioRecord, **changes: object) -> ScenarioRecord:
    h = record.household
    return replace(record, household=replace(h, wff=replace(h.wff, **changes)))


def _resolve(record: ScenarioRecord, **kw: object) -> Resolution:
    return resolve(record, WFF_POLICY_DIR, AS_POLICY_DIR, FACTS, **kw)  # type: ignore[arg-type]


def _check_branches_are_real_runs(res: Resolution, record: ScenarioRecord) -> None:
    for branch in res.branches:
        direct = record
        for slot, value in branch.assignment:
            direct = assign(direct, slot, value)
        assert result_payload(_run(direct)) == result_payload(branch.result)


def test_complete_household_needs_no_branching() -> None:
    res = _resolve(G0)
    assert len(res.branches) == 1 and res.branches[0].assignment == ()
    assert not any(m.branchable for m in res.missing)


def test_unknown_claimant_category_branches_over_every_category() -> None:
    record = _as(G0, claimant_category=None)
    res = _resolve(record)
    assert (
        component(res.base, "accommodation_supplement").outcome == "needs_review"
    )  # base unchanged
    labels = {m.slot.label for m in res.missing}
    assert "accommodation_supplement.claimant_category" in labels
    values = {
        {s.label: v for s, v in b.assignment}["accommodation_supplement.claimant_category"]
        for b in res.branches
    }
    assert values == set(FACTS[("accommodation_supplement", "claimant_category")].domain())
    _check_branches_are_real_runs(res, record)
    bounds = res.bounds["accommodation_supplement"]
    assert bounds.branches == 6 and 0 < bounds.calculated < 6 and not bounds.complete
    # the real category is among the branches and reproduces the golden result
    actual = component(_run(G0), "accommodation_supplement").value
    assert (
        bounds.low is not None and bounds.high is not None and bounds.low <= actual <= bounds.high
    )


def test_eligibility_unknown_gives_eligible_and_excluded_branches() -> None:
    record = _wff(G0, household_eligibility=FactStatus.UNKNOWN)
    res = _resolve(record)
    assert all(
        component(res.base, c).outcome == "needs_review"
        for c in ("family_tax_credit", "best_start")
    )
    assert res.next_question is not None and res.next_question.slot.field == "household_eligibility"
    _check_branches_are_real_runs(res, record)
    outcomes = {
        {s.field: v for s, v in b.assignment}["household_eligibility"]: component(
            b.result, "family_tax_credit"
        ).outcome
        for b in res.branches
    }
    assert outcomes["verified"] == component(_run(G0), "family_tax_credit").outcome
    assert outcomes["excluded"] != "needs_review"


def test_two_unknowns_branch_jointly_and_the_cap_holds() -> None:
    record = _as(G0, claimant_category=None, tenure_type=None)
    full = _resolve(record)
    assert not full.capped and len(full.branches) <= 12
    _check_branches_are_real_runs(full, record)
    capped = _resolve(record, max_branches=4)
    assert capped.capped and len(capped.branches) <= 4
    assert any(b.unresolved for b in capped.branches)
    _check_branches_are_real_runs(capped, record)


def test_child_level_fact_branches_per_child() -> None:
    children = list(G0.household.wff.children)
    children[0] = replace(children[0], best_start_cohort=BestStartCohort.UNKNOWN)
    record = _wff(G0, children=children)
    res = _resolve(record)
    assert "children[0].best_start_cohort" in {m.slot.label for m in res.missing}
    _check_branches_are_real_runs(res, record)


def test_numeric_facts_are_listed_not_branched() -> None:
    record = _as(G0, weekly_income=None)
    res = _resolve(record)
    numeric = [m for m in res.missing if not m.branchable]
    if component(res.base, "accommodation_supplement").outcome == "needs_review":
        assert any(m.entry.id == "weekly_income" for m in numeric)
        assert all(
            not b.assignment or all(s.field != "weekly_income" for s, _ in b.assignment)
            for b in res.branches
        )


def test_every_branch_result_explains_and_verifies() -> None:
    res = _resolve(_as(G0, claimant_category=None))
    for branch in res.branches:
        for name in COMPONENTS:
            r = component(branch.result, name)
            assert r.trace is not None
            assert verify(explain(r.trace.component_id, r), r) == []


def test_known_components_and_totals_only_within_one_branch() -> None:
    res = _resolve(_as(G0, claimant_category=None))
    assert "family_tax_credit" in res.known  # WFF is unaffected by the AS fact
    total = res.bounds[WFF_TOTAL]
    assert total.calculated <= total.branches


def test_uncatalogued_fact_is_an_error() -> None:
    with pytest.raises(UncataloguedFactError):
        resolve(_as(G0, claimant_category=None), WFF_POLICY_DIR, AS_POLICY_DIR, {})


def test_unknown_partner_status_preserves_supplied_partner_income() -> None:
    record = _wff(GOLDEN[1], partner_status=PartnerStatus.UNKNOWN)
    res = _resolve(record)
    assert result_payload(res.base) == result_payload(_run(record))
    assert len(res.branches) == 1
    assert {s.label: v for s, v in res.branches[0].assignment} == {
        "wff.partner_status": "partnered"
    }
    _check_branches_are_real_runs(res, record)


def test_explicit_incompatible_answer_is_still_rejected() -> None:
    record = _wff(GOLDEN[1], partner_status=PartnerStatus.UNKNOWN)
    with pytest.raises(IncompatibleAssignmentError):
        assign(record, Slot("wff", "partner_status"), "single")


def test_invalid_catalogue_enum_is_not_silently_skipped() -> None:
    facts = dict(FACTS)
    key = ("wff", "partner_status")
    facts[key] = facts[key].model_copy(update={"values": {"invalid": "Invalid"}})
    with pytest.raises(ValueError, match="not a valid PartnerStatus"):
        resolve(
            _wff(GOLDEN[1], partner_status=PartnerStatus.UNKNOWN),
            WFF_POLICY_DIR,
            AS_POLICY_DIR,
            facts,
        )


def test_newly_revealed_facts_are_ranked_by_impact_under_cap() -> None:
    record = _as(_wff(G0, household_eligibility=FactStatus.UNKNOWN), claimant_category=None)
    record = replace(
        record,
        household=replace(
            record.household, as_claimant_is_wff_claimant_or_partner=FactStatus.UNKNOWN
        ),
    )
    res = _resolve(record, max_branches=3)
    assert len(res.branches) == 3
    assert any(
        s.label == "wff.household_eligibility" for b in res.branches for s, _ in b.assignment
    )
    assert res.bounds["family_tax_credit"].calculated > 0
    assert res.capped
    _check_branches_are_real_runs(res, record)


@pytest.mark.parametrize("index", range(len(GOLDEN)))
def test_golden_households_are_unchanged_by_resolution(index: int) -> None:
    record = GOLDEN[index]
    res = _resolve(record)
    assert result_payload(res.base) == result_payload(_run(record))
