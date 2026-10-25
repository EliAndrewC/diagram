I found new observed prices for **beijing-1820** (salt, fish, fuel, cloth and a house rent), **beijing-1615** (fish, from secondary sources) and **suzhou-1750** (cotton cloth). **beijing-1500** is still empty. Soybeans are observed only for songjiang-1680. Fish stays absent for 1736, 1900, songjiang-1680 and suzhou-1750.

The record holds more than the json's `confidence` and `goods_left_out` fields say. Observed prices already in the record but not in the json:
- 1615: cloth.
- 1736: cloth and salt.
- songjiang-1680: cloth and firewood.
- canton-1835: salted fish.
- beijing-1900: fuel and rent.

The json leaves these out because their units don't fit the basket, not because the record lacks them.

Labels: **OBS-official** is a government purchase or fixed price, **OBS-market** is a recorded shop or market price, **RECON** is the Allen et al. 2011 reconstruction, **ABSENT** means nothing found. **NEW** marks a price found in this pass.

## 1. Era x good

| era | soybeans / beans | fish | cotton cloth | salt | fuel | rent |
|---|---|---|---|---|---|---|
| beijing-1500 | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT |
| beijing-1615 | ABSENT | **NEW** OBS-market, but only through secondary sources: Beijing 1590s-1602, about 0.01-0.02 tael a jin | OBS-official: 0.094 tael a zhang (1615 handbook, Gao Shouxian's table 22) | OBS-official: 0.006-0.007 tael a jin (Wanli kuaiji lu and Wanshu zaji, via Gao) | OBS-official: firewood 0.125-0.35 tael and coal 0.1-0.12 tael per 100 jin (Gao) | ABSENT |
| beijing-1736 | bean flour OBS-official, 0.0135 tael a jin; whole beans RECON, 0.84 g of silver a kg | RECON only (Allen's "meat/fish", 2.04 g a kg) | OBS-official: coarse white 0.09 tael a zhang; blue biao cloth 9 cun wide 0.188 a zhang | OBS-official: 0.012 tael a jin | OBS-official: firewood 0.162-0.3, coal 0.26-0.27, charcoal 0.225-1.1 tael per 100 jin | OBS-official: rule of 1727, 0.05-0.2 tael a bay a month (Imperial Household houses) |
| beijing-1820 | RECON | **NEW** OBS-market (Timkovski, 1821) | **NEW** OBS-market (Timkovski) | **NEW** OBS-market (Timkovski); the record also has the Changlu fixed official price, 0.0104-0.0126 tael a jin from 1688 | **NEW** OBS-market (Timkovski) | OBS-market: Daoguang mutton shop, 2 shop rooms for 1 diao 600 wen a month; **NEW** a small house for 1,000 cash a month (Timkovski) |
| beijing-1900 | bean flour OBS-market: $5.16 (1900-09) and $5.68 (1910-19) per 100 catties (Meng and Gamble) | ABSENT | ABSENT | ABSENT (F. H. King's 1909 figure names no place) | OBS, per family per year only: $6 | OBS, per family per year only: $5-12, houses outside the city |
| canton-1835 | ABSENT | OBS-market: salted fish 0.05-0.16 tael a catty | ABSENT | OBS-market: 0.02-0.04 tael a catty | OBS-market: wood 0.1-0.18, charcoal 1.0, coal 0.24 tael a picul | OBS-market: $1.50 a month for 2 rooms |
| songjiang-1680 | OBS-market: 0.6-0.7 tael a shi (1682), about 1 (1684) | ABSENT (the whole 閱世編 text has 魚 only in idioms) | OBS-market: biao cloth about 0.2 tael a bolt, coarse 0.13-0.15 (1684); zhongji cloth 0.3 (1682) | OBS-market: 0.032 tael a jin (1683), 0.006-0.007 (1688) | OBS-market: 14-15 jin of firewood for 0.006-0.007 tael (1688) | ABSENT (only a 房租 of exam-hall rooms, with no price) |
| suzhou-1750 | ABSENT | ABSENT | **NEW** OBS (recollected, round figures): Changzhou, 30-40 cash a zhang about 1740s, 100-200 cash a zhang in 1793 | ABSENT | ABSENT | ABSENT |

## 2. New observed prices

**A. Timkovski, *Travels of the Russian Mission through Mongolia to China* (English edition 1827), vol. 2, pp. 199-204**
- Text: https://archive.org/download/travelsrussianm04klapgoog/travelsrussianm04klapgoog_djvu.txt. I checked the figures against the page images: https://archive.org/download/travelsrussianm04klapgoog/page/n212_w1400.jpg, n213 and n216.
- Place and date: Peking, 1821. Units are cash ("thsian") a kin unless marked.
- Verbatim:
  - Heading: "PRICES OF PROVISIONS AND VARIOUS OTHER ARTICLES AT PEKING, IN THE YEAR 1821. (Reckoning … the Chinese lan or liang at 8 rubles, or 1100 thsian, or pieces of Chinese copper coin.)"
  - Fish and salt (p. 200): "Frozen fish (sturgeon), per kin - 60 a 400"; "Sazans (a kind of carp), and other white fish, per kin - 50 a 60"; "Ditto, alive, ditto - 100 a 130"; "Salt, ditto - 20".
  - Fuel (p. 201): "Coals, ordinary, per kin - 4½"; "——, of the best quality, ditto - 6"; "Charcoal - 13 a 16"; "Wood (also sold by weight), per kin - 6". Wages on the same list: "A common workman - 130" (p. 202).
  - Cottons (p. 204), in liang: "Pou (in Russian Kitaika), per piece of 9 arsheens, undressed - 1⅓"; "——, dressed, the piece of 7 arsheens ⅗ a 7/10"; "Thsou pou, or Daba (ordinary Nankin), the best, per piece of 20 a 24 arsheens - 1 1/10 a 1⅗"; "Ta lian pou, or Dalenba, ½ arsheen broad, per piece of 15 arsheens - 1 3/10"; "Baika, white cotton, 13 arsheens - 1½"; "Raw cotton, the best quality, per kin - 250 thsian".
  - Coin note (p. 206): "500 are put on a string … A tiao ta thsian is a great string of 1000 pieces; a liang in silver is reckoned as 1100 tchek."
  - Rent (another page of the same volume, about p. 45): "He pays the rent of a thousand tchoki, or thsian, about eight francs a month". The tenant is a Manchu imperial guard in a small house beside the Russian church, and he also has to guard the church, so the rent may be below market.
- My arithmetic at his 1,100 cash a tael:
  - Salt: 0.018 tael a jin.
  - White fish: 0.045-0.055 tael a jin; live fish 0.09-0.12.
  - Ordinary coal: about 0.41 tael per 100 jin.
  - Wood: about 0.55 tael per 100 jin.
  - Cloth: the Dalenba cloth is 15 arsheens, about 10.7 m, by 35.6 cm wide, for 1.3 tael. That assumes an arsheen of 0.711 m, which is my figure, not his.
- Caveats:
  - The cottons column prints no unit. I read it as liang because the silk rows just above it say "liang" and the raw-cotton row says "thsian".
  - Whether his cash are the Beijing count (two counted as one) is not stated. His 1,100 sits near Allen's 1,159-1,203 for 1820-22.
- Verdict: **ATTESTED**, market prices for Peking in 1821, written down by a foreign visitor.

**B. 洪亮吉 Hong Liangji, 意言·生計篇** (essays usually dated 1793; that date is from my general knowledge, not the page)
- Source: https://zh.wikisource.org/zh/洪北江詩文集_(四部叢刊本)/甲集卷第一. Place: Yanghu, in Changzhou prefecture, next to Suzhou.
- Verbatim: 「聞五十年以前吾祖若父之時米之以升計者錢不過六七布之以丈計者錢不過三四十……今則不然……且昔之以升計者錢又須三四十矣昔之以丈計者錢又須一二百矣」
- (translation) "I have heard that fifty years ago, in my grandfather's and father's time, rice reckoned by the sheng cost no more than six or seven cash, and cloth reckoned by the zhang no more than thirty or forty cash … now it is otherwise … what was reckoned by the sheng now needs thirty or forty cash, and what was reckoned by the zhang now needs one or two hundred."
- My arithmetic: about 0.04-0.05 tael a zhang around the 1740s at about 800 cash a tael, and about 0.07-0.15 tael a zhang in the 1790s at 1,300-1,400. Kishimoto 1979 gives 0.043-0.057 and 0.071-0.15 tael a zhang, but her text layer is too garbled to quote.
- Verdict: **ATTESTED ONLY FOR** a recollected, rounded cash price in Changzhou, not Suzhou itself. The cloth grade is not stated.

**C. Beijing, 1590s-1602, fish (secondary sources only)**
- Brook, *The Price of Collapse*, Chinese excerpt: https://www.yicai.com/news/102960940.html
  - 「肉的標準價格是每斤2分……鮮魚或鹹魚的售價通常與肉類差不多。不過，在1602年的一封信中，耶穌會教士龐迪我曾寫道，在北京，1分白銀可以買到1斤鱒魚。」 (translation: "The standard price of meat was 2 fen a jin … fresh or salted fish usually sold at about the price of meat. But in a letter of 1602 the Jesuit Pantoja wrote that in Beijing 1 fen of silver bought a jin of trout.")
  - 1 qian buys 「1整條鯽魚」 ("a whole crucian carp").
  - This blends Hai Rui's Zhejiang prices with Shen Bang's Wanping (Beijing) prices.
- Yang Jintao, a popular article: https://m.huxiu.com/article/375586.html
  - 「《宛署雜記》中記錄說，豬肉每斤白銀0.02兩……5斤重大鯉魚0.1兩」 (translation: "the Wanshu zaji records pork at 0.02 tael a jin … a large carp of 5 jin at 0.1 tael").
  - That is 0.02 tael a jin, but secondhand and with no juan cited.
- Verdict: **ATTESTED ONLY FOR** secondary reports, about 0.01-0.02 tael a jin. Shen Bang's own text could not be read (see SILENT).

## 3. Reading

**ATTESTED ONLY FOR** some eras and goods:
- beijing-1820 moves from reconstruction-only to market-observed for salt, fish, fuel and cloth (by the piece), plus a house rent, all from Timkovski's 1821 list.
- suzhou-1750 gains one cloth price, recollected and from neighbouring Changzhou.
- beijing-1615 gains fish only through secondary sources.
- beijing-1500 stays **SILENT** for all six goods.

Still absent:
- Soybeans for every era except songjiang-1680. Timkovski lists no beans, and the 1736 list prices only bean flour.
- Fish for 1736, 1900, songjiang-1680 and suzhou-1750.
- Cloth for Canton and for 1900.
- Rent for songjiang-1680, suzhou-1750 and 1615.

Many cells are observed but official: all of 1615 and 1736. They should be weighted apart from market prices.

**What I searched:**
- The archive, for 宛署杂记 / 沈榜 / 阅世编 / 閱世編 / Meng and Gamble / GPIH / Chinese Repository / 彭信威 / Timkovski / 生計篇. The archived 閱世編 was grepped for 魚, 房租, 賃, 柴, 布 and 豆.
- The archived Gamble 1921 survey (budgets per family only).
- GPIH Beijing_prices_1900-1924.xls: grains and bean flour only, nothing else.
- Archived Chinese Repository vols 1, 4 and 10: no nankeen, bean or rent prices.

**SILENT / blocked:**
- 宛署雜記 itself: wikisource is a stub, and ctext returned only an anti-scraping notice, which I did not try to get around.
- Kishimoto (中山美緒) 1979, 「清代前期江南の物價動向」: the PDF has no readable text layer, and its .txt layer is scrambled vertical text.
- Timkovski vol. 2 copy TravelsoftheRussianmissionthroughMongoli10: Cyrillic OCR garbage.
- Web searches that found nothing usable: 乾隆 江南 棉布 每匹 价银; 乾隆 苏州 盐价 每斤; Canton nankeens prices current 1835; Brook Shen Bang prices; two 宛署杂记 price searches.

## 4. Leads not followed
- Kishimoto 1979, table 7 (Jiangnan cotton cloth prices, 17th-18th c.): needs the page images, https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/0dd66e9f-8bc7-4e41-b4a1-8922af2fe819/content
- Brook, *The Price of Collapse* (2023), its 15 tables of Shen Bang and Hai Rui prices: a print copy is needed.
- Pantoja's 1602 letter (Beijing prices), in Spanish.
- Canton Register / Canton Press "prices current" for nankeen cloth (wholesale), and Morse's *Chronicles*; British History Online, EIC Appendix B no. 26 (quantities only).
- 《兩浙鹽法志》 for a Suzhou-area salt price; 中國第一歷史檔案館 Qianlong salt memorials.
- Meng and Gamble 1926 in full (the GPIH file carries only grains); Gamble 1933 is out of era (1926-27).
- Academia Sinica Qing grain-price database (https://mhdb.mh.sinica.edu.tw/foodPrice/), for bean prices by prefecture: still not tried.

Sources:
- [Timkovski vol. 2 text](https://archive.org/download/travelsrussianm04klapgoog/travelsrussianm04klapgoog_djvu.txt) and [page image p. 200](https://archive.org/download/travelsrussianm04klapgoog/page/n212_w1400.jpg)
- [洪北江詩文集 甲集卷第一 (wikisource)](https://zh.wikisource.org/zh/洪北江詩文集_(四部叢刊本)/甲集卷第一)
- [Yicai, Brook excerpt](https://www.yicai.com/news/102960940.html)
- [Huxiu, Yang Jintao](https://m.huxiu.com/article/375586.html)
- [Kishimoto 1979 text layer](https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/7f68fc60-9af3-44cf-ad0f-f7013f9b3e4d/content)
- [GPIH Beijing prices](http://gpih.ucdavis.edu/files/Beijing_prices_1900-1924.xls)
- [ctext 宛署雜記](https://ctext.org/wiki.pl?if=gb&res=545777)