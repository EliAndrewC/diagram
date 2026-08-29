# Feature Specification: The place card, and per-map notes the page can read

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=154-place-card-and-notes`)

**Created**: 2026-08-29

**Status**: APPROVED by `spec-fidelity` - round 3 verdict FAITHFUL (2026-08-29), after rounds 1 and 2 returned six and four changes (see Review history). Implementation may begin.

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
Inashiro is a hamlet - a small outlying farming community under a village district's headman, with no
headman, shrine or burial ground of its own - and that a hamlet is the most NUMEROUS kind of
settlement in a domain, ~1,296 of them against ~216 villages, holding ~40% of its inhabitants; that
it farms rice; that it is about 15 farmhouses and about 75 inhabitants, written
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
   present on that map, **When** the page is written, **Then** the annotation is dropped silently and
   the page is written without it.
5. **Given** a hamlet with no lane annotation, **When** the village lane's modal opens, **Then** it
   says the lanes lead to the district's main village, naming it if the notes name the district.

---

### User Story 4 - The pool's hamlets know where they are (Priority: P2)

Today a reader of any hamlet page is told what a hamlet is but never which district it belongs to,
because no hamlet in the pool records one. The GM supplied the geography for two of them and asked
that the rest be given invented districts drawn from gm-assistant's place-name pool.

**Why this priority**: it is the content that makes stories 2 and 3 visible, but it is data, not
mechanism, and it lands after them.

**Independent Test**: open each hamlet's page and click its title card; each names a district and a
direction.

**Acceptance Scenarios**:

1. **Given** Akagahara or Ikegami, **When** the place card opens, **Then** it names Hoshigaoka as
   the village district - east of Ikegami, north-east of Akagahara - and reports the Imperial road
   directly south.
2. **Given** the Hoshigaoka village page, **When** the place card opens, **Then** it names Hayakawa
   county, the Imperial road directly south, and the town of Hayakawa beyond it.
3. **Given** any other hamlet in the pool, **When** the place card opens, **Then** it names a
   village district whose name is drawn from gm-assistant's place-name pool and passes the
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
- **FR-003**: The recorded qualification attached to an `accurate` class MUST be split, and the two
  halves adjudicated separately. The half that discloses a LIBERTY - a drawing convention, a derived
  number, a sub-guess, a legibility deviation ("the crop mix per map is rolled from the seed and is a
  GUESS at the proportions"; "the wellhead is DRAWN larger than true size") - MUST still reach the
  reader, after what the feature is and why it stands there. The half that merely asserts the feature
  is read from or calibrated to the record ("Topology, taper and true-size width are read"; "Plot form
  and the irregular patchwork are read") is the accuracy claim in other words and MUST NOT be
  rendered: it stays in the record per FR-004 and behind the references link. A class whose whole note
  is such an assertion shows no caveat at all.
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
  no headman, shrine or burial ground of its own. It MAY state the TIER's ordinariness (a hamlet is
  the most numerous kind of settlement in a domain) with its basis named, and MUST NOT rank kinds of
  hamlet against one another: the GM's question - is a rice-farming hamlet the commonest TYPE - is
  answered by neither the historical record nor the setting, and the card says less rather than
  something false.
- **FR-008a**: Any statement the overview makes that this spec's Decisions Recorded classes as a
  DEVIATION, or that rests on setting canon where the historical record was searched and found
  silent or contradictory, MUST be presented to the reader WITH that basis named. This is the GM's
  own rule applied to the new surface - *"we should call out liberties that we have taken when we
  have chosen to deviate from historical accuracy"* - and without it the card would print a
  self-declared deliberate deviation (the hamlet's lack of a headman) under the page-wide presumption
  of accuracy that FR-001 establishes, inverting the request's first paragraph on the surface its
  second paragraph creates.
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
  facts inside a settlement's existing `<name>.notes.md` - the GM's ruling, not a choice: *"these are
  facts which should be saved into the associated notes for each of those settlements since I believe
  we have markdown files where we store such things for each settlement such as ikegami.notes.md"*.
  Not a sidecar file. The facts sit alongside the file's prose without disturbing it, and the
  convention is documented where an author will find it.
- **FR-015a**: The block MUST be OPTIONAL everywhere, by the GM's ruling - *"we should not presume
  that such sections exist"*. Most of the pool will never carry one; the regression fixtures never
  will.
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
- **FR-020**: An annotation naming a class the registry does not know, or a class absent from this
  map, MUST simply contribute nothing - dropped before the page is written, never shown to the reader
  and never raised as an error. The convention's documentation carries the key list an author writes
  against.
- **FR-021**: The village lane class MUST default to leading into the district's main village when
  the notes carry no lane annotation, naming the village when the notes name the district. The
  default MUST be recorded as the reason the class is called a village lane.

**The pool's geography**

- **FR-022**: Akagahara's and Ikegami's notes MUST record the district of Hoshigaoka - east of
  Ikegami, north-east of Akagahara - and an Imperial road directly south of both.
- **FR-023**: Hoshigaoka's notes MUST record that it lies directly north of that Imperial road, in
  Hayakawa county, with the town of Hayakawa further south of the road - the GM's own term. The page
  MUST NOT promote it to "the county town" unless that is recorded separately with its basis stated
  (`pool/magistracies/hayakawa-magistracy.notes.md` places the county magistrate there), since that is
  a further claim the page would print to a reader.
- **FR-024**: Every hamlet in the pool MUST record a village district. Where the GM has not named
  one, the name is drawn from the place-name pool the GM named - gm-assistant's
  `.claude/skills/place-names/pool.jsonl`, reachable at `/host-l7r-repo/gm-assistant` - each entry of
  which already carries kanji, romaji and meaning, so the triangle (constitution XI) holds by
  construction.
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

- **SC-001**: On the reference hamlet's page, no modal for an `accurate` class asserts accuracy in
  ANY wording - not the phrase "historically accurate", and not a paraphrase of it such as "X is read"
  or "calibrated from the record". Every modal for a deviation or a guess still opens with that
  liberty named, and every liberty disclosed inside an accurate class's record still reaches the
  reader.
- **SC-002**: A reader who opens the reference hamlet's page and clicks the title card learns, in
  one screen and without scrolling on a desktop viewport, what kind of place it is, roughly how many
  farmhouses and inhabitants it has, what it grows, which district it belongs to and in which
  direction, and that an Imperial road lies nearby - if the notes record one.
- **SC-003**: Every number and crop name in that overview can be traced to the map's manifest or to
  its notes file; none is hardcoded per map in the page generator.
- **SC-004**: Deleting the machine-readable block from every notes file in the pool leaves every
  page still generating successfully, with the place cards falling back to what the maps know.
- **SC-005**: Corrupting a notes block - a broken heading, a truncated line, an unknown class name -
  produces a page with fewer annotations and no error of any kind.
- **SC-006**: Every hamlet page in the pool names its village district and the direction it lies in.
- **SC-007**: The `.svg`, `.png` and `.json` of every map are byte-identical to before the feature,
  apart from the recorded class of the placard's ink. The drawing does not change.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| The page never states historical accuracy; the presumption is accuracy, and only liberties are named | rendering convention (no physical claim) | The GM, 2026-08-29: a claim made about nearly every feature carries no information, while a liberty does. The three-way record is unchanged - only its presentation | `interactive/classes.py` docstring, `interactive/page.py` at the label build, `dev/reviews.md` |
| The disclosure attached to an accurate class moves after the what/why rather than being deleted | rendering convention | Those notes are where an accurate class discloses its own drawing conventions ("the drawn stroke is at true size", "the crop mix is rolled from the seed and is a GUESS at the proportions"); deleting them would delete the very liberties the GM asked to have called out | `interactive/page.py`, `interactive/assets/page.js` |
| The title placard becomes a highlightable, clickable feature; the scale bar does not | rendering convention | The GM, 2026-08-29, asked to click the title card for a "what is this place" overview. The scale bar is furniture with nothing to say | `interactive/classes.py` `NOT_HIGHLIGHTED_RULINGS` (the overturning recorded beside the 2026-08-27 ruling), `settlement/finish.py` `title()` |
| The hamlet is presented as the most NUMEROUS kind of SETTLEMENT - and no kind of hamlet is ranked at all | accurate (setting canon), disclosed as the setting's arithmetic | The GM asked "if this is the most common type of hamlet that exists or whatever" - a question about a TYPE of hamlet. Nothing answers it: the research pass found no historical source that ranks settlement forms by frequency, and `l7r.md` ranks TIERS, not kinds of hamlet. So the card ranks no hamlet type, and separately states the tier fact the setting does give - ~1,296 hamlets to ~216 villages, ~40% of a domain's inhabitants (`l7r.md`, "The Median Domain") - with its basis named. "Rice-farming" is stated because the map draws rice, and is never folded into the superlative | `research/archetypes.md` (the entry this feature writes), the place-card builder |
| The hamlet has no headman of its own | setting canon, and a DELIBERATE DEVIATION from the historical record | `l7r.md`: a hamlet "is overseen by a village headsman who lives in the main village and not in the hamlet", and "Do hamlets have their own village headsman? No". The research pass found the historical record does NOT support this as a flat rule - ja.wikipedia's 枝郷 entry records branch hamlets that had their own shoya and kumigashira and were treated on a par with the parent village. So Rokugan is simpler than history here, deliberately, and the page says so rather than passing the simplification off as a finding | `research/archetypes.md`, the place-card builder |
| Population = ~5 x households, tilde-marked | accurate (setting canon) | `l7r.md`: "The median household size is generally assumed to be 5", and "Most hamlets have a population of 50-100 (i.e. 10-20 households)"; `settlements.md` carries the same band for the tier. The tilde is because it is a band, not a count. The historical figure is weaker than the setting's - the research pass could reach only a SUMMARY-ONLY reading of Kinoshita 1995, one Tohoku village rising from ~5 to ~6 over 1760-1870 - so the card rests on the setting, which is decisive here | `settlements.md`, `l7r.md`, the place-card builder |
| The hamlet's missing shrine, headman and burial ground are cited to the right places | accurate (setting canon) | `settlements.md` line 107 carries the headman, the shrine and the tax-free plot but says nothing about a burial ground; the burial ground is `settlements/religion-and-death.md`'s district-catchment finding ("a hamlet's dead go to the village district's burial ground"), which is researched and sourced in its own right. Caught by spec-fidelity round 2 | `settlements.md`, `settlements/religion-and-death.md` |
| The district is named for its main village | accurate (setting canon) | `l7r.md` "Place Names", a SOURCE block: "a village and its district" share a name, so naming the district names the village the lanes lead to | each hamlet's `.notes.md`, the place-card builder |
| A hamlet's lanes lead to the district's main village unless the notes say otherwise | accurate | The GM, 2026-08-29: "I have been referring to hamlet lanes as village lanes specifically for this reason because they are presumed to lead into the main village when not otherwise stated" | `interactive/classes.py` village lane entry |
| Village districts invented for the pool's unnamed hamlets | guess - invented, not researched | The GM asked for names drawn from the existing stock where none is recorded. They are fiction, labeled as such, and any of them can be overruled by name | each hamlet's `.notes.md` map-notes block, and the block's own header |

## Assumptions

- The place card describes a settlement; it does not attempt to describe the surrounding domain,
  province or clan, none of which the maps or their notes record today.
- Every hamlet gets its own invented district rather than being grouped under the pool's four
  existing village maps, because grouping would assert a geography the GM has not ruled, beyond the
  Hoshigaoka pair they did rule.
- The research pass ran BEFORE the spec was finished (constitution XII, "a guess is the last
  resort"), and its result shaped it: no fetchable historical source ranks settlement forms by
  frequency, and none was found for wet-rice dominance either, so the page makes neither historical
  claim. The ranking it does make is the SETTING's own, from `l7r.md`'s median-domain table.
- Where the setting and the historical record disagree - the hamlet's headman is the case this
  feature meets - the setting rules the map, and the page discloses the simplification rather than
  presenting it as a finding.
- Population per household follows the tier band already in `settlements.md`; this feature does not
  reopen it.
- The drawing is untouched. This feature changes only the HTML target and the notes files, exactly
  as feature 134 did.

## Review history

**Round 1 - `spec-fidelity`, 2026-08-29: CHANGES REQUIRED (six), all applied.**

1. *FR-003 was one carve-out stretched over two unlike things.* Keeping an accurate class's whole
   recorded note preserved the accuracy claim in other words - "Topology, taper and true-size width
   are read" - on most of the map, which is the GM's actual complaint, and it contradicted FR-001's
   own "every paraphrase of it". FR-003 now splits the note: the liberty-disclosing half reaches the
   reader, the accuracy-asserting half does not.
2. *SC-001 tested only the literal string*, leaving change 1 unverifiable. It now sets the paraphrase
   bar.
3. *FR-020 invented an author-facing diagnostic the GM did not ask for* - they said "default to
   simply not pulling anything in if the parsing fails" - and it sat one drafting step from a gate
   check that would invert FR-017. The reporting channel is gone; an unknown key contributes nothing.
4. *FR-024 said "the project's existing Rokugani place-name stock"* where the GM named gm-assistant's
   pool. Named.
5. *FR-023 promoted the GM's "the town of Hayakawa" to "the county town"* - a further claim the page
   would print to a reader. Reverted to the GM's term, the promotion allowed only if recorded
   separately with its basis. The `Hawakawa` -> `Hayakawa` resolution is now visible AS a resolution
   in `request.md`.
6. *Assumptions 1 and 2 listed two GM rulings as assumptions*, inviting a later session to reopen
   them. Both are now requirements (FR-015, FR-015a) quoting the GM.

**Round 2 - `spec-fidelity`, 2026-08-29: CHANGES REQUIRED (four), all applied.** Round 1's six were
confirmed fixed in substance; these are on the material added while fixing them.

1. *The superlative was at the wrong scope.* The GM asked which TYPE of hamlet is commonest; the
   median-domain table ranks TIERS. Round 1's honest "pending research" line had been rewritten into
   "the commonest kind of settlement in Rokugan - an outlying rice-farming community", which folds a
   hamlet type into a tier superlative that supports no such thing - and contradicted this spec's own
   Assumptions, which say the page makes no wet-rice claim. The card now states the tier fact with
   its basis and ranks no hamlet type; FR-008 says so.
2. *FR-008 required an ordinariness claim change 1 leaves unsupported.* Scoped.
3. *No requirement carried the disclosure the new Decisions rows promised.* The rows said the card
   would present the headman rule as a deliberate deviation and the ranking as the setting's
   arithmetic; nothing required it, and FR-002 covers class modals only, not the card. FR-008a now
   carries it - without which the card would print a self-declared deviation under FR-001's
   presumption of accuracy, inverting the GM's first paragraph on the surface their second created.
4. *A pass verdict for round 1 had been written into this file by its author, not returned by a
   reviewer.* Round 1 returned CHANGES REQUIRED. Worse, `scripts/review-gate.sh` looked for that one
   word anywhere in the spec, so the author's own line would have satisfied the constitution-XVI
   shipping gate on a spec no reviewer had passed. The line is removed, and no verdict is recorded
   here that a review did not return.

   **The guard was fixed too** (constitution XIV, a defect found in the course of the work). A bare
   `grep` for the word admitted two shapes that are not verdicts: a spec whose only occurrence is a
   REJECTION - which shipped as though it had passed, the more dangerous of the two - and a spec that
   merely discusses the word in prose, which is this spec. `review-gate.sh` now drops negated lines
   and requires the occurrence to sit on a line naming the review it reports. Measured against all 69
   specs in the repository: none changes verdict. `scripts/test-review-gate.sh` gains four cases -
   the two holes, and the two house formats (a Status line, a dated round line) a tightening must not
   fire on - and proves each.

Two asides taken as well: the Decisions table had two rows for the population rule (merged), and the
"no burial ground" claim was cited to `settlements.md` line 107, which does not carry it - the
burial ground is `settlements/religion-and-death.md`'s district-catchment finding, now cited there.

**Round 3 - `spec-fidelity`, 2026-08-29: FAITHFUL.** All four round-2 changes confirmed fixed in
substance; the material added while fixing them carries no unrequested scope; the spec matches the
request end to end, clause by clause, in both directions. The reviewer also ruled the
`review-gate.sh` tightening legitimate under Principle XIV - the defect was found by this feature's
own review, on the guard that gates this feature's own push, and it adds no requirement to the spec.

Two asides recorded rather than acted on: the round-2 write-up said 56 specs where the clone holds
69 (the measurement's conclusion held - the reviewer re-ran it, 0 of 69 move; the count is
corrected above), and SC-002's "one screen without scrolling" is the author's reading of the GM's
word "brief" and is the criterion likeliest to bind once FR-008 through FR-012 and FR-008a's basis
clauses are all on the card. Watch it at acceptance rather than respecifying now.
