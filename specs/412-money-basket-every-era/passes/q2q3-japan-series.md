# Feature 412, questions 2 and 3 (Japan): price and wage SERIES per era - search pass, 2026-10-24

Not written to specs/412-money-basket-every-era/passes/ because this agent's contract is READ ONLY in every
repository; the dispatching session can file this text there.

## Sources found (series first)

### S1. Mitsui Bunko (1989), Tables 6-8, as transcribed by Bassino for GPIH: `Japan_1710-1871.xls`
URL: https://gpih.ucdavis.edu/files/Japan_1710-1871.xls (listed at https://gpih.ucdavis.edu/Datafilelist.htm as
"Japan 1710-1871 (Mitsui Bunko)"). Evidence: Mitsui house account books, Kyoto 1713, 1741-1762, 1791-1871; Edo
1710-11, 1713, 1716, 1818-1871; Osaka 1713, 1818-1871. Premodern record transcribed by moderns (counts).
This is the master multi-good series behind Bassino & Ma 2005 (their "Table 6" = Mitsui Kyoto table). Check
(derived): the 1745-54 means below, rice 71.9 monme/koku x 3.11 / 150 = 1.49 g/kg and lamp oil 328 x 3.11 / 180.9 =
5.64 g/L, match Bassino-Ma Table 3's printed 1.49 and 5.66.
How read: `make source-pages` refused the .xls/.xlsx files ("would not decode"); downloaded with curl and parsed with
xlrd/openpyxl. Originals: /tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/gpihjp/ ; text
dumps: /tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/dumps/ (mitsui_yearly.txt,
mitsui_eras.txt, kumon_eras.txt and one dump per file). The session must archive the served files itself.

