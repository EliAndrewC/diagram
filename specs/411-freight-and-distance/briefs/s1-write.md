# Brief - feature 411, how far goods traveled. Session 1: write (new questions A and B)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you,
the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant's money skill guesses what carriage added to a good's price (issue EliAndrewC/diagram#12,
verbatim in `specs/411-freight-and-distance/request.md`). Four search passes ran; yours are
`specs/411-freight-and-distance/passes/water.md` and `distance.md` (leads, not citations: read each passage on its page
before citing it; where it does not read as the pass says, write what the page does say, or SILENT). Write TWO new money
questions, each reserved with `make reserve KIND=question KEY=<heading id>` and tagged as 0260 or 0278 are (look at
`research/tags.json` and `contents.json`), **China first, then Japan**:

Each figure sits beside the craftsman's AND the unskilled laborer's day wage of the same place and period; where no source
gives one, say that wage is SILENT and name the nearest already in the record (0250, 0255, 0260, 0275, 0278 hold them), with
its class, place, unit and gap in years, labeled as the nearest. Label every figure the project computes (ratios, per-li
rates, distances) as the project's arithmetic. No price is converted to koku; between coins only by a rate the source gives
or 0277's, labeled. An official reimbursement rate is ATTESTED ONLY FOR official rates, not a fare; a modern historian's
statement is reported as that historian's statement, quoted. Each verdict is one of the four of `research/money-requests.md`;
a figure for which only a nearest exists is SILENT, the nearest named as a nearest, the search in the absence note.
Research only: edit no code, modal, sheet or canon. Keep each question under the 20,000-byte cap.

**Already in the record - name by file, do not repeat:** 0260 (Japan's post-station fares; Zhili carts; Hunan 1769 porter
0.003 tael a li for 80 jin and boat 0.002 tael per 10 li for 100 jin, laborer 0.03); 0278 (Yunnan and Gansu carts and
porters); 0273 (salt doubling within 2 ri inland, a blog; Huaibei salt 1 cash a jin at the works against 60-70 in its
district).

## Your items

