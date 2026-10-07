"""Task 31: the calculation provenance report.

Turns traced component results (`ComponentResult.trace`, produced by the
simulator) into a report that names, for each component, the parameters
and sources, scenario facts, specification rules, decisions, and rounding
rules behind the result.

Before resolving anything, the report verifies that every file the run
bound when its parameters were loaded -- `policy.yaml`, the source
catalogue, `specification.md` and each decision file -- still has the
recorded SHA-256. If one has changed, the report is refused
(`ArtifactHashMismatchError`) rather than built from current content: a
report must describe what the run used (BUILD_PLAN.md Task 31.3). Retaining
the original bytes so an edited file can still be reported on is Tasks
30/32; until then, refusal is the only faithful answer.

All components in one report must come from one calculation: the same
policy, lookup date, artifacts and scenario (`ComponentTrace.scenario_sha256`).
Components from different households are refused even under the same policy.

Source entries carry their catalogue check evidence verbatim. A check
recorded as a mapping with a structured `checked_on` date (e.g. Task 28.2's
`task_28_2_check`) is reported in `checked_on`, naming the check it came
from. Dates inside free-text notes are never parsed, and the catalogue's
`as_of` is never relabelled as a source's check date: a source with no
structured check reports `checked_on` as empty.

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
from dataclasses import fields
from datetime import date, datetime
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from poltika.common.errors import ArtifactHashMismatchError, ProvenanceError
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.trace import ComponentTrace, ParameterUse, plain
from poltika.engines.simulator.wff import WffResult
from poltika.scenarios.combined import SHARED_FACT_CHECKS
from poltika.scenarios.record import ScenarioRun

REPORT_FORMAT = "poltika-provenance/0.1"

# A specification.md rule row: "| WFF-03 | summary | sources |".
_RULE_ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|\s*(.*?)\s*\|")

# Catalogue fields that identify a source rather than record evidence about
# checking it. Every other field is carried verbatim as check evidence.
_SOURCE_IDENTITY_FIELDS = frozenset({"id", "kind", "title", "url", "audit_version_url", "covers", "locator"})


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

    if "specification.md" not in verified:
        raise ProvenanceError("the run did not bind specification.md, so its rule ids cannot be resolved")
    rule_summaries = _rule_summaries(verified["specification.md"].decode("utf-8"))

    components = []
    cited_sources: dict[str, dict[str, Any]] = {}
    for (component_id, result), trace in zip(results.items(), traces):
        if trace.component_id != component_id:
            raise ProvenanceError(
                f"result supplied as '{component_id}' carries a trace for '{trace.component_id}'"
            )
        if component_id not in component_rule_ids:
            raise ProvenanceError(f"component '{component_id}' is not declared in policy.yaml's components")
        decisions = [{"id": d, "path": _decision_path(verified, d)} for d in trace.decisions]
        parameters = [_parameter_entry(use, sources) for use in trace.parameters]
        for use in trace.parameters:
            if use.source_id is not None and use.source_id not in cited_sources:
                cited_sources[use.source_id] = _source_entry(use.source_id, sources[use.source_id])
        components.append(
            {
                "component_id": component_id,
                "outcome": result.outcome,
                "value": plain(result.value),
                "reason": result.reason,
                "code": result.code,
                "category": result.category,
                "missing_facts": list(result.missing_facts),
                "upstream_components": list(trace.upstream_components),
                "source_rules": [
                    {"id": rule_id, "summary": _rule_summary(rule_summaries, rule_id)}
                    for rule_id in component_rule_ids[component_id]
                ],
                "calculation_rules": list(trace.calculation_rules),
                # Task 34.3 F9: a component replaced after the module ran
                # (e.g. needs_review from the combined runner) keeps its
                # module trace; its rules and decisions were not applied to
                # the reported outcome.
                "rules_applied": result.outcome == "calculated",
                "decisions": decisions,
                "parameters": parameters,
                "inputs": [
                    {"name": use.name, "value": plain(use.value), "asserted_by": use.asserted_by}
                    for use in trace.inputs
                ],
                # v0.1.5 Task 2.4: the arithmetic the calculator performed.
                "steps": [
                    {
                        "step_id": step.step_id,
                        "rule_id": step.rule_id,
                        # Resolved like every other citation: a step citing
                        # a rule the specification lacks refuses the report.
                        "rule_summary": _rule_summary(rule_summaries, step.rule_id),
                        "description": step.description,
                        "inputs": {name: plain(value) for name, value in step.inputs},
                        "result": plain(step.result),
                    }
                    for step in trace.steps
                ],
            }
        )
    return {
        "format": REPORT_FORMAT,
        "policy": {
            "policy_id": header["policy_id"],
            "policy_version": header["policy_version"],
            "schema_version": header["schema_version"],
            "modelled_date": header["modelled_date"].isoformat(),
            # [from, to), exclusive end; None when the results did not come
            # through a module entry point that states its period.
            "assessment_period": (
                {"from": header["assessment_period"][0].isoformat(), "to": header["assessment_period"][1].isoformat()}
                if header["assessment_period"] is not None
                else None
            ),
        },
        "scenario_sha256": header["scenario_sha256"],
        "code_version": _code_version(),
        "source_catalog_as_of": plain(catalog.get("as_of")),
        "artifacts": artifacts,
        "sources": [cited_sources[source_id] for source_id in sorted(cited_sources)],
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
        f"- Assessment period: {_period_text(policy['assessment_period'])}",
        f"- Parameter lookup date: {policy['modelled_date']}",
        f"- Scenario SHA-256: `{report['scenario_sha256']}`",
        f"- Schema version: {policy['schema_version']}",
        f"- Code version: {report['code_version']}",
        f"- Source catalogue as of: {report['source_catalog_as_of']} (the catalogue's date, not each source's check date)",
        (
            "- Every input below is the caller's own assertion. Poltika has not independently verified it, "
            "so each result is a conditional simulation, not an entitlement determination."
        ),
        "",
        "## Artifacts",
        "",
        "All bound when the run's parameters were loaded, and verified unchanged before this report was built.",
        "",
        "| Path | SHA-256 |",
        "| --- | --- |",
    ]
    lines += [f"| {_cell(a['path'])} | `{a['sha256']}` |" for a in report["artifacts"]]
    lines += ["", "## Sources cited", ""]
    for source in report["sources"]:
        lines += [
            f"### {source['title']} (`{source['id']}`)",
            "",
            f"- Kind: {source['kind']}",
            f"- URL: {source['url']}",
        ]
        if source["audit_version_url"]:
            lines.append(f"- Audit version URL: {source['audit_version_url']}")
        if source["checked_on"]:
            lines += [f"- Checked on: {c['date']} ({c['field']})" for c in source["checked_on"]]
        else:
            lines.append("- Checked on: not recorded as a structured field")
        for note in source["check_evidence"]:
            lines.append(f"- {note['field']}: {_cell(note['text'])}")
        lines.append("")
    if not report["sources"]:
        lines += ["None.", ""]
    if lines[-1] == "":
        lines.pop()
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
        if component["code"]:
            lines.append(f"- Code: `{component['code']}`")
        if component["category"]:
            lines.append(f"- Category: {component['category']}")
        if component["missing_facts"]:
            lines.append(f"- Waiting for: {', '.join(component['missing_facts'])}")
        if component["upstream_components"]:
            lines.append(f"- Depends on: {', '.join(component['upstream_components'])}")
        lines += ["", "### Specification rules", ""]
        lines += [f"- {rule['id']}: {rule['summary']}" for rule in component["source_rules"]]
        applied = "applied" if component["rules_applied"] else "from the superseded module result (not applied)"
        if component["calculation_rules"]:
            lines += ["", f"### Calculation rules {applied}", ""]
            lines += [f"- {rule}" for rule in component["calculation_rules"]]
        if component["decisions"]:
            lines += ["", f"### Decisions {applied}", ""]
            lines += [f"- {d['id']} (`{d['path']}`)" for d in component["decisions"]]
        if component["steps"]:
            lines += ["", f"### Calculation steps ({applied})", ""]
            lines += ["| Step | Rule | What | Inputs | Result |", "| --- | --- | --- | --- | --- |"]
            for step in component["steps"]:
                inputs = ", ".join(f"{name} = {value}" for name, value in step["inputs"].items())
                lines.append(
                    f"| `{step['step_id']}` | {step['rule_id']} | {_cell(step['description'])} "
                    f"| {_cell(inputs)} | {step['result']} |"
                )
        lines += ["", "### Parameters consulted", ""]
        if component["parameters"]:
            lines += [
                "| Parameter | Outcome | Value | Unit | Effective | Review status | Source | Locator |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
            for p in component["parameters"]:
                effective = f"{p['effective_from']} to {p['effective_to']}" if p["effective_from"] else ""
                source = f"`{p['source_id']}`" if p["source_id"] else ""
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
        (
            t.policy_id,
            t.policy_version,
            t.schema_version,
            t.modelled_date,
            t.artifact_sha256,
            t.scenario_sha256,
            t.assessment_period,
        )
        for t in traces
    }
    if len(headers) != 1:
        raise ProvenanceError(
            "component traces come from different runs "
            "(policy identity, artifacts, scenario, or assessment period differ)"
        )
    policy_id, policy_version, schema_version, modelled_date, artifact_sha256, scenario, period = headers.pop()
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
        "scenario_sha256": scenario,
        "assessment_period": period,
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
        entries.append({"path": name, "sha256": expected})
    if "policy.yaml" not in verified:
        raise ProvenanceError("the run's trace has no hash for policy.yaml")
    return entries, verified


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


def _decision_path(verified: Mapping[str, bytes], decision_id: str) -> str:
    matches = [name for name in verified if PurePosixPath(name).match(f"decisions/{decision_id}-*.md")]
    if len(matches) != 1:
        raise ProvenanceError(
            f"decision '{decision_id}' must match exactly one decision file the run bound, found {len(matches)}"
        )
    return matches[0]


def catalogue_source_entry(source_id: str, entry: Mapping[str, Any]) -> dict[str, Any]:
    """One catalogued source as the provenance report shows it, with its
    dated checks and check evidence, for other read-only views (Task B0.1.1's
    `/api/v1/evidence`)."""
    return _source_entry(source_id, entry)


def _source_entry(source_id: str, entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": source_id,
        "kind": entry.get("kind"),
        "title": entry.get("title"),
        "url": entry.get("url"),
        "audit_version_url": entry.get("audit_version_url"),
        "checked_on": _structured_check_dates(entry),
        "check_evidence": [
            {"field": key, "text": _evidence_text(value)}
            for key, value in entry.items()
            if key not in _SOURCE_IDENTITY_FIELDS
        ],
    }


def _structured_check_dates(entry: Mapping[str, Any]) -> list[dict[str, str]]:
    """Each check recorded as a mapping with a `checked_on` date, oldest
    first. Only a real date (YAML date or ISO-format string) counts; any
    other `checked_on` value stays in the evidence text, unparsed."""
    checks = []
    for key, value in entry.items():
        if not isinstance(value, Mapping) or "checked_on" not in value:
            continue
        checked_on = value["checked_on"]
        if isinstance(checked_on, str):
            try:
                checked_on = date.fromisoformat(checked_on)
            except ValueError:
                continue
        if isinstance(checked_on, date) and not isinstance(checked_on, datetime):
            checks.append({"field": key, "date": checked_on.isoformat()})
    return sorted(checks, key=lambda c: (c["date"], c["field"]))


def _evidence_text(value: Any) -> str:
    """Free text as given; a structured check as canonical JSON."""
    rendered = plain(value)
    if isinstance(rendered, str):
        return rendered
    return json.dumps(rendered, sort_keys=True, ensure_ascii=False)


def _parameter_entry(use: ParameterUse, sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    if use.source_id is not None and use.source_id not in sources:
        raise ProvenanceError(
            f"parameter '{use.parameter_id}' cites source_id '{use.source_id}', "
            "which is not in the run's source catalogue"
        )
    return {
        "parameter_id": use.parameter_id,
        "outcome": use.outcome,
        "value": plain(use.value),
        "unit": use.unit,
        "effective_from": plain(use.effective_from),
        "effective_to": plain(use.effective_to),
        "review_status": use.review_status,
        "locator": use.locator,
        "source_id": use.source_id,
    }


def _code_version() -> str:
    try:
        return f"poltika {package_version('poltika')}"
    except PackageNotFoundError:
        return "poltika (package metadata unavailable)"


def _period_text(period: Mapping[str, str] | None) -> str:
    if period is None:
        return "not stated (results did not come through a module entry point)"
    return f"{period['from']} to {period['to']} (end exclusive)"


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


COMBINED_REPORT_FORMAT = "poltika-combined-provenance/0.1"


def build_combined_provenance_report(
    run: ScenarioRun, wff_policy_dir: Path, as_policy_dir: Path
) -> dict[str, Any]:
    """Task 31.6: provenance for a combined household run (Task 28.4/30).

    Holds the run's scenario and result identities, reproducibility, artifact
    manifest and shared-fact disagreements, plus each policy's own provenance
    report built from the run's final results -- a `needs_review`
    replacement keeps its module trace, so its parameters and inputs are
    still reported. Each policy report verifies its bound files as usual; the
    combined report then requires the manifest to name exactly the files the
    two reports verified, so the manifest cannot drift from what was used.
    """
    wff_results = {f.name: getattr(run.result.wff, f.name) for f in fields(WffResult)}
    wff_report = build_provenance_report(wff_policy_dir, wff_results)
    as_report = build_provenance_report(
        as_policy_dir, {"accommodation_supplement": run.result.accommodation_supplement}
    )

    verified = {
        f"{report['policy']['policy_id']}/{artifact['path']}": artifact["sha256"]
        for report in (wff_report, as_report)
        for artifact in report["artifacts"]
    }
    if verified != dict(run.manifest.policy_files):
        raise ProvenanceError(
            "the run's artifact manifest does not match the files its policy reports verified"
        )

    code = run.manifest.code
    return {
        "format": COMBINED_REPORT_FORMAT,
        "scenario_id": run.scenario_id,
        "result_id": run.result_id,
        "reproducible": run.manifest.reproducible,
        "code": {
            "package_version": code.package_version,
            "source_commit": code.source_commit,
            "source_tree_clean": code.source_tree_clean,
            "dependency_lock_sha256": code.dependency_lock_sha256,
        },
        "policy_files": [{"path": path, "sha256": sha} for path, sha in run.manifest.policy_files],
        "contradictions": list(run.result.contradictions),
        # Task 34.3 F9: the combined runner's own inputs and checks.
        "combined_inputs": [
            {
                "name": "as_claimant_is_wff_claimant_or_partner",
                "value": run.record.household.as_claimant_is_wff_claimant_or_partner.value,
                "asserted_by": "caller",
            }
        ],
        "shared_fact_checks": list(SHARED_FACT_CHECKS),
        "working_for_families": wff_report,
        "accommodation_supplement": as_report,
    }


def render_combined_markdown(report: Mapping[str, Any]) -> str:
    """Both policies' reports under one header. Periods stay native: WFF
    annual, AS weekly; there is no combined total."""
    code = report["code"]
    lines = [
        "# Combined household provenance report",
        "",
        f"- Scenario id: `{report['scenario_id']}`",
        f"- Result id: `{report['result_id']}`",
        f"- Reproducible from a committed source tree: {'yes' if report['reproducible'] else 'no'}",
        (
            f"- Code: {code['package_version']}, commit {code['source_commit'] or 'unknown'}, "
            f"clean tree {code['source_tree_clean'] if code['source_tree_clean'] is not None else 'unknown'}"
        ),
        "- Each policy is reported in its own period; there is no combined total.",
        "",
        "## Combined-run inputs",
        "",
    ]
    lines += [f"- {i['name']}: {i['value']} (asserted by {i['asserted_by']})" for i in report["combined_inputs"]]
    lines += ["", "## Shared-fact checks run", ""]
    lines += [f"- {check}" for check in report["shared_fact_checks"]]
    lines += ["", "## Shared-fact disagreements", ""]
    lines += [f"- {c}" for c in report["contradictions"]] or ["None."]
    for key, title in (
        ("working_for_families", "Working for Families (annual)"),
        ("accommodation_supplement", "Accommodation Supplement (weekly)"),
    ):
        body = render_markdown(report[key]).replace("\n# ", "\n### ").replace("\n## ", "\n#### ")
        body = body.replace("# Provenance report:", "### Provenance report:", 1)
        lines += ["", f"## {title}", "", body.rstrip("\n")]
    return "\n".join(lines) + "\n"
