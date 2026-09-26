# Feature Specification: Interactive magistracy pages

**Feature Branch**: `262-interactive-magistracy-pages` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-26

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): *"clickable user interactable versions of the
magistracy maps that tie into our research"*, using *"existing research findings that already exist, rather than
doing new research findings"*, so the GM can *"highlight things like the outer courtyard versus the inner courtyard
and see write-ups of what these things were and the extent to which this is indeed based on real historical research
or is a thing specific to this fictional setting"*; with the constraint that *"the labels and the features on the
building diagram for each magistracy have a common source, such that changing that source in one place is enough to
change it downstream"*, and that we *"not create a process by which we are by hand making the same changes in
multiple places."* The GM accepted the session's proposed design on 2026-09-26 (*"That sounds great"*): tags in the
hand-drawn SVG, one shared registry of kinds written from the existing record, a script that writes the page, and a
test that every drawn element carries a known tag. The magistracies stay hand-drawn.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore a magistracy by hovering and clicking (Priority: P1)

The GM opens `ochiba-magistracy.html` beside the map's PNG. Hovering the outer court lights the outer court's ground
and its label; hovering the inner court lights the inner court's. Clicking either opens a write-up of what that court
was in a real magistrate's compound, with "See references" listing the research questions it rests on. Clicking the
Vermilion threshold stones opens a write-up that leads by saying they are a deliberate deviation - something of this
setting, not of history.

**Why this priority**: it is the whole of what the GM asked to see, on the map they named.

**Independent Test**: write the Ochiba page, open it, hover and click the outer court, the hearing court and the
threshold stones; the first two do not announce a liberty and link at least one research question, the third leads
with "This is a deliberate deviation".

**Acceptance Scenarios**:

1. **Given** the Ochiba page, **When** the pointer rests on open ground of the outer court, **Then** every element
   tagged as the outer court lights and nothing of the inner court does.
2. **Given** the Ochiba page, **When** the GM clicks the hearing court, **Then** the modal says what an oshirasu
   was, why it stands before the office hall, and "See references" lists the record's question(s) about the
   courtroom and the two-court split.
3. **Given** the Ochiba page, **When** the GM clicks the threshold stones, **Then** the modal leads "This is a
   deliberate deviation - ..." and says what the setting's canon makes of them (the senior Pact-Bowl checkpoint).
4. **Given** any kind whose research record is silent, **When** the GM clicks it, **Then** the modal leads "This is
   a guess - ..." and says in so many words that the record has no entry on it yet.

---

### User Story 2 - Every magistracy map in the pool gets its page (Priority: P1)

Every map under `pool/magistracies/` writes its `.html` page beside its `.png` whenever it is rendered: the three
hand-drawn sheets (Ochiba, Hayakawa, Ubame) and the two sheets the compound placer generates (the county example and
the Ochiba round-trip test).

**Why this priority**: the GM's words are "the magistracy maps", and the standing goal is that every scripted map is
interactive; a page for one of five would be "X except where Y".

**Independent Test**: run each of the five `.gen.py`; each writes an `.html` whose census reports no unclassed ink
and no unregistered kind.

**Acceptance Scenarios**:

1. **Given** a hand-drawn sheet, **When** its `.gen.py` runs, **Then** it writes the PNG as before AND the page.
2. **Given** a placer-generated sheet, **When** its `.gen.py` runs, **Then** the SVG the placer writes already
   carries each element's kind, and the page is written from it the same way.

---

### User Story 3 - One source, no double bookkeeping (Priority: P1)

