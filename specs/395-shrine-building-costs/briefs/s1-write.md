# Brief - feature 395, what a small forest shrine cost to build. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#6 (gm-assistant, for the GM's session on 2026-10-19): what a small forest shrine
cost to build, Japan first, each figure beside the craftsman's and laborer's day wage of the same place and period. The
request is verbatim in `specs/395-shrine-building-costs/request.md`. This is research only: edit no code, modal, sheet or
canon.

## The passes (leads, not citations)

`specs/395-shrine-building-costs/passes/`: `q-sanctuary.md`, `q-roof.md`, `q-stone.md`, `q-rites.md`. Each holds verbatim
passages, URLs and local copies. Read each passage on its page before citing it.
- The two AIJ papers (No. 420 and No. 435, Kawakami 1991 and 1992) are scanned PDFs: read them by OCR, check every quote
  against the page image, then `make archive URL=<public url>`.
- `make source-pages` cannot read a PDF: download it and read it with pdftotext, or OCR it.
- Wages already in the record: 0250 (unskilled wages; Saito 2003; Bassino and Ma). Cite those rather than duplicating
  them.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure a pass computed (per-day equivalents, the
600-1,100 craftsman-day reading of the 30-ryō contract) as the project's arithmetic.

- S1 **"What did a small shrine sanctuary cost to build?"** (`setting=countryside`)
  - The 1841 Shibasaki one-bay sanctuary: the winning bid of 30 ryō against bids of 50-80; what was paid outside the bid
    (timber, carvings at 3 ryō a panel); the worship hall's 11 ryō 2 bu; and the building funds of over 120 ryō.
  - The 1749 Kasuga repair: 187 carpenter and sawyer days plus 24 roofer days. Its cost shares, 43 ryō 1 bu in all, are
    kept in S2.
  - The 1805 repair (about 61 ryō 2 bu 3 shu; wages 44.2%); the Mitake 1764-70 repair (about 9 ryō 2 bu; wages and rice
    66.3%).
  - The day wages: Tama 1749; Kumehara 1818 and 1830, with the 1830 notice board at 50 carpenter-days.
  - Small hokora: silent (an absence note).
- S2 **"What did a shrine roof cost, in copper, bark or shingle?"** (`setting=countryside`)
  - The 1749 copper re-roofing: 43 ryō 1 bu in all, materials 53.1%, wages 14.6%, a 7 shaku 8 sun bay. The 1772-73 copper
    tiles: 11,000 for just under 30 kan of silver.
  - The carpenter wages the pass found (the 1751 shogunate standard; Edo 1804-30 and 1853-56).
  - Silent (absence notes): cypress bark, shingle, roofer-days per tsubo, persimmon tannin, and the roof area.
- S3 **"What did a torii, stonework and earthwork cost?"** (`setting=countryside,city`)
  - Osaka 1620s: earthwork at 7-10 monme per tsubo of earth beside day wages of 0.8-1.2 monme; rubble at 23 men per tsubo;
    stone-hauling paid 1.3-1.5 monme.
  - The pack-horse load of stone (two blocks); the 1708-09 great stone torii at a reported 3,200 ryō, as an upper bound.
  - Silent (absence notes): a wooden torii, posts, stepping stones, mason-days, and a burial mound.
- S4 **"What did a shrine's rites and furnishings cost?"** (`setting=countryside,city`)
  - The Fushimi Inari installation fee schedules (before 1864 and 1864) and the grades chosen (28 of 46 the abbreviated).
  - Silent (absence notes): the ground rite, depositing remains, the bell and rope, the plaque, and the offering table.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=395`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (or the PDF route above), then `source-reader`
   from a bundle. A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the
   eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `395: `.
4. Write `specs/395-shrine-building-costs/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/395-shrine-building-costs/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
