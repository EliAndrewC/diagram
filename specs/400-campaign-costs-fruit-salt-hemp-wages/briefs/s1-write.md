# Brief - feature 400, campaign costs III. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** EliAndrewC/diagram#5 (gm-assistant's money skill): what fruit, salt, hemp cloth and shrine amulets
cost, and what skilled craftsmen earned against unskilled labor. Japan first, China as comparison, each figure beside the
craftsman's AND the unskilled laborer's day wage of the same place and period. Where no source gives one, say that wage is
SILENT and name the nearest, with its class (unskilled or craftsman), its place, its unit and its gap in years; a
craftsman's wage is never shown as the unskilled wage. Where the record already gives a figure (0250, 0255, 0256, 0261,
0262, 0263), point at that page and state its limit rather than repeating it. No price is converted between coins unless
its source converts it. The request is verbatim in `specs/400-campaign-costs-fruit-salt-hemp-wages/request.md`. Research
only: edit no code, modal, sheet or canon.

## The passes (leads, not citations)

`specs/400-campaign-costs-fruit-salt-hemp-wages/passes/`: `q-fruit.md`, `q-salt.md`, `q-hemp-amulets.md`, `q-wages.md`.
Each holds verbatim passages, URLs and archive copies. Read each passage on its page before citing it. Gao Shouxian on the
1736 Beijing list (`gao-shouxian-jiuqing-wuliao`) and the 欽定大清會典則例 卷130 (`daqing-huidian-zeli-130`) are already
registered; 卷154 and 卷162, the 明會典 卷136 and the others are new keys.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first,
`level=counts-and-measurements`, with no drawing page. Label every figure the project computes as the project's
arithmetic.

- B1 **"What did fruit cost?"** (`setting=countryside,city`)
  - Japan: a fresh persimmon 6 mon, rural Kanto, first half of the 1800s, from the Bank of Japan Currency Museum's sheet,
    which takes its items from several documents and names none: ATTESTED ONLY FOR that. Nearest wage: the 1818 Kumehara
    carpenter, 200 mon (0255). Edo, castle towns, pears, native apples (wa-ringo), dried persimmons: SILENT.
  - China: the Qing court's fruit purchases (會典則例 卷154, 光祿寺): persimmon 0.008 tael, apple (蘋果) 0.03, crabapple
    (花紅) 0.003, pears 0.013-0.015; dried persimmon 0.022 a jin. Court purchase prices, not the market; that the unit is
    the piece is the record's reading. Undated, in the Qianlong compilation. Beside it, Beijing 1736's laborer 75 and
    craftsmen 154 cash (on Gao; Gao's own 800 cash to the tael for 1737 is Gao's conversion). The Shengjing tax-offset
    valuations (卷162: a 香水 pear 0.01 tael, 1706; peaches by the basket). The Ming valuation of stolen goods in paper
    money (明會典 卷136): ratios only, no wage in the same money.
