<!-- page-load: kind=assertions -->
# Brief - feature 444 T28, the dry fields behind the houses recorded. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** The round arbiter's ruling on ask:444-T27-seat-hem (2026-11-04): the Rust field lays the dry hem "just upslope of
the supply canal", which on about one seed in ten stands where the houses would, so the seat finds no margin. A research pass of
2026-11-04 found where a clustered hamlet's houses stand against its dry fields. Record that finding on 0006 and redraw 0006's
drawing page to it. Two questions at most; no new registry keys beyond the one source below.

## The finding to record (from the research pass; verify each quote against the source before citing it)

- Source: Yamamoto Shozo et al., 「鉾田町鳥栖地区における土地利用の構造」, 地域調査報告 6 (University of Tsukuba, 1984),
  http://www.geoenv.tsukuba.ac.jp/~chicho/nenpo/6/01.pdf - a scanned PDF with no text layer (the pass read it by OCR and checked
  the sentences against the page images). Archive it first (`make archive-inbox`, `make archive-find`; `research/CLAUDE.md`); if it
  cannot be read, do not cite it - say so in the handoff and stop.
- The hamlet: Torisu Hongo (本郷), Ibaraki, dated by the authors to before the Edo period; its "traditional" land use rests on the
  1876 cadastral map (地引絵図) and the army survey of the mid-1880s (迅速図).
- p. 7: 「本郷の伝統的な土地利用のセットは第3図のa)に示されている。集落は洪積台地と巴川低地との境に位置し，塊村形態を呈している。集落前面の巴川低地には水田が立地し，集落背後の洪積台地には畑地が立地している。さらに畑地の外側を取り囲むように林地と採草地が広がっている。つまり，集落を中心にして，水田と畑地，採草地を含む林地は圏状に配列されている。」 (the paddy in front of the settlement, the dry fields behind it, woodland and grass beyond)
- p. 7: 「水田―集落―畑地―林地という本郷のセット」 (paddy - settlement - dry fields - woodland)
- p. 11: 「本郷では従来より水稲が最も重要な作物であり…したがって，集落が水稲の近くに立地し，畑作物への配慮はあまりなされなかった。」 (the settlement stood close to the rice)
- Reading for the record: ATTESTED ONLY FOR one clustered plateau-edge hamlet with paddy, evidence of the 1870s-1880s read back to
  the pre-modern hamlet: paddy, then the houses, then the dry fields behind them. NOT ATTESTED in the pass: a belt of dry fields
  between the houses and the paddy. Kitchen plots by the house (0039) are a separate thing and stay as they are.

## Your items

1. 0006's finding page (`research/questions/0006-dry-fields-and-their-crops-hatake.html`, its notes and originals): a block on
   where the dry fields stand against the houses, citing the source above verbatim (Japanese original in the originals file, the
   English marked as a translation), with its date of evidence and its reach (one hamlet; form (b)).
2. 0006's drawing page (`research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html`): where it draws "a hem of small
   rectangular plots just upslope of the supply canal that runs along the paddy's high edge", draw the hem BEHIND the settlement
   where the settlement stands on the paddy's high edge - the houses between the paddy (its canal) and the dry fields - and just
   upslope of the canal along the rest of that edge; label the choice as the record's finding (historically accurate for the
   attested case) and note that a single hamlet attests it.

## The procedure (session W: write)

1. `make research-claim Q="0006" FEATURE=444`.
2. Edit the fragments, then `make record && make citations` and the record tests; `make quick` green but for its known failures.
   Commit with messages opening `444 T28: `.
3. Append to `specs/444-work-budget-program/briefs/t28-hem-handoff.md` (with `make append`) a `## Session W` section: each block
   changed (`- SECTION=0006/<id>`), its anchor, the registry key added.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
