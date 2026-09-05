# interactive/ - the HTML target (feature 134)

The map as a page a player can use: hover a feature and every feature OF ITS KIND lights up; click
it and a modal says what it is, why it stands there, whether that is historically accurate, a
deliberate deviation or a guess (constitution XII); "See references" lists the QUESTIONS the research
asked about it, each linking to its answer in `research/` on GitHub (feature 180 - see below).
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
| `sources.py` | a modal's references look wrong - they are READ FROM THE RECORD at page-write time: `research_questions()` resolves the class's `entry` to the research sections it names and builds each one's GitHub anchor (`RESEARCH_URL`, `github_anchor`, `question_text`); `research_sources()` / `registry()` read the `**Sources:**` keys and `SOURCES.md`, which the record tests still prove complete though the page no longer shows them |
| `page.py` - `merge_primitives` | the page draws too many elements, or a merge changed the picture. It gathers same-styled `<line>`/`<circle>`/`<ellipse>` into one `<path>` WHEREVER the reorder is invisible - an element joins an earlier bucket only if nothing it must pass overlaps it, and neither a TRANSLUCENT nor an OUTLINED element merges with one it overlaps (0.85 blobs stack darker than one merged fill - feature 148 R3; and a path paints every subpath fill before its stroke, so merged crowns show each other's outlines - feature 153 R5). A line has no fill and so is never outlined - getting that wrong un-merges every scatter. An extent it cannot compute counts as being in the way, and a circle's is tested as a circle |
| `page.py` | `wrap()` (the HTML form of one stream string), `ink_census()` (the FR-009 data: elements per class, and the unclassed ones), `explanations()` (only present classes, only present siblings), `render_page()` / `write_html()` |
| `assets/page.css`, `assets/page.js` | the look and the behavior; inlined at write time. The highlight color is a recorded rendering decision (research.md R2) - change it there and here together |

## The presumption of accuracy (feature 156)

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
questions - and through them the sources - stay one click away.

## The references modal lists QUESTIONS, not sources (feature 180)

The GM, 2026-09-05, looking at the hamlet pages: *"instead of listing individual sources on the
references modal, we will list the questions which we asked and researched - those pages are themselves
sourced with links, so a user who wants to follow through and read the original sources can do so."*
The audience is a casual RPG enthusiast, and *"they are not immediately presented with an overwhelming
amount of third party sources."* The whole sensibility - who the reader is, the four-step chain from
map to sources, what it asks of a research heading - is written in `research/CLAUDE.md`, "Who the
record is for"; this section is the mechanics.

| on the page | where it comes from |
|---|---|
| the explanation's footer has NO `Record: research/...` line | removed (the GM: *"I don't think we need lines like [that] on our main modal"*); `FeatureClass.entry` stays in the registry as the record |
| *"See references (N)"* - N questions; hidden when the entry resolves to none (only `fallow` today) | `page.js` `open()`, off `d.questions` |
| the references modal: one lead-in line (`page.REFERENCES_LEAD`), then one link per question, opening in a new tab | `sources.research_questions(entry)` - the `##`/`###` sections the entry's quoted headings name, in the ENTRY's order (the author's primary question first), text = heading less its dated `(researched ...)` parenthetical, URL = `RESEARCH_URL + file + "#" + github_anchor(heading)` |
| the button reads *"Return to Farmhouse writeup"* (the settlement's name on the place card) | `page.js` `openRefs()`; the GM: *"just saying close might make it seem like we are closing all of the modals"* |

**The anchor rule is GitHub's, reproduced** (`github_anchor`): lowercase, drop everything but letters,
digits, combining marks, spaces, hyphens and underscores, spaces to hyphens (so ` - ` is `---`), and a
repeated heading in one file numbered `-1`, `-2` in order of appearance - counted over EVERY heading
level and outside code fences, as GitHub counts. Checked against the live site on seven headings before
it shipped (spec D7) and pinned by `test_page.py`, so a divergence fails a test that states the expected
string. The links point at `blob/main`, not a commit (spec D1): a reader gets the current answer; a
renamed heading breaks old pages' anchors, which is why `research/README.md` rules anchors stable and
why every pool page re-renders at each landing.

**A class with a heading nobody can find shows no link and no error** - `research_questions` is quiet
like everything else here. So when you add a class, open its page and click "See references" once.

## The blue plot is its own class (feature 159)

A paddy plot drawn with the FLOODED fill (`#93B7AC`) carries `wet paddy`, not `paddy`. The GM,
2026-08-29: *"that is its own type of thing, and it deserves its own explanation."* It is the
**shitsuden** - ground too poorly drained to dry out, which holds water even out of season, takes no
winter crop and yields unreliably - against the **kanden**, the paddy that empties to a dry field.
The research is `research/fields.md`, 'The wettest plots are their own kind of ground'.

Decided at ONE emit site, `settlement/fields/comb.py` `_comb_draw_paddies`, from the fill about to be
drawn, so the class and the color cannot disagree. Every field engine reaches that site, so every
tint rule gets the class.

**THERE ARE TWO TINT RULES, and the shared explanation must be true under both.** This is the thing
to know before editing the class's prose:

| engine | rule | measured |
|---|---|---|
| comb (`waterfields/carve.py:356`) | a random 45% of the closing rank - the plots on the drain collector - less the pointed slivers `carve.py:361` demotes back to green | inashiro 2/24, kashikawa 3/24, mizuguchi 2/20, sawada 0/19 |
| terrace and polder (`hill.py:75`, `hill.py:191`, `polder.py:328`) | every `low` plot, no sample | **kuwabata 5/5** (the only LIVE one); enokida 22/22, tanada 40/40, yatsuda 18/18 are frozen legacy exhibits and never re-roll |

So blue is a SAMPLE of the wet ground on a comb map and the WHOLE of it on the others, and the
modal's disclosure is written conditionally ("on a comb field...") for that reason. A flat "only a
sample" is false on kuwabata, which a reader can open today; a flat "the wet ground" is false on
the comb maps. The
`low` / `fill` split is the engine's own (`carve.py`: *"`low` is the TOPOGRAPHY; `fill` is only the
PICTURE"*), and the land-use overlays still key off `low`, never off the class.

## The map-notes block: facts a `.notes.md` hands its page (feature 156)

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
one `add*()` call. A class key MUST be a row of `classes.py` - `all_ink_is_ruled_on` (now
`tests/gate/test_map_vocabulary.py`)
fails a hamlet map on ink with no class and on a key the registry does not know. A feature the GM
rules NOT highlighted is tagged `"-"` and gets a row in `NOT_HIGHLIGHTED_RULINGS`.

A caption gets the class of the feature it names (`label(..., cls=...)`), which is all FR-006
needs: label and subject are one class, so hovering either lights both.

`place` is a RESERVED key rather than a row of `classes.py`: it tags the title placard and its name,
and its modal is built per map by `place.py` instead of being written once in the vocabulary. The
census and the ruling both know it, so the placard is highlightable and is never reported as
unruled ink. The scale bar beside it keeps `cls="-"`.

## Verifying

`tests/interactive/` - the registry (every entry complete, siblings closed and symmetric), the
page (wrap, census, self-containment, present-only data), and the browser test (Playwright +
Chromium, `rolls_map`: opens the reference hamlet's page from `file://` and drives hover, click and
the modal). `make map GEN=pool/hamlets/inashiro/inashiro.gen.py` writes the real page; open it in a browser.
