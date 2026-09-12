# Feature 231 - review only when the layout moved

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5; round 1 CHANGES REQUIRED on FR-002's dispatch clause, its aside on FR-005 taken) - implementing.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - where feature 228's 32 minutes went, why the pair guard
read the mirror, what "the layout moved" is in this repository's own terms, and what the reviewer
rebuilt by hand.
**Predecessors**: 151 (the gate and the review run together), 164/212 (the pair guard rewrites and
permits), 204 (a guard resolves the session's clone, never the cwd), 223 (review a snapshot of the pool
beside a detached gate), 193 (the reviewer parses, looks and judges; it is handed no verdict).

## Summary

The GM, after feature 228: a settlement-review of a change that moved nothing in the layout took nearly
twenty minutes and should not have been triggered at all; the pair guard's refusal should be made
impossible or auto-corrected the way the main-tree guard corrects a `cd` into the mirror; the pool
snapshot the reviewer needs should happen automatically; and the reviewer should be given the tools it
keeps rewriting. So: a scripted check decides whether a settlement-review is owed - a pool manifest
changed against main - and every place that asks the question asks that check; the pair guard resolves
the session's clone; `make verify` snapshots the changed maps for the reviewer; and two measurement
tools, with `make` targets, replace the scratch scripts.

## Functional requirements

- **FR-001 The trigger is scripted.** One script, `scripts/review-owed.py`, prints the pool maps
  whose manifest differs from the merge base with `origin/main` - committed or uncommitted, both pool
  trees, a new map counted as changed - and exits 0 either way; `--why` prints the base and the
  ruling in one line. It is the ONLY place the question "is a settlement-review owed" is answered,
  and it is asked FRESH at every decision point (never recorded at the start of a gate: the gate's
  pool phase can move a manifest, and the answer must follow the tree).
- **FR-002 No layout change, no review.** When the script finds no changed manifest: a plain
  `make done` is permitted as it is (not rewritten to `make verify`), told in its context that no
  settlement-review is owed because no pool manifest moved against main and that a glyph-only
  change is the GM's to look at; a `settlement-review` dispatch is judged exactly as today - the
  feature-151 rule that a review needs a gate running or freshly green is untouched, and this feature
  adds no new refusal of a dispatch merely because no review is owed; the stop branch stays quiet; and `make verify` says the same and starts the gate. The
  automatic waiver is RECORDED (the pairing state's `waived_key` with the reason
  `no pool manifest moved against <base>`, and the guard log) so `make audit` can count it.
- **FR-003 A layout change owes the review, as today.** When the script names changed maps, every
  existing behavior stands: the rewrite to `make verify`, the DISPATCH NOW context, the stop branch's
  half-open refusal, the `PAIR_OK` escape with a reason.
- **FR-004 The guard resolves the session's clone.** `pair-hooks.sh` finds its tree through
  `clone-sync-hooks.sh resolve` (the payload's session_id; a subagent resolves to its parent's clone),
  and only when that answers nothing through the cwd's git root as today. The key, the pairing state
  and the verification record are all read from that tree. And a `settlement-review` dispatched with
  `PAIR_OK` in its prompt is still a review: the escape branch records `review_key` as the normal
  branch does, beside the bypass it already logs.
