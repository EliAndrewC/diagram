# Research - 199 Tile the merged scatter paths

All of it is RENDERING research: how a browser paints the page, nothing about how a place was built.
Measured 2026-09-07 in headless Chromium (Playwright, the same browser the FULL tree's page test
drives), viewport 1400 x 1000, on the pool pages as rendered on main at `d1d1232e`. The scripts are in
the session's scratchpad (`measure.py`, `ablate.py`, `zoomcmp.py`); the method is recorded here so it
can be re-run from the description alone.

**The instrument.** The user-facing cost is one real pointer move: Playwright `mouse.move` over a grid
of 150 points across the viewport, wall time per move. Each move fires `pointerover`, the page toggles
the hovered class, and Chromium restyles and REPAINTS before the next move is accepted. The floor of
that instrument is about 16-17 ms per move (a page with the scrub deleted measures 16.8). A
`requestAnimationFrame` pair was tried first and rejected: its floor is two frames (~30 ms) and it is
confounded by whatever happens to sit under the pointer. `document.elementFromPoint` isolates the
HIT-TEST half alone.

## R1. What the cost is: paint of one giant path per screen tile, not hit-testing (GM's question)

The two pages are the same size in every count that usually matters:

| | Inashiro | Kuwabata |
|---|---|---|
| DOM nodes | 9,882 | 11,218 |
| class groups (`g.f`) | ~2,300 | ~900 |
| merged path data (`d` chars) | 8.07 M | 8.95 M |
| scrub subpaths | 230,646 | 258,949 |
| biggest single path (subpaths) | 63,738 | 86,895 |
| ms per pointer move, opening view | **19.3** | **57.3** |
| `elementFromPoint`, median / max | 0.8 / 16.9 ms | 2.0 / 40.1 ms |

Ablation on Kuwabata - one category of content removed from the page, everything else as shipped:

| variant | ms / move | hit-test ms | scroll frame ms | nodes |
|---|---|---|---|---|
| as shipped | 58.7 | 1.33 | 72 | 11,218 |
| scrub group deleted | **16.8** | 0.15 | 32 | 9,617 |
| marsh deleted | 54.0 | 1.28 | 57 | 10,767 |
| mulberry dike deleted (5,071 elements) | 58.6 | 1.30 | 65 | 6,043 |
| perimeter dike deleted | 60.1 | 1.32 | 68 | 11,192 |
| field ditches deleted | 57.1 | 1.27 | 49 | 10,234 |
| fish ponds deleted | 58.4 | 1.29 | 72 | 11,172 |
| windbreaks and copses deleted | 54.1 | 1.41 | 72 | 10,506 |
| every `opacity` / `fill-opacity` attribute removed | 58.8 | 1.40 | 68 | 11,218 |
| every `clip-path` removed | 58.2 | 1.44 | 69 | 11,218 |
| the whole hit layer removed (regions, widened copies, lifted sluices) | 38.8 | 1.28 | 26 | 10,408 |
| `pointer-events: none` on every scrub and marsh mark | 58.9 | **0.14** | 73 | 11,218 |
| **scrub and marsh paths tiled by 400 px cell** | **17.3** | 0.24 | 28 | 11,998 |

Two rows settle the mechanism. Taking the scrub marks OUT of hit-testing (`pointer-events: none`) cut
the hit-test to a tenth and left the move cost exactly where it was - so the cost is not the browser
asking "which element is under the pointer". Tiling the same marks into ~15 paths per giant path,
same ink, same order within each tile, took the move cost to the instrument's floor. What tiling
changes is PAINT: Chromium rasterizes the page in screen tiles, a repaint of a hovered class
invalidates that class's bounding box, and every raster tile in it replays every display item whose
bounding box touches the tile. A single path of 86,895 subpaths whose box spans the map is replayed,
whole, for every tile on screen; fifteen paths of ~6,000 are each replayed only for the tiles they
touch. (The hit layer row is the same effect at one remove: the widened field-ditch copies put
"field ditch" - a class spanning the map - under the pointer after every scroll, so each scroll frame
repainted the map; with the giant paths tiled that repaint is cheap and the row is moot.)

The scroll frame column is confounded by what sits under the pointer during the wheel and is shown
for completeness only; the move column is the measurement.

## R2. Why Kuwabata and not Inashiro: the opening zoom of a portrait map

