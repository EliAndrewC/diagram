# Tasks: the implementation brought to the research, easiest first (feature 328)

**Input**: plan.md (Phase 1, Phase 2, D1-D4). Only the CURRENT wave's rows are task boxes (spec FR-006); the rest of the
ranking is data in `ranking.json` / `ranking.md`, and the next wave is appended here as an amendment once this one lands.

## Occasions

- none: wave 1 changes `Research:` claim lines only (tier E0) - nothing a map draws or where it is placed moves.
- none (wave 2): each fix moves one value inside a rule that already places the element (a weight, a pitch, a share, a
  count's cap, an extent); no element is new to a map, no glyph is redrawn, and no element is re-placed by different rules.

## Phase 1 - the audit

- [x] T01 the findings snapshot: `findings.json` = every finding of `make claims-report` at `a52ff1bcd` (565) (FR-001)
      research: rendering
      verify: DONE. findings.json: 565 findings (DRIFTED 439, MISLABELED 50, UNCLAIMED 36, NEEDS-RESEARCH 20, CANNOT-TELL 20) from dev/claims-index.json at a52ff1bcd
- [x] T02 the nine ranking batches, one Opus agent each, read-only, from `ranking-brief.md`; every finding tiered E0-E4 with its fix, files and dependencies (FR-002, FR-003)
      research: rendering
      verify: DONE. nine Opus batches (47-76 rows) returned 565 rows, each once (merge.py checked missing/extra = 0); 26 flagged deviation-tempting
- [x] T03 the merge: `ranking.json` in tier order (by module within a tier, dependencies after what they wait on), `ranking.md` generated; E0 rows outside the bounded E0 re-tiered; `tests/test_328_ranking.py` green (FR-001, SC-001)
      research: rendering
      verify: DONE. ranking.json 565 rows: E0 60, E1 162, E2 169, E3 136, E4 38; 30 flagged deviation-tempting. The 30 E0 rows tiered on the unbounded wording re-checked bounded (audit/e0review-out.jsonl): 23 stay E0 with a quoted e0_basis, 7 re-tiered; the shops-face-the-street row moved to E3 (its basis was a recorded DEVIATION, FR-004). Reproducible: python3 audit/merge.py audit . ; tests/test_328_ranking.py 2 passed
- [x] T04 the second reader: 30 rows sampled across tiers re-tiered blind by a fresh Opus reader; a batch disagreeing by more than one tier on more than 5 rows is re-run (plan D4)
      research: rendering
      verify: DONE. 30 rows (6 per tier, seed 328) re-tiered blind: 25/30 exact; 4 off by more than one tier (batches 8, 8, 5, 9) - no batch over 5, so none re-run (plan D4); for the 2 where the second reader ranked higher, the higher taken (audit/overrides.json)

## Phase 2 - wave 1 (tier E0: the claim alone)

- [x] T05 every E0 row's claim corrected to what the implementation already matches, module by module; `make claims-owed` lists them; each re-checked by `impl-drift` from `make claims-bundle` and recorded with `make claims-checked`; every one IN-STEP (FR-004, FR-005, SC-002)
      research: rendering
      verify: DONE. 56 of 57 E0 rows closed IN-STEP by impl-drift (audit/waves.json, from the claims index); 3 rows moved down when the re-check found a code mismatch (the rank step, the merchant kura, the universal shrine sheet - audit/overrides.json); three rounds of claim corrections (113 + 46 + 12 + 1 claims re-checked, bundles 1-8); 15 found rows added (audit/found-wave1.jsonl). Findings 565 -> 523.
- [x] T06 the wave's close: `make claims-report` shows the E0 rows gone and no new finding; `make done` green; `ranking.json` rows marked wave 1; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. make claims-report: 5,934 claims, findings 565 -> 518 (DRIFTED 437, MISLABELED 28, UNCLAIMED 20, NEEDS-RESEARCH 20, CANNOT-TELL 13 at the close; owed 0); no finding introduced beyond the 7 named in claims-followup.md (ranked as found rows); make done green (174 s); ranking.json wave column set from the index

## Phase 3 - wave 2 (tier E1: one value) - amendment 1, 2026-10-07

Wave 2 takes the first sixteen E1 rows of `ranking.json`, less the row pitch and the brook's weight (see below), (the eight procedure fixes that change only the procedure's
own text, and eight single values of the hamlet generator outside its lane code). The E1 row
`hamletgen/consts.py::FOOTPATH_FABRIC_GAP` waits for wave 3: it is the same constant as the lane-law rows, and its
`after` names `ways/bund.py::RunOnBlocks.clear#off the steadings` (spec SC-003). No row of this wave redraws a sheet.

