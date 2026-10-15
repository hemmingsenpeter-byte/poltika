- Development workflow (decision log D43): one integration owner, at most
  two implementation lanes, `gh stack` for dependent pull requests,
  changelog fragments in `changelog.d/`, CodeRabbit advisory, and one
  review cycle per stable semantic change. ADR-0020's mechanical main
  update now covers a conflict confined to append-only records whose
  resolution keeps every line of both sides.
- CI: `test` runs its suite on parallel workers (`pytest-xdist`); `web` and
  `pilot-image` skip a pull request that changes none of their inputs and
  always run on `main`. Required check names are unchanged. No calculated
  amount changes.
