# Future work: towns

**A town is its own thing, and this file exists because it is not obviously either of its
neighbours** (GM 2026-08-24). It has storefronts, inns, caravans and a theater, which a farming
community does not; it has a farmers plurality and no wall-and-ward apparatus, which a provincial
city does. Filed with cities in the first cut of this split, and pulled out the same day because
burying town material inside the capital-era backlog is how it stops being found.

**Thin today, and that is about where the work has been rather than about towns.** Every hand-authored town
(Hoshizora, Hirameki, Ubame) is
FROZEN, and the town tier is NOT STARTED for scripted generation
([`../migration-plan.md`](../migration-plan.md)) - so nothing has been generating town defects to
find. Expect this file to fill when the town tier converts, and treat its current emptiness as a
statement about attention, not about quality.

## OWED AT CONVERSION: two `s.kiln` glyph defects (settlement-review on Ubame, 2026-08-17)

Both found on Ubame's new potters' kiln works and both deliberately NOT fixed there: they are
defects in `settlement/trades.py::kiln`, not in that map, and a shared-glyph change made under a
one-off content edit lands on Tango, Minami, Nagahara and `wip/shiro-daika` as well. Every map that draws
the kiln today is frozen (or `wip/`), so the fix lands with the first scripted tier that draws a kiln. Still in
the code as of 2026-10-07 (`trades.py` the wisp path, `cxs_` the two-cottage case).

1. **The smoke wisp ignores the map's declared wind.** The plume is authored in the glyph's LOCAL
   frame (`q 2 -3.5 0.5 -7`, toward local -y), so it rotates with the kiln. On Ubame, at
   `rot=351.9`, that puts it at world bearing NNW - blowing INTO the declared `windward="NW"`, and
   pointing at the magistrate's manor. The SITING is right (the works is downwind of every
   dwelling) and only the ink contradicts it, which is the worst version: a reader who trusts the
   drawing reads the nuisance axis backwards. **Fix sketch**: derive the wisp's bearing from
   `meta["windward"]` in world coordinates and counter-rotate it out of the glyph's group, the way
   `_trade_record`'s `lab_off` already counter-rotates a caption. Then the plume becomes free
   evidence for the reader instead of a contradiction.
2. **The two-cottage case is mirrored, with the well centered above it.** `cxs_ = {2: (-f(22),
   f(22))}` puts the pair symmetrically about the works' axis, and the private well's saturated
   blue disc sits centered above them - a bright centered mark over a symmetric pair, which is the
   composition the mirror rule warns about. It does not resolve into a face (one disc, not two),
   but at fit zoom the well becomes the loudest thing in the works and the eye lands on its least
   important object. **Fix sketch**: offset the 2-cottage case the way the 3-cottage case already
   is asymmetric in effect, or move the private well off the axis. Cheap, but it changes every
   two-cottage works, so it belongs with item 1 in one pass.

## OWED AT CONVERSION: the frozen towns' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)

The GM's rule of 2026-09-28 eliminates anything attested only in modern times; the frozen maps are not redrawn, so each
form is owed when the town tier is scripted (`specs/280-modern-only-sweep/outcomes.md` has each item's finding).

- **Hoshizora**: M120 (the funerary ground's pyre clearance, "triple the bonfire"), M123 (the moat offtake angles,
  a guess on modern hydraulics), M127 (the storehouse cap ~1 to 10 houses), M69 (the crematory's 390 ft set-back is a guess, 190),
  M84 (the wagon inn's grooms' lean-to, well, stable and cart yard), M85 (the stall 8-9 ft, not 10), M86 (the
  flophouse as a plain thatched house), M87 (the road town's length from the Edo counts), M90 (no hay barns - haystacks
  or stores), M92 (no bales or fence round the hayfield), M97 (the well's capacity from the Beijing figure), M108 (the
  farrier's sling frame is Western; the Qing two-post tie frame is the attested alternative).
- **Hirameki**: M123, M124 (a private back-gate landing is modern only), M127, M69, M84, M85, M86, M97.
- **Ubame** (the legacy town map, not the magistracy sheet): M114 (the freestanding notice board is a guess), M115
  (the striking bundle - upright posts only), M120, M123, M127, M69,
  M84, M85, M86, M87, M92, M97, M104 (no charcoal cooling ground), M105 (the bale sizes).
