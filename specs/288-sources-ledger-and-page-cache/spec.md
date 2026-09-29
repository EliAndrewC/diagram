# Feature Specification: a sources-consulted ledger and a saved-page cache keyed by URL

**Feature Branch**: `288-sources-ledger-and-page-cache` (no branch; committed on `main` in the clone)

**Created**: 2026-09-29

**Status**: FAITHFUL (spec-fidelity round 2, 2026-09-29)

**Input**: the GM, 2026-09-29 ([`request.md`](request.md)): "I like the idea of the cheap fixes that you have
suggested so far. So please do make that small tooling change. Both of the cheap fixes, I mean." The two fixes: a
record of every source consulted, with its outcome, and a saved-page cache keyed by URL. The measurement behind them
is [`research.md`](research.md) R1.

## Summary

Today nothing records that a page was read and NOT cited: 208 uncited pages were read again in a later session, 144
of them under a different feature, and the later reader never knew (R1). And the saved pages are filed per run under
`/tmp/l7r-check/<run>/`, so a page saved once is never found again (R1). This feature adds:

1. a **sources-consulted ledger**, host-wide, one line per read with its question and outcome, printed to the
   session whenever it is about to read a page it (or another session) read before; and
2. a **saved-page cache keyed by the normalized URL**, filled by every save and read by every script that fetches a
   source page, so a page is fetched once and found again by URL.

Both are tooling that makes the right shape automatic; neither is a guard (R1: the saving is too small to justify a
refusal).

## User Scenarios & Testing

### User Story 1 - A session learns a page was read before, and what came of it (Priority: P1)

A research session runs `make source-pages` for a URL. Before anything is fetched, the command prints every earlier
ledger line for that URL: when, which feature, clone and session, for which question, and with what outcome
(`cited:<key>`, `rejected:<why>`, `nothing-found`, `unreadable`, `pending`, or the seed's `unknown-outcome`). The
session sees, for example, that the page was rejected last week for the same question, and does not re-read it
without a reason.

**Independent Test**: seed a ledger line `rejected:no dimensions` for a URL; run source-pages on the same URL (in any
spelling the normalization folds together); the line is printed before the fetch.

**Acceptance Scenarios**:

1. **Given** earlier ledger lines for a URL, **When** `make source-pages` names it, **Then** every one of them is
   printed before the page is fetched or taken from the cache.
2. **Given** a URL saved by `make source-pages`, **When** the save finishes, **Then** the ledger holds a new `pending`
   line for it with the date, feature, clone, session and (when given) the question.
3. **Given** a session has judged a page, **When** it runs `make source-outcome URL=<u> OUTCOME=<o> [QUESTION=<q>]`,
   **Then** the ledger holds that outcome line; an outcome of any other shape is refused with the allowed forms.
4. **Given** `make sources-consulted URL=<u>` or `KEY=<regex>`, **When** it runs, **Then** it prints every line for
   that URL, or every line whose outcome cites a registry key matching the regex.
5. **Given** source-reader's whole-page bundle, `make check-bundle KEY=<k> WHOLE=1 [QUESTION=<q>]`, **When** it saves
   the key's page, **Then** it prints the earlier lines and appends a `pending` line exactly as scenarios 1 and 2 say
   of `make source-pages`; an excerpt bundle (`KEY=<k>` without `WHOLE=1`) prints and appends nothing (D1).

### User Story 2 - A new citation marks its source cited without a separate step (Priority: P1)

A session reserves a registry entry with `make reserve KIND=registry KEY=<k>`. Where the stub names the URL
(`URL=<u>` given to the reserve), the ledger gets `cited:<k>` for it at once; otherwise the ledger gets it when the
entry is filled - the next `make record` or `make sources-consulted` run finds the filled entry's URL with no
`cited:<k>` line and appends one.

**Independent Test**: reserve a key with a URL: the ledger line appears. Reserve one without, fill the entry with a
URL, run `make record`: the line appears, once.

**Acceptance Scenarios**:

1. **Given** `make reserve KIND=registry KEY=k URL=u`, **Then** the stub carries the URL and the ledger holds
   `cited:k` for `u`.
2. **Given** a filled registry entry whose URL the ledger does not mark `cited:<its key>`, **When** `make record` or
   `make sources-consulted` runs, **Then** one such line is appended; a second run appends none.
3. **Given** `make reserve` without `URL=`, **Then** it behaves exactly as today (same stub, same output).

### User Story 3 - The ledger is useful on day one (Priority: P1)

The ledger is seeded once from the measurement: every URL in `per_url.json`, with its reads' dates and features,
`cited:<key>` where the URL is in a registry entry, else `unknown-outcome`. The seeding and its count are recorded in
research.md.

**Independent Test**: after seeding, `make sources-consulted URL=<a URL from per_url.json>` prints its seeded
lines.

### User Story 4 - A page is fetched once and found again by URL (Priority: P1)

`make source-pages` stores each fetched page ONCE in a host-wide cache keyed by the hash of its normalized URL,
saved in parts as today, and fills the requested `OUT=` directory from the cache. A cached page is not fetched again
unless `REFRESH=1` is given or the copy is older than the stated age. `make check-bundle ... WHOLE=1` (and every
other bundle that saves a page) and `make quote-verbatim` read the cached text the same way. The existing
`/tmp/l7r-check` saves are imported into the cache once, deduplicated.

**Independent Test**: save a URL twice into two OUT directories; the second makes no network request and produces
the same files. Run quote-verbatim on a question whose pages are cached: no network request is made.

**Acceptance Scenarios**:

1. **Given** a URL not in the cache, **When** source-pages saves it, **Then** the cache holds it under its
   normalized-URL hash with its metadata, and OUT holds the same files and MANIFEST row as today.
2. **Given** a cached copy younger than the age, **When** any of source-pages, check-bundle or quote-verbatim needs
   the page, **Then** it is read from the cache and not fetched; the manifest row says it came from the cache and
   when it was fetched.
3. **Given** `REFRESH=1`, or a copy older than the age, **Then** the page is fetched again and the cache updated.
4. **Given** the import has run, **Then** each distinct page of `/tmp/l7r-check` is in the cache once.

### User Story 5 - The check agents read the saved text first (Priority: P2)

The `quote-check` and `source-reader` contracts say to read the cached text their bundle carries before any
`WebFetch`. The edits are minimal; each file keeps its `omitClaudeMd`, model and effort.

### User Story 6 - The process text says what to do (Priority: P2)

The research record's `CLAUDE.md` and `container-scripts/page-session-rules.md` say: check the ledger (source-pages
prints it); record every page's outcome with `make source-outcome`; a page already `rejected` for the same question
is not re-read without a reason. The feature-274 drift test stays green.

