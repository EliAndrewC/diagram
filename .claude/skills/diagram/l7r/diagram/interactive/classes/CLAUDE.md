# interactive/classes/ - the feature-class vocabulary, one class per kind of thing on the map

**The explanation IS the docstring** (feature 189, GM 2026-09-05: *"the documentation within the code is
literally the documentation that is visible in the user interface"*). What a modal says about a farmhouse
is the docstring of `class Farmhouse(Kind)` in `homestead.py`, and nothing else. The gate's key is the
docstring-stripped AST, so rewording an explanation does not re-open the nine-minute gate: it owes
`make page-check` (the registry's tests and the browser test, 26 s), which the `page` stamp demands at
push. Both caches see the edit (the generation cache hashes a class body by its source text; the render
fingerprint hashes bytes), so the page regenerates.

| module | holds |
|---|---|
| `_base.py` | the machinery: `FeatureClass` (what the page reads), `Label`, `ANNOUNCED`, the lead sentence and label phrase, `slug`, the not-highlighted rulings, the `Kind` base class, `parse_explanation`, `install_siblings` |
| `homestead.py` | farmhouse, storage shed, byre, threshing yard, garden, privy, woodpile, manure heap, bathhouse, hen coop, household shrine, persimmon |
| `greenery.py` | homestead bamboo, shared bamboo grove, windbreak, copse, woodland commons, scrub and rough grazing, marsh |
| `fields.py` | paddy, wet paddy, bund, bund beans, millet, buckwheat, barley, soy, fallow |
| `water_and_ways.py` | stream, irrigation ditch, drainage ditch, pond, field pond, field rock, grave island, village lane, footbridge, well, notice board |
| `dikepond.py` | fish pond, mulberry dike, pond sluice, sugarcane dike, banana dike, fruit dike, vegetable ground, pig sty, duck pen, fry pond, manure pit, sluice gate, perimeter dike |
| `siblings.py` | the pair texts ("how the farmhouse differs from the storage shed"), string constants because the page renders sibling LINKS, not these texts (spec 189 D4) |
| `__init__.py` | imports the families in the spec's FR-007 order and builds `CLASSES`; re-exports everything the old `classes.py` exported |

## Writing an entry

```python
class HenCoop(Kind):
    """
    What: A small ground-level roost for a few chickens, drawn as a box beside the house.

    Why: The Qimin Yaoshu says to build the roost as an enclosure on the ground with a perch inside,
    because birds left to the trees sicken; so it stands in the yard, not in a tree.

    Note: The coop's existence and ground form are read; the household proportion and the 5 x 5 ft size
    are guesses bounded by 'most regions'.

    Name: hen coop
    Covers: `farm_fixtures[kind=coop]`
    Label: guess
    Sources: cambridge-poultry, qimin-yaoshu
    Entry: research/homesteads.html - 'The farmstead's fixtures'
    """

    key = "hen coop"
```

- Four tags, each at the start of a line: `What:` and `Why:` (the two paragraphs of the modal), `Note:`
  (the one line that justifies the label - for a `convention` the GM's *"we have rendered ... in order
  to ..."* sentence, which the modal opens with after "Note: "), and an optional `Caveat:` (the liberty
  half of the note, shown under the why; it must be a verbatim substring of `Note:` - a test holds that).
- A value runs to the next tag; wrapped lines are joined with one space, so wrap freely. A missing
  docstring or a missing required tag fails at IMPORT, naming the class.
- The DATA tags follow the prose, each one line (feature 207 - they were class attributes until then, and
  relabeling a class or repointing its research entry was an ENGINE change that cost the whole gate):
  `Name:` (the modal's heading), `Covers:` (which manifest features the class draws - documentation for
  the next reader), `Label:` (`accurate` / `deviation` / `convention` / `guess` - constitution XII,
  four-way since feature 183), `Sources:` (keys in `research/SOURCES.html`, comma-separated, or
  `not recorded`), `Entry:` (the research section the text was written FROM, in the form `sources.py`
  parses - it is what puts the questions on the references modal). All five are required of a `Kind`;
  a missing one fails at import naming the class.
- ONE class attribute stays: `key` - the tag the engine writes on the ink and the CSS token. It is code:
  changing it changes what the engine emits, so it re-keys the gate, as it should.
- The sibling texts are `../assets/siblings.json` and the page's fixed phrases and rulings record
  `../assets/page-text.json` (`_base.py` loads them via `../content.py`). A docstring or a content-file
  edit owes `make page-check`, not the gate.
- Definition order within a module, and the module order in `__init__.py`, is `CLASSES`'s order.
- Comments (`#`) above a class are for the next developer and never reach the page; the docstring is
  for the reader and always does.

## The conversion (2026-09-05)

The 51 entries were converted by script from the old `_DEFS` tuple, never retyped, and
`tests/fixtures/classes_before_189.json` holds every field as it was; `test_classes_docstrings.py`
proves the registry equals it field by field.
