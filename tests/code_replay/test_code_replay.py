"""Task 32.4 / 34.2 (Task 34.3 F5): replay a stored run on its *retained code
revision*, not just the code running now.

Stores a run made from a clean, committed checkout, then checks out the run's
recorded `source_commit` into a separate git worktree, builds that revision's
environment with uv, and re-runs the stored scenario there against the
store's retained policy artifacts. The result must equal the stored result,
and the code that ran must be the worktree's own `src/poltika`.

Marked `code_replay`: excluded from the default suite (it builds a second
environment). Needs a clean checkout, git, uv and PostgreSQL; CI runs it.
Locally, with a dirty tree, it skips unless POLTIKA_REQUIRE_CODE_REPLAY is set.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from poltika.scenarios.record import canonical_json, detect_code_identity, run_scenario
from poltika.scenarios.store import ScenarioStore
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import _household, record_from_yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# Runs inside the retained revision's own environment.
_REPLAY_SCRIPT = """
import json, sys
from pathlib import Path
import poltika
from poltika.scenarios.record import CodeIdentity, canonical_json, result_payload, run_scenario
from poltika.scenarios.store import record_from_plain
record = record_from_plain(json.loads(Path(sys.argv[1]).read_text()))
run = run_scenario(record, Path(sys.argv[2]), Path(sys.argv[3]), code=CodeIdentity("replay", None, None, None))
print(json.dumps({"package": str(Path(poltika.__file__).resolve()),
                  "result": json.loads(canonical_json(result_payload(run.result)))}))
"""


@pytest.mark.code_replay
def test_stored_run_replays_on_its_retained_code_revision(database_url: str, tmp_path: Path) -> None:
    if shutil.which("uv") is None or shutil.which("git") is None:
        pytest.skip("uv and git are required")
    code = detect_code_identity(REPO_ROOT)
    if not code.reproducible:
        if os.environ.get("POLTIKA_REQUIRE_CODE_REPLAY"):
            pytest.fail("POLTIKA_REQUIRE_CODE_REPLAY is set but the checkout is not clean and committed")
        pytest.skip("needs a clean, committed checkout")

    store = ScenarioStore.from_url(database_url)
    run = run_scenario(record_from_yaml(_household()), WFF_POLICY_DIR, AS_POLICY_DIR, code=code)
    assert run.manifest.reproducible
    store.save_run(run, WFF_POLICY_DIR, AS_POLICY_DIR)

    stored = store.get_run(run.result_id)
    commit = stored.manifest["code"]["source_commit"]
    wff_dir, as_dir = store.restore_artifacts(stored, tmp_path / "artifacts")
    record_path = tmp_path / "record.json"
    record_path.write_text(canonical_json(stored.record))

    worktree = tmp_path / "revision"
    subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "add", "--detach", str(worktree), commit], check=True)
    try:
        env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "PYTHONPATH")}
        out = subprocess.run(
            ["uv", "run", "--project", str(worktree), "--locked", "python", "-c", _REPLAY_SCRIPT,
             str(record_path), str(wff_dir), str(as_dir)],
            capture_output=True, text=True, check=True, cwd=worktree, env=env,
        )
    finally:
        subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "remove", "--force", str(worktree)], check=False)

    replayed = json.loads(out.stdout.strip().splitlines()[-1])
    assert Path(replayed["package"]).is_relative_to(worktree.resolve())
    assert replayed["result"] == stored.result

