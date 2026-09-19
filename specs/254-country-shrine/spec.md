# Feature 254 - the country shrine: a second Mode A building type, and checks in two layers

**Feature Branch**: `254-country-shrine` (no branch; `export SPECIFY_FEATURE=254-country-shrine`)

**Created**: 2026-09-19

**Status**: specified; FAITHFUL at round 2 (see Review history); planning

**Input**: the GM's message of 2026-09-19, verbatim in [`request.md`](request.md); the research pass in
[`research.md`](research.md).

## Summary

The GM wants to add building types beyond the magistracy, hand-authored as the magistracy is and held to
automated checks - some shared by every type ("whether different shapes end up overlapping with each
other"), some specific to one - and, because this is the first time a second type is added, wants the
structure of those checks and the process of adding a type thought through now. The next type is the
**country shrine**: the shrine of a village district's country monk. The GM asked three research
questions of it and answered the third in advance: does the monk live there (if there is any choice,
yes - for consistency with past adventures and the RPG's source material), what is in one, and how big
is it against a farmhouse - noting that the village maps' shrine size was never itself researched.

The research pass ran first (constitution XII) and is recorded in `research.md`. Its answers, in one
line each: **the monk lives there, and that is the historically accurate form** - before 1868 a
Japanese village's sacred site was ordinarily a shrine with a small Buddhist temple attached where the
shrine-monk lived and performed the villagers' rites, and the parish temple's priest lived in its kuri;
**a country shrine is a small precinct** - a tiny sanctuary, and a hall that is at once the villagers' rite-place and
the monk's home, the GM's form ("the shrine is both their home and the place where the villagers come"),
which the sources attest as a hall and dwelling under one roof and call rare against the ordinary parish
temple's separate hall and priest's house - with an arch on its approach, a well, a fence, its grove and
the burial ground beside it; **it is larger than a farmhouse because it contains one**: a village hall
alone runs from about 20 ft square to 35 ft square on measured examples, and the one-roof building adds
a farmhouse to it, so the 60 by 48 ft hall the village maps draw is inside the one-roof form's measured
band. (The source dimensions: observed 2026-09-19; method: the dimension as printed on the cited cultural-property or encyclopedia page, read by a Sonnet reader whose report is in the session's scratchpad and becomes the footnote when the entry lands. The 60 by 48 ft: observed 2026-09-19; method: read off the record's own rule text (religion-and-death.html, homesteads.html) - the project's drawn values, not a source's.)

Three things are delivered: (1) the check architecture for many building types - a type is declared
ONCE and everything keys off the declaration; the checks are a shared layer and a per-type layer; every
Mode A sheet in the live pool is swept by the gate - and the written process for adding a type; (2) the
country shrine's program in the catalog, its research on the record with footnotes, and the village
tier's shrine-size entry corrected by the same research; (3) one exemplar country shrine, drawn,
reviewed and in the pool under its own tier.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A building type is declared once, and the checks come in two layers (Priority: P1)

A session adding a building type declares it in one place - the type's name (which is its pool tier),
the program items every instance must carry, the size band of each, and which checks apply to it - and
nothing else in the engine has to learn the type's name. The checks that run on the type's sheets are
the shared layer, which asks of every Mode A sheet the questions that are pure geometry (does any built
shape overlap another, stand in a wall or fence, bury a label or a glyph; does every opening's ink match
its stated width; is the scale bar present; is the sheet cropped), plus the type's own layer (are the
program's required items present and labeled; is each within its size band; does the composition rule
that defines the type hold - two courts and a perimeter ring for a magistracy, a sanctuary behind a hall
on the approach axis for a shrine). Every sheet in the live pool is swept by the gate exactly as a
scripted map is, and a failure names the sheet, the check and the fix.

**Why this priority**: it is the GM's structural question, asked because "this is the first time that
we are adding a second type of diagram", and every later type inherits whatever is decided here. Today
a second type would touch five places by hand (`request.md`, "What the record held"), and the scripted
audit assumes a walled compound with an earth court and is run only when a session remembers to.

**Independent Test**: with the magistracy re-declared under the new shape and the shrine declared beside
it, (a) a grep for either type's name outside its declaration, its pool tier, its program prose, its
fixtures and its tests finds nothing; (b) `make quick` fails on a pool sheet given a deliberate defect
of each shared check and each per-type check, and passes on the pool as it stands; (c) the checklist in
`buildings.md` for adding a type lists exactly the files touched.

**Acceptance Scenarios**:

1. **Given** the magistracy and the country shrine declared as types, **When** the gate runs, **Then**
   every sheet under `pool/magistracies/` and `pool/country-shrines/` is swept with the shared layer and
   its own type's layer, and the sweep is listed in the gate's roster of what it checks.
2. **Given** a red fixture for each check (a copy of a pool sheet with one defect introduced by hand),
   **When** the check runs on it, **Then** it fails naming the defect; and on the unbroken sheet it
   passes. A check with no red fixture is not merged.
3. **Given** a shrine sheet whose precinct is bounded by a fence and a hedge rather than a wall,
   **When** the shared layer parses it, **Then** it reads the precinct from the sheet's own declaration
   of it and does not require a compound wall or an earth court to exist.
4. **Given** a third type declared in a future feature, **When** its declaration is added, **Then** the
   pool classification, the pool index, the ignore rules for hand-drawn source, the size table and the
   sweep all pick it up without an edit of their own.

---

### User Story 2 - The country shrine's program and its research are on the record (Priority: P1)

The program catalog gains the country shrine: what every instance carries, the knobs that make two
differ, and the size band of each part, with the reasoning in the record. The record answers the GM's
three questions as questions a reader might ask from the map, each assertion footnoted with the passage
it rests on, the four labels applied; the village tier's shrine-size entry - which says no source gives
a village shrine a footprint - is corrected, because sources now do.

**Why this priority**: the GM said "I am going to want to know what is in one of these shrines"; the
program is what the exemplar is drawn to and what the reviewers check against; and an unrecorded
research decision is the one failure (CLAUDE.md, Research).

**Independent Test**: the program entry exists in `buildings/programs.md` with required items, knobs and
size anchors; the record's new sections pass `quote-check` (every footnote readable and verbatim),
`record-format` and `source-applicability` for every new source; the village-shrine section no longer
says no source gives a footprint.

**Acceptance Scenarios**:

1. **Given** the record, **When** a reader asks "Does the country monk live at the shrine?", **Then**
   a section answers yes with the jingūji and bettō-ji finding, the parish temple's kuri, the Chinese
   resident keeper, the RPG's own statement, and discloses that a pure Shinto village shrine had no
   resident and some rural temples stood unstaffed - labeled ACCURATE.
2. **Given** the record, **When** a reader asks "How big is a country shrine, and what stands in its
   precinct?", **Then** a section gives the measured halls (a village Kannon hall 6.54 m square of 1778;
   a haiden of 9.78 by 10.62 m of 1790; a hondō of 5 by 5 ken), the sanctuary of one bay, the
   kuri "resembling the farmhouse of its region", the one-roof form of Kaie-ji, and states which sizes
   on the sheet are accurate, which are guesses, and why.
