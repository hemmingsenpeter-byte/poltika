"""Task 24.1 official MSD Accommodation Supplement benchmarks."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import (
    calculate_accommodation_supplement,
)

from .test_as_spec_cases import _load_cases, _parameters, _scenario

AS_POLICY_DIR = Path(__file__).resolve().parents[4] / "policy_specs" / "accommodation_supplement"
BENCHMARKS_PATH = AS_POLICY_DIR / "benchmarks.yaml"

_BENCHMARKS = _load_cases(BENCHMARKS_PATH, "benchmarks")
_BENCHMARK_IDS = [case["id"] for case in _BENCHMARKS]


def test_as_benchmarks_are_complete_traceable_and_unique() -> None:
    assert len(_BENCHMARKS) >= 3
    assert len(_BENCHMARK_IDS) == len(set(_BENCHMARK_IDS))
    source_catalog = yaml.safe_load((AS_POLICY_DIR / "sources.yaml").read_text())
    known_source_ids = {source["id"] for source in source_catalog["sources"]}
    for benchmark in _BENCHMARKS:
        assert benchmark["msd_source"] in known_source_ids
        assert benchmark["outcome_kind"] in (
            "conditional_arithmetic_match",
            "scope_boundary",
        )
        assert benchmark["benchmarked_components"] == ["accommodation_supplement"]
        assert benchmark.get("assumed_facts")
        assert benchmark.get("source_note")
        assert set(benchmark["expected"]) == {"accommodation_supplement"}
        expected = benchmark["expected"]["accommodation_supplement"]
        if benchmark["outcome_kind"] == "conditional_arithmetic_match":
            assert expected["outcome"] == "calculated"


@pytest.mark.parametrize("benchmark", _BENCHMARKS, ids=_BENCHMARK_IDS)
def test_as_benchmark(benchmark: dict[str, Any]) -> None:
    result = calculate_accommodation_supplement(
        _scenario(benchmark["scenario"]), _parameters(benchmark)
    )
    expected = benchmark["expected"]["accommodation_supplement"]
    assert result.outcome == expected["outcome"], (
        f"{benchmark['id']}: expected {expected['outcome']}, "
        f"got {result.outcome} ({result.reason})"
    )
    if expected["outcome"] == "calculated":
        assert result.value == Decimal(expected["value"])
    else:
        assert result.value is None
