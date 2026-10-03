"""A real population run for the reporting tests: the toy synthetic
population (made-up shares, no claim about New Zealand), run under the
runner's own threshold reform, plus two withdrawal paths and example
households."""

from __future__ import annotations

from decimal import Decimal as D
from typing import Any

import pytest

from poltika.api.analyst import examples
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.microsim.runner import PopulationRun, run_population
from poltika.scenarios.microsim.synthetic import SyntheticSpec, generate
from poltika.scenarios.microsim.withdrawal import WithdrawalPath, withdrawal_path
from poltika.scenarios.microsim.worked_examples import WorkedExample, run_examples
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_runner import THRESHOLD
from tests.unit.scenarios.microsim.test_synthetic import TOY
from tests.unit.scenarios.test_population import GOLDEN
from tests.unit.scenarios.test_scenario_record import record_from_yaml

CODE = CodeIdentity("test", None, None, None)
FTC = ("family_tax_credit",)


class Case:
    def __init__(
        self,
        population: PopulationDataset,
        run: PopulationRun,
        paths: list[tuple[str, WithdrawalPath]],
        examples_: list[WorkedExample],
        parameter_sets: list[PolicyParameterSet],
    ) -> None:
        self.population = population
        self.run = run
        self.paths = paths
        self.examples = examples_
        self.parameter_sets = parameter_sets


@pytest.fixture(scope="session")
def case() -> Case:
    spec: dict[str, Any] = {**TOY, "households": 60}
    population, _ = generate(SyntheticSpec.model_validate(spec))
    run = run_population(population, THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    wff_record = record_from_yaml(GOLDEN[1])
    as_record = record_from_yaml(GOLDEN[0])
    paths = [
        (
            "wff path",
            withdrawal_path(
                wff_record,
                "working_for_families",
                [D(v) for v in (40000, 60000, 80000, 100000)],
                WFF_POLICY_DIR,
                AS_POLICY_DIR,
            ),
        ),
        (
            "as path",
            withdrawal_path(
                as_record,
                "accommodation_supplement",
                [D(v) for v in range(0, 1001, 250)],
                WFF_POLICY_DIR,
                AS_POLICY_DIR,
            ),
        ),
    ]
    records = [
        (e["id"], record_from_request(HouseholdCalculationRequest.model_validate(e["request"])))
        for e in examples()
    ]
    worked = run_examples(records, THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR)
    sets = [
        load_policy_parameters(
            WFF_POLICY_DIR,
            wff_record.wff_lookup_date,
            requested_policy_version=wff_record.requested_wff_policy_version,
        )
    ]
    return Case(population, run, paths, worked, sets)
