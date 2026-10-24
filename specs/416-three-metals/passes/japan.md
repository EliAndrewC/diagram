<!-- 416 pass: Japan's three monies: the research-pass agent's report, 2026-10-24, filed verbatim by the session -->

I found something for all four questions. Japan's three metals had legal rates (1609, 1700, 1842) and a legal Osaka floor in 1843. The market always set the real rate, and the law was changed to follow it. Only the gold count (4 bu to the ryo, 16 shu to the ryo) and the silver coins stamped in gold units were fixed. Copper and weighed silver floated. A price could depend on the money it was paid in. The clearest cases are Edo in 1842, Tsugaru in 1837, and Edo in 1865-68.

Nothing was written in any repository. Some things the session needs to know first:
- **The Oishi paper has no usable archive copy.** Both captures of `https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf` in `/diagram/.specify/source-archive/71/714c023c43be/` are HTTP 406 stubs with no text. My quotes come from a fresh download read with pdftotext, in `/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/oishi/o.txt`. It should be re-archived.
- **Three other PDFs were read the same way, outside the ledger.** `make source-pages` could not read them, so I downloaded them with curl. Their text is under the same scratchpad: Iwahashi in `mu/p.txt`, Kano in `ds/p.txt`, Kobayashi in `imes/c.txt`.
- **I recorded four rejected or failed pages on the ledger.** Two guessed kotobank IDs pointed to unrelated entries, and two pages could not be read or held nothing. All pages that bear on the questions are left for the session to cite.
- **Quoting conventions.** Quotes keep the text layer as it came out; my bracketed corrections mark garbled characters. Percentages and conversions marked "my arithmetic" are mine, not the sources'.

---

## Q1. Legal rates against market rates

**S1. jawiki 御定相場** (archived `a4/a4231cae78de`). Evidence 1609-1842; cites 宮本又次 in 国史大辞典 and 三上 1996.
「江戸幕府は慶長14年（1609年）金1両＝銀50目＝銭4貫文（4000枚）という御定相場を定めた。だが、東西間の経済活動が活発化するにつれて民間での金相場・銀相場は変動を生じさせ、幕府の定めた御定相場が形骸化するようになった。」
(translation) "In 1609 the shogunate set the official rate at 1 ryo of gold = 50 monme of silver = 4 kanmon (4,000 coins). But as trade between east and west grew, the private gold and silver rates moved, and the official rate became a dead letter."

「元禄13年11月（1700年12月頃）に金1両＝銀60目と御定相場を改定し、両替商らには金1両＝銀58匁以下の銀高、金1両＝銭3900文以下の銭高で取引することを禁じた。…しかし、市場相場は御定相場を維持することができず、上方で銀が払底するなど混乱を生じた。」
(translation) "In 1700 it revised the official rate to 1 ryo = 60 monme. It forbade money changers to deal with silver dearer than 58 monme to the ryo, or copper dearer than 3,900 mon to the ryo. ... But the market could not hold the official rate, and there was disorder, with silver running out in the Kamigata."

「元文元年…両替商が良質の旧銀を退蔵し銀相場が一時的に高騰したが、…大岡忠相は両替商を呼び出し相場の操作を止めるよう勧告するなど取り締まったが、しばらく銀高騰は収まらず」「このように、実際には御定相場の方が民間の市場相場に左右されて改定を余儀なくされていた。」
(translation) "In 1736 money changers hoarded the good old silver and its rate shot up. Ōoka Tadasuke summoned them and told them to stop manipulating the rate, but silver stayed dear for some time." "So in practice it was the official rate that was swayed by the market and forced to change."

**S2. jawiki 江戸時代の三貨制度** (archived `c5/c58cdc0ca3f7`). Evidence 1609-1871.
「幕府は慶長14年（1609年）に金1両=銀50目=永1貫文=鐚4貫文、…元禄13年（1700年）に金1両=銀60目=銭4貫文と改訂した御定相場を公布した。上納金など公的なものにはこの御定相場が守られたが、市場では江戸、大坂を中心として各地で相場が立てられ、両替商らは日々の相場に基づいて取引を行った」
(translation) "The shogunate proclaimed 1 ryo = 50 monme = 1 kanmon of ei = 4 kanmon of bita coin in 1609, revised in 1700 to 1 ryo = 60 monme = 4 kanmon. The official rate was kept for public payments such as dues to the shogunate. In the market, rates were set in Edo, Osaka and elsewhere, and money changers dealt at each day's rate."

「江戸時代初期には金1両は銀43匁程度であったが…元禄の吹替えは…再び金1両が銀50目程度まで銀高に戻り、これを是正するための御定相場改訂であった。しかし市場は御定相場に従うようなものではなく、宝永期の銀貨吹替えによりようやく銀高が解消された」
(translation) "Early in the period a ryo was about 43 monme. ... After the Genroku recoinage silver rose again to about 50 monme a ryo, and the 1700 revision was meant to correct this. But the market did not follow the official rate; silver's dearness ended only with the Hoei silver recoinages."

「明和期に寛永通寳鉄一文銭および真鍮四文銭が大量に発行されるようになると銭相場は次第に下落し金1両が銭6貫文程度となり…明治維新の頃には金1両が銭10貫文程度に達した。」
(translation) "From the Meiwa era (1764-72), with mass issue of iron one-mon and brass four-mon coins, copper fell to about 6 kanmon a ryo ... by the Restoration it reached about 10 kanmon."

**S3. jawiki 寛永通宝** (`https://ja.wikipedia.org/wiki/寛永通宝`). Evidence 1694-1778. This gives the market against the 1700 rule.
「元禄7年（1694年）に金一両＝4800文前後であったものが元禄13年（1700年）には一両＝3700文前後となった」; 「元文2年（1737年）には…銭相場が一両＝2800文前後まで急騰した」; 「銭相場は下落し安永7年（1778年）ごろには一両＝6000文前後を付けるに至った」
(translation) "From about 4,800 mon a ryo in 1694 it went to about 3,700 in 1700." "In 1737 ... copper shot up to about 2,800 mon a ryo." "Copper fell, reaching about 6,000 mon a ryo around 1778."

