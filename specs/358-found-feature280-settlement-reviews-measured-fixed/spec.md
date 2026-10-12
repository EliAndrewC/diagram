# Feature Specification: Map-moving fixes the settlement-reviews found, measured and not yet fixed (one re-roll wave)

**Status**: Filed - from future-work/farming-communities.md, "Found by feature 280's settlement-reviews (2026-09-29), measured and not yet fixed", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Why one feature** (2026-10-10): every item here moves every map and owes a pool re-roll and its review; done together they are one wave instead of six (355, 356, 359, 360 and 362 carried below; this feature's own entry was feature 280's review findings). Each measurement predates later re-rolls - re-measure before fixing.

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

- **The privy's sun-side share is under the ruled 0.727 on every scripted map** - re-measured 2026-10-07 (bearing 112.5-202.5
  from the nearest house): Inashiro 6 of 13, Kashikawa 4 of 17, Kuwabata 9 of 14, Mizuguchi 5 of 11, Sawada 7 of 17; the
  shortfall predates feature 280. Sketch: record the realized share in `meta` beside the target and walk the sector's
  bearings before its radii.
- **Sawada's entrance board stands inside the last junction** on the connector (re-measured 2026-10-07: the board 36 ft
  along it, a join at 50 ft; Inashiro, where the 280 review found it, is now clear): a household joins beyond it and passes
  within sight of the board, not by its face. Sketch: seat the entrance board at or beyond the outermost junction.
- **A dike pond's water is its parcel shrunk toward its center, not offset inward** (`landuse.py`, `s_w = 1 - DIKEPOND_WATER_INSET /
  apo`; `features.py` `_rounded_pond` the same): measured on Kuwabata's 29 ponds (settlement-review, 2026-09-29) the bank runs
  7-35 ft (p50 18.5) round a 23 ft average, thin on a long pond's sides and fat at its ends, and the four mulberry rows crowd the
  thin sides. Sketch: offset the parcel inward by the inset (a polygon buffer) for the water and each row loop, and re-measure
  the share.
- **A bath room beside the main door is never drawn**: the work yard covers the front wall on every scripted house, so a hamlet
  whose seat is `main_door` (Kuwabata, Sawada) draws its bath rooms at the next seat, and `meta.bath_seats_drawn` says so
  (re-measured 2026-10-07: Kuwabata `floored_rooms` 2 and `stable_end` 3, Sawada `stable_end` 5, none at the door).
  Sketch: let the bath lap the yard's corner under the eaves beside the door - the yard's keep-out is a guess, the seat is not.
- **Some houses walk several times the straight distance to the way out** (the 280 round-5 review measured Mizuguchi's two east
  houses at about four times; re-measured 2026-10-07 on an approximate lane graph - ends within 8 px joined, each house tied
  to its nearest lane vertex - Mizuguchi's worst is now 1.46, Kuwabata's 3.69 (981 ft for 266) and Inashiro's 2.81 (550 for
  196)). Sketch: re-measure on the engine's own way graph first; if it holds, a detour test in `ways/sweeps.py` re-routes a
  way whose walk exceeds a ratio of its chord.

## Carried: the other map-moving fixes from reviews

Carried word for word on 2026-10-10 (the GM, 2026-10-10: "Yes, please.", on the session's proposal to merge them); each old feature reads `Superseded by 358`.

### 355 - What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)

**Taken out of this wave 2026-10-11**: done by feature 355 itself, reopened at the GM's word (the goal of the session "Diagram magistracies" named 355); the hue taper is built there - this wave does not do it again.

**Status**: Filed - from future-work/farming-communities.md, "What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, 2026-09-13)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

**Measured** (Sawada): the head race leaves the brook at `#6C9CBE` (128,167,191) - darker and more saturated than the
brook's own `#9CB4C8` (168,187,199) - and at 6.0 px against the brook's 7, so it is 86% of the trunk's width. At 9x the
dug ditch can read as the principal watercourse. The mouth half is done (269 B22: the race now opens out of the brook's
bank, research/contents.json#water 310, `hamletgen/water/brook.py` `open_race_mouth`); the width and the hue are what remain.
**Mechanism**: both widths are the water-width ladder's own figures, drawn by RANK rather than discharge, and the hues
are the supply/brook pair every map uses; changing either for this junction trades a junction-scale misread for a
map-scale one. **Sketch**: judge the new mouth at 9x in a settlement-review first; only if the race still reads as the
river, taper its first ~30 ft from the brook's hue to its own.

### 356 - Two ways that meet where the material changes (feature 230 pass 12, 2026-09-13)

**Status**: Filed - from future-work/farming-communities.md, "Two ways that meet where the material changes (feature 230 pass 12, 2026-09-13)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

**Measured** (Kuwabata, the polder ring): at the SE corner the e_toe pond canal ends at (2699.2, 2186.1) with a rounded
cap at its 3.0 ft tail width while the drain trunk starts at (2702.2, 2185.6) at 5.0 - centerlines 2.5 ft apart, widths
2 ft apart, and since feature 230 in two different inks. The SW corner is the same joint. The strokes overlap, so there
is no gap; what a reader sees at 7x is a blue cap stuck on the end of a wider gray pipe. Re-measured 2026-10-07: three
such joints on Kuwabata, a 5.0 ft stroke meeting a 3.0-3.4 ft one with ends 3.0 px apart.

**Sketch**: end the toe ON the drain's centerline rather than 3 ft short and 2.5 ft off, or taper the drain's head to
the toe's width where they meet, the way the feeder/lateral junctions already read. Both are changes to the polder ring
builder's corner, which every polder map draws.

### 359 - Found by feature 291's settlement-reviews (2026-09-30), measured and left

**Status**: Filed - from future-work/farming-communities.md, "Found by feature 291's settlement-reviews (2026-09-30), measured and left", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

### 360 - OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is refused, not straightened

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is refused, not straightened", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

`hamletgen/ways/tree.py:rejoined` pads a run 4 ft (`REJOIN_PAD_FT`) either side of a water crossing before the
crossing is squared, which leaves two elbows of about 70 deg some 21 ft apart on any run crossing more than about 18 deg
off square; the lane law's `bends` then refuses it. On rolled maps the seating's `tree.admits` refuses such corridors
before any is drawn, so nothing ships kinked (0 `bends` over the pool and cohort 1-20) - but the seating may be turning
down seats a straighter rejoin would keep. Sketch: size the pad from the crossing angle (the squared leg's own length),
or square the crossing before rejoining; measure seats offered and refused on the cohort before and after. Moves maps.

### 362 - OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward corner

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward corner", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

**Measured**: the 293 review found Inashiro's connector leaving through the windbreak's north-west apex, about 13 degrees
off the north-west wind. Re-measured 2026-10-07: Inashiro's now leaves south-west, but Kuwabata's runs through the belt -
27 belt clumps within 40 px of its connector, centered 141 degrees from the cluster (about north-west).
**Mechanism**: the connector's dry-exit search (`ways/track.py`, `connector_through`, `dry_exit.py`) scores bearings by dry,
clear ground and has no preference for the belt's open side. research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html records the lane's crossing as a GUESS and the old entrances found as standing on the grove's open side (Tonami;
the Huizhou water mouths). **Sketch**: among the dry bearings the sweep admits, prefer the one that leaves through the
belt's lee or flank arc (`plan.windward`), and fall back to the windward arc only where no other is dry - asked of the
whole cohort, since it moves every map whose connector currently leaves windward.

