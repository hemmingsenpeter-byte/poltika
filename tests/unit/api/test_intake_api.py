"""v0.3 Task 1b.5 (ADR-0016): the conditional answer on
/household/calculate and the stateless /household/intake route."""

from __future__ import annotations

import copy
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from tests.unit.api.test_household_api import _payload

client = TestClient(app)
G1 = "g1_sole_parent_two_children_non_beneficiary"


def _calc(payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/household/calculate", json=payload)
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def _intake(payload: dict[str, Any], **kw: Any) -> Any:
    return client.post("/household/intake", json={"household": payload, **kw})


def _outcomes(body: dict[str, Any]) -> dict[str, Any]:
    return {**body["wff"], "accommodation_supplement": body["accommodation_supplement"]}


def _identity(body: dict[str, Any]) -> tuple[Any, ...]:
    return (body["result_id"], body["wff"], body["accommodation_supplement"])


def test_complete_household_has_no_resolution() -> None:
    body = _calc(_payload())
    # The in-work tax credit waits on its rate, not a fact: nothing to ask.
    assert body["resolution"] is None


def test_missing_category_gives_branches_but_no_calculated_amount() -> None:
    body = _calc(_payload(G1, claimant_category=None))
    assert body["accommodation_supplement"]["outcome"] == "needs_review"
    res = body["resolution"]
    missing = {m["fact"]: m for m in res["missing"]}
    category = missing["accommodation_supplement.claimant_category"]
    assert category["kind"] == "enum" and category["rule"]
    assert len(category["answers"]) == 6 and all(a["label"] for a in category["answers"])
    assert len(res["branches"]) == 6
    # The real category's branch reproduces the complete household.
    full = _calc(_payload(G1))
    real = next(
        b for b in res["branches"]
        if b["assignment"][0]["value"] == _payload(G1)["accommodation_supplement"]["claimant_category"]
    )
    assert real["components"]["accommodation_supplement"] == {
        "outcome": "calculated",
        "value": full["accommodation_supplement"]["value"],
    }
    bounds = res["bounds"]["accommodation_supplement"]
    assert bounds["branches"] == 6 and not bounds["complete"] and bounds["kind"] == "bounds"
    assert res["next_question"]["fact"] == "accommodation_supplement.claimant_category"
    assert res["summary"][0].startswith("Poltika can't give one figure without")


def test_conditional_summary_preserves_the_engine_half_cent() -> None:
    payload = _payload(G1)
    payload["wff"]["household_eligibility"] = "unknown"
    payload["wff"]["family_scheme_income"]["claimant_amount"] = "50001"
    body = _calc(payload)
    res = body["resolution"]
    values = [
        Decimal(branch["components"]["family_tax_credit"]["value"])
        for branch in res["branches"]
        if branch["components"]["family_tax_credit"]["outcome"] == "calculated"
    ]
    assert values and any(value != value.quantize(Decimal("0.01")) for value in values)
    text = "\n".join(res["summary"])
    for value in values:
        # Compare the text with the actual engine output; no new statutory
        # expected amount is introduced by this transport regression.
        assert f"family tax credit ${value:,f} a year" in text
    assert body["wff"]["family_tax_credit"]["outcome"] == "needs_review"


def test_intake_asks_then_is_ready_with_the_full_result() -> None:
    full = _payload(G1)
    partial = copy.deepcopy(full)
    partial["wff"]["household_eligibility"] = "unknown"
    step = _intake(partial).json()
    assert step["status"] == "ask"
    question = step["question"]
    assert question["fact"] == "wff.household_eligibility"
    assert [a["value"] for a in question["answers"]] == ["verified", "excluded"]
    assert step["calculation"]["resolution"] is not None

    done = _intake(partial, answers=[{"fact": question["fact"], "answer": "verified"}]).json()
    assert done["status"] == "ready" and done["question"] is None
    assert _identity(done["calculation"]) == _identity(_calc(full))


def test_intake_numeric_answer_and_child_fact() -> None:
    full = _payload(G1)
    partial = copy.deepcopy(full)
    partial["accommodation_supplement"]["weekly_income"] = None
    partial["wff"]["children"][0]["best_start_cohort"] = "unknown"
    answers: list[dict[str, str]] = []
    for _ in range(5):
        step = _intake(partial, answers=answers).json()
        if step["status"] != "ask":
            break
        fact = step["question"]["fact"]
        value = (
            full["accommodation_supplement"]["weekly_income"]
            if fact == "accommodation_supplement.weekly_income"
            else full["wff"]["children"][0]["best_start_cohort"]
        )
        assert fact in ("accommodation_supplement.weekly_income", "children[0].best_start_cohort")
        answers.append({"fact": fact, "answer": str(value)})
    assert step["status"] == "ready" and len(answers) == 2
    assert _identity(step["calculation"]) == _identity(_calc(full))


def test_declined_fact_gives_incomplete_with_resolution() -> None:
    partial = _payload(G1)
    partial["wff"]["household_eligibility"] = "unknown"
    step = _intake(partial, declined=["wff.household_eligibility"]).json()
    assert step["status"] == "incomplete" and step["question"] is None
    assert [q["fact"] for q in step["remaining"]] == ["wff.household_eligibility"]
    res = step["calculation"]["resolution"]
    assert len(res["branches"]) == 2
    assert step["calculation"]["wff"]["family_tax_credit"]["outcome"] == "needs_review"


@pytest.mark.parametrize(
    ("label", "message"),
    [
        ("wff.children.best_start_cohort", "child"),
        ("children[9].best_start_cohort", "child"),
        ("children[-1].best_start_cohort", "not a fact label"),
        ("wff.no_such_fact", "not a catalogued fact"),
        ("nonsense", "not a fact label"),
    ],
)
def test_invalid_declined_labels_are_422(label: str, message: str) -> None:
    partial = _payload(G1)
    partial["wff"]["children"][0]["best_start_cohort"] = "unknown"
    response = _intake(partial, declined=["wff.household_eligibility", label])
    assert response.status_code == 422
    assert "declined[1]" in response.json()["detail"]
    assert message in response.json()["detail"]


@pytest.mark.parametrize("label", ["children[0].best_start_cohort", "children[00].best_start_cohort"])
def test_declined_child_fact_is_not_asked_again(label: str) -> None:
    partial = _payload(G1)
    partial["wff"]["children"][0]["best_start_cohort"] = "unknown"
    response = _intake(partial, declined=[label], asked=["best_start"])
    assert response.status_code == 200
    step = response.json()
    assert step["status"] == "incomplete" and step["question"] is None
    assert [q["fact"] for q in step["remaining"]] == ["children[0].best_start_cohort"]
    assert step["calculation"]["wff"]["best_start"]["outcome"] == "needs_review"


def test_asked_components_limit_the_questions() -> None:
    partial = _payload(G1, claimant_category=None)
    partial["wff"]["household_eligibility"] = "unknown"
    step = _intake(partial, asked=["accommodation_supplement"]).json()
    assert step["question"]["fact"] == "accommodation_supplement.claimant_category"
    assert all("accommodation_supplement" in q["blocks"] for q in step["remaining"])


@pytest.mark.parametrize(
    ("answers", "message"),
    [
        ([{"fact": "wff.household_eligibility", "answer": "maybe"}], "admissible"),
        ([{"fact": "wff.no_such_fact", "answer": "verified"}], "not a catalogued fact"),
        ([{"fact": "nonsense", "answer": "verified"}], "not a fact label"),
        ([{"fact": "children[9].best_start_cohort", "answer": "unknown"}], "child"),
        ([{"fact": "wff.children.qualifies_whole_year", "answer": "verified"}], "child"),
        ([{"fact": "wff.children.best_start_cohort", "answer": "outside_best_start_entitlement"}], "child"),
        ([{"fact": "wff.children.best_start_no_disqualifying_payment", "answer": "verified"}], "child"),
        ([{"fact": "accommodation_supplement.weekly_income", "answer": "-5"}], "non-negative"),
    ],
)
def test_inadmissible_answers_are_422(answers: list[dict[str, str]], message: str) -> None:
    partial = _payload(G1)
    partial["wff"]["household_eligibility"] = "unknown"
    response = _intake(partial, answers=answers)
    assert response.status_code == 422
    assert "answers[0]" in response.json()["detail"] and message in response.json()["detail"]


def test_unknown_component_and_fields_are_422() -> None:
    assert _intake(_payload(), asked=["no_such"]).status_code == 422
    assert _intake(_payload(), asked=[]).status_code == 422
    assert client.post("/household/intake", json={"household": _payload(), "extra": 1}).status_code == 422


def test_openapi_lists_the_route_and_field() -> None:
    schema = client.get("/openapi.json").json()
    assert "/household/intake" in schema["paths"]
    assert "resolution" in schema["components"]["schemas"]["HouseholdCalculationResponse"]["properties"]
