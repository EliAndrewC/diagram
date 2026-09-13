# Plan - feature 238

Spec: [`spec.md`](spec.md). Research notes: [`research.md`](research.md).

## Constitution check

- **Principle XII (research before a ruling, and a guess is the last resort).** This feature is nothing
  but that principle applied to the sentences it was never applied to. FR-003 sends every `CITE` entry to
  a `source-reader` before a note is written.
- **Principle I / XVI (the author is not the reviewer).** FR-001 puts the inventory in a `quote-check`
  agent's hands rather than the session's, for the same reason a Mode B map is not reviewed by the
  session that drew it. The spec itself went to `spec-fidelity`, which refused round 1 - see D4.
- **Principle X clause 5 (100% coverage).** FR-011 touches `settlement/civic_grounds/lodging.py`. The
  glyph's lines are executed by the existing lodging tests; removing three of them removes no branch, so
  the floor is met by the tests that already exist. Verified at the gate, not assumed.
- **Principle XIII (no known regressions).** The only engine change is the inn glyph, and no LIVE map
  draws an inn - the six generators that call `s.inn()` are all in the frozen legacy pool, three towns
  (ubame, hoshizora, hirameki) and three provincial cities (tango, minami, nagahara), and no live pool
  map calls it at all (`research.md` R2). The
  gate is the measurement.
- **Principle XIV (fix defects where you find them).** A reading pass over nineteen pages will turn up
  defects outside the unfootnoted sentences - a wrong number, a stale link, a quotation that drifted.
  FR-006 covers the contradictions; anything else found is fixed in this work.
- **Principle XV (keep going).** The pass is long. FR-009's page-by-page batching is what lets it be
  interrupted without leaving the record half-noted.

## Shape of the work

**Phase 1 - the inventory.** Nineteen pages read by `quote-check` agents in subject batches, each asked
for the one thing this feature needs and its documented job already includes: per section, which
assertions carry no footnote. Their reports are kept verbatim under `reader-reports/`. The session then
builds `research.md` R3 - the inventory proper - giving every named sentence one of FR-002's four
dispositions. Nothing is written to a page in this phase.

**Phase 2 - page by page.** One task per page. For each: dispatch `source-reader` on that page's `CITE`
entries, write the footnotes from the quotes that come back, write the `GROUNDS` and `ABSENCE` notes,
retire the inline `(unsourced)` markers those notes replace, register any new key in `SOURCES.html` with
both write-ups. A page is done when every sentence its inventory named carries a note or is recorded as
`COVERED` / `NOT AN ASSERTION`.

Ordering: the pages the residue named as clusters go first, because they are where the density is -
`religion-and-death` (the torii distribution), `vegetation` (forest density and crown size),
`urban-features` (the tanning yard, the bell-and-drum tower), `cities/capitals` (the nine class-scaling
bullets). Then the rest by descending inline-marker count from R1, so the pages that already know they
have a problem are worked before the ones that may not.

**Phase 3 - the checks.** `record-format` over every changed page, `quote-check` over every new footnote,
`source-applicability` over every new key. These are FR-007 and they are the same three that feature 232
paid for and got its money's worth from - the memory of that pass says `entry-drift` was the highest
yield and `record-format` found about 130 edits over 13 pages.

**Phase 4 - the caravan inn (FR-011).** The glyph, the docstring, the page. Independent of phases 1 to 3
and small; it is scheduled last only because it is what makes the delta engine code, and the gate should
run once over everything.

**Phase 5 - closing.** Part 4 of `TO-DOWNLOAD.md` appended as documents are met (FR-005, continuous, not
a phase-5 job - it is listed here only so the closing report can confirm it happened). The closing report
names what is left open. Then `make done`, the reviews the push demands, and the push.

## What could make this go wrong, and the answer

- **The inventory is enormous and the pass never finishes.** R1 bounds it at 864 paragraphs and floors it
  at 285 markers. If the real inventory is nearer the bound than the floor, the answer is FR-009: pages
  land as they finish, and an unfinished feature is a partial record improvement rather than nothing.
- **An agent reviews the summary rather than the file.** Feature 232's memory names this: a reader that
  cannot open a paper called a threshold a sign flip from the abstract alone. Every verdict that
  contradicts the record gets the passage read before the page is changed.
- **A reviewer's own facts are wrong.** Also from 232: one reader reported a date pair that appears
  nowhere in the paper it described. Agent findings are checked, not applied.
