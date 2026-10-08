# Implementation Plan: Unskill the repository

**Feature**: 329-unskill-the-repo | **Spec**: spec.md | **Request**: request.md | **Research**: research.md

## Summary

One `git mv` of everything under `.claude/skills/diagram/` to the root (a prefix strip), the three colliding files and
the lint fence merged, every live pointer rewritten by a sweep script plus hand edits for the forms a sweep cannot judge
(depth-dependent code), a carry step in sync-in for each clone's gitignored artifacts, a check that refuses the old
prefix in a live file, and the Markdown audit (FR-012) applied as its own step after the move.

## Performance bookends (constitution VI)

Not a generator change: no stage's code changes, only where it lives. The gate's own ratchet (`_ratchet.py`) and the
first warm gate after the carry (SC-004) are the measurement; recorded in research.md R6.

## Decisions

**D1 - Layout (FR-001).** Every tracked path `.claude/skills/diagram/X` becomes `X`, by `git mv` in one commit, so
`git log --follow` and merge rename detection both see renames. No name exists at both levels except the four D2/D3
settle (research.md R1: the root holds `CLAUDE.md`, `Makefile`, `.gitignore`, `ruff.toml`; the skill dir holds
`CLAUDE.md`, `Makefile`, `.gitignore`, `pyproject.toml`). `.claude/skills/` keeps only the speckit skills.

**D2 - The colliding files (FR-002).**
- `Makefile`: the skill's Makefile becomes the root's; the root forwarder is deleted, and with it
  `scripts/make-docs.py --forwardable` and its test (nothing else calls it; dead code is removed, not kept). Every
  `../../../` in it becomes the root itself (research.md R2: 30 sites), every `cd .claude/skills/diagram &&` goes.
- `.gitignore`: the skill's ten rules move into the root file, root-relative (`.gencache/`, `.testmondata*`, ...); the
  root's `.claude/skills/diagram/pool/...` rules lose the prefix.
- `CLAUDE.md`: the skill's 18-line index is folded into the root `CLAUDE.md` opening ("you are / read" table) and the
  file is deleted. What a research session loads SHRINKS: it loaded root + skill index + `research/CLAUDE.md`; it now
  loads root + `research/CLAUDE.md`.

**D3 - One config root (FR-002a).** `pyproject.toml` moves to the root and `ruff.toml` is deleted; the fence's purpose
moves into `[tool.ruff] extend-exclude` naming every root entry that was outside the skill (`specs`, `scripts`,
`.clones`, `.claude`, `.specify`, `buildspec`, `container-scripts`, `docs`), with the fence's incident note carried
beside it. Proven equal, not assumed: `ruff check --show-files` and `ruff format --check` file lists, and pyrefly's
checked-file list, taken from the skill dir before and from the root after, compared with the prefix stripped
(research.md R3). `testpaths = ["tests"]` and coverage `source = ["l7r"]` already scope pytest and coverage; a root
`.clones/` is outside both, and a test pins that the resolved pytest rootdir is the repository root and its collection
never enters `.clones/`. SC-007's seeded-lint test: a lint test copies one engine file into a temp tree with the root
config, plants an unused import, and asserts `ruff check` fails on it while a planted error under `specs/` is ignored.

**D4 - `SKILL.md` (FR-003, FR-011).** Becomes `docs/usage.md`, frontmatter dropped, links corrected, content per the
audit (D12). The root `CLAUDE.md` names it. `dev/skill-boundary.md` and the root `CLAUDE.md` opening say once that the
project stopped being a skill in feature 329 and why (nothing invoked it; the prefix cost every pointer).

