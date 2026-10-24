# Search pass: feature 412 (EliAndrewC/diagram#13) Q2, Q3, Q4, China

Pass run 2026-10-24. Read only: this file sits in the agent scratchpad, not in the clone. The parent asked for
specs/412-money-basket-every-era/passes/q2q3q4-china.md; the agent contract forbids writing into any repository, so move it there if wanted.

Cloth units: Allen's GPIH sheet prices cloth per square meter (6.14 g); the paper's Table 5 prints the same 6.14 against "3m"/"5m" of cloth, and its appendix gives 5.12 g/m2 for the 18th century. The basket wants linear metres of cloth about 36 cm wide, so convert by area. Of the Chinese cloth prices only Gao's 1736 蓝标布 states a width (9 cun); 白粗布, Ye Mengzhu's biao cloth and the 1615 cloth do not.
Units used below (taken from the sources, not new findings): tael (liang) = 10 mace (qian) = 100 candareens (fen) = 1000 li;
shi (picul, by volume) = 10 dou = 100 sheng; jin (catty) = 16 liang. Arithmetic marked "(this pass)" is mine. Everything else is quoted.

------------------------------------------------------------------------------------------------------------------
## A. Sources and passages
------------------------------------------------------------------------------------------------------------------

### A1. Allen, Bassino, Ma, Moll-Murata, van Zanden 2011, EHR 64 S1 (open copy https://eprints.lse.ac.uk/32403/1/Ma_Wages-prices-living-standards-China-1738-1925_2011.pdf; WP version archived, https://www.lse.ac.uk/asset-library/information/wp123.pdf)
Ledger: make source-pages said NOT-CHECKED (PDF, no text layer read by the tool); read through curl + pdftotext.

Tael (EHR p. 2 and n. 6): "Unminted silver measured in taels (one tael equalled 37 grams) was a universal medium of exchange in China in this period." n.: "The present study applies this average value; variation for the four most important units ranged between 36.54 and 37.58 grams. See Peng, Zhongguo huobi shi, p. 669, nn. 4–7."

Table 5, "Comparison of different basket costs around 1750", Beijing prices in grams of silver (verbatim rows):
  Oats/sorghum 0.48 | Bread 0.95 | Beans 0.84 | Meat/fish 2.04 | Eggs 0.074 | Beer/rice wine 1.98 | Oil/cooking 4 | Soap 1.65 |
  Linen/cotton 6.14 | Candles 3.3 | Lamp oil 3.3 | Fuel 11.2 (M BTU). "Total basket cost (grams of silver)" bare bones North China 182.6.
  Units: per kg, per liter for liquids, per meter of cloth, per million BTU.
Canton and Suzhou prices (EHR p. 18 / WP p. 20): "For the eighteenth century, Wang's Yangzi Delta rice price series was used for Suzhou and Chen's series for Guangdong. These are probably wholesale rather than retail prices. ... The prices of other foods and fuel were taken from the costs incurred by European trading companies in provisioning their ships in Canton."
Canton rice (EHR): "0.024 taels—roughly the cost of one kilogram of rice in Canton or millet in Beijing in the middle of the eighteenth century".
Wages (EHR): "From the VOC archives, 63 wage quotations spanning the eighteenth century can be obtained. The wages fluctuated, but they clustered between 0.08 and 0.1 taels per day with no additional food allowances." / "the wage level for Beijing and Canton was set in 1700, based on the predicted values in the regression of 0.0897 and 0.0835 taels respectively ... For Suzhou, 0.09 taels for 1700 were used, very close to the 0.0968 taels for the calenderers' wages."
Table 1 (regulated construction wages 1769-95, taels/day, unskilled / skilled): "Beijing* 0.077 0.141", "Tianjin/Baoding* 0.071 0.112", "Residual Zhili* 0.054 0.081", "Jiangsu** 0.040 0.051", "Guangdong 0.040 0.050".
Suzhou calenderers (WP App. I): "we converted the piece wage of 0.0113 taels (in 1730) and 0.013 taels (in 1772 and 1795) per bolt of cloth into 0.0994 and 0.1144 taels per day respectively."
Cash conversion: "these wages (mostly in copper cash) were converted to silver tael based on Vogel's exchanges rates" ... n. 14 "Vogel, 'Chinese central monetary policy' contains the most comprehensive collection of market exchange rates for various provinces in China for the seventeenth to nineteenth centuries. But these exchange rates do not apply to the case of the co-circulation of multiple versions of silver and copper cash within the same locality". 1870-1900 Beijing wages: "converted to silver wages using copper–silver rates from Peng (p. 548)".
Tiao / double count (EHR App.): "interpreting the value of one tiao, which usually contained 1,000 copper coins but could vary by region, is a major hurdle. Gamble remarked that one tiao in rural Beijing was equal to 500 copper cash before 1860 and 100 copper cash after 1860. In other words, the copper cash before 1860 circulated in that locality was only half of the value of the official cash. This seems to be corroborated by Yan et al.'s study ... the authors pointed out that the value of two copper cash was counted as one." / "Despite their footnote, Yan et al. derived their copper–silver series based on the standard rate of one tiao being equal to 1,000 cash. Our copper–silver exchange rate series in the second column is similarly derived ... the third column of table A1 is the silver wage converted from the first two volumes further divided by two."
Table A1 rows (cash wage / "Copper cash per silver tael" / silver wage taels): 1807 81 979 0.041; 1820 95 1,159 0.041; 1822 99 1,203 0.041; 1827 88 1,265 0.035; 1830 96 1,329 0.036; 1835 94 1,251 0.038; 1838 91 1,553 0.029; 1842 100 1,439 0.035; 1845 86 1,823 0.024; 1848 68 2,049 0.017; 1850 94 1,997 0.024; 1854 90 2,723 0.017; 1856 110 4,970 0.011; 1865 265 5,180 0.026; 1880 410 8,510 0.024; 1890 393 7,254 0.027; 1902 470 6,079 0.039.
Basket costs: "Using average prices for 1745–54, the 'bare bones' cost of maintaining a family was 22.59 taels".
Reading: ATTESTED ONLY FOR a modern reconstruction (see A2 for per-good provenance). Wages for 1738-1800 are regression levels, not observed series.