**S4. Oishi Shinzaburō 1966**, 学習院大学『経済学研究』2(2): 69-128 (`https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf`). It prints the town orders of 1842 and summarizes those of 1796-1829. This shows enforcement.

The order of 1842/8/5:
「連年銭相場下値二而，諸色値段江も相響，下々難儀いたし…巳来金壱両二付銭六貫五百二入替之積を以売買可致候，且仙台角銭石巻銭，其外他国♂銭相廻し候儀，一切可為無用候，若相背候族有之二おゐて者，右銭取立厳重之餐[咎]可申付候。…此上御趣意之趣等閑二相心得候者有之者…町役人共迄急度曲事可申付候。…番屋江張出井両替渡世之者見世先江張出置可申候」
(translation) "Copper has been cheap year after year, which affects the prices of goods and causes hardship to the lower people ... From now on trade at 6 kanmon 500 mon to 1 ryo of gold. Bringing in copper from Sendai, Ishinomaki or other provinces is forbidden. Anyone who disobeys will have that copper seized and be strictly punished. ... If anyone neglects this, the town officials too will be held to account. ... Post this at the guardhouses and at the shopfronts of money changers."

Oishi on how the 6,500 line came about:
「寛政8年の「銭相場年々下直にて日用諸色高値になり，下々難儀に付，御救のため当春以来度々銭御買上あり」，寛政12年の「銭相場下落につき引上げを令す」，文化10年の「近年別て銭相場下落し，銭にて商売の軽き商人が難儀をするので，他国より銭をまわす事を禁ず」…寛政年間にすでにほぼ6貫500文ラインに近い当局の銭相場観があったことが分かる。」
(translation) "1796: 'copper has fallen year by year and daily goods have become dear, a hardship for the lower people, so for their relief the shogunate has bought copper repeatedly since this spring'. 1800: 'copper having fallen, an order to raise it'. 1813: 'copper has fallen especially in recent years, a hardship to small merchants who trade in copper, so bringing copper from other provinces is forbidden'. ... So already in the 1790s the authorities had a view of copper close to the 6,500 line."

He also records the reverse case. In 1829 copper was "dear", and the shogunate ordered 5,000 ryo's worth of copper sold off 「金壱両二付六貫五百文余替位迄を限り」 (translation: "down to about 6,500 mon or so a ryo"). His Table 1 gives Edo yearly rates from 1751. In the Hōreki era (1751-64) they ran about 3,900 to 4,455 mon a ryo. He describes the trend: 「明和6年（1769）に一度4貫文代を割って5貫文代におちこみ以後急速に5貫文代を下落して安永7年（1778）には6貫文代におちこみ」 (translation: "in 1769 it broke below 4 kanmon into the 5,000s, fell quickly through them, and in 1778 dropped into the 6,000s").

**S5. 貨幣博物館 常設展示図録 p.42** (`https://www.imes.boj.or.jp/cm/collection/tenjizuroku/mod/book/pageindices/index42.html`). Modern museum text on 1609-1870. It gives the ladder of ratios fixed by count.
「公定相場（1700年）金貨（計数貨幣）1両＝4分＝16朱…二分金2枚（1818〜）一分金4枚二朱金8枚（1697〜）一朱金16枚（1824〜）1765年〜計数銀貨五匁銀12枚一分銀4枚二朱銀8枚一朱銀16枚1609年金1両＝銀50匁＝銭４貫文1700年金1両＝銀60匁＝銭４貫文1842年金1両＝銀60匁＝銭６貫500文」「18世紀後半、幕府が両建ての計数銀貨を発行するようになると、匁建ての秤量銀貨はほとんど流通しなくなった。それでも、大坂を中心とする両替屋や商人たちは、明治時代初めまで銀貨の単位である匁建て（銀目）で…取引を行っていた。」「大坂の有力な両替屋の間で金銀銭を交換するときの相場が、各地の基準となった。」
(translation) "Official rates (1700). Gold, counted: 1 ryo = 4 bu = 16 shu, paid as 2 ni-bu gold pieces (1818-), 4 ichi-bu, 8 ni-shu gold (1697-) or 16 isshu gold (1824-). Counted silver from 1765: 12 five-monme pieces, 4 ichi-bu silver, 8 ni-shu silver, 16 isshu silver. 1609: 1 ryo = 50 monme = 4 kanmon; 1700: 60 monme = 4 kanmon; 1842: 60 monme = 6 kanmon 500." "In the later 18th century, once the shogunate issued counted silver coins in ryo units, the weighed silver priced in monme hardly circulated. Yet the money changers and merchants of Osaka kept dealing in monme (the silver unit of account) until early Meiji." "The rate at which the leading Osaka changers exchanged gold, silver and copper became the standard everywhere."

**S6. jawiki 南鐐二朱銀** (`https://ja.wikipedia.org/wiki/南鐐二朱銀`, re-read for this question). Evidence 1772-1800.
「金貨の通貨単位である2朱に相当する銀貨を発行して、金貨と銀貨の為替レートを固定、事実上の通貨統一を果たし」「小判と丁銀相互の変動相場による両替を元に利益を上げていた両替商にとって南鐐二朱銀の発行は死活問題であり、…南鐐二朱銀の小判および丁銀への両替に対し、2割5分の増歩を要求する」「京都、大坂においては「金百両に南鐐二朱廿五両差」…」「「売上四分、買上八分」すなわち、両替商が南鐐二朱銀を売るとき買手に一両当り銀四分を与え、買上げるときは南鐐二朱銀の売り手から銀八分を徴収するよう取り決めた。また商人に対して南鐐二朱銀による貸付の場合は江戸では一万両、大坂では四万両を限度として3年間、無利子、無担保とした」「丁銀から南鐐二朱銀への改鋳が進行するにつれ…天明6年（1786年）には金1両＝銀50匁をつけるに至った。」
(translation) "By issuing a silver coin worth 2 shu in gold units, it fixed the gold-silver rate and in effect unified the currency." "For changers who profited from exchanging koban and chogin at floating rates, the nanryo was a matter of survival. ... They demanded a 25% premium for changing nanryo into koban or chogin." "In Kyoto and Osaka the rule was '25 ryo of nanryo mixed into every 100 ryo of gold'." "'Sell 4 fun, buy 8 fun': when a changer sold nanryo he gave the buyer 4 fun of silver per ryo, and when he bought it he took 8 fun from the seller. Merchants were also lent nanryo free of interest and security for 3 years, up to 10,000 ryo in Edo and 40,000 in Osaka." "As chogin was recoined into nanryo ... by 1786 silver reached 50 monme a ryo."

