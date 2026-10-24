# Brief - feature 412, the basket in every era. Session 1: write (question 1 and the Japanese wages)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant prices one standard basket in each era the record cites, to convert every historical amount
(issue EliAndrewC/diagram#13, verbatim in `specs/412-money-basket-every-era/request.md`). Its question 1: salt, firewood or
other cooking fuel, and a back-tenement room in Kyoto or Osaka in 1745-1754, **or the nearest dates found**, and how much salt
a person used a year. Five search passes ran; yours are `passes/q1-kyoto-salt-fuel-rent.md` and the Japanese wage parts of
`passes/q2q3-japan-series.md` (leads, not citations: read each passage or cell on its page before citing it; where it does
not read as the pass says, write what the page does say, or SILENT). Write into FOUR existing questions; no new question.

A figure from outside Kyoto/Osaka 1745-1754 is ATTESTED ONLY FOR its place and years, the gap stated (the issue asks for the
nearest dates found). Label every figure the project computes (a mean, a per-kg or per-million-BTU figure, grams of silver)
as this project's arithmetic, with what it assumes; put the arithmetic in `specs/412-money-basket-every-era/measure/` as a
script and cite it. No price is converted to koku. Research only: edit no code, modal, sheet or canon. Keep each question
under the 20,000-byte cap; if one would pass it, split along its topics and say so in the handoff.

## The spreadsheets

The Mitsui Bunko series is Bassino's transcription, `https://gpih.ucdavis.edu/files/Japan_1710-1871.xls` (sheets "Mitsui
Bunko Kyoto T6", "... Edo T7", "... Osaka T8", and "Sources and conversion" - its notes, quoted from that sheet). A copy is at
`/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/gpihjp/Japan_1710-1871.xls` with a text dump in
`.../scratchpad/dumps/`; re-download if absent. A cell of a public spreadsheet is a readable page (research/CLAUDE.md): quote
the cell, name its sheet and row, and link the file. Read with xlrd; give source-reader and quote-check a row dump of each
cited row. Columns: 白米, 麦, 餅米, 塩 (per koku), 味噌 (per 10 kan), 醤油, 酢, 酒 (per koku), 煎茶, 煙草 (per kin), 炭 and 薪
(per 10 kan), 水油 (per koku), 蝋燭 (per 100 monme), 日雇賃 (per man), all in silver monme, spring and autumn.

## Your items

- `0273-what-did-salt-cost.html`: Kyoto's salt 1745-1754 (塩, per koku, the twenty seasons and their mean, this project's
  arithmetic); a per-kg figure only from a stated weight of a koku of salt, labeled as assumed if no source gives it (the pass
  searched 塩 一升 目方, 赤穂 四斗俵 貫, 塩 一俵 重さ and found none - try once more, then write the silence). How much salt a
  person ate a year: Huang Guoxin 2021 (`https://ha.sysu.edu.cn/article/90`), 「清代人均食盐消费量应该在今市秤11斤也就是当时
  的计量9斤多」, ATTESTED ONLY FOR the Qing official reckoning; Japan SILENT with the search. A lead to try: the Kashimo diary
  already in 0273 bought 52 sho one day of 1772 - if the booklet gives the household's size, a household's year; else name it.
- `0279-what-did-charcoal-cost.html`: Kyoto firewood 1745-1754 (薪, per 10 kan = 37.5 kg), priced by weight; the per-kg figure
  and a price per million BTU as this project's arithmetic, the wood's energy (about 15 MJ/kg air-dry) labeled as a modern
  assumption with its source if one is cited, else as a guess. Mitsui's charcoal (炭) for Edo 1710-1716 and 1818 on, and Osaka
  1818 on: check the Osaka 1818-23 rows, where charcoal reads cheaper than firewood per 10 kan, against the sheet; if the sheet
  reads so, cite it with that said, else write what it reads. The Kyoto sheet has no charcoal column: say so.
- `0265-what-did-it-cost-to-rent-a-room-or-a-house.html`: a back-tenement room in Kyoto or Osaka, 1745-1754: SILENT, with the
  pass's searches in the absence note (京都 裏借家 家賃 銀 匁 宝暦/寛延/延享; 近世京都 借家 家賃 論文; 杉森哲也/塚田孝 借家 店賃;
  三井 京都 貸家 家賃; the osaka-angenet Tsukada lecture, no amounts). Name Edo 1804-1830, 300-500 mon a month, already in the
  question, as the nearest, with its gap.
- `0250-what-did-an-unskilled-laborer-earn.html`: Mitsui's 日雇賃 by decade for Kyoto (1741-1762, 1791-1871) and Edo
  (1818-1871), decade means as this project's arithmetic: Kyoto about 0.85 in the 1790s, 0.94 in 1804-29, 0.98 in 1830-44,
  1.04 in the 1850s, 1.32 in 1860-67; Edo 0.90 flat 1818-1859 (say it reads as a book rate, not a market one, in this
  project's reading), 1.14 in 1860-67, 1.92 in 1868-71. The 1780s and 1872-1879: SILENT, with the search. The pass also found
  that Bassino and Ma's Table A.1 is Kyoto throughout 1741-1871; if 0250 says otherwise, correct it from the paper's words.

**New registry keys** (at most ten this session): the GPIH Mitsui file (Bassino 2006), Huang Guoxin 2021, and any source the
salt-weight or energy search cites - expect three to five.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0250 0265 0273 0279" FEATURE=412`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, a row dump for a spreadsheet). A new source takes `make reserve KIND=registry
   KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `412: `.
4. Append to `specs/412-money-basket-every-era/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/412-money-basket-every-era/briefs/handoff.md` (create it if absent) a `## Session 1` section:
   - `- SECTION=<NNNN>/<id>` for each question touched;
   - per figure question 1 and question 3 ask, its verdict and the fragment file (the reply on #13 is built from this);
   - each search named; the new registry keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
