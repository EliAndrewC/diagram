# Research - 231 Review only when the layout moved

TOOLING research, nothing physical. Measured on feature 228's session transcript and the repository on
main, 2026-09-12.

## R1. What feature 228 cost, and where

Feature 228 (the crop dike lit as a ring: one path's `d`, a unit test, a regenerated map whose manifest
was byte-identical) took 32.1 minutes of wall clock. From the transcript's timestamps:

| phase | min | share |
|---|---|---|
| waiting on the settlement-review (73 tool calls; the gate itself green at 2.5 min) | 18.7 | 58% |
| the session's own model turns (36 tool calls) | 9.6 | 30% |
| spec written, spec-fidelity (2.1 min, idle for 1.8 of it) | 3.8 | 12% |
| the pair guard refusing the review `make verify` had just asked for, then the stop hook firing on the escaped dispatch | 1.8 | 6% |
| a scratch pixel-check script, four attempts | 1.7 | 5% |
| tool execution, everything | 1.0 | 3% |

The reviewer's own timeline: about 8 minutes rendering both SVGs at full size and building class masks,
2 minutes waiting for pool renders that the gate had evicted (feature 223's snapshot practice, not
followed), 3 minutes writing its own page-lighting measurement, 2 minutes of per-pond comparison, and a
spelling sweep. Its two new numbers (the water area lit 100% -> 6.2%; the earth mottle a third of the
rim) did not change the map.

## R2. Why the pair guard read the wrong tree

`scripts/pair-hooks.sh` `find_root` is `git rev-parse --show-toplevel` from the hook's cwd. The
session's shell stood in `/diagram` (the mirror) - a subagent's shell starts there, and a session's does
until it cds out - so the guard computed the MIRROR's engine key, read and wrote the mirror's
`.git/pairing-state.json` (which holds a `gate_key` and a `waived_key` for the mirror's own tree),
found no gate for the clone's content, and refused the review. The escaped dispatch (`PAIR_OK` in the
prompt) is logged as a bypass and records no `review_key`, so at turn end the stop branch, by then
reading the clone (feature 204's main-tree guard had moved the shell), found the gate green with no
review recorded. Feature 204 solved the same cwd problem for the main-tree guard with
`clone-sync-hooks.sh resolve` (the claim map, then the transcript's last rename, then the sessions json;
a subagent resolves to its parent's clone).

## R3. What "the layout moved" is, in the repository's own terms

A pool map's manifest (`pool/*/*/*.json`, `legacy-hand-authored-pool/*/*/*.json`) is the record of every
placed feature's geometry; the SVG, the PNG and the page are derived from it and from the drawing
code. `review-gate.sh` already uses the manifest as the unit at push time (a changed manifest needs
its notes touched in the same push), and `make verify` already prints "maps whose manifest changed" -
over `HEAD~1..HEAD`, which sees only the last commit. The gate's pool phase obtains each shipped map
through the gen cache and regenerates it IN PLACE when the engine key moved (`tests/gate/_pool.py`
`obtain`, `gencache.gate_obtain`) - which is why the clone's Kuwabata `.json` and `.svg` carried the
gate's 13:00 timestamp and its `.png`/`.html` were evicted - so by the time a gate is green, the
manifests in the tree are the layout the engine now produces. A manifest diff against the merge base
with `origin/main` (committed or in the working tree) is therefore a sound, scripted answer to "did any
settlement's layout change": empty means nothing placed moved, and a settlement-review would re-judge
ink it already judged.

What the diff does NOT see: a change to a glyph's FORM with the same manifest (a redrawn well glyph,
this feature's ring). Those are the GM's to look at - the 2026-08-29 ruling that they read the one
changed map faster than the agent does - and `make verify` says so when it waives.

## R4. What the reviewer needs handed to it

Two measurements the reviewer rebuilt from scratch on feature 228, both general:

- **the page, one class lit** - which OTHER classes' pixels change when class K is lit, as a share of
  each class's on-screen pixels. The page already carries a class id map (`raster.id_map`: one red
  value per class at 1 px per map px, `payload.raster.idmap` + `palette` + `step`) and exposes
  `window.l7rMap.highlight`, `mode` and the SVG's screen transform; a screenshot diff attributed
  through the id map answers the question for any class with no manifest polygons at all.
- **the picture, before and after** - the share of differing pixels between two renders, the max
  channel delta, the bounding box, and which class's ink the differing pixels lie on or near
  (through the same id map of the new SVG).

The snapshot the reviewer needed: the changed maps' `.json/.svg/.png/.html/.notes.md` from the clone
beside main's copies from the mirror, somewhere the gate's cache does not evict (`.git/` of the clone).
