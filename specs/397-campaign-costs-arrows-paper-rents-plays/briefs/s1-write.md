# Brief - feature 397, campaign costs II: arrows, paper, rents and plays. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#4 (gm-assistant's money skill): what arrows, paper and ink, rents, and plays and
shows cost, Japan first with Qing China beside it, each figure beside the craftsman's AND the unskilled laborer's day wage
of the same place and period. Where no source gives one, say that wage is SILENT and name the nearest, with its class
(unskilled or craftsman), its place, its unit and its gap in years; a craftsman's wage is never shown as the unskilled
wage. The request is verbatim in `specs/397-campaign-costs-arrows-paper-rents-plays/request.md`. This is research only: edit no code, modal, sheet or canon.

## The passes (leads, not citations)

`specs/397-campaign-costs-arrows-paper-rents-plays/passes/`: `q-arrows.md`, `q-notices.md`, `q-rents.md`, `q-plays.md`. Each holds verbatim passages, URLs and
archive copies; the rendered page images they used are named in them. Read each passage on its page before citing it.
- Wages already in the record: 0250 (Kyoto 1802-04), 0256 (Edo carpenter 1804-60), `allen-2009-china-wages` (Qing
  construction wages 1769-95). Point at them rather than repeating them. Check `make archive-find` and the registry for
  Gao Shouxian's 1736 Beijing price list before registering it (feature 396 may have).
- **Units.** Mon and silver, and Qing cash and taels, are not converted: no exchange rate is written in this feature. A
  price set beside a wage in another unit states both units.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure the project computes as the project's
arithmetic.

- A1 **"What did arrows cost?"** (`setting=countryside,city`)
  - Per arrow, ordinary and fine, ATTESTED ONLY FOR Ming and Qing China: late Ming about 0.0136 tael (under 0.033 within
    a set); 1650, 0.04; 1727 Beijing, war arrows 0.05-0.08 and fine arrows 0.12-0.36.
  - Japan, fletcher output per day, arrowheads: silent (absence notes); Kawato's remark that a head traded at about a
    spearhead's value is a historian's guess, labeled as one.
  - Recovery after battle: NOT ATTESTED; the Qing code writes battle losses off.
- A2 **"What did paper and ink cost?"** (`setting=city`)
  - Qing Beijing 1736, paper per sheet by grade, beside that list's own wage; ink per jin as the nearest to an ink stick.
  - An ink stick, and Edo paper and ink: silent (the two web figures disagree and neither is citable: say so in the
    absence note's comment).
- A3 **"What did it cost to rent a room or a house?"** (`setting=city`)
  - Edo: one Bunsei-era carpenter's back-tenement rent, 10 monme a month.
  - Qing: government houses per bay (the 1727 schedule); shop-front rooms (Daoguang-era contracts; the 1871-1911
    government file); one official's 15-16-bay house (Li Ciming, 1871).
  - The rent-to-value ratio: an Edo lot with its houses (3-5% net; 4.8% gross by Mitsui's 1811 rule); Qing administrative
    prices per bay (about 4-6%); against the building alone, silent.
  - Silent in Japan: a street-front shop, a small house, a samurai residence and a storehouse by the month; castle-town
    rents; any rent by the week.
- A4 **"What did a play or a show cost to see?"** (`setting=city,countryside`)
  - Edo kabuki 1803: the pit 132 mon to boxes of 25-35 monme for seven; the single-act view at 16 mon, at the oikomi only.
  - Noh: kanjin-no only (30 mon c.1614-24; Saikaku's "one gold piece" box, 1688; the 1848 forced tickets).
  - Temple-fair shows: silent. Rural troupes: troupe hire only (Funai 1690-1735), not per seat.
  - Donations: a Japanese street performer's collection silent; village hana and shugi silent; a Qing street act of the
    1720s asking 3 cash.
  - Troupe composition (kabuki and joruri troupes; misemono a separate trade); Qing seats (pit per head, gallery per
    table, 130 cash before 1900; a rural Henan troupe for three days).
  - Do NOT write the English players here: session 2 writes them as a comparative question.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=397`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext), then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; a scanned page's images go in
   with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At
   the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `397: `.
4. Append to `specs/397-campaign-costs-arrows-paper-rents-plays/implementation-check.md` one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/397-campaign-costs-arrows-paper-rents-plays/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
