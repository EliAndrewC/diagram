# Feature 230 - research

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## R1 The state of the record before the pass (2026-09-12)

What the engine draws at the head of a comb field today, read from the code and from Inashiro's manifest:

| piece | where | what it is |
|---|---|---|
| the intake point | `hamletgen/water.py` `head_sluice` | 36% of the canvas up the fall from the center, plus a rolled lateral offset (`HEAD_OFFSETS`) |
| the brook | `hamletgen/water.py` `feed_brook` | a fixed 420 px run ending AT the intake, one 26 px bow, bearing swung off the fall only to clear the crop; recorded as a `streams` record with no `to` |
| the head race | `waterfields/comb.py` `_comb_skeleton` | a hardcoded 90 px straight continuation down the fall from the intake to the fork (the bunsuiguchi); `role: main` |
| the drawn join | Inashiro's PNG | the 7 px stream meets the ~5 px head race at a rounded cap, 90 ft above the fork, on one straight line - no weir, gate or bend |

Neither constant carries a comment or a research entry. `settlements/water.md` line 12 (the Ikegami rule) says the brook
"reaches the sluice, and there BECOMES the irrigation channel - it hands off to the comb and stops", a rule that came
from the GM's catch of two overlapping water lines on the first Ikegami draft, not from research. `research/water.html`
"Drawn width is RANK" mentions "ponding above the weir" in passing as the physical reading of the width step, and
`research/fields.html` "The communal-system floor" lists "weir, head-race, canal fork" as the communal works, with no
footnote on the weir. No section of the record asks where a stream becomes a ditch.

At the foot: the collector (`role: drain`) ends at its outfall; with `water_sink="pond"` the run to the tameike is drawn
by `field_channel` at the drain's width and recorded as a `channels` record `frm: drain -> to: pond` (class `field
ditch`); with `water_sink="offmap"` the run is drawn by `stream` at 8 px and recorded in `streams` `frm: drain -> to:
offmap` (class `stream`). Inashiro and Mizuguchi drain to a pond; Sawada and Kashikawa off the frame; Kuwabata is a
pond-fed polder.

The class: one `FieldDitch` class covers `field_ditches` and `channels` alike, its explanation written about supply
(the comb layout, the taper, sparseness). Every `field_ditches` record carries `role` (`main`, `branch`, `drain`; a
polder adds `lateral`, and `seg` names its ring segments), and the drain is painted `#7C9EB0` against the supply net's
`#6C9CBE` at the one emit loop in `fields/comb.py`.

## R2 The pass

Two background Opus readers, dispatched 2026-09-12, one attempt per host, verbatim passages with URLs. The China
reader's report follows the Japan reader's below when it lands. Passages are as the readers transcribed them
(WebFetch could not parse the Japanese PDFs; the reader read each saved file page by page).

### R2a Japan-first reader (58 tool uses, 14 min)

**Q1 - what marks the take-off, what a premodern small-stream weir was, which bank the canal leaves - FOUND.**

