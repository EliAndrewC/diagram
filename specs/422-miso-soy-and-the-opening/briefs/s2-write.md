<!-- page-load: kind=assertions -->
# Brief - feature 422, what the opening changed, and modern miso and soy sauce. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all (its "Comparative money sources" section binds item 2), along with
`research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#18 (verbatim in `specs/422-miso-soy-and-the-opening/request.md`):
Q4, per era and good, whether foreign trade after the opening visibly changed the price - Edo 1860-67: rice, salt, lamp oil,
firewood, soybeans, barley and wheat, cooking oil; Beijing 1900-19: rice and millet - with the evidence, or not, or SILENT; and why
Tokyo 1882's soybeans stand at 0.65 times rice, below every Tokugawa era's 0.89-1.43. A good is "changed" only where a source ties
its price to trade, never from timing alone; a price that moved for another stated cause (the recoinage, the money supply, a
harvest) is said so. Q3, the cheapest plain household pack at a national US retailer of miso (by the kg) and naturally brewed soy
sauce (by the liter), in the snapshot rule's sense, dated and linked.

**Your passes:** `specs/422-miso-soy-and-the-opening/passes/q4-opening.md` and `passes/q3-modern.md` - leads, not citations: read
each passage on its page before citing it (Shinbo 1975 is a scan: read its page images); where a page does not read as the pass
says, write what it says, or SILENT. Every conversion and ratio is this project's arithmetic, labeled.

**Already in the record - name by file, do not repeat:** 0290 (price stability; the 1859 opening), 0293 (why prices changed era
to era), 0295 (the three metals; the recoinages of 1859-60), 0286, 0301 and 0302 (feature 420), 0288, 0299 (modern US basket goods,
comparative).

## Your items

1. **A new question** in "Money and prices", `subject=money`, its title asking which goods' prices the opening of the ports
   changed. Sections:
   - **Edo 1860-67, good by good**: rice (NOT ATTESTED as a trade effect: the treaties kept its export banned, Bernhofen and Brown;
     its 1859 fall and late rise, Shinbo's Table 4; Shinbo ties the general rise to the money supply), lamp oil and 雑穀 (ATTESTED
     ONLY FOR 1859-60, from the Nipponica entry on the 五品江戸廻送令; exports of the four non-silk goods fell from 1861), soybeans
     (SILENT on a trade tie; no source says 雑穀 covers 大豆), cooking oil (its own verdict, by name: the basket's edible oil is
     the same rapeseed oil as its lamp oil, 0249, so it takes lamp oil's evidence where a source prices that oil - 水油, 種油,
     白油 - and SILENT where none reaches it), salt, firewood and wheat (NOT ATTESTED), barley (SILENT; Shinbo left it
     out); that Shinbo's prices are Kansai's, and that his period ratios cannot separate trade from money (raw silk below the
     general index), said; wax (an 1869 trade-raised export, Bernhofen and Brown) only as context.
   - **Beijing 1900-19**: rice and millet SILENT on foreign trade (Meng and Gamble's series via GPIH; no source names a trade
     cause; the 1920 railway cut is domestic and outside the years).
   - **Tokyo 1882's soybeans**: the low ratio in every observed year 1879-95 (1882 itself the highest, 0.86) and Bassino and Ma's
     0.65 an 1882-86 mean; that it starts at Kumon's 1879 switch to LTES Tokyo retail (a series or grade difference possible, a
     reading); the Matsukata trough 1884-86; Manchurian imports' start SILENT. Ratios from the GPIH cells are this project's
     arithmetic.
2. **0299 (comparative)**: a bullet for miso (Shirakiku red 2.2 lb and white 2 x 2.2 lb on Amazon; Walmart's Hikari 10.5 oz, its
   cheapest it sells itself) and one for soy sauce (Walmart's Great Value Naturally Brewed 15 fl oz; Kikkoman 40 oz and 1 gallon,
   the gallon's name not saying naturally brewed; Kroger's basic soy sauce hydrolyzed per a review, its price unread); the Roland
   listing's pack contradiction left out or said; USDA and BLS SILENT. Each dated (the day you read it), linked and archived; the
   page's opening already says it never sets a Rokugani price.

**New registry keys** (at most ten): Shinbo 1975 (if not registered; the pass names `shinbo-1975-bakumatsu-prices`), Bernhofen and
Brown 2004, the Kotobank Nipponica entry, the GPIH Beijing prices file and the Kumon file if not registered; the Walmart and Amazon
pages (comparative).

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="0299" FEATURE=422`, and claim the new question's number (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups (comparative for the retail pages).
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   A modern dollar price is not a Rokugani sum; mark a historical sum paid as `research/CLAUDE.md` says (`make money-candidates
   CHECK=1` must exit 0). Commit with messages opening `422: `.
4. Append to `specs/422-miso-soy-and-the-opening/implementation-check.md` (create it if absent) one line per touched question.
5. Append to `specs/422-miso-soy-and-the-opening/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S2`
   section, as S1's. This is task T02.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
