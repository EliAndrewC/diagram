# Research - 228 The crop dike lights as a ring

RENDERING research, nothing physical. Read off the Kuwabata page and the engine on main, 2026-09-12.

## R1. Why the pond lights with its dike

The crop dike of a dike-pond parcel is drawn as ONE FILLED PATH covering the whole parcel
(`settlement/fields/landuse.py`, `_landuse_draw_plot`: the bank outline `bd` at inset 0, filled the
bank's tan), and the pond is drawn AFTER it as a second path (`wd`, inset 11 px) under its own class.
On the vector page that is invisible: the pond paints over the disk, and lighting the dike paints gold
under the pond. In raster mode - the mode every opening view of Kuwabata is in (feature 200) - the lit
class is drawn as vector ABOVE an image of the whole picture, with its filled shapes at 0.45 opacity
(feature 201's wash), so the dike's lit disk lies over the image's pond and the pond reads as lit
gold-blue. That is what the GM sees: the ponds "inside each Mulberry dike" lighting with it.

The perimeter dike (`settlement/land/dikes.py`) is drawn as a BAND - the outer edge out and the inner
edge back, one closed path with a hole - so lighting it lights the earthwork alone; the polder inside
shows through the hole untouched. That is the behavior the GM asked for.

## R2. The fix: the bank is a ring

Draw the crop dike's bank as the ring between its two edges: one path whose `d` is the bank outline
followed by the water outline, `fill-rule="evenodd"`, so the fill has a hole exactly where the pond is
drawn. Both outlines were already computed, in that order, from the same random draws (`_rounded_pond`
for the bank, then for the water), so the pond's shape, the manifest's `parcel`/`water`/`bank`
records, the crowns (clipped to the bank outline, unchanged) and every check reading them are
untouched; only the SVG text of the bank path changes.

What the PNG can change: the bank's 1.2 px stroke now also runs along the inner edge, under the
pond's own 1.4 px stroke on the same outline; the pond's stroke is drawn later, wider and opaque, so
the inner stroke is covered and only antialiased fringe pixels at the pond's edge can blend
differently. Byte-identity of the picture is not required (GM 2026-09-08: a map may look a little
different if the rules hold and nothing overlaps that must not).

## R3. Alternatives priced

- **A stylesheet or page.js fix** (an asset tweak, no feature): a stylesheet cannot cut a hole in a
  fill, and the page does not know which pond sits in which dike. Declined.
- **Drawing the ponds above the lit class in raster mode** (the exact answer): priced and declined by
  feature 201 (223 ms of raster per hover on the paddy); the wash was the GM's accepted trade. This
  feature does not reopen it.
- **A second stroke-only element for the outer edge** so the inner edge carries no stroke at all:
  doubles the dike's element count for a fringe no reader can see under the pond's own stroke. Declined.
