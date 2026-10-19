# Brief - feature 403, the earlier money answers' open leads. Session 4: write (0270)

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

- **0270 "What did a shrine's metal furnishings cost?"** - 『高岡史料』 下 (NDL pid 899935, public): read its shrine appendix
  from about IIIF frame R0000523 on (`https://dl.ndl.go.jp/api/iiif/899935/R0000523/full/full/0/default.jpg`) to the
  関野神社 section, and 第四章 工業 (p. 590; in 上, pid 899934, if it is not in 899935) for the caster 甚右衛門, for the 1833 mirrors' cost. A sum found is cited,
  beside the wages as above; if the frames are read and give none, SILENT naming them; if NDL refuses the frames (and the
  viewer), an unread lead, dated as observed. The donor's letters (岡本家文書, quoted on the Yamagen page already cited):
  search once more for a public copy and read it if found; otherwise name them as not found online, dated. A hand mirror's retail price: SILENT in Morisada (its 鏡 hits are the mirror-polisher, no
  fee), named.

Keep each question under the 20,000-byte cap.

## The procedure (session 4: write)

1. `make archive-inbox`. Then `make research-claim Q="0270" FEATURE=403`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `403: `.
4. Append to `specs/403-money-earlier-leads/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/403-money-earlier-leads/briefs/handoff.md` (create it if absent) a `## Session 4` section:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, each changed figure or verdict, old and new, and each search named;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
