<!-- page-load: kind=assertions -->
# Brief - feature 428, working days and terms of engagement. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-research`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#20 (verbatim in `specs/428-working-days-and-performances/request.md`,
with the canon each answer sits beside), parts 1 and 2. Japan first, China beside it. Every figure gets a verdict - ATTESTED,
ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - per kind of worker, with place and date. Any days-worked
figure from rest days a month, and any yearly total, is this project's arithmetic, labeled. A study's ASSUMED working year (the
250 days of the wage comparisons) is reported as an assumption, never as a count. Two sources that disagree are both given, not
reconciled by guess. Say, in a sentence per question, how the findings stand against the canon the request names.

**Your passes:** `specs/428-working-days-and-performances/passes/q1-working-days.md` and `passes/q2-engagement.md` - leads, not
citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or
SILENT. The passes read some pages from local copies (Kumon 2020 and the postal-museum PDFs by pdftotext; research_09_02 by OCR;
the 2013 chinanews page decoded from GBK) - their paths are in the passes; get each page into the record's tooling with `make
archive-find` / `make source-pages` (an image page goes to the checks with `IMAGES=`). The 古川貞雄『村の遊び日』 figures come only
through three summaries: cite each as a summary of 古川, never as 古川.

**Already in the record - name by file, do not repeat:** 0250 (the unskilled day; no count of working days), 0115 (servants;
degawari), 0260 (porter and horse fares), 0307 (clerks, guards, skilled servants: live-in clerks yearly, Beijing escort agencies
paid yearly), 0305 (books; no Japanese copyist's rate).

## Your items

1. **Working days**, a NEW money question (`make reserve KIND=question`), its title asking how many days a year a worker worked;
   `subject=money`; a pointer to it from 0250, 0115 and 0260. Per kind: a day laborer (hiyatoi); a live-in servant (yabuiri and
   festival days; term farm servants' contract rest days, Kumon 2020); porters - post-station porters and packhorse drivers and
   porters hired by the job in towns and ports - busy or idle between jobs, by season; a carpenter or construction worker (rain days, and WINTER
   separately - a figure or SILENT; weather idling is not winter); a farm laborer BY SEASON (a seasonal split, or SILENT: a yearly count is not one); the village's collective rest days (asobi-bi), not added to a servant's contract days unless
   a source says both applied. China beside it: the 250 days of Allen et al., Bassino and Ma, Liu 2022 quoted as an assumption;
   Qing accounts' notional 360; Li and Pomeranz's 200 spinning days as an estimate. Against the canon: a weekly county market day
   and no working calendar.
2. **Terms of engagement**, in 0307 or a sibling question by size (0307's prose cap): an armed escort of goods or cash (Japan:
   the courier house's own convoy, the cash courier's short sword, the by-the-run unarmed couriers and the yearly village courier;
   China: escort-masters kept on by the agency, trips a year, house guarding between trips, clients' contracts by trip, season or
   year); a literate scribe or clerk (China paid by the document; Japan's kept-on ward clerk, petition-writing by the case at the
   litigants' inns; a day-hired scribe SILENT unless found). Against the canon: scribes among the heimen.

**New registry keys** (at most ten): as the passes name them; at most ten. If more are needed, `make reserve`'s eleventh key
writes a continuation brief - follow it.

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="0307" FEATURE=428`, `Q="0250"`, `Q="0115"`, `Q="0260"`, and claim the new
   question's number (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `428: `.
4. Append to `specs/428-working-days-and-performances/implementation-check.md` (create it if absent) one line per touched
   question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/428-working-days-and-performances/briefs/handoff.md` (with `make append`; create it if absent) a
   `## Session S1` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file;
   searches; new keys; leads not followed. This is task T01.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
