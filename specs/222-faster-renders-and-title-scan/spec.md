# Feature 222 - faster renders and an indexed title scan

**Status**: IMPLEMENTED 2026-09-11 (regen per pool hamlet 17-28 s -> 11-19 s, Kuwabata 27.9 -> 14.1; its hinterland stage 10.0 -> 1.6 s with byte-identical manifests; the SVG 16.4 -> 9.4 MB; the picture's encode child 2.9-5.2 s -> 0.5-0.8 s; the PNG render fully hidden under the page's work; `make map PROFILE=1` prints again - research R2). `spec-fidelity` round 1 FAITHFUL (D1 legitimate; FR-005 under Principle XIV), round 2 FAITHFUL on FR-008/D6 with two amendments (SC-1, D5), round 3 FAITHFUL. SC-2 missed on Kuwabata (4.10 s, its resvg render alone 3.56) and SC-4 on Mizuguchi by 0.1 s - both reported in R2, neither reached for. `make done` green (3,521 tests, 100% coverage, roll census green).
**Request**: [`request.md`](request.md) - the GM's words after the 2026-09-10 end-to-end profile
(`.claude/skills/diagram/dev/performance.md`, last section). **Research**: [`research.md`](research.md)
- the measurements before (R1, from the profile) and after (R2). **Predecessors**: 200 (the page's raster
picture and id map), 199 (the merged scatter paths, tiled), 208 (the picture's encode in a child), 218
(the hinterland scatter indexed - the work the GM remembered), 151 (`make map PROFILE=1`), 213 (the roll
in a child).

## Summary

The profile found that the engine stages are under half of a pool hamlet's regeneration: the page's
low-zoom picture costs 6.4-7.8 s on every map (about 4 s of it the lossless WebP encode), the PNG render
2-3 s, and the SVG is 13-16 MB of which 89% is 268,000 individual `<line>` grass and reed blades that
resvg parses three times per gen. Inside the stages, Kuwabata's hinterland spends 8.7 of its 10 s in the
title-pocket scan, which tests every candidate box against every edge of every obstacle. The GM approved
four of the levers offered; this feature delivers exactly those four. Anything else the profile ranked
(the bamboo scan, the wells key, `RASTER_R`, not emitting the off-map scatter) is NOT in scope.

## Functional requirements

- **FR-001 Each blade group is written as merged paths.** The commons grass bucket
  (`settlement/land/cover.py`, `<g stroke="#A7A860" ...>`) and the marsh reed bucket
  (`settlement/land/wet.py`, `<g stroke="#6E9377" ...>`) are written to the SVG as `<path>` elements in
  the page's own merge grammar (`interactive/page.py` `merge_primitives`: `M x,y L x,y` subpaths,
  `fill="none"`, the group's stroke) instead of one `<line>` per blade. The ink is identical - a path of
  M/L subpaths draws the same strokes - and the SVG, the PNG, the page's picture and its id map all read
  the smaller file. The page's later `merge_primitives` pass finds paths and leaves them, so the page
  carries what it carried; `drop_offmap` already judges merge-grammar subpaths and `_MARK_XY` already
  reads `M x,y`, so the scrub's hit region and the off-map drop are unchanged. The two readers that parse
  blade roots from `<line x1= y1=` - `tools/scatter_audit.py` and `tests/settlement/test_wet_ground.py`
  - read `M x,y` subpath starts as well. See D1 for the tiling question.
- **FR-002 The page's picture is a lossy JPEG.** `interactive/raster.py` `picture` returns the resvg
  render encoded as JPEG (in the same child process feature 208 introduced, for the same memory reason)
  at the quality and chroma subsampling recorded in D2, and the page embeds it as `image/jpeg`. The id
  map stays a PNG (a lossy id map would alias classes). `RASTER_R` stays 3. This supersedes specs/200 D2
  ("lossy WebP rings on line art and was declined") by the GM's own words on 2026-09-11, which also
  record the reversal clause: *"If we don't like it or if the lossy nature means that it becomes blurry
  or otherwise bad, then we can always reverse it."* The encode settings live in one place so reversing
  or retuning is one edit.
- **FR-003 The three renders run concurrently.** The PNG render (`finish.render_png`, resvg at 2600 px
  from the written `.svg`), the picture (resvg at `RASTER_R` plus the encode child) and the id map
  (resvg at zoom 1) are independent subprocess-bound steps run in sequence today. `finish()` starts the
  PNG render as soon as the `.svg` is written and joins it after the `.json` is written; `render_page`
  runs the picture and the id map at the same time. Every output is byte-identical to the sequential
  form; a failed render still raises out of `finish()`; `DIAGRAM_SKIP_RENDER` and `render=False` behave
  exactly as before (nothing to run concurrently). Peak memory rises only where renders happen - `make
  map`, `make maps`, render-sync - never on a gate roll, which renders nothing (feature 208).
- **FR-004 The title-pocket scan is indexed.** `Settlement._title_obstacles` returns an index built once
  per call - the rects as they are, and for every obstacle polygon and line a bounding box plus every
  edge filed in a `PointGrid` (`settlement/_geom/indexes.py`) - and `Settlement._box_clear` asks the
  index: only obstacles whose box meets the candidate box are tested, and only the edges the grid returns
  near it, by the same `point_in_poly`, vertex-in-box and `segments_cross` tests as today. The index
  prunes, the exact test decides: every verdict is the linear scan's, so no map moves. All four callers
  (`_blank_label_spot`, the outside-pocket tries in `hinterland/frame.py`, the preferred-pocket check
  and the corner fallback in `title()`) go through it unchanged in meaning.
- **FR-005 The stage profile reaches the terminal again** (constitution Principle XIV - a defect found
  while doing this work is fixed in it). `make map ... PROFILE=1` has printed nothing since feature 213
  moved the roll into a child whose stderr `rollcache._in_child` captures and discards on success. The
  child's stderr is forwarded to the parent's when the stage profile is requested, so the GM's instrument
  from feature 151 works from `make map` as documented.
- **FR-008 The title's cover fallback works** (Principle XIV, found while reading `_title_obstacles` for
  FR-004). Feature 137 T06 gave `_title_obstacles(cover_ok=True)` the meaning "the belt, the bamboo and the
  woodland commons are not obstacles" - the last resort `title()` and `_blank_label_spot` try before the
  corner fallback - but the method's second half is a leftover copy of its first: it appends the placed
  labels a second time and the groves, bamboo stands, marshes and woodland UNCONDITIONALLY, so `cover_ok`
  has never excluded anything and the cover rung of the ladder is dead. The duplicate block is removed; the
  fields loop after it stays. Which pool maps this moves (a title that now finds a seat on cover instead of
  falling to a corner or the title band) is measured at T02 and recorded in R2; a moved title is reported to
  the GM by name.
