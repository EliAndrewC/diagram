# Feature 268 - a village shrine's grounds, researched: no wall, a grove, close-set arches

**Feature Branch**: `268-shrine-grounds-researched` (no branch; `export SPECIFY_FEATURE=268-shrine-grounds-researched`)

**Created**: 2026-09-27

**Status**: specified; awaiting spec-fidelity

**Input**: the GM's message of 2026-09-27 and their two rulings on the research pass, verbatim in
[`request.md`](request.md); the four readers' reports in [`reader-reports/`](reader-reports/).

## Summary

The GM looked at the Hoshigaoka country-shrine sheet (feature 254) and asked four things: why the shrine
is "a walled compound and a very significantly sized walled compound" with "basically nothing there",
and whether a small farming-village shrine had a wall at all; why the frame leaves "a ton of basically
empty space" above, below, left and right ("whatever kind of cropping we are doing is not working very
well"); whether the distances between the torii arches are accurate ("They seem spaced further apart
than I would have expected"); and, generally, a deep research dive on "what these country shrines were
like and what features they had", recorded in the research record in the form the other maps have, so
the sheet rests on "real historical research and rulings that I make about this specific setting".

The research pass ran first (constitution XII). In one line each:

- **No enclosure.** No fence around a whole village-shrine precinct is attested; every dated fence
  rings only the sanctuary (Taisho/Showa donations) or lines the approach; an ordinary neighborhood
  shrine "has only a torii". Walls are temple rank markers. The sheet's fence was the sheet's own
  invention - the village map draws none - and the program's rule ("a fence or hedge, never a wall")
  was an unsourced guess.
- **The precinct's size is right; its contents were wrong.** Meiji village-shrine registers give
  medians of 403 tsubo (Saitama, 14 shrines) and 655 (Tochigi, 50); the sheet's 385 is typical. But
  buildings cover about 1.5-14% of a precinct and the registers praise its old trees: a precinct that
  size is mostly wood. The GM ruled: add a grove to the village map, and the sheet draws it, with a
  small swept clearing at the hall.
- **The arches are too far apart.** No source supports 30 ft; donation rows stand nearly post to
  post, and the one small rural row that can be estimated works out at about 3-4 m. The GM ruled: all
  maps, ~10-13 ft.
- **What else a village precinct holds.** A sacred tree (near-universal); a stone basin (the likely
  village form of the purification stop); guardian dogs, lanterns and strength stones (late-Edo
  villager donations - a wealth matter); a farmers' stage and a sumo ring (attested, not general).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The research is on the record (Priority: P1)

A reader at the shrine sheet opens the research record and finds each question the GM asked answered
with quoted sources: whether a village shrine was enclosed and by what; how big a village precinct was
and how much of it was built on; how far apart the arches of an approach stood; and what a village
precinct held beyond the hall and the sanctuary, feature by feature, with how common each was at village
scale and before 1868.

**Why this priority**: the GM's primary ask - "These are all research questions" - and every change
below rests on it.

**Independent Test**: each question is a heading on the record, answered, every assertion footnoted with
a verbatim quote from a readable page or an absence note, and passed by the record's checks.

**Acceptance Scenarios**:

1. **Given** the record, **When** a reader asks "was a village shrine walled?", **Then** a heading
   answers it with the dated examples and the neighborhood-shrine quote, and says what bounded a
   precinct instead (its arch and its wood).
2. **Given** the record, **When** a reader asks how big a precinct was, **Then** the answer gives the
   register medians and ranges and the built fraction, and the program's precinct size is labeled by it
   rather than as a guess.
3. **Given** the existing torii-spacing entry, **When** it is revised, **Then** it states the research
   finding (near-touching rows; the 3-4 m small-row estimate labeled as arithmetic; no attested
   pre-1868 village row), the GM's ruling of 2026-09-27, and the new pitch - and no longer calls the
   30 ft village avenue a GM preference.
4. **Given** the record, **When** a reader asks what else stands in a village shrine's precinct,
   **Then** each feature is listed with its prevalence and dating and the sheet's treatment of it.

### User Story 2 - The sheet shows a village shrine as it was (Priority: P1)

The GM opens the Hoshigaoka shrine sheet and sees no wall or fence around the precinct; the hall and the
sanctuary stand in a small swept clearing inside a grove; a sacred tree and a stone basin beside the
approach; the seven arches close-set up the approach; and the sheet cropped to what is drawn.

