<!-- page-load: kind=assertions -->
# Brief - feature 420, the method: what baskets compute, which mean, rice as numeraire. Session S5: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#17 (verbatim in `specs/420-koku-index-basis/request.md`, with the
GM's dictated words and gm-assistant's Q4 addendum) what economic historians do when a historical sum is put into modern money with a basket and relative prices have moved by orders of magnitude, which papers put an Allen-style or basic-needs basket into modern money and how, whether one figure or a range is the norm, what these baskets are used to compute in academic papers (the GM's own question), and whether rice is a sound numeraire across debasements and harvest swings (Q5); and the housing allowance of a world poverty line (part of Q3).

**Your passes:** `specs/420-koku-index-basis/passes/q5-method.md` (and, for the poverty-line housing allowance, `passes/q2-q6-modern.md`: Allen's LIS Working Paper 706, 3 m² a person and about $25 a m² a month in the US, UK and France, 2011) - leads, not citations: read each passage on its page before citing it; where a page does not read as
the pass says, write what the page says, or SILENT. Every figure this project computes is labeled its arithmetic.

**Already in the record - name by file, do not repeat:** 0249 (the basket), 0286 and 0288 (the eras), 0290-0294 (price stability; 0294 the closeness rule), 0291 (modern prices), 0297 (English prices).

## Your items

1. **A new question** in "Money and prices", `subject=money` (NOT the comparative section: this is method, and it bears on how
   Rokugan's prices are set; its sources are tagged by what they are, scholarship or institutional, not `comparative`), its title
   asking how economic historians carry a basket of goods into another time's or place's money. Sections:
   - **What the baskets compute**: welfare ratios (a wage over a basket's cost; Allen et al. 2011, Bassino and Ma 2005 and their
     account of Allen 2001) and poverty lines priced in each place's own prices (Allen's 2016 draft of the 2017 paper; Moatsos
     through Our World in Data); a ratio or a headcount, not what a coin is worth today.
   - **Which index**: a Laspeyres and a Paasche resolved by their geometric mean, the Fisher, with the robustness check (Allen et
     al. 2011); the Laspeyres-Paasche spread read as the uncertainty itself, and its 5-10 times cases (Deaton and Heston);
     Nordhaus on what conventional indexes miss over two centuries (food and plain cloth less, housing and heating and lighting
     most).
   - **One figure or several**: MeasuringWorth's measures side by side; the Bank of Japan's 1 ryo by rice against by a
     carpenter's wage.
   - **Which papers put a basket into modern money**: Allen's draft does, to show the problem (US prices against rupees at PPP,
     about 2:1); say which others the search found, or SILENT with the search beyond them; Allen 2017's final text, Moatsos 2016
     and 2021 and Allen 2001 named as not read in the original.
   - **Rice as numeraire**: accepted as a convenience (the NDL's 便宜的), its weaknesses named from the sources (harvest swings,
     Allen's fifty-year averages via Broadberry and Gupta; rice's own relative fall across Kyoho, Kobayashi; grain wages'
     wrong rankings, Broadberry and Gupta); the Japanese series deflate by Shinbo's multi-good index (Bassino and Ma).
   - **The housing allowance of a basic-needs line**, as the modern pass gives it, if it does.
   Any rule drawn for gm-assistant is labeled this project's derivation, not a source's.

**New registry keys** (at most ten): Allen et al. 2011 (if not registered); Allen's 2016 NBER draft; Our World in Data on Moatsos; Deaton and Heston w14499; MeasuringWorth's essay (if not registered); Nordhaus c6064; the BOJ 1 ryo sheet (if not registered); the NDL research guide; Broadberry and Gupta 2006; BOJ Kobayashi 2017 (if not registered).

## The procedure (session S5: write)

1. `make archive-inbox`. Then claim the new question's number as the record's tooling says (`make reserve`).
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (a rate between coins is NOT
   marked; `make money-candidates CHECK=1` must exit 0). Commit with messages opening `420: `.
4. Append to `specs/420-koku-index-basis/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/420-koku-index-basis/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S5` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per figure asked, its verdict and fragment file; each search named; the
   new keys; leads not followed. This is task T05.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
