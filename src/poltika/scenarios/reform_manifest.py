"""Task 14 (counterfactual scenario contract): the reform run manifest.

A reform run's manifest records what the run was made from, using only
values the run already holds: the law baseline date, each option's reform
and run id, the population id, version and SHA-256, the code identity, the
policy artifacts as (name, SHA-256) pairs, the assumptions the reform
overrode, the unit labels, the synthetic flag and the stated limitations.

The manifest is stored beside the run, never inside the hashed results
payload, so it cannot change a run id (`reform_record.reform_run_id`). A run
stored before migration 0003 has no manifest: it is "not retained" and is
never backfilled.

`verify_manifest` compares a stored manifest with a fresh run of the same
options against the current population and policy files. It reads only.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from poltika.engines.simulator.trace import plain
from poltika.scenarios.microsim.runner import PopulationRun
from poltika.scenarios.record import canonical_json

MANIFEST_FORMAT = "poltika.reform_run_manifest/1"


def build_manifest(
    law_baseline_date: date,
    options: Sequence[tuple[str, PopulationRun]],
    *,
    units: Sequence[str],
    limitations: Sequence[str],
) -> dict[str, Any]:
    """The manifest as a plain, JSON-safe dict."""
    return {
        "format": MANIFEST_FORMAT,
        "law_baseline_date": law_baseline_date.isoformat(),
        "units": list(units),
        "limitations": list(limitations),
        "options": [_option(label, run) for label, run in options],
    }


def _option(label: str, run: PopulationRun) -> dict[str, Any]:
    return {
        "label": label,
        "reform_id": run.reform.reform_id,
        "reform_sha256": run.reform.reform_sha256(),
        "option_run_id": run.run_id,
        "option_results_sha256": run.results_sha256,
        "population": {
            "population_id": run.population_id,
            "version": run.population_version,
            "sha256": run.population_sha256,
        },
        "synthetic": run.synthetic,
        "code": plain(run.code),
        "reproducible": run.code.reproducible,
        "policy_artifacts": [{"name": n, "sha256": s} for n, s in run.policy_artifacts],
        "assumptions": [plain(o) for o in run.overridden],
    }


VerificationStatus = Literal["identical", "drifted", "not_retained"]


@dataclass(frozen=True)
class ReformVerification:
    status: VerificationStatus
    # What differs, by name: "option[0].population_sha256",
    # "option[0].policy_artifact:<name>", "option[0].code", ... Empty unless
    # drifted.
    changed: tuple[str, ...] = ()


def verify_manifest(
    manifest: dict[str, Any], rerun: Sequence[PopulationRun]
) -> ReformVerification:
    stored_options = manifest["options"]
    if len(stored_options) != len(rerun):
        return ReformVerification("drifted", ("options",))
    changed: list[str] = []
    for i, (stored, run) in enumerate(zip(stored_options, rerun, strict=True)):
        now = _option(stored["label"], run)
        p = f"option[{i}]."
        if stored["reform_sha256"] != now["reform_sha256"]:
            changed.append(p + "reform_sha256")
        if stored["population"] != now["population"]:
            for key, label in (
                ("population_id", "population_id"),
                ("version", "population_version"),
                ("sha256", "population_sha256"),
            ):
                if stored["population"].get(key) != now["population"][key]:
                    changed.append(p + label)
        if canonical_json(stored["code"]) != canonical_json(now["code"]):
            changed.append(p + "code")
        old = {a["name"]: a["sha256"] for a in stored["policy_artifacts"]}
        new = {a["name"]: a["sha256"] for a in now["policy_artifacts"]}
        for name in sorted(old.keys() | new.keys()):
            if old.get(name) != new.get(name):
                changed.append(p + f"policy_artifact:{name}")
        unexplained = not any(c.startswith(p) for c in changed)
        if unexplained and stored["option_results_sha256"] != now["option_results_sha256"]:
            changed.append(p + "results")
    return ReformVerification("drifted" if changed else "identical", tuple(changed))
