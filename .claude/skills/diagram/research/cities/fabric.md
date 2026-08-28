# Urban fabric: the research behind the frontage and row-packing rules

*The research behind the rules in [`../../settlements/cities/fabric.md`](../../settlements/cities/fabric.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing a fabric rule or a packing threshold - or you want the historical basis before overriding one.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## Urban commoners built in continuous street walls

**Grounds:** `s.rowpack`, `city_row_housing_touches`

**Evidence:** attested (Japan), researched (China - not re-read)

**Sources:** `kyomachiya-jawiki`, `kyototuu-unagi`, `nagaya-jawiki` (READ). Chinese county-seat party-wall housing not re-sourced - leftover

- *What the history says.* Urban commoners in both reference cultures did not build detached-with-yard. Machiya street frontage was continuous - party walls or touching eaves, because street frontage was taxed and precious; back-lot *nagaya* were literally ONE ROOF over a row of family units; Chinese county-seat courtyard housing shared rammed-earth or brick party walls in continuous street walls. Detached-with-yard was a samurai (and rural) form.

*Correction to the record (2026-08-28, feature 138):* "street frontage was taxed" is the popular explanation of the narrow lot (`kyototuu-unagi` carries it), and ja.wikipedia 京町家 disputes it outright - Edo-period Kyoto assessed a lump sum per town, not per frontage. The continuous built edge is read either way; the tax is not the reason to cite.

## Machiya row density: a commercial street is a continuous built edge

**Evidence:** attested

**Sources:** `kyototuu-unagi` (READ: frontage ~2 ken, depth 10-12 ken), `kyomachiya-jawiki`, `hiyokechi-jawiki` (READ: breaks at block scale after 1657). See the frontage-tax correction in the entry above

**The question (GM, 2026-08-11), looking at Shiro Daika's north gate market:** *"Is that the
correct amount of space between gate market buildings? No objection, they just look more spaced
out than I expected."* Measured on the drawn map, the median gap between neighboring shop
footprints was **84 ft** - each shop standing alone in its own clearing.

**What the research says.** The Japanese urban shophouse (*machiya*) was built to the street and
to its neighbors. Frontage was the taxed and traded dimension, so lots were narrow and deep: a
Kyoto *kyo-machiya* typically fronted 2-3 *ken* (about 12-18 ft) on a lot running 60 ft or more
back, and the fronts abutted, sharing party walls and a continuous eave line down the block. The
street read as a WALL of shopfronts pierced by gateways and alley mouths, not as a row of
detached boxes. Post-fire policy in Edo cut firebreaks (*hiyokechi*) and broad avenues THROUGH
the fabric and pushed tile roofing, but it never spaced individual machiya apart - the breaks
were at block scale, and the block itself stayed solid.

So an 84 ft gap between two shops is not a small error of degree. It is the wrong urban form: a
market strip drawn as a hamlet.

**What was actually causing it - not the spacing knob.** The engine's `_fits` measures a
candidate against everything standing with a rotation-invariant CIRCUMSCRIBED CIRCLE (the
documented over-restriction in the skill's CLAUDE.md, "CENTER vs FOOTPRINT" item 2). For a 46x28
ft shop that forces neighbors 57.8 px apart center to center where the true touching distance is
28. Compounding it, a frontage run's `skip` matched the fronted way by OBJECT IDENTITY, so a row
written against a sub-stretch of a street (`[(1595, 1390), (2130, 1390)]` rather than the street
variable itself) was refused by the cleared band of the very street it was meant to line.

**The decision.** `frontage(..., dense=True)` opts a row into three changes together: row mates
measured edge to edge along the row's own axis, the fronted street skipped ALONGSIDE any caller
skip rather than replaced by it, and a corridor segment counted as running along the stretch if
either contains the other (so a road that BENDS inside the fronted stretch stops refusing it).
Opt-in, because each one re-rolls any map that takes it - the same bargain `footpaths=0` struck.
Shiro Daika's rows declare it; the shipped provincial cities keep the old fabric until someone
re-lays them deliberately, with a review.

**The deliberate departure from literal reality.** True machiya shared party walls - a gap of
ZERO. We land at a median of **18 ft** on the capital's north and south gate markets (9 ft on the
crowded southwest strip, 48 ft on the loose roadside market at the east gate, which is a
different thing and should stay loose). At 3 ft/px an 18 ft gap is 6 px: enough that a reader can
still count individual shops and see which way each one faces, which is the whole job of the
drawing. The relative sizes stay honest; only the mortar joint is drawn wider than life.

## A county seat's street share, open reserve and civic share

**Grounds:** `citybudget.py` (module docstring: streets ~10-20% of ground, 25-30% deliberately unbuilt), `check_village/common_03_capacity.py` (civic buildings ~3-6% of a county seat; the ~20% reserve cap); `settlements/cities/sizing.md`

**Evidence:** interpolated (the circulation figure is triangulated - specs/009 research B says so), attested (the named open-ground anchors)

**Sources:** `chang-morphology-walled-capitals`; specs/009-city-area-budget/research.md section B (Quanzhou a quarter vacant in 1945, Suzhou's intramural farmland, Jinan's lake, Pingyao's "4 big streets, 8 small streets, 72 lanes") - recorded at the 2026-07 pass, not re-read 2026-08-28

*Recorded here on 2026-08-28 (feature 138) because the finding was stated only in engine comments.* A Chinese county seat ran a sparse street net - one or two gate-to-gate trunks in a cross or T with the drum tower at the crossing, everything else lanes - at roughly 10-20% of the walled ground, and normally enclosed 25-30% deliberately unbuilt ground: walls were sized to administrative rank and growth, and intramural fields, gardens and ponds were siege insurance and flood refuge. Civic buildings alone took only a few percent; the big open consumer was the drill ground and the under-built remainder. The maps draw streets at ~7% (deep blocks, alley warrens) and admit open ground only as a declared, drawn line (agricultural district, drill ground, gardens), never as ambient slack - the engine's budget constant is map-calibrated, the historical band its plausibility envelope.
