# Feature Specification: Uncited-source catalog

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=312-uncited-source-catalog`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`, with the rulings settled there. In short: a usefulness FILTER (its
own subagent check) over the ~2,846 pages read and never cited, so that only pages *"above a certain threshold of usefulness
or reliability"* are stored, and the rest leave *"a record of them. So that we know not to check them next time"*, tagged
with a few high-level reasons; a WRITE-UP for each kept page *"exactly the same as what we have for our existing sources"*
with subagent checks that it is accurate; a per-source record of *"all of the things that we have tried to use a source
for. and found it wanting"*, for cited and uncited sources alike, checked first on the next research pass; kept uncited
sources shown in their own "Uncited sources" part of Sources; a BLOCKED-DOMAIN category (AI-generated sites, Grokipedia its
first member) *"tool enforced"* at every route; every citation rule enforced by tooling; paywalled citations removed; and
the high-risk sources (`high-risk-sources.md`) downloaded by the GM and confirmed before the feature closes.

Builds on feature 313 (the access tags, read through its report command, and the canonical download list
`research/to-download.md`, built by a peer session in parallel and landing first), feature 309 (the archive), feature 305
(source tags and sections) and feature 288 (the sources-consulted ledger and the page cache).

## Context (observed 2026-10-02, `prep.md`)

- **2,843** uncited URLs (`scripts/_archive_ops.py:consulted_urls`, no manifest row) plus **3** captured before the GM held
  the backfill. **1,200** have saved text in the page cache (median 2,415 characters); **1,643** need a fetch to be read.
- About **160** are mechanically without substance: search-result pages and API or raw URLs (the regexes are in `prep.md`).
- The ledger (`<mirror>/.specify/sources-consulted.jsonl`, 8,535 reads of 4,903 URLs) names a question on 7,155 rows but
  carries no outcome on 3,314 and a reason on only 73; its question ids before feature 303 are old page-and-number forms
  (`research/moved-303.json` maps them). It is host-local and nothing asks it "has this source been tried for this question".
