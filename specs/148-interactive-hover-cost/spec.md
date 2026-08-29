# Feature Specification: the interactive map's hover cost

**Feature Branch**: none - this repository does not use feature branches (`SPECIFY_FEATURE=148-interactive-hover-cost`)

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM, 2026-08-29: *"Now I notice that kuwabata.html is much slower to load and more sluggish than inashiro.html - I'm guessing there are some places where we're checking for mouse pointer hovering by looking at individual lines and glyphs rather than by drawing bounding boxes, and that's why - does that sound right?"* - and, when the diagnosis and the proposed fix were put to them: *"yes please"*.

## What the GM asked for

One thing: **make the interactive page stop resolving hover against individual glyph geometry where a
bounding box would do**, because that is why `kuwabata.html` is sluggish next to `inashiro.html`.

The GM's guess was checked and is correct. Hover is resolved by the browser, not by our code: the page
listens for `pointerover` on the SVG and reads `e.target.closest("g.f")`, so every pointer move makes the
browser hit-test the real drawn geometry - and for a stroked `fill="none"` path that is stroke-geometry
hit-testing across every subpath. Measured on the two pages, path data by feature class:

| class | inashiro | kuwabata |
|---|---|---|
| scrub and rough grazing | 5.93 MB / 229,646 subpaths | 6.76 MB / 260,374 subpaths |
| marsh | 1.61 MB / 53,956 | 1.35 MB / 45,723 |
| every other class together | ~0.08 MB | ~0.40 MB |

Two classes are ~95% of everything the browser hit-tests on both maps, and kuwabata carries more of it -
3,455 `<path>` elements against inashiro's 1,576, worst-case merged path 2.2 MB / 87,603 subpaths against
1.6 MB / 63,738.

The bounding boxes the GM assumed were missing DO exist - `hit_regions` builds footprint polygons for the
scatter classes and `marks_region` a 24 ft grid for scrub - but they are placed at the BOTTOM of the stack
and, as that function's own docstring says, everything drawn later "keeps the pointer". So the boxes are
ADDITIVE: they catch bare ground falling through, while the scatter above them is still hit-tested in full.

## User Scenarios & Testing

### US1 - the heavy scatter stops being hit-tested (Priority: P1)

A reader opens a map whose ground is mostly scrub and marsh and moves the pointer across it. The
highlight follows as it does today, and the page does not lag.

**Independent Test**: the generated page carries `pointer-events: none` on the scrub and marsh ink, and
the browser test still highlights those classes from a point inside their ground AND from a point on a
disabled mark.

**Acceptance Scenarios**:

1. **Given** a map with scrub and marsh, **When** the page is written, **Then** the ink of those classes
   is not hit-testable and their regions are.
2. **Given** the reference hamlet's page in a browser, **When** the pointer is moved onto bare scrub,
   **Then** every scrub feature highlights, exactly as before this change.
3. **Given** the same page, **When** the pointer is moved onto a house, a lane or a bund standing ON that
   ground, **Then** that feature highlights and not the scrub - the ink drawn above keeps the pointer.

### US2 - no class loses its hover (Priority: P1)

**Independent Test**: for every class whose ink is made non-hit-testable, its region coverage is asserted
to contain the class's own marks - a tuft outside its polygon would otherwise go dead.

**Acceptance Scenarios**:

1. **Given** any pool hamlet, **When** the page is written, **Then** no class has its ink disabled unless
   its hit region is present on that page AND covers that class's own marks - presence alone is not
   enough, per FR-002.

### One thing the session told the GM was inexact

The proposal the GM approved said the fix was safe *"since those two classes already have region coverage
built from their own marks"*. That is exact for SCRUB - `HIT_FROM_MARKS` contains scrub alone, and its
region is `marks_region(..., within=polys)`, built from the marks themselves. It is NOT true of MARSH,
whose region is the recorded `marshes` footprint polygon taken from the manifest; nothing checks that the
polygon contains every marsh mark drawn on it. So for marsh, FR-002's coverage requirement is not
belt-and-braces - it is the whole of the safety, and FR-006's browser assertion is what proves it. Said
plainly here because the GM said yes to a sentence that was half right, and the correction changes which
requirement is load-bearing rather than whether the fix is sound.

## Requirements