The cost grows with the on-screen scale, because more raster tiles cover the same map area. The page
opens fitted to the viewport's WIDTH (feature 134 FR-013), so a tall map opens at a larger scale than
a square one: Kuwabata's viewBox is 1070 x 1928 and opens at 2.5x its fit-everything scale; Inashiro's
is 1708 x 1738 and opens at 1.4x. Milliseconds per pointer move, before and after tiling:

| view | Inashiro | tiled | Kuwabata | tiled | Kashikawa | tiled | Sawada | tiled |
|---|---|---|---|---|---|---|---|---|
| whole map fitted | 21.0 | 17.6 | 21.5 | 18.2 | 22.6 | 18.3 | 26.9 | 18.3 |
| opening view (fit to width) | 19.5 | 17.8 | **57.0** | 17.3 | 25.6 | 18.2 | 26.7 | 18.2 |
| zoomed 2x from there | 26.9 | 17.1 | 37.5 | 16.6 | **98.8** | 18.8 | **100.8** | 18.0 |
| zoomed 4x | 25.6 | 16.6 | 27.1 | 16.6 | **128.9** | 18.6 | **100.6** | 16.7 |

So the GM saw Kuwabata's opening view; Kashikawa (viewBox 1276 x 2122, biggest path 100,680 subpaths)
and Sawada (biggest path 218,088) are worse than Kuwabata the moment a reader zooms. Every page in the
pool carries the shape:

| page | viewBox | opening zoom (x fit) | biggest paths (subpaths) |
|---|---|---|---|
| inashiro | 1708 x 1738 | 1.4 | 63,738 / 62,073 / 52,929 / 47,760 |
| kashikawa | 1276 x 2122 | 2.3 | 100,680 / 93,372 / 83,084 / 38,508 |
| kuwabata | 1070 x 1928 | 2.5 | 86,895 / 84,168 / 61,167 / 15,540 |
| mizuguchi | 1648 x 1590 | 1.4 | 87,561 / 44,913 / 41,492 / 20,121 |
| sawada | 2054 x 1214 | 1.0 | 218,088 / 81,192 / 51,600 / 30,576 |

## R3. The cell size, and the threshold

Kuwabata, opening view, scrub and marsh paths tiled at three cell sizes:

| cell | ms / move | hit-test ms | nodes added |
|---|---|---|---|
| 200 px | 17.1 | 0.28 | +2,340 |
| **400 px** | 17.3 | 0.24 | +780 |
| 800 px | 19.6 | 0.36 | +279 |

200 buys nothing over 400 and triples the added nodes; 800 gives back a little of the gain. 400 map
px is the cell (D1). It is a rendering constant with nothing physical behind it - the cell is in map
units, so at the hamlet scale (1 px = 1 ft) it is 400 ft of ground, and that reading is incidental.

The prototype tiled only paths of 200 or more subpaths (D2): a merged path of a few dozen subpaths
costs nothing to replay, and a tile per cell would multiply elements for no gain. The threshold is
on the BUCKET, where the merge already decides what becomes one path.

## R4. The picture does not change - by construction, and measured