### A2. GPIH data file "China_1730-1933_Allen_et_al.xls" (http://gpih.ucdavis.edu/files/China_1730-1933_Allen_et_al.xls)
Ledger: NOT-CHECKED (binary); read by download + xlrd. Sheet "Beijing prices": "Beijing price data base (all prices in grams of silver)", per kg unless liters / sq m / million BTU.
Era means computed from its annual rows (this pass):
| good | 1738-69 | 1745-54 | 1820-29 | 1830-39 | 1900-09 | 1910-19 |
| rice ("lao mi") g/kg | 1.32 | 1.43 | 1.75 | 1.81 | 2.54 | 3.16 |
| wheat flour g/kg | 1.40 | 1.38 | 1.97 | 1.88 | 2.54 | 2.57 |
| millet g/kg | 1.07 | 1.04 | 1.47 | 1.53 | 1.98 | 2.19 |
| bean flour g/kg | 1.11 | 1.06 | 1.62 | 1.60 | 2.29 | 2.52 |
| beans g/kg | 0.89 | 0.84 | 1.30 | 1.29 | 1.98 | 2.37 |
| sorghum g/kg | 0.50 | 0.48 | 0.71 | 0.73 | 1.00 | 1.10 |
| meat g/kg | 2.07 | 2.04 | 2.90 | 2.77 | 4.64 | 5.73 |
| edible oil g/L | 4.07 | 4.01 | 5.71 | 5.44 | 7.62 | 8.58 |
| cloth g/m2 | 6.14 | 6.14 | 6.14 | 5.78 | 5.73 | 8.31 |
| lamp oil g/L | 3.36 | 3.31 | 4.71 | 4.49 | 6.08 | 6.91 |
| fuel g/M BTU | 11.20 | 11.20 | 9.48 | 9.85 | 11.75 | 10.14 |
Sheet "Figures2-6", silver wages of unskilled labourers, g/day, era means (this pass): Beijing 3.25 (1738-69), 2.82 (1820-29), 2.49 (1830-39), 6.55 (1900-09), 5.86 (1910-19); Suzhou 3.26 (1738-69), 6.04 (1910-19); Canton 3.02 (1738-69), 2.93 (1820s, 1 yr), 8.81 (1910-19).
Provenance (WP App. II, verbatim): "we applied Lillian Li's study of wholesale grain prices in Zhili province ... we could read off the prices of wheat, millet, sorghum from 1738 to 1908 ... These are five-year moving averages"; "for rice (lao mi, old or blackened rice), the price of rice in the Yangzi delta, based on the 1901-04 benchmark"; "for meat, edible oil, lamp oil, candles, the price of wheat flour was applied"; cloth "Pomeranz estimated the price of cloth in a low price scenario at 0.5 taels per bolt ... we assume that cloth prices remained constant over the eighteenth century"; fuel "For 1739-69, we used the data implied by charcoal prices in Zhili province in the 1769 Wuliao jiazhi zeli, and for 1816, the price implied by the price of coal in Beijing given by Timkovski ... the values for the missing years were interpolated."
Reading: ATTESTED ONLY FOR the Allen reconstruction. Its "Beijing rice" is the Yangzi series rescaled, not a Beijing price; meat, oils and candles are wheat-indexed back from 1902; cloth is one constant.

