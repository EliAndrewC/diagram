# Feature Specification: Back up each clone's unlanded work to a GitHub branch

**Feature**: 321-clone-backup-branches | **Created**: 2026-10-04 | **Status**: Draft (spec FAITHFUL; filed for another session to plan and implement)
**Input**: the GM's words, verbatim in `request.md`.

## Summary

Work committed in a session clone reaches GitHub only when it lands on `main`; until then it exists in one place, the
clone's directory on the host's disk. This feature pushes each clone's unlanded commits to a remote-only branch
`backup/<clone-name>` when a session stops work, and deletes that branch once its contents are on `main`. The GM: push
*"if we're running sync with main ... any time we are finishing work"*, never *"every time that we save a change to a
file"*, and the branches *"deleted after their contents have been merged into main, just to keep the branches that are
visible manageable"*.

## Context

Observed 2026-10-04 by the filing session's read of `scripts/sync-with-main.sh` and `git ls-remote origin`, and by the
session that answered the GM:

- `sync-with-main.sh` pushes only `HEAD:main` (the two `git push origin HEAD:main` calls, lines 456 and 460).
- GitHub carries `refs/heads/main` alone (`git ls-remote origin`: `HEAD` and `refs/heads/main`, nothing else).
- `no-branch-hooks.sh` blocks creating a LOCAL branch (`checkout -b`, `switch -c` and their forms; the GM's 2026-07-27
  ruling). Neither it nor `repo-safety-hooks.sh` (which refuses a force push, a history rewrite and a write to
  `/host-l7r-repo`) refuses a push to a remote branch other than `main` today.
- The open-task refusal (`sync-with-main.sh`, around line 393: "nothing lands on main until it is complete") keeps an
  in-progress feature's work in its clone. On 2026-10-04 feature 319 held 34 unlanded commits there, with no copy
  anywhere else.
- Nothing was lost that day: a sync paused mid-merge, and the missing map page was a generated, untracked file. But a
  damaged disk or a deleted `.clones/` directory would take every unlanded commit of every clone with it.

## User Scenarios & Testing

### US1 - Unlanded work is backed up when a session stops (P1)

A session ends its work with `sync-with-main.sh done`. Whether the work lands or is refused (the open-task refusal
included, the case that most needs a backup), the clone's HEAD is on GitHub afterwards, on `backup/<clone-name>`, unless
nothing there is new.

**Independent Test**: in a fixture clone with a bare fixture remote, commit, run `done` against a feature with open tasks,
and read the remote's `backup/<clone-name>`.

**Acceptance Scenarios**:

1. **Given** a clone with commits `main` does not hold and a feature with open tasks, **When** `done` is refused,
   **Then** `backup/<clone-name>` on the remote points at the clone's HEAD and the refusal is unchanged.
2. **Given** `backup/<clone-name>` already points at HEAD (or HEAD is already contained in `origin/main`), **When** `done`
   runs, **Then** no backup push is made.
3. **Given** a backup branch whose tip is not an ancestor of HEAD (a clone rebuilt under the same name), **When** `done`
   runs, **Then** nothing is forced: the step says so in one line and prints the command that would resolve it.
4. **Given** the remote refuses the backup push (network, permission), **When** `done` runs, **Then** the stop-work step
   carries on and reports the failure in one line with its reason.

### US2 - Backups are cleaned up once their work is on main (P1)

When `done` lands a clone's work, that clone's backup branch is deleted; and a sweep deletes every `backup/*` branch whose
tip is already contained in `origin/main`, which covers clones abandoned after their work landed.

**Independent Test**: in the fixture, land the clone's work and read the remote's branches; push a stale `backup/other`
whose tip is in main and one whose tip is not, run the sweep, read the branches again.

**Acceptance Scenarios**:

1. **Given** a clone with a backup branch, **When** `done` lands its work, **Then** `backup/<clone-name>` is gone from the
   remote.
2. **Given** `backup/*` branches, some contained in `origin/main` and some not, **When** the sweep runs, **Then** exactly
   the contained ones are deleted.

### Edge Cases

- A clone with uncommitted changes: out of scope; the stop-work procedure commits first, and only commits are pushed.
- A clone whose HEAD is already in `origin/main` and which has a leftover backup branch: the branch is deleted (it is
  contained), and nothing is pushed.
- A backup branch whose tip is NOT contained in main is never deleted or overwritten, by any step or command this feature
  runs or prints, whatever its age.
- Two sessions sharing one clone name over time (a clone deleted and rebuilt): the non-fast-forward case of US1 scenario 3.

## Requirements

- **FR-001**: `sync-with-main.sh done` MUST push the clone's HEAD to `refs/heads/backup/<clone-name>` on `origin` on
  every stop, landed or refused (the open-task refusal included), unless that branch already holds HEAD or HEAD is
  already contained in `origin/main`. `<clone-name>` is the clone directory's name.
- **FR-002**: The backup push MUST happen at the stop-work step only: never per file save and never at the per-prompt
  `sync-in`.
