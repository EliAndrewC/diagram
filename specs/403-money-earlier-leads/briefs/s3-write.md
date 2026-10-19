# Brief - feature 403, the earlier money answers' open leads. Session 3: write (0256, 0257, 0268, 0269)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you,
the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM asked for every outstanding money research task to be finished. Earlier answers (#3, #4, #6, #7)
left leads unfollowed; two search passes have followed them: `specs/403-money-earlier-leads/passes/morisada-prices.md` and
`passes/other-leads.md` (leads, not citations: read each passage on its page before citing it). Write the found figures
into your questions, and where a question says SILENT, name in its absence note the search that found nothing. A SILENT
is recorded, with its search, in the question that says it. Each new figure sits beside the craftsman's AND the unskilled
laborer's day wage of the same place and period; where no source gives one, say that wage is SILENT and name the nearest,
with its class, its place, its unit and its gap in years. Label every figure the project computes as the project's
arithmetic. No price is converted between coins unless its source converts it or 0277's rates are applied and labeled.
Research only: edit no code, modal, sheet or canon. Change only the sections the new figures or searches touch.

**Reading NDL scans.** 類聚近世風俗志 上 (pid 991466) and 下 (pid 991467) are public in NDL's viewer. Feature 402's scripts
in `specs/402-money-open-leads/measure/` find and read them: `ft.sh <pid> <bundle id> <term>` (NDL full-text search with
the viewer's full request body; bundle ids 991466 `45a5a644-ed77-472c-b3c1-fa0c40e9023f`, 991467
`a095a11b-e2e7-49cc-9c01-0005f73e7d02`; the index is the viewer koma minus one for 下, equal for 上) and `shot.py` (a viewer
screenshot per koma), run with `/usr/bin/python3`. Read every quotation on the page image; images go to source-reader with
`IMAGES=`. The registry already holds `ruiju-kinsei-fuzokushi-jo` (上); add a key for 下 if you cite it.

## Your items

- **#6's leads** - the absence notes of **0256** (cypress-bark, shingle and copper roofs; roofer-days), **0257** (carrying
  stone a ri; mound labor), **0268** and **0269** (a mason's day wage) name the 2026-10-19 search
  (`passes/other-leads.md`, lead 6: nothing new public beyond the two Kawakami papers the record holds).
- Retry the two failed reads: Hasegawa 1987 (Hirosaki University repository; timed out) and nabunken's 「近江の石工たち」
  (HTTP 429). Read, a figure is cited in its question (beside the wages, as above) or the SILENT names it; still failing,
  each is named with the failure and its date as an unread lead.
- Read if public, or name as leads still open: 湯浅隆「近世寺社の造営費用調達について」, the 静岡浅間神社『御再建場所日記』
  翻刻, and KAKEN 19K15191's project page.

Keep each question under the 20,000-byte cap.

## The procedure (session 3: write)

1. `make archive-inbox`. Then `make research-claim Q="0256 0257 0268 0269" FEATURE=403`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `403: `.
4. Append to `specs/403-money-earlier-leads/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/403-money-earlier-leads/briefs/handoff.md` (create it if absent) a `## Session 3` section:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, each changed figure or verdict, old and new, and each search named;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
