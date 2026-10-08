# The interactive page - how it is written fast, and the blue plot's two tint rules

**Load this file when:** the page draws too many elements or a merge changed the picture (`page.py`
`merge_primitives`), the raster looks wrong or a hover in raster mode names the wrong class (`raster.py`), or you are
editing what the `wet paddy` modal says about which plots are blue. The package index is
[`l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md).

## `page.py` - merging primitives

`merge_primitives` gathers same-styled `<line>`/`<circle>`/`<ellipse>` into one `<path>` WHEREVER the reorder is
invisible: an element joins an earlier bucket only if nothing it must pass overlaps it, and neither a TRANSLUCENT nor
an OUTLINED element merges with one it overlaps (0.85 blobs stack darker than one merged fill - feature 148 R3; and a
path paints every subpath fill before its stroke, so merged crowns show each other's outlines - feature 153 R5). A line
has no fill and so is never outlined - getting that wrong un-merges every scatter. An extent it cannot compute counts
as being in the way, and a circle's is tested as a circle (`extents.py`).

**A merged scatter is written as ONE PATH PER 400 px CELL, not one path** (feature 199, GM 2026-09-07: Kuwabata's page
"a lot more noticeably sluggish"): a bucket of `TILE_MIN` (200) or more members is split by the cell of each member's
anchor at emit time. Chromium replays every display item whose box touches a screen tile, and one 87,000-subpath path
whose box spans the map was replayed for every tile on every hover. Which elements join a bucket is untouched, so the
picture is unchanged. The measurements are `specs/199-*/research.md`; the browser guards it shipped with were retired
with every rolled-page browser test (`interactive/CLAUDE.md`, "Verifying").

## `raster.py` - the page is TWO MODES (feature 200)

GM 2026-09-07: *"all of the above feel slow"* - hover, scroll, zoom, load, in Chrome. Below a screen scale (`RASTER_R`
px per map px - 2 since feature 223 - against `view.s x devicePixelRatio`) the map is ONE IMAGE of the whole picture,
rendered by resvg (the PNG's own renderer) in tiles in parallel, and every class group is hidden except the lit one,
drawn as vector above it; above the scale the page is feature 199's vector page. The page paints the vector first and
switches when both images are decoded.

- **The pointer in raster mode** is answered from the CLASS ID MAP: the same SVG recolored one flat color per class,
  hit geometry painted as the DOM hits it, opacities stripped, no anti-aliasing, read from a canvas (`page.js`
  `keyAtPoint`; 98.2% agreement with the DOM, the rest single-pixel edges). The id map holds past 63 kinds on one page
  (`palette_rgb`); a sheet page's id map draws text unblended (`crisp_text`).
- **The OFF-MAP INK is dropped first** (`drop_offmap`): 90% of a hamlet page's subpaths lay outside the viewBox - the
  hinterland scatter the crop never shows - and dropping them is what holds the first load down once the image's
  decode is added.
- **The picture carries NO TEXT** (feature 201, `without_text`), and raster mode hides LEAF INK outside the lit group
  rather than class groups, so every `<text>` is the browser's in both modes. A lit class's filled shapes are a 0.45
  WASH over the image, so what lies beneath a lit paddy shows through - the exact stacking and a mask were priced and
  declined (`specs/201-*/research.md` R2, R3).
- **The lit BEADS take no wash** (feature 245, GM 2026-09-13: *"the bund beans don't visible light up when highlighted
  while zoomed out"*): a fill-only mark a few screen pixels across under a 0.45 gold wash is an olive dot the eye never
  reads as lit. They are named by class in the stylesheet after the wash rule; a second class measured the same way is
  added there.
- **The PLACARD is never hidden in raster mode** (feature 203): its card and name (`place`) and its scale bar
  (`g.scale`) stay vector in both modes, drawn last, because a lit class beneath the card was painting over the image's
  card.
- **The raster is a RENDER** (feature 208, GM 2026-09-07: *"a whole lot of rasterizing that is completely pointless and
  not actually needed for the tests"*): `finish()` passes the PNG's own condition (`render` and no
  `DIAGRAM_SKIP_RENDER`) as `with_raster`, so a test roll writes the vector-only page (`"r": 0`) and never pays the
  picture. A page with no raster at all (resvg absent) is `r: 0` too, and never leaves vector mode. The generation
  cache treats a skip-render page as it treats a skip-render PNG.
- **The picture is a JPEG q90 4:4:4** (feature 222), encoded in a child Python (`_PICTURE_CHILD`) so the encoder's C
  buffers live and die there and the parent's memory rests where the roll left it. The reverse is three lines,
  named in `raster.py` beside `PICTURE_FORMAT`.

Numbers and the priced alternatives: `specs/200-raster-mode-below-the-vector/research.md` and the features named
above; `raster.py`'s module docstring and constant comments carry the live ones.

## The blue plot: TWO TINT RULES (feature 159)

A paddy plot drawn with the FLOODED fill carries the class `wet paddy` (the shitsuden), decided at ONE emit site,
`settlement/fields/comb.py` `_comb_draw_paddies`, from the fill about to be drawn, so the class and the color cannot
disagree. Every field engine reaches that site, but the engines tint by different rules, and **the shared modal must
be true under both**:

| engine | rule |
|---|---|
| comb (`waterfields/tint.py`, feature 302) | a random 45% (`FLOOD_SAMPLE`) of the plots ON the drain collector, less those the re-judgment sends back to rice green because they would not read as a basin |
| terrace and polder (`waterfields/hill.py`, `waterfields/polder.py`) | every `low` plot, no sample (the lowest steps or rows) |

At feature 159 the comb maps showed 0-3 blue plots of about 20, and Kuwabata (the one live terrace or polder map) 5 of
5; the legacy exhibits never re-roll.

**So blue is a SAMPLE of the wet ground on a comb map and the WHOLE of it on the others.** The wet-paddy modal
(`l7r/diagram/interactive/assets/modals/hamlet/wet-paddy.md`, its Depiction tab) says so conditionally ("on some fields
every one of them, on others only some"). **Do not flat-state "only a sample"** - false on Kuwabata, which a reader can
open - nor "the wet ground" - false on the comb maps. The `low` / `fill` split is the engine's own (`tint.py`: *"`low`
is the TOPOGRAPHY; `fill` is only the PICTURE"*), and the land-use overlays key off `low`, never off the class.
