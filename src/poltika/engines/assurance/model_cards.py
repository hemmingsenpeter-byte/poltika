"""Task 1.5: the model registry, and the model cards generated from it.

`model_registry/registry.yaml` has one entry per model (engine or runner).
`render_card()` turns an entry into a Markdown card, and
`python -m poltika.engines.assurance.model_cards` writes every card to
`model_registry/cards/<id>.md`. With `--check` it writes nothing and exits 1
if a card is missing, stale or has no registry entry. A test runs the same
check in CI (`tests/unit/engines/assurance/test_model_registry.py`).

The rules are in `doctrine/model-governance.md`. This module calculates no
policy outcome.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

REPO_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_DIR = REPO_ROOT / "model_registry"
REGISTRY_PATH = REGISTRY_DIR / "registry.yaml"
CARDS_DIR = REGISTRY_DIR / "cards"

# The eight classes of doctrine/epistemic-constitution.md.
EvidenceClass = Literal[
    "Fact",
    "Rule",
    "Estimate",
    "Transferred estimate",
    "Assumption",
    "Scenario",
    "Model output",
    "AI hypothesis",
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EntryPoint(_Strict):
    module: str
    function: str


class ValidationCase(_Strict):
    kind: str
    path: str
    count: int | Literal["unknown"]


class Validation(_Strict):
    level: str
    basis: str
    cases: tuple[ValidationCase, ...]
    tests: tuple[str, ...]
    reviews: tuple[str, ...]
    open_items: tuple[str, ...]


class Statement(_Strict):
    text: str
    source: str


class ChangeRecord(_Strict):
    date: str
    change: str
    why: str
    evidence: str
    validation_rerun: str
    approval: str


class Model(_Strict):
    id: str
    name: str
    kind: Literal["engine", "runner"]
    version: str
    version_basis: str
    owner: str
    purpose: str
    entry_points: tuple[EntryPoint, ...]
    depends_on: tuple[str, ...]
    validation: Validation
    evidence_classes_consumed: tuple[EvidenceClass, ...]
    evidence_note: str
    limitations: tuple[Statement, ...]
    model_risks: tuple[Statement, ...]
    change_log: tuple[ChangeRecord, ...]

    @model_validator(mode="after")
    def _complete(self) -> Model:
        if not (self.entry_points and self.limitations and self.change_log):
            raise ValueError(f"model '{self.id}' needs entry points, limitations and a change log")
        if not self.validation.cases:
            raise ValueError(f"model '{self.id}' needs at least one linked validation case")
        return self


class NotEngine(_Strict):
    module: str
    function: str
    reason: str
    wraps: str | None

    @model_validator(mode="after")
    def _documented(self) -> NotEngine:
        if not self.reason.strip():
            raise ValueError(f"{self.module}.{self.function} needs a nonempty exclusion reason")
        return self


class NotModelPackage(_Strict):
    package: str
    reason: str


class Registry(_Strict):
    schema_version: str
    validation_levels: tuple[str, ...]
    models: tuple[Model, ...]
    not_engines: tuple[NotEngine, ...]
    not_model_packages: tuple[NotModelPackage, ...]

    @model_validator(mode="after")
    def _consistent(self) -> Registry:
        ids = [m.id for m in self.models]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate model id in the registry")
        known = set(ids)
        for m in self.models:
            if m.validation.level not in self.validation_levels:
                raise ValueError(f"model '{m.id}': unknown validation level '{m.validation.level}'")
            for dep in m.depends_on:
                if dep not in known:
                    raise ValueError(f"model '{m.id}' depends on unknown model '{dep}'")
        for n in self.not_engines:
            if n.wraps is not None and n.wraps not in known:
                raise ValueError(f"{n.module}.{n.function} wraps unknown model '{n.wraps}'")
        return self

    def model(self, model_id: str) -> Model:
        return next(m for m in self.models if m.id == model_id)

    def label(self, model_id: str) -> str:
        """The validation level of the least mature model this one relies on,
        itself included."""
        seen: set[str] = set()
        stack = [model_id]
        levels: list[str] = []
        while stack:
            current = self.model(stack.pop())
            if current.id in seen:
                continue
            seen.add(current.id)
            levels.append(current.validation.level)
            stack.extend(current.depends_on)
        return min(levels, key=self.validation_levels.index)


def load_registry(path: Path = REGISTRY_PATH) -> Registry:
    return Registry.model_validate(yaml.safe_load(path.read_text()))


def _bullets(items: tuple[str, ...]) -> list[str]:
    return [f"- {item}" for item in items] or ["- none"]


def _one_line(text: str) -> str:
    return " ".join(text.split())


def render_card(registry: Registry, model_id: str) -> str:
    m = registry.model(model_id)
    v = m.validation
    lines = [
        f"# Model card: {m.name}",
        "",
        "Generated from `model_registry/registry.yaml` by",
        "`python -m poltika.engines.assurance.model_cards`. Do not edit by hand.",
        "",
        f"- **Id:** `{m.id}` ({m.kind})",
        f"- **Version:** {m.version}. {_one_line(m.version_basis)}",
        f"- **Owner:** {_one_line(m.owner)}",
        f"- **Validation status:** `{v.level}`",
        (
            f"- **Computed dependency label:** `{registry.label(m.id)}` "
            "(the least mature model it relies on; not yet attached to runtime outputs)"
        ),
        "",
        "## Purpose",
        "",
        _one_line(m.purpose),
        "",
        "## Methods",
        "",
        "Entry points:",
        "",
        *[f"- `{e.module}.{e.function}`" for e in m.entry_points],
        "",
        "Relies on: " + (", ".join(f"`{d}`" for d in m.depends_on) or "no other registered model") + ".",
        "",
        "Evidence classes consumed: " + ", ".join(m.evidence_classes_consumed) + ".",
        "",
        _one_line(m.evidence_note),
        "",
        "## Validation",
        "",
        _one_line(v.basis),
        "",
        "Validation cases:",
        "",
        *[f"- {c.kind}: `{c.path}` ({c.count})" for c in v.cases],
        "",
        "Tests:",
        "",
        *_bullets(tuple(f"`{t}`" for t in v.tests)),
        "",
        "Reviews:",
        "",
        *_bullets(tuple(f"`{r}`" for r in v.reviews)),
        "",
        "Open items:",
        "",
        *_bullets(tuple(_one_line(o) for o in v.open_items)),
        "",
        "## Limitations",
        "",
        *_bullets(tuple(f"{_one_line(s.text)} (`{s.source}`)" for s in m.limitations)),
        "",
        "## Known model risks and failure modes",
        "",
        *_bullets(tuple(f"{_one_line(s.text)} (`{s.source}`)" for s in m.model_risks)),
        "",
        "## Change log",
        "",
        "| Date | What changed | Why | Evidence | Validation re-run | Approval |",
        "| --- | --- | --- | --- | --- | --- |",
        *[
            f"| {c.date} | {_one_line(c.change)} | {_one_line(c.why)} | `{c.evidence}` "
            f"| {_one_line(c.validation_rerun)} | {_one_line(c.approval)} |"
            for c in m.change_log
        ],
        "",
    ]
    return "\n".join(lines)


def card_problems(registry: Registry, cards_dir: Path = CARDS_DIR) -> list[str]:
    """Every card that is missing, stale or has no registry entry."""
    problems: list[str] = []
    expected = {f"{m.id}.md" for m in registry.models}
    for m in registry.models:
        card = cards_dir / f"{m.id}.md"
        if not card.is_file():
            problems.append(f"no card for model '{m.id}' (expected {card.name})")
        elif card.read_text() != render_card(registry, m.id):
            problems.append(f"card for model '{m.id}' is stale; regenerate it")
    if cards_dir.is_dir():
        for card in sorted(cards_dir.glob("*.md")):
            if card.name not in expected:
                problems.append(f"card {card.name} has no registry entry")
    return problems


def write_cards(registry: Registry, cards_dir: Path = CARDS_DIR) -> None:
    cards_dir.mkdir(parents=True, exist_ok=True)
    for m in registry.models:
        (cards_dir / f"{m.id}.md").write_text(render_card(registry, m.id))


def main(argv: list[str]) -> int:
    registry = load_registry()
    if argv == ["--check"]:
        problems = card_problems(registry)
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    if argv:
        print("usage: python -m poltika.engines.assurance.model_cards [--check]")
        return 2
    write_cards(registry)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