A merged path's members were admitted under the merge's own premise (feature 134, 148, 153): two
elements of the same style paint the same ink in either order, and the two cases where that is
false - overlapping translucent shapes, overlapping outlined shapes - are refused from the bucket
before it is written. So every bucket's members are mutually reorderable, and emitting them as
several paths (one per cell, consecutive, at the bucket's position) changes nothing any earlier or
later element can see. Measured on the prototype, screenshot of the page as shipped against the
tiled page, pixels differing by more than 8/255:

| page | opening view | zoomed 4x |
|---|---|---|
| inashiro | 3 of 1,400,000 | 0 |
| kuwabata | 1 | 17 |
| kashikawa | 2 | 0 |
| sawada | 0 | 0 |

The handful that differ are anti-aliasing seams where a stroke ends at a cell boundary and its
neighbor starts in the next path. The implementation repeats this measurement (T05).

## R5. What was NOT done, and why

- **`pointer-events: none` on the scatter marks** (the region rects would take the pointer alone).
  Measured above: it fixes the hit-test half, which is not what the GM sees, and it would change WHICH
  feature takes the pointer where a blade crosses a lane or a house. Declined (D3).
- **A cell in the bucket KEY** (`(tag, style, cell)`) rather than a split at emit time. It gives the
  same paths, but every open bucket receives every other element's extent as a `skip`, so fifteen
  open buckets per style is fifteen times that bookkeeping and fifteen times the `_SKIP_CAP`
  blockings, for the same output. The split at emit time leaves which elements join a bucket, and the
  three refusals, byte for byte as they are (D4).
- **Raster layers per class** - declined in feature 134 R5 and still declined: the 16x zoom stays
  vector.
- **A wall-clock assertion as the gate's guard.** The FULL run is loaded (`-n auto`) and feature 145
  already had to replace two fixed waits with state polls. The deterministic guard is structural -
  every merged path on the real page is confined to one cell - and the timing is recorded, with a
  loose cap (D5).

## R6. The harness, and why the cap is on the mean (T04, SC-005)

The FULL tree's browser test rolls Kuwabata from the pool's declaration and sweeps 150 real pointer
moves at the opening view (`test_kuwabata_pointer_moves_are_cheap_at_the_opening_view`). The reversion
probe of SC-005 - `_tiles` returning the whole bucket as one run, `TILE_MIN` untouched, the cap forced
to fail so the numbers print - measured, in the harness itself:

| | mean | median | p90 | max |
|---|---|---|---|---|
| tiling ON | 17.1 | 16.7 | 20.5 | 32.5 |
| tiling OFF | 59.5 | 21.0 | 156.2 | 183.2 |

The spec's first draft capped the MEDIAN, on the reasoning that one scheduler stall should not decide
the test - and the median of the untiled page is 21 ms, under a 40 ms cap. The cost is not spread over
the moves: it lands on the one move in five that crosses into a map-spanning class (the scrub, the
ditches) and repaints the whole scrub, and the median never sees those. The MEAN is R1's own instrument
(total time over 150 moves) and separates the two pages by 3.5x; one 200 ms stall moves it by 1.3 ms.
So the cap is on the mean. A first, wrong probe is also recorded: raising `TILE_MIN` to switch the
split off ALSO raised the threshold the structural guard reads, so that guard failed for the wrong
reason ("testing nothing") - the split must be reverted at the mechanism, not at the constant a test
shares.

The structural guard, with the split off: 39 paths of 200+ subpaths on the reference page, spanning
up to 22 cells each; with it on, none spans more than one.

## R7. The implementation, measured over the pool (T05)

Every live pool page as regenerated by the green gate (the clone, tiled) against main's page at
`470b0faca` (untiled), same machine, same run. Mean ms per real pointer move; the node count of the
page; pixels differing by more than 8/255 in a 1400 x 1000 screenshot at the opening view and at 4x:

| page | fit old/new | opening old/new | 2x old/new | 4x old/new | nodes | px diff open / 4x |
|---|---|---|---|---|---|---|
| inashiro | 21.1 / 18.2 | 19.8 / 17.4 | 27.0 / 17.4 | 26.7 / 16.7 | 9,882 -> 10,583 (+7.1%) | 3 / 0 |
| kuwabata | 22.0 / 18.3 | **57.7 / 17.4** | 38.6 / 16.7 | 27.2 / 16.6 | 11,218 -> 11,999 (+7.0%) | 1 / 17 |
| kashikawa | 23.0 / 18.2 | 25.7 / 17.7 | 102.9 / 18.5 | **133.3 / 17.9** | 12,412 -> 13,548 (+9.2%) | 0 / 0 |
| mizuguchi | 20.4 / 17.7 | 20.3 / 18.1 | 53.6 / 18.8 | 38.1 / 16.6 | 9,137 -> 9,668 (+5.8%) | 2 / 0 |
| sawada | 27.1 / 18.2 | 26.9 / 18.8 | 102.6 / 18.7 | 102.8 / 16.8 | 12,131 -> 13,873 (**+14.4%**) | 0 / 0 |

SC-001 holds (Kuwabata's opening view 17.4 against Inashiro's 17.4); SC-002 holds (every view of every
page under 25 ms - the worst is 18.8); the picture is unchanged (0-17 pixels of 1,400,000, FR-004).
**SC-003 is MISSED on Sawada**: the spec set the node budget at under 10% from the Kuwabata prototype's
+7%, and Sawada grows 14.4% (1,742 nodes on 12,131) - its scrub is the pool's largest single path
(218,088 subpaths) over the widest map (2,054 px), so it splits into more cells. What the extra nodes
cost is in the same table: nothing measurable - Sawada's whole-map view went from 27.1 to 18.2 ms and
its zoomed views from 103 to 17-19. The budget was a guess at a number; the measurement is the record,
and the miss is reported to the GM rather than the bar moved (constitution XVI).
