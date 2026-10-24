# Brief - feature 414, how stable prices were. Session 1: write (new questions A and E)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM asked how stable premodern prices were (issue EliAndrewC/diagram#15, verbatim in
`specs/414-price-stability/request.md`, read it): how much prices moved at every time scale - within a day, day to day, week to
week, month to month, year to year, decade to decade, century to century - trend against swing, the shocks dated, which goods
were steady and which swung, beside a modern fiat-money yardstick. Your passes: `passes/japan.md`, `passes/qing.md`,
`passes/modern-yardstick.md` (leads, not citations: read each passage on its page before citing it; where it does not read as
the pass says, write what the page says, or SILENT). This project's arithmetic is in `measure/`: `mitsui_stability.py` (Mitsui
Bunko by city and good: the SD of log change from half a year to 50 years, drift, seasonality, city spreads),
`osaka_daily.py` (the daily Osaka rice series: a day, a week, a month, three and six months, a year), `qing_stability.py`
(Allen et al.'s Suzhou, Canton and Beijing basket costs and Kishimoto's Suzhou rice, by lag) - each with its `.out.md`. Cite a
computed figure as this project's arithmetic, naming the series, the city, the measure and the pairs or years it rests on, and
link the script. Copies of the data files are in `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/`
(`gpihjp/`, `gpih/`) and the RIEB file at `/diagram/.specify/source-archive/d2/d2aae944e8db/20261019T161020Z/served.xlsx`.

## Your items

- `A` **"How steady were prices in Edo Japan and Qing China, from one day to the next century?"** (new, tagged as the money
  section's price questions are). Japan first, China beside it. Per scale the request names, a verdict (one of the four of
  `research/money-requests.md`; below a month: this project's arithmetic from the daily Osaka series, beside the sources' silence
  on size). The drift beside each swing (Mitsui's drift: each city's span with its early observations named - Kyoto 1713, then
  1741-1762 and 1791-1858; Osaka 1713, then 1818-1858; Edo four years 1710-1716, then 1818-1858). The shocks dated (1732,
  1783-87, 1833-38, the 1818-29 recoinage, 1859; China 1642, 1651, 1669-70, 1680-81, 1707, 1755, 1785, the Taiping years). Copper
  against silver drift for China kept apart (Qian Yong and 全漢昇 in cash; Lu and Peng in silver). Per good a verdict, SILENT
  with the search at worst: rice, soybeans, other grains (barley and wheat, buckwheat and millets), other beans, fish, edible oil,
  cloth (cotton, and other cloth where priced), lamp oil, salt, fuel, rents, crafted goods, services, the unskilled day wage (sticky
  or not - Saito 1993 for Japan; Allen and Liu for China). Kyoto's salt from 1791 is a unit change in the series: say so, use
  no figure across it. Say how the answer stands against its canon: gm-assistant's conversion table treats each era as one price
  level for its years; the measured within-era spread (Mitsui, 5 years) is the honest size of that simplification.
- `E` **"How steady are prices today, under paper money?"** (new; COMPARATIVE: tag `subject=comparative,money`, its sources the
  kind `comparative` - `research/CLAUDE.md`, "Comparative money sources"). The US CPI since 1971 and Japan's (drift; monthly,
  12-month and annual SD), a staple's modern monthly and 12-month SD (BLS average prices), Rolnick and Weber's commodity against
  fiat inflation. Below a month: read one daily staple series (a daily futures settlement for rough rice or wheat, e.g. from an
  exchange's public history or a data mirror) or record the search, SILENT its result. Do NOT write England's premodern series
  (the Bank of England millennium dataset, Clark): it waits on the GM's approval.

**New registry keys** (at most ten this session): Shinbo 1975, Miyamoto 1975, Takatsuki 2007, Shiue 2002, Shiue and Keller (NBER),
Keller-Shiue-Wang appendix, Lu and Peng 2004, 全漢昇 1957, the RIEB database, the BLS/DBnomics series - expect ten; anything more
goes to the continuation brief `make reserve` writes.

## The procedure (session 1: write)

1. `make archive-inbox`. Reserve both questions, then `make research-claim Q="<A> <E>" FEATURE=414`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`, a row dump for a spreadsheet, page images with `IMAGES=` for a scan). A new source takes `make
   reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `414: `.
4. Append to `specs/414-price-stability/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/414-price-stability/briefs/handoff.md` (create it if absent) a `## Session 1` section: `- SECTION=<NNNN>/<id>`
   per question; per figure the issue asks, its verdict and the fragment file; each search named; the new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
