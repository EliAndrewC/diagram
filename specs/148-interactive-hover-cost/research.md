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
