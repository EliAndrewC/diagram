# Feature Specification: OPEN 2026-09-28 (269 B16): the shared byre on the commons is still rolled, one map in ten, on no evidence

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-28 (269 B16): the shared byre on the commons is still rolled, one map in ten, on no evidence", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

`settlement/_knobs.py` `byre_form` rolls `courtyard` (the inner stable) / `yard_shed` (the outer stable) /
`detached_commons` at 0.6 / 0.3 / 0.1. The record found the beast living with its household (research/contents.json#homesteads
300), and research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html draws the third form as "rarely, a
shed on the common ground among the houses ... a GUESS, found on no page we read". A knob is for forms the research
supports, so a form found on no page is not one to roll (`docs/research-doctrine.md`). **Measurement**: Inashiro and Sawada
roll `detached_commons` and draw it. **Sketch**: drop `detached_commons` from the knob (or weight it 0), re-roll the two
maps, retire its gate form, the `fraction` sizing the test pins and the guess on 0048's drawing page. If the GM keeps it
instead: lay the pockets during the seating rather than before it (`reserve_commons_byres` runs before the houses, so a
re-pack can leave a shed out of every household's `_BORROW_REACH`).
