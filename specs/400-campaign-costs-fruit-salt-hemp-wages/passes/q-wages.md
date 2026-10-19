# Pass - skilled day wages (#5 question 4) (research-pass, 2026-10-19; its reply verbatim)

I found new same-document skilled/unskilled pairs, but only for Osaka (Japan) and for Zhili province (Qing). For Edo itself and for castle towns the pass is SILENT: I found no new paired figures. Nothing was written to the repository.

## 1. Sources that bear

**A. Osaka building trades — Takeya Yoshiyuki (武谷嘉之), 「近世大坂における家作「手伝」職の仲間形成」, 『社会経済史学』 65-1 (1999).** https://www.jstage.jst.go.jp/article/sehs/65/1/65_KJ00004591901/_pdf. The evidence describes 1785 to about 1853. I read it by curl and pdftotext because `make source-pages` cannot read PDFs. It is not yet in the archive. The text layer is two-column OCR, so I quote only the clean spans.

- 「先の天明5年の奉行所の口達においては「日雇賃是迄弐百三十六文」となっている。」 — "In the city magistrate's oral order of Tenmei 5 [1785], 'the day-labour wage up to now, 236 mon'" (translation).
- The 手伝 (building-site helpers) guild petition, quoted by Takeya: 「日雇賃是迄弐百三十六文宛之所，以来弐百四十八文与相定，右十弐文相増候内，四文ハ手伝之者へ差遣シ，残り八文宛受取」 — "the day wage, hitherto 236 mon each, is henceforth set at 248 mon; of the 12 mon added, 4 mon go to the helpers and 8 mon each are received [by the guild]" (translation). Takeya dates this petition "この3年後", i.e. three years after a petition he places in the 1780s.
- 「享和元年に焼失した四天王寺の再建に当たって見積もられた大工賃金は…金剛組の史料によれば1人銀4匁となっており，これを当時の相場で銭に換算すると420文となる。」 — "For rebuilding Shitennōji, burned in Kyōwa 1 [1801], the estimated carpenter wage in the Kongō-gumi records was silver 4 monme per man, which is 420 mon at the rate of the time" (translation).
- 「『守貞謾稿』においては大坂の大工賃金は飯料ぬきで銀3匁1分であり，手伝の賃金は280文とされている。」 — "In Morisada Mankō, the Osaka carpenter's wage is silver 3 monme 1 bun without meal money, and the helper's wage is 280 mon" (translation). His note 14 cites 朝倉治彦編『守貞謾稿』東京堂出版 1992, pp. 159-161.
- 「どちらにしても手伝の賃金は大工と比較すればかなり低かったと言ってよいだろう。」 — "Either way, the helpers' wage was considerably lower than the carpenter's" (translation).
- Labeled arithmetic: 420 ÷ 236 = **1.78**. This is Takeya's own juxtaposition of an 1801 estimate with an 1785 order, so it is not a same-document pair.
- Morisada is the one same-document pair (written about 1837-53), but its two figures are in different metals. Applying Takeya's 1801 rate (4 monme = 420 mon, about 105 mon per monme) to the 1840s figure gives 3.1 monme ≈ 325 mon, and 325 ÷ 280 ≈ **1.16**. That is indicative only, and the carpenter figure excludes meal money.

**B. Zhili province official public-works wage norms, the 『物料價值則例』 (memorial dated 1769).** These come from the Ruhr-Universität Bochum database spreadsheets, `https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/zhili/wuliao_jiazhi_zeli_zhili_<N>.xls`, N = 1-24, with the landing page at https://www.oaw.ruhr-uni-bochum.de/gc/forschung/zhili_province.html. `make source-pages` could not decode the .xls files, so I read curl copies with xlrd.

- The landing page says of the figures: "They give the rates which the Zhili provincial government could request to be reimbursed by the central government. According to the prefatory edicts, they reflect market prices at medium market activity, but some are also indicated as being extrapolated from earlier prices."
- Rows as the spreadsheets give them (chapter, folio, district: trade, rate in taels of silver per workday; 工 is the unit for a craftsman's day, 名 for a laborer's):

