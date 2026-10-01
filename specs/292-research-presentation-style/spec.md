# Feature 292 - how a research section is presented

**Feature**: 292-research-presentation-style | **Created**: 2026-09-29 | **Status**: Sweep (the pilot signed off by the GM, 2026-09-30)
**Input**: the GM's request, verbatim in [`request.md`](request.md).

## Summary

The research record is organized one section per question asked, and many of those questions arose mid-session, so
their headings read as session artifacts and one topic is scattered over several sections. The GM asks for a
STYLE GUIDE and a CHECK that holds it: a section is a TOPIC with a plain-English title; it opens with a short
plain-English account of what the thing was and why it existed; its findings follow as short bullets, each led by a
bold line of its own - a Q&A-style question or a plain statement of the point; framing, restatement, and statements
that say nothing about the thing or the research but only what the map visibly shows are cut; unfamiliar terms are glossary tooltips; there is no `Sources:` roster and no quotation of the GM's inciting
question. Two mechanical changes come with it: a footnote tooltip's source link goes to the work's entry on the
citations page, not to the source; and a section's sources are read from its footnotes once it has no roster.

The feature runs in two phases. **Pilot**: write the guide and the check, rewrite one topic (the homestead grove),
and iterate topic by topic with the GM until they sign off on the guide and the check. **Sweep**: only after that
sign-off, tasks are added to rewrite every other section of the record in the style. Nothing lands on main during
the pilot; the GM reads the pages in this feature's clone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A written style guide MUST state the presentation rules generalized from the GM's worked example -
  the topic title, the opening paragraphs, the bullet form (a bold lead line of its own - a question or a plain
  statement of the point - and a lead-in sentence where the bullet needs context or a reason it is relevant), one
  finding per bullet, an aside carrying real content taken out of its parentheses and made its own bullet, what is cut
  (framing that the whole record presumes, restatements of a number already given, a statement that says nothing
  about the thing or the research but only what is visible on the map - while a statement of HOW the map draws
  something, and why, is kept), when prose is left as prose, and a glossary tooltip preferred to a lead-in for a term
  used in many places - each rule with the GM's words it comes from.
- **FR-002**: Sections that cover one topic MUST be merged into one section under a plain-English title naming the
  topic, organized for a reader who knows nothing of it: the account of what the thing was and why first, then the
  findings in the order a reader needs them - never one section appended after another.
- **FR-003**: A restyled section MUST carry no `Sources:` roster, and removing a roster MUST lose no citation: every
  key the roster named is cited by a footnote of the section, and every passage the roster's own footnote quoted is
  quoted by a footnote in the section, and any information the roster states that the section does not state
  elsewhere is carried into the section's text.
- **FR-004**: A section's sources, as the map's references read them, MUST be derived from the keys its footnotes
  cite when it has no roster.
