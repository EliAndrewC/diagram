# Feature Specification: when towns are scripted - what we know it must do

**Status**: Filed - the town tier's placeholder (2026-10-10): every item known to be owed when towns become scripted, carried here word for word. Not exhaustive: what that work finds is added here, never filed as a town-only feature of its own (`make speckit-todo CHECK=1` refuses one and names this feature).

**Approved**: the GM, 2026-10-10, "I agree with your approach, so please do it."

**Affects**: town

**Input**: the GM, 2026-10-10 (request.md, verbatim): *"I think that all of the things that are owed when we implement villages should be consolidated into a single spec kit feature ... that feature should not be exhaustive, because we are not saying in advance what will happen as part of that scripting ... but that is the placeholder feature for anything that we come up with that we realize needs to happen when villages become scripted. And then the same thing applies to towns. And then the same thing applies to provincial cities."*

Rewriting this into a full spec, a plan and tasks is the work of whoever scripts the town tier (`/speckit-specify` on this directory, `docs/migration-plan.md` for the order); each carried item below becomes a requirement or is answered there.

## Carried items

- **The drawing code the frozen maps used is retired** (feature 392, the GM 2026-10-18: "the frozen maps do not need to stay
  runnable"): the town's drawing API that only the legacy exhibits called - its buildings, walls, wards, streets, moat and canals,
  civic and funerary grounds, trades, the not-to-scale farmstead path - was deleted. It is readable from git at `8c31f6d01`
  (the commit before the deletion); the scripted tier builds what it needs anew or recovers it from there. A pointer, not an
  owed item.

Each was a filed feature of its own until 2026-10-10 and now reads `Superseded by 381`; its text is kept here as filed, headings demoted two levels.

### 332 - The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8)

*Also owed at: provincial city, capital - the later tier confirms it still holds.*

**Status**: Filed - from future-work/cities.md, "The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town, provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

Feature 266 built ONE caption placer (`l7r/diagram/labels/`, the cartographic standard: ranked positions, a
consistent gap, free space first, leaders) and routed every caption a live map draws through it. The unscripted tiers
still carry 47 hand-seated `self.label(x, y, ...)` calls in 33 functions - a ministry's name written across its roof,
a hall caption a fixed drop below it - which no live generator runs; the maps that used them are frozen exhibits.
`tests/labels/test_caption_paths.py` lists them by file and function (`D8_HAND_SEATS`) and fails on any NEW hand
seat. **When a tier is scripted**, each of its captions names its SUBJECT instead: `self._captions.append(...)` via
`place_caption(text, box, rot=...)` for a feature beside which it stands, an area subject for a name that lies on its
building or district (`Subject("area", ...)` through `_draw_seated_caption`), and a civic building's own caption with
`Subject(civic=True)` so it keeps off the other named civic buildings (spec FR-014). Delete the row from
`D8_HAND_SEATS` as each goes. The town and city cover rule (research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html) is already in the weights.

### 363 - Two `s.kiln` glyph defects (settlement-review on Ubame, 2026-08-17)

*Also owed at: provincial city, capital - the later tier confirms it still holds.*

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: two `s.kiln` glyph defects (settlement-review on Ubame, 2026-08-17)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town, provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

Both found on Ubame's new potters' kiln works and both deliberately NOT fixed there: they are
defects in `settlement/trades.py::kiln`, not in that map, and a shared-glyph change made under a
one-off content edit lands on Tango, Minami, Nagahara and Shiro Daika as well. Every map that draws
the kiln today is frozen, so the fix lands with the first scripted tier that draws a kiln. Still in
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

### 364 - The frozen towns' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: the frozen towns' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

### 365 - The enclosed-fan tract floor (GM decision 2026-08-03)

*Also owed at: provincial city, capital - the later tier confirms it still holds.*

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: the enclosed-fan tract floor (GM decision 2026-08-03)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town, provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

The rule is DECIDED (research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html, "no
settlement-class cap"): **a paddy fan ENCLOSED in the rendered view reads as a complete field system, and the smallest
attested communal waterworks - a weir, canals and a drain collector - commands about 8 real acres (hamlet grade).** A fan
under 8 acres that is fully inside the view is a defect; a fan running off the view edge is a slice of a larger tract and
exempt, and so is a documented in-wall agricultural district (Tango's nw1), bounded by the rampart rather than claiming to
be a complete rural system. Universal on purpose: history sizes a tract by water, terrain and households, never by
settlement class. Measured on the recorded outline's AREA.

It was never gated because the three frozen towns break it (hoshizora-west 1.8 ac, ubame-west 2.1 ac, hirameki w1/e1/e2
1.1-2.5 ac), and a scale-exempted check is a check that never runs. The scripted town tier owes it as a guarantee of its
field placer (a unit test on the placer, the violating case included), not as a post-hoc check. Probe findings worth
keeping: `build_comb` clips its march ~40 px inside the W/H it is handed, so a fan crosses a canvas edge only when built on
an oversized canvas; a brook-fed fan can slice an edge by raising its sluice off-canvas; and at 1 ft/px a single fan tops
out at ~5-7 ac, so an 8-ac ENCLOSED fan needs genuinely open ground. The retired check's code is in git history (removed
with `pending-enclosed-fan-floor.md`, feature 329).

### 366 - Generator-parity gaps (town-checks audit, 2026-07-21; re-checked 2026-10-07)

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: generator-parity gaps (town-checks audit, 2026-07-21; re-checked 2026-10-07)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

- **The nucleated bundle packer still tests placed buildings as unrotated boxes.** `settlement/rolling/fit.py`
  `_bundle_side_fits` compares each placed entry's `pw`/`ph` (its unrotated `w`/`h`), though `structures/urban.py` now
  records every urban building's drawn extent beside them (`drawn_extent(w, h, rot)`, feature 121). A rotated shopfront's
  swung corner is invisible to the homestead fit (worked around with hand `block_polys` on Hoshizora twice). Fix sketch:
  read the trailing drawn-extent pair where an entry carries one, as `houses.py` already does.
- **A hand-shaped channel knows nothing of stream corridors.** `village_grove` now keeps its clumps off streams, channels
  and the moat itself (`homestead_parts/stands.py`); `water_ways/water.py` `channel` still trusts the points it is handed.
  Only hand-authored polys bite, so the town tier's scripted water owes it a clear-of-watercourses rule at the placer.

### 367 - The town deep audit's open items (2026-07-24, against the frozen Hoshizora and Hirameki)

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: the town deep audit's open items (2026-07-24, against the frozen Hoshizora and Hirameki)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

- **Servant houses** (6.1): the record now settles it - only the ~5 miscellaneous servant households are drawn as houses
  of their own, the other ~8 living inside the compounds they serve
  (research/questions/0120-towns-the-county-seat-and-the-post-town-and-who-lives-in-them-machi.drawing.html). The frozen
  maps draw 16 (Hoshizora) and 13 (Hirameki); the scripted tier draws the record's count.
- **Samurai houses against households** (6.3): the record's rule draws 5 to 10 samurai houses for about 4 samurai
  households (the same drawing page); WHY four households show as eight or nine houses is still not written. Record the
  reason or change the band when the tier converts.
- **Named trades and town shrines** (7.2-7.5, 8.7, 8.8): the record now has pages for the brewery
  (research/questions/0207-sake-breweries-sakagura.html), the smith and farrier
  (research/questions/0205-smiths-and-farriers-kajiya.html), the shops and trades of a town
  (research/questions/0183-shops-and-trades-in-towns-and-villages.html), the teahouse along a highway
  (research/questions/0088-highways-and-what-lines-them-kaido.html), market days and the market ground
  (research/questions/0130-market-days-and-the-market-ground-ichi.html) and shrines in towns
  (research/questions/0216-shrines-in-towns-and-cities.html). What is owed is the drawing decision: which of them a town
  draws as its own feature and which the generic merchant and shop glyphs stand for.
- **The URBAN size table** (8.2): `structures/urban.py` `URBAN` gives every urban kind's footprint with no recorded why
  (its only `Research:` claim is the palette). Record each size against the record, and decide the merchant frontage:
  wide-shallow shophouse glyphs as a declared convention, or narrower and deeper frontage
  (research/questions/0154-merchants-townhouses-machiya.html).
- **Detached or row-fronted** (8.4): the audit asked for the town/city fabric split to be written down. The record's town
  rule now gives the county town a close-packed front, each main house filling its lot's width
  (research/questions/0120-towns-the-county-seat-and-the-post-town-and-who-lives-in-them-machi.html and its drawing page),
  which the frozen towns' detached fabric does not follow; the scripted tier draws the record's.

## Later tiers

The capital has no placeholder yet (nothing is owed at it alone). Items above marked *Also owed at: capital* are confirmed when the capital is scripted; the first capital-only item becomes that tier's placeholder.
