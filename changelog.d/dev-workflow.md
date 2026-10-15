- Development workflow (decision log D43): one integration owner, at most
  two implementation lanes, `gh stack` for dependent pull requests,
  changelog fragments in `changelog.d/`, CodeRabbit advisory, and one
  review cycle per stable semantic change. ADR-0020's mechanical main
  update now covers a conflict confined to append-only records whose
  resolution is an exact combination of existing, independent entries,
  with no new text, duplicate record IDs or contradictory statuses or
  decisions. Reviewed changes must match with whitespace preserved;
  no-deletion diffs and matching patch IDs alone do not prove equivalence.
  Pete explicitly approved this bounded rule on 16 October 2026.
- CI: `test` runs its suite on parallel workers (`pytest-xdist`); `web` and
  `pilot-image` skip a pull request that changes none of their inputs and
  always run on `main`. Required check names are unchanged. No calculated
  amount changes.
