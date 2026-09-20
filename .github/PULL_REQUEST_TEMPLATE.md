## Handoff

- Build-plan task:
- Author (GPT or Claude Code):
- Requested reviewer (the other model):
- Pete's review request or approval:

## Reviewer inputs

- Primary sources and source-map paths:
- Policy specification or schema paths:
- Test command and result (or `not applicable`):
- Diff: this PR

## Gate

- [ ] The PR contains one bounded task or review handoff.
- [ ] The reviewer has the sources, spec, diff, and tests needed for an independent pass.
- [ ] No implementer explanation or proposed expected behaviour is included above.
- [ ] Any genuine interpretation ambiguity is reserved for Pete and a decision artifact.

The reviewer records findings before reading the author's rationale. Use
`review_packets/TEMPLATE.md` for the review record. Pete chooses when to request
the review and whether to accept the result; opening a PR does not automate
the next BUILD_PLAN task.
