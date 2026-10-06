# Codex recheck of closeout records — 7 October 2026

## Findings and clearance

**No P1/P2 or escalation. One nonblocking P3, R1 below.** The Claude-authored
#167 integration/record changes and #151 conflict resolution are independently
rechecked within this record's bounded scope. The Claude-authored #177 records
are faithful to observed approval and review history, apart from R1's conflict
count. R1 does not prevent bounded clearance; correct it in the existing handoff.

This is an **independent cross-model review (GPT/Codex)** of the named Claude
changes, not author preflight or acceptance. It clears only approval fidelity,
integration preservation and historical-review provenance for those changes.
It does not independently clear the underlying Codex-authored source research,
#171's entity implementation, #174's parser or #176's review-rule semantics.
Their separately assigned reviews retain ownership. No queue is edited here.

## Review inputs

- Reviewer: GPT/Codex, 7 October 2026, Pacific/Auckland; read-only except this record.
- Checkout: `/private/tmp/poltika-codex-closeout-rechecks-20261007`, pinned main
  `a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d`.
- Contract derived before reading target diffs or target PR rationale. During
  review the commit messages and PR/comment rationale were read as historical
  evidence; this was not a blind pass throughout.
- Contracts: AGENTS.md; BUILD_PLAN.md's retained Roles/review doctrine;
  ARCHITECTURE.md; REPOSITORY_STRUCTURE.md; current programme Phase A record
  fidelity; review, test and IP doctrines; ADR-0020; the repository `pr-review`
  skill and `references/writing-findings.md`; Pete's dated approval record.
- No external policy implementation was inspected. No statutory rate, rule,
  threshold, date or interpretation is independently rederived in this pass.

