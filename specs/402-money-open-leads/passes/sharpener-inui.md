# Pass: sharpener's fee (磨師/研師) and Inui Hiromi's Sakai / Takefu papers - 2026-10-19

## (1) Sharpener's fee

### 守貞謾稿 / 類聚近世風俗志 - the 磨師 entry
- Where it is: NOT in 下 (pid 991467, which holds 編 17-33). It is in 上, pid 991466 (國學院大學出版部 1908), 第五編 生業下,
  printed p.149, koma 94: https://dl.ndl.go.jp/pid/991466/1/94 . The one-volume 1934 edition (pid 1444386) has the same entry at koma 95:
  https://dl.ndl.go.jp/pid/1444386/1/95 . 
- Publicly readable? YES in the viewer, with no login: permission type `internet`. Both 1908 volumes (991466, 991467) and 1444386 are
  published online under a Copyright Act Art. 67(1) ruling (文化庁長官裁定, 2019). BUT the IIIF API refuses them (manifest gives
  `checkResult NG`; /api/iiif image URLs give 404; lab.ndl.go.jp full text says "This PID is not allowed"). Pages load only through the
  viewer, which fetches tiles with a session token. The text was read from a headless-browser screenshot of the viewer page, and NDL's
  full-text search (POST /api/fulltext/search) found it. The manuscript, 守貞謾稿 巻6 (pid 2592395), is public domain (pdm). I did not open it.
- Evidence date: Kitagawa Morisada, written 1837-1853 (late Edo; the subject is the three cities, Edo/Kyoto/Osaka).
- Verbatim, transcribed from the page image as printed, keeping the old glyph forms:
  「磨師　挿刀庖刀小刀等を磨す又鋸の齒をも磨す蓋刀劔は磨することを得ず別に刀磨工あり（俗に此徒をとぎやと云とぎ師は自刀劔研のこととす）」
  (translation) "Polisher (togi): he sharpens short swords, kitchen knives, small knives and the like, and also sharpens saw teeth. He
  may not polish swords: there is a separate sword-polishing craft (commonly this group is called togiya; togishi properly means
  sword-polishing)."
  The column that closes the page:「下駄齒入れ　下駄足駄等の齒の減じたるを新齒と刺かゆる也　鑄かけ　磨師　齒人等其形相似たり故に磨師と下駄齒人の圖は省畧す」
  The page prints 齒人 twice; I take this as a misprint for 齒入. (translation) "Geta-tooth replacer: he takes the worn teeth of geta and
  ashida and fits new teeth. The tinker, the polisher and the tooth-replacer all look alike, so the pictures of the polisher and the
  geta-tooth replacer are left out." The drawing on this page has a box labelled 「輪フイコ」 (small bellows), and the caption above it
  (「…其扮三都相似たり」) closes the preceding 鑄かけ (tinker) entry. The drawing is therefore the tinker, not the polisher.
- How each copy was checked: 991466 koma 94 was read from the image. For 1444386 koma 95 I matched the OCR text only and did not view
  the page image.
- The front-matter list of itinerant trades (vol. 上 koma 11; 1444386 koma 12) also names 磨師 and 鏡磨き (mirror polisher). That list
  gives no price.
- NO fee is stated in the 磨師 entry. Full-text search found no 研賃 in 991466 or 1444386. The only 研師 hit, koma 87, is a list of
  craft names (「…筆師研師等無限也」).

### 愛媛県史 近世下 (1987), archived (i-manabi.jp ecode:2/63/view/7977) - sword polishing in Uwajima domain
- Evidence date: 寛文2年 (1662), from the domain's 「細工直付定」 as quoted in 『家中由緒書』.
- Verbatim:「同二年二月の「細工直付定」では刀装は鞘の大小やはばき（鎺）の種類ごとに賃金が定められ、研賃は一寸に付古身六分、新身八分であった」
  (translation) "In the 'fixed prices for craft work' of the 2nd month of the same year [Kanbun 2, 1662], sword fittings had wages set by
  scabbard size and kind of habaki, and the polishing fee was, per sun [of blade], 6 bu for an old blade and 8 bu for a new one."
  The page does not say which 分. It is my reading, not the page's, that this is silver fun (0.1 monme) and not gold bu (1/4 ryo):
  6 gold bu per sun would make a two-shaku blade cost about 30 ryo, which is absurd.

