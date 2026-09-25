# Poltika v0.1.5 Build Plan

**Date:** 25 September 2026
**Status:** DRAFT for Pete's approval. Nothing here is frozen until Pete
approves it. `BUILD_PLAN.md` stays the frozen record of v0.1 and its
doctrines, which still apply here.

## Why this plan exists

Until now v0.1.5 was a label with no content: "evidence intelligence /
pilotability" in the Roadmap Doctrine, and a "deferred repo taxonomy rework"
in Task 35.4. This plan gives it a scope, tasks and an exit gate, using only
work that v0.1 already identified and deferred.

## Purpose

v0.1 proves the engine is correct for one scoped household. v0.1.5 makes it
usable by someone who did not build it, and keeps the evidence behind every
number visibly current. It adds no new policies and no new data; those are
v0.2.

- **Evidence intelligence:** Poltika tells you when a result depends on a
  rate that is pending, open-ended, expiring or out of date, before you rely
  on it.
- **Pilotability:** a pilot user can deploy Poltika, ask a supported question
  and read the answer and its provenance without the builders present.

## Scope

In scope:

1. Rate-status and source-freshness reporting.
2. Closing the in-work tax credit gap when the evidence allows.
3. A reproducible deployment and a pilot-user guide.
4. Repository clean-up: the deferred "taxonomy rework".
5. The development workflow, written down.

Out of scope, and where each goes:

| Item | Goes to |
| --- | --- |
| New policies | v0.2 onward |
| Statistical data and connectors | v0.2 |
| Policy interaction graph | v0.3 |
| Scenario comparison | v0.4 |
| Sensitivity and uncertainty analysis | v0.5 |
| Next.js front end | v0.9, unless Pete brings a minimal screen forward (open decision D2) |

## Tasks

Owners follow the v0.1 roles: GPT/Codex for sources and interpretation,
Claude Code for implementation, and the other model reviews.

### 1. Rate-status and source-freshness report (evidence intelligence)

- **1.1 — Claude Code.** A command, and an API route, that reports for each
  policy:
  - every parameter value that is `needs_review` or open-ended, or whose
    `effective_to` falls within a set window (for example 90 days);
  - every `sources.yaml` entry whose retrieval date is older than a set age.

  This only reads the policy files; it never looks anything up on the web.
- **1.2 — Claude Code.** Put that status into each result's provenance
  report, so a reader sees for example "in-work tax credit base: pending
  Order in Council check" next to the numbers.
- **1.3 — GPT/Codex.** A written procedure for re-checking a pending or
  expiring rate against its primary source: what to fetch, how to record it
  in `sources.yaml`, and who approves it.

### 2. Close the in-work tax credit gap (Task 26b follow-on)

- **2.1 — GPT/Codex.** Re-check the Order in Council record for the
  temporary in-work tax credit base. If it confirms $7,670 for the whole of
  2026-27 (or once the year has ended), record the evidence and propose the
  `review_status` change; otherwise record the new date to check again.
- **2.2 — Claude Code.** Only after 2.1 is approved: update the protected
  values and tests through the test-doctrine process. WFF totals then become
  possible. The README limitation is removed only at that point.
- **2.3 — GPT/Codex.** Source the 2027-28 WFF and Accommodation Supplement
  rates when they are published, before the 1 April 2027 end of every
  current interval.

### 3. Pilot deployment

- **3.1 — Claude Code.** A container image and a compose file that run the
  API and PostgreSQL, apply migrations, and mount `policy_specs/`
  (ADR-0011). CI builds it.
- **3.2 — Claude Code.** A pilot-user guide: how to deploy, how to call
  `/household/calculate`, how to read `calculated`, `needs_review` and
  `unsupported`, and what the results are not (conditional on asserted
  facts; not entitlement determinations).
- **3.3 — Pete.** Run one pilot session with someone outside the build and
  record what they could not do unaided. Their findings become v0.1.5 fixes
  or v0.2 inputs.

### 4. Repository clean-up (the deferred "taxonomy rework")

- **4.1 — Claude Code.** One home for review material. `review_packets/`,
  `reviews/` and `docs/research/` hold overlapping kinds of records. Propose
  a single structure in `REPOSITORY_STRUCTURE.md`, move the files with
  `git mv` (history is kept), and fix every link.
- **4.2 — Claude Code.** Trim code comments that narrate review history
  (task and PR numbers) to what the code does; the history stays in git and
  the review records. No behaviour change.
- **4.3 — Claude Code.** Split `BUILD_PLAN.md`'s finished task log from its
  doctrines, so the doctrines are short enough to read before every task.
  Pete approves the split, because the doctrines are frozen.

### 5. Development workflow

- **5.1 — Claude Code.** Write the working agreement into
  `doctrine/development-doctrine.md`:
  - every change goes to `main` through a pull request, never a direct push;
  - a PR merges only with CI green and its review recorded;
  - releases are tagged on merge commits.
- **5.2 — Pete.** Decide on enforcement (open decision D3): GitHub branch
  protection needs a paid plan or a public repository (ADR-0007). Until
  then, the rule is kept by agreement.

## Exit gate

A pilot user who did not build Poltika can:

- deploy it from the documented container setup;
- answer a supported WFF and Accommodation Supplement household question
  through the API;
- see, for every number, which sources back it and whether any rate is
  pending, open-ended or expiring.

Along with that, every release check passes (CI, the question-set scripts
reproduce), and the in-work tax credit is either calculated from approved
evidence or shown as pending with its next check date.

## Open decisions for Pete

- **D1:** Approve this scope, or change it.
- **D2:** Should a minimal read-only results screen come forward from v0.9?
  The recommendation is no: the guide and the provenance report are enough
  to pilot.
- **D3:** Branch protection: stay on agreement only, or make the repository
  public or upgrade the plan to enforce it.
- **D4:** Should DEC-001's option (c), a machine-readable reason category
  inside `unsupported`, be part of v0.1.5? The recommendation is yes, if the
  pilot shows users need to tell "not modelled" from "not entitled" without
  reading the reason text.