**Why this priority**: the GM's three concrete complaints are about this sheet.

**Independent Test**: render the sheet and read it; the program and map-match checks pass; the crop check
runs on it and passes.

**Acceptance Scenarios**:

1. **Given** the sheet, **When** it is drawn, **Then** there is no fence, wall or hedge around the
   precinct, and nothing in the program requires one.
2. **Given** the village map edited by hand, **When** the sheet is checked against it, **Then** the
   grove, the sacred tree, the basin and the seven arches are on both, in the same places.
3. **Given** the sheet, **When** the crop check runs, **Then** no side of the frame leaves more empty
   parchment than the checklist's border.
4. **Given** the seven arches, **When** they are measured, **Then** consecutive arches and the innermost
   arch's gap to the hall's face are each the new pitch, and no two arch glyphs touch or overlap.

### User Story 3 - Every map's avenues use the researched pitch (Priority: P2)

A newly generated map at any scale lays its torii avenue at the new pitch, with the innermost arch one
pitch off its hall (the GM's 2026-07-27 threshold rule, unchanged), and the arches stay legible as
separate arches at every map scale.

**Why this priority**: the GM chose "All maps"; no live pool map draws torii today (every map with an
avenue is a frozen hand-authored exhibit), so this governs future rolls.

**Independent Test**: unit tests of the avenue placer at each scale: the stride, the threshold, the floor,
and non-overlap of the drawn glyphs at the pitch.

**Acceptance Scenarios**:

1. **Given** a village roll with a seven-arch avenue, **When** it is generated, **Then** its stride is
   the new pitch (not 30 ft) and its innermost arch is one pitch off the hall.
2. **Given** a town or city avenue authored wider than the pitch, **When** it is placed, **Then** it is
   re-laid at the new pitch along its authored line.
3. **Given** the arch glyph at 1, 2 and 3 ft per pixel, **When** arches stand at the new pitch,
   **Then** neighboring glyphs do not overlap.

### User Story 4 - The program carries the research's features as knobs (Priority: P3)

A session drawing the next country shrine finds the program's items and knobs updated: a grove and a
sacred tree as defaults, a stone basin beside the approach, guardian figures, lanterns and strength
stones on the wealth knob (off at average), a farmers' stage and a sumo ring as knobs whose prevalence
the record states, and no precinct fence.

**Independent Test**: the program text and the type declaration agree; the program check passes on the
exemplar and fails on a fixture that draws a precinct fence.

**Acceptance Scenarios**:

1. **Given** the program, **When** a sheet draws a fence around the precinct, **Then** the program
   check reports it.
2. **Given** the exemplar's notes, **When** every knob is listed, **Then** the new knobs appear with
   Hoshigaoka's settings (average wealth: none of the donated stonework; stage and ring absent, as the
   map draws neither).

### Edge Cases

- A sanctuary-only fence (tamagaki) is attested from 1918 on; before 1868 at village scale it is not
  attested, so the average-wealth sheet draws none. Whether a richer shrine may draw one is recorded as
  a wealth-knob item, not a precinct boundary.
- The frozen village map is a permanent exhibit; it is edited by hand here as it was for the seven
  arches on 2026-09-26, on the GM's ruling, and its notes record the edit. It is not regenerated.
- The other frozen maps with avenues (Minami, Nagahara, Tango, Hirameki, Hoshizora, Ubame, Hikari no
  Sato, Kikuta, Ueda) keep their arches: "the fix for a frozen map is conversion, not retrofit", and the
  GM's ruling names Hoshigaoka's seven as the ones to move.