3. **Given** the existing section "Where does a village put its shrine, and how big is it?", **When**
   it is revised, **Then** it cites the measured halls, says the drawn 60 by 48 ft hall reads as a hall
   and dwelling under one roof - the GM's form, the attested Kaie-ji form - and is inside that form's
   measured band, so the village maps draw the country shrine the GM described.
4. **Given** every source the pass brought in, **When** `source-applicability` judges it, **Then** each
   is APPLICABLE or APPLICABLE-WITH-LIMITS with the limits written into its registry entry (the RPG
   wiki as a tertiary summary of the rulebooks; the Chinese Mianning study as Qing Sichuan; the modern
   Fuzhou earth-god shrine as illustrative only).

---

### User Story 3 - One country shrine is drawn, reviewed and in the pool (Priority: P2)

A first country shrine is hand-authored to the program at 3 px = 1 ft, with its design notes, passes
`building-review` and `size-audit` (each pass a ledger row), and stands in the pool under
`pool/country-shrines/<name>/` with the same three files a magistracy has.

**Why this priority**: a program with no instance has taught the checks nothing; the exemplar is what
proves the type's layer fires (its red fixtures are cut from it) and what the GM opens.

**Independent Test**: the folder holds `<name>.svg` (tracked source), `<name>.gen.py` (rasterizes
only), `<name>.notes.md` (program type, every knob, particulars, review log); `make quick` sweeps it
green; `docs/review-ledger.md` carries its building-review and size-audit rows; the pool index lists it
under its tier with its program type.

**Acceptance Scenarios**:

