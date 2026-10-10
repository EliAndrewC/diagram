# Feature Specification: The enclosed-fan tract floor (GM decision 2026-08-03)

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: the enclosed-fan tract floor (GM decision 2026-08-03)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

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
