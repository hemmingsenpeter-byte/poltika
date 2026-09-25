"""Runs the v0.1 question set through Poltika and writes results.json.

Every number in calculations.md comes from this script's output, not from
hand arithmetic or model memory. Run from the repository root:

    uv run --extra dev python review_packets/v0_1_question_set/run_questions.py

Poltika v0.1 models Working for Families (2026-27) and the Accommodation
Supplement only. It has no income tax module, so income tax questions are not
run here (see calculations.md).
"""

from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffResult,
    WffScenario,
    calculate_wff,
    run_wff_module,
)
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import CodeIdentity, ScenarioRecord, run_scenario

ROOT = Path(__file__).resolve().parents[2]
WFF_DIR = ROOT / "policy_specs" / "working_for_families"
AS_DIR = ROOT / "policy_specs" / "accommodation_supplement"
DATE = date(2026, 6, 1)
V = "0.1.0"
OUT = Path(__file__).with_name("results.json")
V_ = FactStatus.VERIFIED
U_ = FactStatus.UNKNOWN


def child(cohort: BestStartCohort = BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
          qualifies: FactStatus = V_) -> ChildFacts:
    return ChildFacts(qualifies_whole_year=qualifies, best_start_cohort=cohort,
                      best_start_no_disqualifying_payment=V_)


def household(income: str | None, children: int | list[ChildFacts] = 1, *,
              partner: str | None = None, partnered: bool = False,
              net: str | None = None, **overrides: Any) -> WffScenario:
    """An ordinary in-work, non-beneficiary household with every non-income
    fact verified unless overridden. `net` is the ME 3 net family scheme
    income, needed only by MFTC; None leaves it unverified."""
    kids = [child() for _ in range(children)] if isinstance(children, int) else children
    total = None if income is None else Decimal(income) + (Decimal(partner) if partner else 0)
    fsi = None
    if income is not None:
        fsi = VerifiedIncome(claimant_amount=Decimal(income),
                             partner_amount=Decimal(partner) if partner is not None else None)
    base = WffScenario(
        household_eligibility=V_, extra_instalment_status=V_, children=kids,
        partner_status=PartnerStatus.PARTNERED if partnered else PartnerStatus.SINGLE,
        family_scheme_income=fsi,
        net_family_scheme_income=Decimal(net) if net is not None else None,
        net_family_scheme_income_me3_attested=net is not None,
        in_work_eligibility=V_, ftc_iwtc_protected_or_direct_abatement=V_,
        mc6a_veterans_payment=V_, mc6b_disqualifying_payment=V_,
        minimum_family_full_time_earner_weeks=V_, best_start_no_shared_care=V_,
        best_start_protected_credit=V_,
    )
    del total
    return replace(base, **overrides)


def wff(scenario: WffScenario, modelled_date: date = DATE, policy_dir: Path = WFF_DIR) -> dict[str, Any]:
    result = run_wff_module(policy_dir, modelled_date, scenario, requested_policy_version=V)
    return components(result)


def components(result: WffResult) -> dict[str, Any]:
    out = {}
    for name in ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"):
        c = getattr(result, name)
        out[name] = {"outcome": c.outcome, "value": None if c.value is None else str(c.value),
                     "reason": c.reason}
    return out


def api(path: str, body: Any) -> dict[str, Any]:
    with TestClient(app) as client:
        r = client.post(path, json=body)
    detail = r.json().get("detail") if r.headers.get("content-type", "").startswith("application/json") else r.text
    if isinstance(detail, list):
        detail = [{"loc": d.get("loc"), "msg": d.get("msg")} for d in detail]
    return {"status": r.status_code, "detail": detail if r.status_code != 200 else None}


def wff_request(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "modelled_date": "2026-06-01", "requested_policy_version": V,
        "household_eligibility": "verified", "extra_instalment_status": "verified",
        "partner_status": "single",
        "family_scheme_income": {"claimant_amount": "50000"},
        "in_work_eligibility": "verified", "ftc_iwtc_protected_or_direct_abatement": "verified",
        "mc6a_veterans_payment": "verified", "mc6b_disqualifying_payment": "verified",
        "minimum_family_full_time_earner_weeks": "verified", "best_start_no_shared_care": "verified",
        "best_start_protected_credit": "verified",
        "children": [{"qualifies_whole_year": "verified",
                      "best_start_cohort": "outside_best_start_entitlement",
                      "best_start_no_disqualifying_payment": "verified"}],
    }
    body.update(overrides)
    return body


