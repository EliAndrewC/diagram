I found Mitsui prices for miso and soy sauce in 8 of the 23 eras. Six eras have clean in-city rows: kyoto-1745, kyoto-1790, kyoto-1800, edo-1818, edo-1830 and edo-1850. Edo-1860 has in-city rows, but its mean hides a 2.5- to 3.5-fold rise. Osaka-1712 has a single Osaka soy sauce price from 1713, and osaka-1706 has only Edo rows. One more Japanese era, osaka-1620, has a column called "Soya" that is probably soy sauce but unconfirmed. No Chinese era prices soy sauce or 醬 in anything I could read. Tokyo-1882 has no figure inside its years; the nearest is 1887.

**Silver rate: please decide.** The request's 1.28 g a kg (miso) and 1.57 g a liter (soy sauce) for Kyoto 1745-54 were worked out at Bassino and Ma's 3.11 g of silver a monme. `money-conversions.json` prices kyoto-1745 at 1.725 g a monme (Genbun silver, source 0287). At that rate the same cells give **0.71 g a kg and 0.87 g a liter**. Below I give the monme figures first, then grams at the era file's rate, then grams at 3.11.

## 1. Sources and passages

**A. Mitsui Bunko (1989), Tables 6-8, in GPIH `Japan_1710-1871.xls`** (archive `d3/d31a02b796e1`; https://gpih.ucdavis.edu/files/Japan_1710-1871.xls). These are retail account-book prices, read here only from the half-yearly Spring and Fall cells.
- Headers, the same on all three sheets: column 7 「味噌」「10貫匁ニ付」「銀匁」 / "Miso" "10 kan" "Silver monme"; column 8 「醤油」「1石ニ付」「銀匁」 / "Soy sauce" "1 koku". (translation) Miso is priced per 10 kan of 1,000 monme weight, soy sauce per 1 koku, both in silver monme.
- What the sheets cover: 「Table 6: … Kyoto, 1713, 1741-1762, 1791-1871」「Table 7: … Edo (Tokyo), 1710-1711, 1713, 1716, 1818-1871」「Table 8: Retail prices in Osaka, 1713, 1818-1871」.
- Conversions are the file's own: 「1 kan = 3.75 kg」 and 「1 koku = 180.891 liters」. That makes 10 kan = 37.5 kg.
- Sample cells: Edo row 17, 1818 Spring: miso 13.0, soy sauce 69.0. Osaka row 11, 1818 Spring: miso 15.0, soy sauce 80.0. Kyoto row 55, 1791 Spring: miso 16.95, soy sauce 77.45.
- Caveat: Edo dealt in gold and copper coin, yet Table 7 is headed silver monme. The sheet does not say how Mitsui converted.

How each gram figure is worked out (my arithmetic):
- miso: monme per 10 kan × grams of silver per monme ÷ 37.5 kg
- soy sauce: monme per koku × grams of silver per monme ÷ 180.891 L

| Era (years) | Sheet and rows | n | Miso, monme per 10 kan: mean (range) | g/kg at era rate · at 3.11 | Soy sauce, monme per koku: mean (range) | g/L at era rate · at 3.11 |
|---|---|---|---|---|---|---|
| kyoto-1745 (1745-54) | Kyoto | 20 | 15.43 (12.2-18.54) | 0.71 · 1.28 (1.725 g) | 91.06 (82.63-98.22) | 0.87 · 1.57 |
| kyoto-1790 (sheet has 1791-99) | Kyoto | 18 | 18.34 (16.55-20.58) | 0.84 · 1.52 (1.725) | 76.77 (68.94-86.6) | 0.73 · 1.32 |
| kyoto-1800 (1800-17) | Kyoto | 36 | 17.11 (13.38-19.5) | 0.79 · 1.42 (1.725) | 68.94 (61.94-75.57) | 0.66 · 1.19 |
| edo-1818 (1818-29) | Edo | 22 | 12.86 (12.0-13.6) | 0.46 · 1.07 (1.35) | 68.89 (64.0-71.8) | 0.51 · 1.18 |
| edo-1830 (1830-44) | Edo | 30 | 17.70 (12.5-25.5) | 0.46 · 1.47 (0.975) | 87.03 (67.92-115.0) | 0.47 · 1.50 |
| edo-1850 (1850-59) | Edo | 20 | 21.00 (20.0-22.0) | 0.55 · 1.74 (0.975) | 105.70 (95.5-112.0) | 0.57 · 1.82 |
| edo-1860 (1860-67) | Edo | 13 | 47.15 (25.0-85.0) | 0.61 (range 0.33-1.11) (0.4875) | 213.64 (118-321) | 0.58 (range 0.32-0.87) |
| osaka-1712 (1712-18) | Osaka 1713 Fall | 1 | blank | — | 120.0 | 0.995 (1.5 g) |
| osaka-1712, other cities | Kyoto 1713 Fall; Edo 1713 Fall and 1716 Spring | 1 / 2 | Kyoto 31.74; Edo 19.26, 26.08 | Kyoto 1.27 (1.5 g) | Kyoto 123.1; Edo 135.06, 275.43 | Kyoto 1.02 |
| osaka-1706 (1706-11), Edo only | Edo 1710-11 | 4 | 12.30 (11.6-12.7) | 0.62 (1.875 g) | 104.38 (101.12-106.09) | 1.08 |

The silver rates are each era's own `units.monme.silver_g` in `money-conversions.json`, which cites 0287. Notes on the table:
- The era file prices edo-1818 at Bunsei silver although 1818-19 were Genbun, and edo-1830 at Tenpo silver although 1830-36 were Bunsei. One rate per era blurs those years.
- The Osaka sheet's 1818-1867 rows fall in no era gm-assistant holds; every Osaka era ends by 1789. As cross-checks in the Edo eras' years:
  - Osaka miso: 15.50, 19.97, 22.82, 61.15. Osaka soy sauce: 77.95, 98.67, 95.00 (flat), 283.85 (100-670).
  - Kyoto miso: 18.79, 25.21, 28.53, 100.32. Kyoto soy sauce: 71.05, 77.96, 81.99, 267.34.
- My script is `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/red.py`.

**B. Kimura 1987 in GPIH `Osaka_1600-1650.xls`** (archive `69/69fbb2a437a8`), sheet "starches". The headers read 「Soybeans」「per koku」 beside 「Soya」「per sho」, with 「All prices in momme de plata.」 (translation) prices in silver monme.
- Cells inside osaka-1620's 1620-1650: 1631 **0.5**, 1636 **0.9**, 1637 **0.9** monme a sho.
- The sheet's own grams-a-liter column, at 3.0 g a monme (which matches the era's Keicho 3.00 g), gives 0.83, 1.50, 1.50 g a liter, mean 1.28.
- Why I read it as soy sauce: it is priced by volume per sho, separately from "Soybeans" per koku. 0.5 monme a sho is 50 a koku, against soybeans at 26 a koku in 1631. The header does not say soy sauce, and Kimura's Spanish "soya" is ambiguous.
- The era file warns the series is "only some years … Osaka's and the rest chiefly Kyoto's".