1. **Given** the drawn sheet, **When** `size-audit` runs from `make size-table`, **Then** every building
   is within the program's band and the hall out-foots the sanctuary and the dwelling does not out-foot
   the hall by more than the program allows; any exception is a recorded particular.
2. **Given** the sheet, **When** `building-review` runs, **Then** every required item is present, no
   label states the obvious (no "gate", no "to the village"), and nothing generic stands in a box.
3. **Given** the pool index rebuilt, **When** the GM opens it, **Then** the shrine appears under a
   "country shrines" tier with its program type read from its notes, beside the magistracies.

---

### Edge Cases

- A sheet whose tier folder has no declaration: the sweep fails loudly naming the folder (the pool
  classifier's "unknown" today), never silently skips it.
- A magistracy sheet that generates its SVG (`county-magistracy-example`, `ochiba-roundtrip-test`)
  alongside hand-drawn ones in the same tier: the ignore rule is per tier and per file-kind, and a
  generated SVG in a hand-authored tier is a declared exception, not a pattern.
- The two knob forms of the hall and dwelling - one roof (the default, the GM's form; Kaie-ji, attested
  and called rare) or two buildings (the ordinary parish temple's hall and kuri): the program-completeness
  check counts a combined building as both items when the notes declare the form.
- A shrine with no bell tower: the knob's absent value; the check does not require one.
- A check the shared layer inherits from the magistracy that is really the magistracy's (the coverage
  band of 37-42%, perimeter hugging, the notice board by the gate, two-court zoning): each is moved to
  the magistracy's layer, not generalized. Fire-water is NOT one of these: both programs require it, so
  the check declares both types.

## Requirements *(mandatory)*

### Functional Requirements

**A. The type declaration and the two layers**

- **FR-001 - one declaration per type.** A Mode A building type is declared once, as data the engine
  reads and the docs render from: its tier name (the pool folder, `magistracies`, `country-shrines`),
  its program's required items with the label each is found by, the size band of each item in feet,
  the composition checks that apply to it, and whether its SVG is hand-drawn source. Every consumer
  that today names `magistracies` or lists compound gens by filename - the pool classifier, the pool
  index, the size table's usage text, the gate's sweep - derives from the declaration. The ignore rule
  for hand-drawn source is written per tier, not per file, and the declaration states which tiers are
  hand-drawn so a test can hold the ignore file to it.
- **FR-002 - a shared layer, for every sheet.** The audit's geometry checks - structures overlapping
  each other, structures in wall or fence ink, occlusion of labels and glyphs, label clashes, dark-on-
  dark labels, floating doors, passage blockers, opening widths against their stated widths, the scale
  bar present, the viewBox cropped - run on every Mode A sheet regardless of type. The shared layer
  reads the precinct from the sheet's own declaration of it (a marked boundary element), never by
  requiring a compound wall or an earth-court fill; a sheet that declares no precinct fails naming that.
- **FR-003 - a per-type layer.** A check declares the types it applies to; those that are the
  magistracy's (coverage band, perimeter hugging, notice board by the gate, two-court zoning) move under
  the magistracy, and the shrine gets its own (below). A check declares EVERY type it applies to, and a
  check two programs require declares both: fire-water declares the magistracy and the country shrine. Two checks are per-type in
  MECHANISM but generic in code: program completeness (every required item's label present) and size
  bands (every item within its band, from the same size table `size-audit` is handed), both reading the
  declaration.
- **FR-004 - the gate sweeps the live pool.** Every sheet under a declared tier in `pool/` is swept
  by the gate with the shared layer and its type's layer; the sweep is a test of the pool, listed in
  the gate's roster, and a failure names the sheet, the check and the compliant fix. The frozen legacy
  tree is not swept (it holds no Mode A sheets).
- **FR-005 - every check has a red fixture.** Each shared and per-type check is proven to fire on a
  fixture with one defect introduced by hand (the existing `tests/fixtures/*-red.svg` convention), and
  to pass on the unbroken sheet; a check without one is not merged.
- **FR-006 - the reviewers stay one per mode.** `building-review` and `size-audit` remain the single
  reviewers for every type, reading the type's program at review time; their prompts name the program
  by type rather than by the magistracy. Adding a type adds no agent.
- **FR-007 - the process is written.** `buildings.md` gains a section "Adding a building type": research
  pass first; the record entry; the program entry (data and prose); the type's checks with red
  fixtures; the exemplar with notes, both reviews and ledger rows; the pool tier. It lists exactly the
  files a type touches, and a test holds the list to the declaration (a type name found outside them
  fails).

**B. The country shrine's program**

- **FR-008 - the program entry.** `buildings/programs.md` gains "Country shrine (a village district's
  shrine)", the seat of the district's country monk. Required program: a **sanctuary** (the deity's
  house, one bay, at the back of the precinct on the approach axis, raised); a **hall** where the
  villagers gather, the precinct's largest building, on the axis before the sanctuary; the **monk's
  dwelling**, farmhouse-class, beside or joined to the hall, with a writing room or record chest for
  the district's registers; an **arch** on the approach where the way enters the precinct and the
  **approach** running under it to the hall; a **well or basin** beside the approach, never under the
  arch; a **fence or hedge**, never a wall; the **grove** the precinct stands in, with hall and arch in a
  cleared opening; the **burial ground** beside the precinct; a **kitchen garden** and a **privy** at the
  dwelling; **fire-water** at the wooden buildings. No office building, no bell as a requirement, no
  guardian figures as a requirement. The tax-free fields lie off the sheet.
