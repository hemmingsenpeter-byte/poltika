# Phase B live reconciliation and amount verification — 15 October 2026

GPT/Codex; independent economic verification lane. Claude Code remains sole
integration coordinator and implementation owner. No implementation file,
protected statutory expectation or shared programme file was edited by this
lane. The shared checkout's existing untracked work was left intact.

## Live reconciliation

Initial live main was verified as
`63359fecfe3b6659476528da021ea0ade0023537`, matching the planning reference.
The actual fork of #218–#220 is
`7342e528ad67b58984de5711ba2d195bdef97c67`. GitHub's reported baseRefOid
must not be mistaken for current main. Heads below identify observations,
not transferable review approval.

| PR | Observed state / disposition | Next owner/action |
| --- | --- | --- |
| [#217](https://github.com/hemmingsenpeter-byte/poltika/pull/217) | Initially draft `85f89f2`; Claude rebased to `c8a400cc2969a4ddc8639a37ef69cc40b9e90633`, marked ready and posted exact-head documentation review. It remains the existing #193 clearance handoff | Claude integrates when its checks/gates pass; not duplicated or merged by Codex |
| [#218](https://github.com/hemmingsenpeter-byte/poltika/pull/218) | Published `f1c106a5ea48b40ca0cb87c553ef76df652d74f3`, conflicting/DIRTY against main. The local `354aa8a` integration candidate is unpublished | Independent [mapping record](2026-10-15-pr218-independent.md), [posted exact-head review](https://github.com/hemmingsenpeter-byte/poltika/pull/218#pullrequestreview-5529256922) and [final-head request](https://github.com/hemmingsenpeter-byte/poltika/pull/218#issuecomment-6186118607). Claude publishes final integration SHA; renew review on it |
| [#219](https://github.com/hemmingsenpeter-byte/poltika/pull/219) | Initial draft `a6d1667`; source-only follow-up pushed as `8e1e861fbda0f6382278d0e1ca6fa379b6adf173` | [Exact-head author handoff](https://github.com/hemmingsenpeter-byte/poltika/pull/219#issuecomment-6186242211). Independent Claude source/numeric review; no promoted value |
| [#220](https://github.com/hemmingsenpeter-byte/poltika/pull/220) | Initial draft `0994a0c`; source correction `c5ef0085827e39cbf41372d70e28e8a2d25ad929`; JS-only ACC follow-up `712402da10682d481f14381533049008a8092fc9`, all on the same draft | [Final author handoff](https://github.com/hemmingsenpeter-byte/poltika/pull/220#issuecomment-6186369959). Independent Claude source review of the latest head, then JS method/precision before values |

No Claude review/inline findings existed on #219 or #220 when checked.
Their updates are independent author-side source reconstruction, not fixes
of invented reviewer findings or cross-model clearance. CI after the new
pushes is separate from the earlier green CI and is not claimed complete.

## Source-state and priority gap

1. **Income tax:** independently derived bracket boundaries and one-dollar
   neighbours match all 17 candidate numeric cases; none was changed.
   Official latest-positive observations remain select committee, with IRD's
   page dated 12 October. Annual authority and whole-period currency remain
   `needs_review` under D11/Q16. Q17 whole-dollar input Assumption and Q18's
   IR3G `SOURCE_CONFLICT`/benchmark exclusion stand. No period-matched
   official numeric benchmark was obtained. #219's packet contains full
   source dates/locators, derivation and output-precision alternatives.
2. **Benefits:** #220 corrects the Regulations' stale latest-version claim
   to 1 October 2026 and locates IRD DET 24/03 (issued 10 July 2024), while
   preserving draft scope/gates. Gross/net-M, payable/assessment periods,
   r 205 weekly agreements, per-person overlap and asserted capacity remain
   explicit. No policy.yaml, gross expected fixture or rounding rule was
   invented. The priority gap is now the exact JS determination/table
   application and complete rounding, followed by a matching gross benchmark;
   it is narrower than “no determination found”.
3. **Interactions and methods:** [interaction inventory](../docs/research/phaseb_interaction_matrix_20261015.md)
   distinguishes demonstrated rules from blocked executable edges. The
   [income-method decision pack](../docs/research/phaseb_income_methods_20261015.md)
   uses #172's retained comparison and fresh official source checks to give
   D2/D3 options, explicit units/periods/coverage and independent examples.
   These are candidates pending Claude source review and Pete selection.

## B0.1 economic/amount verification

Reviewed exact main `63359fec...`: Task B0.1's amount invariants from its
plan and ADR-0018 were reconstructed before inspecting display assembly.
Checked `api/v1_scenarios.py` household/reform metrics and component table,
stored-result/provenance use, `web/src/format/index.ts`, metric card/chart
and table rendering, and their applicable tests. Values remain backend
strings; missing outcomes remain nonnumeric; household monetary precision
is preserved in text; WFF annual and AS weekly amounts are separate.
Chart floating-point scaling is presentation-only, with exact text/table
alternatives. No new actionable finding in this bounded amount path.

This is supporting current-main verification, not a blanket re-review of
every B0.1 PR, live deployment, a real-phone check or external-user acceptance.
The existing #189 waived-review record and hosting/real-phone gates are not
silently cleared. No Render resource was read or changed in this lane.

Exact commands from the isolated main worktree, with `PYTHONPATH=src` and
the existing repository Python environment:

```sh
python -m pytest -q tests/unit/api/test_v1_scenarios.py \
  tests/unit/api/test_v1_workspace_regressions.py \
  tests/unit/api/test_workbench_api.py \
  tests/unit/scenarios/test_golden_households.py \
  tests/unit/scenarios/test_interaction_spec_cases.py
```

**86 passed, 6 skipped**, exit 0; the six skips are PostgreSQL-marked
scenario tests in the environment without configured PostgreSQL. Two
Starlette/httpx deprecation warnings. No fresh database-backed or restart
verification is claimed.

Frontend check from `web/`, using existing locked dependencies via a local
ignored `node_modules` symlink (no manifest/lock changes):

```sh
npm test -- --maxWorkers=1 --testTimeout=30000 \
  src/format/index.test.ts src/components/charts/MetricChart.test.tsx \
  src/components/blocks/BlockRenderer.test.tsx src/api/schemas.test.ts
```

**52 passed**, four files, exit 0. Initial default-concurrency invocation
had 51 pass / one chart test timeout at 5 seconds on the loaded shared host;
the same selection passed with one worker/30-second timeout. This was not
treated as a product defect or a changed expected value. No frontend code
was modified.

## Author/source verification and reserved decisions

#219: 76 focused tests and source checks pass; nine sourced parameter
candidates, zero approved, nine due. Separate exact-commit `8e1e861`
author preflight repeated evidence/currency and whitespace checks.
#220: 3 focused source-scope tests, catalogue validation (16/17/20 source
IDs), 27 local links and whitespace pass at `c5ef008`, including a separate
exact-commit author checkout. The first author-check script used a wrong
import path; the corrected `source_catalog.SourceCatalog` check passed.
The JS-only ACC follow-up increases its catalogue to 17 unique entries;
its three source-scope tests, links and whitespace pass, with a separate
exact-commit author check recorded in the #220 handoff.
Detailed source-only amendment evidence stays in each existing PR packet.
No passing full suite is inferred from these bounded checks.

The income-method script uses Decimal and no simulator imports. A supporting
same-model source check caught a percentage-unit error in its companion
document's decomposition; it was corrected to
`100 × (Δtax + Δlevy − Δtax_credits − Δother_transfers) / h`, with disjoint
components. It also corrected wording about the next taxable dollar and
the retained DI-4 retrieval date. All seven method examples reproduce.
The matrix's supporting check also found an overbroad grouped propagation
row: an unrelated tax refusal could have gated a valid before-tax benefit
input. I09's dependent MFTC mapping and I10's independent before-tax inputs
are now separate, and exclusion derivations add no producer gate to an
already-resolved valid consumer input. These checks are not Claude's
independent acceptance.
The same check distinguished I05's recipient/date-only contradiction from
I06's monthly protected-credit derivation: monthly facts now gate only the
latter derivation, without clearing or obstructing the retained date guard.

Pete's source decisions, after independent source review:

- D2: select one complete dated definition and approve any explicit
  modelling adaptation/common-period contract; incomplete components never
  become zero. The current HILS, historical MSD and later-MSD-with-body-gap
  alternatives and consequences are in the method pack.
- D3: approve the income perturbation, denominator, step and resource basis;
  EMTR first does not approve annual/weekly conversions or PTR/RR endpoints.
- Benefits: retain the full abated gross scope or explicitly narrow/change
  it; resolve sourced method/precision ambiguity before protected values.
- Tax: Q16–Q18 are already decided and are not reopened. Any assumed final
  output convention requires its own explicit decision; source authority,
  benchmark and independent protected-value gates remain.

Next work is limited to the final #218 integration review, Claude review of
the existing source drafts and this bounded method pack, and the JS method
gap. No later-phase implementation or remaining benefit engines were opened.
Gate B remains unmet: there is no reviewed connected example yet where an
approved new-policy calculated amount feeds a dependent policy, and D2/D3,
source, coverage, benchmark and provenance gates remain named.
