# Brief - feature 410, charcoal, ordinary and fine white. Session 1: write (new 0279)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you,
the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant's money skill prices charcoal by its own guess (issue EliAndrewC/diagram#11, verbatim in
`specs/410-charcoal-prices/request.md`): black and white charcoal by the bale with its weight, retail and wholesale; the
white-to-black ratio; burner-days per bale; what carriage added; a Ming/Qing comparison. Two search passes have run:
`specs/410-charcoal-prices/passes/japan.md` and `china.md` (leads, not citations: read each passage on its page before
citing it; where it does not read as the pass says, write what the page does say, or SILENT). Write ONE new money question,
**0279 "What did charcoal cost?"**, tagged as 0262 or 0276 are (look at `research/tags.json` and `contents.json`), Japan
first, then the Qing comparison. Each figure sits beside the craftsman's AND the unskilled laborer's day wage of the same
place and period; where no source gives one, say that wage is SILENT and name the nearest already in the record (0250,
0255, 0257, 0275 hold them), with its class, place, unit and gap in years. Label every figure the project computes as the
project's arithmetic. No price is converted to koku; between coins only by a rate the source gives or 0277's, labeled.
Research only: edit no code, modal, sheet or canon. Keep the question under the 20,000-byte cap (split into a second money
question, tagged the same, if it would pass it).

**Already answered, nearest, OPEN.** The bale's weight is in 0197 (`0197-charcoal-yards-and-charcoal-stores.html`, about 4
kan): name it, and give the Itsukaichi bulletin's 4, 5 or 6.5 kan as the variation. A figure for which only a nearest exists
(another century, another fuel) is OPEN: name the nearest as a nearest, never as an answer, and put the search in the
absence note.

## The figures (from the passes)

- Black/ordinary by the bale, retail: Ōishi 1966 table (12), Edo 1842, 上中下炭 500/448/364 -> 466/422/342 mon a bale,
  佐倉炭 144/132/120 -> 135/124/112 (read on page images pp. 86-87; key oishi-1966-tenpo13-bukka-kakiage, live host 406 -
  `make archive-find`, then render the PDF's pages with pdftoppm and pass the images with `IMAGES=`). No weight printed; the
  grades are not called black or white: say so. 佐倉炭's low price is as printed, unexplained: say so.
- White, white against white: Itsukaichi 郷土あれこれ 33 (2022), 1716 via Mitamura Engyo: Kumano 400-500 mon a bale, 8-9
  bales a ryo, Hachiōji about 20 a ryo; Tama charcoal "all white". Japan's black-against-white SILENT.
- Kiln output: the same bulletin's undated statement, 20-30 bales an earth kiln of black in 3-4 days, 2-3 a stone kiln of
  white - ATTESTED ONLY FOR the author's general statement. Burner-days, yield SILENT.
- Wholesale and carriage: OPEN/SILENT - the brokers' levy 8 (later 12) mon per 8-bale horse-load (a tax), horse-loads of 6-8
  bales, the 1814 women carriers (no amount); 809,710 bales by ship in 1726 (second hand, tamaikada blog - cite only if
  the page reads so).
- Nearest only: Akita 1600, 181 kanmon for 120 bales of smith's charcoal (Wayback copy of 高橋正's paper).
- Qing: Gao 2022 (key gao-shouxian-jiuqing-wuliao): Beijing 1736 炭 0.225, 黑炭 0.5/0.6, 白炭 1.1, 紅螺炭 1.06 tael per 100
  jin; 1615 炭 0.12-0.75, 白炭 0.49-1.113; wages 154 / 75 cash (Gao's 800 cash a tael). Bochum Zhili 1769 木炭 by district
  (the pass's table, with each district's 匠 and 夫 wage rows): give the range and a few named districts, with sheet and
  row. 武編 (key wubian-qianji-05): 170 jin 0.51 tael, 500 jin 0.85 tael, smiths 0.03-0.05 a day.
- Leads to try if time allows, else name them in the handoff: Morisada 生業 pages (pid 991466, pp. 87-186) for 炭売 -
  `specs/402-money-open-leads/measure/shot.py` takes a koma screenshot (run with `/usr/bin/python3`; skip it if memory is
  low); the 飯能市 1822 broker agreement PDF.

**Reading what the reader cannot.** A PDF `make source-pages` cannot read: download it with curl into its own empty
directory and read it with pdftotext, or render its pages (pdftoppm) and pass the images to source-reader with `IMAGES=`. A
Bochum .xls: read the cells with xlrd and give source-reader a text dump of the rows cited.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0279" FEATURE=410` (create the question first per
   `research/editing-the-record.md` if the claim needs the file).
2. For each page you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, page images with `IMAGES=`). A new source takes `make reserve KIND=registry
   KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the eleventh new key, follow the continuation rule.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `410: `.
4. Append to `specs/410-charcoal-prices/implementation-check.md` (create it if absent) one line:
   `- 0279: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/410-charcoal-prices/briefs/handoff.md` (create it if absent) a `## Session 1` section:
   - `- SECTION=0279/<id>`;
   - per figure the issue asks for, its verdict and the fragment file (the reply on #11 is built from this);
   - each search named; the new registry keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