- **FR-009 - the knobs.** (1) **Hall-and-dwelling form**: one roof (the default - the hall is the monk's home and the villagers'
  rite-place in one building, attested at Kaie-ji and called rare there) or two buildings (the ordinary
  parish temple's hall and kuri). The default is set against the sources' "rare" on the GM's own words
  of 2026-09-19 - "the shrine is both their home and the place where the villagers come ... if there is
  any choice in the matter, then I want to make that the case" - and the entry says so. (2) **Bell tower**: absent (default)
  or present. (3) **Dedication and its furniture**: the Fortune the shrine serves and what that puts on
  the sheet - the instance particular, designed with the GM. (4) **Grove and burial-ground side**: which
  side of the precinct each takes, by the site. (5) **Wealth**: a poor district's thatch and plain
  timber against a rich one's tile and lanterns. Each knob's setting is written in the notes file.
- **FR-010 - the size anchors.** Sanctuary about 6 ft square (a one-bay honden, 1.98 by 1.82 m
  measured; ACCURATE). The one-roof building - the villagers' hall and the monk's home together, the
  default - 200 to 330 sq m (Kaie-ji, 25.2 m long by 8 to 13 m deep; ACCURATE as a band from one
  attested example, disclosed as such), its hall end 20 to 35 ft on a side (a 1778 village hall 6.54 m
  square; a 1790 haiden 9.78 by 10.62 m; a hondō 5 by 5 ken; ACCURATE as a band) and its dwelling end
  the farmhouse's 46 by 28 ft (form ACCURATE - a kuri "resembling the farmhouse of its region"; size
  a GUESS, no small kuri measured). In the two-building form the same two bands apply to the two
  buildings. Precinct a GUESS bounded by its contents, disclosed as such (no Japanese precinct area
  read; the one compound figure is Chinese, 2.5 mu). The hierarchy holds: the hall-and-dwelling
  building out-foots every other building on the sheet, and the sanctuary is the smallest. (The source
  figures: observed 2026-09-19; method: the dimension as printed on the cited cultural-property or
  encyclopedia page, read by a Sonnet reader; the 46 by 28 ft is the project's drawn farmhouse from
  the record.)
- **FR-011 - residence is fixed, not a knob.** The monk lives at the shrine, and on the sheet that means
  UNDER THE HALL'S ROOF by default (knob 1), not merely within the fence. The record labels it
  ACCURATE (the jingūji and bettō-ji before 1868; the parish temple's kuri; the RPG's own statement)
  and discloses the two forms history also had - a pure Shinto village shrine with no resident, tended
  by the parishioners' rota, and the unstaffed rural temple with a commuting priest - as forms the
  setting does not draw, by the GM's ruling of 2026-09-19 and the campaign notes.

**C. The record**

- **FR-012 - two new sections** on `research/religion-and-death.html`: "Does the country monk live at
  the shrine?" and "How big is a country shrine, and what stands in its precinct?", each with its
  `Sources:` line, every assertion footnoted on the citations page with the passage verbatim (English
  translation marked as one, the original kept), glossary tooltips for kuri, honden, haiden, bettō,
  jingūji, miyaza, jochi, and the four labels applied. Both are `research: physical` work with the five
  boxes.