The GM or a session redraws a building on a hand-drawn sheet, relabels it, or adds a new one. The page follows on
the next render with no second file to edit. A new element drawn without a kind fails a test naming it; a kind the
registry does not know fails a test naming it. Rewording what a KIND of thing is (the granary's write-up) is one
edit that reaches every magistracy page carrying a granary.

**Why this priority**: the GM's one stated constraint.

**Independent Test**: add an untagged `<rect>` to a copy of a sheet - the completeness test fails naming it; tag it
with an unknown kind - the test fails naming the kind; tag it with a known kind - it passes and the page lights it
with that kind.

**Acceptance Scenarios**:

1. **Given** a sheet, **When** an element is drawn with no kind anywhere in its ancestry and is not ruled out,
   **Then** the magistracy completeness test fails and names the element.
2. **Given** the registry, **When** a kind is registered that no pool magistracy draws, **Then** a test fails - the
   vocabulary is closed over the maps it serves, as the hamlet vocabulary is.
3. **Given** a label drawn on the sheet, **When** its text changes, **Then** nothing else needs editing: the label
   is part of its kind's ink and the modal's heading is the registry's name for the kind.

---

### User Story 4 - The page shows where the research is thin (Priority: P2)

Because every kind carries its classification, a kind whose record is silent is labeled a guess on the page. The GM
can click through a magistracy and see which parts rest on research and which do not, which is the "big bonus" they
named.

**Independent Test**: the list of Mode A kinds labeled `guess` because the record is silent is printed in this
feature's closing report to the GM, and each one's modal says so.

### Edge Cases

- A tagged group containing a child tagged with another kind (the magistrate's dais inside the office hall): the
  child's kind wins for the child's subtree; the rest of the group keeps the group's kind.
- Ink that is not a feature of the compound - the sheet background, the title, the scale bar - is ruled out of
  highlighting with a recorded ruling, never left untagged.
- `<defs>` patterns are not ink and need no tag.
- A hand-drawn sheet's other readers (the pack audit, the size table, render-sync) must read the tagged sheet exactly
  as they read the untagged one.
- The two courts are one ground rect today on most sheets; splitting it into a rect per court must not change the
  picture (the ground pattern is in user space, so two abutting rects paint what one did) and must keep the
  precinct declaration the pack audit reads.
- A host without resvg writes the vector-only page, as a hamlet page does.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every map in `pool/magistracies/` MUST write `<map>.html` beside its PNG when rendered, through the
  same interactive page the hamlets use (hover lights every element of a kind; click opens its write-up; "See
  references" lists research questions; glossary tooltips; the four-way label with the presumption of accuracy).
- **FR-002**: What each drawn element IS MUST be declared ON the element in the SVG (a kind attribute on the
  element or on an enclosing group, the nearest one winning), so the drawing is the single source of where a thing
  is, what it is called and what kind it is. No side file maps elements to kinds.
- **FR-003**: What a KIND is - its name, what it is, why it stands where it does, its classification (accurate /
  deviation / convention / guess), its note, its sources and the research section it was written from - MUST live
  in one registry of Mode A kinds, in the same docstring form as the hamlet classes, shared by every magistracy.
- **FR-004**: The outer court and the inner court (and any further court a sheet draws, such as Ubame's border
  court) MUST each be highlightable as a region of its own ground, with its band label lighting with it.
- **FR-005**: Every write-up MUST be written FROM the existing research record and name its section in `Entry:`;
  no new research finding is made in this feature. A kind the record does not cover is labeled `guess`, its note
  saying the record has no entry on it. A thing specific to the setting (the threshold stones, the salt wards, the
  Fox border) is labeled `deviation` and written from the GM's canon (`l7r.md`) and the map's design notes.
- **FR-006**: A test MUST fail, naming the element, when any drawn element of a pool magistracy carries no kind and
  is not ruled out; and naming the kind, when a kind is not in the registry.
- **FR-007**: The registry MUST be closed over the maps: a Mode A kind no pool magistracy draws fails a test.
- **FR-008**: The placer's SVG emitter MUST write the kind of every element it draws, taken from the program's
  declarations, so a generated sheet needs no tagging by hand.
- **FR-009**: The PNG of every magistracy MUST be unchanged by the tagging (the page is a second serialization of
  the same drawing), and the pack audit MUST report the same findings on every sheet before and after.
- **FR-010**: Where a generic kind has a particular on one map (Ochiba's shrine is a two-altar Inari hall; Hayakawa's
  bath was enlarged by its magistrate), the particular MUST reach that map's modal from the map's own notes file,
  never by writing a second copy of the kind.
- **FR-011**: The Mode A vocabulary and its rulings MUST NOT change any hamlet page.

### Key Entities

- **Kind tag**: an attribute on an SVG element naming its kind, or the not-highlighted ruling.
- **Mode A kind**: one registry entry - the reader's write-up of one kind of thing in a compound plan.
- **Map notes block**: the existing per-map annotations in `<map>.notes.md` that the page shows as "on this map".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five pool magistracies write a page; each page's census reports 0 unclassed elements and 0
  unregistered kinds.
- **SC-002**: The GM's two examples hold on the Ochiba page: the threshold stones' modal leads with "deliberate
  deviation"; the hearing court's modal announces no liberty and lists at least one research question.
- **SC-003**: Each hand-drawn sheet's PNG is pixel-identical before and after the feature (measured), and its pack
  audit output is identical (measured).
- **SC-004**: Changing one kind's write-up is one edit, and changing one element's drawing or label is one edit -
  proven by the completeness test failing on an untagged or unknown element and passing on a tagged one.
- **SC-005**: Every hamlet page's registry and output are unchanged (the hamlet interactive tests pass untouched
  except where they are generalized to cover both registries).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Each Mode A kind's classification | as its research section says (copied, not re-decided) | FR-005 - no new findings | each kind's docstring `Label:` / `Entry:` |
| A kind the record does not cover is a `guess` | guess | the GM: tie into existing research only; the gap is shown, not filled | each such kind's `Note:`; listed in the closing report |
| Setting-specific features are `deviation` | deviation | canon (`l7r.md`, the map's notes), which needs no citation | each such kind's `Note:` |
| A drawn label lights with the feature it names | map drawing convention | a label is the feature's ink on a labeled plan; hamlet pages do the same for the placard | `interactive/compound/` module docstring |
| Title and scale bar are not highlighted | map drawing convention (ruling) | they are the sheet's apparatus, not a feature of the compound | the not-highlighted rulings record |
| Court ground split into one rect per court | map drawing convention | the only way to light one court's ground; paints what one rect did | the sheet's comment at the split |

## Assumptions

- The Hoshigaoka country shrine (Mode A, not a magistracy) is out of scope; the machinery built here serves it later
  with a tagging pass and its kinds, and that is named as follow-up in the closing report.
- A place card (the title placard's modal) for a magistracy is not asked for; the placard is ruled not highlighted.
- The page is gitignored and derived like every pool page; the tagged SVG is the tracked source.
