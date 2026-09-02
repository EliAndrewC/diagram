# Feature 176 - The lit placard keeps its name; the placement page catches up

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI)
**Request**: `request.md` (the GM's words, verbatim, two messages)

## Why

Two things the GM saw while reading the hamlet deliverables, both about a reader being able to
READ what the page shows them.

1. On the interactive HTML map, hovering the title card lights it: the highlight paints every
   filled element of the hovered class gold (`page.css`, `g.f.on *:not([fill="none"]) { fill: var(--hl) }`).
   The card's rectangle and the settlement's name share the reserved class `place` (feature 156,
   `settlement/finish.py`), so the name is painted the SAME gold as the card under it and vanishes.
2. `dev/placement-stages/hamlet-placement.html` - the plated walk-through of the hamlet's `STAGES` -
   is generated from `NOTES` in `tools/placement_stages.py`, and three stages have no entry there:
   `stage_waterward` (5), `stage_pond_stock` (9) and `stage_labels` (18). Each shows as
   "(no note yet)". The label phase (feature 157) and the notice board's move to after the frame
   (feature 154) are both rules the repository has - `driver.py` records them at `STAGES` and
   `dev/placement.md` rows 17 and 18 state them - but the page the GM reads says nothing about the
   labels and, for the board, its note still calls it "the LAST thing placed" with a stage after it.

## Scope

**In**: the highlight styling of the placard's NAME on the interactive map; the stage notes of the
placement-order page and its re-plating; a test that keeps the page from going silent on a stage again.
**Out**: anything else on the title card (the GM: *"I don't care whether anything else on the title
card is readable or not"* - the scale bar beneath the name is `cls="-"`, not part of the lit class,
and is not touched); the highlight colors of any other class; the stage ORDER itself (`STAGES` is the
generator's design and the page reports it, per the page's own lede); `dev/placement.md`, which is
already current on both rules.

## Functional requirements

- **FR-001** While the title card is highlighted, the settlement's NAME MUST remain readable: its
  text color MUST have decent contrast against the highlight fill. "Decent" is made measurable as
  the WCAG AA threshold for normal text, a contrast ratio of at least 4.5:1, computed from the two
  colors in `page.css` and recorded at the point of change.
- **FR-002** The change applies to the name on the lit placard and nothing else: the card itself
  still lights gold like every other hovered class, and no other class's highlight changes.
- **FR-003** `hamlet-placement.html` MUST carry a note for EVERY stage in `STAGES`; none may render
  as "(no note yet)". The three missing notes are written from the stages' own recorded reasoning
  (`driver.py`'s `STAGES` comments, the stage docstrings, `dev/placement.md`), and they say what the
  GM named: that the labels are their own final step, after the last map feature, and why; and that
  the notice board comes after everything else THAT IS A FEATURE - after the frame, before only the
  label phase - and why.
- **FR-004** The notice board's existing note MUST be reconciled with the stage that now follows it:
  it is the last FEATURE placed, and the note says so and names what comes after.
- **FR-005** A test MUST fail whenever a stage in `STAGES` lacks a `NOTES` entry, or `NOTES` names a
  stage that no longer exists - so the page cannot silently go stale in this way again. It MUST be
  shown to fire (red on the tree before the notes are added, green after).
- **FR-006** The page is RE-PLATED from the current engine (`make placement-stages`) so the
  committed HTML and plates match the notes and today's `STAGES` - the page's own lede says to re-run
  it when `STAGES` changes, and `STAGES` has changed twice (features 154 and 157) since it was last
  re-run with all its notes.

## Decisions Recorded

All rendering-class decisions (nothing physical is decided here):

- **D1** The name keeps the map's own ink (`--ink`, `#2D2A24`) on the lit card rather than taking a
  new color: 9.2:1 against `--hl` `#FFC83D`, and it is the color the name already has, so a reader
  sees the card light and the name stay put. A white or a darker gold were not priced - the existing
  ink clears the bar by a factor of two and adds no color to the palette.
- **D2** The rule is scoped to the placard's class (`g.f.on.f-place text`) rather than to every
  `text` in every lit class: the GM asked about the title card, and the placard is the one lit class
  whose text sits on its own fill. Widening it would change other classes' highlights, which FR-002
  forbids and nobody asked for.
- **D3** The stale docstring on `stage_waterward` ("Called from `stage_hinterland`" - it has been its
  own stage 5 since feature 150) is corrected in passing (Principle XIV: a defect found is fixed in the
  work that found it). Docstring-only, so it re-keys nothing.
