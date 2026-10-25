<!-- page-load: kind=assertions -->
# Brief - feature 420, the modern goods. Session S4: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all (its "Comparative money sources" section binds every line you write), along
with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#17 (verbatim in `specs/420-koku-index-basis/request.md`, with the
table of its current snapshot at the top) for: Q2, the modern US product that best matches each basket good, priced at retail
(the cheapest plain household pack from a national retailer, about 2-25 lb) and, where the historical price is wholesale, at a
wholesale or farm-gate level; Q3 (modern half), the candidates for a laborer's tenement share per m² a year with what each
measures; Q6, what a US adult consumes in a year of each basket good. These are COMPARATIVE sources: the GM asks for them here.

**Your pass:** `specs/420-koku-index-basis/passes/q2-q6-modern.md` - leads, not citations. Every price is a dated observation
(seen 2026-10-25 by the pass; re-read each page on the day you cite it and say the date you saw it); where a page reads
differently now, write what it says. Every conversion is this project's arithmetic, labeled so, its factors stated (and an
outside factor, such as a bushel's weight or a cord's BTU, cited to its source). A retail page that cannot be archived or read
is not cited.

**Already in the record - name by file, do not repeat:** 0291 (modern prices under paper money: BLS CPI, rice and flour
average prices from DBnomics), 0297 (English prices), 0249 (the Kyoto basket); the method question session S5 writes in the
same clone (Allen's 3 m² a person housing allowance belongs there - point to it, do not repeat it).

## Your items

1. **A new question in `comparative-money`** (or two, if one would pass the size cap: goods and quantities in one, housing in
   the other), `subject=comparative,money`, its title asking what the standard basket's goods cost in the US today and how much
   of each an American uses. Its opening says it never sets a koku's value or a Rokugani price, and that gm-assistant's snapshot
   is not edited here. Sections:
   - **Per good, the like-for-like product**: rice (long and medium, a 20 lb bag; the BLS average price beside it); conventional
     dried soybeans (only marketplace sellers: say so); dried beans; wheat flour (all-purpose and whole wheat) and pearled
     barley against the snapshot's wheat berries; millet; small fish (canned sardines, dried anchovy) against cod fillets;
     canola oil; cotton muslin per m²; plain and pickling salt (the pickling price was a sale: say so); charcoal; firewood per
     cord and per million BTU (the EIA cord figure; the Vermont range ATTESTED ONLY FOR a news report). Each with its farm-gate
     price where NASS gives one (prices received by farmers, not wholesale: say so; rough rice to milled at ERS's milling rate).
   - **Housing per m² a year**: the median asking rent over a mean rented unit (RECS) or the median unit (AHS), each division
     labeled with the two sources it mixes; HUD's non-metropolitan and SRO rents (no room size: no per-m² figure); construction
     cost per m² without land (NAHB), a capital cost that needs a building life to become a rate (say so; do not choose one);
     the snapshot's $269 not rebuilt (say what unit size it would imply, as arithmetic).
   - **What an American uses in a year**: wheat flour, other grains, rice (2010, the series' last year: say why), dry beans,
     fish (ERS edible weight 2018; NOAA 2023, its basis unstated), cooking oil (2010, product weight), salt (from the FDA
     sodium figure: total dietary sodium, not salt bought), home heating and cooking fuel (RECS 2020; wood kept apart), floor
     area a person (AHS 2023; RECS cross-check). Soybeans as food and textiles: SILENT with the search.

**New registry keys** (at most ten; group by publisher): BLS average prices; USDA NASS Agricultural Prices; the Walmart product
pages (one key per page you can archive, or one for the retailer if the registry's rules allow); EIA (Btu, RECS); Census (HVS,
AHS); HUD FMR notice; NAHB; USDA ERS food availability; FDA sodium. Over ten: the eleventh goes to a continuation brief, as
`make reserve` says.

## The procedure (session S4: write)

1. `make archive-inbox`. Claim the new question's number as the record's tooling says (`make reserve`).
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` with the kind
   `comparative`, and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   A modern dollar price is not a Rokugani sum: follow `research/CLAUDE.md` on the money tooltip (`make money-candidates
   CHECK=1` must exit 0). Commit with messages opening `420: `.
4. Append to `specs/420-koku-index-basis/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - a comparative money question, consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/420-koku-index-basis/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S4` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; each figure's fragment file and verdict; the new keys; anything you could
   not support; leads not followed. This is task T06.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
