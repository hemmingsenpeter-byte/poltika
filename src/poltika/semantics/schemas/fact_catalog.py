"""v0.3 Task 1b.1 (ADR-0016): the fact catalogue model.

`policy_specs/<policy>/facts.yaml` holds one entry per fact an engine can
report in `missing_facts`, keyed by the same id. It gives the intake planner
a question to ask and the conditional resolver the admissible answers to
branch over. It is not a statutory file. Question wording is reviewed like
specification text, but it sits outside the protected, hash-bound
`policy.yaml`, so wording changes never touch a statutory value.

Kinds of fact:

- `fact_status`: `answers` maps exactly `verified` and `excluded` to plain
  labels. Whether "verified" means the condition holds (a precondition) or
  that a trigger does not apply (an exclusion trigger) is the engine
  field's own semantics, and the labels must say which.
- `enum`: `values` maps each admissible engine value to a label.
- `money` or `count`: numeric. There's no finite domain to branch over.
- `attestation`: a yes/no declaration about how another input was derived
  (for example that net family scheme income follows ME 3). It is never
  branched on, because assuming it was done would be assuming a fact.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Scope = Literal["wff", "accommodation_supplement", "household"]
Kind = Literal["fact_status", "enum", "money", "count", "attestation"]

_RULE = re.compile(r"^[A-Z]+-\d+$|^Task \d+(\.\d+)?|^DEC-\d+")


class FactEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    scope: Scope
    rule: str
    question: str = Field(min_length=10)
    kind: Kind
    answers: dict[str, str] | None = None  # fact_status only
    values: dict[str, str] | None = None  # enum only
    unit: str | None = None  # money only

    @model_validator(mode="after")
    def _shape(self) -> FactEntry:
        if not _RULE.match(self.rule):
            raise ValueError(f"'{self.id}': rule '{self.rule}' is not a rule id, task or decision")
        if self.kind == "fact_status":
            if self.answers is None or set(self.answers) != {"verified", "excluded"}:
                raise ValueError(
                    f"'{self.id}': fact_status answers must be exactly verified and excluded"
                )
        elif self.answers is not None:
            raise ValueError(f"'{self.id}': answers are only for fact_status facts")
        if self.kind == "enum":
            if not self.values:
                raise ValueError(f"'{self.id}': an enum fact needs values")
        elif self.values is not None:
            raise ValueError(f"'{self.id}': values are only for enum facts")
        if (self.kind == "money") != (self.unit is not None):
            raise ValueError(f"'{self.id}': a unit is required for money facts, and only then")
        return self

    @property
    def finite(self) -> bool:
        return self.kind in ("fact_status", "enum")

    def domain(self) -> tuple[str, ...]:
        """Admissible engine values, in catalogue order."""
        if self.kind == "fact_status":
            return ("verified", "excluded")
        return tuple(self.values or ())


class FactCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["0.1"]
    policy_id: str
    wording_status: Literal["drafted", "reviewed"]
    facts: tuple[FactEntry, ...]

    @model_validator(mode="after")
    def _unique(self) -> FactCatalog:
        ids = [f.id for f in self.facts]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate fact ids: {duplicates}")
        return self
