# Feature Specification: OPEN 2026-09-30 (feature 293, settlement-review of Kuwabata, round 2): the notes census does not count the storehouse annexes

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 293, settlement-review of Kuwabata, round 2): the notes census does not count the storehouse annexes", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: hamlet, tooling

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

`make notes-census` derives each map's fixture counts from its manifest but leaves out `farm_sheds`, so a map's storehouse
count lives only in hand-typed dated entries - the kind of line that went stale on Kuwabata (round 1, F1). Sketch: one
`storehouses: **n** of **m** farmhouses` line in the census block, read from `farm_sheds` and the plain houses, beside the
fixture line.
