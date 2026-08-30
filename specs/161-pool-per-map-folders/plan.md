# Implementation Plan: One folder per map, and the frozen hand-authored pool moved out of `pool/`

**Branch**: none - this project does not use feature branches. `SPECIFY_FEATURE=161-pool-per-map-folders` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/161-pool-per-map-folders/spec.md`

**Spec review status**: a `spec-fidelity` pass against the GM's verbatim request was dispatched
before this plan was written; its verdict is recorded in the spec's "Review history" section. No
task below may be implemented until that verdict reads FAITHFUL (constitution XVI, and
`scripts/review-gate.sh` refuses the push without it).

## Summary

The pool is flat: `pool/hamlets/` holds 65 files in which one map's five artifacts are scattered
across five alphabetical columns, and a frozen exhibit (`akagahara`) is indistinguishable from a
live scripted map (`inashiro`) without opening a file. This feature gives every map its own folder
and splits the tree in two - `pool/` for what is live (5 scripted hamlets, 5 Mode A magistracies),
`legacy-hand-authored-pool/` for the 18 frozen hand-authored exhibits - then brings every consumer
and every document along.

The technical core is NOT the move. It is that **~10 consumers each independently hardcode the
two-level shape** `pool/<tier>/<stem>.gen.py`, as a glob, an `os.listdir`, or a `join`. Deepening
ten hardcoded globs would satisfy the spec and leave the defect class intact for the next layout
change. Instead this feature adds **one discovery surface** to `pipeline/poolmaps.py` - already
declared "the single source of truth ... so they cannot drift apart" - and converts every consumer
to ask it. That is `migration-plan.md` section 6's "derive, don't pin" applied to the pool walk
itself, and it is what makes FR-013 (different consumers legitimately want different trees)
expressible instead of ad hoc.

## Technical Context

**Language/Version**: Python 3.14 (container pin), plus GNU make, git and `.gitignore` pattern rules

**Primary Dependencies**: none added. The feature touches `l7r/diagram/pipeline/`,
`l7r/diagram/tools/`, `l7r/diagram/check_village/__main__.py`, `l7r/diagram/ci/delta.py`, the skill
`Makefile`, `/diagram/.gitignore`, the test tree, and ~20 documents.

**Storage**: the filesystem tree under `.claude/skills/diagram/` and git's index. The 18 frozen
maps' `.svg`/`.png` (~195 MB) are committed write-once exhibits and must survive as renames.

**Testing**: pytest via `make quick` (unit, testmon-selected) and `make done` (integration).
`tests/test_villages.py`'s ratchet is the existing guard that every pool gen is accounted for; it
becomes the guard that every map is accounted for in the RIGHT TREE.

**Target Platform**: the dev container; the index is additionally opened from a plain `file://` URL
on the GM's laptop, which is what makes FR-018's relative-link requirement real rather than academic.

**Project Type**: repository restructuring plus the tooling that walks the restructured tree.