- **FR-003**: The backup push MUST be fast-forward only and NEVER forced. A backup that would need a force stops and says
  in one line that this clone's HEAD is NOT backed up, and prints a command that resolves it without deleting or
  overwriting the existing backup (fetch the backup's tip, merge it into HEAD, push fast-forward). The message also says
  that the command merges the existing backup's commits into this clone's HEAD, so they land on `main` with this clone's
  work. The command is printed for the GM to decide; a session MUST NOT run it without the GM's word.
- **FR-004**: No local branch MUST be created: the push is `HEAD:refs/heads/backup/<clone-name>`.
- **FR-005**: Neither `no-branch-hooks.sh` nor `repo-safety-hooks.sh` MUST refuse the backup push
  (`HEAD:refs/heads/backup/<clone-name>`) or its delete; a `make hooks-test` case for each guard pins both as permitted.
- **FR-006**: A failed backup push or delete MUST NOT block or change the outcome of the stop-work step; it is reported
  in one line with the reason.
- **FR-007**: Nothing MUST go to a backup branch beyond what the clone would push to `main`: the same commits, no
  untracked or ignored files, no extra refs.
- **FR-008**: When `done` lands the clone's work on `main`, it MUST delete `backup/<clone-name>` on `origin`, but only when
  that branch's tip is contained in `origin/main`.
- **FR-009**: A sweep MUST delete every `backup/*` branch on `origin` whose tip is contained in `origin/main`, and no other.
  Where it runs (`sync-in` at most once a day, `make idle-tests`, or its own make target) is the implementing session's
  plan decision, recorded in the plan.
- **FR-010**: The no-branch row of the guard table in the root `CLAUDE.md` and `docs/guards.md` MUST say that the
  remote-only `backup/<clone-name>` branches exist, who pushes and deletes them, and that they are not local branches.

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-004, FR-007): a test on a fixture clone and bare remote: after a refused `done` the
  remote's `backup/<clone-name>` equals HEAD, the clone has no local branch but `main`, and the remote has no other new
  ref; after a `sync-in` alone, no backup ref moved.
- **SC-002** (FR-001): a second `done` with nothing new makes no push (the test counts pushes or reads the reflog of the
  bare remote).
- **SC-003** (FR-003): a test with a diverged backup branch: no forced push is made, the remote branch is unchanged, the
  one-line message says HEAD is not backed up, and the printed command is the fetch, merge and fast-forward push (no
  delete, no force); the message says the command merges the existing backup's commits into HEAD so they land on
  `main` with this clone's work; running it in the fixture leaves a backup that contains both the old tip and HEAD.
- **SC-004** (FR-006): a test with an unreachable remote for the backup push: `done` exits as it would without the
  backup, and prints one line naming the failure.
- **SC-005** (FR-005): `make hooks-test` passes with cases for both guards showing the backup push and its delete
  permitted.
- **SC-006** (FR-008, FR-009): a test: landing deletes the clone's backup branch; the sweep deletes exactly the
  contained `backup/*` branches and keeps one that is ahead of main.
- **SC-007** (FR-010): the no-branch rows of the root `CLAUDE.md` and `docs/guards.md` name the backup branches.

## Decisions Recorded

This feature draws and states nothing on a map; the table records its tooling decisions.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Branch name `backup/<clone-name>`, remote-only, no local branch | tooling decision (the filing session's proposal, accepted by the GM 2026-10-04) | one branch per clone keeps the list readable; remote-only keeps the GM's 2026-07-27 no-branch ruling for local work | this spec, FR-004 |
| Push at stop-work only | tooling decision (the GM's words) | *"we shouldn't take the time to do a GitHub push like literally every time that we save a change"* | FR-002 |
| Never forced | tooling decision (the force-push rule, `repo-safety-hooks.sh`, which has no escape) | a force push overwrites work silently | FR-003 |
| Public visibility of in-progress branches accepted | GM decision, 2026-10-04 | *"I don't mind people being able to see branches in progress"* | Assumptions |
| Deleted once contained in main, never before | GM decision, 2026-10-04 | *"deleted after their contents have been merged into main"* | FR-008, FR-009 |

## Assumptions

- The repository is public; the GM accepts that in-progress work is visible on GitHub (2026-10-04).
- The stop-work procedure commits before `done`, so uncommitted work is out of scope.
- `origin` is GitHub (feature 130); the clone's name is unique among live clones on the host.

## Review history

- Round 1 (spec-fidelity, 2026-10-04): CHANGES REQUIRED - (1) FR-005's refusal of other remote branch names was not
  asked for (no guard refuses a remote push today, and the backup runs inside `sync-with-main.sh`): FR-005 now only pins
  the backup push and delete as permitted, the edge case, SC-005's refusals and the decision row cut; (2) the listing
  target (US3, its FR and SC) was not asked for: removed; (3) FR-003's resolving command named (fetch, merge,
  fast-forward push), never deleting or overwriting a backup not in main, and the message says HEAD is not backed up;
  SC-003 and the edge case follow. Applied.
- Round 2 (spec-fidelity, 2026-10-04): the three round-1 items confirmed; CHANGES REQUIRED on one new point - FR-003's
  command would carry a dead clone's unlanded backup into this clone and onto `main` (and an unfinished feature in it
  could block landing): the message now says so, the command is the GM's to run, never a session's unasked; SC-003
  checks the statement. Applied.
- Round 3 (spec-fidelity-verify, 2026-10-04): FAITHFUL - the round-2 item confirmed in FR-003 and SC-003; nothing new.
