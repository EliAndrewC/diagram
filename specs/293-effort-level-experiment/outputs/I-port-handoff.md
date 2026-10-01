# 293 I, ported onto main after feature 287: the storehouse annex goes to the larger houses first - handoff

Clone: `/diagram/.clones/diagram-effort-land`, commits `293 land:` on `main`, not pushed; `sync-with-main.sh` not run.
Base: the mirror's `2b2b8ee4e` (feature 287 landed). The earlier session's work (clone `diagram-exp-e7`, base `ec99356cf`)
was read from its handoff, log and diff; main's engine is authoritative wherever the two disagree.

## What was done

On main, feature 287 already gives each household a LOT before it is seated - its size rung, whether it keeps a kura, its
beast - and already deals one quota to the larger houses first (the wood shed, `larger_first`). So the core change is
one line of engine: the kura quota is dealt by `larger_first` instead of the shuffled quota (`settlement/rolling/lot.py`
`HouseholdLots.kura`). The earlier pass's hold-the-room-and-hand-it-back machinery (`_kura_room`, `storehouses.py`) is not
needed: the size is known before the seat. The annex's length is held in the Edo farm sheds' band inside the one table
every reader of the annex uses (`settlement/farm_fixtures.py` `kura_rect`, which now takes the map's scale).

| map | carriers on main (size rank) | carriers now | annexes drawn (ft) | house centers kept |
|---|---|---|---|---|
| Inashiro | 8th, 12th of 15 | 1st, 2nd | 23.0 x 12.8, 24.7 x 13.8 | 10 of 15 |
| Kashikawa | 1st, 2nd, 3rd of 20 | 1st, 2nd, 3rd | 24.2 x 13.4, 24.6 x 13.7, 24.4 x 13.5 | 3 of 20 |
| Kuwabata | 9th, 16th of 16 | 1st, 2nd | 24.0 x 13.3, 23.1 x 12.8 | 5 of 16 |
| Mizuguchi | 1st, 11th of 12 | 1st, 2nd | 20.6 x 11.4, 24.0 x 13.3 | 6 of 12 |
| Sawada | 5th, 14th of 19 | 1st, 2nd | 24.8 x 13.8, 24.6 x 13.7 | 4 of 19 |

Pool share: 11 of 82 farmhouses (main's lot quota rounds a half up, so Kashikawa's 20 carry three). The hand-drawn maps are
frozen and keep 324 of 1,126 (re-measured).

## Each of the earlier session's changes -> ported / dropped / changed

| earlier change | here | why / how |
|---|---|---|
| The storehouse dealt to the largest houses, the count `round(0.125 x seated)` (`storehouses.py` `deal_storehouses`, `storehouse_count`) | **changed** | main's lots carry the kura before the seat, so the deal is `larger_first(seed, "kura", sizes, KURA_SHARE)`; the count is the lots' quota, `floor(n/8 + 0.5)` of the DECLARED households (half up, not half to even: Kashikawa 3, not 2). A carrier lot that failed to seat would lower the count, never put the annex on a smaller house |
| Holding the annex's room during seating and handing it back (`Settlement._kura_room`, `hold_storehouse_room`, `hand_back`, `meta.storehouse_room_held`) | **dropped** | not needed: the size and the kura are the lot's before the seat is sought, so only the carriers ever reserve the annex |
| The tie rule: a positional roll (`_hjit`, salt 3.0), a guess | **changed** | positions are not known when the lot is dealt; a tie goes by the seed-shuffled quota order `larger_first` already uses - still a guess, labeled in research/homesteads/120 and at `HouseholdLots.kura`; the ladder's rungs are distinct, so it practically never binds |
| The annex's length held to 18-27 ft and 1.5-1.8 to one (`rolling/bundle.py` `north_annex`) | **changed** | the same band, in main's one table `kura_rect` (drawing, bundle reservation, flush side choice, fixture walls all read it); `steading_rects` and every caller pass the scale. Its docstring carries the tried-and-reverted deepening and the deviation label |
| `farmstead_fixtures`'s woodpile seat beside the back kura (`homesteads/fixtures.py`) | **dropped** | main's fixtures are laid in the bundle by `homestead_parts/fixture_seats.py`, which reads `kura_rect` through `steading_rects` - so it gets the band with no edit |
| Research homesteads 120 (the new paragraph, notes -12, -13, -2, -3) and 430 | **ported, changed** | applied whole, then corrected for main: 11 of 82 and "three on twenty", the tie keyed to the map's seed, the code pointers. quote-check and record-format clean (the ledger's last row) |
| The farmhouse / storage-shed sibling text (the retired 4.4 outbuildings) and its snapshot | **ported** | still on main; now also true ("the larger farms have") |
| `tools/CLAUDE.md`'s retired `crop_map` row | **ported** | still on main |
| A doubled-ink sweep once more after `split_at_crossings` (`ways/web.py`) | **ported** | the same pass order stands on main; unit test ported. Moved no pool map |
| `along_tail` reading every reach within 14 ft, not only the nearest (`ways/tails.py`) | **ported** | the code was unchanged on main (a logic defect at a way's vertex); test ported. Moved no pool map |
| A junction end not carried on to the bund (`ways/bund.py`) | **ported** | the loop is unchanged on main; test ported. Moved no pool map |
| A lone spur remnant swept before the footpaths (`_sweep_debris(spur_only=True)`) | **dropped** | 287 dropped the straggler footpath pass the defect lived in (the access tree reserves every door's corridor; the settle draws it) |
| The skeleton arm's trim and drop lifted to `arm_served_or_dropped` | **dropped** | a coverage lift only; main's gate reaches the lines (100% over 39,174 statements) |
| `entrance_in_frame` (the frame takes in the entrance an entrance board stands at), `board_seat`, `_board_footprint` moved | **dropped** | 287 decides the view once (`frame_for`, `plan.view`) and posts the board by its way; on all five maps the board stands inside its view and every household passes it (the reviews confirm) |
| The joint zigzag re-route (`joints.unzigged`, `_UNZIG_SNAP_FT`) | **dropped** | the guard test `test_no_zigzag_straddles_a_joint` (ported) passes on all five maps with the core change in |
| `shadow_measure` lifted from `_lay_web_lane`, and `test_no_two_ways_run_side_by_side_past_a_pitch` | **ported** | the test passes on all five; kept as the guard |
| The bamboo thicket: wells kept by their radius, seats only behind the back row and on the sheet, a whole-sheet search past `THICKET_REACH_FT`, `nearest_fitting`'s centered box | **ported, changed** | the defect is on main: its Kashikawa thicket drew 5 of 12 outline points off the sheet, and 12 of 12 with the core change. "On the sheet" is main's `frame_bounds` (the page as it stands; the belt, planted later, only grows it) instead of the earlier `least_view`. Kashikawa's and Mizuguchi's thickets now stand wholly on the sheet at full size. Two 287 unit tests whose toy map had no page behind the row were given a garden north of it |
| `test_every_bamboo_stand_is_on_the_sheet` | **ported, changed** | non-vacuity per the map's `bamboo` knob (three maps roll homestead bamboo only) |
| The Kuwabata rescue-cloud reorder (a failed fix) and its outlier | **dropped** | no outlier on this roll: the widest nearest-neighbor gap is 171 ft on Kuwabata (243 ft on Inashiro, the same as main) |
| Mizuguchi's district direction re-measured | **dropped** | the connector did not move; the review confirmed the notes' northeast |
| Future-work: the thicket after the windbreak, the roadside pit, the annex resize | **dropped / to the GM** | the thicket seats at full size on both maps; the pit was not reached by this port either; the resize is item 2 below |
| The review rounds' ledger rows, perf bookends, run logs of the earlier clone | **not carried** | this port's own are in `docs/review-ledger.md` and `dev/perf-log/` |

New in this port (found by its reviews): the lane law's `dangling_lane_ends` counts a way as reached only where its nearest
point is nearer the lane's end than its far end (`_walked_to`, `ways/law.py`): a 32 ft skeleton stub on Inashiro left the
connector at the entrance and "reached" the exit strip's end at the same junction. No other map moved.

## Decisions recorded (the four classes)

| decision | class | where |
|---|---|---|
| The storehouse goes to the larger houses first, by the main house's footprint | historically accurate (the direction; Kakimochi's historian and table) | research/homesteads/120 notes -12, -13; `HouseholdLots.kura` |
| Strictly the largest houses | deliberate deviation (Kakimochi's largest had none; the weighted draw priced, not taken) | research/homesteads/120; `HouseholdLots.kura` |
| One farm in eight | historically accurate as a calibration (Kakimochi's 2 of 16; feature 280 M20) | `KURA_SHARE` |
| The count the lots' quota, rounded half up, of the declared households | map drawing convention (287's quota, unchanged) | `quota_carriers`, `larger_first` |
| A tie by the seed-shuffled order | guess (searched 2026-09-30; absence note -3) | research/homesteads/120; `HouseholdLots.kura` |
| The annex's length in the Edo sheds' band, 18-27 ft, 1.5-1.8 to one, the depth a share | deliberate deviation (the kura read were 15 x 18 and 12 x 18 ft) | research/homesteads/120, 430; `kura_rect` |
| The annex on a fixed wall | map drawing convention contradicting the record (unchanged) | research/homesteads/120, 430 |
| A thicket stands behind the back row and on the page; wells kept by radius | historically accurate as the record had it (the settlement's edge, behind its houses); the page and the keep-out are map drawing conventions | `hinterland/bamboo.py` |
| `THICKET_REACH_FT` = 220 ft before the whole-page search | guess (the literal predates this; no distance in the record) | `hinterland/bamboo.py` |
| A lane end reaches a way only where it came toward it | map drawing convention (a lane-law repair) | `ways/law.py` `_walked_to` |
| One more doubled-ink sweep after the split; `along_tail` at a vertex; no junction end carried on | map drawing convention (lane-web repairs) | `ways/web.py`, `ways/tails.py`, `ways/bund.py` |

## The questions I would have asked the GM, and what I did

- **Port the hold-and-hand-back machinery?** No: on 287's lots the size is known before the seat, so the literal ask
  ("the houses that carry the annex are the largest ones") is met by dealing the existing quota by size.
- **Round half to even (the earlier pass) or half up (main's quota)?** Main's, as the brief makes 287 authoritative;
  Kashikawa carries three. Recorded in homesteads/120.
- **Fix the shared byres Sawada's review found?** Deferred - see item 3 below.

## Verification

- **Baseline** on unmodified main (this clone at `2b2b8ee4e`, clean, before the first engine edit): `make done` green,
  cohort 48/48, `make perf LABEL=293-start` 25.5 s.
- **The gate:** `make done` green on the final engine (100% coverage over 39,174 statements; all 138 hamlet-path modules at
  100%; the roll census green). The last engine commit is `fb1d4c1b6`; the commit after it changes only notes, the
  ledger, future-work and this file.
- **Cohort:** 48/48 on every engine committed (the baseline's 48/48; no regression).
- **Performance:** `make perf LABEL=293-end` 18.0 s against 25.5 s, band 0, nothing owed. The drop is not claimed for this
  change: other sessions shared the host, and the host warned of memory pressure minutes after the start bookend.
- **Tests added:** the kura dealt to the largest houses over 30 seeds x 20 counts (`test_lot.py`); the annex band
  (`test_farm_fixtures.py`); on the shipped pool, the carriers are the largest houses with the band held
  (`test_pool_storehouses.py`), no two ways side by side past a pitch, no zigzag across a joint, every thicket on the sheet
  (`test_pool_261.py`); the thicket's wells, back row, page and far search, `nearest_fitting`'s box (`test_hinterland.py`);
  the post-split sweep, the vertex tail (`test_sweeps.py`), the junction end (`test_bund.py`), `shadow_measure`
  (`test_serve.py`), the walked-away end (`test_law.py`). The thicket-on-the-sheet and walked-away tests fail on main's
  shipped manifests by measurement (Kashikawa's off-sheet points; Inashiro's stub); the others are the earlier pass's,
  each shown red there, and were not re-shown red on main.
- **Reviews:** settlement-review round 1 on all five (two pass, three needs-work), round 2 on the three (all pass); every
  finding fixed with a verifying record (`specs/293-effort-level-experiment/measurements.json`) or accepted with
  `make review-accept`; quote-check and record-format clean on homesteads 120 and 430; the GM list below filtered by
  escalation-check. Every pass is a row in `docs/review-ledger.md`.

## For the GM (filtered by `escalation-check`)

1. **The result.** On all five scripted hamlets the storehouses now stand on the largest farmhouses by main-house
   footprint: two each, and three on Kashikawa, because main's lot quota rounds a half up (20 farmhouses). On main they stood
   on the 8th and 12th of 15 (Inashiro), the 9th and 16th of 16 (Kuwabata), the 1st and 11th of 12 (Mizuguchi) and the 5th
   and 14th of 19 (Sawada); Kashikawa's were already its three largest. Kakimochi, the one village read, put its two with its
   2nd- and 3rd-largest houses and its largest had none, so the strict cut is labeled a deliberate deviation in
   research/homesteads/120.
2. **Decision: the storehouse annex's size.** It draws 20.6-24.8 ft by 11.4-13.8 ft, in the Edo farm sheds' band (18-27 ft
   long, 1.5-1.8 to one); the record reads the annex as the kura, and the kura read were about 15 by 18 ft (the commonest
   in a new-field village west of Edo) and 12 by 18 ft (Kakimochi's). Labeled a deliberate deviation. The priced
   alternative: size it as the kura, 3 ken along the wall by 2 to 2.5 ken deep (18 by 12-15 ft); every scripted hamlet
   re-packs, costing a cohort run and a review per map.
3. **Decision: the shared ox sheds on Sawada.** Sawada now has two of four shared sheds past the 120 ft reach that
   `draft_byres` treats as a floor (124 and 174 ft, center to center), where main had one (129 ft); Inashiro has one of
   three (138 ft) on both. The pocket path feature 287 lays before any house is seated has never been held to that floor,
   and no test enforces it; this port's re-pack moved the houses away from the pockets. Ship with this and fix it later by
   laying each pocket during the seating, beside the households just seated (the sketch in
   future-work/farming-communities.md) - or fix it before landing?

## Notes

- The review snapshots' "main" side is the merge base `2b2b8ee4`, so round 1 reviewed the whole feature; round 2 reviewed
  the three maps that needed work. Kashikawa's and Mizuguchi's manifests did not move after their round-1 PASS (only their
  notes did).
- The regenerated maps carry renders; a gate files its rolls without them, so re-run `make map` on each before a review
  snapshot (the snapshot tool says which are missing).

## The merge with main (feature 291, grove sides and row villages), 2026-09-30

**What the merge resolved, and how.** `git merge origin/main` (143 commits of feature 291) conflicted in three engine files,
the five hamlets' manifests and notes, and the assembled homesteads pages.

- `hamletgen/hinterland/bamboo.py`: both keep-outs kept - 291's farm groves (`("groves", 4.0)`) in the rect list, 293's
  wells entered by their radius below it; the list's dead `("wells", 14.0)` entry (a well record has no width) dropped, as
  293 had.
- `hamletgen/ways/bund.py`: both import sets (291's `poly_gap`, `crop_polys`, `stroke_quad` and `carry_on`; 293's
  junction-end skip, which sits beside 291's `carry_on` unchanged).
- `tests/hamletgen/test_hinterland.py`: both features' tests kept.
- The manifests took main's side and were regenerated (Inashiro first); each notes file kept main's text, with 293's entry
  rewritten as measured on the regenerated map against main's 291 roll. `research/homesteads/` and
  `research/citations/homesteads.*` were re-assembled by `make record` and `make citations` (both then `CHECK=1` in sync).

**What the merge broke, measured, and fixed.** After the merge the gate failed three tests and the cohort fell to 50/54
against main's 51/54 (taken in a detached worktree at `origin/main`):

- *Audit-903 refused* (a row village): 293's `_walked_to` rule rightly stopped counting a 41 ft stub as reaching the
  junction it left; the last resort dropped the stub and its join, and the street's end, 191 ft past its nearest farm,
  then served nothing - a tree lane, so the web was refused. `settle_street_ends` now cuts a dangling street end back to
  its last joint (`street.end_to_its_joint`), in the settle's rounds and again in the last resort.
- *Mizuguchi's field spur* ran 10-12 ft beside its street for 210 ft (293's side-by-side guard, 237 ft): `doubled_tails`
  asked only a lane's last end. It and its settle repair now ask both ends, and `along_tail` walks through a junction's
  approach inside `_ALONG_FT`. The spur is 139 ft where it was 339; the field is still joined.
- *Kashikawa's join remnant* ran within 30 ft of a door path for 106 ft: `settle_shadows` drops the shorter ordinary lane
  of a pair side by side past a pitch (`serve.shadowed_by`, `_lay_web_lane`'s own refusal) where the network keeps.
- *The row test's nucleated control* seated 9 of 10 on its synthetic one-margin field (the storehouse now on the largest
  house, seated last); on main the same fixture seats 10/10, 10/11, 8/12, 6/13, so it is the fixture's edge. It now
  asserts every household seated or the site refused by name (feature 287 plan D2), and no row planned.

Cohort after: 51/54, main's three refusals (Audit-29, 33, 45). `make done` green, 100% coverage. Kashikawa's and Mizuguchi's
manifests moved only by the fixes above and the annex band; Inashiro, Kuwabata and Sawada match the pre-merge port's
figures (the same storehouse carriers and sizes, board, wells and lane counts).

**The reviews.** Round 1 was refused at dispatch (gate red, keys moved). Round 2, all five on key `cd09f76a`: Kashikawa,
Mizuguchi and Sawada pass; Inashiro and Kuwabata needs-work on notes text only - Inashiro's woodland count (grazing commons
counted), and on Kuwabata two reader-facing errors that were on main too (the district said to lie west where the road
leaves north; 7 retirement houses where 4 stand). Round 3: Inashiro's entry pointed at an earlier roll's measured line and
did not name the connector's north-west move; Kuwabata kept a stale own-burial-ground line (main's too). Round 4: both pass.
Every finding has a verifying record in `measurements.json` or a `make review-accept`; the connector's crossing of the
belt's windward corner is in future-work (the record calls the crossing a GUESS and attests the open side). Every pass is a
row in `docs/review-ledger.md`.

**For the GM (filtered by `escalation-check`):**

4. **The merge with main (feature 291).** The merge exposed three engine defects, now fixed: a row street's dangling end is
   cut back to its last joint (cohort seed 903 had been refused, its street running 191 ft past its last farm); the
   doubled-lane rule now checks both ends of a lane (Mizuguchi's field spur ran 10-12 ft beside its street for 210 ft; it is
   now 139 ft, where it was 339); and where two ordinary lanes run within 30 ft of each other for more than 100 ft, the
   shorter one is dropped (Kashikawa loses one 106 ft remnant beside a door path). The cohort is 51/54 on both main and the
   merge, with the same three refusals. The row test's nucleated control sits at its fixture's capacity edge (9 of 10
   seated after the merge, 10 of 10 on main), so it now asserts that every household is seated or the site is refused by
   name, per feature 287 plan D2. On Kuwabata's page, three errors that were also on main are fixed: the district lies
   north, not west; 4 homesteads keep a retirement house, not 7; and it uses the village's burial ground.

Not pushed, and `scripts/sync-with-main.sh` not run, as the merge brief asked. The perf bookends were not re-taken after the
merge (`make done FULL=1` was not run); the push's `perf_review.py --check` will ask for them.
