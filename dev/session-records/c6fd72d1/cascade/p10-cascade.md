# Cascade P10 (polder follow-ups: 0018, 0019 drawing pages) - owed checks, 2026-11-24

Clone `/diagram/.clones/diagram-backlog` at d76187f689 (page session P10's commit). Nothing staged, committed or pushed;
no rust/ file edited. Working files: `/home/agent/.claude/jobs/c6fd72d1/tmp/cascade/p10/` (every tool output and agent
reply); bundles under the session scratchpad (`p10-mt`, `p10-owed`, `p10-dir`, `p10-hold`).

## Counts per stage

| stage | in | out |
|---|---|---|
| `make claims-owed` at start | 68 claims: 65 triage-only, 3 rests changed (all `field/ponds.rs`) | |
| `make claims-triage` | 65 | 65 cleared by the tool unread (FR-005 a: no rested block moved); no bundle, no agent |
| impl-drift, owed (`claims-bundle OWED=1`) | 3 (`LEAST_SHARE#the least pond`, `rounded#the bank's inset`, `rounded#the least pond`) | 3 IN-STEP; `claims-checked` 3 of 3 recorded |
| impl-drift, DIRECTED (6 claims, PAGES = 0018, 0019, 0068 drawing) | 6 | 6 DRIFTED (2 fix: code, 4 fix: claim); the tool printed "6 of 6 recorded" and one HELD line (451 T218, exit 3), `a creek's mouth`, which "stays owed" |
| impl-drift, T218 re-judge (1 claim, PAGES = 0014 drawing, 0019 drawing, 0019) | 1 | DRIFTED fix: claim; recorded (exit 0) - the hold cleared on one re-judge, as last time |
| `make record-owed` at start | 34 units by the delta, 26 unanswered, all `modal-depiction` (the 8 record checks were answered by P10's check session) | |
| `make modal-triage` | 26 | 23 cleared by the tool; 3 to the agent (`hamlet/pond-canal`, `hamlet/fish-pond`, `choice/pond_layout--grid`) |
| modal-triage agent | 3 | `NONE` - nothing touches; `modal-triaged`: 0 of 3 sent on |
| pop-up checks, `record-checked`, `apply-edits` | 0 | none run: nothing sent on, no EDIT |
| `make record CHECK=1` | | builds cleanly (4416 pages) |
| `make quick` | | clean (green-local recorded) |

Spend: 3 impl-drift dispatches (owed 18 s, 45k in / 1.1k out; directed 56 s, 60k in / 5.2k out; re-judge 28 s) and 1 modal-triage (21 s,
14k tokens); 3 ledger rows written (`make ledger-owed WRITE=`).

## Verdicts, quoted

Owed (`field/ponds.rs`, all IN-STEP):
- `LEAST_SHARE#the least pond` IN-STEP - "0.1 is the tenth §17 gives for a parcel too small for its bank, which §17 records
  as a GUESS; the sliver case belongs to `rounded`'s claim [§17]"
- `rounded#the bank's inset` IN-STEP - "the inset ... is applied on every side alike, and a parcel that falls back to the
  least pond is excepted, as §3 and §17 say [§3, §17]"
- `rounded#the least pond` IN-STEP - "the code covers both of §17's cases: the inset fails (`pushed_in` returns None), or
  a side of the water is shorter than LEAST_SHARE times the parcel's same side; either way the parcel is shrunk about its
  middle to a tenth across [§17]"

Directed (all DRIFTED):
- `field/polder.rs::ditches#the ring canal on a dike-pond block` DRIFTED fix: code - "the code still sets the four trunks
  at the rice rungs whatever the creek width (`w: 4.5, w_tail: 1.5` / `1.5` / `4.0 -> 1.5` / `1.2 -> 5.5`), so a 6 to 8 ft
  `creek` opens on a 1.5 ft trunk; fix: code (on a dike-pond block, set every trunk to at least `creek`; the claim then
  cites 0019 §18 as the GUESS's record); effect: map - each dike-pond creek is drawn wider than the ring canal it joins".
  EXPECTED: 449 T427's finding.
- `field/polder.rs::ditches#the widths` DRIFTED fix: code - "the claim gives the ring canal the rice ladder's rungs 'on
  either form', which 0019 now contradicts for a dike-pond block; ... the supply arms, the deliveries with their 0.8 cap,
  the drain and the dike-pond column channels at creek width all match their pages; fix: code (as in the ring-canal
  claim; this claim then limits the ladder's trunk rungs to a rice polder)". `claims-checked` dropped its 0019 rests (a
  page it does not cite), as the prediction foresaw: T427's builder adds the citation.
- `field/polder.rs::ditches#a creek's mouth on the ring canal` DRIFTED fix: claim - first HELD by 451 T218 ("it says the
  pages are silent, and the record's nearest pages ... are not in the bundle (0019 research page, 0014 drawing)"); the
  re-judge: "the code does what the page now says ... but the claim still calls the 0019 drawing page 'silent' ... fix:
  claim (restate as `GUESS ...0019...drawing.html: a creek between ponds stops where it meets the ring canal, its end drawn
  to the ring canal's middle line and no farther`, keeping the half-width stop and the measured 4-in-2,700 ends); effect:
  none [§16, §18, §19, §138]".
- `polder/creeks.rs::EASE_STEPS#the easing's steps` DRIFTED fix: claim - "the claim says the 0019 drawing page has 'no rule
  for a block it pinches', but 0019 now gives it ... `EASE_STEPS = 20` matches; cite 0019 drawing §30 ... drop 'no rule'".
- `polder/creeks.rs::eased#room for the creeks` DRIFTED fix: claim - "the code matches 0019 §30 ... but the claim cites
  0019 only for 'its strength a calibrated liberty' (§29) and points its GUESS at 0018 ... point the GUESS at 0019 drawing
  §30".
- `polder/creeks.rs::creek_width#one width a block` DRIFTED fix: claim - "the code ... is exactly 0018's new block ... but
  the claim points at #creek-width-between-ponds (§99) and argues from the page's silence ... cite 0018 drawing §100".
- NOTED, NOT FILED (dropped: no `effect:` tail, 451 T219): "0019 drawing §19 holds only once §18 does: while the ring
  canal stays 1.5 ft, a creek end stopped at its middle line has a 3 to 4 ft rounded end that fills the trunk's whole
  width." - a T427 note, not a defect of the page.

Pop-ups: modal-triage replied `NONE` for `hamlet/pond-canal`, `hamlet/fish-pond`, `choice/pond_layout--grid`. No EDIT
anywhere.

## PREDICTED vs ACTUAL

| prediction | actual |
|---|---|
| `ditches#the ring canal on a dike-pond block` DRIFTED fix: code until T427 | exactly that |
| `ditches#a creek's mouth` "IN-STEP, then restated" | DRIFTED fix: claim (the agent's call: a "silent" claim against a page no longer silent is a wording DRIFT, effect none); held by T218, cleared on one re-judge |
| `EASE_STEPS`, `eased`, `creek_width` IN-STEP then restated | all DRIFTED fix: claim, effect none - same substance, verdict word stricter |
| `ditches#the widths` owed nothing by the pair; directed check; T427 adds the citation | DRIFTED fix: code; its 0019 rests dropped by `claims-checked` (uncited page) |
| `LEAST_SHARE`, `rounded#the least pond` IN-STEP | IN-STEP both (+ `rounded#the bank's inset` IN-STEP, owed by the same rest) |
| 0018: `CREEK_FT`, `ditches#the creeks' width`, `row_ditches#the row ditch's width` SHOULD re-check | cleared by the tool (FR-005 a); not directed. My read (no agent verdict): `ditches#the creeks' width` and `row_ditches#the row ditch's width` state one creek width a block with no taper citing only `creek-width-between-ponds` - the same under-citation `creek_width` was ruled DRIFTED fix: claim for; `CREEK_FT` ("no page giving a channel between ponds a width before modern times") stays true |
| 0019 neighbors (`DRIFT_SHARE`, `Warp.at`, `RING_FT`, `ditches#the ring canal`, `polder#the ring canal's place`, `RING_CANAL`) IN-STEP | cleared unread by the tool; not directed |
| 0018 pop-ups: `pond-canal`, `fish-pond` re-check; `dikepond_split--*`, `mulberry-dike`, `fruit-dike`, `fry-pond` sent on for the least pond | 23 cleared by the tool, including all the dikepond_split, mulberry/fruit/fry kinds; `pond-canal` and `fish-pond` (plus `pond_layout--grid`) to the agent, all untouched |
| 20 research-note pop-ups (0018's "commissioner" note) clear | none was even owed: `record-owed` owed only the 26 `modal-depiction` units whose `Drawing:` page moved |
| 0019 pop-ups `pond_layout--mosaic`, `field_archetype--mulberry_dike_fishpond`, `water_source_position--corner_high` re-check | owed, cleared by the tool unread |
| `pond-canal` SHOULD come to carry the width guess on Guesses; lose "not every dike-pond hamlet need have had water a boat could travel" | not done: no check sent it on, no EDIT. Its Guesses tab holds only the inlet/outfall guess; it states neither the creek width (6 to 8 ft) nor the ring canal's bound; About says "How wide or deep the canals between the ponds ran before modern times is not recorded". The Depiction sentence on boats is still there (line 25-26) |
| `fish-pond` "mosaic among winding rivers"; `sluice-gate` "upstream head ... downstream tail" as fact | both still stand; `sluice-gate` cleared by the tool, `fish-pond` triaged untouched. Not hand-edited (brief: report, do not add) |

## Judgment

(a) **Over-cascade: none.** 65 of 68 claims and 23 of 26 pop-ups cleared by the tool; the owed impl-drift was 3 claims,
all IN-STEP, the pop-up triage 3 units in 21 s. The `rounded#the bank's inset` claim was re-owed by the restated block
though it states nothing of the least pond's sliver case - cheap, inside the same bundle.

(b) **Under-cascade: as in every all-additions session, the owed machinery could not see it.**
- All 6 non-IN-STEP verdicts came from the DIRECTED check; the owed machinery found none of them. Four are the "stale
  silent / under-cited" pattern again (`a creek's mouth`, `EASE_STEPS`, `eased`, `creek_width`), cleared by FR-005 a
  because a new block is a block no claim rests on. Two (`ditches#the ring canal on a dike-pond block`, `ditches#the
  widths`) are the real code finding T427 owns - the second visible only because the brief named it: it cites 0068 only,
  so no 0019 change could ever re-owe it, and `claims-checked` drops its 0019 rests.
- Not directed, read by me (no agent verdict): `polder.rs::RING_FT#the ring canal` ("the offsets a GUESS, 6 and 12 ft"),
  `ditches#the ring canal`, `polder#the ring canal's place`, `driver/check.rs` `the ring canal` state the ring's PLACE,
  none its width: not stale. But `RING_FT` = (6, 12) is the offset the ring sits in - T427's builder must check an 8 ft
  ring canal still fits it. `ditches#the creeks' width` and `row_ditches#the row ditch's width` under-cite
  `one-creek-width-a-block` (items 7-8 below). `CREEK_FT` stays true.
- The check handoff's echo list (`.git/l7r-handoffs/p10-polder-followups-check.md`, "Wording that pop-ups or claims may
  echo"): grepped "ladder's widths", "map's seed anywhere", "about a fifth gentler", "reached the dike's inner face" over
  the modals and `rust/phases/src`: one hit, the `a creek's mouth` claim's own measured fact ("the end ... reached the
  dike's inner face"), which is the code's measurement, not an echo of the page - kept in item 3. No pop-up echoes any.
- Pop-ups: the new GUESS items reach no pop-up (451 T226), as predicted. `hamlet/pond-canal`'s Guesses tab states neither
  the creek width nor the ring canal's bound; its About line "is not recorded" stays true (the width is the project's
  guess), so no ACCURACY fault, but a reader of the map cannot learn that the 6 to 8 ft creeks and the ring no narrower
  than them are this project's choice. The two older wording points (`fish-pond`'s flat mosaic, `sluice-gate`'s "upstream
  head" as fact) and `pond-canal`'s boat sentence remain, cleared unread.

(c) **Rules that fired.**
- FR-005 a (page moved, no rested block moved): 65 claims cleared.
- Rests changed: 3 owed (0018's restated least-pond block).
- Modal triage's tool clearance: 23; the agent: 3, `NONE`.
- 451 T218: held 1 line (`a creek's mouth`, the known misfire: "the claim says silent, the page no longer is"); one
  re-bundle with the guard's PAGES (0014 drawing, 0019 drawing, 0019) cleared it.
- `claims-checked` dropped rests on pages a claim does not cite (`ditches#the widths` on 0019; `a creek's mouth` on the
  0019 research page) - harmless, the directed bundles carry extra pages on purpose.
- 451 T219: the NOTED line dropped for want of an `effect:` tail.
- Decide-first guard: not refused this time (the task in the description and `DECIDE_OK` in each prompt from the start).

## Rust claims to restate (not done; rust/ not edited)

T427's builder must change these BECAUSE THE CODE CHANGES (fix: code):
1. `rust/phases/src/field/polder.rs::ditches#the ring canal on a dike-pond block` - after T427: "GUESS
   0019...drawing.html (`ring-canal-width-dike-pond`): on a dike-pond block the ring canal's reaches drawn no narrower
   than the block's creek width (0018 drawing `creek-width-between-ponds` / `one-creek-width-a-block`), every trunk at
   least `creek`"; drop "no width of its own" and the "creek opens on a ring canal narrower than itself" sentence.
2. `rust/phases/src/field/polder.rs::ditches#the widths` - limit the ladder's trunk rungs (4.5 to 1.5, 4.0 to 1.5, 1.2 to
   5.5) to a RICE polder; add the citation of 0019 drawing `ring-canal-width-dike-pond` for the dike-pond form.

Wording only (code IN-STEP, fix: claim, effect none):
3. `field/polder.rs::ditches#a creek's mouth on the ring canal` - "GUESS 0019...drawing.html
   (`creek-mouth-on-ring-canal`): a creek between ponds stops where it meets the ring canal, its end drawn to the ring
   canal's middle line and no farther" - drop "silent", keep the half-width stop and the measured ends.
4. `field/polder/creeks.rs::EASE_STEPS#the easing's steps` - cite 0019 drawing `pinched-mosaic-eased` ("eased a twentieth
   at a time"); drop "no rule for a block it pinches".
5. `field/polder/creeks.rs::eased#room for the creeks` - ADD 0019 drawing `pinched-mosaic-eased` as the GUESS of the easing; keep its 0018 `creek-width-between-ponds` citation for the 6 to 8 ft (it rightly cites 0018 for the width).
6. `field/polder/creeks.rs::creek_width#one width a block` - cite 0018 drawing `one-creek-width-a-block`; drop the argument
   from the page's silence ("a range and no figure within it"; "the page names no wider or narrower kind ... no end to taper
   toward" is now the page's own words).
7. (my read, not judged) `field/polder.rs::ditches#the creeks' width` - add 0018 drawing `one-creek-width-a-block`.
8. (my read, not judged) `field/polder.rs::row_ditches#the row ditch's width` - add 0018 drawing `one-creek-width-a-block`.

Every item id above exists as a `data-item` on its page (grepped: `ring-canal-width-dike-pond`, `creek-mouth-on-ring-canal`,
`pinched-mosaic-eased` on 0019 drawing; `one-creek-width-a-block`, `creek-width-between-ponds` on 0018 drawing).

## Owed at the end

- `L7R_LAND_ALONE=1 make claims-owed`: no claim is owed.
- `L7R_LAND_ALONE=1 make record-owed UNANSWERED=1`: no record check is owed.
- The 6 DRIFTED verdicts are FINDINGS listed by `make claims-report` (with `field/staged.rs::polder_stage#a rice polder's pocket pond`, already DRIFTED in HEAD's index: pre-existing); at the claims switch's `report` setting they refuse no
  landing and filed no task. Nothing counts as OWED.
- `make record CHECK=1`: builds cleanly (4416 pages). `make quick`: clean (re-run after the index writes: see
  `p10/quick2.log`).
- `make ledger-owed` after `WRITE=`: clean; 3 rows, no `?`.
- Pop-ups: the predicted `hamlet/pond-canal` re-check did NOT happen (triage `NONE`), and no directed pop-up check was run.
- Files changed (uncommitted): `dev/claims-index.json`, `dev/claims-pages.json`, `dev/review-ledger.md` (3 rows).
