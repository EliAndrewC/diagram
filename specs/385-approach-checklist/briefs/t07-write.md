# Brief - feature 385 T07, how far a farmhouse wall stood from a village lane. Session 1: write

You are a FRESH session for the record edits of one task. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What is asked** (feature 385 T07, a ranking row of feature 328: "the 4 ft wall-to-tread margin (`TREAD_WALL_FT`) has no
source; research the clearance or claim it UNRESEARCHED"): record what a search pass found on the gap between a village house's
wall (or its eaves' drip) and the lane beside it. The maps keep a lane's tread 4 ft clear of a farmhouse wall, a GUESS on a
townhouse's three-shaku eaves strip; the pass suggests about 3 ft. Research features annotate the record; edit no code, modal or
sheet.

## The pass's findings (verify each passage yourself before citing it; these are leads, not citations)

- Wigmore, *Materials for the Study of Private Law in Old Japan* (1892), Part V ch. II s.2 "Vicinage", pp. 25-39 (archive.org
  `materialsforstu00japagoog`; the registry already holds `wigmore-1892-servitudes` - cite the same source at these pages, a
  new registry key only if the record's rules want one): Mino, Ono kori - "No such proceedings are necessary in case of a house
  in a village, but a house must stand back about 3 feet from the boundary line of a road or of cultivated land; this is called
  'shade-withdrawal.'" (the "feet" are shaku, his footnote: "One jo = ten shaku"; NB the scan prints 3 as 8 elsewhere -
  this entry reads a clean 3). Also Totomi, Sano kori (towns build close; villages "far enough away from the boundary to shed
  the rain on one's own land"), and Chikugo, Yamato kori (towns "close up to the highway line"; villages so that "rain is not
  shed by either on the adjoining premises"). Late-Tokugawa custom (compilations of 1877 and 1880).
- Wang Zhenghua 王正華, 「清代华北乡村田宅交易中的"水"」, 重庆大学学报(社会科学版) 2021, 27(1),
  http://qks.cqu.edu.cn/html/cqdxskcn/2021/1/20210123.htm (saved by the pass in `/tmp/l7r-pass/cqu-dishui/`): the drip ground
  (滴水) at a house's wall foot - 嘉祥县 "建筑房屋，须留滴水地二、三尺" (2-3 chi), 平遥县 6 or 8 cun from the wall foot; a
  rural 1868 deed bounding a plot by the wall's drip; deeds that meet a road name the road as the edge with no strip. Qing deeds
  1692-1909 and the 1930 customs survey (the article's own caveat on that survey's reliability).
- Silent: no rural figure for how far a farmhouse's eaves projected, in China or Japan.

## Your items (one question)

- **0081** (`research/questions/0081-village-lanes.*`):
  1. **The record.** On the findings page (`.html`), under a heading a reader would ask (for example "How far did a house
     stand back from a village lane?"), state what was found - the Japanese village rule of about 3 shaku back from a road's
     boundary, the drip strip a house kept on its own ground (Chinese 2-3 chi at the wall foot; a Japanese village set back to
     shed its rain on its own land), that Chinese deeds meeting a road name no strip, and that the eaves' projection is not
     attested - each assertion footnoted to a passage quoted verbatim (English translation marked as one), China first. Where
     the sources are silent, an absence note whose HTML comment names the searches run (the pass's: amaochi 雨落ち 民家; 軒の出
     民家 寸法; 雨落ち溝; 滴水 屋檐 距离 村; 散水 宽度 民居; 屋檐 出檐 尺寸 民居; 滴水線 地界; eaves drip line village house lane).
  2. **On the drawing page** (`.drawing.html`), one sentence on how our maps settle it: a lane's tread is kept about 3 ft clear
     of a farmhouse wall - a house's drip strip on its own ground, the Japanese village's 3 shaku - labeled with the finding (an
     attested figure for Japan; China's drip strip the same order).

Keep the question under the 20,000-byte cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0081"`. If another session holds it, stop and say so in your handoff. Else
   `make research-claim Q="0081" FEATURE=385`.
2. For each page you cite, `make archive-find URL=<u>` first, then `make source-pages`, then the `source-reader` agent from a
   bundle on the passage. A new source takes `make reserve KIND=registry KEY=<k>` and its registry write-up.
3. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with a message opening `385: `.
4. Write `specs/385-approach-checklist/briefs/t07-handoff.md`: one `- SECTION=0081/<id>` line per changed heading, then a sentence
   naming what was found. Release the claim (`make research-claim Q="0081" FEATURE=385 STATUS=done`). Do not push. Your last
   message is one paragraph.