- `A` **"What did carrying goods cost by water, against by land?"** (new) - from `passes/water.md`:
  - Jiangsu's 物料價值則例 (Bochum jiangsu_transport.xls and jiangsu_wages.xls, linked from
    oaw.ruhr-uni-bochum.de/gc/forschung/jiangsu_province.html; read the cells with xlrd, give source-reader a row dump):
    Kunshan/Xinyang, Zhenyang (and Chongming, Jiading/Baoshan), Wujin/Yanghu, the Songjiang counties - boat rates per
    boatload per li or per 100 li, porters at the landing 0.002-0.003 tael per 100 jin a li, wages 夫 0.04 per 名, 匠
    0.05-0.06 per 工. The value-share rows (3 and 5 percent of the goods' value) are not per weight: say so. Date: the
    Bochum page's own words on the edition.
  - 清史稿 卷122 (zh.wikisource): 1695 Tianjin lighters 1.32 tael per 100-shi boat per 100 li; 1868 sand-junk rate 0.55
    tael a shi Shanghai-Tianjin with lighterage 0.07 and insurance 0.03; the sea route "over 4,000 li" (1826); the
    Guangxu ceiling 0.7 rising to about 1. The steamer 2.7 and the frozen-season 8.4: only if the page reads so, flagged.
  - The ratio: Cheng 2024, LSE Economic History WP 371 (lse.ac.uk/asset-library/information/wp371.pdf; pdftotext copy at
    /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/cheng/c.txt), his words on one-tenth and
    on 1:10 to 1:37.5, and his tables' rates as his calculation; 大學衍義補 卷34 (Qiu Jun 1487): canal saves 30-40 percent,
    sea 70-80. The Jiangsu and Hunan porter-to-boat ratios as this project's arithmetic.
  - Japan: Kato 2007 (ryuka.repo.nii.ac.jp/record/181/files/n20-1kato.pdf; a downloaded copy may be at
    /tmp/l7r-pass/pdf-kato/k.pdf): about 60 monme of silver per 10 da of sake to Edo, his note's source and its caveat;
    Kibe (petit.lib.yamaguchi-u.ac.jp/8245/files/164377; text at
    /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/yam/y.txt): Hagi freight as a share of the
    rice, 3.4 percent in 1652, about 4 to 1763, 6-7 from 1764; chuma (registered key, kotobank 中馬): 3-4 horses, about 100
    kan a trip. An Edo land-to-water ratio: SILENT.
- `B` **"How far did goods travel before carriage priced them out?"** (new) - from `passes/distance.md`:
  - The rule: Shiji 129 (zh.wikisource 史記/卷129), 「百里不販樵，千里不販糴」 (Han); Xu Tan (registered,
    19010-xutan-2000-market-network) on Ming-Qing everyday goods breaking it and hubs along waterways; Skinner (registered,
    8660-skinner-2002-etudes-rurales), the marketing area's 3.4-6.1 km and modal 4.5 km.
  - Carriage as a share of the good: 明史 卷79, the 1431 surcharge by province (8/7/6/5 dou a shi, 4 at Huai'an; later 6 at
    most, 2.5 at least); 大學衍義補 卷33, Qiu Jun quoting the Han and Tang extremes (30 zhong to deliver one shi; more than
    10 zhong; Liu Yan's per-dou costs) - as Qiu Jun quotes them, dated to their periods.
  - The distance at which carriage equaled the price: SILENT in the sources. Beside it, this project's arithmetic from
    Cheng's official land rates (Table A6, as he prints them) and his 1680 grain price, labeled, with what it assumes.
  - Hauls: Ohara women (keihan.co.jp/navi/kyoto_tsu/tsu201205.html, "it is said": about 15 km, 30-40 kg on the head);
    Luopang firewood (廣東新語 卷25, registered: 10920-guangdong-xinyu-25), "a hill near water is worth double"; 0273's salt
    named; Hagi rice to Osaka (A). Tea, cloth and silk distances: SILENT beyond Xu Tan's destinations.
  - A Japanese rule from the literature (the issue asks for Japan or China): search it (the 津出し五里 rule, that villages
    bore the carriage of tax rice to the shipping point up to 5 ri, is a lead; the pass's Azumino PDF returned 404). Give it
    a verdict and the search, or SILENT with the search in the absence note.
  - Leads to try if time allows, else name them in the handoff: Kibe's Table 1 (freight by district), Furushima on chuma
    freight per ri, 新唐書 食貨志 for Liu Yan.

**New registry keys** (at most ten this session): Bochum Jiangsu, 清史稿 卷122, Cheng 2024, 大學衍義補 卷34, 大學衍義補 卷33,
Kato 2007, Kibe, 史記 卷129, 明史 卷79, the Keihan Ohara page - ten. Do not add kotobank 廻船 or 江戸地回り経済.

**Reading what the reader cannot.** A PDF `make source-pages` cannot read: download it with curl into its own empty
directory and read it with pdftotext, or render its pages (pdftoppm) and pass the images to source-reader with `IMAGES=`. A
Bochum .xls: read the cells with xlrd and give source-reader a text dump of the rows cited.

## The procedure (session 1: write)

1. `make archive-inbox`. Reserve both questions, then `make research-claim Q="<A> <B>" FEATURE=411`.
2. For each page you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, page images with `IMAGES=`). A new source takes `make reserve KIND=registry
   KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `411: `.
4. Append to `specs/411-freight-and-distance/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/411-freight-and-distance/briefs/handoff.md` (create it if absent) a `## Session 1` section:
   - `- SECTION=<NNNN>/<id>` for each question;
   - per figure the issue asks for, its verdict and the fragment file (the reply on #12 is built from this);
   - each search named; the new registry keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
