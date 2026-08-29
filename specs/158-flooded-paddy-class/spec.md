# Feature Specification: The blue paddy plot is its own kind

**Feature Branch**: none - this project stays on `main` (CLAUDE.md, GM 2026-07-27). `SPECIFY_FEATURE=158-flooded-paddy-class`

**Created**: 2026-08-29

**Status**: Draft

**Input**: The GM's request, verbatim, in [`request.md`](request.md):

> Some of the plots on the rice paddy field are totally filled in blue, and the rest are green. My
> understanding is that this is deliberate and that that is a specific type of plot. However, if
> that is the case, then I should be able to highlight it and click on it separate from the rest of
> the fields, because that is its own type of thing, and it deserves its own explanation. Please
> make that change for the reference Hamlet HTML.

## Context: what the blue actually is

Measured on the reference hamlet before this spec was written. `waterfields/carve.py`
`_sector_canal_closers` tints a plot `FLOODED` (`#93B7AC`) instead of a rice green (`#A6C398`)
when, and only when, the plot belongs to the CLOSING RANK and its bottom edge lies on the drain
collector - the lowest, wettest ground the field has. The engine's own comment: *"only the level
whose BOTTOM edge lies on the collector floods (the wettest, lowest ground); an upper split level
cascades into it and stays green - so a blue plot always abuts the drain."*

Two properties of that tint matter to the reader and are the reason this feature is not just a
second row in a table:

1. **It is a SAMPLE, not a set.** Eligible plots take the tint at `R.random() < 0.45`. The engine
   says so where it does it: *"`low` is the TOPOGRAPHY; `fill` is only the PICTURE. FLOODED tints a
   random 45% of the bottom level blue for texture, so it is not the low ground - it is a sample of
   it."* Inashiro carries 24 low plots and 2 blue ones. So a reader who is told "blue = the wet
   ground" is being told something false about the 22 low plots that are green.
