"""Source-preservation archive (ADR-0022): the architecture boundary.

Adds to `tests/unit/data/test_boundary.py`; never replaces it. The archive is
evidence of what a source published, not governed modelling data. Nothing on
the governed path (registry, context, transform, transforms/) may import it,
it may import nothing downstream, and nothing outside `poltika.data.acquisition`
may name its location.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from poltika.data.registry import DatasetRegistry
from tests.unit.data.test_boundary import DATA_PACKAGE, SRC, _imports

ACQUISITION = DATA_PACKAGE / "acquisition"
ACQUISITION_MODULE = "poltika.data.acquisition"
GOVERNED = ("poltika.data.registry", "poltika.data.context", "poltika.data.transform")
DOWNSTREAM = (
    "poltika.engines",
    "poltika.policy",
    "poltika.scenarios",
    "poltika.api",
    "poltika.llm",
)
_ARCHIVE_NAME = re.compile(r"source_archive|POLTIKA_SOURCE_ARCHIVE_DIR")
REPO = SRC.parents[1]


def _is_acquisition(name: str) -> bool:
    return name == ACQUISITION_MODULE or name.startswith(ACQUISITION_MODULE + ".")


def _imports_acquisition(path: Path) -> list[str]:
    return sorted(n for n in _imports(path) if _is_acquisition(n))


def _governed_files() -> list[Path]:
    files = [
        DATA_PACKAGE / "registry.py",
        DATA_PACKAGE / "context.py",
        DATA_PACKAGE / "transform.py",
    ]
    return files + sorted((DATA_PACKAGE / "transforms").rglob("*.py"))


def _forbidden_acquisition_imports(path: Path) -> list[str]:
    forbidden = (*GOVERNED, *DOWNSTREAM)
    return sorted(
        n
        for n in _imports(path)
        if n.startswith(forbidden)
        or n == "poltika.data.transforms"
        or n.startswith("poltika.data.transforms.")
    )


def _names_archive(path: Path) -> bool:
    return bool(_ARCHIVE_NAME.search(path.read_text()))


def test_governed_data_modules_do_not_import_the_archive() -> None:
    files = _governed_files()
    assert len(files) >= 3
    assert {f"{f.relative_to(DATA_PACKAGE)}": _imports_acquisition(f) for f in files} == {
        f"{f.relative_to(DATA_PACKAGE)}": [] for f in files
    }


def test_the_archive_imports_nothing_governed_or_downstream() -> None:
    files = sorted(ACQUISITION.rglob("*.py"))
    assert files
    offenders = {str(f.relative_to(SRC)): _forbidden_acquisition_imports(f) for f in files}
    assert {k: v for k, v in offenders.items() if v} == {}


def test_nothing_downstream_can_import_the_archive_explicitly() -> None:
    for layer in ("engines", "policy", "scenarios", "api", "llm"):
        for path in (SRC / layer).rglob("*.py") if (SRC / layer).exists() else []:
            assert _imports_acquisition(path) == [], str(path.relative_to(SRC))


def test_nothing_else_in_the_package_imports_the_archive() -> None:
    offenders = sorted(
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if ACQUISITION not in p.parents and _imports_acquisition(p)
    )
    assert offenders == []


def test_nothing_outside_the_archive_names_its_location() -> None:
    offenders = sorted(
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if ACQUISITION not in p.parents and _names_archive(p)
    )
    assert offenders == []


def test_dataset_registry_never_sees_the_archive(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "metadata" / "datasets").mkdir(parents=True)
    runtime = data_root / "source_archive" / "runtime"
    for sub in ("blobs/sha256/ab", "records/stats_nz/x", "metadata/stats_nz/x"):
        (runtime / sub).mkdir(parents=True)
    (runtime / "blobs/sha256/ab/abcd").write_bytes(b"bytes")
    (runtime / "records/stats_nz/x/r.json").write_text("{}")
    (runtime / "metadata/stats_nz/x/m.json").write_text("{}")
    assert DatasetRegistry(data_root).snapshots() == []


def test_snapshot_guard_does_not_cover_the_archive_runtime() -> None:
    workflow = (REPO / ".github" / "workflows" / "data-snapshot-guard.yml").read_text()
    guarded = re.findall(r"'(data/[^']*)'", workflow)
    assert guarded, "guard paths not found"
    runtime = "data/source_archive/runtime/x"
    assert not any(runtime.startswith(p) for p in guarded if not p.startswith(":"))


def test_runtime_is_gitignored_narrowly() -> None:
    lines = [ln.strip() for ln in (REPO / ".gitignore").read_text().splitlines()]
    assert "data/source_archive/runtime/" in lines
    assert not {"data/", "data/source_archive/", "data/raw/"} & set(lines)


def test_source_definitions_are_not_in_the_governed_metadata_tree() -> None:
    manifests = REPO / "data" / "metadata" / "datasets"
    for p in manifests.glob("*.yaml"):
        assert "source_archive" not in yaml.safe_load(p.read_text()).get("raw_file", "")


def test_the_checks_would_catch_planted_violations(tmp_path: Path) -> None:
    importing = tmp_path / "bad_import.py"
    importing.write_text("from poltika.data.acquisition.archive import SourceArchive\n")
    assert _imports_acquisition(importing) == ["poltika.data.acquisition.archive"]
    relative = tmp_path / "ok.py"
    relative.write_text("import os\n")
    assert _imports_acquisition(relative) == []

    reaching = tmp_path / "bad_reach.py"
    reaching.write_text(
        "from poltika.data.registry import DatasetRegistry\nimport poltika.policy\n"
    )
    assert _forbidden_acquisition_imports(reaching) == [
        "poltika.data.registry",
        "poltika.policy",
    ]

    naming = tmp_path / "bad_name.py"
    naming.write_text('ROOT = "data/source_archive/runtime"\n')
    assert _names_archive(naming)
    env = tmp_path / "bad_env.py"
    env.write_text('os.environ["POLTIKA_SOURCE_ARCHIVE_DIR"]\n')
    assert _names_archive(env)
