# Tasks - feature 321, back up each clone's unlanded work to a GitHub branch

Every task is tooling over `sync-with-main.sh`, two guard companions and two docs. Nothing a map draws or states changes,
so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 [US1] [US2] `backup_step`, `backup_sweep` and `backup_on_exit` in `scripts/sync-with-main.sh`; the EXIT trap in
      the `done` and `push` arms (FR-001 to FR-004, FR-006 to FR-009; plan D1-D5)
      research: rendering
      verify: DONE. backup_step, backup_delete, backup_on_exit in sync-with-main.sh; EXIT trap in the done and push arms; plan review CLEAR
- [x] T02 [US1] [US2] The fixture cases in `scripts/test-sync-with-main.sh`: refused stop backed up, sync-in moves nothing,
      a second stop pushes nothing, diverged, unreachable and rejecting remotes, landing deletes, the sweep (SC-001 to
      SC-004, SC-006; plan D8)
      research: rendering
      verify: DONE. test-sync-with-main.sh cases 11-14 green (97 checks); 19 go red with the trap removed
- [x] T03 The guard cases: three `expect_allow` in `scripts/test-no-branch-hooks.sh`, three `ok` rows in
      `scripts/test_hooks_cases.py` (FR-005, SC-005; plan D6)
      research: rendering
      verify: DONE. test-no-branch-hooks 19/19, repo-safety cases 28/28 with the backup push and both delete forms permitted
- [x] T04 The doctrine: the no-branch rows in the root `CLAUDE.md` and `docs/guards.md`, one sentence in
      `docs/session-clones.md` (FR-010, SC-007; plan D7)
      research: rendering
      verify: DONE. no-branch row in CLAUDE.md, a row in docs/guards.md, one sentence in docs/session-clones.md
- [x] T05 `make hooks-test` green against a detached-worktree baseline; the first real stop of this clone backs it up
      research: rendering
      verify: DONE. make hooks-test green at db10236b8 (baseline worktree green); the pre-existing open-questions timing red fixed by an exact index (research.md R1); the first real backup is this clone's own done
