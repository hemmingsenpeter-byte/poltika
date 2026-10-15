import sys
import pytest
import poltika.scenarios.household_mappings as m
mode=sys.argv[1]
root='tests/unit/scenarios/test_household_run.py::'
if mode=='relationship':
 m._relationship_refusal=lambda household:None
 selected=[root+'test_a_relationship_change_in_the_year_is_unsupported']
elif mode=='child_origin':
 original=m._household_contradictions
 m._household_contradictions=lambda *args:tuple(c for c in original(*args) if not c.startswith('dependent children:'))
 selected=[root+'test_a_count_derived_child_difference_keeps_the_pair_gate']
elif mode=='canonical_order':
 m._spell_order=lambda spell:0
 selected=[root+'test_the_named_evidence_does_not_depend_on_spell_order',root+'test_the_q19_5_refusal_does_not_depend_on_spell_order']
elif mode=='protected_month':
 original=m._household_contradictions
 m._household_contradictions=lambda *args:tuple(c for c in original(*args) if not c.startswith('main benefit:'))
 selected=[root+'test_a_benefit_spell_in_the_year_flags_a_verified_no_protected_month']
else:raise ValueError(mode)
raise SystemExit(pytest.main(['-q',*selected]))
