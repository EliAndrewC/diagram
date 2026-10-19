# Pass - rents (#4 Q3) (research-pass, 2026-10-18; its reply verbatim)

I have rent figures for every type you asked about except the samurai residence and the storehouse. They are partly attested, and the strongest result is the rent-to-value ratio. Neither record page has any of this: 0126 has no rent amounts at all, and 0251 has only Washizaki 2007's 20 times net / 5% valuation of a central Edo town lot. Everything below is missing from both. I edited nothing in the clone.

**Saved texts the session can cite without fetching again:**
- /tmp/l7r-pass/dl3/k.txt (Washizaki 2012)
- /tmp/l7r-pass/dl5/t.pdf (Tanigama 2014)
- /tmp/l7r-pass/dl6/d.txt (Teng 2014)
- /tmp/l7r-pass/rent-wulp/01-www.sohu.com.txt (Wu Liping 2017)
- Washizaki 2007 is in the archive at /diagram/.specify/source-archive/38/386afe5fc8e0/20261019T000327Z/served.pdf. I read its pages 11 and 15 as images, because the text layer is garbled.

`make source-pages` would not read any of the four new PDFs ("NOT-CHECKED - a PDF"), so I downloaded each with curl and converted it with pdftotext. Each URL is on the ledger with what I was looking for in it.

## Sources

