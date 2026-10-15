"""Reproduce inherited income-period refusal diagnostic ordering on PR #218."""
from dataclasses import replace
from datetime import date
from decimal import Decimal
from poltika.semantics import household as hh
from poltika.scenarios.household_mappings import household_from_combined, to_wff
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.record import canonical_json
from poltika.engines.simulator.wff import PartnerStatus
from poltika.engines.simulator.outcome import FactStatus
from tests.unit.scenarios.test_combined import _wff, _as, WEEK
from tests.unit.scenarios.test_household_run import TAX_YEAR, _with, _run
base = household_from_combined(
    CombinedHouseholdScenario(
        wff=replace(_wff(), partner_status=PartnerStatus.PARTNERED),
        accommodation_supplement=_as(partner_status=None),
        as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED,
    ), household_id='probe', tax_year=TAX_YEAR, assessment_week=WEEK,
)
spells = tuple(
    hh.IncomeSpell(person_id=person, income_type=hh.IncomeType.UNSPLIT_TOTAL,
                   start=start, end=TAX_YEAR.end, amount=Decimal(100),
                   basis=hh.IncomeBasis.WFF_FAMILY_SCHEME)
    for person, start in [('claimant', date(2026, 3, 31)), ('partner', date(2026, 3, 30))]
)
a, b = _with(base, income_spells=spells), _with(base, income_spells=spells[::-1])
ra, rb = _run(a), _run(b)
print('First household hash:', a.content_sha256())
print('Second household hash:', b.content_sha256())
print('Equal to_wff refusal:', to_wff(a, TAX_YEAR) == to_wff(b, TAX_YEAR))
print('Equal run_household refusal:', ra == rb)
print('First refusal:', canonical_json(ra))
print('Second refusal:', canonical_json(rb))
print('Refusal exposes result_id:', hasattr(ra, 'result_id'))
print('Refusal exposes trace:', hasattr(ra, 'trace'))
