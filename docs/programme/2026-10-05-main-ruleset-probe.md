# Main ruleset negative probe — 5 October 2026

## Fixed artifact and observation

The deliberate failing-check PR was
[#168](https://github.com/hemmingsenpeter-byte/poltika/pull/168), at immutable
head `fb92c17f6d9e90f081e6d3cec778a6bb23030513`. It was closed without an
attempt to merge; the failing change never entered main.

The session recorded `mergeStateStatus=BLOCKED` while the PR was open,
with required `test` failing intentionally at Ruff and all eight other
required jobs passing. The contemporaneous record is
[this PR comment](https://github.com/hemmingsenpeter-byte/poltika/pull/168#issuecomment-5988329364).
Readback on 6 October confirmed the same immutable head and check results
below. The closed PR now reports `BEHIND` as main has advanced; readback
cannot independently reconstruct its earlier transient merge state. The
BLOCKED assertion is the contemporaneous observation, not a claimed new
observation or a test of a rejected merge request.

## Retained required-check results

| Required check | Result | Immutable run/job evidence |
| --- | --- | --- |
| test | FAILURE | [Tests job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131923/job/111620224793) |
| pilot-image | SUCCESS | [Pilot image job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131923/job/111620225021) |
| check-protected-paths | SUCCESS | [Statutory guard job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131913/job/111620224417) |
| check-immutable-snapshots | SUCCESS | [Data guard job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131903/job/111620224768) |
| links | SUCCESS | [Offline links job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131873/job/111620224418) |
| pip-audit | SUCCESS | [Security job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131899/job/111620224467) |
| source-currency | SUCCESS | [Currency job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131892/job/111620224398) |
| Bandit (python) | SUCCESS | [Bandit job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131894/job/111620224624) |
| zizmor (actions) | SUCCESS | [Zizmor job](https://github.com/hemmingsenpeter-byte/poltika/actions/runs/37265131894/job/111620224804) |

The schedule-only `external-links (report only)` and `publish-issue` jobs
were skipped and were not required checks. Readback used
`gh pr view 168 --repo hemmingsenpeter-byte/poltika --json headRefOid,state,statusCheckRollup,mergeStateStatus`.

The active ruleset supersedes ADR-0007's historical platform limitation.
The statutory-value guard reports protected-path changes; a successful guard
run does not approve statutory values, interpretation or Tier C decisions.
