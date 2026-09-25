# v0.1.0 baseline

v0.1.5 Task 0.4. Measured on 25 September 2026 at the `v0.1.0` release
commit, `e41871d`, in a clean worktree, with Python 3.12.3 and a throwaway
PostgreSQL 16.

v0.1.5 must reproduce every v0.1 result unless a reviewed statutory
correction changes it. The golden snapshot
(`tests/fixtures/golden_results_v0_1.json`) and the protected spec and
benchmark files are what "reproduce" is checked against.

## Tests

| Measure | v0.1.0 |
| --- | --- |
| Default suite (`pytest -q`, PostgreSQL available) | 429 passed, 0 failed |
| Installed-artifact and code-replay tests (opt-in) | 1 and 1 passed |
| Statement coverage of `src/poltika` (`--cov=poltika`) | 95% (1,781 statements, 87 missed) |

The two migration modules show 0% coverage because Alembic loads them from
files, which coverage does not attribute. They run in every PostgreSQL test.

## Protected cases

| File | Cases |
| --- | --- |
| `working_for_families/spec_cases.yaml` | 23 |
| `working_for_families/benchmarks.yaml` | 9 |
| `accommodation_supplement/spec_cases.yaml` | 26 |
| `accommodation_supplement/benchmarks.yaml` | 4 |
| `wff_as_interaction/spec_cases.yaml` | 5 |
| `wff_as_interaction/golden_households.yaml` | 9 |

## Policy files at v0.1.0 (SHA-256)

| File | SHA-256 |
| --- | --- |
| `accommodation_supplement/decisions/DEC-001-income-excess-rounding.md` | `36974df5ca3de1b28a83284fd55a62cb482a02f176737b3285b3b0786b8aa7e0` |
| `accommodation_supplement/decisions/DEC-002-published-thresholds-and-rate-scope.md` | `5086c2fe0aed7433050be354d119f1094bfb240fb1aafe67b3121e961dd3d146` |
| `accommodation_supplement/decisions/DEC-003-msd-paid-wff-income-exclusion.md` | `8ecb738044afef3b046c581c52b13c6d10719380dce700f12c2223ec8a55c8e2` |
| `accommodation_supplement/policy.yaml` | `d46078bc9ab3cb6babdd304b752de9cc3cec3a2d304c3e6b09fd0bb45ecac180` |
| `accommodation_supplement/sources.yaml` | `1063aea45898c771f2bf7af4db0830972288f74618914936c4dd66918a3256e2` |
| `accommodation_supplement/specification.md` | `8e4227c458c2aabd1c9e5aa35ee25dd5b65c20fff2c43b0e1966f1d044948c83` |
| `working_for_families/decisions/DEC-001-evidenced-ineligibility-outcome.md` | `dac88e829868c78c603caf7c5e311ea1dab3230f041dfed252ef6e02ca9ff47b` |
| `working_for_families/policy.yaml` | `7f83084d52b37e0df1c19ef7e0d7232d2dbe2b56b5f9ef65eb837a2340c47745` |
| `working_for_families/sources.yaml` | `7775f9135c8b76e528f4d850518a1083e9c5c4a3e88af46f51e43742085995b3` |
| `working_for_families/specification.md` | `9a9e1283c2c741d32dbaa7553ddcbfa88809678e4d3fb415ae689d75aafd61b8` |

## Reproducing it

```sh
git worktree add ../poltika-v0.1.0 e41871d
cd ../poltika-v0.1.0
uv sync --locked --extra dev
uv run --extra dev --with pytest-cov pytest -q --cov=poltika
```
