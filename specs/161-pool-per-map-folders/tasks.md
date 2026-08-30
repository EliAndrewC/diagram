# Tasks: One folder per map, and the frozen hand-authored pool out of `pool/` (feature 161)

**Every task here is `research: rendering`.** This feature reorganizes a directory tree and the
tooling that walks it. It changes no glyph, size, placement rule, distance or density; no map is
re-rolled; every render is byte-identical after the move (FR-007). No question about how a place was
built, farmed, planted or lived in arises anywhere in the work, so no task carries research boxes -
and the spec's "Decisions Recorded" table is kept and explicitly empty rather than deleted, so the
nil return reads as a nil return.

The design and what was rejected: [`research.md`](research.md). The tree and its invariants:
[`data-model.md`](data-model.md). The one discovery surface every consumer calls:
[`contracts/pool-discovery.md`](contracts/pool-discovery.md). The spec's two review rounds are in
[`spec.md`](spec.md) "Review history" - round 2 returned **FAITHFUL**.

**Sequencing (research R2): the tooling learns the new shape BEFORE the files move.** Phases 1 and 2
leave the tree untouched, so the suite stays green throughout and each consumer is converted against
a known-good baseline. Phase 3 moves exactly ONE map. Only then does Phase 4 move the other 27.

---

## Phase 0 - baseline and research

- [x] T01 measured regression baseline on unmodified code in a **detached worktree** (never a stash - a
      stash mutates the tree under the two `spec-fidelity` agents reading it). `make done` on commit
      `81641618`: **2737 passed, 2 skipped, 0 failed**, gate green. Zero pre-existing failures, so the
      bar after the change is exactly this. Recorded in `research.md` R8
      research: rendering
- [x] T02 census the worktree-versus-clone gitignored-artifact gap that the baseline rule warns about.
      MEASURED: both trees hold the same 8 hamlet renders, and they are the frozen exhibits - the 5
      scripted maps have no renders in either. No gap; the baseline is directly comparable. `research.md` R8
      research: rendering
- [x] T03 settle the design questions: the discovery surface (R1), move-first versus dual-support (R2),
      the `ci/delta.py` decision and the alternative declined (R3), the engine-fingerprint prune lists
      (R4), the `.gitignore` collapse (R5), `check_village`'s default (R6)
      research: rendering
- [x] T04 confirm Principle IV/V/XII are nil returns by METHOD, not assertion: grep the moved set for
      `SOURCE: GM NOTES` - none; no claim about the world changes. `research.md` R7
      research: rendering

## Phase 1 - the discovery surface (red-green; the tree is NOT touched)

- [x] T05 write the FAILING tests for `poolmaps` discovery against a `tmp_path` tree: the seven
      invariants in `contracts/pool-discovery.md` (round trip, tree-agrees-with-kind, exact filtering,
      determinism, depth, absent-tree-is-empty, non-maps-excluded). They must fail before T06 exists
      research: rendering
- [x] T06 implement `MapBundle` and `bundles(*, trees, kinds, skill_dir)` in
      `l7r/diagram/pipeline/poolmaps.py`. `classify()` unchanged. Turn T05 green
      research: rendering
- [x] T07 pin FR-011 with a test that `classify()` gives the same answer one level deeper. It holds by
      construction (basename-keyed closed lists), and the point of the test is that a future change to
      `classify` cannot break it silently
      research: rendering
- [x] T08 `make quick` green; the tree is still the OLD shape and nothing else has changed yet
      research: rendering

## Phase 2 - convert every consumer to the surface (the tree is STILL not touched)

Each of these keeps the suite green, because the surface describes whatever tree is on disk.

- [ ] T09 `pipeline/render_cache.py` - `regen_pool` asks for bundles (BOTH trees; the missing-exhibit
      warning follows the exhibits into the legacy tree). Reporting paths become tree-relative
      research: rendering
