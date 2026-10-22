# Pass 1 of 4 (feature 411): water freight costs, and how land carriage compared

**Verdict: ATTESTED for China, with figures for each mode. Japan is ATTESTED ONLY FOR an Osaka-area-to-Edo sake freight standard.** Archive search: most terms gave hits, but nothing in the archive gave a freight rate. 清史稿 卷123 (salt) has only salt-route costs, and 卷122 was not archived, so I fetched it fresh. Every record below is new; none duplicates what 0260 or 0278 already hold.

## Sources

### 1. 江蘇省《物料價值則例》 (official construction-material price regulations), Bochum database
- **Where:** the transport sheet https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/jiangsu/jiangsu_transport.xls and the wage sheet https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/jiangsu/jiangsu_wages.xls. Both are linked from https://www.oaw.ruhr-uni-bochum.de/gc/forschung/jiangsu_province.html.
- **How read:** `make source-pages` could not decode the binary .xls files and logged them as NOT-CHECKED. I downloaded them with curl and read them with xlrd.
- **Date:** the Bochum page gives no year of compilation. It cites Sheng Jun's 1940 study, titled 清乾隆朝江蘇省物價工資統計, and says his copy bore a Daoguang 10 (1830) imprint. The Naikaku Bunko copy the database uses has no imprint. So these are Qianlong-era regulations in an undated edition.
- **Nature:** these are official allowances for building materials, not merchant freight rates.

**Kunshan / Xinyang (蘇州府), chapter 2, folio 18:**
> 查原定成規內開一切竹木等料離城柒拾貳里，每價銀壹兩，給簰腳銀伍分，陸路挑運每百斤每里夫腳銀叄釐……至石料壹項，成規內開離城壹百里陸拾餘里船運每載萬塊每百里給腳銀壹兩貳錢，該處現送冊開每船裝載萬餘斤，其道路里數、水腳銀兩與成規相符。

(translation) The original regulations say: for all bamboo and timber, 72 li from the city, the raft fee is 0.05 tael for every tael of material value. Carrying overland costs a porter fee of 0.003 tael per 100 jin per li. For stone, shipped by boat from 160-odd li away, each load of 10,000 pieces gets 1.2 tael per 100 li. The register now submitted says each boat carries 10,000-odd jin, and the distances and water fees match the regulations.

**Zhenyang (太倉州), chapter 2, folio 43** (Chongming and Jiading/Baoshan say the same):
> 該處現送冊開石料買自蘇郡金、焦等山，計程壹百餘里，每船裝載萬斤，每里需銀壹分，磚瓦、灰斤等項於蘇郡采買，每船裝載萬斤，每里需銀陸釐。又開近工河下夫運木石磚瓦灰斤至工每百斤每里需銀叄釐

(translation) Stone is bought at Mount Jin, Mount Jiao and others in Suzhou prefecture, over 100 li away. Each boat carries 10,000 jin at 0.01 tael per li. Bricks, tiles and lime are bought in Suzhou, 10,000 jin a boat, at 0.006 tael per li. Porters carrying timber, stone, bricks and lime from the riverside to the site cost 0.003 tael per 100 jin per li.

**Wujin / Yanghu (常州府), chapter 4, folio 7:**
> 灰斤自宜興買運計程壹百餘里，每船裝運伍拾擔，擔水腳銀叄錢……自上河至縣市每百斤每里銀貳釐

(translation) Lime is bought at Yixing, over 100 li away, 50 dan a boat, at a water fee of 0.3 tael [per boatload]. From the landing to the county market, 0.002 tael per 100 jin per li.

**Songjiang counties (奉賢 and others):** bricks, tiles and lime from more than 100 li away, 10,000 jin a boat, 水腳銀捌錢 (water fee 0.8 tael).

**Two kinds of rate in the sheet.** The 每價銀壹兩給簰腳銀伍分 / 船腳銀叄分 rows charge a share of the goods' value (5% and 3%), not a rate per weight. They can't be converted to a cost per jin per li.

