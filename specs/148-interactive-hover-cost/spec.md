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

**Independent Test**: the generated page carries `pointer-events: none` on the ink of every class that
has a hit region, and the browser test still highlights that class from a point inside its ground.

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
   a hit region for that class is also present on that page.

## Requirements

- **FR-001** The ink of a feature class MUST NOT be hit-tested when that class has a hit region on the
  same page; the region resolves the hover instead.
- **FR-002** A class MUST NOT have its ink disabled unless a region for it is present - a page that would
  disable a class with no region keeps the ink hit-testable.
- **FR-003** Hover behavior MUST be unchanged for the reader: the same classes highlight from the same
  places, and features drawn above the scatter keep the pointer as they do now.
- **FR-004** The SVG and PNG MUST remain byte-identical - the class and its hit behavior ride in the
  page's own serialization, never in the drawn record (feature 134 FR-010).
- **FR-005** The change MUST be measured on both pages, before and after, by the geometry the browser
  would hit-test.

## Success Criteria

- **SC-001** The hit-testable path geometry on the reference hamlet's page falls by at least 90%.
- **SC-002** The browser test's hover assertions pass unchanged.
- **SC-003** `make done` is green and the pool maps gate clean.

## Assumptions

- The GM's complaint is about pointer responsiveness, not initial load: both pages are ~9 MB and within
  0.7 MB of each other, so download and parse are not the difference. Load time is expected to improve
  only incidentally.
- Kuwabata itself belongs to another session's clone (feature 147, `diagram-kuwabata`); this feature
  changes the shared page writer, so that map benefits without this session touching it.
