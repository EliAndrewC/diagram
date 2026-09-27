# Research - feature 264 (measurements; no research pass, GM 2026-09-26)

## R1 - The state before (2026-09-27, Ochiba page, the kind named under the pointer)

The kitchen well already named `well`; the hearth `kitchen`, the pond `garden`, a striking post `practice ground`, a
kneeling mark `hearing court`, the genkan `residence`, a clerk's seat `office hall`. Method: a Playwright pointer at
each part's drawn map coordinate, `elementFromPoint` in vector mode and `l7rMap.keyAtPoint` in raster mode.

## R2 - A room as its own floor paints the picture the one rect did (2026-09-27)

A one-shot observation, observed 2026-09-27; method: resvg renders of a scratch copy of the sheet, compared pixel by
pixel. Ochiba's west residence block as a fill-only rect, two room rects of the same fill, then the outline with
`fill="none"`, rendered by resvg at 2400 px against the one rect: 0 px differ. Drawing the room rects OVER the one
filled-and-stroked rect instead covered the inner half of its stroke: 6,752 px differed. So D4's order is fill,
rooms, outline. After the whole feature, `make picture-diff` against main's PNG: 0 px on all five sheets.

## R3 - The pack audit (2026-09-27)

A one-shot observation, observed 2026-09-27; method: `make pack-audit` on the three hand sheets, main's SVG against the feature's: without `rooms_folded`, Ochiba +1
finding (13.3 ft LOOSE at svg(800,509)) and Ubame +1/-1 (17.3 ft LOOSE at svg(334,503) gained, one kura fire-gap
line lost), each a room edge read as a gap between buildings; with it, identical output on all three, and the old
SVGs' output unchanged by the fold (plan review re-measured all six audited sheets).

## R4 - Two page defects the parts exposed, both fixed (2026-09-27)

- **A part was missing from the raster id map.** `data-in` was first written between `class` and `data-k`, and
  `raster._GROUP` finds a group by `class` then `data-k`, so every part fell out of the id map and, zoomed out,
  named its parent (Ochiba: 24 of 25 part kinds). `data-in` now goes after `data-k`.
- **The id map's palette held 63 kinds** (red channel only, step 4). With the parts as kinds Ubame draws 69 on one
  page and its page failed to write - hidden until the first fix, because the missing parts were not counted.
  Green now counts the rows past 63 (`raster.palette_rgb`); the first 63 keep their red-only colors and keys, so no
  hamlet id map changes color.
- **A label's edge pixels answered as the kind one palette step away.** `crispEdges` does not reach glyphs, so text
  was anti-aliased in the id map, and a blended edge snapped to the neighboring palette entry. On main this made
  small labels answer on few pixels or none (Ochiba's "Akami-fude": 278 of its box's pixels); once the shrine
  altar sat next to the fox relics in the palette, the label answered as the altar (19 fox-relics pixels, 688
  shrine-altar). A sheet page's id map now renders text with `--text-rendering optimizeSpeed`: 0 off-palette
  pixels on Ochiba's id map (of 496,926 painted), and the label answers on 962. The flag is passed only for a Mode A
  sheet's page; the hamlet id maps are held unchanged (FR-008), though the same blending presumably touches their
  small labels too - not measured here, and not changed. The picture a reader sees is not the id map.

## R5 - The probe (SC-001, SC-002, FR-009; 2026-09-27)

A one-shot observation, observed 2026-09-27; method: `probe264.py` (Playwright, 1400 x 1000; device scale 1 opens at fit in raster mode, 4 in vector mode), over the five
pages, samples each part group's shapes - box centers, and 61 points along every path with 1.5 px nudges, because
the page merges circles and lines into one path whose box center falls between its pieces - and asks the page
which kind answers:

| page | parts | parts that answer as themselves (raster / vector) | parents | parents pointable and opening their write-up | parent lit, a part unlit | part lit, a parent lit |
|---|---|---|---|---|---|---|
| Ochiba | 25 | 25 / 25 | 15 | 15 / 15 | 0 | 0 |
| Hayakawa | 29 | 29 / 29 | 15 | 15 / 15 | 0 | 0 |
| Ubame | 30 | 30 / 30 | 20 | 20 / 20 | 0 | 0 |
| county example | 2 | 2 / 2 | 1 | 1 / 1 | 0 | 0 |
| Ochiba round trip | 2 | 2 / 2 | 1 | 1 / 1 | 0 | 0 |

The standing unit test (`test_every_part_is_its_own_kind_and_lights_with_its_parent`) holds the same parts and
parents on the reader's output without a browser.