| PR and coverage | Integration/source head reviewed | Merge base/main and squash |
| --- | --- | --- |
| [#167](https://github.com/hemmingsenpeter-byte/poltika/pull/167), Claude integration and records after Codex `6fcfab5126bb6ad3504b19126ff4eb372966564d` | `52cf02e8026332dfcc22ec51362b55200849365b` | Final main `94df1a06fa08ee093f43fb3ae0f22c68cb5cf2dc`; squash `1b64d0e29685a5f445428d14bcfec33c8b9380b9` |
| [#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151), Claude conflict resolution only | `c4c4b2a2b40a4cc86b0dedffb1cc072b875dfc32` | Parents `e0e1c44b15f1cdc319696c50d5213032b2aa0147`, `164fdbd792e490c772f2ca028c21f6516da77a9d`; squash `38e5629b3db62539fa4f0714deecbe87353bdb8c` |
| [#177](https://github.com/hemmingsenpeter-byte/poltika/pull/177), Claude record commit; Codex locator cherry-pick observed separately | `40b3386b66b1ce3414184dd3700d873115b029bc` | Record parent `354079e1d30b09910c1b93ebc88f385089f86d70`; PR base `38e5629b3db62539fa4f0714deecbe87353bdb8c`; squash `0046be02257d9ddfeeb32d7abd4c6bf5da620417` |

### Complete authored scope and integration inventory

Read the record changes commit by commit and the combined merge resolutions;
compare both parents for preservation. Main-only imports are byte-identical to
the integrated main parent and are not newly authored policy logic in this pass.

| Claude commit | Exact parent(s) | Authored/resolved scope |
| --- | --- | --- |
| `cb32c8127d75e9f219301e7e055e006c01c34479` | `6fcfab5126bb6ad3504b19126ff4eb372966564d`, `0d115b4e2c63b5d6f2d6517d92f74d9d9ffdc934` | `docs/decision_log.md`: retain closeout D9–D18 and main D19 |
| `ecb9f13fc25d77a92466c12232cb68ec2a5b4c78` | `cb32c8127d75e9f219301e7e055e006c01c34479` | `BUILD_PLAN_v0_3.md`, `PROGRAMME_STATUS.md`, `docs/decision_log.md`: dated SLP confirmation and merged #171 |
| `912f8e9294d30427a122a418e07ae0862016051d` | `ecb9f13fc25d77a92466c12232cb68ec2a5b4c78`, `7c0f67e7e847e5e57f66269bf007c9fe88d1e5e7` | Conflicted `PETE_QUEUE.md` and `PROGRAMME_STATUS.md` retained the newer PR-side records |
| `02e84a4f56fd4585533a8484321febaf4efccd4d` | `912f8e9294d30427a122a418e07ae0862016051d` | `PETE_QUEUE.md`, `docs/decision_log.md`: D17 distinguishes the transcription from untranscribed detail |
| `52cf02e8026332dfcc22ec51362b55200849365b` | `02e84a4f56fd4585533a8484321febaf4efccd4d`, `94df1a06fa08ee093f43fb3ae0f22c68cb5cf2dc` | `PROGRAMME_STATUS.md`: merged #164, retaining its scope caveats |
| `c4c4b2a2b40a4cc86b0dedffb1cc072b875dfc32` | As above | `REPOSITORY_STRUCTURE.md` conflict: keep income-tax and all three benefit catalogue entries; `BUILD_PLAN_v0_3.md` automatically combines main's scope section and the existing per-person item 3.4 |
| `40b3386b66b1ce3414184dd3700d873115b029bc` | As above | All ten paths below |

#167's final own diff has nine documentation paths: `BUILD_PLAN_v0_3.md`,
`PETE_QUEUE.md`, `PROGRAMME_STATUS.md`, `adr/0021-economist-first-pilot-programme.md`,
`docs/archive/README.md`,
`docs/archive/programmes/2026-10-03-economist-first-migration-brief.md`,
`docs/decision_log.md`, `docs/programme/2026-10-06-pete-approvals.md` and
`review_packets/2026-10-05-closeout-decisions-preflight.md`. This review's
other-model clearance applies to the five Claude commits above, not the prior
Codex authored delta.

The first integration imports eight unchanged main-only files beyond the
resolved decision log: `CHANGELOG.md`, `REPOSITORY_STRUCTURE.md`,
`reviews/2026-10-05-entities-preflight.md`, `src/poltika/common/errors.py`,
`src/poltika/data/xlsx.py`, `src/poltika/semantics/entities.py`,
`tests/unit/data/test_xlsx_pinned.py`, `tests/unit/semantics/test_entities.py`.
The next integration imports fifteen unchanged main-only files:
`.claude/agents/poltika-reviewer.md`,
`.claude/skills/pr-review-preflight/SKILL.md`, `.claude/skills/pr-review/SKILL.md`,
`.github/workflows/statutory-value-guard.yml`, `.github/workflows/tests.yml`,
`AGENTS.md`, `BUILD_PLAN.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
`adr/0007-pr-visibility-statutory-value-protection.md`,
`adr/0020-delegated-acceptance.md`, `doctrine/development-doctrine.md`,
`doctrine/review-doctrine.md`, `review_packets/pr170_reconstruction_preflight.md`,
`review_packets/review_queue.md`.

The ten #177 record-commit paths are `PROGRAMME_STATUS.md`,
`docs/research/task_0_1_income_tax_scope.md`,
`docs/research/task_0_4a_disposable_income_source_scope.md`,
`review_packets/review_queue.md`, `reviews/2026-10-06-integration-train.md`,
`reviews/2026-10-06-pr148.md`, `reviews/2026-10-06-pr151.md`,
`reviews/2026-10-06-pr172.md`, `reviews/2026-10-06-pr175.md` and
`src/poltika/semantics/entities.py`. The last edit corrects only the citation in
an unassigned-identifier refusal string, `population.py:52` to `:50`; line 50
is `person_id: str`. #177's other commit, Codex `354079e`, changes only
`review_packets/core_benefit_source_scope_preflight.md`; its original is
`3ff3590c082ff5f210fb95b51860e2ac7a048d25`. It is observed, not independently
cleared by this same-model reviewer.

## Independent review

### Independently derived expected behaviour

1. Approval records preserve the dated quotations and bounded scope in
   `docs/programme/2026-10-06-pete-approvals.md`. Scope approval alone approves
   neither a statutory amount nor a specification, D2 definition, final-head
   review or CI. ADR-0018 stays proposed and Q10 stays open.
2. Later confirmations must be dated and traceable separately from the original
   attachment. Record only observed history and distinguish its limitations.
3. Integration preserves independent parent content and correct repository
   locations. A conflict resolution is a fix, not a mechanical main update.
4. Reviewer model, authorship and exact-SHA coverage must match the evidence.
   A same-model check supports assurance but cannot clear its own model's
   cross-model gate. Mechanical updates require matching own-diff patch IDs.

### Verified observations

- The 5 October SLP approval says “Supported Living Payment single with no
  children.” The later [#167 final-head comment](https://github.com/hemmingsenpeter-byte/poltika/pull/167#issuecomment-6008967335)
  quotes Pete's 6 October clarification, “Restricted capacity only.” `ecb9f13`
  dates that clarification separately; it does not alter the verbatim attachment.
- `02e84a4` explicitly identifies the missing #170/#167 attachment sections,
  retains the actual “agree to both” quotation and points to the adopted rule
  in ADR-0020 and the supplied brief hash rather than inventing quoted detail.
- D1–D19 survive without collision. The original approval-file SHA-256 is
  `5cf4373b883e09ef7a4904eae950003b0f868781f25f60b34f1bd21303d9d06a`
  at both Codex `6fcfab5` and pinned main. The migration body, excluding its
  two-line metadata header, hashes to
  `3d0ae319bdc8167fd914ae977bd8f5fb7da340825f529ab23f098ddb7c9aa041`.
- #151 preserves source catalogues, research, regression and approval bytes
  from `e0e1c44`; its source-only boundary and the per-person item 3.4 survive.
  [Its final-head record](https://github.com/hemmingsenpeter-byte/poltika/pull/151#issuecomment-6009420684)
  accurately labels Claude's conflict resolution as previously same-model-only.
- #177's source-review summaries match the historical independent comments:
  [#148](https://github.com/hemmingsenpeter-byte/poltika/pull/148#issuecomment-6008258102),
  [#151](https://github.com/hemmingsenpeter-byte/poltika/pull/151#issuecomment-6008285786),
  [#172](https://github.com/hemmingsenpeter-byte/poltika/pull/172#issuecomment-6008301945),
  [#175](https://github.com/hemmingsenpeter-byte/poltika/pull/175#issuecomment-6008241074).
  They preserve the stated earlier gaps, exact source/delta heads and the
  distinction between source review and numerical/specification approval.
  Queue text retains the Claude-owned follow-ups; it labels none independently
  reviewed by Codex. Closed-without-merge #155/#170 matches GitHub metadata.

### Discrepancies

| ID | Severity / proposed doctrine class | Trigger and expected versus actual | Impact / resolution |
| --- | --- | --- | --- |
| R1 | P3 / SPEC_ERROR | `reviews/2026-10-06-integration-train.md:25` says “#167 twice”; git and the PR records identify three conflicted integrations: `cb32c81`, `912f8e9`, `52cf02e` | Minor historical undercount. No gate is cleared by it. Open; replace with “#167 three times” or name all three commits in the existing handoff |

Reproduction on `40b3386` and pinned main:

```sh
git show -s --format='%H%n%B' cb32c81 912f8e9 52cf02e
```

All three commit bodies carry `# Conflicts:`. They name, respectively,
`docs/decision_log.md`; `PETE_QUEUE.md` and `PROGRAMME_STATUS.md`; and
`PROGRAMME_STATUS.md`. The [#167 final-head record](https://github.com/hemmingsenpeter-byte/poltika/pull/167#issuecomment-6008967335)
explicitly calls `912f8e9` a conflict resolution; the
[last round](https://github.com/hemmingsenpeter-byte/poltika/pull/167#issuecomment-6009134024)
records the third one. Thus the discrepancy is reproduced rather than inferred
from a merge commit alone.

## Author rationale and response

Rationale read after deriving the contract: #167's final-head comments document
Pete's SLP clarification, D17's transcription limitation, the newer PR-side
queue/status resolutions and #164 caveats. #151's final-head comment documents
preserved catalogue bytes and the same-model-only conflict-resolution pass.
#177 describes the record refresh and correctly labels the locator cherry-pick.
Those explanations match the observed changes. No response to R1 has yet been
requested or received; this reviewer made no code/record correction or GitHub post.

## Resolution and verification

- `git show --cc` and both-parent diffs: all listed resolutions inspected;
  main-only imported paths compare byte-identical to the respective main parent.
- `git diff --exit-code e0e1c44 c4c4b2a --` the three benefit catalogues,
  source note, existing regression and approval file: no difference.
- `git diff --exit-code 52cf02e 1b64d0e`,
  `git diff --exit-code c4c4b2a 38e5629`,
  `git diff --exit-code 40b3386 0046be0`: identical trees.
- `git diff --exit-code 40b3386 a8b214f05c7aa7380fb0ca0adfd68c30c81bf06d --` all eleven #177 PR paths: no difference.
- `git diff --check 52cf02e^2 52cf02e`,
  `git diff --check c4c4b2a^2 c4c4b2a`,
  `git diff --check 40b3386^ 40b3386`: clean.
- Mechanical-update own-diff patch IDs reproduced locally using
  `git merge-base <old head> <new main>` and
  `git diff <base>...<head> | git patch-id --stable`:
  #148 `73ffb16` → `c064533`, main `30935de`,
  `6c10020df08078c85acafab54ab1ad4b9aa36f9f` on both sides;
  #172 `b3f26fe` → `85b6797`, main `4c09972`,
  `c9f9eb74945b1d3336d17157fe09f83d44c23c9a` on both sides;
  #175 `b401939` → `795f1b2`, main `1b64d0e`,
  `04955f14e27cda3b1f6aaf4349112c55eebf6840` on both sides.
- GitHub connector readback: #167, #151, #177 are merged at the exact heads
  and squashes above. On each head all nine required jobs succeeded: `test`,
  `pilot-image`, `check-protected-paths`, `check-immutable-snapshots`,
  `source-currency`, `pip-audit`, `links`, `Bandit (python)`, `zizmor (actions)`.
  Representative Tests runs: [#167](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37412186831),
  [#151](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37414420296),
  [#177](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37415064914).
  `publish-issue` and `external-links (report only)` were skipped on PR events;
  no required job was skipped. Offline Links jobs succeeded on all three heads.

### Limits and remaining gates

No local runtime suite or source-law check was run for this bounded records
review; the root lane owns current-main broad verification. Local `lychee` was
not on PATH. Historical green CI supports the exact historical heads, not the
new review-documentation head. Local relative-link verification is recorded
below after writing this file. External statutory/public links were not fetched
as a law check. The original private attachments and direct Claude-session user
conversation are not available in this review; their historical quotations and
hashes are checked against committed records and exact GitHub comments, with no
claim of independent original-attachment authentication.

R1 remains nonblocking. Queue closeout, new-document author preflight, a fresh
Claude review of the resulting documentation head, green final-head CI and
Claude's integration decision remain separate steps. This record neither
accepts Tier C choices nor authorizes an implementation or release gate.

Local read-only Perl link probe over this record and fourteen scoped Markdown
inputs: **56 relative file links, four heading fragments, 77 external links
identified; zero local errors**. The probe resolves relative targets and matches
Markdown heading slugs; external targets are counted but not fetched. This is a
bounded local check, not a replacement for the successful historical Links CI.
