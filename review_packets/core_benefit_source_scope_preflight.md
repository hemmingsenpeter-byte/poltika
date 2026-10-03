# Core-benefit source scope — author preflight and review handoff

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex source writer, coordinated by GPT/Codex project manager.
- Base: prepared programme migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Fixed sources/scope: `cf83e16e956ff5e5bed9c49f6a38a26c091add74`.
- Branch: `codex/core-benefit-source-scope`; no PR, push or merge by this writer.
- Label: **author preflight**, followed by a separate same-model source check
  recorded in `reviews/2026-10-03-core-benefit-source-scope.md`. Claude source
  acceptance and Pete D1 remain pending under ADR-0020.

## Mechanical review inputs

- [Jobseeker source catalogue](../policy_specs/jobseeker_support/sources.yaml).
- [Sole Parent source catalogue](../policy_specs/sole_parent_support/sources.yaml).
- [Supported Living source catalogue](../policy_specs/supported_living_payment/sources.yaml).
- [Scope and interaction proposal](../docs/research/task_0_2_core_benefit_scope.md).
- [Placement](../REPOSITORY_STRUCTURE.md) and Programme Task 8 only in
  [the live tracker](../PROGRAMME_STATUS.md).
- Contracts: active programme Task 8; detailed v0.3 local 0.2–0.4 and Phase 3;
  primary-source/IP/review/test doctrine; existing `SourceCatalog`; new-policy
  workflow and author-preflight skill. No external engine was inspected.

No approved new-benefit spec exists. The catalogues are sources only; they
must not be treated as approved entitlement rules or executable policy packs.

## Expected contract before checking

Record eligibility gate classes, rate categories, partner/child/income-test
locators and explicit coverage limits for all three benefits. Separate an
as-of source version from commencement; distinguish future enacted changes
from operative law. Preserve missing/ambiguous evidence and proposed D1
choices rather than invent values, approved slices or graph edges. Existing
WFF/AS meanings, periods and decisions remain dependencies.

## Findings and unresolved gates

| Finding | Proposed classification | Scope and resolution |
|---|---|---|
| JS Schedule 4 Part 1 cl 1(a) mistakenly labelled at/away from parental home | `SPEC_ERROR`, P2, found by separate source checker | Corrected to under 20 living with parent plus benefit commencement condition; cl 1(b) separately identifies other under-25 singles without dependent children. Dated Act independently retrieved; no amount changed |
| Detailed local 3.4 household prohibition versus Act s 18 own-right per-person restriction and Schedule 4 partner categories | `SPEC_ERROR`, subject to reviewer confirmation | Recorded with sources; detailed plan remains unchanged. Clarification is required before implementation |
| Benefit-specific rounding, gross/net M reconciliation, tax treatment and payment/deduction ordering are not established by this scoped source pass | `MISSING_SOURCE` for a dependent monetary claim | Numerical implementation/benchmarks remain gated; this draft supplies no guessed values |
| D1 assessment period, established-grant result meaning, population breadth and SPS/SLP assessment basis | Pete supported-slice decisions; not silently classified as settled policy | Proposed ordinary single slices and excluded routes are explicit; no DEC or approval created |
| SPS overview's abbreviated relationship wording and SLP carer/partner distinctions | Scope traps checked against primary provisions | Broader s 30 routes and Schedule 4 Part 3 distinctions are retained, not flattened into one gate/rate |

The first two findings block their dependent implementation claims, not the
existence of a source draft documenting those gaps. This packet does not
recommend acceptance or clear any unresolved finding for an implementation PR.

## Checks actually performed

The source artifacts were inspected at their fixed commits in separate
`git archive` snapshots, outside the author checkout. The full base-to-source
diff was read, including sections reread after truncated tool output.
The author tightened two statements in follow-up `cf83e16`: the JS slice
describes what future implementation would exercise, and the SPS regulation
entry confines its finding to its own income/AS locators.

At `cf83e16`, these commands exited 0:

```sh
git diff --check 422b055cb65570d9dd070eae3e054574aa2858d7 cf83e16e956ff5e5bed9c49f6a38a26c091add74
```

The existing locked testing environment was used with `PYTHONPATH=src` in
the fixed archive, so the schema imported from that archive. The following
reproduces the catalogue checks with the same dependencies installed:

```sh
PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python - <<'PY'
from pathlib import Path
from datetime import date
from urllib.parse import urlparse
import yaml
from poltika.semantics.schemas.source_catalog import SourceCatalog
for policy, count in [('jobseeker_support', 9), ('sole_parent_support', 10), ('supported_living_payment', 10)]:
    p = Path('policy_specs') / policy / 'sources.yaml'
    raw = yaml.safe_load(p.read_text())
    cat = SourceCatalog.model_validate(raw)
    assert len(cat.sources) == count and len({s.id for s in cat.sources}) == count
    assert raw['status'] == 'task_0_2_source_scope_draft_pending_review'
    assert sorted(x.name for x in p.parent.iterdir()) == ['sources.yaml']
    for s in cat.sources:
        e = s.model_dump()
        date.fromisoformat(e['checked_on'])
        assert e['checked_on'] == '2026-10-03'
        assert all(e[k] for k in ('locator', 'finding', 'limitation'))
        assert urlparse(s.url).hostname in ('www.legislation.govt.nz', 'www.workandincome.govt.nz', 'map.workandincome.govt.nz', 'www.ird.govt.nz')
        if s.kind.value == 'future_amending_legislation':
            assert e['version_as_at'] == '2026-09-03' and 'Not operative' in e['limitation']
    print(policy, len(cat.sources), 'validated')
PY
```

Results: all three catalogues validate, with 9/10/10 unique entries; official
hosts, dated retrievals, locators, limitations and future-law separation are
present. Changed-document relative links resolve. Each new policy directory
contains `sources.yaml` only; no `policy.yaml` or runnable discovery is added.
The final packet-only commit must be checked against this source SHA before
publication; its head is obtained with `git rev-parse HEAD`.

Full pytest, Ruff and strict mypy were not rerun for this source/document-only
change. The project manager holds the separately measured clean-main baseline;
that evidence is not a CI pass for this branch. No runtime calculation,
installed-wheel claim, database test, protected expected value or numerical
benchmark is introduced or verified by this packet.

## Fresh checker and later independent handoff

Review the final branch head and primary sources without accepting the
author's slice recommendation as a decision. Independently check ss 16–42;
Schedules 2–4; rr 10–11, 205/Schedule 6, 17–18; rate-order commencement;
the as-enacted 2026/54 s 2 boundary; and Income Tax Act CF 1/YA 1,
MB 1–2, MC 6, MD 8/14, ME 2, MG 4.

Pay particular attention to per-person versus household receipt, SPS s 30
routes, SLP personal-earnings and carer distinctions, zero-payment status,
annual versus agreed-weekly assessment, protected-month WFF and limits of
live guidance. The rounding/payment source gap remains unresolved.

Separate source review, Pete D1, specification, dated values/cases, statutory
implementation, interactions and release gates remain outstanding. An author
preflight does not satisfy the GPT/Claude reviewer rotation or the required
fresh-context `poltika-reviewer` pass. Task 8 remains In progress.
