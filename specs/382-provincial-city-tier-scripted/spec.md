# Feature Specification: when provincial cities are scripted - what we know it must do

**Status**: Filed - the provincial city tier's placeholder (2026-10-10): every item known to be owed when provincial cities become scripted, carried here word for word. Not exhaustive: what that work finds is added here, never filed as a provincial city-only feature of its own (`make speckit-todo CHECK=1` refuses one and names this feature).

**Approved**: the GM, 2026-10-10, "I agree with your approach, so please do it."

**Affects**: provincial city

**Input**: the GM, 2026-10-10 (request.md, verbatim): *"I think that all of the things that are owed when we implement villages should be consolidated into a single spec kit feature ... that feature should not be exhaustive, because we are not saying in advance what will happen as part of that scripting ... but that is the placeholder feature for anything that we come up with that we realize needs to happen when villages become scripted. And then the same thing applies to towns. And then the same thing applies to provincial cities."*

Rewriting this into a full spec, a plan and tasks is the work of whoever scripts the provincial city tier (`/speckit-specify` on this directory, `docs/migration-plan.md` for the order); each carried item below becomes a requirement or is answered there.

## Carried items

- **The drawing code the frozen maps used is retired** (feature 392, the GM 2026-10-18: "the frozen maps do not need to stay
  runnable"): the provincial city's drawing API that only the legacy exhibits called - its buildings, walls, wards, streets, moat and canals,
  civic and funerary grounds, trades, the not-to-scale farmstead path - was deleted. It is readable from git at `8c31f6d01`
  (the commit before the deletion); the scripted tier builds what it needs anew or recovers it from there. A pointer, not an
  owed item.

Each was a filed feature of its own until 2026-10-10 and now reads `Superseded by 382`; its text is kept here as filed, headings demoted two levels.

### 331 - Fold settlement/city/civic.py into castle_civic.py (feature 113, 2026-08-16)

**Status**: Filed - from future-work/cities.md, "Fold settlement/city/civic.py into castle_civic.py (feature 113, 2026-08-16)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

### 333 - What the scripted city generator must draw differently (269's research, 2026-09-28)

*Also owed at: capital - the later tier confirms it still holds.*

**Status**: Filed - from future-work/cities.md, "OWED AT CONVERSION (269's research, 2026-09-28): what the scripted city generator must draw differently", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

Feature 269 read these questions for the city tier (research/contents.json#cities; `specs/269-research-backfill/outcomes.md`
section 3). The hand-drawn maps are frozen, so each is owed by the city tier's conversion (`docs/migration-plan.md`), and
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

### 334 - The frozen cities' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)

**Status**: Filed - from future-work/cities.md, "OWED AT CONVERSION: the frozen cities' modern-only forms (feature 280, the modern-only sweep, 2026-09-29)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

### 344 - 2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION

*Also owed at: capital - the later tier confirms it still holds.*

**Status**: Filed - from future-work/cross-cutting.md, "2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

Today's order is shell-first: wall/roads/water, then fabric fitted inside, with the wall
PRE-SIZED from a budget density constant. The constant was wrong once (Tango's 690 vs the
capital's as-built 1,367) and the failure mode was structural: fabric could not fit, overflow
silently went extramural. A fabric-first order - grow streets/quarters/temples roughly
radially, THEN wrap wall/moat/ring around the built hull - makes wall-sizing correct BY
CONSTRUCTION. Known hard parts (the GM named them): gate-anchored programs (guard houses,
inspection stations, caravan clusters) need the gates, so it becomes two-pass - grow fabric,
choose gates on the hull, then place gate programs and re-arrange locally; ring/moat must
wrap an irregular hull rather than an ellipse. This is a full feature with its own spec, not
a mid-feature pivot. Candidate: the city tier's conversion (the GM, 2026-10-07: the capital goes straight to
a scripted generator; Shiro Daika's hand pass is dropped).

Design inputs measured on Shiro Daika's hand-authored first pass (2026-08-10), the motivating example:
- **Wall-to-fabric fullness is the headline requirement** (GM 2026-08-10). After three wall derivations the
  interior slack check passed (claimed-open + unclaimed <= ~15% of the interior), yet the map still read empty: 41% of
  the walled interior had been claimed-open commons at the first derivation, and hours of fine adjustment were tuned
  against a wall about to be wrong. A grown fabric with the wall wrapped round it has the right slack by construction;
  a wall must never be adjusted after the fine work.
- **Realized machi density is bounded by the SERVICE fabric, not the packer**: streets, kido reserves, well courts and
  roji took ~8% of the packed ground at the settled wall. Budget service ground per district (wells per ~20
  households, roji per 95 px reach) BEFORE deriving the wall, or the same gap reappears.
- **Place service features and packs in one deterministic order per district**, so a local edit stays local: the
  hand pass's endgame was cross-coupled reflows, every well, claim or alley edit re-rolling neighboring packs (three
  "dead cores" moved five times).

## Carried from an earlier tier, to confirm

- 332 - The town, city and capital tiers' hand-seated captions go through the one placer when their tier is scripted (feature 266, spec D8): carried by 381 (the town tier); confirm it at this tier.

- 363 - Two `s.kiln` glyph defects (settlement-review on Ubame, 2026-08-17): carried by 381 (the town tier); confirm it at this tier.

- 365 - The enclosed-fan tract floor (GM decision 2026-08-03): carried by 381 (the town tier); confirm it at this tier.

## Later tiers

The capital has no placeholder yet (nothing is owed at it alone). Items above marked *Also owed at: capital* are confirmed when the capital is scripted; the first capital-only item becomes that tier's placeholder.
