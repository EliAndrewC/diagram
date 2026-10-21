# Tasks - feature 405: the engine and record findings moved from 385

Spec: [`spec.md`](spec.md). T01-T27 keep their 385 id in their title (the boxes moved on 2026-10-19, 385 amendment 11); T28 on are found work filed here (FR-002).

- [x] T30 make decide / plan-delta build a bundle whose MANIFEST names request.md when the feature has none; the plan review stops without a verdict - refuse at build time, naming the file to write (found working 405 T12, 2026-10-20) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [x] T31 task-add's next_id counts every T<n> in the files, so a moved task's '(385 T147)' gave 405 the ids T148-T150 - count the boxes' and sections' own ids only (found working 405 T12, 2026-10-20) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [x] T32 Only the task being worked holds a landing: a feature in progress holds a landing through its active task (make task-start) while it is open and the landing does not tick it; the Lands open line and the [lands-open] marks retired (the GM, 2026-10-20; landing-analysis.md) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [x] T33 make land F= T="...": one command for one task or several - every cheap refusal first and together, then make done and make cohort-landing where their records do not cover the content, the gate's regenerated files committed, the push, the ticks; land-batch the same command (landing-analysis.md) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [x] T34 The push asks its cheap questions first: the holding rule and the review gate's occasions run before push_checks.py and the claims gate (landing-analysis.md) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [x] T35 render-sync after a landing runs in the background: sync-with-main.sh done returns once the work is on main (landing-analysis.md) [lands-open]
      research: rendering
      verify: DONE. landed in batch T30+T31+T32+T33+T34+T35: tests/tooling 2076 green; test-sync-with-main and the approval suite green; hooks-test green; each red without its change (plan review CLEAR, D2-D7)
- [ ] T01 (385 T35) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T02 (385 T36) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T03 (385 T37) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T04 (385 T38) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T05 (385 T39) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T06 (385 T40) FR-003: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T07 (385 T12) Carried from T03 by the round arbiter (hour:385-approach-checklist@6, ask:t03-d17-route, ask:t03-seed57-residue): D17's side-by-side merge (saved; F1-F3 merged and seed 49 fixed, six seeds regressed - 7, 24, 37, 51, 52, 57 - because the later settle passes are blind to the junctions it makes), seed 49, seed 55 (lane_knots 1, as at HEAD), seed 57 (lanes 1/13, ends 21.6 ft apart, settle_knots' gather refused by needle_loops; 2 knots against HEAD's 1) and Inashiro F1-F3's glyph-check NEEDS-WORK; done when seed 57 PASSES. Its Approach first asks whether the merge needs a fixed reach at all (REACH 20 then 25 ft is ours), whether the refusals behind seed 49 (a field and farmhouses unreached) rest on research, and whether needle_loops' and needle_joins' rules are research or ours; only then the design that makes the later passes aware of the merge's junctions. Also carried at T03's landing (ask:t03-claims-at-landing): settle.py::theirs DRIFTED - take a lane's own household from fabric.owned_gardens instead of the 80 ft radius, measured on the cohort; Lawful.fault's doubled tail at 15 degrees against 0081's 20 - which number the research fixes, first; clearance.py::_clear_link re-checked once its bundle carries link_survives; its retro row [lands-open]
      research: rendering
- [ ] T08 (385 T111) 0033's drawing page gives a door path only to a farm whose grove stands between it and its street, on the near row; the code lays one for every grove farm its street does not serve (impl-drift aside, T97's round) - settle which, and label it [lands-open]
      research: rendering
- [ ] T09 (385 T112) The track's fallbacks walled as its first route is: _thread_the_fabric's grove fallback, unrouted clip and swing wall only the fabric or the bands, so a track may cross row crops, the paddy or wet ground (DRIFTED) or a brook off its crossing places (CANNOT-TELL); and its five unclaimed decisions - the largest piece kept, a near end counted a junction, an end walked clear along its own leg, the water-crossing limit, the order of the three fallback routes (found working T109, 2026-10-19) [lands-open]
      research: rendering
