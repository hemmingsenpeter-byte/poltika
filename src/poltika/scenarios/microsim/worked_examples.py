"""Worked examples: named households run once under a reform.

The population runner (`runner.py`) runs every household in a population.
An analyst also wants a handful of standard family types shown one by one,
before and after. Each is an ordinary `ScenarioRecord` run twice through
`run_combined_household`, with the approved parameters and with the reform's
copy, exactly as the runner does. There is no other calculation path, and
the per-component outcome and delta rules are the runner's own (`_delta`).

Amounts stay in each component's own period (`UNITS`): WFF per tax year, AS
per week. Nothing here adds them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim.reform import Reform, apply_reform
from poltika.scenarios.microsim.runner import (
    COMPONENTS,
    ComponentDelta,
    _component,
    _delta,
    _run,
)
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.record import ScenarioRecord


@dataclass(frozen=True)
class WorkedExample:
    example_id: str
    components: dict[str, ComponentDelta]


def run_examples(
    examples: Sequence[tuple[str, ScenarioRecord]],
    reform: Reform,
    wff_policy_dir: Path,
    as_policy_dir: Path,
) -> list[WorkedExample]:
    reform.check_supported()
    results = []
    for example_id, record in examples:
        wff_base = load_policy_parameters(
            wff_policy_dir,
            record.wff_lookup_date,
            requested_policy_version=record.requested_wff_policy_version,
        )
        as_base = load_policy_parameters(
            as_policy_dir,
            record.as_lookup_date,
            requested_policy_version=record.requested_as_policy_version,
        )
        base = _run(record, wff_policy_dir, as_policy_dir, wff_base, as_base)
        new = _run(
            record,
            wff_policy_dir,
            as_policy_dir,
            apply_reform(wff_base, reform),
            apply_reform(as_base, reform),
        )
        results.append(
            WorkedExample(
                example_id,
                {
                    c: _delta(_component(base, c), _component(new, c), RecordStatus.VALID)
                    for c in COMPONENTS
                },
            )
        )
    return results
