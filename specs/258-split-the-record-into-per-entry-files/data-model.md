# The fragment layout

What a fragment is, where it lives, and what its name means. The grammar of what goes INSIDE one, and
every refusal, is [contracts/fragment-format.md](contracts/fragment-format.md).

## The rule in one sentence

A page is a directory of fragments; a fragment is one entry of the record; a section that has entries of
its own gets a directory named exactly as its own file is, without the extension.

## Where a page is cut

A research page is cut on `<h2>` and nothing else. 14 `<h3>` headings stand inside questions on six
pages, and a modal's `Entry:` tag may name one (`sources.py` resolves both levels), so breaking them out
would fragment a question and lose the entry a modal points at. Only the registry's works roster has
entries of its own, at `<h3>`, and the level is passed to the splitter rather than guessed.

A page's closing run - the citations-page pointer where there is one, then `</main></body></html>` - is
the tail, not part of the last question. Every one of the record's 38 pages ends in exactly that, and a
page that does not is refused rather than cut by guesswork.

Within that, a section begins at every `<hN` that opens a real one, which is not the same as every `<hN`
in the file:

- **a heading inside an HTML comment is not a section.** The registry carries an 8,042-byte commented-out
  block holding two whole `<h2>` groups - the old citing rules and the re-sourcing queue (R1). Cutting on
  the plain text splits that comment in two and invents two sections no reader sees. The comment rides
  with the front matter, verbatim.
- **a heading is recognized wherever it stands on its line.** No heading in the record needs this today:
  the only two that do not begin their line are both inside that same comment, and are therefore not
  sections anyway. It is stated so that the cut is never anchored to the line start, which would pass on
  today's record and fail on the first page that indents a heading.

The registry therefore has THREE visible sections, not the five a plain `<h2>` count reports.

## Names

| name | what it holds | ordered by |
|---|---|---|
| `_front.html` | everything from `<!DOCTYPE` to just before the first `<h2` | first, always |
| `NNN-<slug>.html` | one section: its `<h2 id=...>` heading and everything up to the next `<h2` | its prefix |
| `NNN-<slug>.notes.html` | the notes belonging to that section, in the order they are referenced | with its section |
| `NNN-<slug>/` | the entries of that section, where it has them (the registry's works roster) | its prefix |
| `NNNN-<key>.html` | one entry inside such a directory: its `<h3 id=...>` and its body | its prefix |
| `_tail.html` | everything after the last section: the closing tags, and a research page's pointer to its citations page | last, always |
| `_citations-front.html` | the citations page from `<!DOCTYPE` through the works section's own opening - `<section class="works">` and its `<h2 id="works-cited">` heading | first on that page |
| (the works block) | DERIVED at assembly by the engine's existing derivation, from the assembled page. NOT a fragment | after the front |
| `_citations-mid.html` | the hand-authored bytes between the works block and the notes: `</section>`, the `<h2 id="notes">` heading, and `<section class="footnotes"><ol>` | after the works block |
| `_citations-tail.html` | `</ol></section>` and the closing tags | last on that page |

- **The prefix is gapped by ten** (`010`, `020`, `030`) - three digits for a page's questions, four for the
  registry's 920 entries (`0010`, `0020`). Inserting between two neighbors takes an unused number and
  renames nothing. When a gap is exhausted the assembly says so and the directory is re-spaced
  deliberately, as one commit that changes no assembled byte.
- **The slug is a convenience, not an anchor.** The record's anchors are the heading ids inside the
  fragments, exactly as they are today; a map modal's `Entry:` tag names a heading, never a filename. A
  slug may therefore be imperfect, and renaming a file changes nothing a reader can see.
- **The key in a registry entry's filename is its source key** - the one a footnote cites and
  `SOURCES.html` registers - so one glob finds it: `ls research/sources/*/*fei-1939*`.

## The tree, as it will stand

```text
research/
├── SOURCES.html                                   ASSEMBLED
├── sources/
│   ├── _front.html                                 incl. the 8,042-byte commented-out block
│   ├── 010-works-cited.html                        the roster's heading and its 213-byte intro
│   ├── 010-works-cited/
│   │   ├── 0010-kitamoto-mushiro-niwa.html
│   │   ├── 0020-kodaira-niwa.html
│   │   └── ... 920 entries
│   ├── 020-attested-instances.html
│   ├── 030-setting-canon.html
│   └── _tail.html
├── ways.html                                      ASSEMBLED
├── ways/
│   ├── _front.html
│   ├── 010-how-far-past-the-bank-does-a-bridge-land.html
│   ├── 010-how-far-past-the-bank-does-a-bridge-land.notes.html
│   ├── ... 5 questions
│   ├── _tail.html
│   ├── _citations-front.html
│   ├── _citations-works.html
│   └── _citations-tail.html
├── cities/
│   ├── defenses.html                              ASSEMBLED
│   └── defenses/                                  the same shape, one level down
└── citations/
    ├── ways.html                                  ASSEMBLED
    ├── ways.js                                    DERIVED (unchanged)
    └── cities/defenses.html                       ASSEMBLED
```

## Entities

### Fragment

One hand-authored file holding one entry. Its identity is its path; its order is its prefix; its content
is bytes that are copied into the assembled page without normalization. A fragment is never rewritten by
a tool except by the splitter, once, and by `make citations` in the one case that is marked DERIVED in
its own first line.

### Page

A directory under `research/` whose name matches a committed `.html` beside it. Holds one research page
and its citations page, because a question's prose and that question's notes belong together - which is
the whole of stage 3.

### Note

A footnote, living in the `.notes.html` beside the question that references it. Identified by a **key**,
not a number:

- unique within its page;
- lower-case, digits and hyphens;
- derived once by the splitter from the note's own leading source key (`fei-1939`, `fei-1939-2`, ... for
  the 635 repeats), or from the question's slug and the note's ordinal for the 326 notes that lead with
  no source key (R5);
- thereafter whatever its author writes.

### Reference

A citation of a note, in a question's prose, written `<sup class="fn" data-note="<key>"></sup>`. The
assembler turns it into the numbered anchor the page carries today. One note may be referenced more than
once; each reference gets its own document-unique id, and the note's back link points at the first.

### Number

Not an entity: a number is allocated at assembly, in the order references appear in the assembled page,
and appears in no fragment anywhere.

## What does NOT change

- The assembled pages: same paths, same bytes at stages 1 and 2, same anchors, same links from every map
  modal, same `citations/<name>.js` beside them.
- `SOURCES.html` keeps its name and its place; the engine parses it exactly as it does now
  (`interactive/sources.py` is untouched).
- `make citations` keeps its name and its job; at stage 3 its output moves from the middle of a page into
  `_citations-works.html`.
- Every existing test over the record reads the assembled pages and keeps passing unchanged (FR-027).
