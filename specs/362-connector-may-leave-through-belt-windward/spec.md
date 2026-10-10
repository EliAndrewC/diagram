# Feature Specification: OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward corner

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward corner", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: now

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

**Measured**: the 293 review found Inashiro's connector leaving through the windbreak's north-west apex, about 13 degrees
off the north-west wind. Re-measured 2026-10-07: Inashiro's now leaves south-west, but Kuwabata's runs through the belt -
27 belt clumps within 40 px of its connector, centered 141 degrees from the cluster (about north-west).
**Mechanism**: the connector's dry-exit search (`ways/track.py`, `connector_through`, `dry_exit.py`) scores bearings by dry,
clear ground and has no preference for the belt's open side. research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html records the lane's crossing as a GUESS and the old entrances found as standing on the grove's open side (Tonami;
the Huizhou water mouths). **Sketch**: among the dry bearings the sweep admits, prefer the one that leaves through the
belt's lee or flank arc (`plan.windward`), and fall back to the windward arc only where no other is dry - asked of the
whole cohort, since it moves every map whose connector currently leaves windward.
