"""Task 32.2-32.4: the PostgreSQL scenario store, against a throwaway real
PostgreSQL server (never SQLite, per ADR-0013)."""

from __future__ import annotations

import shutil
import socket
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from poltika.common.errors import ImmutableRecordError, StoreError
from poltika.scenarios.record import CodeIdentity, run_scenario
from poltika.scenarios.store import ScenarioStore, migrate
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import _household, record_from_yaml

pytestmark = pytest.mark.postgres

_CANDIDATE_BIN_DIRS = [Path("/usr/local/opt/postgresql@16/bin"), Path("/opt/homebrew/opt/postgresql@16/bin")]
CODE = CodeIdentity("0.1.0", None, None, None)


def _pg_bin() -> Path | None:
    found = shutil.which("pg_ctl")
    if found:
        return Path(found).parent
    return next((d for d in _CANDIDATE_BIN_DIRS if (d / "pg_ctl").exists()), None)


@pytest.fixture(scope="session")
def database_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    bin_dir = _pg_bin()
    if bin_dir is None:
        pytest.skip("PostgreSQL server binaries not installed")
    data = tmp_path_factory.mktemp("pgdata")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    subprocess.run([str(bin_dir / "initdb"), "-D", str(data), "-U", "poltika", "--auth=trust"], check=True, capture_output=True)
    subprocess.run(
        [str(bin_dir / "pg_ctl"), "-D", str(data), "-o", f"-p {port} -c listen_addresses=127.0.0.1 -c unix_socket_directories=''", "-l", str(data / "log"), "-w", "start"],
        check=True, capture_output=True,
    )
    try:
        subprocess.run([str(bin_dir / "createdb"), "-h", "127.0.0.1", "-p", str(port), "-U", "poltika", "poltika"], check=True, capture_output=True)
        url = f"postgresql+psycopg://poltika@127.0.0.1:{port}/poltika"
        migrate(url)
        yield url
    finally:
        subprocess.run([str(bin_dir / "pg_ctl"), "-D", str(data), "-m", "fast", "stop"], capture_output=True, check=False)


def _copy_policies(tmp_path: Path) -> tuple[Path, Path]:
    wff, as_ = tmp_path / "wff" / "working_for_families", tmp_path / "as" / "accommodation_supplement"
    shutil.copytree(WFF_POLICY_DIR, wff)
    shutil.copytree(AS_POLICY_DIR, as_)
    return wff, as_


def test_save_and_fetch_round_trips_the_record(database_url: str) -> None:
    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)  # identical content: a no-op
    stored = store.get_run(run.result_id)
    assert stored.record == run.record
    assert stored.scenario_id == run.scenario_id
    assert stored.result["accommodation_supplement"]["value"] == "176"


def test_replay_reproduces_after_the_current_policy_files_change(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    # Change the current AS policy after the run (a different threshold).
    policy = as_ / "policy.yaml"
    policy.write_text(policy.read_text().replace("value: 168,", "value: 170,"))
    assert store.replay(run.result_id, tmp_path / "replay") is True


def test_rerun_against_current_files_is_a_new_run_reporting_drift(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    policy = as_ / "policy.yaml"
    policy.write_text(policy.read_text().replace("value: 168,", "value: 170,"))
    drift = store.rerun_against_current(run.result_id, wff, as_, code=CODE)
    assert drift.changed_artifacts == ("accommodation_supplement/policy.yaml",)
    assert drift.result_changed
    assert drift.new_result_id != run.result_id
    assert store.get_run(run.result_id).result["accommodation_supplement"]["value"] == "176"  # original untouched


def test_drift_is_reported_even_when_amounts_are_unchanged(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    store.save_run(run, wff, as_)
    with (wff / "sources.yaml").open("a") as f:
        f.write("\n# catalogue note added\n")
    drift = store.rerun_against_current(run.result_id, wff, as_, code=CODE)
    assert drift.changed_artifacts == ("working_for_families/sources.yaml",)
    assert not drift.result_changed


def test_saving_a_run_whose_files_changed_since_the_run_is_refused(database_url: str, tmp_path: Path) -> None:
    store = ScenarioStore.from_url(database_url)
    wff, as_ = _copy_policies(tmp_path)
    run = run_scenario(record_from_yaml(_household()), wff, as_, code=CODE)
    with (as_ / "specification.md").open("a") as f:
        f.write("\nedited\n")
    with pytest.raises(StoreError, match="no longer matches"):
        store.save_run(run, wff, as_)


def test_a_stored_id_cannot_be_rewritten(database_url: str) -> None:
    from dataclasses import replace

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    forged = replace(run, result=replace(run.result, contradictions=("forged",)))
    with pytest.raises(ImmutableRecordError):
        store.save_run(forged, WFF_POLICY_DIR, AS_POLICY_DIR)


def test_replay_fails_explicitly_when_an_artifact_is_missing(database_url: str, tmp_path: Path) -> None:
    # Runs last in this file: the deleted artifact is content-addressed and
    # shared by other stored runs in the session database.
    from sqlalchemy import create_engine, delete

    from poltika.scenarios.store import artifact_table

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household("g1_sole_parent_two_children_non_beneficiary")), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    sha = dict(run.manifest.policy_files)["working_for_families/specification.md"]
    with create_engine(database_url).begin() as conn:
        conn.execute(delete(artifact_table).where(artifact_table.c.sha256 == sha))
    with pytest.raises(StoreError, match="missing"):
        store.replay(run.result_id, tmp_path / "replay")