- ja.wikipedia 堰 (READABLE): 「堰（せき、英語: weir）とは、河川の流水を制御するために河川を横断する形で設けられるダム以外の構造物で堤防の機能をもたないものをいう」 - "A seki (weir) is a structure other than a dam, built across a river in order to control its flowing water, and which does not have the function of an embankment." 「取水堰 - 河川水位を調節するための堰で灌漑用水、水道用水、工業用水、発電用水などを取水するための堰」 - "Intake weir - a weir for regulating the river water level, for taking irrigation water, waterworks water, industrial water, power-generation water and so on." 「常時（および洪水時に）水を堰の上から越流させるタイプの堰は洗堰（あらいぜき）と呼ぶこともある」 - "A weir of the type that lets water overflow over the weir at all times (and at flood time) is sometimes called an araizeki."
- ja.wikipedia 頭首工 (READABLE): 「河川湖沼から用水路に農業用水を引き入れるための構造物を総称して頭首工（とうしゅこう）という」 - "Structures for drawing agricultural water from rivers and lakes into an irrigation canal are collectively called toshuko (head works)"; components 「取水堰、取水口、付帯施設（沈砂池、魚道、舟通し等）」 - "intake weir, intake mouth, ancillary facilities (settling basin, fishway, boat passage, etc.)". Modern.
- https://www.japanriver.or.jp/merumaga/koborebanashi/bn/no21.pdf (松田芳夫「河川こぼれ話」21 頭首工と取水堰; READABLE): 「河川の水面を高くして取水の便を良くするために、河川を横断する堰（取水堰）を設けることは、堰の構造や規模を別にして古くから行われています。水田に取水するための小渓流の堰の原型は弥生時代に見られるといいますから、二千年以上の昔から堰は造られてきたわけです。」 - "Setting a weir (an intake weir) across a river so as to raise the water surface and make taking water convenient has been done since ancient times, whatever the weir's structure or scale. The prototype of the weir on a small mountain stream for taking water into paddy fields is said to be seen in the Yayoi period, so weirs have been built for more than two thousand years." 「もともとは、農業用水を河川から取水するための一連の施設、堰、取水口（堤防を横切るときは樋管）、沈砂池、分水工などの施設の総称だったのですが、時代とともに主要な施設としての堰が主役になり頭首工の名も堰が独占してしまうようになりました。」 - "Originally it was the collective name for a series of facilities for taking agricultural water from a river - the weir, the intake mouth (a culvert pipe where it crosses the embankment), the settling basin, the division works and so on - but with time the weir, as the principal facility, took the leading role, and the name toshuko came to be monopolized by the weir."
- https://www.maff.go.jp/j/nousin/attach/pdf/tousyukou-3.pdf (MAFF 土地改良事業計画設計基準 設計「頭首工」付録技術書, ch. 1 頭首工の歴史的経緯, pp. 76-85; READABLE): 「古い時代においては、技術はもちろんのこと材料もみるべきものがなかったので、取水堰はほとんど設けずに自然取入れとし、自然取入れの可能な場所を求めて取入口を求めて導水路を開削するといったものが多く、水位の堰上げあるいは河川内導水を必要とする場合は取水期だけ一時的に役立つ仮設の堰を設けていたところもある。いずれも半川締切が多かった。」 - "In old times, neither technique nor materials were worth much, so in many cases no intake weir was built at all - water was taken naturally, a place where natural intake was possible was sought for the intake mouth, and a conveyance canal was cut; where raising the water level or conveying water within the river channel was necessary, there were places that set up a temporary weir useful only for the intake season. In either case, half-river closures were common." 「これには、牛枠・蛇籠・そだ工を用いてそれぞれ単独に使用したり、これらを組合わせてさらに土砂・礫を被覆したものがある。例えば、岡山県高梁川湛井堰（1183年築造）は、木枠に詰石した底枠と上枠からなり、延長約230mの全川締切り斜め堰である。ミオ筋部の上枠は非かんがい期には洪水対策・土砂掃流の目的で撤去し、かんがい期に毎年設置していた。堰から圦樋（取入口）に導水するため、巻石・小波戸を設けて、増水時には水勢を和らげ圦樋を保護する役割を果たしていた。」 - "For these, ox-frames (ushiwaku), gabions (jakago) and brushwood works (sodako) were used singly, or combined and then covered with earth and gravel. For example the Tatai weir on the Takahashi River in Okayama Prefecture (built 1183) consists of a bottom frame and an upper frame of timber packed with stone, and is an oblique weir closing the whole river, about 230 m long. The upper frame at the thalweg was removed in the non-irrigation season for flood countermeasures and to sweep out sediment, and was installed anew every year in the irrigation season. To lead water from the weir to the iri-hi (intake mouth), wrapped stone and small breakwaters were provided, which served to soften the force of the water at high water and protect the intake." 「いずれの材料を使用しても当時の技術では河川の大洪水に対して永久的に耐えることは困難であり、これを少しでも緩和するために、ほとんどの堰は斜め堰（斜め湾曲堰）で、単位幅当たりの洪水越流量を少なくし決壊を少なくするように工夫されてきた。」 - "Whatever material was used, with the technology of the time it was difficult to endure a great river flood permanently, and to mitigate this even slightly almost all weirs were oblique weirs (obliquely curved weirs), contrived so as to reduce the flood overflow per unit width and reduce breaching." Quoting 上野英三郎他「土地改良論」(1902): 「頭首工は一般に河が山間部より出る所に置くを可とす」 - "It is best to place the head works generally where the river issues from the mountains."
- https://www.jsidre.or.jp/wordpress/wp-content/uploads/2023/12/ouyouR5_tokubetsukoen.pdf (三輪弌「川の流れの原理に基づく河川取水」2023; READABLE): 「自然取水　みお筋が沿っている河岸に取水口を設置する。」「固定堰　河川取水位を安定させるため横断構造物の設置する。」 - "Natural intake: the intake mouth is set on the bank along which the thalweg runs." / "Fixed weir: a transverse structure is installed in order to stabilize the river intake water level." 「古来の堰の多くは取水口から斜め上流方向に長く延ばした「斜め堰」であった。」「斜め堰は，淵の深みを避け河床が浅くなった瀬を堰き止めて取水口に導く。洪水時には高流速域を外した位置に堰があるので，破壊されにくいという利点も持っている。」 - "Many of the weirs of old were 'oblique weirs', extended long in the diagonally upstream direction from the intake mouth." / "An oblique weir avoids the depth of the pool and dams the riffle where the bed has become shallow, leading water to the intake mouth. At flood time the weir lies at a position off the high-velocity zone, so it also has the advantage of being hard to destroy." 「自然取水の場合には，河川流量が減少して取水位が低下すると所要流量が取水できない。堰を設けることで取水位を維持する。」 - "In the case of natural intake, when river discharge falls and the intake level drops, the required discharge cannot be taken. By providing a weir, the intake level is maintained."
- https://zoukou.life.shimane-u.ac.jp/ruraleng/shisetsuken/12kougisiryou/15.pdf (Shimane University rural-engineering lecture, 「3. 頭首工」 pp. 121-130; READABLE): 「頭首工とは、河川より必要な農業用水、その他の用水を用水路に取り入れる目的で設置する施設の総称であり、取入口、取水堰、付帯施設、管理施設から構成されている。」 - "Toshuko is the collective name for facilities installed for the purpose of taking necessary agricultural water and other water from a river into a canal, and consists of the intake mouth, the intake weir, ancillary facilities and management facilities." 「戦国末までの取水施設は木枠に石詰めを基本とした小規模なものが多かった。」 - "Intake facilities up to the end of the Sengoku period were mostly small-scale, based on timber frames packed with stone." 「これには片岸取入と両岸取入がある。受益地が片岸にある場合は受益地側の取入に良好な地点に取入口を設ける。…渓流河川では片岸取入にする。急流河川においても片岸取入とする。緩流河川でも片岸取入を原則とする。」 - "There are one-bank intake and both-bank intake. Where the benefited land is on one bank, the intake mouth is provided at a point good for intake on the side of the benefited land. ... On torrent rivers, one-bank intake is used. On steep rivers too, one-bank intake is used. On gentle rivers, one-bank intake is the rule." 「自然取り入れの場合はミオ筋が河岸に接して，水深が大きく，流れが安定している所で，河川水位が設計水位より常に高い位置であることが必要である。取水堰のある場合は水位を取水堰で調節するのでミオ筋が河岸に接している地点を選べばよい。一般に取入口は土砂吐に接して設けられる。」 - "In the case of natural intake it is necessary that the thalweg touch the bank, that the depth be large and the flow stable, and that the river level always be higher than the design water level. Where there is an intake weir, the level is regulated by the weir, so it suffices to choose a point where the thalweg touches the bank. Generally the intake mouth is provided adjoining the sand sluice."
- kotobank 井堰 (READABLE, thin): 「水を他に引くために、土や木などで川水をせきとめた所」 - "A place where river water is dammed with earth, timber and the like in order to draw the water elsewhere."

**Q2 - does the stream continue; was a brook ever wholly taken - PARTIAL.**

- MAFF 計画「農業用水（水田）」技術書 https://www.maff.go.jp/j/nousin/noukan/tyotei/kizyun/attach/pdf/nougyouyousui_suiden-1.pdf (1.1(2) 江戸期の水田と用水の開発; READABLE): 「特に、農業用水が不足する干ばつ時には、山地流域から流出する水が全て農業用水に取入れられるばかりでなく、一つの用水地区から河川に還元流入する排水も下流の用水によって全量使用されることになり、流域レベルで水資源は徹底的に利用された。」 - "In particular, in a drought when agricultural water is short, not only is all the water flowing out of the mountain catchment taken into agricultural water, but the drainage returning from one irrigation district into the river is also used in its entirety by the irrigation downstream, so that at the basin level the water resource was exhaustively used." 「旧河川を利用した用排兼用水路のように自動的に用水の反復利用が行われる場合のほか、排水を用水路に戻したり、排水をそのまま用水として使用したりするための施設が建設されるなどの結果、全ての水田かんがい地区内には、無駄な水を一切出さない、極めて高い水利用効率を実現する徹底的な用排反復利用システムができあがった。」 - "Besides cases where repeated use of the water happens automatically, as with combined irrigation-drainage canals using an old river course, facilities were built for returning drainage to the irrigation canal or using drainage directly as irrigation water, and as a result, within all paddy-irrigation districts a thoroughgoing irrigation-drainage reuse system was completed that lets out no wasted water at all and realizes an extremely high water-use efficiency." (Edo section of a modern standard; catchment and basin scale.)
- MAFF tousyukou-3.pdf (1.6(5) 石井樋, 1615): 「取水堰には戸立て（角落しゲート）を設けて洪水と土砂を排除し、象の鼻・天狗の鼻・亀石の機構で水流を迂回させて石井樋で取水し、余水は島と井樋の間から本流に戻している。」 - "The intake weir was provided with totate (stoplog gates) to expel flood and sediment; the water flow was made to detour by the mechanism of the Elephant's Nose, the Tengu's Nose and the Turtle Stone, water was taken at the Ishi-ibi, and the surplus water is returned to the main river from between the island and the sluice."
- jsidre 2023 slide 3: 「全面可動堰　河道全面に可動堰ゲートを配置する。取水時はゲート閉鎖して取水し，洪水時にはゲートを開放して洪水を流下させる。」 - "Fully movable weir: movable weir gates are placed across the whole channel. At intake time the gates are closed and water is taken; at flood time the gates are opened and the flood is let flow down." (modern)
- Tabayashi 1987 p. 51 (English): "Torrent irrigation occurs in terraced paddy field locations in mountains, sometimes on landslide areas (TAKEUCHI, 1984, pp. 80-261). Small streams are dammed and the water is conducted through small canals usually for short distances and on gentle slopes."
- https://www.asaza.jp/activity/yatsuda2/ (NPO page on yatsuda, present day; READABLE): 「天の恵みであるこの水をみんなで大切に使うために、湧きだす場所にはため池が作られています。ため池の下には谷津田があります。」「大切に使った水はその後、川へ流れ込み、やがて湖へと流れます。」 - "So that everyone may use this heaven-sent water carefully, a reservoir pond is made at the place where it issues. Below the pond are the yatsuda paddies." / "The water, after being used carefully, then flows into the river and eventually into the lake."
- ja.wikipedia 谷戸: absent on how the water is led in or whether a stream survives.
- Reader's verdict: surplus and flood are deliberately passed down the river at a weir; at basin scale in Edo drought all runoff was taken up; NO page attests one small brook taken wholly so that nothing continues below the intake.

