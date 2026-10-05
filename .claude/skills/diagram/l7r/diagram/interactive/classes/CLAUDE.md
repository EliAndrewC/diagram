# interactive/classes/ - the feature-class vocabulary, one class per kind of thing on the map

**A MODAL'S TEXT IS ITS OWN FILE since feature 319** (plan D12, GM 2026-10-03: *"I believe that feature 189's reasoning has
been superseded by the fact that we now cross-reference our implementation with our research"*):
`../assets/modals/hamlet/<slug of the key>.md` (a sheet's kinds: `../assets/modals/sheet/`), in the About form (below). The class keeps `key` - what the engine stamps on the ink - and its `#` comments; `Kind.feature()` reads the
file (`_base.modal_path`). Editing a modal reads one small file, not a module of 14; a test holds that every kind has its file,
no class carries modal text, and no file is an orphan (`tests/interactive/test_about_form.py`). Where this page says
"docstring" below, read "its modal file".

**The explanation IS the docstring** (feature 189, GM 2026-09-05: *"the documentation within the code is
literally the documentation that is visible in the user interface"*). What a modal says about a farmhouse
is the docstring of `class Farmhouse(Kind)` in `homestead.py`, and nothing else. The gate's key is the
docstring-stripped AST, so rewording an explanation does not re-open the nine-minute gate: it owes
`make page-check` (the registry's tests and the browser test, 26 s), which the `page` stamp demands at
push. Both caches see the edit (the generation cache hashes a class body by its source text; the render
fingerprint hashes bytes), so the page regenerates.

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
  `../assets/page-text.json` (`_base.py` loads them via `../content.py`). A modal-file or content-file
  edit owes `make page-check`, not the gate.
- Definition order within a module, and the module order in `__init__.py`, is `CLASSES`'s order.
- Comments (`#`) above a class are for the next developer and never reach the page.

## The conversion (2026-09-05)

The 51 entries were converted by script from the old `_DEFS` tuple, never retyped, and
`tests/fixtures/classes_before_189.json` holds every field as it was; `test_classes_docstrings.py`
still proves `name`, `covers` and the sibling texts equal it (the old form's label and prose went with feature 319).

## When a section a modal was written FROM moves (GM 2026-09-12, feature 234)

What a map's modal says about a feature IS the docstring of its `Kind` class
(`interactive/classes/`, feature 189), written FROM a research section the class names in its `Entry:`
tag. Nothing used to notice when that section's content moved underneath it, and the GM asked the
question that closed the gap - told to update the pigsty write-up, *"if I hadn't said that ... then
would you have done it?"*

**What is owed.** `scripts/_entry_owed.py` names every class whose section's BODY changed while its own
explanation prose did not. `make page-check` prints that list and does not block. **The push REFUSES**
until each named pair is answered: dispatch the `entry-drift` agent at it, rewrite the prose it calls
DRIFTED - or, where the sections moved without any FINDING moving, discharge the lot with one recorded
line, `ENTRY_DRIFT_OK="<what moved, and why no modal is now wrong>"`, which `make audit` lists.

It is enforced rather than expected, on the GM's ruling: *"I don't believe that we should have any such
thing as an unenforced doctrine. If it is unenforced, then it is not a doctrine. something should either
not be considered doctrinal or it should be enforced."* Narrowing the key so it would fire less was
priced first and does not work - firing only on what a reader SEES takes 28 of 30 research-only commits to 27 of 30 (`specs/234-entry-owed-when-the-record-moves/research.md` R5), because separating "this
section now says something different" from "this section was maintained" is a judgment about meaning.

**`record-format` and `quote-check` are NOT this check.** They read a research ENTRY - whether a reader
would understand it, whether its quotations are on the page and support what they are attached to.
Neither of them ever opens a `Kind` docstring, so neither can tell you a modal has gone stale. They are
the changed research entry's own standing obligations and a green pass from either says nothing about
any modal.

**And a renamed heading owes its inbound links** - the rule this file already stated, now checked:
`scripts/check-entry-headings.py` fails the gate and the push when a class's `Entry:` resolves to no
section. A section deliberately not written is written in the declared form
`research/<file>.html (no dedicated entry - recorded as silent)`, which `make audit` enumerates.