### A3. 高寿仙 Gao Shouxian 2022, 清代《九卿议定物料价值》的分类整理, Gugong xuekan (archived: https://www.dpm.org.cn/Uploads/File/2023/02/10/u63e60647c73ae.pdf, key gao-shouxian-jiuqing-wuliao). Beijing official purchase prices, 1736 list; Ming 1615 handbook beside it.
Table 1 (1736): 「白面每斤0.014；江米每石2.52；麸子每斗0.054；麦余每斤0.002；豆面每斤0.0135」「盐每斤0.012」「香油每斤0.044」 (translation: wheat flour 0.014 tael a jin; glutinous rice 2.52 a shi; bran 0.054 a dou; ...; bean flour 0.0135 a jin; salt 0.012 a jin; sesame oil 0.044 a jin).
Table 2 (1736): 「木柴每百斤0.162/0.3；硬木柴每百斤0.266」「煤每百斤0.26/0.27」 (translation: firewood 0.162/0.3 tael per 100 jin; hardwood firewood 0.266; coal 0.26/0.27 per 100 jin).
Table 4 (1736): 「白粗布每丈0.09」「蓝标布（宽9寸）每丈0.188」 (translation: coarse white cotton cloth 0.09 tael a zhang; blue biao cloth, 9 cun wide, 0.188 a zhang).
Table 22, Ming 1615 // Qing 1736: 「白面每斤0.008//0.014；江米每石1//2.52；香油每斤0.028//0.044；...盐每斤[0.006-0.007]//0.012」「木柴每百斤0.125-0.35//0.162-0.3；...煤每百斤[0.1-0.12]//0.26-0.27」「粗白棉布//白粗布每丈0.094//0.09」「桐油每斤0.03-0.036//0.05-0.06」「油烛//桕油烛每斤0.08-0.1//0.08」 (translation: wheat flour 0.008 tael a jin in 1615, 0.014 in 1736; glutinous rice 1 // 2.52 a shi; sesame oil 0.028 // 0.044 a jin; salt [0.006-0.007] // 0.012; firewood 0.125-0.35 // 0.162-0.3 per 100 jin; coal [0.1-0.12] // 0.26-0.27; coarse white cotton cloth 0.094 // 0.09 a zhang; tung oil 0.03-0.036 // 0.05-0.06 a jin; tallow candles 0.08-0.1 // 0.08 a jin). Bracketed = from Wanli kuaiji lu / Wanshu zaji.
Rates and wages: 「雍正九年（1731）户部议言：“五城十厂粜卖成色米所得钱文，发五城钱铺，照定价九百五十文兑换。” 这是官定比价」 (translation: 1731, Board of Revenue: cash from selling rice at the ten depots of the Five Wards is to be exchanged at the shops at the fixed price of 950 wen [a tael]; "this is an official rate"). 「乾隆二年（1737），户部会同提督衙门奏言：“见在京城，每纹银一两，换大制钱八百文，较之往时稍觉昂贵。”」 (translation: 1737, the Board with the gendarmerie memorialized: "now in the capital each tael of wen silver exchanges for 800 large standard cash, somewhat dearer than before"). Table 23: 「壮夫 每日长工给钱80文、短工60文 不论长、短给钱75文」 (translation: laborers, formerly 80 wen a long day and 60 a short; now 75 wen whatever the day); craftsmen 154. 「按照前述银1两兑钱800文的比例，154文折合白银0.1925两、75文折合白银0.09375两」.
Reading: ATTESTED (official purchase prices, not market prices; Beijing; 1736 and 1615).

### A4. 葉夢珠 Ye Mengzhu, 閱世編 卷七 (archived, https://zh.wikisource.org/wiki/閱世編). Songjiang (Lower Yangzi), evidence c.1620s-1690.
食貨一 rice: 「崇禎三年庚午，年荒穀貴……越二載，壬申夏，白米每斗價錢一百二十文，值銀一錢，民間便苦其貴……迨秋成，早米每石價錢止六百五、六十文耳。自是而後，米價大約每以千文錢內外為率。」 (translation: 1632 summer, white rice 120 wen a dou, worth 0.1 tael of silver, and people found it dear ... at autumn harvest early rice only 650-660 wen a shi; after that rice ran at about 1,000 wen a shi). 「時錢價日賤，每千值銀不過四錢幾分，白米每石紋銀五兩，計錢十二千有奇」 (translation: [1642] cash fell daily, 1,000 worth no more than 0.4-odd tael; white rice 5 taels of fine silver a shi, over 12,000 wen).
錢法: 「崇禎初……若京師每千價銀一兩二錢，外省猶兌九錢一千」 (translation: early Chongzhen [c.1628-30], in the capital 1,000 cash were priced at 1.2 taels, in the provinces still 0.9 tael for 1,000) ; 「馴至十三年戊寅夏，價至六錢耳……庚辰、辛巳之間，遞減至四、五錢一千。癸未而後，每千兌銀不過三錢有奇」 (translation: by summer [1638] down to 0.6 tael [per 1,000]; 1640-41 0.4-0.5 per 1,000; after 1643 no more than 0.3-odd). Early Qing: 「價定每千值銀一兩……價至每千兌銀九錢有奇，民間日用文作一厘，謂之厘錢」 (translation: [Kangxi] the price fixed at 1 tael per 1,000 ... it rose to 0.9-odd per 1,000, and people reckoned a wen as one li, calling it li-cash); 「十七、八年之間，每千價銀又兌至八錢七、八分及九錢二、三分」 (translation: Kangxi 17-18 [1678-79], 1,000 again fetched 0.87-0.88 and 0.92-0.93 tael); 「制錢每千價至紋銀一兩二、三分」 (translation: [1690] standard cash 1.02-1.03 tael of fine silver per 1,000).
食貨三 wheat (1682): 「圓麥三百五十文一石，準銀三錢一分五厘，小麥每石五百三十文，大麥每石二百五十文」 (translation: round wheat 350 wen a shi = 0.315 tael; wheat 530 wen; barley 250 wen).
食貨五 cloth (late Ming): 「上闊尖細者，曰標布……每疋約值銀一錢五六分，最精不過一錢七八分至二錢而止」 (translation: the wide, fine biao cloth ... about 0.15-0.16 tael a bolt, the finest no more than 0.17-0.2) ; small cloth 「闊不過尺餘，長不過十六尺……每疋在前值銀止六七分」 (translation: little more than 1 chi wide, at most 16 chi long ... formerly only 0.06-0.07 tael a bolt).
食貨二 soybeans: 「黃豆之價，常年較米稍減，大約豆一石可準米八、九斗」 (translation: soybeans usually a little cheaper than rice, about 1 shi of beans for 8-9 dou of rice).
Reading: ATTESTED (market prices, Songjiang, 1630s-1690; the rice-cash pair of 1632 gives 1,200 cash a tael, this pass).

