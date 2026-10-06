# Pete approval record — 6 October 2026

Recorded by GPT/Codex from Pete's supplied closeout follow-up brief received
on 6 October 2026. The attachment's SHA-256 is
`c6e679467e65e04f54ac27d7b16cda9a988df096a1c8aa69d73a424334cea640`.
The dated quotations and their approved scope below reproduce the supplied
record. This records Pete's decisions; it does not independently settle a
statutory rule, select D2's definition, approve protected values, or clear a
PR's final-head review or CI. ADR-0018 remains proposed and Q10 remains open.

## Ground rules (Pete's decisions)

- **Merges.** Pete, 6 Oct 2026: "yes this session owns all merges into main". The Claude
  Code session is the only merger into `main`. You push fixes to PR branches and open
  PRs; you do not run `gh pr merge` or enable auto-merge. (#173 merged outside that rule
  on 6 Oct; nothing to undo, just don't repeat it.)
- **Reviews.** After every push, a fresh Claude review of the final head decides the
  merge. Fix findings in-branch and push again; never force-push.
- **Branches.** Keep each PR up to date with `main` by merging `origin/main` in. If
  `main` moves after your push, the Claude train updates the branch itself.
- **Unchanged.** No statutory value, threshold, rule or date from memory, and no Tier C
  decision. Primary sources only.

## 1. Pete's approvals to record

Record each approval verbatim, with its date, in `PETE_QUEUE.md` (Done section) and the
relevant decision records. The Claude session cannot write approval records, so this
falls to you.

- **5 Oct, "approve commit and merge where required".** Covers committing the recovered
  Step 1.2, 1.5, 1.6, 2.2, 2.3 and 2.4 worktree drafts into PRs and merging them where
  their gates pass.
- **5 Oct, "make the best decisions for this".**
  - Q1: main ruleset id 24478578, applied. #168 showed it blocks merges on a failing
    required check.
  - Q8: the v0.2.0 tag.
  - Plan item 3.4: reworded to the Social Security Act 2018 s 18 per-person rule.
    Schedule 4 Part 1 cl 1(g) and Part 3 cl 1(d) set rates for partners each on a main
    benefit; mixed-benefit couples are `unsupported` until a specification models them.
- **5 Oct, "accept, approve, proceed"** (on Claude's recommendations):
  - P8: Analyst Workbench first. ADR-0018 stays proposed (Q9).
  - v0.2.0: annotated tag on `adf4058`. Done; the tag object peels to adf4058.
  - Accept #163 and #164.
  - The cross-model review comes from the model that did not author the PR (#170).
  - Q5:
    - D1 income tax: 2026-27 basic annual tax, salary and wages first. Stays
      `needs_review` until Bill 344-1 is enacted.
    - D1 benefits: single-person slices only (Jobseeker Support single 25+ with no
      children; Sole Parent Support single principal caregiver; Supported Living
      Payment single with no children). Each is the gross weekly entitlement for an
      established grant, as at a stated date before 2 November 2026.
    - D2: adopt one official disposable-income definition whole, after source-scoping.
      Components Poltika doesn't model are reported as uncovered, never as zero.
    - D3: effective marginal tax rates first; adequacy measures only after D2's
      sources are reviewed.
- **5 Oct, "accept merge and commit all".**
  - #163: Pete's acceptance covers the epistemic-constitution amendment, including the
    rewritten non-negotiable 2.
  - #164: Pete accepts the governance choices as resolved, including the three that
    differ from the draft: Pete as accountable owner of all four models, change records
    required at review time with no CI gate, and demotion triggers set.
  - #164: apply the card fixes. Done in 4975124.
- **6 Oct, "agree to both".**
  - The #170 single-pass rule with a condition; see #170 below.
  - The #167 brief hash approach; see #167 below.

