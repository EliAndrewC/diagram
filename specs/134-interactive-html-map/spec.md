# Feature Specification: The Interactive HTML Map

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=134-interactive-html-map`)

**Created**: 2026-08-27

**Status**: APPROVED by `spec-fidelity` - round 3 verdict **FAITHFUL** (2026-08-27), after rounds 1 and 2 each returned changes. Implementation may begin.

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Every Mode B generator run that writes an SVG and a PNG also writes an **HTML page of the same
map**, in which mousing over any drawn feature highlights **every feature of that kind** on the
map, and clicking a highlighted feature opens a modal that explains what it is - starting with the
reference hamlet, Inashiro, as a **generalized mechanism** that any scripted hamlet gets for free.

## Why this exists (the GM's words)

- *"I would like to add the ability to have HTML be one of the things that we are generating in
  addition to an SVG that becomes a PNG file. I believe our project already talks about this as a
  future goal"* - it does: constitution XII (v2.5.0, GM 2026-08-26) records every rendering
  decision as accurate / deviation / guess *for the reader who will click on it*, and
  [`research/README.md`](../../.claude/skills/diagram/research/README.md) says the interactive
  HTML map *"will show a reader exactly this"*. This feature is that map.
- *"We can start with the reference hamlet specifically, though I expect that what we are doing
  is a generalized process that will kind of work for other hamlets as well."*
- *"the main thing that we need is to have the script, which is already storing coordinates and
  glyphs and such, to be able to result in an HTML page that has user interaction."*

## How the request was read

The request was dictated, and four phrases are transcription slips or hedges. Each is read as
follows, and the fidelity review is asked to confirm the reading:

| the GM's words | read as | why |
|---|---|---|
| *"If I highlight a flushing field, I want all flushing fields on the map to become highlighted"* | the **flooded** (paddy) plots - the wet field | the map's fields are paddies (`wet_plots` in the manifest); "flooded field" is the only field kind the phrase can name. If the GM meant the fallow patches, those are a class of their own below (FR-007) and nothing is lost |
| *"the earthen buns"* / *"the earthen bunds"* | the paddy bunds | said correctly in the same sentence |
| *"the different Categories of bamboo grudge"* | bamboo **grove** | the sentence before names *"the shared bamboo grove"* |
| *"a generalized process that will kind of work for other hamlets as well"* | the mechanism is built once, in the shared engine, so any scripted hamlet's run writes the page - **proven on the reference hamlet**, the GM's stated starting point (*"We can start with the reference hamlet specifically"*) | "kind of work" is a weaker bar than a passing suite; a second hamlet's page is expected to work, and is checked when scope unlocks (SC-008), but the feature is not held to it |

**All ways are one feature.** The GM: *"all of the village lanes ... if they were not connected, I
would still expect them to all be highlighted and to be treated as a single feature."* That is the
only instruction about ways, and it covers every lane on the map - the connector to the off-map
road and the field spur included. The engine's own distinction between them (provenance - `dev/
placement.md`) is about generation order, and the GM has already closed it as a basis for
exceptions (`dev/RESUME-HERE.md`: *"ANY lane. There is no exogenous class, no connector
exception"*). The lane explanation MAY mention that the connector predates the settlement; it is
not a separate class. (A first draft of this spec made it one; the fidelity review struck it.)

**The judgment calls are listed so the GM can overrule any by name.** The GM: *"we have a lot of
different judgment calls to make about what things get highlighted and which things do not"* -
so FR-007 lists every class, and FR-002 provides for the second half of that sentence: a thing
the GM rules does NOT highlight is declared as such, not left unclassed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hover lights up the kind (Priority: P1)

A player opens `inashiro.html` from the pool directory (a plain `file://` open, no server, no
network) and moves the mouse over one farmhouse. That farmhouse and every other farmhouse on the
map highlight together. Moving to a paddy plot highlights every paddy plot; to the marsh, every
marsh patch; to the scrub, every scrub patch. Moving off the map clears the highlight.

**Independent Test**: a headless browser opens the page, dispatches a pointer move onto a
farmhouse, and asserts that every element classed `farmhouse` - and nothing else - carries the
highlighted state; then the same for two disconnected pieces of one class (FR-004).

**Acceptance Scenarios**:

1. **Given** the page is open, **When** the pointer enters any ink belonging to a class, **Then**
   every element of that class on the map is highlighted and no element of any other class is.
2. **Given** a class whose pieces are not connected (two marsh patches, two scrub patches,
   two lanes that do not meet), **When** the pointer enters one piece, **Then** every piece
   highlights - the class is one feature regardless of connectivity.
