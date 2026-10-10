# Feature Specification: Found by feature 291's settlement-reviews (2026-09-30), measured and left

**Status**: Filed - from future-work/farming-communities.md, "Found by feature 291's settlement-reviews (2026-09-30), measured and left", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: now

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

- **A far-row farm's grove and its holding strip do not meet** (Kashikawa, nitpick F1 of the passing round). The grove is
  square to the page (the house faces south) and the strip square to the street (-59 degrees), so a wedge of open scrub
  26-56 ft wide at its nearest lies between them on all 11 far farms; at fit zoom the holdings read as one field block
  behind the row rather than as the back of each lot. No norm sets a gap (homesteads/157: "house lot, then field").
  Sketch: start the strip at the lot's back edge as drawn (the grove band's outer edge along the normal), or turn the
  farm's frame to the street on a street laid first - the latter a question for the record first (does a planned row's
  house face its street or the south?).
- **A carried-on spur's end is written at full float precision** (Sawada, nitpick of the passing round; re-measured
  2026-10-07: 112 unrounded lane points on Kashikawa, 100 on Mizuguchi, so possibly wider than `carry_on` alone):
  `ways/bund.carry_on` draws `[q, *step]` unrounded where every other lane point is rounded to one decimal. Sketch: round
  the step's points in `carry_on` as `commit_lane` does. An engine change, so it waits for the next feature that re-rolls
  the pool rather than re-keying a reviewed one.