**Q3 - intake to first division; settling reach - PARTIAL.**

- https://www.maff.go.jp/j/nousin/attach/pdf/tousyukou-79.pdf (ch. 20 沈砂池, p. 575; READABLE): 「沈砂池は、取入口に続いて、用水路の始点に設けるようにするのが一般的であるが、やむを得ない場合には、なるべく取入口に近い適当な場所に設ける。」 - "It is general to provide the settling basin immediately following the intake mouth, at the starting point of the canal; where unavoidable, it is placed at a suitable spot as near the intake mouth as possible." No metric distance anywhere in the chapter.
- Shimane 15.pdf: 「取水庭は取入口から導水路入口までの水流を滑らかにするために設ける漸縮の取付け部で、導流壁を設けて偏流を避ける。」 - "The intake court is a gradually contracting connecting section provided to smooth the flow from the intake mouth to the entrance of the conveyance canal; guide walls are provided to avoid skewed flow." 「取入口の流入流速は 0.6～1.0m/sec を標準としている。」 - "The inflow velocity at the intake mouth is standardized at 0.6-1.0 m/sec."
- Tabayashi 1987 p. 57: "Excavations at Toro in Shizuoka Prefecture uncovered third century paddy fields totaling 7.5 hectares and irrigated by a canal more than 370 meters long." p. 57: "Small streams from ravines served for irrigation. Archaeologists have unearthed intake dams that once stretched across streams 10 meters wide, and irrigation canals with diversion devices (MASAOKA, 1983)."
- Reader's verdict: the settling basin sits at the canal's start; no source gives a length from intake to first division - a site variable.

**Q4 - the intake angle - NOT-FOUND.** No term 取水角/取入角, no degrees. Position rules instead: MAFF tousyukou-3.pdf p. 81 (羽根川頭首工, 1974): 「…取入口の位置を河川湾曲部凹岸側中央直下流付近に選定したことで土砂の流入が少なく成功している。」 - "...selecting the position of the intake mouth near immediately downstream of the middle of the concave-bank side of a river bend has succeeded in giving little sediment inflow." Plus the oblique weir running diagonally upstream from the intake (jsidre slide 15, above). The only degree figures (10, 40-60, 45) are internal to a settling basin.

**Q5 - 用水路 / 排水路 / 用排水分離; where a drain discharged - FOUND.**

- ja.wikipedia 用水路: 「用水路（ようすいろ）は、農業用灌漑や上水道、工業用水道などのために水を引く目的で造られた水路である。」 - "A yosuiro is a channel made for the purpose of drawing water for agricultural irrigation, waterworks, industrial water supply and so on."; a purely drainage channel (放水路) is 「通常は用水路に含まない」 - "normally not included in yosuiro".
- MAFF nougyouyousui_suiden-1.pdf, 図-1.1 the three irrigation types by name: 「ア. 田越しかんがい」「イ. 用排兼用型かんがい」「ウ. 用排分離型かんがい」 - "a. Field-to-field (over-the-bund) irrigation / b. Combined irrigation-drainage type / c. Separated irrigation-drainage type". 1.1(7): 「ほ場整備事業では、用水路と排水路を分離して独立に配置し、1枚ごとに用水の取入口と排水口を付けること、排水路は田面下1m程度と十分に深くして乾田化を図るのが標準的な方式である。…」 - "In field-consolidation projects, the standard method is to separate the irrigation canal and the drainage canal and lay them out independently, to give every single field its own irrigation inlet and drainage outlet, and to make the drainage canal deep enough - about 1 m below the field surface - to achieve dry-field conditions. ..." 7.3(2)ア: 「一般に、用排水が分離され、乾田化が進むと、…耕区ごとに独立した水利用になることで残水は直接排水路に排水されて反復利用の機会は少なくなり、…用排水を分離する場合には用水量は一般に増加する。」 - "In general, when irrigation and drainage are separated and dry-field conversion advances, ... because water use becomes independent for each plot, residual water is drained directly into the drainage canal and the opportunity for repeated use decreases; ... where irrigation and drainage are separated, the water requirement generally increases."
- Tabayashi 1987 p. 46: "The canal network extending widely over the area of paddy fields supplied irrigation water to paddies and received discharge from them." p. 47: "Irrigation and drainage canals were separated and arranged along farm roads (Figure 3-b)." p. 61: "The activities were incorporated into Farm Consolidation Projects begun in 1963. ... with a road, an irrigation channel, and a drainage channel adjacent to each block." p. 60: "This sort of farmer interest led to enactment of the Arable Land Reorganization Law in 1899".
- https://www.jsidre.or.jp/tabata6-d/: 「江戸末期ごろから、耕地の排水については、地中に溝を設けて水を抜く、暗渠排水の技術が普及していた」 - "From about the end of the Edo period, as regards drainage of arable land, the technique of underdrainage - cutting a trench in the ground to let water out - had spread."
- NOT-READABLE: suido-ishizue.jp/daichi/part3/01/09.html (title only), ja.wikipedia 分水工 (404), kotobank 井堰-30265 (wrong entry).
- Reader's verdict: three named layouts; separation is the standard only from field consolidation (postwar; 1963 projects, 1899 law the earlier step); before that drainage ran to the next field or back into the combined channel and was taken up in full downstream, the river the return path.

**Q6 - Tabayashi 1987 read in full (pp. 41-65) - PARTIAL.** Beyond the passages above: p. 42 "He further subdivided river irrigation systems into those with a diversion dam and reservoir on a river and those diverting water directly from the river."; p. 44 "Water diverted from a river by means of a diversion dam enters a main canal and is delivered into secondary and lesser canals one after another by gravity. Finally the water arrives at each paddy field."; p. 45 "Secondary canals tap water from diversion works on the main canals. Water distribution from a secondary canal is managed by a village."; p. 45 "The smallest ditches bringing water to the inlets of paddy fields are controlled by small groups of farmers, and the ditches are often considered parts of the paddy fields they serve."; p. 58 "They drew water from diversion dams constructed across rivers as wide as 50 to 70 meters (SUGAWARA, 1980)."; p. 60 (intake consolidation after floods, 1881 Joganji, 1886 Tedori); p. 62 "Early paddy fields probably evolved in marshy locations. Later, irrigation water was drawn from small streams. Then ponds were constructed, especially in western Japan, and diversion weirs on small and medium size rivers came to be utilized." ABSENT on water continuing below an intake and on drainage returning to a river as such (nearest, p. 47: "Discharge of surplus water from paddy fields occurred by opening the gate at low tide times.").

