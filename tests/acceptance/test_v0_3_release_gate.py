"""v0.3 exit gate (BUILD_PLAN_v0_3.md), one test per row, built up as the
phases land (Task 7.1). A row whose phase isn't built yet skips with its
reason. A green run with no skips means the gate is met.
"""

from __future__ import annotations

import dataclasses
import re
import tempfile
import unicodedata
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.scenarios.microsim import analysis, explain, runner
from poltika.scenarios.microsim.reform import Reform
from poltika.scenarios.microsim.runner import run_population
from poltika.scenarios.microsim.synthetic import generate
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import (
    SYNTHETIC_LABEL,
    HouseholdCharacteristics,
    PersonRecord,
    PopulationDataset,
    PopulationHousehold,
)
from tests.acceptance.review_queue import open_reviews
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR

ROOT = Path(__file__).resolve().parents[2]
CATALOGUES = sorted((ROOT / "policy_specs").glob("*/facts.yaml"))


# Row 1: every modelled component can say what it is missing. Catalogue
# completeness is held by tests/unit/policy/test_fact_catalogs.py, and the
# intake replay by tests/unit/scenarios/test_intake.py. This row adds the
# wording check (Task 1b.1c).
@pytest.mark.parametrize("catalogue", CATALOGUES, ids=lambda p: p.parent.name)
def test_every_shipped_catalogue_has_reviewed_wording(catalogue: Path) -> None:
    status = yaml.safe_load(catalogue.read_text())["wording_status"]
    assert status == "reviewed", f"{catalogue.parent.name}: question wording is {status}"


def test_catalogues_exist_for_the_modelled_policies() -> None:
    assert {p.parent.name for p in CATALOGUES} >= {
        "working_for_families",
        "accommodation_supplement",
        "wff_as_interaction",
    }


@pytest.mark.parametrize(
    "row",
    [
        "income tax and the three core main benefits (Phases 2-3)",
        "the kernel household to disposable income (Phases 1-5)",
        "every golden household through the shared household model and graph (Phases 1, 4)",
        "one policy's output feeding another's input, explained (Phase 4)",
        "disposable income and effective marginal tax rates (Phase 5)",
        "a population run by decile and household type (Phases 5-6)",
        "the secure-environment runner exports only checked aggregates (Phase 6)",
    ],
)
def test_rows_for_later_phases(row: str) -> None:
    pytest.skip(f"not built yet: {row}")


def test_independent_review_complete() -> None:
    pending = open_reviews("v0.3")
    if pending:
        pytest.skip(f"release gate not yet met: awaiting independent review {', '.join(pending)}")


# ---------------------------------------------------------------------------
# Programme Step 1: the mechanical never-build checks (Task 1.6) and the
# interim data-governance rule P5 (Task 1.4, test part). Rows, in the order of
# BUILD_PLAN_PROGRAMME.md "What Poltika never builds":
#   - every population result carries its label (the validation grade, P4, is
#     not built yet: its row skips with that reason);
#   - no output schema scores or ranks a party or plan;
#   - no user-facing page claims a milestone Poltika hasn't reached;
#   - P5: no output disaggregated by ethnicity or iwi.
# Each check is a pure function over names or text, so the injection tests
# below prove it fails on a violation as well as passes on the repository.
# ---------------------------------------------------------------------------

_WORD_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _tokens(name: str) -> set[str]:
    """Whole words of a field name: snake_case, kebab-case and camelCase are
    split, so `partner_status` never matches `party`, and macrons are folded."""
    folded = unicodedata.normalize("NFKD", _WORD_BOUNDARY.sub("_", name))
    ascii_name = "".join(c for c in folded if not unicodedata.combining(c))
    return {t for t in re.split(r"[^a-z0-9]+", ascii_name.lower()) if t}


# Task 1.6, scoring or ranking a party or plan. A name is refused if it holds
# (a) a party word or manifesto, (b) a score word (a validation or ledger
# score is monitored, never targeted, so a future field for one must be added
# to SCORE_ALLOWED with its reason, deliberately), or (c) a judgement word
# next to the thing judged: best_plan, plan_rank, preferred_option,
# winning_reform. Deliberately NOT refused, checked against the repository:
# `authority_rank` (a source's authority, workbench registry), `best_start`
# (a payment), `ranked` (the intake planner's question order),
# `winners_losers_*` (households' gain or loss, Step 8.1), `options`
# (the reforms a caller compares) and `partner_*` (a household member).
PARTY_WORDS = frozenset({"party", "parties", "manifesto", "manifestos"})
SCORE_WORDS = frozenset({"score", "scores", "scoring", "scored"})
JUDGED_THINGS = frozenset(
    {
        "plan", "plans", "party", "parties", "policy", "policies", "option",
        "options", "scenario", "scenarios", "reform", "reforms", "proposal",
        "proposals", "manifesto", "manifestos",
    }
)  # fmt: skip
JUDGEMENTS = frozenset(
    {
        "rank", "ranks", "ranked", "ranking", "rankings", "best", "better",
        "worst", "preferred", "recommended", "optimal", "winner", "winners",
        "winning", "wins", "rating", "ratings", "verdict", "leaderboard",
    }
)  # fmt: skip
SCORE_ALLOWED: frozenset[str] = frozenset()


