# Pete's queue

The open Tier C items (ADR-0020): the decisions and actions only Pete can
take. Each says what it blocks and the smallest action that clears it.
Work routes around every item here. When one is done, Pete (or the session
that records his answer) moves it to "Done" with the date and the PR or
commit that records it.

## Open

| # | Item | Blocks | Smallest action |
| --- | --- | --- | --- |
| Q1 | Activate ADR-0020's target `main` ruleset and squash-only auto-merge. On 3 October GitHub reports main protected but no repository rulesets; classic protection could not be read with this integration. | Mechanical enforcement of the agreed merge rules; baseline task 2. | Run the commands below as repository owner, checking existing protection first. No settings changed in this migration. |
| Q2 | Māori data governance, privacy and security (old 1.4/P5). Engage people with standing in Māori data governance. | Ethnicity/iwi-disaggregated outputs and microdata uses where governance is required (E/M); the interim ban holds. It does not block unrelated deterministic household modelling or Pilot 1. | Name who to engage, or direct GPT/Codex to begin dated primary-source research. All applicable privacy/data constraints still apply. |
| Q3 | IDI access (P12): lodging an application. | IDI-calibrated population claims and applicable microdata work (E/M), not household Pilot 1. | Lodge after a dated, sourced access-route document and project scope are prepared. |
| Q4 | Reserved programme decisions, explicitly remapped below. | Only their named capabilities. P18 governs claiming each milestone; no migration document declares a gate met. | Decide concrete options with evidence when each capability starts. |
| Q5 | Household lane D1–D3: income-tax and core-benefit supported slices; disposable-income definition; sourced income-adequacy, replacement and participation measures where supported. Draft evidence: [#148](https://github.com/hemmingsenpeter-byte/poltika/pull/148), [#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151); Claude source review pending. | D1-dependent tax/benefit implementation and later disposable-income/measures in B; period/payment-precision gaps and the §3.4 household restriction remain unresolved. Preserving current WFF/AS and reviewing the existing mapping increment can proceed. | After source review, decide the smallest evidenced slices and confirm whether §3.4's household restriction is a deliberate supported-slice exclusion or should be corrected; see the dated evidence below. No decision is requested or recorded by this queue update. |
| Q7 | P11: historical horizon for policy/data states and replays. | Phase I historical scope and historical statutory years. No inherited November deadline or household-kernel dependency. | Choose the earliest year from a sourced coverage proposal when Phase I starts, or explicitly delegate the reversible choice. |
| Q8 | Tag v0.2 (`BUILD_PLAN_v0_2.md` 10.3). GitHub has no `v0.2.0` tag as verified 3 October. | The release record; it does not block household work or Pilot 1. | Select the reviewed commit and create/push the annotated tag. Tagging remains Tier C. |
| Q9 | Accept or revise ADR-0018's proposed Workbench design. PR #133 implements its backend; the independent review is in `reviews/2026-10-02-pr133.md`. | Acceptance of that design, not preservation of its existing backend or the strategic choice of Workbench first. | Record “accept ADR-0018” or the specific changes required. Implementation and review alone do not establish acceptance. |
| Q10 | Household/fiscal methodology: v0.2 D8/D9 annualising AS and mapping a single income path across tax/benefits/WFF/AS. | Combined disposable-income/EMTR and direct fiscal results where the definition is required (B/F). | Decide the sourced period/income mapping with the relevant household specifications; retain native units until then. |
| Q11 | External analyst participation and eventual release tags for untagged work. | Pilot evidence in D/G; v0.1.5 release completion and later tags. No external pilot is recorded yet. | Name and authorise an external pilot participant/session when the workflow is ready; tag only against the actual release evidence. No outreach or public deployment is authorised by this migration. |

### Reserved programme decisions (Q4)

| Historical decision | Current capability | Reserved action |
| --- | --- | --- |
| P6 | C, conformance-suite publication | Decide publication/IP; internal conformance can proceed. |
| P7 | I, prediction/model-error ledger | Choose timestamping and the first genuinely predictive targets. Early C validation does not wait on this. |
| P13 | H/L, demand-driven expansion | Decide domain priorities from concrete analytical/pilot demand. |
| P14 | N, policy search | Set the causal-credibility gate before search. |
| P18 | Every phase's evidence gate | Set tolerances and record milestone acceptance against evidence. |
| P20 | K, national scenario library | Choose its first national scenario set; core counterfactuals in C can proceed. |

P8's strategic first-product choice is now the Analyst Workbench (Pete's
3 October directive, ADR-0021). This does not accept ADR-0018; see Q9.
P10's technical batch-engine decision remains delegated under ADR-0020 and
moves to E when profiling demonstrates need. P19's technical state-schema
scope remains delegated but moves to K. The new sequence does not change
other reserved authority.