### R2b China-first reader (48 tool uses, 16 min)

**Q1 - headworks doctrine, the two forms, does the stream continue - FOUND.**

- FAO Irrigation Manual, Module 7 ch. 6 "Hydraulic structures", https://www.fao.org/4/ai596e/ai596e03.pdf (READABLE, pp. 61-72; English): p. 62 "The function of a headwork is to divert the required amount of water at the correct head from the source into the conveyance system. It consists of one or more of the following structures: Offtake at the side of the river; Regulating structure across the river or part of it; Sediment flushing arrangement". p. 62 (6.1.1, the weirless case): "In rivers with a stable base flow and a high enough water level throughout the year in relation to the bed level of the intake canal, one can resort to run-off-river water supply (Figure 38 and Example 1 in Figure 37). A simple offtake structure to control the water diversion is sufficient." p. 63: "In some instances, the base flow water level fluctuates greatly over the year and the water level can become so low that the gate opening to the offtake structure will be at a higher elevation than the normal base flow water level. To abstract the required discharge in these situations, one could consider the options below: Select an offtake site further upstream. ... Build a cheap temporary earthen dam and temporary diversion structure. This method is especially suitable in unstable rivers, where high expenses for a permanent structure are not warranted because of the danger of the river changing its course. Construct a permanent diversion dam or structure (weir or gate) across the river, where the design elevation of the weir should relate to the design water level in the conveyance canal". p. 64: "Structures constructed across rivers and streams with an objective of raising the water level are called cross regulators". p. 72 (6.1.4): "A properly-designed intake should divert only the relatively clean upper part of the water flow into the canal and dispose of the lower part down the river. A sluice should therefore be incorporated into the diversion structure design. It should be placed in line with the weir near the canal intake (Figure 51)." p. 72: "During the flood season, the sluice is permanently open or opened at regular intervals so that depositions of sediments can be flushed away. The guide wall prevents lateral movement of sediments deposited in front of the weir and separates the flow through the sluice and the flow over the weir." Figure 51 legend: "a Desilting section b Flushing sluice c Conveyance sluice d Flushing canal e Gravel and sand trap f Flushing gate g Regulation basin". Modern, small-scheme (gabion and masonry weirs, 1.25 and 37 m3/s examples).
- FAO "Water sources and water availability" 2.2.2, https://www.fao.org/4/u5835e/u5835e03.htm (READABLE): "To avoid the problems caused by fluctuating water levels in a river, a weir can be built across the river." ... "The water level upstream of the weir will show little variation during the year, and it will remain higher during the dry season than it would without the weir." ... "During periods of high river discharges, water will flow over the weir." ... "Usually, to avoid changes in the discharge, a control gate can be installed. The gate can then be opened completely when the river level is low, and opened only partly when the water level is high."
- 水知识助手 无坝取水, https://www.shuizhishi.cn/c/2020-04-09/523479.shtml (READABLE; tertiary knowledge base, modern): 「不设拦河闸或壅水坝，从天然河道中直接引水的取水枢纽」 - "A water-intake complex that sets no barrage gate or backwater dam, and takes water directly from the natural river channel." 「河流水量较丰富、引水比不大、水位及河势能满足或基本满足引水要求的情况」 - "[Used in] the case where the river's flow is fairly abundant, the diversion ratio is not large, and the water level and the river's regime meet, or essentially meet, the requirements for diverting water." 「取水口选在河岸坚固、河流弯道顶点以下的凹岸处，以引取表层清水」 - "The intake mouth is sited where the bank is firm, on the concave bank below the apex of a river bend, so as to draw the clear surface water." 「当枯水期引水比超过20%～30%时，应考虑采用有坝取水方式的可行性」 - "When the diversion ratio in the low-water season exceeds 20%-30%, the feasibility of adopting the with-dam intake method should be considered."
- ja.wikipedia 頭首工 (READABLE): 「河川等をせき止めて上流側の水位を上げることによって、水を貯留したり、用水路などへの取水を容易にしたり、計画的な分流を行ったりする役割を持つ」 - "By damming a river and so raising the water level on the upstream side, it serves to store water, to make intake into a canal and the like easier, and to carry out a planned division of the flow."
- NOT-READABLE: slt.zj.gov.cn (timed out), gzhxaq.com (refused), iwhr.org (refused).

**Q2 - attested premodern examples - FOUND.**

- zh.wikipedia 都江堰, https://zh.wikipedia.org/zh-hans/都江堰 (READABLE): 「它位于江心，把岷江分成内外二江。外江位在西，又称"金马河"，是岷江正流，主要用于行洪；内江位在东，是人工引水总干渠，主要用于灌溉，又称"灌江"。」 - "It stands in mid-channel, dividing the Min River into an inner and an outer river. The outer river lies to the west, also called the 'Jinma River'; it is the true course of the Min and is used chiefly to carry the floods. The inner river lies to the east; it is the artificial main head canal, used chiefly for irrigation, and is also called the 'irrigation river'." 「春季水量小时，四成流入外江，六成流入内江以保证春耕用水；春夏洪水季节时，水位抬高漫过鱼嘴，六成水流直奔外江，四成流入内江。」 - "In spring, when the flow is small, four parts flow into the outer river and six into the inner river, to guarantee water for the spring ploughing; in the spring-and-summer flood season, when the water rises and overtops the fish mouth, six parts of the flow run straight to the outer river and four into the inner river." 「飞沙堰将超过灌区需要的江水自行排到外江，使成都平原免受洪涝；…」 - "The Feishayan spillway discharges of itself into the outer river whatever river water exceeds the irrigated area's need, sparing the Chengdu plain from flooding; ..." 「都江堰以其为"当今世界年代久远、惟一留存、以无坝引水为特征的宏大水利工程"。」 - "Dujiangyan is [described] as 'the grand hydraulic work of the present-day world that is ancient, uniquely surviving, and characterized by weirless diversion.'"
- zh.wikipedia 灵渠, https://zh.wikipedia.org/zh-cn/灵渠 (READABLE): 「铧嘴将湘江水分为两股，其中七分水顺大天平回流到湘江，三分水经小天平和南渠注入漓江，即所谓的"湘七漓三"。」 - "The ploughshare-snout divides the water of the Xiang River into two streams: seven parts of the water flow back along the Great Balance into the Xiang, and three parts pass by the Little Balance and the Southern Canal into the Li River - what is called 'Xiang seven, Li three'." 「天平的主要作用是拦江堵水，在汛期时还可使洪水通过天平顶漫入湘江故道，兼具分水与调水的功能，保证渠内安全。」 - "The main function of the Balances is to bar the river and hold back the water; in the flood season they also let the flood overtop the crest of the Balances and spill into the old bed of the Xiang, so that they combine the functions of dividing water and regulating water, guaranteeing safety inside the canal."
- zh.wikipedia 郑国渠, https://zh.wikipedia.org/wiki/郑国渠 (READABLE): 「渠首设于泾河流出北山的仲山、瓠口一带」 - "The canal head was set at Zhongshan and Hukou, where the Jing River issues from the northern hills." 「关于郑国渠渠首的形制，学术界主要有三类观点。一是修筑大型土石坝形成蓄水区，二是以装石的囷笼或低堰抬高水位，三是不建横断河道的大坝，利用河湾、水位和导流设施实行无坝自流引水。」 - "As to the form of the Zhengguo canal's headworks, scholarship holds mainly three views. One is that a large earth-and-stone dam was built to form a storage area; the second is that stone-filled crib baskets or a low weir raised the water level; the third is that no dam crossing the channel was built at all, and weirless gravity diversion was carried out using the river bend, the water level and guiding works."
- Wang Zhen, 農書 卷十八 農器圖譜十三 灌溉門 (Yuan), https://zh.wikisource.org/wiki/王禎農書/卷十八 (READABLE): 「水柵，排木障水也。若溪岸稍深，田在高處，水不能及，則於溪之上流作柵遏水，使之旁出下溉，以及田所。」 - "The water palisade: a row of timbers set to block the water. If the banks of the brook are somewhat deep and the fields lie high, so that the water cannot reach them, then upstream on the brook one makes a palisade to check the water, causing it to issue out at the side and run down to irrigate, so reaching the place of the fields." 「開閉水門也。間有地形高下，水陸不均，則必跨據津要，高築堤埧彙水，前立鬥門：甃石為壁，疊木作障，以備啟閉。」 - "The water gate: a water door that opens and shuts. Where the lie of the land is high and low and water and dry land are uneven, one must straddle the key crossing-point, build up a high embankment and dam to gather the water, and set a sluice-door in front of it: coursed stone for the walls, stacked timbers for the barrier, so as to provide for opening and closing." 「《說文》曰：陂，野池也，塘，猶堰也。陂必有塘，故曰陂塘。」 - "The Shuowen says: a bei is a pool in the open country; a tang is like a weir. A bei must have a tang, hence the compound beitang."

