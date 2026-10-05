# Security policy

## In scope

- The API (`src/poltika/api/`) and its request handling.
- The hosted pilot (`docs/pilot/HOSTING.md`), including its password.
- CI: the workflows under `.github/workflows/`.
- Dependencies (`pyproject.toml`, `uv.lock`).
- Secrets: any credential, key or connection string in the repository,
  its history or its CI.

A wrong calculated result is not a security issue. Open a "Bug or wrong
result" issue for it.

## Report a vulnerability

The repository is currently private. Collaborators can use the
[Security report issue form](https://github.com/hemmingsenpeter-byte/poltika/issues/new?template=security_report.yml).
Reports are visible to everyone with repository access, not only the owner.
Address the report to `@hemmingsenpeter-byte`; include a minimal description
and ask for an existing confidential channel if access-sensitive details
need narrower disclosure. Never paste credentials, personal data or unit records.

Someone without repository access should use an existing private channel
to the owner. No external confidential inbox is configured by this PR.
Before making the repository or product public, Pete must configure and
verify the external confidential reporting route under ADR-0020's Tier C
publication gate. GitHub's private vulnerability reporting is an option
for public repositories when enabled; it is not the current private-repo route.

Say what you found, how to reproduce it and what it could expose. You will
get an acknowledgement. Please give us time to fix it before you tell
anyone else.

## What not to do

- Do not put personal data, unit-record data or microdata in an issue, a
  PR, a comment or a report. Poltika commits no unit records, and its
  privacy rules are set out in the programme plan
  (`BUILD_PLAN_PROGRAMME.md`, Privacy and security). Describe the shape of
  the data instead.
- Do not paste a secret. Say where it is, and rotate it.
- Do not test against the hosted pilot beyond what is needed to show the
  problem, and do not try to read other people's data.

## Supported versions

`main` only. There are no maintained release branches. A fix lands on
`main`.

## Automated checks

The professional baseline (`PROGRAMME_STATUS.md`). Each runs in CI; the job names below are what
GitHub reports:

- Dependabot: weekly dependency update PRs (`uv` and GitHub Actions).
- `pip-audit`: known vulnerabilities in the locked Python dependencies, on
  pull requests, `main` and weekly.
- `Bandit (python)`: static analysis of `src/`. High-severity findings fail
  the check; every finding is retained in the `bandit-report` artifact.
- `zizmor (actions)`: static analysis of the workflows under
  `.github/workflows/`. Any finding fails the check.
- `links`: offline check of relative Markdown links and anchors.
- `source-currency`: reports sources due for re-check. It runs weekly and on pull requests,
  and never fails a PR for something being due.

CodeQL is not used on this private repository. No secrets scanner has been
added. Do not infer that secret detection is covered by the checks above.

These help. They do not replace a private report.
