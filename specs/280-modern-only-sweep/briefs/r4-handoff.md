# Feature 280 group R4 - handoff (session 1: research and write, 2026-09-29)

None of R4's sections was held: 269 has no unlanded commits touching 0235, 180, 206 or 270, and none
of them falls in 279's 124-129.

- SECTION=0235
- SECTION=religion-and-death/180
- SECTION=religion-and-death/206
- SECTION=religion-and-death/270
- SECTION=religion-and-death/750
- KEY=edo-jinko-tokei-jawiki
- KEY=tsuya-kurosu-tokugawa-mortality
- KEY=yagura-jawiki-weblio

Keys newly cited on the page but already registered: sohu-xuancheng-yizhong, kotobank-ryobosei, ryobosei-jawiki,
yoro-sosoryo-sol, kaf2-kinsei-bo, feng-yizhong-jiangnan, chinese-units-enwiki, kimura-1934-bochi-menseki.
demographic-transition-enwiki is no longer cited anywhere; its registry entry is marked *Not cited*.
The glossary term `crypt precinct` (15550) was used only by the paragraph of 180 that went with the set-back
ladder, so it was deleted (git rm, `make glossary` run).

## Items

M74 MIXED - 160 now rests the death rate on Edo village registers: three Nihonmatsu villages at about 30 per 1,000 in
the famine decades and 18 after, birth rates of 18.4-31.9 per 1,000 across seven villages from 1671 to 1871, a nearly
flat national population from 1721 to 1846, and a life expectancy of about 37 at Saijo in Mino (1773-1869), which gives
about 27 per 1,000. The premodern calibration is about 20-30 per 1,000 in ordinary years, and the rule's 25-30 falls
inside it. The grave sizes are Edo. The 30-year reuse period is this project's choice (an absence note, no figure
before the 1934 paper), and the 1934 reckoning is now labeled a modern check, not a basis. - Kinds and maps: nothing
the generator draws has to change. BurialGround's P x 7.5-18 sq ft and the hamlet ground's 750-2,450 sq ft (still a
labeled guess) stand. Any modal or code comment that cites the demographic transition or the 1934 reckoning as the
basis should point at the Edo rates instead (`hamletgen/burial.py` docstring; the BurialGround class). - Searched
2026-09-29: 江戸時代 農村 死亡率 人口千人当たり 宗門改帳 (Japanese); "Tokugawa village crude death rate" Hayami (English);
村明細帳 墓所 除地; ja.wikipedia 江戸時代の日本の人口統計; Kito's 人生40年の世界 (no death rate, only stagnation); Tsuya and
Kurosu, IPC 2021. - GM ruling: the GM ruled the hamlet burial knob in feature 273, not the size or the death rate.
The death rate and the reuse period were this project's choices, not ruled.

M75 MIXED - 180 now finds the high, dry site premodern in China: Song pauper grounds from 1104, some on ground chosen
"high and barren", one to ten li outside county towns (sohu-xuancheng-yizhong, quoting the Song-Yuan gazetteers;
louzeyuan-zhwiki). In Japan the premodern evidence runs the other way: in 871 Kyoto's commoners buried on the lower
Kamo riverbanks, and the two-grave burial grave (dated to the early Edo period) lay on riverbeds and beaches. No
distance from water is attested before the 1884 instruction; the only figure is a present-day ordinance's 20 m. The
record now says the maps do not draw a set-back that scales with the watercourse. The rule is: the higher, drier
ground to hand, never in open water or a flooded field, never upstream of the houses; the cremation ground may stand
nearer the water (a guess). The moat, river and canal ladder (225/390/420 ft on a city sheet), the 150 ft field margin,
the 90 ft cremation margin and the walled-ground and crypt exemptions are gone from the record. - Kinds and maps: stop
drawing the scaled set-backs in `hamletgen/burial.py` (STREAM_SETBACK_PX 75, FIELD_SETBACK_PX 50) and in
`settlement/civic_grounds/edge_seat.py` (the stream, moat, river and canal bands and the field-edge margin). Keep only
"not in the water or the flooded field" (the existing ditch margin is enough for that) and "not upstream". This touches
the pool hamlets and the legacy villages, towns and provincial cities. - Searched 2026-09-29: 喪葬令 皇都 道路側近;
延喜式 鴨御祖社 葬斂; 貞観13年 太政官符 葬送 放牧 鴨川; 漏澤園 擇高曠不毛之地; 清代 義冢 縣志 選址 高阜 避水; 葬書 界水則止
(Wikisource summary only; ctext unreadable); 江戸時代 村絵図 墓 立地; a Kumamoto prefectural paper (404) - Japanese,
Chinese, English. - GM ruling: none. The ladder was labeled a guess in the record and the code and was never ruled.

