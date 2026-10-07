"""Task B0.1.2 (ADR-0023): the scenario workspace contract.

A workspace is a scenario, the run being viewed, and seven tabs. Each tab
holds typed blocks the web app renders with one component per block type;
no component knows which policy or model produced a block (ADR-0018).

Every value is the string the backend produced (amounts already rounded
once, a component that was not calculated shown as its outcome, never 0).
The frontend formats; it never sums, converts or derives a value.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Cell = str | None
TabStatus = Literal["available", "empty", "unavailable", "deferred"]
TabId = Literal[
    "overview", "fiscal", "distribution", "evidence", "assumptions", "technical", "audit"
]
# The epistemic constitution's eight classes (doctrine/epistemic-constitution.md).
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


class _Block(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str | None = None


class Column(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    # money, count and share cells are numeric strings or an outcome word.
    kind: Literal["text", "money", "count", "share"]
    group: str | None = None
    precision: Literal["household_rule", "population_estimate"] = "household_rule"


class TableBlock(_Block):
    type: Literal["table"] = "table"
    columns: list[Column]
    rows: list[list[Cell]]
    notes: list[str] = []


class HorizonYear(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    modelled: bool
    note: str


class HorizonBlock(_Block):
    type: Literal["horizon"] = "horizon"
    years: list[HorizonYear]


class ListBlock(_Block):
    type: Literal["list"] = "list"
    items: list[str]


class Unit(BaseModel):
    """What a value is measured in. `label` is the engine's own unit string;
    `period` and `currency` state it structurally so nothing is guessed."""

    model_config = ConfigDict(frozen=True)

    label: str
    currency: Literal["NZD"] | None
    period: Literal["tax_year", "week"] | None
    basis: Literal["nominal"] | None
    per: Literal["household", "population"] | None


class ProvenanceRef(BaseModel):
    """Where to look next: the tab and block that explain this value."""

    model_config = ConfigDict(frozen=True)

    tab: TabId
    block_id: str


class MetricValue(BaseModel):
    """One option's value. `value` is a decimal string when `outcome` is
    `calculated`, and null otherwise; `outcome` then says why."""

    model_config = ConfigDict(frozen=True)

    option: str
    value: Cell
    outcome: Literal["calculated", "needs_review", "unsupported", "not_calculated"]


class MetricBlock(_Block):
    type: Literal["metric"] = "metric"
    label: str
    unit: Unit
    values: list[MetricValue]
    # household_rule: legal precision. population_estimate: three
    # significant figures on screen (P3); stored values keep full precision.
    precision: Literal["household_rule", "population_estimate"]
    evidence_class: EvidenceClass
    context: str
    provenance: list[ProvenanceRef] = []


class Notice(_Block):
    type: Literal["notice"] = "notice"
    tone: Literal["info", "caution", "unavailable"]
    text: str


class SourceCheckOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    date: str


class SourceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str | None
    url: str | None
    kind: str | None
    source_type: str | None
    authority_rank: int | None
    checked_on: list[SourceCheckOut]
    check_evidence: list[str]


class SourcesBlock(_Block):
    type: Literal["sources"] = "sources"
    policy_id: str
    policy_version: str | None
    sources: list[SourceItem]


class AuditField(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    value: Cell
    note: str | None = None


class AuditRecordBlock(_Block):
    type: Literal["audit_record"] = "audit_record"
    fields: list[AuditField]


class ChainStep(BaseModel):
    model_config = ConfigDict(frozen=True)

    component_id: str
    step_id: str
    rule_id: str | None
    description: str
    inputs: dict[str, Cell] = {}
    result: Cell


class CalculationChainBlock(_Block):
    type: Literal["calculation_chain"] = "calculation_chain"
    steps: list[ChainStep]


class ModelRefItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    version: str
    label: str


class ModelRefBlock(_Block):
    type: Literal["model_ref"] = "model_ref"
    models: list[ModelRefItem]


Block = Annotated[
    TableBlock
    | HorizonBlock
    | ListBlock
    | MetricBlock
    | Notice
    | SourcesBlock
    | AuditRecordBlock
    | CalculationChainBlock
    | ModelRefBlock,
    Field(discriminator="type"),
]


class Tab(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: TabId
    title: str
    status: TabStatus
    note: str | None = None
    blocks: list[Block] = []


class ScenarioHeader(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: str
    kind: Literal["reform", "household"]
    title: str
    description: str
    created_at: datetime | None


class RunHeader(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    created_at: datetime | None
    reproducible: bool | None


class RunRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    created_at: datetime | None


class Context(BaseModel):
    """What the results are relative to."""

    model_config = ConfigDict(frozen=True)

    law_baseline: str
    reference_period: str
    policy_versions: dict[str, str]
    population_label: str | None
    synthetic: bool


class Workspace(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario: ScenarioHeader
    run: RunHeader | None
    runs: list[RunRef]
    context: Context | None
    tabs: list[Tab]


TAB_TITLES: dict[TabId, str] = {
    "overview": "Overview",
    "fiscal": "Fiscal",
    "distribution": "Distribution",
    "evidence": "Evidence",
    "assumptions": "Assumptions",
    "technical": "Technical",
    "audit": "Audit",
}
