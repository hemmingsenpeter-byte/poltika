# Changelog

## v0.1.0 (25 September 2026)

Accepted by Pete (BUILD_PLAN.md Task 34.5).

v0.1 is a deterministic foundation: two New Zealand policies modelled from
cited primary sources, a combined household scenario, and provenance.

- Working for Families, 2026-27: family tax credit, minimum family tax
  credit and Best Start calculated inside a scoped domain. The in-work tax
  credit is `needs_review` until its 2026-27 base rate is confirmed (Task
  26b). Protected-credit, shared-care and part-year cases are
  `unsupported`.
- Accommodation Supplement, weekly: published MSD entry thresholds and
  income levels (DEC-002), statutory area caps and the 70% subsidy rate,
  asset imputation, and the non-beneficiary income reduction (DEC-001),
  with r 19 rounding. Homeowners, mixed-benefit couples and NZ
  Superannuation are `unsupported`.
- The WFF and AS interaction: a combined household runner that keeps each
  policy's native period, with no combined total and no income coupling
  (DEC-003). Conservative shared-fact checks downgrade disagreements to
  `needs_review`.
- Every component is `calculated`, `needs_review` or `unsupported`. A
  missing fact never becomes zero.
- Provenance: per-component traces and hash-bound artifacts, and
  per-policy and combined provenance reports that resolve sources, rules
  and decisions.
- Scenarios: canonical scenario and result ids, code identity, and an
  append-only PostgreSQL store (ADR-0013) with replay on retained
  artifacts, including on the retained code revision.
- API (FastAPI): per-policy routes, `/household/calculate`, and stored
  `/scenarios` routes (create, fetch, replay, re-run).
- Tests: spec, benchmark and regression layers, golden households, a
  frozen golden snapshot, an installed-artifact check and code replay, run
  in CI on every PR and push.
- Demo: `docs/demo/v0_1/`.
- Post-review fixes (PR #79; author-reviewed, merged on Pete's acceptance
  without a GPT/Codex audit):
  - storing the same household with its children in another order no longer
    returns 409;
  - each module's checks refuse a `policy.yaml` that changed after its
    parameters were loaded;
  - committed policy-file lookups are cached;
  - the statutory-value guard also lists the golden-results fixture and the
    source, specification and decision files;
  - Python is pinned to 3.12;
  - WFF DEC-001 records when an evidenced eligibility failure is $0 and when
    it is `unsupported`.
- Known limitation: no WFF total. The 2026-27 in-work tax credit base rate
  can be reversed early by Order in Council, so it stays `needs_review`.

## Scaffolding

- Seeded the Poltika repository structure
- Added doctrine, ADR, and policy-spec scaffolding
- Added baseline documentation and initial guardrails
