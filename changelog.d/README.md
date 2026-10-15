# Changelog fragments

Each pull request adds one fragment here instead of editing
[CHANGELOG.md](../CHANGELOG.md), so two open pull requests never conflict
over the changelog (decision log D43).

- Name it after the change: `changelog.d/<short-topic>.md`, for example
  `changelog.d/household-runs.md`. One file per pull request; amend it in
  the same pull request.
- Write the bullets as they should read in `CHANGELOG.md`: what changed for
  a reader, the decision-log or queue reference, and whether any calculated
  amount changed. Name paths in backticks rather than linking them, because
  the text moves to the repository root when folded.
- Only the integration owner (`doctrine/development-doctrine.md`,
  "Integration and lanes") folds fragments into `CHANGELOG.md`, in a commit
  of its own that deletes the folded files.
