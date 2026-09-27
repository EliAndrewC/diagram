# Feature Specification: A feature inside a feature is its own kind

**Feature Branch**: `264-nested-features-own-kinds` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-27

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): *"I would like for individual features inside of
buildings or other features to get their own individual highlighting"* - the well inside the kitchen *"should get its
own highlighting and separate pop-up"*, and the same for *"the porch in front of the houses. Or the striking posts
within the practice ground. Or the pond within the inner garden. Or the witness/defendent positions, etc."*

## The state, measured

Feature 262 gave every drawn element of a magistracy sheet a kind; an element without its own `data-kind` takes the
nearest enclosing one. So a part drawn inside a feature lights, and opens, as the feature. Measured on the Ochiba page
(2026-09-27, the kind the page names under the pointer): the kitchen well already names `well` (the one example that
was already right); the hearth names `kitchen`, the pond `garden`, a striking post `practice ground`, a kneeling mark
`hearing court`, the genkan `residence`, a clerk's seat `office hall`. The inventory of every such part on all five
sheets is [`inventory.md`](inventory.md); what the record says about each is [`coverage.md`](coverage.md).

## What counts as a feature inside a feature

A **part** is anything drawn within or against a feature that a reader would name as a thing in its own right - an
object, a fixture, a mark, an opening, a room, a porch, a veranda, a corridor, an altar, a vessel. Every part on every
pool magistracy becomes its own kind. What stays the parent's is the parent's own **fabric**: its outline, fill and
texture, the lines that divide it into bays or stalls, a cell's lattice, a roof's edging, a colonnade's posts, the
river's flow chevrons and the bath's steam mark (a sign drawn to say "bath", not a thing in it). The line is drawn by
the question "is this something the reader could point at and ask what it is?"; each fabric element the inventory
lists is named in `inventory.md` with that ruling.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A part lights and opens as itself (Priority: P1)

The GM hovers the hearth inside Ochiba's kitchen: the hearth lights (and every other kitchen hearth on the page),
the kitchen does not; clicking it opens a write-up of the hearth. The same holds for every part the GM named - the
genkan, the striking posts, the garden pond, the witness/defendant positions - and for every other part the
inventory lists.

**Independent Test**: on each of the five pages, the kind named under the pointer at each part's drawn position is
the part's own kind, and its modal is the part's write-up.

**Acceptance Scenarios**:

1. **Given** the Ochiba page, **When** the pointer rests on the hearth, the pond, a striking post, a kneeling mark,
   the genkan or a clerk's seat, **Then** the page names `hearth`, `garden pond`, `striking posts`, `kneeling
   positions`, `genkan`, `clerks' seats` respectively, in both the vector and the raster (zoomed-out) mode.
2. **Given** a part, **When** it is clicked, **Then** its own modal opens, written from the research section that
   covers it, or saying the record has no entry on it.
3. **Given** a labeled room of a building (the reception, the day office), **When** the pointer rests anywhere in
   the room's floor, **Then** the room lights and names itself - not only its label.

### User Story 2 - The whole still lights as a whole (Priority: P1)

Hovering the kitchen still lights the whole kitchen: its hearth and its well light with it, because they are part of
it. Hovering the residence lights every room, the veranda, the corridor and the genkan. Taking the parts out as
kinds must not hollow out the thing they are part of.

**Independent Test**: highlight the kitchen; every element drawn as part of it (the hearth, the kitchen well) is lit.
Highlight `well`; the kitchen is not lit.

**Acceptance Scenarios**:

1. **Given** a part drawn inside its parent's group, or drawn elsewhere in the file for paint order and declared part
   of the parent, **When** the parent is highlighted, **Then** the part lights with it.
2. **Given** a part's kind is highlighted, **When** other kinds contain an instance of it, **Then** only the part's
   instances light, never their parents.

### User Story 3 - What the research does not cover is marked (Priority: P1)

Per the GM's standing instruction (2026-09-26: hold off research passes; *"make sure that everything which later
needs research is marked as such"*), a new kind no research section covers says so on its page and is listed in
`future-work/compounds.md` "Research owed", as are any contradictions `coverage.md` finds.

## Edge Cases

- A part of the same kind drawn free-standing elsewhere (the garden well beside the kitchen well): one kind, both
  light together, as every kind on these pages does.
- A room's floor is part of its building's fill. It is drawn as its own fill over the building's, in the building's
  color, so the picture does not change and the room can light; the building's outline and dividers stay on top.
