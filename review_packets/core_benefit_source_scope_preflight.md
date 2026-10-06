# Core-benefit source scope — author preflight and review handoff

- Date: 3 October 2026, Pacific/Auckland.
- Author: GPT/Codex source writer, coordinated by GPT/Codex project manager.
- Base: prepared programme migration `422b055cb65570d9dd070eae3e054574aa2858d7`.
- Original author sources/scope: `cf83e16e956ff5e5bed9c49f6a38a26c091add74`.
- Final source-backed category correction: `b238820`, separately delta-checked
  against reviewed `59d5e4a`; inventories unchanged, no remaining finding.
- Branch: `codex/core-benefit-source-scope`; writer made no PR/push/merge.
  Project manager published draft [#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151)
  after the separate final source check; no merge or source approval.
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
The later category-label correction is recorded separately above; all
catalogues remain byte-identical to this source SHA. Final delta whitespace
passes. Later commits only record checks and the draft PR tracking number.

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

## 5 October 2026 source refresh — author preflight

Refresh base: `main` at `1e185f7652bebce693a9c709cb716b4a9bcfdf5a`.
The earlier check is historical and does not cover this changed head. The
author knew the proposal rationale; a new final-head Claude pass is required.

Expected contract: source-only catalogues, current/future-law separation,
precise amendments, per-person own-right restriction, unsupported
mixed-benefit couples and no approved monetary result. Recorded findings:

- P3 `SPEC_ERROR`: 2026 No 54 change inventory added to all three catalogues.
  Part 1's JS/equivalent-emergency-benefit parental-income requirement,
  review/regulation and Schedule 1–3 changes and Part 2's AS homeowner
  categories/SLP-linked exception are named. Shared definitions and new
  Schedule 3 cl 16A's benefit-reduction/cancellation power retain a fresh
  cross-policy review gate; SPS/SLP implications are not assumed absent.
- P3 `SPEC_ERROR`: JS cl 1(c) follows the gender-neutral 2013 transfer locator;
  repealed 1964 Act Schedule 32 remains an unscoped dependency.
- P3 `SPEC_ERROR`: annual-charging transition now follows Regulations
  Schedule 1 cl 25(4)'s per-grant 52 weeks under cl 25(1)(b); MAP corroborates.
- `SPEC_ERROR`: local 3.4 now follows SSA s 18 and Schedule 4 Parts 1/3.
  Pete's 5 October closeout authorised the correction; preserved Lane 3
  wording supplied its starting point. Couples stay unsupported pending spec.

Official SSA/Regulations HTML (4 September 2026 versions) and 2026 No 54
as enacted were retrieved on 5 October with `curl --fail --location
--user-agent 'Mozilla/5.0'`. Pinpoints are retained in the catalogues and
scope note. No external policy engine was accessed and no amount was adopted.

Checks completed, exit 0: `git diff --check`; existing `SourceCatalog`
validation (9/10/10 entries, 29 unique IDs, source-only packs, precise
future-law locators/limitations); local 3.4 own-right/unsupported checks; and
`PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python -m pytest -q tests/acceptance/test_programme_authority.py`
(10 passed). Monetary implementation, payment precision, protected values,
independent final-head review and CI remain separate gates.

## 6 October 2026 review-record closeout — author preflight

The independent [Claude review of source head `7418c99`](https://github.com/hemmingsenpeter-byte/poltika/pull/151#issuecomment-5990307455)
and its separate fresh reviewer pass are now recorded in the existing review
file, including the SPS/SLP field-by-field limitation. The historical
same-model review above is not presented as that independent review.
Local 3.4 links the verbatim Pete approval record. Each catalogue now carries
a structured coverage limit for both partners receiving own-right main benefits:
`unsupported` / `not_modelled`, before `needs_review`. Its statutory locator
distinguishes the per-person law from the approved coverage exclusion. Source
entries and monetary values remain unchanged; no runtime gate is added.

The author knows the source rationale. Checks actually run on the prepared
delta, exit 0: `git diff --check`; existing `SourceCatalog.model_validate`
(9/10/10 sources, 29 globally unique IDs, no executable `policy.yaml`);
targeted changed-document relative-file/anchor checks. This is author
preflight. Later main integration, the final commit and current CI must be
checked separately; the final reviewer pass is recorded in the PR without
editing the already committed evidence again. Monetary specification and
protected-value gates remain separate.

### Current follow-up and verification — 6 October 2026

Merged current `origin/main` (`f9c69d8e3384f0753be482c5ee4a6564cfa5d8ea`)
without rewriting history. Copied the identical approval record from #170
head `ac6366f47b52a184b168a748e85a25ab8db7cd89` so the approval citation
resolves before that PR lands; the merge train must integrate main again.
The three source catalogues now expose the approved coupled-benefit coverage
limit, with a regression guard over outcome, category, status precedence,
source identity and the approval-record link. This does not implement any
benefit calculation or claim that mixed-benefit couples cannot qualify legally.

The new changes are outside the recorded historical/source-delta reviews.
Claude's final-head primary-source review and current CI remain outstanding.
No review-queue row was changed before #170 merged.

Current checks exited 0: `git diff --check`; `SourceCatalog.model_validate`
(9/10/10 sources, 29 globally unique IDs); targeted relative-file/anchor
checks (11 links); `ruff check tests/unit/policy/test_core_benefit_source_scope.py`;
and `PYTHONPATH=src /private/tmp/poltika-testing-e52f5d3-venv/bin/python -m pytest -q tests/unit/policy/test_core_benefit_source_scope.py tests/acceptance/test_programme_authority.py`
(13 passed). Monetary spec/benchmark/protected-value gates remain open.