- **FR-013 - the village section corrected.** "Where does a village put its shrine, and how big is it?"
  drops "No source gives a village shrine a footprint", cites the measured halls, and states that the
  drawn 60 by 48 ft hall IS the one-roof form - the monk's home and the villagers' hall in one building,
  the GM's form, attested at Kaie-ji - and lies inside that form's measured band (200-330 sq m), labeled
  ACCURATE with the disclosure that the sources call the one-roof form rare and the two-building form
  ordinary. No village map is redrawn: nothing on them is wrong. `entry-drift` is run on every class
  entry that names the section.
- **FR-014 - the registry.** Every page read gets a registry entry with its two write-ups, judged by
  `source-applicability` before its numbers reach the program: the Japanese Wikipedia pages on the
  kuri, the jūshoku, the miyaza, the shake, the bettō, the bettō-ji, the jingūji, the shrine, the
  shrine office, the precinct, the jochi, the shuinchi, the danka system and the registers; the
  English pages on the kuri, the jingūji, shinbutsu bunri and shinbutsu shūgō, nagare-zukuri and the
  Chinese temple; the cultural-property pages for Chōnen-ji, Kaie-ji, Daiō-ji, Tokuun-ji, the Saitama
  Kannon hall, the Chikusei Yakushi hall, the Nara hondō and the Ehime honden and haiden; JAANUS
  shamusho; homemate's seven-hall page; the Mianning village-temple study; the Chinese Wikipedia pages
  on the earth-god shrine, the Xietang shrine, the lijia and the she; the Gantang temple article; and
  the L5R wiki's Seidō, Shinden and Monk pages. Pages that would not read (Baidu Baike, the Palace
  Museum PDFs, the Sakuragawa PDF, the Nagano register) are named in an absence note, not cited.

**D. The exemplar**

- **FR-015 - one country shrine drawn** at 3 px = 1 ft to the program, hand-authored SVG with a
  rasterizing gen and a notes file, under `pool/country-shrines/<name>/`, named for a village district
  already on the maps; its particulars beyond the program are the GM's to add later and the notes say
  so. It passes both reviewers with ledger rows, and it is the sheet the shrine's red fixtures are cut
  from.
- **FR-016 - the Mode B glyph is not changed.** The village tier is frozen; no village map is redrawn
  under this feature, and none needs to be: the record now states what the drawn hall is (FR-013).

### Key Entities

- **Building type**: a declared kind of Mode A sheet - tier name, required items with labels, size
  bands, applicable checks, hand-drawn or generated source.
- **Check**: one question asked of a parsed sheet, with the types it applies to (all, or a list), a
  result record, and a red fixture.
- **Program**: the prose a reviewer reads for a type, rendered from and consistent with the declaration.
- **Exemplar**: one pool sheet per type with its notes and review rows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: after the feature, a type's name appears outside its declaration, its pool tier, its
  program prose, its fixtures, its tests and the docs in ZERO engine files (a gate test counts).
- **SC-002**: every Mode A sheet in `pool/` is swept by `make quick` and `make done`; the sweep's cost on
  the six sheets (five magistracies and the shrine) is measured at implementation and recorded in the
  feature's measurements file, and the gate's ratchet holds it.
- **SC-003**: every shared and per-type check has a red fixture on which it fails and a pool sheet on
  which it passes - every check, none excepted, counted by a test over the check registry.
- **SC-004**: the record's two new sections and the revised village section pass `quote-check` with
  every footnote READABLE and VERBATIM, `record-format` with no SESSION NOTE or HISTORY finding, and
  every new source APPLICABLE or APPLICABLE-WITH-LIMITS with HONEST write-ups.
- **SC-005**: the exemplar passes `building-review` and `size-audit` with no open finding, each pass a
  ledger row.
- **SC-006**: the GM's three questions are each answered in one section heading a reader can reach
  from a map's references modal, with the label (accurate / deviation / convention / guess) on each
  finding.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| the country monk lives at the shrine; the dwelling stands on the precinct | accurate (Japan, the jingūji / bettō-ji before 1868 and the parish temple's kuri; China, the resident keeper at Mianning; the RPG's "most had at least one resident monk"), with the disclosure that a pure Shinto village shrine had no resident and some rural temples were unstaffed | the GM's ruling and the sources coincide; no knob | `research/religion-and-death.html`, "Does the country monk live at the shrine?"; `buildings/programs.md`, the shrine program; the exemplar's notes |
