<!-- page-load: kind=assertions -->
# Brief - feature 420, the Japanese eras beyond rice. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#17 (verbatim in `specs/420-koku-index-basis/request.md`, with the
GM's dictated words and gm-assistant's Q4 addendum) for each era gm-assistant holds, which of soybeans, fish, cloth, salt, fuel and housing can be priced from an observed price rather than a reconstruction (Q4), Japan first; per era, which goods are observed and which reconstructed or borrowed, and for each borrowed one, the era or source it was borrowed from (gm-assistant's addendum: kyoto-1745's beans, grains and fish may be early-Meiji relatives, counted twice beside tokyo-1882). The Japanese eras are in `research/assets/money-conversions.json` ("eras"; each era's "confidence" says what it uses).

**Your passes:** `specs/420-koku-index-basis/passes/q4-japan.md` and its draft table `passes/q4-japan-table.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as
the pass says, write what the page says, or SILENT. Every figure this project computes is labeled its arithmetic.

**Already in the record - name by file, do not repeat:** 0286 (the Japanese eras, the Mitsui means, 'Kyoto's salt from 1791 is doubtful'), 0249 (the Kyoto basket and its reconstructions; session S1 may have added a section on each good's form and level), 0261, 0265, 0273, 0279, 0287 (coins), 0290.

## Your items

1. **A new question beside 0286** (0286 is near the size cap), `subject=money`, in "Money and prices", its title asking which of
   a year's necessities were observed and which reconstructed, era by era, in Japan. A table per era (or one table, eras as
   rows) of soybeans, fish, cotton cloth, salt, fuel and housing: each cell observed (source and city), observed in another city
   (which), reconstructed, borrowed (the era or source it came from: kyoto-1745's beans, grains and fish from early-Meiji ratios
   per Bassino and Ma's Table 3 note; its soybeans set equal to rice; Kumon's soybeans Osaka's, Bassino and Ma's Table 3 note
   naming Osaka from 1757; tokyo-1882's from LTES Tokyo retail), held in the record but unused by the era, or absent. New
   observed prices in 0286's format (grams of pure silver a unit at the era's coin, its label, its source): the Edo rents of the
   Kansei years and 1840 and the Osaka 1814 rates only if session S1 has not already written them into 0265 (then point to
   0265); the 1887 GPIH figures only as nearest, not observed for tokyo-1882. Fish: SILENT for every Edo-period era with the
   search (every Kumon fish cell is imputed). Each cell also says, where it differs from 1745's (session S1's section in 0249
   on each good's form and market level), the good's form and the price's market level - Kumon's Osaka figures 相場
   (wholesale) quotations where the pass dates them to the Mitsui Bunko tables, the Mitsui books purchases, salt and charcoal by
   the bale in Kyoto from 1791, tokyo-1882 LTES retail - or SILENT with the search where no source says.
2. **0286: Kyoto's salt from 1791.** The Mitsui Kyoto books price salt by the bale from 1791, and hard charcoal by the bale too
   (Kusano 1996, p. 41, read on its page image); revise "Kyoto's salt from 1791 is doubtful" to the unit change, give the
   koku-equivalent means only as this project's arithmetic at Kusano's 3 to 2 sho a bale, labeled as his own assumption, with
   0273's Ako bale sizes beside it. Do not edit `money-conversions.json` (gm-assistant's file).

**New registry keys** (at most ten): Kusano 1996; the GPIH Japanese Wages (Kumon) file and Japan_1885-1926 file if not registered; any other the pass names that you cite.

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="0286" FEATURE=420` and claim the new question's number as the record's tooling says (`make reserve`).
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (a rate between coins is NOT
   marked; `make money-candidates CHECK=1` must exit 0). Commit with messages opening `420: `.
4. Append to `specs/420-koku-index-basis/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/420-koku-index-basis/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S2` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per figure asked, its verdict and fragment file; each search named; the
   new keys; leads not followed. This is task T03.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
