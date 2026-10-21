# Pass, group 4 (porterage), 2026-10-21

I found good Qing rates for stone by cart and for porters, but nothing yet on Edo-period Japan for either cart hire or porterage into the mountains.

| Item | Verdict |
|---|---|
| Japan (a) hired cart near a road | **SILENT** for the Edo period. The only rate found is from Kyoto in 1390 |
| Japan (b) porters into the mountains | **SILENT** |
| Qing (a) stone by cart | **ATTESTED** (Yunnan and Gansu 1769, Peking regulations) |
| Qing (b) porters into the mountains | **ATTESTED ONLY FOR** timber and for unnamed loads. The Gansu regulations refuse to set a separate porter rate for stone |

**Ledger notes**
- The four Bochum .xls files could not go through `make source-pages` ("would not decode"). I downloaded them with curl, so they still need a ledger entry. Copies are in `/tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/xls/`. Their province pages are on the ledger: `.../gc/forschung/yunnan_province.html` and `.../gansu_province.html`.
- No rate below has been scaled. Each keeps its own load unit (jin per cart, jin per li, tael), so you can convert to 400 kg.
- 1 jin ≈ 0.6 kg.

## Sources

**1. Wuliao jiazhi zeli 物料價值則例, Yunnan edition (1769). Bochum database**
- File: `https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/yunnan/yunnan_transport_costs.xls`. Wages are in `.../yunnan/yunnan_wages.xls`.
- Each row's remark reads: 「此款係原定成規。今照旧開載。嗣後修建工程，將物料觔重、道路里數於估銷冊內分晰登明。」 (translation: "This item is the established rule; it is listed as before. In future building work, record the weight of materials and the road distance in li in the estimate-and-accounts register.")

| Place (卷/folio) | Mode, as the row gives it | Load (jin) | Tael per li | Craftsman wage (匠/工) | Laborer wage (夫/名) |
|---|---|---|---|---|---|
| 曲靖府 南寧縣 等 (6/4) | 牛車運石料 (oxcart, stone) | 100 | 0.001 | 0.06 | 0.04 |
| same places | 木植夫運 (porter, timber) | 100 | 0.0013 | 0.06 | 0.04 |
| 臨安府 建水州 (3/4) | 牛車運石料 (oxcart, stone) | 100 | 0.001 | 0.07 | 0.05 |
| 臨安府 建水州 (3/4) | 木石灰觔 (timber, stone, lime; no mode given) | 100 | 0.0015 | 0.07 | 0.05 |
| 顺寧府 (5/24) | 挑運 (one man, carrying pole) | 100 | 0.0017 | 0.07 | 0.05 |
| 顺寧府 (5/24) | 抬運 (carried by two or more) | 100 | 0.0021 | 0.07 | 0.05 |
| 永北府 (9/16) | 夫運 (porter, material not named) | 100 | 0.0025 | 0.06 | 0.04 |
| 麗江府 (7/32) | 夫運 (porter, material not named) | 80 | 0.0012 | 0.06 | 0.04 |

- The 昆明 rows (65–80 jin, 0.001 tael per li) give no mode or material, so I am not reading them as porterage.

**2. Wuliao jiazhi zeli, Gansu edition (1769). Bochum database**
- File: `https://www.oaw.ruhr-uni-bochum.de/mam/gc/content/db/gansu/database_of_transport_cost.xls`. Wages are in `.../gansu/database_of_wages.xls`.

*Stone by cart:*
- 甘州府 撫彛廳 (7/20): 石料, 600 jin per cart, 0.01 tael per cart per li. Wages: 匠 0.06, 夫 0.05.
- 直隷肅州 (7/27): the same, at 0.012. Wages: 匠 0.06, 夫 0.05.
- 高臺縣 (7/34): 0.01.
- 安西府 玉門縣 (8/30), which defines the cart load: 「石料、石灰每陸百斤裝車壹輛，俱每車每里腳銀壹分叁釐捌毫，核於乾隆貳拾伍年准銷原案每壹百叁拾斤每里銀壹釐玖毫陸絲之價浮多，今照原案運價核定」 (translation: "Stone and lime are loaded 600 jin to a cart, freight 0.0138 tael per cart per li. Checked against the case approved in Qianlong 25 [1760], 0.00196 tael per 130 jin per li, this is excessive; the rate of the original case is fixed.") The database figure is 0.00803 tael per cart per li. Wages: 匠 0.07, 夫 0.06.

