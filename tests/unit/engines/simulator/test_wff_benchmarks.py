"""Task 14: benchmark tests.

Per doctrine/test-doctrine.md's "Benchmark tests for expected statutory
values" class: this file is a thin loader/runner over
`policy_specs/working_for_families/benchmarks.yaml`, exactly like Task 13's
`test_wff_spec_cases.py` is for `spec_cases.yaml`. Expected values are not
authored here -- see `benchmarks.yaml`'s own header for why every numeric
value there is copied verbatim from a cited IRD page, not derived.

Runs against a synthetic parameter fixture carrying the real approved WFF
rates but with every parameter (including `in_work_base`) marked approved
-- the same design `test_wff.py` (Task 12) already established: the live
`in_work_base` rate-status gate is a separate, already-protected concern
(`spec_cases.yaml`, Task 13); using it here would mask whether a genuine
arithmetic or scope-boundary bug exists behind that unrelated gate.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    FactStatus,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
    calculate_wff,
)
from poltika.policy.loader import load_policy_parameters

WFF_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "working_for_families"
BENCHMARKS_PATH = WFF_POLICY_DIR / "benchmarks.yaml"
MODELLED_DATE = date(2026, 6, 1)

_COMPONENT_IDS = frozenset(
    {"family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"}
)


def _load_benchmarks() -> list[dict[str, Any]]:
    raw = yaml.safe_load(BENCHMARKS_PATH.read_text())
    benchmarks: list[dict[str, Any]] = raw["benchmarks"]
    return benchmarks


def _param(param_id: str, value_type: str, unit: str, value: str) -> dict[str, Any]:
    return {
        "id": param_id,
        "value_type": value_type,
        "unit": unit,
        "values": [
            {
                "effective_from": "2026-04-01",
                "effective_to": "2027-04-01",
                "value": value,
                "source_id": "test-source",
                "locator": "s 1",
                "review_status": "approved",
            }
        ],
    }


@pytest.fixture(scope="module")
def parameters(tmp_path_factory: pytest.TempPathFactory):
    """Same statutory rates as the real approved WFF policy.yaml, but with
    every parameter -- including in_work_base -- approved. See this file's
    module docstring and benchmarks.yaml's header for why."""
    policy_dir = tmp_path_factory.mktemp("wff_benchmark_fixture")
    policy = {
        "schema_version": "0.1",
        "policy_id": "bench_wff",
        "policy_version": "0.1.0",
        "status": "approved",
        "reference_period": {"from": "2026-04-01", "to": "2027-04-01"},
        "source_catalog": "sources.yaml",
        "assessment": {},
        "inputs": [],
        "parameters": [
            _param("family_tax_credit_eldest_child", "money", "NZD_per_tax_year", "7921"),
            _param("family_tax_credit_additional_child", "money", "NZD_per_tax_year", "6454"),
            _param("family_tax_credit_abatement_threshold", "money", "NZD_per_tax_year", "44900"),
            _param(
                "family_tax_credit_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.275",
            ),
            _param("in_work_base", "money", "NZD_per_tax_year", "7670"),
            _param("in_work_additional_child", "money", "NZD_per_tax_year", "780"),
            _param(
                "minimum_family_prescribed_amount",
                "money",
                "NZD_per_tax_year_after_tax",
                "36604",
            ),
            _param("best_start_annual_amount", "money", "NZD_per_child_per_tax_year", "4041"),
            _param("best_start_abatement_threshold", "money", "NZD_per_tax_year", "79000"),
            _param(
                "best_start_abatement_rate",
                "fraction",
                "NZD_per_complete_NZD_above_threshold",
                "0.21",
            ),
        ],
        "components": [],
        "outputs": {},
    }
    (policy_dir / "policy.yaml").write_text(yaml.safe_dump(policy))
    (policy_dir / "sources.yaml").write_text(
        yaml.safe_dump({"sources": [{"id": "test-source", "kind": "legislation"}]})
    )
    return load_policy_parameters(policy_dir, MODELLED_DATE)


def _income_from_yaml(raw: dict[str, Any] | None) -> VerifiedIncome | None:
    if raw is None:
        return None
    partner_amount = raw.get("partner_amount")
    return VerifiedIncome(
        claimant_amount=Decimal(raw["claimant_amount"]),
        partner_amount=Decimal(partner_amount) if partner_amount is not None else None,
    )


def _child_from_yaml(raw: dict[str, Any]) -> ChildFacts:
    return ChildFacts(
        qualifies_whole_year=FactStatus(raw["qualifies_whole_year"]),
        best_start_cohort=BestStartCohort(raw["best_start_cohort"]),
        best_start_no_disqualifying_payment=FactStatus(raw["best_start_no_disqualifying_payment"]),
    )