**D5 - The pointer sweep (FR-004).** A one-shot script in the feature directory (`specs/329-unskill-the-repo/sweep.py`,
run through `make`-free `python3` as a spec tool, like features 022-116's migrations) rewrites every LIVE tracked file:
`<anything>/.claude/skills/diagram/` -> `<anything>/`, a token-initial `.claude/skills/diagram/` -> nothing, and for a
moved file, every relative link that climbed OUT of the skill dir (`../../../../docs/x` from `dev/`) recomputed from the
new location (a link that stays inside never changes). The remaining bare forms (`SKILL = ".claude/skills/diagram"`,
`cd .claude/skills/diagram && `, `-C $(DIAGRAM)`, a `parents[k]` that climbed past the skill dir, `SKILL.parents[2]`)
are listed by the script and edited by hand (research.md R2 lists them: about 20 path constants in `scripts/`,
about 40 depth computations in the engine's tests and tools, 30 `../../../` in the Makefile). A constant whose value
becomes the root is deleted and its uses made root-relative, never set to `"."` (a `./research/...` string would stop
comparing equal to git's output).
- NOT live, left as written (FR-004's verbatim records): `specs/`, `dev/*-log/` (perf, run, idle, bypass records),
  `scripts/fixtures/*.json` (recorded real commands the hook suite replays), and `docs/review-ledger.md` (its rows are
  history). Their tests stay meaningful because the hooks they exercise match command SHAPES (an interpreter, a pytest,
  a write into the mirror), not the skill path; any fixture case whose expectation depended on the old layout is found
  by `make hooks-test` and judged one by one (research.md R5).
- `dev/claims-index.json` is live data keyed by unit path: its keys lose the prefix (a rename of the unit; the code and
  research fingerprints are content hashes, so no claim is re-owed by the move). A unit the audit moves (D12) has its
  key renamed the same way.

**D6 - Path guards (FR-006).** Each guard and push check that names the skill path (research.md R4 lists them) is
edited, and its existing test companion re-pointed; `make hooks-test` green is the proof, and each guard whose test
did not exercise the path gets one case that does.

**D7 - The old-layout check (FR-007).** `scripts/check-old-layout.py`: every tracked file outside the D5 verbatim list
that contains `.claude/skills/diagram` fails, naming the file, the line and the path with the prefix removed. Run in
`lint` (the gate) and in `sync-with-main.sh` push. The review ledger is exempt LINE BY LINE, not as a file: a ledger
line naming the old path passes only if it stands verbatim in the ledger as of the commit that added this check (the
rows written before this feature, FR-004); a row written after it is held like any live line (plan review round 1).
`--selftest` plants a live file, an exempt file, an old ledger row and a new one. The check names the prefix by
concatenation so it does not find itself.

**D8 - The carry (FR-008).** `scripts/_layout_carry.sh <tree>`, idempotent, called by `sync_in` after the clone's pull
and after `mirror_refresh` on the mirror: when `<tree>/l7r` is tracked and `<tree>/.claude/skills/diagram/` exists, each
file left there (all untracked or ignored by then) is moved to the same path at the root. Where the root already holds
that path (measured: 9 clones hold a `.ruff_cache` at both places), a CACHE's old copy is invalidated - deleted, the
reason recorded here: the root's copy is the one the tools now write, and a cache is rebuilt on demand
(`__pycache__`, `.ruff_cache`, `.pytest_cache`, `.mypy_cache`, `.coverage*`, `.testmondata*`, `.gencache`); any other
colliding file is moved beside its twin as `<name>.pre-329` and reported, never deleted. The old directory therefore
always goes (FR-008, plan review round 1). `seed_roll_cache` looks at the new `.gencache` path.
A dirty clone on the old layout (sync-in merges only clean clones) is told by the mirror-only branch: "main moved the
project to the root (feature 329) - commit and sync in". The gate's caches carry: the roll cache's dependency records
are root-relative to the project dir (feature 167), and testmon's node ids (`tests/...`) do not change, so both stay
warm (research.md R6 measures the first gate after the carry).

**D9 - Clones with work in flight (FR-009).** `test-sync-with-main.sh` gains a case: a scratch main does the move; a
clone holding an unpushed commit that edits a moved file and adds a new file under the old directory syncs in; the edit
lands on the moved file and the new file at the new place. git's ort merge reports a file added under a renamed
directory as a conflict unless `merge.directoryRenames=true`; the pull in `sync_in` passes it (research.md R5).

**D10 - The feature history (FR-005).** `specs/README-paths.md` is not added (the GM's READMEs are theirs); instead the
root `CLAUDE.md` "Key paths" line on `specs/` says: a path in a spec before 329 that starts `.claude/skills/diagram/`
now drops that prefix.

**D11 - Outside this repository.** gm-assistant's `docs/iteration-loop.md` names the old path; it is reported to the GM,
not edited. The user-level memory gains one entry recording the move.

**D12 - The Markdown audit (FR-012).** Four readers (Opus, one per slice) judged the 85 documentation files; the 274
modal write-ups and the pool's per-map notes are judged as classes (KEEP). The table, every member listed, is
`audit.md`, with the session's final calls at its head: the destinations of the documents that leave the project root
(`docs/usage.md`, `docs/buildings.md`, `docs/buildings/programs.md`, `docs/migration-plan.md`, `dev/timings.md`,
`docs/package-boundary.md`, `docs/reviews.md`, `docs/switches.md`), and `wip/README.md` KEPT and raised with the GM (a
README is theirs; the audit request is not the explicit delegation `readme-hooks.sh`'s escape asks for). Applied AFTER
the move commit, as its own commit: the moves and deletions by the session (`git mv`/`git rm`, each deletion's carried
facts written first); the trims, splits and merges by editing agents (Opus - what to cut is judgment), each given only
its files' rows and the carry list, on disjoint files, then every diff read by the session before commit. The gate
(`test_docs_match_the_mechanism.py`, `check-research-pointers.py`, `make-docs --check`) holds what code reads.
Verdicts on the Mode A procedure files (`buildings.md`, `buildings/programs.md`) respect the claims index: the move
renames their keys and `_claims.py`'s `BASE_PATHS`; a section whose text the trim changes is re-owed and answered by
`impl-drift` before the push (claims-gate).

**D13 - CI.** `buildspec/*.yml`, `buildspec/run.sh`, `sparse-excludes.txt` and `Dockerfile.ci` are swept; the remote is
off and is not dispatched; `tests/tooling/ci/` (config, cache, image check) is the proof.

## Tests

- `scripts/check-old-layout.py --selftest`; the gate runs the check.
- The ruff seeded-error test and the pytest-rootdir test (D3).
- `scripts/test-sync-with-main.sh`: the carry (a tree with ignored files at the old place, one colliding) and the
  in-flight clone (D9).
- Every existing suite: `make hooks-test`, `make done`.

## Verification

`make hooks-test`; `make done` from the root; the R3 equality lists; the scratch-clone case; `claude` started in the
clone lists no `diagram` skill (SC-003); the first warm gate after the carry in a second clone (SC-004).

## Constitution Check

No map draws or states anything differently (no Decisions Recorded entries). Not a research question: every task is
`research: rendering`. Python: the new scripts carry selftests; engine code changes only in path arithmetic, held by
the 100% floor. XIII: baseline gate taken before the move (research.md R6). XVI: the one exception (the verbatim
records) was judged legitimate by spec-fidelity round 1.

## Review history

- Plan review round 1 (spec-fidelity MODE 4, 2026-10-07): BLOCKED - D7 exempted the whole review ledger (now line by
  line, as of the commit that adds the check) and D8 left the old directory behind on a collision (now: caches
  invalidated, other files kept beside their twin). D12's `wip/README.md` ruled LEGITIMATE.
