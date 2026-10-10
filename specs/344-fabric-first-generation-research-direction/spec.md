# Feature Specification: 2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION

**Status**: Filed - from future-work/cross-cutting.md, "2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: provincial city, capital

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

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
