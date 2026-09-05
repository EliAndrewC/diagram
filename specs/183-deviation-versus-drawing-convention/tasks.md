# Tasks - feature 183

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 5). Request: [`request.md`](request.md).

## The vocabulary

- [x] T01 FR-001/FR-002: `classes.py` - `Label` gains `convention`; `ANNOUNCED`, `_LABEL_WORDS`, `lead_sentence` ("Note: " + the note)
      research: rendering
      verify: DONE. `Label` is four; `ANNOUNCED` = {deviation, convention, guess}; `_LABEL_WORDS["convention"]` = "a map drawing convention"; `lead_sentence("convention", note)` = `CONVENTION_LEAD` ("Note: ") + note. Pinned in `test_classes.py`
## The research the notes need (constitution XII - a guess is the last resort)

- [x] T02 FR-005: the soybean plant - height, spread, foliage color - and azemame on the bund; a new `research/fields.md` section with sources in `SOURCES.md`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
      verify: DONE. Reader dispatched 2026-09-05: READ - height 50-125 cm (Wikipedia, Soybean), erect and bushy with medium-green leaflets (cropfarming.org, the one page read stating color), azemame sown on the bund and harvested with the rice (Nara National Research Institute, Asuka); NOT-FOUND - plant spread (Iowa State row-spacing page gives closure timing, not width). Recorded as `research/fields.md` "What a bund bean actually looks like", keys `nabunken-azemame`, `wikipedia-soybean`, `cropfarming-soybeans`; the SUMMARY-ONLY snippets are named and unused
- [x] T03 FR-005: the well's true size - the curb (井戸枠) and the hand-dug shaft - against the drawn head; recorded in `research/urban-features.md` under the wells entry, sources registered
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
      verify: DONE. Reader dispatched 2026-09-05: READ - the hand-dug shaft is about 1 m across (Saijo City water museum), the well house is posts and a roof (Digital Daijisen via kotobank); NOT-FOUND - the curb frame's width (three pages define 井桁, none sizes it) and the well house's prevalence. Recorded in `research/urban-features.md` under the wells entry, keys `saijo-mizu-rekishikan`, `kotobank-idoyakata`; the code comment's "~3-4 ft curb" is named as an unsourced estimate
## The reclassification

- [x] T04 FR-003/FR-004/FR-005: six classes to `convention` with notes in the GM's form carrying the real figures; the grave island stays a `deviation`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
      verify: DONE. Six classes to `convention`, each note in the GM's form: shrine (6 x 6 ft for a 40 cm stone), two bamboos (culm strokes on a 7 ft grid for culms inches across), bund beans (3 ft beads in deep pine green; the plant 50-125 cm, medium green; spread "not found"), stream (width by rank; a creek ~2 m), well (~19 ft head for a ~1 m shaft; curb width "not found"). Grave island stays a deviation. Research: the record answers the shrine, bamboo and stream (pointers in each note); T02/T03 answer the beans and the well. The bund beans and well entries cite the new keys; the beans entry names the new section, so its modal gains a fourth question
- [x] T04a FR-012: every surviving "deviation" that describes a reclassified or legibility decision says `convention` - the measured census in FR-012 (shrine x4, bamboo x5, stream x1, compound wall x2, drain grade x4, grave mound drawing x1); the setting-vs-history sites stay; completeness confirmed by the grep, not the list
      research: rendering
      verify: DONE by script with asserted anchors, 21 sites: shrine x4 (`research/homesteads.md:708`, `settlements/homesteads.md:137`, `farm_fixtures.py:31`, `inashiro.notes.md:1408`), bamboo x5 (`research/vegetation.md:326,349`, `settlements/vegetation.md:82`, `stands.py:19`, `inashiro.notes.md:1364`), stream x1 (`test_water_width_ladder.py:41`), wall x3 (`buildings.md:79,87` incl. the "Class for the HTML modal" line), drain x4 (`water.md:512,576,719`, `inashiro.notes.md:1217`), grave mound drawing x1 (`features.py:190`), highlight x1 (`page.css:4`), rule statement x1 (`page.js:114`). Re-grep after: "deviation for legibility" / "legibility deviation" / "recorded as a deviation" survive only in `research/CLAUDE.md`'s sentence saying they were renamed. archetypes, capitals, the headman canon untouched
## Where the rule is written

- [x] T05 FR-007: the constitution - Principle XII's list of three becomes four, 2.16.0 -> 2.17.0, Sync Impact Report, footer
      research: rendering
      verify: DONE. Principle XII's live list is four items with the GM's two definitions verbatim and their examples; "legibility (the well)" moved out of the deviation item; Sync Impact Report entry for 2.17.0 quoting the GM and listing dependents; footer 2.17.0 / 2026-09-05. `:123` (the 2.5.0 PRIOR record) untouched; a duplicate header line my insertion created was removed
- [x] T06 FR-008: root `CLAUDE.md`, `interactive/CLAUDE.md`, `SKILL.md`, `research/CLAUDE.md`; `research/README.md` reported as the GM's to update
      research: rendering
      verify: DONE. Root `CLAUDE.md` bullet (four classes, the well and the beads now under convention, the GM quoted), `interactive/CLAUDE.md` (intro, table row for `convention`, "three-way" corrected), `SKILL.md:28`, `:35`, `:223`, `tests/gate/test_map_vocabulary.py:44`, `research/CLAUDE.md` new section. `research/README.md:27` still says three - the GM's to edit (constitution XVII)
## Closing

- [ ] T07 FR-009/FR-010: regenerate the reference hamlet's page and read the bund beans' and the well's modals; `make done` green; the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (no drawn ink moved)