2. **It is one crop at one growth stage.** The whole field is one transplant (`carve.py`: *"One
   village = one transplant = one growth stage, so the field reads as ONE green"*). The blue plot
   is not a different crop, a different season or a fallow - it is the same rice under more water.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reader asks what the blue plot is (Priority: P1)

A player opens the reference hamlet's HTML map, notices that two plots in an otherwise green field
are filled blue, and wants to know what makes them different. They put the pointer on one.

**Why this priority**: it is the GM's request in full. Everything else in this spec exists to make
this answer honest.

**Independent Test**: open `pool/hamlets/inashiro.html`, hover a blue plot, click it, read the modal.

**Acceptance Scenarios**:

1. **Given** the reference hamlet's page, **When** the reader hovers a blue plot, **Then** the blue
   plots highlight and the green paddy plots do not.
2. **Given** the reference hamlet's page, **When** the reader hovers a green paddy plot, **Then**
   the green plots highlight and the blue ones do not.
3. **Given** the reference hamlet's page, **When** the reader clicks a blue plot, **Then** a modal
   opens whose heading and text are about the blue plot specifically, not about paddies in general.
4. **Given** that modal, **When** the reader reads it, **Then** it says what the plot is, why it
   stands where it does, and discloses that only a sample of the wet plots carries the tint.
5. **Given** that modal, **When** both kinds are on the map, **Then** it links to the ordinary paddy
   as a "not to be confused with" sibling, and the paddy's modal links back to it.

---

### User Story 2 - The reader is not misled about the wet ground (Priority: P2)

A reader who has just learned that blue means "lowest, wettest, on the drain" looks at the rest of
the field and concludes that every other plot is dry-footed. That conclusion is wrong, and the map
would have taught it to them.

**Why this priority**: constitution XII's one failure is telling a reader a guess is a finding. A
tint that samples 45% of an eligible set, presented as the set, is that failure in a new place.

**Independent Test**: read the modal; the disclosure is present in the text, not only in a source.

**Acceptance Scenarios**:

1. **Given** the blue plot's modal, **When** the reader reads it, **Then** it states that the tint
   marks a sample of the wet ground rather than all of it.

---

### User Story 3 - Every other map keeps its meaning (Priority: P3)

The class vocabulary is per KIND and shared by every Mode B map. A blue plot on any other map that
draws one must carry the same class and the same explanation as the reference hamlet's.

**Why this priority**: an identical picture that highlights differently on two maps is worse than
either behavior alone.

**Independent Test**: the gate's `all_ink_is_ruled_on` passes on every map in the pool, and any
other map with FLOODED-filled plots reports them under the new class in its ink census.

**Acceptance Scenarios**:

1. **Given** any pool map whose field carries FLOODED-filled plots, **When** its page is written,
   **Then** those plots carry the new class and the remaining paddy plots carry `paddy`.

---

### Edge Cases

- **A map with no blue plot at all.** Most of the pool. The class must simply be absent from that
  page - no empty modal, no sibling paragraph on the paddy's modal claiming a distinction from a
  class that is not there. This is existing page behavior (`explanations()` emits present classes
  and present sibling pairs only) and the feature must not break it.
- **A map whose field is ENTIRELY blue.** Not currently produced by any generator, but the page
  must then show the new class and no `paddy`, with the sibling paragraph likewise absent.
- **The bund is unaffected.** A plot is drawn as one polygon with two classes (`Split`): the fill is
  the plot, the stroke is the bund. Only the FILL half changes; a blue plot's bund keeps `bund` and
  goes on highlighting with every other bund in the field.
- **The topography record is unaffected.** `wet_plots` (which plots are LOW) and `flooded_plots`
  (which are BLUE) are separate records that the land-use overlays and the gate read. This feature
  reads the paint, exactly as `flooded_plots` does, and writes neither.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The interactive class vocabulary MUST carry a new feature class for the blue paddy
  plot, distinct from `paddy`, with its own name, `what`, `why`, label, `label_note`, sources and
  research entry - the same completeness every other class is held to.
- **FR-002**: A paddy plot drawn with the FLOODED fill MUST carry the new class; a paddy plot drawn
  with a rice green MUST keep `paddy`. The engine MUST decide this from the fill it is about to
  draw, at the emit site, so the class and the color cannot disagree.
- **FR-003**: The bund stroke of every paddy plot MUST keep the `bund` class, blue plot or green.
- **FR-004**: The new class and `paddy` MUST be siblings of each other, with symmetric sibling text
  written once for the pair, so each modal links to the other when both are on the map.
- **FR-005**: The new class's explanation MUST disclose that only a sample of the eligible wet plots
  carries the tint, in the modal's own text.
- **FR-006**: The new class's explanation MUST rest on the research record and cite it, per
  constitution XII: what the record says a permanently-wetter bottomland paddy was, with its
  `research/` entry and `**Sources:**` keys. Where the record is silent, the text MUST say so in
  the words the project reserves for it rather than asserting a finding.
- **FR-007**: The label (`accurate` / `deviation` / `guess`) MUST follow what the research pass
  actually supports, and MUST NOT be chosen to avoid printing a liberty.
- **FR-008**: The reference hamlet's page MUST be regenerated so the GM can open it and see the
  change, and the change MUST be visible there without any other map being regenerated.
- **FR-009**: The gate check `all_ink_is_ruled_on` MUST pass with the new class on every map.
- **FR-010**: The registry's existing invariants MUST continue to hold for the new row: siblings
  closed and symmetric, `caveat` a verbatim substring of `label_note`, every glossary term used in
  the text defined, and every source key registered in `research/SOURCES.md` with a URL.

### Key Entities

- **The blue plot's feature class**: one row of the interactive vocabulary - the key the engine
  tags ink with, the display name, what it is, why it is there, its constitution-XII label and the
  liberty that label discloses, its sources and its research entry.
- **The tint decision**: the engine's existing choice, per plot, between the FLOODED fill and a rice
  green. This feature reads it; it does not change which plots are tinted, how many, or where.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the reference hamlet's page, hovering a blue plot highlights exactly the blue plots
  (2 on Inashiro) and no green one; hovering a green plot highlights no blue one.
- **SC-002**: Clicking a blue plot opens a modal whose text differs from the paddy's and answers
  "what makes this one different" without the reader consulting anything else.
- **SC-003**: A reader of that modal can state correctly whether every wet plot on the map is blue.
  (It is not; 2 of 24 low plots carry the tint.)
- **SC-004**: The drawn map is unchanged: the `.svg` and `.png` of every pool map are byte-identical
  before and after, and no manifest changes.
- **SC-005**: No regression - the whole gate is green, and no check, seed or pool artifact that
  passed before this change fails after it.

## Decisions Recorded *(mandatory)*

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| A paddy plot drawn with open water showing is a SEPARATE highlightable kind from a paddy under closed crop | rendering decision, not a physical one - it changes what the page groups, not what the map draws | The GM: "that is its own type of thing, and it deserves its own explanation". The picture already distinguished them; only the page did not. | this spec; `classes.py` new row; comment at the emit site in `settlement/fields/comb.py` |
| What the blue plot depicts - the lowest, wettest bottomland plot lying on the drain | to be set by the research pass (FR-006/FR-007); the label follows the record, and the pass is dispatched before the text is written | constitution XII: a claim about how ground was farmed is a research question, and a guess is the last resort | `research/fields.md` entry + `research/SOURCES.md` keys, cited from the class's `entry` and `sources` |
| Only ~45% of eligible closing-rank plots carry the tint - blue is a SAMPLE of the wet ground, not the whole of it | deviation - a drawing convention for texture, disclosed | The engine has always done this (`carve.py`); until now nothing told the reader, and a reader who takes the tint for the set is misled about 22 of Inashiro's 24 low plots | the class's `label_note` / `caveat` (so it reaches the modal), and the existing comment at `waterfields/carve.py` |

## Assumptions

- The tint rule itself is OUT OF SCOPE. Which plots are blue, how many, and the 45% share are the
  engine's existing behavior and this feature does not change them - it names what is already drawn.
  If the research pass shows the 45% is wrong, that is a finding to report to the GM, not a change
  to make under this spec.
- `wet_plots` and `flooded_plots` stay as they are; the land-use overlays keep keying off `low`.
- The other tiers' maps get the class by sharing the vocabulary; no per-map text is added, since the
  vocabulary is per KIND (a map-specific sentence would go in that map's `.notes.md`, feature 156).
- The GM said "for the reference Hamlet HTML"; that is where it must be visible and verified. The
  class is global because the vocabulary is, which is the only way a blue plot on another map does
  not silently keep the old behavior.
