"""Independent Codex review probes for PR #218 at affda3298547ae9d2c8c2f0e9ddd58971f838197.

Reviewer artifact, reconstructed without changes from the three review heredocs
already executed on 16 October 2026. Saving this file did not rerun the probes.
It does not modify production code or protected fixtures.

Reproduce from the repository root:
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. <python> reviews/2026-10-16-pr218-probes.py

Original execution evidence:
1. First block: cwd /private/tmp/poltika-pr218-codex-final-20261016.bLNmvo,
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:.
   /Users/peterhemmingsen/Poltika/.venv/bin/python - <<'PY'
   [first block below]
   PY
   Exit 0; printed "30 independent benefit-kind/year-edge probes passed;
   replaced components retain original traces".
2. Second block: cwd /private/tmp/poltika-pr218-codex-head-20261016,
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:.
   /private/tmp/poltika-int218-20261015/.venv/bin/python - <<'PY'
   [second block below]
   PY
   Exit 0; printed the child-origin serialization result and
   "4 independent partial-week/exclusive-edge mixed-benefit single-family
   checks passed".
3. Third block: same cwd/environment/python as block 2, invoked with the same
   heredoc form. Exit 0; printed "4 independent one-day-straddle/exact-year-edge
   full household probes passed; outside weeks withhold every calculated
   amount and preserve traces".
"""

# First executed block: all six benefit kinds at five WFF tax-year edges.
from dataclasses import replace
from datetime import date
from tests.unit.scenarios.test_household_run import _household, _run, _with, _components, _originals
from tests.unit.scenarios.test_combined import _wff
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import PartnerStatus
from poltika.scenarios.household_mappings import HouseholdResult
from poltika.semantics import household as hh

base = _household(wff=replace(_wff(), partner_status=PartnerStatus.PARTNERED, in_work_eligibility=FactStatus.UNKNOWN, mc6b_disqualifying_payment=FactStatus.UNKNOWN), partner_status=None)
periods = [
    (date(2026,3,25),date(2026,4,1),False),
    (date(2026,3,31),date(2026,4,2),True),
    (date(2026,4,1),date(2026,4,8),True),
    (date(2027,3,31),date(2027,4,2),True),
    (date(2027,4,1),date(2027,4,8),False),
]
probes=0
for kind in hh.BenefitKind:
    for start,end,overlap in periods:
        spell = hh.BenefitSpell(person_id='partner',benefit=kind,start=start,end=end)
        value = _run(_with(base,benefit_spells=(*base.benefit_spells,spell)))
        assert isinstance(value, HouseholdResult), value
        expected = overlap and kind in {hh.BenefitKind.JOBSEEKER_SUPPORT,hh.BenefitKind.SOLE_PARENT_SUPPORT,hh.BenefitKind.SUPPORTED_LIVING_PAYMENT}
        assert bool(value.combined.contradictions) == expected,(kind,start,end,value.combined.contradictions)
        assert all(c.trace == o.trace for c,o in zip(_components(value),_originals(value))), 'trace lost'
        probes+=1
print(f'{probes} independent benefit-kind/year-edge probes passed; replaced components retain original traces')

# Second executed block: child-origin serialization and partial-week mixed benefit.
from datetime import date
from tests.unit.scenarios.test_household_run import _two_listed_one_counted, _with, _run, _household
from poltika.scenarios.household_mappings import HouseholdResult
from poltika.semantics import household as hh

_, adapted = _two_listed_one_counted()
for from_count in (True, False):
    h = _with(adapted, families=(adapted.family.model_copy(update={'as_child_statuses_from_count':from_count}),))
    encoded = h.model_dump_json(exclude_defaults=True)
    restored = hh.Household.model_validate_json(encoded)
    assert restored.family.as_child_statuses_from_count is from_count
    assert restored.content_sha256() == h.content_sha256()
    result, replay = _run(h),_run(restored)
    assert result == replay
    assert isinstance(result,HouseholdResult)
    assert bool(result.combined.contradictions) is from_count
    assert bool(result.definitional_differences) is not from_count
print('Child-origin marker survives JSON with defaults omitted; canonical identity, refusal gates, definitional diagnostics and replay preserved for both origins')

base = _household()
periods = [
    (date(2026,5,31),date(2026,6,1),False),
    (date(2026,6,1),date(2026,6,2),True),
    (date(2026,6,7),date(2026,6,8),True),
    (date(2026,6,8),date(2026,6,9),False),
]
for start,end,overlap in periods:
    spell = hh.BenefitSpell(person_id='claimant', benefit=hh.BenefitKind.MIXED_BENEFIT_COUPLE,start=start,end=end)
    result = _run(_with(base,benefit_spells=(spell,)))
    assert isinstance(result,HouseholdResult),result
    assert bool([c for c in result.combined.contradictions if c.startswith('partner status:')]) is overlap,(start,end,result.combined.contradictions)
print('4 independent partial-week/exclusive-edge mixed-benefit single-family checks passed')

# Third executed block: full household runs at both assessment-year boundaries.
from datetime import date
from poltika.scenarios.household_mappings import household_from_combined,run_household,HouseholdResult
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.engines.simulator.accommodation_supplement import AssessmentWeek
from poltika.engines.simulator.outcome import FactStatus
from tests.unit.scenarios.test_household_run import TAX_YEAR,_components,_originals
from tests.unit.scenarios.test_combined import _wff,_as,LOOKUP,WFF_VERSION
from tests.conftest import WFF_POLICY_DIR,AS_POLICY_DIR,AS_POLICY_VERSION
pair = CombinedHouseholdScenario(wff=_wff(),accommodation_supplement=_as(),as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED)
periods = [
    (date(2026,3,31),date(2026,4,7),True),
    (date(2026,4,1),date(2026,4,8),False),
    (date(2027,3,25),date(2027,4,1),False),
    (date(2027,3,26),date(2027,4,2),True),
]
for start,end,outside in periods:
    week=AssessmentWeek(start=start,end=end)
    h=household_from_combined(pair,household_id='edge',tax_year=TAX_YEAR,assessment_week=week)
    value=run_household(h,tax_year=TAX_YEAR,assessment_week=week,wff_policy_dir=WFF_POLICY_DIR,as_policy_dir=AS_POLICY_DIR,wff_lookup_date=LOOKUP,as_lookup_date=start,requested_wff_policy_version=WFF_VERSION,requested_as_policy_version=AS_POLICY_VERSION)
    assert isinstance(value,HouseholdResult),value
    assert bool([c for c in value.combined.contradictions if 'not inside the WFF year' in c]) is outside,(start,end,value)
    assert all(c.trace == o.trace for c,o in zip(_components(value),_originals(value)))
    if outside: assert all(c.outcome != 'calculated' for c in _components(value))
print('4 independent one-day-straddle/exact-year-edge full household probes passed; outside weeks withhold every calculated amount and preserve traces')