**1. Tanigama Hironori 2014, Toyo University, スポーツ健康科学紀要 11, pp. 55–77.** https://toyo.repo.nii.ac.jp/record/6852/files/sportskenkokagaku11_055-077.pdf. It describes Edo in the Bunsei era (1818–30) from 『文政年間漫録』 (in 『未刊随筆百種』 1). It is a modern paper reading a source from the period.
- 「なお，ここでは貨幣の交換率を「金1両＝銀60匁＝銭6000文｣とし」 — "Here the exchange rate is taken as 1 ryō gold = 60 monme silver = 6,000 mon cash" (translation). The mon figures below are his conversions.
- 「文政期頃の大工の日収は飯料込みで銀5匁4分（540文）であったという。また，大工の生活における毎月の支出は，店賃(家賃）が10匁(1000文）で」 — "Around the Bunsei era a carpenter's daily income, meal allowance included, was 5 monme 4 bu of silver (540 mon). His monthly outgoings included house rent of 10 monme (1,000 mon)" (translation).
- 「棒手振に代表される中下層の商人の日収は400文程度であった計算になる」 — "this works out to a daily income of about 400 mon for the lower-middle traders typified by the street peddler" (translation).
- Limits: the size of the carpenter's unit is not stated. The 400 mon is Tanigama's own sum of the peddler's spending plus what he had left, so it is a peddler's takings, not a laborer's wage.

**2. Archived page `muraoka-edo-nagaya-life`** (http://www.eonet.ne.jp/~shoyu/mametisiki/reference-8.html). A hobby page that names no source; it describes Edo in 1804–30 and the late Edo period.
- 「文化文政(1804～1830)頃の裏長屋の店賃(たなちん＝家賃)は、月に300～500文程度であった。物価が上がった幕末頃は、九尺二間の店賃が500～600文だったという記録がある。」 — "Back-tenement rent around Bunka–Bunsei was about 300–500 mon a month; in the late Edo period, when prices had risen, there is a record of 500–600 mon for a 9-shaku × 2-ken unit" (translation).
- 「１日の稼ぎは、大工・左官・土方などが１日320~540文、野菜の棒手振りが１日100~200文程度であった。」 — "Daily earnings were 320–540 mon for carpenters, plasterers and navvies, and about 100–200 mon for vegetable peddlers" (translation).
- The "record" behind the 500–600 mon figure is not named.

**3. Washizaki Shuntaro 2012, 「江戸の町屋敷経営と不動産収益率の長期分析：1775〜1872」, 經濟學研究 79(4), Kyushu University.** https://api.lib.kyushu-u.ac.jp/opac_download_md/25880/p095.pdf. Edo, 1700s–1872, from the Mitsui house's account books.
- 「インカム収益率が18世紀初頭に６％台を記録したものの､ その後は３〜５％台に低下していた」 — "the income yield [on Edo town lots] reached the 6% range in the early 18th century but then fell to 3–5%" (translation).
- 「インカム収益率は1770〜90年代に４％前後で推移していた｡ … 1800年代に入ると､ 4[.]5％近くまで上昇した｡ … 66年には単年 () で1[.]8％」 — "the income yield ran at about 4% in the 1770s–90s … rose to nearly 4.5% in the 1800s … and was 1.8% in 1866 on the single-year measure" (translation). The [.] marks are decimal points the PDF text drops.
- 「｢流れ込んだ家屋敷を所持したときの宿賃の利率は月４厘ほど｣ と記載されている｡ 月４厘というのは､ 年利に換算すると4[.]8％」 — "[an 1811 Mitsui survey] records that 'the rent rate on a forfeited house-lot one holds is about 4 rin a month'; 4 rin a month is 4.8% a year" (translation).
- Note 66: 「宿賃の利率のうち半分が普請金積除になるため､ 純利益ベースでは月２厘 (年利2[.]4％) ほどとなり､ 名目金貸付の年利 (10〜12％)､ 家質貸の年利 (６％) と比較すると非常に低率だった」 — "half the rent rate was set aside for rebuilding, so the net rate was about 2 rin a month (2.4% a year), very low beside 10–12% on loans and 6% on house-pledge loans" (translation).
- 「地代店賃は毎月晦日に取り立てられ」 — "ground and house rents were collected on the last day of every month" (translation, of the 1729 rules).
- The yield's denominator is the 40 lots' 沽券金高 「５万6565両」 (56,565 ryō), which the paper says doubled as their market price (踏値段). It is a fixed figure covering the lot and its houses.
- Appendix table 1, in ryō per month, for 1790: total rent 262, ward charges 43, manager's pay 33, owner's take 186. My own arithmetic from this, not the paper's: gross about 0.46% of value a month (5.6% a year), owner's take about 0.33% a month (3.9% a year).
- Storehouses: income included 「蔵敷料」 (storage fees), and 「一部の水運沿いの地面は土蔵貸として使用されていた」 — "some waterside lots were let as storehouses" (translation). No rate is given.

**4. Washizaki 2007** (the 0251 source, archived), Table 2 and Table 4, read as page images.
- Table 2 is 「江戸町屋敷1小間の実質地価と収益還元地価（享保〜寛政期，日本橋地区表店）」 — "real land price and capitalized-income price of one 小間 (20 tsubo) of an Edo town lot, 1716–1800, Nihonbashi street-front shops" (translation). It gives Rt, the real ground rent per year, beside Pt, the real land price, both in ryō:

| Lot | Period | Ground rent Rt | Land price Pt | Ratio (my division) |
|---|---|---|---|---|
| 本町2丁目 (mid-block lot) | Kyōhō (1716–36) | 23.3 | 265 | 8.8% |
| 本町2丁目 | Genbun | 25.6 | 233 | 11% |
| 本町2丁目 | Meiwa | 19.1 | 277 | 6.9% |
| 通1丁目 (corner lot) | Kyōhō | 38.8 | 388 | 10% |
| 通1丁目 | Meiwa | 25.2 | 344 | 7.3% |
| 通1丁目 | Kansei (1789–1801) | 25.3 | 345 | 7.3% |

- Both columns are deflated by the rice price, so the ratio holds but the ryō are not nominal sums.
- Table 4, text beside it: 「利子率Itは，Rtに①表店地代と②裏店地代を用いた場合，それぞれ①9.5％，②5.0％と推定された」 — "the interest rate is estimated at 9.5% using street-front ground rent and 5.0% using back-tenement rent" (translation). This is Tenpō-era Kyōbashi (Table 4 gives 9.463% and 5.030%).

**5. Teng Deyong 2014, 「清代内务府房产经营状况探析」, 故宫博物院院刊 2014(4).** https://www.dpm.org.cn/Uploads/File/2018/06/04/u5b1537cba43d1.pdf. Beijing, government-owned houses, 1700s.
- 「官房租价，按檩征租。凡七檩房每间租银二钱，六檩房每间租银一钱五分，五檩、四檩房每间各租银一钱，三檩房并三檩游廊每间均各租银五分。」 — "Government-house rent is charged by purlin count: 0.2 tael per bay for a 7-purlin house, 0.15 for 6-purlin, 0.1 for 5- and 4-purlin, 0.05 for a 3-purlin house or 3-purlin veranda" (translation).
- 「这些租赁房屋的租金按月收取」 — "the rent on these houses was collected monthly" (translation).
- 「九檩房每间价银70两，八檩房每间价银60两，七檩房每间价银50两，六檩房每间价银40两，五檩房每间价银30两，四檩房每间价银20两，三檩房每间价银10两。」 — "sale price per bay: 9-purlin 70 taels, 8-purlin 60, 7-purlin 50, 6-purlin 40, 5-purlin 30, 4-purlin 20, 3-purlin 10" (translation). This schedule applied before 1731 and was restored in 1775.
- A higher schedule from 1802 also exists: 七檩一等瓦房每间作价银八十两 (80 taels a bay for a first-grade 7-purlin tiled house).

**6. Wu Liping, 「清朝人在北京怎样租房?房租有多高?」, 文史知识, 2017.** https://www.sohu.com/a/152159933_672913. Beijing, 1727–1907.
- 「据雍正五年（1727）的规定 … 七檩每间租银二钱 … 官房铺面房租价，除了原先已有租价，其他根据坐落冲要还是偏僻位置，每间三四钱至三四两不等」 — "under the 1727 rule … 0.2 tael per bay for 7-purlin … government shop-front rooms, unless already rented, 0.3–0.4 tael to 3–4 taels a bay by how busy or remote the site" (translation). This dates Teng's rent schedule.
- The official Li Ciming, 1871: 「约十五六间，月租三万六千文，押金一万文」 — "about 15–16 bays, monthly rent 36,000 wen, deposit 10,000 wen" (translation). The paragraph names the currency only as 京钱 (Beijing cash).
- His later residence: 「每月租金四两」, and in 1880 「月租六两」 — "4 taels a month", later "6 taels a month" (translation). In 1875: 「一年房租四十八两 … 这年李慈铭的收入为168.56两 … 光绪元年一两等于一万文」 — "48 taels' rent for the year … his income that year was 168.56 taels … in 1875 one tael equalled 10,000 wen" (translation).
- Shops, from Daoguang-era (1821–50) contracts: 「门面房二间 … 每月初六日取房租满一吊六百文」 — "two shop-front rooms … rent of 1 diao 600 wen collected on the 6th of each month" (translation).
- Government shop rooms, from a file covering 1871–1911: 4 rooms at 8 吊 a month, 3 rooms at 8 吊, 4 rooms (two storeys) at 10 吊.
- 1783 ground lease for a shop site outside Zhengyangmen: 「房基租价每月广平纹银拾两」 — "site rent 10 taels of silver a month" (translation).

## Verdict

**ATTESTED ONLY FOR** the back-tenement unit, the lot-level rent-to-value ratio in Edo, and the Qing government house.

**Edo rents.** A Bunsei-era carpenter household's back-tenement rent was 10 monme (about 1,000 mon) a month (Tanigama, from 『文政年間漫録』). A peddler took in about 400 mon a day, so that rent is about 2.5 days of his takings. The 300–500 mon a month (1804–30) and 500–600 mon for a 九尺二間 unit (late Edo) rest only on the unsourced hobby page.

**Pairing with a day wage.** Record 0250's unskilled wage of about 0.9 monme is from 1745–54, so it does not match these years. The only wage figures from the same years are the peddler's takings and the hobby page's 320–540 mon for navvies, which has no named source.

**Rent-to-value in Edo** is well attested:
- Owner's net income ran about 3–5% a year of the lot-and-house market value: about 4% in the 1770s–90s, nearly 4.5% in the 1800s, down to about 2% by 1866.
- Mitsui's own 1811 rule of thumb was gross rent of 4 rin a month (0.4%, 4.8% a year), or 2 rin net of the rebuilding reserve.
- Street-front ground rent against land price ran about 7–11% a year (1716–1800). Tenpō-era capitalization implies 9.5% for street-front rent and 5.0% for back-tenement rent.

**Qing Beijing government houses** come out at almost the same ratio, though both prices are administrative, not market:
- 7-purlin: 0.2 tael a month against 50 taels ≈ 0.4% a month (4.8% a year)
- 6-purlin: 4.5% a year
- 5-purlin: 4.0%
- 4-purlin and 3-purlin: 6%

That division is mine, putting the 1727 rent schedule beside the sale schedule in force before 1731. Against 0250's Qing wage of 0.045 tael a day, one 7-purlin bay rented for about 4.4 days' pay and a 3-purlin bay for about 1 day.

**What is missing:**
- **Edo street-front shop (表店) rent for one unit, in money:** not found. Only ground rent per 小間 in real (deflated) terms and lot-level yields.
- **Samurai residence:** SILENT on any amount. Tahara 2023 (Edo-Tokyo Museum bulletin 13) shows retainers letting parts of their granted lots for ground rent but gives no figure. For Qing China, the nearest match is Li Ciming's 15–16-bay house at 36,000 wen a month, or 4 taels a month later.
- **Storehouse rent:** SILENT on the rate. Washizaki 2012 shows storehouses were let and storage fees came in, but gives no rate.
- **A small house:** not found, as distinct from a tenement unit.

**Pages read that did not bear:**
- Saito and Takashima 2020: medieval wages
- Suzuki DP 22-04: no rent
- Tamai 1978 (AIJ 265): rent tables illegible in the text layer
- Yamada (Osaka Kashima-ya): aggregate rent only
- Chiebukuro Q&A: anonymous
- eonet reference-8c: a secondary copy of Tanigama

## Leads not followed
- 『文政年間漫録』 itself (未刊随筆百種 1, NDL), to check the 店賃 百二十匁 line and the unit size. Nakae Katsumi's retelling gives 四畳半二間 (two 4.5-mat rooms).
- 三田村鳶魚『江戸っ子』, said to give 400 mon a month for a back tenement under Bunsei and 600 mon under Tenpō. This claim came only from an anonymous Q&A answer.
- The Tenpō 13 (1842) survey of ground rents, house rents and lot values (地代店賃沽券高調査), in 東京市史稿 市街編39, pp. 718–852. It gives each lot's street-front and back-tenement rent in money.
- 小澤詠美子 1989, 「江戸における町屋敷の経営」, 史潮 新25.
- 刘小萌『北京商业契书集』 (2011), Qing rental contracts.
- 张德昌『清季一个京官的生活』 (1970), Li Ciming's rents against his income.
- The 京钱-to-制钱 rate needs a source before the 36,000 wen figure is converted.