**Q3 - intake to first division; settling reach - PARTIAL.** FAO ai596e p. 62: "The offtake should preferably be built in a straight reach of the river (Figure 39)." Figure 51's order of parts (desilting section, sand trap, regulation basin). 水知识助手 沉沙池 https://www.shuizhishi.cn/c/2020-04-09/519571.shtml: 「在进水闸下游不远处的河岸上设渠首沉沙池」 - "A canal-head settling basin is set on the river bank not far downstream of the intake gate." 「沉沙池的断面大于引水渠道的断面，水流经过时，流速降低」 - "The cross-section of the settling basin is larger than the cross-section of the diversion canal, so that when the flow passes through it the velocity falls." No distance anywhere; a design-code sentence on the 分水闸 appeared only in a search summary (hosts refused) and is not cited.

**Q4 - the angle - PARTIAL.** FAO ai596e p. 62: "The offtake should preferably be built in a straight reach of the river (Figure 39). When the water is free from silt, the centre line of the offtake canal could be at an angle to the centre line of the parent canal. When there is a lot of silt in the system, the offtake should have a scour sluice to discharge sediments or should be put at a 90° angle from the parent canal." "If it is not possible to build the offtake in a straight reach of the river, one should select a place on the outside of a bend, as silt tends to settle on the inside of bends. ... The offtake can be perpendicular, at an angle or parallel to the riverbank, depending on site conditions, as illustrated in Figure 40." Figure 39's two cases are labeled "Silt free" (the canal leaving at an acute angle, angling downstream) and "Silt laden" (a right angle). The Chinese 30-40 degree figures were in search summaries only (bad certificates) and are not cited; no premodern angle was read.

**Q5 - what a weir does; a whole small stream - FOUND, one gap.** FAO u5835e (above). ICID term list, https://icid-ciid.org/Knowledge/basic_term/0/Diversion%20Weirs/2247 (READABLE): "A low dam or wall across a stream for the purpose of diverting part or all the water from a stream into a canal." en.wikipedia Diversion dam: "A diversion dam is a dam that diverts all or a portion of the flow of a river from its natural course." en.wikipedia Weir: "Commonly water flows freely over the top of the weir crest before cascading down to a lower level." No page describes taking a whole small stream, nor conditions for it; none states a minimum flow to leave.

**Q6 - supply vs drainage vocabulary (China) - NOT-FOUND for the substance.** zh.wikipedia 排水沟 is about street gutters; the Taiwan MOA page names a hierarchy (幹線、支線、分線、給水路) without definitions; the design standards refused. The Japanese half (R2a Q5) carries the finding.

### R2c What the pass establishes (the session's reading of both halves)

1. **The place where a stream's water becomes a ditch is an INTAKE on one bank of the stream, and the stream goes on below it.** Both traditions name the parts in the same order - a barrier across the stream or part of it (the weir), the intake mouth on the bank, a settling reach at the canal's start, then the division works - and both say the stream keeps its course: half-river closures were the common old form, an araizeki lets water over its crest at all times, the 1615 Ishi-ibi returns its surplus to the main river, FAO's intake takes the upper part of the flow and "dispose[s] of the lower part down the river", Dujiangyan and Lingqu divide the river in stated proportions and spill the surplus back. The GM's candidate reading - the stream stays a stream until the fork - is REFUTED in its literal form and confirmed in its spirit: the stream stays a stream, all the way past the field; what forks is the dug canal, at a division works some way below the intake, and the fork is never on the stream.
2. **Whole capture of a small brook is admitted by definition and unattested as practice.** ICID and Wikipedia define a diversion weir as taking "part or all" of a stream; MAFF's Edo passage says that in drought all the mountain catchment's runoff was taken; no page shows a brook extinguished by a village ditch. So the drawn form is the attested one: the brook continues. The whole-capture reading is recorded as declined, with these two passages, and is not a knob value - the two-forms rule turns on a thing being shown DONE two ways, and this one is shown done one way.
3. **TWO attested intake forms - a KNOB.** (i) The bare bank intake (自然取入れ / 無坝引水): "in old times ... in many cases no intake weir was built at all - water was taken naturally, a place where natural intake was possible was sought for the intake mouth"; the modern rule for it is that the take is a minority of the flow (under 20-30% at low water) and the level suffices. (ii) The weir: on a small mountain stream since the Yayoi period; timber frames packed with stone, gabions, brushwood and ox-frames; temporary and seasonal or fixed; oblique, "extended long in the diagonally upstream direction from the intake mouth"; Wang Zhen's timber palisade across the brook upstream of the fields pushing the water out sideways. The record gives no proportion between the two, so the roll is even and the proportion is a GUESS.
4. **Which bank, and at what angle.** The intake is on the benefited side - one-bank intake is the rule for torrent and steep rivers - where the thalweg touches the bank, preferably in a straight reach or on the outside of a bend; the canal leaves at an acute angle pointing downstream when the water is clean and at a right angle when silt-laden (FAO), which agrees with the record's existing offtake rule (an offtake leaves its parent at an acute angle, 30-45 degrees, "instead of 90"). A mountain brook feeding a hamlet fan is drawn with the acute offtake.
5. **The head race's length is a site variable.** No source gives a distance from the intake to the first division; Tabayashi says small streams' canals run "for short distances"; the Toro canal was over 370 m for 7.5 ha. The settling basin sits at the canal's start, immediately after the intake mouth. So the length is DERIVED from the geometry - where the brook passes the fan's head and where the fork stands - never a constant, and the entry says the distance itself is unattested.
6. **The foot.** Before postwar field consolidation, drainage went field to field or back into a combined channel, and returned to the river to be taken up by the district below; separate drainage canals are the postwar standard. So a drain that reaches the passing brook joins it (a confluence), and a drain the brook does not pass runs on as a dug ditch to wherever the map sends it; either way its run is a DUG continuation of the collector - FR-002's default stands and D3 is settled. The pond at the foot as the drain's sink is a prior decision of the record ("On this map the pond is the field's drainage sink") and is not reopened here.

