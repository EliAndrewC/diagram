# Brief - feature 401, kitchen knives and the copper-to-silver rate. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#8 (gm-assistant's money skill): what kitchen knives cost in Edo Japan, ordinary and
by a noted maker, a smith's output a day and the split between smith, sharpener and handle-maker, with a Ming or Qing
cleaver beside them; and the market rate of copper mon to silver monme and to the gold ryo, 1780s-1850s, Osaka and Edo,
with the official rate beside it. Each knife price sits beside the craftsman's AND the unskilled laborer's day wage of the
same place and period; where no source gives one, say that wage is SILENT and name the nearest, with its class, its
place, its unit and its gap in years. The rate question gives rates, not converted prices. The request is verbatim in
`specs/401-knives-and-copper-rate/request.md`. Research only: edit no code, modal, sheet or canon.

## The passes (leads, not citations)

`specs/401-knives-and-copper-rate/passes/`: `knives.md`, `knives-2.md`, `exchange-rate.md`. Each holds verbatim passages,
URLs and where they were read. Read each passage on its page before citing it. The NDL scans are read on their page
images (render them; NDL's `lab.ndl.go.jp` full-text JSON is the OCR, checked against the image), and the images go to
source-reader with `IMAGES=`. `gao-shouxian-jiuqing-wuliao`, `daqing-huidian-zeli-130` and `saito-2003-wages` are already
registered.

## Your items (two new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure the project computes as the project's
arithmetic.

- B1 **"What did a kitchen knife cost?"** (`setting=city,countryside`)
  - Edo 1851: the tool and blade wholesalers' price-cut list (『諸問屋再興調』, 「大工道具打物直段引下ケ書」), old and reduced
    prices in silver monme for usuba cooking knives, sashimi, deba, vegetable and tobacco knives by grade. Wholesale.
    The unit (per ten blades, 「十枚ニ付」) is the record's reading of the page layout and is said so; settle it on the
    images (R54, R57, R58) and say what the page shows. The pass reads 弐匁庖丁 as 出刃 in cursive: settle it on the
    image or keep the printed reading and say so. A price a knife is the project's arithmetic.
  - Tsuyama 1665 (『吉備群書集成』2, 「諸職人作料値段定帳」): a kitchen knife 8 monme of silver, a ceiling on the town's
    three sword smiths' work; the separately licensed polishers' tariff is for swords only.
  - The makers: price by maker SILENT for Sakai, Seki, Takefu and Tosa, each named. Sakai's tobacco-knife guild (1730
    stamp, 31 shares, the levy per knife: 1 rin in 『堺市史』, 3 rin in the 1761 rules - state the disagreement) and
    Takefu's smithies and sickle-and-knife sales (福井県史) with their verdicts.
  - Output: ATTESTED ONLY FOR Sakai's 1761 night-work rule, 21, 27 or 30 tobacco knives a day by size; kitchen knives
    SILENT; no per-smith rate from Takefu's totals.
  - The split: polishers a separate trade at Sakai bargaining over pay (1855); smiths, grinders and handle-makers about
    1757 at second hand (Kawashima on Yamaguchi); a kitchen-knife handle-maker SILENT; a sharpener's fee SILENT.
  - China: a 1-jin kitchen cleaver 0.1 tael on Beijing's lists (1736, Gao Table 7; 會典則例 卷130), beside the same
    list's laborer 75 and craftsmen 154 cash (Gao's 800 cash to the tael is Gao's conversion); a Wanli-era cutting knife
    about 0.05 at second hand, beside Gao's 1615 Board of Works wages (0.03-0.07 tael).
  - Wages beside Edo 1851 and Tsuyama 1665: the nearest named with class, place, unit and gap (0250, 0255, 0256).
- B2 **"What was copper coin worth in silver?"** (`setting=city`)
  - The official rate: 1 ryo = 60 monme = 4,000 mon from 1700 (kotobank 銭相場; ja.wikipedia 御定相場); 6,500 mon to the
    ryo in Edo from 1842. Law, not the market.
  - The Osaka market (Kobe RIEB / Mitsui 近世経済データベース, from the Osaka exchange office's diary, 1787-1871): archive
    the Excel file (`make archive-inbox`), then compute decade means from the archived file with a script you commit and
    name in the note. Give mon per monme and mon per ryo by decade, beside the source's own units (monme per kanmon,
    monme per ryo), and state the method: the days used, each day's value (the midpoint where a minimum and maximum are
    given), the years missing. 1844-49 is the administered floor of 10 monme a kanmon (the 1843 order), never a market
    rate. After 1859 gold is quoted in subsidiary coins; stop the decade table at the 1850s or say so.
  - Edo: a printed figure only. Iwahashi 1998's figure 3 is a chart: any value read off it is the project's reading of the
    chart, or the Edo rate is SILENT with the nearest printed figure (the 1766 Osaka and 1867 Kyoto single days in
    ja.wikipedia 三貨制度; about 6,000 mon about 1778, 寛永通宝) named with its place and gap.
  - Before 1787: the 1766 Osaka figure (about 66 mon a monme) and what a printed source gives for the 1780s.
  - The anchor years: 1802-04 (the Kyoto wages, 0250) and 1842 (the Kazusa list, 0262), each with the rate the series
    gives and which question it serves.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=401`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan, render its pages; a spreadsheet, read it with a script and commit the script), then `source-reader`
   from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page images with `IMAGES=`). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `401: `.
4. Write `specs/401-knives-and-copper-rate/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/401-knives-and-copper-rate/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
