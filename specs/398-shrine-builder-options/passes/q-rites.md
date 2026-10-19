# Pass - rites and the dead (#7 Q4) (research-pass, 2026-10-19; its reply verbatim)

I found four figures that come close, and none of the six fees as asked. Two are Japanese: an in-kind 遷宮 list from 1549 and a Hakata Gion float budget from 1838. One is Chinese, used as the fallback: Zheng Banqiao's price list of 1759. The fourth, a plaque fee from 1890, is after 1868, so it counts only as a lead.

Three of the PDFs (xsyk, Hakata, Dazaifu) are not in the archive: `make source-pages` saved nothing for them ("no text layer can be read here"). I downloaded them with curl and read the pdftotext output in the scratchpad: `/tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/xs/a.txt`, `/tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/hk/a.txt` and `/tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/dz/a.txt`.

**1. Sources that bear on the question**

**遷宮 (enshrinement)**
- The cost share is already in the record: covered by 0255/0256 (the 1749 Kasuga repair, 20.0% of about 43 ryo).
- **Archived copy:** the ja.wikipedia article 出雲国造, at `/diagram/.specify/source-archive/6d/6d1839e913a3/20261002T122638Z/text.txt`. It quotes 「杵築大社遷宮入目注文」 of 天文18年 (1549), 新出北嶋家文書 36号. This is the Sengoku period, not Edo, and the list gives goods only, with no money:
  > 就御遷宮入目之事 … 一、両国造こてふくめん六たん / 一、御かとまらふと両社ヘ六たん / 一、末社三社ヘ九たん / 一、御神馬かさり二疋ニ六たん、同引まハしにきぬ二ひき、同しんつな布二たん

  (translation) "Concerning the costs of the enshrinement … for the two kuni no miyatsuko's (the shrine's two hereditary chief priests) coverings, six tan (bolts) of cloth; for the two gate shrines, six tan; for three subsidiary shrines, nine tan; for the trappings of two sacred horses, six tan, plus two hiki of silk for the lead ropes and two tan of cloth for the sacred reins."

**御霊会 (goryo festival)**
- **Source:** 宇野功一「近世博多祇園山笠における当番町制度と当番費用徴収法」, 国立歴史民俗博物館研究報告 121, https://rekihaku.repo.nii.ac.jp/record/1336/files/kenkyuhokoku_121_02.pdf
  - Printed p.53 (PDF p.9). The text is vertical and came out through pdftotext, so the punctuation shows in vertical forms.
  - The year 2005 is from memory: the repository's landing page returned 404.
  - The evidence describes 1838:
  > 行町は天保九︵一八三八︶年に︑今後の山笠当番のさいの山笠仕立銀を総額で七貫三〇〇目と見積もっており︑そのうち御渡り銭の分についてはひとまず八〇〇目と予想している︒

  (translation) "In Tenpō 9 (1838) Gyō-machi estimated the total silver for building its float on future duty turns at 7 kan 300 me (7,300 monme), of which it provisionally expected 800 me to be the procession money."
- Printed p.67 (PDF p.23) puts the same 7貫300目 at 438貫文 of copper cash.
- Around 1691 the levy on the nine towns not on duty that year (祇園銭) was:
  > 祇園銭は普通︑二〇〇匁強であったと結論できる︒

  (translation) "We can conclude that the Gion levy was normally a little over 200 monme."
- I left out the fragment that follows the 1838 sentence, 「仕立銀総額のわずかニパーセント」. It is an OCR misread: 800 of 7,300 is 11%, not 2%.

