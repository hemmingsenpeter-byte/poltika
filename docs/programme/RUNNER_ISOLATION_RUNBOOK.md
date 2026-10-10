# Runner isolation runbook (PETE_QUEUE Q13)

Status: prepared for Pete, not executed. Nothing here changes the Mac, the
runner service or GitHub settings until Pete does it. Evidence base:
`reviews/2026-10-11-audit-191-verification.md` (finding A1).

## Why

The runner `pete-mac-1` (`[self-hosted, poltika]`, decision D21) runs pull
request code (`uv sync`, `npm ci` lifecycle scripts, pytest) as Pete's own
macOS login user. That code can read anything Pete can: home directory,
`~/.ssh`, keychains, browser data. The repository is private and
collaborator-only, so this is an accepted-by-default exposure, not an
observed breach. Repository controls already in place: every workflow has
`permissions: contents: read`, `persist-credentials: false`, pinned actions,
no `pull_request_target` or `workflow_run`, and (this change) no fork pull
request reaches the runner. None of these isolates the host.

## Target

A dedicated Standard (non-admin) macOS user, `poltika-ci`, owning the runner
and its work directory, with no access to Pete's home. Better still, if the
Actions budget allows later: GitHub-hosted runners or a disposable VM per
job. The steps below are the interim, no-cost option.

## Steps (Pete, at the Mac, between jobs)

1. System Preferences, Users and Groups: create a Standard user `poltika-ci`.
   Do not sign it in to iCloud, a password manager or any personal service.
   Do not add it to the admin group or to Pete's sharing groups.
2. Let the running job finish. As Pete, in `~/actions-runner`:
   `./svc.sh stop`, then `./svc.sh uninstall`. Never run old and new runners
   with the same label at once.
3. Restrict Pete's home from other users: inspect `ls -lde ~` and, if
   compatible with how Pete shares files, `chmod go-rwx ~`. Do not rewrite
   ACLs recursively. Note the previous mode so it can be reversed.
4. Log in as `poltika-ci`. `umask 077`. In GitHub, repository Settings,
   Actions, Runners, New self-hosted runner (macOS): run the displayed
   download and checksum commands in `/Users/poltika-ci/actions-runner`.
   Configure with the same label set `poltika`; use a fresh registration
   token (shown once, never paste it into a session or file).
5. Install the service from that session: `./svc.sh install`,
   `./svc.sh start`, `./svc.sh status`. A login LaunchAgent for that user, not
   a root daemon. Install what the jobs need under that user: Python 3.12
   via uv, Node 20.19 or later, and access to Postgres.app's PostgreSQL 16
   binaries (`/Applications/Postgres.app/...` is world-executable; no data
   directory of Pete's is used because tests start a throwaway server under
   `RUNNER_TEMP`).
6. Remove the old runner registration in GitHub Settings once the new one
   is online and idle.
7. Optional hygiene: a weekly job or manual step deleting
   `/Users/poltika-ci/actions-runner/_work` contents and `~/.npm`, `~/.cache`
   so one run cannot plant files for the next.

## Verify (report pass or fail only; never print file contents)

As Pete, create `~/poltika-ci-denial-probe.txt` (mode 0600, harmless text).
As `poltika-ci`:

```sh
id -Gn            # must not include admin
test ! -r /Users/peterhemmingsen/poltika-ci-denial-probe.txt && echo ok
test ! -x /Users/peterhemmingsen/.ssh && echo ok
test ! -x /Users/peterhemmingsen/Library/Keychains && echo ok
ps -o user= -p "$(pgrep -f Runner.Listener | head -1)"   # poltika-ci
```

Then push a trivial branch change that opens a PR and confirm the required
checks (test, pilot-image, check-protected-paths, check-immutable-snapshots,
source-currency, pip-audit, links, Bandit (python), zizmor (actions),
npm audit) run on the new runner and pass. Delete the probe file.

## Rollback

`./svc.sh uninstall` as `poltika-ci`; reinstall the original runner under
Pete's account from a fresh registration token; restore the recorded mode on
`~`. While no runner is online, required checks queue and PRs cannot merge,
so schedule the cutover when no merge is pending.

## What this does not fix

A persistent runner account still carries state between PR jobs, and
`poltika-ci` still has the repository's `GITHUB_TOKEN` (read-only) during a
run. Fork pull requests are blocked, so the remaining trust boundary is
repository collaborators. Treat any collaborator addition as a runner-trust
decision.
