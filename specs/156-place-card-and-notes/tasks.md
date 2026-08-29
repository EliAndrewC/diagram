# Tasks: the place card, and per-map notes the page can read

**Feature**: 156-place-card-and-notes | **Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md)

Most of this feature is `research: rendering` - what a modal prints and in what order, and a parser
for a markdown block. Four tasks are `research: physical`, because the place card makes claims about
how a settlement is organized and populated: those carry the three boxes. The research pass ran
BEFORE the spec was finished (`source-reader`, 2026-08-29) and its result changed the spec - the
historical record ranks no settlement form by frequency and does not support "a hamlet has no
headman" as a flat rule, so the page rests those two on the GM's own canon and DISCLOSES the
simplification. The pass is recorded in [`research.md`](research.md).

## Phase 1 - the presumption of accuracy (US1)

- [x] **T01** `FeatureClass.caveat: str = ""` in `classes.py`, with the docstring saying what belongs
      in it (the liberty an accurate class discloses) and what does not (the accuracy claim in other
      words). `label` and `label_note` are unchanged - the record keeps both halves.
      `research: rendering`
- [x] **T02** Fill `caveat` for every `accurate` class from its own `label_note`, taking ONLY the
      liberty-disclosing clause and leaving `caveat=""` where the note merely says the feature is
      read from the record. `deviation` and `guess` classes keep `caveat=""` - their lead already
      carries the liberty. `research: rendering`
