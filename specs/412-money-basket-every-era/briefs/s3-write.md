# Brief - feature 412, the basket in every era. Session 3: write (new questions B and D, China)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant prices one standard basket in each era the record cites (issue EliAndrewC/diagram#13,
verbatim in `specs/412-money-basket-every-era/request.md`; Japan first, China beside it): per adult a year, rice 114 kg,
soybeans 52 kg, barley and wheat 10 kg, buckwheat and millets 16 kg, other beans 4 L, fish 3.5 kg, edible oil 1 L, cotton
cloth 5 m, lamp oil 2.6 L, salt 7.3 kg, fuel 3 million BTU, a room. Question 2: each good's price per era and place in its own
money; question 3: an unskilled day wage there; question 4: the money in grams of pure silver. Your pass:
`passes/q2q3q4-china.md` (leads, not citations: read each passage or cell on its page before citing; where it does not read
as the pass says, write what the page says, or SILENT). Sessions 1 and 2 wrote the Japanese side: read `briefs/handoff.md`.

Write TWO new money questions, each reserved with `make reserve KIND=question KEY=<heading id>` and tagged as 0250 or 0260
are:

## Your items

- `B` **"What did a year's necessities and a day's labor cost in China, era by era?"** (new) - one block per era: the official price table after the ruling of 1497 (0272 holds it: rice 25 guan a shi,
  a tael 80 guan - name it, add only what its source adds); Beijing
  1573-1627 (late Ming: the official Beijing prices of 1615 in Gao 2022, rice by reign in Peng via Liu 2022, wage 0.036-0.043
  tael); Songjiang 1670-1690 (閱世編: rice 2 taels a shi in 1680 and
  the late-Ming and early-Qing prices it records, salt, cloth, cash rates); Beijing 1736-1760 (the official 1736 list, Gao 2022: wheat flour, sesame oil, salt, firewood, coal, coarse cloth; no
  ordinary rice; Allen et al.'s c. 1750 Table 5; wage 75 cash; the 1769 regulated wages already in 0275 or 0260 - name
  them); Suzhou and the Lower Yangzi 1750-1799 (Qian Yong's 履園叢話 rice in cash a sheng; Liu's 0.064-0.071 tael wage; Allen's
  0.09 for Suzhou); Beijing 1820-1830 (Allen's reconstruction; the rural fuel-store wage 95-99 cash, and Allen's paper halving
  it against his own GPIH sheet - say so); Canton 1830s (Chinese Repository vol. 3 no. 10, 1835: rice, salt, salted fish, flour,
  firewood, charcoal, coal, a two-room house at $1.50 a month; wage 1 mace); Beijing 1900-1919 (Gamble 1921, registered as
  `gamble-burgess-1921-peking-survey`; Meng and Gamble via the GPIH Beijing_prices file: flour, millet, corn flour, rice, the
  poor's rent; wage 19-27 cents). Song: rice alone, as Peng's decade averages (via Liu), its own block, so the record carries a Song price for a Song row
  (name in the handoff the decade or span the row should take); no wage or cash-silver rate: say so. **Official
  prices are ATTESTED ONLY FOR official prices; Allen et al.'s Beijing database is ATTESTED ONLY FOR a modern reconstruction**
  (its rice rescaled from the Yangzi, oils indexed to flour, cloth held constant - quote the paper or its appendix saying so).
- `D` **"What was a tael, a string of cash and a Chinese dollar worth in silver?"** (new) - the tael's weight (Allen et al.'s
  37 g; kuping 36.9 g in the 1500s and 37.3 g after the mid-1600s, Liu 2022; Song 37.68 g); fineness: SILENT unless a source
  read gives it; the dollar at 0.72 tael; strings (tiao, chuan) of 900-1,000 cash or fewer (Ma 2012), Beijing's jingqian counted
  double (Liu), rural Beijing's tiao of 500 cash before 1860 and 100 after (Gamble via Allen); cash a tael by the point rates
  the pass found - Ming 700 (1500-1525), 800 (Longqing), 550 official 1628 (明史 卷81); Songjiang 1,080-1,150 (1678-79) and 975
  (1690, 閱世編); 1737 800, the 1760s-70s 720-900, 1796 1,300-1,400 (履園叢話); 1820-30 1,159-1,329 (Allen Table A1); the 1728
  Changlu memorial's 1,400-2,000 and the pass's unconfirmed reading that it counts two cash as one (a guess: label it). A
  market cash-a-tael series by decade: SILENT in any readable copy; Lin Man-houng's 銀線 Table 2.6, Peng's 中國貨幣史 tables,
  Yan Zhongping's Table 31 listed as not read (put them on the download list with `make download-add` if the GM may own them).

**New registry keys** (at most ten this session): Gao 2022, Liu 2022, Ma 2012, 閱世編, 履園叢話, 清史稿 卷123, 明史 卷81, the
Chinese Repository 1835, the GPIH Beijing_prices and China_1730-1933 files - ten. Allen et al. 2011 and its working paper are
registered (`allen-2009-china-wages` and kin: find them with `make archive-find`); Gamble 1921 is registered.

## The procedure (session 3: write)

1. `make archive-inbox`. Reserve both questions, then `make research-claim Q="<B> <D>" FEATURE=412`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, a row dump for a spreadsheet; page images with `IMAGES=` for a scan). A new source
   takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `412: `.
4. Append to `specs/412-money-basket-every-era/implementation-check.md` one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/412-money-basket-every-era/briefs/handoff.md` a `## Session 3` section:
   - `- SECTION=<NNNN>/<id>` for each question;
   - per era and good, its verdict and the fragment file, the wage, and the money in grams of silver (the reply on #13 is
     built from this);
   - each search named; the new registry keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
