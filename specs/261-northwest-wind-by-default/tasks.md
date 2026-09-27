# Tasks - feature 261, the wind is northwest unless a map declares otherwise

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6). Research: [`research.md`](research.md) (R0-R4).
American spellings, hyphens only.

**No task here is `research: physical`.** The northwest default and the katabatic reading are already cited in
`research/vegetation/030` from sources read and quote-checked before this feature; no new source is used and no
historical question is reopened. What changes is which of the two recorded forms the map takes by default - the
GM's ruling - and the record is rewritten to say so. `quote-check` and `record-format` still run on the changed
entry (T10).

## Phase 1 - the engine (D1-D3)

- [x] T01 The default: `DEFAULT_WINDWARD`, `plan_site` takes it unless the spec declares a wind; `windward_for`
      and `WIND_TURNS` deleted with the retirement reasoned at the constant; `meta.wind_source`
      research: rendering
      verify: DONE. plan_site takes DEFAULT_WINDWARD unless the spec declares one; windward_for and WIND_TURNS deleted, the retirement reasoned at the constant; meta.wind_source written in water/skeleton.py. test_plan: NW for every fall and seed, a declared quarter used as declared.
- [x] T02 The seat bends to the wind: `WIND_BACK_MIN_DOT`, the off-wind fallback, `seat["offwind"]`, and
      `meta.seat_offwind` where `stage_ways` used to rename the wind
      research: rendering
      verify: DONE. WIND_BACK_MIN_DOT (cos 45); a margin off the wind is only the last fallback, seat[offwind] and meta.seat_offwind where stage_ways used to rename the wind. test_cluster: the seat faces the wind for all 8 quarters x 4 falls; the hemmed case falls back and says so.
- [x] T03 The fallback order (D3): wind-facing clean, off-wind clean, divided with a wind-facing one first
      research: rendering
      verify: DONE. Order: clean wind-facing, clean off-wind, divided (wind-facing first) - feature 230 unchanged after two MODE 1 exception checks refused the wind-first order (research R4). brook_banks() fixed the divided test (D7). test_cluster covers both fallbacks and brook_banks.

## Phase 2 - measurement (R1-R3)

- [x] T04 R1 trial and R2 seed search, recorded
      research: rendering
      verify: DONE. research R1 (the trial: Kashikawa 0 clumps with the seat unchanged) and R2 (Sawada 1-30, Mizuguchi 1-30 plus five candidates through the real generator).
- [x] T05 R3 cohort both ways, baseline in a detached worktree; every new failure checked against it
      research: rendering
      verify: DONE. Baseline 37/48 in a detached worktree at HEAD; final engine 38/48, every failure also failing on the baseline (scatter_frame_breach), seed 37 fixed, no households_seated failure (research R3, R5).

## Phase 3 - the pool (D4)

- [x] T06 Sawada 6 -> 24, Mizuguchi 23 -> 27 and Kashikawa 3 -> 8, the reason in each generator; all five re-rolled
      research: rendering
      verify: DONE. Sawada 6->24, Mizuguchi 23->27, Kashikawa 3->8 (seed 14 refused for a 333-degree wrap), Inashiro kept at 4; reasons in each gen docstring; all five re-rolled on engine key 1ffef5ec (research R5).
- [x] T07 The pool test: no spec declares a wind; every manifest NW / regional / not off-wind / every household
      seated / belt center within 45 degrees of northwest
      research: rendering
      verify: DONE. tests/hamletgen/test_pool_wind.py: no pool spec declares a wind; every manifest NW / regional / not off-wind / every household / belt center within 45 deg of NW / arc at most 200 deg. Green in make quick.

## Phase 4 - the page (D5)

- [x] T08 `windbreak_default` and its wiring; the class `What`, `Entry`, the snapshot; `siblings.json`
      research: rendering
      verify: DONE. place.windbreak_default wired in page.py (the notes win); Windbreak What hooked not embracing, Entry names vegetation/030, Note names what the side rests on; siblings.json and the snapshot. test_place + test_page cover the three cases.

## Phase 5 - the record and the docs (D6)

- [x] T09 `research/vegetation/030` rewritten to the rule as built, arcs re-measured, the footnote gloss;
      `hamletgen.md`, the two package indexes, the five notes files
      research: rendering
      verify: DONE. vegetation/030 rewritten to the rule as built, arcs re-measured (113/134/87/168/157), gloss corrected; hamletgen.md, hamletgen and sitegen indexes, five notes files. make record also fixed to write the citations page (a notes-only edit was unwritable).
