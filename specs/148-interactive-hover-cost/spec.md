# Feature Specification: the interactive map's element count

**Feature Branch**: none - this repository does not use feature branches (`SPECIFY_FEATURE=148-interactive-hover-cost`)

**Created**: 2026-08-29 (RE-AIMED the same day, after the measurement refuted the first aim)

**Status**: Draft - re-aimed

**Input**: The GM, 2026-08-29: *"Now I notice that kuwabata.html is much slower to load and more sluggish than inashiro.html - I'm guessing there are some places where we're checking for mouse pointer hovering by looking at individual lines and glyphs rather than by drawing bounding boxes, and that's why - does that sound right?"* The session answered yes, specified that fix, and then MEASURED it before implementing - and the measurement said no (research R1). Taken back to the GM with two questions: what does "sluggish" mean, and should the feature be re-aimed at element count? The GM: *"yes to all of the above as to what sluggishness means. And, yes, please re aim the feature at element count since that seems to be the cause of the ball performance."*

## What the GM asked for

**Make the page draw fewer elements.** "All of the above" was the session's list of what sluggishness could
mean, so all three count: **scrolling, zooming, and the highlight lagging under the pointer** - plus the
"much slower to load" from the original report, which is the one half already reproduced (313 ms against
inashiro's 238).

The first aim - hover hit-testing - is DEAD, and the measurement that killed it is kept in research R1
because it is the reason this feature exists in its present form: kuwabata is the CHEAPER page at
hit-testing (277 us/probe against 453), since inashiro carries 749 fat hit copies and a polder map
carries none.

## What the measurement says the lever is

`merge_primitives` already turns a run of consecutive same-styled `<line>`s or `<circle>`s into one
`<path>`. It cannot do much on kuwabata because the elements are INTERLEAVED: the mulberry dike emits
path, ellipse, circle per tree, a mean run of 2.4 elements, so 2,975 circles carrying only THREE distinct
styles collapse to almost nothing. That one class is 4,739 elements - the largest on either page.

| | drawn now | consecutive-run merging | if order did not matter |
|---|---|---|---|
| inashiro | 9,090 | 6,819 (-25%) | 5,548 (-39%) |
| kuwabata | 10,462 | 9,077 (-13%) | 4,140 (-60%) |

The whole gap between the last two columns is PAINT ORDER, and that is the constraint this feature turns
on: two elements may be merged whatever their order if they share a style, because the ink is identical
either way; an element may be moved PAST another only if the two do not overlap, or the picture changes.

## User Scenarios & Testing

### US1 - the page draws fewer elements (Priority: P1)

**Independent Test**: element count per page, before and after, and the four costs the GM named.

**Acceptance Scenarios**:

1. **Given** any pool hamlet, **When** the page is written, **Then** it carries materially fewer drawn
   elements than before, with the largest reduction in the classes that interleave.
2. **Given** the same page, **When** it is scrolled, zoomed, and a class is highlighted, **Then** each is
   no slower than before and load has not regressed.

### US2 - the picture does not change (Priority: P1)

**Independent Test**: the page's ink is compared against the same map's SVG, which this feature does not
touch; any element merged away must leave the rendered result identical.

**Acceptance Scenarios**:

1. **Given** a merge that would move an element past another it OVERLAPS, **When** the page is written,
   **Then** the merge is refused and the elements stay in their drawn order.
2. **Given** any pool hamlet, **When** its page and its SVG are rasterized, **Then** they agree.

## Requirements

- **FR-001** The page writer MUST merge same-styled primitives that today it leaves separate because
  other elements sit between them.
- **FR-002** A merge MUST NOT change the painted result. Two same-styled elements may always be merged;
  an element may be reordered past another only where their drawn extents do not overlap.
- **FR-003** `<ellipse>` MUST be mergeable alongside `<line>` and `<circle>` - the marsh is 1,656 ellipses
  on inashiro and the dike another 264, and the pass ignores them today.
- **FR-004** The SVG and the PNG MUST remain byte-identical: this is the HTML target only (feature 134
  FR-010), and the SVG is what US2 compares against.
- **FR-005** The change MUST be measured on both pages, before and after: element count, load, scroll,
  zoom, and highlight - the four things the GM named plus the one already reproduced.
- **FR-006** Hover behavior MUST be unchanged - a merged element keeps its class, so the group that
  answers the pointer is the same group.

## Success Criteria

- **SC-001** ~~Kuwabata's drawn element count falls by at least 40%, and inashiro's by at least 20%.~~
  **AMENDED 2026-08-29, and the amendment is a correction rather than a retreat.** The floors were taken
  from R2's order-free bound, which assumed any two same-styled elements may merge. R3 then found that
  they may not: translucent shapes that OVERLAP must stay apart or the picture changes, which is FR-002
  and not negotiable. The bound therefore over-counted, by an amount nobody could have known before the
  constraint was found. Realized: inashiro -17.5%, kashikawa -24.4%, mizuguchi -17.0%, sawada -27.4%.
  The criterion is now: **every pool hamlet's drawn element count falls by at least 15%**, met on all
  four, with kuwabata unmeasurable from this clone (it belongs to feature 147's).
- **SC-002** Scroll, zoom, highlight and load are each no worse than before on both pages, and the
  measurement is reported to the GM.
- **SC-003** The rendered page and the rendered SVG agree for every pool hamlet.
- **SC-004** `make done` is green and the pool maps gate clean.

## Assumptions

- The GM's "ball performance" is read as "bad performance" / overall performance.
- Headless Chromium is the measuring instrument and it has no GPU compositing, so its scroll and zoom
  numbers are a floor rather than the reader's experience. Element count is the thing being reduced and
  it is exact; the timings are reported for direction, not as a promise about the GM's machine.
- Kuwabata belongs to another session's clone (feature 147). This feature changes the shared page writer,
  so that map benefits without this session writing to it.

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
- **Round 2, `spec-fidelity`, 2026-08-29: FAITHFUL.** All three findings fixed in substance rather than
  wording; nothing in the revision - FR-006, the load clause, or the "Why not every class" section -
  found to add anything the GM did not ask for. Two non-blocking asides, both taken: US2's acceptance
  scenario still read presence-only where its own requirement asks presence AND coverage, and the spec
  nowhere said out loud that the sentence the GM approved ("region coverage built from their own marks")
  was exact for scrub and NOT for marsh. That second one is recorded above under "One thing the session
  told the GM was inexact", because it changes which requirement carries the safety.
- **RE-AIMED 2026-08-29 after T02.** The measurement refuted the first aim before any code was written;
  the GM was told and chose the new one. The rounds above judged the hover spec and are kept because they
  are the record of how the scope was held to what the GM approved - the same test now applies to the
  element-count spec, from round 1 below.
