# Feature Specification: Rename the `grave island` class to `field grave`

**Status**: In progress (2026-10-10) - the GM: "Yes, please."; spec-fidelity round 2 FAITHFUL

**Affects**: hamlet, interactive page

**Input**: request.md - the entry as filed (settlement-review of Kashikawa, 2026-09-28) and the GM's go-ahead, 2026-10-10.

## Why

Feature 267 made the field grave a knob with two forms - an island inside a plot (the Chinese form) or a grave in a plot's
corner (the Japanese form) - but the page class kept the name of one of them. A corner-form hamlet's hover says "grave
island" while its own note says the grave is "not an island" (Kashikawa's review raised it twice).

## User Scenarios & Testing

### US1 - the hover names what the map draws (P1)

A reader hovers a field grave on any hamlet and the page names it a field grave, whichever form the hamlet rolled.

**Acceptance**: 1. Given Kashikawa (corner form), when its field grave is hovered, the class shown is `field grave`, with
the same modal text as before apart from its name. 2. Given an island-form hamlet, the same. 3. Given a map's notes keyed by
the class, the sentence still reaches the modal.

## Requirements

- **FR-001**: The page class whose key is `grave island` is renamed `field grave` everywhere the key is used: the engine's
  ink tags, the class registry, the title card's collision text, the sibling pairs, the modal file and its Name, the maps'
  manifests and notes keys, and the tests.
- **FR-002**: Nothing a reader sees changes but the name and the two sibling texts that named the class: the glyph, its
  placement and the About, Guesses and Depiction text are unchanged; the `siblings.json` pairs with the paddy and the field
  rock say "the field grave" for "the grave island", the first adding that it stands "on an island in a plot or in its
  corner", so it is true of both forms.
- **FR-003**: The island FORM keeps its name - the `grave_form=island` choice and its modal, `_plot_grave_island`, and the
  glossary term `grave island`, whose definition (since feature 267) names the island form, "the Chinese form of the field
  grave" - because they name the form, not the class; renaming the term would define every field grave as a mound in a
  plot's middle, the contradiction this feature removes.
- **FR-004**: The rename is carried by the class snapshot's renaming table, as `bathhouse -> bath room` was (the snapshot of
  feature 189 is never edited).

## Success Criteria

- **SC-001**: No shipped hamlet's manifest or page names `grave island` as a class; Kashikawa's names `field grave`.
- **SC-002**: The interactive tests pass, and Kashikawa's manifest differs from before only in `ink_classes` (its geometry unchanged).

## Decisions Recorded

- The modal's research checks are not re-run: only its Name line changed, and its About, Guesses and Depiction passed them
  under the old name in feature 319; `modal-form`, the check that reads the name, ran on the renamed modal (map drawing
  convention for the name; no physical claim moves).

## The entry, as filed

Feature 267 made the field grave a knob - an island inside a plot (the Chinese form) or a grave in a plot's corner (the
Japanese form) - but the page class is still keyed and named `grave island`, so a corner-form hamlet's hover says
"grave island" while its own feature note says the grave is "not an island". Kashikawa's review raised it twice; it was
accepted for 267 with that note standing in. The rename touches 17 files: the ink tags in `settlement/fields/features.py`,
`GraveIsland` in `interactive/classes/water_and_ways.py`, the glossary term, `place.json`, `siblings.json`,
`overlap/taxonomy.py`, `tools/placement_stages.py`, the Mizuguchi and Kashikawa manifests' `ink_classes`, and the pinned
snapshot `tests/fixtures/classes_before_189.json` (through `SINCE_189`, the renaming table the snapshot test keeps).

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED.
  1. The entry lists "the glossary term" among what the rename touches; no requirement carries it or records its
     exclusion, and plan D5 keeps it - a narrowing that lives only in the plan. Ruled LEGITIMATE on the request's purpose:
     the term's definition has named the island FORM since feature 267 ("the Chinese form of the field grave"), so renamed
     it would define every field grave as a mound in a plot's middle, the contradiction the request removes. FR-003 must
     name the glossary term `grave island` as kept, with that reason.
  2. FR-002 says nothing a reader sees changes but the name; the diff rewords both `siblings.json` pair texts, adding
     "standing on an island in a plot or in its corner". The reword serves the request; the spec must say so (FR-001 or
     FR-002 names the sibling texts' reword).
  Measured, no change needed: Mizuguchi's manifest names no grave class at HEAD; `overlap/taxonomy.py` keys
  `field_graves`, its "grave island" is a comment. Implementation note under FR-001: `interactive/place.py:71`'s comment
  still names the class as `grave island`.
- spec-fidelity, Mode 3 (verify), round 2 (2026-10-10): FAITHFUL.
  1. RESOLVED - FR-003 names the glossary term `grave island` as kept, with the reason (its definition names the island
     form since feature 267); the quoted definition matches `glossary.json` at HEAD; plan D5 now agrees with the spec.
  2. RESOLVED - FR-002 names the two `siblings.json` texts (paddy, field rock); its quoted wording matches the file.
  Read in full: the FR-002 and FR-003 diff hunks, plan D2/D5, the `siblings.json` pair texts, the glossary entry and
  `place.py:68-73`. Aside: FR-002 no longer lists "the PNG" by name; "nothing a reader sees" still covers it.
