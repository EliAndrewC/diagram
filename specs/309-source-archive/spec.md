# Feature Specification: Source archive

**Feature Branch**: none - committed on `main` in the clone (`SPECIFY_FEATURE=309-source-archive`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: download a copy of every external source the research record cites -
*"every webpage we cite and every pdf of every academic paper"*, and *"even things which seem at low risk of going away, like
wikipedia pages"* - into the private repository <https://github.com/EliAndrewC/diagram-research>, as a hedge against
*"websites going offline, failing to be maintained"* or *"changing URLs in a website redesign"*, with *"backup links to the
Github where we check these in"*. The repository is private on purpose (copyright): *"for now I just want an archive."*

## Context (observed 2026-10-02)

- The registry is `.claude/skills/diagram/research/sources/010-works-cited/`: **2,126** entries. A source's URL is written in
  its entry's first paragraph; 1,454 entries carry one URL in the common `(https://...)` form, 21 carry two to thirteen, and
  651 carry a URL in another form (`in Japanese; https://...`) or none (a print work). Most-cited hosts: ja.wikipedia (437
  links), kotobank (245), en.wikipedia (158), zh.wikipedia (151), J-STAGE (62), zh.wikisource (56); 105 entries link a PDF.
- The feature-288 page cache (`<mirror>/.specify/page-cache/`, ~3,000 pages, 148 MB) is NOT an archive: it holds the
  visible text only, not the page as served; it is host-local and gitignored; a copy older than seven days is fetched again;
  and it holds pages that were read and rejected as well as the cited ones.
- `EliAndrewC/diagram-research` is private, empty, and the session's GitHub PAT (`load_secrets(...).github_pat`) has push.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every source already cited is archived (Priority: P1)

A one-time backfill walks every cited URL (FR-001: every URL in a registry entry and every URL a footnote links) and stores, in the archive repository, the page or file as the
site served it, its readable text, and a record of when and from where it was taken.

**Why this priority**: it is the GM's request; every day before it runs is a day a cited page can vanish unrecorded.

**Independent Test**: after the backfill, a coverage report lists every cited URL (FR-001) with its outcome, and every outcome is
one of archived / archived from an earlier snapshot / unreachable (with the reason); a sample of archived copies opens offline.

**Acceptance Scenarios**:

1. **Given** the 2,126 registry entries and the footnotes, **When** the backfill runs, **Then** every cited URL (FR-001) has an archive outcome, and
   every reachable one has its served bytes stored (an HTML page as HTML, a PDF as the PDF), its text, and its capture record.
2. **Given** a Wikipedia article, **When** it is archived, **Then** its capture record names the article revision it was
   taken at, so the copy can be matched to the live history later.
3. **Given** a URL the live site no longer answers (an error status, a dead host, a page that redirects to a site's front
   page), **When** the backfill reaches it, **Then** the newest earlier copy that a public web archive holds is stored in its
   place and marked as taken from there with that copy's date; where none exists, the outcome is unreachable with the reason,
   and the page-cache text is stored as the fallback copy where the cache holds one.
4. **Given** the backfill stopped part-way, **When** it is run again, **Then** it resumes and does not fetch again what is
   already archived.

---

### User Story 2 - A source cited from now on is archived when it is cited (Priority: P1)

When a session registers a new source (`make reserve KIND=registry KEY=<k> URL=<u>`, or a registry entry's URL is added or
changed), the page is archived as part of that step, so the archive never falls behind the record.

**Why this priority**: without it the archive is a snapshot of 2026-10-02 and begins rotting from the other end.

**Independent Test**: register a source in a scratch run; the archive gains its copy; a cited URL (FR-001) with no archive outcome
fails the record check that runs at the push, naming the command that archives it.

**Acceptance Scenarios**:

1. **Given** a new registry entry, **When** it is reserved with its URL, **Then** its page is archived before the command
   returns, or the command reports the failure and the outcome is recorded as unreachable.
2. **Given** a cited URL (FR-001) with no archive outcome, **When** `make record CHECK=1` runs (the gate and the push run it),
   **Then** it fails, naming the URL and the command that archives it.
3. **Given** two sessions archiving at once, **When** both write, **Then** neither loses the other's copies.

---

### User Story 3 - The GM can find a source's copy from the record (Priority: P2)

Each source's page in the built record carries a link to its archived copy in the archive repository (the GM's *"backup
links to the Github"*), which opens for the GM, who has access, and for no one else.

**Why this priority**: an archive the GM cannot reach from the citation is an archive they will not use when a link breaks.

**Independent Test**: build the record; a source page shows an archived-copy link beside its live link; following it (signed
in) opens that source's capture.

**Acceptance Scenarios**:

1. **Given** an archived source, **When** the record is built, **Then** its source page shows the live link and an
   archived-copy link with the capture date.
2. **Given** a source whose outcome is unreachable, **When** the record is built, **Then** the page says no copy was
   archivable and when that was found.

---

### User Story 4 - The GM's download directory is an inbox (Priority: P1, Amendment 1)

The GM downloads a file a bot cannot fetch into `/host-l7r-repo/academic-sources/`. Once it is in the archive repository
and pushed, it is deleted from that directory, so whatever is still there has not been processed yet (the GM: *"looking
at that directory is just a good way to know whether there is something that we have not processed yet"*).

**Why this priority**: the GM asked for it in this feature, and it changes where a session reads a downloaded copy.

**Independent Test**: drop a file in a scratch inbox; `make archive-inbox` archives it, verifies the push, deletes it, and
the file is found again by `make archive-find`; a file whose push fails stays in the inbox.

**Acceptance Scenarios**:

1. **Given** a file in the inbox matched to a cited key, **When** the inbox is processed, **Then** it is archived under
   `gm-copies/`, the key's rows naming it, pushed, confirmed on GitHub, and only then deleted from the inbox; its match row keeps where it went.
2. **Given** a file in the inbox that copies no cited source, **When** the inbox is processed, **Then** it is archived
   all the same (Amendment 1: *"store sources which we ourselves do not end up citing"*), under `gm-copies/` with no keys, and deleted.
3. **Given** the GM's two lists (`TO-DOWNLOAD.md`, `for-the-gm-fetch-list.md`), **When** the inbox is processed, **Then**
   they stay: they are the GM's notes, not sources.
4. **Given** a push that fails, **When** the inbox is processed, **Then** nothing is deleted.

---

### User Story 5 - Every page a session reads is archived, cited or not (Priority: P2, Amendment 1)

A page a research session reads and does not cite is archived too, so a later question can consult it again from the
archive (the GM: *"When we check a paper for one fact, it may not have what we need ... we may end up wanting to check the
paper later for a different fact"*). The GM chose every page read, the earlier reads included.

**Independent Test**: `make source-pages` on a URL archives it; the earlier reads on the sources-consulted ledger are
archived by a backfill, from a live fetch where the page answers and from the page cache's saved text where it does not.

**Acceptance Scenarios**:

1. **Given** a page read with `make source-pages`, **When** the read finishes, **Then** the page has an archived copy and a
   manifest row, cited or not.
2. **Given** the ~4,900 URLs on the sources-consulted ledger (observed 2026-10-02: 4,903 distinct, 3,072 with saved text),
   **When** the consulted backfill runs, **Then** each has a row: a whole live capture where the page answers, else the
   saved text, else unreachable with its reason.

---

### User Story 6 - A session looks in the archive before the web (Priority: P1, Amendment 1)

The research procedure's first step for a source is to check whether we already have it (the GM: *"our research procedure
should include a step where we first check to see if we already have something, rather than going out and trying to find it
on the internet"*). `make archive-find` answers by URL, by registry key, or by words in the archived text, naming the local
copy to read.

**Independent Test**: `make archive-find TERMS="..."` finds an archived page by a phrase in its text and prints its local
path; the research rules, the page-session rules and the reading agents' contracts name the step.

**Acceptance Scenarios**:

1. **Given** an archived source, **When** a session asks by URL, key or a phrase in it, **Then** it is told the copy's local
   path and its row, without a fetch.
2. **Given** the procedure documents, **When** a session starts a research pass, **Then** the first step they name is the
   archive lookup, and a copy the GM downloaded is read from the archive once the inbox has moved it.

---

### Edge Cases

- **One source, several URLs**: every URL is archived; the entry links each copy.
- **A source with no URL** (a print work): nothing to fetch; its outcome is "no online copy" and the coverage report counts it.
- **A URL that changed after it was cited** (a redirect to a new address): the copy is taken from where the redirect lands,
  and the capture record keeps both addresses.
- **A page that needs a script to show its text** (the whole-page capture renders it as a browser would),
  **or refuses an automated reader**: where the GM has downloaded a copy of the source (into
  `/host-l7r-repo/academic-sources/`, then moved into the archive by the inbox, FR-013), the archived copy stands as the
  source's copy (FR-012); otherwise an existing web-archive snapshot
  (FR-005); only then the served bytes as served, with the page-cache text beside them where their text is empty, and the
  outcome says the copy is partial.
- **A file larger than the archive host accepts in one file** (GitHub refuses one past 100 MB): stored in parts, with a
  checksum of the whole so the parts can be joined and verified.
- **A URL cited by several entries**: archived once, linked from each.
- **Re-archiving**: a later capture of the same URL is stored beside the first, dated, never over it - the copy the
  citation was made from is the one that must survive.
- **The archive host is unreachable at cite time**: the reserve still succeeds (research is not blocked by GitHub), the
  copy is held locally, and the outcome is "pending upload" until the next archive run sends it; the record check counts a
  pending upload as covered for a set grace period and then fails.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every URL the record cites - every URL in a registry entry and every URL a footnote in
  `research/questions/*.notes.html` links - MUST have exactly one archive outcome: archived (live), archived (earlier
  web-archive snapshot), archived (the GM's downloaded copy), partial, unreachable (with reason), pending upload, or no
  online copy.
- **FR-002**: An archived copy MUST hold the bytes as served (HTML document or file, unaltered); for a web page, ALSO the
  whole page as a reader saw it - its images, stylesheets and fonts - as one self-contained file that opens offline in a
  browser (the GM: *"download the whole webpage with images and css and such and not just the html content"*); the
  extracted readable text; and a capture record: the URL cited, the URL finally fetched, the time, the HTTP status, the content type, a checksum of
  the bytes, the source key(s) that cite it, and for Wikipedia and other MediaWiki sites, the revision id.
- **FR-003**: Copies MUST live in the private repository `EliAndrewC/diagram-research`; nothing from the archive is
  published anywhere public. The layout keeps every directory to a few hundred entries as the archive grows to every page read (4,903 distinct
  URLs on the sources-consulted ledger, observed 2026-10-02, cited ones included)
  (the GM, mid-backfill: *"limit the number of directories in any given directory to no more than a few hundred"*):
  a URL's captures under `<id[:2]>/<id>/`, the GM's copies under `gm-copies/`, the manifest's rows under
  `research/archive/<id[:2]>/`; a key finds its copies through the manifest and `make archive-find` (FR-015).
- **FR-004**: A one-time backfill MUST archive every cited URL (FR-001) as of the run, resumably, reporting a coverage table
  (counts per outcome, and each unreachable URL with its reason).
- **FR-005**: Where the live page cannot be fetched, the backfill MUST try the newest snapshot a public web archive already
  holds and store that, marked with its source and date.
- **FR-006**: Registering a source with a URL MUST archive that URL in the same command; a failure is recorded as an outcome,
  never silently dropped, and never blocks the registration.
- **FR-007**: `make record CHECK=1` MUST fail on a cited URL (FR-001) with no outcome, naming the URL and the command that
  archives it; it MUST read a manifest committed in this repository, so the check needs no network.
- **FR-008**: The archive repository has ONE working copy on the host, shared by every session and pushed straight to
  GitHub - no per-clone copy, no sync-in/done route (the GM: *"you can just push directly to it without each of our diagram
  .clones/ having its own copy"*); writes from concurrent sessions MUST be serialized under a host-wide lock, as `make
  reserve` is.
- **FR-009**: A capture MUST never overwrite an earlier capture of the same URL.
- **FR-012**: Every file in `/host-l7r-repo/academic-sources/` that is a copy of a cited source MUST be matched to its
  source key and archived, the key's manifest rows naming it (copied unchanged; the file is left in place until FR-013
  removes it after a confirmed push) - whether or not the registry
  entry mentions the file, and IN ADDITION to the cited URL's own capture attempt, never in place of it. The match is
  measured in the plan: how many files, how many matched, the unmatched listed. The outcome "archived (the GM's downloaded
  copy)" is used only where the live fetch of that source fails or is refused.
- **FR-013** (Amendment 1): `/host-l7r-repo/academic-sources/` is an INBOX. Every file or saved-page folder in it except
  the GM's two lists is archived under `gm-copies/` - its key's rows naming it where it copies a cited source, its keys
  empty where it copies none - and deleted from the inbox only after the push is confirmed on GitHub. The match table keeps every processed file's
  name, keys and archive path, so a copy stays findable after its file is gone. The 7 files that copy no cited source today
  are archived and deleted too.
- **FR-014** (Amendment 1): every page a session reads is archived when the read is recorded, cited or not - by any route
  onto the sources-consulted ledger (`make source-pages`, `make source-outcome`, `make reserve ... URL=`); a row records
  it, and a URL that already has a row is not captured again. A one-time consulted backfill archives every URL on the sources-consulted ledger with no row: a whole live capture where
  the page answers, else the page cache's saved text (`partial`), else `unreachable` with its reason.
- **FR-015** (Amendment 1): `make archive-find URL=<u> | KEY=<k> | TERMS="a|b"` answers from the manifest and the archived
  text, without a fetch, naming each copy's local path.
- **FR-016** (Amendment 1): the research procedure names the archive lookup (`make archive-find`) as the first step for
  any source, and `make archive-inbox` as a step of every research pass (at its start, and whenever the GM has downloaded
  something), so the inbox is a queue that empties as it is used - in the root `CLAUDE.md`'s Research section,
  `docs/research-doctrine.md`, `research/CLAUDE.md` (its download-list passage rewritten: a downloaded copy is read from
  the archive once the inbox has moved it), `container-scripts/page-session-rules.md` and the `source-reader` and
  `quote-check` contracts.
- **FR-010**: The built record's source pages MUST show an archived-copy link with its capture date beside each live link,
  or say that no copy could be archived.
- **FR-011**: The GitHub credential MUST be read from the existing secrets loader and never written to a file, a log, a
  commit or a command line that the hooks record.

### Key Entities

- **Capture**: one URL fetched once - bytes, text, capture record; identified by URL and capture time.
- **Archive manifest**: committed in this repository; one row per archived URL - every cited URL (FR-001) and every page
  read (FR-014) - with its source key(s) or citing note(s) where it is cited, outcome, path of the latest capture in the
  archive repository, its date and checksum; beside it `gm-copies.json`, every GM file processed (FR-012, FR-013) with
  its keys and archive path. The record check and the source pages read it; the lookup searches it.
- **Archive repository**: `EliAndrewC/diagram-research`, private; holds the captures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the backfill, every cited URL (FR-001) has an outcome in the manifest, and the share archived (live or from
  an earlier snapshot) is reported; every unreachable one carries a reason.
- **SC-002**: A random sample of 20 archived copies - at least 5 Wikipedia, 5 PDFs, 5 small sites - each opens offline from a
  fresh clone of the archive repository and contains the passage its registry entry quotes (where the entry quotes one).
- **SC-003**: A source registered after the feature lands has its copy in the archive repository with no step beyond the
  registration command.
- **SC-004**: The record check fails on a cited URL with no manifest row, proven by a test that removes one row.
- **SC-005**: Re-running the backfill on a complete archive fetches nothing.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws and states nothing on a map; it changes the research tooling and the source pages of the built record.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Archive every cited URL (FR-001), Wikipedia included | the GM's ruling | *"even things which seem at low risk of going away, like wikipedia pages, seem worth storing to me"* | `request.md` |
| The archive is private; nothing is republished | the GM's ruling | copyright: *"for now I just want an archive"*; a public copy waits on the author's permission | `request.md` |
| A web page is captured whole - images, styles and fonts - as one self-contained offline file, beside the served HTML and the text | the GM's ruling | *"we should download the whole webpage with images and css and such and not just the html content"*; the session had proposed text and HTML only to save space, and the GM chose the whole page. Cost: a larger archive, measured on a sample in the plan before the full run. A PDF is stored whole | `request.md`; the capture module's docstring |
| A dead page falls back to an existing public web-archive snapshot | tooling decision | a copy someone else took is better than none, and it is labeled as theirs with its date | this spec; the capture module |
| No submission to a public web archive, no change to how citations link | scope | not in the GM's request; offered by the session and not taken up | this spec |
| `academic-sources/` is an inbox: a file is deleted once its archived copy is pushed and confirmed | the GM's ruling (Amendment 1) | *"once something has been added to the diagram research repository and then pushed, then we can delete it"*; the deletion waits on a confirmed push so nothing exists only locally. The directory is in the GM's own repository, so the deletions show in that tree for the GM to commit; nothing here runs git there | `request.md`; `scripts/_archive.py` |
| Every page a session reads is archived, the ~4,900 earlier reads included | the GM's ruling (Amendment 1, chose "Every page we read") | a page read for one fact may answer a later question | `request.md` |
| The archive lookup is the first step of a research pass | the GM's ruling (Amendment 1) | *"first check to see if we already have something, rather than going out and trying to find it on the internet"* | `research/CLAUDE.md`, the page-session rules, the reading agents' contracts |
| Captures sharded `<id[:2]>/<id>/`, the GM's copies under `gm-copies/`, the manifest sharded alike | the GM's question answered by the session (`request.md`) | GitHub lists only a directory's first 1,000 entries (observed 2026-10-02: the contents API returned 1,000 of the archive's 1,775 top-level entries), and the archive is headed for the ledger's 4,903 URLs (observed 2026-10-02); 256 two-hex buckets hold about 19 each at that size (derived: 4,903 / 256) and stay under 300 a bucket to about 76,800 URLs (derived: 300 x 256); the GM's copies need no bucket (40 entries, the FR-012 match of 2026-10-02, tasks T12). Cost: a key's copies are not browsable by key name - the manifest and `make archive-find` find them | `scripts/_archive.py:capture_base`, `record/archive.py:ROW_GLOB` |

## Assumptions

- The registry is NOT the complete list of what the record cites (spec-fidelity round 1, measured 2026-10-02): about a
  dozen URLs that footnotes in `questions/*.notes.html` link directly appear in no registry entry, so FR-001 takes both.
- The GM's own campaign notes (github.com/EliAndrewC/gm-assistant links) are archived like any other URL - they are cheap,
  and the literal request is every cited page.
- Fetching ~2,200 URLs politely (a delay per host) takes hours, not days; the backfill runs in the background on the host.
- The archive's size is expected to be a few hundred MB to low GB; the plan measures it on a sample before the full run.
- GitHub's per-repository soft limit (several GB) is not reached; if the measured estimate says otherwise, the plan raises it.

## Review

- Round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 3 items - (1) footnotes link about a dozen URLs no registry entry
  carries, so FR-001/004/007 and the manifest take every footnote URL too; (2) sources read from the GM's downloaded copy in
  `academic-sources/` archive that file (FR-012, a new outcome, the edge case reordered); (3) the Wayback row's reason no
  longer quotes the GM's hosting answer as a ruling on it. Addressed as stated.
- Round 2 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 2 items - (1) the user stories, their tests and the Wikipedia
  decision row still said "registry URL": now "every cited URL (FR-001)"; (2) FR-012 chose the GM's copies by an entry's
  marker, which misses most (42 files, 5 entries name one): it now matches every file in `academic-sources/` to its key,
  measured in the plan, archived beside the live capture and in addition to it, the GM-copy outcome used only where the live
  fetch fails.
- Round 3 (spec-fidelity, verify, 2026-10-02): the spec FAITHFUL; 1 item on the plan - D2 still chose the GM's copies by the
  entry marker, put them ahead of the live fetch, and lacked FR-012's match measurement. Addressed in `plan.md`: the live
  fetch first, every matched file copied in addition, and the measured match (42 entries, 33 matched over 30 keys, 7 copy no
  cited source).
- Amendment 1 (2026-10-02, the GM mid-backfill, verbatim in `request.md`): User Stories 4-6 and FR-013 - FR-016 - the
  download directory as an inbox emptied once a copy is pushed, every page a session reads archived (the GM chose all of
  them, the earlier reads included), and the archive looked in before the web. FR-012's 7 unmatched files, listed and not
  archived before, are archived under FR-013.
- Amendment 1, round 1 (spec-fidelity, 2026-10-02): CHANGES REQUIRED, 3 items - (1) FR-014 now archives a page read by
  any route onto the ledger (`source-pages`, `source-outcome`, `reserve`), not `source-pages` alone; (2) FR-012 leaves the
  GM's file in place until FR-013 removes it, the Edge Case points at the archived copy, the manifest entity covers every
  archived URL and the GM-copy table; (3) FR-016 names `make archive-inbox` as a step of every research pass and adds the
  root `CLAUDE.md` and `docs/research-doctrine.md`. Also folded in: the GM's sharding question (FR-003, a Decisions row).
