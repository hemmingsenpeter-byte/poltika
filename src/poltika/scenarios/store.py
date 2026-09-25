"""Task 32: PostgreSQL store for scenario runs (ADR-0013).

Tables (append-only; the repository layer has no update path):
- `scenario`: a `ScenarioRecord`, keyed by `scenario_id`;
- `run`: a result, keyed by `result_id`, with its artifact manifest and
  reproducibility flag;
- `artifact`: the exact bytes of every file a run bound, keyed by SHA-256.

Storing the bytes lets a run replay after the repository's policy files
change (Task 32.4). Code replay uses the manifest's git commit and is
exercised separately (Task 34.2).

Saving an id again with identical content is a no-op; with different
content it raises `ImmutableRecordError`. Saving a run whose bound files no
longer match their recorded hashes is refused, as is replaying from missing
or hash-mismatched artifacts.

The database URL is operator configuration (`POLTIKA_DATABASE_URL`),
following ADR-0011's deploy-time convention.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Engine,
    ForeignKey,
    LargeBinary,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)

from poltika.common.errors import ImmutableRecordError, StoredRunNotFoundError, StoreError
from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
)
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
)
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import (
    CodeIdentity,
    ScenarioRecord,
    ScenarioRun,
    canonical_json,
    result_payload,
    run_scenario,
    scenario_id,
)

metadata = MetaData()
scenario_table = Table(
    "scenario",
    metadata,
    Column("scenario_id", String(64), primary_key=True),
    Column("record_json", Text, nullable=False),
)
artifact_table = Table(
    "artifact",
    metadata,
    Column("sha256", String(64), primary_key=True),
    Column("content", LargeBinary, nullable=False),
)
run_table = Table(
    "run",
    metadata,
    Column("result_id", String(64), primary_key=True),
    Column("scenario_id", String(64), ForeignKey("scenario.scenario_id"), nullable=False),
    Column("manifest_json", Text, nullable=False),
    Column("result_json", Text, nullable=False),
    Column("reproducible", Boolean, nullable=False),
)


def database_url() -> str:
    url = os.environ.get("POLTIKA_DATABASE_URL")
    if not url:
        raise StoreError("POLTIKA_DATABASE_URL is not set")
    return url


def migrate(url: str) -> None:
    """Apply the packaged Alembic migrations up to head."""
    from alembic import command
    from alembic.config import Config

    config = Config()
    config.set_main_option("script_location", str(Path(__file__).parent / "migrations"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")


@dataclass(frozen=True)
class StoredRun:
    result_id: str
    scenario_id: str
    record: ScenarioRecord
    manifest: dict[str, Any]
    result: dict[str, Any]
    reproducible: bool


@dataclass(frozen=True)
class ReplayReport:
    reproduced: bool
    code_matches: bool


@dataclass(frozen=True)
class DriftReport:
    """A re-run against current files, stored as its own run."""

    original_result_id: str
    new_result_id: str
    changed_artifacts: tuple[str, ...]
    result_changed: bool


class ScenarioStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @classmethod
    def from_url(cls, url: str) -> ScenarioStore:
        return cls(create_engine(url))

    def save_run(self, run: ScenarioRun, wff_policy_dir: Path, as_policy_dir: Path) -> None:
        dirs = {"working_for_families": wff_policy_dir, "accommodation_supplement": as_policy_dir}
        artifacts: dict[str, bytes] = {}
        for key, sha in run.manifest.policy_files:
            policy_id, relative = key.split("/", 1)
            content = (dirs[policy_id] / relative).read_bytes()
            if hashlib.sha256(content).hexdigest() != sha:
                raise StoreError(f"{key} no longer matches the run's recorded hash; refusing to store")
            artifacts[sha] = content
        with self._engine.begin() as conn:
            _insert_once(conn, scenario_table, "scenario_id", run.scenario_id, {"record_json": canonical_json(run.record)})
            for sha, content in artifacts.items():
                _insert_once(conn, artifact_table, "sha256", sha, {"content": content})
            _insert_once(
                conn,
                run_table,
                "result_id",
                run.result_id,
                {
                    "scenario_id": run.scenario_id,
                    "manifest_json": canonical_json(run.manifest),
                    "result_json": canonical_json(result_payload(run.result)),
                    "reproducible": run.manifest.reproducible,
                },
            )

    def get_run(self, result_id: str) -> StoredRun:
        with self._engine.connect() as conn:
            row = conn.execute(select(run_table).where(run_table.c.result_id == result_id)).one_or_none()
            if row is None:
                raise StoredRunNotFoundError(f"no stored run {result_id}")
            record_json = conn.execute(
                select(scenario_table.c.record_json).where(scenario_table.c.scenario_id == row.scenario_id)
            ).scalar_one()
        record = record_from_plain(json.loads(record_json))
        if scenario_id(record) != row.scenario_id:
            # Task 34.3 F10: never replay a different scenario than was stored.
            raise StoreError(f"stored scenario {row.scenario_id} does not rebuild to the same identity")
        return StoredRun(
            result_id=row.result_id,
            scenario_id=row.scenario_id,
            record=record,
            manifest=json.loads(row.manifest_json),
            result=json.loads(row.result_json),
            reproducible=row.reproducible,
        )

    def restore_artifacts(self, stored: StoredRun, target: Path) -> tuple[Path, Path]:
        """Write the run's bound files into `target/<policy_id>/`, verifying
        every hash. Missing or mismatched bytes fail explicitly."""
        with self._engine.connect() as conn:
            for key, sha in stored.manifest["policy_files"]:
                content = conn.execute(
                    select(artifact_table.c.content).where(artifact_table.c.sha256 == sha)
                ).scalar_one_or_none()
                if content is None:
                    raise StoreError(f"artifact {key} ({sha}) is missing from the store")
                if hashlib.sha256(content).hexdigest() != sha:
                    raise StoreError(f"artifact {key} does not match its hash {sha}")
                path = target / key
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        return target / "working_for_families", target / "accommodation_supplement"

    def replay(self, result_id: str, workdir: Path, *, code: CodeIdentity) -> ReplayReport:
        """Re-run a stored run against its own retained files with the code
        running now (`code`). `reproduced` when the deterministic result and
        bound file hashes reproduce exactly; `code_matches` only when both the
        stored and the current code are identified reproducibly and are the
        same (Task 34.3 F4: a rerun is never labelled with the stored code)."""
        stored = self.get_run(result_id)
        wff_dir, as_dir = self.restore_artifacts(stored, workdir)
        rerun = run_scenario(stored.record, wff_dir, as_dir, code=code)
        same_result: bool = json.loads(canonical_json(result_payload(rerun.result))) == stored.result
        same_files: bool = [list(item) for item in rerun.manifest.policy_files] == stored.manifest["policy_files"]
        stored_code = _code(stored.manifest)
        code_matches = stored_code.reproducible and code.reproducible and (
            (stored_code.source_commit, stored_code.dependency_lock_sha256)
            == (code.source_commit, code.dependency_lock_sha256)
        )
        return ReplayReport(reproduced=same_result and same_files, code_matches=code_matches)

    def rerun_against_current(
        self, result_id: str, wff_policy_dir: Path, as_policy_dir: Path, *, code: CodeIdentity
    ) -> DriftReport:
        """Run a stored scenario against the current files as a new,
        separately stored run, and report what changed."""
        stored = self.get_run(result_id)
        rerun = run_scenario(stored.record, wff_policy_dir, as_policy_dir, code=code)
        self.save_run(rerun, wff_policy_dir, as_policy_dir)
        before = dict(tuple(item) for item in stored.manifest["policy_files"])
        after = dict(rerun.manifest.policy_files)
        changed = tuple(sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)))
        return DriftReport(
            original_result_id=result_id,
            new_result_id=rerun.result_id,
            changed_artifacts=changed,
            result_changed=json.loads(canonical_json(result_payload(rerun.result))) != stored.result,
        )


def _insert_once(conn: Any, table: Table, key: str, value: str, columns: dict[str, Any]) -> None:
    existing = conn.execute(select(table).where(table.c[key] == value)).one_or_none()
    if existing is None:
        conn.execute(table.insert().values({key: value, **columns}))
        return
    for name, new in columns.items():
        if getattr(existing, name) != new:
            raise ImmutableRecordError(f"{table.name} {value} is already stored with different {name}")


def _code(manifest: dict[str, Any]) -> CodeIdentity:
    c = manifest["code"]
    return CodeIdentity(c["package_version"], c["source_commit"], c["source_tree_clean"], c["dependency_lock_sha256"])


def _opt_dec(v: Any) -> Decimal | None:
    return None if v is None else Decimal(v)


def record_from_plain(d: dict[str, Any]) -> ScenarioRecord:
    """Rebuild a `ScenarioRecord` from its canonical JSON form."""
    h = d["household"]
    w, a = h["wff"], h["accommodation_supplement"]
    income = w["family_scheme_income"]
    wff = WffScenario(
        household_eligibility=FactStatus(w["household_eligibility"]),
        extra_instalment_status=FactStatus(w["extra_instalment_status"]),
        children=[
            ChildFacts(
                qualifies_whole_year=FactStatus(c["qualifies_whole_year"]),
                best_start_cohort=BestStartCohort(c["best_start_cohort"]),
                best_start_no_disqualifying_payment=FactStatus(c["best_start_no_disqualifying_payment"]),
            )
            for c in w["children"]
        ],
        partner_status=PartnerStatus(w["partner_status"]),
        family_scheme_income=None
        if income is None
        else VerifiedIncome(Decimal(income["claimant_amount"]), _opt_dec(income["partner_amount"])),
        net_family_scheme_income=_opt_dec(w["net_family_scheme_income"]),
        net_family_scheme_income_me3_attested=w["net_family_scheme_income_me3_attested"],
        in_work_eligibility=FactStatus(w["in_work_eligibility"]),
        ftc_iwtc_protected_or_direct_abatement=FactStatus(w["ftc_iwtc_protected_or_direct_abatement"]),
        mc6a_veterans_payment=FactStatus(w["mc6a_veterans_payment"]),
        mc6b_disqualifying_payment=FactStatus(w["mc6b_disqualifying_payment"]),
        minimum_family_full_time_earner_weeks=FactStatus(w["minimum_family_full_time_earner_weeks"]),
        best_start_no_shared_care=FactStatus(w["best_start_no_shared_care"]),
        best_start_protected_credit=FactStatus(w["best_start_protected_credit"]),
    )

    def opt(enum: Any, v: Any) -> Any:
        return None if v is None else enum(v)

    as_ = AsScenario(
        household_eligibility=FactStatus(a["household_eligibility"]),
        claimant_category=opt(ClaimantCategory, a["claimant_category"]),
        tenure_type=opt(TenureType, a["tenure_type"]),
        partner_status=opt(PartnerType, a["partner_status"]),
        statistical_area_unit=opt(Area, a["statistical_area_unit"]),
        weekly_accommodation_costs=_opt_dec(a["weekly_accommodation_costs"]),
        dependent_children_count=a["dependent_children_count"],
        cash_assets=_opt_dec(a["cash_assets"]),
        exempt_cash_asset_status=FactStatus(a["exempt_cash_asset_status"]),
        weekly_income=_opt_dec(a["weekly_income"]),
        ordinary_rate_status=FactStatus(a["ordinary_rate_status"]),
        eldest_dependent_child_under_16=FactStatus(a["eldest_dependent_child_under_16"]),
        # Absent from runs stored before DEC-004 (26 September 2026), whose
        # scenarios had no such fact: unverified, the field default.
        specified_lump_sum_status=FactStatus(a.get("specified_lump_sum_status", "unknown")),
    )
    week = d["assessment_week"]
    return ScenarioRecord(
        household=CombinedHouseholdScenario(
            wff=wff,
            accommodation_supplement=as_,
            as_claimant_is_wff_claimant_or_partner=FactStatus(h["as_claimant_is_wff_claimant_or_partner"]),
        ),
        wff_lookup_date=date.fromisoformat(d["wff_lookup_date"]),
        as_lookup_date=date.fromisoformat(d["as_lookup_date"]),
        assessment_week=AssessmentWeek(date.fromisoformat(week["start"]), date.fromisoformat(week["end"])),
        requested_wff_policy_version=d["requested_wff_policy_version"],
        requested_as_policy_version=d["requested_as_policy_version"],
    )