### A5. 錢泳 Qian Yong, 履園叢話 卷一 (archived, https://zh.wikisource.org/wiki/履園叢話/01). Suzhou-Songjiang-Changzhou-Zhenjiang, 1707-c.1820s.
米價: 「雍正、乾隆初，米價每升十餘文。二十年蟲荒，四府相同，長至三十五六文……後連歲豐稔，價漸復舊，然每升亦祇十四五文為常價也。至五十年大旱，則每升至五十六七文。自此以後，不論荒熟，總在廿七八至三十四五文之間為常價矣。」 (translation: Yongzheng and early Qianlong, rice 10-odd wen a sheng; Qianlong 20 [1755] insect famine, up to 35-36; then good years, 14-15 wen the normal price; Qianlong 50 [1785] drought, 56-57; after that, famine or harvest, 27-28 to 34-35 wen is the normal price).
銀價: 「乾隆初年，每白銀一兩換大錢七百文，後漸增至七二、七四、七六至八十、八十四文。余少時每白銀一兩，亦不過換到大錢八九百文。嘉慶元年，銀價頓貴，每兩可換錢一千三四百文，後又漸減。近歲洋錢盛行，則銀錢俱賤矣。」 (translation: early Qianlong, a tael of white silver bought 700 large cash, rising gradually to 720, 740, 760, to 800 and 840. In my youth a tael still bought no more than 800-900 large cash. In Jiaqing 1 [1796] silver suddenly dear, 1,300-1,400 a tael, later falling back. In recent years foreign dollars are everywhere, and silver and cash are both cheap).
Reading: ATTESTED (memoir; Qian Yong was born 1759, so "my youth" is c.1760s-70s - that dating is mine). Mid-Qianlong rice 14-15 wen a sheng at 760-840 cash a tael is 1.7-2.0 taels a shi (this pass).

