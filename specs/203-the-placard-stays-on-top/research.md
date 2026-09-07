# Research - 203 The placard stays on top

RENDERING research, nothing physical. Read off the feature-201 Kuwabata page on main, 2026-09-07.

## R1. The mechanism: not the placard's z-order, the lit scrub's

The placard's z-order never changes. What the GM sees is feature 200's stacking rule (its D4, revised by
201's D5): in raster mode the LIT class is drawn as vector ABOVE the image of the whole picture, and the
image holds the placard. The scrub scatter has blades under the card - the vector page draws the card
over them, last - so when the pointer leaves the card onto the scrub around it, the scrub lights and
its gold blades are painted over the image's card. Before the pointer ever touched the card the scrub
was not lit, so the card looked untouched; after, the pointer sits on the scrub. "Highlighting and
unhighlighting the title card" is the sequence that puts the pointer there.

The same rule affects every class drawn late over ink drawn early, and feature 201 accepted that for
the general case with the wash (a lit class's FILLS at 0.45). The placard is the one case the wash
cannot cover: the scrub is strokes, drawn solid, and the card is the one element on the map that is a
decal laid over the field on purpose (finish.py: *"the placard read as a decal laid on the field rather
than a feature of it"*).

## R2. The fix, and why it reaches the scale bar

Keep the placard as vector, on top, in both modes - as it is on the vector page. Its card and its name
are the `place` class (feature 156), so a stylesheet rule can exempt them from raster mode's leaf
hiding. But the card's fill is opaque parchment, and the scale bar under the name is an UNCLASSED
string (`cls="-"`, the GM's 2026-08-29 ruling that the bar is furniture, not the place): with the card
always drawn as vector, the image's copy of the bar beneath it would vanish behind the card. So the
bar's lines must be vector on top as well, and a stylesheet cannot name them without a marker: the
writer gives the scale bar's group a `class="scale"` - the SVG text gains one attribute, the PNG is
unchanged (resvg ignores it), the ruling that the bar is not highlighted stands (no `f-` class, no
`data-k`). The bar's two captions are `<text>` and already vector everywhere (feature 201).

Cost: two rectangles, four lines and three texts painted as vector in raster mode - nothing.

## R3. What the gate's ratchet found: the picture's encode, 9.6 s per page write

The first green-test gate of this feature ran 772 s against the `done` ratchet's 713 s ceiling (pinned
baseline 549 s; the two green gates before it 690 and 549), and the ratchet refused (feature 171: a
target that gets slower fails). Measured on Kuwabata's page (18.6 Mpx picture):

| step | time |
|---|---|
| resvg render of the picture at 3 px per map px | 5.1 s |
| lossless WebP encode, method 4 (feature 200 as shipped) | 9.6 s, 2.97 MB |
| lossless WebP encode, method 2 | 9.1 s, 2.96 MB |
| lossless WebP encode, method 0 | 2.2 s, 3.20 MB |
| the id map render | 0.3 s |

The gate writes a page for every map it rolls, so the slow encode cost it about 7 s per roll for a
quarter-megabyte saving on a 6 MB page. Method 0 - still lossless, the same pixels - is what ships
(feature 200's D2 chose lossless WebP for the bytes; it did not price the encode). The slowest tests
otherwise are the polder gate tests' roll (54 s of setup, most of it the roll itself) and the perf
snapshot (25 s); the browser package is ~100 s wall on one worker and is the other cost features
199-203 added.
