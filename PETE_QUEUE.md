# Pete's queue

The open Tier C items (ADR-0020): the decisions and actions only Pete can
take. Each says what it blocks and the smallest action that clears it.
Work routes around every item here. When one is done, Pete (or the session
that records his answer) moves it to "Done" with the date and the PR or
commit that records it.

## Open

| # | Item | Blocks | Smallest action |
| --- | --- | --- | --- |
| Q2 | Māori data governance, privacy and security (old 1.4/P5). Engage people with standing in Māori data governance. | Ethnicity/iwi-disaggregated outputs and microdata uses where governance is required (E/M); the interim ban holds. It does not block unrelated deterministic household modelling or Pilot 1. | Name who to engage, or direct GPT/Codex to begin dated primary-source research. All applicable privacy/data constraints still apply. |
| Q3 | IDI access (P12): lodging an application. | IDI-calibrated population claims and applicable microdata work (E/M), not household Pilot 1. | Lodge after a dated, sourced access-route document and project scope are prepared. |
| Q4 | Reserved programme decisions, explicitly remapped below. | Only their named capabilities. P18 governs claiming each milestone; no migration document declares a gate met. | Decide concrete options with evidence when each capability starts. |
| Q5 | D1 supported slices and D2/D3 order decided by Pete on 5 October 2026; [decision log](docs/decision_log.md), D11–D12. Income tax: 2026–27 basic annual salaries/wages first, `needs_review` until Bill 344-1 is enacted; benefits: single existing-grant slices as at a stated date before 2 November 2026, gross weekly entitlement. Official disposable-income source scoping commissioned; EMTR first. | Numerical implementation still needs independently reviewed source/spec/precision/benchmark evidence; D2 definition and income-path methodology remain unapproved. | Review the official-definition source pack when ready. No unsupported component becomes zero and no unenacted annual-rate authority becomes calculated. |
| Q7 | P11: historical horizon for policy/data states and replays. | Phase I historical scope and historical statutory years. No inherited November deadline or household-kernel dependency. | Choose the earliest year from a sourced coverage proposal when Phase I starts, or explicitly delegate the reversible choice. |
| Q9 | Accept or revise ADR-0018's proposed Workbench design. PR #133 implements its backend; the independent review is in `reviews/2026-10-02-pr133.md`. | Acceptance of that design, not preservation of its existing backend or the strategic choice of Workbench first. | Record “accept ADR-0018” or the specific changes required. Implementation and review alone do not establish acceptance. |
| Q10 | Household/fiscal methodology: v0.2 D8/D9 annualising AS and mapping a single income path across tax/benefits/WFF/AS. | Combined disposable-income/EMTR and direct fiscal results where the definition is required (B/F). | Decide the sourced period/income mapping with the relevant household specifications; retain native units until then. Update 11 October: Claude review of #195 ([record](reviews/2026-10-11-pr195-review.md)) found it consistent with ADR-0017/D6 and v0.2 D8/D9 with no statutory claim. Decide whether #195's wording is the interim contract for Tasks 5, 6 and 9 (Tasks 10–11 stay gated), and whether a dated income spell may ever become a policy-period amount (for example daily apportionment into an AS week) or the caller must supply the amount per policy period. The household mapping now refuses rather than apportions. |
| Q12 | Delete merged remote branches (Tier C: deleting history). Of 103 remote branches, 87 have a tip that is the head of a squash-merged PR (GitHub keeps `refs/pull/N/head`); 16 are kept (8 closed-unmerged PR branches, 8 with no PR at their tip). List: `reviews/2026-10-07-closeout.md`. | Nothing functional; branch-list clutter only. | Approve deleting the 87 listed branches, or keep them. |
| Q13 | Self-hosted runner account (D21): pull-request code runs as Pete's macOS login user, so a CI job can reach his keychain, SSH keys and files. | Nothing functional; a security-exposure choice. | Accept the exposure for this collaborator-only private repository, or move the runner to a dedicated non-admin macOS user. |
| Q14 | Confirm two reversible D20 defaults: the 50 MiB response cap (real Stats NZ sizes unverified; `POPES_SUB_004` may exceed it) and the Bandit MEDIUM gate. | Nothing until a live Stats NZ retrieval; an oversize source then fails loudly and needs a reviewed override. | Confirm both, or name a different cap or gate. |
| Q11 | External analyst participation and eventual release tags for untagged work. | Pilot evidence in D/G; v0.1.5 release completion and later tags. No external pilot is recorded yet. | Name and authorise an external pilot participant/session when the workflow is ready; tag only against the actual release evidence. No outreach or public deployment is authorised by this migration. |
| Q15 | Task B0.1 deployment (D24, ADR-0023): confirm which Render workspace holds the `poltika.onrender.com` service, choose the Render PostgreSQL plan/size, and set `POLTIKA_ACCESS_PASSWORD` as a secret in the Render dashboard; optionally make the new `web` CI check required in the repository ruleset. | B0.1.7 deployment only. B0.1.0–B0.1.6 proceed without it. | Tell the session the workspace and database plan; set the password yourself (it is never committed or sent through a session). Update 11 October: B0.1.7 readiness check ([record](reviews/2026-10-11-b017-deploy-readiness.md)): fail-closed auth, `/healthz` and PostgreSQL persistence are in place; set `POLTIKA_DATABASE_URL` (internal URL, same workspace and region) as well as the password. Audit A6: the `web` job is still not a required check. |
| Q16 | Income-tax annual authority: [TAA s 92A](https://www.legislation.govt.nz/act/public/1994/166/en/2026-09-04/) expressly permits Commissioner basic-rate assessments before annual enactment. [DEC-001](policy_specs/income_tax/decisions/DEC-001-annual-authority.md) records the newly checked provision and the unresolved effect on Poltika's component. Bill 344-1 remains proposed-law context; D11's `needs_review` gate remains in force. | Promotion of the 2026–27 annual-tax specification/parameters and numeric results; no claim that pre-enactment official assessments are automatically invalid. | Review s 92A with the independent Claude source/spec review and confirm the component's authority basis; any revised D11 gate needs your explicit decision. Update 11 October: a second independent source review ([record](reviews/2026-10-11-pr193-independent-source-review.md)) confirms the Schedule 1 table matches statute and Bill 344-1 cl 3 (introduced 10 September 2026) would impose the same rates but is unenacted. Decide: `calculated` labelled "annual rates Act pending", or `needs_review` until Royal assent. |
| Q17 | Income-tax precision: checked annual Acts and IRD material have not established treatment of taxable-income cents, intermediate precision, final rounding or ties for this basic-tax component. [DEC-002](policy_specs/income_tax/decisions/DEC-002-annual-precision.md) gives the bounded search and its limits; no PAYE/FBT convention is transferred. | Numeric annual-tax specification, values/cases/benchmarks and implementation; even known-zero outcomes remain gated. | Identify or commission a dated official annual basic-tax method/clarification, then decide after source and independent review. No rounding choice is proposed as law. Update 11 October: the independent review found no TAA or ITA rule for fractional dollars. Choose a labelled Assumption: cent-exact with a stated final rounding mode and tie rule, or whole-dollar inputs only (anything else `unsupported`). |
| Q18 | Apparent earlier-year IR3G worksheet discrepancy: the author visually confirmed p 43 threshold A $78,101 for the $78,101–$180,000 band, alongside accumulated tax $15,650.50; statutory per-dollar bands appear inconsistent with that worksheet threshold. [DEC-003](policy_specs/income_tax/decisions/DEC-003-ird-worksheet-conflict.md) records source and inference separately. | Adoption of that guide as benchmark evidence; it covers 2025–26 and does not establish the commissioned 2026–27 year. | Review the row independently and obtain official correction/clarification or independently retained period-matched benchmarks; do not silently repair or adopt a worksheet cell. Update 11 October: the independent review re-extracted IR3G p 43 ($78,101 / .33 / $15,650.50) and confirms a $0.33 understatement against the statute-derived bands; it recommends the statute prevails and the guide is excluded as a benchmark. |
| Q19 | Household mapping questions from Tasks 5–6 (this PR's [packet](review_packets/task5_6_unit_binding_household_mapping.md)): (1) what period an AS stock amount (`NZD`: asset ceilings, imputation thresholds, `cash_assets`) belongs to, a point in time or the assessment week; (2) reconciling the WFF and AS dependent-child definitions that `ChildFacts` holds, and the AS source; (3) person and family identifier schemes (synthetic ids today); (4) may the pairwise checks be retired for `Household` inputs only, keeping the pair format unchanged; (5) the period relation between a weekly main-benefit spell and the WFF year for the restated main-benefit check; (6) how stored-scenario and API formats treat a disagreeing pair once the household is canonical; (7) whether WFF gains a "relationship changed in year" fact so that case is explicitly `unsupported`. | ADR-0017 Task 1.4, Tasks 9–10 and the WFF relationship-change conformance row. Tasks 5–6 as merged change no amount. | Answer (4) and (7) as engineering choices if you wish (both change no output); (1), (2) and (5) need a sourced reading, with GPT/Codex review. |

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

### Q1 commands (already applied on 5 October 2026; do not re-run, a second POST would create a duplicate ruleset)

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
| P8: strategic first-product surface | 3 October; reconfirmed 5 October 2026 | Pete's original brief is archived under docs/archive/programmes/; ADR-0021 records Workbench first. ADR-0018 acceptance remains Q9. |
| Q8: v0.2.0 release record | 5 October 2026 | Pete's 5 October "accept, approve, proceed", [dated scope record](docs/programme/2026-10-06-pete-approvals.md): annotated tag 63f5f0d points to adf4058, verified remotely. D10 records the guarded correction. |
| Q1: main ruleset and squash-only auto-merge | 5 October 2026 | Applied by Claude Code under Pete's delegation: repo settings allow_auto_merge, delete_branch_on_merge, squash only; ruleset id 24478578 "main", active, no bypass actors, no deletion or force-push, PR required, strict up-to-date, required checks test, pilot-image, check-protected-paths, check-immutable-snapshots, source-currency, pip-audit, links, Bandit (python), zizmor (actions). Red-check blocking observed on #168 at fb92c17: required test FAILURE, other eight required checks SUCCESS, GitHub BLOCKED. No merge attempt or bypass was made. |
| Recovered Step 1.2/1.5/1.6/2.2/2.3/2.4 drafts | 5 October 2026 | "approve commit and merge where required"; [dated record](docs/programme/2026-10-06-pete-approvals.md), decision log D13. Gates still apply. |
| Q1/Q8 and plan item 3.4 wording authority | 5 October 2026 | "make the best decisions for this"; [dated record](docs/programme/2026-10-06-pete-approvals.md), D14. Item 3.4's edit is in pending #151. |
| P8, Q5 scope/order, #163/#164 and other-model rotation | 5 October 2026 | "accept, approve, proceed"; [dated record](docs/programme/2026-10-06-pete-approvals.md), D9–D12 and D15–D17. ADR-0018 remains proposed; D2's actual definition and Q10 remain open. |
| #163 constitution and #164 resolved governance/card choices | 5 October 2026 | "accept merge and commit all"; [dated record](docs/programme/2026-10-06-pete-approvals.md), D15–D16. This records acceptance, not final review/CI or merge. |
| Conditioned #170 single pass and #167 brief hash | 6 October 2026 | "agree to both"; [dated record](docs/programme/2026-10-06-pete-approvals.md) names both by reference only; detail is in Pete's supplied brief (sha256 c6e67946…). Adopted as ADR-0020 via #176 (replaced #170) and D9; D17. |
| #154 reporting library disposition | 7 October 2026 | Closed unmerged and parked for Phase F Task 24 by Pete's coordinator session (D22, [#154 closing comment](https://github.com/hemmingsenpeter-byte/poltika/pull/154)). Supersedes the earlier "fix and merge 154" instruction. |
| #130 source-currency report | 7 October 2026 | Pete: keep the weekly tracker open. Its one Due item (`in_work_base` 2026-27 `needs_review`) settles under BUILD_PLAN_v0_1_6 Task 3 after 1 April 2027; the 25 source rechecks go to the Codex lane ([#130 comment](https://github.com/hemmingsenpeter-byte/poltika/issues/130)). |
| Sole merger for this closeout | 6 October 2026 | "yes this session owns all merges into main"; [dated record](docs/programme/2026-10-06-pete-approvals.md), D18: Claude alone merges, Codex pushes PR fixes. |

## Decisions made under Pete's delegation, 5 October 2026

Pete's instructions that day: "approve commit and merge where required" (commit the uncommitted worktree work into PRs and merge where gates pass) and "make the best decisions for this" (plan item 3.4, Q8, Q1). The approvals do not clear #148/#151: Codex-authored source scopes still require a full final-head independent Claude pr-review with primary-source re-derivation.

- **Plan item 3.4 (`BUILD_PLAN_v0_3.md`) rewording approved; pending in #151.** Social Security Act 2018 s 18 (as at 4 September 2026) bars receiving, at the same time and in one's own right, more than one main benefit, or a main benefit with New Zealand superannuation or a veteran's pension. It is per person, not per household. Schedule 4 Part 1 cl 1(g) and Part 3 cl 1(d) set rates for a beneficiary whose partner is granted a main benefit in the partner's own right. Decision: state the per-person restriction with that citation; a couple where each partner receives a main benefit is `unsupported` until a specification models the Schedule 4 categories. No new entitlement logic is asserted. The quotations were checked in the PM's copy of the source. Whether the BUILD_PLAN_v0_3.md edit has merged is recorded in that file's history, not by this entry.
- **Q1** applied (see Done). **Q8** was resolved by Pete on 5 October; see Done.

### Q5 approval, 5 October 2026

Pete approved the best choices in the supplied closeout recommendations.
D11–D12 record the chosen scope and measure order. The prepared evidence above
remains a historical draft snapshot; it does not supply approved statutory
parameters or a disposable-income definition. Source review and precision
gates remain open. Mixed-benefit couples remain a supported-slice exclusion,
with the per-person s 18 wording to be integrated through #151.