| Chapter, folio | District | Skilled rows | Laborer rows |
|---|---|---|---|
| 1, 25a | 順天 良鄉 (Liangxiang) | 匠 0.12/工 | 夯硪夫 0.08, 夫 0.06/名 |
| 1, 70b | 順天 通州 (Tongzhou) | 匠 0.15, 石匠 0.18 | 夯硪夫 0.10, 夫 0.08 |
| 13, 9a | 天津 天津 (Tianjin) | 匠 0.12, 瓦匠 (plasterer) 0.15, 石匠 0.13, 鋸匠 (sawyer) 0.10 | 夫 0.09, 夯硪夫 0.07 |
| 15, 30a-b | 正定 晉州 (Jinzhou) | 匠 (木,石,油,畫,裁,縫 — carpenter, stonemason, painter, limner, tailor) 0.08; 匠 (鋸 瓦棚裱) 0.07 | 夫 0.06 |
| 15, 48b | 正定 藁城 (Gaocheng) | the same two groups, 0.08 and 0.07 | 夫 0.06 |
| 17, 8b | 趙州 (Zhaozhou) | 匠 0.08, 瓦匠 0.10 | 夫 0.06 |
| 20, 11a-b | 廣平 永年 (Yongnian) | 匠 0.075 | 壯夫 0.06, 夫 0.05 |
| 22, 8a | 大名 大名 (Daming) | 匠 0.05 | 夯硪夫 0.05, 小夫 0.04 |

- Labeled arithmetic on these rows:
  - Tianjin: plasterer ÷ laborer = 0.15/0.09 = **1.67**; stonemason 1.44; sawyer 1.11; generic 匠 1.33.
  - Tongzhou: stonemason ÷ laborer = 0.18/0.08 = **2.25**.
  - Jinzhou: the group that includes tailors ÷ laborer = 0.08/0.06 = **1.33**.
- Labeled arithmetic across all 125 districts that have a plain 匠 row and a plain 夫 row: 匠/夫 runs from **1.00 to 2.12, median 1.60**. Districts whose artisan row is a grouped category are left out.
- The wage lists have no smith (鐵匠) or roofer rows, and no rows at all for 大興 or 宛平, the two counties of Beijing proper.

**C. Allen, Bassino, Ma, Moll-Murata and van Zanden, "Wages, Prices, and Living Standards in China, 1738-1925" (LSE WP 123/09).** This is archived: https://www.lse.ac.uk/asset-library/information/wp123.pdf. I found nothing from it in the record.

- On the 1813 『工部軍器則例』 (Gongbu junqi zeli): "the norm for average daily wages of unskilled labourers in most provinces in 1813 was about 0.04 taels". Footnote 12: "Wages of skilled craftsmen were 0.020 or 0.010 taels higher." Labeled arithmetic: 0.05-0.06 ÷ 0.04 = **1.25-1.5**.
- On their regression over private-sector wages from judicial cases of the 1740s-1810s: "the dummy for skill premium is significant; its level in regression is 63% of the wage of an unskilled labourer in the Yangzi delta." That is a regression estimate (ratio about 1.63), not a recorded pair.

