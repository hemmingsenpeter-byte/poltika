"""v0.1.5 Phase 6: the thin analyst page and its example requests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from poltika.api.main import app

client = TestClient(app)


def test_page_is_self_contained_html() -> None:
    response = client.get("/analyst")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert 'src="http' not in html and 'href="http' not in html  # no external assets
    for status in ("CALCULATED", "NEEDS REVIEW", "UNSUPPORTED"):
        assert status in html
    assert "/household/calculate" in html and "/analyst/examples" in html
    # Task 6.1: the household form is generated from the API's own schema.
    assert "/openapi.json" in html and "HouseholdCalculationRequest" in html


def test_every_example_request_runs() -> None:
    examples = client.get("/analyst/examples").json()
    assert len(examples) == 9
    for example in examples:
        response = client.post("/household/calculate", json=example["request"])
        assert response.status_code == 200, example["id"]
        body = response.json()
        assert set(body["explanations"]) == {
            "family_tax_credit",
            "in_work_tax_credit",
            "minimum_family_tax_credit",
            "best_start",
            "accommodation_supplement",
        }


def test_evidence_summary_reports_no_gaps_for_the_deployed_policies() -> None:
    reports = client.get("/analyst/evidence").json()
    assert [r["policy_id"] for r in reports] == ["working_for_families", "accommodation_supplement"]
    assert all(r["problems"] == [] for r in reports)


def test_pilot_case_pack_runs_and_spans_every_outcome() -> None:
    """v0.1.5 S2.2: 15 cases, each runs, and together they show every
    outcome, both unsupported categories and a shared-fact disagreement."""
    cases = client.get("/analyst/pilot-cases").json()
    assert len(cases) == 15 and all(c["description"].endswith("?") or c["description"].endswith(".") for c in cases)
    outcomes: set[str] = set()
    categories: set[str] = set()
    disagreements = 0
    for case in cases:
        response = client.post("/household/calculate", json=case["request"])
        assert response.status_code == 200, case["id"]
        body = response.json()
        components = [*body["wff"].values(), body["accommodation_supplement"]]
        outcomes |= {c["outcome"] for c in components}
        categories |= {c["category"] for c in components if c["category"]}
        disagreements += bool(body["contradictions"])
    assert outcomes == {"calculated", "needs_review", "unsupported"}
    assert categories == {"evidenced_exclusion", "not_modelled"}
    assert disagreements >= 2  # p08 (children) and p15 (claimant link)


def test_an_unverified_claimant_link_is_a_missing_fact_not_a_disagreement() -> None:
    """S2.2 finding: p15's only failed check is the unverified AS-to-WFF
    claimant link. It is coded as that missing fact, while p08's real
    disagreement (children) keeps the disagreement code."""
    cases = {c["id"]: c for c in client.get("/analyst/pilot-cases").json()}
    link = client.post("/household/calculate", json=cases["p15_claimant_link_unverified"]["request"]).json()
    ftc = link["wff"]["family_tax_credit"]
    assert ftc["code"] == "COMBINED_CLAIMANT_LINK_UNVERIFIED"
    assert ftc["missing_facts"] == ["as_claimant_is_wff_claimant_or_partner"]
    disagree = client.post("/household/calculate", json=cases["p08_children_disagree"]["request"]).json()
    assert disagree["wff"]["family_tax_credit"]["code"] == "COMBINED_SHARED_FACTS_DISAGREE"
