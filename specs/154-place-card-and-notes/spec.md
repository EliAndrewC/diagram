# Feature Specification: The place card, and per-map notes the page can read

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=154-place-card-and-notes`)

**Created**: 2026-08-29

**Status**: Draft

**Input**: GM request, 2026-08-29, verbatim in [`request.md`](request.md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The modal stops claiming accuracy (Priority: P1)

A player opens the Inashiro page and clicks a paddy. Today the first line of the modal reads *"This
is historically accurate - Plot form and the irregular patchwork are read; plot sizes are calibrated
from the record."* Almost every feature on the map says that, so the sentence carries no
information: the reader learns nothing from a claim that is made about everything. What the reader
actually wants told is the opposite case - the places where the map departs from the record.

After this story, a click on a paddy leads with what a paddy IS. Nothing on the page says
"historically accurate". A click on the well - drawn larger than a real wellhead so it can be seen
at map scale - still leads with *"This is a deliberate deviation - ..."*, and a click on the
woodpile still leads with *"This is a guess - ..."*, because those are the cases worth a reader's
attention.

**Why this priority**: it is the GM's first-named complaint, it is the smallest change of the three,
and it is independent of everything else here.

**Independent Test**: regenerate the reference hamlet's page and read three modals - a paddy
(accurate), the well (deviation), the woodpile (guess). The accurate one leads with what the thing
is; the other two lead with the liberty.

**Acceptance Scenarios**:

1. **Given** a class the record classifies `accurate`, **When** its modal opens, **Then** no
   sentence claims historical accuracy, and the modal leads with what the feature is.
2. **Given** a class the record classifies `deviation` or `guess`, **When** its modal opens,
   **Then** the first line names the liberty and says what it is, exactly as today.
3. **Given** an `accurate` class whose recorded note nevertheless discloses a drawing convention or
   a derived number, **When** its modal opens, **Then** that disclosure is still shown to the
   reader - it is not deleted along with the accuracy claim.
4. **Given** any class, **When** the manifest and the class registry are inspected, **Then** the
   three-way `accurate`/`deviation`/`guess` classification is still recorded for every class
   (constitution XII), whether or not the page prints it.

---

### User Story 2 - Clicking the title card explains the place (Priority: P1)

A player opens the Inashiro page, and before looking at any one feature wants to know what they are
looking at. They click the parchment title card and get a short "what is this place" overview: that
Inashiro is a hamlet of the commonest kind - an outlying rice-farming community with no headman,
shrine or burial ground of its own; that it is about 15 farmhouses and about 75 inhabitants, written
with tildes so the numbers read as approximate; that the wet fields grow rice and the dry margins
millet, soy, barley and buckwheat; that it belongs to a named village district lying in a named
direction; and what else of consequence lies nearby, such as an Imperial road.

**Why this priority**: the GM asked for it in as much detail as the accuracy change, and it is what
turns the page from a diagram of parts into a description of a place.

**Independent Test**: open the reference hamlet's page, click the title card, and read the overview
against the manifest and the hamlet's notes file.

**Acceptance Scenarios**:

1. **Given** any settlement page, **When** the reader hovers the title card, **Then** the card
   highlights like any other feature, and **When** they click it, **Then** a modal opens describing
   the place rather than a kind of feature.
2. **Given** a hamlet of 15 households, **When** the place card opens, **Then** it states the
   farmhouse count and the population with a tilde (e.g. "about 15 farmhouses, population ~75") and
   never as an exact figure.
3. **Given** a map whose fields grow paddy rice and whose dry plots carry millet, soy, barley and
   buckwheat, **When** the place card opens, **Then** it names those crops, and names no crop the
   map does not draw.
4. **Given** a hamlet whose notes record a village district and its direction, **When** the place
   card opens, **Then** it names the district and the direction.
5. **Given** a hamlet whose notes record an Imperial road nearby, **When** the place card opens,
   **Then** it says so and gives the direction.
6. **Given** a settlement whose notes record none of those facts, **When** the place card opens,
   **Then** it still describes the place from what the map itself knows, and asserts nothing it
   cannot support.

---

### User Story 3 - A notes file can annotate any feature on one map (Priority: P2)

The facts in story 2 are not derivable from the drawing - no manifest knows which village district a
hamlet belongs to. They are authored, and they belong with the map's other authored material, in the
`<name>.notes.md` file that already sits beside every generator. A GM (or a session) writing a note
about ONE map's windbreak, or about where ONE map's lanes lead, writes it there in a documented
format, and it appears in that feature's modal on that map only.

The village lane is the worked example, and it has a default: a hamlet's lanes lead into the
district's main village unless the notes say otherwise - which is why the class is called a *village
lane* and not a hamlet lane.

**Why this priority**: it is the mechanism stories 2 and 4 stand on, but the GM described it as a
general capability in its own right, and it must be usable for a feature nobody has thought of yet.

**Independent Test**: add a per-map note for one feature class to one notes file, regenerate that
map, and see the note in that class's modal - and see the same class's modal on a different map
unchanged.

**Acceptance Scenarios**:

1. **Given** a notes file carrying a per-map annotation for a feature class present on the map,
   **When** that class's modal opens, **Then** the annotation is shown, distinguished from the
   class's general explanation as something true of THIS map.
2. **Given** a notes file with no machine-readable section at all - which is the normal case for
   most of the pool - **When** the page is written, **Then** it is written successfully with no
   annotations and no warning, exactly as before this feature.
3. **Given** a notes file whose machine-readable section is malformed, misspelled, half-written or
   truncated, **When** the page is written, **Then** the page is still written, the unparseable
   material is ignored rather than guessed at, and nothing false reaches the reader.
4. **Given** a notes file annotating a class key that is not in the class registry, or a class not
   present on that map, **When** the page is written, **Then** the annotation is dropped silently
   from the page and reported to the author by the map's own tooling, not to the reader.
5. **Given** a hamlet with no lane annotation, **When** the village lane's modal opens, **Then** it
   says the lanes lead to the district's main village, naming it if the notes name the district.

---

### User Story 4 - The pool's hamlets know where they are (Priority: P2)

Today a reader of any hamlet page is told what a hamlet is but never which district it belongs to,
because no hamlet in the pool records one. The GM supplied the geography for two of them and asked
that the rest be given invented districts drawn from the existing Rokugani place-name stock.

**Why this priority**: it is the content that makes stories 2 and 3 visible, but it is data, not
mechanism, and it lands after them.

**Independent Test**: open each hamlet's page and click its title card; each names a district and a
direction.

**Acceptance Scenarios**:

1. **Given** Akagahara or Ikegami, **When** the place card opens, **Then** it names Hoshigaoka as
   the village district - east of Ikegami, north-east of Akagahara - and reports the Imperial road
   directly south.
2. **Given** the Hoshigaoka village page, **When** the place card opens, **Then** it names Hayakawa
   county, the Imperial road directly south, and the county town of Hayakawa beyond it.
3. **Given** any other hamlet in the pool, **When** the place card opens, **Then** it names a
   village district whose name is drawn from the project's Rokugani place-name stock and passes the
   kanji-romaji-meaning triangle (constitution XI).

---

### Edge Cases

- **A map with no notes file at all** (a `wip/` draft, a regression fixture): the page is written
  from the manifest alone.
- **A notes file that is not the map's** - two maps in one directory, a stale file: the reader looks
  only for the file whose stem matches the map's own output base, never a directory scan.
- **A settlement that is not a hamlet.** A village has a headman and a shrine and is itself the head
  of its district; a town has a magistrate. The place card must say the right thing at each scale,
  or say less rather than say something false.
- **A map that grows no dry crops at all**, or whose only field is dry: the crop sentence adapts or
  is omitted; it never names an empty list.
- **Annotation text containing markdown or HTML characters**: it reaches the page as text, never as
  markup.
- **A very long annotation**: the modal scrolls; it does not overflow the page.
- **The place card and the map's furniture.** The scale bar stays un-highlighted and unclickable -
  only the placard changes status.

## Requirements *(mandatory)*

### Functional Requirements

**The presumption of accuracy**

- **FR-001**: The page MUST NOT tell the reader that a feature is historically accurate. The phrase
  and every paraphrase of it disappear from the rendered page.
- **FR-002**: The page MUST continue to lead a `deviation` or `guess` modal with the liberty: the
  first thing the reader is told about such a feature is that it departs from the record, and how.
- **FR-003**: The recorded qualification attached to an `accurate` class (which typically discloses
  which parts are read and which are drawing conventions) MUST still reach the reader, positioned
  after what the feature is and why it stands there rather than before it.
- **FR-004**: The three-way classification MUST remain recorded per class in the vocabulary, and
  MUST remain readable by the map's own tooling - constitution XII requires the record whether or
  not the page prints the word.

**The place card**

- **FR-005**: The title placard MUST become a highlightable, clickable feature of the page. The
  ruling that placed it out of highlighting is overturned for the placard and its title text, and
  the overturning is recorded beside the ruling it replaces.
- **FR-006**: The scale bar and its captions MUST remain out of highlighting.
- **FR-007**: Clicking the placard MUST open an overview of the SETTLEMENT rather than of a kind of
  feature, headed by the settlement's name.
- **FR-008**: The overview MUST state what kind of settlement this is in terms a player can use -
  for a hamlet, that it is a small outlying farming community belonging to a village district, with
  no headman, shrine or burial ground of its own - and MUST say whether that is the ordinary case
  or an unusual one.
- **FR-009**: The overview MUST state the approximate number of farmhouses and the approximate
  population, both marked as approximate with a tilde, derived from what the map actually drew.
- **FR-010**: The overview MUST name the crops the map grows, distinguishing the wet fields from the
  dry ground, and MUST name only crops the map draws.
- **FR-011**: The overview MUST name the village district the settlement belongs to and the
  direction it lies in, when the map's notes record them.
- **FR-012**: The overview MUST report other notable things in the area recorded by the map's notes
  - an Imperial road and its direction, the county, the county town - and MUST omit each cleanly
  when unrecorded.
- **FR-013**: The overview MUST be correct at every settlement scale the generator supports, and
  MUST omit rather than invent what does not apply at a given scale.
- **FR-014**: Every figure the overview states MUST be derived from the map's own manifest or from
  the map's notes file. The overview MUST NOT contain a number, a crop or a name written into the
  page generator by hand for one map.

**Notes the page can read**

- **FR-015**: A documented, human-readable convention MUST exist for recording machine-readable
  facts inside a settlement's existing `<name>.notes.md`, alongside its prose, without disturbing
  that prose. The convention MUST be documented where an author will find it.
- **FR-016**: The convention MUST support two kinds of entry: facts about the PLACE (feeding the
  place card), and an annotation attached to a named feature class (feeding that class's modal on
  that map).
- **FR-017**: The reader MUST be resilient by construction: a missing file, a missing section, a
  malformed section, an unknown key, an empty value or a truncated file MUST each yield no
  annotation rather than an error, a crash, a guess, or a half-parsed sentence. Page generation
  never fails because of a notes file.
- **FR-018**: A per-feature annotation MUST appear only on the map whose notes carry it, and only
  when that feature class is present on that map.
- **FR-019**: A per-feature annotation MUST be presented as being about this map, distinct from the
  class's general explanation, so a reader is never led to think a local fact is a general one.
- **FR-020**: An annotation naming an unknown or absent class MUST be reported to the author through
  the map's own tooling, so a typo is caught, while never reaching the reader.
- **FR-021**: The village lane class MUST default to leading into the district's main village when
  the notes carry no lane annotation, naming the village when the notes name the district. The
  default MUST be recorded as the reason the class is called a village lane.

**The pool's geography**

- **FR-022**: Akagahara's and Ikegami's notes MUST record the district of Hoshigaoka - east of
  Ikegami, north-east of Akagahara - and an Imperial road directly south of both.
- **FR-023**: Hoshigaoka's notes MUST record that it lies directly north of that Imperial road, in
  Hayakawa county, with the county town of Hayakawa further south of the road.
- **FR-024**: Every hamlet in the pool MUST record a village district. Where the GM has not named
  one, a name is invented from the project's existing Rokugani place-name stock and passes the
  kanji-romaji-meaning triangle.
- **FR-025**: The invented names and the geography they imply MUST be recorded as invented, so a
  later reader can tell them from the GM's own rulings.

### Key Entities

- **Map notes block**: the machine-readable region of a `<name>.notes.md`. Holds place facts and
  feature annotations. Optional everywhere; absent from most files.
- **Place facts**: district name, district direction, county, nearby Imperial road and its
  direction, county town - each optional, each authored.
- **Feature annotation**: a class key plus a sentence or two true of this map's instance of that
  class.
- **Place overview**: the assembled description shown when the placard is clicked - manifest-derived
  figures and crops, plus the authored place facts, plus the settlement-kind text for the scale.

## Success Criteria *(mandatory)*

- **SC-001**: On the reference hamlet's page, no modal contains the words "historically accurate";
  every modal for a deviation or a guess still opens with that liberty named.
- **SC-002**: A reader who opens the reference hamlet's page and clicks the title card learns, in
  one screen and without scrolling on a desktop viewport, what kind of place it is, roughly how many
  farmhouses and inhabitants it has, what it grows, which district it belongs to and in which
  direction, and that an Imperial road lies nearby - if the notes record one.
- **SC-003**: Every number and crop name in that overview can be traced to the map's manifest or to
  its notes file; none is hardcoded per map in the page generator.
- **SC-004**: Deleting the machine-readable block from every notes file in the pool leaves every
  page still generating successfully, with the place cards falling back to what the maps know.
- **SC-005**: Corrupting a notes block - a broken heading, a truncated line, an unknown class name -
  produces a page with fewer annotations and no error, and the unknown class name is reported to the
  author by the tooling.
- **SC-006**: Every hamlet page in the pool names its village district and the direction it lies in.
- **SC-007**: The `.svg`, `.png` and `.json` of every map are byte-identical to before the feature,
  apart from the recorded class of the placard's ink. The drawing does not change.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| The page never states historical accuracy; the presumption is accuracy, and only liberties are named | rendering convention (no physical claim) | The GM, 2026-08-29: a claim made about nearly every feature carries no information, while a liberty does. The three-way record is unchanged - only its presentation | `interactive/classes.py` docstring, `interactive/page.py` at the label build, `dev/reviews.md` |
| The disclosure attached to an accurate class moves after the what/why rather than being deleted | rendering convention | Those notes are where an accurate class discloses its own drawing conventions ("the drawn stroke is at true size", "the crop mix is rolled from the seed and is a GUESS at the proportions"); deleting them would delete the very liberties the GM asked to have called out | `interactive/page.py`, `interactive/assets/page.js` |
| The title placard becomes a highlightable, clickable feature; the scale bar does not | rendering convention | The GM, 2026-08-29, asked to click the title card for a "what is this place" overview. The scale bar is furniture with nothing to say | `interactive/classes.py` `NOT_HIGHLIGHTED_RULINGS` (the overturning recorded beside the 2026-08-27 ruling), `settlement/finish.py` `title()` |
| Population is stated as ~5 inhabitants per household, tilde-marked | accurate | The tier's own band: `settlements.md` puts a hamlet at 50-100 inhabitants for 10-20 households, which is the same 5. Stated with a tilde because it is a band, not a count | `settlements.md`, the place-card builder |
| A rice-farming hamlet belonging to a village district is presented as the ORDINARY kind | accurate, pending the research pass | The GM asked whether this is "the most common type of hamlet that exists". The claim needs the research pass and a source before the page states it; if the record is silent the page says less | `research/archetypes.md` (the entry this feature writes), the place-card builder |
| A hamlet's lanes lead to the district's main village unless the notes say otherwise | accurate | The GM, 2026-08-29: "I have been referring to hamlet lanes as village lanes specifically for this reason because they are presumed to lead into the main village when not otherwise stated" | `interactive/classes.py` village lane entry |
| Village districts invented for the pool's unnamed hamlets | guess - invented, not researched | The GM asked for names drawn from the existing stock where none is recorded. They are fiction, labeled as such, and any of them can be overruled by name | each hamlet's `.notes.md` map-notes block, and the block's own header |

## Assumptions

- The machine-readable block lives inside the existing `<name>.notes.md` rather than in a new
  sidecar file: the GM named that file, and a second file would drift from it.
- The block is OPTIONAL everywhere. Most of the pool will never carry one, and the pool's regression
  fixtures never will.
- The place card describes a settlement; it does not attempt to describe the surrounding domain,
  province or clan, none of which the maps or their notes record today.
- Every hamlet gets its own invented district rather than being grouped under the pool's four
  existing village maps, because grouping would assert a geography the GM has not ruled, beyond the
  Hoshigaoka pair they did rule.
- The claim that a rice-farming hamlet under a village district is the commonest kind is treated as
  a RESEARCH question and runs the research pass before the page states it (constitution XII, "a
  guess is the last resort"). If the record is silent, the overview describes the place without
  ranking it.
- Population per household follows the tier band already in `settlements.md`; this feature does not
  reopen it.
- The drawing is untouched. This feature changes only the HTML target and the notes files, exactly
  as feature 134 did.