*Porters (timber only):*
- 直隸秦州 (4/8): 「人夫擡運，每夫每日給銀肆分…該處現送冊內…人夫擡運每伍拾觔運行陸拾里給銀肆分，今照冊核定。至石料、灰觔成規內並不另開運腳，應照舊辦理」 (translation: "Porters carrying: each porter is given 0.04 tael a day … the register now submitted has porters carrying 50 jin for 60 li for 0.04 tael, which is approved. For stone and lime, the established rule sets no separate freight; handle as before.")
  - Wages at the same place: 匠 0.05, 夫 0.04. The porter's day rate is exactly the laborer's day wage.
- 西寧府 歸德縣 (5/63), the rugged-mountain case: 「其木植壹項，產自堪卜拉山，番子所管，地方崎嶇峻嶺，用夫抬運每陸拾斤每里腳銀玖釐。該處現送冊開每陸拾斤運夫壹名每里給銀參釐，核與成規運價無浮，今照冊開載」 (translation: "Timber comes from the Kanbula mountains, held by the fanzi; the country is rugged with steep ridges. Porters carry it at 0.009 tael per 60 jin per li [the old rule]. The register now submitted gives 0.003 tael per li per porter for 60 jin; this does not exceed the rule and is listed as entered.")
  - Wages (5/62): 匠 0.05, 夫 0.04.

*Against stone by porter:*
- Nearly every Gansu remark repeats the refusal for stone, for example 蘭州府 臯蘭縣 (1/23): 「至磚瓦、石料、石灰等項，成規內不另開運腳，應照舊辦理」 (translation: "As for bricks, tiles, stone and lime, the established rule sets no separate freight; handle as before.")

**3. 欽定大清會典則例 卷130 (archived)**
- URL: `https://zh.wikisource.org/wiki/欽定大清㑹典則例_(四庫全書本)/卷130`. The entry is undated in the text; the regulations were compiled in the Qianlong reign.
- This volume is already cited for another question, but this passage is not in the record.
- Passage: 「丈席二百五十領一車八尺席三百領一車竹竿五百根一車葦箔二百塊一車繩一千三百斤一車 京城内每車給制錢二百出城十里内給制錢三百十里外照每里銀二分例算給」 (translation: "… rope, 1,300 jin to a cart. Inside the capital, 200 copper cash per cart; within 10 li outside the city, 300 cash; beyond 10 li, 0.02 tael per li.")
- This is a general Board of Works cart rate. The loads it names are mats, poles and rope, not stone.
- The same volume has a long-haul stone case: 「康熙三年議準 盛京 福陵 昭陵石料行取直隸山東山西四輪車…每車驘二十頭…車夫各給銀五兩」 (translation: "Kangxi 3 [1664]: for stone for the Fu and Zhao tombs at Shengjing, four-wheeled carts were requisitioned from Zhili, Shandong and Shanxi … twenty mules per cart … each carter given 5 taels.")

**4. Kotobank 車力, 日本国語大辞典 entry (Muromachi Kyoto only)**
- URL: `https://kotobank.jp/word/%E8%BB%8A%E5%8A%9B`
- Passage: 「七十五文車力借用〈略〉車力七十五文返之」(東寺百合文書, 明徳元年 1390) (translation: "Borrowed a cart for 75 mon … returned the cart, 75 mon.")
- The same entry adds: 「近世では、一般に零細業者が多く、大八車所持の有力商人などと雇用関係にある者も少なくなかった」 (translation: "In the early modern period most were small operators, and not a few were employed by powerful merchants who owned the carts.")

