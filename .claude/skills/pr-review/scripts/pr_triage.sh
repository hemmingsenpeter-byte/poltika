#!/usr/bin/env bash
# Pin a Poltika pull request and print what a reviewer needs before reading
# any code: exact SHAs, commits and their authorship trailers, changed files
# by risk tier, protected-value and snapshot changes, diff size, and the
# review-debt count. Read-only apart from fetching two refs.
#
# Usage: pr_triage.sh <PR number> [base branch, default main]
#
# The diff runs from the PR's fork point. For a merged PR that is the first
# parent of its merge commit on the base branch, found automatically. After a
# squash or fast-forward merge, set BASE_SHA to the base.sha GitHub recorded
# for the PR (pull_request_read, method get).
set -euo pipefail

pr="${1:-}"
base="${2:-main}"
case "$pr" in
  '' | *[!0-9]*) echo "usage: pr_triage.sh <PR number> [base branch, default main]" >&2; exit 2 ;;
esac

cd "$(git rev-parse --show-toplevel)"
git fetch --quiet origin \
  "+refs/heads/$base:refs/remotes/origin/$base" \
  "+refs/pull/$pr/head:refs/remotes/origin/pr/$pr"

head=$(git rev-parse "origin/pr/$pr")
tip=$(git rev-parse "origin/$base")

section() { printf '\n## %s\n' "$1"; }

echo "# PR #$pr triage"
echo "head        $head"
echo "base        $base at $tip"

merged=""
if git merge-base --is-ancestor "$head" "$tip"; then
  # The merge commit is the oldest merge on the base whose second parent is
  # the head. Its first parent is the base the PR merged into.
  for m in $(git rev-list --reverse --merges --ancestry-path "$head..$tip"); do
    if [ "$(git rev-parse "$m^2")" = "$head" ]; then
      merged="$m"
      break
    fi
  done
  echo "state       merged into $base${merged:+ by $(git rev-parse --short "$merged")}: review it as merged work (fixes go in a new PR)"
fi

if [ -n "${BASE_SHA:-}" ]; then
  mb=$(git merge-base "$BASE_SHA" "$head")
  echo "fork point  $mb (from BASE_SHA)"
elif [ -n "$merged" ]; then
  mb=$(git merge-base "$merged^1" "$head")
  echo "fork point  $mb (merge-base with the merge commit's first parent)"
else
  mb=$(git merge-base "$tip" "$head")
  echo "fork point  $mb (merge-base with $base)"
  if [ "$mb" = "$head" ]; then
    echo "            The head is already in $base with no merge commit, so the diff is empty."
    echo "            Rerun with BASE_SHA=<the PR's base.sha from GitHub>."
  fi
fi
if [ -z "$merged" ]; then
  echo "behind      $(git rev-list --count "$mb..$tip") commit(s) on $base since the fork point"
fi
echo "diff        git diff $mb...$head"

section "Commits, oldest first"
# The git author name is not a reliable signal here: both models' commits can
# carry the same automation name. Claude Code commits carry a
# Co-Authored-By: Claude trailer; confirm the rest against the PR's Handoff.
total=0
claude=0
while read -r sha; do
  total=$((total + 1))
  subject=$(git show -s --format=%s "$sha")
  if [ "$(git rev-list --no-walk --count --merges "$sha")" = 1 ]; then
    printf '%s  [merge]  %s\n' "$(git rev-parse --short "$sha")" "$subject"
    continue
  fi
  # Captured first: grep -q exits at its first match, which can fail the
  # writer of a pipe under pipefail.
  message=$(git show -s --format=%B "$sha")
  if grep -qiE '^(Co-Authored-By: Claude|Claude-Session:)' <<< "$message"; then
    claude=$((claude + 1))
    tag="claude"
  else
    tag="no claude trailer"
  fi
  printf '%s  [%s]  %s\n' "$(git rev-parse --short "$sha")" "$tag" "$subject"
done < <(git rev-list --reverse "$mb..$head")
echo "$claude of $total commit(s) carry a Claude trailer (merge commits count as neither)."