**Outcome on FR-004's ladder: (a) with (c) inside it.** The stream continues past the intake (a, decisive); the intake form is a knob between the bare bank intake and the weir (c, two attested forms); the head race's length is derived from the geometry with the record's silence on the distance labeled; the whole-capture reading is declined with its passages.

## R3 The maps before and after (2026-09-12)

The pool, rolled through the finished feature. "Brook before" is the length of the feed brook as the
generator drew it until now - a fixed 420 px run ending at the intake; "after" is the whole course, down
off the high ground, past the intake and on down one flank of the fan to the frame. The head race was a
hardcoded 90 px straight down the fall on every comb map; it is now the rolled lead on the rolled bearing.
Kuwabata is the polder: pond-fed, no brook, and its 775 ft "head race" is the perimeter ring's own trunk,
untouched by this feature.

| map | intake | flank | brook before (ft) | brook after (ft) | head race (ft) | the drain's sink | irrigation-ditch marks | drainage-ditch marks | weir |
|---|---|---|---|---|---|---|---|---|---|
| Inashiro | weir | +1 | 423 | 3,223 | 105 | pond | 154 | 16 | 1 |
| Kashikawa | weir | +1 | 423 | 3,263 | 105 | off the frame | 200 | 10 | 1 |
| Kuwabata | weir | -1 | 0 | 0 | 775 | off the frame | 327 | 2 | 0 |
| Mizuguchi | weir | -1 | 423 | 3,256 | 105 | pond | 155 | 9 | 1 |
| Sawada | open | -1 | 423 | 2,830 | 130 | the passing brook | 164 | 17 | 0 |

**All three sinks are on the sheet**, which the spec's own reviewer doubted would happen: two maps drain to
a tameike, one off the frame, and Sawada to the brook that passes 82 ft from its outfall. That last one took
two corrections, both worth keeping. The first: the nearest point on a brook running down the flank is
LEVEL with the outfall - Sawada's was 79.7 px away and 4.4 px UPHILL - so a test for "downslope" refused the
join and sent the drain off the frame on its own, two watercourses leaving the map side by side, which is
the overlap the GM caught on the first Ikegami draft in another place. The join is now the nearest point
that has FALLEN (`BROOK_JOIN_DESCENT`, 20 px). The second: the outfall stands ON the crop's edge and a
comb's envelope bows out around its own collector, so a crossing test from it reported the route running
through the rice on every candidate; the route is exempt over the lead it takes to leave the envelope, the
same exemption the gate makes for a brook's leading vertices, and refused past `BROOK_JOIN_LEAD` of the run.

**Both knob values are on the sheet, and one is pinned.** The roll is even - 477 weirs in 1,000 seeds,
measured - but all five pool seeds landed on the weir, so Sawada declares `intake="open"` in its generator,
recorded there with this measurement. A knob owes one map per value.

**Two things this feature had to give back.** Mizuguchi lost the tameike it is named for on the first
sweep: the brook now runs down the flank the reservoir wanted, the set-back walk is straight downslope, and
the pond was pushed past the canvas into the clamp, which falls back to draining off the frame. The seat
search gained one degree of freedom (`pond_seat`: sways of 0.9 and 1.8 of the long radius, nearest first,
the straight seat still winning whenever it is clear) and the pond came back. And the first clearance test
held the pond a circle of its LONG radius from the brook, half again the pond across its short axis; it is
the pond's own ellipse plus a rim's margin now.

## R4 The course, after five review passes (2026-09-12)

`settlement-review` read the maps five times and its findings drove the whole of the brook's geometry. What the
course is, in the end: a walk down the fall in the fall's own frame, each station held outside the crop's
CROSS-SECTION at that point by a skirt, wandering on a seeded reflecting walk, bounded to the field's own extent
so it stays on the sheet, corner-cut once so a vertex becomes two bends, and running free of the bound only in
the legs that leave the frame. Beside it, two changes that are not the course at all: the fan's supply canal is
trimmed on the brook's flank, so the field is cut away from the stream; and the cluster seater scores a seat down
when the brook would cross the band, so the hamlet stands on one side of its own water.

The measurements, pool-wide, against what each pass found:

| | pass 1 | pass 2 | pass 3 | now |
|---|---|---|---|---|
| brook vertices in cultivated ground | 15 of 25 plots on one map | 1 | 1 | **0 on every map** |
| the course, in the cropped view | - | 2 to 7 pieces | 1 to 3 pieces | **1 piece on every map** |
| sharpest turn | 67 deg round a 300 ft straight | 83 deg | 83 to 100 deg | **49.3, 48.6, 51.9 deg; 104.5 on Kashikawa** |
| median turn | - | 9 to 34 deg | 13 to 34 deg | **4.1, 9.1, 13.4, 15.4 deg** |
| turns past 70 deg | - | up to 16 on one map | up to 16 | **0 on three maps, 2 on Kashikawa** |
| the offtake angle a reader measures | 64 and 46 deg | 64 and 46 | 35 | **35 on every map, the record's own figure** |
| homesteads across the water from their lanes | - | 2, no crossing | 1, no crossing | **0** |
| the brook's course with no meander at all | - | - | 32% of one map | **0 to 10%, and only where it leaves** |

The last pass's two errors closed by two changes apiece. The stranded homestead: the seater now REFUSES a margin
the brook divides rather than scoring it down, keeping the scored form only for a hamlet whose every margin is
divided; and the fan's supply canal is trimmed on the brook's flank, which gives the stream its own ground to run
in. The mitred head and the ruled reaches: the corner cut rounds by a DISTANCE from each vertex rather than a
fraction of the leg, so a turn whose other arm is short is rounded too; the approach above the tap wanders like
the rest; and the reach that leaves the frame is exempt from the bound that keeps the rest on the sheet, since
holding a leaving course inside the picture is what folded it back on itself.

**What is left, measured and accepted.** Kashikawa keeps one turn of 104.5 degrees where its course meets the frame
bound and slides along it; that map's median turn is 4.1 degrees, and the three other maps' sharpest are 49.3,
48.6 and 51.9. The cause is the bound itself: on a map whose land falls on a diagonal the bound is a box in the
sheet's own axes and the course runs across it, so where they meet the course must turn. Two ways out were priced
and neither belongs to this feature: loosen the bound, which puts part of the course back outside the picture -
the defect measured at 67% of one brook in three pieces - or build the course in the frame's axes from the start,
which is a different construction and would move every map again. It is recorded here rather than left for a
reader to find.

