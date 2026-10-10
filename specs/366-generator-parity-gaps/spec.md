# Feature Specification: Generator-parity gaps (town-checks audit, 2026-07-21; re-checked 2026-10-07)

**Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: generator-parity gaps (town-checks audit, 2026-07-21; re-checked 2026-10-07)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: town

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

- **The nucleated bundle packer still tests placed buildings as unrotated boxes.** `settlement/rolling/fit.py`
  `_bundle_side_fits` compares each placed entry's `pw`/`ph` (its unrotated `w`/`h`), though `structures/urban.py` now
  records every urban building's drawn extent beside them (`drawn_extent(w, h, rot)`, feature 121). A rotated shopfront's
  swung corner is invisible to the homestead fit (worked around with hand `block_polys` on Hoshizora twice). Fix sketch:
  read the trailing drawn-extent pair where an entry carries one, as `houses.py` already does.
- **A hand-shaped channel knows nothing of stream corridors.** `village_grove` now keeps its clumps off streams, channels
  and the moat itself (`homestead_parts/stands.py`); `water_ways/water.py` `channel` still trusts the points it is handed.
  Only hand-authored polys bite, so the town tier's scripted water owes it a clear-of-watercourses rule at the placer.
