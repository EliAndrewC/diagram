<!-- page-load: kind=assertions -->
# Brief - feature 420, the Chinese eras beyond rice. Session S3: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#17 (verbatim in `specs/420-koku-index-basis/request.md`, with the
GM's dictated words and gm-assistant's Q4 addendum) for each era gm-assistant holds, which of soybeans (or beans), fish, cloth, salt, fuel and housing can be priced from an observed price rather than a reconstruction (Q4, China beside Japan); per era, which goods are observed and which reconstructed or borrowed, and for each borrowed one, the era or source it came from. The Chinese eras are in `research/assets/money-conversions.json` ("eras"; each era's "confidence" says what it uses).

**Your passes:** `specs/420-koku-index-basis/passes/q4-china.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as
the pass says, write what the page says, or SILENT. Every figure this project computes is labeled its arithmetic.

**Already in the record - name by file, do not repeat:** 0288 (the Chinese eras), 0289 (tael, cash, dollar), 0290, 0261, 0265, 0273, 0279; the Japanese counterpart session S2 may have written (point to it, same shape).

## Your items

1. **A new question beside 0288**, `subject=money`, in "Money and prices", in the same shape as the Japanese one if it exists:
   per Chinese era, soybeans or beans, fish, cotton cloth, salt, fuel and housing, each cell observed (official or market,
   kept apart; source and place), reconstructed (Allen et al. 2011), borrowed (from where), held in the record but unused by the
   era (the pass lists those: 1615 cloth, 1736 cloth and salt, songjiang-1680 cloth and firewood, canton-1835 salted fish,
   beijing-1900 fuel and rent), or absent. New prices: Timkovski's Peking list of 1821 for beijing-1820 (salt, fish, coal, wood,
   charcoal, cottons by the piece, the 1,000-cash rent), read on the page images, the conversions at his own 1,100 cash a tael
   labeled this project's arithmetic and the arsheen's length labeled as an outside figure with its source; Hong Liangji's
   Changzhou cloth recollection for suzhou-1750 (ATTESTED ONLY FOR a neighboring prefecture's rounded memory; the essay's date
   from a source, not memory); the Beijing fish of the 1590s-1602 only as secondary reports, ATTESTED ONLY FOR them, or left out.
   beijing-1500: SILENT for all six, with the search.

**New registry keys** (at most ten): Timkovski vol. 2 (archive.org); the 洪北江詩文集 wikisource page; the secondary Brook excerpt only if cited.

## The procedure (session S3: write)

1. `make archive-inbox`. Then claim the new question's number as the record's tooling says (`make reserve`), and `make research-claim Q="0288" FEATURE=420` if you add a pointer there.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (a rate between coins is NOT
   marked; `make money-candidates CHECK=1` must exit 0). Commit with messages opening `420: `.
4. Append to `specs/420-koku-index-basis/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/420-koku-index-basis/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S3` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per figure asked, its verdict and fragment file; each search named; the
   new keys; leads not followed. This is task T04.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
