# Feature 265 - research and the closing report

## R1. The closing report (FR-009, 2026-09-27)

Per class of 250's carried work: what closed and what did not, and for each item left open, whether it was
searched and failed or never searched.

### FR-002 and FR-006 - the six pages (T01 to T06)

Worked by the landed process in three parallel queues (FR-010): A `urban-features`; B `towns` then `ways`;
C `cities/river-cities`, `buildings`, `cities/capitals`. Every page closed with one write session and check groups
packed by load, each group checked by `quote-check` and `record-format` (and `source-applicability` over new keys)
with one re-check round; the per-page verdicts are the tasks' verify lines.

- **Closed:** every FR-002 item and every FR-006 bare item the work list placed was footnoted, narrowed to its quote,
  or labeled as this page's reading or guess.
- **The 17 items the work list could not place** (urban-features 6, cities/capitals 10, towns 1): each was found
  or confirmed gone by reading the page (SC-006): 11 FOOTNOTED, 5 GONE (rewritten out by the research, one of them
  reversed by it - Lin'an ran several dozen crematoria, not "a small number"), 1 LABELED. None is bare.
- **Searched and failed, labeled in the record:** the claims whose only readable evidence is a scanned PDF with no
  text layer in this container (below, FR-008) are labeled where they stand; the Mukoyama and Abele passages were
  read from the GM's own copies and cannot be re-verified against a public page.

### FR-003 and FR-004 - the vocabulary and history sweeps (T07, T08)

- **Closed:** the 177 distinct VOCABULARY findings of 242's reports and the 72 HISTORY findings, each answered or
  measured as no longer in the text (T07 and T08's verify lines give the counts); `ochiba` no longer glosses the
  manor Ochiba - a glossary term can be `cased` now, and `han` and `fen` were made so for the Han and Fen rivers -
  and `fire-gap` is a variant of `fire gap`.
- **Found by the checks, fixed here:** the T11 `record-format` passes over the 30 questions the sweeps and splits
  changed reported further vocabulary, session notes and history, all applied.
- **Not closed:** none.

### FR-005 - English titles on the registry (T09)

- **Closed:** 542 citation lines carry an English rendering of a title given only in Japanese or Chinese, marked as
  this project's translation. The residue a detector still flags was spot-checked: author names, place names used
  as names, and titles whose English stands before them.

### FR-007 - the checks over what the sweeps changed (T11)

- **Closed:** 30 changed questions checked by 12 `quote-check` and 12 `record-format` agents, packed by load; a
  re-check round over the 43 cited notes the first round changed (4 agents), and the new question `fields` 075 checked
  whole. What failed again after the re-check was labeled as this page's reading, not checked a third time.
- **Questions split under the 20,000-byte cap on the way:** `homesteads` 140 (into 140 and 145), `urban-features`
  010 (010 and 012) and 080 (080 and 082), `fields` 070 (070 and 075).
- **The owed modals:** every pair `_entry_owed.py` names was dispatched to `entry-drift` (14 groups in the three
  queues, and the last five pairs directly); the verdicts are in `owed-verdicts.md`.

### FR-008 - the download list (T10)

- **Added at the end, both links on each:** 244 Tanigawa 1992, 245 Chang's scanned chapter (Figure 5), 249 the
  Nagaokakyo leaflet, 251 Yannopoulos 2015, 252 Endo 2013.
- **Already listed:** Tabayashi 1987 (226), Sugiura 1973, the Northampton tannery report, Feng (228), the Tama
  crematoria study (124).
- **Searched and failed, still open:** the quotations from those scans cannot be confirmed character for character
  until someone reads them from a copy with a text layer; each is labeled where it stands.

### FR-010 - parallel queues and reserved prefixes (T12 to T14)

- **Closed:** `make reserve` (a host-wide lock and ledger), the new-file guard, `page-queue.sh` and
  `pull-queue.sh`; the six pages were worked by three queues at once.
- **What the first real use found, fixed where found:**
  - Two queues reserved the same glossary term (`plinth`) and the same registry key (`daikan-jawiki`) under
    different prefixes. The lock kept the numbers apart but not the key; `reserve` now refuses a key another
    clone holds, and the two were merged.
  - A merge from main collided on 23 prefixes that another session had taken without a reservation (`make reserve`
    was not yet on main). This clone's side was renumbered under the lock, and the registry has passed 9990, so
    the guard now reads five-digit prefixes.
  - `pull-queue.sh` was refused by the check briefs a finished queue leaves untracked, and stopped on a hand
    conflict with the generated files still unresolved. It now commits the briefs and resolves the generated side
    first.
  - `make apply-edits` refused every edit to a building-plan sheet's modal (feature 262's `compound_kinds/`). It
    now reaches them.
