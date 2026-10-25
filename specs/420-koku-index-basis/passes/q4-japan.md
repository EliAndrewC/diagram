I filled several gaps for housing and salt and none for fish. Nothing in the repo was edited; the draft table is at /tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/q420-4-table.md.

Four things change the record's picture:
1. **Kyoto salt from 1791 is per bale, not per koku.** That settles the DOUBTFUL flag.
2. **Kumon's soybeans are Osaka's.** Bassino & Ma name Osaka, Mitsui Bunko table 3, from 1757.
3. **There are Edo and Osaka rent rates by the month for 1789-1846.**
4. **Some eras the JSON calls "rice alone" have Mitsui salt, firewood and charcoal for 1710-1716** already in 0286. The 1716 cotton in 0261 is from Yamato province, not a city.

## 1. Era x good, as the record stands

O = observed in that city and those years · O-Osaka = Kumon's Osaka soybeans, chained to another city · O-? = Kumon, no city named · R = reconstructed · B = borrowed · H = in the record but not used by the era · A = absent · **NEW** = found by this pass.

| era | soybeans | fish | cotton cloth | salt | fuel | housing |
|---|---|---|---|---|---|---|
| osaka-1620 | O (Kimura, 31.0 monme a koku; Osaka and Kyoto mixed) | A | H (Kimura: white 2.86 a tan, bleached cotton 10.0; left out because the grades differ 3x) | O (Kimura, 1.08 a to) | H, unusable units (pine by 9x9 cm, coal by the sack) | A |
| osaka-1695 | A | A | A | A | A | A |
| osaka-1700 | H (Kumon 1725, 0.36 a kg) | A | H (Kumon 1725-26, 4.2-4.3 a tan) | A | A | A |
| osaka-1706 | A | A | A | H (Mitsui Edo 1710-11, about 37-38 a koku) | H (Mitsui Edo 1710-11, firewood and charcoal) | A |
| osaka-1712 | A | A | H (1716 white cotton 14-15 a hiki, Yotsuho silver; **Yamato province**, 大和国庶民記録) | H (Mitsui Edo 1713/1716; Kyoto 1713, 29.33) | H (Mitsui firewood: Kyoto 3.82, Osaka 5.43 for 10 kan, 1713; charcoal Osaka 4.84; Edo 1716 Kumano charcoal 500 mon a bale) | A |
| osaka-1736 | A | A | A | A | A | A |
| osaka-1780 | O (Kumon/Mitsui Bunko Osaka, 0.466 a kg) | A | H (Ako 1781: 4-7 a tan; Ako 1790: 6-9; Nishinomiya 1790: 9-13; Kumon 1771-73: 4.9-5.3) | H (Kashimo village, Mino, 1763-74: 17-33 mon a sho) | A | A |
| kyoto-1745 | R (Bassino & Ma set it equal to rice); H (Kumon Osaka 1757-58) | R (ratio to rice) | B (Osaka 1840s, 5.83 g a m); H (Kumon 1757-59, 4.8-5.0 a tan) | O (Mitsui Kyoto, 17.8 a koku) | O (Mitsui Kyoto firewood, 2.64 for 10 kan) | B (Edo 1804-30, unsourced page) |
| kyoto-1790 | O-Osaka | A | A; H (Edo wholesalers 1791, 3-17.5 a tan); **NEW** Mitsui buying Hōki cotton at about 5 a tan | **NEW: O, 6.1 a bale** (also H: Edo brokers 1791) | O (firewood 2.79) | **NEW** (Edo, Kansei rents) |
| kyoto-1800 | O-Osaka | A | O-? (6.21 a tan, chained) | **NEW: O, 6.5 a bale** | O (firewood 2.81) | **NEW** (Osaka, 1814 rates) |
| edo-1818 | O-Osaka | A | O-? | O (15.2 a koku) | O (firewood 1.96, charcoal 5.02) | B (unsourced 300-500 mon page), though H: the Bunsei carpenter's 10 monme a month |
| edo-1830 | O-Osaka | A | O-? | O (23.9) | O (firewood 1.99, charcoal 6.42) | A → **NEW** (Edo 1840 rents) |
| edo-1850 | O-Osaka | A | O-? (7.85, 2 years) | O (35.7) | O (firewood 2.08, charcoal 7.33) | A → **NEW**, nearest only (Osaka 1846) |
| edo-1860 | O-Osaka | A | A (Kumon's one figure, 133 a tan in 1867, is an outlier) | O (82.2) | O (firewood 3.84, charcoal 16.9) | A |
| tokyo-1882 | O (LTES Tokyo retail, 0.97 g a kg) | R (wholesale salmon and cod ratio) | O (LTES Tokyo retail, 3.07 g a m) | A (nearest only, 1887) | A (nearest only, 1887) | A |

Sources for the cells in the archive:
- **Mitsui books:** GPIH `Japan_1710-1871.xls` (archived): "Table 6: … Kyoto, 1713, 1741-1762, 1791-1871 / Table 7: … Edo (Tokyo), 1710-1711, 1713, 1716, 1818-1871 / Table 8: Retail prices in Osaka, 1713, 1818-1871". It has no soybeans, cotton or fish. Kyoto has no charcoal column.
- **Kumon:** GPIH `Japanese Wages.xlsx`: "Prices are retail prices | yellow highlight indicates years where there are no underlying data and it is imputed". Every fish, buckwheat and sake cell is yellow in every year. Soybeans are observed in 1725, 1757-58, 1767, 1771-72, 1781-96 and 1802-71. Cloth is observed in 1725-26, 1757-59, 1766-68, 1771-73, 1802-51 and 1867.
- **Bassino & Ma 2005, Table 3 notes** (archived `gpih.ucdavis.edu/files/Bassino_Ma..pdf`):
  - "Data for prices of rice, soybeans, beans, edible oil, lamp oil (kerosene), and linen in 1882-86 are retail prices in Tokyo reported in LTES"
  - "we calculated the ratio of wholesale price of fish (salmon and cod) to wholesale price of rice in 1882-86 and multiplied this ratio to the retail price of rice"
  - "Prices of soybeans are available for Osaka in Mitsui Bunko from 1757 (table 3). … we just assume that the soybeans price in 1745-54 to be equal to rice prices."

## 2. New prices

The garbled text layers of Kusano, Tani and Washizaki Table 5 were read from the page images.

**a. Kyoto salt is priced per bale from 1791.** Kusano Masahiro, 『近世の市場経済と地域差』 (Kobe thesis, 1996): https://da.lib.kobe-u.ac.jp/da/kernel/D2002030/D2002030.pdf. The evidence is the printed Mitsui Bunko Kyoto table, 1713-1871.
- p.41: 「2）塩の価格は、1713（正徳3）年以降、1762（宝暦12）年春までは、1石ニ付銀匁の表示であるが、1791（寛政3）年以降、1俵ニ付銀匁の表示に変更されている。換算することも考えられるが、今回は、1762年春までのデータを除外した。」 (translation) "From 1713 to spring 1762 salt is shown in silver monme per koku, but from 1791 it is shown per bale. It could be converted, but here the data to spring 1762 were left out."
- Same page, for charcoal: 「6）堅炭の価格は、1741（寛保元）年以降、1762（宝暦12）年春までは、10貫匁ニ付銀匁の表示であるが、1791（寛政3）年以降は、1俵ニ付銀匁の表示に変更されている。」 (translation) "Hard charcoal is per 10 kan from 1741 to spring 1762, and per bale from 1791."
- p.31, on the older edition of the data: 「塩は1石につき銀匁で表示されるのが普通であるが、しばしば1俵につき銀匁で表示されている場合があり、これも1俵＝3斗2升として換算した。」 (translation) "Salt is usually in monme per koku, but is often per bale, and this too was converted at 1 bale = 3 to 2 sho."
- **Verdict: ATTESTED** that the unit is a bale. GPIH heads the column 1石ニ付 throughout, so its transcriber did not adjust.
- At Kusano's 0.32 koku a bale, 0286's Kyoto means become about 19 (1791-99), 20 (1800-17) and 22 (1830-44) monme a koku, beside Edo's 15-24. That is this pass's arithmetic.
- Three caveats:
  - The 3斗2升 is Kusano's own assumption ("として換算した").
  - For his own index he dropped data rather than convert across the break.
  - 0273's Edo brokers' Akō bales of 1791 (3斗5升 down to 3斗2升) support the bale size independently.

**b. Osaka rents, 1814 and 1846, per tatami a month.** 谷直樹「近世大坂の居住事情」 (1989), p.166: https://ocu-omu.repo.nii.ac.jp/record/2015149/files/111H0000001-37-14.pdf. The parallel question-3 pass fetched this page today, so dedupe.
- 「三井の借家の家賃は，嘉永年間のものを欠いているが，文化11年以降しばらくは表借家が1畳につき9分（空地は1坪につき9分）裏借家が7分（空地は1坪につき7分）になっている。また同じ三井の借家で弘化3年（1846）新築の南小幡町建家の「宿賃町入用差引見積額」によると，表借家は1畳につき9分（空地は1坪につき9分）裏借家が7分（空地は1坪につき5分）である。」 (translation) "Mitsui's rents lack the Kaei years, but from 1814 for some while a front house was 0.9 monme per tatami (open ground 0.9 per tsubo) and a back house 0.7 (open ground 0.7). In Mitsui's newly built houses of 1846 a front house is 0.9 per tatami and a back house 0.7 (open ground 0.5)."
- He also quotes 『所以者何』: 「家賃銀高下平均裏店にて半坪約七分位，表店九分位」 (translation) "rent on average about 0.7 monme per half tsubo for a back house, about 0.9 for a front."
- His worked example, 「合計406.14匁が1カ月の家賃収入」, shows the rates are by the month.
- City: Osaka (Mitsui's Kyōmachibori houses).
- **Verdict: ATTESTED** as landlord-side rates per tatami, not the rent of a stated dwelling. Use it for kyoto-1800 as the nearest city, and for the edo-1830 and edo-1850 eras only as another city's rate.

**c. Edo rents, Kansei period and 1840, monme a month.** Washizaki Shuntarō 2012 (archived, Kyushu `p095.pdf`), p.113 and Table 5. The evidence is Edo, Minami-Denmachō 1-2 chōme: Kansei period (1789-1801) and Tenpō 11 (1840).
- 「表5の列①と③は、各地面の表坪における月平均の地代を表している。寛政期のそれが南伝馬町1丁目：3.8〜4.0匁、同2丁目：3.8〜4.5匁の間で推移していたのに対して、天保期になると、それぞれ4.0〜4.5匁、4.0〜5.0匁に微増していた。他方、列②と④は裏坪における月平均の店賃を示しており、寛政期には1〜2丁目とも3匁台だったが、天保期には多くの地面で4匁台の金額を付けていた。」 (translation) "Columns 1 and 3 give the monthly mean ground rent on the front tsubo: in the Kansei period 3.8-4.0 monme in 1-chōme and 3.8-4.5 in 2-chōme, rising slightly in the Tenpō period to 4.0-4.5 and 4.0-5.0. Columns 2 and 4 give the monthly mean house rent on the back tsubo: in the 3-monme range in both chōme in the Kansei period, and in the 4-monme range on many lots in the Tenpō period."
- From the table:
  - Back-lot house rent: Kansei 3.3-3.8, Tenpō 11 3.7-5.0.
  - Front-lot ground rent: Kansei 3.8-4.5, Tenpō 11 4.0-5.5.
- The unit is printed as (匁／月) under the heads 表坪 and 裏坪. That it is per tsubo is implied by those heads, not stated.
- **Verdict: ATTESTED.** Kansei goes to kyoto-1790 (Edo, nearest city); 1840 goes to edo-1830 (Edo).

**d. The 1848 carpenter's rent is the same figure as the Bunsei one.** BOJ Kobayashi 2017 (archived, `cm_201703kinsei.pdf`) cites 『柳菴雑筆』 (1848): 「大工の給料は1日4匁2分、飯米料…1匁2分…房賃(家賃)120匁」 (translation) "a carpenter's pay 4.2 monme a day plus 1.2 for meals … rent 120 monme [a year]". That is 5.4 a day and 10 a month, the 文政年間漫録 figures 0265 already holds, so it is one observation, not two.

**e. 1887 prices from the GPIH Japan 1885-1926 file — nearest only.** https://gpih.ucdavis.edu/files/Japan_1885-1926.xls
- Source line: "The main source is Financial and Economic Annual of Japan; TOKYO: DEPT. OF FINANCE GPO".
- 1887 row, in yen: salt 1.19 a koku; soybeans 4.07 a koku; cotton cloth 0.31 a tan; charcoal 0.29 for 10 kwan.
- No city is stated, and 1887 is after tokyo-1882's years, so it fills no cell as observed.

## 3. Reading

**ATTESTED ONLY FOR** salt, fuel and housing in some eras; fish is **SILENT**.
- **Salt:** kyoto-1790 and kyoto-1800 now have Kyoto salt per bale (a). The koku figure depends on Kusano's bale size.
- **Housing:** edo-1830 has Edo rents of 1840, and kyoto-1790 has Edo rents of the Kansei period (c). kyoto-1800 has Osaka's 1814 rates (b). edo-1818 holds an observed rent it doesn't use. The Bunsei carpenter's 10 monme a month could replace the unsourced page.
- **Soybeans:** observed only in Osaka (Kumon, from 1757), so every Kyoto and Edo era borrows them. tokyo-1882 is the exception (LTES Tokyo).
- **Cloth:** observed in a named city only for tokyo-1882. Elsewhere it is Kumon's unnamed-city series, the 1791 Edo wholesalers, or country prices (Akō, Nishinomiya, Hōki).
- **Eras before 1710:** osaka-1695 and osaka-1736 stay rice-only; nothing near them was found.
- **Fish SILENT.** Every Kumon fish cell is imputed, and the Bassino & Ma fish figures are reconstructed.
  - Searched: archive terms 三井, 守貞, 岩橋, 三貨図彙, gpih, mitsui, kumon, 江戸物価, 物価事典 and 山崎隆三, with the hits grepped for 魚 and 鰯.
  - Queries: 「江戸時代 魚 値段 物価 鰯 一尾 文 天保」, 「近世 魚価 史料 鮮魚 塩魚 値段 匁 大坂 雑喉場 相場」, 「"鰯" 値段 江戸後期 "文"」, and an English Tokugawa fish price query.
  - Pages read: Ōishi 1966's 58 Edo price returns of 1842 have only kamaboko and fish oil. The Handa museum PDF's fish are a list supplied to the Owari lord.

**Ledger correction:** I recorded `unreadable` for `Japan_1885-1926.xls` because `make source-pages` could not decode it. I then read it with curl and xlrd, so that outcome needs correcting.

## 4. Leads not followed
- Fish for tokyo-1882: the wholesale salmon and cod prices of 1882-86 in Historical Statistics of Japan, CD-ROM tables 17-16 (cited by Bassino & Ma).
- Kyoto charcoal (堅炭, 和炭): in the printed Mitsui Bunko Kyoto table 1741-1871, left out by GPIH. Kusano's tables may print the values.
- Sano 1962's Edo-Tokyo rent series, named in Saito 1993 (archived), which calls it less reliable.
- 東京府統計書 for 1882-86 salt, fuel and rent. The Hitotsubashi yearbook tables begin in 1887 and their xlsx files would not download.
- 『我国商品相場統計表』: Tokyo prices 1830-79, named in Saito 1993.
- The Hōki cotton at about 5 monme a tan (Shimomukai, archived) is a country purchase price of about 1789-1808, not a city retail price.
- Matsue rents (920 mon a month front, 1826; 260 mon back, 1852) are a castle town, outside these eras' cities. Question 3 is covering them.

Sources:
- [Kusano 1996 thesis](https://da.lib.kobe-u.ac.jp/da/kernel/D2002030/D2002030.pdf)
- [Tani 1989](https://ocu-omu.repo.nii.ac.jp/record/2015149/files/111H0000001-37-14.pdf)
- [Washizaki 2012](https://api.lib.kyushu-u.ac.jp/opac_download_md/25880/p095.pdf)
- [BOJ Kobayashi 2017](https://www.imes.boj.or.jp/cm/research/kinken/mod/cm_201703kinsei.pdf)
- [GPIH Japan 1885-1926](https://gpih.ucdavis.edu/files/Japan_1885-1926.xls)
- [GPIH Japan 1710-1871](https://gpih.ucdavis.edu/files/Japan_1710-1871.xls)
- [GPIH Japanese Wages (Kumon)](https://gpih.ucdavis.edu/files/Japanese%20Wages.xlsx)
- [Bassino & Ma](https://gpih.ucdavis.edu/files/Bassino_Ma..pdf)
- [Shimomukai](https://mitsui-bunko.or.jp/archives/pdf_data/mbr-47_shimomukai.pdf)
- [Ōishi 1966](https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf)
- [Handa museum](https://www.city.handa.lg.jp/_res/projects/default_project/_page_/001/002/711/r1komonnjo.pdf)
- [Hitotsubashi yearbook table](https://d-repo.ier.hit-u.ac.jp/records/2009025)