# Implementation Plan: Back up each clone's unlanded work to a GitHub branch

**Spec**: `specs/321-clone-backup-branches/spec.md` | **Created**: 2026-10-04

## Summary

`sync-with-main.sh done` (and `push`, the same stop-work step without the render) ends with one backup step that runs
whatever the push did - landed, refused, or died partway: it fetches `origin`, then pushes the clone's HEAD fast-forward to
`refs/heads/backup/<clone-name>` when HEAD holds commits `origin/main` lacks, or deletes that branch once its tip is in
`origin/main`; then it sweeps every other `backup/*` branch whose tip is contained in `origin/main`. Nothing in the step can
change the stop's exit code or block it. The two guards gain test cases pinning the backup push and its delete as
permitted, and the guard rows say the branches exist.

## Technical Context

- Tooling only: `scripts/sync-with-main.sh` (bash, git), its companion `scripts/test-sync-with-main.sh` (the bare-remote
  fixture it already builds), `scripts/test-no-branch-hooks.sh`, `scripts/test_hooks_cases.py` (the repo-safety cases),
  the root `CLAUDE.md` and `docs/guards.md`. No engine module (`l7r/**`) changes, so the delta takes the DIRECT route; no
  map changes, so no bookends and no review occasion.
- Measured before planning (2026-10-04): a clone's `origin` fetch refspec is git's default `+refs/heads/*:refs/remotes/origin/*`,
  so every `git fetch origin` already brings any `backup/*` tip into `refs/remotes/origin/backup/*` - the tip's objects are
  local when containment is judged. `push.followTags` is unset. Neither guard refuses `git push origin
  HEAD:refs/heads/backup/x` or `git push origin --delete backup/x` today (read in `no-branch-hooks.sh`, which matches
  branch creation verbs only, and `repo-safety-hooks.sh`, which matches force flags).

## Decisions

**D1 - Where the step runs: an EXIT trap set by `done` and `push`.** `push_cmd` ends in a dozen ways - `die`, `exit 1`
from a gate, the open-task refusal's `exit 1`, the overlap `exit 3`, success - and many of its lines rely on `set -e`.
Running it as `( push_cmd ) || rc=$?` would switch `set -e` off inside it (bash ignores `-e` in a `||` context), so a
failed `flock ... git push` would fall through silently. An EXIT trap keeps `push_cmd` exactly as it is and still runs on
every one of those exits: `trap 'backup_on_exit $?' EXIT`, set only in the `done` and `push` arms of the dispatch. The trap
runs the step with `set +e` and exits with the code it was given, so the outcome is unchanged (FR-006). `push` is included
because it is the same stop-work step (`done` is `push` then render-sync); `sync-in`, `render-sync` and the runner never set
the trap (FR-002). The one-line notes the step prints go after the push's own output, so the refusal text is unchanged.

**D2 - The step, in order** (`backup_step`, never fatal):

1. `git fetch -q --prune origin`. On failure: one line `backup NOT checked - cannot reach origin: <git's last line>` and
   stop (FR-006). `--prune` keeps the clone's `refs/remotes/origin/backup/*` tracking refs in step with the remote, so a
   deleted backup is not judged again.
2. Own branch, `B=backup/<basename of the clone>`, tip `T` (from `refs/remotes/origin/$B`, or none):
   - HEAD contained in `origin/main` (landed, or nothing new): no push. If `T` exists and is contained in `origin/main`,
     delete it (FR-008). If `T` exists and is NOT contained, keep it and say so in one line (the edge case: never deleted).
   - else `T` = HEAD: nothing (already backed up, SC-002).
   - else `T` exists and is not an ancestor of HEAD: the FR-003 message (D4); nothing pushed.
   - else `git push --no-follow-tags origin HEAD:refs/heads/$B` - no `--force`, no `+`, so git itself refuses anything but
     a fast-forward (FR-003, FR-004, FR-007). On success one line naming the branch and the commit; on failure one line
     `backup NOT pushed: <git's last line>` (FR-006).
3. The sweep (D3).

**D3 - The sweep runs at the stop-work step, from the same fetch** (FR-009, the plan decision the spec leaves open).
Every `refs/remotes/origin/backup/*` other than the clone's own whose tip is an ancestor of `origin/main` is deleted. Chosen
over `sync-in` once a day, `make idle-tests` and a target of its own because the fetch it needs has already been made, so it
costs a `for-each-ref` and, only when something is contained, one push; and it runs on the GM's own occasion ("any time we
are finishing work"), so an abandoned clone's branch goes at the next stop of any session, without a timer file or a
command nobody runs. A failed delete is one line and changes nothing (FR-006).

