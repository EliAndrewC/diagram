# Brief - feature 403, the earlier money answers' open leads. Session 2: write (0250, 0260, 0261, 0266, and the wage line of 0265)

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

- **Gamble's Beijing day wages, 1807-1902** - LSE working paper 123 (archived; its Appendix Table I reprints Gamble's
  fuel-store series): ATTESTED ONLY FOR one fuel store's hands, food extra, the cash units changing around 1860, and any
  further caveat as wp123 itself states it (read it there; add none it does not state). Write it into **0250** (the unskilled wage), **0265** (its line "no Beijing day wage of a
  laborer or a craftsman for the Daoguang era or the 1870s") and **0266** (its note naming Gamble's 1870-1900 wages
  unreached). Gamble 1943 (paywalled) and *Ting Hsien* (restricted loan) are named as not publicly readable.
- **The 1921 *Peking: A Social Survey*** (archive.org, public; p. 431, the gilds' wages "50 years ago" and "25 years ago";
  pp. 195-196, the 1885 jade-workers' strike): write it in where one of your questions needs a Beijing craftsman's wage,
  ATTESTED ONLY FOR what gilds recalled in 1918-19, each wage in its unit as printed (dollars, taels or cents a day), the monthly reading the record's (from p. 184); otherwise
  name it in your handoff as found and not written.
- **0260 "What did hiring a horse or a porter cost?"** - the Zhili official freight rates (Bochum database, chapters 1 and
  13: carts per 100 li, porter, pack animal, boat), ATTESTED ONLY FOR official building work, dated in the source's own
  words ("Qianlong reign") unless 1769 is read on the cited page. Chapter 13 labels the same value "per 100 li" at Tianjin
  and "per li" elsewhere: settle it on the scanned original before citing; if it cannot be settled, leave the rates out
  and name them. Chapters 2-12 and 14-24 (not scanned) and 大清会典事例 (already named unread) are named as leads still
  open. The 宿村大概帳 print edition (NDL-only) is named where the note touches it.
- **0261 "What did cloth and clothing cost?"** - a used kimono's price and a kimono's sewing stay SILENT after Morisada's
  search (仕立, 仕立賃, 仕立代, 縫賃, 縫代, 針賃, 手間賃, 裁縫, 古着, 古手: the trade attested at 上 koma 70, no fee), named;
  the Osaka cotton series "from 1757" is soybeans (Bassino and Ma, archived), and the Mitsui (1952, login; 1989,
  NDL-only) and Miyamoto 1963 (login) books are not public; Koyaizu's 『近世賃金物価史史料』, which 0261's notes cite, is
  NDL-only (pid 14107062), said so.

Keep each question under the 20,000-byte cap.

## The procedure (session 2: write)

1. `make archive-inbox`. Then `make research-claim Q="0250 0260 0261 0265 0266" FEATURE=403`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `403: `.
4. Append to `specs/403-money-earlier-leads/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/403-money-earlier-leads/briefs/handoff.md` (create it if absent) a `## Session 2` section:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, each changed figure or verdict, old and new, and each search named;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
