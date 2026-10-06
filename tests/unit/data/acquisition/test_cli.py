"""The Stats NZ CLI (ADR-0022), driven through `main(argv)`. No live network."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from poltika.data.acquisition.ingest import main
from poltika.data.acquisition.source import FetchRequest, RawResponse

REPO = Path(__file__).resolve().parents[4]
KEY = "SENTINEL-CLI-KEY-77777777"
FIX = Path(__file__).parent / "fixtures" / "stats_nz"
CATALOGUE = """
source_system: stats_nz
sources:
  - id: syn_flow
    verification: synthetic
    dataset: {identifier: "STATSNZ:TST_TST_001"}
    distribution: {identifier: ade_csv, access_kind: api}
    request: {agency_id: STATSNZ, dataflow_id: TST_TST_001, version: "1.0"}
  - id: syn_off
    enabled: false
    verification: unverified, synthetic
    dataset: {identifier: "STATSNZ:TST_OFF"}
    distribution: {identifier: ade_csv, access_kind: api}
    request: {agency_id: STATSNZ, dataflow_id: TST_OFF, version: "1.0"}
"""


class Fake:
    def __init__(self) -> None:
        self.requests: list[FetchRequest] = []

    def send(self, request: FetchRequest, timeout: float) -> RawResponse:
        self.requests.append(request)
        if "/dataflow/" in request.url:
            return RawResponse(200, (), (FIX / "structure_dataflow.xml").read_bytes())
        return RawResponse(200, (), (FIX / "data.csv").read_bytes())


def run(
    argv: list[str], tmp_path: Path, env: dict[str, str] | None = None, fake: Fake | None = None
) -> tuple[int, str, str]:
    cat = tmp_path / "cat.yaml"
    cat.write_text(CATALOGUE)
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["--catalogue", str(cat), *argv],
        env=env or {},
        transport=fake,
        repo_root=tmp_path,
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue(), err.getvalue()


def test_list_needs_no_key(tmp_path: Path) -> None:
    code, out, _ = run(["--list"], tmp_path)
    assert code == 0
    assert "syn_flow\tenabled\tSTATSNZ:TST_TST_001\tade_csv" in out
    assert "syn_off\tdisabled" in out


def test_shipped_catalogue_lists() -> None:
    out = io.StringIO()
    assert main(["--list"], env={}, repo_root=REPO, stdout=out) == 0
    assert "stats_nz_ade_inc_inc_011" in out.getvalue()


def test_missing_key_is_exit_2_with_clear_error_and_no_fetch(tmp_path: Path) -> None:
    fake = Fake()
    code, _, err = run(["--all"], tmp_path, env={}, fake=fake)
    assert code == 2
    assert "POLTIKA_STATS_NZ_API_KEY" in err
    assert fake.requests == []
    assert not (tmp_path / "data").exists()


def test_dry_run_needs_no_key_and_writes_nothing(tmp_path: Path) -> None:
    fake = Fake()
    code, out, _ = run(
        ["--all", "--dry-run", "--archive-dir", str(tmp_path / "x")], tmp_path, fake=fake
    )
    assert code == 0
    assert fake.requests == []
    assert not (tmp_path / "x").exists()
    assert "fingerprint:" in out and "syn_off" in out and "skipped" in out


def test_dataset_real_run_preserves_and_never_echoes_key(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "arch"
    env = {"POLTIKA_STATS_NZ_API_KEY": KEY}
    code, out, err = run(
        ["--dataset", "syn_flow", "--archive-dir", str(root), "--no-enrich"],
        tmp_path,
        env=env,
        fake=Fake(),
    )
    assert code == 0
    assert "content blob: created" in out and "summary: 1 ok, 0 failed" in out
    cap = capsys.readouterr()
    for text in (out, err, cap.out, cap.err):
        assert KEY not in text
    for path in root.rglob("*"):
        if path.is_file():
            assert KEY.encode() not in path.read_bytes()


def test_archive_dir_falls_back_to_env_then_default(tmp_path: Path) -> None:
    env = {"POLTIKA_STATS_NZ_API_KEY": KEY, "POLTIKA_SOURCE_ARCHIVE_DIR": str(tmp_path / "envdir")}
    assert run(["--all", "--no-enrich"], tmp_path, env=env, fake=Fake())[0] == 0
    assert (tmp_path / "envdir" / "records").is_dir()
    env2 = {"POLTIKA_STATS_NZ_API_KEY": KEY}
    assert run(["--all", "--no-enrich"], tmp_path, env=env2, fake=Fake())[0] == 0
    assert (tmp_path / "data" / "source_archive" / "runtime" / "records").is_dir()


def test_acquisition_failure_exits_1(tmp_path: Path) -> None:
    class Down:
        def send(self, request: FetchRequest, timeout: float) -> RawResponse:
            return RawResponse(403, (), b"forbidden")

    code, out, err = run(
        ["--all", "--no-enrich"],
        tmp_path,
        env={"POLTIKA_STATS_NZ_API_KEY": KEY},
        fake=Down(),  # type: ignore[arg-type]
    )
    assert code == 1
    assert "FAILED" in out and "403" in out and KEY not in out + err


def test_unknown_and_disabled_dataset_are_usage_errors(tmp_path: Path) -> None:
    env = {"POLTIKA_STATS_NZ_API_KEY": KEY}
    assert run(["--dataset", "nope"], tmp_path, env=env)[0] == 2
    code, _, err = run(["--dataset", "syn_off"], tmp_path, env=env)
    assert code == 2 and "disabled" in err


def test_one_mode_is_required(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        run([], tmp_path)
    assert exc.value.code == 2