**扁額 揮毫 (calligrapher's fee for a plaque), China fallback**
- **Source:** 陶小军「近代书画润例的商业广告与文化认同」 (2025), p.160, https://www.xsyk021.com/fileXSYK/journal/article/xsyk/2025/8/PDF/xsyk-2025-8-160.pdf
  - It quotes the 板桥润格 of 乾隆己卯 (1759), citing 《郑板桥集》 (1979), p.184, in simplified characters.
  - It says the inscribed stone is in the Yangzhou Museum.
  > 大幅六两，中幅四两，小幅二两。条幅、对联一两。扇子、斗方五钱。凡送礼物食物，总不如白银为妙……画竹多于卖竹钱，纸高六尺价三千。

  (translation) "Large pieces six taels, medium four taels, small two taels. Hanging scrolls and couplets one tael. Fans and square album leaves five qian. Gifts of things or food are never as good as silver … I paint more bamboo than I could earn selling bamboo; paper six feet high costs three thousand."
- **Wage base:** Allen et al., LSE wp123 (archived, `/diagram/.specify/source-archive/0d/0d03ddf5fea8/20261018T232808Z/text.txt`), Table 1, "Nominal Wages of Workers in Public Construction, 1769-95":
  > Jiangsu** 0.040 0.051

  (unskilled and skilled, taels per day; English, no translation needed). The government norm's own preface says these wages were "near to market prices at low market activity". The paper's market level for Suzhou is 0.09–0.0968 taels.
- **The 1890 plaque fee (post-period, lead only):** the Dazaifu 宮小路家文書目録, https://www.city.dazaifu.lg.jp/uploaded/attachment/3670.pdf, records 「帝国議会扁額四大字揮毫の謝礼金五拾円の受け取り」, dated 明治23年12月17日. (translation) "Receipt of a fee of 50 yen for writing the four large characters of the Imperial Diet plaque." 1890 is after 1868, so it is not premodern evidence. I have marked its ledger outcome rejected.

**2. Reading**

- **遷宮 — ATTESTED ONLY FOR** an in-kind requisition list, outside the Edo period: Kizuki (Izumo) in 1549, cloth counted in tan and hiki with no money total. The cost share is covered by 0255/0256. A fee for a priest's night rite is **SILENT**.
- **御霊会 — ATTESTED ONLY FOR** one city ward's float-duty budget at a Gion festival, which descends from the goryo-e. It is not a priestly pacification rite and not a village rite. In 1838 Hakata's Gyō-machi estimated 7,300 monme, about 122 ryo at the 60 monme to the ryo that 0258 borrows. Around 1691 the levy on the towns not on duty was a little over 200 monme.
  - No Hakata wage is in the record. On 0258's bases, which are from a different place and period, 122 ryo is about 7,900 days of a Kyoto laborer (0.92 monme a day, 1802–04) or about 970 days of a carpenter (0.125 ryo a day, 1853–60).
- **永代供養 / 永代経 / 位牌安置料 — SILENT.** The Edo term is 祠堂金 (endowment money for a memorial tablet's perpetual rites). No amount for it turned up in any source I found or read.
- **分骨 / 納骨 to Kōyasan — SILENT.** This is in line with 0258's negative. The search results showed only today's prices (100,000 yen at Kongōbuji); I did not fetch those pages and they are not evidence.
- **洗骨 — SILENT.** This is Okinawa and Amami practice, a different region. I found no fee.
- **扁額 揮毫料 in Japan — SILENT. In China, ATTESTED ONLY FOR** a calligrapher-painter's posted price list by format. Zheng Banqiao, Yangzhou, 1759: six taels for a large piece, one tael for a hanging scroll or couplet, five qian for a fan. The list has no plaque line.
  - At Jiangsu's 1769 construction norms, six taels is 150 unskilled or 118 skilled days. At Suzhou's market rate it is about 65 days.
  - One tael is 25 or 20 days. Five qian is 12.5 or 10 days.
  - The phrase 价三千 ("costs three thousand") is a cash figure; I have not converted it.

**What the SILENT verdicts searched**
- **Archive terms**, one at a time:
  - 遷宮 25 texts, 仮遷宮 0, 遷座 22
  - 御霊会 0, 御霊祭 0, 鎮魂祭 0
  - 永代供養 10, 永代経 0, 位牌 30
  - 分骨 11, 納骨 30, 高野山 42, 洗骨 9
  - 扁額 31, 揮毫 11, 潤筆 0, 書家 10
  - eitai 11, Koyasan 3

  A grep of all those texts for a money unit within 60 characters of these terms found no premodern fee.
- **About 20 web queries:**
  - 潤筆料 / 潤例 / 潤格, and 市河米庵, 頼山陽, 巻菱湖, 亀田鵬斎, 貫名菘翁
  - 高野山 納骨, plus pilgrimage travel diaries (道中日記)
  - 永代供養料 / 永代回向料 / 祠堂金
  - 遷宮入用 / 神主 礼金
  - 御霊会 入用, 祇園会 入用
  - 洗骨 費用
  - English "Edo calligrapher fee ryo"
- **Pages read and rejected:**
  - Ishikawa Prefectural Library booklet 875.pdf: a 2020s exhibition on Kamigamo shrine, no cost.
  - Kanazawa University AA12079036-32-127-137.pdf: modern fieldwork on graves in Noto.
  - Kyushu University 41_p001.pdf (Munakata village festivals, 17th–19th c.): mentions a 1701 遷宮 but gives no cost.

**3. Leads not followed**
- NDL R100000039-I1116312, Hakusan 正遷宮御入用帳 (1714), 入用物品受取扣 (1734), 荒御前社御遷宮入用帳 (1763): scans only.
- 坂本亮太「高野山奥之院への納骨」, 季刊考古学 134 (2016).
- Nagoya University 高木家文書, notices of 永代祠堂経 (1835–65): catalogue entries only; amounts not checked.
- 関根達人『琉球・奄美の葬墓制』, for 洗骨.
- Edo-Tokyo Museum, Ishii Ryōsuke collection: Yotsuya Shiomachi 御仮屋諸入用勘定割合請取帳 of 天保7 (1836), a festival account.
- 《郑板桥集》 (1979), p.184, the primary text of the price list.

Sources:
- [Kizuki shrine 1549 遷宮 list, via ja.wikipedia 出雲国造](https://ja.wikipedia.org/wiki/出雲国造)
- [宇野功一, 歴博研究報告 121](https://rekihaku.repo.nii.ac.jp/record/1336/files/kenkyuhokoku_121_02.pdf)
- [陶小军 2025, Zheng Banqiao's 润格](https://www.xsyk021.com/fileXSYK/journal/article/xsyk/2025/8/PDF/xsyk-2025-8-160.pdf)
- [Allen et al., LSE wp123](https://www.lse.ac.uk/asset-library/information/wp123.pdf)
- [Dazaifu 宮小路家文書目録](https://www.city.dazaifu.lg.jp/uploaded/attachment/3670.pdf)
- [Ishikawa Prefectural Library 875.pdf](https://www.library.pref.ishikawa.lg.jp/file/875.pdf)
- [Kanazawa University AA12079036-32-127-137.pdf](https://kanazawa-u.repo.nii.ac.jp/record/6706/files/AA12079036-32-127-137.pdf)
- [Kyushu University 41_p001.pdf](https://catalog.lib.kyushu-u.ac.jp/opac_download_md/1559850/41_p001.pdf)