**S7. jawiki 一分銀** (`https://ja.wikipedia.org/wiki/一分銀`). Evidence 1837-1859.
「その貨幣価値は、金貨である一分金と等価とされ…表面には「一分銀」と直接額面が表示されることとなり、ここで江戸時代の計数銀貨としての完成形を見た」「天保一分銀、および安政一分銀共に発行高は同時期の丁銀をはるかに上回るものとなり、これ以降計数銀貨が流通の主流となった。」
(translation) "Its value equalled the gold ichibu (1/4 ryo) ... it carried its face value as 'ichibu-gin', the finished form of Edo counted silver." "Both the Tenpo and the Ansei ichibu-gin were issued in far greater amounts than the chogin of their time, and counted silver became the main currency from then on."

**S8. Saito Osamu 2003**, "Wages, inequality and pre-modern growth in Japan, 1727-1894" (archived `29/29b24c306697`, p.5).
"the central government made their preference explicit that gold should become the standard of money in the national economy. The new policy was first exemplified by the issue in the 1770s of silver coins denominated in a gold unit. The following period witnessed an irreversible decline of the Osaka merchants' control over both credit and commodity markets"

**Reading: ATTESTED.**
- **The legal rates.** They were set by shogunal order in 1609 (50 monme = 4 kanmon), 1700 (60 monme = 4 kanmon) and 1842 (6,500 mon a ryo for copper). Each was a revision to follow the market (S1, S2, S5).
- **Enforcement.** The tools were orders to money changers, such as the 1700 ban on dealing at 58 monme or less, or at 3,900 mon or less. Ōoka summoned the changers in 1736. The shogunate also bought copper (1796) or sold it (1829). Posted town orders banned copper from other provinces (1813, 1842).
- **The direction flipped.** The 1700 rule capped copper's dearness: the market was about 3,700 mon and went to about 2,800 in 1737. The 1842 Edo order and the 1843 Osaka floor (in 0277) propped up cheap copper instead.
- **Punishments are attested only as written in the 1842 order.** The order threatens seizure of the coin and penalties reaching the town officials. I found no record of an actual prosecution.
- **How far and how long the market strayed.**
  - Silver: about 48-50 monme against the legal 60 from 1695 until the Hoei recoinages of 1706-11.
  - Copper: 2,800-3,700 mon against 4,000 around 1700-37. Then 5,000-7,000 from 1769 until the 1842 rate, which itself followed the market. Then about 10,000 by the late 1860s, while the legal 6,500 stood.