3. **Given** the pointer leaves the map or enters unclassed ground, **Then** no element is
   highlighted.

---

### User Story 2 - Different kinds light up separately (Priority: P1)

The player hovers a farmhouse: the farmhouses light, and the storage sheds (attached or detached) do
not. Hovering a storage shed lights the storage sheds and not the detached animal sheds
(byres); hovering a byre lights the byres alone. Hovering the shelter belt lights the whole
windbreak and none of the other tree patches; hovering a copse lights the copses and not the
windbreak. Hovering a household bamboo patch lights those and not the shared grove.

**Independent Test**: for every pair of classes the GM named as distinct (farmhouse / storage shed / byre; windbreak / other trees; homestead bamboo / shared grove; bund / bund beans; each dry
crop against the others), a headless-browser test hovers one and asserts the other is dark.

**Acceptance Scenarios**:

1. **Given** the pointer is on a farmhouse, **Then** no shed of either kind is highlighted.
2. **Given** the pointer is on a storage shed, **Then** no byre is highlighted, and the
   reverse.
3. **Given** the pointer is on the windbreak, **Then** no copse, woodland or homestead tree is
   highlighted, and the reverse.
4. **Given** the pointer is on a homestead bamboo patch, **Then** the shared bamboo grove is not
   highlighted, and the reverse.

---

### User Story 3 - A thing inside another thing (Priority: P1)

The bund beans (the dark green soybean plants drawn along the paddy bunds - `azemame`, the
beaded-bund accent in `waterfields/palette.py`) sit on the bunds. Hovering the beans lights every
bean run on the map and NOT the bunds; hovering a bund between the beans lights every bund and not
the beans. The dry plots are one fabric but three crops: hovering a millet plot lights the millet
plots only, and buckwheat and barley each light alone.

**Independent Test**: the headless-browser test hovers a bean run and asserts no bund is
highlighted; hovers a bund and asserts no bean is; hovers one dry plot per crop and asserts the
other two crops are dark.

**Acceptance Scenarios**:

1. **Given** the pointer is on a bund-bean run, **Then** the beans highlight and the bunds do not.
2. **Given** the pointer is on a bund, **Then** the bunds highlight and the beans do not.
3. **Given** the pointer is on a millet plot, **Then** only millet plots highlight.

---

### User Story 4 - Click opens the explanation (Priority: P1)

