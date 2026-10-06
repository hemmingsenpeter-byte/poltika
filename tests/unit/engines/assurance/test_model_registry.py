"""Task 1.5: every engine has a registry entry and a card.

An engine is found mechanically. It is a public, module-level function whose
name starts with `run_` or `calculate_`, anywhere under `src/poltika`. Each one
found must be an entry point of a registered model, or be listed under
`not_engines` with a reason. Each subpackage of `poltika.engines` must hold a
registered model's entry point, or be listed under `not_model_packages`. Each
registered model needs a current generated card. CI runs this with the rest of
`pytest`.
"""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import pytest
import yaml

from poltika.engines.assurance.model_cards import (
    CARDS_DIR,
    REPO_ROOT,
    Registry,
    card_problems,
    load_registry,
    render_card,
)

SRC = REPO_ROOT / "src"
ENGINE_PREFIXES = ("run_", "calculate_")


def discover_engine_functions(src: Path) -> set[tuple[str, str]]:
    """(dotted module, function) for every public run_*/calculate_* function
    defined at module level under `src/poltika`."""
    found: set[tuple[str, str]] = set()
    for path in sorted((src / "poltika").rglob("*.py")):
        module = ".".join(path.relative_to(src).with_suffix("").parts)
        module = module.removesuffix(".__init__")
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(ENGINE_PREFIXES):
                found.add((module, node.name))
    return found


def unclassified(registry: Registry, src: Path) -> list[str]:
    """Engines and engine packages under `src` that the registry doesn't cover."""
    registered = {(e.module, e.function) for m in registry.models for e in m.entry_points}
    registered |= {(n.module, n.function) for n in registry.not_engines}
    problems = [
        f"{module}.{function} is an engine entry point with no registry entry"
        for module, function in sorted(discover_engine_functions(src) - registered)
    ]
    entry_modules = {e.module for m in registry.models for e in m.entry_points}
    excluded = {p.package for p in registry.not_model_packages}
    engines_dir = src / "poltika" / "engines"
    if engines_dir.is_dir():
        for child in sorted(engines_dir.iterdir()):
            if not (child / "__init__.py").is_file():
                continue
            package = f"poltika.engines.{child.name}"
            covered = any(mod == package or mod.startswith(package + ".") for mod in entry_modules)
            if not covered and package not in excluded:
                problems.append(f"{package} is an engine package with no registry entry")
    return problems


@pytest.fixture(scope="module")
def registry() -> Registry:
    return load_registry()


def test_registry_loads_and_has_the_four_planned_models(registry: Registry) -> None:
    ids = {m.id for m in registry.models}
    assert {"wff_engine", "as_engine", "combined_runner", "population_runner"} <= ids


def test_every_engine_in_the_source_tree_is_registered(registry: Registry) -> None:
    assert unclassified(registry, SRC) == []


def test_every_registered_entry_point_exists(registry: Registry) -> None:
    found = discover_engine_functions(SRC)
    listed = [(e.module, e.function) for m in registry.models for e in m.entry_points]
    listed += [(n.module, n.function) for n in registry.not_engines]
    stale = [f"{module}.{function}" for module, function in listed if (module, function) not in found]
    assert stale == [], "registry names a function that does not exist"


def test_acquisition_coordinator_is_explicitly_classified_as_non_model(
    registry: Registry,
) -> None:
    coordinator = next(
        entry
        for entry in registry.not_engines
        if entry.module == "poltika.data.acquisition.ingest" and entry.function == "run_sources"
    )
    assert coordinator.wraps is None
    assert coordinator.reason


def test_model_wrappers_still_reject_unknown_models(registry: Registry) -> None:
    data = registry.model_dump(mode="json")
    data["not_engines"][0]["wraps"] = "unregistered_model"
    with pytest.raises(ValueError, match="wraps unknown model 'unregistered_model'"):
        Registry.model_validate(data)


@pytest.mark.parametrize("reason", ["", " \n "])
def test_non_models_require_a_documented_reason(registry: Registry, reason: str) -> None:
    data = registry.model_dump(mode="json")
    data["not_engines"][0]["reason"] = reason
    with pytest.raises(ValueError, match="needs a nonempty exclusion reason"):
        Registry.model_validate(data)


def test_every_model_has_a_current_card(registry: Registry) -> None:
    assert card_problems(registry) == []


def test_linked_paths_exist(registry: Registry) -> None:
    missing: list[str] = []
    for m in registry.models:
        paths = [c.path for c in m.validation.cases]
        paths += [*m.validation.tests, *m.validation.reviews]
        paths += [s.source for s in (*m.limitations, *m.model_risks)]
        missing += [f"{m.id}: {p}" for p in paths if not (REPO_ROOT / p).exists()]
    assert missing == []


