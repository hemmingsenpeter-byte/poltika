"""Reviewer artifact, not production code or an automatically collected test.

Provenance: copied from the independent GPT/Codex reader's executed stdin
probe on 16 October 2026, at PR #228 head
64a081d7a05a38caba7caf496d78379fd1c18008 in
/private/tmp/poltika-pr228-codex-review-20261016. The probe ran with
PYTHONPATH=src and /private/tmp/poltika-incspell-20261016/.venv/bin/python;
all assertions passed. This header was added when preserving the script;
the preserved artifact was not rerun. Root pytest/CI results are separate.
"""

from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from itertools import permutations
from pydantic import ValidationError
from poltika.semantics import household as hh
from poltika.semantics.population import PersonRole
from poltika.scenarios.household_mappings import to_wff, to_as, MappingRefusal, RELATIONSHIP_FACT, LINK_FACT
from tests.unit.semantics.test_household import _household, YEAR, WEEK
from tests.unit.scenarios.test_household_run import _run

def sp(person,typ,basis,start,end,amount='1'):
 return hh.IncomeSpell(person_id=person,income_type=typ,basis=basis,start=start,end=end,amount=Decimal(amount))
def changed(base,**kwargs):
 return hh.Household.model_validate({**base.model_dump(),**kwargs})
base=_household(hh.Assertion.VERIFIED)
year_spells=(
 sp('p',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.WFF_FAMILY_SCHEME,date(2026,3,30),YEAR.end),
 sp('a',hh.IncomeType.EMPLOYMENT_EARNINGS,hh.IncomeBasis.WFF_FAMILY_SCHEME,date(2026,3,30),date(2027,5,1)),
 sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.NET_OF_TAX,date(2026,3,30),YEAR.end),
 sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.WFF_NET_FAMILY_SCHEME_ME3_ATTESTED,date(2026,3,30),YEAR.end),
)
refusals=[]
for order in permutations(year_spells):
 h=changed(base,income_spells=order)
 assert h.content_sha256()==changed(base,income_spells=year_spells).content_sha256()
 r=to_wff(h,YEAR)
 assert isinstance(r,MappingRefusal)
 assert (r.outcome,r.code,r.missing_facts)==('needs_review','HOUSEHOLD_SPELL_PERIOD_MISMATCH',())
 refusals.append(r)
assert all(r==refusals[0] for r in refusals)
print('WFF ties across person/type/basis: all 24 permutations give identical MappingRefusal and household hash')
as_spells=(
 sp('p',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.AS_CHARGEABLE_WEEKLY,date(2026,5,1),date(2026,8,1)),
 sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.GROSS,date(2026,5,1),date(2026,8,1)),
 sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.AS_CHARGEABLE_WEEKLY,date(2026,5,31),WEEK.end),
 sp('a',hh.IncomeType.EMPLOYMENT_EARNINGS,hh.IncomeBasis.AS_CHARGEABLE_WEEKLY,date(2026,5,30),WEEK.end),
)
rs=[to_as(changed(base,income_spells=order),WEEK) for order in permutations(as_spells)]
assert all(r==rs[0] for r in rs)
assert isinstance(rs[0],MappingRefusal) and '[2026-05-30, 2026-06-08)' in rs[0].reason
print('AS ties/filtering: all 24 permutations give identical refusal; ignored partner and gross spells do not win')
for assertion in (hh.Assertion.UNKNOWN,hh.Assertion.EXCLUDED):
 h=changed(base,income_spells=year_spells,asserted_facts={RELATIONSHIP_FACT: assertion})
 r=to_wff(h,YEAR)
 assert isinstance(r,MappingRefusal)
 assert r.code==('HOUSEHOLD_RELATIONSHIP_CHANGED_IN_YEAR' if assertion is hh.Assertion.EXCLUDED else 'HOUSEHOLD_SPELL_PERIOD_MISMATCH')
family=base.family.model_copy(update={'wff_children_complete':hh.Assertion.UNKNOWN})
r=to_wff(changed(base,income_spells=year_spells,families=(family,)),YEAR)
assert isinstance(r,MappingRefusal) and r.code=='HOUSEHOLD_CHILD_LIST_INCOMPLETE' and r.missing_facts==('wff_children_complete',)
for assertion in (hh.Assertion.UNKNOWN,hh.Assertion.EXCLUDED):
 h=changed(base,income_spells=year_spells,asserted_facts={LINK_FACT:assertion})
 r=_run(h)
 assert isinstance(r,MappingRefusal)
 assert r.code==('HOUSEHOLD_PAIR_LINK_EXCLUDED' if assertion is hh.Assertion.EXCLUDED else 'HOUSEHOLD_PAIR_LINK_UNVERIFIED')
print('Existing relationship, child-list and household-link precedence/missing_facts preserved')
x=sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.WFF_FAMILY_SCHEME,date(2026,3,31),YEAR.end,'0001.00')
y=sp('a',hh.IncomeType.UNSPLIT_TOTAL,hh.IncomeBasis.WFF_FAMILY_SCHEME,datetime(2026,3,31),datetime(2027,4,1),'1.00')
ha=changed(base,income_spells=(x,)); hb=changed(base,income_spells=(y,))
assert ha.content_sha256()==hb.content_sha256()
assert to_wff(ha,YEAR)==to_wff(hb,YEAR)
print('Hash-equivalent Decimal lexical forms and midnight datetime/date inputs give identical refusal')
# Invalid inputs have no Household hash; check the selected semantic diagnostic.
for kind in ('type','basis','benefit'):
 if kind=='benefit':
  spells=tuple(hh.BenefitSpell(person_id=p,benefit=hh.BenefitKind.JOBSEEKER_SUPPORT,start=s,end=date(2026,7,1)) for p in ('p','a') for s in (date(2026,6,1),date(2026,6,15)))
  field='benefit_spells'; expected='benefit spells for a overlap'
 else:
  vals=(hh.IncomeType.EMPLOYMENT_EARNINGS,hh.IncomeType.SELF_EMPLOYMENT_INCOME) if kind=='type' else (hh.IncomeBasis.GROSS,hh.IncomeBasis.NET_OF_TAX)
  spells=tuple(sp('a',v if kind=='type' else hh.IncomeType.EMPLOYMENT_EARNINGS,hh.IncomeBasis.GROSS if kind=='type' else v,s,date(2026,7,1)) for v in vals for s in (date(2026,6,1),date(2026,6,15)))
  field='income_spells'; expected='income spells for a/employment_earnings/gross overlap'
 msgs=set()
 for order in permutations(spells):
  try: changed(base,**{field:order})
  except ValidationError as exc: msgs.add(exc.errors(include_input=False)[0]['msg'])
  else: raise AssertionError('Overlap accepted')
 assert msgs=={'Value error, '+expected},msgs
print('Overlap group selection across income type, basis and benefit person: 72 permutations, one expected semantic error each')
