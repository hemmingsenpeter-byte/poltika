# Pete's queue

The open Tier C items (ADR-0020): the decisions and actions only Pete can
take. Each says what it blocks and the smallest action that clears it.
Work routes around every item here. When one is done, Pete (or the session
that records his answer) moves it to "Done" with the date and the PR or
commit that records it.

## Open

| # | Item | Blocks | Smallest action |
| --- | --- | --- | --- |
| Q2 | Māori data governance, privacy and security (old 1.4/P5). Engage people with standing in Māori data governance. | Ethnicity/iwi-disaggregated outputs and microdata uses where governance is required (E/M); the interim ban holds. It does not block unrelated deterministic household modelling or Pilot 1. | Parked with a trigger. Decided 13 October 2026 (D38, after the [research](docs/research/q2_maori_data_governance.md)): keep the ban, name nobody yet; reference frameworks Ngā Tikanga Paihere and the Te Mana Raraunga principles. When a use of Māori data or an IDI project is first proposed: commission a bounded governance proposal, then Pete decides whom to engage. |
| Q3 | IDI access (P12): lodging an application. | IDI-calibrated population claims and applicable microdata work (E/M), not household Pilot 1. | Parked with a trigger. Decided 13 October 2026 (D38, after the [access-route research](docs/research/q3_idi_access_route.md)): no contact or lodging. When Gate E is in view: commission a one-page project scope and dataset-feasibility check (public aggregates or a CURF first); contact and lodging stay Pete's. |
| Q4 | Reserved programme decisions, explicitly remapped below. | Only their named capabilities. P18 governs claiming each milestone; no migration document declares a gate met. | Decide concrete options with evidence when each capability starts. Decided 12 October 2026 (D36): nothing now. P6 stays internal; P7, P13, P14 and P20 wait for their phases. Remaining: P18 acceptance tolerances before the next phase gate is claimed. |
| Q5 | D1 supported slices and D2/D3 order decided by Pete on 5 October 2026; [decision log](docs/decision_log.md), D11–D12. Income tax: 2026–27 basic annual salaries/wages first, `needs_review` until Bill 344-1 is enacted; benefits: single existing-grant slices as at a stated date before 2 November 2026, gross weekly entitlement. Official disposable-income source scoping commissioned; EMTR first. | Numerical implementation still needs independently reviewed source/spec/precision/benchmark evidence; D2 definition and income-path methodology remain unapproved. | Review the official-definition source pack when ready. No unsupported component becomes zero and no unenacted annual-rate authority becomes calculated. Decided 12 October 2026 (D36): one main benefit per household is a deliberate coverage limit for the first benefit slice, not a legal claim. `BUILD_PLAN_v0_3.md` 3.4 already says so, so no plan change is needed. Remaining: review the disposable-income source pack when ready. |
| Q11 | External analyst participation and eventual release tags for untagged work. | Pilot evidence in D/G; v0.1.5 release completion and later tags. No external pilot is recorded yet. | Name and authorise an external pilot participant/session when the workflow is ready; tag only against the actual release evidence. No outreach or public deployment is authorised by this migration. Decided 12 October 2026 (D36): no external participant until B0.1.7 is deployed and Q23 passes; tag v0.1.5 only against its release evidence. Remaining: name a participant, and tag. |
| Q15 | Task B0.1 deployment (D24, ADR-0023): confirm which Render workspace holds the `poltika.onrender.com` service, choose the Render PostgreSQL plan/size, and set `POLTIKA_ACCESS_PASSWORD` as a secret in the Render dashboard; optionally make the new `web` CI check required in the repository ruleset. | B0.1.7 deployment only. B0.1.0–B0.1.6 proceed without it. | Tell the session the workspace and database plan; set the password yourself (it is never committed or sent through a session). Update 11 October: B0.1.7 readiness check ([record](reviews/2026-10-11-b017-deploy-readiness.md)): fail-closed auth, `/healthz` and PostgreSQL persistence are in place; set `POLTIKA_DATABASE_URL` (internal URL, same workspace and region) as well as the password. Audit A6: the `web` job is still not a required check. Decided 12 October 2026 (D36): a paid PostgreSQL plan with backups, and `web` becomes a required check. Found on 12 October (read-only): the "Poltika" workspace holds the `poltika` web service (Docker, Oregon, auto-deploys on commits to `main`, no health-check path set) and the PostgreSQL instance `poltika-db` (plan `0.1c-256mb`, 1 GB, Oregon). Remaining: Pete confirms that this plan includes backups, sets `POLTIKA_ACCESS_PASSWORD` and `POLTIKA_DATABASE_URL`, and adds `web` to the required checks (see Q20). **Found 15 October 2026 (read-only HTTP probes, no Render change): the live service is open with no password.** It is serving `main` `63359fe`; `/api/v1/meta` reports `"password_required": false`, and `/`, `/models` and `/api/v1/meta` answer 200 without credentials. The image sets `POLTIKA_REQUIRE_ACCESS_PASSWORD=1` (`Dockerfile`), so a Render environment variable is probably overriding it (inferred from the image and `api/access.py`; the dashboard will confirm). The data is synthetic, but the CPU-heavy population runs have no rate limit and are open to anyone with the address. Steps in the Render dashboard, workspace "Poltika": (1) service `poltika` > Environment: add `POLTIKA_ACCESS_PASSWORD` (a long random password, entered there only), delete any `POLTIKA_REQUIRE_ACCESS_PASSWORD` override (the image default is `1`), and add `POLTIKA_DATABASE_URL` = `poltika-db`'s **internal** connection URL; (2) service Settings > Health Check Path: `/healthz`; (3) `poltika-db`: check that its plan shows backups or point-in-time recovery, and upgrade it if not (D36 asks for a backed-up paid plan); (4) save, which redeploys. Then tell the session, which runs the live smoke: 401 without the password; Home, Scenarios, a created and reopened run, Models and Data with it; and the same run still there after a manual restart. **Update 16 October 2026: password set.** At Pete's instruction, Claude Code set `POLTIKA_ACCESS_USER=pilot`, `POLTIKA_ACCESS_PASSWORD` and `POLTIKA_REQUIRE_ACCESS_PASSWORD=1` on the `poltika` service through the Render MCP (merge, no other variable touched), which redeployed it. Checked live: `/`, `/api/v1/meta` 401 without credentials, 200 with them; `/healthz` 200; `access.password_required: true`. The password passed through that session's transcript, so Pete may rotate it in the dashboard. Still open: no database is attached (a scenario lookup answers 503), so `POLTIKA_DATABASE_URL`, `poltika-db`'s backed-up plan (step 3), the health-check path (step 2) and the live smoke remain. |
| Q20 | Audit A1/A2 follow-ups (#191; `reviews/2026-10-11-audit-191-verification.md`): (1) the hosted pilot has one shared login and no per-user ownership of stored scenarios: confirm it stays synthetic or public non-personal data only (`docs/pilot/HOSTING.md`), and whether the web app shows a banner saying so; real personal data or multi-user use needs a per-user authorisation and retention design first; (2) confirm in GitHub Settings > Actions that workflows from fork pull requests are off or need approval, and who has write access; (3) a skipped required check counts as passing, so a fork PR shows green unless `fork-pr-gate` becomes a required check (ruleset change). | Real personal data, multi-user or public use of the hosted pilot; fork contributions. Not the synthetic single-operator pilot. | Confirm (1) and (2) in a line each; add `fork-pr-gate` to the ruleset once it has run, or decline. Decided 12 October 2026 (D36): (1) synthetic or public non-personal data only, with a web banner (shipped: a notice under the header on every page); (2) workflows from fork pull requests are already disabled in this private repository's settings, which is stricter than requiring approval, so no change is needed; (3) required checks. Update 16 October 2026 (D41): the repository is public and CI is GitHub-hosted, so `fork-pr-blocked` is retired and a fork pull request runs every check instead of skipping to green; (2) is now the public-repository setting that requires approval before an outside contributor's workflows run. Remaining: Pete adds `web` to ruleset 24478578's required checks. The offline runner registration `pete-mac-1` was deleted on 16 October; the repository has no self-hosted runner. The Claude Code session's classifier blocked that change. `web` reports on every PR to `main`, and a skipped check counts as passing. |
| Q23 | Real-phone check of B0.1.6 (iOS Safari and Android Chrome): the drawer, tab-strip swiping, scroll regions by finger, the address-bar resize, and tapping the 24px targets. The headless Chromium and WebKit measurements at 360px pass (`reviews/2026-10-12-b016-360px-browser-check.md`). | B0.1.6 acceptance; Q11's external pilot. | About 10 minutes on one iPhone and one Android phone; record the result in that review file. |
| Q24 | Accept #219 (Task 7 numeric draft) into `main` as an explicitly draft packet: `policy_specs/income_tax/policy.yaml`, `spec_cases.yaml` and `benchmarks.yaml` are protected statutory-value files. The independent Claude review on 15 October ([comment](https://github.com/hemmingsenpeter-byte/poltika/pull/219)) found no P1, P2 or P3. All nine parameters match the ITA dated 4 September 2026 (Schedule 1 Part A Table 1), and all 17 arithmetic candidates reproduce. Every expected result stays non-numeric (`needs_review` or `unsupported`), `policy_version: null`, and every value is `review_status: needs_review`. | Task 7's engine PR, which would build on these files. It would still return only `needs_review` for this slice until the annual-rates bill gets Royal assent (Q16; select committee as at 12 October) and DEC-004's benchmark and precision gaps close. | Say "accept #219 as draft" or decline. Accepting approves no value as authoritative. |
| Q25 | Task 8 coverage choice for SPS and SLP (#220, review finding R1): their drafts cover only a person with an active r 205(2) one-week income agreement. SSR Schedule 6 item 1 puts both benefits on a 52-week income basis by default, so the ordinary recipient would be `unsupported`. Also narrowed without a decision record: SLP excludes under-18s, and SPS requires the s 30(a) route with no shared or split care. | Approval of the SPS and SLP specifications, not Jobseeker Support (whose basis is one week under Schedule 6 item 2). | Once GPT/Codex adds the DEC: choose (a) the agreement-only slice now, with a 52-week path later as its own reviewed slice, or (b) commission the 52-week basis before implementation. |

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
| Q26: licence for the public repository | 16 October 2026 | Proprietary, all rights reserved, view only ([LICENSE](LICENSE)); D42. |
| Q13: self-hosted runner account | 16 October 2026 | Moot: the runner `pete-mac-1` is retired and CI runs on GitHub-hosted runners (D41), so the `poltika-ci` cutover is not needed. |
| Q19: household mapping questions (1), (2), (5) | 13 October 2026 | (1) a stock has no period, `cash_assets` is the caller's balance for the assessment week; (2) separate WFF/AS child facts, first-N adapter marking is not membership; (5) a main-benefit spell in the tax year is refused against a verified whole-year no-benefit assertion, dates only. (3), (4), (6), (7) were decided 12 October (D36). [record](docs/programme/2026-10-13-pete-approvals.md), D38. |
| B4: s 423(3) incomplete $100 asset blocks | 13 October 2026 | Complete steps only, as the engine does; AS [DEC-004](policy_specs/accommodation_supplement/decisions/DEC-004-asset-imputation-complete-steps.md). [record](docs/programme/2026-10-13-pete-approvals.md), D38. |
| Q12: delete merged remote branches | 12 October 2026 | Pete approved (D36). Claude Code re-checked every tip and deleted 91 branches: 87 still at the head of their squash-merged PR and 4 whose content is on `main` through #211. Tips are recorded in `reviews/2026-10-12-q12-branch-verification.md`. Twelve clean local worktrees whose branches had merged were also removed (D35). [record](docs/programme/2026-10-12-pete-approvals.md). |
| Q7: historical horizon (P11) | 12 October 2026 | Defer the historical horizon to Phase I; the earliest year is then a delegated, reversible choice made from a sourced coverage proposal. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q9: ADR-0018 Workbench design | 12 October 2026 | ADR-0018 accepted as built; later changes go through new ADRs. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q10: Household/fiscal methodology | 12 October 2026 | #195's wording is the interim income and period contract for Tasks 5, 6 and 9. No apportionment: the caller supplies an amount per policy period (D32). [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q14: Confirm two reversible D20 defaults | 12 October 2026 | The 50 MiB response cap and the Bandit MEDIUM gate are confirmed. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q16: Income-tax annual authority | 12 October 2026 | D11 stands: `needs_review` until Royal assent, then `calculated` after a dated source check. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q17: Income-tax precision | 12 October 2026 | Whole-dollar taxable income only, anything else `unsupported`, labelled as an Assumption; revisit if an official method is found. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q18: Apparent earlier-year IR3G worksheet discrepancy | 12 October 2026 | The statute prevails; IR3G is excluded as a benchmark and recorded as `SOURCE_CONFLICT`; IRD is not contacted for now. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q21: Task 14 reform replay | 12 October 2026 | (a) Rerun-and-compare for now; a retention ADR when a real population arrives. (b) Effective-from date required, fiscal year derived, announcement date optional (a Claude Code task). (c) Follows Q9. (d) Implemented: inputs and results decide `identical` or `drifted`, and a code change is reported as `code_changed`. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
| Q22: Dependabot alert #1 (`braces`) | 12 October 2026 | Alert #1 dismissed by Claude Code on 12 October as tolerable risk (dev-only, no patched version); revisit when a patch ships. [record](docs/programme/2026-10-12-pete-approvals.md), D36. |
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