**Background for Japan (a), not a hire rate.** Morisada 守貞謾稿, 類聚近世風俗志 下 p.469 (archived GM copy `ruiju-kinsei-fuzokushi-ge-ndl991467-part-241-300.pdf`, frame 11). This is the Osaka べか車 licence fee, not a charge for hiring a cart:
- 「文政中私に製レ之ことを禁じ從來所持の車及び新製共に傳馬役所に錢を募りて用レ之ことを許す…行は驛家公用繁く市中運輸の諸物此車を用ふを以て也遂に驛家より官に請て車一輛春秋二季に金二朱計より金一両餘に至り募レ之用レ之の多寡に應じ初年定レ之有レ差也」 (translation: "In Bunsei, making them privately was forbidden; both old and new carts were allowed if a fee was paid to the post-horse office … the post station petitioned, and per cart, each spring and autumn, a fee from about 2 shu up to over 1 ryō was levied according to use, fixed in the first year with gradations.")
- The 1701 Edo 極印賃 in kotobank's 大八車 entry is the same kind of licence fee.

**Wage context for Japan.** Rinseishi booklet 09 (archived), 加子母村, 安永3 (1774): 「廿七日相働候賃銭一日六拾文充之積」 (translation: "wages for 27 days' work, reckoned at 60 mon a day"). That is a farm laborer. The booklet's carpenter figure is in modern yen, not an Edo wage.

## Reading

**ATTESTED**, for Qing (a): in Yunnan in 1769, stone by oxcart was reimbursed at 0.001 tael per 100 jin per li. That is roughly a fifth to a third of the porter rates there (0.0013–0.0025 per 100 jin per li). The labourer's day wage there was 0.04–0.05 tael and the craftsman's 0.06–0.07. In Gansu, stone went in 600-jin carts at 0.01–0.012 tael per cart per li. In Peking, a 1,300-jin cart cost 200 cash in the city, 300 within 10 li, then 0.02 tael per li.

**ATTESTED ONLY FOR timber and unnamed loads**, for Qing (b): Gansu porters were paid by the day, 0.04 tael at 秦州, equal to the labourer's wage there, carrying 50 jin for 60 li. 歸德, on rugged mountain timber, paid 0.003 tael per 60 jin per li in the register the district submitted, against 0.009 under the old rule. The Gansu regulations expressly set no separate porter rate for stone.

**SILENT**, for Edo (a) and (b): no Edo-period hire rate for a cart or carter by the day or the load turned up, and no porter or bokka rate for carrying into the mountains. Morisada's carts chapter (pp. 451–469) gives only descriptions and the Osaka licence fee.

What I searched for Japan:
- Archive terms: 大八車, 車力, 車借, 歩荷, 中馬, 人足賃, 守貞, 地方凡例録. The 中馬 kotobank entry gives no rate, only "100貫前後" per driver. The 車借 hit was zh-wiki 典當業.
- Queries: 守貞謾稿 車力 大八車 賃; 歩荷 賃銭 一貫目; 石段 普請 石材 運搬 人足 賃銭; 歩荷 千国街道 塩 賃; 石灯籠 運び上げ 人足 賃; 背負 一貫目 一里 文; 車力 賃銭 江戸 (×2); 丸山雍成 封建都市と陸上交通; 地方凡例録 人足 貫目 歩掛; 寺 山上 背負い上げ 人足 賃; 木曽 杣 日用 賃銭; 歩荷 一貫目に付; 背負賃/持上賃.
- Pages that did not bear:
  - natgeo 大八車 article: no rate, mostly behind a paywall.
  - 都史紀要32 page: table of contents only.
  - kyobunken PDF: no text layer.
  - Kyushu handle for the Maruyama paper: connection reset.
  - NDL fulltext API and IIIF for 991466: "PID not allowed" and empty images.
  - The search results (bunka.go.jp bokka entries, tabi-mag, Oya): no rates, or (Oya) already in 0257.

## Leads not followed
- 都史紀要32『江戸の牛』, 表16 享保十一年 and 表17 寛保二年 牛車運賃表, p.101 (1726 and 1742 Edo oxcart freight tables). Print only, not online. Its 図14 is 御影石を運ぶ牛車 (oxcarts carrying granite).
- Morisada 上 (991466), 雑業編 pp.187–209, for 車力: there is no GM copy, and NDL refused both routes.
- 丸山雍成 「封建都市と陸上交通」, 史淵 119 (1982), on the Kyushu repository.
- kotobank 日雇 entry `https://kotobank.jp/word/%E6%97%A5%E9%9B%87-612888`, not opened.
- Bochum Shanxi and Jiangsu pages exist (`shanxi_province.html`, `jiangsu_province.html`), not opened. Shanxi is mountainous and worth trying for porter or mule rates for stone.