- **FR-006 Measured before and after, per hamlet.** Each pool hamlet's regeneration is timed the way the
  profile timed it (R1's numbers are the before) and recorded in R2 with the SVG and page sizes; the JPEG
  gain is stated against the GM's "about four seconds".
- **FR-007 Verification.** `make done` green; the pool regenerated; the moved manifests carry the same
  geometry (the `ink_classes` census counts paths where it counted lines) and the pages a JPEG picture -
  see D5 for the review gate.

## Success criteria

- SC-1 Kuwabata's `stage_hinterland` under 2 s (10.0 s before); no pool map's houses, lanes, fields,
  water or cover move. The manifests differ in the `ink_classes` and `unclassed_ink` counts, and - only on a
  map whose title FR-008 moves - in `title`, and in `meta.title_band` and the view (so the crop and the
  rendered sheet) where a title band is dropped or added. Nothing else.
- SC-2 The page's picture step under 3.5 s on every pool hamlet (6.4-7.8 s before), the JPEG encode
  itself under 0.5 s where the lossless WebP was about 4 s.
- SC-3 A pool hamlet's `.svg` under 10 MB (13-16 MB before; R1 measured the merged form of Inashiro's at
  9.37 MB - the draft said 5 MB against its own number, corrected at T07); each resvg pass at least 0.8 s
  faster, measured on the TILED form.
- SC-4 Regeneration wall time per pool hamlet down by at least 6 s on every map, by at least 12 s on
  Kuwabata.
- SC-5 `make map GEN=... PROFILE=1` prints the stage profile.

## Decisions Recorded