- [ ] T10 `pipeline/pool_index.py` - discovery via the surface; `SKIP_DIRS`' non-map exclusion moves
      into the surface so the two cannot disagree
      research: rendering
- [ ] T11 `tools/cache_audit.py` (live pool, `scripted` only), `tools/timings.py` (both trees, a
      census), `tools/mapcheck.py` `_live_gens` (live pool, not `legacy` - keep its recorded
      Kuwabata lesson: ASK `classify`, never read the list)
      research: rendering
- [ ] T12 `tests/test_villages.py` - GENERATORS (live, scripted), the ratchet (BOTH trees, FR-013a),
      and the stale-render sweep (BOTH trees, FR-013b - the regression T02 found)
      research: rendering
- [ ] T13 `tests/test_notes_census.py`, `tests/pipeline/test_pool_index.py`,
      `tests/tooling/pipeline/test_gencache.py` (it names `hoshizora`, a frozen map that changes
      trees), `tests/test_compound.py`
      research: rendering
- [ ] T14 **the top risk (R4)**: add `legacy-hand-authored-pool` to the directory-prune tuples in
      `render_cache.engine_fingerprint()` AND `gencache.engine_files()`, with a test asserting the
      fingerprint is UNCHANGED across the move. Note the direction is OPPOSITE to T16's: these prune
      the tree because map gens are not engine SOURCE, while `delta.py` keeps counting it for the
      merge ROUTE
      research: rendering
- [ ] T15 `check_village/__main__.py`'s default manifest RE-POINTED at the live reference hamlet -
      `pool/villages/` ceases to exist, so re-pathing it would aim the validator's out-of-the-box
      behavior at a frozen exhibit in the wrong tree (R6)
      research: rendering
- [ ] T16 `ci/delta.py` `_ENGINE_DIRS` gains the legacy tree, keeping the merge-route classification
      byte-for-byte identical (R3); extend `tests/tooling/ci/test_delta.py`, which already walks every
      path KIND and pins its classification
      research: rendering
- [ ] T17 `scripts/review-gate.sh`'s changed-manifest pattern reaches both trees, and
      `scripts/test-review-gate.sh` proves it. **Silent failure if missed**: the "a re-rolled map has
      a review logged beside it" guard would quietly stop covering the legacy tree (FR-020a)
      research: rendering
- [ ] T18 the remaining guard-script fixtures that construct pool paths -
      `scripts/test-sync-with-main.sh`, `scripts/test-make-only-hooks.sh`
      research: rendering
- [ ] T19 `Makefile`: the `GEN=`/`M=`/`A=`/`B=` defaults, `notes-census`' `$(wildcard)`, `verify`'s
      `git diff` glob, and `pool-index-if-stale`'s `find` - which must now watch BOTH trees, since the
      index covers both
      research: rendering
- [ ] T20 **`pyproject.toml`'s `[tool.ruff] extend-exclude`** - round 2's highest-value find, and the
      one whose failure is DESTRUCTIVE rather than silent: `legacy-hand-authored-pool` does not match
      the pattern `pool`, and `make done`'s lint and format phases rewrite in place without failing,
      so this feature's own gate would reformat all 18 frozen exhibits and breach FR-007/FR-009/SC-004.
      Also `[tool.coverage.run] omit`'s depth-sensitive `pool/*/*.gen.py`
      research: rendering
- [ ] T21 `make quick` green. Still the OLD tree - this is the checkpoint that proves Phase 2 changed
      behavior nowhere
      research: rendering

## Phase 3 - move ONE map (the reference-first step, constitution VI)

- [ ] T22 `git mv` the inashiro bundle into `pool/hamlets/inashiro/`; deepen its own `sys.path`
      arithmetic by one level
      research: rendering
- [ ] T23 prove it on the one map: `make map GEN=pool/hamlets/inashiro/inashiro.gen.py` green, the
      index rebuilt, its links resolving, and inashiro's moved files content-hash identical
      research: rendering