- [x] **T03** `page.py` `explanations()` emits `lead` (empty for `accurate`, "This is a deliberate
      deviation - ..." / "This is a guess - ..." otherwise) and `caveat`; `label` stays in the blob
      for `data-label`. `research: rendering`
- [x] **T04** `page.js` fills `#x-label` from `lead` and hides it when empty; a new `#x-caveat`
      section renders after `#x-why`, styled as a quiet aside in `page.css`. `research: rendering`
- [x] **T05** Tests: no `accurate` class's rendered modal contains "historically accurate" or a
      paraphrase; every `deviation`/`guess` still leads with its liberty; a class with a caveat shows
      it after the why; a class without one shows no caveat element. A registry test asserts every
      `accurate` class's `caveat` is either empty or a substring of its `label_note`, so the two
      cannot drift. `research: rendering`

## Phase 2 - the notes reader (US3)

- [x] **T06** `interactive/notes.py`: `read_map_notes(path) -> MapNotes(place, features)`. Pure
      functions over strings - `_section(text, heading)`, `_bullets(block)` - lifted to module level
      so the tests call them with plain strings (the closure rule, GM 2026-08-28).
      `research: rendering`
- [x] **T07** Resilience, each a test: no file; unreadable file; no `## Map notes` heading; the
      heading present but empty; `### Place` without `### Features` and the reverse; a bullet with no
      colon; an empty value; a duplicate key; a truncated final line; a wrapped continuation line; a
      nested list; an HTML comment inside the block; text containing `<` and `&`. Every one returns
      a usable result and never raises. `research: rendering`
- [x] **T08** `page.py` reads `<base>.notes.md` beside the output when writing the page, drops
      annotations for keys the registry does not know or the map does not draw, and emits the rest
      as `"on_this_map"` per class. `page.js` renders it as a distinct "On this map" section so a
      local fact is never read as a general one. `research: rendering`
- [x] **T09** The convention is documented where an author will find it: a section in
      `interactive/CLAUDE.md` (the key list, the two subsections, the failure behavior) and a pointer
      from `settlements.md`. `research: rendering`

## Phase 3 - the place card (US2)

- [x] **T10** `interactive/place.py`: `place_card(meta, manifest, notes, present) -> dict | None`.
      Pure. Assembles kind, size, crops and location as separate strings so each can be omitted
      independently. `research: physical` - the settlement kinds it describes
      - [x] research pass (the `source-reader` run of 2026-08-29, before the spec was finished; specs/156/research.md)  - [x] source-reader confirmed (that run: READ, SUMMARY-ONLY, CONTRADICTED and NOT-FOUND per claim)  - [x] recorded and cited (research/archetypes.md 'What a settlement IS...'; 8 keys in research/SOURCES.md)
- [x] **T11** The crop table: class key -> (wet | dry | dike | water, display name), covering the
      paddy, the four dry crops, the four crop dikes, the vegetable ground and the fish pond. Derived
      from the CLASSES PRESENT, never from a per-map list, so Kuwabata (no dry plots, four dike
      crops) describes itself with no per-map code. A test asserts every key is a real class.
      `research: physical` - which crops a map grows
      - [x] research pass (the `source-reader` run of 2026-08-29, before the spec was finished; specs/156/research.md)  - [x] source-reader confirmed (that run: READ, SUMMARY-ONLY, CONTRADICTED and NOT-FOUND per claim)  - [x] recorded and cited (research/archetypes.md 'What a settlement IS...'; 8 keys in research/SOURCES.md)
- [x] **T12** The size sentence: `~N farmhouses` from the drawn house count and `population ~N` from
      `meta.population` where the tier records one, else `~5 x meta.households`; both tilde-marked,
      both omitted when unavailable. `research: physical` - the population model
      - [x] research pass (the `source-reader` run of 2026-08-29, before the spec was finished; specs/156/research.md)  - [x] source-reader confirmed (that run: READ, SUMMARY-ONLY, CONTRADICTED and NOT-FOUND per claim)  - [x] recorded and cited (research/archetypes.md 'What a settlement IS...'; 8 keys in research/SOURCES.md)
- [x] **T13** `finish.py` `title()` tags the placard and its text `cls="place"`; the scale bar keeps
      `cls="-"`. `NOT_HIGHLIGHTED_RULINGS` keeps the 2026-08-27 row and records the overturning
      beside it. `research: rendering`
- [x] **T14** `page.js` opens the place card from the placard like any class, with the settlement's
      name as the heading, no label line, and no references link when there are none.
      `research: rendering`
- [x] **T15** The `village lane` default: its `why` gains the sentence, with the GM's reason for the
      class's name at the point of change; `place.py` supplies the district's name when the notes
      record one. `research: physical` - where a hamlet's lanes lead
      - [x] research pass (the `source-reader` run of 2026-08-29, before the spec was finished; specs/156/research.md)  - [x] source-reader confirmed (that run: READ, SUMMARY-ONLY, CONTRADICTED and NOT-FOUND per claim)  - [x] recorded and cited (research/archetypes.md 'What a settlement IS...'; 8 keys in research/SOURCES.md)
- [x] **T16** Tests: the card on a hamlet, on a village, on a town and on a map with no notes at all;
      the tilde on both figures; no crop named that the map does not draw; each authored fact omitted
      cleanly when absent.  `research: rendering`

## Phase 4 - the pool's geography (US4)

- [x] **T17** The research entry: `research/archetypes.md` gains the settlement-kind entry with its
      `**Sources:**` line, and `research/SOURCES.md` the new keys with URLs. It records BOTH what the
      historical pass found and what it could not find, and names the two places where the setting
      overrules history. `research: physical`
      - [x] research pass (the `source-reader` run of 2026-08-29, before the spec was finished; specs/156/research.md)  - [x] source-reader confirmed (that run: READ, SUMMARY-ONLY, CONTRADICTED and NOT-FOUND per claim)  - [x] recorded and cited (research/archetypes.md 'What a settlement IS...'; 8 keys in research/SOURCES.md)
- [x] **T18** Akagahara's and Ikegami's `## Map notes` blocks: Hoshigaoka east / north-east, the
      Imperial road directly south, quoting the GM. `research: rendering`
- [x] **T19** Hoshigaoka's block: north of the Imperial road, Hayakawa county, the town of Hayakawa
      further south. `research: rendering`
- [x] **T20** A block for every remaining hamlet, each district drawn from gm-assistant's
      `place-names/pool.jsonl` with its kanji and meaning, each labeled INVENTED, and the direction
      taken from the map's own connector track where it draws one. `research: rendering`
- [x] **T21** Inashiro's block, including the village-lane annotation the GM asked for by name.
      `research: rendering`

## Phase 5 - verification

- [x] **T22** The reference hamlet, then the tier. `make maps` cannot reach the pool: it halts at
      tripwire seed 37 (`paddy_bunds_do_not_stagger`), red before this feature and ledgered in
      `specs/153-highlight-legibility/research.md` R9. So the five scripted maps were regenerated
      directly, which is also what cleared three stale clone-side renders. **The result is SC-007
      exactly**: Inashiro, Kashikawa and Sawada byte-identical, Mizuguchi and Kuwabata differing in
      `ink_classes` alone (`-` 10 -> 7, `place` 3). No map's geometry moved. `research: rendering`
- [x] **T23** `make verify` - the gate and the independent `settlement-review` together (feature 151)
      - green, with every finding either fixed or recorded. `research: rendering`
- [x] **T24** The review ledger row in `docs/review-ledger.md`, and this feature's entry in
      `dev/reviews.md` if the pass changed doctrine. `research: rendering`

## Found while doing it (constitution XIV)

- [x] **T25** `scripts/review-gate.sh` accepted a MENTION where it wanted a VERDICT: a bare
      `grep FAITHFUL` passed a spec whose only occurrence was "NOT FAITHFUL" - one a reviewer had
      REJECTED - and passed prose that merely discusses the word. Found by this feature's own round-2
      review, on the guard that gates this feature's own push. Fixed: negated lines are dropped and the
      occurrence must sit on a line naming the review. Measured against all 69 specs in the clone, none
      moves; `scripts/test-review-gate.sh` gains four cases (the two holes, the two house formats).
      `research: rendering`
- [x] **T26** the glossary defined two terms no modal would have shown any more, because `glossary_for`
      scanned `label_note`, which feature 156 stops rendering. It reads what the page RENDERS now
      (`what`, `why`, `lead`, `caveat`); `magariya` returned with the byre's caveat, and `satoyama`
      is named in the woodland commons' own explanation, where it belonged. `research: rendering`

## The GM's follow-up rulings, 2026-08-29 (verbatim in [`request.md`](request.md))

- [x] **T27** A drawn count is EXACT and carries no tilde; only the population keeps one. The GM:
      *"that actually IS an exact map feature - the number of farmhouses listed should be whatever is
      actually displayed on the map itself for hamlets and villages."* `research: rendering`
- [x] **T28** A town and a city count their NON-FARM dwellings - enumerated, exact, all drawn - and
      state no farmhouse count, because the countryside around them is deliberately not drawn whole.
      Implemented by excluding houses inside a drawn `agricultural_district` quarter (Tango: 13 of 273),
      with the manifest's lack of a per-dwelling farm flag recorded as the limit in `dwellings_shown`.
      `research: rendering`
- [x] **T29** Each tier says what its population figure COUNTS: a town's takes in the surrounding
      farmers, a provincial city's takes in the samurai country estates but not the farmers, whose
      village districts and counties the Imperial census counts separately. Recorded in
      `settlements.md` as well, since it is tier doctrine and not a page detail.
      `research: physical` - an Imperial census convention
      - [x] research pass (the GM's ruling IS the record here - a setting convention, not a historical
        question; `l7r.md` "The Median Domain" for the tier populations it applies to)  - [x] source-reader
        confirmed (n/a - nothing historical is claimed; the card states the convention as the setting's)
        - [x] recorded and cited (`settlements.md`, the spec's Decisions Recorded, `place.py` `population_note`)

## From `settlement-review`, round 1 on Inashiro (2026-08-29)

Four errors, four questionable, eleven nitpicks. Every error and every questionable is fixed.

- [x] **T30** (error 1) The place card's basis was rendered under "On the drawing:" - a sourcing
      disclosure labeled as a drawing note, because `page.js` prepended one lead-in to every caveat.
      The lead-in belongs to the ENTRY now: `CAVEAT_LEAD` for a class, `BASIS_LEAD` ("What this rests
      on: ") for the card, and the renderer prints what it is given. `research: rendering`
- [x] **T31** (error 2) The lane default composed its direction from `district direction`, so
      Akagahara and Ikegami would have said "the lanes lead northeast/east to Hoshigaoka" while their
      connectors run SOUTH to the Imperial road. The direction a district LIES in is not the direction
      its track LEAVES in, and a route off the sheet is not something the map knows - the default names
      the destination only, and both maps now carry the true sentence in their own `### Features`.
      `research: rendering`
- [x] **T32** (error 3) Moritono's recorded direction was north-west against a track running north
      (350.5 deg end-to-end), and the same re-measurement moved Kashikawa from north-east to east. The
      original figures came from cluster-centroid-to-far-end, which is not the track's own bearing.
      `research: rendering`
- [x] **T33** (error 4, and nitpick 7) Three caveats were not liberties: `bund` ("the drawn stroke is
      at true size") and `notice board` ("drawn at its true 12 x 5 ft") are the accuracy claim in other
      words, under a heading that promises a disclosure; `windbreak`'s discloses nothing either way.
      All three join the no-caveat list, and a test now rejects the true-size shape specifically - it
      is the one a later editor is likeliest to re-open. `research: rendering`
- [x] **T34** (questionable 1) The basis block had grown longer than the card, burying the one fact
      the GM asked about by name. The tier ranking moved into the body; the basis keeps only the
      disclosure. `research: rendering`
- [x] **T35** (questionable 2) A village card could state a farmhouse count and a population that do
      not divide - Hikari no Sato draws 66 houses against 70 households, which `settlements.md`
      permits. The households are named when the two differ. `research: rendering`
- [x] **T36** (questionable 3) "district headman" was a coinage; `l7r.md`'s term is "village
      headsman". `research: rendering`
- [x] **T37** (questionable 4) "An Imperial road runs directly south" states the road's course where
      the GM's fact is its position. It passes south OF HERE. `research: rendering`
- [x] **T38** (nitpicks 1, 2, 3, 4, 5, 6, 8, 9, 11) The unregistered-class stub moved to the post-154
      contract and got its announcement back; `PLACE_KEYS` is bound by a guard that censuses what the
      card actually reads; the glossary scans `on_this_map`; northeast/northwest in the notes blocks;
      two caveats stopped addressing the developer ("the entry itself advises"); the copse's pronoun
      reaches its noun; the village lane's `why` lost a block-caps sentence and a dated quote about
      our own vocabulary; the lane line names the connector rather than all nine lanes; and two
      British spellings in `inashiro.notes.md` prose. `research: rendering`

## From `settlement-review`, round 2 (Kashikawa and Sawada, 2026-08-29)

- [x] **T39** (error) The card said a hamlet has "no shrine" on a page carrying a `household shrine`
      class, and "no burial ground" on maps drawing a `grave island` - both true, both reading as
      contradictions, and already live on the reference map. Reworded at the tier, so every hamlet is
      fixed at once: "no VILLAGE shrine ... and no burial ground OF ITS OWN", with the hokora and the
      grave mound named so a reader who clicks either is not left with a collision. `research: rendering`
- [x] **T40** (questionable) Kashikawa's invented district was Kawakami, 川上 "upstream", recorded
      lying 54 degrees off DOWNSTREAM of a hamlet whose own name is 樫川, "oak river" - the same water.
      The bearing is measured and cannot move, so the NAME did: Hirose, 広瀬 "broad rapids", which is
      what a reach downstream is. `research: rendering`
- [x] **T41** (questionable) Whether the page should disclose that a district name is invented.
      ACCEPTED as is - the disclosure stays in the notes, where the GM reads it, and off the card. The
      three alternatives are priced in research R7, along with what the acceptance costs and who chose.
      `research: rendering`
- [x] **T42** (error, handed on) The stale-render guard cannot see a manifest that has moved past its
      render, because it compares PNG to SVG and those are written together. The invariant that closes
      it (`viewBox == meta.view`) is measured and recorded in research R6, and NOT applied here:
      feature 155 owns that file and is in flight in another session. `research: rendering`
- [x] **T43** (error, non-issue for the push) The clone's kashikawa/sawada renders are from an earlier
      roll, and those maps' pages predate this feature. Both are clone-local: the pool's `.svg`, `.png`
      and `.html` are gitignored and rebuilt by render-sync from main's own tip, so what the GM browses
      is generated fresh after the push. Recorded in research R6 rather than papered over.
      `research: rendering`
- [x] **T44** The number claim collided: a peer session's `154-kosatsuba-placement-knob` reached main
      first and `155-mains-red-floor` behind it, so this feature renumbered 154 -> 156 and every
      reference moved with it (32 files). `research: rendering`

## From `settlement-review`, round 3 - the verification pass (2026-08-29)

A pass whose whole job was to check that round 1's and round 2's fixes fired. Four of the seven did
exactly what the commit claimed; three did not, and one of those was the GM's own ruling implemented
backwards.

- [x] **T45** (error 1, the serious one) `dwellings_shown` counted `houses` at town and city scale -
      but `houses` IS the farm ring at those tiers, so the GM's "state the non-farm dwellings, not the
      farmhouses" was implemented as "state the farmhouses". The `273 -> 260` result looked like proof
      and was 260 farmhouses. Now counts `buildings` under `DWELLING_KINDS`, the same set the capacity
      checks use, so there is one definition of a dwelling in the engine: Minami 520, Tango 583, Ubame
      82. The arithmetic is the check - Minami's 520 x 5 is its declared 2,600 exactly.
      `research: rendering`
- [x] **T46** (error 2) The town's population note asserted the GM's Imperial convention over a figure
      that means something else: every town in the pool declares the DEPICTED slice (Ubame's 590 is
      (36 + 82) x 5 exactly), and `settlements.md` has said so since before this feature. The card now
      states what its figure IS and names the larger one as not yet given; the convention is recorded
      as owed, with what implementing it costs. `research: rendering`
- [x] **T47** (error 3) The fix for the shrine collision opened another: the card put the hokora
      "beside a farmhouse door" where its own class puts it in a corner of the plot - and Sawada's sits
      46 ft from its house. The card follows the class's wording now. `research: rendering`
- [x] **T48** (error 4) The Kawakami defect had a second instance the first sweep missed: Yatsuda's
      Takadani, 高谷 "high valley", recorded on the downhill side. It is Kayano, 萱野 "reed plain",
      which claims no elevation. The rest of the pool was swept against the same standard and is clean.
      `research: rendering`
- [x] **T49** (questionable 2) The disambiguating clause was unconditional, so Mizuguchi - which draws
      neither a household shrine nor a grave island - was told about both. It is per-class and keyed on
      what is present now, the same rule the crop sentence follows. `research: rendering`
- [x] **T50** (nitpicks) Kashikawa's notes quoted a math-convention angle in a file whose neighbors
      speak compass, so it read as "north" three lines under "east"; Akagahara's "lies northeast along
      it" attached to the road rather than the district; and two pre-existing British spellings.
      `research: rendering`


## From `settlement-review`, round 4 - the second verification pass (2026-08-29)

Three of round 3's five fixes landed clean; the other two carried the same defect one tier over.

- [x] **T52** (error 1) The CITY population note asserted that the figure "takes in the samurai
      country estates", which all three city manifests deny: Minami's 520 dwellings x 5 IS its declared
      2,600, with no headroom for an undrawn household, and each city draws three estates that
      contribute nothing. The note states what its figure IS now - the households drawn inside the
      city - and the estate convention is recorded as owed rather than asserted, the same treatment
      the town's county figure already had. `research: rendering`
- [x] **T53** (error 2) "but NOT the farmers" was false on Tango, whose declared 3,000 is
      (583 dwellings + 17 IN-WALL farmhouses) x 5 - which is how the gate closes it
      (`common_04_urban_policy.py`, in-wall `houses` count too). The note names the in-wall farmhouses.
      `research: rendering`
- [x] **T54** (error 3) "That figure is the settlement as drawn" was an exact identity on Ubame and
      Hoshizora and 6.4% out on Hirameki, passing only inside the 7% tolerance. Stated as the model it
      is. Two pre-existing record defects behind it, both fixed: `settlements.md`'s spelled-out
      dwelling-kind list had gone stale by four kinds and now points at the one definition, and
      Hirameki's notes quoted the figure that list produced (156 against the engine's 166) - corrected
      with the measurement, and NOT re-declared, because which figure a town should state is the
      question the GM deferred. `research: rendering`
- [x] **T55** (questionable 1) The deferred import broke the cycle but executed all 52 modules and
      14,524 lines of the check battery on every town and city page write, for a ten-element set.
      `DWELLING_KINDS`, `BUSINESS_KINDS` and `HOUSEHOLD` moved to the leaf `l7r/diagram/dwellings.py`;
      `common_03_capacity` re-exports them, so every existing import still works and there is one
      definition with no cycle. `research: rendering`
- [x] **T56** (questionable 3) `COLLISIONS` is appended at every tier, so its clause must not talk
      about hamlets - a village that ever seats a household shrine would have been told about "the
      village shrine a hamlet does not have" two sentences after being told it has one. Tier-neutral
      now, and a test says so. `research: rendering`
- [x] **T57** (nitpicks) Kashikawa's parenthetical attributed a y-up frame to the engine, whose axes
      are 0 = east, 90 = south - dropped, leaving the compass bearing that was right all along; the
      "along it" sweep finished in both files and both places; and the doubled noun at town, city AND
      village scale ("is a town of 82 dwellings, population ~590: a county town: the lowest ...") -
      the village had it too, caught by the guard written for the other two. `research: rendering`

## From `settlement-review`, round 5 - convergence (2026-08-29)

**All six of round 4's fixes fired**, verified independently: one definition of each moved name with
identity holding through the re-export, every consumer censused and resolving, and - the measurement
that proves the point of the move - importing `interactive.place` now loads **zero** `check_village`
modules. Three residues, all in prose or in a constant, all closed:

- [x] **T58** Hirameki's correction said "the four `_large` variants"; there are three, and the fourth
      kind in the gap is `merchant_house`, which is not one. `research: rendering`
- [x] **T59** `settlements.md` said the old list "had gone stale by four kinds"; it was five. (The
      enumeration beside it was already right, which is how the count was checkable.)
      `research: rendering`
- [x] **T60** `place.py` still defined `PER_HOUSEHOLD = 5` beside the leaf it now imports - the
      household constant kept two live definitions in the very module the move was made for. It is the
      leaf's `HOUSEHOLD` now. `research: rendering`

## From `settlement-review`, round 6 - the readthrough (2026-08-29)

The pass was commissioned to answer one question no author can answer about their own page: after five
rounds of correcting errors, does it still read as something written for a player? Its verdict was that
the feature modals do and the place card did not - it had accreted into a specification of the hamlet
tier, with fine print addressed to reviewers.

- [x] **T61** The basis opened on "Two of those", which pointed at nothing a reader could see - residue
      of T34's own fix, which had moved the tier ranking out of the basis into the body and left the
      pronoun behind. Rewritten to name what rests on the setting and stop. `research: rendering`
- [x] **T62** The card defined the place by four absences, and "tax-free plot" is defined nowhere on
      the page - a player met a term and was told this place lacks it. Dropped; the two absences with
      a stated consequence stay. `research: rendering`
- [x] **T63** Where the place IS was the fourth sentence of the crop paragraph, opening on an "It"
      whose nearest nouns were "weeds" and "ground". `where_sentences` runs before `crop_sentence` now.
      `research: rendering`
- [x] **T64** Two spellings of one office in one sentence ("no headman of its own - the village
      headsman who oversees it"), and "about 1,296" hedging an exact figure. `research: rendering`
- [x] **T65** Six sentences in the class prose written for the build team, in windows a player opens -
      the same defect the GM reported originally, one layer down. The lane modal described the data
      model ("Every lane on the map is one feature, connected or not"); the farmhouse led with
      generator ordering; the footbridge cited "the spec template's own worked example"; the well
      called itself "the project's canonical example of a legibility deviation"; the household shrine
      carried ", ruled by the GM, like the oversized well"; and the hen coop told a player the GM had
      chosen a Chinese reading over Japan's, "where chickens before Meiji were timekeepers and coops
      rare" - a sentence that deletes the feature it explains. `research: rendering`
- [x] **T66** REGRESSION, mine, caught by the gate: tightening `review-gate.sh` to demand a verdict
      rather than a mention broke two fixtures in `scripts/test-sync-with-main.sh`, which wrote a bare
      `FAITHFUL` line to get past the review gate - precisely the shape the tightening rejects. The
      fixtures write a verdict line now; all 43 checks pass. `research: rendering`

## Questions for the GM (not tasks - nothing here is owed by this feature)

Both are recorded so they are not lost, and neither is a checkbox: an open task refuses a push, and
these are rulings rather than work.

**Q1 - should the presumption of accuracy extend to the DEVIATION and GUESS leads?** They open with
the provenance half before the liberty - *"This is a guess - The firewood SHED is read (Boso-no-Mura);
where the open STACK stood ... is a guess"*. `settlement-review` argues, twice, that "X is read" is
exactly the paraphrase FR-001 bars from the page and it now survives on the modals a reader opens
most; it also notes the shorthand source names in those leads go unglossed, so a player reading about
a Rokugani well meets "the Sphere/UNICEF figures". The machinery exists - the caveat is the liberty
half - and is simply not populated for announced classes. NOT DONE because the approved spec's FR-002
says those leads are "unchanged, exactly as today" and `spec-fidelity` passed that wording three
times against the GM's own request; changing it is this session carving an exception into its own
approved spec, which Principle XVI forbids. One word settles it either way.

**Q2 - should a town's population become the county figure?** The GM's ruling is that it *"includes
the nearby farmers who are counted as being part of the town, Not all of which are depicted on the
map"* - Ubame's ~1,200, not the ~590 it declares. Every town in the pool declares the depicted slice
and `settlements.md` has said so since before this feature, so the card states the smaller true thing
and names the larger as not yet given. Implementing the ruling needs the town gens to re-declare
`population` and `population_consistent_with_housing` to stop keying off it at town scale - the
towns-and-cities work the GM deferred this to.

**Q3 - the references and the modal chrome.** Not this feature's delta but measured while reviewing
it, and the largest remaining gap between what the page is and what it is for: seven farmstead
fixtures share one research entry and therefore ONE 17-source reference list, so clicking the woodpile
returns a Han pigsty latrine and three chicken-coop sources; every entry carries its own provenance
stamp (`READ 2026-08-27, source-reader`, `SUMMARY-ONLY - HTTP 403 on one attempt`); one carries a
spec-kit task number and one exists only to warn future sessions off a source; two classes advertise
"the research entry records no citation yet"; three crop modals share a verbatim-identical `why`; and
nothing on the page hints it is clickable at all. An editorial pass over feature 134's vocabulary,
worth commissioning as its own feature rather than smuggling into this one.

## The GM's rulings of 2026-08-29 (verbatim in [`request.md`](request.md))

Q1 and Q2 above are answered; a third clarification arrived with them.

- [x] **T68** (answers Q2) A town's population is **1,200**, the tier's standing county figure,
      and it takes in a farming population deliberately not drawn. The three town maps are FROZEN
      legacy exhibits, so their manifests keep the depicted slice `population_consistent_with_housing`
      keys on and the page states the real figure - `Kind.default_population`. Documented in
      `settlements.md` with what a later scripted conversion would owe. `research: rendering`
- [x] **T69** (answers Q1) The presumption of accuracy does NOT mean staying silent about a liberty
      inside an otherwise accurate feature: *"even when we are displaying something which we believe
      to be accurate, then if we had to guess or deviate from some documented source, then we should
      say so and explain why we did it."* The caveat mechanism already said so; eight of them did not
      explain WHY. Each now carries its reason, and `label_note` moved with it so the registry's
      verbatim-substring guard still holds. The deviation and guess LEADS stay as they are - the
      ruling asks for saying and explaining, which is what they do. `research: rendering`
- [x] **T70** A village IS its district and the two names are always the same, so a village page never
      states a district at all - it states its COUNTY, which every village belongs to. The shared name
      is a deliberate departure from history, documented in `l7r.md` and reviewed with the players, and
      the maps do NOT flag it. A hamlet genuinely belongs to a district with a different name and still
      says so. `research: rendering`
