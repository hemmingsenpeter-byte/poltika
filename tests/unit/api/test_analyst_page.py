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