- [x] T10 `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class
      research: rendering
      verify: DONE. quote-check: 2/2 READABLE and VERBATIM, the katabatic clause trimmed to what the quote supports; record-format: Siberian high glossed, maps named, a history clause dropped; entry-drift: IN-STEP (embracing -> hooked applied).

## Phase 6 - acceptance

- [x] T11 `make done` green
      research: rendering
      verify: DONE. make done green on 0d44e65c (merged with main at 19837bc2): every test passed, coverage 100% (27454 statements), roll census green; the batching-test race and the stale roll roster were fixed on the way.
- [x] T12 `settlement-review`, one agent per re-rolled map, findings through `escalation-check`; ledger rows
      research: rendering
      verify: DONE. make verify ruled NO SETTLEMENT-REVIEW OWED (rendering-only feature, feature 248); the one earlier dispatch round came back NOT-REVIEWABLE on a red gate and held no map findings. The five maps are handed to the GM to look at, per their standing rule.

## Phase 7 - the amendment of 2026-09-27: the brook crossed, and the reviews' findings (D9-D14)

- [x] T13 Fords and crossings (D9): `brook_fords`, `gap_segments`, `ford_crossing`; the strike-out, its re-roll and
      the far-bank refusal deleted; `research/water/270` rewritten to the rule as built with the spacing's absence note
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. brook_fords every 160 ft (m:ford-spacing) where the brook bends under 20 degrees, gap_segments opens its corridor 30 ft each side, ford_crossing routes the spur through one, bridges() decks every crossing; far_bank, the strike-out and the brook re-roll deleted. Research pass 2026-09-27 found no source for spacing or form: absence note on research/water/270, whose question and rule paragraphs now state the rule as built; quote-check READABLE/VERBATIM on the Harie notes, its three unlabeled clauses labeled; no new source relied on here; tests: ways/test_checks ford tests, test_pool_261 every brook crossing bridged on all five maps.
- [x] T14 The seeds (D4): Kashikawa 3 and Mizuguchi 23 measured at their originals and kept; Sawada 24 kept
      research: rendering
      verify: DONE. DONE. Measured at the original seeds once crossings existed (research R7): Kashikawa 3 seats 20/20 wind-facing, belt 285 crowns at 320 deg; Mizuguchi 23 seats 12/12 wind-facing astride its brook (4 and 8), the weir back. Both kept; Sawada 24 kept (seed 6 refused by drain and wet toe). Reasons in each generator's docstring and notes.
- [x] T15 A farmstead whole on one bank (D10): `_parts_across_stream`, `across_the_brook`; `research/homesteads/250`
      with its absence note; the unread paper on the GM's download list
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. Settlement._parts_across_stream refuses a configuration whose house-to-part line crosses a stream; across_the_brook refuses a fixture or persimmon seat the same way; unit tests in settlement/test_rolling and hamletgen/test_homesteads; pool 0 across (was Inashiro 4, Mizuguchi 2). Research pass 2026-09-27 (sonnet reader): nothing places parts across or forbids it; research/homesteads/250 a guess with an absence note, mizu-no-bunka-60 quoted VERBATIM (quote-check), source-applicability APPLICABLE-WITH-LIMITS and the limits written into its registry entry; the Asuka paper appended to the GM's download list.
- [x] T16 The copse within reach (D11), the re-seat nudge included
      research: rendering
      verify: DONE. DONE. village_grove near=(points, reach), the re-seat nudge included; copse within 90 ft of a house (m:copse-house-reach) or 60 ft of the belt; test_pool_261 holds it on all five maps (medians 63-72 ft), test_homestead_parts the nudge.
- [x] T17 The entrance board offered the way that meets its anchor (D12)
      research: rendering
      verify: DONE. DONE. stage_notice and place_kosatsuba rank lanes meeting the anchor; kosatsuba_anchor falls back to the approach point nearest the houses; entrance boards 65-139 ft from their anchors, each within 100 ft of a house (test_pool_261); Sawada was 669 ft.
- [x] T18 The brook never doubles back (D13)
      research: rendering
      verify: DONE. DONE. unfold(course, BROOK_MAX_TURN_DEG=100) in water/brook.py; test_water unit test; sharpest turns Inashiro 41, Kashikawa 53, Mizuguchi 53, Sawada 95 (was 123); test_pool_261 holds it.
- [x] T19 The belt's depth held by the pool test, the pop-up naming a direction (D14)
      research: rendering
      verify: DONE. DONE. test_pool_wind belt_depths: every 40 ft bin no way, brook or page edge cuts holds 30 ft (minimums 51-133 ft); the pop-up says toward the northwest; the class text says one or two windward sides.
- [x] T20 The notes, gen docstrings, docs and record say what the maps draw (FR-009, FR-018); `make notes-census`;
      the future-work item closed
      research: rendering
      verify: DONE. DONE. Notes: Kashikawa district southwest (218 deg), Kuwabata northeast (28 deg), the confluence 476/655 ft, Sawada's water story at seed 24, the kept seeds, a dated feature-261 entry per map; make notes-census; hamletgen.md, the hamletgen CLAUDE.md driver row, the future-work item closed to closed.md; the record's arcs re-measured; the scrub keep-out follows the cluster hull (Sawada F5).
- [x] T21 The 48-seed cohort against R3's baseline
      research: rendering
      verify: DONE. DONE. make cohort N=48 on engine 9eba368c: 38/48, failing 2, 8, 23, 25, 28, 31, 35, 36, 40, 46 - each also failing on the R3 baseline, all scatter_frame_breach; seed 37 fixed; 0 farmstead_across_brook (SC-009); 3 of 48 seats off-wind (22 under the retired order).
- [ ] T22 `make done` green on the amendment
      research: rendering
- [ ] T23 `settlement-review`, one agent per map, on the amended maps; findings through `escalation-check`; ledger
      rows (T12's "no review owed" was wrong: the maps' layout moved, and the reviews were owed and run)
      research: rendering
