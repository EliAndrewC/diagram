## claims gate at T05 (2026-10-18), refusals
claims-gate: REFUSED owed (new): l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#front-row standoff from the field set by the house and its yard
claims-gate: REFUSED owed (new): l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#the shed counted in the standoff, the garden not
claims-gate: REFUSED introduced: DRIFTED        l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#the front row's size - on the dispersed path the row is capped at `max(6, round(sqrt(N*(lo+hi))))` and `_seat_rank_rounds` seats ranks behind it, but the page has a scattered settlement's "whole line is hugged to the field edge in single file"; either seat single file or record a DEVIATION on the page

## 328 ranking row (open, E3 kept)
{
 "key": "l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a scattered hamlet's seating",
 "tier": "E3",
 "fix": "seat a scattered hamlet's farms in single file hugged to the field edge, no front-row cap, brick ranks or cloud",
 "files": [
  "l7r/diagram/hamletgen/homesteads/stages.py"
 ],
 "after": [],
 "flag": "",
 "tier_as_ranked": "E3",
 "verdict": "DRIFTED",
 "wave": "",
 "scope": "kept"
}

## the 1.3:1 floor (impl-drift round 3, MISLABELED on a withdrawn claim)
impl-drift: 2 claims - MISLABELED 2; UNCLAIMED 0

VERDICT l7r/diagram/hamletgen/homesteads/wells.py::shared_row_wells#a farm counted to its nearest street MISLABELED - GUESS is the right class, since 0033 spaces farms along the street and lays streets side by side but never says how far a farm may stand from its street. But the label's "nearest street" is not what the code does: `mine = [... if d <= 2.0 * frame_w]` counts a farm to every street within two frames, not only the nearest one. Relabel it "a farm counted to each street within two farmstead frames", or make the code keep only the nearest street [§7, §8, §11, §12, §24]
VERDICT l7r/diagram/settlement/houses.py::HousesMixin._try_place_bundle#a caller's squarer house kept MISLABELED - This is not a GUESS, because 0029 answers it: "No farmhouse is drawn squarer than about 1.3 to 1". The code (`if max(size) > FARMHOUSE_MAX_ASPECT * min(size)`) holds a caller's stated size only to the 2.7:1 ceiling and exempts it from the 1.3:1 floor, and the page records no such exemption, so as written the code drifts from §64. Either hold sized callers (and the lot ladder) to the 1.3:1 floor as they are held to 2.7, or record the exemption on 0029 and claim DEVIATION research/questions/0029-farmhouses-minka.drawing.html [§63, §64]
## houses.py sizing unchanged since main: git diff origin/main shows only the claim lines and household_parts' dropped well

## pool rolled on T05's tree, 2026-10-18 (make maps SCOPE=all, exit 0)
REGENERATED  inashiro          17.7s
REGENERATED  kashikawa         10.6s
REGENERATED  kuwabata           9.6s
REGENERATED  mizuguchi          7.4s
REGENERATED  sawada            11.9s

[1mmaps clean[0m
pool-index: wrote /diagram/.clones/diagram-backlog/pool/index.html

## the standoff claim, rounds 2 to 5
### t05-standoff.txt
impl-drift: 1 claim - CANNOT-TELL 1; UNCLAIMED 0

VERDICT l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#front-row standoff from the field set by the homestead core's reach (house, yard, shed, well pocket; garden excluded) CANNOT-TELL - The house's distance from the paddy is still decided by code this bundle does not include. `front_row` only hands off to `_front_row_from_chains`, which is not here, and the chains come from `install_site_boundary`, also not here. The visible code passes `standoff=None` and `envelope=_reach`, so the core's near face (yard, shed or house end) sits on the chain with no gap added. `turn_the_seat` and `_ground_push` only move a seat outward, never nearer. So "never nearer than 6 ft", measured from the house's corners, and "10 to 13 ft" both depend on how far the chain stands off the paddy and on anything `_front_row_from_chains` adds. Bundle those two to decide. A house set further back, behind its yard, is allowed by "No farmhouse is held to a maximum distance". Separately, the label lists a "well pocket", but the code's comment says a clustered household has carried none since feature 374, so the label can drop it. [§210, §211, §212]
### t05-standoff2.txt
impl-drift: 1 claim - NEEDS-RESEARCH 1; UNCLAIMED 0

VERDICT l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#front-row standoff from the field set by the homestead core's reach (house, yard, shed; garden excluded) NEEDS-RESEARCH - the house-and-yard part is backed by the page: the yard stands before the south wall and the homestead turns "as one" (§204); the core's near edge is held the wall gap plus a foot (and the slack) beyond a chain already pushed out by the paddy's keep-out, so "no farmhouse wall stands within 6 ft" holds (§210); and §212's "no farmhouse is held to a maximum distance" covers a house set a yard's depth further out than §211's drawn 10 to 13 ft. But the page places nothing about the shed (kura) or the garden beds relative to the paddy. Two decisions rest on nothing in it: holding the shed off the paddy at the wall's gap, and leaving the garden free to stand nearer the paddy. Keep the house/yard part on 0029.drawing and give the shed-in and garden-out rule its own UNRESEARCHED line [§204, §210, §211, §212]

The bundle is `/tmp/l7r-check/claims-standoff2/MANIFEST.md`, and the cited page is `/tmp/l7r-check/claims-standoff2/questions/0029-farmhouses-minka.drawing.html.txt`. I judged this unit on which parts of the homestead count toward the paddy. The gap figures themselves (`HOUSE_PADDY_GAP_FT`, `STANDOFF_SLACK_PX`) are not stated anywhere in the bundle, and they are not this claim's to answer: they belong to the claim on `_front_row_from_chains` ("the wall rule's gap plus a foot").
### t05-standoff3.txt
I could judge one of the two claims. The other is CANNOT-TELL, because the constants that set the house's distance from the field are not in the bundle.

impl-drift: 2 claims - IN-STEP 1, CANNOT-TELL 1; UNCLAIMED 1

VERDICT l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#front-row standoff from the field set by the house and its yard CANNOT-TELL - the 6 ft floor holds by construction: the reach is taken at the largest house's corners and then turned (`turn_the_seat`). Whether front houses stand the page's "drawn 10 to 13 ft" off the paddy needs three values the bundle does not inline: `HOUSE_PADDY_GAP_FT`, `STANDOFF_SLACK_PX`, and the keep-out the site-boundary chords are already pushed out by. It also needs to know whether the placer pulls a smaller house in toward the field. If it does not, a house rolled at 0.85 of the length stands its reach off at `_house_max` (46*1.35), so it sits up to about 11.5 ft farther out than the largest house; if the largest sits at 10 to 13 ft, that is past the page's range. [§187, §204, §210, §211, §212]
VERDICT l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#the shed counted in the standoff, the garden not IN-STEP - the page applies the minimum to the house wall only and turns the yard and beds with the house; it never places a shed or garden beds against the paddy, so counting the shed in `_core` and leaving the garden out is unresearched [§204, §210]
UNCLAIMED l7r/diagram/hamletgen/homesteads/stages.py::_seat_households - a row village's whole farmstead, grove included, stands off the field (`_reach` from `_g0["bbox"]` on the linear form), not just the house and yard
