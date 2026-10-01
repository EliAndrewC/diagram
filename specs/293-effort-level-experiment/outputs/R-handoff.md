# Handoff - feature 293, task R: the servants' quarters (session 1: research and write)

- SECTION=buildings/910
- KEY=shinke-nagayamon-kanazawa
- KEY=kochi-hantei-jstage
- KEY=hoppou-shibata-ashigaru
- KEY=qianggen-siheyuan-layout

## Outcome

The record now has a new question, buildings 910, "Did the servants' rowhouse have one door, or a door for each household?".
It finds that both forms are attested for servants, so the answer is a KNOB. The first form is a row of dwellings, each
with its own entry. Evidence for it:

- Mitamura's front and middle rowhouses.
- The Shibata row of 1842, whose eight households were servants and rope men, not foot soldiers.
- The Kochi domain's Osaka and Kyoto plans of the 1790s, read by Uematsu, Nakajima and Tani, with dwellings down to the
  permanent servants and gatekeepers.

The second form is a common room behind one entrance: the chugen lived in large common rooms, and the Shinke gate range
in Kanazawa has a chugen room of two six-mat rooms, with one entrance named. A row of walled dwellings sharing one door
is on no page read. For China, servants lived in a Beijing house's south range, and a three-bay range had one door;
how the servants' bays were entered was not found.

The rule on the page: the servants' quarters takes one form per compound. It is either a common room of open or
sliding-partitioned bays with one door, or dwellings of one or two bays each with a door of its own. Both forms are
accurate; the share of compounds that take each, and how many bays a common room runs to, are guesses. Walled bays
behind one shared door are never drawn.

**What the Ubame sheet should draw:** its four bays with one door are the common-room form and are accurate as drawn,
provided the bay divisions read as sliding partitions within one room, not walls between dwellings. If a later change
rolls the other form for Ubame, it takes a door to each dwelling. The sheet, engine and maps were not changed.

**Searched 2026-09-29, with the session's web search tool:**

- Japanese:
  - 中間部屋 大部屋 武家屋敷 間取り 長屋
  - 長屋門 中間部屋 入口 戸口 間取り 武家屋敷
  - 足軽長屋 各戸 入口 土間 間取り 復元
  - 大名屋敷 表長屋 間取り 一戸 入口 勤番長屋
  - 中間部屋 大部屋 雑居 中間 小者 屋敷 住み込み
  - 旧厚狭毛利家萩屋敷長屋 内部 部屋 入口 間取り
  - 長屋門 両側 中間部屋 物置 馬屋 図 復元 武家住宅 土間 出入口
  - jstage 藩邸 長屋 平面 中間 部屋 割 戸口 論文
  - 中間長屋 平面図 藩邸
  - 旗本屋敷 間取り 表門 長屋 中間部屋 若党部屋 図
  - 陣屋 代官所 中間部屋 下男 長屋 間取り 復元
  - 高山陣屋 長屋 中間 部屋 入口 間取り
- Chinese:
  - 四合院 倒座房 仆人 居住 门
  - 衙署 衙役 住房 班房 仆役 居住 清代 县衙 布局
  - 下房 仆人 居住 官邸 清代 宅院 佣人
  - 倒座房 间数 明间 开门 次间 隔断 四合院 房门
  - 四合院 一明两暗 明间 开门 暗间 不直接对外开门
  - 倒座房 每间 单独开门 还是 一门 仆人住 格局
  - 北京四合院 "两侧两间仅向堂屋开门"
- English:
  - samurai residence nagaya servants' quarters chugen room layout door
  - Chinese courtyard house servants' quarters daozuofang each room door opening onto outer courtyard

About 35 pages were saved and grepped, all under `/tmp/l7r-check/293-r-e2-pages`. Every page's outcome is on the
sources-consulted ledger, under the question `buildings/910`.

## Checks run in this session

- One `source-reader` over 14 claims: 12 READ, 1 NOT-FOUND (how the servants' rooms of a Chinese house were entered),
  and 1 that was READ in two files and NOT-FOUND in six.
- `source-applicability` on the 4 new keys: all APPLICABLE-WITH-LIMITS. Their edits were applied:
  - Shibata is a single row, not back to back; it was restored in 1971-72, and it stood outside any compound.
  - The Shinke page names one entrance but does not rule out a second door.
  - The Kochi plans do not tell walls from doors, and the Kyoto gatekeepers had no earth floor.
  - The Beijing door rule is claimed for Beijing only.

The record checks (quote-check, record-format) were NOT run; they are owed to the next session.

## Left open

- The Kochi note `kochi-hantei-jstage-4` quotes p. 46: "the plans make no distinction between walls and fittings, so
  this was decided taking account of the entrances, earth floors, privies". The sentence does not name what "this" is.
  `source-applicability` read the page images and says it is each dwelling's extent. The quote-check should confirm
  that from the page.
- The Kochi quotes keep the PDF text layer's vertical-form punctuation (︑︒), and one quote writes 土間 where the text
  layer's OCR reads 土聞. `make quote-verbatim` may flag both.
- The `source-reader` noted that the Mitamura transcription contradicts itself on who lived in the middle rowhouse
  (its lines 19 and 27). Question 910 does not rest on that rank wording, but question 900 does ("men below full
  samurai rank down to the foot soldiers"). That is 900's to check, not changed here.
- For the GM (default taken: none needed): the share of compounds taking each form is left to the engine as a guess.
- Pages directory: the brief named `/tmp/l7r-check/293-r-pages`, but it already held another run's pages (saved
  21:55-22:15). A few of this session's pages were added to it before this session switched to its own directory,
  `/tmp/l7r-check/293-r-e2-pages`.