### Q5 prepared evidence — 3 October 2026, second cycle

The source drafts are review preparation, not approved specifications:

| Draft | Fixed evidence | Remaining source/slice gate |
| --- | --- | --- |
| Income tax [#148](https://github.com/hemmingsenpeter-byte/poltika/pull/148), head `0db2bfaf787280a6cda252f6fa7e9287ba107ef7` | [Scope options](https://github.com/hemmingsenpeter-byte/poltika/blob/0db2bfaf787280a6cda252f6fa7e9287ba107ef7/docs/research/task_0_1_income_tax_scope.md); [source catalogue](https://github.com/hemmingsenpeter-byte/poltika/blob/0db2bfaf787280a6cda252f6fa7e9287ba107ef7/policy_specs/income_tax/sources.yaml) | Claude source review and Pete D1 pending; enacted-period coverage and rounding/benchmark evidence not approved. |
| Core benefits [#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151), head `50f13f44533cdab2939dd80e37538c8313ecb774` | [Scope and interactions](https://github.com/hemmingsenpeter-byte/poltika/blob/50f13f44533cdab2939dd80e37538c8313ecb774/docs/research/task_0_2_core_benefit_scope.md); [JS sources](https://github.com/hemmingsenpeter-byte/poltika/blob/50f13f44533cdab2939dd80e37538c8313ecb774/policy_specs/jobseeker_support/sources.yaml), [SPS sources](https://github.com/hemmingsenpeter-byte/poltika/blob/50f13f44533cdab2939dd80e37538c8313ecb774/policy_specs/sole_parent_support/sources.yaml), [SLP sources](https://github.com/hemmingsenpeter-byte/poltika/blob/50f13f44533cdab2939dd80e37538c8313ecb774/policy_specs/supported_living_payment/sources.yaml) | Claude source review and Pete D1 pending; benefit payment precision, gross/net reconciliation, assessment basis and period coverage remain explicitly gated. |

**Specific plan discrepancy to decide later:** [the detailed household plan](BUILD_PLAN_v0_3.md)
§3.4 says one main benefit per household unless a specification says otherwise.
The independently retrieved [Social Security Act s 18, version as at 4 September 2026](https://www.legislation.govt.nz/act/public/2018/32/en/2026-09-04/)
restricts simultaneous main-benefit receipt per person in their own right;
Schedule 4 Parts 1 and 3 recognise partner own-right benefit categories.
Pete should confirm whether the household wording is an intentional coverage
exclusion for the first supported slice or should be corrected to the sourced
per-person boundary. A chosen household exclusion would be a coverage limit,
not a claim that mixed-benefit couples are legally prohibited.

The plan is unchanged and no interpretation is chosen here. Same-model source
checks, including #151's resolved JS category correction, do not supply Claude
review, Pete D1, monetary parameters or complete historical coverage.
D1-dependent implementation remains gated. Existing WFF/AS preservation and
the pinned review intake of the current household writer need no new Pete
slice decision; their source/interpretation and acceptance gates still hold.

### Q1 commands

```sh
gh api -X PATCH repos/hemmingsenpeter-byte/poltika \
  -F allow_auto_merge=true -F delete_branch_on_merge=true \
  -F allow_merge_commit=false -F allow_rebase_merge=false -F allow_squash_merge=true

gh api -X POST repos/hemmingsenpeter-byte/poltika/rulesets --input - <<'JSON'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "bypass_actors": [],
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false,
      "allowed_merge_methods": ["squash"]}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "do_not_enforce_on_create": false,
      "required_status_checks": [
        {"context": "test"},
        {"context": "pilot-image"},
        {"context": "check-protected-paths"},
        {"context": "check-immutable-snapshots"}
      ]}}
  ]
}
JSON
```

The required checks are the CI jobs that run on pull requests today. Each
new CI job is added to the list when its PR merges (`docs/decision_log.md`
records which), so after the first run the session can only propose the
updated list here; it cannot apply it.

## Done

| Item | Date | Record |
| --- | --- | --- |
| Q6: obsolete blanket Pete-acceptance wording in reviewer/preflight skills | 3 October 2026 | This migration replaces the blanket instructions with ADR-0020's Tier A/B Claude Code and Tier C Pete acceptance; author preflight remains distinct from independent review. |
| P8: strategic first-product surface | 3 October 2026 | Pete's supplied migration directive, recorded in ADR-0021; Analyst Workbench chosen. ADR-0018 acceptance remains Q9. |
