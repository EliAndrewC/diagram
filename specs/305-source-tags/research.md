# Feature 305 - research (Phase 0)

Every figure here was observed 2026-10-02 in the clone `diagram-organization` at `main` 35610506e (method: a
one-shot extraction of every file in `research/sources/010-works-cited/` into the session's scratchpad, each entry's
key, citation line, first URL and its three write-ups, then counted). These are one-shot observations, not harness
measurements: the migration consumes them once.

## R1 - What the registry holds

- 2,126 entry files (observed 2026-10-02; method: file listing). 45 have no "What it is" or "Why it applies" yet;
  those are entries no question cites (the build refuses a cited one without a write-up, feature 211), and they are
  tagged like the rest.
- 16 entries name `l7r.md` or `budgets.md` on their citation line (observed 2026-10-02; method: grep). They are the
  canon entries `sources.canon_keys` already recognizes.
- 19 entries carry no URL (observed 2026-10-02; method: extraction).
- "Why it applies, and its limits" totals 1,249,774 characters, mean 587 per entry (observed 2026-10-02; method:
  extraction). The repetition the GM named is measurable. The word "tertiary" appears in 651 of them, "modern" in
  623, "encyclopedia" in 340, "Meiji" in 179, "touris(t/m)" in 51, "promotional" in 22, "present tense" in 15
  (observed 2026-10-02; method: case-insensitive regex over the paragraph).

**Decision**: the trim is worth doing across the whole registry. About a third of the limits paragraphs carry the
reference-work caveat alone.

## R2 - How much a URL alone decides

The leading hosts (observed 2026-10-02; method: host of the first URL on the citation line): ja.wikipedia.org 436,
kotobank.jp 242, en.wikipedia.org 157, zh.wikipedia.org 149, zh.wikisource.org 54, jstage.jst.go.jp 53,
online.bunka.go.jp 27, fao.org 22, crd.ndl.go.jp 15.

A host decides the KIND for about 1,000 entries: the Wikipedias, kotobank (a dictionary aggregator) and baike are
reference, and wikisource is primary. It decides neither PERIOD nor REGION: a Japanese Wikipedia article may be about a
Chinese city wall, and an article on Edo moats is premodern evidence even though it was written this decade.

**Decision**: every entry is classified by reading its write-up. The host is given to the classifier as a hint and
used afterward as a consistency check: a Wikipedia entry not tagged `reference` is listed for a second look. No entry
is tagged by host alone.

**Alternative rejected**: tag kind by host and only period and region by reading. Rejected because a reading is needed
for every entry anyway, and kotobank sometimes serves a primary text or a museum's entry, not a dictionary.

## R3 - Who classifies, and how it is checked

Most write-ups state the era and the place of their evidence in prose ("a 1771 house register of Kamikanai village",
"a modern tourism page"), so classification is reading, not research. No page is fetched.

- **Classifier**: ad-hoc Sonnet agents (CLAUDE.md: `sonnet` to read and extract), each given a batch of about 100
  entries as compact JSON, the vocabulary with its explanations, and the rules in this file's R5. That makes 22
  batches. Each returns, per key, the three facets (primary first) and the trimmed limits paragraph (R4).
- **Check**: SC-004 and SC-005, an independent `source-applicability` pass (Opus, its pinned tier) over a stratified
  sample of at least 60 entries covering every period and region value. Any error pattern it finds is swept across
  the whole registry by rule.
- **Mechanical checks first**, by script: every value is in the vocabulary; every non-canon entry carries all three
  facets; Wikipedia, kotobank and baike entries are tagged reference (else listed); an entry whose write-up names a
  year in 1868-1955 together with Japan, or contains "Meiji", "Taisho" or "Republican", and is tagged premodern is
  listed for a second look.

