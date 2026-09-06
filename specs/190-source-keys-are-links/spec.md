# Feature 190 - every source in a research finding is a link

**Status**: NOT FAITHFUL at round 5 of 5 (`spec-fidelity`, 2026-09-06) - ESCALATED TO THE GM under constitution XVI.
Round 5 returned two items: (1) the document-name pattern in FR-006 misses citation by AUTHOR SURNAME in a
finding's body (*"Sugiura counts a firewood SHED on 0.76"*, *"that is Tabayashi's rule"*, *"Wang & Ochiai surveyed
farmhouses"* - nine sites found, every one already keyed and linked on its section's Sources line), and whether
those are "references" in the GM's sense is the question the reviewer says five rounds circled without asking;
(2) the prose pass could be run with D5 switched off (an argv flag read at import) and its 122/8 split was
measured that way - FIXED: D5 is the sweep's default and the split is 119/11. Nothing is implemented; the GM's
answer to (1) decides the last surface. Rounds 1-4 returned NOT FAITHFUL (round 4's items and their fixes are in
FR-006, FR-007 and D8; rounds 1-3 below).
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessors**: feature 143 (every entry cites; every `SOURCES.md` key carries the URL where it can be
read, or `URL: none - <why>`); feature 180 (the modal's references link to the research on GitHub, so a
reader now arrives at these `**Sources:**` lines)

## Summary

A research section ends in a `**Sources:**` line naming keys - *"`wang-ochiai-2022` (the sun-side share
the heap inherits)"*. On GitHub, where feature 180 sends the reader, the key is plain code and leads
nowhere; the URL sits in `SOURCES.md`, one file away. The GM: *"I want all of our references to be
links ... Any reference to an external document which we were able to read in order to do our research
should be a link to that external document."*

The GM's rule has two halves and this spec follows both: EVERY reference becomes a link, and the link goes
to the DOCUMENT when the document was read. A reference here is either a registry KEY (459 sites) or a
document NAMED IN PROSE without a key (ten source-attribution paragraphs and about forty body mentions). The
"which we were able to read" qualifier is what decides the target: a document the registry records as not
read links to the registry entry that says so, never to a page nobody read.

Measured before writing this (`SOURCES.md`, 333 entries after D6's merge): a `URL: none` key (the GM's own
notes) and 17 keys whose CITATION LINE says SUMMARY-ONLY; 15 more whose citation line records the URL as
`unfetched` with no READ against it (D5); 300 whose citation line carries a URL and no not-read marker,
which under the registry's own rule (a key is added only after the source is read, SUMMARY-ONLY otherwise)
is what a read document looks like - most say READ with a date, the pre-143 ones do not.

## Functional requirements