### A6. 王宏斌 Wang Hongbin, 清代社会动荡时期银钱比价变化规律之探析 (http://jds.cssn.cn/xscg/xslw/201605/t20160506_5253273.shtml), quoting memorials.
「（二）1746年（乾隆十一年），陕西巡抚陈弘谋奏报说：“陕西钱价向来每银一两易钱八百文以上，近则只易钱七百二三十文”……两年后，“西安省城每银一两止换钱六百十余文”」 (translation: 1746, Shaanxi governor: "a tael has always bought over 800 cash; lately only 720-730"; two years later, "in Xi'an a tael buys only 610-odd").
「（四）1771年……“因钱价昂贵，每两合制钱九百六十八文”……而在此两年前，每两银价尚在一千二百文左右」 (translation: 1771, flood work near the capital: "as cash is dear, a tael equals 968 standard cash"; two years earlier a tael was about 1,200).
「1803年（嘉庆八年），河南……“每银一两不过易钱七百二三十文”……按照水灾发生之前的银价（850文）」 (translation: 1803 Henan, after the breach a tael bought only 720-730; the rate before the flood, 850).
「（八）1841年8月，开封银价在水灾之前通常是一千六七百文」 (translation: Kaifeng, before the August 1841 flood, usually 1,600-1,700); 「（九）1846年……“每纹银一两可换制钱一千八百余文，迨至九十月间，每两仅换一千二三百文不等”」 (translation: Xi'an 1846, 1,800-odd standard cash a tael, falling to 1,200-1,300 in autumn); 1851 「此前，苏北每两银价在二千三四百文」 (translation: northern Jiangsu, before the breach, 2,300-2,400 a tael). Kangxi: 「到1684年（康熙二十二年）下跌至每两换钱850文」.
Reading: ATTESTED for these places and years. The "about 1,200" of 1769 near the capital sits against 800 (1737) and Qian Yong's 760-840, so it is another figure whose count (standard or doubled) is uncertain. The article's subject is disaster spikes, so several are abnormal; the "normal" rates stated beside them are the usable ones.

### A7. 清史稿 卷123 食貨四 鹽法 (archived, https://zh.wikisource.org/wiki/清史稿/卷123)
「雍正六年，巡鹽御史鄭禪寶疏稱「商課用銀，民間買鹽用錢。康熙時，銀一兩換制錢千四五百，每鹽一斤，錢十六文。今每兩合錢二千，而鹽價如故」」 (translation: 1728, the Changlu salt censor: "merchants pay tax in silver, people buy salt with cash. Under Kangxi a tael bought 1,400-1,500 standard cash and salt was 16 wen a jin; now a tael is 2,000 cash and the salt price is unchanged").
Reading: ATTESTED as written, but it collides with A3 (800 in Beijing, 1737), A4 (about 975-1,150 in Songjiang, 1678-90) and A5 (700 in Jiangnan, early Qianlong). Guess (not attested): the Changlu (Zhili) figure may be in the local count in which two cash were reckoned as one (see A9, A10), which would put it at 700-750 and 1,000 real standard cash.

### A8. 明史 卷81 食貨五 錢鈔 (https://zh.wikisource.org/wiki/明史/卷81; fetched this pass). Ming silver-copper rates.
Hongzhi: 「京衛軍秋糧取給焉，每七百當銀一兩」 (translation: the capital guards' autumn grain was paid from it, 700 [cash] to a tael). 1508: 「每七十文徵銀一錢」 (70 wen for 0.1 tael). 1525: 「錢七文折銀一分」 (7 cash for 0.01 tael). Jiajing: 「民間行濫惡錢，率以三四十錢當銀一分。後益雜鉛錫……至以六七十文當銀一分」 (translation: debased private cash at 30-40 to 0.01 tael, later 60-70); 「定嘉靖錢七文，洪武諸錢十文，前代錢三十文，當銀一分」 (translation: fixed: 7 Jiajing cash, 10 Hongwu-era cash, 30 cash of earlier dynasties, to 0.01 tael). Longqing: 「時錢八文折銀一分」 (8 cash to 0.01 tael). Wanli (some ten years after 1576): 「初鑄時，金背十文直銀一分，今萬曆金背五文，嘉靖金背四文，各直銀一分」 (translation: when first cast, 10 gold-back cash were worth 0.01 tael; now 5 Wanli gold-back, or 4 Jiajing gold-back, are each worth 0.01 tael); 「北錢視南錢昂值三之一」 (translation: northern cash valued a third higher than southern). 1628: 「其所鑄錢，皆以五十五文當銀一錢」 (translation: the cash they cast all at 55 wen to 0.1 tael).
Per tael (this pass): 700 (c.1500-1525), 700 Jiajing cash / 1,000 Hongwu / 3,000 older (1550s), 800 (Longqing), 1,000 then 500 (Wanli gold-back, 1576 to c.1586+), 550 (1628 official).
Reading: ATTESTED (mostly official or fixed rates; the market rates given are for debased cash).

### A9. Ziang Liu 2022, "Wages, Labour Market, and Living Standards in China, 1530-1840", LSE Economic History WP 339 (https://www.lse.ac.uk/Economic-History/Assets/Documents/WorkingPapers/Economic-History/2022/WP-339.pdf). Ledger NOT-CHECKED; read through curl + pdftotext.
「The most common standard was the so-called kuping weight, where one tael of silver equalled 36.9 grams in the sixteenth century, or 37.3 grams after the mid-seventeenth century.」 (citing Qiu, Zhongguo lidai duliangheng kao, pp. 419, 512). "grain tributes paid in cash adopted caoping weight, which was slightly lighter than kuping weight. For transit taxes and customs, guanping weight was applied, and it was slightly heavier".
"In the late-sixteenth century, the official exchange rate between silver tael and standard copper coin, zhiqian, was around 1:800 in Beijing due to the heavier weight of copper coins issued by mints in the capital. But in the Lower Yangzi delta, the official exchange rate was usually around 1:1200." (n. 28: Wang, Xuwenxian tongkao, vol. 18).
"the 'capital coin' (jingqian) was commonly circulated in North China, including Shandong province, North Zhili, and Beijing. It was traded at a ratio of 2:1 against the standard coin minted in Beijing. While in Northeast China (Manchuria), wages were commonly marked in 'eastern coin' (dongqian) or 'market coin' (shiqian), trading at a ratio of 6:1".
Table 8, unskilled daily wage, Lower Yangzi, silver taels (Liu, building): 1500-49 0.036; 1550-99 0.040; 1600-49 0.043; 1650-99 0.055; 1700-49 0.064; 1750-99 0.071; 1800-49 0.082 (Allen et al. beside it: 0.090, 0.088, 0.086, 0.085 for 1650-99 to 1800-49; Broadberry farming 0.040, 0.040, 0.045, 0.045). "my estimate of the day rate of an unskilled building labourer in 1760s Beijing (0.0789 taels)". n. 36: early-17th-c. Lower Yangzi mulberry-field hand "2.2 taels of silver per annum and food payments of 7.2 shi of rice (or 8 taels equivalent) ... 0.028 taels per day".
Silver-copper source: "Silver-copper coin exchange ratios ... see Lin, Yinxian, 76-77, Table 2.6. Noticing that Lin's exchange rates are more representative of northern and Beijing markets".
Reading: ATTESTED (modern estimates from archival wage records). The 7.2 shi = 8 taels pair gives about 1.1 taels a shi of rice, early 1600s (this pass).

### A10. Debin Ma 2012, "Money and monetary system in China in the 19th-20th century: an overview", LSE WP 159/12 (https://researchonline.lse.ac.uk/id/eprint/41940/1/WP159.pdf). Ledger NOT-CHECKED; read through curl.
"copper cash usually of 1000 pieces were strung together to form a unit of account often referred to as a tiao or chuan. But the tiao as a unit varied again by regions or trades. While the number of cash strung in each tiao usually ranged between 900 and 1000 in most places, they could be as low as 150 in some regions of the empire."
Quoting an 1889 Westerner via Kann 1927: "One hundred cash are not 100, and 1,000 cash are not 1,000, but some other and totally uncertain number, to be ascertained only by experience. In wide regions of the Empire 1 cash counts for 2, that is, it does so in numbers above 20, so that when one hears that he is to be paid 500 cash he understands that he will receive 250 pieces, less the local abatement".
"the value of silver trended upward, reaching by the mid-19th century above 2000 copper cash/tael (see Lin 2006)". "One tael or liang of silver was roughly equal to 37 grams of silver."
Reading: ATTESTED (the nominal-vs-actual count; no Beijing-specific series).

### A11. GPIH "China_wages_1807-1925.xls" and "Beijing_prices_1900-1924.xls" (http://gpih.ucdavis.edu/files/...). Ledger NOT-CHECKED; read by download + xlrd.
Urban Beijing wages (Meng and Gamble 1926, p. 100), "Daily Wages of Unskilled Construction Workers in Beijing 1900-1925", silver cents: 1900 23.6; 1905 23.6; 1909 19.4; 1910 19.1; 1913 22.4; 1916 22.6; 1919 21.8. Notes: "All wages include food allowance." "1 tael = 37 grams of silver, a silver dollar = 0.72 silver taels."
Rural Beijing sheet: "1807.0 | 81.0 | 979.0 | 0.083 | 3.071" (cash wage, cash per tael, taels, grams): NOT halved, unlike the paper's 0.041 for the same year (A1). The two readings of one series differ by a factor of two.
Canton: "Daily Wages of Unskilled construction workers in Canton, 1912-1927", dollars: 1912-14 0.275; 1915-16 0.3375; 1917-18 0.3625; 1919 0.4.
Beijing prices 1900-1924 (Meng and Gamble), "Local physical units and local currency", dollars per 100 catties. Notes: "NB: 1 tiao = 100 cash = 10 coppers; 1 dollar = c .72 taels"; "1 catty (jin) = 0.5 kg".
Decade means of the local-currency columns (this pass), $/100 catties: 1900-09 flour 5.73, wheat 3.82, bean flour 5.16, millet (retail) 4.46, corn flour 3.08; 1910-19 flour 5.78, wheat 4.30, rice 5.76 (1913-19 only), bean flour 5.68, millet 4.92, corn flour 3.56.
Two traps in this sheet: (1) its "grams of silver" columns use a US dollar at the world silver price (54-67 g per dollar, Notes sheet), not the Chinese dollar; the wage sheet's 0.72 tael x 37 g = 26.64 g is the consistent rate. (2) it takes a catty as 0.5 kg; Gamble 1921 (A12) gives 100 catties = 133 lb (about 60.3 kg). Rice 1913-19 is $5.76/100 catties, so $0.096/kg at Gamble's catty, about 2.5 g silver/kg at 26.64 g/$ (this pass); 3.07 g/kg at the sheet's 0.5 kg.
Reading: ATTESTED (retail market prices and guild wage series, Beijing 1900-1924).

### A12. Gamble, Peking: A Social Survey (1921) (https://archive.org/stream/pekingsocialsurv00gamb/pekingsocialsurv00gamb_djvu.txt). Evidence 1917-1919.
"The exchange shops ordinarily give from 136 to 140 coppers for a dollar. The old style Chinese cash are seldom used". "'Big money' is coppers and 10, 20 and 50 cent silver coins that pass as 1/100, 1/10, 1/5 and 1/2 of a dollar. 'Small money' is coppers, 10 and 20 cent silver pieces whose value, in terms of a dollar, is not fixed but fluctuates".
Rice: "allowed to purchase rice from their employers for $2.40 a picul (100 catties — 133 pounds), even though the market price of rice may be $10 or $12 a hundred catties."
Rent (poor families, Dittmer's study): "Rents average from $5 to $12 a year or from 5 to 15 percent of the family income. Even the best house costs only $15 a year. Fuel enough to keep the family from freezing costs $6 a year". "a family of five can live in comparative comfort according to the local standard on $100 per year (35 to 40 coppers a day)". Story-tellers: "100 coppers (72 cents) a day".
Wages (guild): "The painters receive 65 cents a day, board themselves ... The paper-hangers receive board and 57 cents a day in spring and fall, and 77 cents a day in summer and winter".
Reading: ATTESTED. The $10-12 market rice is about twice Meng and Gamble's 1917-19 rice ($5.35-6.00); the grade is probably different. Not resolved.

### A13. The Chinese Repository vol. 3 no. 10 (Feb. 1835), "Diet of the Chinese", pp. 457-471 (https://archive.org/stream/chineserepositor3101unse/chineserepositor3101unse_djvu.txt). Canton, 1834-35. OCR text; T.M.C.C. = taels, mace, candareens, cash.
Wages: "The wrages [sic, OCR] of a person in the fields, or in the workshop, generally, is one mace or about fourteen cents per day ; and the boatmen and others engag- ed on the river, receive still less. Those who are employed as por- ters and menials, are also paid, on an average, one mace per day."
Rent: "One containing two rooms, large enough to lodge five individuals can be procured for $1 50 per month. ... Not a few of the poorest people live in hovels or boats for which one dollar, and sometimes a half or fourth of that sum per month".
Prices: "The dollar bears about the same relation to the tael, as the catty does to the pound". Rows (OCR): "Rice, to 3. 0. 0. 0 per pecul." [lower bound lost in OCR]; "Salted fish, 5 can. to 0. 1. 6. 0" per catty; "Flour, (wheaten) 4 can. to 0. 0. G. 0 per catty" [G = 6]; "Salt . 2 can. to 0. 0. 4. 0 per catty"; "Wood, 1 ma. to 0. 1. 8. 0 per pecul"; "Charcoal, 1. 0. 0. 0" per pecul; "Fossil coal. 0. 2. 4. 0" per pecul; "Pork, 0. 1. 0. 0" per catty; "Eggs ... 0. 0. 0. 7 apiece".
In taels (this pass): rice up to 3 a picul; salted fish 0.05-0.16 a catty; wheat flour 0.04-0.06; salt 0.02-0.04 a catty; firewood 0.1-0.18 a picul; charcoal 1.0 a picul; coal 0.24 a picul; wage 0.1 tael a day (about $0.14, so $1 is about 0.72 tael).
Reading: ATTESTED (retail prices, Canton, 1835; the rice lower bound needs the page image).

### A14. GPIH "China_rice_prices_961-1910.xls" (Liu 2005 transcribing Peng Xinwei and Kishimoto). Ledger NOT-CHECKED; read by download.
Notes: "1 Ming tael = 36.9 grams of silver, and 1 Qing tael = 37.3 grams of silver." "One shi equaled 107.3 liters in the Ming dynasty, and 103.5 liters in the Qing" (Kang Chao). "For the Song era Liu uses 1 tael = 37.68 grams of silver."
Peng p. 459, Ming averages, taels per shi: "1522-1566 | 0.584"; "1567-1572 | 0.591"; "1573-1620 | 0.638"; "1621-1627 | 0.927"; "1628-1644 | 1.159".
Kishimoto Table 3.1, Suzhou area, taels per shi: 1584 0.35; 1585 0.32/0.25/0.33; 1588 1.8; 1589 1.6/1.8; 1608 1.2; 1620 1.4/1.8; 1624 1.4/1.5; 1625 1.2; 1627 1.5; 1748 3.0; 1751 3.1; 1755 3.1; 1756 3.6. These are scattered and mostly dearth years.
Song, Peng decadal via Liu pp. 160-162, grams of silver per hectoliter: 961-70 12.39; 1001-10 22.76; 1061-70 25.7; 1071-80 55.1; 1101-10 59.61; 1121-30 265.42; 1131-40 243.0; 1151-60 42.84; 1181-90 44.5; 1201-10 96.08; 1231-40 37.9; 1251-60 37.83.
Reading: ATTESTED ONLY FOR modern silver conversions. The Song quotes behind them were in copper cash, and the cash-silver rate Liu used is not in the sheet.

------------------------------------------------------------------------------------------------------------------
## B. Per era: what was found (Q2 goods, Q3 wage, Q4 coin)
------------------------------------------------------------------------------------------------------------------

Tael in grams (all eras): 37 g (Allen; 36.54-37.58 for the four main units, Peng p. 669); kuping 36.9 g (16th c.), 37.3 g (after mid-17th c.) (Liu / Qiu); Song 37.68 g (Liu). Fineness: NOT FOUND in a source read this pass. Kuping is a weight standard, and 紋銀 "wen silver", the usual sycee, was below full fineness. The 1737 memorial prices cash in 紋銀.

1. Qing Beijing / Zhili, 1736-1760s
 Q2: official 1736 list (A3): wheat flour 0.014 tael/jin, glutinous rice 2.52/shi, bean flour 0.0135/jin, sesame oil 0.044/jin, salt 0.012/jin, firewood 0.162-0.3/100 jin, coal 0.26-0.27/100 jin, coarse cotton cloth 0.09/zhang. Allen reconstruction (A1/A2) in g silver: sorghum 0.48/kg, beans 0.84, oil 4/L, lamp oil 3.3, cloth 6.14/m, fuel 11.2/M BTU (c.1750). No price for ordinary (non-glutinous) rice in Beijing except the Allen proxy: 江米 at 2.52 is glutinous rice, not the staple.
 Q3: 75 wen/day, official 1736 (A3), = 0.094 tael at 800; Allen regulated 1769 Beijing 0.077 tael, Zhili 0.054-0.071 (A1 T1); Liu 1760s Beijing 0.0789 (A9).
 Q4: Beijing 950 cash/tael official (1731), 800 market (1737) (A3); Zhili near capital 968 (1771), about 1,200 (1769) (A6). Collision: Changlu 1,400-1,500 (Kangxi) and 2,000 (1728), "制錢" (A7). jingqian counted 2:1 in north Zhili, Shandong, Beijing (A9).

2. Beijing 1820s
 Q2: only the Allen reconstruction (A2, 1820-29 means). Q3: rural Beijing fuel-store wage 95-99 wen (1820-22) (A1 T.A1); Allen's silver reading 0.041 tael (halved) vs the GPIH sheet's unhalved 0.083 (A11); Allen Beijing series 2.82 g/day. Q4: Table A1 col. 2: 1,159 (1820), 1,203 (1822), 1,208 (1824), 1,265 (1827), 1,294 (1829), 1,329 (1830) per tael. Allen read this as the count of 1,000 to the tiao. Gamble says the local tiao was 500 cash before 1860.

3. Lower Yangzi (Suzhou/Songjiang) 18th century
 Q2: rice 10-odd wen/sheng (1720s-30s), 14-15 (normal, after 1755), 27-35 (after 1785) (A5); Kishimoto Suzhou dearth years 3.0-3.6 tael/shi (A14); Allen uses Wang's series (not read). Q3: Allen Suzhou 0.09 (1700), calenderers 0.0994 (1730) and 0.1144 (1772) (A1); Liu 0.064 (1700-49), 0.071 (1750-99) (A9); Jiangsu regulated 0.040 (A1 T1). Q4: 700 cash/tael (early Qianlong) rising to 720-840, then 800-900 (c.1760s-70s), 1,300-1,400 (1796) (A5).
 Earlier Songjiang (1630s-90): rice 120 wen/dou = 0.1 tael (1632); wheat 350-530 wen/shi (1682); biao cotton cloth 0.15-0.2 tael/bolt (late Ming); cash about 1,080-1,150 per tael (1678-79) and about 975 (1690), i.e. 1,000 / (0.87-0.93) and 1,000 / 1.02-1.03 (this pass) (A4).

4. Canton 1830s
 Q2: Chinese Repository 1835 list (A13): rice up to 3 taels/picul, salt 0.02-0.04/catty, salted fish 0.05-0.16/catty, flour 0.04-0.06/catty, firewood 0.1-0.18/picul, charcoal 1.0/picul, coal 0.24/picul; 2-room house $1.50/month. 18th-c. Canton rice about 0.024 tael/kg (A1). Q3: 1 mace (0.1 tael), about 14 cents a day, 1835 (A13); VOC 0.08-0.1 tael (18th c.) (A1). Q4: dollar about 0.72 tael (A13 relation; A11 note). Canton cash/tael: NOT FOUND.

5. Beijing 1900-1919
 Q2: Meng and Gamble retail (A11), $/100 catties: flour 5.73/5.78, millet 4.46/4.92, corn flour 3.08/3.56, bean flour 5.16/5.68, rice 5.76 (1913-19); market rice $10-12 c.1919 (A12); rent $5-12/year (poor families) (A12). Q3: unskilled construction 19.1-27.2 silver cents/day with food (A11); painters 65 cents, paper-hangers 57-77 cents + board (A12). Q4: $1 = 0.72 tael (A11); 136-140 coppers/$ (A12); "1 tiao = 100 cash = 10 coppers" (A11 note). 1 tael = 37 g, so $1 = 26.64 g by that rule (A11).

6. Late Ming 1500s-1620s
 Q2: Beijing official 1615 (A3): wheat flour 0.008/jin, glutinous rice 1/shi, sesame oil 0.028/jin, salt 0.006-0.007/jin, firewood 0.125-0.35/100 jin, coal 0.1-0.12, coarse cotton cloth 0.094/zhang, tung oil 0.03-0.036/jin; rice Peng 0.584 (1522-66), 0.638 (1573-1620), 0.927 (1621-27) tael/shi; Suzhou 0.25-0.35 (1584-86), 1.2-1.8 (1608-27) (A14). Q3: Liu Lower Yangzi 0.036 (1500-49), 0.040 (1550-99), 0.043 (1600-49) (A9); 1615 handbook craftsmen/laborers 0.03-0.07 (record, 0279). Q4: Ming tael 36.9 g; 700/tael (1500-1525), 800 (Longqing), Wanli gold-back 1,000 then 500 (A8); official c.1580s-90s 800 Beijing vs 1,200 Lower Yangzi (A9); early Chongzhen 833 capital / 1,111 provinces, 1,200 Songjiang 1632, 1,667 (1638), 2,000-2,500 (1640-41), 3,000+ (1643) (A4).

7. Song
 Q2: rice only, as Peng's decadal series in modern grams of silver per hectoliter (A14). Q3: SILENT. Q4: Song tael 37.68 g (Liu, A14); Song cash-silver rate SILENT.

------------------------------------------------------------------------------------------------------------------
## C. SILENT / blocked
------------------------------------------------------------------------------------------------------------------
- Market cash per tael by decade as one series: no open copy found of 林滿紅 Lin Man-houng 銀線 Table 2.6 / China Upside Down, 彭信威 中國貨幣史 (pp. 608-615 tables), 嚴中平 統計資料選輯 Table 31 (Ningjin 1798-1850), Vogel 1987, or 陳昭南. Searches: 清代 銀錢比價 乾隆 每兩 制錢 歷年 表; 寧津 大柳鎮 銀錢比價; "China Upside Down" copper cash per tael table; 彭信威 "白银一两合制钱". Pages that did not bear: en.wikipedia Qing dynasty coinage (secondary; 700-1,200 range, 1896 official 2,200 vs market 1,600-1,700, kuping 37.5 g; not used as evidence); zh.wikipedia 京錢 (404, unreadable); ce.visuallibrary.net 265203.pdf (table of contents only, rejected).
- Wang Yeh-chien Suzhou rice series and 陳春聲 Guangdong rice: not read (IHP grain.html timed out; Academia Sinica Qing grain-price database https://mhdb.mh.sinica.edu.tw/foodPrice/ not tried).
- 全漢昇 北宋物價的變動 (IHP Bulletin 11; https://www1.ihp.sinica.edu.tw/storage/w2_file/4842RgUMcAJ.pdf): an image scan with no text layer, unreadable.
- iisg.nl/hpw/data.php: 403.
- Gamble 1943 "Daily Wages" pp. 44, 69 (tiao = 500 cash before 1860): paywalled; known only through Allen.
- Gamble 1933 How Chinese Families Live in Peiping: not searched (its evidence is 1926-27, after the era).
- Soybeans, buckwheat, other beans, fish and lamp oil as separate market prices: found only for Canton 1835 (fish) and in the Allen proxies.
