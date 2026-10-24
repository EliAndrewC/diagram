# Feature 412 - handoff between the page sessions

## Session 1

Commits b14ed2a49 and 4c1c055c4 (and the ledger/handoff commit after them).

- SECTION=0273/what-did-salt-cost
- SECTION=0279/what-did-charcoal-cost
- SECTION=0265/what-did-it-cost-to-rent-a-room-or-a-house
- SECTION=0250/what-did-an-unskilled-laborer-earn

### Question 1: Kyoto/Osaka 1745-1754 (or nearest), verdicts

- Salt, Kyoto 1745-1754: ATTESTED. Mitsui Kyoto 塩, mean 17.8 silver monme a koku (twenty seasons, 14.3-25.69), about 0.18 monme a sho; a day's wage (0.91) bought about 5 sho. `research/questions/0273-what-did-salt-cost.html` (#salt-kyoto-1745).
- Salt per kg: SILENT on the weight; the per-kg figure (0.08-0.10 monme) is this project's GUESS at 1.0-1.2 kg a liter and the file's 180.891 L a koku. Same file.
- Salt a person used a year: ATTESTED ONLY FOR the Qing: Huang Guoxin's estimate, 11 market jin (about 5.5 kg, arithmetic), a little over 9 jin of the time, the yardstick he judges the state's allotments against (NOT the state's own reckoning - source-reader corrected this). Japan SILENT. The Kashimo lead was read: 1773's table shows about 89 sho in three purchases, but the table is a selection, much salt went to miso, and the household was seven listed members plus an unstated number of servants, so no per-head figure. Same file.
- Edo salt (bonus, the Mitsui Edo books): about 15 monme a koku 1818-1829, 22 in the 1830s, 29 in the 1840s, 36 in the 1850s. Same file.
- Firewood, Kyoto 1745-1754: ATTESTED. Mitsui 薪, mean 2.64 monme for 10 kan (37.5 kg), 2.42-2.77; 0.070 monme a kg; about 13 kg a laborer's day. A million BTU: 68 kg, 4.8 monme, about five laborer-days, this project's arithmetic at FAO's 15.5 MJ/kg for air-dried wood (a modern assumption, cited). `research/questions/0279-what-did-charcoal-cost.html` (#charcoal-firewood-by-weight).
- Charcoal by weight: ATTESTED ONLY FOR Edo 1710-1716 (7.25-16.64 a 10 kan) and 1818-1823 (about 5, 2.5-2.9x firewood on average), and Osaka 1818-1823 (3.1-3.7, 0.89x firewood - the sheet reads so in all 11 entries and in 1713; why is not said; the 1989 printed tables were not read). Kyoto has no charcoal column: said. Same file.
- Back-tenement room, Kyoto or Osaka 1745-1754: SILENT; nearest Edo 1804-1830, 300-500 mon a month (a popular page with no source), 50-80 years later and another city. `research/questions/0265-what-did-it-cost-to-rent-a-room-or-a-house.html`.

### Question 3: Japanese wages by era, verdicts

ATTESTED (Mitsui 日雇賃, silver monme a day), `research/questions/0250-what-did-an-unskilled-laborer-earn.html`, a decade table. Method: the mean of every quarterly (spring/autumn) cell, each weighted alike (specs/412-money-basket-every-era/measure/mitsui_basket.py and .out.txt). The pass averaged the file's YEARLY cells instead, so these differ from the brief's figures in the second decimal: Kyoto 1804-29 0.93 (brief 0.94), 1860-67 1.34 (brief 1.32); Edo 1860-67 1.18 (brief 1.14), 1868-71 1.84 (brief 1.92). The reply on #13 should use these, with the method.
- Kyoto: 1741-49 0.86, 1750s 0.88, 1760-62 0.80, 1790s 0.85, 1800s 0.80, 1810s 0.92, 1820s 1.04, 1830s 0.95, 1840s 1.03, 1850s 1.04, 1860-67 1.34, 1868-71 1.69; 1804-29 0.93; 1830-44 0.98.
- Edo: 1710-16 1.75; 1818-29 0.90; 1830s-1850s 0.91-0.92 (82 cells, all 0.87-0.97: read as a book rate, this project's reading); 1830-44 0.91; 1860-67 1.18; 1868-71 1.84.
- The 1780s and 1872-1879: SILENT (absence note wage-gap-absence).
- Bassino and Ma's Table A.1: 0250 already says Kyoto's (its registry entry: "Its Tokugawa wage is Kyoto's alone"); nothing to correct.
- Rewritten because the Mitsui file answers them: 0279's "no Edo wage of 1842 / of 1716" and "no charcoal price by weight"; 0273's "no Edo retail salt to the 1850s" (now: none by the sho in copper, none for 1791) and its 1791 nearest wage (now Kyoto's 1791 Mitsui 0.84/0.8, about 4-6 sho of the brokers' salt); 0265's "no unskilled Edo wage in the Bunsei years" (now Mitsui Edo 0.9).

### Searches named

- Salt weight: 塩 一升 目方; 赤穂 四斗俵 貫; 塩 一俵 重さ; archive 俵 (the pass); 江戸時代 塩 一俵 何貫 赤穂塩 重さ 升; 塩 一石 何貫 近世 塩 一斗 目方 貫目 換算 (this session) - only a Matsue salt tag reading 目方九貫目, a bale's weight with no volume.
- Salt per person, Japan: 一人一年 塩; 渡辺則文; 廣山堯道; 塩業史; yanagihara.pdf; mealtime.jp refused.
- Wood energy: air-dry fuelwood calorific value 15 MJ/kg FAO -> FAO Forestry Paper 93, Appendix IV.
- Kyoto/Osaka rent: 京都 裏借家 家賃 銀 匁 宝暦/寛延/延享; 近世京都 借家 家賃 論文; 杉森哲也/塚田孝 借家 店賃; 三井 京都 貸家 家賃; the osaka-angenet Tsukada lecture (no amounts).
- Wages 1780s / 1872-79: Mitsui file, Bassino-Ma A.1, Kumon's Japanese Wages.xlsx, GPIH Japan_1885-1926.xls.

### New registry keys (3)

- bassino-2006-gpih-mitsui (the GPIH Mitsui file; archived by make source-outcome)
- huang-guoxin-2021-qing-yanzheng
- fao-1990-energy-conservation-forest-industries

### Checks run here

- source-reader: all owed notes READ (Mitsui 8/8 on a cell-by-address dump written into the bundle's pages/, since the bundle cannot decode .xls; Kashimo 4/4; FAO 1/1; Huang 1 CONTRADICTED in round 1, fixed, 7/7 in round 2). Recorded with make record-checked.
- Still owed for session 4: quote-check, record-format (0250 0265 0273 0279), intro-check (0273 0279), source-applicability (the three keys), translation-check (0273 Huang and Kashimo-4). The Mitsui quote-check needs the cell dump: regenerate it with the xlrd one-liner pattern in mitsui_basket.py or hand it /tmp/l7r-check/key-bassino-2006-gpih-mitsui-whole/pages/01-cells-by-address.txt.

### Leads not followed

- Kyoto 塩 drops to 4.5-8 monme a koku from 1791, a third of Edo's and Osaka's: probably a unit or grade change; do not use Kyoto salt after 1791 without the printed table.
- Mitsui Bunko 1989 (近世後期における主要物価の動態), print only: confirm 10貫匁 for 薪/炭 and the Osaka charcoal cells.
- Saito Osamu 1998, Kyoto day wages 1773-1790 (fills the 1780s gap), print only.
- 黄国信 2017 《中国经济史研究》 no. 4 (两广盐法志 卷19 「每日口食不过三钱」).
- 0277's Edo copper table from 1751, for a closer rate than 1766/1804.
- The archive inbox holds two WAITING downloads (堺市史_1049487_0001 (1).pdf, (2).pdf) and four over-size PDFs, none of this feature's; left for their sessions.
- Session 1, last: the Mitsui cell dump is kept at specs/412-money-basket-every-era/measure/mitsui_cells_by_address.txt (every non-empty cell, columns A-R, by address) - hand it to the Mitsui quote-check with EXTRA=. SIZE MARGIN: 0273 is about 19,550 bytes and 0279 about 19,080, against the 20,000 cap; a check's EDITs there have roughly 450 and 900 bytes of room before the split rule applies.