**The last two passes found nothing more about the course, and two things about what stands beside it.** Pass 4
asked for the seat and the corner cut, both above; pass 5 read the result and said Kashikawa's remaining turn was
acceptable as drawn. What it found instead was that Inashiro had no drawn way to its rice at all. The spur to the
field is the one lane fragment that serves no HOUSE, and both orphan sweeps ask whether every house a fragment
serves is served elsewhere - so a fragment serving only the field answers yes vacuously and is dropped. The spur
is flagged now and kept exactly as a house's only way is, and the length the clip leaves is recorded on every map
whether the spur is drawn or not (`meta.field_spur_ft`), which is how three maps with no path to their own rice
became visible rather than staying silent (measured and deferred in `future-work/farming-communities.md`). Pass 5's
other finding is the page's, not the map's: lighting a watercourse repaints the footbridge and the weir that cross
it, measured and deferred in `future-work/cross-cutting.md` against feature 201's own priced-and-declined fix.

The course as it stands, measured on the four comb maps the day the feature landed:

| map | brook vertices in cultivated ground | pieces in the cropped view | sharpest turn | median turn | turns past 70 deg |
|---|---|---|---|---|---|
| Inashiro | 0 | 1 | 49.3 | 15.4 | 0 |
| Kashikawa | 0 | 1 | 104.5 | 4.1 | 2 |
| Mizuguchi | 0 | 1 | 48.6 | 13.4 | 0 |
| Sawada | 0 | 1 | 51.9 | 9.1 | 0 |

## R5 What the seat rule cost, and what it costs now (2026-09-12)

The fourth review pass was answered by seating the hamlet on ONE bank of its brook - `seat_cluster` scores a
margin down when the brook runs near the band and strikes the margin out entirely when the brook DIVIDES it.
That answered the review and was never measured against a cohort until this task, which is where the price
showed up.

BASELINE, taken in a detached worktree at the pre-feature commit (`git worktree add --detach /tmp/base230
7f4113a3`), same command, same 48 seeds:

| | seeds passing the whole gate | the residue |
|---|---|---|
| before feature 230 | 48 of 48 | - |
| with the seat rule as pass 4 left it | 46 of 48 | seed 15 seated 15 of 16, seed 22 seated 8 of 10 |
| with the shortfall re-roll | 48 of 48 | - |

The two seeds failed by the two DIFFERENT halves of one rule, which is why the first fix only half worked.
Seed 15 failed on the strike-out: the best undivided margin left to it held fifteen bundles where sixteen were
declared (reproduced with `make cohort N=1 SEED=15`, which this task added to the target so a cohort member can
be re-rolled without a 48-seed sweep). Seed 22's band was never struck out at all - the brook merely ran near it,
the 3.0 crossing penalty scored it below a margin clear across the map, and that margin held eight of ten. So a
rule stated as "the settlement does not straddle its stream" was also, unstated, "the settlement may lose a
household to avoid its stream".

THE RESOLUTION, and why it is not a preference: both readings are defects the GM would see. A hamlet in two
halves with no crossing was measured by two review passes; a hamlet missing a household is missing a household.
Neither can be waived, so the MAP decides - a roll that comes up short and whose seat the brook steered is rolled
again with the brook ignored at the seat, and that roll is kept only if it seats more (`generate`; the counting
is `plan.seat_brook_steered`, the outcome `meta.seat_divided` on every map). Across the pool and the 48-seed
cohort the second roll is needed by two maps and by neither pool hamlet, so the rule holds everywhere it can.

FOUND ON THE WAY, and fixed with it: the re-roll loop handed back the LAST roll's manifest rather than the kept
one. The re-emit that corrects this needs an `out_base`, and a cohort passes none - every member finishes into a
scratch directory - so a rejected re-roll was the manifest the report carried, and `cohort_audit` reads the seated
count off exactly that manifest. The verdict lines were the kept roll's and the numbers beside them the rejected
roll's. It predates this feature and is fixed here (constitution XIV).

## R6 One bank or both? The record answers by SCALE (2026-09-12)

The spec review's amendment round would not let D9's seat rule stand unlabeled, and it was right: "a hamlet does
not straddle its own brook" is a claim about how a place was built, and nothing in the record had been asked.
A `source-reader` pass asked it. The finding is not the one the rule assumed.

**Against a RIVER, one bank is what the record shows.** Harie in Shiga "lies on the LEFT BANK of the alluvial fan
at the lower reaches of the Ado River" (translated from the Japanese; 針江 生水の郷, harie-syozu.jp). Imazato's
study of Hagikura in Nagano describes a hamlet on a river terrace whose own folk names carry the arrangement -
the hill behind is the Urayama, the "back mountain", and the hill ACROSS the river is the Mukoyama, the "facing
mountain", which is hillside and not houses (『人文地理』51-5, 1999, pp. 436-439). And an Edo lawsuit over the
Tenryu names its parties by their side of the water, 川東の村々 and 川西の島田村, with the boundary running
wherever the main current ran (平沢清人『村境は不思議だ』, an MLIT river-office booklet, p. 20).

**Against the settlement's OWN small channel, the record shows the opposite, and says so plainly.** The SAME
Harie page that puts the village on one bank of the river says "the Harie Okawa flows through roughly the CENTER
of the district"; the settlement's channels are 集落内の水路, channels INSIDE the settlement, and a magazine
account of the kabata describes "the channel that flows ALONGSIDE THE HOUSE". Harie with its neighboring
Shimofuri is a national Important Cultural Landscape, so this is not an oddity.

**So the two are not rival claims about one thing - they are claims about watercourses of two different sizes,
and the maps' brook is the SMALL kind.** Seven feet wide, tapped by the hamlet it passes. On the record's own
division that is the kind a settlement is shown standing around, not beside.

**What the fengshui siting literature adds, with its scope stated.** The 四神相応 formulation wants "flowing
water on the LEFT" of the site, and the Chinese village-siting studies describe streams that 绕村而过 - flow
around and past the village - with Shanggantang's ideal stated as 三面环山，一面临水, "mountains on three sides,
water on ONE side". None of it contemplates a site divided by its water. The limit to carry: this is
capital- and residence-siting doctrine and village-landscape scholarship, not a rule anyone states for a farming
hamlet's brook.

**NOT FOUND, searched 2026-09-12**: no readable page says in words that dwellings at Harie face its channels
from both banks, nor what crosses them - the Agency for Cultural Affairs selection text, which would be the
authority, renders an empty 解説文 at both official database URLs and the Takashima city page returns 404. And
nothing was found naming a plank bridge, ford or stepping stones inside a settlement's own channel, ordinary or
remarkable. The trap the pass avoided is worth recording: 線状集落 is defined as buildings "lined up on BOTH
SIDES OF A SINGLE STREET", and the both-sides there is a STREET, not a watercourse.

