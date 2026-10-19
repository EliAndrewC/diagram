# Feature 401, session 1 (write) - handoff

- SECTION=0276/what-did-a-kitchen-knife-cost
- SECTION=0277/what-was-copper-coin-worth-in-silver

Every note went through a source-reader from its bundle (page images for the four NDL scans), answered with `make
record-checked`; its findings were fixed by hand in commit `401: the source-reader round ... applied by hand`. The fixes
have not had a second source-reader round. One item is past the ten-key cap and went to the continuation brief: a
registry key for the RIEB Excel file (`rieb-kinsei-db-data`), so that note `rieb-kinsei-db-3` (the 1843 order, readable
only in the data file) links where its passage can be read; until then it links the database's about page.

## 0276 What did a kitchen knife cost?

- Edo 1851, the tool and blade wholesalers' price-cut list (ninth month), silver monme for ten, old -> reduced:
  thin-bladed cooking knife 200/85/20 -> 190/80/18; sashimi 150/50/18 -> 140/47/17; deba 28.5/20/12 -> 27.5/19/11;
  vegetable 12/8.5/7.5 -> 11.5/8/7; tobacco 65/35/15 -> 63/33/14 - ATTESTED ONLY FOR wholesale prices. A price a knife
  (0.7 to 19 reduced) is the project's arithmetic. The per-ten unit is the record's reading of where 「十枚ニ付」 stands
  (beside the first cooking knife's first price; the other unit notes beside the first small knife and the needles) -
  GUESS-labeled reading. The deba is the record's reading of the cursive name the OCR prints 弐匁庖丁 (source-reader:
  the form matches 出 and 刃, unlike this hand's 弐 and 匁) - a reading, hedged on the page.
- Mimasaka 1665 (作州記, 諸職人作料値段定帳): kitchen knife 8 monme apiece, another knife 5.6, razors 3.2 a pair, a
  body-tested sword 60 - ATTESTED ONLY FOR ceilings on three named swordsmiths' work. The eight named polishers' tariff
  is for swords and polearms only.
- Price by maker (Sakai, Seki, Takefu, Tosa): SILENT.
- Sakai tobacco-knife guild: 1730 stamp, 31 shares, 30 ryo a year, levy 1 rin a knife (堺市史) vs 3 rin (the 1761
  rules in Takekoshi 1935) - both ATTESTED, the disagreement stated.
- Output: ATTESTED ONLY FOR the 1761 night-work cap, 21/27/30 tobacco knives a day by size (the historian reads it as
  night work; a daytime rule unknown). Kitchen knives SILENT. Takefu: 72 smithies 1797, 111 in 1850, 129 in 1866; 151
  shares from 1853; a share 300 monme (1814), 600 (1842); 807,000 sickles and vegetable knives taxed c. 1865-68; 20,000
  ryo sold out of the domain 1864-68 - ATTESTED, no per-smith rate.
- The split: smiths, grinders and handle-makers at Sakai about 1757 - ATTESTED ONLY FOR a historical geographer's
  summary of Yamaguchi, hedged as hearsay; the 1757 petition (forge helpers, middlemen, provincial wholesalers) and the
  polishers' dispute over raised pay (1855) - ATTESTED. Kitchen-knife handle-maker SILENT; sharpener's fee SILENT.
- China: a 1-jin kitchen cleaver 0.1 tael, Beijing 1736 (Gao Table 7; 會典則例 卷130) - ATTESTED ONLY FOR official
  prices; beside laborer 75 and craftsmen 154 cash (same list), about a laborer's day at Gao's 800 cash to the tael.
  Wanli-era cutting knife about 0.05 tael - ATTESTED at second hand (Gao's bracket); Board of Works wages 1615,
  0.03-0.07 tael.
- Wages beside Edo 1851: Edo unskilled SILENT; nearest unskilled Kyoto 1851, 3.37 g silver (about 1.08 monme), same
  year, other city (bassino-ma-2005); nearest craftsman Edo carpenter 1854, 4 monme top / 3.75 ordinary + 1.2 meals, 3
  years later, and a flat 7.5 monme with meals 1853-60 (saito-1993-bakumatsu-wages).
- Wages beside Mimasaka 1665: SILENT; nearest unskilled Kyoto 1741, 2.57 g (about 0.83 monme), 76 years later; nearest
  craftsman Musashi (Tama) carpenters and sawyers 1749, 1-1.67 monme a day, 84 years later (kawakami-1992-shrine-headman).

## 0277 What was copper coin worth in silver?

- Official: 1 ryo = 60 monme = 4 kanmon from 1700 (about 67 mon a monme), copper not to trade dearer than 3,900 mon a
  ryo; 6,500 mon a ryo from 1842 - ATTESTED (law, not market). Edo quoted mon a ryo, Osaka monme a kanmon.
- Osaka market, the Mitsui diary via RIEB, decade means (the project's arithmetic, specs/401-.../measure/rieb_decades.py
  on the archived Excel file): monme a kanmon / monme a ryo / mon a monme / mon a ryo -
  1787-89 9.49/55.6/105/5,860; 1790s 9.37/60.6/107/6,470; 1800s 9.20/64.3/109/6,990; 1810s 9.14/64.6/109/7,060;
  1820s 9.21/63.4/109/6,880; 1830s 9.10/61.8/110/6,790; 1840-43 9.25/62.8/108/6,790; 1850-54 9.56/64.1/105/6,710;
  1855-59 10.53/70.9/95/6,740 - ATTESTED series, ARITHMETIC means. Floor 1843-04-13 to 1850-02 (10.00) left out, the
  1843 order quoted. Gold after 1859-06-01 left out; table stops at 1859. 19 years missing, listed.
- Before 1787: Osaka 1766 one day, 15.19 monme a kanmon (about 66 mon a monme), 4,201 mon a ryo - ATTESTED; the
  Meiwa-era fall to about 6 kanmon a ryo - ATTESTED, no figure by year; the early 1780s SILENT.
- Edo market rate by decade: SILENT (Iwahashi 1998 fig. 3 is a chart only, named in the absence note's comment);
  nearest printed: Osaka's series, and Kyoto first month of 1867, 8,460 mon a ryo.
- Anchors: 1804 (1802-03 missing) 9.22 monme a kanmon, 108 mon a monme, 6,930 a ryo, so 0250's 0.92 monme is about 100
  mon; 1842 9.53, 105 mon a monme, 6,710 a ryo, so 0262's Nagata 132 mon is about 1.26 monme - ARITHMETIC.

## New registry keys (10)

shomonya-saiko-1851-tools, kibi-gunsho-2-sakushuki, takekoshi-1935-keizaishi-9, sakai-shishi-1930-3,
fukui-kenshi-takefu-kaji, fukui-kenshi-takefu-sales, kawashima-2012-kaji-review, rieb-kinsei-db, jawiki-sanka-seido,
jawiki-gojo-soba. Existing keys newly cited: gao-shouxian-jiuqing-wuliao, daqing-huidian-zeli-130 (entry widened),
bassino-ma-2005, saito-1993-bakumatsu-wages, kawakami-1992-shrine-headman.

## Still open

- `rieb-kinsei-db-data` (the continuation brief).
- The 磨師 entry of 守貞謾稿 (a sharpener's fee): the GM's download 類聚近世風俗志 下 (433 MB) waits in the inbox, over
  the archive's size limit and not yet split.
- A pass for a seventeenth-century day wage (beside Mimasaka 1665) was not run; the nearest named are of 1741 and 1749.
- The hand fixes of the source-reader round are owed session 2's checks (`make record-owed`); the Ming bullet of 0276 gained Beijing and the gap after the round.
- Inui Hiromi's papers on the Sakai tobacco-knife guild and the Takefu sickle smiths; 新保 1978's rate tables (Osaka
  before 1787); 校註両替年代記 (Edo rates) - not reached.