**Wage (same sheet set, every county):**
- Labourer 夫: 0.04 tael per 名 (per person). The sheet gives the unit as per person, not per day.
- Master artisan 匠: 0.05–0.06 tael per 工 (workday).
- Rammer 夯夫: 0.05.

### 2. 清史稿 卷122 食貨三 漕運 (the Qing grain-tribute chapter)
https://zh.wikisource.org/wiki/清史稿/卷122. The passages date from 1695 to about 1880, so each is dated separately.

**1695, river lighters (Tianjin to Jizhou):**
> 康熙三十四年……撥天津紅剝船百五十艘，運至薊州五里橋，船載百石，每百里給腳價一兩三錢二分

(translation) Kangxi 34 [1695]: 150 Tianjin red lighters carry [the grain] to Wuli bridge at Jizhou. Each boat carries 100 shi and is paid 1.32 tael per 100 li.

That works out to 0.0132 tael per shi per 100 li.

**1826, first sea shipment of tribute grain:**
> 計海運水程四千餘里，逾旬而至。

(translation) The sea route is over 4,000 li by water; [the fleet] arrived in a little over ten days.

This text gives no 1826 freight per shi; it gives only the distance.

**1868, sea freight (Shanghai to Tianjin):**
> 同治七年，議試用夾板船裝運採買米石，水腳銀數悉仍沙船例，給銀五錢五分，挽至天津紫竹林……所需小船剝價、棧租、挑力，每石給銀七分……又每石給保險銀三分

(translation) Tongzhi 7 [1868]: purchased rice was to be shipped on trial in clipper-built ships. The water fee follows the sand-junk (沙船) precedent exactly: 0.55 tael [per shi], delivered to Zizhulin at Tianjin. Lighterage, warehouse rent and porterage are 0.07 tael per shi, and insurance is another 0.03 tael per shi.

The 0.55 tael is explicitly the sand-junk rate.

**Early Guangxu (memorial of 黃元善), cost ceiling for sea transport:**
> 當時奏定江蘇漕額，以河運經費作為海運支銷，每石不得過七錢。嗣以經費不敷，迭次請增。江蘇所加，距一兩不遠，浙江已加至一兩

(translation) At the time it was decided that Jiangsu's tribute grain would pay for sea transport out of the canal-transport funds, at no more than 0.7 tael per shi. Since the funds proved too little, increases were requested again and again. Jiangsu's additions bring it close to 1 tael, and Zhejiang's have already reached 1 tael.

**Also in the chapter, flagged:**
- Tianjin lighters 「封河守凍期內……運米百石，給腳價八兩四錢」 (8.4 tael per 100 shi). The clause sits under the frozen-season heading and gives no distance.
- 同治十三年 [1874]: China Merchants steamers 「每石腳價銀二兩七錢」 (2.7 tael per shi). This is a steamer figure, not a junk one, and is out of line with 0.55.

### 3. Ruoran Cheng, "Transport cost in the Great Divergence: Yangtze China vs England", LSE Economic History Working Paper 371 (2024)
https://www.lse.ac.uk/asset-library/information/wp371.pdf. Read as a pdftotext copy in the session scratchpad. These are a modern historian's statements about late-17th-century to 18th-century practice.

> In early and mid-Qing China, waterway freight costs were about one-tenth of mule-pack-based land transport costs, consistent with Kiyokoba's (1996) estimation for Song China. … Waterway freight costs in the Grand Canal and upstream of the Xinjiang River were slightly higher compared to downstream trips along the Yangtze River.

> both England and the Yangtze Delta maintained a ratio of approximately 1:10 between water and land transport costs at the end of the seventeenth century … the cost of water transport in the Yangtze Delta was approximately 0.125 grams of silver per ton-mile, and the cost of land transport was 1.254 grams

