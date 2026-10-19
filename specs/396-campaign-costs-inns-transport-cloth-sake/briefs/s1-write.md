# Brief - feature 396, campaign costs I: inns, transport, cloth and sake. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#3 (gm-assistant's money skill): what a night at an inn, a hired horse or porter,
cloth and clothing, and sake cost, Japan first (China where the request names it), each figure beside the UNSKILLED
laborer's day wage of the same place and period. Where no source gives one, say that wage is SILENT and name the nearest
(a craftsman's only if no unskilled wage exists, always named as a craftsman's and never shown as the unskilled wage),
with its class, its place, its unit and its gap in years. The request is verbatim
in `specs/396-campaign-costs-inns-transport-cloth-sake/request.md`. This is research only: edit no code, modal, sheet or
canon.

## The passes (leads, not citations)

`specs/396-campaign-costs-inns-transport-cloth-sake/passes/`: `q-inns.md`, `q-transport.md`, `q-cloth.md`, `q-sake.md`.
Each holds verbatim passages, URLs and archive copies. Read each passage on its page before citing it.
- A popular website (coin-walk, eonet, a blog) is cited only where nothing better gives the figure, and its write-up says
  it is popular and at what remove from the period.
- Wages already in the record: 0250 (Kyoto 1802-04 unskilled and craftsman; Bassino and Ma; Saito 2003), 0256 (Edo
  carpenter 1804-60; Edo unskilled only "broadly level with Kyoto"), 0257 (Osaka 1620s). Point at them rather than
  repeating them. Bassino and Ma's cotton is in 0249.
- **Units.** Most prices are in copper mon and the wages in silver monme. A mon price set beside a silver wage states both
  units and does NOT convert: the copper-to-silver rate is not written in this feature.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure the project computes (a per-ri or per-day
equivalent) as the project's arithmetic.

- I1 **"What did a night at an inn cost?"** (`setting=countryside,city`)
  - A hatago night with two meals, about 120-200 mon on the Tokaido and Ise roads, 1790 to the 1850s; in a town, ATTESTED
    ONLY FOR Tsu (130 mon, 1790); in a big city, silent.
  - A kichin-yado night: the regulated 3-16 mon (1611-1686), about 50 mon by the 19th century, Edo 1843 24 mon plus 16-24
    for bedding.
  - A horse for the night: only the regulated firewood charge per horse; feed and stabling silent (an absence note).
  - The Qing inn: silent.
- I2 **"What did hiring a horse or a porter cost?"** (`setting=countryside`)
  - The official stage rates per ri for a pack horse, a light horse and a porter (1665, 1711, the 1820s surcharge); the
    negotiated rate "about twice" (hedged, as its source hedges it).
  - The return: paid one way, stage by stage, on the official relay; the return on a day hire silent.
  - A horse with its driver by the day, a cart by the day: silent.
  - The Qing: one 1863 private mule hire (Michie).
- I3 **"What did cloth and clothing cost?"** (`setting=countryside,city`)
  - A tan's length; cotton per tan (1781-91, Ako and Edo); plain silk (one 1692 figure, from Saikaku's fiction, so
    labeled); the silk-to-cotton ratio, a weak Japanese pairing of about 6:1 (1692 silk against 1716 cotton, marked weak)
    and Qing Beijing's official prices (1736).
  - Pongee: silent in Japan; ATTESTED ONLY FOR Shandong pongee as priced in Songjiang (the 閱世編), 0.03-0.1 tael a chi (1680s-90s).
  - A new plain kimono: silent in Japan; the Qing ready-made garments of Beijing 1736 are the nearest.
  - Silent: used kimono, sewing, silk bedding.
  - Bassino and Ma's cotton linen at 5.83 g silver a meter, set beside the recorded cotton prices (point at 0249).
- I4 **"What did sake cost, by the shop and by the cup?"** (`setting=city,countryside`)
  - Edo shop prices per sho and per go; Edo tavern and soba-shop prices per go; the 1842 Kazusa list (rural ceilings).
  - The Edo shop-to-tavern markup: silent.
  - The Qing: bought wine twice home-brewed, retail spirit 25% over bulk; the Qing tavern price silent.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=396`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; a scanned page's images go in with
   `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the
   eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `396: `.
4. Write `specs/396-campaign-costs-inns-transport-cloth-sake/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/396-campaign-costs-inns-transport-cloth-sake/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
