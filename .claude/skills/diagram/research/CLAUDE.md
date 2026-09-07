# research/ - the historical record, and who it is written for

This file auto-loads when a research entry is being written or changed - which is exactly when the
rule below applies. The entry FORMAT, the evidence classes, the citing rules and the table of which
research file grounds which rule file are in [`README.md`](README.md); this file carries the one thing
that is not a format rule: who the reader is.

## Who the record is for, and how it is organized for them (GM 2026-09-05, feature 180)

The reader this record ultimately serves is not the next session - it is the person looking at an
interactive map. The GM's description of them: *"casual RPG enthusiasts who might be interested to
learn a little more about why these settlements are the way that they are. You know, like the different
types of crops that are grown, that kind of thing."* They are curious, not scholarly, and *"they are not
immediately presented with an overwhelming amount of third party sources that they could go read to
become an expert."*

**So the record is organized as QUESTIONS**, and the reader reaches it through a chain with one step per
level of curiosity:

1. **The map.** They hover a feature and click it; the modal says what it is and why it stands there.
2. **"See references."** The references modal lists the questions we asked while working out that kind
   of feature - the headings of the research sections its explanation was written from, each a link.
3. **The answer.** A question links to its section of the research PAGE, locally from the map
   (`../../../research/<file>.html#<anchor>`; feature 194 - it was the GitHub rendering of the Markdown before),
   where the well-formatted markdown gives the finding, the decision it drove and any disclosed liberty.
4. **The sources.** Every section ends in a `**Sources:**` line, and every key in [`SOURCES.html`](SOURCES.html)
   carries the URL where the work can be read (constitution v2.13.0), so a reader who truly wants to
   check can - *"which both demonstrates that this was based on actual research and also gives them the
   ability to go read Wikipedia or whatever other public source we have linked to."*

The sources are deliberately one click further out than the questions. A reader who stops at step 2 has
learned what was looked into; one who stops at step 3 has the answer; the works themselves are for the
reader who asks for them.

**What this asks of an entry:**

- **Its heading is the question a reader might ask from the map**, and the answer may follow in the same
  line - *"How close does a farmhouse stand to the paddy? Up against it - but never on the bund"*, *"Is
  every farmhouse reached by a lane, and in what FORM?"*. A heading is the line the reader sees on the
  modal, so write it for them. The trailing bookkeeping - *"(researched 2026-08-27, feature 133 T41)"* -
  stays in the record and is stripped from the modal's text by `interactive/sources.py` (it is for us,
  not for them).
- **Its anchor is stable** (already the rule in README's "Adding to the record"): the modal links to the
  heading's anchor (GitHub's rule, kept), so a rename must fix its inbound links - the rule files, and the class entries
  in `interactive/classes.py` that quote the heading.
- **A class's explanation names the entries it was written from** (`interactive/classes.py`, the `entry`
  field), and that pointer is the whole of what puts a question on a modal: the page resolves it at
  write time, so a new section reaches every map the moment a class entry names it. Nothing is re-typed.