- **D1 The writer emits the page's tiles, not literally one path.** The GM said *"merging each blade
  group into one path"*. Feature 199 tiles a merged scatter into one path per tile cell so the browser
  paints only the visible tiles; a single path per group in the file would arrive at the page already
  merged and, since `merge_primitives` leaves paths alone, untiled - a paint regression on the page for
  no gain on the file, where resvg does not care how many paths hold the subpaths. So the writer calls
  the page's own `merge_primitives` on each blade group, which yields one path per tile (the same tiling,
  grammar and bytes the page produced from the lines), and a group under `TILE_MIN` blades becomes one
  path exactly as the GM said. Put to `spec-fidelity` as the one place this reads the request's goal
  over its letter.
- **D2 JPEG quality 90, chroma 4:4:4.** Measured on Inashiro's 26-Mpx picture (R1): lossless WebP
  method 0, 4.12 s, 3.87 MB; lossy WebP q90, 0.93 s, 2.32 MB; JPEG q90 4:2:0, 0.10 s, 3.58 MB; JPEG q90
  4:4:4, 0.15 s, 4.56 MB; JPEG q95 4:4:4, 0.18 s, 6.39 MB. 4:4:4 keeps full chroma resolution on the
  map's thin colored strokes (a 0.8 px blade is 2.4 px in the picture; 4:2:0 would halve its color
  resolution) for one megabyte more page; q95 buys little visible fidelity for two more. The picture has
  no transparency (its alpha channel is 255 everywhere - the sheet is drawn), so JPEG loses nothing there.
  The GM asked for JPEG by name, not lossy WebP, and named the reversal clause.
- **D3 Threads over subprocess calls, not processes.** Each render is already a subprocess (resvg, the
  encode child); the parent only waits, so a thread per render overlaps them with no pickling and no
  change to the working set of the parent. Order of the output files on disk may change (the PNG may
  land before the page); nothing reads them until `finish()` returns.
- **D4 The index shape is the existing `PointGrid`**, with per-obstacle boxes - the prefilter family
  constitution X clause 15 names - rather than a new occupancy raster, because an occupancy grid would
  have to be proven exact at cell edges and the grid needs no such proof: it returns a superset and the
  old tests decide.
- **D5 Two kinds of moved manifest, two routes.** A map whose manifest moved only in the ink census's
  element counts and whose page changed only in the picture's encoding lands under `REVIEW_GATE_OK` with the
  GM's 2026-08-29 ruling that a settlement-review is not per map (*they read the map themselves*); the GM
  said they would judge the JPEG by eye and reverse it if bad. A map whose TITLE moved under FR-008 is NOT
  covered by that waiver: it is named to the GM with its sheet, per FR-008's own reporting clause, because a
  placard that changed corner is a layout decision on the sheet the GM reads.
- **D6 The duplicate obstacle block is a defect, not a second rule.** Two readings were possible: that the
  unconditional second loop was a deliberate override making cover always an obstacle, or that it was left
  behind when 137 T06 rewrote the first loop. The commit that added `cover_ok` also documented the cover rung
  in `title()`'s own comments ("cover (a belt, a wood) as the last resort before the corner") and in
  `_blank_label_spot`'s docstring, and a rule nobody can reach is not a rule; so it is read as a defect.

## Review history

- Round 1 (2026-09-11): FAITHFUL. The reviewer judged D1 a legitimate reading (feature 199's one-path-per-tile
  ruling is the GM's own; the purpose - element and byte count over three resvg passes - survives) and FR-005
  faithful under Principle XIV, and noted that SC-3 must be measured on the TILED form (R1's 1.17 s was the
  literal one-path file) and that a missed SC-4 bar is reported, never reached for with an excluded lever.
- Round 2 (2026-09-11): FR-008 FAITHFUL (Principle XIV's core case - FR-004 rewrites the very method) and D6's
  reading sound on three witnesses; CHANGES REQUIRED to SC-1 and D5, which still said no map could move:
  SC-1 now admits `title`, `meta.title_band` and the view on a map FR-008 moves; D5 splits the waiver -
  the ink-census-only maps under the 2026-08-29 ruling, a moved title named to the GM. Applied.
- Round 3 (2026-09-11): FAITHFUL - both amendments applied as stated, nothing else loosened.
