# Feature Specification: Found by feature 280's settlement-reviews (2026-09-29), measured and not yet fixed

**Status**: Filed - from future-work/farming-communities.md, "Found by feature 280's settlement-reviews (2026-09-29), measured and not yet fixed", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

- **The privy's sun-side share is under the ruled 0.727 on every scripted map** - re-measured 2026-10-07 (bearing 112.5-202.5
  from the nearest house): Inashiro 6 of 13, Kashikawa 4 of 17, Kuwabata 9 of 14, Mizuguchi 5 of 11, Sawada 7 of 17; the
  shortfall predates feature 280. Sketch: record the realized share in `meta` beside the target and walk the sector's
  bearings before its radii.
- **Sawada's entrance board stands inside the last junction** on the connector (re-measured 2026-10-07: the board 36 ft
  along it, a join at 50 ft; Inashiro, where the 280 review found it, is now clear): a household joins beyond it and passes
  within sight of the board, not by its face. Sketch: seat the entrance board at or beyond the outermost junction.
- **A dike pond's water is its parcel shrunk toward its center, not offset inward** (`landuse.py`, `s_w = 1 - DIKEPOND_WATER_INSET /
  apo`; `features.py` `_rounded_pond` the same): measured on Kuwabata's 29 ponds (settlement-review, 2026-09-29) the bank runs
  7-35 ft (p50 18.5) round a 23 ft average, thin on a long pond's sides and fat at its ends, and the four mulberry rows crowd the
  thin sides. Sketch: offset the parcel inward by the inset (a polygon buffer) for the water and each row loop, and re-measure
  the share.
- **A bath room beside the main door is never drawn**: the work yard covers the front wall on every scripted house, so a hamlet
  whose seat is `main_door` (Kuwabata, Sawada) draws its bath rooms at the next seat, and `meta.bath_seats_drawn` says so
  (re-measured 2026-10-07: Kuwabata `floored_rooms` 2 and `stable_end` 3, Sawada `stable_end` 5, none at the door).
  Sketch: let the bath lap the yard's corner under the eaves beside the door - the yard's keep-out is a guess, the seat is not.
- **Some houses walk several times the straight distance to the way out** (the 280 round-5 review measured Mizuguchi's two east
  houses at about four times; re-measured 2026-10-07 on an approximate lane graph - ends within 8 px joined, each house tied
  to its nearest lane vertex - Mizuguchi's worst is now 1.46, Kuwabata's 3.69 (981 ft for 266) and Inashiro's 2.81 (550 for
  196)). Sketch: re-measure on the engine's own way graph first; if it holds, a detour test in `ways/sweeps.py` re-routes a
  way whose walk exceeds a ratio of its chord.
