"""v0.3 Task 1b.1: load a policy's fact catalogue (`facts.yaml`)."""

from __future__ import annotations

from pathlib import Path

import yaml

from poltika.semantics.schemas.fact_catalog import FactCatalog, FactEntry


def load_fact_catalog(policy_dir: Path) -> FactCatalog:
    return FactCatalog.model_validate(yaml.safe_load((policy_dir / "facts.yaml").read_text()))


def fact_index(*catalogs: FactCatalog) -> dict[tuple[str, str], FactEntry]:
    """Entries keyed by (scope, id). The same id can mean different facts in
    different scopes (WFF and AS each have their own `partner_status`)."""
    index: dict[tuple[str, str], FactEntry] = {}
    for catalog in catalogs:
        for entry in catalog.facts:
            index[(entry.scope, entry.id)] = entry
    return index
