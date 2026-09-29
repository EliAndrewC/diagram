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