- **FR-005**: The source link inside a footnote's hover MUST lead to that work's entry on the page's citations page
  (`citations/<page>.html#work-<key>`), which itself links the source; every link that leads to the citations page -
  that one and the footnote number itself - opens in a new tab (GM 2026-09-29: *"links to citations should open in a
  new tab"*).
- **FR-006**: The guide MUST say the GM's inciting question appears nowhere in a section. The practice of quoting it
  was never written as a rule (a search of every rules file, agent, template and test found none - 44 `The question`
  paragraphs, all on the water page, follow it), so there is no rule text to strike; removing the quotations is the
  sweep's work.
- **FR-007**: "knob" MUST be a glossary term whose definition says what the GM said a knob is (the settings the
  generator varies to show the ways settlements differ - by chance, by region, by the lie of the land), and "canopy
  tree" MUST be a glossary term whose definition carries the context of the GM's lead-in: a tree with a large crown of
  leaves, which the maps draw one crown at a time at its real size, unlike bamboo, drawn by a convention.
- **FR-008**: A check agent MUST judge a section against the guide - one verdict per rule, with the passage and the
  fix - pinned to a tier, launched without the repository's CLAUDE.md files, reading a bundle.
- **FR-009**: The pilot's first topic MUST be the homestead grove: the scale section the GM quoted, the section on
  the grove before 1868 that it links to, and the section on which sides of the house the grove took (split from the
  second by feature 291), folded into one section titled for the reader.
- **FR-010**: A merge MUST keep every finding, label (accurate / deviation / convention / GUESS), GM ruling, spec
  rule and footnote of the sections merged, except what the guide cuts by name; every link into a merged section MUST
  be re-aimed at the new anchor.
- **FR-012** (GM 2026-09-29, the review of the first pilot): the bullet list is named **lead-line bullets**, not Q&A;
  a lead line is a one-sentence summary of its bullet - a declarative statement for a straightforward fact, a question
  for a finding that is complicated, a range or approximation, an educated guess or a conclusion from thin sourcing -
  and makes sense to a reader who has read only what comes before it. The check MUST rule on every lead line.
- **FR-013** (GM 2026-09-29): a metric figure in the record's own prose MUST carry its conversion to feet, rounded to
  the nearest foot with a tilde, in parentheses; a quotation is never converted. A script MUST list every metric figure
  in a section's own prose that lacks one, and the check MUST report each as a failure.
- **FR-014** (GM 2026-09-29): no research section, and no map modal, shows a GM ruling - no "the GM ruled", no quotation
  of the GM, no "the GM accepted". The decision is told as the project's choice and why, in terms of the history
  (which forms existed, which the evidence suggests were commoner, how the maps render that variety, and which shares
  are arbitrary); the ruling, its date and words are kept for later sessions in an HTML comment beside it. The prepass
  MUST list every visible "GM", and the checks (`record-style`, `record-format`) MUST report it. The sweep carries this
  to the 111 research sections and every map modal that shows one (19 modals when the sweep closed).
- **FR-015** (GM 2026-09-29): number follows the map - a feature a map has one of is singular, one it has many of
  plural ("a map's groves"); the guide states it and `record-style` checks it.
- **FR-016** (GM 2026-09-29, DEFERRED to after the sweep): a section a reader could mistake for another opens with
  *Not to be confused with:* - each entry the other section's final title, linked, and the record's definition of it.
  The pairs are data kept once, always two-way (a pair declared once yields both entries), and the list is written by
  `make record`; a test fails on a pair naming a section that does not exist. It waits for the sweep because the
  titles it links are not final; until then each restyle records its pairs in `confusables.md`.
- **FR-017** (GM 2026-09-29): how the maps draw a thing is a section of the RENDERING collection
  (`research/rendering/<page>.html`), never part of the research section; each rendering section declares the research
  section it is about once, and `make record` writes a link under both headings; a declaration naming a missing
  section refuses the build. The grove topic's map bullets and its rule of the map moved there.
- **FR-018** (GM 2026-09-29): no paragraph, and no bullet's own text, runs over 150 words - a mechanical check in the
  style prepass; the rule of the map becomes a (nested) list.
- **FR-019** (GM 2026-09-29): the question-size cap counts prose only; the quote-check is handed a large question's notes
  in bundles of at most 12,000 bytes; `record-style` (except in a merge audit) and `entry-drift` are not handed notes.
- **FR-020** (GM 2026-09-29): a translated quotation's original is stored apart from its note (`NNN-<id>.originals.html`),
  moved there by `make record` from a note written inline, put back by the assembly, and shown collapsed behind a click
  in the hover and on the citations page; no check but `translation-check` reads an original, and that check runs only
  on the pairs `make translation-owed` names (new or changed since the merge base). The whole record is converted - a
  conversion proved lossless: every assembled page, the originals' wrapper removed, equals its bytes before.
- **FR-021** (GM 2026-09-29): the link between a research section and its rendering section sits on the heading's own
  row, floated right, and reads "How it's drawn" (back: "The history behind it"); a heading's text never includes it.
- **FR-022** (GM 2026-09-29): English is presumed - "(the source's own English)" is struck from the record - and this
  project is presumed the translator - `(translated from the <language> by this project; original:` becomes
  `(translated; original:`; a translation by anyone else, or one that says more than its language, keeps its words. A
  test fails on either retired form.
- **FR-023** (GM 2026-09-29): a lead line and its body stand on their own for a reader who skims: a year or concept the
  bullet leans on is explained in the lead line or is a glossary tooltip ("1868" is one); the prepass lists every year
  in a lead line and whether the glossary defines it, and `record-style` rules on it.
- **FR-024** (GM 2026-09-29): a footnote quoting several passages is shown as a list - flat for siblings, nested under a
  passage that introduces others - written by the assembly with the separators kept, hidden, so the page's text is
  unchanged.
- **FR-025** (GM 2026-09-29): an absence note opens, for its reader, with "Our research of publicly-available sources
  couldn't find anything conclusive:", kept in ONE place (`record/absence.py`) and put in place of the note's marker by
  the assembly; the search's date and terms are an HTML comment; what was found is visible, a (nested) list where it is
  several things; no untranslated foreign word stands in our own text. The prepass lists old-form absence notes and
  foreign script in our words; `record-style` and `record-format` report them. The grove topic's six are converted; the
  other ~720 are the sweep's.
- **FR-026** (GM 2026-09-30): a claim of what a page we could not read says does not stand - it is read and quoted, or
  removed with its history in a comment; the style prepass lists every sentence resting on an absence note, and
  `record-style` rules on each. The work-yard topic's three such claims (the Kodaira yard, the Akishima lot band, the
  Genroku house plots - all from feature 134's pass of 2026-08-28, before the read-and-quote rules) are removed; the
  Kodaira page, which a person can open, is on the GM's download list (no. 302).
- **FR-027** (GM 2026-09-30): kanji in our own words takes one form, `漢字 (romaji, "English meaning")`, and the style
  prepass fails any other; a gloss whose characters or meaning changed is owed a `translation-check`.
- **FR-028** (GM 2026-09-30): no glossary variant is a common English word ("are" wrapped as the land unit); a gate test
  holds it - the term keeps its unambiguous forms ("ares") or is matched only as written.
- **FR-029** (GM 2026-10-01): every map modal's references point at the sections as they now stand - each title a modal's
  `Entry:` quotes names a section that exists, held by a test over every title, not only every entry - and the
  references box opens with "Topics we researched for this map feature:".
- **FR-011**: The GM's sign-off on the guide and the check MUST be an open task, and the sweep's tasks MUST NOT be
  written or started before it is ticked.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-006): the guide exists, each rule carries the GM's words or says it is the session's
  inference awaiting the GM, and it says the inciting question appears nowhere.