- [ ] T10 (385 T120) The track out's last resort never crosses a drawn channel (connector_dry_exit, UNCLAIMED, T102's round): claim it, or let it cross a ditch on a plank as 0084 gives (found working T102, 2026-10-19) [lands-open]
      research: rendering
- [ ] T11 (385 T124) web._web_cut_lines' _extent falls back to every house in the cluster when no house stands within WEB_REACH_FT of a cut, so such a lane runs the whole cluster serving none, against 0246 (along the houses it serves; a stretch joining nothing is not drawn) (impl-drift, T106's round) [lands-open]
      research: rendering
- [x] T12 (385 T126) geom._trim_to_service pops a whole last segment before its 4 ft walk, pulling an end back past the last house it serves (0246 §6) - DRIFTED (impl-drift, T106's round) [lands-open]
      research: rendering
      verify: DONE. landed on main 12:35Z: _trim_to_service walks every end in (D1); test red at HEAD, ways 574 green, cohort 16/16, make done green 263 s, landing cohort 54/54; both claims IN-STEP
- [ ] T13 (385 T127) settle.settle_street_ends cuts a street end to other lanes' ends only, never street_anchors, so a farm the street serves without a door path is cut off it (0246 §6) - DRIFTED (impl-drift, T106's round) [lands-open]
      research: rendering
- [ ] T14 (385 T128) sweeps._sweep_dangling_ends pulls an end back by whole vertices with no walk along the segment, past the last house it serves (0246 §6) - DRIFTED (impl-drift, T106's round) [lands-open]
      research: rendering
- [ ] T15 (385 T129) A lane that serves nothing: _pull_back leaves it whole, settle_dangling and tidy_lane_ends drop it, 0246 is silent - research pass, then one rule, claimed (three NEEDS-RESEARCH) (impl-drift, T106's round) [lands-open]
      research: rendering
- [ ] T16 (385 T131) Two UNCLAIMED rules: run_lanes_on_to_the_bund never carries a row street's ends on (skips street); dangling_lane_ends exempts the connector - claim each; and two more in run_lanes_on_to_the_bund (T33's round): how far an end may be carried on (RUN_ON_REACH_FT), and an end carried on to the dry hem's edge as well as the paddy's; and run_on_target's 60 ft carry-on reach (RUN_ON_REACH_FT) and its TIP_MARGIN_FT stop outside the worked ground (impl-drift, T106's round) [lands-open]
      research: rendering
- [ ] T17 (385 T133) Stale words on the lane-end rules: _pull_back's 'ends the lane at the homestead'; WAY_END_REACH_FT's docstring naming the field at 60 ft; _lay_skeleton's span floor 100 ft vs the code's 50; sweeps _SERVE_FT 100 vs 0246's 60; 0246 §6 cited both plain and GUESS (impl-drift, T106's round) [lands-open]
      research: rendering
- [ ] T18 (385 T134) settle.theirs drops the 7 ft gap for every steading within DOORSTEP_FT of a lane end, neighbors' gardens at a junction too - 0246 §16 keeps it off another household's garden: record a DEVIATION or narrow the exemption to the lane's own household (impl-drift, T108's round) [lands-open]
      research: rendering
- [ ] T19 (385 T135) law.fouls_fabric with own set drops its own garden from the check; 0246 §16 keeps an own way off the beds - confirm every caller with own also holds the beds, as fouled_segment does (impl-drift, T108's round) [lands-open]
      research: rendering
- [ ] T20 (385 T138) street.to_its_joints' touch (how close an end must come to count as a joint) arrives from its callers unclaimed - check each call site's value against 0246's reach to another way and claim it; and whether the callers pass field-path and bund ends as joints (0246 §6 lets a lane run on to them) (impl-drift, the T132 batch's round) [lands-open]
      research: rendering
