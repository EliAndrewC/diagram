# Feature 228 - the crop dike lights as a ring

**Status**: IMPLEMENTED - FAITHFUL (`spec-fidelity`, round 1 of 5); `settlement-review` pass on Kuwabata (water pixels lighting with the dike 100% -> 6.2%, all within the rim; the picture within antialiasing of the shipped render); gate green (151 s). Its aside is taken in the delivery note: the crowns overhanging the water's rim still light with the dike (their clip is unchanged by design).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - why the pond lights (the dike is a filled disk under the
raster wash) and why the perimeter dike does not (it is a band with a hole).
**Predecessors**: feature 153 (the crop dike's crowns keep their tone while lit); 200/201 (raster
mode, the lit class above the image, the wash); the perimeter dike's band (`land/dikes.py`).

## Summary

The GM, on the Kuwabata page: hovering the mulberry dike lights *"not only the Mulberry Dyke itself,
but the fish ponds Inside each Mulberry dike"*; they want *"only the Mulberry dikes"* lit, *"the same
behavior that we give to the perimeter dyke"*. The dike is drawn as a filled disk covering the whole
parcel with the pond painted over it, and in raster mode the lit disk is washed over the image's pond
(R1). The perimeter dike is a band with a hole. The fix draws the crop dike's bank as the ring between
its outer edge and the pond's edge, so lighting it lights the bank alone and the pond shows through.

## Functional requirements

- **FR-001** The crop dike's bank is drawn as a RING: one path whose fill covers the bank between its
  outer edge and the pond's outline and nothing inside the pond (`fill-rule="evenodd"`, the bank
  outline then the water outline). Lighting the dike on the page lights the bank and its crowns and
  nothing of the pond, in raster mode and on the vector page alike - as the perimeter dike behaves.
- **FR-002** This holds for every crop the knob rolls - mulberry, sugarcane, banana, fruit - and for
  fry ponds, because all four classes and both pond kinds are drawn by the same code.
- **FR-003** Nothing else moves: the pond's shape and class, the manifest's `dikeponds[]` records, the
  crowns and their clip, the sluices, every check that reads them. The random draws are unchanged.
  Byte-identity of the PNG is not required; the only change the picture may carry is antialiasing at
  the pond's edge (R2).
- **FR-004** Tests: a unit test that the bank path emitted for a dike-pond parcel carries both
  outlines and the even-odd rule, and that the pond's path is unchanged; the existing dike-pond
  checks stay green. The why at the point of change, and in the crop dike's operative doc.
- **FR-005** Kuwabata is regenerated, its page opened by the session with the dike lit, and the map
  is reviewed by `settlement-review` before it ships (a Mode B map changed).

## Success criteria

- **SC-001** On Kuwabata's page in raster mode with the mulberry dike lit, a pixel inside a pond is
  the pond's own color, not the highlight; a pixel on the bank is lit.
- **SC-002** The unit test fails on the old emit (a single outline, no fill rule) - shown once.
- **SC-003** `make done` green; `settlement-review` recorded; the pool's dike-pond checks green.

## Decisions Recorded

- **D1 - a ring, not a re-stacking.** The exact answer in raster mode (the pond drawn above the lit
  class) was priced and declined by feature 201; the ring is the perimeter dike's own form and costs
  nothing on the page. Map drawing convention, recorded at the point of change.
- **D2 - the inner edge carries the bank's stroke**, under the pond's wider, later stroke. A
  stroke-only second element was declined (R3).