- **SC-002** (FR-002, FR-009, FR-010): the grove topic is one section with a plain-English title; the three old
  anchors resolve to nothing and nothing links to them; a diff of footnote keys and labels before and after shows
  each one kept or cut by a named rule.
- **SC-003** (FR-003): a test fails on a restyled section whose roster key or roster-footnote passage is quoted by
  no footnote of the section - proved by seeding one.
- **SC-004** (FR-004): a unit test derives a roster-less section's sources from its footnotes.
- **SC-005** (FR-005): a unit test shows the hover's key link aimed at the work's entry on the citations page.
- **SC-006** (FR-007): both terms are in the glossary and wrap on the restyled section.
- **SC-007** (FR-008): the check, run on the grove section as it stood before the rewrite, finds the faults the GM
  named in their example; run on the rewrite, it finds none it cannot justify.
- **SC-009** (FR-012): the updated check, run on the grove section as it stood before the GM's review, names the
  "before 1868" lead line and the lead lines in the wrong form; run on the revision, it finds none.
- **SC-010** (FR-013): a unit test proves the prepass lists an unconverted metric figure in the prose and never one in a
  quotation, a comment or with its conversion beside it.
- **SC-008** (FR-011, spec-wide): the tasks file ends the pilot in an unticked GM sign-off task.
- **SC-011** (FR-014): the style prepass lists "GM" in a section's visible text, with its test, and its list is empty on
  every restyled section; `tests/interactive/test_modal_no_gm.py` fails on any map modal whose visible text (its What,
  Why, Note, Caveat or Name) names the GM; `record-style` and `record-format` report a visible "GM".
- **SC-012** (FR-015): `record-style` rule 9a judges number against the map; every restyled section passed it in its
  check session.
- **SC-013** (FR-016): `research/confusables.json` holds the pairs once; `tests/interactive/test_confusables.py` fails on a
  pair naming no section, a pair listed twice, or an assembled page missing either entry of a pair.
- **SC-014** (FR-017): every rendering section declares the research section it is about; `tests/interactive/test_xref.py`
  proves the links are written both ways and that a declaration naming no section refuses the build.
- **SC-015** (FR-018): the style prepass lists a paragraph over 150 words, with its test; its list is empty on every
  restyled section.
- **SC-016** (FR-019): `scripts/check-question-size.py` counts prose only, and `make check-bundle ... FOR=quote-check`
  splits notes into bundles of at most 12,000 bytes, each with its test; `record-style` (but for a merge audit) and
  `entry-drift` are handed no notes (`tests/tooling/test_check_bundle.py`).
- **SC-017** (FR-020): `tests/interactive/test_originals.py` proves an original is moved apart by `make record` and put
  back by the assembly; the browser test (`tests/full/interactive/page_browser/test_synthetic.py`) proves it is hidden
  on the page and in the hover and shown by its toggle.
- **SC-018** (FR-021): the browser test places the heading's link on the heading's own row, floated right.
- **SC-019** (FR-022): `tests/interactive/test_footnotes.py` fails on "(the source's own English)" or "translated from the
  ... by this project" anywhere in the record.