## Phase 4 - move the remaining 27

- [ ] T24 the 4 other scripted hamlets and the 5 magistracies into per-map folders under `pool/`
      research: rendering
- [ ] T25 create `legacy-hand-authored-pool/` and `git mv` all 18 frozen maps into
      `<tier>/<stem>/`, preserving the committed `.svg`/`.png` exhibits as RENAMES (FR-008)
      research: rendering
- [ ] T26 deepen the `sys.path` arithmetic in all 27 remaining gens - the 18 frozen ones included. A
      frozen gen that is silently broken is worse than one that is merely frozen
      research: rendering
- [ ] T27 collapse `/diagram/.gitignore` (R5): pattern rules for the live tree, `!` re-track for Mode A
      `.svg`, nothing ignored under the legacy tree; all 36 hand-written un-ignore lines deleted.
      Verify with `git check-ignore -v` on representative paths in both trees
      research: rendering
- [ ] T28 the index emits BOTH trees on one page with cross-tree links that resolve from a `file://`
      open (FR-016/017/018), keeping FR-019's properties (deterministic, derived columns, unknown
      folder still sectioned, missing manifest still red). Any closure over the tree being rendered is
      LIFTED to module level and unit-tested with plain dicts - dropping the test is not an option
      (GM 2026-08-28, feature 146)
      research: rendering

## Phase 5 - documentation, the found defects, and verification

- [ ] T29 **R10, Principle XIV**: `scripts/gate-stamp.py` cannot stamp inside a git worktree - it writes
      `<root>/.git/<name>`, but a worktree's `.git` is a FILE, so the Principle XIII baseline this
      feature is REQUIRED to take crashes it with `NotADirectoryError`, twice. Line 150 already guards
      `.is_dir()` for its memo cache, so the case was known and missed here. Resolve through
      `git rev-parse --git-common-dir`; `scripts/test-gate-stamp.sh` gains a real-worktree case
      research: rendering
- [ ] T30 `migration-plan.md` (FR-021): the new layout, and that a converted map MOVES TREES
      research: rendering
- [ ] T31 `dev/pool.md` (FR-022): what the two trees mean, what decides which tree a map goes in, and
      what a session does when a map is converted
      research: rendering
- [ ] T32 the remaining ~18 documents carrying literal pool paths - `SKILL.md`, `buildings.md`,
      `buildings/programs.md`, `dev/diagnostics.md`, `dev/loop.md`, `dev/placement.md`,
      `hamletgen.md`, `future-work/*.md`, `research/*.md`, the three package `CLAUDE.md` files,
      `wip/README.md`, and the `.notes.md` inside both trees
      research: rendering
- [ ] T33 SC-004: content-hash every moved file across the move, ASSERTED by script, not eyeballed.
      Only a `.gen.py`'s path arithmetic and a document's paths may differ
      research: rendering
- [ ] T34 SC-003 / FR-008: `git status` shows renames only, and the 18 exhibits are still tracked.
      28 maps before, 28 after
      research: rendering
- [ ] T35 SC-007: repo-wide sweep for surviving old two-level paths; every hit is either fixed or
      deliberately historical
      research: rendering
- [ ] T36 SC-006: rebuild the index, open it, and check every thumbnail, notes link and interactive
      link resolves - in the CLONE, where the renders actually are (research R8)
      research: rendering
- [ ] T37 **`make done` green, ONCE, at the end** (SC-005). Zero new failures against T01's
      2737 passed / 0 failed. The map sweep gates the same five scripted maps
      research: rendering
- [ ] T38 update `dev/lessons.md` with the two findings a future session would otherwise re-discover:
      that the stale-render sweep's "live hamlet render" message has not described what it checks
      since the 2026-08-16 freeze, and that a directory-prune tuple keyed on NAMES is a trap for any
      new top-level tree
      research: rendering
