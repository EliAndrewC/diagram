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
