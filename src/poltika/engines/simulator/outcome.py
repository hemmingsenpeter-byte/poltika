"""The outcome types every simulator module returns.

A component resolves to `calculated`, `needs_review` or `unsupported`
(`ComponentOutcome`), carrying a value only when calculated
(`ComponentResult`). `FactStatus` is the tri-state for any fact that gates
a component. These were first written for WFF (Task 12) and are shared by
Accommodation Supplement (Task 23) and everything downstream, so they live
here rather than in either policy's module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Literal

from poltika.engines.simulator.trace import ComponentTrace

ComponentOutcome = Literal["calculated", "needs_review", "unsupported"]


class FactStatus(str, Enum):
    """Tri-state for any fact that gates a component.

    One shared tri-state covers both flavours of gate the calculation
    contracts use:

    - A **domain/eligibility precondition** (e.g. WFF's "in-work eligibility
      established"): `VERIFIED` means the condition holds and the branch may
      proceed; `EXCLUDED` means it's verified *not* to hold, so the scenario
      is structurally outside this branch (`unsupported`); `UNKNOWN` means
      it hasn't been verified either way (`needs_review`).
    - A **known exclusion trigger** (e.g. WFF's MD 14/15 protected credit):
      `VERIFIED` means verified that the trigger does *not* apply (the
      ordinary branch proceeds); `EXCLUDED` means verified that it *does*
      apply (`unsupported` -- the protected/direct-abatement/etc. pathway
      needs its own specification); `UNKNOWN` means unverified
      applicability (`needs_review`).

    Never a bare `bool`: SCHEMA.md forbids silently defaulting a missing
    fact to a value that would yield entitlement, and a bool has no way to
    represent "not verified" distinctly from "verified false".
    """

    VERIFIED = "verified"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ComponentResult:
    """One component's outcome. `value` is populated only when
    `outcome == "calculated"` -- the calculators' equivalent of the loader's
    `ParameterResolution` contract: never treat a missing value as zero.
    """

    outcome: ComponentOutcome
    value: Decimal | None = None
    reason: str | None = None
    # Task 31: what this result was computed from. Excluded from equality,
    # so attaching a trace never changes whether two results compare equal.
    trace: ComponentTrace | None = field(default=None, compare=False)