- **FR-001** In every research file, EVERY backticked registry key MUST be a markdown link - in a
  `**Sources:**` paragraph and in a finding's prose alike (the GM: *"all of our references"*; the round-1
  review measured 23 inline citations such as *"up to ~1 m - `kojodan-dobei`"* in 7 files that a
  Sources-line-only rule would have left as plain code, the defect verbatim). The target is decided by the
  entry's CITATION LINE - the first paragraph of the `` ### `key` `` entry, the line that names the work
  and its URL; never by the `*Used for:*` notes below it, which can say SUMMARY-ONLY about a DIFFERENT
  claim drawn from a read document (the round-3 review's finding: 27 keys by the whole entry, 17 by the
  citation line - 10 read documents would have been sent to the registry):
  - a key whose citation line carries a URL and no not-read marker - a document we READ - links to that URL:
    `` [`wang-ochiai-2022`](https://...) ``. The FIRST URL on the citation line is the document (D2).
  - a key whose citation line says `SUMMARY-ONLY`, or `URL: none`, or records its URL as `unfetched` /
    `not fetched` with no `READ` beside it (D5), links to its registry entry - `SOURCES.md#<key>`
    (relative: `../SOURCES.md#<key>` from `cities/`) - because we did NOT read that document and the
    entry is where that is said; linking it to the page would claim a reading that never happened.
- **FR-002** The key text stays the backticked key, so nothing that reads these lines changes:
  `interactive/sources.py`'s `section_sources` finds keys by their backticks and already accepts the link
  form (its test has `` [`b-2`](SOURCES.md#b-2) ``), the SOURCES.md anchors are the GitHub anchors of the
  `` ### `key` `` headings (backticks are stripped by the slugger, so `#wang-ochiai-2022`), and the modal's
  question links are untouched.
- **FR-003** The 86 keys already linked to `SOURCES.md` are re-pointed by the same rule: a READ key's link
  goes to the document. The registry entry stays reachable - `research/CLAUDE.md` and the modal's chain
  point at `SOURCES.md` - but the GM asked that the reference lead to the document.
- **FR-004** The keyed sweep is SCRIPTED, never retyped, and nothing but the link wrapping changes: the prose
  around a key, the parenthetical notes, the order. The search space, stated by MECHANISM so the count can
  be re-derived: the 18 `.md` files under `research/` including `cities/`, excluding `SOURCES.md` itself,
  `README.md` and `CLAUDE.md` (FR-007); the TOKENIZER is every backticked span matching
  `` `[a-z0-9][a-z0-9-]*` `` whose text equals a `` ### `key` `` heading of `SOURCES.md`, whether bare or
  already inside `` [`key`](...) ``; a backticked token that is not a heading (`paddy`, `low`, `w` - 42
  distinct, printed by the dry run) is not touched. Measured by the sweep's dry run under FR-001's rule:
  **459 sites** - 373 bare keys (355 in a Sources paragraph, 18 in prose) and 86 already linked; **418
  become links to a document, 41 to a registry entry** (33 keys: 18 SUMMARY-ONLY or `URL: none`, 15
  `unfetched` without READ), and 70 of the 86 re-point. (The round-3 review counted 370 bare keys; the
  three-key difference is the tokenizer - a token counted once per site here, and heading-matched rather
  than Sources-line-matched - and the number that binds is the dry run's, re-derivable by the stated rule.)
- **FR-005** A test holds the rule from here on, over the same surface as FR-004: in every research file,
  every backticked registry key is inside a markdown link; a READ key's target is the first URL of its
  citation line; a not-read key's target is its registry anchor. A new entry or a new inline citation
  written with a bare key fails the gate. The test imports the same classifier the sweep used, so the rule
  has one body.
- **FR-006** **The documents named in PLAIN PROSE, with no key, are in scope - over a DERIVED surface, with a
  verdict recorded for every candidate.** Round 4 found the surface written out by hand (ten paragraphs, six
  files); it is now derived by the mechanism `surface190.py` states and re-runs: over the same 18 files as
  FR-004, (a) every Sources paragraph - any spelling, `**Sources:**`, `*Sources:*`, `- Sources:`,
  `**Sources (read):**`, bare `Sources:` - that carries NO registry key, or whose text with its keyed tokens
  removed matches the document-name pattern; (b) every other line matching that pattern. The pattern names the
  ways this record names a document: `wikipedia`, `kotobank`, `PMC <n>`, J-STAGE, a bare domain
  (`nakasendoway.com`), JAANUS, Britannica, MDPI, Springer, Nature, Cambridge, Wikisource, archive.org, NDL,
  MAFF, MLIT, FAO, IRRI, JSIDRE, NIES, AAS, ResearchGate, EUNIS, Wiley, ScienceDirect, doi.org, Grokipedia,
  `museum`, `Institute`, `library`, `et al`, and the token `READ`. Measured: **356 candidates** - 35
  keyless Sources paragraphs, 98 keyed Sources paragraphs that also name a page in prose, and
  223 body lines, across 13 of the 18 files. **Every candidate carries a verdict in the script's table,
  and the script fails on a candidate without one or a verdict without a candidate**, so the surface cannot
  drift from the table. The verdicts, by class:
  - a code, no document to link - 163 `status` (READ or "read" as a status word or verb: *"the
    category and its penalties are READ"*, *"reads as a brook"*), 15 `unnamed` (a page referred
    to and not named: *"the page read gives"*), 25 `linked` (already a markdown link to the
    document), 4 `keyed` (the document is the registry key on the line, which FR-001 links),
    9 `internal` (a pointer into this repository - `budgets.md`, a spec), 11 `none`
    (*"Sources: none - a rendering rule"*), 2 `repeat` (the same document named again in the
    paragraph where it is already linked), 1 `notread` (a pointer not read, no name to record);
  - or a list of NAME rows, each asserted to occur exactly once in its paragraph or line. Three treatments:
    - (i) **registered under a key the prose does not name** - **130 link sites** (*"Wikipedia 'Desire
      path'"* is `desire-path-enwiki`, *"an Okayama museum"* is `yonekura-mushiro`, *"the Himeji page"* is
      `himeji-shironameshi-jawiki`). The NAME becomes the link text, wrapped in place, with FR-001's target rule
      (119 to the document, 11 to a not-read entry - measured with the same D5-on classifier as FR-004, which is now the sweep's default so the two passes cannot disagree about one key; round 5, item 2). A
      registered name is linked WHATEVER the sentence says about it - in a `**SUMMARY-ONLY:**` or
      `**Withdrawn:**` list, in a "not re-read" note - because the citation line, not the label around the
      name, decides read-ness (round 4, item 3: `326-woods` sat under SUMMARY-ONLY while its entry says READ
      with a URL; `Boso-no-Mura firewood placement` under Withdrawn - a claim withdrawn, not a document unread).
    - (ii) **read, but not registered** - 32 documents sent to the `source-reader` on 2026-09-06 with the claim
      the record attributes to each: **24 READ** (a new entry: key, citation line with URL and READ
      date, *Used for:*; the name links to the URL - 30 sites), **6 SUMMARY-ONLY** (a new entry
      labeled so; the name links to it - 6 sites): the Kanto Gakuin tsuijimatsu column (404), the MLIT
      「扇状地と人々の暮らし」 PDF (did not render), the Tedori fan paper (Springer login), the Sendai igune
      species PDF (did not render), Minami/Yonezawa/Okaze 2022 (abstract only, and the abstract does not
      carry the north/west siting), Ushijima 2020 (Wiley, ResearchGate and DOAJ all 403). Three results
      CORRECT the record and are recorded in the entry and reported to the GM, the link still made: JAANUS
      "yashikimon" defines a WARRIOR'S gate (the record's own body line at `homesteads.md:490` already says
      so); ja.wikipedia 農業全書 gives 1697 where the record says 1696, and does not mention night soil; the URL
      the record calls "FAO's basin-irrigation manual" is FAO's rice-fish culture chapter - the "dry bund"
      quote is on it, the name is wrong. Six more documents sent to the reader turned out ALREADY registered
      under keys the prose does not suggest and are (i), not (ii) - D7.
    - (iii) **the residue** - **2 NOT-FOUND**, 3 sites: the Tonami Scattered-Village Research
      Institute's 1996 model homestead (searched in Japanese for the institute, its 1996 publications and the
      figure; general pages only) and the J-STAGE study of Kishū multi-hamlet villages (five searches on
      J-STAGE and the geography journals; nothing tied to Kishū). Each stays plain and gains *"(URL not
      found 2026-09-06)"*. Nothing is guessed at: a URL is written only after the page was fetched.
    - and **75 names recorded and left plain**, each a `plain` row so the decision is on the record: a
      `**Pointers, not read:**` item with no entry (*"Britannica 'Paddy'"*, *"Kids Web Japan"*), a page named
      only as silent, 404, unreadable or a disambiguation (*"zh.wikipedia 圩田 silent"*, *"ja.wikipedia 外濠 is a
      disambiguation page"*), an unregistered summary-only or withdrawn item (*"japaaan 五右衛門風呂"*, *"MAFF
      persimmon"*), and the two Grokipedia mentions that record a WITHDRAWN citation. These are the
      round-4 reviewer's own three unlinked classes; nothing read with a URL is among them.
- **FR-006b** `research/CLAUDE.md` gains the rule in one paragraph (a source is cited by key AND the key is
  written as a link; which target; a document named in prose is linked the same way; the test).
  `research/README.md`'s entry template (line 44, `` **Sources:** `key`, `key` ``) is the GM's to edit
  (constitution XVII) and is reported.

### What this feature does not do

- **FR-007** It changes no finding's meaning, no citation text beyond the link wrapping and the (iii)
  parenthetical, no modal, no map. It invents no URL. What stays unlinked, on the GM's own qualifier *"which we
  were able to read"*: a `**Pointers, not read:**` item, a searched-and-not-found or page-was-silent note, and
  a `budgets.md` or spec pointer - WHEN the document has no registry entry (a registered one is linked by
  FR-001's rule wherever it stands, D8). `**SUMMARY-ONLY:**` and `**Withdrawn:**` labels decide nothing by
  themselves (round 4, item 3). Boundaries: `SOURCES.md`'s own prose (the re-sourcing queue and the `*Used
  for:*` lines name keys) is left as it is, because a key named there refers to an entry in the same file the
  reader is already in, and the entry carries the URL - which GitHub renders as a link by itself; `README.md`'s
  template is the GM's (FR-006b); the directory `CLAUDE.md` names keys only as examples of the form.

## Decisions Recorded

- **D1 - a not-read key links to the registry, not to the document.** The GM's words are *"which we were
  able to read"*; a SUMMARY-ONLY or unfetched entry records that we could not, and the registry entry is
  where that is said. Linking it to the page would present an unread source as a read one - constitution
  XII's one named failure in another form. Cost: 41 sites link one hop short of the document; each such
  entry carries the URL in its text for a reader who wants to try.
- **D2 - the first URL on the citation line is the document.** A few entries carry more than one URL (a
  page and a mirror, a paper and its publisher); the first is the one the citation opens with and the one
  the entry was written from. Recorded so the choice is a rule, not a coincidence of order.
- **D3 - the key stays visible as the link text.** `[wang-ochiai-2022](url)` rather than the title: the key
  is what the registry, the tests and the class entries name, and a reader who wants the full citation has
  the registry one hop away. Replacing the key with a title would be a second edit to every line and would
  break the parser's contract. A prose-named document keeps its NAME as the link text for the same reason -
  the text is what the record says; only the wrapping is new.
- **D4 - the prose-named documents are done here, by lookup, and only the measured residue is left plain.**
  Replaces round 3's blanket deferral. Declined: registering keys for them from the prose alone (a key with
  no read behind it - the failure feature 143 exists to prevent); dropping the surface from the spec (a rule
  stated by class cannot be satisfied by a sweep over a token); and a deferral "to a second pass" (priced at
  the hardest member - the round-3 review). The body mentions are INCLUDED, not argued away: an argument
  that the Sources line is "the" reference and a body mention only a marker is exactly the carve-out
  constitution XVI presumes wrong, and the GM's *"any reference"* does not make the distinction.
- **D5 - `unfetched` with no READ is not read.** Fifteen citation lines record their URL as `unfetched
  2026-08-28` and carry no READ marker: feature 143's re-sourcing pass recorded the address without fetching
  the page. The same qualifier that governs SUMMARY-ONLY governs these - the record does not say we read the
  document, so the link goes to the record. Where a citation line says both (`artic-pigsty-latrine`: the
  catalog text READ through the museum's API, the page itself `unfetched`), the READ governs and the link
  goes to the document. Cost: 15 keys, 22 sites, one hop short; the alternative - treating "we have the URL"
  as "we read it" - is the claim the GM's qualifier forbids.
- **D6 - two duplicate registry entries were merged; the first entry wins.** `kagawa-tameike-structure`
  and `yashikirin-jawiki` each had two `### ` headings (the second added by a later feature's pass), which
  gives one anchor two bodies and the sweep two citation lines to choose from. The first entry is kept
  (its citation line is the one the earlier findings were written from) and the second's *Used for:* is
  appended to it as *"Also (a second entry under the same key, READ again <date>, merged here by feature
  190)"*, so nothing recorded is lost. Found by the round-3 review; a check for duplicate headings joins
  FR-005's test.
- **D7 - a name is looked up by URL as well as by name before a key is coined.** Six of the 26 documents
  sent to the reader turned out to be registered already, under keys the prose does not suggest
  (`edago-ja`, `kokudaka-en`, `ndl-hongo-edago`, `pmc5723622-bamboo-range`, `saijo-mizu-rekishikan`,
  `nabunken-azemame`). A second entry for the same URL is the D6 duplicate in another form - two anchors
  for one work - so T01c refuses a new key whose URL (percent-decoded) already stands in an entry, and links
  the name to the existing key instead. Cost: six reader fetches that only confirmed what the registry held.
- **D8 - a registered name is linked wherever it stands; a label around it decides nothing.** Round 4 found
  `326-woods` under a `**SUMMARY-ONLY:**` label with an entry saying READ, and `Boso-no-Mura firewood placement`
  under `**Withdrawn:**` with an entry saying READ. The labels describe the CLAIM's fate; the citation line
  describes the DOCUMENT, and FR-001 already decides by the citation line. So the rule is monotone: registered
  -> linked (to the document or to the entry, by the citation line); unregistered and read with a stated fact
  -> the reader, then an entry; unregistered and named only as unread, silent or withdrawn -> a recorded
  `plain` row. Declined: excluding by label (round 3's FR-007), and registering the unread pointers as
  SUMMARY-ONLY entries to give them a link (feature 143's queue owns that; a link to "we could not read it"
  adds nothing for the reader that the sentence does not already say).
