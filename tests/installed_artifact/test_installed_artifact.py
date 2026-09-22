"""Task 21's deployment gate, second half (ADR-0011): confirm the API
actually serves a request successfully from an *installed* artifact, not
merely that the Task 21 startup check fails cleanly when `policy_specs/`
is missing (already covered by `tests/unit/api/test_wff_api.py`'s
`test_startup_fails_loudly_if_policy_directory_is_missing`).

Builds the real wheel (`uv build --wheel`), installs it into a throwaway
venv with no source checkout on `sys.path`, points `POLTIKA_POLICY_SPECS_
DIR` at this checkout's `policy_specs/` (the deploy-time mount
convention -- a real deployment would mount/copy this directory itself;
reusing the checkout's copy here only avoids duplicating it, it is not
importing from the checkout's `src/`), and runs `_probe_installed_api.py`
inside that venv's own interpreter.

Marked `installed_artifact` -- excluded from the default `pytest -q` run
(`pyproject.toml`'s `addopts`) because building a wheel and creating a
venv is much slower than the rest of the suite. Run explicitly with
`uv run pytest -m installed_artifact -v`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_SCRIPT = Path(__file__).resolve().parent / "_probe_installed_api.py"


def _run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, **kwargs)  # type: ignore[arg-type]
    if result.returncode != 0:
        pytest.fail(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


@pytest.mark.installed_artifact
def test_installed_wheel_serves_a_request_end_to_end(tmp_path: Path) -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv not on PATH -- cannot build/install the wheel")

    dist_dir = tmp_path / "dist"
    venv_dir = tmp_path / "venv"

    # Build the real wheel from this checkout -- not a mock, not a copy of
    # src/ into a fake package layout.
    _run(["uv", "build", "--wheel", "--out-dir", str(dist_dir)], cwd=REPO_ROOT)
    wheels = list(dist_dir.glob("poltika-*.whl"))
    assert wheels, f"no wheel produced in {dist_dir}"
    wheel = wheels[0]

    # A venv with nothing but the wheel's own declared dependencies
    # (fastapi, pydantic, pyyaml) plus httpx, which TestClient needs but
    # which is a dev-only extra, not a poltika runtime dependency.
    _run(["uv", "venv", str(venv_dir)])
    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    _run(["uv", "pip", "install", "--python", str(python), str(wheel), "httpx>=0.27"])

    # Deploy-time mount convention (ADR-0011): point at this checkout's
    # policy_specs/ directly, standing in for whatever a real deployment
    # would mount/copy there. The installed poltika package on sys.path
    # inside the venv has no src/ checkout at all -- only the wheel.
    probe_env = dict(os.environ)
    probe_env["POLTIKA_POLICY_SPECS_DIR"] = str(REPO_ROOT / "policy_specs")
    probe = subprocess.run(
        [str(python), str(PROBE_SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,  # deliberately NOT the repo root -- no accidental src/ import
        env=probe_env,
    )

    assert probe.returncode == 0, f"probe failed:\nstdout:\n{probe.stdout}\nstderr:\n{probe.stderr}"
    assert "PROBE_OK" in probe.stdout
