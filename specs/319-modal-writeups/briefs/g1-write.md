# Brief - feature 319 (modal write-ups), G1: the farm kitchen garden. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**Why.** The kitchen garden's map modal is being rewritten to answer what a reader asks of a plot: what it was and who used it,
what it looked like (its surface, its edges, what grew, by season), and how big it was. Question 0039 ("Kitchen gardens beside
farmhouses (yashikibatake)") gives the bed's name and purpose and calls everything else a GUESS with no source: its area, its
crops. Nothing records its look, its edges, who worked it, or what it yielded.

**What a research pass found** (a sonnet agent, 2026-10-04, fetching raw pages with curl; read each page yourself before you
cite it - `make archive-find` first, then `make source-pages`, then the `source-reader` agent from a bundle on every passage you
will quote; the translations below are the pass's and must be your own, marked as translations):

- 愛媛県史 民俗上 (1983), 屋敷取り, https://www.i-manabi.jp/system/regionals/regionals/ecode:2/49/view/6470 -
  「こうして造成された屋敷の面積は平野部の農村で四畝、山間部で二～三畝、島方や漁村では一～二畝で、総じて三畝程度が県下の標準であった。」;
  「大正一三年当時の平均屋敷面積は一二八坪であった。」; 「とはいえ菜園を有したり樹木を植え込む家の割合は半数を越えており、当時の調査担当者は「養鶏、野菜地は少ク庭園、樹林地ハ相当ニ広ク垣、通路ハ約一割ニ近ク其多ハ総平均約八坪内外トナルベキヲ以テ…」と考察を加えている。」 (read the whole sentence: what the eight tsubo is the average OF must be settled from the page, or the figure not used);
  「家の周囲は野菜畑とし、特別な境界を設けなかった。」 (a hillside house, Hisatani). Homestead areas; over half of households with a vegetable plot or trees (1924 survey); a vegetable field round the house with no special boundary. Taisho survey and oral accounts, Ehime: state the period.
- 清良記 巻七 (c. 1629-54, Iyo), as quoted in 愛媛県史, https://www.i-manabi.jp/system/regionals/regionals/ecode:2/49/view/6464 -
  monthly lists of the kitchen garden's vegetables (「二月に取って食する野菜菜園の事」, 「正月取りて給る菜蔬野菜の事 △萱草 △蕪莢 △大根 △芹 △薺 △牛房 …△韮 △夏菜 △葱 …」), and on the same page Meiji-Taisho accounts that vegetables came only from the household's own growing (Ozu: 「野菜は自家栽培に限っていて、…ダイコン・ニンジン・ゴボウ・ネギ・ネブカなど一〇種類くらいのほか、フキ・ミツバ・ヨモギ…」; Matsumae: daikon cut and dried for the lean season). Limit: the Seiryoki names 菜園 in its headings but does not say the plot was beside the house; its author was a warrior-landlord. This is the record's first EDO-PERIOD evidence of what the bed grew, by season.
- 宮代町史 民俗編, 屋敷構え, https://adeac.jp/miyashiro-lib/texthtml/d100020/mp100020-100020/ht061560 -
  「前菜畑には、自分の家で食される野菜類などが植えられている。主に日常の葉物・大豆・サツマイモ・里芋などが栽培されていた。畑が近いと家に害虫が入ってくるといわれるが、遠いと収穫に行くのが大変なので、結局は近くに作っておくことになるという。」; sibling pages ht061550 (the plot on the way from the lane to the house) and ht061590 (「農家の場合、屋敷の周りは生垣で囲われることが多い。」). Kanto plain, twentieth-century folk memory: state it; sweet potato is an eighteenth-century arrival in the Kanto, so say so if you cite the list.
- ja.wikipedia 家庭菜園 (already cited as `kateisaien-jawiki`): the same section adds the regional names (センザイバタ, サエンバ, カドノハタケ) and that the plot was often on marginal ground away from the house - a corner of the homestead, beside the fields, a riverbank.
- 補農書, Zhang Lüxiang, 1658, Tongxiang (Zhejiang), http://agri-history.ihns.ac.cn/books/bns.htm (http-only: `curl -sL http://...` if a fetch refuses) -
  「…则编篱为圃，一以养生，一以御盗…俗篱用槿易成，然实寡用而不固，不若间以枳橘，杂以五茄皮、枸杞三物有刺，可御暴客。…园中菜果瓜蒲，惟其所值，每地一亩，十口之家，四时之蔬，不出户而皆给。」 and 「基址宽旷，则前植榆、槐、桐、梓，后种竹木，旁治圃，中庭植果木。」 A fenced plot beside the house, a thorny hedge, one mu feeding a household of ten its vegetables year round. Prescriptive, one scholar-farmer: state it. This bears on 0039's south-China question and on its area guess (one mu is several hundred sq m - convert with a source for the Qing mu, or say the unit's size is not given here).
- Marginal: 佐藤甚次郎「日本農家の建物構成と配置方式」 (1962), https://www.jstage.jst.go.jp/article/jjhg1948/14/6/14_6_445/_pdf - the Shonai front yard often fruit trees, flower beds or a yashiki-batake. The record may already carry this passage (grep `0046`/`0006` for 「花畑」).
- Searched and NOT found (for absence notes): who worked the bed (women, the elderly) - nothing; an Edo-period yield or the share of a household's vegetables from the bed - only the qualitative accounts above; fencing against hens and manuring the bed with night soil - nothing for the household plot; 農業全書, 百姓伝記, 会津農書 on the vegetable bed - no open full text.

## Your items (one question; at most four new registry keys)

- 0039 (`research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.html` and its notes): replace the crop GUESS
  with what the sources give (the Seiryoki's seasonal lists, the later accounts), with their limits; add what the bed looked
  like (its edges: often no special boundary, the farmstead hedged around; rows or ridges only where a source says so) and where
  it lay (beside the house on the approach, or on marginal ground away from it); add the size evidence and say plainly how it
  bears on the 10-140 sq m guess, which stays a GUESS for Japan unless a source sizes a Japanese bed; answer the south-China
  question from the 補農書 with its limit; an absence note for who worked it and for yield. Keep each assertion's evidence class
  honest in the `Evidence:` comment.

Do NOT edit any drawing page or any modal file - a later step writes the modal.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0039"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G1 in progress (0039 kitchen garden) | 2026-10-04"`.
2. Read the fragment and its notes; `make archive-find` for each source first, then `make source-pages`, then the source-reader
   agent from a bundle on every passage you will quote. Reserve any new key with `make reserve KIND=registry KEY=<key>`, and write
   its two write-ups and tags as the record's CLAUDE.md requires.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/g1-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 G1:`), do not push. Your last message is one paragraph.
