"""Reviewer artifact for #224 at 2248390; not a production or statutory test.

Run from that exact checkout with its development environment:
    PYTHONPATH=src:. python reviews/2026-10-16-pr224-probes.py

The assertions demonstrate the reviewed defects. A fixed implementation may
fail them because the defects no longer reproduce. Temporary policy copies
and runtime substitutions never change the repository's policy files.
"""

from dataclasses import replace
from decimal import Decimal, localcontext
from hashlib import sha256
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from poltika.common.errors import ProvenanceError, UnsupportedSchemaVersionError
from poltika.engines.assurance.explanation import explain, verify
from poltika.engines.assurance.provenance import build_provenance_report
from poltika.engines.simulator import income_tax
from poltika.engines.simulator.income_tax import (
    COMPONENT_ID,
    POLICY_DIR,
    basic_tax_band_sum,
    calculate_income_tax,
    run_income_tax_module,
)
from poltika.engines.simulator.outcome import ComponentResult
from poltika.policy.loader import ParameterResolution, load_policy_parameters
from tests.unit.engines.simulator.test_income_tax import ORDINARY, synthetic


missing = replace(ORDINARY, annual_taxable_income=None)
wrong = run_income_tax_module(missing, policy_dir=Path("policy_specs/working_for_families"))
assert wrong.trace is not None
assert wrong.trace.policy_id == "working_for_families"
assert wrong.trace.component_id == COMPONENT_ID
print("R1 wrong policy accepted:", wrong.code, wrong.trace.policy_id, wrong.trace.component_id)

with TemporaryDirectory(prefix="pr224-review-", dir="/private/tmp") as temp:
    directory = Path(temp) / "income_tax"
    shutil.copytree(POLICY_DIR, directory)
    policy = directory / "policy.yaml"
    original = policy.read_text()
    policy.write_text(original.replace('schema_version: "0.1"', 'schema_version: "999"'))
    result = run_income_tax_module(ORDINARY, policy_dir=directory)
    assert result.trace is not None and result.trace.schema_version == "999"
    print("R1 unsupported schema accepted:", result.code, result.trace.schema_version)
    try:
        load_policy_parameters(directory, result.trace.modelled_date)
    except UnsupportedSchemaVersionError:
        print("R1 normal loader rejects the same schema")
    else:
        raise AssertionError("normal loader unexpectedly accepted schema 999")

    policy.write_text(original)
    original_bytes = policy.read_bytes()
    original_parser = income_tax.load_policy_spec

    def replace_before_parse(path: Path):
        path.write_text(original.replace("policy_id: income_tax", "policy_id: renamed_tax"))
        return original_parser(path)

    income_tax.load_policy_spec = replace_before_parse
    try:
        changed = run_income_tax_module(missing, policy_dir=directory)
    finally:
        income_tax.load_policy_spec = original_parser
    assert changed.trace is not None and changed.trace.policy_id == "renamed_tax"
    bound_hash = dict(changed.trace.artifact_sha256)["policy.yaml"]
    assert bound_hash == sha256(original_bytes).hexdigest()
    assert bound_hash != sha256(policy.read_bytes()).hexdigest()
    print("R2 policy hash and parsed identity come from different byte snapshots")

draft = run_income_tax_module(ORDINARY)
assert draft.trace is not None
assert set(dict(draft.trace.artifact_sha256)) == {"policy.yaml"}
try:
    build_provenance_report(POLICY_DIR, {COMPONENT_ID: draft})
except ProvenanceError as error:
    assert "no hash" in str(error) and "sources.yaml" in str(error)
    print("R2 current draft provenance fails:", error)
else:
    raise AssertionError("reviewed missing-artifact defect no longer reproduces")

parameters = synthetic(
    band_1_upper=ParameterResolution(parameter_id="band_1_upper", outcome="needs_review", reason="candidate"),
    band_5_rate=ParameterResolution(parameter_id="band_5_rate", outcome="unsupported", reason="no interval"),
)
mixed = calculate_income_tax(ORDINARY, parameters)
assert (mixed.outcome, mixed.code) == ("needs_review", "IT_PARAMETER_NOT_APPROVED")
print("R3 mixed parameter outcomes:", mixed.outcome, mixed.code, "(expected unsupported/IT_PARAMETER_NO_INTERVAL)")

# Synthetic arithmetic only: no real policy parameter or expected value is changed.
flat = synthetic(**{
    f"band_{number}_rate": ParameterResolution(
        parameter_id=f"band_{number}_rate", outcome="resolved", value=Decimal("0.175")
    )
    for number in range(1, 6)
})
with localcontext() as context:
    context.prec = 28
    exact = basic_tax_band_sum(Decimal(15603), flat)
with localcontext() as context:
    context.prec = 4
    rounded = basic_tax_band_sum(Decimal(15603), flat)
assert exact == Decimal("2730.525") and rounded != exact
print("P3 synthetic helper depends on Decimal context:", exact, rounded)

steps = []
total = basic_tax_band_sum(Decimal(45), synthetic(), steps)
trace = calculate_income_tax(ORDINARY, synthetic()).trace
assert trace is not None
recorded = replace(trace, steps=tuple(steps), calculation_rules=("IT-05",))
conditional = ComponentResult(outcome="calculated", value=total, trace=recorded)
problems = verify(explain(COMPONENT_ID, conditional), conditional)
assert any("not a recorded value" in problem for problem in problems)
print("P3 synthetic explanation verification:", problems)