The row pitch (`hamletgen/consts.py::BUNDLE_PITCH`, 100 -> 0038's 92 ft) left the wave on measurement (2026-10-07): at
92 ft Kuwabata's lanes 3 and 8 zigzag across a joint that the engine's joint pass cannot repair (the T's foot falls on
the joint from both sides; both links that would drop the 36 ft jog skirt a steading and are refused). Held at 100 with
the regression gone, it now waits (`after`) for the found row that re-routes such a joint (E3).

The brook's weight (`hamletgen/cluster.py::seat_cluster#brook penalty weight`, 3.0 -> 0035's tiebreak) left the wave on
measurement (2026-10-07, the closing bookend): at 0.05 the 10-household seed 4 seated astride its brook and the settled
web left ten farmhouses off the network (`WebRefused`); restoring 3.0 alone, of the wave's values, rolls it. Held at 3.0
(`cluster.py` as on main), it waits for the found row that lets the web reach a cluster its brook crosses (E3). The rows:

  - `buildings.md::Fire-water tubs#tub glyph` - procedure's tub glyph r5 -> r~3.8 (2.5 ft across); sheets already draw r3.8
  - `buildings.md::Outer court (administrative / public)#archery bank` - archery lane drawn per 0164's yaba ~250 x 8 ft with the azuchi at its end, not ~90 ft (no sheet draws one)
  - `buildings.md::Sacred features#grove crown size` - grove crowns 13-24 ft (0080.drawing's 0.75-1.4 x 17 ft), cited to 0080's drawing page as a guess
  - `buildings.md::Scale#main gate passage width` - Scale section's main-gate passage made the two forms (yakuimon ~6-8.5 ft, nagaya-mon ~12 ft), dropping '~10-13 ft, ~40 px'; sheets already comply
  - `buildings/programs.md::Country shrine (a village district's shrine)#basin beside the approach` - procedure basin sentence: drop 'from Nikko in 1636'; the one pre-1868 pavilion found is Yakyu Inari's (1836), a village's plain basin attested (Nagao 1828)
  - `buildings/programs.md::Country shrine (a village district's shrine)#farmers' stage knob` - procedure knob 6: replace 'none in thirteen' with the record's 1,777 stages nationwide (lost stages and noh/puppet stages included); absent by default stands
  - `buildings/programs.md::Country shrine (a village district's shrine)#precinct size` - procedure precinct sentence: replace the stale 'one Edo set ... 60-240 tsubo' with Saga's Edo returns (lower part of 150-650) and Kami-Nerima 1821 (~10 to ~3,350 tsubo), plus 'a register can also overstate'
  - `buildings/programs.md::Magistrate's manor (county magistracy)#posting wealth knob` - the procedure calls the poor end's look a GUESS (0091 drawing: no page describes how a short-funded office looked); only the shortfall is attested
  - `l7r/diagram/hamletgen/hinterland/parcels.py::WET_SHARE_CAP#woods mostly on dry ground` - WET_SHARE_CAP 0.5 -> ~0 (0077: low ground by a river or marsh is left to grass, not wood)
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#mostly dry` - same constant: woodland parcels on dry ground only, WET_SHARE_CAP -> ~0
  - `l7r/diagram/hamletgen/homesteads/farm_water.py::farm_channel#where the channel ends` - cap the channel's end at one step (~6 ft) off the threshing yard, not up to 3.5 steps (21 ft)
  - `l7r/diagram/hamletgen/homesteads/fixtures.py::_PRIVY_SEATS#four privy seats` - privy seat weights to stable 35, yard 30, front 20, barn 15
  - `l7r/diagram/hamletgen/homesteads/wells.py::_WELL_DRAWN_R#wellhead drawn extent` - take the drawn extent from the glyph's vr (12.376 ft roof half-size, `_well_vr`) and fix the docstring's 16 px
  - `l7r/diagram/hamletgen/homesteads/wells.py::well_target#how many wells` - cap a hamlet's well count at two (min(2, round(households/6)))
- [x] T07 the bookend and the baseline before the first edit: `make perf LABEL=328-w2-start` on the clone while its engine content is main's (0cb60fb5e, nothing edited); that unmodified tree's green gate is the baseline each regression is judged against (plan Phase 2, constitution VI, XIII)
      research: rendering
      verify: DONE. 328-w2-start taken on the clone at main's engine content (0cb60fb5e, nothing edited): total 16.6s, median 3.9s, worst 5.1s (dev/perf-log 20261007T050851Z); the baseline tree's gate green at wave 1's landing
- [x] T08 the eight procedure rows: each sentence or figure in `buildings.md` / `buildings/programs.md` brought to its page; a row whose fix turns out to need a sheet redrawn moves to E3 and says so (FR-003, FR-004, FR-009)
      research: rendering
      verify: DONE. the eight procedure rows brought to their pages (tub r3.8, archery lane 250 x 8 ft, grove crowns 13-24 ft, the gate's two forms, the basin, the stage count, the Edo precincts, the poor posting a GUESS); none needed a sheet; each re-checked IN-STEP (wave 2 bundles 1-4)
- [x] T09 the eight generator values, each with the unit tests it moves, proven first on the reference hamlet (Inashiro) and then across the pool (FR-004, FR-005)
      research: rendering
      verify: DONE. six generator values landed (wet share 0, the channel one step, the privy seats in the page's order, the wellhead's extent from its glyph, at most two wells, WEB_REACH_FT decoupled at 0246's 100 ft); two rows held back on measurement and now wait for found E3 rows: the row pitch (at 92 a Kuwabata joint Z'd) and the brook's weight (at 0.05 the 10-household seed 4 refused); Inashiro looked at; the pool regenerated by the gate
- [x] T10 every unit the wave touched re-checked by `impl-drift` (`make claims-owed` -> bundles -> `make claims-checked`); each wave-2 row IN-STEP; anything the re-check finds ranked as a found row (FR-005, SC-002)
      research: rendering
      verify: DONE. every touched unit re-checked: 271 + 102 + 60 + 16 claims over bundles 1-11; all 14 wave-2 rows IN-STEP (audit/waves.json); what the re-checks found is ranked (audit/found-wave2*.jsonl) and listed in claims-followup.md
- [x] T11 the close: `make perf LABEL=328-w2-end` and the band's records; `make done` green; `ranking.json` wave column; `make claims-report` falls by the wave's rows with nothing introduced beyond a follow-up note; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. 328-start -> 328-end band 1 (total -1.2%; 20-household seed 4 +0.7 s and 10-household seed 25 +0.2 s, both from the privy seats in 0047's order, measured by perf-audit's control and confirmed consistent); make done green (172 s); 14 wave-2 rows IN-STEP in ranking.json's wave column; the findings the re-checks exposed are found rows, listed in claims-followup.md

