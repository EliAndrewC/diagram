# Brief - feature 416, gold, silver and copper as separate monies. Session 1: write (new question A, Japan)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM wants the record to know how gold, silver and copper actually worked as separate monies, so he can
decide how much to import into Rokugan's fixed decimal coinage (issue EliAndrewC/diagram#16, verbatim in
`specs/416-three-metals/request.md`; read its four questions). Your pass: `passes/japan.md` (leads, not citations: read each
passage on its page before citing it; where it does not read as the pass says, write what the page says, or SILENT). PDFs the
reader cannot read (Oishi 1966 - the archive holds only HTTP 406 stubs, re-archive it; Iwahashi 2010; Kano; Kobayashi 2017): the
pass's text dumps are in `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/` (`oishi/o.txt`,
`mu/p.txt`, `ds/p.txt`, `imes/c.txt`); download into an empty directory and read with pdftotext if absent, page images
(`IMAGES=`) for the checks where the text layer is garbled; quote as printed, garbled characters bracketed.

**Already in the record - name by file, do not repeat:** 0277 (Japan's legal rates of 1700 and 1842, the Osaka and Edo market
series, the 1843 floor); the coin question feature 412 wrote (chogin fineness, koban gold, the nanryo and ichibu-gin's silver
against their face); 0265 (rents in mon and in monme); feature 414's questions on price stability.

## Your items

- `A` **"Were gold, silver and copper one money or three in Edo Japan?"** (new, tagged as the money section's questions are).
  The four questions in order:
  1. The legal rates of 1609, 1700 and 1842 and who set them; enforcement as the orders print it (Oishi's 1842 order and its
     penalties, the 1813 ban, the 1796 purchases and 1829 sales of copper, Ooka's summons of 1736); a prosecution SILENT; the
     market's straying by period (silver 48-50 monme against 60, 1695 to the Hoei recoinages; copper 2,800-3,700 against 4,000,
     5,000-7,000 from 1769, about 10,000 by the late 1860s against 6,500); the fixed-by-count ladder (ryo = 4 bu = 16 shu; the
     five-monme piece of 1765, the nanryo of 1772, the ichibu-gin of 1837) and what it did to weighed silver; the changers'
     resistance to the nanryo (the 25% premium demanded, the allowances, the loans).
  2. Which metal priced and paid which transaction - wholesale against retail, gold in the east against silver in the west (the
     rice price quoted both ways, Morisada via jawiki 金遣), wages, rents (0265, named), taxes (in koku, paid in rice and money in
     shares; the Kanto's ei), samurai stipends (rice through the fudasashi), shop purchases (copper); domains' outside trade in
     shogunal coin and inside trade in notes and copper (Kano); the fees attested - the 1859 recall (about 3.2%, this project's
     arithmetic), the nanryo allowances (about 0.7% and 1.3%), the fudasashi's 3 bu per 100 bales - and the common "1-2%" said to
     carry no citation.
  3. Edo 1842's copper-only cuts (silver-priced goods exempt; the cuts doubtful - Oishi); Tsugaru 1837-38's coin and note prices;
     Edo 1854-1868's different values for one face (legalized 1865, raised 1868); the Tenpo coin at about 80 for 100; premia for
     full-weight old coin after recoinages; Sengoku's discounted bad coin (4 bita to a good mon; Nobunaga's grading of 1569); a
     premium or discount for paying in GOLD - search it (金払い 打歩, 小判 増歩, 金建て 値引), SILENT with the search if none; how
     fast copper prices followed the rate outside 1842: SILENT (searched; Mitsui's series are in silver).
  4. The four groups - wage earners paid in copper, taxpayers, merchants, samurai on rice stipends - in the Meiwa iron and brass
     coins (copper about 4,000 to 6,000 mon a ryo, 1769-1778; Oishi on the Tanuma-period risings), the Tenpo recoinage and
     copper's fall of the 1830s-40s (Edo craftsmen's copper wages not falling with rice after 1836), the Bunsei, Tenpo and Man'en
     recoinage gains (Kobayashi 2017), the 1860s silver-west real wage (Saito 1993); each effect where a source gives one, SILENT
     with the search where none (a Meiwa-An'ei real wage in copper; a Japanese tax burden measured); what people did (hoarding,
     refusing or discounting coin, the changers' resistance, riots; a wage earners' petition SILENT).
  Against each question's canon, said on the page as the setting's choice beside the history (a deviation where it differs):
  Rokugan's fixed decimal coinage (1 koku = 10 bu = 100 zeni = 1,000 sen, `l7r.md` "Money", read with `make canon TERMS="koku|zeni|sen"`);
  the money skill's who-uses-which-coin; the conversion table's route through silver - and, if copper prices were sticky, that
  a mon amount is better measured against copper prices. Do not edit the canon.

**New registry keys** (at most ten): jawiki 御定相場, 三貨制度, 寛永通宝, 天保通宝, 南鐐二朱銀, 一分銀, 金遣, 撰銭 (check which are
registered), Oishi 1966, Iwahashi 2010, Kano, Kobayashi 2017, the Bank of Japan museum catalog pages - the rest to the
continuation brief.

## The procedure (session 1: write)

1. `make archive-inbox`. Reserve the question, then `make research-claim Q="<A>" FEATURE=416`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragment, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `416: `.
4. Append to `specs/416-three-metals/implementation-check.md` (create it if absent):
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/416-three-metals/briefs/handoff.md` (create it if absent) a `## Session 1` section: `- SECTION=<NNNN>/<id>`; per
   figure the issue asks, its verdict and the fragment file; each search named; the new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