### Edge Cases

- The same page under different spellings (`http` vs `https`, `www.`, `m.wikipedia`, a fragment, a trailing slash,
  percent-encoding): one ledger URL and one cache entry (the measurement's normalization, R1).
- A page that fails to fetch (UNFETCHABLE, a PDF, undecodable): nothing is cached; the manifest row is as today; the
  ledger gets a `pending` line only for a page actually saved.
- Two sessions saving at once: ledger appends and cache writes are under a host-wide lock, and a cache entry is
  written to a temporary name and renamed, so a reader never sees half a page.
- A queue mid-run when this lands (feature 280's sweep merges main between groups): every existing make target keeps
  its interface and its output shape; the new arguments are optional.
- A long page saved as an excerpt for a check (`--quotes`): the cache holds the whole page; the excerpt is cut from it
  into OUT, as now.
- The re-verification saves - a `make check-bundle KEY=<k>` excerpt bundle (no `WHOLE=1`, the page cut around the
  passages already quoted) and `make quote-verbatim` - re-check passages of an already-cited page: they use the cache
  but do not print or append ledger lines (D1). `make check-bundle KEY=<k> WHOLE=1` is source-reader's search of a
  cited page for a NEW claim, a research read: it prints and appends exactly as `make source-pages` does.

## Requirements

### Functional Requirements

- **FR-001** A host-wide ledger `<mirror>/.specify/sources-consulted.jsonl`, gitignored, appended under a lock beside
  `make claim`'s and `make reserve`'s. One JSON line per read: normalized URL, UTC date, feature, clone, session,
  question(s), outcome. Outcomes: `cited:<registry key>`, `rejected:<why>`, `nothing-found`, `unreadable`, `pending`
  (and `unknown-outcome`, written only by the seeding).
- **FR-002** URL normalization exactly as the measurement's `extract_norm.py` (R1), shared by the ledger and the
  cache.
- **FR-003** `make source-pages`, and `make check-bundle KEY=<k> WHOLE=1`, print every earlier ledger line for each
  URL BEFORE fetching it, and append a `pending` line for each URL they save. An optional `QUESTION=<page/NNN>` on
  either is recorded on those lines.
- **FR-004** `make source-outcome URL=<u> OUTCOME=<o> [QUESTION=<page/NNN>]` records an outcome; a malformed outcome
  is refused, naming the allowed forms.
- **FR-005** `make reserve KIND=registry KEY=<k>` marks the URL `cited:<k>`: at once when an optional `URL=<u>` is
  given (the stub then names the URL), else when the entry is filled - found by `make record` and `make
  sources-consulted`. Without `URL=`, reserve is unchanged.
- **FR-006** `make sources-consulted URL=<u>` | `KEY=<regex>` prints the matching lines.
- **FR-007** The ledger is seeded once from `per_url.json`: every URL, its reads' dates and features, `cited:<key>`
  where it is in a registry entry, else `unknown-outcome`; the seeding and its count are recorded in research.md.
- **FR-008** A host-wide cache keyed by the normalized URL's hash holds each fetched page once, with its parts as
  today and its metadata (URL, fetch time); `make source-pages` fills OUT from it, and OUT's files and manifest keep
  today's names and shape.
- **FR-009** A cached page is not fetched again unless `REFRESH=1` or it is older than a stated age; the age and its
  reason are recorded in the plan and in the code.
- **FR-010** `make check-bundle` (every mode that saves a page, `WHOLE=1` among them) and `make quote-verbatim` read
  the cached text.
- **FR-011** The `quote-check` and `source-reader` agent files say to read the cached text their bundle carries
  before any WebFetch; `omitClaudeMd`, model and effort unchanged.
- **FR-012** A one-time import deduplicates the existing `/tmp/l7r-check` saves into the cache.
- **FR-013** The research record's `CLAUDE.md` and `container-scripts/page-session-rules.md` carry the three process
  rules (check the ledger; record the outcome with `make source-outcome`; no re-read of a page `rejected` for the
  same question without a reason); the feature-274 drift test stays green.
- **FR-014** No guard is added; every existing make target keeps its interface.
- **FR-015** Full coverage (the gate's floor) of the new and changed code, tests beside the existing ones; the new Makefile targets carry
  `GUARD_EDIT_OK` with the feature and a reason.

### Key Entities

- **Ledger line**: `{url, raw, utc, feature, clone, session, questions, outcome}` (+ `reads`, `seed` on a seeded line).
- **Cache entry**: a directory named by the hash of the normalized URL: `meta.json` (url, normalized url, fetched
  utc, characters, origin), the visible text, and its parts.

## Success Criteria

### Measurable Outcomes

- **SC-001** Tests: an earlier line for a URL, in another spelling, is printed by source-pages, and by
  `check-bundle KEY=<k> WHOLE=1`, before its fetch, and each save appends a `pending` line; an excerpt bundle
  appends none (FR-001, FR-002, FR-003).
- **SC-002** Tests: source-outcome records a well-formed outcome and refuses a malformed one; sources-consulted finds
  lines by URL and by key regex (FR-004, FR-006).
- **SC-003** Tests: reserve with `URL=` writes the ledger line; without it the stub and output are as before; a filled
  entry is marked once by the fill pass (FR-005, FR-014).
- **SC-004** The seeded ledger holds a line for every URL of `per_url.json`, and research.md states the count
  (FR-007).
- **SC-005** Tests: a second save of a URL makes no fetch and yields the same OUT files; `REFRESH=1` and an old copy
  do fetch; check-bundle and quote-verbatim make no fetch for a cached page (FR-008, FR-009, FR-010).
- **SC-006** The import leaves each distinct page of `/tmp/l7r-check` in the cache once, and reports its counts
  (FR-012).
- **SC-007** The two agent files carry the instruction; `test_agent_models.py` stays green (FR-011).
- **SC-008** The two process files carry the rules; `test_page_session_rules.py` stays green (FR-013).
- **SC-009** `make done` green with the coverage floor held (FR-015) (spec-wide).

## Decisions Recorded

- **D1 - re-verification reads stay out of the ledger; a WHOLE=1 read does not**: the excerpt bundles
  (`check-bundle KEY=<k>` without `WHOLE=1`) and `quote-verbatim` use the cache but neither print nor append ledger
  lines. They re-check passages already quoted from an already-cited page, with no research question and no outcome
  from the ledger's list; a `pending` line would put a false open status on a cited page. R1 (observed 2026-09-29;
  method: research.md R1) found 60% of reads were that within-session re-verification, by design. `check-bundle
  KEY=<k> WHOLE=1` is different: source-reader searches the whole cited page for the passage behind a NEW claim -
  a cited page read for a new question, which the GM asked about by name - so it prints and appends as
  `source-pages` does (spec-fidelity round 1).
- **D2 - "when the entry is filled" is found by a pass**, run by `make record` (which every research session runs
  after editing the record) and by `make sources-consulted`, rather than by a new hook: the GM's measurement said no
  guard.

## Assumptions

- The mirror (`/diagram`) is the host volume, so `<mirror>/.specify/` survives a container rebuild, as `make claim`'s
  ledger does.
- The feature is read from the clone's `.specify/feature.json` (or `SPECIFY_FEATURE`), the session from
  `L7R_PAGE_SESSION` or the harness's session id.

## Out of scope

- A per-source facts list (R1: 0.05% of reads would use it).
- A guard refusing a re-read.

## Review history

- Round 1 (spec-fidelity, 2026-09-29): CHANGES REQUIRED - D1 excluded the `WHOLE=1` bundle, a research read of a
  cited page for a new claim; D1, the edge case, FR-003 and SC-001 now ledger it, with `QUESTION=`.
- Round 2 (spec-fidelity-verify, 2026-09-29): FAITHFUL - all three items resolved.
