# Plan - 197 Claim feature numbers under a lock

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## Constitution Check

- **VI Verify before done**: the tool's every behavior has a pytest case on a fixture; the concurrency
  property (SC-001) is asserted by running twelve real processes against one lock, and the test is
  shown to FAIL with the lock removed before it is trusted (Principle XVIII's "prove it fires").
- **X Python discipline**: a `scripts/*.py` tool like `tick-task.py`; ruff/pyrefly run over `scripts/`
  through `make static`; `scripts/` is outside the measured `l7r` surface, so the coverage floor does
  not apply - the pytest suite is the verification, as it is for `tick-task.py`. Under 1,000 lines.
- **XIII No regressions**: the only engine-adjacent changes are the skill Makefile (a new target, a
  section appended to `audit`) and the root Makefile's forward list. `make done` runs; `make docs`
  regenerates the target page so `test_make_docs` stays green.
- **XVI Build what was asked**: the spec goes to `spec-fidelity` before any code is written; D1 and D3
  are put to it explicitly as the two places the spec makes a choice the GM did not dictate.
- **XVIII A guard ships with its test**: not a guard (it refuses a session nothing and rewrites no
  command), so not on the `hooks-test` roster; the `hooks` stamp still covers `scripts/*.py` at push.
- **Iteration cost**: one new turn in the specify step (`make claim`), replacing a scan the session did
  by hand and a renumber it sometimes did later.
- **Route**: no `l7r/**/*.py`, no pool - DIRECT. The Makefile and `scripts/` changes owe a green
  `make hooks-test` stamp (scripts) and a green `make done` is run anyway because the skill Makefile
  changed and `test_make_docs` reads it.

## Design

### `scripts/claim-feature.py`

```
claim-feature.py <slug> [--dry-run] [--root DIR] [--main DIR] [--json]
```

- `root` = `git rev-parse --show-toplevel` of the cwd; `main` = root's grandparent when root's parent
  is `.clones`, else root itself (the same derivation as `sync-with-main.sh` and
  `main-tree-hooks.sh`). `--root`/`--main` exist for the tests' fixtures and are ordinary arguments,
  not seams.
- Refuse (exit 2) when `root == main`: main is never a workspace.
- Validate the slug: `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Take `fcntl.flock(LOCK_EX)` on `<main>/.specify/feature-numbers.lock`, polling for up to 30 s
  (`LOCK_NB` in a loop, so a hung holder produces a refusal naming the file rather than a hang).
- Under the lock, collect `(number, name, where)` for every `NNN-*` directory in: `<main>/specs`;
  `git -C <main> ls-tree --name-only origin/main specs/` (best effort - a fixture or a mirror with no
  such ref contributes nothing); every `<main>/.clones/*/specs`; `<root>/specs` (already covered when
  root is under `.clones`, harmless twice); plus every `number` in the ledger.
- Warn on stderr for any number held by two different names in `<main>/specs` (FR-004).
- Refuse when the slug is already in use by any collected directory.
- `next = max + 1`; `name = f"{next:03d}-{slug}"`. Unless `--dry-run`: `mkdir <root>/specs/<name>`,
  append the ledger row (`{"number", "slug", "clone", "utc"}`), write `<root>/.specify/feature.json`.
- Print `name` on stdout. On stderr: the sources' maxima in one line, then the two `export` lines.
- Python only - `fcntl` is the same lock `flock(1)` takes, so it also serializes against any shell
  that ever takes `flock` on the same file.

### Makefile

Skill Makefile, `[project]` group:

```
claim:          ## [project] claim the next spec-kit feature number under the host-wide lock   SLUG=kebab-slug [PEEK=1]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/claim-feature.py" "$(SLUG)" $(if $(PEEK),--dry-run,)
```

Root Makefile: `claim` joins `FORWARD`. `audit`: a final section prints the last ten ledger rows
(FR-008) - a small `python3 -c` like the sections above it, reading `<main>/.specify/feature-numbers.jsonl`
resolved the same way (the mirror is the grandparent of a clone). `make docs` after.

### `create-new-feature.sh` (FR-006)

The three automatic-number branches (`check_existing_branches` and the two `get_highest_from_specs`
fallbacks) collapse to one call: `claim-feature.py "$BRANCH_SUFFIX" [--dry-run]`, parsing the number
off the front of its output. `--number N` unchanged. The `git checkout -b` that follows is already
blocked by `no-branch-hooks.sh` in this repository and is not this feature's business.

### Documents (FR-007)

Surfaces, from an unfiltered grep for `highest`, `NNN`, `renumber`, `plus 1`, `next available` over
`CLAUDE.md`, `docs/`, `.specify/`, `.claude/skills/*/SKILL.md`, `.claude/skills/diagram/CLAUDE.md`,
`.claude/skills/diagram/dev/`:

- `CLAUDE.md` "Concurrent sessions" bullet - rewritten around `make claim`; renumber becomes the
  fallback for the D4 window.
- `docs/session-clones.md` "Concurrent sessions: coordinating spec-kit feature numbers" - points 1-3.
- `.claude/skills/speckit-specify/SKILL.md` step 3 "Resolution order" - the sequential case runs
  `make claim SLUG=<short-name>` and takes its output; the mkdir/feature.json lines note the tool did them.
- `.specify/memory/constitution.md` Development Workflow: a new paragraph; header sync-impact note;
  footer version 2.20.0, last amended 2026-09-07.
- `.gitignore`: the ledger line, with the reason.
- `docs/make-targets.html`: `make docs`.
- Memory note for the next session.

### Tests - `tests/tooling/test_claim_feature.py`

Fixture `mirror(tmp_path)`: `git init` a mirror with `specs/001-a`, `specs/002-b`, a commit, and
`refs/remotes/origin/main` pointing at a commit whose tree has `specs/003-c` (built with a second
commit then `update-ref`, HEAD reset back so the working tree lacks it); `.clones/alpha` and
`.clones/beta` as plain directories with `.git` files? - simpler: real `git clone`s of the mirror,
which is what a clone is. Cases:

1. mirror working tree alone -> next after its max
2. `origin/main` ahead of the working tree -> counted
3. another clone's unpushed `specs/009-x` -> counted
4. ledger row 020 with no directory anywhere -> counted; a missing ledger file -> not an error
5. twelve concurrent subprocesses from one clone, and twelve split across two clones -> distinct,
   consecutive; with the lock code disabled (monkeypatched to a no-op via an env only the test sets?
   NO - seams are refused outside fixtures; instead the test asserts the property and a second test
   removes the lock FILE mid-run? Not meaningful.) -> the proof-it-fires is a one-off measurement
   recorded in research.md R1: the test run with the flock lines commented out, showing duplicates.
6. refusals: from the mirror root; bad slug (`Bad_Slug`, `a--b`, `-a`); slug in use in another clone;
   lock held by a sleeping holder with a short timeout argument (`--lock-timeout 0.2`, an argument
   for exactly this test) -> exit 2, nothing created, ledger unchanged
7. FR-004: mirror with `specs/005-x` and `specs/005-y` -> warning names both, claim still succeeds
8. `--dry-run` prints the name, creates nothing, appends nothing
9. `feature.json` written with the right path; stderr carries both `export` lines
10. `make claim` through the real Makefile in a fixture clone (like `test_switches.py` does) - one case,
    `tooling`-marked, proving the target wiring and the root forward

### Research

`research.md` R1: the concurrency proof (the test with the lock removed). R2: the collision census -
every duplicate number in main's history and how each was resolved (184/186, 195/195, 107).