- [ ] T21 (385 T140) 0014's drawing page says 'a sector's first and last rows' (valley fan) with no gloss or glossary term for sector - add the glossary entry or an inline gloss from the valley-fan page (record-format, T33's round) [lands-open]
      research: rendering
- [ ] T22 (385 T141) law.FIELD_REACH_FT counts a way within 60 ft as reaching the field, where 0014 now records the join at 6 ft (a GUESS): five claims DRIFTED on it (refuse_unreached, FIELD_REACH_FT x2, settle_field, settle_reach) - bring the bar to the 6 ft join, or record the 60 ft on 0014 as a DEVIATION with its reason - SPUR_REACH_FT and field_unreached too, so the law gate and the placer read one distance; and whether a dry plot's edge counts as arrived (trim_lane_stubs, field_unreached apply the 6 ft to dry plots; 0014 speaks of the paddy) (impl-drift, T33's rounds) [lands-open]
      research: rendering
- [ ] T23 (385 T142) bund.tip_onto_the_bund returns a spur tip more than 60 ft off, or one whose run-on turns back or is blocked, as it came - short in open ground, against 0014's 'never ends in open ground short of the bund': name the fallback in the claim or make the tip arrive (impl-drift, T33's round) [lands-open]
      research: rendering
- [ ] T24 (385 T144) FR-003: a ranking row in place of T32's, whose row turned out dead code (retired in T143) - a live row, chosen at its start; its retro row [lands-open]
      research: rendering
- [ ] T25 (385 T145) 0043's drawing page, 'How many farmsteads have a wood shed?': 'the share chosen at random for each hamlet from its seed' - seed is the generator's word; reword for a reader (the glossary lists a `seed` variant: check its sense first) (record-format, T34's round) [lands-open]
      research: rendering
- [ ] T26 (385 T146) fixture_seats' wood shed: shed_off_a_wall tests the 9.5 ft only against the house (walls[:1]) while against_a_wall accepts the kura, so a seat can stand 3.5 ft off the kura; in_front lets a flank shed stand partly forward of the front wall; _wood_shed rolls its first seat with zero, unlike the coop and privy; the kura passed as 'N' though a scattered farmstead's kura stands west (0040); against_a_wall's 1.5 ft tolerance lets the shed stand up to ~11 ft out, unclaimed (impl-drift, T34's rounds) [lands-open]
      research: rendering
- [ ] T27 (385 T147) taxonomy._OVERLAP_EXEMPT['farm_fixtures'] says each fixture is 'seated against its own farmhouse' (the shed is 9.5 ft off, shrine and grave 14 ft, the privy up to 48 ft); its claim cites 0039 for the bed beside the house, which only 0038 backs; fixture_seats' CANOPY_PAD and SHADE_MARGIN_FT carry no claim; _seats' privy front step and stable seat unclaimed (impl-drift, T34's round 2) [lands-open]
      research: rendering
- [ ] T28 385's found.jsonl: its 63 rows all read open - map each to the 405 task that carries it, or file it here as a task, and mark the row (the spec review of 405, 2026-10-20) [lands-open]
      research: rendering
- [ ] T29 found.jsonl rows never close: a finding filed as a task (make task-add) or settled keeps status open, so the log cannot say what is unfiled - record the task id or settlement on the row (found working 405 T12, 2026-10-20) [lands-open]
      research: rendering

- [ ] GM review (make gm-reviewed F=405) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)

## Occasions

- none: T12 - a lane end now stops on its last segment where it last serves, not on the vertex before it; the rule it keeps (0246's drawing page, "Lane ends": pulled back to the last house it serves) is unchanged and no glyph is redrawn, so no glyph or settlement review is owed (one pool map, Kuwabata, moved by the gate)
- none: T14 - the finishing sweep's lane ends now stop where they last serve, and a link off a way with nothing at its far end is still emptied; the rule it keeps (0246's drawing page, "Lane ends") is unchanged and no glyph is redrawn, so no glyph or settlement review is owed