On the 1890 Royal Asiatic Society survey (via Fan 1992 and Kingsmill 1898):
> When comparing the cost of transporting goods by junk from Kiangsu to Honan via the Grand Canal and Huai River with land freight costs, the ratios range from 1:10 to 1:25. In Kiangsu, the ratio can be as low as 1:37.5.

His tables (his own calculations, in tael per 100 kg per 100 km):
- **Table 5**, from the 大清會典 (DQHD), 1738–1776: primary river 0.015, secondary river 0.023, tertiary river upstream 0.043 / downstream 0.035, flat land 0.229, hill land 0.452.
- **Table 6**, late 17th century: flat land by mule 0.213, by wheeled vehicle 0.077, by labourer 1.594.

Wage: "the nominal wage for unskilled labor was 0.06 silver taels per day at the end of the 17th century" (citing Liu 2024). This pairs only with his 1680s figures.

### 4. 加藤慶一郎「樽廻船の加入形態に関する一考察」 (Kato Keiichiro on investment in sake ships), 流通科学大学論集 20-1 (2007)
https://ryuka.repo.nii.ac.jp/record/181/files/n20-1kato.pdf. `make source-pages` timed out on this URL. I read a copy another pass had downloaded today (/tmp/l7r-pass/pdf-kato/k.pdf).

> 毎回 40 駄の積み込みの約束がある。酒荷物の運賃がおよそ 10 駄につき銀 60 匁が基準であったから 8）、40 駄ならば銀 240 匁で大体計算が合う。

(translation) There is a promise to load 40 駄 each voyage. Since the standard freight for sake was about 60 monme of silver per 10 駄, 240 monme for 40 駄 roughly adds up.

Note 8:
> 柚木学『酒造りの歴史』（雄山閣、1988 年）272 頁。ただし、時期により変動があり、幕末に向かうにつれ上昇した（前掲書、272 頁、第 59 表）。

(translation) Yunoki Manabu, *Sakezukuri no rekishi*, p. 272. But the rate varied over time and rose toward the end of the shogunate (same book, p. 272, table 59).

- **Context:** a contract of 安政2 (1855) with a Nishinomiya sake-ship agent, for carriage to Edo.
- **Date of the standard:** late Edo; the year of the 60-monme base is not stated.
- **Missing:** the page gives no distance and no wage. I have not converted 駄 into casks because no source here does.

### 5. kotobank, 廻船 (cargo ships; 日本大百科全書, entry by 柚木学)
https://kotobank.jp/word/%E5%BB%BB%E8%88%B9-42600. Edo period.

> 廻船の経営形態については、運賃積みと買い積みとがあり、菱垣廻船、樽廻船、御城米積船などは前者を、北前船などは後者を代表した。

(translation) Cargo ships ran on two business models, carrying for freight and buying their own cargo. The Higaki and Taru ships and the shogunal rice ships represent the first; the kitamaebune and their like represent the second.

So the kitamaebune generally had no freight rate: they bought and sold their own cargo.

## Reading

**ATTESTED.** Results by mode:

- **River and canal, Qing China.** The Jiangsu regulations (Qianlong) give boat rates of 0.006–0.012 tael per 10,000 jin per li around Suzhou, Taicang, Changzhou and Songjiang. Porters at the landing in the same counties cost 0.002–0.003 tael per 100 jin per li, and a labourer earned 0.04 tael per person. Dividing one by the other (my arithmetic, not a figure the source states), porterage cost 25–50 times boat carriage:
  - Kunshan stone: about 25:1
  - Zhenyang stone: 30:1; bricks and lime: 50:1
  - Wujin lime: about 33:1