- **FR-001** The ink of the **scrub-and-rough-grazing** and **marsh** classes MUST NOT be hit-tested on a
  page where that class has a hit region; the region resolves the hover instead. THESE TWO ONLY - see
  "Why not every class with a region" below.
- **FR-002** A class MUST NOT have its ink disabled unless its region is present AND covers that class's
  own marks on that page. Presence is not coverage: a mark outside its region would go dead, which is the
  one failure this change can cause. Where coverage does not hold, the ink stays hit-testable.
- **FR-006** The browser test MUST assert hover FROM A POINT ON THE DISABLED INK ITSELF for each affected
  class, so the verification the GM was promised happens before this ships - not merely that the existing
  hover assertions still pass, which they would even if a mark went dead.
- **FR-003** Hover behavior MUST be unchanged for the reader: the same classes highlight from the same
  places, and features drawn above the scatter keep the pointer as they do now.
- **FR-004** The SVG and PNG MUST remain byte-identical - the class and its hit behavior ride in the
  page's own serialization, never in the drawn record (feature 134 FR-010).
- **FR-005** The change MUST be measured on both pages, before and after: the geometry the browser would
  hit-test, AND page load to first interaction. The GM reported BOTH "slower to load" and "more sluggish";
  this feature targets the second, and the first is measured rather than assumed away so the GM gets a
  plain answer about it.

### Why not every class with a region

The first draft made FR-001 general - any class with a hit region. `spec-fidelity` refused it, and was
right on the mechanism as well as the scope. `HIT_REGIONS` covers seven classes, and the safety argument
the GM approved does not reach five of them:

- **Coverage.** Only scrub goes through `marks_region(..., within=polys)`, which builds the region FROM
  the marks. The other five take the recorded footprint polygon out of the manifest, so "region coverage
  built from their own marks" - the sentence the GM said yes to - is simply not true of them.
- **Stack order, which is worse.** Regions sit at the BOTTOM, and `hit_regions`' own docstring says
  everything drawn later keeps the pointer. Windbreak (stage 11), bamboo (stage 12) and the copse are
  drawn LATE, above yards, gardens, houses and paddies. They keep the pointer today BECAUSE they are on
  top; disable their ink and wherever a crown overlaps a yard, the yard - drawn below the crown but above
  the region - takes the pointer and the class goes dead there. That is the hover regression FR-003
  forbids.
- **Worth.** The table above says the two named classes are ~95% of the hit-test geometry. The other five
  together buy under 5%, for five untested classes.

A general rule is a separate ask to the GM, and would need per-class region coverage and a draw-order
answer first.

## Success Criteria

- **SC-001** The hit-testable path geometry on the reference hamlet's page falls by at least 90%.
- **SC-002** The browser test's hover assertions pass unchanged.
- **SC-003** `make done` is green and the pool maps gate clean.

## Assumptions

- The approved fix targets pointer responsiveness. The GM also reported the page being "much slower to
  load", and that is NOT resolved here: byte size settles download and the two pages are within 0.7 MB,
  but it says nothing about parse, layout or first paint, and kuwabata carries 3,455 `<path>` elements to
  inashiro's 1,576 at that similar size. FR-005 measures load before and after; if the fix does not move
  it, the load half is an OPEN QUESTION FOR THE GM, not something this feature has answered.
- Kuwabata itself belongs to another session's clone (feature 147, `diagram-kuwabata`); this feature
  changes the shared page writer, so that map benefits without this session touching it.

## Review history

- **Round 1, `spec-fidelity`, 2026-08-29: CHANGES REQUIRED.** Three findings, all accepted and all fixed
  above. (1) FR-001 widened the GM's "scrub and marsh" to every region-bearing class - a real widening
  with a real hazard, since five of the seven take a manifest polygon rather than a marks-built region and
  three of them are drawn late enough that disabling their ink would hand the pointer to whatever sits
  under them. (2) FR-002 demoted the session's own caveat from COVERAGE to mere presence, and nothing
  required the browser verification the GM was promised - now FR-002 requires coverage and FR-006 requires
  the assertion. (3) The Assumptions section explained the GM's "much slower to load" away on evidence
  that did not reach it - the claim is deleted, FR-005 now measures load, and the load half is named as an
  open question rather than answered by assertion.