- **The questions the GM has said they will add** are of this kind, in their words: *"how many farmers
  lived in each farmhouse, or why are there more rice plots than there are farmhouses, and how many rice
  plots were farmed by each farmhouse, or how many different types of crops were grown, that kind of
  thing."* Each is a research entry with its citations first, and only then a line on a modal. Feature
  180 added none of them - it shows only the questions the record already held (*"For now, you can just
  limit yourself to the questions that we already have"*); the GM will say at a later time which new
  questions they want added to what is shown.

## Four labels, and the GM's line between two of them (GM 2026-09-05, feature 183)

An entry's finding, and the class explanation written from it, carries one of FOUR labels (constitution
XII; `README.md` still lists the original three and is the GM's to update): **accurate**, **deviation**,
**convention**, **guess**. The GM's rule for the two in the middle, verbatim: a deviation is *"our
fictional setting being different from the actual history and historical places it is based on"*; a map
drawing convention is *"rendering glyphs on a map which are differently scaled or differently colored than
what the features would be in order to make the map more readable and legible to human eyes."* So the
oversized wellhead, the 6 ft hokora, the stand-level bamboo glyph, the dark bund beads and a stream drawn
by rank are CONVENTIONS; a hamlet with no headman, the 6:4 dike reading and the 30 ft trunk road are
DEVIATIONS. A convention's modal note is written in the GM's form - *"Note: we have rendered the bund
beans as ... in order to make them visible on the map at this scale"* - and ends with the real size or
color from the record, or says in so many words that it was searched for and not found. Write the word
the same way in the entry, the rule file, the code comment and the map's notes: since feature 183 the
record says "a map drawing convention" wherever it used to say "a deviation for legibility".

## Every reference is a link (GM 2026-09-06, feature 190)

The GM: *"I want all of our references to be links ... Any reference to an external document which we were
able to read in order to do our research should be a link to that external document."* So a key in a
research file is never bare. Write it as a link, and the target follows from the key's CITATION LINE in
`SOURCES.html` (the entry's first paragraph, the one that names the work and its URL):

- a document we READ - the citation line carries a URL and no not-read marker - links to that URL, the FIRST
  one on the line: `` [`wang-ochiai-2022`](https://doi.org/10.1080/13467581.2021.1972810) ``;
- a document we did NOT read - the line says `SUMMARY-ONLY` or `URL: none`, or records its URL as `unfetched`
  with no `READ` beside it - links to its registry entry, `` [`ma-2024-desire-paths`](SOURCES.html#ma-2024-desire-paths) ``
  (`../SOURCES.md#...` from `cities/`), because the entry is where "we could not read it" is said, and a link
  to the page would present an unread source as a read one.

The key stays the link text (the registry, the tests and the class entries name keys). A document named in
prose without a key - *"Wikipedia 'Desire path'"* in an older `**Sources (read):**` paragraph or a body
sentence - is linked the same way, by looking its key up; and so is a citation by AUTHOR SURNAME in a finding's
body (*"Sugiura counts a firewood SHED on 0.76"*, *"that is Tabayashi's rule"*; GM 2026-09-06: *"Yes link them
too"*), at its first mention in a section, later mentions in the same section staying plain. A read document with
no entry gets one first (the `source-reader` fetches the page; the entry records the URL and the READ date) and is
never linked to a URL nobody fetched; before a key is coined the registry is searched by URL, percent-decoded, and
by the whole entry - six "unregistered" documents in feature 190 were registered under keys the prose did not
suggest. A `**Pointers, not read:**` item with no entry, a page named only as silent or unreadable, and an
unregistered summary-only or withdrawn item stay plain; a REGISTERED name is linked whatever label surrounds it.
`tests/interactive/test_sources.py` holds the rule: a bare key anywhere in a research file, a mis-targeted link,
or a duplicate `### ` heading in the registry fails the gate. The one-off conversion (459 keyed sites, 202
prose-named citations, 32 new entries; five review rounds and the GM's ruling) is recorded in
`specs/190-source-keys-are-links/`.

## A reference QUOTES the passage it rests on, and the quote is checked (GM 2026-09-06, feature 194)

The GM: *"Anytime we add a new reference in order to support something, then in our references section, we
quote the passage or passages from the reference which support the assertion that we are making. There is no
point in including a reference if it is not being quoted."* So the citation form is a FOOTNOTE that quotes:

- after the assertion, `<sup class="fn"><a id="fnref-n" href="#fn-n">n</a></sup>` - one per assertion, *"even if this means multiple footnote links per paragraph or
  even multiple per sentence in sentences which make multiple assertions"*; a sentence that rests on two sources
  carries two;
- at the page's foot, in `<section class="footnotes"><ol>`, `<li id="fn-n"><a href="url"><code>key</code></a> -
  「the quoted passage」 (an English gloss when the passage is not English; one clause on what it bears on when
  that is not plain) <a class="fnback" href="#fnref-n">back</a></li>` - the key linked by feature 190's rule, the
  passage VERBATIM from the page, or PASSAGES when one is not enough - verbatim INCLUDING the source's own spelling and dashes: the house-style guard holds quoted spans (「」, “”, a straight-quoted span in prose) out of its corrections (GM 2026-09-06: *"The house style should not normalize british spellings or em-dashes inside things we are quoting, because that requires us to edit other people's quotes"*), and a `quote-check` reports a hyphen for a dash or an Americanized spelling as `DIFFERS`. A SUMMARY-ONLY source is NOT cited (feature 195, below); the
  GM's own notes (`URL: none`) quote the note. Nothing is quoted from memory.
- the section's `<p><strong>Sources:</strong> ...</p>` roster stays (the map's modal reads it) and every key on it is quoted by at least
  one footnote in that section - a key with nothing to quote leaves the roster.

## A citation LINKS to a page where its quote can be READ - or there is no citation (GM 2026-09-06, feature 195)

The GM: *"If we are linking to online sources whose content which is quotable from public sources does not support our claims then we should not cite it. For example, even if a given source is "known" to support a point we are making, if we are not able to simultaneously quote a relevant passage with a quote which actually backs up our assertion and then link to a page on the public internet where that quote can be read, then we should NOT be claiming that the source supports us."* Two halves, both or neither: the quoted passage that backs the assertion, and a link to a page on
the public internet where that passage can be read. So a footnote is one of exactly two forms:

- **CITATION**: `<a href="https://..."><code>key</code></a> - 「passage」 (gloss)`, the link an `http(s)` page on which the
  passage can be read - the paper's public PDF rather than its abstract page, the full-text view rather than a library
  landing page, the original-language page rather than an English rendering that is on no page. A paywalled or
  login-walled text, a search summary, an abstract that does not carry the passage: none is such a page.
- **ABSENCE**: `no publicly readable source (searched YYYY-MM-DD: what was tried; the passage the record carried came from
  the registry entry key, which is no longer cited)` - no key link (not even a bare `<code>` one), no URL. The assertion stands, honestly
  labeled as resting on nothing a reader can check (constitution XII: an unlabeled guess is the one failure); the
  registry entry stays as the record of the search, marked *Not cited*.

The one carve-out, by KEY: the GM's own campaign notes (`l7r.md`, `budgets.md`; today `l7r-median-domain`) are canon,
not a source claimed to support a historical point - they keep their registry link. Nothing else is carved out: not a
`URL: none` print-only book, not a page that has gone away, not a SUMMARY-ONLY entry. This superseded the 2026-08-27
SUMMARY-ONLY citation clause (constitution v2.19.0); the 2026-09-06 sweep that brought the record under it - 780
footnotes, every one without a recorded SEEN verdict re-fetched - is `specs/195-cite-only-what-can-be-read/`.

**A page the container cannot fetch is not thereby unreadable.** mdpi.com, Wiley, Springer, ScienceDirect and others
refuse automated fetches while serving a person; when a source matters, the GM downloads it (2026-09-07: *"I can try to
download them myself as a human and then save them somewhere that you can see them"*) into `l7r/academic-sources/`,
mounted here at `/host-l7r-repo/academic-sources/`. The session reads the copy (an Opus reader per paper, passages
verbatim with page or section), the footnote links the PUBLIC page and says the copy was read, and the quote-check runs
against the copy. A paywalled full text whose abstract is public is cited for the abstract's words only. What the paper
does NOT say is written down where the claim stands - the first six papers read this way (feature 195 T07) supported
about half of what the record had attributed to them, and the rest is labeled GUESS now.

Two checks hold it. `tests/interactive/test_footnotes.py` holds the mechanical half at the gate: every reference
resolves, every definition is referenced, names a registry key and carries a quotation, and every roster key is
quoted in its section. The **`quote-check` agent** (`.claude/agents/quote-check.md`, Opus like every check agent - GM 2026-09-07, verification not
judgment - the sibling of `source-reader`) holds the half a test cannot: per footnote, is the quote VERBATIM on
the page (or DIFFERS / NOT-ON-PAGE), does it SUPPORT the assertion it is attached to (or PARTIAL /
DOES-NOT-SUPPORT), and per section, which assertions carry no footnote. Run it in the background on every new or
changed research entry before the feature lands, and record its verdicts in the feature's tasks (a physical
task's `source-reader confirmed` box is `quote-check confirmed` from here). The page renders the footnotes with
the ACOUP hover (`html/`, below): hover a reference and the note appears beside it.

## The record IS HTML - edit the page (feature 194, the GM's ruling through its spec review)

Since 2026-09-06 the record's files are `research/<name>.html` (`cities/<name>.html`, `SOURCES.html`), hand-authored
and tracked; the Markdown they were converted from is gone (the GM: *"the markdown on GitHub will no longer exist
as it has been replaced with HTML"*). A page's `<head>` carries the charset, the title and two relative links -
`assets/record.css` and `assets/record.js` (the footnote hover; `../assets/` from `cities/`) - and its body is one
`<main>`. Section ids are the record's anchors (`github_anchor` in `interactive/sources.py` - GitHub's rule, kept
when the record converted), the registry's entries are `<h3 id="<key>"><code>key</code></h3>`, and a section's
sources roster is `<p><strong>Sources:</strong> ...</p>`, which the map's modal reads. The maps' "See references"
opens these pages locally (`../../../research/<name>.html#<id>`). GitHub shows a committed `.html` as source, so
the reading path is the local page, not GitHub. `README.md` and this file stay Markdown: they are instructions,
not the record.
The mechanics of the page side - the anchor rule, the ordering, the button - are in
[`../l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md), "The references modal
lists QUESTIONS".
