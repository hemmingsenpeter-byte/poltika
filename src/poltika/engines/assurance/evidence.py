"""v0.1.5 Phase 1 (Tasks 1.3, 1.4): evidence coverage for one policy.

Reads the policy's `policy.yaml`, source catalogue and `specification.md`
and reports, without calculating anything:

- for every parameter value: its source, the source's type and authority
  rank, and its review status;
- for every specification rule: the catalogue sources it cites and whether
  it cites primary legislation (by an Act/Regulations provision or a rank 1-2
  source);
- `problems`: every gap the release gate forbids. A parameter value whose
  source is unknown, or ranked below official operational material (rank
  3), or a rule that cites an unknown source or no primary legislation.

`python -m poltika.engines.assurance.evidence <policy_dir>...` prints the
report; CI runs it, and a test requires no problems for the real policies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from poltika.policy.loader import load_policy_spec
from poltika.semantics.schemas.source_catalog import SourceCatalog

# The weakest source a parameter value may rest on: official operational
# material, such as MSD's published rate tables used under AS DEC-002.
MAX_PARAMETER_RANK = 3

_RULE_ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|[^|]*\|([^|]*)\|", re.MULTILINE)
_CITED_ID = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")
_PRIMARY_TEXT = re.compile(r"\bAct\b|\bRegulations\b|\bSchedule \d|\bss? [A-Z]{0,2} ?\d|\br \d+")


def evidence_coverage(policy_dir: Path) -> dict[str, Any]:
    spec = load_policy_spec(policy_dir / "policy.yaml")
    catalog = SourceCatalog.model_validate(yaml.safe_load((policy_dir / spec.source_catalog).read_text()))
    sources = catalog.by_id()
    problems: list[str] = []

    parameters = []
    for param in spec.parameters:
        for value in param.values:
            source = sources.get(value.source_id)
            entry: dict[str, Any] = {
                "parameter_id": param.id,
                "effective_from": value.effective_from.isoformat(),
                "source_id": value.source_id,
                "locator": value.locator,
                "review_status": value.review_status.value,
            }
            if source is None:
                problems.append(f"parameter '{param.id}' cites unknown source '{value.source_id}'")
            else:
                entry.update(source_type=source.source_type.value, authority_rank=source.authority_rank)
                if source.authority_rank > MAX_PARAMETER_RANK:
                    problems.append(
                        f"parameter '{param.id}' rests on '{source.id}' ({source.source_type.value}, "
                        f"rank {source.authority_rank}); rank {MAX_PARAMETER_RANK} or better is required"
                    )
            parameters.append(entry)

    rules = []
    for rule_id, citation in _RULE_ROW.findall((policy_dir / "specification.md").read_text()):
        tokens = set(_CITED_ID.findall(citation))
        cited = sorted(tokens & set(sources))
        unknown = sorted(tokens - set(sources))
        primary = bool(_PRIMARY_TEXT.search(citation)) or any(sources[c].authority_rank <= 2 for c in cited)
        if unknown:
            problems.append(f"rule {rule_id} cites unknown source(s) {unknown}")
        if not primary:
            problems.append(f"rule {rule_id} cites no primary legislation")
        rules.append({"rule_id": rule_id, "sources": cited, "cites_primary_legislation": primary})

    approved = [p for p in parameters if p["review_status"] == "approved"]
    return {
        "policy_id": spec.policy_id,
        "policy_version": spec.policy_version,
        "parameters": parameters,
        "rules": rules,
        "summary": {
            "parameter_values": len(parameters),
            "approved_parameter_values": len(approved),
            "parameter_values_with_ranked_source": sum(1 for p in parameters if "authority_rank" in p),
            "rules": len(rules),
            "rules_citing_primary_legislation": sum(1 for r in rules if r["cites_primary_legislation"]),
        },
        "problems": problems,
    }


def main(argv: list[str]) -> int:
    reports = [evidence_coverage(Path(arg)) for arg in argv]
    print(json.dumps([{k: r[k] for k in ("policy_id", "summary", "problems")} for r in reports], indent=2))
    return 1 if any(r["problems"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