- A label naming a part lights with the part (as every label does, feature 262).
- The two placer-drawn sheets draw only the practice ground's rack and posts as parts; the placer's emitter writes
  their kinds itself (262 FR-008).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every part (the definition above) drawn on a pool magistracy MUST carry its own kind, one registry
  entry per kind of part, shared across the maps that draw it. The DEFINITION decides; `inventory.md` records it,
  swept over every element that names a parent's kind, inherited or explicitly tagged (a part drawn in a group of its
  own that restates its parent's kind - the nakamon's posts tagged `court divider`, the genkan tagged `residence` -
  counts). A part missing from the inventory is a defect of the inventory, never out of scope.
- **FR-002**: A room labeled on a building MUST light across its floor, not only at its label.
- **FR-003**: Highlighting a kind MUST also light every part drawn as part of an instance of it (a part inside its
  group, or declared part of it); highlighting a part's kind MUST NOT light its parents.
- **FR-004**: Every new kind's write-up MUST be written from the existing record (`coverage.md`), carrying an
  existing classification and naming its section in `Entry:`; where no section covers it, the kind says the record
  has no entry and names no question, and the gap is listed in `future-work/compounds.md` "Research owed" with any
  contradiction `coverage.md` finds. No research pass is run (GM 2026-09-26).
- **FR-005**: A parent kind's write-up MUST no longer claim to cover a part that is now its own kind (its `Covers:`
  and its prose), and MUST keep saying what the parent is.
- **FR-006**: The PNG of every magistracy MUST be unchanged (measured with `make picture-diff`), and the pack audit
  MUST report the same findings before and after.
- **FR-007**: The completeness and closure tests of feature 262 MUST hold: no untagged ink, no unknown kind, and every
  registered kind drawn on some pool magistracy.
- **FR-008**: The hamlet pages MUST be unchanged.
- **FR-009**: Every parent kind that has parts MUST still be named under the pointer somewhere on each of its
  instances - at least its label, where it has one - and clicking there MUST open the parent's own write-up; the
  GM's "separate pop-up" means both pop-ups exist.

### Key Entities

- **Part**: a thing drawn within or against a feature, with a kind of its own.
- **Part-of declaration**: for a part drawn outside its parent's group (for paint order), an attribute on the part
  naming the parent kind, read by the sheet reader exactly as the enclosing group would be.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-009): a browser probe of the five pages names each inventoried part's own kind at its drawn
  position (a point inside each room's floor for a room), in vector and raster mode; zero parts name their parent.
  The same probe (FR-009) finds, for every instance of every parent kind with parts, a point that names the parent,
  and clicking it opens the parent's write-up.
- **SC-002** (FR-003): the same probe, highlighting each parent kind, finds every one of its parts lit; highlighting
  each part kind finds no parent lit.
- **SC-003** (FR-004, FR-005): every new kind's `Entry:` matches `coverage.md`; every kind `coverage.md` lists as
  uncovered is in "Research owed"; no parent's `Covers:` names a part that has its own kind.
- **SC-004** (FR-006): `make picture-diff` reports 0 differing pixels on each of the five PNGs; the pack audit output
  is identical per sheet.
- **SC-005** (FR-007, FR-008): the interactive tests and `make done` green; the hamlet pages' census unchanged.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Each new kind's classification | as `coverage.md` measures it from the record (carried, not re-decided) | FR-004: no new findings | each kind's docstring `Label:` / `Entry:` |
| A part with no covering section is a `guess` saying the record is silent | guess | the GM: research passes held off, gaps marked | the kind's `Note:`; `future-work/compounds.md` |
| Fabric (outlines, dividers, stall lines, lattice, edging, colonnade posts, flow chevrons, steam mark) stays the parent's | map drawing convention | they are how the parent is drawn, not things in it | this spec; `inventory.md` |
| A room is drawn as its own fill in the building's color over the building's fill | map drawing convention | the only way a room's floor can light; the picture is unchanged | the sheet's comment at the first room |
| A lit parent lights its parts | map drawing convention | a building includes what is in it; taking parts out must not hollow it | `interactive/sheet.py`, `page.js` |

## Review history

- Round 1 (2026-09-27, `spec-fidelity`, Opus): CHANGES REQUIRED, two items, both applied. (1) The inventory missed the
  nakamon, because its sweep read only inherited kinds: FR-001 now makes the definition decide, the sweep covers
  explicitly tagged parts, and the nakamon is a part. (2) Nothing kept the parent's own pop-up reachable: FR-009 and
  its SC-001 check added. It ruled the part/fabric line, the rooms (FR-002) and FR-003 legitimate.
- Round 2 (2026-09-27, `spec-fidelity`, Opus): FAITHFUL - both items resolved.
- After acceptance, spec-lint only: SC-001 names FR-009 in its FR list (the text already carried the check).
- Plan review (`spec-fidelity` MODE 4): CLEAR on D1-D9; BLOCKED on D11 while the id map's unblended text reached
  hamlet pages (FR-008); CLEAR once it was scoped to sheet pages.