**Performance Goals**: none. No generator logic changes; no map is re-rolled. The one measurable
cost to watch is that the discovery surface is called on hot paths (the gate's map sweep, the render
cache's freshness check) and must not turn an `os.listdir` into a repeated deep walk.

**Constraints**: FR-007 - pure relocation. Every moved file's bytes unchanged except a `.gen.py`
whose own path arithmetic must deepen and a document that names a path. No manifest or render
rewritten. Verified by content hash, not by eye.

**Scale/Scope**: 28 maps (23 Mode B settlements, 5 Mode A plans) = 28 new directories; ~120 files
moved; ~20 code files and ~20 documents edited; 36 `.gitignore` lines deleted.

**Single-artifact target** (constitution VI): **not applicable in its usual form, and this is worth
stating rather than skipping.** That requirement exists so a generator change is proven on ONE map
before a sweep. This feature changes no generator and rolls no map - FR-007 forbids re-rolling
anything. The analogous "one artifact first" discipline still applies and is planned as such: the
discovery surface and the tree shape are proven on **`pool/hamlets/inashiro/`** alone (moved first,
`make map GEN=pool/hamlets/inashiro/inashiro.gen.py` green, index rebuilt and opened) before the
other 27 maps move. Inashiro is the reference hamlet and rebuilds in ~15 s.

**Every step is two steps.** Phases 3 and 4 below are exactly this split: Phase 3 moves and proves
ONE map; Phase 4 moves the remaining 27 and re-proves across both trees. Neither is complete without
the other, and Phase 4 is not started until Phase 3 is green.

## Performance bookends (constitution VI)

**N/A - with the reasoning, because "N/A" on a required bookend is the kind of thing that should
never be a bare assertion.** The bookend exists to catch a generator getting slower. This feature
changes no code that runs during a roll: `poolmaps`, `pool_index`, the `.gitignore` and the docs are
outside the generation path entirely, and the two files that ARE on a hot path (`render_cache`,
`gencache`) change only their directory-pruning tuple and their discovery call - neither is inside a
per-candidate or per-feature loop.

Two guards make this checkable rather than assumed:

1. `tests/test_villages.py` already enforces a **per-gen CPU budget** (the 2026-08-03 Minami
   incident: a gen silently became a 45-minute grind and nothing failed). That budget runs at the
   gate under this feature unchanged, on the same five scripted maps, and is the measurement that a
   roll did not get slower.
2. If the gate's wall time moves by more than a few seconds against the last recorded green run, the
   bookends get taken after all rather than argued about. Named here so the trigger is written down
   before the number is seen.

## Constitution Check

*GATE: passed before Phase 0. Re-checked after Phase 1 - see "Post-design re-check" below.*

- **I. Accessibility-First Viewports**: **N/A** - no UI in this repository (constitution 2.0.0).
  `pool/index.html` is a derived, gitignored local browsing artifact opened over `file://`, not a
  served page; it has no viewport suite and gm-assistant's `dom_audit.py`/`screenshot.py` do not
  live here. It still owes FR-018 (every link resolves) and FR-019 (deterministic output), which are
  verified in Phase 5 by opening the page and by an automated link check.
- **II. Bold, Intentional Design**: **N/A** - same reason. The index's visual style is unchanged by
  this feature apart from the new tree headings required by FR-017.
- **III. Pool Data Conventions**: **N/A for the frontmatter clause** - that clause governs
  markdown-with-YAML generated content (chargen and its kin). The `/diagram` pool is code, manifests
  and renders, and has never used that format. **But the directory-layout half of this principle is
  precisely this feature's subject**, and the layout it lands is specified in FR-001 to FR-006 and
  in `data-model.md`. No city is baked into anything; no frontmatter exists to bake it into.
- **IV. One Canonical Home for GM Source**: **N/A** - this feature moves no SOURCE block. Verified
  in Phase 0 by grepping the moved set for `SOURCE: GM NOTES`; the finding is recorded in
  `research.md` R7 rather than assumed.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: **PASS**. No task modifies content inside
  SOURCE markers. The `.notes.md` files move and some have their internal path references updated
  (FR-020); any edit inside a SOURCE block is forbidden, and `scripts/source-block-hooks.sh`
  enforces containment against the file on disk, so a slip is refused rather than reviewed.
- **VI. Verify Before Reporting Done**: **PASS**. Every phase names its verification; Phase 5 is
  nothing but verification, and it is scheduled as tasks rather than as a closing paragraph. The
  reference-then-pool split is Phases 3 and 4. `settlement-review` is **N/A** here and the reason is
  recorded: that agent judges what a MAP looks like, and this feature changes no map's pixels
  (FR-007 makes every render byte-identical). Per the GM's own ruling (2026-08-29, "settlement-review
  is not per-map ... they read the map themselves"), dispatching it on a delta that moved no ink
  would burn ~17 minutes to confirm nothing changed; the push uses `REVIEW_GATE_OK` with the GM's
  words and the byte-identity evidence.
- **VII. De-Localized Generation by Default**: **N/A** - no pool content is generated.
- **VIII. Direct Voice Over Framing Distance**: **N/A** - no in-world content is written.
- **IX. Setting Integration**: **N/A** - no setting detail is asserted, invented or moved. No new
  named figure.
- **X. Python Discipline (NON-NEGOTIABLE)**: **PASS, with three commitments made explicit**:
  - `ruff check`, `ruff format --check`, `pyrefly` (mypy-strict rule set) and `pytest` with
    `--cov-fail-under=100` all run under `make done`. New code in `poolmaps.py` is small and pure -
    a directory walk returning dataclass-ish records - which is exactly the shape that reaches 100%
    from plain unit tests over a `tmp_path` tree.
  - **Red-green** on the discovery surface: its tests are written and FAIL before it exists
    (T09 before T10), and the classification-at-new-depth test (FR-011) is written against the OLD
    tree first, where it must fail, so it is proved to have teeth.
  - **No inner function left untested** (GM 2026-08-28, feature 146): if the index's two-tree
    rendering wants a closure over the tree being rendered, it is LIFTED to module level with its
    captured values as parameters and tested with plain dicts. Dropping the test is not an option.
  - **File size** (clause 13): `pool_index.py` is 296 lines and gains the two-tree sectioning -
    nowhere near ~1,000. `poolmaps.py` is 92 lines and roughly doubles. Neither approaches the
    threshold; no split is planned and none is needed. Clause 14 (derive, don't maintain) is not
    merely satisfied but is the feature's whole method: the ten hardcoded pool walks ARE a roster
    restating what one module could declare, and they are being derived rather than maintained.
- **XI. Japanese Authenticity**: **N/A** - no kanji surfaces. The map names that appear in paths are
  existing names, unchanged.
- **XII. Historical Grounding Bookends (NON-NEGOTIABLE)**: **N/A, and the spec says so positively
  rather than by omission.** This feature changes nothing a generator asserts about the world: no
  glyph, size, placement rule, distance or density moves, and every render is byte-identical
  (FR-007). The spec's "Decisions Recorded" table is kept and explicitly empty for exactly this
  reason. Every task is classified `research: rendering` and carries no research checkboxes, because
  no question about how a place was built, farmed, planted or lived in arises anywhere in the work.
  - [x] **XII, decisions for the reader**: nil return, recorded as a nil return in the spec.
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: **PASS, with a measured baseline scheduled as
  T01** - and this feature needs the baseline more than most, because it touches shared discovery
  code that ten consumers ride:
  - Baseline command: `git worktree add --detach /tmp/base161 HEAD` then `make done` in
    `/tmp/base161/.claude/skills/diagram`, recorded in `research.md` R8 with the pass/fail counts.
    A detached worktree, never a stash (a stash mutates the tree under the review agent currently
    reading it).
  - **The known worktree trap applies here with unusual force and is planned for.** A fresh worktree
    carries no gitignored artifacts, so the live maps' `.svg`/`.png`/`.html` are absent there while
    the clone has them. Two named tests read renders off disk and skip when absent -
    `test_villages.py`'s render-aspect sweep (`if not (isfile(svg) and isfile(png)): continue`) and
    the index's "render not synced" path. In the worktree they will silently pass by skipping. The
    baseline therefore records, per test, whether it RAN or SKIPPED, and any test that skips in the
    baseline is re-measured in the clone before the move. This is the reverse-direction failure the
    project's own rule warns about - a test that passes only in the worktree hides a real regression
    from the moment the baseline is taken.
  - **Zero new failures at merge.** Per-seed comparison is fully preserved here (no re-roll, no
    rotation), so the rule applies in its strict form: anything that passed before and fails after
    is a regression and blocks.
- **XIV. Fix Defects Where You Find Them (NON-NEGOTIABLE)**: **one already found and fixed.** The
  two Python lockfiles pinned conflicting numpy versions (`requirements.txt` 2.5.1 via shapely,
  `requirements-dev.txt` 2.5.2 via types-shapely) and `setup-dev-env.sh` installs both in ONE pip
  command, so `pip` refused the whole install and a fresh container could not be provisioned at all.
  Fixed in commit `81641618` with the dev compile constrained to the runtime lock (`-c
  requirements.txt`) so the drift cannot recur, and the why recorded beside it. Any further defect
  the work surfaces is fixed in this feature, not filed.
- **XV. Keep Going**: acknowledged. The stop-and-ask calculus was exercised ONCE, before any
  implementation, on the two questions that had no defensible default (filenames inside a map folder;
  one index or two). Both are recorded as GM decisions in FR-002 and FR-016. Nothing else in this
  feature is worth a stop.
- **XVI. Do the Literal Thing; a Spec is Reviewed by Someone Else**: the spec was handed to
  `spec-fidelity` with the GM's request VERBATIM before this plan was written, and the review was
  asked specifically whether the one interpretive move in the spec - reading "no plans to become
  hand-authored" as "no plans to become SCRIPTED" - is defensible or is a session substituting its
  judgment. Implementation waits on the verdict.
- **XVII. A README is the GM's to Write**: **N/A** - no README is added. `legacy-hand-authored-pool/`
  gets no README; what the tree means is recorded in `migration-plan.md` (FR-021) and `dev/pool.md`
  (FR-022), which are the documents a session actually reads.
- **XVIII. Every Guard Has a Test Companion**: no new guard script is added, so no new companion is
  owed. The two guard-adjacent lists this feature touches - the engine-fingerprint prune lists and
  `ci/delta.py`'s `_ENGINE_DIRS` - already have companions (`tests/tooling/ci/test_delta.py` walks
  every path KIND and pins its classification), and T14/T16 extend those companions to the new tree
  rather than adding a parallel guard.

**No DEFERRED gates. No Complexity Tracking entries** - nothing in this plan needs a justified
violation.

## Post-design re-check (after Phase 1)

Re-run once `data-model.md` and `contracts/pool-discovery.md` exist. The design adds one module-level
API and deletes 36 ignore lines; it introduces no new project, no new dependency, no new layer, and
no new guard. Principle X's file-size and derive-don't-maintain clauses come out BETTER after the
design than before it (ten hardcoded walks become one declared surface), which is the outcome clause
14 is written to produce. **Re-check status: PASS, unchanged.**

## Project Structure

### Documentation (this feature)

```text
specs/161-pool-per-map-folders/
├── plan.md                        # this file
├── spec.md                        # the requirements, + the fidelity verdict
├── research.md                    # Phase 0: the design decisions and what was rejected
├── data-model.md                  # Phase 1: the two trees, the bundle, the invariants
├── contracts/
│   └── pool-discovery.md          # Phase 1: the one discovery surface every consumer calls
├── quickstart.md                  # Phase 1: how to move a map between trees afterwards
├── checklists/requirements.md     # spec quality checklist
└── tasks.md                       # Phase 2, written by /speckit-tasks
```

### Source layout this feature lands

```text
.claude/skills/diagram/
├── pool/                                   # LIVE: regenerated and gated
│   ├── index.html                          # derived, gitignored - ONE page over BOTH trees
│   ├── hamlets/
│   │   ├── inashiro/                       # inashiro.gen.py .json .notes.md .svg .png .html
│   │   ├── kashikawa/  mizuguchi/  sawada/  kuwabata/
│   ├── magistracies/                       # Mode A, hand-authored BY DESIGN
│   │   ├── county-magistracy-example/      # <stem>.gen.py .notes.md .svg (tracked) .png
│   │   ├── hayakawa-magistracy/  ochiba-magistracy/
│   │   ├── ochiba-roundtrip-test/  ubame-magistracy/
│   └── regressions/                        # UNCHANGED, flat: 107 negative fixtures, not maps
│
└── legacy-hand-authored-pool/              # FROZEN exhibits: never regenerated, never re-gated
    ├── hamlets/     akagahara/ enokida/ honda/ ikegami/ moritono/ shimizu/ tanada/ yatsuda/
    ├── villages/    hikari-no-sato/ hoshigaoka/ kikuta/ ueda/
    ├── towns/       hirameki/ hoshizora/ ubame/
    └── provincial-cities/  minami/ nagahara/ tango/
```

Note what disappears: **`pool/villages/`, `pool/towns/` and `pool/provincial-cities/` cease to
exist**, because every map they held is frozen. That is not a side effect to absorb quietly - it
breaks any default that names one, and `check_village/__main__.py`'s default manifest is exactly
such a default (`pool/villages/kikuta.json`). It must be RE-POINTED at a live map, not re-pathed.

**Structure Decision**: two sibling trees inside the skill directory, each `<tree>/<tier>/<map>/`,
with the map's stem preserved as every file's basename (FR-002). The tier level is kept in both
trees because it is how the GM reads the pool and how the index sections it; the map level is the
new one. `pool/regressions/` keeps its flat shape (FR-006) because its contents are fixtures, not
map bundles - there is no bundle to fold.

## Phases

Each phase's tasks are enumerated by `/speckit-tasks`. All tasks are `research: rendering`.

- **Phase 0 - Baseline and research** (`research.md`). Take the measured regression baseline in a
  detached worktree, recording per-test RAN-vs-SKIPPED. Settle the seven design questions (the
  discovery surface's shape; move-first vs dual-support; the `ci/delta.py` decision; the
  `.gitignore` collapse; the `check_village` default; the SOURCE-block sweep; the index's two-tree
  form). Nothing is implemented in this phase.
- **Phase 1 - The discovery surface, red-green, no files moved yet.** Write the failing tests, then
  `poolmaps`' discovery API. The tree is untouched, so the whole existing suite must stay green
  throughout - this phase is provably safe and is where the risk is bought down.
- **Phase 2 - Convert every consumer to the surface, still no files moved.** Each consumer stops
  hardcoding a shape and starts asking. The suite stays green because the surface still describes
  the CURRENT tree. This is the sequencing choice justified in `research.md` R2: at no point is the
  repository in a state where `make done` cannot run.
- **Phase 3 - Move ONE map** (`inashiro`) and make the surface describe the new shape for it.
  Prove: `make map GEN=...` green, index rebuilt and links resolve, content hashes identical.
- **Phase 4 - Move the remaining 27**, create `legacy-hand-authored-pool/`, collapse the
  `.gitignore`, re-point the defaults that named a now-legacy map.
- **Phase 5 - Documentation and verification.** ~20 documents; then the whole verification battery
  (content hashes, `git status` renames, `git check-ignore -v`, the old-path sweep, the index
  opened, `make done`).

## Complexity Tracking

No entries. The Constitution Check has no violations to justify.
