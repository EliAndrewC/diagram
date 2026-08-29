# interactive/ - the HTML target (feature 134)

The map as a page a player can use: hover a feature and every feature OF ITS KIND lights up; click
it and a modal says what it is, why it stands there, whether that is historically accurate, a
deliberate deviation or a guess (constitution XII), and which `research/` entries it rests on.
Written by `Settlement.finish()` beside the `.svg`, `.png` and `.json` of every Mode B map. The
GM's request, verbatim, and the spec: `specs/134-interactive-html-map/`.

**The SVG and the PNG are untouched** (spec FR-010). The class of a primitive rides in a SIDE LIST
beside the record streams (`Settlement.out_cls` etc., `core.py`), never in the SVG text, so the
PNG is byte-identical by construction; the page is a second serialization of the same strings.

| file | look here when |
|---|---|
| `tags.py` | you need the tag shapes: a `str` class, `Parts` (one string, several classes - a farmhouse and its shed), `Split` (one element, fill and stroke in different classes - a paddy and its bund), `"-"` (ruled not highlighted), `None` (nobody ruled) |
| `classes.py` | you are adding a KIND of feature, changing what a modal says, or adding a sibling distinction. The vocabulary is the spec's FR-007 table; every entry is written FROM a `research/` entry and carries its label; sibling text is per PAIR and symmetric; `NOT_HIGHLIGHTED_RULINGS` is the record of what was ruled out and by whom, and `NOT_HIGHLIGHTED_OVERTURNED` of what was ruled out and later let back in |
| `notes.py` | a fact you wrote into a map's `.notes.md` is not reaching its page, or you are adding a key the block understands. The reader has no error path ON PURPOSE - see below |
| `place.py` | the title card says something wrong, or you are describing a new tier. It holds the per-tier text, the crop table and the basis the card owes its reader |
| `glossary.py` | you are adding a term the explanations use, or a definition reads wrong - every occurrence of a term in a modal is a hover tooltip; a test proves each term is used and each explanation's terms are defined |
| `sources.py` | a modal's references look wrong - they are READ FROM THE RECORD at page-write time: the class's research entry's `**Sources:**` keys and `research/SOURCES.md`'s citation text; the registry's own `sources` tuple is only the fallback |
| `page.py` - `merge_primitives` | the page draws too many elements, or a merge changed the picture. It gathers same-styled `<line>`/`<circle>`/`<ellipse>` into one `<path>` WHEREVER the reorder is invisible - an element joins an earlier bucket only if nothing it must pass overlaps it, and neither a TRANSLUCENT nor an OUTLINED element merges with one it overlaps (0.85 blobs stack darker than one merged fill - feature 148 R3; and a path paints every subpath fill before its stroke, so merged crowns show each other's outlines - feature 153 R5). A line has no fill and so is never outlined - getting that wrong un-merges every scatter. An extent it cannot compute counts as being in the way, and a circle's is tested as a circle |
| `page.py` | `wrap()` (the HTML form of one stream string), `ink_census()` (the FR-009 data: elements per class, and the unclassed ones), `explanations()` (only present classes, only present siblings), `render_page()` / `write_html()` |
| `assets/page.css`, `assets/page.js` | the look and the behavior; inlined at write time. The highlight color is a recorded rendering decision (research.md R2) - change it there and here together |

## The presumption of accuracy (feature 154)

The page never tells a reader that a feature is historically accurate. The GM, 2026-08-29: *"we
almost always say that it is historically accurate ... I want the presumption to be that things are
always historically accurate unless stated otherwise. In other words, we should call out liberties
that we have taken."* A claim made about nearly every feature carries no information; a liberty does.

The three-way classification is UNCHANGED and still recorded on every class (constitution XII) - it
just is not announced. What a modal prints:

| the record says | the modal leads with | and below the why |
|---|---|---|
| `accurate` | nothing - what the feature IS | `caveat`, when its record discloses a liberty |
| `deviation` | "This is a deliberate deviation - ..." | nothing (the lead already carried it) |
| `guess` | "This is a guess - ..." | nothing |

`caveat` is the LIBERTY HALF of `label_note`, verbatim - the drawing convention, the derived number,
the sub-guess ("the crop mix per map is rolled from the seed and is a GUESS at the proportions"). The
other half - "Topology, taper and true-size width are read" - is the accuracy claim in other words
and is NOT rendered; four classes whose whole note is that get no caveat at all, and a test lists
them so a fifth is a decision rather than an omission. Both halves stay in the record, and the
sources stay one click away.

## The map-notes block: facts a `.notes.md` hands its page (feature 154)

A settlement's own `<name>.notes.md` may carry a `## Map notes` section, and the page reads it.
Optional everywhere, and absent from most of the pool.

```markdown
## Map notes

### Place

- **district**: Hoshigaoka
- **district direction**: east
- **imperial road**: directly south
- **county**: Hayakawa
- **town**: Hayakawa
- **town direction**: further south, beyond the Imperial road
- **also**: anything else worth a sentence on the card

### Features

- **village lane**: A sentence true of THIS map's lanes, shown under "On this map".
- **windbreak**: ... any class key from `classes.py` works. That generality is the point
  (GM: "in general, the kind of thing that we want to be able to do for any kind of map feature").
```

`### Place` feeds the title card (`place.py`; `PLACE_KEYS` is what it understands, and an
unrecognized key is simply unused rather than wrong). `### Features` is keyed by CLASS KEY and
appears in that class's modal on that map only.

**The reader has no error path, and that is the requirement rather than a shortcut** (GM: *"we should
not presume that such sections exist and our code that parses the notes file to find these special
notes should be resilient against that formatting not being present, and should default to simply
not pulling anything in if the parsing fails"*). A missing file, a missing section, a bullet with no
colon, a nested list, a truncated line, a class key nobody knows - each contributes nothing, silently.
`read_map_notes()` cannot raise. The cost of that, accepted deliberately: a typo in a key produces
silence rather than a complaint, so check a new block by regenerating the map and opening its page.

**One default is synthesized rather than authored**: a hamlet's `village lane` with no annotation of
its own says where the lanes lead, naming the district's main village when the notes name the
district. A district takes its main village's name (`l7r.md`, "Place Names"), which is what makes the
one key enough - and it is why the class is a VILLAGE lane rather than a hamlet lane.

## Tagging a new feature

At the emit site, either `with self.feature("<class key>"):` around the drawing, or `cls=` on the
one `add*()` call. A class key MUST be a row of `classes.py` - the gate check `all_ink_is_ruled_on`
fails a hamlet map on ink with no class and on a key the registry does not know. A feature the GM
rules NOT highlighted is tagged `"-"` and gets a row in `NOT_HIGHLIGHTED_RULINGS`.

A caption gets the class of the feature it names (`label(..., cls=...)`), which is all FR-006
needs: label and subject are one class, so hovering either lights both.

`place` is a RESERVED key rather than a row of `classes.py`: it tags the title placard and its name,
and its modal is built per map by `place.py` instead of being written once in the vocabulary. The
census and the gate check both know it, so the placard is highlightable and is never reported as
unruled ink. The scale bar beside it keeps `cls="-"`.

## Verifying

`tests/interactive/` - the registry (every entry complete, siblings closed and symmetric), the
page (wrap, census, self-containment, present-only data), and the browser test (Playwright +
Chromium, `rolls_map`: opens the reference hamlet's page from `file://` and drives hover, click and
the modal). `make map GEN=pool/hamlets/inashiro.gen.py` writes the real page; open it in a browser.
