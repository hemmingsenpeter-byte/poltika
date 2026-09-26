# v0.1 acceptance coverage

`test_v0_1_release.py` is the release-level layer over the existing spec,
benchmark, regression, API, installed-artifact and code-replay suites. It adds
five-point statutory money boundaries, generated invariants, metamorphic
cross-policy isolation, explanation equivalence and repeat-run determinism.

`test_orientation_examples.py` runs the two examples in `docs/ORIENTATION.md`
as written and compares their results with the committed demo summary, so
the orientation page fails the build when the contract it shows changes.

The existing suite supplies the remaining local evidence:

- statutory rules and numerical precision: `tests/unit/engines/simulator/`
- independently derived golden and official cases: policy YAML runners
- missing and invalid inputs: calculator and API tests
- temporal selection: policy loader and module-boundary tests
- provenance: `tests/unit/engines/assurance/`
- frozen regression results: `tests/regression/`
- API and schema contracts: `tests/unit/api/`
- installed and historical reproducibility: `tests/installed_artifact/` and
  `tests/code_replay/`

Two suggested assurance mechanisms are not represented as ordinary passing
pytest cases. Cross-engine differential testing needs a separately approved,
pinned reference-engine scope and a classified discrepancy corpus; external
engines are not policy authority. Mutation testing must run a mutation tool
against the whole suite and enforce a reviewed score threshold. Existing
targeted tests kill the mutations found during v0.1 review, but that is not a
substitute for a measured mutation campaign.