M76 MIXED - the new 750 ("Were a town's and a city's burial grounds that size before modern times?") finds Qing charity
graveyards measured by the mu. Xuancheng's gazetteer lists four by road at 1-3 mu each (about 0.15-0.45 acre, some 1.1
acres together) plus 22 mu bought in 1805; Baoshan's (Guangxu count) ran from 3 fen to 10 mu (about 0.05-1.5 acres).
A town's 0.25-0.75 acre and a city's 0.75-2 acres split across yards fall inside those figures, and Xuancheng's grounds
by different roads match the split. The limit: they are charity grounds for the unclaimed and the poor, with no
population given. No premodern Japanese ground's area was found; an Edo temple's burial area (Obodo) was dug over and
over for want of room. The 1934 path factor of 1.5-2 is modern only. 206 now says the maps' sizes do not rest on it
and points to 750. - Kinds and maps: BurialGround keeps the town and city ladder. Stop applying the 1.5-2 factor for
paths to plots anywhere it is used; a ground is its graves and the lanes drawn. The 750 spec wants a city's ground
split across two or more yards, each 0.05-1.5 acres, by different roads where the plan allows: check that the
legacy cities do this. Affects the pool hamlets and the legacy villages, towns and cities only through the path
factor. - Searched 2026-09-29: 村明細帳 墓所 除地 坪/畝歩; 御府内寺社備考 墓所 坪数; 近世墓 村落墓地 発掘 墓域 面積;
皇国地誌 村誌 墓地 反別; 清代 義冢 縣志 畝; Tanigawa's Waseda paper (unreadable, on TO-DOWNLOAD as 297); the Kanagawa
archaeology foundation page - Japanese, Chinese, English. - GM ruling: none. The ladder is this project's arithmetic.

M77 MIXED undated-custom - 270 now finds the form premodern: the two-grave custom, dated to the early Edo period, set
the visiting grave in the grounds of the village's temples and halls, and the burial grave away from the houses; the
two were often close, across a road or on one piece of ground. No premodern distance exists: the Yoro code bans burial
only near the capital and beside roads. The 650 ft is the reach of today's visiting graves, and 60 ken is an 1884
rule. The record now says the maps do not draw a set distance. The rule is: the ground lies within the village, beside
the hall or at the edge of the houses, never upstream; a ground apart from the shrine lies downstream, just beyond the
last houses. - Kinds and maps: `hamletgen/burial.py` and legacy hoshigaoka should drop the 650 ft (325 px) cap as a
measured figure and place the ground beside the shrine or at the edge of the houses. - Searched 2026-09-29: 両墓制
成立 時期 詣り墓 距離; 江戸時代 村絵図 墓 位置 集落 はずれ; 三昧 村境 近世; Kotobank and ja.wikipedia 両墓制; the Yoro code; the
Tanigawa Waseda paper (unreadable); the Kumamoto paper (404) - Japanese, Chinese, English. - GM ruling: none on the
distance. The two-grave reading was feature 269's, not the GM's.

## Left open

- The downstream side (180 and 270) is attested only by the 2010 survey of today's two-grave villages
  (kawazoe-2010-ryobosei), an undated record of present layout. By spec D1 that is undated-custom. The inventory did
  not name it, so the record keeps it as attested "in today's villages only". The GM may want it swept too. The 871
  lower-Kamo burial ground is consistent with it but is not proof.
- 750's calibration rests on Chinese charity grounds while the setting follows the Japanese form. No Japanese area
  exists to replace it until someone reads a source like TO-DOWNLOAD 297.
- The Kito paper's percentage for 1721-1846 population growth is lost in its text layer. It is not needed, because
  the jawiki article carries the same finding.