- B2 **"What did salt cost?"** (`setting=countryside,city`)
  - Japan: Kashimo (Mino, upland), the Hikoshichi diary 1763-74: 6 sho for 100 mon (1763), 5 sho (1765), about 5.6 (1772),
    3.2 (1773). Settle each entry's year from the booklet's own table and text before citing (the pass found 明和九年
    printed as 1771, and the 366-mon purchase under a different year in the table). Beside it, the same household's farm
    hand, 60 mon a day (1774). Otsukawa (Owari) 1842: retail 18 mon a sho; bought at 45½ bales of 9 sho per ryo (no ryo-mon
    rate given). Edo retail, Ako salt, the Edo wholesalers' bale price: SILENT. The inland price ladder (5-6 mon on the
    Inland Sea to 300 in Ichinoseki) is ATTESTED ONLY FOR a secondary, hearsay account (a blog citing 廣山堯道).
  - China: the field price 1-2 cash a jin (Lianghuai, about 1830, 清史稿 卷123); the official Changlu price 0.0104-0.0126
    tael a jin from 1688, and 16 cash a jin then, 13-14 later (the 1728 memorial); Beijing 1736 salt 0.012 tael beside its
    wages (Gao). The markups the sources state: a yin over 10 taels in the selling district against 0.64 at the field (the
    CASS paper on Tao Shu's reform); a few cash at the field against 30-70 to the consumer (Wu Haibo, OCR); King 1909,
    retail 12-15 times a manufacture cost of 1.5-4 cash a catty, not tied to a place (his Sichuan figure is a manufacture
    cost of 13-14 cash and 9 cash tax, with no Sichuan retail); Songjiang local retail of official salt, 1651-88 (閱世編).
- B3 **"What did hemp cloth and a shrine's amulets cost?"** (`setting=countryside,city`)
  - Japan hemp: one lot of Etchu hemp cloth, 20 rolls for 180 monme (a Maeda Toshinaga letter, before 1614), the roll's
    length unknown and the lot judged inferior: ATTESTED ONLY FOR that. A price by the tan, Nara-zarashi, Echigo jofu, Omi:
    SILENT; no cotton price beside it (0261's cotton is of the 1780s-90s).
  - China hemp: Beijing 1736 (Gao, Table 4): hemp cloth 0.216 tael a pi, ramie cloth 0.05 a zhang, beside coarse cotton
    0.09 a zhang on the same list, and its wages; the 1615 Ming list beside it (ramie 0.1 a zhang, cotton 0.094), with no
    wage. Gao's caveat that a pi's length varied is stated.
  - Amulets: one Ise oshi's 1813 round of 2,162 households in Ozu domain took 48 ryo 2 bu gross (29 ryo 3 bu costs), given
    in proportion, in rice or coin, for the talisman with the calendar and gifts (愛媛県史, from 宇治山田市史): ATTESTED
    ONLY FOR that; *arithmetic* per household labeled. A price per amulet or talisman: SILENT, Japan and China.
- B4 **"What did a skilled craftsman earn against a laborer?"** (`setting=city,countryside`)
  - Osaka: Takeya 1999 (社会経済史学 65-1): the magistrate's day-labor wage 236 mon (1785), raised to 248 by the helpers'
    guild; the 1801 Shitennoji carpenter estimate 4 monme (420 mon at the time's rate); Morisada's carpenter 3 monme 1 bun
    without meal money against the helper's 280 mon. Ratios are the project's arithmetic; the conflict with Saito's 4.7
    times (0250) is stated, not resolved.
  - Edo and castle towns: a same-place, same-period skilled and unskilled pair is SILENT. Gather the one-sided figures with
    places, years and gaps (0250, 0255, 0256, 0262); any Edo ratio built from them is arithmetic across places and decades.
    Saito's 2.6 times (0250) is the only single-place pair, and it is a village.
  - Qing: Zhili 1769 official norms (the Bochum 物料價值則例 database): craftsmen against laborers by county (Tianjin,
    Tongzhou, Jinzhou and others), labeled as government reimbursement rates; the 1813 Board of Works norm (Allen et al.:
    unskilled about 0.04 tael, skilled 0.01-0.02 higher); Allen's regression premium (63%) labeled as an estimate.
  - Tailors: Japan SILENT; Qing ATTESTED ONLY FOR the Jinzhou and Gaocheng grouped craftsmen's rate that names tailors
    (0.08 tael against 0.06); piece rates SILENT. Smiths: Japan SILENT; China ATTESTED ONLY FOR the Ming manual's forge
    smiths in 0263. Fletchers: SILENT, pointing at 0263.

Keep each under the 20,000-byte cap.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=400`.
2. For each page you cite, run `make archive-find`, then `make source-pages` (a PDF: download it and read it with
   pdftotext; a scan or slide, render its pages; a spreadsheet, read it and save the rows you cite), then `source-reader`
   from a bundle (`make check-bundle KEY=<k> WHOLE=1`, page images with `IMAGES=`). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `400: `.
4. Write `specs/400-campaign-costs-fruit-salt-hemp-wages/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/400-campaign-costs-fruit-salt-hemp-wages/briefs/s1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
