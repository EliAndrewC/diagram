# Brief - feature 403, the earlier money answers' open leads. Session 1: write (0259, 0262, 0264, 0265)

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

- **0259 "What did a night at an inn cost?"** - Morisada 上 koma 79-80: Kyoto and Osaka first-class inns 3 monme 5 bu of
  silver with two meals; Kyoto's lesser inns and its merchants' inns 200-250 mon, the merchants' including the midday
  meal (if 三條以下 can be read two ways, say which reading is the record's); Osaka's low-grade inns about 200 mon; Edo
  about 248 mon with two meals; Osaka's beggars' lodging (ぐれ宿) 36 mon, no bedding; the Tokaido 200 mon and Nakasendo
  148 before Ansei, 700-800 by Keio. ATTESTED, each with its city and the date Morisada gives (1837-53 unless the text
  says otherwise). Name the 宿村大概帳 print edition (『近世交通史料集』, NDL-only) in the absence note it touches.
- **0262 "What did sake cost, by the shop and by the cup?"** - Morisada 下 koma 229 (the best sake a sho: Osaka 164 mon and
  Edo 200-248 in his childhood, born 1810; from about Tenpo 「三百五十八十錢或は四百錢」, given as printed, 350-380 or
  400); 上 koma 137 (Edo good morohaku about 250 "thirty years ago", now 350-400; dating it to about the 1810s-20s is the
  record's reading, said so); 上 koma 76 (one go of good sake 40 mon on an Edo soba board); soba, 上 koma 74-76 (16 mon a
  bowl in Edo and Kyoto-Osaka; raised in Keio to 20, then 24 in Edo; the boards' other dishes, their cursive names the
  record's reading; 3,763 Edo soba shops in 1860). The koma 228 handbill (several grades, 42-132 mon, measure unstated):
  transcribe it on the image, or name it as a lead still open.
- **0264 "What did paper and ink cost?"** - SILENT in Morisada after a search of its text (半紙, 一帖, 紙屋, 墨, 筆墨, 墨屋),
  named in the absence note in place of the web query alone.
- **0265 "What did it cost to rent a room or a house?"** - Morisada 上 koma 57: Edo rent (店賃) paid at each month's end to
  the yanushi; the move-in fee (樽代) 2 shu or 1 bu up to 3-5 or even 10 ryo, against Kyoto-Osaka's chit for 1-2 sho of
  sake; festival payments (節句錢); a Tenpo order banning both. ATTESTED ONLY FOR the system; a monthly amount SILENT in
  Morisada, the search named. (Session 2 edits 0265's Beijing wage line after you.)

Keep each question under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0259 0262 0264 0265" FEATURE=403`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `403: `.
4. Append to `specs/403-money-earlier-leads/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/403-money-earlier-leads/briefs/handoff.md` (create it if absent) a `## Session 1` section:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, each changed figure or verdict, old and new, and each search named;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
