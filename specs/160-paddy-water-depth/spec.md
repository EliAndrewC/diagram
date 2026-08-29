# Feature Specification: The paddy is not four to six inches deep

**Feature Branch**: none - `SPECIFY_FEATURE=160-paddy-water-depth`

**Created**: 2026-08-29

**Status**: Draft

**Input**: the GM's words in [`request.md`](request.md): *"we should definitely either do more
research to confirm the number or label it as an educated guess."*

## What the research pass found

Dispatched before this spec was written, per constitution XII (research first; a guess is the last
resort). It returned neither of the two outcomes the GM's sentence anticipated - the number is not
confirmed, and it is not merely unsourced. It is **wrong twice**:

- **The number is wrong.** Maintained depth in the sources that give one is **2-4 cm (about one to
  one and a half inches)**, not the 10-15 cm our text asserts. MAFF: *"活着後は水深2~3cmのやや浅水と
  し"* (after rooting, a slightly shallow 2-3 cm). Zennoh, for the critical twenty days from heading:
  *"2~3cm程度の湛水状態を保つことが重要です"*. The only figures near ours are **10 cm and 20 cm, and
  both are an emergency cold-protection measure** at panicle formation and booting - MAFF gives them
  under *"気温が下がる恐れがある場合は"* ("when there is risk of falling temperature") - not a
  maintained depth.
- **The SHAPE is wrong, which matters more.** Depth is staged, not constant: 3-4 cm at rooting, 2-3
  cm at tillering, then **中干し, a deliberate mid-season drain to the point where the surface cracks
  and takes a light footprint**, then intermittent wet-and-dry, standing water again at heading, and
  a final drain before harvest. A single number describing the whole season is the wrong kind of
  sentence however the number is chosen, and ours also omits that the field is deliberately dry for
  a stretch of midsummer.
- **The citation is not defensible.** `tabayashi-1986` is about the distribution and development of
  irrigation systems, classified by water source. It says nothing about water depth. Our own
  `SOURCES.md` "Used for" line already showed this - it lists tameike siting, the single outlet, the
  canal taper and supply/drain separation, and no depth - which is exactly what that field is for.
- **No pre-modern figure exists in anything read.** Both usable sources are modern Japanese
  extension guidance. A search for Edo-period depth records returned infrastructure and water-dispute
  histories and no number.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reader is told something true about the water (Priority: P1)

A player clicks a paddy and reads what it is. Today they are told it holds four to six inches of
water all season. Both halves of that are false.

**Why this priority**: it is the GM's request, and it is a claim the map asserts as fact.

**Independent Test**: open `pool/hamlets/inashiro.html`, click a paddy, read the modal.

**Acceptance Scenarios**:

1. **Given** the paddy modal, **When** the reader reads it, **Then** it does not state four to six
   inches, and does not state any single depth as the season's constant.
2. **Given** the paddy modal, **When** the reader reads it, **Then** it conveys that the water is a
   shallow sheet and that the season is staged, including a deliberate mid-season drain.
3. **Given** the paddy modal's references, **When** the reader opens them, **Then** `tabayashi-1986`
   is not offered as the source for a depth claim.

---

### User Story 2 - The reader knows how good the number is (Priority: P2)

The depths we can now give come from modern agricultural extension, not from any pre-modern record.

**Why this priority**: constitution XII's one failure is telling a reader a guess is a finding. A
modern number applied backward to a pre-modern map is exactly that risk.

**Acceptance Scenarios**:

1. **Given** the paddy modal, **When** the reader reads its liberty line, **Then** it says the
   depths are read from modern extension guidance because no pre-modern figure was found.

---

### Edge Cases

- **The same false number is in SEVEN places, not one.** `classes.py` `paddy.what`; four sibling
  texts (`paddy` against millet, buckwheat, barley and soy) that each repeat it; the `seams.py`
  module docstring; and `research/fields.md`'s aze finding. Fixing the modal alone would leave the
  research record asserting it, which is where the next session would read it back.
- **The bund is NOT re-derived from this.** `research/fields.md` has the aze at roughly 1-2 ft wide
  and about a foot high, separately sourced. A foot of bund over an inch of water is not a
  contradiction to be "fixed": the ridge has to hold the 10-20 cm cold-protection state and keep
  freeboard in rain, and it is walked. Nothing drawn changes, and `AZE_FT` is untouched.

## Requirements *(mandatory)*

- **FR-001**: No text shipped by this repository may state that a paddy holds four to six inches of
  water, in the modal, the sibling texts, an engine docstring or the research record.
- **FR-002**: The replacement text MUST convey a shallow sheet of water rather than a single
  season-long depth, and MUST say the season is staged including a deliberate mid-season drain.
