# Research - 245 Lit beads at low zoom

## R1. Why the lit beads do not read as lit, measured

**What the page does.** Below the raster switch (feature 200) the map is one image and the lit class is
drawn as vector above it; since feature 201 a lit class's FILLED shapes are drawn at 0.45 opacity, a wash,
so that the bunds, beans and ponds beneath a lit paddy show through the gold
(`interactive/assets/page.css`, "THE LIT CLASS IS A WASH OVER THE IMAGE"). The rule is written for every
lit class. The beads are `<circle r="1.4" fill="#2F6B35"/>` inside a group at 0.85 opacity
(`settlement/fields/comb.py` `_comb_draw_beads`), no stroke - so the wash is the whole of their highlight,
and gold at 0.45 over a dark pine green is an olive.

**The measurement** (observed 2026-09-13; method: a scratch Playwright script over the shipped Inashiro
page in a 1400-wide window at its opening view, which is raster mode at 1.58x of fit; the bead-densest
window of the map, 260 by 180 map units, screenshotted unlit and lit under each CSS variant; the mean
color of the pixels the highlight moved by more than the page-lit threshold, and the WCAG contrast ratio
between the two states). A bead at that view is about two and a half screen pixels across.

| variant | unlit bead (mean RGB) | lit bead (mean RGB) | contrast lit against unlit | contrast lit against the rice fill |
|---|---|---|---|---|
| shipped (the wash) | 97, 126, 79 | 136, 144, 76 | 1.33 | 1.77 |
| the beads exempt from the wash | 102, 130, 84 | 180, 167, 77 | 1.75 | 1.27 |
| exempt, and the group's 0.85 opacity to 1 | 103, 131, 85 | 193, 173, 77 | 1.89 | 1.16 |

The contrast ratios say what the eye said on the contact sheet (the four variants side by side, unlit and
lit, upscaled three times): under the wash a lit bead is a dull olive dot that changes almost nothing
about the picture; exempt from it the beads turn a clear gold and the whole run along a bund reads as lit.
The gold's luminance is close to the rice fill's (1.27), and the beads still read - the change of hue
from dark green to saturated gold is what the eye picks up at that size, which the luminance ratio does
not measure. In vector mode the beads were already solid gold and larger, which is why the GM saw no
problem zoomed in.

**A stroke ring, tried and dropped.** A fourth variant added the highlight stroke to the lit beads. The
class's widened hit discs (`fill="none"`, painted for the pointer) took the stroke too and every bead grew
a ring several times its size; and the rule that only a shape DRAWN with a stroke takes the highlight
stroke is the GM's own (2026-08-28, the conifer's apex disc). Not pursued.

**The tool.** `make page-lit ... VECTOR=1` on the same page reported `mode: raster` - the `--vector` loop
turned the mouse wheel, and the page scrolls on the wheel by ruling (feature 134, GM 2026-08-28: *"I
don't want scrolling to zoom"*); zoom is Ctrl and the plus or minus key, the buttons, or Ctrl+wheel. The
browser test that covers the loop measures a 200-unit synthetic map in a 1400-wide viewport, which opens
in vector mode already, so the loop never ran in a browser. A viewport of 100 by 100 over that map opens
in raster mode (screen scale 0.5 against the picture's 2 per map unit) and three doublings reach vector,
which is the page the fixed test measures.
