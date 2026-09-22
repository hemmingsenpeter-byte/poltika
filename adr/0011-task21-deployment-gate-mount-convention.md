# ADR-0011: Task 21 deployment gate — `policy_specs/` as a deploy-time mount, not package data

**Date:** 23 September 2026
**Status:** accepted

## Context

PR #22's review (Task 21) confirmed, by actually building a wheel and
inspecting its contents, that `policy_specs/` is absent from it --
`pyproject.toml`'s `[tool.setuptools.packages.find]` only packages `src/`,
and `policy_specs/` lives at the repo root, outside `src/poltika/`. A
normally `pip install`-ed deployment of the API would therefore fail to
locate `policy.yaml` at all. Pete accepted PR #22 scoped explicitly to a
source-checkout deployment and recorded a future gate requiring an
explicit packaging/deployment decision, plus an installed-artifact test
proving the API works outside a source checkout, before either WFF's or a
later Accommodation Supplement API could be presented as deployable
beyond one.

Three approaches were on the table:

1. **Embed `policy_specs/` under `src/poltika/`** so setuptools' ordinary
   package-data mechanism includes it in the wheel automatically.
2. **Package `policy_specs/` as a separate, independently-versioned
   distribution artifact**, installed alongside the API package.
3. **Treat `policy_specs/` as deploy-time configuration**, supplied by
   whoever runs the installed artifact (an environment variable or a
   volume/directory mount), never baked into the wheel at all.

## Decision

Option 3. `policy_specs/` is deploy-time configuration, not package data.
The WFF API route resolves its policy directory via
`poltika.api.wff._wff_policy_dir()`: if the `POLTIKA_POLICY_SPECS_DIR`
environment variable is set, WFF's directory is `<that path>/
working_for_families`; otherwise it falls back to the source-checkout-
relative path Task 21 originally used, so local development and every
existing deployment are unaffected by default.

Task 21's `_lifespan` startup check (fail loudly and immediately if the
resolved directory has no `policy.yaml`) is unchanged -- only what feeds
`WFF_POLICY_DIR` changed, not the safety net around it.

An installed-artifact test (`tests/installed_artifact/
test_installed_artifact.py`, marked `installed_artifact` and excluded
from the default fast suite per `pyproject.toml`'s `addopts`) builds the
real wheel, installs it into a throwaway venv with no source checkout on
`sys.path`, sets `POLTIKA_POLICY_SPECS_DIR`, and confirms `/wff/calculate`
actually serves a request successfully end-to-end -- not merely that the
startup check fails cleanly when the variable is unset (already covered
by a unit test).

## Rationale

Option 1 (embed under `src/`) was rejected: at the time of this decision,
12+ Python files and three CI glob patterns (`statutory-value-guard.yml`)
already reference `policy_specs/` at its repo-root path, and
`REPOSITORY_STRUCTURE.md`'s whole documented tree treats it as top-level
content alongside `doctrine/`, `adr/`, and `review_packets/` -- parallel
to, not nested inside, `src/`. Moving it would be a large, disruptive,
repo-wide change for a packaging concern, and would blur the existing
distinction between `policy_specs/` (reviewed, independently-versioned
policy content, governed by its own ADR/decision-artifact workflow) and
`src/` (code).

Option 2 (separate distribution artifact) was not chosen for now: it adds
real complexity (two build/publish artifacts, a version-coordination
relationship between them) the project doesn't need at this stage, though
it remains a reasonable future evolution if `policy_specs/` versioning
needs to become fully independent of code releases.

Option 3 fits the project's own established architecture most directly:
the Data Acquisition Doctrine already treats `data/`'s raw snapshots as
external to the code package, supplied and versioned separately, never
baked into `src/`. `policy_specs/` -- reviewed, ADR/decision-governed
content that changes on a different cadence than code -- fits the same
pattern. It required zero file moves and zero changes to any of the 12+
existing references, satisfying the same "narrow, additive" discipline
already applied to the Task 23 schema extension.

## Consequences

- Deployments outside a source checkout must set `POLTIKA_POLICY_SPECS_DIR`
  and ensure `policy_specs/` is present at that path (e.g. a Docker volume
  mount, a config-management step, or a sidecar container) -- an
  operational requirement, not a code change, and one the existing
  `_lifespan` startup check already surfaces loudly if missed.
- Local development, CI, and every existing test are unaffected -- the
  environment variable is optional.
- A future Accommodation Supplement API route should follow the same
  `_wff_policy_dir()`-style pattern (an `_as_policy_dir()` reading the
  same `POLTIKA_POLICY_SPECS_DIR` variable), not invent a second
  packaging convention.
- If `policy_specs/` versioning ever needs to be fully decoupled from code
  releases (Option 2's benefit), that remains a valid future evolution
  layered on top of this decision, not blocked by it.
