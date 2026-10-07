"""Task B0.1.2 (ADR-0023): identities for a reform scenario and its runs.

A reform scenario is the analytic question: one or two labelled options,
each a `Reform`, compared with the status quo at the law baseline date. Its
id hashes that definition only, so the same question asked twice is the same
scenario; its title and description are labels kept beside it.

A reform run is one execution of every option on a population. Each option's
own run id already hashes the population, the reform, the code identity and
the policy files (`microsim.runner`), so the reform run id hashes the
scenario id with those option run ids. Rerunning on the same deployment
reproduces the same id; a changed population, code or policy file gives a
new one. Timestamps are never hashed (as in `record.py`).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from datetime import date
from typing import Any

from poltika.scenarios.microsim.reform import Reform
from poltika.scenarios.record import canonical_json


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reform_definition(
    law_baseline_date: date, options: Sequence[tuple[str, Reform]]
) -> dict[str, Any]:
    return {
        "law_baseline_date": law_baseline_date.isoformat(),
        "options": [
            {"label": label, "reform": reform.model_dump(mode="json")} for label, reform in options
        ],
    }


def reform_scenario_id(definition: dict[str, Any]) -> str:
    return _sha256(canonical_json({"type": "reform_scenario", "definition": definition}))


def reform_run_id(scenario_id: str, option_run_ids: Sequence[str]) -> str:
    return _sha256(
        canonical_json(
            {
                "type": "reform_run",
                "scenario_id": scenario_id,
                "option_run_ids": list(option_run_ids),
            }
        )
    )


def results_sha256(results: dict[str, Any]) -> str:
    return _sha256(canonical_json(results))
