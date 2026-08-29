# Research: feature 148 - where the interactive page actually spends its time

## R1 - the BEFORE measurement (T02, 2026-08-29), and it REFUTES the feature's premise

Headless Chromium, 1400x900, both pages from `file://`. `elementFromPoint` over 400 random points inside
the map is exactly the hit-test the browser runs for `pointerover`, so it isolates the cost this feature
was written to remove.

| | inashiro | kuwabata |
|---|---|---|
| load to `#map` attached | 238 ms | **313 ms (31% slower)** |
| hit-test | **453 us/probe** | **277 us/probe (CHEAPER)** |
| highlight, every class summed | 18 ms | 27 ms |
| zoom relayout | 1 ms | 0 ms |
| hit-testable elements / subpaths | 9,105 / 293,435 | 10,476 / 318,345 |
| biggest single class | bund, 2,513 elements | **mulberry dike, 4,739** |
| costliest single highlight | scrub, 3.2 ms | **mulberry dike, 10.5 ms** |

**Hover hit-testing is not what makes kuwabata slower.** It is the CHEAPER of the two pages at it, by
40%. The reason is the thing this feature would have added more of: inashiro carries 749 fat invisible
hit copies (`HIT_WIDEN` covers bund, bund beans, field ditch, stream, village lane - a paddy hamlet's
whole fabric) and kuwabata carries none, because a polder map's ink is dike, pond and marsh. Those copies
are hit-test candidates too. So the class of fix in this spec - `pointer-events: none` on scrub and marsh
ink - would speed up the page that is already faster at the thing being fixed, and would not touch the
difference the GM reported.

**What does differ is element count in one class.** Kuwabata's `mulberry dike` is 4,739 elements (2,975
circles, 1,500 paths, 264 ellipses) - the largest class on either page by a wide margin, the costliest
single highlight by 3x, and the plausible driver of the 31% load gap, since load is dominated by building
and styling the DOM rather than by hit-testing it.

**What this does NOT settle.** These are headless numbers on a server with no GPU compositing. The GM
reads the page in a real browser, and "sluggish" may be scroll or zoom repaint, which headless does not
reproduce faithfully - the zoom relayout measured here is ~0 ms, which is not credible as the reader's
experience of a 9 MB SVG. The load half of the GM's report IS reproduced and is real.

**Consequence for the feature:** the approved mechanism does not serve the approved goal. Implementing it
would be building the letter of the spec against a premise the measurement has since falsified, which is
the one thing `spec-fidelity` exists to stop happening in the other direction. Taken back to the GM.

**Method:** `scratchpad/measure_hover.py` and the inline probes; both pages read, neither written -
kuwabata belongs to the `diagram-kuwabata` clone (feature 147).

## R2 - the element-count headroom, and how it was counted (T04)

SC-001's floors rest on these numbers, so the method is written down rather than left in a table.

Every `<g class="f f-..." data-k="...">` group is taken by a BALANCED scan (the groups nest, so a
non-greedy regex to the first `</g>` reads the wrong body - that mistake was made once while measuring).
Inside each group every `<path|circle|ellipse|line|rect|polygon>` is counted, and its STYLE is its tag
plus every attribute except the coordinates (`cx cy r`, `x1 y1 x2 y2`, `rx ry`).

- **drawn now** - the elements as the page carries them.
- **order-preserving floor** - consecutive same-style runs collapsed (`itertools.groupby` over the
  signature sequence). This is what today's `merge_primitives` could reach if it also handled ellipses.
- **order-free bound** - one element per distinct (tag, style) in the group. Not reachable in full,
  because FR-002 refuses a reorder that passes an overlapping element; it is the ceiling.

| | drawn now | order-preserving floor | order-free bound |
|---|---|---|---|
| inashiro | 9,090 | 6,819 (-25%) | 5,548 (-39%) |
| kuwabata | 10,462 | 9,077 (-13%) | 4,140 (-60%) |

The whole gap between the last two columns is PAINT ORDER. Kuwabata's mulberry dike is the case: 2,975
circles carrying THREE distinct styles (`#7C9A54`, `#6E8B4A`, `#5E7C40`, all at opacity 0.85), interleaved
with paths and ellipses at a mean run of 2.4 elements, so consecutive merging collapses almost nothing.

SC-001 asks kuwabata for -40% (above the -13% that ellipse support alone buys, below the -60% ceiling, so
it commits the work to real reordering) and inashiro for -20% (just under the -25% its runs already
offer, because its scatter is far less interleaved and the reordering has less to find there).

**Method:** the inline probes recorded in this session; both pages read, neither written - kuwabata
belongs to the `diagram-kuwabata` clone.

## R3 - the merge has been changing the picture since feature 134 (found while measuring R2's fix)

`merge_primitives` turned a run of same-styled circles or lines into one `<path>`, with no test for
whether they OVERLAPPED. Where the style is semi-transparent that is not the same ink: two blobs at
`opacity="0.85"` stack darker where they cross, while the same two as subpaths of ONE path are a single
0.85 fill and the crossing goes light. The scrub, the marsh and the crowns are all drawn translucent, so
the effect is everywhere.

Measured by rasterizing each page's own `<svg>` and its canonical `.svg` at the same width and counting
pixels differing by more than 8/255:

| map | page vs its SVG, BEFORE | after the guard |
|---|---|---|
| inashiro | 14.470% | 0.026% |
| kashikawa | 12.003% | 0.026% |
| mizuguchi | 17.746% | 0.027% |
| sawada | 12.077% | 0.044% |

**Every interactive page has been rendering differently from its own PNG since the HTML target shipped**,
on 12-18% of its pixels, and nothing caught it: the SVG and PNG are byte-identical by construction
(FR-010) so the pool checks never look at the page, and the browser test asserts hover, not pixels. The
residue (~0.03%) is antialiasing along the merged subpath joins.

Found only because FR-002 made "the picture does not change" a requirement with a test attached, on a
feature whose FIRST aim had already died to its own measurement. Guarded now: a translucent element does
not merge with one it overlaps; opaque ones still do, because overlapping subpaths under the default
nonzero fill rule paint exactly what the separate shapes painted.

## R4 - what the change realized, against R2's bound

| map | elements before | after | change |
|---|---|---|---|
| inashiro | 9,105 | 7,511 | -17.5% |
| kashikawa | 12,497 | 9,447 | -24.4% |
| mizuguchi | 8,228 | 6,833 | -17.0% |
| sawada | 12,400 | 9,006 | -27.4% |

Load and hit-test, median of five runs each (headless Chromium, `file://`):

| page | load before | after | hit-test before | after |
|---|---|---|---|---|
| inashiro | 328 ms | 312 ms | 661 us | 639 us |
| kashikawa | 468 ms | 440 ms | 574 us | 501 us |
| sawada | 492 ms | 463 ms | 1,106 us | 921 us |

Highlighting every class in turn: inashiro 30 -> 29 ms, sawada 42 -> 33 ms. Zoom relayout stays ~1 ms,
which headless does not measure meaningfully.

**R2's order-free bound was too generous, and the reason is a correctness constraint rather than slack.**
It counted one element per distinct (tag, style) per group, which assumes every same-styled element may
merge. R3 shows they may not: translucent ones that overlap must stay apart or the picture changes. That
constraint was not known when the bound was computed, so the bound - and SC-001's floors taken from it -
over-counted. Recorded rather than quietly restated: SC-001's inashiro floor of -20% is not met (-17.5%),
and the honest reading is that the floor was wrong, not the work. See the spec's amended SC-001.
