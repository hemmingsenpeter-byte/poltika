"""The workbench registry: instruments, parameters, sources and decisions,
read from the policy specification directory.

Every directory under the specs root that holds a `policy.yaml` is an
instrument. Nothing here names Working for Families or the Accommodation
Supplement: a new instrument appears in `GET /workbench/registry` when its
spec directory is added. It is *runnable* only when the engines model it
(`reform.MODELLED_POLICIES`); an instrument that parses but is not modelled
is listed, read-only, and its parameters can't be overridden.

A directory that fails to parse is reported with its error and never hides
the others. Paths are never returned.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from poltika.api.wff import WFF_POLICY_DIR
from poltika.common.errors import PoltikaError
from poltika.policy.loader import ParameterResolution, load_policy_parameters, load_policy_spec
from poltika.scenarios.microsim.reform import MODELLED_POLICIES
from poltika.semantics.schemas.policy_spec import ParameterSpec, PolicySpec
from poltika.semantics.schemas.source_catalog import SourceCatalog, SourceEntry

# Display labels for the units a spec may use. An unknown unit is shown as
# written, so a new unit needs no change here to appear.
UNIT_LABELS: dict[str, str] = {
    "NZD": "NZ$",
    "NZD_per_week": "NZ$ per week",
    "NZD_per_tax_year": "NZ$ per tax year",
    "NZD_per_tax_year_after_tax": "NZ$ per tax year, after tax",
    "NZD_per_child_per_tax_year": "NZ$ per child per tax year",
    "NZD_per_complete_NZD_above_threshold": "rate per complete NZ$ above the threshold",
    "fraction": "fraction of 1",
}


def specs_root() -> Path:
    return WFF_POLICY_DIR.parent


def _policy_dirs() -> list[Path]:
    return sorted(p for p in specs_root().iterdir() if (p / "policy.yaml").is_file())


def _heading(path: Path, fallback: str) -> str:
    if path.is_file():
        for line in path.read_text().splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return fallback


def _decisions(policy_dir: Path) -> list[dict[str, str]]:
    found = []
    for path in sorted((policy_dir / "decisions").glob("DEC-*.md")):
        decision_id = re.match(r"(DEC-\d+)", path.name)
        if decision_id is None:
            continue
        title = _heading(path, path.stem)
        found.append(
            {
                "id": decision_id.group(1),
                "title": re.sub(r"^DEC-\d+:\s*", "", title),
            }
        )
    return found


def decision_text(policy_id: str, decision_id: str) -> str | None:
    """The decision's Markdown, found by scanning (never by joining a
    caller-supplied path)."""
    for policy_dir in _policy_dirs():
        if policy_dir.name != policy_id:
            continue
        for path in (policy_dir / "decisions").glob("DEC-*.md"):
            if path.name.startswith(decision_id + "-"):
                return path.read_text()
    return None


def _resolution_json(r: ParameterResolution) -> dict[str, Any]:
    return {
        "outcome": r.outcome,
        "value": None if r.value is None else str(r.value),
        "reason": r.reason,
        "effective_from": None if r.effective_from is None else r.effective_from.isoformat(),
        "effective_to": None if r.effective_to is None else r.effective_to.isoformat(),
        "review_status": r.review_status,
        "source_id": r.source_id,
        "locator": r.locator,
    }


def _source_json(entry: SourceEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "title": entry.title,
        "url": entry.url,
        "kind": entry.kind.value,
        "source_type": entry.source_type.value,
        "authority_rank": entry.authority_rank,
    }


def _parameter_json(
    spec: ParameterSpec, policy_id: str, runnable: bool, current: ParameterResolution | None,
    reason: str | None,
) -> dict[str, Any]:
    return {
        "id": spec.id,
        "policy_id": policy_id,
        "value_type": spec.value_type.value,
        "unit": spec.unit.value,
        "unit_label": UNIT_LABELS.get(spec.unit.value, spec.unit.value),
        "editable": runnable,
        "current": (
            _resolution_json(current)
            if current is not None
            else {"outcome": "unsupported", "value": None, "reason": reason}
        ),
        "values": [
            {
                "effective_from": v.effective_from.isoformat(),
                "effective_to": None if v.effective_to is None else v.effective_to.isoformat(),
                "value": str(v.value),
                "review_status": v.review_status.value,
                "source_id": v.source_id,
                "locator": v.locator,
            }
            for v in spec.values
        ],
    }


def _safe_error(exc: Exception, policy_dir: Path) -> str:
    """An error message without the server's file paths."""
    if isinstance(exc, OSError):
        return "a specification file could not be read"
    message = str(exc)
    for path in (policy_dir, policy_dir.parent):
        message = message.replace(str(path), "<specs>")
    return message


def _instrument(policy_dir: Path, as_at: date) -> dict[str, Any]:
    try:
        spec: PolicySpec = load_policy_spec(policy_dir / "policy.yaml")
        catalog = SourceCatalog.model_validate(
            yaml.safe_load((policy_dir / spec.source_catalog).read_text())
        )
    except (PoltikaError, ValueError, OSError, yaml.YAMLError) as exc:
        return {"id": policy_dir.name, "valid": False, "error": _safe_error(exc, policy_dir)}
    runnable = spec.policy_id in MODELLED_POLICIES
    resolutions: dict[str, ParameterResolution] = {}
    reason: str | None = None
    try:
        resolutions = load_policy_parameters(
            policy_dir, as_at, requested_policy_version=spec.policy_version
        ).resolutions
    except PoltikaError as exc:
        reason = _safe_error(exc, policy_dir)
    return {
        "id": spec.policy_id,
        "valid": True,
        "title": re.sub(
            r"\s+specification$", "", _heading(policy_dir / "specification.md", spec.policy_id)
        ),
        "version": spec.policy_version,
        "status": spec.status.value,
        "reference_period": {
            "from": spec.reference_period.from_.isoformat(),
            "to": spec.reference_period.to.isoformat(),
        },
        "runnable": runnable,
        "parameters": [
            _parameter_json(p, spec.policy_id, runnable, resolutions.get(p.id), reason)
            for p in spec.parameters
        ],
        "sources": [_source_json(s) for s in catalog.sources],
        "decisions": _decisions(policy_dir),
    }


def instruments(as_at: date) -> list[dict[str, Any]]:
    return [_instrument(policy_dir, as_at) for policy_dir in _policy_dirs()]
