# Feature Specification: five things about highlighting

**Feature Branch**: none (`SPECIFY_FEATURE=153-highlight-legibility`)

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM, 2026-08-29, in full: *"Thanks. That is much better. Here are a few things related to highlighting. First, the pond sluices are really hard to click on, and I think we should do the thing where we give them a larger highlight box. similar to what we are doing with the field ditches. Second, when the Mulberry dikes are highlighted that we can no longer see the greenery along them. So I think it would make sense to highlight both the dikes themselves and also the plants which are rendered onto the dikes so that when someone has The modal active, then it will be clear that there is cultivated plant life growing on top of the thing, which they have highlighted. We should also do the thing where the pond sluice modal links to the field ditch modal and vice versa, as we do with e.g. woodland commands and windbreak forests. We can do the same with the two different dike modals too. I think I would also like the windbreak model to actually say "Windbreak forest" instead of just "windbreak"."*

## What the GM asked for

Five separate things, all about the highlight and the modal. Nothing else.

1. **A pond sluice is hard to click.** Give it a fat hit box, *"similar to what we are doing with the
   field ditches"* - which is `HIT_WIDEN`, the invisible widened copy of a thin mark.
2. **A highlighted mulberry dike loses its greenery.** Highlight the dike AND the plants on it, so a
   reader with the modal open can see *"that there is cultivated plant life growing on top of the thing,
   which they have highlighted"*. Today one `fill` covers the whole group and the dike goes flat.
3. **Pond sluice and field ditch link to each other**, as woodland commons and windbreak forest do.
4. **The two dike modals link to each other** likewise.
5. **The windbreak modal says "Windbreak forest"**, not "windbreak".

## User Scenarios & Testing

### US1 - the sluice can be hit (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a dike-pond map, **When** the page is written, **Then** each pond sluice mark carries a
   widened invisible copy, as a field ditch does.
2. **Given** that page, **When** the pointer is near a sluice but not exactly on its 2.4 px stroke,
   **Then** the pond sluice class highlights.

### US2 - a highlighted crop dike still reads as planted ground (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a mulberry dike highlighted, **When** the reader looks at it, **Then** the bank and the
   coppiced crowns are BOTH lit and still tell apart, so the dike reads as planted rather than as a
   solid block.
2. **Given** any other class, **When** it is highlighted, **Then** nothing about its look changes.

### US3 - the modals link (Priority: P2)

**Acceptance Scenarios**:

1. **Given** the pond sluice modal, **When** it is open, **Then** it links to the field ditch modal, and
   the field ditch modal links back.
2. **Given** a crop dike's modal, **When** it is open, **Then** it links to the perimeter dike modal, and
   back.

### US4 - the windbreak is named in full (Priority: P3)

1. **Given** the windbreak modal, **When** it is open, **Then** its heading reads "Windbreak forest".

## Requirements

- **FR-001** `pond sluice` MUST get a `HIT_WIDEN` entry. Its mark is a 2.4 px line, thinner than a field
  ditch's, so it takes at least the ditch's widening.
- **FR-002** When a crop dike is highlighted, its bank and its planted crowns MUST both be highlighted
  and MUST remain distinguishable from each other. (The crowns already carry the DIKE's own class - that
  is why they light today, and why they vanish into it: one highlight color covers both. So this is a
  distinction WITHIN one class, not a new class and not a re-tagging.)
- **FR-003** FR-002 MUST NOT change how any other class highlights, and MUST NOT change the drawn map -
  the SVG and PNG stay byte-identical (feature 134 FR-010), so this is a page-side distinction only.
- **FR-004** `pond sluice` and `field ditch` MUST be siblings, with text that says how they differ.
- **FR-005** The crop dike and the `perimeter dike` MUST be siblings, likewise.
- **FR-006** The `windbreak` class MUST be named "windbreak forest". Its KEY does not change - the key is
  what the ink carries and what `all_ink_is_ruled_on` checks.

## Success Criteria

- **SC-001** A pointer within the widened box of a sluice highlights the pond sluice class.
- **SC-002** With a mulberry dike highlighted, the crowns are a different color from the bank.
- **SC-003** Five new sibling pairs appear in both directions - `pond sluice` <-> `field ditch`, and each
  of the four crop dikes <-> `perimeter dike` - and the existing pairs are untouched.
- **SC-004** The windbreak modal's heading reads "Windbreak forest" (the registry holds `windbreak forest`
  lowercase; the page capitalizes the heading, as it does every other name).
- **SC-005** `make done` green; the pool maps gate clean; the page still matches its own SVG (feature 148
  R3's check, ~0.03%).

## Assumptions

- **FR-002 and FR-005 both read one rolled label as its kind.** The GM wrote "the Mulberry dikes" and
  "the two different dike modals", naming what was on the sheet in front of them. The crop dike is one
  knob whose VALUE is the label, and both defects - one fill covering the greenery, and the confusion
  with the perimeter dike - are identical on a cane, banana or fruit dike. Writing either requirement
  for mulberry alone would leave the reported defect standing on three of the four values while
  claiming the feature had fixed it. Declared here, and adjudicated by the spec review.
- **The crop dike is a rolled knob with four values** (`mulberry`, `sugarcane`, `banana`, `fruit`), each
  its own class. The GM said "the two different dike modals", speaking of the two on the map in front of
  them - mulberry and perimeter. FR-005 is written for the crop dike WHICHEVER kind it is, because the
  distinction from the perimeter dike is identical in all four cases and a cane hamlet would otherwise
  ship a half-linked pair. Flagged for the spec review as the one place this reads past the GM's words.
- "Windbreak forest" is written lowercase in the registry to match every other name there (`fish pond`,
  `field ditch`); the page styles the heading.

## Review history

- **Round 1, `spec-fidelity`, 2026-08-29: CHANGES REQUIRED.** Three findings, all accepted and fixed
  above. SC-003 counted two sibling pairs where the spec creates five; SC-004 said the modal "reads
  windbreak forest" without saying that the heading is what the GM sees or that the registry holds the
  name lowercase; and FR-002 did not record that the crowns ALREADY carry the dike's class, which is
  what makes this a distinction within one class rather than a new class or a re-tagging.
- **Round 2, `spec-fidelity`, 2026-08-29: FAITHFUL.** Every clause of the GM's message traced to a
  requirement, nothing found that was not asked for, and the declared read-past (four crop-dike values
  where the GM said "the two different dike modals") adjudicated as within the request: it is one
  relationship over a rolled label, the page shows a sibling only when both classes are present, and
  restricting it would leave the reported defect standing on three of the four values. Two non-blocking
  asides, both taken: FR-002 generalizes in exactly the same way and the Assumptions block now says so,
  and US4's scenario has been brought into line with SC-004's "Windbreak forest".