- Grokipedia is banned in writing only (`docs/research-doctrine.md`, the registry's `_front.html`); no tool refuses it and
  no Grokipedia URL is on the ledger or in the archive.
- 22 sources on `high-risk-sources.md`: 7 a footnote rests on, 8 cited with no claim resting on them, 7 unreachable.
- 8 URLs the ledger marks `cited:<key>` have no manifest row (a different spelling of the cited URL).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A blocked domain cannot be read, recorded or cited (Priority: P1)

Grokipedia, and any domain the GM later adds to the blocked category, is refused at every fetch route a session or an
agent has, never enters the ledger, the cache, the archive, the not-kept list, the attempts log or the registry, and a
citation of one fails the record build.

**Independent Test**: a WebFetch, a `curl` and each make fetch route aimed at a `grokipedia.com` URL are refused with the
reason; a fixture registry entry or footnote linking one fails `make record CHECK=1`.

**Acceptance Scenarios**:

1. **Given** a WebFetch of `https://grokipedia.com/page/X`, **When** the hook runs, **Then** it is refused, naming the
   blocked-domain list and why the domain is on it.
2. **Given** a subdomain (`www.grokipedia.com`), **Then** it is refused the same way.
3. **Given** the GM approves a new AI-generated domain, **When** it is added to the list with the approval recorded,
   **Then** every route refuses it with no code change.

### User Story 2 - Every uncited page is judged once: kept, or recorded as not kept with its reasons (Priority: P1)

Every uncited page passes the filter: a mechanical rule for what needs no judgment, the `source-filter` agent for the
rest. A kept page is archived and written up; a page not kept is a line in the not-kept list with its reasons, and is
never stored.

**Independent Test**: after the run, every URL in the uncited set has exactly one verdict; no not-kept URL has a manifest
row; every kept URL has one and a registry entry.

**Acceptance Scenarios**:

1. **Given** a DuckDuckGo results page, **Then** it is not kept, reason `no-substance`, basis `rule`, with no agent call.
2. **Given** a page on modern mechanized rice yields, **Then** it is not kept, reason `modern-only`.
3. **Given** a ja.wikipedia article on a premodern village institution, **Then** it is kept.
4. **Given** one of the 3 pre-hold captures is not kept, **Then** its manifest row is removed and its copy stays only in the
   archive's history (the GM: *"their disposition should just be whatever the filter ends up saying"*).

### User Story 3 - The filter is trusted only after it is calibrated (Priority: P1)

Before its verdicts are applied, the filter is run three times on each leg of a control: cited pages (it should keep
them) and a labeled set of junk (it should not).

**Independent Test**: the calibration record in this directory shows three runs a leg and the agreement on each.

### User Story 4 - A kept uncited source reads like a cited one, in its own part of Sources (Priority: P1)

A kept page has a registry entry of the same form as a cited work - its citation line and link, what it is, why it
applies and its limits, its tags - checked by `source-applicability`, and appears under "Uncited sources" in the built
record, grouped by the same sections as the works cited. The GM's L7R setting notes are never there; L5R wiki pages may be.

**Independent Test**: `make record` builds an "Uncited sources" part; a fixture uncited entry pointing at the GM's notes
fails the build.

### User Story 5 - A research pass checks what was tried before it reads (Priority: P1)

Every attempt to use a source for a question - what was sought and what came of it - is kept per source, cited and
uncited alike, in a committed log; old reads whose reason is unknown say so. Before a page is fetched, the tooling prints
the source's earlier attempts and its filter verdict; every new consult records what was sought.

**Independent Test**: `make source-pages` on a URL with earlier attempts prints them before fetching; run without saying
what is sought, it is refused with the compliant command; `make attempts URL=<u>` lists the attempts.

### User Story 6 - A cited source no one can read is not cited (Priority: P1)

A cited source that is paywalled (by its access tag) or was never read stops being cited: its footnotes become absence
notes where it was the only support, and the build refuses a footnote citing such a source.

### User Story 7 - The high-risk sources are confirmed or removed (Priority: P1, needs the GM)

The GM downloads each of the 22 high-risk sources or reports it not found; each downloaded one is read by `source-reader`
and its notes by `quote-check`, and the record is corrected where they disagree; one not found or paywalled is removed as
in User Story 6.

### Edge Cases

- A URL cited under a different spelling (the 8 in `prep.md`) is not uncited: it is matched to its key's own URL first.
- A kept uncited source later cited: its entry moves to the works cited and gains its `Used for:` line; the build refuses
  an entry in the uncited part that a footnote cites, naming the command that moves it.
- A not-kept page later read for a new question: allowed (a verdict is not a ban); the tooling shows the verdict first, and
  the page may be judged again and kept.
- A page no route can read (refused, down, gone): not kept, reason `unreadable`, carrying its access state from 313's
  vocabulary, so a later check can find it.
- A filter verdict that finds an AI-generated site: it proposes the domain for the blocked list; only the GM adds it.
- Grokipedia found while looking for other sources: refused - the GM accepted blocking the domain entirely.

## Requirements *(mandatory)*

### Functional Requirements

**The blocked domains and the banned citations**

- **FR-001**: The blocked-domain list is `research/blocked-domains.json`: per domain, its category (`ai-generated` to start),
  why it is there, the date added and the GM's approval (date and words). Grokipedia (`grokipedia.com`) is its first
  member. A test refuses an entry without an approval. The list is a category any domain can join, not a rule for one site.
- **FR-002**: A URL on a blocked domain or any subdomain of one is refused at every fetch route: WebFetch (a PreToolUse
  hook), a Bash command that fetches it (`curl`, `wget`, a make fetch target), and the Python fetch layer every make route
  shares (`make source-pages`, `make archive` / `archive-sources` / `archive-find`, `make reserve ... URL=`,
  `make source-outcome`, `make quote-verbatim`). One function decides, and each refusal names the list and the reason.
- **FR-003**: A blocked URL is never recorded: the ledger, the page cache, the archive, the not-kept list, the attempts
  log and the registry each refuse it, and `make record CHECK=1` refuses a registry entry or footnote that links one. It is
  never written up as considered and rejected.
- **FR-004**: Sources forbidden for other reasons are banned at the CITATION, by URL pattern, in
  `research/banned-citations.json` (pattern, reason, the GM's approval); the build refuses a citation matching one. Fetching
  them is not blocked (they may share a domain with allowed sources).
- **FR-005**: Every citation rule is enforced by tooling. Every citation rule stated in `CLAUDE.md`, `research/CLAUDE.md`,
  `docs/research-record-rules.md`, `docs/research-doctrine.md` and `container-scripts/page-session-rules.md` is
  inventoried, each with the tool that enforces it (a script, a build refusal, a hook, or the check agent the record gate
  owes); a rule with no tool gets one - a mechanical check, tested, where it can be checked mechanically, otherwise a check
  the record gate owes on the words it governs. The inventory lives in the doctrine.

**The filter**

- **FR-006**: The uncited set is computed, never hand-listed: the ledger's and the cache's URLs with no archive manifest
  row, minus a URL that is a respelling of a cited URL (matched to its key), plus the 3 pre-hold captures. Its count is
  recorded.
- **FR-007**: A rule, with no agent, decides what needs no judgment: a search-result, listing, API or raw URL is not kept,
  reason `no-substance`; a page no route can read (the cache, a live fetch, an archived snapshot) is not kept, reason
  `unreadable`, with its access state (`bot-refused`, `down`, `gone`, `paywalled`).
- **FR-008**: The `source-filter` agent (a defined agent, Opus, its tier pinned) judges each remaining page from its saved
  text, with no question in hand, against the THRESHOLD: the page holds checkable evidence on a subject the record covers
  (building, farming, settlement, landscape, daily life, religion, administration - the subjects of `research/tags.json`),
  of a kind of source the record would cite (scholarship, a primary text, a museum, archive, government or reference
  work, an established encyclopedia), of evidence the setting could use: premodern or traditional practice, another
  period's or region's as an analog, or facts not bound to a period (the `works-timeless` section); never the canon
  section. Its verdict is KEEP or NOT-KEPT; a NOT-KEPT carries one or more reasons from the fixed set -
  `off-topic` (the title misled), `modern-only` (industrial or mechanized practice whose numbers would mislead),
  `unreliable-kind` (AI-generated, content farm, unsourced aggregator), `no-substance` (search, listing, index or stub
  page), `duplicate` (a copy of a kept or cited page), `unreadable` - and an optional one-line note. It may propose a domain
  for the blocked list, never add one. It reads batches of pages from a bundle outside the repository.
- **FR-009**: The filter is calibrated before any verdict is applied: three runs a leg on a POSITIVE control (cited
  pages, which it should keep) and a NEGATIVE control (a labeled set of junk pages from the uncited set, each label with its
  reason). It is trusted at agreement on 19 verdicts in 20 or more on each leg in every run (`research.md` R1); below that its contract is amended and the
  calibration re-run. The record of the runs is in this directory.
- **FR-010**: A not-kept page is a line of `research/not-kept.jsonl` (union-merged): its URL, reasons, note, access state
  where unreadable, the basis (`rule` or `source-filter`), the date and the feature. It is never archived. A pre-hold capture
  not kept loses its manifest row; its copy stays in the archive's history, which is never rewritten.
- **FR-011**: A kept page is archived (`make archive-sources CONSULTED=1`, which archives kept pages only and refuses any
  other), and gets a write-up (FR-012).

**The write-ups and the record**

- **FR-012**: Each kept page gets a registry entry in `research/sources/040-uncited-works/`, keyed by `make reserve`, of the
  same form as a cited work's: the citation line with its URL, `What it is:`, `Why it applies, and its limits:` and its
  tags marker - no `Used for:` line. Each entry is checked by `source-applicability` (its write-up and its tags accurate to
  the source, its limits honest), from a check bundle, through the record gate (`make record-owed`).
- **FR-013**: The built record's Sources gains an "Uncited sources" part, grouped by the same sections, in the same order,
  as the works cited (an empty section omitted). The canon section (the GM's L7R notes) never appears in it, and the build
  refuses an uncited entry linking the GM's notes; L5R setting wiki pages may appear.
- **FR-014**: When an uncited entry is first cited, it moves to the works cited with its `Used for:` line
  (`make cite-uncited KEY=<k>`); the build refuses a footnote citing an entry still in the uncited part, naming that command.

**What was tried**

- **FR-015**: The attempts log is `research/source-attempts.jsonl` (union-merged), one line per attempt: the URL, its key
  where it has one, the question (its current stem), what was sought, the outcome (`found`, `partial`, `not-found`,
  `not-applicable`, `unreadable`, `unknown`), the date and the feature. It covers cited and uncited sources alike; what a
  cited source WAS used for stays derived from its footnotes and is not copied here.
- **FR-016**: The log is seeded from the ledger: every row becomes an attempt, its question id mapped to the current stem
  (`moved-303.json`), or `unknown` where it names none, its outcome mapped (`nothing-found` -> `not-found`, `rejected:` -> `not-applicable`
  with the reason, `unreadable`, `cited:` -> `found`, the rest `unknown`), and what was sought written as unknown - recorded
  before feature 312 (the GM: *"it is of course okay in any case to mark that we don't know why something was consulted
  originally"*).
- **FR-017**: Every new consult records what was sought, by every route that reads a page: `make source-pages` requires
  the question and `SOUGHT=` and refuses without them, printing the compliant command; `make archive-find` and `make
  archive` write an attempt with what they were asked for; a WebFetch writes one through the hook FR-002 and FR-018 add,
  its `prompt` serving as what was sought where no question is named. `make source-outcome` writes the attempt's outcome.
- **FR-018**: Before a page is fetched, its earlier attempts and its filter verdict are printed: by `make source-pages`, by
  `make archive-find`, and by the WebFetch hook as added context. `make attempts URL=<u> | KEY=<k> | Q=<NNNN>` prints them on
  demand. A verdict never refuses a read.

**Sources no one can read**

- **FR-019**: A cited source where what can be read is less than the work - the GM marked it paywalled or not found, or its
  access state (feature 313's report) is `paywalled`, `gm-partial` or `never-read` - is removed as a source footnote by
  footnote: each footnote citing it is removed (an absence note where it was the claim's only support, dropped where
  another note carries the claim) unless `quote-check` has confirmed its quoted passage in the readable part (the open page,
  an open abstract, or the GM's partial copy), a confirmation recorded per footnote. A source left with no footnote leaves
  the works cited and is recorded known-unavailable through 313's hand-recorded state (a date and a reason) and a not-kept
  line (`unreadable`, its access state).
- **FR-020**: The push and the gate refuse a footnote citing a source FR-019 names unless its confirmation is on record.
- **FR-021**: Each of the 22 sources on `high-risk-sources.md` (tiers 1 and 2 and the unreachable 7) is downloaded by the GM
  and ingested (feature 313), or reported not found; each one got is read by `source-reader` and its footnotes checked by
  `quote-check`, and the record is corrected where they disagree; one not found or paywalled is removed by FR-019.
- **FR-022**: The 8 cited respellings (`prep.md`) are each confirmed covered by their key's archived URL, or archived.

### Key Entities

- **Blocked domain**: a domain no route may read or record (category, reason, approval).
- **Banned citation**: a URL pattern no footnote or entry may cite (reason, approval).
- **Verdict**: KEEP, or NOT-KEPT with reasons, for one uncited URL, by rule or by `source-filter`.
- **Uncited entry**: a registry entry of a kept page, under `040-uncited-works/`, with no `Used for:` line.
- **Attempt**: one use of one source for one question - what was sought and what came of it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003): a `grokipedia.com` URL is refused by each route listed in FR-002 and by each store in
  FR-003, each pinned by a test; a fixture citing one fails `make record CHECK=1`.
- **SC-002** (FR-004): a fixture citation matching a banned pattern fails the build; fetching the same URL is not refused.
- **SC-003** (FR-005): the inventory names a tool for every citation rule; each mechanical rule's tool has a test.
- **SC-004** (FR-006, FR-007, FR-010, FR-011): every URL of the uncited set has exactly one verdict; 0 not-kept URLs have
  a manifest row; every kept URL has one.
- **SC-005** (FR-008, FR-009): the calibration record shows three runs a leg at agreement on 19 verdicts in 20 or more on each (`research.md` R1).
- **SC-006** (FR-012, FR-013, FR-014): every kept URL has an uncited entry that `source-applicability` has answered;
  `make record` builds the "Uncited sources" part; the fixtures for a canon link and a cited uncited entry fail the build.
- **SC-007** (FR-015, FR-016, FR-017, FR-018): every ledger row has an attempt line; `make source-pages` without `SOUGHT=`
  is refused; with earlier attempts it prints them before the fetch; one consult by each route of FR-017 writes an
  attempt, each pinned by a test.
- **SC-008** (FR-019, FR-020): no footnote cites a source FR-019 names without its recorded confirmation, held at the push
  and the gate.
- **SC-009** (FR-021, FR-022): each of the 22 high-risk sources is confirmed by `source-reader` and `quote-check`, corrected,
  or removed; each of the 8 respellings is covered.

## Decisions Recorded

- The threshold (FR-008) is the session's, from its proposal the GM accepted (`request.md`, point 1), widened from
  "premodern East Asian" to the record's subjects, its analogs and facts not bound to a period, since the record cites
  European, modern-preindustrial and period-free evidence with its limits (`research/source-sections.json`; ruled faithful by
  `spec-fidelity`, round 1).
- The negative control is labeled by this session from the uncited set itself, since the ledger's 60 rejections are
  "not useful for that question", which is not "not worth keeping" (`request.md`, point 1).
- The attempts log and the not-kept list are committed, union-merged files beside the record rather than host-local, since
  the GM asked for a record kept with the sources and the ledger is host-local.
- An open abstract that carries a footnote's passage keeps the footnote (FR-019): the passage is readable, so the citation
  meets the rule; the session's refinement, offered to the GM in `request.md`, ruled within the GM's ruling by
  `spec-fidelity` (round 1), and raised with the GM once the removal has run.

## Assumptions

- Feature 313 lands first, with the access tags and the ingest; this feature reads the tags through 313's report command
  (its JSON output) and records a state only through 313's hand-recorded state, never by editing 313's files.
- The GM's downloads (FR-021) are the GM's time; the feature stays open until they are done.

## Review

- Round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 6. Applied: FR-008 takes period-free evidence; FR-019/FR-020 made
  consistent (removal footnote by footnote unless the passage is confirmed in the readable part; `gm-partial` and "not
  found" included; the refusal at the push and the gate); FR-005's inventory covers every rules file and gives a
  non-mechanical rule a gate-owed check; FR-017 reaches every reading route; FR-016 seeds every ledger row; the 313 boundary
  reads 313's report command, not a file.
