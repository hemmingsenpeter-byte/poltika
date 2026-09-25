"""Run the 26 September 2026 70-question set through Poltika v0.1.

The questions include both fully specified calculations and deliberate
missing/conflicting-input cases. This runner records only executable model
outputs. Interpretive notes and underdetermined answers live in
`calculations_for_review.md`.
"""

from __future__ import annotations

import json
from dataclasses import fields, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    ComponentResult,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    WffScenario,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.combined import CombinedHouseholdScenario, run_combined_household

ROOT = Path(__file__).resolve().parents[2]
WFF_POLICY_DIR = ROOT / "policy_specs" / "working_for_families"
AS_POLICY_DIR = ROOT / "policy_specs" / "accommodation_supplement"
AS_POLICY_VERSION = "0.1.1"
MODELLED_DATE = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
OUTPUT = Path(__file__).with_name("current_70_results.json")
VERIFIED = FactStatus.VERIFIED
UNKNOWN = FactStatus.UNKNOWN
EXCLUDED = FactStatus.EXCLUDED


def component(result: ComponentResult) -> dict[str, Any]:
    return {
        "outcome": result.outcome,
        "value": str(result.value) if result.value is not None else None,
        "reason": result.reason,
    }


def wff_result(result: WffResult) -> dict[str, Any]:
    rendered = {field.name: component(getattr(result, field.name)) for field in fields(WffResult)}
    total = result.total_annual_entitlement()
    rendered["total_annual_entitlement"] = str(total) if total is not None else None
    return rendered


def child(
    *,
    qualifies: FactStatus = VERIFIED,
    cohort: BestStartCohort = BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
    best_start_eligibility: FactStatus = VERIFIED,
) -> ChildFacts:
    return ChildFacts(
        qualifies_whole_year=qualifies,
        best_start_cohort=cohort,
        best_start_no_disqualifying_payment=best_start_eligibility,
    )


def wff_scenario(
    income: str | None,
    *,
    children: list[ChildFacts] | None = None,
    child_count: int = 1,
    partnered: bool = False,
    partner_income: str | None = None,
    net_income: str | None = None,
    hours: FactStatus = VERIFIED,
    household_eligibility: FactStatus = VERIFIED,
) -> WffScenario:
    family_income = None
    if income is not None:
        family_income = VerifiedIncome(
            claimant_amount=Decimal(income),
            partner_amount=Decimal(partner_income) if partner_income is not None else None,
        )
    return WffScenario(
        household_eligibility=household_eligibility,
        extra_instalment_status=VERIFIED,
        children=children if children is not None else [child() for _ in range(child_count)],
        partner_status=PartnerStatus.PARTNERED if partnered else PartnerStatus.SINGLE,
        family_scheme_income=family_income,
        net_family_scheme_income=Decimal(net_income) if net_income is not None else None,
        net_family_scheme_income_me3_attested=net_income is not None,
        in_work_eligibility=VERIFIED,
        ftc_iwtc_protected_or_direct_abatement=VERIFIED,
        mc6a_veterans_payment=VERIFIED,
        mc6b_disqualifying_payment=VERIFIED,
        minimum_family_full_time_earner_weeks=hours,
        best_start_no_shared_care=VERIFIED,
        best_start_protected_credit=VERIFIED,
    )


def calculate_wff_scenario(scenario: WffScenario, *, when: date = MODELLED_DATE) -> dict[str, Any]:
    return wff_result(
        run_wff_module(
            WFF_POLICY_DIR,
            when,
            scenario,
            requested_policy_version="0.1.0",
        )
    )


def as_scenario(
    *,
    rent: str | None = "600",
    income: str | None = "1346",
    assets: str | None = "2000",
    area: Area | None = Area.AREA_1,
    partner: PartnerType = PartnerType.ORDINARY_COUPLE,
    children: int = 2,
    category: ClaimantCategory = ClaimantCategory.NON_BENEFICIARY,
    tenure: TenureType | None = TenureType.RENT_CONTRIBUTIONS_OR_BOARD,
    household_eligibility: FactStatus = VERIFIED,
) -> AsScenario:
    return AsScenario(
        household_eligibility=household_eligibility,
        claimant_category=category,
        tenure_type=tenure,
        partner_status=partner,
        statistical_area_unit=area,
        weekly_accommodation_costs=Decimal(rent) if rent is not None else None,
        dependent_children_count=children,
        cash_assets=Decimal(assets) if assets is not None else None,
        exempt_cash_asset_status=VERIFIED,
        weekly_income=Decimal(income) if income is not None else None,
        ordinary_rate_status=VERIFIED,
        eldest_dependent_child_under_16=VERIFIED if children else UNKNOWN,
    )


def single_jobseeker(
    *,
    rent: str = "250",
    assets: str | None = "0",
    area: Area | None = Area.AREA_1,
    household_eligibility: FactStatus = VERIFIED,
) -> AsScenario:
    return as_scenario(
        rent=rent,
        income=None,
        assets=assets,
        area=area,
        partner=PartnerType.SINGLE,
        children=0,
        category=ClaimantCategory.JOBSEEKER_SUPPORT,
        household_eligibility=household_eligibility,
    )