@pytest.mark.parametrize(
    ("path", "collection"),
    [
        ("policy_specs/working_for_families/spec_cases.yaml", "spec_cases"),
        ("policy_specs/working_for_families/benchmarks.yaml", "benchmarks"),
        ("policy_specs/accommodation_supplement/spec_cases.yaml", "spec_cases"),
        ("policy_specs/accommodation_supplement/benchmarks.yaml", "benchmarks"),
        ("policy_specs/wff_as_interaction/spec_cases.yaml", "interaction_cases"),
        ("policy_specs/wff_as_interaction/golden_households.yaml", "households"),
    ],
)
def test_numeric_case_counts_match_yaml_evidence(
    registry: Registry, path: str, collection: str
) -> None:
    cases = yaml.safe_load((REPO_ROOT / path).read_text())[collection]
    registered_counts = [
        case.count
        for model in registry.models
        for case in model.validation.cases
        if case.path == path
    ]
    assert registered_counts, f"no registered validation evidence for {path}"
    assert all(isinstance(count, int) for count in registered_counts), (
        f"{path}: the case count is available in YAML and must be numeric"
    )
    assert set(registered_counts) == {len(cases)}, f"{path}: registry case counts do not match YAML"


def test_labels_take_the_least_mature_dependency(registry: Registry) -> None:
    # The registry's own levels, with one dependency set lower, change the label.
    levels = registry.validation_levels
    lowered = registry.model_copy(
        update={
            "models": tuple(
                m.model_copy(update={"validation": m.validation.model_copy(update={"level": levels[0]})})
                if m.id == "wff_engine"
                else m
                for m in registry.models
            )
        }
    )
    assert lowered.label("population_runner") == levels[0]
    assert lowered.label("as_engine") == registry.model("as_engine").validation.level


def test_an_engine_without_an_entry_fails(registry: Registry, tmp_path: Path) -> None:
    src = tmp_path / "src"
    shutil.copytree(SRC / "poltika", src / "poltika", ignore=shutil.ignore_patterns("__pycache__"))
    (src / "poltika" / "engines" / "simulator" / "new_benefit.py").write_text(
        "def calculate_new_benefit() -> None:\n    pass\n"
    )
    assert unclassified(registry, src) == [
        (
            "poltika.engines.simulator.new_benefit.calculate_new_benefit is an engine entry point "
            "with no registry entry"
        )
    ]


def test_a_new_engine_package_without_an_entry_fails(registry: Registry, tmp_path: Path) -> None:
    src = tmp_path / "src"
    shutil.copytree(SRC / "poltika", src / "poltika", ignore=shutil.ignore_patterns("__pycache__"))
    package = src / "poltika" / "engines" / "forecast"
    package.mkdir()
    (package / "__init__.py").write_text("")
    assert unclassified(registry, src) == ["poltika.engines.forecast is an engine package with no registry entry"]


def test_a_missing_or_stale_card_fails(registry: Registry, tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    shutil.copytree(CARDS_DIR, cards)
    assert card_problems(registry, cards) == []
    (cards / "wff_engine.md").unlink()
    (cards / "as_engine.md").write_text("stale")
    (cards / "orphan.md").write_text("no entry")
    assert card_problems(registry, cards) == [
        "no card for model 'wff_engine' (expected wff_engine.md)",
        "card for model 'as_engine' is stale; regenerate it",
        "card orphan.md has no registry entry",
    ]


def test_an_async_engine_without_an_entry_fails(registry: Registry, tmp_path: Path) -> None:
    src = tmp_path / "src"
    package = src / "poltika"
    package.mkdir(parents=True)
    (package / "new_benefit.py").write_text("async def calculate_new_benefit() -> None:\n    pass\n")
    assert unclassified(registry, src) == [
        "poltika.new_benefit.calculate_new_benefit is an engine entry point with no registry entry"
    ]


def test_golden_snapshot_count_is_pinned_to_the_fixture(registry: Registry) -> None:
    path = "tests/fixtures/golden_results_v0_1.json"
    snapshot = json.loads((REPO_ROOT / path).read_text())
    registered = {
        case.count
        for model in registry.models
        for case in model.validation.cases
        if case.path == path
    }
    assert registered == {len(snapshot)} == {9}


def test_declared_policy_versions_match_policy_yaml(registry: Registry) -> None:
    declared = {m.id: m.policy_versions for m in registry.models}
    assert declared["wff_engine"] == {"working_for_families": "0.1.0"}
    assert declared["as_engine"] == {"accommodation_supplement": "0.1.1"}
    for model in registry.models:
        for policy_id, version in model.policy_versions.items():
            spec = yaml.safe_load((REPO_ROOT / "policy_specs" / policy_id / "policy.yaml").read_text())
            assert spec["policy_version"] == version, f"{model.id}: {policy_id}"
            assert f"policy {policy_id} {version}" in render_card(registry, model.id).splitlines()[6]