**Already held, not new:** Saito 2003 (archived, https://hi-stat.ier.hit-u.ac.jp/research/discussion/2003/pdf/D03-02.pdf), with village carpenters at "2.6 times" farm labourers and "urban carpenters earned 4.7 times" in 1802-4. The 390 pass at /diagram/.clones/money/specs/390-money-foundation-research/passes/q2-wages.md already quotes it.

## 2. Reading

**ATTESTED ONLY FOR** Osaka's building trades and Qing Zhili official norms.

- **Osaka.** The Morisada pair (carpenter 3 monme 1 bun without meal money against helper 280 mon) and Takeya's 1801/1785 juxtaposition (420 against 236 mon, 1.78) both put the gap well under 2×. That conflicts with Saito's 4.7× for Osaka carpenters against Kyoto day labourers in 1802-4. Two likely reasons:
  - 手伝 were building-site helpers organized in a guild. The magistrate calls their pay 日雇賃, so this is the right comparison for a building site, but they were not generic street labour.
  - The carpenter figures exclude meal money, while the helper figure says nothing about it.
  - I have not resolved the conflict.
- **Zhili (1769).** This is government reimbursement data with uniform county figures, which Allen et al. warn may reflect policy rather than markets. Craftsmen ran about 1.3-2× laborers, with a median of 1.6; plasterers and stonemasons sat above the generic 匠 rate. That fits the Gongbu 1813 range (1.25-1.5) and Allen's regression (about 1.63).
- **Edo proper and castle towns (SILENT).** What I searched:
  - Archive terms: 手間賃, 賃銭, 日雇, skill premium, Umemura, hiyatoi, day labo, Saito, plus a combined multi-term search.
  - Web queries: 天保 職人手間賃 町触; 文政年間漫録 大工 手間; 守貞謾稿 大工 賃 (two queries); 草野 江戸末期 賃金 地域差; 三井 江戸本店 日雇 賃銭; 藩 城下 大工作料 日用賃 (extended); 近世 賃金 大工 日用 格差 城下町 (extended).
  - Pages read that did not bear:
    - Oishi 1842 物価書上 reprint (https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf). It prints the 天保13年3月6日 Edo order 「諸職人手間銭之儀去ル申年巳来，米価下落いたし候而茂不引下ケ趣二有之，右者早ミ取調引下ケ候様可致」 ("craftsmen's wages have not been lowered though rice has fallen since the year of the monkey; investigate and lower them promptly", translation), but gives no figures.
    - Ehime prefectural history page (https://www.i-manabi.jp/system/regionals/regionals/ecode:2/63/view/7977). It says Uwajima's 1663 作事方定書 fixed wages for three grades of craftsmen, with no numbers.
    - Handa 1842 price list: nothing on wages.
    - Saito WP44 (Hosei): nothing.
    - Saito 1993: Edo carpenters against Mitsui 日雇 as indices only.
    - Suzuki DP 22-04 (Osaka University): an exchange-rate paper.
  - No source anywhere gave tailors' piece rates or smiths' day wages.

## 3. Leads not followed

- 朝倉編『守貞謾稿』(1992), pp. 159-161: the Morisada passage itself. It may also give an Edo carpenter rate and the meal money; this needs checking, not assuming.
- 「天保度御改正諸事留」: Oishi's source. It may hold the 1842 Edo wage figures the order implies.
- 三井文庫『近世後期における主要物価の動態』 revised and expanded edition, 「江戸日用品小売物価表」: Mitsui Edo-store 日雇 wages 1818-70 as levels (Saito 1993 gives only indices).
- 草野 1991/1992 (福井県立短期大学研究紀要 16-17): Kyoto against Edo wage levels from Bunsei to the Bakumatsu.
- Edo-Tokyo Museum (江戸東京博物館) 日雇賃銀勘定帳 of 1853, 1857 and 1860 (e.g. https://www.edohakuarchives.jp/detail-303541.html): primary Edo day-labour rates for daimyo processions.
- 『工部軍器則例』 of 1813 itself, which stands behind Allen's footnote 12.
- The other provincial 『物料價值則例』 databases at Bochum (Gansu, Hunan, Shanxi, Yunnan, Jiangsu).

## Ledger and files

- I recorded outcomes for WP44, the Osaka DP, the Oishi reprint, Handa, the Ehime page and Saito 1993.
- The Takeya PDF and the Bochum landing page and spreadsheets bear on the question, so they are left for you to cite.
- Working copies are in /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/wages/: the Takeya text is sehs65r.txt, and the extracted Zhili wage rows are xls/wages.txt.

Sources:
- [Takeya 1999, 社会経済史学 65-1](https://www.jstage.jst.go.jp/article/sehs/65/1/65_KJ00004591901/_pdf)
- [Bochum Zhili 物料價值則例 database](https://www.oaw.ruhr-uni-bochum.de/gc/forschung/zhili_province.html)
- [Allen et al., LSE WP 123/09](https://www.lse.ac.uk/asset-library/information/wp123.pdf)
- [Saito 2003, Hi-Stat D03-02](https://hi-stat.ier.hit-u.ac.jp/research/discussion/2003/pdf/D03-02.pdf)
- [Oishi, 天保13年8月 物価書上](https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf)
- [えひめの記憶 7977](https://www.i-manabi.jp/system/regionals/regionals/ecode:2/63/view/7977)