# Q11 / Q15: analyst demonstration and deployment proposal

**Date:** 9 October 2026. **Status:** proposed for Pete; no outreach,
resources, secrets, settings change, deployment or tag is authorised by this
record. Owner: Pete; preparation: GPT/Codex; implementation/acceptance of
engineering: Claude under [ADR-0020](../../adr/0020-delegated-acceptance.md).

This develops the existing [#191 recommendation](https://github.com/hemmingsenpeter-byte/poltika/pull/191#issuecomment-6069451786).
It does not duplicate an accepted decision: [Q11/Q15](../../PETE_QUEUE.md)
remain open; D24 approved the frontend direction, while leaving workspace,
paid database, secrets and the ruleset change to Pete. See
[ADR-0023](../../adr/0023-web-frontend-product-surface.md) and the
[B0.1 lane](../../BUILD_PLAN_B0_1_WEB.md).

## Wording proposed for acceptance

**Q11.** Permit early contact with one independent New Zealand economic-policy
or tax-transfer analyst and one backup, after Pete names and approves the
actual contacts. The first session may be a protected synthetic-data UI
usability demonstration. Record comprehension, entry friction, evidence and
export navigation, and feedback. It is separate from formal Pilot 1.

Formal Pilot 1 requires the supported household workflow and Phase B/C gates,
an actual external participant and analysis question, recorded consent/scope,
code/policy/run identities, reproducible results, limitations, feedback and
disposition of material findings. No internal demonstration establishes its
completion. Tags require the corresponding reviewed release evidence and
Pete's retained acceptance; create none merely because CI or a demo passes.

**Q15.** Reuse the existing Render workspace and `poltika.onrender.com` Docker
web service after verifying account, workspace, region and current service
settings through Render MCP. Use the smallest suitable paid managed
PostgreSQL plan in the same region, with its private connection URL. Store
all secrets in Render. Pete sets the access password directly; credentials
are never pasted into chat or committed.

The shared-password demonstration is one shared workspace limited to
synthetic or public non-personal data. Before multiple users submit real
identifiable household facts, require individual identity, per-user
authorisation, scoped persistence and exports, and accepted privacy,
retention and deletion arrangements. Basic Auth does not isolate scenarios.

Recommend adding the verified `web` check to the main ruleset after proving
its name, triggers, reliable execution, a failing-test merge block and absence
of deadlocks on non-web PRs. Preserve the nine current required contexts.
Pete retains actual settings authority; no ruleset edit is made here.

## Initial workload and plan evaluation

The coordinator recommends 3–5 invited analysts, about 100 retained household
scenarios and 20 synthetic population runs for the first demonstration.
These are planning assumptions, not measured capacity or an approved spend.
Measure representative stored payloads/artifacts, retained runs per scenario,
database growth and web-service memory before purchase.

Render's current [compute plans](https://render.com/docs/compute-plans) list
paid `0.1c-256mb` (legacy `basic-256mb`: 0.1 CPU, 256 MB) and `0.5c-1g`
(legacy `basic-1gb`: 0.5 CPU, 1 GB). Evaluate the smallest first; retain the
larger as an option if the measured working set or sustained I/O needs it.
Compute and storage are separately billed; confirm current prices, available
region, backups and budget in the target workspace before creating anything.
[Render connection guidance](https://render.com/docs/postgresql-creating-connecting)
requires the same account and region for private connections.

The existing population calculation lock is per application process. Keep a
single application worker for this initial workload until deployment smoke
verification proves the intended concurrency bound. Do not describe it as a
distributed job queue or an assurance of multi-worker isolation.

## Acceptance evidence and remaining actions

The Render connection is unavailable in the coordinator's tool set; the
Render integration was found but was not installed/connected at the check.
No resources, environment values or actual deployment were inspected or
changed. Workspace, service ID/region, capacity and spend remain unverified.

After #188 and #189 are accepted and merged, use separate bounded B0.1.5
completion, B0.1.6 accessibility/charts and B0.1.7 deployment work. Preserve
implemented pages and backend values. Deployment acceptance must demonstrate:

1. Unauthenticated routes return 401 except the intended health endpoint.
2. Authenticated Home, Scenarios, Models and Data work.
3. A synthetic household or supported reform can be stored and calculated.
4. Stored scenarios/results survive application restart.
5. Scenario/run deep links still resolve after restart and hydration.
6. Displayed amounts equal retained backend amounts in native units/periods.
7. Unsupported and unresolved results remain visibly unavailable.
8. Tests and seeded examples contain no real personal data.

Pete's smallest remaining actions are to approve actual analyst contacts,
identify the existing workspace, approve a measured database plan/budget and
set secrets directly in Render. Ruleset and release-tag decisions remain
explicitly separate. An accepted proposal alone is neither deployment nor
formal Pilot 1 evidence.