- **SC-020** (FR-023): the style prepass lists the years in lead lines and `record-style` rule 5c judges them, with its test.
- **SC-021** (FR-024): `tests/interactive/test_passages.py` proves a multi-passage note renders as a list, nested where a
  passage introduces others, and the page's text unchanged.
- **SC-022** (FR-025): `tests/interactive/test_absence.py` proves the one opening sentence is written in place of the
  marker from one place, and the prepass lists an absence note in the old form.
- **SC-023** (FR-026): `record-style` rule 9c and the prepass's list of sentences resting on an absence note judge a claim
  about an unread page; no such claim is left (the closing pass and the sweep's checks).
- **SC-024** (FR-027): the style prepass lists kanji in our own words without its `(romaji, "meaning")` gloss, with its
  test, and `make translation-owed` lists a changed gloss.
- **SC-025** (FR-028): `tests/interactive/test_record_format.py` fails on a glossary variant that is a common English word.
- **SC-026** (FR-029): `tests/interactive/test_entry_titles.py` fails on any quoted title that names no section, and
  `tests/interactive/test_page.py` holds the references lead-in.

## Decisions Recorded

- **Two phases in one feature**, as the GM proposed: the pilot's tasks, the sign-off task, and the sweep's tasks
  added only after it. Nothing is pushed to main during the pilot - the GM inspects the pages in
  `.clones/diagram-reorg`.
- **The third grove section is folded in too.** The GM named two sections; feature 291 has since split the second,
  moving its shape half into "Which sides of the house did a homestead grove take?". Folding only two would leave the
  grove on two sections for no reason the GM would accept, so all three are folded.
- **Built on feature 291's text.** Feature 291 is rewriting the same three sections in another clone and has not
  landed; this clone merges its committed work, so the rewrite starts from the corrected record, not from main's.
- **The 20,000-byte question cap** (feature 250 D14) bounds what one check reads. A merged topic may exceed it; the
  pilot measures the merged section and, if it is over, raises the choice with the GM (a topic cap, h3 subsections
  within the topic, or checks run on subsets of its notes) rather than splitting the topic the GM asked to merge.
- **The roster's job moves to the footnotes.** The map's references list read a section's sources from its roster;
  with no roster they are read from the keys its footnotes cite, which is the same set when the roster was honest
  (every roster key already had to be quoted by a footnote).

## Out of scope

- Rewriting any section other than the pilot's topics before the GM's sign-off.
- The map modals' own prose, except where a merge re-aims an `Entry:` tag, a modal's text drifts from its remade section
  (the sweep's `entry-drift` checks), a ruling of the GM's shows (FR-014), or its references and their lead-in (FR-029).

## Review history

- **Amendment, round 1** (spec-fidelity, 2026-10-01): the success criteria SC-011 to SC-025 added for FR-014 to FR-028
  (spec-lint). CHANGES REQUIRED: SC-011 to cover the modals (19 still named the GM - rewritten, and a test added);
  SC-017 to name the browser test for the collapse; SC-016 to carry the no-notes clause; the GM's request on the
  modals' references made FR-029 and SC-026, and the out-of-scope line narrowed; the GM's messages of 2026-09-29 and
  10-01 that the criteria rest on added to request.md verbatim. All applied.
- **Amendment, round 2** (spec-fidelity, 2026-10-01): items 1-4 RESOLVED; item 5 partly - the GM's work-yard review of
  2026-09-30 had been recorded only to its first point, so FR-027's kanji-gloss words were missing (now recorded in
  full); FR-014's "the modals (stream, footbridge) that show a ruling today" understated the 19 fixed (reworded).
- **Amendment, round 3** (spec-fidelity, 2026-10-01): FAITHFUL - both of round 2's items resolved; FR-027 and SC-024
  checked against the GM's recorded words.

- **Round 1** (spec-fidelity, 2026-09-29): REVISE. Kept: the third grove section folded in, the cap raised with the
  GM, the two phases. Fixed: an aside with real content is promoted, not cut; only map-visible statements with no
  finding are cut, a statement of how the map draws is kept; the lead line may be a statement; the lead-in is for
  context or relevance; a tooltip over a lead-in for a recurring term; the roster's unstated information is carried;
  the canopy-tree definition specified. FR-006 rewritten on the finding that the rule was never written down.
  Aside raised for the GM: `homesteads/046` (which side the windbreak stood on, the yard and the garden) overlaps the
  grove topic and may belong to it later.
