# Feature 183 - a "deviation" is the setting differing from history; a "map drawing convention" is a glyph drawn for the eye

**Status**: FAITHFUL (`spec-fidelity`, round 5 of 5) - cleared for implementation (constitution XVI).
Five rounds, every one smaller than the last and none reopening an earlier item: round 1 found that
`deviation` was in live use as an evidence token in the research (FR-012 had said "untouched") and that
FR-005 had no branch for a silent record; round 2 that the sweep stopped at `research/` while the rule
docs and code pointers said the same word, plus a fourth site to adjudicate; round 3 that the list was
still transcribed rather than measured, and that the road rounding had been classed a convention on a
criterion the GM never gave (D6, withdrawn and reversed); round 4 that a filtered grep had dropped five
hits, one of them the hover highlight's own "class DEVIATION" (D7); round 5 re-measured the 71-hit census
and found the partition total. The recurring lesson is written into FR-012: the census is DERIVED by the
grep, never enumerated by hand - four hand-written drafts were each short.
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessors**: constitution XII's three-way classification (accurate / deliberate deviation / guess, GM
2026-08-26); feature 156 (the presumption of accuracy - a modal announces liberties, not accuracy)

## Summary

The GM has instituted a WORDING RULE: the record and the modals must distinguish

- a **deviation** - *"our fictional setting being different from the actual history and historical places
  it is based on"* - from
- a **map drawing convention** - *"rendering glyphs on a map which are differently scaled or differently
  colored than what the features would be in order to make the map more readable and legible to human
  eyes."*

Today both are filed under one label, `deviation`, and a modal opens on both with *"This is a deliberate
deviation - ..."*. The GM's example is the bund beans: the bead color is a drawing convention, and the
modal should say instead, in the GM's form, *"Note: we have rendered the bund beans as larger and darker
in color than they actually are, in order to make them visible on the map at this scale. <More
information about the actual size and color goes here.>"*

So: a fourth class, `convention`, joins the classification; the classes whose "deviation" is a matter of
scale or color move to it and their notes are rewritten in the GM's form, each ending with the real size
or color from the record; `deviation` keeps only what the setting does differently from history; and the
rule is written where the classification is defined.

## Functional requirements

### The vocabulary

