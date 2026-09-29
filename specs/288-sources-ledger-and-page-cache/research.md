# Research - feature 288, a sources-consulted ledger and a saved-page cache keyed by URL

## R1. Is the same source read over and over? (measured 2026-09-29)

**Method.** Every source-read event in the research transcripts under `~/.claude/projects/-diagram*` since
2026-09-26 was extracted (`measurement/extract.py`): a `WebFetch`, a `make source-pages` save, a `curl`, and a `Read`
of a saved page (mapped back to its URL through the `/tmp/l7r-check/**/MANIFEST.txt` rows). URLs were normalized by
`measurement/extract_norm.py` (scheme, `www.`, the mobile Wikipedia host, a fragment and a trailing slash dropped;
percent-decoded; lower-cased except a Wikipedia path). Each read was classed against the earlier reads of the same
URL (same agent, same session, same feature, other feature) and against the record: cited if the URL is in a
registry entry or a notes file of the mirror or any clone (`measurement/analyze.py`, `measurement/cited_q.py`).
Token figures are the read's characters / 4, and "carry" multiplies that by the turns it then stayed in context.
The data is in `/diagram/.clones/.tools/logs/reread-2026-09-29/` (`result.json`, `per_url.json`,
`cited_questions.json`); the scripts and the small results are copied beside this file under `measurement/`.

**Figures** (observed 2026-09-29 by the method above; 629 research transcripts; 10,720 source reads of 4,282 distinct pages):
- **Repeats:** 60% of reads repeat an earlier one, mostly the check pipeline re-reading within one session by design
  (`result.json` `classes`: 5,236 repeats within an hour of the one before, 174 more than a day apart).
- **Rejected pages rediscovered:** 208 uncited pages were read again in a later session, 144 of them in a different
  feature, with nothing recording the earlier read. That is about 0.08% of tokens; the real loss is knowledge - the
  later session does not know the page was already judged and found wanting.
- **The page folders are not reused:** `/tmp/l7r-check` holds 4,612 saves of 3,089 pages, filed per run rather than
  per URL, so a saved page is never found again. The cross-session repeats cost about 0.45% of spend.
- **A per-source facts list would not pay:** only 0.05% of reads are fresh reads of a cited page for a new question
  (`cited_questions.json` `split_count`: 105 "new: other question" reads against 4,452 "verify" reads); nearly all
  re-reading of cited pages is quote-check re-verifying verbatim passages, which a facts list cannot replace.

**What it decided.** The GM asked for both cheap fixes (request.md): a ledger, so an earlier read and its outcome are
known, and a cache, so a saved page is found again. No guard: the saving is too small for a refusal to be worth a
false firing; the tooling prints what is known at the moment it matters and saves the page where it can be found.

## R2. The one-time seed and import (run 2026-09-29)

**Method.** `make sources-import` (feature 288 plan D9), run once on the host from this clone at the landing, then
counted from `/diagram/.specify/sources-consulted.jsonl` and `/diagram/.specify/page-cache/` (observed 2026-09-29).

- **The ledger seed:** 7,161 lines, one per URL, feature and session of the measurement's reads, covering all 4,282
  URLs of `per_url.json` and all 10,720 of its reads. 3,847 lines (1,458 URLs) are `cited:<key>`, where a registry
  entry of this clone carries the URL; 3,314 are `unknown-outcome`. The measurement counted 1,625 URLs "in a registry"
  (R1) because it also read every other clone's unlanded entries; the seed reads this clone's, which is main's.
  A seeded line's questions are what the read asked of the page: a fetch prompt for an agent's `WebFetch`, the
  command line itself for a main session's `make source-pages` - the measurement recorded no better question for
  those, so the seed carries what it has.
- **The first fill pass** (the first `make sources-consulted` after the seed) added 433 `cited:<key>` lines: registry
  entries whose pointer the measurement never saw read (entries written before 2026-09-26).
- **The page-cache import:** 1,317 manifests under `/tmp/l7r-check`, 3,853 saved rows; 23 excerpts and 7 rows whose
  file was gone were skipped; 2,365 distinct pages imported, 106 MB on disk (observed 2026-09-29 by the method above, `du -sh`), each marked `exact: false`. R1's "4,612 saves of
  3,089 pages" counted every saved-page READ the transcripts showed, excerpts and since-deleted runs among them; this
  counts the whole pages still on disk.
