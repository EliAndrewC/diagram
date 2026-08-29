# Implementation Plan: The place card, and per-map notes the page can read

**Feature**: 156 | **Spec**: [spec.md](spec.md) | **GM request**: [request.md](request.md)
**Created**: 2026-08-29

## Summary

Three changes to the HTML target (`l7r/diagram/interactive/`), plus content in the pool's
`.notes.md` files. **The drawing does not change**: the `.svg`, `.png` and `.json` of every map are
untouched except for the recorded class of the placard's ink, exactly as feature 134 promised
(spec SC-007).

1. The modal stops leading with an accuracy claim. The `accurate` label prints nothing; its recorded
   note moves to a trailing caveat. `deviation` and `guess` are unchanged.
2. The title placard becomes a clickable feature that opens a PLACE card built from the manifest
   plus the map's notes file.
3. A `## Map notes` block in `<name>.notes.md`, read by a new `interactive/notes.py`, supplies the
   place facts and per-map feature annotations. Absent, malformed or unknown - nothing is pulled in.

## Technical Context

**Language**: Python 3.14, no new dependencies (PyYAML is NOT installed and is not being added - the
block is parsed by a small deterministic markdown reader, ~60 lines, fully unit-testable with plain
strings).
**Touched**: `l7r/diagram/interactive/{page.py,classes.py,place.py,notes.py,assets/page.js,assets/page.css}`,
`l7r/diagram/settlement/finish.py` (the placard's `cls=`), `pool/*/*.notes.md`, `research/`,
`settlements/`, `tests/interactive/`.
**Verification**: `make quick` while iterating; `make verify` once at the end (the gate and the
independent settlement-review together, feature 151); the Playwright browser test in
`tests/interactive/` drives the new modal.

## Constitution Check

| Principle | How this feature satisfies it |
|---|---|
| **VI** (verify before done) | One artifact - the reference hamlet - while iterating; `make maps` once at the end; `make verify` for the gate + review pairing |
| **X** (100% coverage on pure logic) | `notes.py` and `place.py` are pure functions over strings and dicts - no settlement, no fabric list. The closure rule (GM 2026-08-28) is met by construction: every unit here is a module-level function taking plain inputs |
| **XI** (kanji triangle) | Every invented district name is taken from the project's existing stock (`gm-assistant/.claude/skills/place-names/pool.jsonl`), which carries kanji, romaji and meaning for each |
| **XII** (record the why, with sources; a guess is the last resort) | The commonest-hamlet-type claim runs the research pass FIRST (dispatched to `source-reader` before implementation). Every rendering decision lands in the spec's Decisions Recorded table and at the point of change. An invented district is labeled invented |
| **XIII** (no regressions) | Baseline taken in a detached worktree before the first engine edit |
| **XIV** (fix defects where found) | Anything the review agents surface outside the delta is fixed in this work |
| **XVI** (spec reviewed by someone else) | `spec-fidelity` against `request.md`, verdict in the spec's Review history |

## The design

### A. The presumption of accuracy

`classes.py` keeps `label` and `label_note` exactly as they are - the record is unchanged
(FR-004). `page.py`'s `explanations()` stops emitting `label_phrase` for `accurate` and instead
emits the note under a separate key, so the page's JS has no way to print the claim:

- `label == "accurate"` -> `"lead": ""`, `"caveat": <label_note>`
- otherwise -> `"lead": "This is " + label_phrase + " - " + label_note`, `"caveat": ""`

`page.js` fills `#x-label` from `lead` (hidden when empty) and a new trailing `#x-caveat` section
from `caveat`. `label` itself stays in the blob for the `data-label` attribute the browser test and
any future styling read - the classification remains machine-readable on the page (FR-004).

**Why the caveat is kept rather than deleted.** Most `accurate` notes exist to disclose the part
that ISN'T read: *"the drawn stroke is at true size"*, *"the crop mix per map is rolled from the
seed and is a GUESS at the proportions"*, *"the 6 x 6 ft footprint is a GUESS - the one sizing page
is dead"*. Deleting them with the accuracy claim would delete exactly the liberties the GM asked to
have called out. They move behind the what and the why so they stop being the first thing read.

### B. `interactive/notes.py` - the map-notes reader

The convention, documented in `interactive/CLAUDE.md` and in `settlements.md`:

```markdown
## Map notes

<!-- Read by the interactive HTML map (l7r/diagram/interactive/notes.py). Every part is optional;
     a file without this section, or with a broken one, simply contributes nothing. -->

### Place

- **district**: Hoshigaoka
- **district direction**: east
- **county**: Hayakawa
- **county town**: Hayakawa
- **county town direction**: south, beyond the Imperial road
- **imperial road**: directly south
- **also**: the county magistrate's hunting lodge stands in the forest north-west

### Features

- **village lane**: The connector track runs south to the Imperial road; the district's
  main village, Hoshigaoka, lies east along it.
```

Parsing rules, every one of them a test:

- Find a heading whose text is `Map notes` at any level; if absent, return empty.
- Inside it, `### Place` and `### Features` subsections; either may be absent.
- A line matching `- **<key>**: <value>` contributes one entry; the key is lower-cased and
  whitespace-collapsed. Anything else in the section is ignored, including prose, blank lines,
  comments and nested lists.
- A continuation line (indented, no bullet) appends to the previous value, so a long annotation may
  wrap.
- An empty value is dropped. A duplicate key keeps the first.
- The section ends at the next heading of the same or higher level.
- Every failure mode - no file, unreadable file, no section, no bullets, a truncated last line -
  returns an empty result. `read_map_notes()` never raises. (FR-017.)

`place` keys are free-form; `place.py` looks for the ones it knows and ignores the rest.
`features` keys must be class keys from `classes.py`: an unknown one, or one absent from this map,
is dropped from the page and reported through the manifest's census so the map's own tooling shows
it to the author (FR-020) - the same channel `unregistered_classes` already uses.

### C. `interactive/place.py` - the place card

`place_card(meta, manifest, notes) -> dict | None`. Pure: dicts in, a dict of strings out. Composed
of, in order:

1. **What kind of place.** From `meta.scale` and a small table of settlement kinds written from
   `settlements.md` and the research entry - for a hamlet, that it is a small outlying farming
   community under a village district's headman, with no headman, shrine or burial ground of its
   own. Whether it is "the ordinary kind" is stated ONLY if the research pass supports it.
2. **Size.** `~N farmhouses` from the drawn house count; `population ~N` from `meta.population`
   where the tier records one (towns and cities do), else `~5 x meta.households` (the band already
   in `settlements.md`: 10-20 households = 50-100 inhabitants). Both tilde-marked (FR-009). Omitted
   when neither is available.
3. **What it grows.** Derived from the CLASSES PRESENT on the map, not from a per-map list: a table
   in `place.py` maps crop classes to (wet | dry | dike | water) and a display name, and the card
   names only what is drawn. This is what makes Kuwabata - mulberry, sugarcane, banana, fruit dikes
   and fish ponds, no dry plots at all - describe itself correctly with no per-map code (FR-014).
4. **Where it is.** The authored place facts: district and direction, Imperial road, county, county
   town, and any `also` lines. Each omitted cleanly when absent (FR-011, FR-012).

The card is delivered in the same JSON blob under the reserved key `"place"`; `page.js` opens it
like any class modal, with the settlement's name as the heading and no label line.

### D. The placard becomes clickable

`finish.py`'s `title()` tags the placard rect and the title text `cls="place"` instead of `"-"`;
the scale bar keeps `"-"` (FR-006). `NOT_HIGHLIGHTED_RULINGS` keeps its 2026-08-27 row and gains
the overturning beside it, so the record shows the ruling and its reversal rather than quietly
losing one. `"place"` is a reserved key `classes.py` declares but the census treats as always-known.

### E. The village lane default

The `village lane` entry's `why` gains the default sentence (FR-021), recorded with the GM's reason
for the class's name. When the notes name a district, `place.py` supplies the village's name to the
lane's annotation so the modal reads "toward Hoshigaoka, the district's main village"; with no
district recorded it reads "toward the district's main village".

### F. The pool's geography

A `## Map notes` block for every hamlet, both maps of the GM's dictated pair, and Hoshigaoka.
Districts the GM named are recorded as theirs; the rest are drawn from the place-name stock and
labeled invented (FR-025). Where a map draws a connector track, the district's direction FOLLOWS
that track's actual bearing off the cluster, so a reader who walks the lane goes the right way -
measured, not asserted: Akagahara's and Ikegami's connectors both run south, which is where the GM
put the Imperial road.

## Risks

| Risk | Mitigation |
|---|---|
| The placard's new class changes the census and trips `all_ink_is_ruled_on` | `"place"` is a registered class; the check reads the census, which will now count it |
| A pool sweep re-rolls maps | Nothing here touches the drawing; the scope lock and `make maps` cover it |
| A notes file is edited by the GM and the block silently stops parsing | Every parse failure is invisible BY DESIGN (the GM's requirement); the compensation is a tooling report, not a page warning |

## Review history

*(the `spec-fidelity` verdict is recorded here before implementation begins - constitution XVI)*