- **Tianjin river lighters, 1695:** 0.0132 tael per shi per 100 li.
- **Coastal junks:** the sand-junk precedent of 0.55 tael per shi from Shanghai to Tianjin is restated in 1868. The route is "over 4,000 li", a figure from the 1826 passage, so 0.55 ÷ 4,000 gives about 0.00014 tael per shi per li. That combines two dates. Later sea-transport costs were capped at 0.7 per shi and rose toward 1 tael.
- **The land-to-water ratio, as a historian states it:** Cheng puts water at about one-tenth of mule-pack carriage for the early-to-mid-Qing Yangtze region, and 1:10–1:37.5 for 1890. His own porter row against secondary rivers is about 75:1 (my division, not his statement). The project's porter figures in 0260 compare to that row, not to the 1:10.
- **Japan: ATTESTED ONLY FOR** a late-Edo standard of about 60 monme per 10 駄 of sake, Osaka-area to Edo, which rose toward the end of the shogunate. It comes with no distance and no wage.

**Searched and SILENT:**
- **No Edo land-to-water ratio statement.** Query: 江戸時代 舟運 陸運 運賃 比較 駄賃 何分の一 米 一俵 (second query, 江戸時代 船 馬 運賃 米 一石 …, also empty).
- **No Takasebune fare (Kyoto, Fushimi–Nijo).** Query: 高瀬舟 運賃 伏見 二条 一石 銀 江戸時代 角倉. Results were tourist pages without figures.
- **No Tone river boat fare.** Query: 利根川 高瀬船 運賃 米 一俵 銀 文 河岸 江戸 史料 運賃表.
- **No Higaki-ship fare per 駄.** Query: 菱垣廻船 運賃 大坂 江戸 一駄 銀 匁 研究.
- **No 1826 per-shi sea freight.** Query: 道光六年 海運 漕糧 每石 水腳銀 沙船 上海 天津.
- **No figures from Perkins, Rawski, Pomeranz or Skinner.** Searched by name; no verbatim passage found online.
- **No Grand Canal merchant (non-tribute) freight.**
- **No Ming figures.** I searched no Ming-specific terms.

**Pages that did not bear:**
- Kuse Hirohito, Kaiyodai osaka3.pdf: history of the Osaka–Edo route, no 運賃 in the text (recorded nothing-found).
- refubium.fu-berlin.de handle: timed out (recorded unreadable).
- Bochum `databases.html` and the Zhejiang, Guangdong and Shandong province pages: HTTP 404 (recorded unreadable).
- Bochum Hunan page: already read for 0260 (recorded nothing-found).
- Archive copies of kotobank 水運, gakken 灘酒, eonet, and the 清史稿 卷123 salt chapter: no freight rate.

## Leads not followed
- 柚木学『酒造りの歴史』p. 272, table 59: the actual series of Taru-ship freight rates over time.
- Cheng's Table A6: the raw 大清會典 rows for 1738–1776, which would give a verbatim 會典 passage. The archived 欽定大清會典則例 卷130 may be related.
- 魏源《籌漕篇》 and 陶澍's sea-transport memorials, for the 1826 water fee per shi.
- Nanny Kim, *Mountain Rivers, Mountain Roads* (Brill 2020): not open access.
- The Kansai University bibliography on Qing inland navigation (kansai-u.repo.nii.ac.jp, record 13020).

Sources:
- [Bochum Jiangsu page](https://www.oaw.ruhr-uni-bochum.de/gc/forschung/jiangsu_province.html)
- [jiangsu_transport.xls](https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/jiangsu/jiangsu_transport.xls)
- [jiangsu_wages.xls](https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/jiangsu/jiangsu_wages.xls)
- [清史稿 卷122](https://zh.wikisource.org/wiki/清史稿/卷122)
- [Cheng, LSE WP 371](https://www.lse.ac.uk/asset-library/information/wp371.pdf)
- [Kato 2007](https://ryuka.repo.nii.ac.jp/record/181/files/n20-1kato.pdf)
- [kotobank 廻船](https://kotobank.jp/word/%E5%BB%BB%E8%88%B9-42600)
