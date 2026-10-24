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
## Session 2
Commits e274411d9 and 03ea408af (and the handoff commit after them).
- SECTION=0286/what-did-a-years-necessities-cost-in-japan-era-by-era
- SECTION=0287/how-much-silver-was-a-monme-a-ryo-and-a-bu-coinage-by-coinage
### Question 2: per era and good, verdicts (all in `research/questions/0286-what-did-a-years-necessities-cost-in-japan-era-by-era.html` unless named)
Method: every figure an era mean, each cell weighted alike (Mitsui spring/autumn cells; Kumon's UNHIGHLIGHTED yearly cells only, the yellow ones being his estimates from rice; Kimura's yearly cells), from specs/412-money-basket-every-era/measure/basket_eras.py and .out.txt. Mitsui columns: rice, wheat (mugi, read as wheat by the transcriber), salt, lamp oil a koku; firewood, charcoal 10 kan; day wage. Kumon: a kg (rice, soybeans, barley), a liter (oils), a tan (cloth, headed "linen"). All silver monme.
- Osaka 1620-1650 (Kimura): rice 33.5 a koku ATTESTED; soybeans 31.0 a koku ATTESTED; salt 1.08 a to ATTESTED (5 yrs); oil 2.41 a sho ATTESTED ONLY FOR oil not said lamp or edible; white cloth 2.86 a tan and bleached cotton 10.0 a tan ATTESTED; wheat/barley SILENT; fuel SILENT (pine by area, coal by the sack, unconvertible); day wage SILENT.
- Osaka 1690-1739: rice by decade 54.2 / 71.2 / 106.5 / 47.9 / 53.8 a koku ATTESTED (Kumon = Iwahashi's Dojima series from 1701; Kumon does not say his 1690s source); barley 0.19 (1720s) and 0.38 (1730s) a kg ATTESTED ONLY FOR 5 years each; soybeans 0.36 a kg (1725) and cloth 4.2-4.3 a tan (1725-1726) ATTESTED ONLY FOR single years. Mitsui 1710-1716: Edo rice 103, salt 41.4, lamp oil 430, firewood 3.43, charcoal 9.87, wage 1.75; Kyoto 1713 rice 151.5, salt 29.3, lamp oil 878, firewood 3.82, wage 1.19; Osaka 1713 rice 135.9, lamp oil 773, firewood 5.43, charcoal 4.84. The recoinages of 1695, 1706, 1710, 1711, 1714 and 1736 are said in the block. Other goods SILENT.
- Kyoto 1745-1754: 0249's basket named, not repeated; the Mitsui books add rice 71.9 and lamp oil 327 a koku (salt 17.8 in 0273, firewood 2.64 in 0279, wage 0.91 in 0250, named). Kumon's Osaka: rice 0.399 a kg, barley 0.301 (9 yrs), lamp oil 1.81 a liter.
- Osaka 1780-1789 (Kumon): rice 0.456, soybeans 0.466 (9), barley 0.369 (8) a kg, lamp oil 1.89 (6) a liter ATTESTED; day wage SILENT (absence note basket-wage-absence).
- Kyoto 1790-1799 (Mitsui 1791-1799): rice 83.0, wheat 99.6 (7 cells), lamp oil 312, firewood 2.79, wage 0.85; salt 6.1 DOUBTFUL. Kumon: soybeans 0.451, barley 0.321, lamp oil 1.73.
- Kyoto 1800-1817: rice 74.5, lamp oil 271, firewood 2.81, wage 0.86 (this session's mean by 0250's method; 0250 gives 0.80 for the 1800s and 0.92 for the 1810s); salt 6.5 DOUBTFUL. Kumon: soybeans 0.368, barley 0.295, edible oil 1.49, lamp oil 1.50, cloth 6.21 a tan.
- Edo 1818-1829: rice 70.7, salt 15.2, lamp oil 284, firewood 1.96, charcoal 5.02, wage 0.90. Osaka the same years: rice 72.3, salt 17.2, lamp oil 284, firewood 3.70, charcoal 3.42. Kumon: soybeans 0.410, barley 0.284, edible oil 1.44, lamp oil 1.54, cloth 6.01.
- 1830-1844: Kyoto rice 101.8, wheat 100.4 (17), salt 7.0 doubtful, lamp oil 351, firewood 2.89, wage 0.98; Edo 111.5, 137.9 (4), 23.9, 405, 1.99, charcoal 6.42, wage 0.91; Osaka 106.1, 101.7 (12), 35.5, 386, 4.26, charcoal 4.05. Kumon: soybeans 0.562, barley 0.419, edible oil 1.85, lamp oil 1.94, cloth 7.17.
- 1850-1859: Kyoto 115.0, 88.0 (18), 6.2 doubtful, 409, 3.25, wage 1.04; Edo 117.2, 92.8 (6), 35.7, 461, 2.08, 7.33, wage 0.92; Osaka 113.1, 106.7 (3), 30.8, 426, 4.72, 4.25. Kumon: soybeans 0.674, barley 0.475 (5), edible oil 2.36, lamp oil 2.26, cloth 7.85 (2).
- 1860-1867: Kyoto 445, 465 (7), 25.8, 1,052, 9.49, wage 1.34; Edo 283, 252 (9), 82.2, 874, 3.84, 16.9, wage 1.18; Osaka 490, -, 107.2, 1,226, 12.37, 12.33. Kumon: soybeans 2.25, barley 0.98 (2), edible oil 6.35, lamp oil 5.32; its one cloth cell (1867, 133 a tan) left out, said. The era's means hide a several-fold rise (Kyoto rice 146-1,188).
- Every era: fish, other beans, buckwheat and millets SILENT (Kumon imputes them from rice in every year before 1879); rent of a room in Kyoto or Osaka SILENT (0265's Edo named in the body). Kyoto salt from 1791: two-fifths of Edo's and Osaka's in 1818-1829, a fifth to a sixth from the 1830s, read as a unit or grade change (absence note kyoto-salt-absence). Cloth: Bassino and Ma's Osaka 1840s cotton, 5.83 g a meter = about 19.9 monme a tan at their 3.11 g, against Kumon's 6-9: said, grade not stated.
### Question 4: grams of pure silver by coinage (all in `research/questions/0287-how-much-silver-was-a-monme-a-ryo-and-a-bu-coinage-by-coinage.html`)
- A monme of chogin (3.75 g x the prescribed fineness, jawiki 丁銀; assays from the Genbun and Tenpo articles): Keicho 1601 3.00 g; Genroku 1695 2.40; Futatsu-takara 1706 1.875; Eiji 1710 1.50; Mitsu-takara 1710 1.20; Yotsu-takara 1711 0.75; Kyoho 1714 3.00; Genbun 1736 1.725 (assay 45.10%: 1.69); Bunsei 1820 1.35; Tenpo 1837 0.975 (assay 26.05%: 0.977); Ansei 1859 0.49-0.525 (13% [sic] or 14%). ATTESTED (prescribed fineness, via the article).
- Side by side: six finenesses 1714-end 1722; Genbun to Feb 1827 beside Bunsei from 1820; old silver withdrawn 1842 with the deadline put off repeatedly; Tenpo to the 1868 abolition of silver units, so beside Ansei from 1859.
- Koban gold: Keicho 15.0-15.5 g; Genroku 10.25; Hoei 7.90; Shotoku 15.0, Kyoho 15.5; Genbun 8.62; Bunsei 7.40; Tenpo 6.39; Ansei 5.11; Man'en 1.87. A bu = a quarter (jawiki 三貨制度).
- Per era of question 2 (chogin; g a monme; monme a ryo -> g a ryo; mon a monme -> g a kanmon): Osaka 1620-1650 Keicho 3.00; 50 (1609 law) -> 150, early market about 43 -> 129; 80 mon (law) -> 37.5 g; copper market SILENT. 1690-1694 Keicho; 61.7 (coin-walk) -> 185. 1695-1705 Genroku 2.40; 60 law -> 144, 47-48 in 1700 -> 114; 67 mon law -> 36.0, 78 mon (1700) -> 30.7. 1706-1721 mixed Hoei/Kyoho, not converted. 1722-1735 Kyoho 3.00; 57.7 -> 173; 83 mon -> 36.2. 1736-1739 Genbun 1.725; 55.1 -> 95; 53 mon -> 32.8. Kyoto 1745-1754 Genbun; 62.5 (Iwahashi Osaka) / 61.3 (coin-walk) -> 108 / 106; 73 mon (coin-walk, city unnamed) -> 23.8. Osaka 1780-1786 Genbun; 58.4 -> 101; 103 mon -> 16.7. Osaka 1787-1789; 55.6 (0277) -> 96; 105 -> 16.4. Kyoto 1790-1799 at Osaka's rate (0277); 60.6 -> 105; 107 -> 16.2. Kyoto 1800-1817 at Osaka's (0277); 64.4 -> 111; 109 -> 15.8. Edo 1818-1829 Genbun to 1827 / Bunsei 1.35; 63.4 (Osaka) -> 109 / 86; Edo's 6,610 mon a ryo -> 104 mon a monme -> 16.5 / 12.9. 1830-1836 Bunsei; 61.8 -> 83; 110 -> 12.3. 1837-1844 Tenpo 0.975 (Bunsei beside it to 1842 and later); 62.8 -> 61 / 85; 108 -> 9.0 / 12.5. 1850-1859 Tenpo; 64.1-70.9 -> 62.5-69; 95-105 -> 9.3-10.3. 1860-1867 Tenpo / Ansei; 83.6 (coin-walk, 72-98) -> 81.5 / 41-44; 84 mon -> 11.6 / 5.8-6.3; Kyoto's own 1867: 107.1 monme and 8,460 mon a ryo, 79 mon a monme.
- Gold rates: ATTESTED 1787-1859 (0277); ATTESTED ONLY FOR a secondary chronology before (coin-walk transcribing 『日本史資料総覧』 1986, labeled so) and Iwahashi's implied Osaka rate from 1720 (they agree within about 1.5 monme). Legal rates 1609 and 1700 ATTESTED (jawiki 三貨制度, BOJ sheet).
- Coins themselves: nanryo 1772, 21.6 monme of pure silver a ryo by the article (81 g), 79 g by the assay; the 1773 order: a ryo = 24 monme of pure silver (90 g) ATTESTED; Bunsei nanryo 1824 59 g a ryo; Tenpo one-bu 9.2 monme a ryo by weight, 34 g pure silver (Tenpo chogin 15.6 monme); Ansei one-bu 31 g.
- Bassino and Ma's 3.11 g a monme: quoted; its basis SILENT (absence note coin-silver-311-absence); Bassino's GPIH note (3.75 g assumed, the content uncertain, 3-3.2 g possible) quoted. 3.11 is 83% of a monme's weight, finer than any chogin after 1736.
### Searches named (this session)
- Copper market rates: 寛永 銭相場 金一両 銭 貫文 1630年代 1640年代 相場; 寛永通宝 発行 銭相場 下落 金1両 銭4貫文 寛永17年 銭相場 (nothing: 1620-1650 SILENT); 元禄 宝永 銭相場 金一両 銭 貫文 推移; 文久 慶応 銭相場 金一両 銭 貫文 幕末 (no series beyond coin-walk, which covers 1692-1867).
- Silent goods: 江戸時代 魚 価格 一貫目 銀 匁 大坂 京都 物価 鰯 干鰯 小売 18世紀; 江戸時代 そば粉 小豆 価格 一石 銀 匁 大坂 物価 系列 (nothing). Rent: session 1's searches stand.
### New registry keys (10)
kumon-2022-gpih-japanese-wages, kimura-1987-gpih-osaka-prices, iwahashi-1981-gpih-rice-prices, jawiki-chogin, jawiki-koban, jawiki-nanryo-nishugin, jawiki-ichibu-gin, jawiki-genbun-chogin, jawiki-tenpo-chogin, coin-walk-edo-kahei-nenpyo.
### Checks run here, and owed for session 4
- source-reader, round 1, on all 14 owed keys (dispatched by hand with WAVE_OK: no Workflow tool in a headless session): every figure READ; the CONTRADICTED and NOT-FOUND findings were sentences that said more than the source (Kyoto salt ratio, a recoinage count, Kimura's fuel, Kumon's start years and city and "farm" servant, coin-walk's cities and coin labels and author, the nanryo article's sources) - all rewritten. Every passage the fixes ADDED (Mitsui A14, Edo E4, the 1840/1850 salt cells; Kumon G134, E136, M136-M137, L152, J213, D23/G23/J23; Kimura's fuel sheet B5-D6, J6; Tenpo's line-1 minting date) was quoted verbatim in the checker's own report. Recorded with make record-checked; nothing re-owed.
- Owed for session 4: quote-check, record-format and intro-check on 0286 and 0287; source-applicability on the ten keys (and the edited boj-imes-edo-ichiryo); translation-check on 0286 and 0287. For the spreadsheet quote-checks hand the cell dumps with EXTRA=: specs/412-money-basket-every-era/measure/{mitsui,kumon,kimura,iwahashi}_cells_by_address.txt, and for coin-walk measure/coin_walk_rows_raw.txt (its saved text flattens the table's columns).
- Sizes: 0286 about 14,400 bytes, 0287 about 14,300.
### Leads not followed
- The individual jawiki chogin pages for the Keicho, Genroku, Hoei, Shotoku, Bunsei and Ansei assays, and 五匁銀 (the ten-key cap); 0287 cites the prescribed fineness of all eleven from 丁銀 and assays for Genbun and Tenpo only.
- 『旧貨幣表』 and the 1875 Ministry of Finance tables themselves; 『日本史資料総覧』 (1986) itself, to learn whose rates coin-walk copies; Iwahashi 1981 p. 277 (his Osaka gold rates).
- A copper market rate for 1620-1650 (none found); Kumon's source for 1690s rice; coin-walk's single gold figures of 1708-1713 and 1717-1721, left unconverted because the coin is not named.
- Saito Osamu 1998 (Kyoto day wages 1773-1790) and Mitsui Bunko 1989 (Osaka tables 1781-1798, 河内木綿 a tan): print only, as session 1 said.
- Session 2, last: 0287 now carries an absence note for the 1620-1650 copper market (copper-early-absence) and, by pointer to 0277, Osaka's 1766 day (110 g a ryo, 26.2 g a kanmon, 66 mon a monme at Genbun's 1.725 g) and the 1842 reset to 6,500 mon a ryo; no cited passage moved.