- **Fixed by count.** Gold ryo = 4 bu = 16 shu throughout. The counted silver was fixed to gold units: 12 Meiwa five-monme pieces to the ryo (1765, which failed), 8 nanryo to the ryo (1772), 4 ichibu-gin (1837).
- **How that changed the system.** The counted coins tied silver to gold without a market, and weighed silver drained from circulation. That raised the weighed silver's price (50 monme in 1786). By the end of the period the monme survived mostly as a unit of account in Osaka.
- **The changers fought it.** They demanded a 25% premium and took nanryo only one part in four. The shogunate answered with fixed buy and sell allowances and interest-free loans.
- **The nanryo held less silver than its face.** It carried 21.6 monme of pure silver per ryo against 27.6 monme in circulating chogin (already in 412's pass). It was accepted at face value only by force of these measures.

## Q2. Who priced and paid in which metal

**S9. jawiki 金遣** (`https://ja.wikipedia.org/wiki/金遣い`). It cites 田谷 (国史大辞典), 滝沢 and 岩橋, and quotes 『近世風俗志』 (1853).
「『近世風俗誌』に「たとえば米価を唱ふにも京坂は一石の価銀幾十匁と云、江戸は金一両に米幾斗幾升と云」…一般的には伊勢国・美濃国・加賀国を境界として東を金遣・西を銀遣とするが例外もあって厳密な区分は困難である」「関東地方の畑作地帯では金1両を銅銭1貫文（永楽通宝1000枚）とみなす「永」という概念が存在し、それに基づいた金納による年貢徴収の仕組（永高・永取）が確立していた」
(translation) "The Kinsei fūzokushi says 'even in quoting the rice price, Kyoto-Osaka says a koku costs so many tens of monme of silver, Edo says a ryo of gold buys so many to and sho of rice'. ... In general Ise, Mino and Kaga are the border, gold to the east and silver to the west, but there are exceptions and a strict line is hard to draw." "In the upland fields of the Kanto there was the unit ei, which counted 1 ryo of gold as 1 kanmon of Eiraku coin. A system of collecting the land tax in gold based on it (eidaka, eitori) was established."

**S10. jawiki 江戸時代の三貨制度** (archived `c5/c58cdc0ca3f7`).
「「江戸の金遣い」とされる通り金貨は主に江戸を中心として流通し、大名および上級武士が大口取引のために小判を使用した。…秤量銀貨は大坂を中心とする西日本から東北の広い範囲で流通し、銀貨は主に商人が大口取引に用い、商品相場は銀建で表されるのが常であった。大口取引にはこのように金貨および銀貨が用いられたが、一般の小売には銭貨が主として用いられ、庶民は銭貨および稀に豆板銀を手にする程度であった。このような住み分けは決して制度として確立されたものではなく自然発生的に形成されたものであった。」「銭貨は金遣いの地域、銀遣いの地域の両方で通用する貨幣であり…全国通貨としての性格も有した。」
(translation) "As the phrase 'Edo's gold use' says, gold coin circulated mainly around Edo, where daimyo and upper samurai used koban for large transactions. ... Weighed silver circulated from western Japan around Osaka to a wide area including the northeast. Silver was used mainly by merchants for large transactions, and commodity prices were usually quoted in silver. ... Ordinary retail was mainly in copper; commoners handled copper and only rarely bean silver. This division was never set by law; it formed of itself." "Copper passed in both the gold and the silver zones ... it was in effect a national currency."

**S11. 貨幣博物館 常設展示図録 p.39** (`https://www.imes.boj.or.jp/cm/collection/tenjizuroku/mod/book/pageindices/index39.html`).
「高額取引については、江戸を中心とする東日本では金の単位（両・分・朱）で、大坂を中心とする西日本や北陸では銀の単位（貫・匁・分）で、価値が表示されることが多かった。小額取引では、全国的に銭貨の単位（文）が用いられた。東北や西南日本では高額取引にも銭貨の単位が用いられることがあった。」
(translation) "Large sums were usually expressed in gold units (ryo, bu, shu) in eastern Japan around Edo, and in silver units (kan, monme, fun) in western Japan around Osaka and in Hokuriku. Small sums used the copper unit (mon) everywhere. In the northeast and southwest even large sums were sometimes in copper units."

**S12. Kano Yoshiaki (鹿野嘉昭), 「銭匁勘定と銭遣い―江戸期幣制の特色を再検討する―」**, 同志社商学 vol.61 no.1 (`https://doshisha.repo.nii.ac.jp/record/21421/files/034061010002.pdf`). Modern study of the 18th-19th centuries.
「財物ごとに表示・決済貨幣が慣行として定まっていた」「年貢米の売却，幕府御用，江戸詰め費用といった領外取引は幕府貨幣により決済される一方，領内での取引については藩札および銭貨が充当されるなど，領外取引＝幕府貨幣，領内取引＝藩札および銭貨という一種の棲み分けがなされていた」「「銀遣い」の西日本地方所在の大名領国における財物の価格は，小額の物品を除き，基本的には銀貨単位の匁で表示されていた。その一方で，…領内では銀貨が極端に不足していたため…銭貨を用いて，銀建て価格を一定比率でもって銭貨建て価格に変換のうえ代金を支払う」
(translation) "Which money each kind of good was quoted and paid in was fixed by custom." "Transactions outside the domain (sale of tax rice, shogunal business, the costs of Edo residence) were settled in shogunal coin. Those inside it were met with han notes and copper: outside = shogunal coin, inside = han notes and copper." "In western domains of 'silver use', prices except for small goods were quoted in silver monme. But silver was extremely scarce, so people paid by converting the silver price into copper at a fixed ratio."

He adds a fee point in note 45: 「宮津藩においては文政末期以降，銀1匁と銭1匁との比率は常に1.13に固定…1.13という比率はむしろ正貨への交換に随伴する固定手数料率と解釈するのが適切」 (translation: "in Miyazu domain from the late 1820s, 1 monme of silver to 1 'copper monme' was always fixed at 1.13 ... better read as a fixed fee rate on exchange into shogunal coin").

**S13. Iwahashi Masaru (岩橋勝) 2010, 「近世銭匁遣い成立の要因―津軽地方を事例として―」**, 松山大学論集 22(4) (`https://matsuyama-u-r.repo.nii.ac.jp/record/1605/files/KJ00008731859.pdf`). Evidence 1791 (Akita) and the 1860s.
「銅山内の人足賃や扶持，道具代等は，一部銀遣いも見られたが，大半が銭遣いであった。寛政３（1791）年…銀1,039貫匁余が投資され，これをすべて92文相場で銭貨に替え，総額9万貫文近くが掘り方人足の給銭や諸道具費用に充てられた。…人足一人当たりの日雇い銭としては数10文ほどにしかならず，どうしても小額な貨幣が必要とされた」; 「一定額以上の取引には銭建てであっても金貨が使用されたことを意味している。」
(translation) "Mine labourers' wages, allowances and tool costs were partly in silver but mostly in copper. In 1791 ... over 1,039 kanme of silver was invested, all changed into copper at 92 mon [to the monme], and nearly 90,000 kanmon went to diggers' pay and tools. ... Per labourer the day wage was only some tens of mon, so small coin was indispensable." "This means that above a certain size, gold was used even when the sum was quoted in copper."

**S14. jawiki 両替商** (`https://ja.wikipedia.org/wiki/両替商`). Evidence 17th-19th centuries. The 1-2% figure carries no citation on the page.
「慶長14年（1609年）に幕府は三貨の御定相場として「金一両＝銀五十匁＝永一貫文＝鐚四貫文」と定め、…貢納金などに対してはこの換算率が用いられたが、一般の商取引では市場経済にゆだね」「そこで1 - 2%程度の手数料を徴収して両替を行う商売が成立することになる。小判を一分判に、あるいは小玉銀を銭に換えるなど、使い勝手のよい小額の貨幣に両替する場合は切賃（きりちん）と呼ばれる手数料が発生し、少額貨幣から高額貨幣への両替手数料より割増されるのが普通であった。一方、少額貨幣を高額貨幣に両替する手数料が高額貨幣からの手数料より高くなる場合は逆打（ぎゃくうち）と呼ばれ、南鐐二朱判および一分銀を小判へ両替する場合などに逆打が見られた。」「本両替を利用したのは大名、有力商人など大口取引を行う者に限られ、町人などが一般に利用したのは脇両替すなわち銭屋（ぜにや）であった。」
(translation) "In 1609 the official rate ... was used for dues paid to the shogunate, but ordinary trade was left to the market." "So a trade arose of exchanging coin for a fee of about 1-2%. Changing into handier small coin, such as koban into ichibu or bean silver into copper, carried a fee called kirichin. It was usually higher than the fee for changing small coin into large. When changing small into large cost more, this was called gyakuuchi, seen for example in changing nanryo or ichibu-gin into koban." "Only daimyo and big merchants used the main changers (hon-ryōgae); townspeople generally used the side changers, the copper shops (zeniya)."

**S15. kotobank 両替**, 改訂新版世界大百科事典, section by 山口徹 (`https://kotobank.jp/word/%E4%B8%A1%E6%9B%BF-149923`).
「両替屋はこうした変動・錯綜する貨幣流通のなかにあって，手数料（切賃（きりちん），打銭（うちせん））をとって貨幣の両替・売買にあたり，莫大な利益を得た。」
(translation) "Amid this shifting, tangled circulation, changers exchanged and dealt in coin for fees (kirichin, uchisen) and made enormous profits." No rate is given.

**S16. kotobank 銭両替**, 山川日本史小辞典 (`https://kotobank.jp/word/%E9%8A%AD%E4%B8%A1%E6%9B%BF-87509`; the ledger has it under the ID 554431, which resolved to this entry).
「近世に銭の売買・両替を業務とし，手数料を取得した両替屋。概して小資本で，金銀を取り扱う本両替に対しては脇両替とよばれた。…大坂の銭両替は，嘉永年間の規定では，1161人を数え…江戸の銭両替は，1718年(享保3)で584株あり」
(translation) "Changers who bought, sold and changed copper for a fee; generally small capital, called side changers as against the main changers who dealt in gold and silver. ... Osaka had 1,161 copper changers under the Kaei-era (1848-54) rules; Edo had 584 licences in 1718."

**S17. Kobayashi Noburu (小林延人) 2017, 「近世・近代日本貨幣史の基礎的研究」**, 貨幣博物館『常設展示リニューアルの記録』 (`https://www.imes.boj.or.jp/cm/research/kinken/mod/cm_201703kinsei.pdf`).
「大坂では、本両替仲間が金相場会所において銭を売買し、銭1貫文につき銀何匁という銭相場を毎日建てていた。この銭相場が触相場として本両替の得意先に通達され…両替商以外の者も、この大坂銭相場を参照しながら、地域内･仲間内において通用相場を形成した」
(translation) "In Osaka the main changers bought and sold copper at the gold exchange hall and set a daily rate in monme of silver per kanmon. It was sent to their clients as the announced rate ... and others, outside the changers, set their local or guild rates by reference to it."

**S18. Changers' fees in documented cases.**
- **1859 copper recall**, jawiki 寛永通宝: 「幕府は銅一文銭を回収し、銅一文銭一貫文に対し鉄一文銭および天保通寳を差交えて一貫五百四十八文と引換え、四十八文は両替屋に手数料として与えた」 (translation: "the shogunate recalled copper one-mon coins, exchanging each kanmon of copper for 1 kanmon 548 mon in mixed iron coins and Tenpo coins, 48 mon of which went to the changers as their fee"). My arithmetic: 48 on 1,500 is 3.2%.
- **Nanryo dealing allowances**, S6 above: 4 fun and 8 fun of silver per ryo. At 60 monme to the ryo that is about 0.7% and 1.3%, my arithmetic.
- **Fudasashi**, jawiki 札差 (`https://ja.wikipedia.org/wiki/札差`): 「札差が旗本・御家人の代りに俸禄米を受取る手数料を札差料といい、蔵米100俵につき金1分であった。またこれを米問屋に売却する手数料を、売側（うりかわ）といって、同じく100俵で金2分…食用の米を除いて残りの米を当日の米相場で現金化し、手数料を差引いて、現金と米を各屋敷に届けてやる」 (translation: "The fee for collecting stipend rice on behalf of bannermen and housemen was 1 bu of gold per 100 bales. The fee for selling it to rice wholesalers, called urikawa, was likewise set at 2 bu per 100 bales ... they turned the rice not needed for eating into cash at that day's rice price, deducted the fees, and delivered the cash and rice"). That is 3 bu = 0.75 ryo per 100 bales. As a percentage it depends on the rice price; the page gives no bale size or price, so I give no figure.
- **Tax**, kotobank 年貢 (archived `a9/a9c523e3e76f`): 「賦課は石高で示されるが，実際の納入はあらかじめ米・金（銀）の納入割合が決められていた。また米の回送が著しく困難な地方は，石代納と称し全額を貨幣で納入した。」 (translation: "The levy was stated in koku, but the shares to be paid in rice and in gold (silver) were fixed in advance. Where shipping rice was very hard, the whole was paid in money, called kokudai-nō").

**Reading: ATTESTED for the pattern.**
- **By region.** East Japan priced large sums in gold and the Kinai and the west in silver. Rice was quoted per koku in monme in Osaka and as rice per ryo in Edo.
- **Retail and wages.** Retail was in copper everywhere. Small wages were paid in copper: the Akita miners at some tens of mon a day; the Edo craftsmen's 手間銭 in Q4.
- **Wholesale and merchants' accounts.** These were in silver in the west, and in silver notes as monme became a unit of account after 1772.
- **Tax.** Tax was assessed in koku, paid in rice and money in set shares, or all in money where rice could not be shipped. Kanto upland tax was reckoned in ei and paid in gold. The legal rate applied to dues paid to the shogunate.
- **Samurai stipends.** Stipends were paid in rice and turned into cash by fudasashi at the day's rice price.
- **Domain economies.** Outside trade used shogunal gold and silver; inside trade used han notes and copper. Western domains paid silver prices in copper at fixed "copper monme" ratios.
- **Changers.** The main changers (gold and silver) were few and used by big clients. The copper shops were many (584 in Edo in 1718; 1,161 in Osaka c.1850).
- **Fees are ATTESTED ONLY FOR** the 1859 recall (about 3.2%), the nanryo allowances (about 0.7% and 1.3%) and the fudasashi 3 bu per 100 bales. jawiki's "1-2%" for kirichin has no citation, and kotobank names kirichin and uchisen without a rate. Craftsmen's pay in silver: I found no source for it, and that part is SILENT.

## Q3. Did a price depend on the coin?

**S19. Oishi 1966** (as S4). Evidence Edo, 1842.
- **The 8/6 addendum, which exempts silver-priced goods:** 「昨五日御触有之候銭相場金壱両二付六貫五百文替御定被仰渡御座候二付，諸色値段，右釣合を以引下ケ候様…右銭相揚釣合を以，値段為引下…但銀目売之分者調二不及申候以上」
  (translation) "As yesterday's order fixed copper at 6 kanmon 500 mon to the ryo, the prices of goods are to be lowered in proportion ... but goods sold in silver monme need not be surveyed."
- **Oishi on how far the rate moved and the prices were to follow:** 「銭公定相場6貫500文の設定によって引き上げられたのは7〜8％前後であったことが分かる。…もしこの「物価書上」通りに実施されたとしたら，ほぼ銭相場引き上げによって，銭による小売相場は7〜8％ほど引き下げられ…しかし現実にそうなったかどうかは，先述の如く大きく疑問のある」; 「この引下げ値段通りに引下げたというのでなく…目標に今から引下げようというのである。」
  (translation) "The 6,500 fixing raised copper by about 7-8%. ... If carried out as in the returns, copper retail prices would have fallen about 7-8%. ... Whether that happened is, as said, very doubtful." "These are not prices actually cut, but targets they now intended to cut to."
- **His table, as printed** (its text layer is garbled): 「72文 64文」「40文 36文」「56文 52文」「48文 44文」「36文 32文」; palanquin fare 「賃銭748文 700文 0．93」; cuts of 「24文 23文 0．95」「16文 15文 0．93」; row averages 「平均 0．92」 and 「平均 0．90」. The cuts are mostly one 4-mon step.
- **The 1842/5/12 order that came before it:** 「諸色直下ケいたし候者勿論之儀二候得共，価而巳相下リ其品劣リ…」 and Oishi's gloss 「一向に値下げが実行されないのみか，品質をおとしたり，掛目・升目を減らしたりなどする者もある有様」
  (translation) "Lowering prices goes without saying, but some lower only the price and the goods get worse ..." "Not only were prices not cut at all; some lowered quality or cut weights and measures."

**S20. Iwahashi 2010** (as S13). Tsugaru, 1837-38, from the diary 「永宝日記」.
「「米も小売止候ニ付，銭ニて壱俵四十匁，預りニて六十匁致候」（p.87）と発行後2カ月余で額面の3分の2の札価となっている。翌年正月には「炭小表銭ニて七分，預りニて弐匁五分」…額面の28％にまで下落」
(translation) "'Rice retail having stopped, a bale is 40 [copper] monme in coin, 60 monme in [Miyazaki] notes': two months after issue the notes passed at two-thirds of face. The next first month: 'a small bale of charcoal, 7 fun in coin, 2 monme 5 fun in notes', down to 28% of face."

**S21. jawiki 寛永通宝** (as S3). Edo, 1768-1868.
- **Four-mon coin and prices:** 「これが発行されたころから、物の値段に16文、24文など4の倍数が多くなり、1串に5つの団子を5文で売られていたのが、1串4つで4文になったという。また…4文均一の「四文屋」というのもあった。」 This sentence has no footnote.
  (translation) "From about the time it was issued, prices of 16 mon, 24 mon and other multiples of 4 became common. Dango sold 5 to a skewer for 5 mon became 4 for 4 mon, it is said. ... There were also 'shimonya' selling everything at 4 mon."
- **Coins of the same face circulating at different values:** 「安政年間に入ると當百銭、真鍮銭、一文小銭などの相場にはそれぞれ差異が生じ、幕府はたびたび額面通り滞りなく通用するよう触書を出すが市場において差別通用が止まず、慶應元年（1865年）閏5月、ついに天然相場を容認し江戸市中両替屋で銅小銭、真鍮銭に対し増歩通用を認めるに至った。…鉄一文銭を基準として…文銭および耳白銭：6文 その他寛永通寳銅一文銭：4文 寛永通寳真鍮當四文銭：12文 文久永寳當四文銭：8文 慶應3年（1867年）、幕府はすべての銭貨を天然相場に委ねる」
  (translation) "From the Ansei era (1854-60) the 100-mon coin, the brass coin and the small one-mon coin each went at different rates. The shogunate repeatedly ordered them to pass at face, but discrimination in the market did not stop. In the intercalary fifth month of 1865 it finally accepted the natural rates and allowed Edo changers to pay premiums on copper and brass coins. Against the iron one-mon as the base: Bunsen and Mimijiro coins 6 mon; other copper one-mon 4; brass four-mon 12; Bunkyu four-mon 8. In 1867 it left all copper coins to the natural rate."
- **The 1868 decree:** 1868 (太政官布告第306号): 「寛永通寳銅一文銭：12文 寛永通寳真鍮當四文銭：24文 文久永寳當四文銭：16文 天保通寳當百文銭：96文」.

**S22. jawiki 天保通宝** (`https://ja.wikipedia.org/wiki/天保通宝`). Evidence 1835-1865.
「貨幣価値は100文（1/40両）とされ…そのため実際には80文（1/50両）程度で通用し、銭相場の下落により安政年間には1/60両、万延年間には1/100両と…減価を重ねていった」「この慶応元年の改正にも批議があり、銭貨通用価格の改正がさらなる物価の騰貴を招いた」
(translation) "Valued at 100 mon (1/40 ryo) ... in practice it passed at about 80 mon (1/50 ryo). As copper fell it lost value further, to 1/60 ryo in the Ansei era and 1/100 ryo in the Man'en era (1860-61)." "The 1865 revaluation was also criticized; changing the coins' values brought further rises in prices."

**S23. Debased and damaged coin.**
- **Kobayashi 2017**, on 1705: 「宝永2年(1705)10月、使用に支障のない切小判を、両替商が歩銀(手数料)をとって両替することを禁じ」 (translation: "in 1705 changers were forbidden to charge a fee for changing cut koban that were still usable").
- **jawiki 三貨制度**, on Genroku: 「高品位の慶長金銀は退蔵され、低品位の元禄金銀のみ流通する…品位の高い貨幣に対し増歩通用を認めて初めて旧貨も流通した。…享保期に品位の異なる元禄銀、宝永銀および慶長・正徳銀が混在通用した際、それぞれ銀含有量に基づいて通用価値が決まった」 (translation: "the good Keichō coin was hoarded and only the poor Genroku coin circulated ... the old coin circulated only once a premium was allowed on it. ... In the Kyōhō era (1716-36), when Genroku, Hōei and Keichō/Shōtoku silver of different fineness circulated together, each passed at the value of its silver content").

**S24. Sengoku 撰銭 (before 1600).**
- **jawiki 撰銭** (`https://ja.wikipedia.org/wiki/撰銭`): 「粗悪な銭貨は鐚銭または悪銭（あくせん）と呼ばれ、一時は鐚銭4枚で一文とする取り決まりがなされる[2]など」; 「織田信長は、1569年（永禄12年）から翌年にかけて撰銭令を発令…銭貨10種を品質によって3段階に分類してそれぞれの交換相場を定め」 (translation: "these bad coins were called bita or akusen; at one time it was agreed that 4 bita made one mon"; "Nobunaga issued 撰銭 laws in 1569-70 ... classing ten kinds of coin into three grades by quality and fixing a rate for each").
- **Kobayashi 2017**: 「悪銭として排除された貨幣を四段階にわけ、打歩(手数料)をつけて通用させた。…中近世移行期には①もっぱら少額取引に銭を用い、②悪貨には打歩を付して通用させる、という形に変化」 (translation: "he divided the rejected coins into four grades and made them pass with a premium (uchibu) ... in the transition from medieval to early modern, the practice became: copper used only for small transactions, and bad coin passing at a premium").
- **jawiki 撰銭令** (`https://ja.wikipedia.org/wiki/撰銭令`): 「大内氏掟書」には自分への貢納銭は撰銭し、庶民は撰銭するなと記している (translation: "the Ōuchi house code says dues paid to the house may be sorted for good coin, but commoners must not sort").

**Reading: ATTESTED ONLY FOR the following cases.**
- **Edo 1842.** The ordered cuts applied only to goods priced in copper; silver-priced goods were exempt. Copper prices did not follow the copper rate by themselves: the shogunate had to order cuts of about 7-8%, and Oishi doubts they were made. Sellers adjusted quality and measures rather than the copper price. The planned cuts came in single 4-mon steps.
- **Tsugaru 1837-38.** Goods carried a price in coin and a price in han notes, with notes at two-thirds of face and then 28%.
- **Edo 1854-68.** Copper coins of the same face value passed at different values, legalized in 1865 (copper one-mon at 4 iron mon, brass four-mon at 12) and raised again in 1868. The Tenpo coin passed at about 80 rather than 100.
- **Recoinages.** Full-weight old coin passed only with a premium.
- **Sengoku.** Bad coin passed at a discount, 4 bita to one good mon at one point, under Nobunaga's grading of 1569.
- **The four-mon rounding** (prices moving to multiples of 4) has no citation on jawiki. I found no measured figure for how fast copper-quoted shop prices followed a rate move outside 1842, and that part is SILENT.

## Q4. Who won and lost

**S25. Oishi 1966** (as S4).
- **Who used copper:** 「銭は…大名・武士・商人達の通貨というより，その下に存在する最下層たる庶民の通貨であるといえよう。したがって銭相場の低落は単純な通貨価値の低落といった問題ではなく，江戸時代社会構成の最下層に位置する庶民大衆をなかんつく難儀させるところの経済現象であった。」
  (translation) "Copper was the money not of daimyo, samurai and merchants but of the lowest commoners beneath them. So a fall of copper was not a simple fall in a currency's value, but something that bore hardest on the common people at the bottom of Edo society."
- **The Tanuma years and unrest:** 「田沼期は庶民通貨たる銭相場の下落という面からでも，庶民生活の困窮は拍車をかけられたといえよう。田沼期の一揆，打ちこわしなどの激化の原因は，単に飢饉などのみではなく，この面からも求むべき」
  (translation) "In the Tanuma period (c.1767-86) commoners' distress was worsened also by the fall of copper, their money. The sharpening of risings and urban riots then should be explained not by famine alone but by this too."
- **The 1842/5/12 order on wages:** 「諸職入[人]手間銭之儀去ル申年巳来，米価下落いたし候而茂不引下ケ趣二有之，右者早ミ取調引下ケ候様可致」
  (translation) "Craftsmen's wages in copper have not come down although rice has fallen since the year of the monkey [1836]; investigate and lower them at once."
- **The 1813 order** (in S4): small merchants dealing in copper suffered when copper fell.

**S26. Saito Osamu 1993, 「幕末－明治の賃金変動再考」**, 経済研究 44(4) (archived `d9/d9a8d821ea4f`; the page is printed in two columns, rejoined by me).
「開港後の金流出による1860年代の急激な金銀比価の変化，すなわち銀建インフレ率が両建インフレ率を大幅に上回るようになった分だけ，実質賃金の下落率は西日本で高く，東日本で低くなるからである．」
(translation) "Because of the sharp change in the gold-silver ratio in the 1860s after the opening and the outflow of gold, inflation in silver terms far exceeded inflation in ryo terms, and by that much the fall in real wages was steeper in western Japan and shallower in the east."

「三井京本店のように貨幣賃金が固定的で，物価上昇とともに実質賃金が直線的に低下する極端なケースは他にはみられないものの，全体として実質賃金の低下傾向は確認されている」; 「スポット・マーケット的な労働市場を通じて雇入れられる日雇や類似の労働者の場合には，そのような配慮は期待できなかった…熟練・不熟練労働者の賃金収入上の格差は，物価が上昇する時期には…拡大した」
(translation) "No other case is as extreme as the Mitsui Kyoto head shop, where money wages stayed fixed and real wages fell in a straight line as prices rose, but a falling trend of real wages is confirmed overall." "Day labourers hired in a spot market could expect no such allowances ... the gap between skilled and unskilled earnings widened in periods of rising prices."

**S27. Kobayashi 2017** (as S17).
「元文の改鋳では…増歩方式を採用し…改鋳益は旧貨幣の保有者に帰属することとなる。…慶長金･享保金100両につき元文金165両の割合…貨幣供給量は40％増加し、新貨は市場に流入して物価を急速に引き上げ」「文政および天保の改鋳は…等価交換方式が採用され…改鋳益は550万両…天保の改鋳による…改鋳益は500万両」「[万延の改鋳で]貨幣供給量は150％も増加…物価は一挙に高騰した。…文久3年(1863)…改鋳益は幕府の歳入総額に対して68％」「正徳…貨幣供給量は減少し、米価をはじめとする物価は下落した。これは、米納年貢を基軸とする幕府財政・藩財政の収入減少にもつながった」
(translation) "The Genbun recoinage used the premium method ... so the recoinage gain went to holders of the old coin. ... 165 Genbun ryo for 100 Keichō/Kyōhō ryo ... money supply rose 40%, and prices rose fast." "The Bunsei and Tenpo recoinages used exchange at par ... gains of 5.5 million ryo (Bunsei) and 5 million (Tenpo)." "[Man'en, 1860] money supply rose 150% ... prices jumped at once. ... In 1863 the recoinage gain was 68% of the shogunate's total revenue." "[Shōtoku, 1714] money supply shrank and prices, rice above all, fell. This cut the income of shogunal and domain finances, which rested on land tax paid in rice."

**S28. jawiki 三貨制度** (as S2), on rice and samurai: 「元禄の吹替えによる貨幣品位の低下はこれに追い討ちをかけ、以後文政年間あたりまで金1両が米1石前後を維持した。」 (translation: "the Genroku debasement added to this, and from then until about the Bunsei era a ryo stayed at about 1 koku of rice"). This bears only indirectly on 米価安の諸色高.

**Reading: ATTESTED qualitatively; measured only for 1842.**
- **Losers when copper fell.** Commoners who earned and spent copper and small copper-trading merchants (the order texts of 1796, 1813 and 1842). Oishi links the Tanuma-period fall of copper to the risings of those years.
- **Wages in the 1830s.** Edo craftsmen's copper wages did not fall when rice fell after 1836, so on that index they gained, and the shogunate ordered them cut.
- **Wages in the 1860s.** Saito shows money wages lagging prices, worse for unskilled spot labour. The real-wage fall was steeper in the silver west than the gold east, because of the gold-silver swing.
- **Recoinages.** Under Genbun's premium method holders of old coin kept the gain. Under Bunsei, Tenpo and Man'en the shogunate took it: 5-5.5 million ryo, and 68% of 1863 revenue.
- **Samurai.** Those on rice stipends lost from the Shōtoku deflation and rice cheapness, a point made at the level of domain finances.
- **The only measured effect.** In 1842 copper was raised about 7-8% by decree and copper prices were to be cut the same; Oishi doubts the cuts happened.
- **An illustration, not a finding.** A fixed mon wage held while copper went from about 4,000 to about 6,000 mon a ryo (1760s to 1778) lost a third of its value in gold. That is my arithmetic, and it holds only for goods priced in gold.
- **What people did, as attested.** Hoarding good coin (1736, Genroku), refusing or discounting coin (the 1854-65 差別通用, 撰銭), changers' resistance (the nanryo), and riots (Oishi). I found no petition from wage earners. SILENT: real wages in copper for the Meiwa-An'ei years, a measured tax burden, and a 太宰春台 passage (the page that would have held it came back as HTML).

## Leads not followed
- Re-archive Oishi 1966 (the archive holds only 406 stubs) and archive the Iwahashi 2010, Kano and Kobayashi 2017 PDFs.
- 新保博's study of the Osaka copper rate (cited by Kobayashi) and 新保・斎藤 1989 on real wages.
- 岩橋勝 「近世三貨制度の成立と崩壊」 and 『近世貨幣と経済発展』 ch.3 (copper rates east and west compared).
- 三上隆三 on the four-mon coin and nanryo (Wakayama repository record 1035 refused the connection).
- Crawcour & Yamamura 1970, "The Tokugawa Monetary System, 1787-1868," EDCC 18(4).
- 中川すがね on copper changers.
- Takatsuki and Mikami on the Osaka money market; 大塚英樹 on copper rates; 作道洋太郎 (the Nipponica 両替 entry, on the same kotobank page, not read in full).
- Kuroda Akinobu on complementarity among monies (Financial History Review 2008).
- 浦長瀬隆 on land-sale deeds by currency (Kokumin Keizai Zasshi, 1999-2002).
- 太宰春台『経済録』 on who gains from cheap rice; the Kyoto kronso PDF returned HTML.
- The Edo-Tokyo Museum's 1853 day-labourer wage ledger (edohakuarchives detail-303536), for the currency wages were paid in.
- The 1865 premium order itself (三上 1996; 滝沢 1996) and the 1773 nanryo order text.

Sources:
- [jawiki 両替商](https://ja.wikipedia.org/wiki/両替商)
- [jawiki 撰銭](https://ja.wikipedia.org/wiki/撰銭)
- [jawiki 撰銭令](https://ja.wikipedia.org/wiki/撰銭令)
- [jawiki 寛永通宝](https://ja.wikipedia.org/wiki/寛永通宝)
- [jawiki 天保通宝](https://ja.wikipedia.org/wiki/天保通宝)
- [jawiki 金遣](https://ja.wikipedia.org/wiki/金遣い)
- [jawiki 匁銭](https://ja.wikipedia.org/wiki/匁銭)
- [jawiki 札差](https://ja.wikipedia.org/wiki/札差)
- [jawiki 南鐐二朱銀](https://ja.wikipedia.org/wiki/南鐐二朱銀)
- [jawiki 一分銀](https://ja.wikipedia.org/wiki/一分銀)
- [jawiki 御定相場](https://ja.wikipedia.org/wiki/御定相場) (archived)
- [jawiki 三貨制度](https://ja.wikipedia.org/wiki/三貨制度) (archived)
- [Oishi 1966](https://glim-re.repo.nii.ac.jp/record/202/files/keizai_2_2_69_128.pdf)
- [Iwahashi 2010](https://matsuyama-u-r.repo.nii.ac.jp/record/1605/files/KJ00008731859.pdf)
- [Kano, 銭匁勘定と銭遣い](https://doshisha.repo.nii.ac.jp/record/21421/files/034061010002.pdf)
- [Kobayashi 2017, IMES](https://www.imes.boj.or.jp/cm/research/kinken/mod/cm_201703kinsei.pdf)
- [IMES 図録 p.39](https://www.imes.boj.or.jp/cm/collection/tenjizuroku/mod/book/pageindices/index39.html)
- [IMES 図録 p.42](https://www.imes.boj.or.jp/cm/collection/tenjizuroku/mod/book/pageindices/index42.html)
- [kotobank 両替](https://kotobank.jp/word/%E4%B8%A1%E6%9B%BF-149923)
- [kotobank 銭両替](https://kotobank.jp/word/%E9%8A%AD%E4%B8%A1%E6%9B%BF-87509)
- [kotobank 年貢](https://kotobank.jp/word/年貢-111662) (archived)
- [Saito 1993, 経済研究 44(4)](https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1995/keizaikenkyu4404330.pdf) (archived)
- [Saito 2003, Hi-Stat D03-02](https://hi-stat.ier.hit-u.ac.jp/research/discussion/2003/pdf/D03-02.pdf) (archived)
