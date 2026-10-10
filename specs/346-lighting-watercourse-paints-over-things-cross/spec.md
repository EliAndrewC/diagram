# Feature Specification: Lighting a watercourse paints over the things that CROSS it (measured 2026-09-12, feature 230)

**Status**: Filed - from future-work/cross-cutting.md, "Lighting a watercourse paints over the things that CROSS it (measured 2026-09-12, feature 230)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: now

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

MEASURED by the feature's fifth settlement-review pass with `make page-lit` on Inashiro's page:
lighting the irrigation ditch repaints 35.8% of the footbridge's ink and 29.5% of the weir's;
lighting the stream repaints 57.7% of the weir's. On the sheet the deck and the stone crib are drawn
OVER the water they cross, which is how a reader knows they are a crossing at all; on the page,
hovering the water puts the water back on top of them.

MECHANISM: below the raster scale the page is one image of the whole picture with every leaf outside
the lit class hidden, and the lit class redrawn as vector ABOVE the image (features 200, 201, 203).
The image carries the map's true draw order. The redraw carries none of it, so a lit stroke lands over
everything the image drew after it. It is not new with this feature - any footbridge over a stream has
behaved this way since raster mode shipped - but the weir is a new thing standing in the water, and it
is the worst case measured so far.

PRICED AND DECLINED ONCE ALREADY, which is why this is a note and not a fix: feature 201 met the same
problem for FILLED shapes (a lit paddy hiding its own bunds and beans), priced exact stacking at 223 ms
per hover and a mask at 300-1,100 ms, and shipped the 0.45 wash instead (`specs/201` research.md R2,
R3). The wash does nothing for a STROKE, which is opaque by design so a ditch reads as a ditch.

SKETCH, the same shape feature 228 took for the crop dike one level down - carry the ORDER, not the
geometry. At page-write time record per class which LATER leaves overlap it (`page.py`'s merge
machinery already computes exactly that overlap to decide its buckets), and in raster mode draw those
few leaves above the lit group in their own order. It is bounded by the overlap, so it is a handful of
elements per hover rather than feature 201's whole-class restacking - which is the reason to think the
223 ms figure does not transfer, and the first thing to measure if anyone picks this up. The
alternative, splitting the water stroke geometrically where a fixture crosses it, is cheaper on the
page and is REFUSED: it would change the SVG and the PNG, which spec 134 FR-010 forbids.