def calculate_as(scenario: AsScenario, parameters: Any) -> dict[str, Any]:
    return component(calculate_accommodation_supplement(scenario, parameters))


def combined(
    wff: WffScenario,
    as_: AsScenario,
) -> dict[str, Any]:
    result = run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        CombinedHouseholdScenario(
            wff=wff,
            accommodation_supplement=as_,
            as_claimant_is_wff_claimant_or_partner=VERIFIED,
        ),
        wff_lookup_date=MODELLED_DATE,
        as_lookup_date=MODELLED_DATE,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )
    return {
        "wff": wff_result(result.wff),
        "accommodation_supplement": component(result.accommodation_supplement),
        "contradictions": list(result.contradictions),
    }


def api_validation(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    with TestClient(app) as client:
        response = client.post(path, json=payload)
    body = response.json()
    return {
        "status": response.status_code,
        "body": body if response.status_code == 200 else None,
        "detail": body.get("detail") if response.status_code != 200 else None,
    }


def as_request(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "modelled_date": "2026-06-01",
        "assessment_week_start": "2026-06-01",
        "assessment_week_end": "2026-06-08",
        "requested_policy_version": AS_POLICY_VERSION,
        "household_eligibility": "verified",
        "claimant_category": "jobseeker_support",
        "tenure_type": "rent_contributions_or_board",
        "partner_status": "single",
        "statistical_area_unit": "area1",
        "weekly_accommodation_costs": "250",
        "dependent_children_count": 0,
        "cash_assets": "0",
        "exempt_cash_asset_status": "verified",
        "ordinary_rate_status": "verified",
    }
    payload.update(overrides)
    return payload


def wff_request(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "modelled_date": "2026-06-01",
        "requested_policy_version": "0.1.0",
        "household_eligibility": "verified",
        "extra_instalment_status": "verified",
        "partner_status": "single",
        "family_scheme_income": {"claimant_amount": "45000"},
        "in_work_eligibility": "verified",
        "ftc_iwtc_protected_or_direct_abatement": "verified",
        "mc6a_veterans_payment": "verified",
        "mc6b_disqualifying_payment": "verified",
        "minimum_family_full_time_earner_weeks": "verified",
        "best_start_no_shared_care": "verified",
        "best_start_protected_credit": "verified",
        "children": [
            {
                "qualifies_whole_year": "verified",
                "best_start_cohort": "outside_best_start_entitlement",
                "best_start_no_disqualifying_payment": "verified",
            }
        ],
    }
    payload.update(overrides)
    return payload


def main() -> None:
    wff_parameters = load_policy_parameters(
        WFF_POLICY_DIR,
        MODELLED_DATE,
        requested_policy_version="0.1.0",
    )
    as_parameters = load_policy_parameters(
        AS_POLICY_DIR,
        MODELLED_DATE,
        requested_policy_version=AS_POLICY_VERSION,
    )
    results: dict[str, Any] = {}

    for question, income, count in (
        ("Q1", "45000", 1),
        ("Q2", "45001", 1),
        ("Q3", "45000", 2),
        ("Q4", "45000", 3),
        ("Q5", "44900", 2),
        ("Q6", "44901", 2),
        ("Q7", "44899", 2),
        ("Q8", "54900", 2),
        ("Q9", "500000", 2),
    ):
        results[question] = calculate_wff_scenario(wff_scenario(income, child_count=count))

    results["Q13"] = calculate_wff_scenario(
        wff_scenario("45000", children=[child(qualifies=UNKNOWN)])
    )
    results["Q14"] = calculate_wff_scenario(
        wff_scenario("45000", children=[child(), child(qualifies=UNKNOWN)])
    )
    results["Q15"] = calculate_wff_scenario(
        wff_scenario("55000", child_count=2, partnered=True, partner_income="0")
    )
    results["Q16"] = calculate_wff_scenario(wff_scenario("55000", child_count=2, partnered=True))
    results["Q17"] = calculate_wff_scenario(
        wff_scenario("30000", partnered=True, partner_income="0")
    )
    results["Q18"] = calculate_wff_scenario(wff_scenario("30000", partnered=True))
    results["Q19"] = calculate_wff_scenario(
        wff_scenario("30000", net_income="30000", hours=UNKNOWN)
    )
    results["Q20"] = calculate_wff_scenario(
        wff_scenario("30000", net_income="30000", hours=EXCLUDED)
    )
    results["Q21"] = calculate_wff_scenario(
        wff_scenario("65000", children=[child(cohort=BestStartCohort.OTHER_COHORT_UNSUPPORTED)])
    )
    results["Q22"] = results["Q21"]
    results["Q23"] = calculate_wff_scenario(
        wff_scenario("65000", children=[child(cohort=BestStartCohort.UNKNOWN)])
    )
    results["Q24"] = calculate_wff_scenario(
        wff_scenario(
            "65000",
            children=[
                child(
                    cohort=BestStartCohort.IN_SUPPORTED_COHORT,
                    best_start_eligibility=UNKNOWN,
                )
            ],
        )
    )
    results["Q25"] = calculate_wff_scenario(
        wff_scenario(
            "30000",
            net_income="30000",
            children=[child(cohort=BestStartCohort.IN_SUPPORTED_COHORT)],
        )
    )
    results["Q26"] = calculate_wff_scenario(
        wff_scenario(
            "30000",
            children=[child(cohort=BestStartCohort.IN_SUPPORTED_COHORT)],
        )
    )
    results["Q30"] = calculate_wff_scenario(wff_scenario("50000"), when=date(2025, 6, 1))

    results["Q31_Q33_g2_assumption"] = {
        rent: calculate_as(as_scenario(rent=rent), as_parameters) for rent in ("599", "600", "601")
    }
    results["Q34_Q35_single_jobseeker_area1"] = {
        rent: calculate_as(single_jobseeker(rent=rent), as_parameters) for rent in ("93", "94")
    }
    results["Q36_Q37_single_jobseeker_area1"] = {
        rent: calculate_as(single_jobseeker(rent=rent), as_parameters) for rent in ("1000", "1100")
    }
    results["Q38_Q39_maxima"] = {
        "single_no_children": {
            area.value: calculate_as(single_jobseeker(rent="2000", area=area), as_parameters)
            for area in Area
        },
        "couple_two_children": {
            area.value: calculate_as(
                as_scenario(
                    rent="2000",
                    income=None,
                    assets="0",
                    area=area,
                    category=ClaimantCategory.JOBSEEKER_SUPPORT,
                ),
                as_parameters,
            )
            for area in Area
        },
    }
    results["Q40_Q42"] = calculate_as(as_scenario(area=None), as_parameters)
    results["Q43"] = calculate_as(as_scenario(rent=None), as_parameters)
    results["Q44_qualifying_cost_650"] = calculate_as(as_scenario(rent="650"), as_parameters)
    results["Q45_Q46"] = calculate_as(as_scenario(tenure=TenureType.HOMEOWNER), as_parameters)
    results["Q47_Q49"] = {
        assets: calculate_as(single_jobseeker(assets=assets), as_parameters)
        for assets in ("8099", "8100", "8101")
    }
    results["Q50_Q52"] = {
        "verified_zero": calculate_as(single_jobseeker(assets="0"), as_parameters),
        "unknown": calculate_as(single_jobseeker(assets=None), as_parameters),
    }
    results["Q54_Q55_g2_assumption"] = {
        income: calculate_as(as_scenario(income=income), as_parameters)
        for income in ("1346", "1347", "1446")
    }
    results["Q56_g2_assumption"] = {
        rent: calculate_as(as_scenario(rent=rent), as_parameters) for rent in ("600", "700")
    }
    results["Q57_g2_assumption"] = {
        area.value: calculate_as(as_scenario(area=area), as_parameters)
        for area in (Area.AREA_1, Area.AREA_2)
    }
    results["Q58"] = calculate_as(as_scenario(area=None), as_parameters)

    g2_wff = wff_scenario(
        "50000",
        child_count=2,
        partnered=True,
        partner_income="20000",
        net_income="70000",
    )
    results["Q59"] = combined(g2_wff, as_scenario(area=None))
    results["Q60"] = combined(
        replace(g2_wff, children=[child(), child(qualifies=UNKNOWN)]),
        as_scenario(),
    )
    results["Q61"] = {
        "wff": results["Q26"],
        "accommodation_supplement": calculate_as(as_scenario(), as_parameters),
    }
    results["Q62"] = combined(
        replace(g2_wff, household_eligibility=UNKNOWN),
        as_scenario(household_eligibility=UNKNOWN),
    )
    results["Q63"] = combined(
        replace(g2_wff, household_eligibility=EXCLUDED),
        as_scenario(household_eligibility=EXCLUDED),
    )
    future_birth_child = wff_request()["children"][0] | {"date_of_birth": "2027-01-01"}
    results["Q64"] = api_validation(
        "/wff/calculate",
        wff_request(children=[future_birth_child]),
    )
    results["Q65"] = api_validation(
        "/accommodation-supplement/calculate",
        as_request(weekly_accommodation_costs="-500"),
    )
    results["Q66"] = api_validation(
        "/accommodation-supplement/calculate",
        as_request(weekly_accommodation_costs="six hundred dollars"),
    )

    deterministic = wff_scenario("45000")
    deterministic_as = as_scenario()
    results["Q70"] = {
        "runs": 10_000,
        "distinct_results": len(
            {
                json.dumps(
                    {
                        "wff": wff_result(calculate_wff(deterministic, wff_parameters)),
                        "accommodation_supplement": calculate_as(
                            deterministic_as,
                            as_parameters,
                        ),
                    },
                    sort_keys=True,
                )
                for _ in range(10_000)
            }
        ),
    }

    OUTPUT.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
