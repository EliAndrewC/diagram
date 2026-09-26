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
4. **Given** a kind no existing finding classifies (no research section and no folded `types.json` item), **When**
   the GM clicks it, **Then** the modal leads "This is a guess - ..." and says in so many words that the record has
   no entry on it yet; and a kind that only a folded `types.json` item classifies shows the gap by having no "See
   references" link.

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

Because every kind carries its classification, a kind no existing finding classifies is labeled a guess on the page,
and a kind no research section covers has no "See references" link. The GM can click through a magistracy and see
which parts rest on research and which do not, which is the "big bonus" they named.

**Independent Test**: the closing report to the GM lists both sets - the kinds labeled `guess` because no existing
finding classifies them, and the kinds no research section covers - and each one's modal shows it as stated.

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
- **FR-003a**: The magistracies tier's `required` entries in `buildings/types.json` MUST be folded into the
  registry, as the design the GM accepted says (*"`buildings/types.json`'s required features folded in rather than
  kept beside it"*): each item names the Mode A kind it is, its classification and its reason are stated ONCE, in
  that kind's registry entry, and its label-to-kind binding is the sheet's own tag. The pack audit's program and
  size-band checks, `buildings/programs.md` and anything else that read the item's class, why or label pattern
  derive them from the registry and the tags; no magistracy item keeps a class, a why or a label pattern in
  `types.json`. What stays there is what only the audit needs: the item's id, its size band, its forms, whether it
  is optional. (The country-shrine tier keeps its own entries until its page is built - out of scope.)
- **FR-004**: The outer court and the inner court (and any further court a sheet draws, such as Ubame's border
  court) MUST each be highlightable as a region of its own ground, with its band label lighting with it.
- **FR-005**: Every write-up MUST be written FROM the existing record and name its research section in `Entry:`
  where one exists; no new research finding is made in this feature, and no existing finding is re-decided. A kind
  an existing finding already classifies - a research section, or the `types.json` item folded into it (FR-003a) -
  keeps that classification, carried with its reason into the kind's note (a size the item called a guess or a
  convention becomes the kind's stated caveat); where no research section covers it, the kind names no question,
  so the page's missing references show the gap. `guess` because the record is silent applies only to a kind no
  existing finding classifies, and its note says the record has no entry on it. A kind `coverage.md` measures as made by the
  setting's canon or the map's story, with no historical counterpart the record covers (the threshold stones, the
  GM's own example), is labeled `deviation` and written from the GM's canon (`l7r.md`) and the map's design notes. Which kinds fall in each case is MEASURED against the record before the
  writing starts (`coverage.md`), not assumed.
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

- **SC-001** (FR-001, FR-006, FR-007, FR-008): All five pool magistracies write a page, the placer's two among them; each page's census reports 0 unclassed elements and 0
  unregistered kinds, and every registered kind is drawn on at least one of them.
- **SC-002** (FR-004, FR-005, FR-010): The GM's two examples hold on the Ochiba page: the threshold stones' modal leads with "deliberate
  deviation"; the hearing court's modal announces no liberty and lists at least one research question; the outer and inner courts each light their own ground; and the stones'
  modal carries Ochiba's own note on them under "On this map".
- **SC-003** (FR-009): Each hand-drawn sheet's PNG is pixel-identical before and after the feature (measured), and its pack
  audit output is identical (measured).
- **SC-004** (FR-002, FR-003, FR-006): Changing one kind's write-up is one edit, and changing one element's drawing or label is one edit -
  proven by the completeness test failing on an untagged or unknown element and passing on a tagged one.
- **SC-006** (FR-003a): No magistracies item in `types.json` carries a `class`, a `why` or a `label`; `programs.md` renders
  each item's class and why from its kind, and the pack audit finds each item by its tag - with every sheet's
  audit output unchanged (SC-003).
- **SC-005** (FR-011): Every hamlet page's registry and output are unchanged (the hamlet interactive tests pass untouched
  except where they are generalized to cover both registries).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Each Mode A kind's classification | as its research section says (copied, not re-decided) | FR-005 - no new findings | each kind's docstring `Label:` / `Entry:` |
| A kind no existing finding classifies (no research section, no folded `types.json` item) is a `guess` | guess | the GM: tie into existing research only; the gap is shown, not filled | each such kind's `Note:`; listed in the closing report |
| A `types.json` item's class and why move into its kind | as the item already said (carried, not re-decided) | FR-003a: the classification is stated once | each kind's `Note:` / `Caveat:`; `coverage.md` |
| Setting-specific features are `deviation` | deviation | canon (`l7r.md`, the map's notes), which needs no citation | each such kind's `Note:` |
| A drawn label lights with the feature it names | map drawing convention | a label is the feature's ink on a labeled plan; hamlet pages do the same for the placard | `interactive/compound/` module docstring |
| Title and scale bar are not highlighted | map drawing convention (ruling) | they are the sheet's apparatus, not a feature of the compound | the not-highlighted rulings record |
| Court ground split into one rect per court | map drawing convention | the only way to light one court's ground; paints what one rect did | the sheet's comment at the split |

## Assumptions

- The Hoshigaoka country shrine (Mode A, not a magistracy) is out of scope; the machinery built here serves it later
  with a tagging pass and its kinds, and that is named as follow-up in the closing report.
- A place card (the title placard's modal) for a magistracy is not asked for; the placard is ruled not highlighted.
- The page is gitignored and derived like every pool page; the tagged SVG is the tracked source.

## Review history

- Round 1 (2026-09-26, `spec-fidelity`, Opus): CHANGES REQUIRED, two items, both applied. (1) The accepted design
  folds `buildings/types.json`'s magistracies items into the registry and the spec had left that out - FR-003a added.
  (2) FR-005 would have relabeled kinds `types.json` already classifies - FR-005 now carries existing
  classifications, with the affected set measured (`coverage.md`).
- Round 2 (2026-09-26, `spec-fidelity`, Opus): CHANGES REQUIRED, two items, both applied. (a) FR-005's example list
  pre-labeled the salt wards and the Fox border as deviations against the measurement - it now names only the
  threshold stones and defers to `coverage.md`. (b) User Story 1's scenario 4, User Story 4 and a Decisions row used
  "the record is silent" where FR-005 carries classifications - all now use "no existing finding classifies".
- Round 3 (2026-09-26, `spec-fidelity-verify`, Opus): FAITHFUL.
- Amendment (2026-09-26, `spec-fidelity-verify`, Opus): FAITHFUL - each success criterion names the requirements it
  measures (spec-lint), SC-001 names the placer's two maps and the closed registry, SC-002 the courts' own ground and
  the map's note.