With a class highlighted, the player clicks. A modal opens naming the feature, saying what it is,
why it is where it is, whether that is **historically accurate**, a **deliberate deviation** or a
**guess** (constitution XII's three labels), and the sources behind the claim. Clicking the
windbreak on a map that also has copses and woodland commons, the text says that the shelter belt
had a different purpose, was regulated differently and was used differently by the villagers than
the other trees on the map. Clicking millet, the text says how millet differs from the buckwheat
and barley beside it. Clicking the bund beans, the text says why beans grow on bunds and that the
bund itself is a separate feature. Clicking the household bamboo, the text distinguishes it from a
shared grove. The modal closes on its close control, on Escape, and on a click outside it.

**Independent Test**: the headless-browser test clicks one element per class on the map and
asserts a modal opens whose text contains the class name, one of the three labels, and - for every
class that has a sibling class present on THIS map - the sibling's name.

**Acceptance Scenarios**:

1. **Given** a class is highlighted, **When** the player clicks it, **Then** a modal opens for that
   class and the page behind it stays put.
2. **Given** the modal is open, **When** the player presses Escape, clicks the close control or
   clicks outside the modal, **Then** it closes and the highlight state resumes.
3. **Given** the class has a sibling class on this map (windbreak with copse or woodland; each dry
   crop with the others; beans with bunds; homestead bamboo with a shared grove; storage shed
   with byre), **Then** the explanation names the sibling and says how the two differ.
4. **Given** the sibling class is NOT on this map (a hamlet with no woodland commons), **Then**
   the explanation does not claim it is.

---

### User Story 5 - The label and the thing it labels are one (Priority: P2)

The notice board carries a label. Hovering the board highlights the board and its label; hovering
the label highlights the label and the board. Clicking either opens the notice board's modal.

**Independent Test**: the headless-browser test hovers the kosatsuba glyph and asserts its label
text is highlighted; hovers the label and asserts the glyph is; clicks the label and asserts the
notice-board modal opens.

**Acceptance Scenarios**:

1. **Given** the pointer is on a labeled feature, **Then** its label is highlighted with it.
2. **Given** the pointer is on a label, **Then** the labeled feature is highlighted with it.
3. **Given** either is clicked, **Then** the modal for the labeled feature opens.

---

### User Story 6 - Every hamlet gets it (Priority: P2)

The GM regenerates any scripted hamlet (Inashiro today; the other hamletgen maps) and finds an
`.html` beside its `.svg`, `.png` and `.json`, with the same interaction. The pool index links to
it. Render-sync writes it into main beside the renders, so it is browsed where the renders are.

**Independent Test**: the reference hamlet's run writes its `.html` through the shared engine
path with nothing hamlet-specific in the way (SC-008); on unlock, regenerate a second scripted
hamlet and assert its `.html` exists, opens in the headless browser, and passes the same
hover/click checks for the classes it contains.

**Acceptance Scenarios**:

1. **Given** any scripted hamlet is regenerated, **Then** `<name>.html` is written beside its
   other outputs.
2. **Given** the pool index is rebuilt, **Then** each map that has an `.html` links to it.

---

### Edge Cases

- **Ink on the not-highlighted list** (the background, the title placard, the scale bar):
  never highlights and never opens a modal. Ink that is in no class AND not on that list is ink
  nobody has ruled on - a DEFECT, caught by a gate check (FR-009) rather than left as dead ground.
- **Ink that belongs to two classes at once** (the beans on the bund): the topmost element under
  the pointer decides. The beans are drawn over the bund, so hovering a bean is the beans and
  hovering the bund beside it is the bund. An element is never in two classes.
- **Two classes, one label**: a label belongs to exactly one labeled feature.
- **A class with one member** (the one hokora, the one notice board): highlighting "all of its
  kind" highlights the one.
- **A class whose explanation names a sibling that is absent from this map**: the explanation is
  assembled per map, so absent siblings are not mentioned (US4 scenario 4).
- **The 16 MB SVG** (Inashiro's SVG is 16,379,741 bytes and ~175,000 elements, of which ~160,000
  are the bund-bean and furrow lines): the page must still open and respond to hover within the
  bounds SC-004 sets. Where the plan finds that a browser cannot do this with one element per
  primitive, the plan reduces the element count in the HTML target only (grouping same-class
  primitives) - the SVG and PNG are not touched (FR-010).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (the HTML target)**: a Mode B generator run that writes `<base>.svg` and `<base>.png`
  MUST also write `<base>.html`, a single self-contained file that opens from `file://` with no
  server, no network access and no external asset. The page shows the same map, at the same
  viewport, as the PNG.
- **FR-002 (every feature is ruled on)**: every drawn feature on the map MUST either belong to
  exactly one **feature class** - the unit of highlighting - or be on an explicitly declared
  **not-highlighted** list (the GM: *"judgment calls to make about what things get highlighted and
  which things do not"*). A class is a kind of thing, not an instance: "farmhouse", not "the third
  farmhouse". Its members highlight together regardless of whether they touch (the GM: *"if they
  were not connected, I would still expect them to all be highlighted and to be treated as a
  single feature"*). The not-highlighted list starts with the frame (background, title placard,
  scale bar) and grows only by a recorded ruling.
- **FR-003 (hover)**: when the pointer enters any ink of a class, every element of that class on
  the map MUST take a visibly distinct highlighted state and every other class MUST stay as drawn;
  when the pointer leaves, the state clears. The highlight MUST be legible against every fill on
  the map (the pale rice, the dark pine of the beans, the blue water, the parchment ground).
- **FR-004 (separate kinds)**: classes MUST be distinguished at the grain the GM named:
  farmhouse vs. storage shed vs. byre; windbreak vs. copse vs. woodland commons vs. persimmon; homestead bamboo vs. a shared bamboo grove; the bund vs. the beans on it;
  each dry crop from the others; marsh from scrub. The full vocabulary is FR-007.
- **FR-005 (the explanation)**: clicking a highlighted class MUST open a modal that gives, for
  that class: its name; what it is; why it stands where it does on the map; its constitution XII
  label - **accurate**, **deviation** or **guess** - stated in those words; and its sources (the
  `research/SOURCES.md` keys the finding cites, or "not recorded"). Where a **sibling class** is
  present on the same map, the text MUST say how the two are distinguished - purpose, regulation
  and use for the tree classes (the GM's example); crop, season and soil for the dry crops; the
  plant vs. the earthwork for beans and bunds; household vs. shared for bamboo; storage vs. animals
  for sheds. The modal closes on Escape, on its close control, and on a click outside it.
- **FR-006 (labels)**: a label and the feature it names MUST highlight together from either end,
  and a click on either MUST open the labeled feature's modal.
- **FR-007 (the class vocabulary of the reference hamlet)**: the judgment calls, made once here so
  the GM can overrule any by name. Each row is one class; the "siblings" column is what its
  explanation must distinguish it from when both are on the map.

  The siblings column is **symmetric** (if A names B, B names A) and names only classes in this
  table - FR-005 keys the distinguishing text off it in both directions.

  | class | what it covers on the map | siblings |
  |---|---|---|
  | farmhouse | the dwelling of each household | storage shed; byre |
  | storage shed | the lean-to shed drawn against a farmhouse (`houses[].shed`) and the detached farm sheds of the same household (`farm_sheds`) - storage either way; the GM's distinction is storage vs. animals | farmhouse; byre |
  | byre | the draft-animal sheds (`byres`) | farmhouse; storage shed; hen coop |
  | threshing yard | the work yard of each household | garden |
  | garden | the kitchen garden of each household | threshing yard; millet; buckwheat; barley |
  | privy | the household privy | manure heap |
  | woodpile | the fuel stack | - |
  | manure heap | the muck heap | privy |
  | bathhouse | the household bath | - |
  | hen coop | the coop | byre |
  | household shrine | the hokora | - |
  | persimmon | the dooryard persimmon tree | copse |
  | homestead bamboo | the bamboo patch by a farmhouse (`bamboo_stands[role=homestead]`) | shared bamboo grove |
  | shared bamboo grove | a bamboo stand held in common (`bamboo_stands` with any other role, when present) | homestead bamboo |
  | windbreak | the shelter belt (`village_groves[role=windbreak]`) | copse; woodland commons |
  | copse | a village tree stand that is not the belt (`village_groves[role=copse]`) | windbreak; woodland commons; persimmon |
  | woodland commons | the woodland of the commons (`commons[role=woodland]`) | windbreak; copse |
  | scrub and rough grazing | the grazing commons (`commons[role=grazing]`) | marsh |
  | marsh | every marsh patch, whatever its role (`marshes`) - the GM: *"all of the marshland"* | scrub and rough grazing; pond |
  | paddy | every wet plot | millet; buckwheat; barley; fallow |
  | bund | the earthen bunds between and around the paddies | bund beans |
  | bund beans | the soybeans on the bunds | bund |
  | millet | dry plots under millet | buckwheat; barley; paddy; fallow; garden |
  | buckwheat | dry plots under buckwheat | millet; barley; paddy; fallow; garden |
  | barley | dry plots under barley | millet; buckwheat; paddy; fallow; garden |
  | fallow | the fallow patches (when present) | paddy; millet; buckwheat; barley |
  | stream | the brook | field ditch; pond |
  | field ditch | the intake, head race, branches and drain (`field_ditches`, `channels`) | stream; pond |
  | pond | the tameike | stream; field ditch; marsh |
  | village lane | EVERY lane on the map - the web, the internal skeleton, the connector to the off-map road and the field spur - one class whether or not they meet; the text may say the connector predates the settlement | - |
  | footbridge | every plank and deck over water | - |
  | well | the wellheads | - |
  | notice board | the kosatsuba, with its label | - |

  **Not highlighted** (FR-002's declared list): the background, the title placard, the scale bar.

  A class in this table that a given map does not contain is simply absent from that page.
- **FR-008 (the explanations are the record)**: the explanation text for a class MUST be drawn
  from the project's research record - the finding in `research/`, the rule in `settlements/` -
  and MUST carry the label that record carries. A class whose record is silent is labeled
  **guess** and says so; it is never presented as a finding (constitution XII: *"an unlabelled
  guess is the one failure"*). The explanations are written once, per class, in one place that any
  hamlet's page reads; a map-specific explanation is not a goal.
- **FR-009 (no unruled ink)**: a gate check MUST fail when a generated map contains drawn ink
  that is neither in a class nor on the declared not-highlighted list (FR-002) - ink nobody has
  ruled on. A deliberate "this does not highlight" ruling never turns the gate red. The check runs
  on the reference hamlet and, on unlock, on every scripted hamlet in the pool.
- **FR-010 (the SVG and PNG are unchanged)**: adding the HTML target MUST NOT change what the SVG
  and PNG show. Inashiro's PNG after this feature is byte-identical to the PNG before it, and so is
  every other pool map's.
- **FR-011 (the pipeline carries it)**: the regen driver, the render cache and render-sync MUST
  treat `<base>.html` as a derived render like the PNG - written with it, refreshed with it,
  gitignored with it, present in main where the renders are browsed. The pool index links to it.
- **FR-012 (verified in a browser)**: the hover, highlight, click and modal behaviors MUST be
  proven by an automated headless-browser test in the suite (constitution VI - a page that was
  never opened has not been verified), running on the reference hamlet's page.

### Key Entities

- **Feature class**: the unit of highlighting and explanation - a name, the manifest features it
  covers, its siblings, its explanation, its constitution XII label, its sources.
- **Not-highlighted list**: the declared ink that is ruled out of highlighting (FR-002).
- **The HTML page**: the map's SVG, with every primitive tagged by class, plus the styling and
  script that implement hover, highlight, click and the modal, plus the class explanations for
  the classes present on that map.
- **Label link**: the pairing of a label with the feature it names.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `inashiro.html` exists after `make reference`, opens in a headless browser from
  `file://` with zero console errors and zero network requests.
- **SC-002**: for every class present on Inashiro, hovering one member highlights every member and
  no non-member; the headless-browser test asserts this for all of them.
- **SC-003**: for every sibling pair in FR-007 that is present on Inashiro, the clicked
  explanation names the sibling.
- **SC-004**: on Inashiro's page, the highlighted state appears within 100 ms of the pointer
  entering a class, measured in the headless browser; the page finishes loading in under 5 s.
- **SC-005**: Inashiro's PNG and every other pool map's PNG are byte-identical before and after
  the feature (FR-010), checked by hash.
- **SC-006**: the unruled-ink check (FR-009) reports zero unruled elements on Inashiro, and a
  regression fixture with one deliberately unruled element makes it fail; an element on the
  not-highlighted list does not.
- **SC-007**: every class explanation carries exactly one of the three labels and a sources line.
- **SC-008**: the `.html` is written by the shared mechanism for any scripted hamlet run, proven
  on the reference hamlet; when scope unlocks, a second scripted hamlet's page passes the same
  browser test for the classes it contains (US6) - owed then, not a condition of this feature.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing new and changes no glyph, size or placement (FR-010). What it adds is
**statements** - one explanation per class - and each is a decision the reader will read. Every
row of FR-007 is therefore a recorded decision: its class label and its sources are the record.
The table is filled at implementation, one row per class, and the fidelity review checks it
against the explanations shipped.

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| the class vocabulary itself (FR-007) - which kinds are distinguished | judgment, not history - the GM's, delegated to this spec | the GM: *"we have a lot of different judgment calls to make about what things get highlighted"* | this spec; the class registry the plan names |
| one row per class explanation | (filled at implementation, from the research entry each cites) | | the class registry; the `research/` entry it cites |

## Review history

- **Round 1** (2026-08-27, `spec-fidelity` against `gm-request.md`): CHANGES REQUIRED - (1) the
  connector track was carved out of "village lane" against the GM's one sentence on ways and the
  GM's recorded closing of that argument; (2) "attached storage shed" misnamed its detached
  members; (3) the siblings column named classes not in the table and was one-way; (4) FR-002 /
  FR-009 made unclassed ink a defect where the GM said some things do not highlight; (5) SC-008
  held the feature to a second hamlet where the GM said "start with the reference hamlet" and
  "kind of work". All five applied.
- **Round 2** (2026-08-27): CHANGES REQUIRED - one item: "attached storage shed" survived in
  FR-004 and four user-story lines, contradicting FR-007's `storage shed`; FR-004 now names
  FR-007's classes verbatim. Applied.
- **Round 3** (2026-08-27): **FAITHFUL**. Aside recorded: FR-004 abbreviates `scrub and rough grazing` to "scrub"; the registry is written from FR-007, never from FR-004.

## Assumptions

- **"Flushing field" is the flooded paddy** (see "How the request was read"). If the GM meant
  another kind of field, it is already its own class and nothing changes.
- **Every lane is one class**, the connector included (see "How the request was read").
- **One explanation per class, not per map**: the GM asked that the explanation *"reference the
  fact that these things are distinguished from one another"*; the distinguishing text is written
  per sibling pair and included only when both are on the map. Nothing in the request asks for
  text specific to one hamlet.
- **Mode B only, scripted hamlets first**: the GM said *"start with the reference hamlet"* and
  *"a generalized process that will kind of work for other hamlets"*. The mechanism is built in
  the shared engine so every Mode B tier inherits the target; the class vocabulary and
  explanations are written for the hamlet tier now, and a class a town draws that the vocabulary
  does not name is what FR-009 reports on that map - the town vocabulary is later work. Mode A
  (hand-authored building plans) is out of scope.
- **Highlight styling is the implementer's**: the GM specified the behavior, not the look. The
  plan picks a highlight that meets FR-003's legibility requirement and records it as a rendering
  decision of the HTML target.
- **A headless browser can be installed in the container** (root `CLAUDE.md`: *"INSTALL WHAT YOU
  NEED"*); Playwright with Chromium is the assumed tool, pinned in the dev requirements.