**Accepted limitation** (session's decision, recorded per CLAUDE.md): `source-applicability` is owed on "every new or
changed write-up", and the trim changes most of 2,126. Running it on all of them would cost about 2,126 Opus
judgments, each fetching its source. The trim only REMOVES text that restates a label, and the label now carries that
limit, so the honesty judgment the agent exists for is unchanged in substance. The 60-entry stratified sample, plus
the mechanical no-new-content check of R4, stands in for the full pass. Alternatives priced: the full pass (about 2,126
judgments); a sample of one entry in ten (213 judgments). The 60-entry sample was chosen because it covers every value with several
entries each, and SC-004 sweeps any pattern it finds across the whole registry.

## R4 - The trim, mechanically held to FR-015

The classifier returns each limits paragraph trimmed, or `null` where nothing in it only restates a label. A script
applies a trim only when all of these hold, and lists every refusal for the session to do by hand:

1. The new paragraph is no longer than the old.
2. **No new content**: every word of the new paragraph occurs in the old one, apart from a short list of connectives
   ("and", "but", "its", "it", "the", "that", "this", "is", "are", "for", "of", "a", "an", "to", "in", "on", "as",
   "so", "only", "which", "here", "used") and changes of case and punctuation.
3. The inline markup the old paragraph carried survives: every `<em>`, `<code>`, `<a ...>` and `<span ...>` it kept
   text from is still there, and no HTML comment is lost (session notes stay).
4. The paragraph still says why the source applies: it is not empty, and its first sentence is kept unless that
   sentence only restated a label.

## R5 - Classification rules (given to every classifier verbatim)

- **Period follows the evidence the record takes from the work**, as its "Used for" line shows, not the publication
  date. If the evidence is from several periods, list each, the one most of the uses rest on first.
- **Cut-offs by region** (FR-003): the table in plan D3, for every region value, verbatim in the batch prompt and in
  the period explanations. A source the table does not settle is not tagged by the classifier's own judgment: it is
  listed (`"unsettled": "<why>"`), and the session extends the explanation before tagging it.
- A present-day source DESCRIBING a premodern thing (a museum page about an Edo farmhouse, a preserved Edo terrace):
  premodern when the record takes the premodern form from it, present day when it takes present-day counts or the
  present working landscape.
- **Not period-bound**: botany, hydraulics, materials, physical facts.
- **Region** is where the evidence is from. Ryukyu, Taiwan and Vietnam are `east-asia-other`; a work about no one
  place is `general`.
- **Kind** is the publication: `primary` (period documents, gazetteers, registers, treatises, period maps; a modern
  edition or translation of one is still primary), `scholarship` (peer-reviewed, academic books, theses, excavation
  reports, specialist dictionaries' signed scholarly entries are reference), `reference` (encyclopedias, Wikipedia,
  dictionaries, kotobank), `institutional` (museums, ministries, prefectures, preservation societies, FAO, university
  public pages), `popular` (blogs, tourism, travel, news, commercial sites).
- **Canon** entries (the citation line names `l7r.md` or `budgets.md`) get no tags.

## R6 - Where the tags live (FR-005)

**Decision**: a marker on the entry's LAST line, `<!-- tags: period=present-day; region=japan; kind=popular -->`, the
grammar feature 303 gave questions (`<!-- tags: subject=...; setting=...; level=... -->`).

- An HTML comment is never shown raw, and a grep for `tags:` finds it.
- It goes LAST rather than under the heading because `sources._ENTRY_HEAD` (canon detection) and feature 211's
  migration read the citation line as the paragraph directly after `</h3>`, and the stub `make reserve` writes keeps
  that shape.
- The builder strips the marker from what it shows and renders the labels in its place, under the heading.

**Alternative rejected**: a `data-tags` attribute on the `<h3>`. Every registry regex matches `<h3 id="...">` exactly
(`_ENTRY_BLOCK`, `registry_keys`, the bundle hooks), and widening all of them buys nothing.

## R7 - The record's build today (what changes)

- `citations.works_html(keys, entries, rel)` renders a question page's "Works cited here" in first-citation order.
  Its only caller is `record/site.py` `Build._works`.
- `Build._registry` writes `sources/<key>.html` with a pager in registry order, and `sources/index.html` listing each
  registry group's entries.
- `Build._single` writes the registry part of `all.html`, group by group, each entry's fragment in registry order.
- The tooltip box `#fntip` in `research/assets/record.js` already serves footnotes and glossary terms. The labels
  reuse it: a `span` with `data-def` gets the same hover handler, and a `title` attribute is the no-script fallback.
