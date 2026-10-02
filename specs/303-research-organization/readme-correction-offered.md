# The `research/README.md` correction, offered to the GM (feature 303) - NOT APPLIED

A README is the GM's to write (constitution XVII, NON-NEGOTIABLE): *"If a README is factually wrong, say so and offer
the correction rather than making it ... a genuine exception is the GM's to make."* Feature 303 flattened the record, so
`research/README.md` is now wrong in the places below; this feature did not edit it, and the pointer check exempts it
until the GM applies or declines what follows (spec FR-017, FR-021, SC-007).

## What is now wrong in it

1. **The page table** (`| Research file | What it records |`, lines 18-32) links fourteen part pages -
   `settlements.html`, `archetypes.html`, `buildings.html`, `cities/` and its seven pages, `fields.html`,
   `homesteads.html`, `presentation.html`, `religion-and-death.html`, `towns.html`, `urban-features.html`,
   `vegetation.html`, `water.html`, `ways.html`. None of them exists: the parts were directories of fragments since
   feature 258, their pages were built and no longer committed since feature 301, and since feature 303 the parts
   themselves are gone - every question is one file in `research/questions/`, grouped into sections by
   `research/contents.json`.
2. **Line 13** links `buildings.html` as the page carrying Mode A's reasoning; that research is now the section
   "Estates and other compounds" of `contents.json`.
3. **Line 88** says a note is *"on the page's citations page"*; the citations pages were retired (feature 301 stopped
   writing them; feature 303 gave each question page its own notes file, shown at the foot of its page in the site).
4. **Lines 60, 88, 90** link `SOURCES.html`; the registry is the fragments under `research/sources/`, built into the
   site's `sources/` pages.

## The replacement text, if the GM wants it

Replace the load line and the table (lines 14-32) with:

```markdown
**Load the questions for the topic you are changing or questioning** - and, for a hand-authored tier, to
draw. A scripted hamlet needs none of it to run. Pointers name a question's file, which keeps its number.

The record is one file per question in [`questions/`](questions/) - `NNNN-<heading id>.html` for the research,
`NNNN-<heading id>.drawing.html` for how our maps draw it, each with its notes beside it - and the sections a reader
browses are declared in [`contents.json`](contents.json), each question placed by its tags ([`tags.json`](tags.json)):

| Section | What it records |
|---|---|
| The settlement tiers | the five tiers: what each is, what a map's page states about it, households, place names |
| The countryside | fields and their crops, the field archetypes, homesteads, water, vegetation and terrain, ways |
| Estates and other compounds | Mode A: the reasoning behind the compound and building plans, whose rules stay in [`../buildings.md`](../buildings.md) |
| Towns | the town tier |
| Cities | domain capitals, city defenses, urban fabric, the government quarter, outside the walls, river cities, sizing a city |
| Trades and services | what a town and a city share: boards, justice works, trades, wells, stable yards |
| Religion and the dead | shrines, temples, and the dead |
| Map conventions | the map's drawing conventions: labels, captions, framing and cropping |

`make record` builds the site a reader opens, `site/index.html`.
```

In line 13, replace ``[`buildings.html`](buildings.html) carries only its reasoning`` with ``the section Estates and
other compounds carries only its reasoning``.

In line 88, replace this text, from its start to the parenthesis' close:

```markdown
Sources live in [`SOURCES.html`](SOURCES.html) with stable keys; an entry cites by key, in a footnote whose note is on the page's citations page (`citations/<name>.html`; the research page keeps the reference and loads the derived `citations/<name>.js` for the hover - run `make citations` after a note changes).
```

with:

```markdown
Sources live in the registry ([`sources/`](sources/)) with stable keys; an entry cites by key, in a footnote whose note is in the question's own notes file beside it (`NNNN-<heading id>.notes.html`); the site shows a question's notes at the foot of its page, numbered from 1 - run `make record` after a note changes.
```

and in the same line, *"derived into the works section of every citations page that cites it"* with *"derived into the
list of works at the foot of every question page that cites it"*, and *"\"The notes live on a CITATIONS PAGE\""* with
*"\"A question's notes stand at its foot\""* (the heading `CLAUDE.md` carries now). In line 90, replace
``in `SOURCES.html` `` with ``in the registry``.
