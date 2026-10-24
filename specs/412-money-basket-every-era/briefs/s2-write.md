# Brief - feature 412, the basket in every era. Session 2: write (new questions A and C, Japan)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant prices one standard basket in each era the record cites (issue EliAndrewC/diagram#13,
verbatim in `specs/412-money-basket-every-era/request.md`): per adult a year, rice 114 kg, soybeans 52 kg, barley and wheat
10 kg, buckwheat and millets 16 kg, other beans 4 L, fish 3.5 kg, edible oil 1 L, cotton cloth 5 m (a ~36 cm bolt), lamp oil
2.6 L, salt 7.3 kg, fuel 3 million BTU, 3.31 m2 of a back-tenement room. Question 2: what each good cost in each era and place,
as many as the sources allow, in its own money; question 4: what each era's money was worth in grams of pure silver. Your
passes: `passes/q2q3-japan-series.md` and `passes/q4-japan-coin-silver.md` (leads, not citations: read each passage or cell on
its page before citing; where it does not read as the pass says, write what the page says, or SILENT). Session 1 has written
question 1 into 0273/0279/0265 and the wages into 0250: read `briefs/handoff.md` and name those by file, do not repeat them.

Write TWO new money questions, each reserved with `make reserve KIND=question KEY=<heading id>` and tagged as 0249 or 0277
are (look at `research/tags.json` and `contents.json`):

- `A` **"What did a year's necessities cost in Japan, era by era?"** (new) - one block per era: Osaka 1620-1650; Osaka 1690-1739 (Kumon's rice by decade, Iwahashi; the Genroku-Hoei-Kyoho
  recoinages fall inside it: say so); Kyoto
  1745-1754 (0249 holds Bassino and Ma's basket: name it, add only what the Mitsui series adds); Osaka 1780-1789 (Kumon); Kyoto 1790-1799;
  Kyoto 1800-1817 (Mitsui Kyoto); Edo 1818-1829; the three cities 1830-1844, 1850-1859 and 1860-1867. Per era: each basket good the sources price, in its own unit
  and money, with its source, the decade or era mean as this project's arithmetic; the goods not found named; the day wage
  beside it (0250, named). Sources: Mitsui Bunko via GPIH (`https://gpih.ucdavis.edu/files/Japan_1710-1871.xls`); Kumon
  (`https://gpih.ucdavis.edu/files/Japanese%20Wages.xlsx`, Osaka rice every decade 1610-1890, soybeans, barley, oils and cloth
  per tan from the 1780s); Kimura (`https://gpih.ucdavis.edu/files/Osaka_1600-1650.xls`); Iwahashi
  (`https://gpih.ucdavis.edu/files/Japan_rice_P_1620-1867.xls`, rice in 14 places). Copies and text dumps:
  `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/gpihjp/` and `.../scratchpad/dumps/`
  (re-download if absent). Mitsui's 麦 is read as wheat by Bassino (his note on the "Sources and conversion" sheet: quote it).
  Say where a figure is doubtful: Kyoto salt from 1791 runs at about a third of Edo's and Osaka's (a unit or grade change in
  this project's reading); Bassino and Ma's cloth (an Osaka price of the 1840s, about 19.9 monme a tan) against Kumon's 6-8.8.
  Fish, other beans, buckwheat and millets before 1880, and rent beyond 0265: SILENT, with the search.
- `C` **"How much silver was a monme, a ryo and a bu, coinage by coinage?"** (new) - the chogin's prescribed fineness and
  grams of pure silver a monme (3.75 g of metal) by recoinage, Keicho 1601 to Ansei 1859, from the jawiki chogin articles that
  cite 『旧貨幣表』 and the Meiji mint's assays (quote each); the koban's gold weight by recoinage; a ryo and a bu in grams of
  silver by the market rate times the fineness (this project's arithmetic): from 1787 0277's Osaka series (name it, do not
  repeat the table), before it the chronology the pass found (coin-walk.site transcribing 『日本史資料総覧』, 1986) labeled as
  a secondary source; what the nanryo nishugin and the Tenpo ichibu-gin themselves held; the 1773 order valuing a ryo at 24
  monme of pure silver if the page reads so. **Per era of question A, the coinage in circulation and its grams** (gm-assistant
  will convert each era at the pure silver of the coinage circulating then, #13 issuecomment-6386690660): a short table naming,
  for Osaka 1620-1650, Osaka 1690-1739, Kyoto 1745-1754, Osaka 1780-1789, Kyoto 1790-1799, Kyoto 1800-1817, Edo 1818-1829, 1830-1844, 1850-1859 and 1860-1867, the chogin then
  current (where two circulated side by side, as after a recoinage, say so and give both) and its grams of pure silver a monme,
  with the recoinage dates cited. **Bassino and Ma's 3.11 g a monme**: quote their sentence, say its basis is not
  given (SILENT), and quote Bassino's GPIH note (3.75 g assumed, the content "uncertain"). **Mon and kanmon in silver for every
  era of A**: where 0277 holds the market rate (Osaka 1787-1859, Edo 1781-1842, Osaka 1766, Kyoto 1867), name it and convert
  its decade at the era's chogin (this project's arithmetic); outside it (Osaka 1620-1650, 1690-1739, Kyoto 1745-1765, Osaka
  1780-1786, the 1860s) give the legal rate (1609: 50 monme and 4 kanmon a ryo; 1700: 60 and 4 - cite the law's page) and the
  market rate where a source gives one (search: 銭相場 寛永, 銭相場 元禄 宝永, 金銭相場 享保, 銭相場 文久 慶応), or SILENT
  with the search in the absence note. Osaka 1690-1739's block names the recoinages of 1695-1714 inside it. Kyoto's rows (1745-1754, 1790-1799, 1800-1817) convert
  mon at Osaka's rate, the nearest market 0277 holds: say so on each row.

**New registry keys** (at most ten this session): Kumon, Kimura, Iwahashi (the GPIH files), the jawiki chogin articles you
cite (each a key), the koban article, coin-walk - expect eight to ten. If they pass ten, `make reserve`'s eleventh sends the
rest to a continuation brief: finish what you can and name the rest in the handoff.

## The procedure (session 2: write)

1. `make archive-inbox`. Reserve both questions, then `make research-claim Q="<A> <C>" FEATURE=412`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, a row dump for a spreadsheet). A new source takes `make reserve KIND=registry
   KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `412: `.
4. Append to `specs/412-money-basket-every-era/implementation-check.md` one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/412-money-basket-every-era/briefs/handoff.md` a `## Session 2` section:
   - `- SECTION=<NNNN>/<id>` for each question;
   - per era and good, its verdict and the fragment file, and per coinage its grams of silver (the reply on #13 is built from
     this);
   - each search named; the new registry keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
