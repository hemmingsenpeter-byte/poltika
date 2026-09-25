"""Task 30: deterministic, identifiable scenario runs.

A `ScenarioRecord` is everything a combined household run depends on:
- the household facts;
- the periods and lookup dates (Task 28.2);
- the requested policy versions.

An `ArtifactManifest` identifies what the run executed against:
- the SHA-256 of every policy file each module bound when its parameters
  were loaded (policy, source catalogue, specification, decisions), taken
  from the run's own traces rather than re-read;
- the code identity: package version, source commit, whether the source
  tree was clean, and the dependency lock's hash.

For v0.1, a git commit reachable from protected `main` plus `uv.lock` is
the retained, immutable reference for code and repository files (BUILD_PLAN
Task 30.1). A run from an uncommitted or modified tree records
`source_tree_clean=False` and is marked not reproducible: its HEAD commit
alone cannot reproduce it.

Identities are SHA-256 hashes of canonical JSON (sorted keys, fixed
separators, `Decimal` as a string):
- `scenario_id` covers the record;
- `result_id` covers the scenario id, the manifest and the result payload.

Operational details, such as when a run happened, are deliberately outside
both.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, fields
from datetime import date
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any

from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.trace import plain
from poltika.engines.simulator.wff import WffResult
from poltika.scenarios.combined import (
    CombinedHouseholdScenario,
    CombinedResult,
    run_combined_household,
)


@dataclass(frozen=True)
class ScenarioRecord:
    household: CombinedHouseholdScenario
    wff_lookup_date: date
    as_lookup_date: date
    assessment_week: AssessmentWeek
    requested_wff_policy_version: str
    requested_as_policy_version: str


@dataclass(frozen=True)
class CodeIdentity:
    package_version: str
    source_commit: str | None
    source_tree_clean: bool | None
    dependency_lock_sha256: str | None

    @property
    def reproducible(self) -> bool:
        """True only when a clean, committed source tree identifies the code."""
        return self.source_commit is not None and self.source_tree_clean is True


@dataclass(frozen=True)
class ArtifactManifest:
    # ("<policy_id>/<path>", sha256) pairs, sorted -- every file either
    # module bound when loading its parameters.
    policy_files: tuple[tuple[str, str], ...]
    code: CodeIdentity
    # True only when every bound policy file equals its committed version at
    # `code.source_commit` (BUILD_PLAN 30.1: verify the recorded hashes match
    # the committed files actually used). False for files outside the
    # repository, e.g. a temporary policy copy.
    policy_files_committed: bool = False

    @property
    def reproducible(self) -> bool:
        return self.code.reproducible and self.policy_files_committed


@dataclass(frozen=True)
class ScenarioRun:
    record: ScenarioRecord
    result: CombinedResult
    manifest: ArtifactManifest
    scenario_id: str
    result_id: str


def canonical_json(value: Any) -> str:
    """Stable JSON for identity hashing: sorted keys, no whitespace, `Decimal`
    as a string, dates as ISO strings (`trace.plain`)."""
    return json.dumps(plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_record(content: dict[str, Any]) -> dict[str, Any]:
    """A record's plain form (as `canonical_json` writes it) with the WFF
    children in canonical order. Task 34.3 F10: the calculators ignore child
    order, so the scenario identity, and the store's check that a stored
    record is the same scenario, ignore it too."""
    household = content["household"]
    wff = household["wff"]
    children = sorted(
        wff["children"], key=lambda child: json.dumps(child, sort_keys=True, separators=(",", ":"))
    )
    return {**content, "household": {**household, "wff": {**wff, "children": children}}}


def scenario_id(record: ScenarioRecord) -> str:
    """Hashes the record in canonical child order (`canonical_record`)."""
    content = canonical_record(json.loads(canonical_json(record)))
    return _sha256(canonical_json({"type": "combined_household_scenario", "record": content}))


def result_payload(result: CombinedResult) -> dict[str, Any]:
    """The deterministic content of a combined result: every component's
    outcome, value and reason, the periods and the disagreements. Traces are
    identified through the manifest, not repeated here."""

    def component(c: ComponentResult) -> dict[str, Any]:
        return {"outcome": c.outcome, "value": plain(c.value), "reason": c.reason}

    def wff(r: WffResult) -> dict[str, Any]:
        return {f.name: component(getattr(r, f.name)) for f in fields(WffResult)}

    return {
        "wff": wff(result.wff),
        "accommodation_supplement": component(result.accommodation_supplement),
        "original_wff": wff(result.original_wff),
        "original_accommodation_supplement": component(result.original_accommodation_supplement),
        "wff_period": plain(result.wff_period),
        "accommodation_supplement_period": plain(result.accommodation_supplement_period),
        "contradictions": list(result.contradictions),
    }


def manifest_from_result(result: CombinedResult, code: CodeIdentity) -> ArtifactManifest:
    """Assemble the manifest from the run's own traces, so it names exactly
    the bytes each module loaded."""
    files: dict[str, str] = {}
    components = [getattr(result.original_wff, f.name) for f in fields(WffResult)]
    components.append(result.original_accommodation_supplement)
    for c in components:
        assert c.trace is not None, "every module result carries a trace"
        for path, sha in c.trace.artifact_sha256:
            key = f"{c.trace.policy_id}/{path}"
            assert files.get(key, sha) == sha, f"{key} bound with two different hashes in one run"
            files[key] = sha
    return ArtifactManifest(policy_files=tuple(sorted(files.items())), code=code)


def run_scenario(
    record: ScenarioRecord, wff_policy_dir: Path, as_policy_dir: Path, *, code: CodeIdentity
) -> ScenarioRun:
    result = run_combined_household(
        wff_policy_dir,
        as_policy_dir,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
    )
    manifest = manifest_from_result(result, code)
    manifest = ArtifactManifest(
        policy_files=manifest.policy_files,
        code=code,
        policy_files_committed=_files_match_commit(
            {"working_for_families": wff_policy_dir, "accommodation_supplement": as_policy_dir},
            manifest.policy_files,
            code.source_commit,
        ),
    )
    sid = scenario_id(record)
    rid = _sha256(
        canonical_json({"scenario_id": sid, "manifest": manifest, "result": result_payload(result)})
    )
    return ScenarioRun(record=record, result=result, manifest=manifest, scenario_id=sid, result_id=rid)


def detect_code_identity(repo_root: Path) -> CodeIdentity:
    """Best-effort code identity for a source checkout. Outside a git
    checkout (e.g. an installed wheel) the commit and cleanliness are
    unknown, so the run is recorded as not reproducible.

    Task 34.3 F4: the commit only identifies the running code when the
    imported `poltika` package *is* this checkout's `src/poltika`. A wheel
    installed into a virtual environment inside the checkout would otherwise
    inherit the checkout's HEAD."""
    try:
        pkg = package_version("poltika")
    except PackageNotFoundError:
        pkg = "unknown"
    lock = repo_root / "uv.lock"
    lock_sha = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None
    if _running_package_dir() != (repo_root / "src" / "poltika").resolve():
        return CodeIdentity(pkg, None, None, lock_sha)
    try:
        commit = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return CodeIdentity(pkg, None, None, lock_sha)
    return CodeIdentity(pkg, commit, status.strip() == "", lock_sha)


def _running_package_dir() -> Path:
    import poltika

    return Path(poltika.__file__).resolve().parent


def _files_match_commit(
    policy_dirs: dict[str, Path], policy_files: tuple[tuple[str, str], ...], commit: str | None
) -> bool:
    """Whether each bound file's hash equals that file's content at `commit`
    in the git repository containing its policy directory."""
    if commit is None:
        return False
    for key, sha in policy_files:
        policy_id, relative = key.split("/", 1)
        path = (policy_dirs[policy_id] / relative).resolve()
        try:
            top = subprocess.run(
                ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            committed = subprocess.run(
                ["git", "-C", top, "show", f"{commit}:{path.relative_to(Path(top).resolve()).as_posix()}"],
                capture_output=True, check=True,
            ).stdout
        except (OSError, ValueError, subprocess.CalledProcessError):
            return False
        if hashlib.sha256(committed).hexdigest() != sha:
            return False
    return True
