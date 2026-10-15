"""v0.3 Task 1b.1: the fact catalogues are complete and match the engines."""

from __future__ import annotations

import re
import types
import typing
from enum import Enum
from pathlib import Path

import pytest
from pydantic import ValidationError

from poltika.engines.simulator.accommodation_supplement import AsScenario
from poltika.engines.simulator.wff import ChildFacts, WffScenario
from poltika.policy.facts import fact_index, load_fact_catalog
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.semantics.schemas.fact_catalog import FactEntry

ROOT = Path(__file__).resolve().parents[3]
POLICIES = ROOT / "policy_specs"
CATALOGS = {
    d: load_fact_catalog(POLICIES / d)
    for d in ("working_for_families", "accommodation_supplement", "wff_as_interaction")
}
INDEX = fact_index(*CATALOGS.values())
SCOPE_OF_ENGINE = {
    "wff.py": "wff",
    "accommodation_supplement.py": "accommodation_supplement",
    "combined.py": "household",
}


def _emitted() -> set[tuple[str, str]]:
    """Every literal missing_facts id in the engines and combined runner,
    plus the ids WFF's partner-income helper computes."""
    found: set[tuple[str, str]] = set()
    for path in [
        *(ROOT / "src/poltika/engines/simulator").glob("*.py"),
        ROOT / "src/poltika/scenarios/combined.py",
    ]:
        scope = SCOPE_OF_ENGINE.get(path.name)
        if scope is None:
            continue
        for block in re.findall(r"missing_facts\s*=\s*\(([^)]*)\)", path.read_text(), re.DOTALL):
            found |= {(scope, i) for i in re.findall(r"\"([a-z0-9_.]+)\"", block)}
    found |= {("wff", "partner_status"), ("wff", "family_scheme_income.partner_amount")}
    return found


def _hint(cls: type, name: str) -> type:
    hint = typing.get_type_hints(cls)[name]
    args = (
        typing.get_args(hint)
        if isinstance(hint, types.UnionType) or typing.get_origin(hint) is typing.Union
        else (hint,)
    )
    return next(a for a in args if a is not type(None))


def _owner(entry: FactEntry) -> tuple[type, str]:
    if entry.scope == "household":
        return CombinedHouseholdScenario, entry.id
    if entry.scope == "accommodation_supplement":
        return AsScenario, entry.id
    if entry.id.startswith("children."):
        return ChildFacts, entry.id.removeprefix("children.")
    return WffScenario, entry.id.split(".")[0]


def test_every_emitted_missing_fact_has_an_entry() -> None:
    missing = sorted(key for key in _emitted() if key not in INDEX)
    assert missing == []


def test_every_entry_is_emitted_by_an_engine() -> None:
    unused = sorted(key for key in INDEX if key not in _emitted())
    assert unused == []


def test_income_tax_draft_catalog_loads_without_registering_an_engine() -> None:
    catalog = load_fact_catalog(POLICIES / "income_tax")
    assert catalog.policy_id == "income_tax"
    assert catalog.wording_status == "drafted"
    assert {entry.scope for entry in catalog.facts} == {"income_tax"}
    assert ("income_tax", "annual_taxable_income") not in INDEX


@pytest.mark.parametrize("key", sorted(INDEX), ids=lambda k: f"{k[0]}:{k[1]}")
def test_entry_domain_matches_the_engine_field(key: tuple[str, str]) -> None:
    entry = INDEX[key]
    cls, name = _owner(entry)
    hint = _hint(cls, name)
    if entry.kind in ("fact_status", "enum"):
        assert isinstance(hint, type) and issubclass(hint, Enum), f"{entry.id} is not an enum field"
        engine_values = {m.value for m in hint} - {"unknown"}
        if entry.kind == "fact_status":
            assert engine_values == {"verified", "excluded"}
        else:
            assert set(entry.domain()) == engine_values
    elif entry.kind == "count":
        assert hint is int
    elif entry.kind == "attestation":
        assert hint is bool
    else:
        assert entry.unit


def test_rule_ids_exist_in_the_specifications() -> None:
    rows = set()
    for d in ("working_for_families", "accommodation_supplement"):
        rows |= set(
            re.findall(
                r"^\|\s*([A-Z]+-\d+)\s*\|", (POLICIES / d / "specification.md").read_text(), re.MULTILINE
            )
        )
    for entry in INDEX.values():
        if re.fullmatch(r"[A-Z]+-\d+", entry.rule):
            assert entry.rule in rows, f"{entry.id}: {entry.rule} is not a specification rule row"


@pytest.mark.parametrize(
    "bad",
    [
        {"kind": "fact_status", "answers": {"verified": "Yes"}},
        {"kind": "enum"},
        {"kind": "money"},
        {"kind": "count", "unit": "NZD"},
        {"kind": "fact_status", "answers": {"verified": "Y", "excluded": "N"}, "rule": "made up"},
    ],
)
def test_malformed_entries_are_rejected(bad: dict[str, object]) -> None:
    fields: dict[str, object] = {
        "id": "x",
        "scope": "wff",
        "rule": "WFF-01",
        "question": "A long enough question?",
    }
    fields.update(bad)
    with pytest.raises(ValidationError):
        FactEntry.model_validate(fields)
