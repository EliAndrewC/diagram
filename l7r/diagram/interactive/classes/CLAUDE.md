# interactive/classes/ - the feature-class vocabulary, one class per kind of thing on the map

**A MODAL'S TEXT IS ITS OWN FILE** (feature 319, plan D12, GM 2026-10-03: *"I believe that feature 189's reasoning has
been superseded by the fact that we now cross-reference our implementation with our research"*):
`../assets/modals/hamlet/<slug of the key>.md` (a sheet's kinds: `../assets/modals/sheet/`; a title-card choice's:
`../assets/modals/choice/`), in the About form (below). The class keeps `key` - what the engine stamps on the ink - and its
`#` comments; `Kind.feature()` reads the file (`_base.modal_path`). A test holds that every kind has its file, no class
carries modal text, and no file is an orphan (`tests/interactive/test_about_form.py`). A modal-file edit owes
`make page-check`, not the gate (the parent `interactive/CLAUDE.md` has the page check).

| module | holds |
|---|---|
| `_base.py` | the machinery: `FeatureClass` (what the page reads), `slug`, the not-highlighted rulings, the `Kind` base class, `parse_explanation` (the modal text's parser), `install_siblings` |
| `homestead.py` | farmhouse, storage shed, byre, threshing yard, garden, privy, wood shed, manure heap, bath room, hen coop, household shrine, persimmon |
| `greenery.py` | homestead bamboo, shared bamboo grove, windbreak, copse, woodland commons, scrub and rough grazing, marsh |
| `fields.py` | paddy, wet paddy, bund, bund beans, millet, buckwheat, barley, soy, fallow |
| `water_and_ways.py` | stream, irrigation ditch, drainage ditch, pond, field pond, field rock, grave island, village lane, footbridge, well, notice board |
| `dikepond.py` | fish pond, mulberry dike, fruit dike, tea dike, pig sty, fry pond, manure pit, sluice gate, perimeter dike |
| `siblings.py` | the pair texts ("how the farmhouse differs from the storage shed"), string constants because the page renders sibling LINKS, not these texts (spec 189 D4) |
| `__init__.py` | imports the families in the spec's FR-007 order and builds `CLASSES`; re-exports the vocabulary |

## Writing an entry

**What a modal SAYS is governed by `dev/modals.md`** (feature 319): the reader, the tabs (About / Guesses / Depiction /
References), the questions each kind's About answers, where a guess, a deviation and a convention go, and which questions the
References tab lists. A kind particular to one sheet or to the setting follows `dev/modals-particular.md`. The checks that hold
them are `modal-form` and `modal-research`, owed by a modal whose prose or `Entry:` changed.

```text
About: A hen coop sheltered a farming household's chickens at night. ...

A coop of the early 1600s ... is not recorded.

Guesses:
- Its size on the map, 5 by 5 ft: the excavated coop is square, but its size is not given.

Depiction: The map draws a coop as Chinese farms kept it ...

Name: hen coop
Covers: `farm_fixtures[kind=coop]`
Sources: buck-1930-farm-economy, qimin-yaoshu-yangji, ...
Entry: research/questions/0045-chickens-and-chicken-coops.html, ...
Drawing: research/questions/0045-chickens-and-chicken-coops.drawing.html
```

- Each tag at the start of a line. `About:` is required (a blank line between paragraphs); `Guesses:` (`- ` bullets),
  `Depiction:` (paragraphs) and `Drawing:` (the "how our maps draw it" pages, in the form `Entry:` takes) are optional.
  Wrapped lines join with one space. A missing text or a missing required tag fails at IMPORT, naming the class.
- The DATA tags, each one line (feature 207: a repointed entry is a page-content edit, not an engine change): `Name:` (the
  modal's heading), `Covers:` (which manifest features the class draws), `Sources:` (keys in `research/sources/`, or
  `not recorded`), `Entry:` (the research questions the text was written FROM, in the form `sources.py` parses - the
  References tab), and an optional `Form: particular`.
- **No class-level label** (feature 319): the classification is per statement - a guess is a Guesses bullet, a deviation is
  said in About where it applies, a convention on the Depiction tab (`dev/modals.md` M11-M13). `What:`, `Why:`, `Note:`,
  `Caveat:` and `Label:` are refused by name: don't let the parser forget them, because an unrecognized `Why:` line would
  silently join the About paragraph above it.
- ONE class attribute stays: `key` - the tag the engine writes on the ink and the CSS token. It is code:
  changing it changes what the engine emits, so it re-keys the gate, as it should.
- The sibling texts are `../assets/siblings.json` and the page's fixed phrases and rulings record
  `../assets/page-text.json` (`_base.py` loads them via `../content.py`).
- Definition order within a module, and the module order in `__init__.py`, is `CLASSES`'s order.
- Comments (`#`) above a class are for the next developer and never reach the page.

The 51 entries were converted by script from the old `_DEFS` tuple (feature 189); `tests/fixtures/classes_before_189.json`
holds the old fields, and `test_classes_docstrings.py` still proves `name`, `covers` and the sibling texts equal it.

**When a research page a modal was written from changes**, the modal owes the modal checks and the push refuses until
they are answered: [`dev/modals.md`](../../../../dev/modals.md), the last section.