| sanctuary about 6 ft square, one bay | accurate | the ikkensha honden is the commonest form; a 1789 example measures 1.98 by 1.82 m | the same section; the size band in the declaration |
| hall 20 to 35 ft on a side | accurate as a band | three measured Edo halls and one haiden span it | the same |
| dwelling at the farmhouse's 46 by 28 ft | form accurate, size guess | the kuri "resembles the farmhouse of its region"; no small kuri measured | the same; the declaration |
| precinct size | guess, bounded by its contents | no Japanese precinct area could be read; one Chinese compound of 2.5 mu | the same |
| a fence or hedge, never a wall | accurate | the tamagaki and the grove bound a shrine; a wall is a compound's | the same; the shared layer's precinct rule |
| hall and dwelling under one roof as the DEFAULT form; two buildings as the knob's other value | accurate (attested at Kaie-ji, "unusual for early-Edo temple architecture"; the ordinary form is two buildings) | the GM's words of 2026-09-19 pick the attested-but-rare form: "the shrine is both their home and the place where the villagers come" | the program's knobs; the residence section |
| bell tower as a knob | accurate | the minimal temple is "a main hall and a bell tower"; a village hall may have neither | the program's knobs |
| the 60 by 48 ft village hall on the Mode B maps is the one-roof form, hall and dwelling in one building | accurate | it lies inside the one-roof form's measured band (Kaie-ji, 200-330 sq m); no village map changes | the revised village section |
| *the source figures in this table: observed 2026-09-19; method: the dimension as printed on the cited cultural-property or encyclopedia page, read by a Sonnet reader whose report is in the session's scratchpad and becomes the footnote when the entry lands; the 60 by 48 ft: observed 2026-09-19; method: read off the record's own rule text (religion-and-death.html, homesteads.html) - the project's drawn values, not a source's* | | | |
| the registers live in the dwelling (a writing room or chest), not a building | accurate | the temple issued the certificate and the headman compiled the ledger; a small shrine had no office building | the program; the second new section |

## Assumptions

- The exemplar's subject is a generic worked instance named for a village district already on the maps
  (as `county-magistracy-example` was for the magistracy); the GM has not named one, and the notes file
  says its particulars are open. Which village is chosen in the plan from the legacy village exhibits.
- "Hand-authored like the magistracy" means tracked SVG source with a gen that only rasterizes; no
  draft placer is written for the shrine (three buildings need none), and `compound.py`'s built-in
  magistracy program is not the declaration - the declaration is new and the placer may read it later.
- The village tier stays frozen (migration plan, GM 2026-08-16); the Mode B shrine finding is recorded,
  not drawn.
- The knob doctrine (constitution XII) applies to a hand-authored sheet as it does to the magistracy:
  a knob is set in the notes by the author, not rolled, because a Mode A sheet has no seed.
- The RPG wiki is cited as a public tertiary summary of the rulebooks (the books themselves are not
  public pages), with that limit in its registry write-up; the GM's campaign notes remain canon and
  need no citation.

## Review history

- Round 1 (2026-09-19, `spec-fidelity`, Opus): CHANGES REQUIRED, four items. (1) Knob 1's default
  was two buildings, against the GM's "the shrine is both their home and the place where the villagers
  come ... if there is any choice in the matter, then I want to make that the case" - the default is
  now one roof, FR-011 says what "lives at the shrine" means on the sheet, and FR-013 stops calling the
  village maps' single hall a limitation: it IS the GM's form. (2) Fire-water was filed as the
  magistracy's alone while FR-008 requires it of the shrine - a check now declares every type it
  applies to, and fire-water declares both. (3) One Decisions row carried a class outside the four -
  now `accurate`, the cost and the ruling in Why. (4) The one-shot labels named one method for three
  families of figure and sat in table header cells - now labeled by family (source-measured,
  converted, the project's own drawn value) in prose or a final table row. The reviewer's aside on
  knob 3 (dedication is a deferred choice, not a knob with values) is carried to the plan: the
  exemplar takes a dedication from the village's clan patron Fortunes, the record's town rule.
- Round 2 (2026-09-19, `spec-fidelity-verify`, Opus, on the diff 5ad5fc83..31d8436c): all four items RESOLVED; FAITHFUL. The reviewer re-derived the three label claims (the record's drawn hall and farmhouse values, the Kaie-ji band) and found them sound.