VERDICT (1): ATTESTED ONLY FOR sword polishing. A domain-fixed rate per sun of blade (Uwajima, 1662) is attested. For a kitchen knife or
razor, Morisada confirms the trade (an itinerant 磨師 sharpened 庖刀, 小刀 and saws; sword polishing was a separate 刀磨工/とぎ師 trade, late
Edo) but gives NO fee. On the fee for a kitchen knife or razor, the evidence is SILENT. Searched: the archive (研師, 研賃, 研ぎ賃, 磨師,
togishi, sharpener); NDL full text in 991466 and 1444386 (研師, 磨師, 研ぎ, とぎ, 鏡磨, 剃刀, 研屋, 研賃; and in 991466 also 庖刀, 庖丁, 磨賃, 挺); one web query (守貞謾稿 研師
庖丁 剃刀 研ぎ 文 代), which gave nothing relevant.

## (2) Inui Hiromi (乾宏巳; some citations print 宏己)
- 「近世都市における地場産業の歴史的性格 -越前武生の鎌鍛冶業の場合-」, 大阪教育大学紀要 第II部門 29(1), pp.1-20, 1980.
  Repository record: https://osaka-kyoiku.repo.nii.ac.jp/records/2069683 (CiNii crid 2120589364840989568 / 1520290884890516608).
  METADATA ONLY: no full-text file is attached (the JPCOAR `<jpcoar:file/>` element is empty, and Inui's other records in the same
  repository are the same). The paper is not on J-STAGE. Two NDL Digital searches found no digitized copy of the 紀要 issue ("大阪教育大学紀要 第2部門 社会科学・生活科学" and "大阪教育大学紀要 1980" both returned 0
  hits). Publicly readable: NO.
  Only the abstract is public: 「越前武生地方には,近世中期以降より鎌鍛冶業が特殊な地場産業として発展し,現在にいたるまで打刃物業の生産地として継承されている。その形成と発展期における鎌鍛冶業について,鍛冶業者と職人及び問屋商人との関連,及び領主側の対応を中心にして,その具体的な史実を明らかにしたものである。」
  (translation) "In the Echizen Takefu district a sickle-smithing trade grew up as a special local industry from the mid-Edo period on, and
  it continues to this day as a producer of forged blades. For the trade in its formative and growth periods, this paper sets out the
  concrete historical facts, centered on the relations between the smith-masters, their workmen and the wholesale merchants, and on the
  lord's response." It gives no figures.
- 「18世紀における手工業技術の流出と市場構造--堺煙草庖丁鍛冶仲間の場合」, 歴史学研究 385 (1972-06), pp.28-41. CiNii crid
  1520009407840126976 (NDL bib 335251). NDL Digital has digitized this issue as pid 13007471 (https://dl.ndl.go.jp/pid/13007471), but
  its permission is `inlibrary`: it can be read only inside the NDL, not online and not even through 送信 (library transmission).
  Publicly readable: NO.
- Archived secondary source: Kawashima 2012 (立命館文學 627, ritsumei kawashima.pdf, already archived) cites both papers.
  Verbatim:「乾宏己氏は武生・三条などの鎌産地が成立したのも 18 世紀であると述べている」 (translation) "Inui says that the sickle-producing
  centers such as Takefu and Sanjo also formed in the 18th century." It gives no price, output or wage figures.

VERDICT (2): SILENT. Neither paper is publicly readable online, so they give no price, output-per-day or wage figures. The only public
content is the Takefu abstract and Kawashima's one-line "formed in the 18th century".

## Leads not followed
- 類聚近世風俗志 上 koma 61 (pid 991466) quotes 本朝世事談綺 on 「御方庖丁」: 「堺より出るたばこ庖丁也此鍛冶己が妻に合槌を打せ云々」 (OCR
  text, not read off the image). The quotation dates Sakai tobacco knives but gives no price.
- The 守貞謾稿 manuscript 巻6 (pid 2592395, public domain, IIIF should work): the 磨師 entry in Morisada's own hand. A fee is unlikely to
  appear in the manuscript, but it could have a note that the printed edition dropped.
- 武生市史 / 越前市史 (資料編) for the Takefu 鎌 documents Inui used. These may be on NDL as 送信限定 (library-transmission only).
- 堺市史 (1929-31, 第3巻 本編) on the 煙草庖丁 仲間. It may be on NDL Digital as an internet-public item.