- **FR-001** `classes.Label` gains a fourth value, `convention`, meaning a map drawing convention as the GM
  defined it: a glyph drawn at a different SCALE or a different COLOR than the feature would have, so the
  map reads to a human eye. `deviation` narrows to the GM's definition: the fictional setting differing
  from the history it is based on (Legend of the Five Rings canon; a ruling of the GM's about their world).
  `accurate` and `guess` are unchanged.
- **FR-002** A `convention` class is ANNOUNCED (feature 156's `ANNOUNCED` set gains it): its modal opens
  with the note, led by *"Note: "* - the GM's form. `label_phrase("convention")` is *"a map drawing
  convention"*. A `deviation` still opens with *"This is a deliberate deviation - ..."*.
- **FR-003** Every `convention` class's `label_note` MUST be written in the GM's form: it begins *"we have
  rendered <the feature> ..."* or *"we have drawn ..."*, states what differs (larger, darker, symbolic),
  states the purpose (*"in order to ..."*, so the map can be read at this scale), and then gives the
  actual size and/or color from the record, with the drawn figure beside it so a reader can compare -
  or, where the record was searched and is silent on a figure, says so in so many words and gives what
  was read (FR-005's silent branch; the well's curb width and the bean's spread are the two cases). A
  test pins the form on every convention class: the opening words, the purpose clause, and either a
  figure or the words "not found".

### The reclassification

- **FR-004** Of the seven classes labeled `deviation` today, the SIX whose departure is one of scale or
  color become `convention`: household shrine (a 1.3 ft stone drawn at 6 x 6 ft), homestead bamboo and
  shared bamboo grove (culms inches across drawn as a stand-level glyph), bund beans (bead size and
  color), stream (drawn width is rank, not the real width), well (the wellhead drawn larger than true
  size). The seventh, the grave island, stays a `deviation`: the in-field grave is drawn where the
  record would put the dead on the slope, at a rate the GM approved - the setting differing from history,
  nothing to do with the eye.
- **FR-005** Each of the six notes MUST carry the real figure. Where the record already holds it (the
  shrine's 40 cm stone; a culm a few inches across; a creek about two meters wide against a ditch), the
  note reads it from there. Where the record does NOT hold it - the soybean plant's size and foliage color
  behind the bund beans; the true size of a well's curb - this feature runs the research pass first
  (constitution XII: a guess is the last resort), records the finding in `research/` with its sources,
  and only then writes the note. A note MUST NOT state a size or color the record does not carry.
  **Where the pass comes back silent on a figure, the note says so in so many words** - "its width was
  not found" - and gives what WAS read beside it; the class stays a `convention` (the convention is a
  fact about the drawing whatever the record says about the thing), and the research entry records the
  silence as a NOT-FOUND with the pages searched. This branch is already exercised: the well pass read
  the shaft's meter and the well house's form, and found no width for the curb frame; the soybean pass
  read the height and the leaf color, and found no spread. Neither note may compare the glyph to a
  figure nobody read.
- **FR-006** The `accurate` classes' caveats (feature 156's "On the drawing: ..." liberties) are NOT
  relabeled by this feature. Many of them ARE drawing conventions (a derived width band, a calibrated row
  pitch) and some are guesses at a proportion; sorting them is a second pass and the GM's example was
  the LEAD sentence of a deviation-labeled class. Recorded as D2 so it is a decision, not an omission.

### Where the rule is written

- **FR-007** The constitution's Principle XII list of *"THREE things"* becomes FOUR, with the GM's two
  definitions verbatim, and *"legibility (the well)"* moves out of the deviation item into the new one.
  MINOR bump (2.16.0 -> 2.17.0, an existing principle materially expanded, as 2.1.0 wrote the matrix in),
  a Sync Impact Report entry quoting the GM, the footer, and the dependent artifacts listed.
- **FR-008** The dependent statements of the three-way rule are updated to four: the root `CLAUDE.md`
  "WHAT THE RECORD IS FOR" bullet (which today files *"legibility - the oversized well"* under deviation),
  `interactive/CLAUDE.md`'s presumption-of-accuracy table and intro, `SKILL.md` at BOTH its sites (the
  "What the record is for" paragraph at `:28`/`:35`, which states the three labels twice, and the
  `finish()` bullet at `:223`), `research/CLAUDE.md` (a paragraph stating the four labels and the GM's
  rule). `research/README.md`
  states the three labels at its line 27 and is the GM's to edit (constitution XVII) - this feature
  reports it as the one statement left saying three.
- **FR-009** Tests: `test_classes.py` admits the fourth label and pins the GM's form on every convention
  note; the browser test's label-text check admits *"Note: we have"*; the presumption-of-accuracy tests
  keep their meaning (an accurate class announces nothing).
- **FR-010** The SVG and the PNG are untouched (feature 134 FR-010). The page's `data-label` carries the
  new value; nothing else about the page changes.

### What this feature does not do

- **FR-011** It changes no glyph, size or color on any map - only how the record describes them.
- **FR-012** The `**Evidence:**` vocabulary keeps `liberty` as the class for a disclosed departure of
  either kind. **But every other statement of these decisions is a description too** (the GM:
  *"distinguish in our descriptions"*; since feature 180 a modal's references send the reader straight to
  the research entries), and constitution XII records each decision in three layers - the finding in
  `research/`, the rule in `settlements/`, the pointer at the point of change - to which this repository
  adds the pool's `.notes.md` journals and test docstrings. **The obligation is DERIVED, not listed:**
  for every decision this feature classes as a map drawing convention, EVERY surviving occurrence of
  "deviation" that describes that decision, in any of those layers, MUST say `convention` / "a map
  drawing convention". The implementation confirms completeness with a grep over the whole skill tree
  (`grep -rniI deviation research settlements l7r pool tests SKILL.md`), not against the list below.
  Three hand-written drafts of this list were each short by several sites; a roster that restates what
  the tree declares is derived (constitution X clause 14).

  The census as MEASURED on 2026-09-05 by that grep - **71 hits in 30 files**, rendered `.html` excluded
  (it is regenerated) - every hit adjudicated into one of the four groups below, and a fifth grep after
  the round-4 review (which found five hits a filtered first grep had dropped: an exclusion of the word
  "specs/" swallowed `page.css:4`, and a 230-character cut hid three more) confirms the partition is
  total:
  - **Reworded to `convention`** - the six reclassified classes' other layers: `research/homesteads.md:708`
    and `settlements/homesteads.md:137` (the shrine; the persimmon's vermilion and fruit dots ride in the
    same sentence and are a drawing convention on a `guess`-labeled class - the sentence is reworded for
    both, the persimmon's label is untouched), `farm_fixtures.py:31`, `inashiro.notes.md:1408`;
    `research/vegetation.md:326` and `:349` (its `Labels:` line, a standing statement of the modal class),
    `settlements/vegetation.md:82`, `homestead_parts/stands.py:19`, `inashiro.notes.md:1364` (the two
    bamboos); `tests/settlement/test_water_width_ladder.py:41` (*"Absolute widths are a legibility
    deviation"* - the stream).
  - **Reworded to `convention`** - legibility exaggerations that are not a class of the hamlet vocabulary
    but describe a drawing the same way: `research/buildings.md:79` and `:87` (the 3 ft compound wall
    drawn thicker so the stroke reads; `:87`'s *"Class for the HTML modal: deviation"* is a standing
    instruction to a future Mode A class and MUST say `convention`); `research/water.md:512`, `:576`
    (the drain drawn steep so its flow reads) and `:719` (*"a legibility deviation"* as a term of art);
    `inashiro.notes.md:1217` (the same drain grade); `settlement/fields/features.py:190` (the grave
    island's mound drawn OVER the paddy tiling rather than carved out of it - a drawing simplification;
    the class itself stays a deviation, see below); `interactive/assets/page.css:4` (the HOVER HIGHLIGHT -
    *"class DEVIATION (specs/134 research.md R2)"*, a saturated gold chosen so the lit class reads
    against every fill on the map: a color chosen for the eye, and the comment's own *"A UI affordance,
    not a claim about the world"* is what makes it a convention and not a deviation - D7).
  - **Staying a `deviation`** - the setting differing from history: `research/archetypes.md:123` and
    `:133` (the 6:4 pond-to-dike regional reading), `:217` and `:226` (*"a hamlet has no headman of its
    own" is CANON*), `research/SOURCES.md:1954` and `tests/interactive/test_place.py:304` (the same
    headman canon, in a source's Used-for line and a test docstring), `research/cities/capitals.md:532`
    and `:559` (the setting's 30 ft trunk road for the historical 29.5 - D6); the grave island class.
  - **Ordinary English, untouched**: statistical and geometric uses (`research/homesteads.md:65`,
    `homestead_parts/yards.py:83`, `:98` and `:109`, `hamletgen/ways/serve.py:100`, `fields/comb.py:567`,
    `tests/settlement/test_homestead_parts.py:482`), *"Deviation comes from TERRAIN"*
    (`capitals.md:349`), *"a deviation carries its reason in writing"* (`:837`), *"Deviation noted"*
    (`research/urban-features.md:35`), `settlements/archetypes.md:66`,
    `pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.notes.md:69` (*"the option-(c) deviation
    story"*, a Mode A staffing variant).
  - **Statements of the three-way RULE** (FR-007/FR-008/FR-009, not this requirement): `classes.py`,
    `interactive/CLAUDE.md`, `SKILL.md`, `tests/interactive/test_classes.py`, `test_page_browser.py`,
    `tests/gate/test_map_vocabulary.py:44` (which also states three and joins FR-009),
    `interactive/assets/page.js:114` (*"a deviation or a guess still leads with its liberty"* - the
    ANNOUNCED set becomes three, so the comment joins FR-009), the pool's rendered `.html` (regenerated).
  No finding, source or figure changes anywhere - the word does. Earlier drafts said the entries were
  untouched (round 1), then named four sites (round 2), then eight (round 3), then a filtered grep short
  by five (round 4); this one is the unfiltered grep's output, and the implementation re-runs it before
  ticking T04a. Since feature 181 the two assets are engine content, so this feature's route is GATED
  either way (`classes.py` already makes it so).

## Decisions Recorded

- **D1 - a fourth LABEL, not a flag on `deviation`.** The GM asked that the two be distinguished "in our
  descriptions"; a label is what the page, the tests and the constitution already key on, so a new label
  makes the distinction enforceable (a test can pin the form of every convention note) where a flag or a
  wording habit could not. It also keeps the constitution's classification a single list.
- **D2 - the accurate classes' caveats are left for a second pass** (FR-006). Thirty-one classes carry a
  caveat; sorting each into convention / guess / derived is real work with its own review, and doing it
  silently inside a feature about the LEAD sentence would be the quiet widening Principle XVI forbids.
  Cost: until that pass, a reader of the well's modal sees the new form and a reader of the perimeter
  dike's caveat sees the old "On the drawing:" register. Reported to the GM rather than decided.
- **D3 - the grave island stays a deviation.** It is drawn where the rice-south record would NOT put it,
  at a rate the GM approved, because the GM likes both looks in their world - that is the setting
  differing from history, exactly the GM's definition. Nothing about it is scale or color.
- **D4 - "Note: " is the whole of the lead-in for a convention.** The GM's example puts the note straight
  after "Note:"; no "This is a map drawing convention -" preamble is added, because the sentence that
  follows says so in plain words ("we have rendered ... in order to make them visible").
- **D6 - the trunk road's rounding STAYS a deviation.** `capitals.md:559` records that the setting's
  trunk road IS 30 ft (`ground.py` `ROAD_W_FT`), rounded from the historical 29.5 ft to the "about
  thirty feet" the GM asked for, and the glyph draws it at 30 ft. Nothing is scaled or colored for the
  eye; what differs from history is the setting's own figure - the GM's definition of a deviation, at a
  trivial magnitude. An earlier draft of this decision called it a convention by inventing a criterion
  ("the picture is different" against "the world is different") the GM never gave, to carry a case it
  had already conceded was neither of the two named things; the round-3 review caught that as
  completing the GM's thought. Same ruling as `archetypes.md:123`, on the same ground (not scale or
  color), and `:559`'s existing text - *"accurate (the width), deviation (the half-foot rounding)"* -
  is already correct under the GM's split and is not edited.
- **D7 - the hover highlight is a map drawing convention.** `page.css:4` calls the gold highlight
  *"class DEVIATION"*, citing feature 134's research R2. It is a color chosen so the lit class reads
  against every fill on the map - the GM's definition of a convention, word for word ("differently
  colored ... in order to make the map more readable") - and the comment's own next clause, *"A UI
  affordance, not a claim about the world"*, is the reason it is NOT a deviation: a deviation is the
  world differing from history, and the highlight says nothing about the world. The comment is reworded;
  feature 134's research record, an account of what was decided at the time, is not.
- **D5 - two research passes are run rather than two guesses written.** The soybean plant and the well
  curb are physical questions (how big, what color) and the GM's template asks for the actual figures.
  Constitution XII: a guess is the last resort and a physical task carries its three boxes.
