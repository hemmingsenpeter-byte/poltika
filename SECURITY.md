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

Report it privately. Do not open a public issue.

1. Use GitHub private vulnerability reporting: the "Security" tab of the
   repository, then "Report a vulnerability".
2. If that is not available to you, send a private message to the
   repository owner, `@hemmingsenpeter-byte`, on GitHub.

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

The baseline, each added by its own PR:

- Dependabot: dependency update PRs.
- pip-audit: known vulnerabilities in Python dependencies.
- CodeQL: static analysis of the code.
- gitleaks: secrets in commits.

These help. They do not replace a private report.
