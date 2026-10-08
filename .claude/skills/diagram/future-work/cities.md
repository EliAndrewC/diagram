# Future work: provincial cities and capitals

**Everything to do with an urban settlement**: walls and gates, wards and quarters, streets and
storefronts, the castle and its moat, ministries and precincts.

Provincial cities and capitals share one file because they are largely scaled versions of one
another (GM 2026-08-24).

**Towns have their own file** ([`towns.md`](towns.md)), split out on the GM's direction the same day:
a town has enough that is specific to it - storefronts, inns, caravans, the theater, a farmers
plurality the larger tiers do not have - that folding it in here would bury it.

**Every tier this file covers is unconverted** - only hamlets are generated
([`../migration-plan.md`](../migration-plan.md)) - and the hand-authored cities are frozen. An entry here is an input
to the tier's conversion, or work on the engine code that conversion will reuse.
## Fold settlement/city/civic.py into castle_civic.py (feature 113, 2026-08-16)

Left deliberately undone by the `settlement/city/` package split, with the reasoning recorded so
the next session does not have to re-derive it.

`governor_mansion` is the only member of `settlement/city/civic.py`. It calls `self.manor(...)` and
re-keys the record out of `M["manors"]` - it is a STRUCTURE reusing the manor glyph, not city
infrastructure, so it belongs with the castle, the ministries and the dojos in
`settlement/castle_civic.py` rather than beside walls and moats. The size works: 903 + 21 = 924
lines, still under the clause-13 bar.

**Why 113 did not just do it.** Feature 113's whole value proposition was "provably nothing moved"
- a pure move verified by byte-identity. Relocating a method to a DIFFERENT mixin widens the
composed-surface guard across two mixins at exactly the moment the guard is meant to be pinning one,
and makes the stage something other than a pure move (112 research R5 on why that property is worth
protecting). Isolating the orphan in its own module was the cheap way to keep the index honest now
and make the relocation a one-file change later.

**What the move costs**: shift the method, drop `CityCivicMixin` from the `CityMixin` bases in
`settlement/city/__init__.py`, move `governor_mansion` out of `_CITY_SURFACE` in
`tests/settlement/test_city.py` and into whatever guard `castle_civic.py` carries, delete the
`civic.py` row from `settlement/city/CLAUDE.md`. Verify with the same byte-identity sweep - the
drawing must not change. `specs/113-city-package/quickstart.md` has the harness.

## The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8)

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


## OWED AT CONVERSION (269's research, 2026-09-28): what the scripted city generator must draw differently

Feature 269 read these questions for the city tier (research/contents.json#cities; `specs/269-research-backfill/outcomes.md`
section 3). The hand-drawn maps are frozen, so each is owed by the city tier's conversion (`migration-plan.md`), and
the rows marked GM wait on a ruling that the conversion puts to the GM through `escalation-check`. The rows the record
now states as the drawing rule (the moat's width by rank, the gate range's guard room, the block-form and
lower-mansion knobs) are on their drawing pages and are not repeated here.

- **The gate's guard and inspection posts (B38, GM).** Measurement: drawn 105-135 ft inside the opening; the Hakone
  barrier puts them 59 ft in. Mechanism: the gate furniture's offsets are fixed. Sketch: the conversion asks the GM,
  then sets the offset.
- **The patrol road and the ward fence (B38, GM).** Measurement: a 20 ft patrol road, and the ward fence runs on to the
  rampart; Tang wards never met the rampart, a road lay between. Today's form is the GM's 2026-07-27 ruling, so the
  conversion puts the Tang reading to the GM before changing it. Sketch: the fence closes on the road's inner edge; the
  road may widen.
- **The gate belt's ceiling (B41a-4, GM).** Measurement: a 6-structure floor and no ceiling. Sketch: the GM sets the
  ceiling; the belt may then be denser.
- **The in-wall samurai share (B41b, GM).** Measurement: `l7r/diagram/citybudget.py` `SAMURAI_INWALL_FRAC` 2/3; the
  history reads 2/3 as low. Sketch: the GM rules a higher share, and the extramural estates are drawn as country estates.
- **The canal's mouth (B46).** Measurement: `settlement/city/canals.py` allows both forms and chooses none. Sketch: a knob
  rolled per city, the moat with a water gate or the canal's own mouth to the river.

## OWED AT CONVERSION: the frozen cities' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)

Beside 269's list above, the modern-only sweep found these on the frozen provincial cities (each item's finding:
`specs/280-modern-only-sweep/outcomes.md`; the town items are in `towns.md`).

- **Minami**: M120 (the funerary ground's pyre clearance and its "triple the bonfire" reasoning, in `citybudget`'s
  comment), M123 (the moat offtake angles, a guess on modern hydraulics), M124 (private back-gate landings), M126 (the generous lot,
  capped at about double the Fukui ladder), M127 (the storehouse cap ~1 to 10 houses), M130 (the moat ~36 ft
  provincial, ~10 ft county - not 66), M14 (the sun lane from the belt's 10 m, a modern working height), M69 (the crematory
  set-back a guess, 190 ft), M84, M85, M86 (the inn, the stall, the flophouse - as in `towns.md`), M96 (a plain one-sided
  stable trough), M97 (the well's capacity), M99 (the brewery's vat hall 50-62 ft), M103 (no log-boom chain fence or
  pens - moored rafts or a pond), M104 (no charcoal cooling ground), M108 (the farrier's sling frame is Western; the Qing two-post tie frame is the attested alternative).
- **Nagahara**: M120, M123, M124, M126, M127, M130, M69, M84, M85, M86, M96, M97, M99, M108.
- **Tango**: M120, M123, M126, M127, M130, M69, M84, M85, M86, M96, M97, M99, M108.
