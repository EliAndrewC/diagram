# Brief - feature 398, the rest of the shrine builder's options. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#7 (gm-assistant's shrine builder): what the builder's alternative options cost,
Japan first, each figure beside the craftsman's AND the unskilled laborer's day wage of the same place and period. Where no
source gives one, say that wage is SILENT and name the nearest, with its class (unskilled or craftsman), its place, its
unit and its gap in years; a craftsman's wage is never shown as the unskilled wage. Where 0255-0258 already give an item,
point at that page and state its limit rather than repeating it. The request is verbatim in `specs/398-shrine-builder-options/request.md`. Research
only: edit no code, modal, sheet or canon.

## The passes (leads, not citations)

`specs/398-shrine-builder-options/passes/`: `q-sanctuary.md`, `q-stone.md`, `q-metal.md`, `q-rites.md`. Each holds verbatim passages, URLs and
archive copies. Read each passage on its page before citing it.
- Kawakami AIJ No. 435 (1992) is archived as `kawakami-1992-shrine-headman` (registered by 0255); its notes 31-36 (pp.
  93-94) are read on the page images, not the garbled text layer. Render the pages and pass them to source-reader with
  `IMAGES=`.
- Wages in the record: 0255 (Kumehara 1830 carpenter; Tama 1749), 0256 (Edo carpenter 1804-60), 0250 (Kyoto 1802-04
  unskilled), `allen-2009-china-wages` (Jiangsu 1769). Point at them.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure the project computes as the project's
arithmetic.

- B1 **"What did a shrine's other sanctuaries, halls and finishes cost?"** (`setting=countryside`)
  - Kasuga- and shinmei-zukuri sanctuaries, a stone hokora: silent (every small-sanctuary cost found is nagare-zukuri).
  - The cover-shed: only inside the Mitake repair in 0255 (sanctuary, covering house and repainting together); alone,
    silent.
  - The worship pavilion: covered by 0255 (11 ryo 2 bu); Shibasaki 1841 fittings: a 1-ryo deposit on the fittings as a
    set, 2 bu 2 shu the final payment for twelve doors. The offering hall: silent.
  - Hinoki, keyaki and sugi timber: silent (Shibasaki 1841 found cedar and pine "out of stock and very dear"; 1 ryo sent to
    buy scaffold cedar is money carried, not a price).
  - Thatch: quantity and labor only (36 horse-loads, unpriced; helpers on both roofs 2 ryo 3 bu wages and keep; thatch
    reckoned 1 shaku 2 sun thick). Shingle: one purchase (eight bundles of roof boards, 2 bu 1 shu, 1840; the roofer's
    3 bu extra and 2-shu gift). Copper: covered by 0256.
  - Vermilion, bengara, black lacquer: silent. Openwork transoms: silent.
  - Relief panels: covered by 0255 (3 ryo a panel). Carved beam ends: only inside a whole sanctuary's carving set (Tanashi
    1858, 147 pieces on a 4.3-shaku bay, 135 ryo, called exceptionally low by the shrine's page). Kawagoe Hikawa
    (1842-49, 1,369 ryo excluding the roof, a large all-keyaki sanctuary): an upper bound only.
- B2 **"What did a shrine's stonework cost?"** (`setting=countryside`)
  - A small stone torii: silent; 0257's great torii is an upper bound only.
  - A pair of stone lanterns: 4 ryo 3 bu delivered, Shibasaki 1841, an Atsugi mason. A tall lantern: silent.
  - A mason's day: only the 1841 payment of 1 bu for four extra men on the plinth work (the source names neither trade nor
    days; about 3.75 monme each if one day each is the project's reading).
  - A stairway: only the plinth stones (2 ryo 2 bu 2 shu toward them, 1840; 2 kanmon for laying them; 2 bu 2 shu estimated
    for the entrance curb).
  - Komainu or foxes, a basin, a stele, a gorinto, a coffer: silent.
- B3 **"What did a shrine's metal furnishings cost?"** (`setting=countryside,city`)
  - The mirror, the waniguchi gong, hanging lanterns, a reliquary, an offering chest and its lock, a lacquered chest:
    silent.
  - The nearest: raw copper bought by the Osaka copper office, 1774, about 139-157 monme per 100 kin; home-market copper
    "about twice" the China export price; a Takaoka shrine mirror of 1833 weighing 34 kg, unpriced. Qing coarse copper ware
    sold by weight, 0.27-0.28 tael a jin (early Qianlong). The metal-floor arithmetic is labeled as such.
- B4 **"What did rites for the dead and a shrine's dedication cost?"** (`setting=countryside,city`)
  - A night enshrinement: the cost share is covered by 0255/0256 (20.0% of the 1749 repair); the priests' fee silent; the
    1549 Izumo list gives goods, no money.
  - A goryo festival: only one Hakata ward's Gion float duty, 1838, 7,300 monme (800 of it procession money); about 1691 the
    levy on the towns off duty a little over 200 monme.
  - Eitai kuyo, washing bones: silent. A portion of remains to a distant mountain temple: silent (searched as Koyasan).
  - A calligrapher's plaque fee: silent in Japan; Zheng Banqiao's 1759 price list (six taels a large piece, one a scroll or
    couplet, five qian a fan), with no plaque line, beside the Jiangsu 1769 wage.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=398`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page
   images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two
   write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `398: `.
4. Write `specs/398-shrine-builder-options/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/398-shrine-builder-options/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