- **FR-003**: `tabayashi-1986` MUST NOT be cited for any depth claim. The two sources actually read
  MUST be registered in `research/SOURCES.md` with what each was used for and its URL.
- **FR-004**: The `paddy` class MUST disclose, in the text the modal shows, that the depths come
  from modern extension guidance and that no pre-modern figure was found.
- **FR-005**: A research entry MUST record the finding, the staging, and the two negatives (no
  pre-modern number; the contradicted citation), and the `SOURCES.md` re-sourcing queue entry that
  feature 159 opened for this MUST be closed out with what was found.
- **FR-006**: Nothing drawn changes. `AZE_FT`, the bund geometry and every manifest stay as they are.
- **FR-007**: `check_village/segments_04a_margins_lanes_and_wells.py` describes a paddy as *"held
  under standing water through the growing season"* - the wrong SHAPE without the number, so FR-001
  does not reach it. It is corrected anyway under constitution XIV (a defect you have seen is fixed
  in the work at hand). Found by spec-fidelity round 1, outside the scope it was given. The check it
  justifies - no wellhead in a paddy - is unaffected either way and MUST NOT change.

## Success Criteria *(mandatory)*

- **SC-001**: `grep -r "four to six inches\|4-6 inches"` over the skill and `docs/` returns only
  RECORDS OF THE CORRECTION - no text that asserts the number. Read that as a category, not as a
  list of directories: `research/fields.md` legitimately holds two of them (the feature-159 note
  that the number could not be sourced, and FR-005's new entry, which must name the claim it
  corrects), alongside the specs, the review ledger and the sources queue. **Do not delete or blur a
  truthful record to make a grep green** - that is the failure this criterion could otherwise
  invite (spec-fidelity round 1).
- **SC-002**: The reference hamlet's `.svg`, `.png` and its manifest's non-`ink_classes` keys are
  byte-identical; this feature changes prose only.
- **SC-003**: A reader of the paddy modal can say whether the field is under water all season. (It
  is not.)
- **SC-004**: No regression - the gate is green.

## Decisions Recorded *(mandatory)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| A paddy is described as a shallow sheet of water, staged through the season, rather than a fixed four to six inches | accurate, with the liberty disclosed - the depths are modern extension figures, no pre-modern number was found | Two extension sources give 2-3 cm maintained at tillering and through the twenty days after heading, and 10/20 cm only as cold contingency; the season includes a deliberate drain to cracking | `research/fields.md` new entry; the `paddy` class's `what` / `label_note` / `caveat`; `SOURCES.md` keys |
| `tabayashi-1986` is dropped as the source for the depth | correction of a mis-citation | The paper is about irrigation-system distribution and says nothing about depth; our own "Used for" line never claimed otherwise | `SOURCES.md` queue entry, closed out |
| The bund's drawn size is NOT re-derived | accurate - unchanged | The ridge answers to the deepest managed state plus freeboard and to being walked, not to the routine depth | this spec's Edge Cases; `AZE_FT` comment untouched |

## Assumptions

- The correction is prose and records only. No geometry, no knob, no map is re-rolled for it beyond
  what regeneration of the reference hamlet's page requires.
- The staged-depth finding is NOT turned into a seasonal knob here. That would be a real feature
  (the map depicts one moment, and which moment is a separate question the GM has not asked); it is
  recorded in the research entry as available if wanted.

## Review history

Constitution XVI: reviewed against the GM's own words by an independent agent before implementation.

| review | verdict | what it found |
|---|---|---|
| spec-fidelity round 1 | **FAITHFUL** | Confirmed "correct it" is the faithful reading, and gave the reasoning the author could not safely give themselves: the GM's two branches were conditioned on the research's outcome, branch A is now unavailable as fact, and branch B was offered on the premise - reported by feature 159 - that the number was *unverified rather than contradicted*, which the research the GM ordered falsified. Executing branch B literally would ship a DISCONFIRMED number labeled as our best estimate. It also held that the spec does not discard branch B: FR-004 IS branch B, applied to the number the record supports. Verified the seven sites, and that `AZE_FT` is a WIDTH so the finding has no geometric path to anything drawn. Three notes taken: SC-001's allowlist reworded so no one deletes a truthful record to green a grep; a seventh site carrying the wrong shape without the number added as FR-007 under Principle XIV; `ink_classes` noted as unmovable by a prose edit. |

**The obligation this leaves, which is the caller's**: the GM ruled on a premise that turned out to
be false. They were told the number was unsourced; it is contradicted. That must be said plainly in
the report, not just recorded here.