- A designated donation-row site (the GM's ruling of 2026-07-25) stays the exempt outlier it is.
- A map's well stays where the map puts it (108 ft behind the hall); with the fence gone it is simply
  on the shrine's ground, and the crop frames it.

## Requirements *(mandatory)*

### Functional Requirements

**The record**

- **FR-001**: The research record MUST gain, on the religion-and-death page, questions answering: whether
  a village shrine's precinct was enclosed and by what; how large a village shrine's precinct was and how
  much of it was built; and what a village precinct held beyond the hall and sanctuary. Each assertion is
  footnoted with a verbatim quote (in translation, marked, original kept) from a readable page, or an
  absence note saying what was searched.
- **FR-002**: The torii-spacing entry MUST be rewritten with the research finding and the GM's ruling of
  2026-09-27, and every other entry or program text that states the old pitch, the 30 ft village
  avenue or the precinct fence MUST be brought to the new rule.
- **FR-003**: Every new source MUST be registered with what it is and why it applies and its limits, and
  judged by `source-applicability` before its numbers reach the program or a map; the new and changed
  entries MUST pass `source-reader`, `quote-check` and `record-format`.

**The program**

- **FR-004**: The country-shrine program MUST drop the precinct fence as a requirement and MUST state
  that the precinct has no enclosing fence, wall or hedge, bounded by its arch and its wood; a sheet
  that draws one fails the program check.
- **FR-005**: The program's precinct size MUST be restated from the register figures (accurate as a
  band), and the grove and a sacred tree MUST be program items (the tree a default; both site items on a
  sheet declared on a map).
- **FR-006**: The program MUST carry a stone basin beside the approach, and the knobs the research
  directs: guardian figures, lanterns and strength stones on the wealth knob (none at average); a
  farmers' stage and a sumo ring as knobs with their recorded prevalence, absent by default.

**The Hoshigaoka map and sheet**

- **FR-007**: The frozen Hoshigaoka village map MUST be edited by hand - its drawing and its manifest
  together - to add a grove around the shrine, a sacred tree and a stone basin beside the approach, and
  to move the seven arches to the new pitch; its notes record the edit and the GM's ruling.
- **FR-008**: The Hoshigaoka shrine sheet MUST be redrawn: no precinct fence; a small swept clearing at
  the hall and sanctuary inside the grove; the sacred tree and the basin; the seven arches at the new
  pitch with the innermost one pitch off the hall; the map's well kept where the map has it; and the
  notes brought to the drawing. It passes the program check and the map-match check.
- **FR-009**: The crop check MUST run on sheets declared on a map, as on any other sheet, and the
  Hoshigaoka sheet MUST pass it; `buildings.md` and the map-match module's exemption are revised to say
  so (the map-match check still requires every map feature inside the frame).

**The generator**

- **FR-010**: The generator's torii pitch MUST be a single value within 10-13 ft, applied to every avenue
  at every scale (village rolls included); the threshold rule (innermost arch one pitch off the hall)
  holds at the new pitch; designated donation-row sites keep their exemption.
- **FR-011**: The arch glyph and the avenue's drawing floor MUST be revised so arches at the new pitch do
  not overlap at 1, 2 or 3 ft per pixel and each still reads as an arch; the choice of glyph is recorded
  with its class (a map drawing convention where it departs from true size) at the point of change.

**Reviews**

- **FR-012**: The redrawn sheet MUST pass `building-review` and `size-audit`, each ledgered, and the
  edited village map region MUST be looked at by `settlement-review`.

### Key Entities

- **The research questions** on `religion-and-death`: enclosure; precinct size and built fraction; the
  precinct's features; torii spacing (revised).
- **The country-shrine program** (`buildings/programs.md` and its type declaration): items, bands, knobs.
- **The Hoshigaoka village map** (frozen, hand-edited) and **the Hoshigaoka shrine sheet**.
- **The torii pitch** - one value in the generator, used by the stride, the threshold and the floor.

## Success Criteria *(mandatory)*

- **SC-001**: The GM's four questions each have an answer on the record with at least one verbatim-quoted,
  readable source (or an absence note where none exists), all checks confirmed.
- **SC-002**: The shrine sheet draws no enclosure around its precinct; built and swept ground together is
  a small share of the drawn grounds, the rest grove.
- **SC-003**: No side of the sheet's frame leaves more than the crop checklist's border of empty
  parchment.
- **SC-004**: On the sheet and the village map, consecutive arches stand 10-13 ft apart and no two arch
  glyphs overlap; a generated avenue at every scale does the same.
- **SC-005**: `make done` is green, and every review pass is a row in the ledger.

## Assumptions

- "All maps" means the generator's rule for every future roll, plus the hand edit of Hoshigaoka the
  GM's ruling names; the other frozen exhibits keep their arches (conversion, not retrofit).
- The seven arches remain the GM's particular for Hoshigaoka even though no pre-1868 village row is
  attested; the record says so.
- A sanctuary-only fence is not drawn at average wealth; it is recorded, not required.
- The GM's rule that the sheet shows what the map shows (2026-09-20) stands; the grove, tree and basin
  reach the sheet by being put on the map first.