tier() {
  case "$1" in
    policy_specs/*/policy.yaml | policy_specs/*/spec_cases.yaml | policy_specs/*/benchmarks.yaml | \
      policy_specs/*/golden_households.yaml | tests/fixtures/golden_*.json)
      echo "1 PROTECTED statutory values: full review + test-doctrine process" ;;
    policy_specs/*/sources.yaml | policy_specs/*/specification.md | policy_specs/*/decisions/* | \
      policy_specs/*/facts.yaml | policy_specs/SCHEMA.md)
      echo "2 INTERPRETATION: full review against primary sources" ;;
    data/raw/* | data/metadata/*)
      echo "3 DATA snapshots and metadata: provenance skill; raw snapshots are immutable" ;;
    src/poltika/engines/* | src/poltika/policy/* | src/poltika/data/* | src/poltika/semantics/* | \
      src/poltika/common/*)
      echo "4 SHARED CODE (engine, loader, data boundary): full review" ;;
    src/* | pyproject.toml | Dockerfile | compose.yaml | deploy/*)
      echo "5 OTHER CODE and packaging: full review" ;;
    doctrine/* | adr/* | BUILD_PLAN*.md | ROADMAP*.md | ARCHITECTURE.md | REPOSITORY_STRUCTURE.md | \
      CLAUDE.md | .github/* | .claude/* | .agents/*)
      echo "6 PROCESS, architecture, doctrine, CI: frozen doctrine and accepted ADRs change only by decision" ;;
    tests/*)
      echo "7 TESTS: light check unless they add statutory expected values" ;;
    uv.lock)
      echo "8 GENERATED" ;;
    *)
      echo "9 DOCS and other: light check; are ORIENTATION.md and CLAUDE.md still true?" ;;
  esac
}

section "Changed files by risk tier (status, +added -deleted, path)"
# Both lists come out in the same path order, so they pair line by line.
paste <(git diff --name-status --no-renames "$mb" "$head") \
  <(git diff --numstat --no-renames "$mb" "$head") |
  while IFS=$'\t' read -r status path added deleted _; do
    if [ "$added" = "-" ]; then size="binary"; else size="+$added -$deleted"; fi
    printf '%s\t%s\t%s\t%s\n' "$(tier "$path")" "$status" "$size" "$path"
  done | sort -t$'\t' -k1,1n -k4,4 |
  awk -F'\t' '$1 != last { print "\n" substr($1, 3); last = $1 } { print "  " $2 "  " $3 "  " $4 }'

section "Size"
git diff --shortstat "$mb" "$head" | sed 's/^ */all files: /'
git diff --shortstat "$mb" "$head" -- . ':(exclude)uv.lock' ':(exclude)tests/fixtures/golden_*.json' \
  ':(exclude)data/raw/' | sed 's/^ */excluding generated and snapshots: /'

section "Guards (the CI checks compute the same lists)"
protected=$(git diff --name-only "$mb" "$head" -- \
  'policy_specs/*/benchmarks.yaml' 'policy_specs/*/spec_cases.yaml' \
  'policy_specs/*/golden_households.yaml' 'policy_specs/*/policy.yaml' 'tests/fixtures/golden_*.json')
if [ -n "$protected" ]; then
  echo "Statutory Value Guard would list (visibility only, never red):"
  echo "$protected" | sed 's/^/  /'
else
  echo "No protected statutory-value files changed."
fi
snapshots=$(git diff --name-status --no-renames --diff-filter=MDT "$mb" "$head" -- \
  'data/raw/' 'data/metadata/datasets/' \
  ':(exclude)data/raw/README.md' ':(exclude)data/metadata/datasets/README.md')
if [ -n "$snapshots" ]; then
  echo "Data Snapshot Guard FAILS: committed snapshots edited, deleted or retyped:"
  echo "$snapshots" | sed 's/^/  /'
else
  echo "No committed data snapshot edited or deleted."
fi
whitespace=$(git diff --check "$mb" "$head" || true)
if [ -n "$whitespace" ]; then
  echo "git diff --check reports whitespace errors (first 20 lines):"
  printf '%s\n' "$whitespace" | sed -n '1,20s/^/  /p'
fi

section "Review queue on $base (review_packets/review_queue.md)"
queue=$(git show "origin/$base:review_packets/review_queue.md" 2> /dev/null || true)
if [ -z "$queue" ]; then
  echo "No review queue on $base."
else
  open_rows=$(printf '%s\n' "$queue" |
    awk -F'|' 'NF == 8 && /^\|[[:space:]]*#[0-9]+[[:space:]]*\|/ {
      status = $(NF - 1); gsub(/^[[:space:]]+|[[:space:]]+$/, "", status)
      pr = $2; gsub(/[[:space:]]/, "", pr)
      if (status !~ /^reviewed/) printf "%s ", pr }')
  open_rows="${open_rows% }"
  count=$(printf '%s' "$open_rows" | wc -w)
  echo "Open implementation rows: $count${open_rows:+ ($open_rows)}"
  doctrine=$(git show "origin/$base:doctrine/development-doctrine.md" 2> /dev/null || true)
  if grep -qF 'Review debt is recorded but not capped.' <<< "$doctrine"; then
    echo "Review-debt cap is suspended; open rows do not stop merges."
  elif [ "$count" -ge 5 ]; then
    echo "At or over the cap of five: no implementation PR merges until the queue is below five."
  fi
  row=$(printf '%s\n' "$queue" | grep -E "^\|[[:space:]]*#$pr[[:space:]]*\|" || true)
  if [ -n "$row" ]; then
    echo "This PR's row: $row"
  fi
fi

section "Next"
echo "git worktree add --detach <scratchpad>/pr-$pr $head"