**What this does to the rule.** D9's refusal is NOT the attested form for a brook at this scale, so it is
labeled as this project's own placement decision. It stands for a reason the record does not supply and the
engine does: a hamlet seated astride the brook is one the maps cannot draw a crossing for - the stream is
registered only as a keep-out, so the router never routes across it and `bridges()` decks only a crossing that
already exists (pass 4's measurement: 0 bridges on 2,000 ft of water with a homestead on the far bank). The
straddling form is therefore recorded as DECLINED-FOR-NOW rather than unsupported, and as the knob candidate it
is: two forms are attested at the two scales, and the day a way can cross a brook, which side a hamlet builds on
is a knob to roll rather than a rule to keep.

## R7 The confluence, and why no pool map draws one (2026-09-12)

FR-002's third sink - the drain joining the brook that passes the field - is implemented, and after review pass 7
no pool map takes it. That is a measurement rather than a retreat, and it is worth writing down before someone
reads the spec and goes looking for the junction.

The rule a confluence has to pass is the reach, a real descent below the outfall, a route that does not cross the
crop, and `BROOK_JOIN_TRUNK` of brook running on below the junction. Passes 6 and 7 both found the LAST of those
being met by brook that no reader could see: the trunk was counted as ARC LENGTH, and Sawada's junction came out
7.4 ft outside the sheet with all 359 ft of its trunk off the canvas. The trunk is counted on the canvas now, and
the junction reserves itself as CONTENT so the crop cannot leave it out (`plan.confluence`, `stage_frame`) - the
same mechanism the title pocket uses, and the right one, because the frame is decided in `stage_frame` and
nowhere else. Two attempts to predict the frame back in `stage_sink` are recorded at the point of change; the
second refused every confluence the generator can draw, which is how the prediction was shown to be unworkable.

MEASURED on Sawada, the map whose brief this sink was written for: one candidate passes the reach, the descent
and the crop - and the brook has **33 ft** of canvas left below it against the 150 ft the rule asks. Pinning the
other flank (`brook_side`, made pinnable for the experiment) gives no candidate at all. The geometry is the
reason: the drain's outfall stands at the field's low corner, which on these two maps is near the canvas edge,
and a brook that leaves the map there cannot carry a visible trunk below the junction. So both maps take the
off-frame sink, which is honest, and the pool exhibits two of the three sinks.

The branch is proved by a unit test instead (`tests/hamletgen/test_sink.py`, the confluence taken on a brook that
runs well inside the picture and refused on one carried outside it), and the third sink will appear on the first
map whose outfall stands far enough inside the frame.

## R8 The confluence, exhibited after all (2026-09-12)

R7 recorded that no pool map draws the third sink. The eighth review pointed at the lever this feature had
built and not pulled: `brook_side` was made pinnable in the same commit, with the stated purpose of letting the
pool exhibit a sink a roll happens not to reach, and an implemented sink owes one exhibit the way a knob owes
one map per value.

MEASURED, per map, walking each brook at a 10 px stride against its own outfall:

| map | rolled sink | the nearest brook point that has FALLEN below the outfall |
|---|---|---|
| Inashiro | pond | none - the brook is 1,049 ft away and 1,033 ft uphill |
| Mizuguchi | pond | 55 ft away, 54 ft fallen (never consulted: it is a pond map) |
| Kashikawa | off-frame | none on the rolled flank - the brook is 840 ft away and uphill |
| Sawada | off-frame | 76 ft away and fallen, and refused: about 85 px of canvas below it against the 150 the rule asks |

So Sawada cannot take it at either flank - its outfall stands at the canvas edge, which is the geometry, not the
rule. Kashikawa can, on the flank it does not roll: pinned to `brook_side=-1` the brook passes the side the
outfall is on, the collector reaches it, and the junction falls **123 ft inside the view with 177 ft of stream
visible below it** (measured on the view box after the fan re-fit; the figure first written here was 347 ft, which
was the raw length of the leg from the junction to the brook's next vertex - 55% of it off the sheet, the same
arc-length measure `sink.py` retired two passes earlier; settlement-review pass 9 caught it). All twenty
households still seat and the roll reports no failure. The pin carries its
reason in the generator, as Sawada's `intake="open"` does.

The pool therefore shows all three sinks again: the pond (Inashiro, Mizuguchi), the off-frame run (Sawada,
Kuwabata) and the confluence (Kashikawa).


## R9 The fan re-sized, and the corner below the weir (2026-09-12)

**The speed lever, taken.** `perf-audit` returned band 1 `inconsistent` and band 2 `not-justified`: it measured
the declined lever (`lo, hi, k` scaled by `sqrt(2 / (1 + BROOK_FAN_TRIM))`) at 26.8 / 26.3 s against an
interleaved baseline of 28.2 / 28.2 s, faster than before the feature where the shipped code was +22%. The reason
recorded for declining it was false. Measured A/B on identical code, the flooded sample's sliver demotion rate is
64 of 90 without the scaling and 66 of 92 with it - the size is not the cause. The two gate failures at the larger
size were defects it landed on: `_unjog`'s apex guards judged only the deduped ring while the gate reads the
recorded one (a 0.2 degree hairline spur shipped), and the map's whole wet-paddy exhibit rested on one surviving
random draw at either size. Both fixed; with them the clone's own pool, before this pass, had shipped Kashikawa and
Mizuguchi with no flooded plot at all, and now every map has one.

**settlement-review pass 9** ran one agent per map; four were killed by an account rate limit before reporting and
only Kashikawa's returned (needs-work, 3 errors, 1 questionable):

1. *The sharpest corner on every brook map is 49 ft below the weir* - 72.4 / 77.9 / 71.9 / 51.9 degrees against
   medians of 10-15. Two levers measured first did nothing: narrowing the first station's look-ahead window
   (71-73, unchanged) and a longer head race (moved it on two maps, 88 degrees on Sawada). Instrumented, the cause
   was a dry hem plot laid round the fork and reaching up beside the intake (to 72 px below the tap, 104 px out on
   the brook's flank on Kashikawa; starting 4 px below the fork on Mizuguchi): the corner-cut point past the tap
   run was floored against it and thrown 138 px sideways in 33, while the fan's own plots do not begin until
   ~120 px down. Crop reaching within one skirt of the fan's head now yields to the brook, as the tap run's crop
   already did. Result: **41.0 / 52.8 / 52.7 / 51.6 degrees**, one dry plot of ~20 given up on two maps, every
   household seated on the first roll, the brook 14-26 px clear of every crop ring, 99 of 99 gate tests green. The
   ~52 degrees left is the fan's own divergence at its head.
2. *The recorded 347 ft of visible trunk below the confluence* was the raw length of one leg, 55% off the sheet.
   Re-measured on the view box: 177 ft (R8, the generator's docstring and the notes corrected).
3. *Kashikawa's notes never mentioned the confluence*, and their last sentence said its runoff leaves the frame.
   Rewritten.

**Open, with its measurement: the confluence can read as a fork.** The drain arrives at 71 degrees to the brook's
downstream heading, 5.5 ft wide against the trunk's 6.5, tapering narrower away from the brook - the silhouette of
an offtake, which is what the same map draws at the intake. The reviewer's lever is to align the drain's last leg
with the brook's downstream heading; whether a field drain's return is swept downstream is a research question the
record has not asked (`city/moat.py` asserts it without a citation), so it is not changed on a guess.