def scoring_or_ranking_names(names: Iterable[str]) -> list[str]:
    bad: set[str] = set()
    for name in names:
        words = _tokens(name)
        if name in SCORE_ALLOWED:
            continue
        if (
            words & PARTY_WORDS
            or words & SCORE_WORDS
            or (words & JUDGED_THINGS and words & JUDGEMENTS)
        ):
            bad.add(name)
    return sorted(bad)


# Task 1.4 / P5: no output disaggregated by ethnicity or iwi. Whole words, so
# `ethnic*` covers ethnicity and ethnic_group. Pacific peoples are an
# ethnicity group, but `pacific` alone is a place word and is not refused.
ETHNICITY_WORDS = frozenset(
    {"ethnic", "ethnicity", "ethnicities", "iwi", "hapu", "maori", "pasifika", "race", "racial"}
)


def ethnicity_names(names: Iterable[str]) -> list[str]:
    bad: set[str] = set()
    for name in names:
        words = _tokens(name)
        if words & ETHNICITY_WORDS or any(w.startswith("ethnic") for w in words):
            bad.add(name)
    return sorted(bad)


def _walk_keys(node: Any) -> Iterator[str]:
    """Every dict key, at any depth: the output schema of a payload. Values
    are data (region names, option labels) and are not read."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            yield from _walk_keys(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_keys(value)


# Keys whose string value names a part of an output rather than carrying data:
# a block, column or table identifier, or a grouping dimension.
_STRUCTURAL_KEYS = frozenset({"id", "dimension", "table_id", "block_id", "column_id", "group"})


def _walk_structural_values(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _STRUCTURAL_KEYS and isinstance(value, str):
                yield value
            yield from _walk_structural_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_structural_values(value)


def _schema_property_names(schema: Any) -> Iterator[str]:
    """Property names in an OpenAPI document's component schemas."""
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "properties" and isinstance(value, dict):
                yield from (str(name) for name in value)
            yield from _schema_property_names(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from _schema_property_names(value)


def _dataclass_field_names(*types: type) -> list[str]:
    names: list[str] = []
    for tp in types:
        names.extend(f.name for f in dataclasses.fields(tp))
    return names


def _output_types() -> list[type]:
    """Every dataclass the population and microsim analysis outputs are built
    from, found rather than listed, so a new output type is checked too."""
    found: list[type] = []
    for module in (analysis, runner, explain):
        found.extend(
            obj
            for obj in vars(module).values()
            if isinstance(obj, type)
            and dataclasses.is_dataclass(obj)
            and obj.__module__ == module.__name__
        )
    return found


@pytest.fixture(scope="module")
def toy_population() -> Iterator[tuple[PopulationDataset, TestClient]]:
    from tests.unit.scenarios.microsim.test_synthetic import _spec

    population, _ = generate(_spec(households=40))
    with tempfile.TemporaryDirectory() as tmp, pytest.MonkeyPatch.context() as patch:
        path = Path(tmp) / "population.json"
        path.write_text(population.model_dump_json())
        patch.setenv("POLTIKA_POPULATION_PATH", str(path))
        yield population, TestClient(app)


_THRESHOLD = {
    "reform_id": "never-build-gate",
    "overrides": [
        {
            "policy_id": "working_for_families",
            "parameter_id": "family_tax_credit_abatement_threshold",
            "operation": "set",
            "value": "50000",
        }
    ],
}


@pytest.fixture(scope="module")
def payloads(toy_population: tuple[PopulationDataset, TestClient]) -> dict[str, Any]:
    """The population outputs a caller can fetch, as served."""
    _, client = toy_population
    run = client.post("/microsim/runs", json={"reform": _THRESHOLD})
    assert run.status_code == 200, run.text
    run_id = run.json()["run_id"]
    results = client.post(
        "/workbench/results",
        json={"scenario": {"name": "gate"}, "options": [{"label": "A", "reform": _THRESHOLD}]},
    )
    assert results.status_code == 200, results.text
    return {
        "population": client.get("/microsim/population").json(),
        "run": run.json(),
        "stored run": client.get(f"/microsim/runs/{run_id}").json(),
        "workbench results": results.json(),
        "workbench registry": client.get("/workbench/registry").json(),
    }


def _all_output_names(
    toy_population: tuple[PopulationDataset, TestClient], payloads: dict[str, Any]
) -> list[str]:
    _, client = toy_population
    names = list(_schema_property_names(client.app.openapi()["components"]["schemas"]))  # type: ignore[attr-defined]
    names += _dataclass_field_names(*_output_types())
    for payload in payloads.values():
        names += list(_walk_keys(payload))
        names += list(_walk_structural_values(payload))
    return names


# Row 2: every population result carries its label. Held three ways: the run
# record, each served payload, and the explanation's first sentence.
def test_every_population_result_carries_its_label(
    toy_population: tuple[PopulationDataset, TestClient], payloads: dict[str, Any]
) -> None:
    population, _ = toy_population
    assert {"label", "synthetic"} <= {f.name for f in dataclasses.fields(runner.PopulationRun)}
    run = run_population(
        population, Reform.model_validate(_THRESHOLD), WFF_POLICY_DIR, AS_POLICY_DIR,
        code=CodeIdentity("gate", None, None, None),
    )  # fmt: skip
    assert run.label.strip() and run.label == population.label == SYNTHETIC_LABEL
    assert run.synthetic is True
    for name in ("population", "run", "stored run"):
        body = payloads[name]
        assert body["label"] == SYNTHETIC_LABEL and body["synthetic"] is True, name
    assert payloads["run"]["explanation"].startswith(SYNTHETIC_LABEL)
    results = payloads["workbench results"]
    assert results["population_label"] == SYNTHETIC_LABEL and results["synthetic"] is True


def test_every_population_result_carries_its_validation_grade() -> None:
    pytest.skip(
        "not built yet: no validation-grade field exists in code. Only `label` "
        "(SYNTHETIC_LABEL) does. The P4 grades (Development, Public-data, "
        "IDI-calibrated) arrive with BUILD_PLAN_PROGRAMME.md Task 7.2"
    )


# Row 3: no output schema scores or ranks a party or plan.
def test_no_output_schema_scores_or_ranks_a_party_or_plan(
    toy_population: tuple[PopulationDataset, TestClient], payloads: dict[str, Any]
) -> None:
    names = _all_output_names(toy_population, payloads)
    assert len(names) > 200, "the check found almost nothing to read"
    assert scoring_or_ranking_names(names) == []


# Row 4: no user-facing page claims a milestone not yet reached. User-facing
# is what a person is served or told to read: every HTML page the app serves,
# the README, and the orientation, pilot and demo docs. Roadmaps, build plans,
# doctrine and research notes are about the future by design and are not read.
# Phase-gated terms come from "Phases, milestones and validation gates" and
# "What Poltika never builds". A milestone leaves GATED_TERMS only when Pete
# records its graduation (Step 6).
GATED_TERMS = {
    "digital twin": "Phase 5 (M16-M28)",
    "decision intelligence": "Phase 6",
    "decision infrastructure": "Phase 7",
    "scientific layer": "Phase 8",
    "policy search": "Step 23, after causal relationships are credible",
    "predictive": "after the ledger's record supports it",
    "forecast": "no black-box AI forecast; after the ledger's record supports it",
}
# A sentence naming a gated term is allowed when it also says the thing is
# absent or future. "will" is not here: a claim of a coming twin is still a
# claim of a twin.
# Negation must sit next to the term: within six words before it, or a verb
# negation within four words after it ("a digital twin is not built"). A "no"
# or "yet" elsewhere in the sentence does not excuse the claim, and nor does
# one in another clause: a colon, semicolon or dash ends the negation's reach
# ("No setup required; Poltika is a digital twin" is a claim).
_NEGATES_BEFORE = frozenset(
    {
        "not", "no", "never", "isn't", "aren't", "doesn't", "don't", "cannot", "without",
        "until", "before", "planned", "future", "eventual", "eventually", "aim", "aims",
        "aspire", "aspires", "roadmap",
    }
)  # fmt: skip
_NEGATES_AFTER = frozenset({"not", "never", "isn't", "aren't", "cannot", "planned", "future"})
USER_FACING_DOCS = (
    "README.md",
    "docs/ORIENTATION.md",
    *(
        str(p.relative_to(ROOT))
        for p in sorted([*(ROOT / "docs" / "pilot").glob("*.md"), *(ROOT / "docs" / "demo").rglob("*.md")])
    ),
)


def _negated(words: list[str], start: int, length: int) -> bool:
    before = words[max(0, start - 6) : start]
    after = words[start + length : start + length + 4]
    return any(w in _NEGATES_BEFORE for w in before) or any(w in _NEGATES_AFTER for w in after)


def unreached_milestone_claims(text: str) -> list[str]:
    plain = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    plain = re.sub(r"<[^>]+>", " ", plain)
    plain = re.sub(r"[-_\s]+", " ", plain)  # "digital-twin" and a line break read the same
    claims: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n\s*\n", plain):
        clauses = [re.findall(r"[a-z0-9']+", c) for c in re.split(r"[;:\u2013\u2014]", sentence.lower())]
        for term in GATED_TERMS:
            term_words = term.split()
            if any(
                words[i : i + len(term_words)] == term_words and not _negated(words, i, len(term_words))
                for words in clauses
                for i in range(len(words) - len(term_words) + 1)
            ):
                claims.append(f"{term!r}: {sentence.strip()[:120]}")
    return claims


def _served_html_pages(client: TestClient) -> dict[str, str]:
    """Every parameterless GET route the app documents, kept if it serves HTML."""
    pages: dict[str, str] = {}
    for path, methods in app.openapi()["paths"].items():
        if "get" not in methods or "{" in path:
            continue
        response = client.get(path)
        if response.headers.get("content-type", "").startswith("text/html"):
            pages[path] = response.text
    return pages


def test_no_user_facing_page_claims_an_unreached_milestone(
    toy_population: tuple[PopulationDataset, TestClient],
) -> None:
    _, client = toy_population
    pages = _served_html_pages(client)
    assert {"/analyst", "/analyst/microsim"} <= set(pages), "the served pages were not found"
    pages.update({name: (ROOT / name).read_text() for name in USER_FACING_DOCS})
    found = {name: unreached_milestone_claims(text) for name, text in pages.items()}
    assert {name: claims for name, claims in found.items() if claims} == {}


# Row 5, P5 (Task 1.4): no output disaggregated by ethnicity or iwi. Held over
# the output schemas and payloads (as for scoring), the population schema's
# grouping dimensions, every `by_*` analysis table the code defines (found,
# not listed), and the grouping dimension each one reports.
def test_no_output_is_disaggregated_by_ethnicity_or_iwi(
    toy_population: tuple[PopulationDataset, TestClient], payloads: dict[str, Any]
) -> None:
    population, _ = toy_population
    names = _all_output_names(toy_population, payloads)
    names += [
        *(n for cls in (PersonRecord, HouseholdCharacteristics, PopulationHousehold)
          for n in cls.model_fields),
        *_walk_keys(population.model_dump(mode="json")),
    ]  # fmt: skip
    tables = {n: fn for n, fn in vars(analysis).items() if n.startswith("by_") and callable(fn)}
    assert len(tables) >= 5, "the by_* analysis tables were not found"
    run = run_population(
        population, Reform.model_validate(_THRESHOLD), WFF_POLICY_DIR, AS_POLICY_DIR,
        code=CodeIdentity("gate", None, None, None),
    )  # fmt: skip
    names += list(tables)
    names += [fn(population, run, ["family_tax_credit"]).dimension for fn in tables.values()]
    assert ethnicity_names(names) == []


# The checks above must fail on a violation as well as pass on the repository.
def test_the_checks_catch_what_they_are_for() -> None:
    assert scoring_or_ranking_names(
        ["party_score", "best_plan", "planRank", "preferred_option", "manifesto", "score"]
    ) == ["best_plan", "manifesto", "party_score", "planRank", "preferred_option", "score"]
    assert (
        scoring_or_ranking_names(
            [
                "authority_rank",
                "best_start",
                "ranked",
                "winners_losers_x",
                "options",
                "partner_status",
            ]
        )
        == []
    )
    assert ethnicity_names(["by_ethnicity", "Iwi", "ethnic_group", "Māori", "region"]) == [
        "Iwi", "Māori", "by_ethnicity", "ethnic_group",
    ]  # fmt: skip
    assert unreached_milestone_claims("<p>Poltika is a digital-twin of New Zealand.</p>")
    assert unreached_milestone_claims("Our forecast shows who wins.")
    assert not unreached_milestone_claims("Poltika is not a digital twin and makes no forecast.")
    assert unreached_milestone_claims("Poltika is a digital twin, with no setup needed.")
    assert unreached_milestone_claims("Our forecast, as yet unmatched, shows who wins.")
    assert not unreached_milestone_claims("A digital twin is not built yet.")
    # Codex recheck of #162, R1: a negation in another clause excuses nothing.
    assert unreached_milestone_claims("No setup required; Poltika is a digital twin.")
    assert unreached_milestone_claims("No login required: Poltika is a digital twin.")
    assert unreached_milestone_claims("No setup required \u2014 Poltika is a digital twin.")
    assert not unreached_milestone_claims("Setup is quick; Poltika is not a digital twin.")
    names = list(_walk_structural_values({"tables": [{"id": "by_ethnicity", "x": "iwi"}]}))
    assert ethnicity_names(names) == ["by_ethnicity"]
