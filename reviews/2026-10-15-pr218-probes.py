from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from itertools import product
import pytest
from pydantic import ValidationError
from poltika.semantics import household as hh
from poltika.scenarios.household_mappings import (LINK_FACT, RELATIONSHIP_FACT, HouseholdResult, MappingRefusal, household_from_combined, run_household, to_as, to_wff)
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.engines.simulator.wff import PartnerStatus, WffScenario
from poltika.engines.simulator.outcome import FactStatus
from tests.unit.scenarios.test_household_run import _household, _with, _run, TAX_YEAR, WEEK, _two_listed_one_counted
from tests.unit.scenarios.test_combined import _wff, _as

MAIN = [hh.BenefitKind.JOBSEEKER_SUPPORT, hh.BenefitKind.SOLE_PARENT_SUPPORT, hh.BenefitKind.SUPPORTED_LIVING_PAYMENT]
S,E=TAX_YEAR.start,TAX_YEAR.end
EDGES=[(S-timedelta(days=7),S,False),(S-timedelta(days=1),S+timedelta(days=1),True),(S,S+timedelta(days=1),True),(E-timedelta(days=1),E,True),(E-timedelta(days=1),E+timedelta(days=1),True),(E,E+timedelta(days=7),False)]
def partnered():
 pair=CombinedHouseholdScenario(wff=replace(_wff(),partner_status=PartnerStatus.PARTNERED), accommodation_supplement=_as(partner_status=None), as_claimant_is_wff_claimant_or_partner=FactStatus.VERIFIED)
 return household_from_combined(pair,household_id='probe',tax_year=TAX_YEAR,assessment_week=WEEK)

@pytest.mark.parametrize('benefit,person,edge',product(MAIN,['claimant','partner'],EDGES))
def test_whole_year_no_benefit_edges(benefit,person,edge):
 start,end,overlap=edge
 base=partnered()
 h=_with(base,benefit_spells=(hh.BenefitSpell(person_id=person,benefit=benefit,start=start,end=end),))
 result=to_wff(h,TAX_YEAR)
 assert isinstance(result,MappingRefusal)==overlap
 if overlap: assert result.code=='HOUSEHOLD_MAPPING_INVALID_FACTS'
 else: assert isinstance(result,WffScenario)

@pytest.mark.parametrize('a,b',product(list(hh.BenefitKind),repeat=2))
def test_overlapping_statuses_never_choose_a_category(a,b):
 h=_household()
 spells=[hh.BenefitSpell(person_id='claimant',benefit=a,start=WEEK.start,end=WEEK.end),hh.BenefitSpell(person_id='claimant',benefit=b,start=WEEK.start+timedelta(days=1),end=WEEK.end)]
 with pytest.raises(ValidationError): _with(h,benefit_spells=spells)
 # Even an unvalidated construction cannot cause to_as to pick the covering status.
 bypass=h.model_copy(update={'benefit_spells':tuple(spells)})
 result=to_as(bypass,WEEK)
 assert isinstance(result,MappingRefusal) and result.code=='HOUSEHOLD_MAPPING_INVALID_FACTS'

@pytest.mark.parametrize('a,b',product(list(hh.BenefitKind),repeat=2))
def test_adjacent_statuses_do_not_justify_whole_week_category(a,b):
 h=_household()
 midpoint=WEEK.start+timedelta(days=3)
 spells=(hh.BenefitSpell(person_id='claimant',benefit=a,start=WEEK.start,end=midpoint),hh.BenefitSpell(person_id='claimant',benefit=b,start=midpoint,end=WEEK.end))
 result=to_as(_with(h,benefit_spells=spells),WEEK)
 assert not isinstance(result,MappingRefusal) and result.claimant_category is None

@pytest.mark.parametrize('link',[None,hh.Assertion.UNKNOWN,hh.Assertion.EXCLUDED,hh.Assertion.VERIFIED])
def test_relationship_refusal_precedes_missing_evidence(link):
 h=_household();facts={**h.asserted_facts,RELATIONSHIP_FACT:hh.Assertion.EXCLUDED}
 if link is not None:facts[LINK_FACT]=link
 family=h.family.model_copy(update={'wff_children_complete':hh.Assertion.UNKNOWN})
 result=_run(_with(h,families=(family,),asserted_facts=facts,income_spells=()))
 assert isinstance(result,MappingRefusal) and result.outcome=='unsupported' and result.code=='HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR'

@pytest.mark.parametrize('origin',[True,False])
def test_count_origin_survives_serialization(origin):
 _,h=_two_listed_one_counted()
 h=_with(h,families=(h.family.model_copy(update={'as_child_statuses_from_count':origin}),))
 restored=hh.Household.model_validate_json(h.model_dump_json())
 assert restored.family.as_child_statuses_from_count==origin
 result=_run(restored)
 assert isinstance(result,HouseholdResult)
 assert bool(result.combined.contradictions)==origin
 assert bool(result.definitional_differences)==(not origin)

@pytest.mark.parametrize('offset',[-1,1])
def test_as_income_straddles_refused_without_scaling(offset):
 h=_household()
 spells=[]
 for s in h.income_spells:
  if s.basis is hh.IncomeBasis.AS_CHARGEABLE_WEEKLY:
   s=s.model_copy(update={'start':s.start-timedelta(days=1)} if offset<0 else {'end':s.end+timedelta(days=1)})
  spells.append(s)
 result=to_as(_with(h,income_spells=spells),WEEK)
 assert isinstance(result,MappingRefusal) and result.code=='HOUSEHOLD_SPELL_PERIOD_MISMATCH'
