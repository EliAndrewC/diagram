# Research: Unskill the repository (feature 329)

Measurements taken in `/diagram/.clones/diagram-unskillify` at `5e2ba4824` (main + this spec), 2026-10-07, by `git grep`
over tracked files unless stated.

## R1 - What collides at the root

Root: `CLAUDE.md`, `Makefile` (a 39-line forwarder), `.gitignore`, `ruff.toml` (the lint fence, `exclude = ["*"]`).
Skill dir: `CLAUDE.md` (an 18-line index), `Makefile` (2,098 lines, every target), `.gitignore` (10 rules),
`pyproject.toml` (ruff, pyrefly, pytest, coverage). ruff prefers `ruff.toml` over `pyproject.toml` in one directory,
hence D3. Nothing else shares a name.

## R2 - Where the old path is named

- Live files outside `specs/`: 176 files, 7,483 occurrences; 6,115 of them in `dev/claims-index.json` (unit keys), 500
  in `scripts/fixtures/*.json` (recorded commands), about 400 in `dev/perf-log/` records.
- Under `specs/`: 12,441 occurrences in 1,105 files (left as written).
- Forms: 6,460 are `.claude/skills/diagram/l7r...`; the bare forms (`cd .claude/skills/diagram &&`, `-C`, a path
  constant, a closing quote) are about 400, listed by the sweep for hand edits.
- Depth arithmetic: 143 sites under the skill dir (`parents[k]` with k >= 3, `.parents[2]` off a skill-root constant,
  `../../../` - 30 of those in the Makefile). Rule for `Path(__file__).resolve().parents[k]` in a file d directories
  below the skill root: `parents[d]` is the skill root and stays the project root; `k > d` climbed into the repository
  and becomes `k - 3`.
- 72 files in `scripts/` name it (20 hold a `SKILL = ".claude/skills/diagram"` constant or its `Path` form).
- `.claude/settings.json` and `container-scripts/append-system-prompt.md`: none (hooks are `/diagram/scripts/...`).
- Outside the repository: gm-assistant `docs/iteration-loop.md` (one file); the user memory, 5 files.

## R3 - The config root is equal

To fill at T03: file lists from `ruff check --show-files`, `ruff format --check`, and pyrefly, before (skill dir) and
after (root), prefix stripped, compared.

## R4 - Guards and push checks naming the path

`canon-read-hooks.sh`, `check-bundle-hooks.sh`, `claims-gate.sh`, `clone-sync-hooks.sh`, `download-copy-hooks.sh`,
`entry-gate.sh`, `finished-run-hooks.sh`, `guard-file-hooks.sh`, `idle-tests-hooks.sh`, `make-only-hooks.sh`,
`new-file-hooks.sh`, `pair-hooks.sh`, `review-gate.sh`, `sync-with-main.sh`, and 19 of their `test-*.sh` companions.

## R5 - Merges across the move

Measured 2026-10-07 in a scratch pair of repositories (git 2.53, ort): main renames `.claude/skills/diagram/dev` to
`dev`; a clone holds a commit editing `dev/x.md` at its old path and adding `dev/new.md` under the old directory.
- Default config: `CONFLICT (file location): ... added in HEAD inside a directory that was renamed ..., suggesting it
  should perhaps be moved to dev/new.md`; the merge stops (the edit itself was applied to `dev/x.md`).
- `-c merge.directoryRenames=true`: `Path updated: ... moving it to dev/new.md`; clean, exit 0, the edit on
  `dev/x.md`, nothing left under `.claude/`.
- Which `sync-with-main.sh` runs: the prompt hook (`clone-sync-hooks.sh`, read from the mirror) runs the CLONE's own
  copy, which in a clone not yet synced is the pre-move script without the flag. So the flag is set where every git in
  the container reads it - the global git config, written by `container-scripts/setup-dev-env.sh` (and applied once by
  hand in the running container) - as well as passed by the new `sync_in`; and the hook, which is always the mirror's
  newest, runs the carry after a successful sync-in.
Fixture cases whose verdict changed: to fill at T05.

## R6 - The gate before and after

Baseline `make done` in this clone at `5e2ba4824` + the spec, before the move, 2026-10-07: GREEN in 459 s. Phases
static, format, typecheck, hooks-test (38 guard suites green), test-full: 10,818 passed, 3 skipped, 2 xfailed in
228.6 s. ruff's checked files from the skill dir: 831 (361 under `l7r/`, 460 under `tests/`, 9 under `wip/`, and
`pyproject.toml`). The first gate after the carry in a second clone: to fill at T09.