Sheet "Sources and conversion", verbatim:
> "Mitsui Bunko, Tables 6, 7 and 8 (Retail prices in local physical units and daily wages of unskilled workers (hiyatoi) recorded by branches of Mitsui House in Kyoto, Edo (Tokyo) and Osaka; monetary unit: silver monme)"
> "Table 6: Retail prices and daily wages of unskilled workers in Kyoto, 1713, 1741-1762, 1791-1871"
> "Table 7: Retail prices and daily wages of unskilled workers in Edo (Tokyo),  1710-1711, 1713, 1716, 1818-1871"
> "Table 8: Retail prices in Osaka, 1713, 1818-1871"
> "Quarterly average (Spring and Autumn) ... yearly average proxied by calculating unweighted average of figures for Spring and Autumn"
> "1 koku of husked rice = 150 kg" ; "1 koku = 180.891 liters" ; "1 kan = 3.75 kg"
> "Unit price of 'mugi' in silver monme per koku is reported in Mitsui Bunko; mugi could be barley (mugi) or wheat (komugi). ... It is therefore assumed that 'mugi' is wheat"
> "Assumption used throughout this file: 1 silver monme = 3.75 grams pure silver" (the paper itself uses 3.11 g; the
> file's own note says "a slightly different assumption would to consider ... 3 to 3.2g per monme")

Goods and units (column headers, verbatim): 白米 1石ニ付 (white rice per koku), 麦 1石ニ付 (mugi/wheat per koku), 餅米
(glutinous rice), 塩 1石ニ付 (salt per koku, a VOLUME koku), 味噌 10貫匁ニ付 (miso per 10 kan = 37.5 kg), 醤油, 酢, 酒 1石ニ付
(sake per koku), 煎茶 1斤ニ付, 煙草 1斤ニ付, 炭 10貫匁ニ付 (charcoal, Edo and Osaka only), 薪 10貫匁ニ付 (firewood per 10 kan),
水油 1石ニ付 (lamp oil, rapeseed, per koku), 蝋燭 100匁ニ付, 日雇賃 1人ニ付 (day laborer per day; Kyoto and Edo only).
All in 銀匁 (silver monme). (Glosses in parentheses are translations.) The monme is Mitsui's bookkeeping unit in
all three cities: Edo's circulating money was ryo/bu/mon, so Edo cells 1818-1871 are account-monme, not Edo market
prices quoted in silver.
NOT in it: soybeans, other beans, buckwheat/millet, fish, cotton cloth, rent.

Representative yearly rows, verbatim cells (silver monme):
Kyoto (白米 | 麦 | 餅米 | 塩 | 味噌 | 醤油 | 酢 | 酒 | 煎茶 | 煙草 | 薪 | 水油 | 蝋燭 | 日雇賃):
- 1750: 77.05 | - | 87.09 | 15.04 | 15.4 | 94.48 | 34.05 | 115.4 | 0.895 | 1.775 | 2.595 | 354.7 | 4.425 | 1.15
- 1795: 79.67 | - | 95.41 | 6.2 | 18.42 | 77.28 | 56.07 | 118.8 | 1.06 | 2.03 | 2.82 | 329.4 | 1.685 | 0.885
- 1815: 81.62 | - | 87.37 | 6.145 | 17.21 | 69.66 | 46.51 | 119.9 | 1.22 | 1.79 | 2.75 | 244.9 | 1.475 | 1.055
- 1825: 78.58 | - | 105.9 | 6.72 | 19.29 | 71.24 | 42.07 | 117.6 | 1.195 | 1.79 | 2.815 | 271.4 | 1.32 | 1.01
- 1837: 178.5 | 179.1 | 131.1 | 8 | 34.67 | 83.4 | 44.86 | 242.5 | - | 1.805 | 2.775 | 399.3 | 1.76 | 0.97
- 1842: 86.12 | 64.92 | 88.91 | 7 | 24.88 | 73.98 | 35.03 | 113.6 | - | 1.88 | 3.105 | 387 | 2.375 | 1.08
- 1855: 90.75 | 66.51 | 112.1 | 5.5 | 30.09 | 79.43 | 43.56 | 135.5 | - | 1.84 | 3.165 | 410.4 | 2.18 | 1.12
- 1866: 933.5 | 791.1 | 1276 | 31.66 | 186.4 | 385 | 663.4 | 825.2 | - | 8.745 | 14.39 | 1426 | 7.87 | 1.32
- 1870: 640.8 | 463 | 727.5 | 38.4 | 131.2 | 478.7 | 676.3 | 661.4 | - | 8.7 | 10.66 | 1898 | 6.91 | 1.565
Edo (白米 | 麦 | 餅米 | 塩 | 味噌 | 醤油 | 酢 | 酒 | 煎茶 | 煙草 | 炭 | 薪 | 水油 | 蝋燭 | 日雇賃):
- 1820: 58.17 | - | 75 | 15.7 | 12.75 | 68.45 | 56.92 | 118 | 0.75 | 1.2 | 5 | 2 | 249.2 | 1.41 | 0.9
- 1830: 87.81 | - | 88 | 15.25 | 13.1 | 70.69 | 55.4 | 142.5 | 0.745 | 1.185 | 5.375 | 1.99 | 319 | 1.475 | 0.905
- 1840: 89.35 | - | 118.6 | 27.66 | 20.75 | 92.11 | 117.3 | 182.8 | 0.81 | 1.35 | 6.985 | 2.01 | 491.6 | 3.04 | 0.91
- 1855: 106 | - | 140 | 33.75 | 20.5 | 103.7 | 113.6 | 252 | 0.8 | 1.4 | 7.115 | 2.04 | 466.5 | 2.595 | 0.92
- 1866: 494.5 | 347.5 | 338 | 113 | 67.5 | 270.5 | 403.5 | 808 | 2 | 3.55 | 23.12 | 5.025 | 1040 | 3.775 | 1.35
- 1870: 558.6 | - | 676.3 | 189.6 | 87.53 | 565.7 | 659.4 | 989.5 | 3.44 | 4.25 | 24.26 | 4.63 | 1768 | 6.405 | 1.925
Osaka (白米 | 麦 | 餅米 | 塩 | 味噌 | 醤油 | 酢 | 酒 | 煎茶 | 煙草 | 炭 | 薪 | 水油 | 蝋燭; no wage):
- 1820: 57.85 | - | 76.1 | 17.5 | 15 | 77.5 | 50 | 127.5 | 1.1 | 1.8 | 3.525 | 3.825 | 294.6 | 1.67
- 1840: 80.05 | - | 103 | 40 | 20 | 120 | 75 | 155 | 1.15 | 1.8 | 4.2 | 4.25 | 466.5 | 2.53
- 1855: 89.65 | - | 119.5 | 25 | 22.5 | 95 | 80 | 140 | 1.1 | 2.5 | 3.9 | 4.75 | 417.5 | 2
- 1866: 1007 | - | 1012 | 180 | 101.5 | 422.5 | 285 | 700 | 3.425 | 5.75 | 21.15 | 19.65 | 1675 | 4.5

Era means I computed from the file's yearly cells (derived, unweighted; n years in parentheses), silver monme:
| era | city | rice /koku | mugi /koku | salt /koku(vol) | firewood /10 kan | charcoal /10 kan | lamp oil /koku | sake /koku | miso /10 kan | day wage |
|---|---|---|---|---|---|---|---|---|---|---|
| 1745-54 | Kyoto | 71.9 | - | 17.8 | 2.64 | - | 328 | 113 | 15.4 | 0.906 |
| 1791-99 | Kyoto | 83.0 | - | 6.12* | 2.79 | - | 312 | 127 | 18.3 | 0.85 |
| 1804-29 | Kyoto | 73.2 | - | 6.39* | 2.81 | - | 271 | 118 | 17.9 | 0.941 |
| 1818-29 | Edo | 71.4 | - | 15.2 | 1.95 | 5.02 | 284 | 128 | 12.9 | 0.901 |
| 1818-29 | Osaka | 72.7 | - | 17.4 | 3.69 | 3.43 | 285 | 131 | 15.5 | - |
| 1830-44 | Kyoto | 102 | 97.9 (10 yrs) | 7.01* | 2.89 | - | 351 | 149 | 25.2 | 0.982 |
| 1830-44 | Edo | 111 | 132 (3 yrs) | 23.9 | 1.99 | 6.42 | 405 | 190 | 17.7 | 0.906 |
| 1830-44 | Osaka | 106 | 106 (7 yrs) | 35.5 | 4.26 | 4.06 | 386 | 160 | 20.0 | - |
| 1850-59 | Kyoto | 115 | 89.2 | 6.22* | 3.25 | - | 409 | 155 | 28.5 | 1.04 |
| 1850-59 | Edo | 117 | 92.7 (4) | 35.7 | 2.08 | 7.33 | 461 | 255 | 21.0 | 0.918 |
| 1850-59 | Osaka | 113 | 109 (2) | 30.8 | 4.72 | 4.25 | 426 | 145 | 22.8 | - |
| 1860-67 | Kyoto | 394 | 370 (5) | 22.8 | 8.39 | - | 962 | 444 | 89.8 | 1.32 |
| 1860-67 | Edo | 261 | 223 (6) | 74.7 | 3.57 | 15.4 | 821 | 497 | 43.8 | 1.14 |
| 1860-67 | Osaka | 432 | - | 93.3 | 10.9 | 10.9 | 1100 | 339 | 54.8 | - |
| 1868-71 | Edo/Tokyo | 505 | 348 (2) | 144 | 4.66 | 23.9 | 1630 | 981 | 85.6 | 1.92 |
*Kyoto salt falls from 15-23 monme/koku (1741-62) to 4.5-8 from 1791 on, a third of Edo's and Osaka's in the same
years: probably a change of unit or grade in the Kyoto table, not a price; do not use Kyoto salt after 1791 without
checking the printed table. Edo's wage is a flat 0.9 monme 1818-1859 (an account-book standard rate, not a market
series; Bassino & Ma call the levels "broadly equal" to Kyoto's). The bakumatsu figures (1864-71) are monme of
account; silver monme ceased as money in 1868, so the 1868-71 cells are a conversion the Mitsui books made.
Reading: ATTESTED for rice, wheat, salt, firewood, charcoal, lamp oil (= Bassino-Ma's edible-oil proxy), sake, miso
and the unskilled day wage, Kyoto 1741-62 and 1791-1871, Edo and Osaka 1818-1871 (Osaka without a wage). Gap: no
Kyoto or Osaka series 1763-1790.

### S2. Bassino & Ma 2005, Appendix Table A.1 (archived: bassino-ma-2005, /diagram/.specify/source-archive/7c/7c5d60ee3cc3/20261018T232430Z/text.txt)
Evidence: Mitsui (1989) for 1741-1871; LTES for 1880-1913. Verbatim:
> "Table A.1. Daily Nominal Wages and Rice Prices in grams of Silver for 1741–1871 and 1880–1913."
> "Note: conversion units used: 1 silver monme ¼ 3.11 g of pure silver; 1 koku of rice ¼ 150 kg; 1 yen ¼ 25 g of pure silver; and 1 sho rice ¼ 1.425 kg. Sources: For 1741–1871, based on Mitsui (1989); for 1880–1913, based on Table 6 and LTES"
> "In the Mitsui Bunko records, there is also a nominal wage series for Tokyo (Edo) for 1818–1871. Although with a different trend, the levels for the Edo series are broadly equal to the Kyoto series."
Rows (Year, Daily Wages g, White Rice g/kg), verbatim: "1795 2.75 1.65"; "1815 3.28 1.69"; "1825 3.14 1.63";
"1837 3.02 3.70"; "1842 3.36 1.79"; "1855 3.48 1.88"; "1866 4.11 19.36"; "1867 4.26 18.49"; "1870 4.87 13.29";
"1880 5.25 1.99"; "1884 4.50 1.41"; "1886 3.75 1.44"; "1890 4.30 2.24". Years 1763-1790 and 1872-1879 absent.
Check: Kyoto 1795 wage 0.885 monme (S1) x 3.11 = 2.75 g, so the 1741-1871 wage column is S1's Kyoto 日雇賃 at 3.11 g
(the table's title "Kyoto-Edo" names no city per row). Further checks (derived): 1825 wage 3.14 = Kyoto 1.01 x 3.11
(Edo 0.9 would give 2.80); 1866 wage 4.11 = Kyoto 1.32 x 3.11 (Edo 4.20); 1870 wage 4.87 = Kyoto 1.565 x 3.11 (Edo
5.99); 1866 rice 19.36 g/kg = 934 monme/koku = Kyoto's 933.5 (Edo 494.5). So Table A.1 is KYOTO throughout 1741-1871,
despite its "Kyoto-Edo" title (0250 carries the ambiguity). Back to monme/koku: g/kg x 150 / 3.11 (derived).
Reading: ATTESTED (rice and wage only), as S1.

### S3. Kumon (2022) data file `Japanese Wages.xlsx`, GPIH
URL: https://gpih.ucdavis.edu/files/Japanese%20Wages.xlsx ("Japanese wages, prices, and living standards 1600-1938
(Kumon)"). Paper: Kumon, "The Labor-Intensive Path: Wages, Incomes, and the Work Year in Japan, 1610-1890", JEH 82.2
(2022); its 2020 draft read at https://www.cirje.e.u-tokyo.ac.jp/research/dp/2020/2020cf1154.pdf.
Evidence: male farm servants' contracts 1610-1890 (rural, all Japan, regression by half-decade); prices Osaka.
Verbatim, sheet "Sources & Notes":
> "wage/prices in silver monme up to 1867, then yen" (the Japan sheet's header still says "Prices in grams of silver"; the note governs: 1750 rice 0.4007 x 150 = 60 monme/koku = Iwahashi's Osaka 60.1)
> "Note: the tan unit is equal to an amount of cloth sufficient for one piece of clothing."
> "Prices are retail prices ... yellow highlight indicates years where there are no underlying data and it is imputed"
> Sources by good: rice "1600-1867 GPIH Jacks Osaka 1600-50, Iwahashi"; barley/wheat, soybeans "近世後期における主要物価の動態　三井文庫, 草野　近世の市場経済と地域差"; lamp oil, clothing "近世後期における主要物価の動態　三井文庫"; edible oil "... 三井文庫 osaka"; 1872-78 rice "米界資料 山崎繁次郎 編"; 1879- "LTES"
Draft paper, verbatim: "I add observed prices for barley, soy beans, edible oil, and linen to varying degrees for the period 1720-1880 ... However, the price of three goods remain unavailable (beans, fish, sake, and buckwheat) for the preceding periods so I follow the pre-industrial wage literature by fixing prices relative to rice prices using shares from the Meiji period."; "prices are only available in Osaka"; "As Osaka prices were in silver, I convert all wage payments in bronze or gold into silver using data from Murakami and Takahashi (1986)."
Columns: year of servant labor (excl. in-kind); rice, soybeans, other beans, barley, buckwheat, fish per kilo; edible
oil, sake, lamp oil per liter; linen per tan. I counted the yellow (imputed) cells: rice and wage are observed in
every decade 1610-1890; soybeans observed from the 1780s; barley partly from the 1720s; lamp oil from the 1740s;
edible oil and linen 1800s-1840s (and 1880s); beans, buckwheat, fish, sake imputed throughout before 1880.
Rows (wage monme/yr | rice monme/kg | soybeans | barley | edible oil /L | lamp oil /L | linen /tan; * = imputed):
- 1620: 55.07 | 0.1862 | 0.1862* | 0.1359* | 0.7445* | 0.7445* | 2.593*
- 1650: 75.31 | 0.26 | 0.2599* | 0.1898* | 1.04* | 1.04* | 3.621*
- 1786: 128.9 | 0.6507 | 0.5745 | 0.6736 | 2.045* | 2.045 | 5.677*
- 1792: 166.8 | 0.5607 | 0.4727 | 0.4251 | 1.743* | 1.743 | 7.015*
- 1820: 172.6 | 0.402 | 0.3163 | 0.2642 | 1.454 | 1.417 | 5.8
- 1842: 214.1 | 0.4833 | 0.4858 | 0.3811 | 1.863 | 2.139 | 8.8
- 1850: 259.6 | 0.9233 | 0.7781 | 0.6371 | 2.018 | 1.923 | 7.7
- 1862: 355.1 | 1.185 | 1.39 | 1.087 | 3.527 | 3.235 | 8.823*
- 1870 (yen): 9.92 | 0.06014 | 0.04823 | 0.0441* | 0.1504 | 0.1564 | 0.3763*
- 1884 (yen): 16.81 | 0.0536 | 0.03101 | 0.03471 | 0.08626 | 0.05132 | 0.39
Observed-only era means (derived): 1610s rice 0.131 monme/kg; 1620s 0.187; 1630s 0.250; 1640s 0.231; 1650s 0.269;
1660s 0.356; servant 55.07 monme/yr 1610-49, 75.31 1650-69 (flat within each span: benchmark levels, not yearly);
1780s rice 0.456, soy 0.466, barley 0.369, lamp oil 1.89/L, servant 139.7; 1790s rice 0.438, soy 0.451, barley
0.321, lamp oil 1.73, servant 172.8; 1804-29 rice 0.412, soy 0.386, barley 0.289, edible oil 1.44, lamp oil 1.50,
linen 6.12/tan, servant 189; 1830-44 rice 0.570, soy 0.562, barley 0.419, ed. oil 1.85, lamp 1.94, linen 7.17,
servant 201; 1850-59 rice 0.656, soy 0.674, ed. oil 2.36, lamp 2.26, servant 273; 1860-67 rice 2.69, soy 2.25,
ed. oil 6.35, lamp 5.32, servant 477; 1868-71 (yen) rice 0.050, soy 0.048, ed./lamp oil 0.165, servant 10.6 yen;
1880-89 (yen) rice 0.059, soy 0.040, beans 0.045, barley 0.033, ed. oil 0.116, lamp oil (kerosene) 0.062,
linen 0.445/tan, servant 16.81 yen.
Cloth caution: Kumon's observed "linen" 1804-49 is 6-8.8 monme per tan; Bassino-Ma's Table 3 cloth, 5.83 g/m
(Osaka 1840-49, Miyamoto 1963) x 10.6 m / 3.11 = about 19.9 monme per tan (derived), more than twice as dear.
Grade and unit unestablished; 0261 already notes the ~19 monme figure is "two to five times Ako's prices", and Kumon's
range sits inside 0261's Edo 1791 range (3-17.5 monme a tan).
How read: the PDF via curl + pdftotext (`make source-pages` reports no text layer); original at
/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/kumonpdf/k.pdf.
Reading: ATTESTED for rice (Osaka) every era and, from the 1780s, soybeans, barley, lamp and edible oil, cotton
cloth per tan; the wage is a farm servant's YEARLY cash wage excluding board, not a day wage. Early Edo: only rice
and the servant wage are observed; every other good is a Meiji ratio to rice.

### S4. Kimura (1987) via Jacks, GPIH `Osaka_1600-1650.xls`
URL: https://gpih.ucdavis.edu/files/Osaka_1600-1650.xls. Evidence: Osaka prices 1600-1650. Verbatim: "Main source:
Kimura, Masahiro. 1987. La Revolución de los precios en la cuenca del pacífico, 1600-1650." Units (verbatim
headers): "Rice per koku", "Soybeans per koku", "Soya per sho"; "Salt per to", "Oil per sho", "Sake per to",
"Vinegar per sho", "Tea per kin"; "Cloth, white per tan", "Cloth, cotton bleached per tan"; "Candles apiece";
"1 tan=10.6m x 34cm". "All prices in momme de plata."
Rows (silver monme): rice/koku 1610 14.89, 1620 27.93, 1630 24.43, 1640 33, 1645 30, 1650 39; soybeans/koku 1625 25,
1630 22.2, 1640 35, 1645 32; salt/to 1609 0.74, 1610 1, 1625 1, 1633 0.85, 1635 1, 1636 1.54, 1640 1; oil/sho 1610
2.8, 1620 2, 1630 2.2, 1635 2.9, 1639 4.4, 1647 1.9; sake/to 1620 3.3, 1630 3.32, 1640 -, 1647 6; white cloth/tan
1622 2, 1625 2.6, 1630 2.15, 1634 2.2; bleached cotton/tan 1610 16.5, 1621 13.5, 1634 8.5. No wage. "Oil" is not
named lamp or edible. Reading: ATTESTED ONLY FOR Osaka 1600-1650 (rice, soybeans, salt, oil, sake, cloth), through a
Spanish-language secondary work whose own sources were not seen.

### S5. Iwahashi (1981), Appendix Table 1, GPIH `Japan_rice_P_1620-1867.xls`
URL: https://gpih.ucdavis.edu/files/Japan_rice_P_1620-1867.xls. Verbatim: "Price of one Koku of Rice given in Ryo or
Monme (1 Ryo = 60 Monme)"; Saito's note: "1. Osaka: prices at Osaka's Dojima market, of rice produced in Higo";
"3. Banshu: rural prices from local sources"; "9. Edo: prices in Edo (present-day Tokyo) and environs"; "11. Nagoya:
prices from Nagoya han's documents"; "12. Shinshu: prices from Ina"; "others are likely ... to have reflected prices
set by han government authorities".
Rows (Osaka monme | Otsu monme | rural Banshu monme | Hiroshima monme | Edo ryo | Nagoya ryo | Shinshu ryo):
1620: -|-|-|20.1|-|-|-; 1640: -|-|-|34.4|-|-|-; 1655: -|-|-|36.1|0.69|0.7|-; 1660: -|-|-|58.2|1.4|1.33|-;
1785: 58.7|55.2|63.6|62.4|1.12|1.3|0.67; 1790: 52.4|45.7|57.4|57.9|0.97|1.08|0.59; 1810: 56.3|52.5|59.7|60.5|
0.88|0.9|0.68; 1825: 72.8|78.5|81.2|78.3|1.12|1.34|0.91; 1840: 60.6|59.7|67.1|71.9|1.17|1.36|0.69; 1855: 74.8|
70.4|80.4|78.2|1.86|1.29|1; 1865: 422.3|446|470.5|-|-|5|-. Osaka series starts 1701; Edo 1652; Hiroshima 1620.
Reading: ATTESTED for rice per koku, yearly, in 14 places; the only early-Edo rice series in the west is Hiroshima's
(a merchant's books), plus Edo in ryo from 1652. Village proxies: rural Banshu, Shinshu (Ina), Nagoya (beside Mino).

### S6. Saito 2003, Appendix table 1 note (archived: saito-2003-wages)
Verbatim: "In the base period of 1802-4, the mean money wage rate for spring tasks that Kami-Kawarabayashi
agricultural day labourers received was 1.0 monme and that for Kyoto day labourers 0.92 monme per person-day."
Edo/Tokyo and Choshi wages are indices only (1840-4=100). Reading: ATTESTED ONLY FOR one village day wage level
(1802-4, Settsu); already held in 0250.

### S7. Nagata village, Kazusa, 1842 official list (archived: oamishirasato-tenpo13-bukka) - already in 0262/0273
Verbatim: "百姓日雇　男　1人　女　1人　銭132文　銭100文"; "地　酒　1升　銭100文"; "白　米　100文につき　5勺下げ";
"水　油　2割下げ" (translation: farm day laborer, man, woman, 132 mon, 100 mon; local sake 1 sho 100 mon; white rice
"lowered by 5 shaku per 100 mon"; lamp oil "lowered 20%"). No rice, salt or oil LEVEL. Reading: ATTESTED ONLY FOR
the wage and sake.

### S8. BOJ IMES leaflet (archived, imes.boj.or.jp 1ryou.pdf)
Verbatim: "江戸の各時期に1両で買えた量をみると、目安としては江戸初期で約350kg、中〜後期で約150kg、幕末の1867（慶応3）年頃で約15〜30kg"
(translation: rice one ryo bought, as a rough guide: early Edo about 350 kg, mid-late about 150 kg, around 1867
about 15-30 kg); "江戸初期（1609年〜）1両＝銀50匁＝銭4,000文". Reading: ATTESTED as a rough guide only.

### S9. Japan 1885-1926, GPIH `Japan_1885-1926.xls` (Financial and Economic Annual of Japan)
URL: https://gpih.ucdavis.edu/files/Japan_1885-1926.xls. Wages, yen per day, verbatim row "1885 ... Day lab. (male)
0.159"; 1887 0.16. Prices 1887, yen: "Rice per koku 4.71", "Soybenas per koku 4.07", "Salt per koku 1.19",
"Charcoal per 10 kwan 0.29", "Cloth (cotton) per tan 0.31", "Wheat 3.89". National averages. Reading: ATTESTED for
late Meiji (1885-87), just past the era.

## Per era

1. Early Edo, Kyoto/Osaka 1610s-1660s: rice (S4 Osaka 1600-50; S5 Hiroshima 1620-, Edo 1652-; S3 Osaka-based
   decadal), soybeans, salt, oil, sake, cloth per tan for Osaka 1600-50 (S4, sparse years). Wage: only a farm
   servant's yearly 55.07 monme (1610-49) and 75.31 (1650-69), excl. board (S3). NO urban day wage found.
2. Osaka/Kyoto 1780s-1790s: Kyoto 1791-99 all S1 goods + day wage 0.85 monme (S1; 2.64 g S2 average); 1780s only
   via S3 (Osaka rice, soybeans, barley, lamp oil) and S5 (rice); no 1780s day wage (S1/S2 gap 1763-90).
3. Edo 1804-1830: Edo 1818-30 all S1 goods incl. charcoal + wage 0.90 monme; Kyoto 1804-29 all S1 goods + wage
   0.94; S3 adds soybeans, edible oil, cloth per tan (Osaka).
4. Tenpo 1830-44: S1 all three cities; wage Kyoto 0.98, Edo 0.906; S3 soybeans, oils, cloth.
5. Bakumatsu 1850-67: S1 all three cities, split 1850-59 / 1860-67 (prices x3-8 by 1866); wage Kyoto 1.04 -> 1.32,
   Edo 0.92 -> 1.14.
6. Villages: Kazusa Nagata 1842 wage 132 mon (S7); Kami-Kawarabayashi 1.0 monme 1802-4 (S6); farm servants' yearly
   wage every decade (S3); rice in rural Banshu, Shinshu-Ina, Nagoya (S5). Mino: nothing found.
7. Meiji Tokyo 1868-1880s: S1 Edo/Tokyo 1868-71 (monme of account) incl. wage 1.92 monme; S3 yen 1868-90 (rice,
   soybeans, beans, barley, edible oil, kerosene, cloth per tan); S2 wage 1880-90 in g silver (1880 5.25 g = 0.21 yen at
   25 g); S9 day laborer 0.159 yen 1885. 1872-79 day wage: none found.

## Basket goods observed in NO era before 1880 in anything read (SILENT)
- Fish, other beans, buckwheat/millets: imputed in Kumon from Meiji ratios to rice; not in Mitsui; Kimura has none.
- Rent of a back-tenement room: none of these series; 0265's Edo 1804-30 figure stands alone.
- Soybeans before 1780s: only Kimura's Osaka 1602-1648 (S4); none 1650-1780.
- Unskilled URBAN day wage before 1741: only Mitsui Edo 1710-1716 (S1, verbatim cells 日雇賃 1710 1.5, 1711 1.5,
  1713 2.1, 1716 2.4 monme, debased-coin years) - nothing for the 1610s-1660s.

## SILENT / not read
- 宮本又次 (ed.) 近世大阪の物価と利子 (1963), 三井文庫 近世後期における主要物価の動態 (1989, the printed source of
  S1, with Osaka Tables 1-5 incl. 1781-1798 and cotton cloth 河内木綿 per tan), 山崎隆三 近世物価史研究, 草野正裕
  近世の市場経済と地域差, 岩橋勝 (book): print only; no readable copy found (contents known from NDL reference entry
  crd.ndl.go.jp id=1000187424, archived).
- Bassino, Fukao & Takashima, Kyoto 1360-1860 (hermes-ir gd12-253.pdf): host does not resolve here (unreadable);
  medievalists.net page: abstract only.
- Japanese search for early-Edo Kyoto day wages (寛永 京都 日雇 賃銀): nothing bearing.

## Leads not followed
- Saito 1998 (賃金と労働と生活水準) Kyoto day-labourer series: Bassino-Ma A.2 has real wages from 1773, so nominal
  Kyoto wages for 1773-1790 exist in print (fills the 1780s wage gap).
- Mitsui Bunko 1989 Tables 1-5 (Osaka 1781-1798 commodities; 河内木綿 per tan): print only.
- Kimura 1987's own sources (likely 京都大学物価史研究会 15〜17世紀における物価変動の研究, 1962) for early-Edo wages.
- LTES vol. 8 (Ohkawa 1967) pp. 153-156 Tokyo retail prices 1868-1880s, and 米界資料 for 1872-78 rice.