**D4 - The deletes are conditional on the tip judged.** A delete is `git push --force-with-lease=refs/heads/<b>:<T> origin
:refs/heads/<b>`: git deletes the branch only if the remote still holds the tip `T` that was judged contained, so a session
that pushed a newer backup between the fetch and the delete keeps it. This is the lease's compare-and-delete, the only
conditional delete git offers; it overwrites nothing and deletes only a tip already in `origin/main` (FR-008, FR-009, the
edge case). The backup PUSH carries no lease and no force (FR-003). The script's own commands are not seen by the session
guards; the guard cases (D6) pin the plain forms a person would type.

**D5 - The diverged message (FR-003).** Two lines on stderr:

```
sync-with-main: this clone's HEAD is NOT backed up - backup/<name> on GitHub holds commits HEAD lacks (a clone rebuilt under this name?); nothing was forced. The command below merges that backup's commits into this clone's HEAD, so they land on main with this clone's work - it is the GM's decision, never run by a session unasked:
  git -C <clone> fetch origin refs/heads/backup/<name> && git -C <clone> merge --no-edit FETCH_HEAD && git -C <clone> push origin HEAD:refs/heads/backup/<name>
```

No delete and no force anywhere in it; running it leaves a backup holding both the old tip and HEAD (SC-003).

**D6 - The guards** (FR-005): no guard changes. `test-no-branch-hooks.sh` gains `expect_allow` for `git push origin
HEAD:refs/heads/backup/diagram-x`, `git push origin --delete backup/diagram-x` and `git push origin
:refs/heads/backup/diagram-x`; `test_hooks_cases.py`'s repo-safety table gains the same three as `ok`.

**D7 - The doctrine** (FR-010): the `no-branch-hooks.sh` row of the root `CLAUDE.md` guard table and its entry in
`docs/guards.md` say that remote-only `backup/<clone-name>` branches exist, that `sync-with-main.sh` pushes them at every
stop and deletes them once contained in main (its own at landing, others by the sweep), and that they are not local
branches. `docs/session-clones.md`'s stop-work section gains one sentence pointing at the same.

**D8 - Tests** in `scripts/test-sync-with-main.sh`, on its existing bare-remote topology (the clone's `origin` is the bare
`github.git`):

| case | asserts | SC |
|---|---|---|
| refused `done` (open tasks) | remote `backup/c` = HEAD; refusal text still present and rc 1; clone's `refs/heads` is `main` alone; remote's refs are `main` + `backup/c` | SC-001 |
| `sync-in` after it, with a new commit | no backup ref moved | SC-001 |
| second refused `done`, nothing new | no push (the bare remote's reflog for `backup/c` has one entry; the "backed up" line absent) | SC-002 |
| diverged backup | remote tip unchanged; message says NOT backed up and that the command merges the backup's commits so they land on main; the command has fetch, merge, push and no `--force`/`+`/`--delete`; running it leaves a backup containing both tips | SC-003 |
| unreachable remote / rejecting remote | a `pre-receive` hook refusing `backup/*` and an origin URL removed after the push step: `done`'s rc as without the backup, one line naming the failure | SC-004 |
| landing | a clone with a backup lands (DIRECT, finished feature): `backup/c` gone | SC-006 |
| sweep | `backup/old` contained in main and `backup/ahead` not: after a stop, exactly `backup/old` gone | SC-006 |

The guard cases are SC-005; the doc rows SC-007, checked by grep in the test task.

## Constitution Check

- I, II: N/A - no UI in this repository.
- III, VII, VIII, IX: N/A - no pool content, no in-world writing.
- IV, V: PASS - no SOURCE blocks, no README.
- VI: PASS - each task names its verification; `make hooks-test` and `make done` at the end.
- X: PASS - bash only; no Python file changes beyond a table in `test_hooks_cases.py`. The coverage floor is over `l7r`
  and does not change.
- XII: N/A for rendering - nothing a map draws or states changes.
- XIII: PASS - the baseline is `make hooks-test` in a detached worktree; the existing `test-sync-with-main.sh` cases stay
  green, with the step now running at the end of each of their `push` calls against the fixture remote.
- XVI: PASS - every FR is built as written; D1's `push` arm is the same stop-work step, not an exception.

## Project Structure

```
scripts/sync-with-main.sh            backup_step, backup_sweep, backup_on_exit; the trap in the done and push arms
scripts/test-sync-with-main.sh       the D8 cases
scripts/test-no-branch-hooks.sh      three expect_allow cases
scripts/test_hooks_cases.py          three repo-safety ok cases
CLAUDE.md, docs/guards.md            the no-branch rows
docs/session-clones.md               one sentence in the stop-work section
```

## Complexity Tracking

None.
