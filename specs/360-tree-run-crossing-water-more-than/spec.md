# Feature Specification: OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is refused, not straightened

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is refused, not straightened", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

`hamletgen/ways/tree.py:rejoined` pads a run 4 ft (`REJOIN_PAD_FT`) either side of a water crossing before the
crossing is squared, which leaves two elbows of about 70 deg some 21 ft apart on any run crossing more than about 18 deg
off square; the lane law's `bends` then refuses it. On rolled maps the seating's `tree.admits` refuses such corridors
before any is drawn, so nothing ships kinked (0 `bends` over the pool and cohort 1-20) - but the seating may be turning
down seats a straighter rejoin would keep. Sketch: size the pad from the crossing angle (the squared leg's own length),
or square the crossing before rejoining; measure seats offered and refused on the cohort before and after. Moves maps.
