# Feature Specification: The implementation brought to the research - the rows feature 328 left open

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=372-match-the-research-remaining`)

**Created**: 2026-10-10

**Status**: Filed - split off feature 328 at its wave 97 by the GM's ruling of 2026-10-10 (328's `request.md`, "the split";
its FR-011): *"land what we have in main now after finishing wave 97's review. By splitting off the rest of our work into a
separate feature."* Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify`
on this directory, taking 328's `spec.md` as its model); until then `make speckit-todo` lists it as filed.

**Input**: feature 328's request (`specs/328-match-the-research/request.md`), unchanged in kind: bring the implementation to
the research it cites, easiest first, in scope only for code the scripted hamlets, the magistracies and the country shrines
execute (328's amendment 8; the legacy hand-drawn settlements' rows stay DEFERRED).

## What it carries

- **The open rows of 328's ranking at wave 97**, in ranking order: 204 rows in scope (`kept` 166, `mode-a` 38) - 161 E3,
  42 E4 (a research pass under the record's own checks before any code change) and 1 E2 held for the GM (`fixture_quota`).
  The ranking, its audit and every record stay in `specs/328-match-the-research/` (`ranking.json`, `ranking.md`,
  `audit/`, `measurements.json`); a row this feature fixes is marked with its wave there or carried over, as its plan
  decides. Each row's fix text carries what 328 measured and tried (the held E3 rows name their reverted waves and
  measurements: waves 83-86, 91, 96).
- **Sawada's zigzag across a joint** (328's T137, lanes 1/3, on the strict `_ZIGZAGS_WAITING`), WAIVED by the GM for 328's
  landing (*"Waive it"*, 328's `request.md`): its fix - re-lay a household's way at seating so it never arrives inside another's
  dooryard (328's plan, wave 54; two seating guards tried and reverted) - is an open E3 row here.
- **A found row from 328's close**: the 40-household roll of seed 25, refused through 328's batch 3 (its T140), draws at
  328's close but carries one lane knot under the cohort's knot rule (lanes 1 and 2, 23.8 ft apart;
  m:t140-seed25-at-head) - the knot rule of 0081 held at 40 households.
- **Every decision still owed to the GM** (the GM, 2026-10-10: *"Anything that we'd need by decision for the existing feature
  can be spun out into the other feature"*): the whole "Held for the GM" section of 328's `claims-followup.md` - among them
  the `bath_seat` settlement choice, row 427's `fixture_quota`, wave 86's privy over the sty, 0006's one-season decision,
  the items raised for the GM's information (waves 80, 82, 94, and the two readings of 0246's serving reach) - and two
  raised at 328's close: the Mode A wells, drawn as location markers the GM confirmed on 2026-07-21 against 0196's curb of
  about 4 ft (`docs/buildings.md`, Scale), and wave 97's charcoal store kept where it stood across its loading apron
  (m:wave97-ubame-charcoal; spec-fidelity ruled it LEGITIMATE, raised under constitution XVI).

- **An efficiency item from 328's landing pair**: `capacity.field_distances` (wave 20's seat-order tie toward the field)
  computes a ring distance for every free grid point but uses it only to break ties within one grid pitch - 0.166 s of the
  homesteads stage at 40 households, seed 47 (m:landing-pair-40hh-field-tie in 328's records); compute it only for the tied
  candidates.

## The filed features, sorted (328's close, 2026-10-10)

The GM asked which of `make speckit-todo`'s filed features relate to this work and which are future work for the tiers that
are not hamlets. A feature is folded into this one only as the GM chooses.

**Related - the scripted hamlets, the magistracies and country shrines, or the research behind them:**

- *A drawn thing that disagrees with its research* (closest to this feature): 353 (the shared byre on the commons rolled
  on no evidence), 357 (the modern-only items left on the hamlets, e.g. wayside stones), 358 and 359 (the settlement-reviews'
  measured findings on the scripted hamlets - the privy's sun-side share, a far-row grove and its strip), 360 (a tree run
  crossing water off square is refused, not straightened), 362 (the connector through the belt's windward corner), 341 and
  342 (Mode A door glyphs outside their walls; the torii drawn in elevation where the procedure says plan), 335 (the
  magistracies' rear strips), 368 (three loose ends in the privy record, 0047).
- *Research questions owed on the magistracy sheets*: 336 (Takayama's guest route), 337 (a roofed hearing court's size),
  338 (the Koseki middle gate), 339 (Hayakawa's stepped landing), 343 (is the receiving court "swept"), 352 (a lane between
  a house and its own grove).
- *Presentation on the hamlet and sheet pages*: 340 (the program example's captions), 346 (lighting a watercourse paints
  over what crosses it), 348 (hamlet labels in the zoomed-out hit map), 349 (rename `grave island` to `field grave`), 355
  (the head race's width and hue at the tap), 356 (two ways meeting where the material changes), 361 (the notes census and
  the storehouse annexes).
- *A new knob the GM has ruled on*: 369 (the season a hamlet's fields show).
- *Tooling, any tier*: 345 (the push-time roll-review agent), 347 (measure 274's write cap), 370 (a function-length gate),
  371 (a ledger row for every recorded review verdict, filed by 328's session).

**Future work for the tiers that are not hamlets** (owed at their conversion, or a direction): 331 (fold `city/civic.py`),
332 (town, city and capital captions through the one placer), 333 and 334 (the scripted city; the frozen cities' modern-only
forms), 344 (fabric-first generation, a research direction), 350 and 351 (a village's funerary grounds and headman's gate;
its shrine grove), 354 (seasonal maps, deferred by the GM), 363 (the kiln glyph, on the towns), 364-367 (the frozen towns:
modern-only forms, the enclosed-fan floor, generator parity, the deep audit's items).

## How it starts

The cohort baseline is 52 of 54 (`make cohort N=48`, seeds 10 and 20 refused) and a newly failing seed is a regression,
reverted with its measurement (328's precedent). The wave cycle, the batch close every four or five waves, and the review
occasions are 328's (`specs/328-match-the-research/plan.md`).
