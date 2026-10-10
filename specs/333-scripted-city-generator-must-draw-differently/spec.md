# Feature Specification: What the scripted city generator must draw differently (269's research, 2026-09-28)

**Status**: Filed - from future-work/cities.md, "OWED AT CONVERSION (269's research, 2026-09-28): what the scripted city generator must draw differently", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

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