- **FR-005 The snapshot is automatic, on every gate shape.** Wherever a review is found owed at gate
  time - `make verify` itself, and the pair guard on every gate shape it rewrites or permits (a plain
  `make done` becoming `make verify`, a detached gate, `make maps`, `FULL=1`) - the changed maps are
  snapshotted before the gate starts: for every map the script names, the clone's `.json`, `.svg`,
  `.png`, `.html` and `.notes.md` and main's copies from the mirror are copied into
  `<clone>/.git/review-snapshot/<map>/clone/` and `.../main/`, the previous snapshot of that map
  cleared first, and the two directories are printed in the DISPATCH NOW line (the guard's context and
  `make verify`'s output alike). A render missing in the clone (`.png`/`.html` are gitignored and may not have been
  regenerated) is named as missing, never silently skipped. The reviewer's instructions say to review
  the snapshot when one is named, and why (the gate evicts the pool's renders).
- **FR-006 The reviewer's tools.** Two modules under `l7r/diagram/tools/`, each with a `make`
  target and a row in the tools index:
  - `page_lit` (`make page-lit MAP=<page.html> CLASS="<key>" [VECTOR=1]`): opens the page headless,
    lights the class, and reports for every class on screen the share of its pixels that changed -
    attributed through the page's own id map and the SVG's screen transform - in raster mode at the
    opening view, and past the raster switch with `VECTOR=1`; writes the lit screenshot beside the
    page or where `OUT=` says.
  - `picture_diff` (`make picture-diff A=<png|svg> B=<png|svg> [SVG=<the new svg>]`): renders an SVG
    argument with the engine's own rasterizer at the other's size when needed, and reports the share
    of differing pixels, the max channel delta, the bounding box, and - when the new SVG is given -
    the share of differing pixels lying on each class's ink, the rest as "off any class".
  Both are measurement, never verdict (feature 193's ruling stands); both are unit-tested on synthetic
  arrays, and `page_lit`'s browser path on the synthetic page the browser tests already drive.
- **FR-007 The doctrine says so.** The settlement-review agent file gains the trigger rule (when it
  is dispatched at all), the snapshot's place in its inputs, and the two tools in its tooling section
  in place of hand-built scripts; `dev/reviews.md` "WHEN a review runs", the pair row in `CLAUDE.md`
  and `docs/efficiency-tooling.md`'s `make verify` line are updated to the rule; `make verify`'s own
  help line says it decides.
- **FR-008 Tests.** `scripts/test-pair-hooks.sh`: with no changed manifest a plain gate is permitted
  untouched and the stop branch is quiet, and the waiver is recorded; with a changed manifest every
  existing case holds; a payload whose cwd is another tree resolves to the session's clone and writes
  that clone's state; the escaped review records `review_key`. `tests/tooling/test_review_owed.py`:
  the script on git fixtures (a committed change, an uncommitted one, a new map, nothing changed, both
  trees, no `origin/main`). `tests/tools/test_page_lit.py` and `test_picture_diff.py`: the pure
  attribution and diff functions; the snapshot's copy and missing-render report as a unit test of the
  script that does it. Every guard suite green (`make hooks-test`), the gate green.

## Success criteria

- **SC-001** Feature 228's delta replayed (the ring commit, byte-identical manifest): `make done` is
  permitted with the no-review context, the stop hook is quiet, the waiver is on record.
- **SC-002** A delta that moves a manifest (a pool `.json` edited in the fixture): the review is owed
  exactly as before, and `make verify` names the snapshot directories, with the missing renders named.
- **SC-003** From a shell standing in the mirror, the pair guard reads and writes the session's
  clone's state (the fixture's claim map names the clone); the mirror's state file is untouched.
- **SC-004** `make page-lit` on Kuwabata's page with `CLASS="mulberry dike"` reports the mulberry dike
  at 100% and the fish pond at about 6%, matching the reviewer's hand measurement; `make picture-diff`
  on main's and the clone's Kuwabata renders reports the 0.14% within the pond classes' ink.
- **SC-005** `make hooks-test` and `make done` green.

## Decisions Recorded

- **D1 - the manifest is the layout.** The unit is the one `review-gate.sh` already uses at push and
  `make verify` already prints; a glyph-form change with the same manifest is not reviewed by the
  agent, by the GM's 2026-08-29 ruling that they read one changed map faster than it does. The waiver
  says so, so the session tells the GM to look.
- **D2 - asked fresh, never cached.** The gate's pool phase can change the answer mid-run
  (research R3), so the check runs at each decision point; recording the waiver is for the audit, not
  for the decision.
- **D3 - the snapshot lives in the clone's `.git/`**, not the scratchpad: `make` has no session
  payload, and `.git/` is where the pairing state and the gate baseline already live; the cache never
  evicts there.
- **D4 - the tools measure and do not judge** (feature 193): `page_lit` reports shares per class,
  `picture_diff` reports shares per class; neither says pass or fail.
- **D5 - `make verify` keeps its name and shape**; a session that types `make done` on a delta with no
  layout change simply runs the gate, which is what the GM asked for.
