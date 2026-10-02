# Feature 305 - closing notes

Kept here rather than in `plan.md`, whose CLEAR review is recorded against its digest.

## What landed

- `research/source-tags.json`: period (premodern, modern preindustrial, present day, not period-bound, fiction), region
  (Japan, China, Korea, other East Asia, Europe, elsewhere, general, Rokugan (published)), kind (primary, scholarship,
  reference, institutional, popular), and the Setting canon label. Every period explanation states every region's
  cut-off and its reason (GM message 2), plus the rules for undated accounts of traditional forms and for evidence that
  straddles a cut-off.
- `research/source-sections.json`: nine sections (amendment 2 added the published game setting, second).
- `record/source_tags.py`; the works foot of every question page, the registry index and pages, and the one-page
  record grouped by section with labels; the label hover in `record.js`; `make reserve ... TAGS=`;
  `make source-tags-contract` and the `source-applicability` contract's Tags rule; the docs.
- Every one of the 2,126 entries tagged (16 canon carry none); `make record CHECK=1` refuses an untagged entry.

## Measured

- Classification: 22 Sonnet batches; 35 unsettled and 98 late-date flags adjudicated by Opus (41 changed).
- SC-004: 60-entry stratified sample by `source-applicability`: 174 of 180 facet tags right (96.7%); 54 of 60 entries
  wholly right. The five wrong tags (four periods missing a modern span, one kind) were corrected, and the pattern was
  swept: 41 more premodern-only entries naming modern dates re-adjudicated, 9 changed. One finding (baler-enwiki) was
  not taken: the agent did not have the vocabulary, and Europe's modern-preindustrial span (about 1800-1950) covers it.
- SC-005: the sample's RESTATES and MISSING findings applied (51 EDIT blocks; two reduced so no fact from a source the
  registry does not cite entered an entry). Swept: 281 paragraphs still carrying generic category phrases re-trimmed
  (163 changed, 0 refused); 15 trims that deleted a place name the tags do not carry checked for a lost limit (0 lost).
- SC-006: the limits paragraphs went from 1,244,183 characters to 1,197,456 (observed 2026-10-02; method: the sum of
  every entry's "Why it applies" paragraph, before and after). The cut is small because most write-ups were already
  specific; the repetition was a clause per paragraph, not whole paragraphs.
- `make record`: 4.6-5.2 s before (three runs, the baseline worktree), 3.2-3.6 s after on warm runs (a first cold run
  took 10 s) - no slowdown.

## A sample finding not taken

- `farrier-enwiki`: the sample's reader said iron horseshoeing reached Japan only with the Meiji army. The GM ruled on
  2026-07-25 that Rokugan shoes horses in iron (`settlement/trades.py`, the `farrier()` docstring answers the Edo
  straw-sandal point), so this is settled canon, not an open question; the entry's limits now say only that the article
  says nothing of East Asia.

## Known limits

- A defined agent loads its contract from the mirror, so the `source-applicability` sample ran on the OLD contract (it
  judged tags from their names). The new contract, with the vocabulary block, lands with this push.