def edited_policy(edit: Any) -> Path:
    """A temporary copy of the WFF policy directory with `edit` applied to
    its parsed policy.yaml (scratch only; the repository is never changed)."""
    tmp = Path(tempfile.mkdtemp()) / "working_for_families"
    shutil.copytree(WFF_DIR, tmp)
    data = yaml.safe_load((tmp / "policy.yaml").read_text())
    edit(data)
    (tmp / "policy.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    return tmp


def param(data: dict[str, Any], pid: str) -> dict[str, Any]:
    return next(p for p in data["parameters"] if p["id"] == pid)


def main() -> None:
    r: dict[str, Any] = {}

    # Q14/Q15: Aroha, sole parent, one child aged 8 (outside Best Start).
    r["Q14"] = wff(household("45000"))
    r["Q15"] = wff(household("45001"))

    # Q16: $70,000 with one, two and three children (partnered, split 35k/35k).
    r["Q16"] = {n: wff(household("35000", n, partner="35000", partnered=True)) for n in (1, 2, 3)}

    # Q17/Q19: age boundaries. Poltika takes the caller's Best Start cohort
    # classification, not a date of birth.
    r["Q17"] = {
        "in_supported_cohort": wff(household("65000", [child(BestStartCohort.IN_SUPPORTED_COHORT)])),
        "other_cohort_unsupported": wff(household("65000", [child(BestStartCohort.OTHER_COHORT_UNSUPPORTED)])),
    }
    # Q18: newborn born 1 April 2026 -- a 2026 birth, outside the one
    # calculable cohort (born 2024-04-01 to 2025-03-31).
    r["Q18"] = wff(household("32500", [child(BestStartCohort.OTHER_COHORT_UNSUPPORTED)],
                             partner="32500", partnered=True))

    # Q20/Q21: MFTC. The question gives gross income only; MFTC needs the
    # ME 3 net family scheme income, which Poltika does not compute.
    r["Q20"] = wff(household("30000", partner="0", partnered=True))
    r["Q21"] = wff(household("30000", partnered=True))  # partner amount unknown

    # Q22: James, $55,000, two children, partnered, partner income unknown.
    r["Q22"] = wff(household("55000", 2, partnered=True))

    # Q23/Q41: dates without a loaded parameter set.
    r["Q23"] = {"2026-03-31": wff(household("50000"), date(2026, 3, 31)),
                "2026-04-01": wff(household("50000"), date(2026, 4, 1))}
    r["Q41"] = wff(household("50000"), date(2025, 6, 1))

    # Q24: a required parameter covers only 1 April-30 June 2026.
    def truncate(data: dict[str, Any]) -> None:
        param(data, "family_tax_credit_eldest_child")["values"][0]["effective_to"] = date(2026, 7, 1)
    r["Q24"] = wff(household("50000"), date(2026, 5, 15), edited_policy(truncate))

    # Q28/Q59/Q61/Q64/Q40: malformed or missing inputs, through the API.
    r["Q28"] = api("/wff/calculate", wff_request(family_scheme_income={"claimant_amount": "-20000"}))
    r["Q61"] = api("/wff/calculate", wff_request(family_scheme_income={"claimant_amount": "sixty thousand dollars"}))
    no_children = wff_request(); del no_children["children"]
    r["Q64"] = api("/wff/calculate", no_children)
    no_date = wff_request(); del no_date["modelled_date"]
    r["Q40"] = api("/wff/calculate", no_date)

    # Q29: couple, two children, $60,000 + $30,000, then +$1 to person A.
    r["Q29"] = {"base": wff(household("60000", 2, partner="30000", partnered=True)),
                "plus_1": wff(household("60001", 2, partner="30000", partnered=True))}

    # Q30: $90,000 (45k/45k) with no children and with two.
    r["Q30"] = {"no_children": wff(household("45000", 0, partner="45000", partnered=True)),
                "two_children": wff(household("45000", 2, partner="45000", partnered=True))}

    # Q33-Q35, Q42: unknown facts.
    r["Q33"] = wff(household("50000", [child(), child(qualifies=U_)]))
    r["Q34"] = wff(household("50000", [child(BestStartCohort.UNKNOWN, U_) for _ in range(3)]))
    r["Q35"] = wff(household("35000", household_eligibility=U_))
    r["Q42"] = wff(household("50000", in_work_eligibility=U_))

    # Q36/Q37: partnered with no partner record vs partner $0 verified.
    # Neither question states children: with none the household is outside
    # WFF; the one-child runs are an illustrative assumption.
    r["Q36_Q37"] = {
        "no_children_partner_missing": wff(household("50000", 0, partnered=True)),
        "no_children_partner_zero": wff(household("50000", 0, partner="0", partnered=True)),
        "one_child_partner_missing": wff(household("50000", 1, partnered=True)),
        "one_child_partner_zero": wff(household("50000", 1, partner="0", partnered=True)),
    }

    # Q43: $0.01 across the FTC abatement threshold ($44,900) and the Best
    # Start threshold ($79,000; supported-cohort child).
    r["Q43"] = {
        "ftc_44900.00": wff(household("44900.00")), "ftc_44900.01": wff(household("44900.01")),
        "ftc_44901.00": wff(household("44901.00")),
        "bs_79000.00": wff(household("79000.00", [child(BestStartCohort.IN_SUPPORTED_COHORT)])),
        "bs_79000.01": wff(household("79000.01", [child(BestStartCohort.IN_SUPPORTED_COHORT)])),
        "bs_79001.00": wff(household("79001.00", [child(BestStartCohort.IN_SUPPORTED_COHORT)])),
    }

    # Q44: $1 steps from $40,000 to $100,000 (one supported-cohort child).
    params = load_policy_parameters(WFF_DIR, DATE, requested_policy_version=V)
    prev: dict[str, Decimal] = {}
    steps: dict[str, dict[str, int]] = {"family_tax_credit": {}, "best_start": {}}
    first_change: dict[str, int] = {}
    for income in range(40000, 100001):
        res = calculate_wff(household(str(income), [child(BestStartCohort.IN_SUPPORTED_COHORT)]), params)
        for name in steps:
            value = getattr(res, name).value
            assert value is not None
            if name in prev:
                delta = str(value - prev[name])
                steps[name][delta] = steps[name].get(delta, 0) + 1
                if delta != "0" and delta != "0.000" and delta != "0.00" and name not in first_change:
                    first_change[name] = income
            prev[name] = value
    r["Q44"] = {"step_counts": steps, "first_income_with_a_change": first_change}

    # Q45: 10,000 identical runs.
    scenario = household("45000")
    distinct = {json.dumps(components(calculate_wff(scenario, params)), sort_keys=True) for _ in range(10000)}
    r["Q45"] = {"runs": 10000, "distinct_outputs": len(distinct)}

    # Q56/Q57: an unknown fact that affects only MFTC.
    r["Q56_Q57"] = wff(household("50000", partnered=True, partner="0",
                                 minimum_family_full_time_earner_weeks=U_))

    # Q62/Q63: parameter-file defects, loaded through a scratch copy.
    def percent_rate(data: dict[str, Any]) -> None:
        param(data, "family_tax_credit_abatement_rate")["values"][0]["value"] = 27.5
    def open_ended(data: dict[str, Any]) -> None:
        param(data, "family_tax_credit_eldest_child")["values"][0]["effective_to"] = None
    for key, edit in (("Q62", percent_rate), ("Q63", open_ended)):
        try:
            r[key] = {"loaded": True, "result": wff(household("50000"), DATE, edited_policy(edit))}
        except Exception as exc:  # noqa: BLE001 -- recording the refusal is the point
            r[key] = {"loaded": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}

    # Q70: the full trace for golden household g2 (ids and headline only).
    gh = yaml.safe_load((ROOT / "policy_specs/wff_as_interaction/golden_households.yaml").read_text())
    import sys

    sys.path.insert(0, str(ROOT))
    from tests.conftest import as_scenario_from_yaml, wff_scenario_from_yaml
    h = next(x for x in gh["households"] if x["id"] == "g2_couple_two_children_income_abated_both")
    from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
    rec = ScenarioRecord(
        household=CombinedHouseholdScenario(wff=wff_scenario_from_yaml(h["wff"]),
                                            accommodation_supplement=as_scenario_from_yaml(h["accommodation_supplement"]),
                                            as_claimant_is_wff_claimant_or_partner=V_),
        wff_lookup_date=DATE, as_lookup_date=DATE,
        assessment_week=AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8)),
        requested_wff_policy_version=V, requested_as_policy_version="0.1.1")
    run = run_scenario(rec, WFF_DIR, AS_DIR, code=CodeIdentity("0.1.0", None, None, None))
    report = build_combined_provenance_report(run, WFF_DIR, AS_DIR)
    ftc = report["working_for_families"]["components"][0]
    r["Q70"] = {"component": ftc["component_id"], "value": ftc["value"],
                "parameters": [(p["parameter_id"], p["value"], p["source_id"], p["locator"]) for p in ftc["parameters"]],
                "inputs": [i["name"] for i in ftc["inputs"]],
                "calculation_rules": ftc["calculation_rules"],
                "source_rules": [s["id"] for s in ftc["source_rules"]]}

    OUT.write_text(json.dumps(r, indent=2, default=str) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