**C. Jacks, GPIH `Japan_1885-1926.xls`** (archive `c0/c09b42e95639`), from the *Financial and Economic Annual of Japan*.
- Headers: 「Soybenas」 [sic] 「per koku」 and 「Soy 」「per koku」. Note: 「From 1917, salt per 100 kin; soy per 9 sho」.
- The first year is **1887: Soy 8.29 yen a koku** (Soybeans 4.07). At 25 g a yen and 180.39 L a koku (the sheet's own koku), that is **1.15 g a liter**.
- 1887 is after tokyo-1882's 1882-1886, and the file names no city before 1906. I could not confirm that a 9-sho barrel is a soy sauce barrel, so "Soy" as soy sauce is probable, not verified.

**D. Bassino & Ma 2005** (archived `reh_japanese_wages_bassino_and_ma.pdf`, lines 229-230): 「Soybeans are used as a proxy for various processed products: soybean paste (miso), soy sauce (shoyu), tofu, and fermented soybeans (natto).」 Its Table 3 (LTES, the 1882 source) prices neither miso nor soy sauce.

**E. China, all archived.** These show what the lists do price, and that soy sauce and 醬 are absent:
- **Timkovski, Peking 1821** (`88/88311ca5eebd`): 「Salt, ditto - 20」「Vinegar, a bottle - 11」「Mustard - 65」. The full list of provisions has no soy, 醬 or bean paste.
- **Gao Shouxian on 《九卿议定物料价值》** (Qing, presented 1736, compared with the Ming 《工部厂库须知》; dpm.org.cn PDF, archive `d7/d7234ae5c7ec`), 表1 副食品: 「鸡蛋每个0.001；蜂蜜每斤0.16；醋每斤0.009；盐每斤0.012；碱每斤0.02；花椒每斤0.08；香油每斤0.044」. (translation) eggs 0.001 tael each; honey 0.16 a jin; vinegar 0.009 a jin; salt 0.012 a jin; lye 0.02 a jin; Sichuan pepper 0.08 a jin; sesame oil 0.044 a jin. The only 酱 in the paper are 「酱色碗」 (brown-glazed bowls) and 「做酱模子每个0.072」 (a mold for making 醬, 0.072 each): a tool, not the food.
- **Chinese Repository vol. II (1834), Canton imports and exports** (`c9/c985642abacb`): 「Soy. This is a condiment made of a species of bean which grows in China and Japan. … It improves much by age.」 Neighbouring entries carry prices ("from $4 to $5 per pecul"); the soy entry has none.

## 2. Verdict

**ATTESTED ONLY FOR** the Mitsui Kyoto and Edo eras (kyoto-1745, kyoto-1790, kyoto-1800, edo-1818, edo-1830, edo-1850, edo-1860), as account-book retail prices.
- edo-1860's mean hides a 2.5- to 3.5-fold rise inside the era.
- osaka-1712 rests on one 1713 Osaka soy sauce cell (120 monme a koku); its miso cell is blank, and the only miso prices in those years are Kyoto's and Edo's.
- osaka-1706 has only Edo prices for 1710-11.
- osaka-1620's "Soya" (3 cells, 0.5-0.9 monme a sho) is probably soy sauce, with no miso.
- For tokyo-1882, the nearest is "Soy" in 1887 at 8.29 yen a koku, the year after the era. The era's own source (Bassino & Ma) prices neither good, so tokyo-1882 is SILENT inside its span.
- If the basket used each era's own coin rate, Kyoto-1745 would fall to 0.71 g a kg and 0.87 g a liter, and the other Kyoto and Edo eras sit at 0.46-0.84 g a kg and 0.42-0.73 g a liter.

**SILENT** for:
- osaka-1695, osaka-1700, osaka-1736, osaka-1780: no Mitsui rows in those years, and neither Kumon's `Japanese Wages.xlsx` nor the Osaka file has a miso or soy column.
- beijing-1500 (rice only), suzhou-1750 (rice only).
- beijing-1615, beijing-1736: Gao's lists; 醋 is priced, 醬 is not.
- beijing-1820: Allen et al.'s columns are bread, beer, flour, millet, rice, beans, sorghum, meat, wine, oil, soap, cloth, candles, lamp oil and fuel; Timkovski has vinegar and mustard only.
- beijing-1900: the Jacks/Meng-Gamble sheet has grains only; Gamble's *Peking: A Social Survey* text has only "salt vegetable" and "Oil, Wine, Vinegar Shops".
- canton-1835: soy described, not priced.
- songjiang-1680: the 閱世編 text (`6d/6ddbacd28ebf`) has 醬 only in 「宋式高大醬口素白碗」 (a style of bowl) and 鹽豉 only in an allusion (「有逾末下鹽豉」), not as prices.
- Qian Yong's 履園叢話/01: no 醬 or 豉.

What I searched:
- Archive terms: miso, 味噌, soy sauce, 醤油, 醬油, shoyu, 醬, 醤, jiang, bean paste, 豆豉.
- Web: 宛署雜記 醬; Meng & Gamble 1926 full text; 明治15年 東京 醤油 小売価格; 醤油樽 9升.
- Pages read: zh.wikisource 宛署雜記 (rejected: a stub pointing to ctext) and simplelits 宛署杂记 (unreadable: chapter files not reachable). Both are recorded on the ledger.

## 3. Leads not followed
- 宛署雜記 卷十四-十五 (經費) itself: the text is at ctext (res=598826, unreadable on 2026-10-22). I only saw its prices second-hand, through Gao's bracketed figures.
- Meng & Gamble, *Price, Wages, and the Standard of Living in Peking, 1900-1924* (1926): no digitised copy found. Jacks transcribed only its grains, and the original may price 醬油.
- An LTES vol. 8 (Prices) Tokyo retail soy sauce series for 1882-86, or 『値段の明治大正昭和風俗史』, for an in-span tokyo-1882 figure.
- Kimura 1987 itself, for what "Soya" translates (醤油 or 溜).
- Whether "soy per 9 sho" in the Jacks note is the soy sauce barrel.
- Canton prices-current tables in the *Canton Register* and Williams's *Chinese Commercial Guide*, which may price soy as an export by the pecul.

Sources:
- [GPIH Japan_1710-1871.xls](https://gpih.ucdavis.edu/files/Japan_1710-1871.xls)
- [GPIH Osaka_1600-1650.xls](https://gpih.ucdavis.edu/files/Osaka_1600-1650.xls)
- [GPIH Japan_1885-1926.xls](https://gpih.ucdavis.edu/files/Japan_1885-1926.xls)
- [GPIH Japanese Wages.xlsx](https://gpih.ucdavis.edu/files/Japanese%20Wages.xlsx)
- [GPIH China_1730-1933_Allen_et_al.xls](https://gpih.ucdavis.edu/files/China_1730-1933_Allen_et_al.xls)
- [GPIH Beijing_prices_1900-1924.xls](https://gpih.ucdavis.edu/files/Beijing_prices_1900-1924.xls)
- [Bassino & Ma 2005](https://www.econhistdbm.com/uploads/8/1/9/7/81977286/reh_japanese_wages_bassino_and_ma.pdf)
- [Timkovski vol. 2, djvu text](https://archive.org/download/travelsrussianm04klapgoog/travelsrussianm04klapgoog_djvu.txt)
- [Gao Shouxian, dpm.org.cn PDF](https://www.dpm.org.cn/Uploads/File/2023/02/10/u63e60647c73ae.pdf)
- [Chinese Repository vol. II text](https://archive.org/download/chinesereposito01willgoog/chinesereposito01willgoog_djvu.txt)
- [Chinese Repository vol. III text](https://archive.org/stream/chineserepositor3101unse/chineserepositor3101unse_djvu.txt)
- [Gamble, Peking Social Survey text](https://archive.org/stream/pekingsocialsurv00gambuoft/pekingsocialsurv00gambuoft_djvu.txt)
- [閱世編](https://zh.wikisource.org/wiki/閱世編)
- [履園叢話/01](https://zh.wikisource.org/wiki/履園叢話/01)
- [zh.wikisource 宛署雜記 (stub)](https://zh.wikisource.org/wiki/宛署雜記)
- [simplelits 宛署杂记](https://simplelits.com/books/classical/classical-04248-宛署杂记)
- [Duke Gamble research guide](https://guides.library.duke.edu/Gamblephotos/research)