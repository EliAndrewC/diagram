# Implementation Plan: the magistracy sheets' open findings (335, carrying 339, 341, 342)

**Spec**: `spec.md` | **Measurements**: `harness.py` (`make spec-harness SPEC=specs/335-magistracies-rear-strips-feature283-reviews-left OUT=<json>`)

## Summary

Three new `tools/pack_audit/` checks, each proven red on a frozen copy of an unfixed sheet before the sheet is fixed (the
landing steps past the revetment, a door not wholly inside a building, a torii not drawn in plan); one bug fixed in the
aligned-gap finder; then each hand sheet redrawn ONCE - Hayakawa (steps, 14 doors, the rear-strip items), Ochiba (7 doors),
Ubame (14 doors, the torii, the rear yard, the servants' partitions) - re-audited, rendered, and reviewed once.

## Decisions

- **D1 - the steps (FR-001, FR-002; research 0176, historically accurate)**: the flight is redrawn notched into the revetment and
  the bank: x 1058-1072 (its water-side end ON the revetment's river face, x 1072; 4.7 ft of run for the treads, its landward 6 px
  cut into the bank street's edge as before), its tread lines at x 1061.5, 1065 and 1068.5, 15 ft wide as drawn (y 492-538). The
  barge's two lines start at the new face (x 1072). The check `steps_past_revetment` reads the rect of the group declared
  `data-id="landing-steps"` and the `data-kind="revetment"` rect, takes the water side as the side facing the `river` shape, and
  reports the px the steps run past that face; red fixture `tests/fixtures/hayakawa-steps-past-revetment-red.svg` (the sheet as
  drawn today, trimmed to the landing).
- **D2 - the door rule (FR-003..FR-005; map drawing convention)**: a door's block is wholly inside the building it is the door of,
  flush to the wall it opens through. Each OUTSIDE or STRADDLE door (`harness.py`'s list) is moved across the edge it abuts or
  crosses by exactly the depth that puts its outer edge on that edge; its size is kept. The host is the building whose tagged group
  holds the door (the harness's max-overlap/nearest host was checked against each group by eye on the list; where they differ the
  group wins). The check `doors_off_their_walls` reads every `data-kind="door"` rect (tag, not fill - the old `door_rects` sees only
  dark fills) and reports one not wholly inside any built footprint (1 px tolerance for the stroke), or wholly inside one but with no edge
  on that footprint's wall (floating just inside it - spec-fidelity's note: the old `floating_doors` reads dark fills only); red fixture a trimmed copy of
  Hayakawa's servants' range and kitchen as drawn today. The rule is written in `docs/buildings.md` (operative), research 0117's
  drawing page (the finding: its "A door glyph sits flush" paragraph says inside, and its program paragraph's "as they set one"
  becomes true), at each sheet's door comment, and here. After the move every sheet is re-audited: a tub now outside
  `TUB_DOOR_MAX_FT` or a door approach the move closed is fixed in the same pass. Done 2026-10-11: the check is red on the sheets
  as they stood (Hayakawa 14, Ochiba 7, Ubame 14 doors - the red runs on Ochiba and Ubame the plan review asked for, from HEAD);
  the move forced four further fixes - Hayakawa's household door from across its two rooms' partition into the family quarters
  (x 310), the karo's house door 6 px down so its tub stays within 10.5 ft, Ubame's kitchen door 6 px down off the kitchen's well
  glyph, and Ochiba's office-hall door drawn after the hall's outline, which painted over it. The one old fixture that must fail
  only its own check (`ochiba-no-scale-red.svg`) took the same door move.
- **D3 - the arches (FR-006..FR-008; drawing rule already settled by feature 268)**: Ubame's approach torii redrawn in plan at the
  shrine's south door, the approach running north-south: the beam a 4.5 px vermilion line x 960.5-1005.5 at y 303, the two
  3.6 px posts at x 964 and 998.4 (10.3 ft clear), the invisible `id="arch"` rect (960.5, 300, 45 x 6). The check `arch_in_plan`
  reports a `data-kind="torii"` group with no `id="arch"` rect; red fixture the Ubame torii as drawn today. Ochiba's altar marker is
  not a torii group and is left (spec D2). If `arch_on_approach` then wants Ubame's approach declared, the approach is declared
  (`id="approach"`) along the shrine's way, not the check waived. The "Modest shrine" clause goes; Ubame's notes record one arch.
- **D4 - Ubame's rear yard (FR-009)**, re-measured 2026-10-11: (a) the garden no longer reaches the rear strip (the garden rect is
  y 326-444, south of the house): NO LONGER APPLIES, recorded. (b) A TRODDEN PATH to the two storehouse doors (plan review round 1: FR-009 asks for a drawn way, the open yard is not one):
  a 7 px (about 2.3 ft) band of trodden earth, lighter than the court's, from the rear alley's service end (x 536, the west end
  of the yard, where the servants' range and the kitchen side meet it) east across the yard at y 216, with a spur up to each
  door (x 647 and x 787). A path, not stepping stones: a rear yard is working ground and stepping stones are a garden's. Its
  class: a GUESS - no page we read draws a way to a storehouse door; drawn because the building review asked for one. (c) The 19 x 31 ft strip east of the reception (x 838-900, y 232-326) joins the rear yard at its top and is clear of the
  garden: it IS the reception privy's service way - the carters come from the rear yard to the privy's east face without crossing
  the garden. Settled by declaring it part of the rear yard: the yard's polygon becomes an L reaching down the strip to the garden's
  top, so the strip is named ground, not leftover. (The finding "its cesspit has no approach that avoids a garden" no longer holds
  on today's sheet; the measurement is recorded.)
- **D5 - Hayakawa's family way out of the inner garden (FR-010)**: NONE drawn. Read at full zoom 2026-10-11: the garden is a
  dashed edge, not a fence, and its west side (x 460, y 326-374) opens onto the court strip between the kitchen and the karo's
  house, which the family's own rooms face; the family walks out there. A wicket is drawn nowhere (research 0104 holds an absence
  note on a wicket; drawing none adds nothing the record does not hold). Recorded at the garden's comment on the sheet.
- **D6 - the well at the middle gate (FR-011; research: physical; historically accurate)**: the search pass (2026-10-11, archive then
  web) found no draw-well on a residence's guest roji: a roji carries stepping stones and a basin; working wells stood by the
  kitchen or bath (Matsue's Shiomi-nawate house, Kaminoyama, Kitsuki, the Urasenke house) or in an official compound's front court
  beside the formal entrance (Iwama jin'ya, 1827); the one tea-roji well curb (Jo-an, 1615) is an homage copy. So the garden well
  at the middle gate's mouth is REMOVED; the kitchen's own well (x 422-444) stands about 13 ft from the bed it watered. The finding
  is recorded on 0104's drawing page (cited, its checks run) by the page sessions in `briefs/r1-write.md` and `r1-check.md`, and the
  sheet's comment points at it.
- **D7 - Hayakawa's rear pocket (FR-012)**: judged 2026-10-11 at full zoom: the ground between the woodshed (x 400-490) and the first
  storehouse (x 590), on the north wall, reaches no door and serves no way the alley below it does not - dead space. CLOSED by
  sliding both storehouses 82 px (27 ft) west, the first to a 6 ft fire gap from the woodshed (x 508). The north-east corner this
  frees (x 638-741) is in use: the second storehouse's door faces east onto it, and it is the carters' ground across the alley
  from the guest privy's cleanout. Tried first and withdrawn: lengthening the woodshed over the pocket (57 x 10 ft) - the woodshed
  is tagged `kitchen` (no woodshed kind exists), so it became the largest `kitchen` footprint and failed the kitchen's size band;
  a woodshed kind of its own would add a modal and its checks, out of this feature's scope.
- **D8 - Ubame's servants' partitions (FR-013; research buildings 910)**: the three bay lines are drawn as sliding partitions - the
  dashed thin line the residences' internal partitions use (`stroke-dasharray`) - instead of solid walls.
- **D10 - a rear yard is open ground to a caption** (found 2026-10-11, fixed here, constitution XIV): `labels/hand_sheet.py`
  `GROUND_KINDS` lacked `rear yard` (feature 283 added the kind), so its outline weighed as an obstacle; once Ubame's yard reached
  the reception privy (D4c), the privy's name was led across the yard into the shrine grove. Added, with a unit test; it re-seats
  captions on Ochiba and Ubame only (the two sheets with a rear yard), both revised and reviewed here.
- **D9 - aligned gaps (FR-014)**: `_blocked` compares a third building's y-extent with the gap's x-interval in the horizontal case
  (the arguments are passed x-range first, as in the vertical case, but tested the other way round). Fixed: one test for both
  orientations; a unit test with three buildings in a row (the middle one blocks) for each orientation, and Ochiba's 28.7 ft pair
  gone from `aligned_gaps`.

## Constitution Check

- XII research: D6 is a physical task with the five boxes; D1, D3 rest on the record; D2, D8 are labeled conventions; D4/D5/D7 each
  recorded with their measurement or class.
- XIII/XIV: the checks are red before the fix; every sheet re-audited; any finding the redraw causes is fixed here.
- XVI literal: each carried entry's ask is a decision above; nothing dropped.
- Performance: no generator stage changes; the three checks run in `pack_audit` on four sheets (linear in their rects).

## Occasions (for tasks.md)

- layout-revised: hayakawa-magistracy, ochiba-magistracy, ubame-magistracy (one `building-review` each, after all its redraws)
- glyph-redrawn: ubame-magistracy torii; hayakawa-magistracy river landing (the steps)
- placement-changed: hayakawa-magistracy door (the door rule)
