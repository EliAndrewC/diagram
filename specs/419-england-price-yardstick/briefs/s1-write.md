<!-- page-load: kind=assertions -->
# Brief - feature 419, England's premodern prices as a comparative yardstick. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all (its "Comparative money sources" section binds every line you write), along
with `research/money-requests.md`.

**What is asked.** The GM approved, on EliAndrewC/diagram#15 (verbatim in `specs/419-england-price-yardstick/request.md`),
adding the Bank of England's millennium dataset and Clark's English prices and wages to the record as COMPARATIVE sources, in
the "Comparative money: other societies" section (`comparative-money`): a yardstick showing the same split as Edo and the
Qing - little drift, a big swing from year to year - and never the basis of a Rokugani price.

**The figures are already computed.** `specs/419-england-price-yardstick/measure/england.py` and its output
`measure/england.out.md` hold every number you may write; compute nothing yourself, and write no figure the output lacks. Every
one is this project's arithmetic, labeled so, naming the series, England, the measure (the standard deviation of annual log
changes; the drift as the mean log change a year), the years and the year pairs. The data files (fetched 2026-10-25):
- Bank of England, "A millennium of macroeconomic data for the UK", sheet "A47. Wages and prices", column D "Consumer Price
  Index (CPI) - preferred measure": https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/a-millennium-of-macroeconomic-data-for-the-uk.xlsx
  (landing page https://www.bankofengland.co.uk/statistics/research-datasets); a local copy at
  `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/dl419/boe/m.xlsx`.
- Clark, English prices and wages 1209-1914, as reformatted by Peter Lindert for GPIH:
  http://gpih.ucdavis.edu/files/England_1209-1914_(Clark).xls; a local copy at
  `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/dl419/clark/c.xls`.
A spreadsheet's citation quotes its cells or notes verbatim (row dumps), as the record's other spreadsheet citations do.

**Already in the record - name by file, do not repeat:** 0290 (how steady prices were in Edo Japan and Qing China, day to
century), 0291 (how steady prices are today under paper money; it already cites Rolnick and Weber), 0292-0294.

## Your items

1. **A new question in `comparative-money`**, tagged `subject=comparative,money`, its title asking how steady English prices
   were before paper money (1209-1914). Its sections:
   - **The drift**: the price level by period (1210-1499, 1500-1650, 1651-1750, 1751-1913, 1821-1913) and by century, from the
     Bank of England's column; its source note quoted; that its years before 1661 are Clark's index rescaled (the constant
     ratio the output shows), labeled this project's check; the one long inflation, the 1500s.
   - **The swing**: the price level's SD by period and the years moving more than 10%; the ten-year changes of 1210-1499;
     goods and wages from Clark (wheat, barley, oats, peas, salt, charcoal, firewood, lamp oil, wool cloth, a building
     laborer's and a farm laborer's wage), each with its year pairs; grain swung most, cloth and wages least.
   - **Beside Edo, the Qing and today**: a line each pointing to 0290's and 0291's figures in the same measure (quote them from
     those pages, do not recompute); the modern 1984-2016 UK row from the output.
   - **Limits, carried from the files and no further**: Clark's file's caveat, verbatim ("Caveat: These series are Professor
     Clark's data as of this date, and are subject to revision."); his blank years are dropped from the year pairs (the counts
     show them); the flat year pairs the output counts are this project's observation, NEVER called interpolation (the file
     does not say so; Lindert's interpolation note covers the silver price of the pound, which no figure uses, so leave it
     out).
   - An opening that says, in the record's own words, that these are a yardstick for players and never set a koku's value or a
     Rokugani price.
2. **0291**: in "Beside the premodern figures", one pointer sentence to the new question; in its source comment, drop "England's
   premodern series ... wait on the GM's approval and are not written here" in favor of the pointer.

**New registry keys** (two): the Bank of England dataset and the GPIH Clark file, each with the kind `comparative`
(`research/source-tags.json`) and the period/region tags England takes, and their two write-ups judged on England's own terms.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0291" FEATURE=419` and claim the new question's number as the record's
   tooling says (`make reserve`).
2. For each file you cite: `make archive-find`, `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups,
   then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`).
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   A comparative price in pence is not a Rokugani sum: follow `research/CLAUDE.md` on the money tooltip (`make money-candidates
   CHECK=1` must exit 0). Commit with messages opening `419: `.
4. Append to `specs/419-england-price-yardstick/implementation-check.md` (create it), one line per touched question:
   `- NNNN: no code implements it - a comparative money question, consumed by no generator; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/419-england-price-yardstick/briefs/handoff.md` (create it) a `## Session 1` section: `- SECTION=<NNNN>/<id>`
   for each section you changed; each figure's fragment file; the new keys; anything you could not support.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
