"""Task 31: the calculation provenance report.

Turns traced component results (`ComponentResult.trace`, produced by the
simulator) into a report that names, for each component, the parameters
and sources, scenario facts, specification rules, decisions, and rounding
rules behind the result.

Before resolving anything, the report verifies that every file the run's
trace recorded (`policy.yaml` and the source catalogue) still has the
recorded SHA-256. If one has changed, the report is refused
(`ArtifactHashMismatchError`) rather than built from current content: a
report must describe what the run used (BUILD_PLAN.md Task 31.3). The
specification and decision files are not hashed at run time yet; the
report records their hashes as read at report time, labelled
`bound_at: "report"`. Binding them at run time is Task 30.1's artifact
manifest.

Any citation that cannot be resolved (a parameter's `source_id`, a
component's rule id, a decision id) raises `ProvenanceError`. A report with
a silent gap would be worse than no report.

`render_json()` and `render_markdown()` both render the same report
dictionary, so the two formats cannot disagree about content.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from poltika.common.errors import ArtifactHashMismatchError, ProvenanceError
from poltika.engines.simulator.trace import ComponentTrace, ParameterUse
from poltika.engines.simulator.wff import ComponentResult

REPORT_FORMAT = "poltika-provenance/0.1"

# A specification.md rule row: "| WFF-03 | summary | sources |".
_RULE_ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|\s*(.*?)\s*\|")


def build_provenance_report(policy_dir: Path, results: Mapping[str, ComponentResult]) -> dict[str, Any]:
    """Build the report for one module run's component results.

    `results` maps component id to result, in the order the report should
    list them (e.g. WFF's four components, or AS's single one). Every result
    must carry a trace, and all traces must come from the same run (same
    policy identity and artifact hashes).
    """
    if not results:
        raise ProvenanceError("no component results to report on")
    traces = [_require_trace(component_id, result) for component_id, result in results.items()]
    header = _shared_header(traces)

    artifacts, verified = _verify_run_artifacts(policy_dir, header["artifact_sha256"])
    policy = yaml.safe_load(verified["policy.yaml"])
    source_catalog_name = policy["source_catalog"]
    if source_catalog_name not in verified:
        raise ProvenanceError(
            f"the run's trace has no hash for the declared source catalogue '{source_catalog_name}'"
        )
    catalog = yaml.safe_load(verified[source_catalog_name])
    sources = {entry["id"]: entry for entry in catalog.get("sources", [])}
    component_rule_ids = {c["id"]: list(c.get("source_rule_ids", [])) for c in policy.get("components", [])}

    specification_path = policy_dir / "specification.md"
    specification_bytes = _read_report_time_artifact(specification_path)
    artifacts.append(_artifact_entry("specification.md", specification_bytes, bound_at="report"))
    rule_summaries = _rule_summaries(specification_bytes.decode("utf-8"))

    components = []
    decision_artifacts: dict[str, dict[str, Any]] = {}
    for (component_id, result), trace in zip(results.items(), traces):
        if trace.component_id != component_id:
            raise ProvenanceError(
                f"result supplied as '{component_id}' carries a trace for '{trace.component_id}'"
            )
        if component_id not in component_rule_ids:
            raise ProvenanceError(f"component '{component_id}' is not declared in policy.yaml's components")
        decisions = []
        for decision_id in trace.decisions:
            if decision_id not in decision_artifacts:
                decision_artifacts[decision_id] = _decision_artifact(policy_dir, decision_id)
            decisions.append({"id": decision_id, "path": decision_artifacts[decision_id]["path"]})
        components.append(
            {
                "component_id": component_id,
                "outcome": result.outcome,
                "value": _plain(result.value),
                "reason": result.reason,
                "upstream_components": list(trace.upstream_components),
                "source_rules": [
                    {"id": rule_id, "summary": _rule_summary(rule_summaries, rule_id)}
                    for rule_id in component_rule_ids[component_id]
                ],
                "calculation_rules": list(trace.calculation_rules),
                "decisions": decisions,
                "parameters": [_parameter_entry(use, sources) for use in trace.parameters],
                "inputs": [
                    {"name": use.name, "value": _plain(use.value), "asserted_by": use.asserted_by}
                    for use in trace.inputs
                ],
            }
        )
    artifacts.extend(decision_artifacts[decision_id] for decision_id in sorted(decision_artifacts))

    return {
        "format": REPORT_FORMAT,
        "policy": {
            "policy_id": header["policy_id"],
            "policy_version": header["policy_version"],
            "schema_version": header["schema_version"],
            "modelled_date": header["modelled_date"].isoformat(),
        },
        "code_version": _code_version(),
        "source_catalog_as_of": _plain(catalog.get("as_of")),
        "artifacts": artifacts,
        "components": components,
    }


def render_json(report: Mapping[str, Any]) -> str:
    """Canonical JSON: sorted keys, fixed separators, trailing newline."""
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    policy = report["policy"]
    lines = [
        f"# Provenance report: {policy['policy_id']} {policy['policy_version']}",
        "",
        f"- Modelled date: {policy['modelled_date']}",
        f"- Schema version: {policy['schema_version']}",
        f"- Code version: {report['code_version']}",
        f"- Source catalogue as of: {report['source_catalog_as_of']}",
        (
            "- Every input below is the caller's own assertion. Poltika has not independently verified it, "
            "so each result is a conditional simulation, not an entitlement determination."
        ),
        "",
        "## Artifacts",
        "",
        "| Path | SHA-256 | Bound at |",
        "| --- | --- | --- |",
    ]
    lines += [f"| {_cell(a['path'])} | `{a['sha256']}` | {a['bound_at']} |" for a in report["artifacts"]]
    for component in report["components"]:
        value = component["value"] if component["value"] is not None else "(none)"
        lines += [
            "",
            f"## {component['component_id']}",
            "",
            f"- Outcome: **{component['outcome']}**",
            f"- Value: {value}",
        ]
        if component["reason"]:
            lines.append(f"- Reason: {component['reason']}")
        if component["upstream_components"]:
            lines.append(f"- Depends on: {', '.join(component['upstream_components'])}")
        lines += ["", "### Specification rules", ""]
        lines += [f"- {rule['id']}: {rule['summary']}" for rule in component["source_rules"]]
        if component["calculation_rules"]:
            lines += ["", "### Calculation rules applied", ""]
            lines += [f"- {rule}" for rule in component["calculation_rules"]]
        if component["decisions"]:
            lines += ["", "### Decisions applied", ""]
            lines += [f"- {d['id']} (`{d['path']}`)" for d in component["decisions"]]
        lines += ["", "### Parameters consulted", ""]
        if component["parameters"]:
            lines += [
                "| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
            for p in component["parameters"]:
                effective = f"{p['effective_from']} to {p['effective_to']}" if p["effective_from"] else ""
                source = f"{p['source']['title']} (`{p['source']['id']}`)" if p["source"] else ""
                lines.append(
                    "| "
                    + " | ".join(
                        _cell(x)
                        for x in (
                            f"`{p['parameter_id']}`",
                            p["outcome"],
                            p["value"],
                            p["unit"],
                            effective,
                            p["review_status"],
                            source,
                            p["locator"],
                        )
                    )
                    + " |"
                )
        else:
            lines.append("None.")
        lines += ["", "### Inputs read", ""]
        if component["inputs"]:
            lines += ["| Input | Value | Asserted by |", "| --- | --- | --- |"]
            lines += [
                f"| `{i['name']}` | {_cell(json.dumps(i['value'], sort_keys=True))} | {i['asserted_by']} |"
                for i in component["inputs"]
            ]
        else:
            lines.append("None.")
    return "\n".join(lines) + "\n"


def _require_trace(component_id: str, result: ComponentResult) -> ComponentTrace:
    if result.trace is None:
        raise ProvenanceError(f"component '{component_id}' result carries no trace")
    return result.trace


def _shared_header(traces: list[ComponentTrace]) -> dict[str, Any]:
    headers = {
        (t.policy_id, t.policy_version, t.schema_version, t.modelled_date, t.artifact_sha256) for t in traces
    }
    if len(headers) != 1:
        raise ProvenanceError("component traces come from different runs (policy identity or artifacts differ)")
    policy_id, policy_version, schema_version, modelled_date, artifact_sha256 = headers.pop()
    if not artifact_sha256:
        raise ProvenanceError(
            "the traces record no artifact hashes -- the parameter set was not loaded from policy files, "
            "so the report cannot identify what the run used"
        )
    return {
        "policy_id": policy_id,
        "policy_version": policy_version,
        "schema_version": schema_version,
        "modelled_date": modelled_date,
        "artifact_sha256": artifact_sha256,
    }


def _verify_run_artifacts(
    policy_dir: Path, artifact_sha256: tuple[tuple[str, str], ...]
) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    entries = []
    verified: dict[str, bytes] = {}
    for name, expected in artifact_sha256:
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ProvenanceError(f"artifact path '{name}' must be relative to the policy directory")
        path = policy_dir / relative
        if not path.is_file():
            raise ArtifactHashMismatchError(f"artifact '{name}' recorded by the run no longer exists")
        content = path.read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ArtifactHashMismatchError(
                f"artifact '{name}' has changed since the run (recorded sha256 {expected}, now {actual}); "
                "the report will not substitute current content for what the run used"
            )
        verified[name] = content
        entries.append({"path": name, "sha256": expected, "bound_at": "run"})
    if "policy.yaml" not in verified:
        raise ProvenanceError("the run's trace has no hash for policy.yaml")
    return entries, verified


def _read_report_time_artifact(path: Path) -> bytes:
    if not path.is_file():
        raise ProvenanceError(f"'{path.name}' not found in the policy directory")
    return path.read_bytes()


def _artifact_entry(path: str, content: bytes, *, bound_at: str) -> dict[str, Any]:
    return {"path": path, "sha256": hashlib.sha256(content).hexdigest(), "bound_at": bound_at}


def _rule_summaries(specification_text: str) -> dict[str, str]:
    summaries: dict[str, str] = {}
    for line in specification_text.splitlines():
        match = _RULE_ROW.match(line)
        if match and match.group(1) not in summaries:
            summaries[match.group(1)] = match.group(2)
    return summaries


def _rule_summary(summaries: Mapping[str, str], rule_id: str) -> str:
    if rule_id not in summaries:
        raise ProvenanceError(f"source rule '{rule_id}' has no row in specification.md")
    return summaries[rule_id]


def _decision_artifact(policy_dir: Path, decision_id: str) -> dict[str, Any]:
    matches = sorted((policy_dir / "decisions").glob(f"{decision_id}-*.md"))
    if len(matches) != 1:
        raise ProvenanceError(
            f"decision '{decision_id}' must match exactly one file in decisions/, found {len(matches)}"
        )
    path = f"decisions/{matches[0].name}"
    return _artifact_entry(path, matches[0].read_bytes(), bound_at="report")


def _parameter_entry(use: ParameterUse, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    source = None
    if use.source_id is not None:
        entry = sources.get(use.source_id)
        if entry is None:
            raise ProvenanceError(
                f"parameter '{use.parameter_id}' cites source_id '{use.source_id}', "
                "which is not in the run's source catalogue"
            )
        source = {
            "id": use.source_id,
            "kind": entry.get("kind"),
            "title": entry.get("title"),
            "url": entry.get("url"),
            "audit_version_url": entry.get("audit_version_url"),
        }
    return {
        "parameter_id": use.parameter_id,
        "outcome": use.outcome,
        "value": _plain(use.value),
        "unit": use.unit,
        "effective_from": _plain(use.effective_from),
        "effective_to": _plain(use.effective_to),
        "review_status": use.review_status,
        "locator": use.locator,
        "source": source,
    }


def _code_version() -> str:
    try:
        return f"poltika {package_version('poltika')}"
    except PackageNotFoundError:
        return "poltika (package metadata unavailable)"


def _plain(value: Any) -> Any:
    """A JSON-safe rendering of a trace value: `Decimal` as a string (never
    a float), dates as ISO strings, enums by value, dataclasses as dicts."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Enum):
        return _plain(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name)) for f in fields(value) if f.name != "trace"}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    raise ProvenanceError(f"cannot render trace value of type {type(value).__name__}")


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")
