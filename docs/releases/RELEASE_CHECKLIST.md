# Release checklist

A release is tagged when its steps' validation gates pass
(`BUILD_PLAN_PROGRAMME.md`, "Releases"). Milestones are claimed separately,
on validation evidence. Tagging is Pete's (Tier C, ADR-0020): this checklist
ends with a request to him, not a tag.

Work from a worktree off `origin/main`. Record each result in the release PR.

## 1. Scope

- [ ] The release's steps and their gates are named, from the "Releases"
      table and "Phases, milestones and validation gates".
- [ ] Every step in scope is Done in `PROGRAMME_STATUS.md` (or the
      programme plan if that file is not yet there).

## 2. Checks

- [ ] `make check` passes on the latest `origin/main`.
- [ ] The release-gate acceptance tests pass, with nothing skipped except
      rows the gate names:
      `uv run --extra dev pytest -q tests/acceptance`. The gate tests are
      `test_v0_1_release.py`, `test_v0_1_5_release_gate.py`,
      `test_v0_2_release_gate.py` and `test_v0_3_release_gate.py`. A skip
      names the PRs or phases it waits on. A green run with no skips means
      the gate is met.
- [ ] `pytest -q -m installed_artifact` and `pytest -q -m code_replay` pass.
- [ ] CI is green on the commit to be tagged.

## 3. Review

- [ ] `review_packets/review_queue.md` has no open row in the release's
      scope, or each open row is named in the release notes.
- [ ] No open P1 or P2 finding.

## 4. Documents

- [ ] `CHANGELOG.md`: "Unreleased" is renamed to the release, with its date.
- [ ] A limitations document exists in `docs/releases/` for the release
      (for example `V0_2_LIMITATIONS.md`) and says what the release does not
      do.
- [ ] `docs/ORIENTATION.md` is accurate for the release, and
      `tests/acceptance/test_orientation_examples.py` passes.
- [ ] `REPOSITORY_STRUCTURE.md` lists every new file.

## 5. Milestones

- [ ] A milestone is claimed only on its validation evidence, in its own
      entry. Tagging a release does not claim one.

## 6. Ask Pete to tag

Merge the release PR with `gh pr merge --squash --auto`. Then add an entry
to `PETE_QUEUE.md` with the squash commit. Tagging is Tier C, so do not tag
it yourself. The entry gives Pete this command:

```sh
git fetch origin
git tag -a vX.Y.Z <squash-commit-sha> -m "Poltika vX.Y.Z"
git push origin vX.Y.Z
```

Replace `vX.Y.Z` and `<squash-commit-sha>` with the release and the squash
commit on `main`.
