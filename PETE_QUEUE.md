# Pete's queue

The open Tier C items (ADR-0020): the decisions and actions only Pete can
take. Each says what it blocks and the smallest action that clears it.
Work routes around every item here. When one is done, Pete (or the session
that records his answer) moves it to "Done" with the date and the PR or
commit that records it.

## Open

| # | Item | Blocks | Smallest action |
| --- | --- | --- | --- |
| Q1 | Activate the `main` ruleset and squash-only auto-merge (ADR-0020, "The ruleset on main"). Changing repository settings was denied to the session. | Mechanical enforcement of the merge rules; `gh pr merge --auto`. Merges continue by agreement meanwhile. | Run the two commands under "Q1 commands" below from a shell logged in as the repository owner. |
| Q2 | Task 1.4: Māori data governance, privacy and security. Engaging people with standing in Māori data governance (P5's process). | Step 1's validation gate; any output about Māori; microdata (Steps 7, 19). The interim rule (P5) holds meanwhile. | Name who you will engage, or say to proceed with GPT/Codex's source research first. |
| Q3 | IDI access (P12): lodging the application. | Step 7's IDI-calibrated grade; Step 19. | Lodge it once W3.1 documents the route. |
| Q4 | Open programme decisions P6, P7, P8, P13, P14, P18, P20. | Nothing in Phase 0. P7 blocks Step 6.4-6.5; P13 Step 16; P14 Step 23; P18 each milestone; P20 Step 15; P6 Step 5.5; P8 the first product. | None yet. Each is raised again, with options, when its step starts. |
| Q6 | `.claude/skills/pr-review/SKILL.md` (lines 3, 11) and `.claude/skills/pr-review-preflight/SKILL.md` (line 106) still say Pete is the acceptance judge for every PR. Editing Claude Code's own skill files was outside the session's permissions. | Nothing: ADR-0020, CLAUDE.md and the doctrines govern. A session reading only a skill could think every merge waits for Pete. | Add one line to each: "Acceptance follows ADR-0020: Claude Code accepts Tier A and B work; Pete decides Tier C." Or allow a session to make that edit. |
| Q5 | v0.3 D1-D3: each Tier 1 domain's supported slice, the disposable-income definition and the income-adequacy measures. | v0.3 Phases 2-5 implementation (Step 3A). | Decide once GPT/Codex's Phase 0 sourcing is in. |

### Q1 commands

```sh
gh api -X PATCH repos/hemmingsenpeter-byte/poltika \
  -F allow_auto_merge=true -F delete_branch_on_merge=true \
  -F allow_merge_commit=false -F allow_rebase_merge=false -F allow_squash_merge=true

gh api -X POST repos/hemmingsenpeter-byte/poltika/rulesets --input - <<'JSON'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "bypass_actors": [],
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false,
      "allowed_merge_methods": ["squash"]}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "do_not_enforce_on_create": false,
      "required_status_checks": [
        {"context": "test"},
        {"context": "pilot-image"},
        {"context": "check-protected-paths"},
        {"context": "check-immutable-snapshots"}
      ]}}
  ]
}
JSON
```

The required checks are the CI jobs that run on pull requests today. Each
new CI job is added to the list when its PR merges (`docs/decision_log.md`
records which), so after the first run the session can only propose the
updated list here; it cannot apply it.

## Done

None yet.