def _scenario_from_yaml(raw: dict[str, Any]) -> WffScenario:
    net_income = raw.get("net_family_scheme_income")
    return WffScenario(
        household_eligibility=FactStatus(raw["household_eligibility"]),
        extra_instalment_status=FactStatus(raw["extra_instalment_status"]),
        children=[_child_from_yaml(c) for c in raw.get("children", [])],
        partner_status=PartnerStatus(raw["partner_status"]),
        family_scheme_income=_income_from_yaml(raw.get("family_scheme_income")),
        net_family_scheme_income=Decimal(net_income) if net_income is not None else None,
        net_family_scheme_income_me3_attested=raw.get("net_family_scheme_income_me3_attested", False),
        in_work_eligibility=FactStatus(raw["in_work_eligibility"]),
        ftc_iwtc_protected_or_direct_abatement=FactStatus(raw["ftc_iwtc_protected_or_direct_abatement"]),
        mc6a_veterans_payment=FactStatus(raw["mc6a_veterans_payment"]),
        mc6b_disqualifying_payment=FactStatus(raw["mc6b_disqualifying_payment"]),
        minimum_family_full_time_earner_weeks=FactStatus(raw["minimum_family_full_time_earner_weeks"]),
        best_start_no_shared_care=FactStatus(raw["best_start_no_shared_care"]),
        best_start_protected_credit=FactStatus(raw["best_start_protected_credit"]),
    )


_BENCHMARKS = _load_benchmarks()
_BENCHMARK_IDS = [b["id"] for b in _BENCHMARKS]


def test_benchmarks_file_is_non_empty() -> None:
    """Guards against an accidental empty/reverted benchmarks.yaml silently
    passing an empty parametrised suite."""
    assert len(_BENCHMARKS) >= 6


def test_benchmark_ids_are_unique() -> None:
    assert len(_BENCHMARK_IDS) == len(set(_BENCHMARK_IDS)), "duplicate benchmarks.yaml id"


def test_every_benchmark_cites_a_known_ird_source() -> None:
    """Every benchmark must trace to a real sources.yaml entry -- a typo'd
    or invented ird_source would silently break the paper trail this file's
    whole purpose depends on."""
    sources_raw = yaml.safe_load((WFF_POLICY_DIR / "sources.yaml").read_text())
    known_ids = {entry["id"] for entry in sources_raw["sources"]}
    for benchmark in _BENCHMARKS:
        assert benchmark["ird_source"] in known_ids, (
            f"{benchmark['id']}: ird_source '{benchmark['ird_source']}' is not in sources.yaml"
        )


@pytest.mark.parametrize("benchmark", _BENCHMARKS, ids=_BENCHMARK_IDS)
def test_wff_benchmark(benchmark: dict[str, Any], parameters) -> None:
    # benchmarked_components must be non-empty and a subset of the four
    # known components -- and expected must still cover all four, per the
    # completeness discipline PR #15's review established for
    # spec_cases.yaml (a case whose expected block silently omitted a
    # component previously passed without that component ever being
    # checked).
    benchmarked = set(benchmark["benchmarked_components"])
    assert benchmarked, f"{benchmark['id']}: benchmarked_components must not be empty"
    assert benchmarked <= _COMPONENT_IDS, (
        f"{benchmark['id']}: benchmarked_components has unknown id(s) {benchmarked - _COMPONENT_IDS}"
    )
    assert set(benchmark["expected"].keys()) == _COMPONENT_IDS, (
        f"{benchmark['id']}: expected block must cover exactly {sorted(_COMPONENT_IDS)}, "
        f"got {sorted(benchmark['expected'].keys())}"
    )
    assert benchmark["outcome_kind"] in ("numeric_match", "scope_boundary")
    if benchmark["outcome_kind"] == "numeric_match":
        for component_id in benchmarked:
            assert benchmark["expected"][component_id]["outcome"] == "calculated", (
                f"{benchmark['id']}.{component_id}: outcome_kind is numeric_match but "
                f"the benchmarked component's expected outcome isn't 'calculated'"
            )

    scenario = _scenario_from_yaml(benchmark["scenario"])
    result = calculate_wff(scenario, parameters)

    component_results = {
        "family_tax_credit": result.family_tax_credit,
        "in_work_tax_credit": result.in_work_tax_credit,
        "minimum_family_tax_credit": result.minimum_family_tax_credit,
        "best_start": result.best_start,
    }

    for component_id, expected in benchmark["expected"].items():
        actual = component_results[component_id]
        assert actual.outcome == expected["outcome"], (
            f"{benchmark['id']}.{component_id}: expected outcome "
            f"'{expected['outcome']}', got '{actual.outcome}' (reason: {actual.reason})"
        )
        if expected["outcome"] == "calculated":
            assert actual.value == Decimal(expected["value"]), (
                f"{benchmark['id']}.{component_id}: expected value "
                f"{expected['value']}, got {actual.value}"
            )
        else:
            assert actual.value is None, (
                f"{benchmark['id']}.{component_id}: expected no value, got {actual.value}"
            )
