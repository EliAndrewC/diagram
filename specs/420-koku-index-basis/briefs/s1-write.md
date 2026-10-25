<!-- page-load: kind=assertions -->
# Brief - feature 420, what was bought and the historical rent. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#17 (verbatim in `specs/420-koku-index-basis/request.md`, with the
GM's dictated words and gm-assistant's Q4 addendum) what form, quality and market level each good of the standard basket had (Q1), and any Kyoto or Osaka rent for c. 1745 or the nearest, with its room size (Q3, the historical half). The basket is Bassino and Ma's Japan basket A plus salt, fuel and a back-tenement room, Kyoto 1745-54 (0249).

**Your passes:** `specs/420-koku-index-basis/passes/q1-what-was-bought.md` and `passes/q3-rent.md` (and, for the Edo rents, the rent part of `passes/q4-japan.md`) - leads, not citations: read each passage on its page before citing it; where a page does not read as
the pass says, write what the page says, or SILENT. Every figure this project computes is labeled its arithmetic.

**Already in the record - name by file, do not repeat:** 0249 (the Kyoto laborer's year of goods: the basket, its prices, its reconstructions), 0261 (cloth), 0265 (rents, the Bunsei carpenter's 10 monme a month), 0273 (salt), 0279 (charcoal), 0286 (the eras), 0250 (wages).

## Your items

1. **0249: what was bought, good by good.** A section giving, per basket good, its form and quality as Bassino and Ma's Table 3
   note states it, and the market level of the price the record cites: rice white; soybeans whole dry beans "of above average
   quality", standing for miso, shoyu, tofu and natto (their Table 1 note); barley and wheat, buckwheat and millets unprocessed
   grain, priced by Meiji farm-gate ratios to paddy (1874-1901) times the 1882-86 retail rice price; fish salmon and cod by a
   wholesale fish-to-rice ratio of 1882-86 times retail rice; oil rapeseed for both lamp and table (sesame "more a condiment");
   cloth plain cotton by the tan, an Osaka price of the 1840s (Miyamoto 1963, not read). Market level: the Mitsui Kyoto books are
   headed "retail" by their editors, but are a merchant house's own purchases (ATTESTED ONLY FOR that label); the soybean
   benchmark is an Osaka 相場 (market quotation) table from 1757 (the NDL reference answer on Mitsui Bunko 1989); the grain and
   fish figures are constructs at no market level. The Mitsui Kyoto miso and soy sauce prices of 1745-54 in the same GPIH sheet,
   unused by the paper, as observed alternatives to the soybean proxy (the means are the pass's arithmetic: recompute them from
   the sheet and label them this project's). Markups: SILENT for Kyoto and Osaka c. 1745, with the search; ATTESTED ONLY FOR
   Mitsui's Edo cotton store, 1790s-1840s (Shimomukai, its 札掛 rates) and a village salt seller in Owari, 1842 (0273's Handa
   passage; the margin is this project's arithmetic). What a commoner's fish was: SILENT for Kyoto and Osaka; the Edo 1860 diary
   only as ATTESTED ONLY FOR one low-stipend samurai, from a modern paraphrase. One pointer sentence each in 0261, 0273 and 0279
   where its good's form or level is now stated in 0249.
2. **0265: the Osaka and Edo rents.** Mitsui's Osaka rental houses, 0.7 monme a mat a month for a back house and 0.9 for a
   front, from 1814 and again in 1846 (Tani 1989, read on its page images or text); the 『所以者何』 average beside it (Tani's note
   11 dates it); Edo's back-lot rents of the Kansei years and 1840 (Washizaki 2012, Table 5, read from the page image); the 1848
   carpenter's rent in 『柳菴雑筆』 (BOJ Kobayashi 2017) named as the same figure as the Bunsei one 0265 holds. A 九尺二間 room at
   the Osaka rate is this project's arithmetic, with its assumption stated. Kyoto: SILENT with the search. c. 1745: SILENT; the
   leads (Fujimoto 1978, Osaka 1764-72; Ito Munehiro on Kyoto; Kagawa) named as not read; McClain and Wakita's *Osaka* to the
   download list (`make download-add`) if it is not already there. The Matsue rents only if you judge them worth a line, as a
   castle town, ATTESTED ONLY FOR it.

**New registry keys** (at most ten): Tani 1989; Washizaki 2012 (if not registered); BOJ Kobayashi 2017 (if not registered); the NDL reference answer on Mitsui Bunko 1989; Shimomukai (if not registered); the GPIH Japan_1710-1871 sheet (if not registered); the bakumatsu.org page if cited.

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="0249" FEATURE=420`, and `Q="0265"`, `Q="0261"`, `Q="0273"`, `Q="0279"`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (a rate between coins is NOT
   marked; `make money-candidates CHECK=1` must exit 0). Commit with messages opening `420: `.
4. Append to `specs/420-koku-index-basis/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/420-koku-index-basis/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S1` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per figure asked, its verdict and fragment file; each search named; the
   new keys; leads not followed. This is task T01 and T02.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
