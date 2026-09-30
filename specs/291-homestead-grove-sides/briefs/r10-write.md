# Brief - feature 291 (how many sides a homestead grove takes), group R10: the field road's width, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** A settlement-review (Sawada, 2026-09-30) found the ways page contradicting itself on a farm path's width:
- ways/020 ("What vehicle used a village lane, and how wide was it?") says a search "found no numeric width for an
  ordinary village lane or farm path in any language", and sets the map's widths as a convention: 3 ft for a footpath,
  5 ft for the cluster's spine and its field spur, 6 ft for the track out.
- ways/100 ("What was a village lane surfaced with ...") says "A traditional classification of roads, said to be
  Ieyasu's own testament, gives the field road (sakuba-michi) a width of 3 shaku, about 3 ft."
The reviewer's search found the testament attributed to Ieyasu (the Goyuijo Hyakkajo, 御遺状百ヶ条) generally held to be
a later forgery (a page they read: https://websv.aichi-pref-library.jp/wahon/detail/143.html; and kotobank's 道幅 entry,
https://kotobank.jp/word/%E9%81%93%E5%B9%85-2085287). The map draws a 5 ft field path wherever a lane end carries on to
the paddy's bund.

## Your items (two questions; registry keys only if a new source is cited)

- ways/100: read the 3-shaku passage's own source and the testament's standing (run the research pass: `source-reader`
  on the pages above and whatever 100's notes cite). Say what the figure is attributed to and how far that attribution
  is trusted, each claim footnoted to a page read; if the figure cannot be traced to a readable page, say so with an
  absence note rather than keep it.
- ways/020: reconcile it with 100 - the one figure that circulates for a field road, and its standing - and say how the
  map's widths stand beside it: the 3 ft footpath at the figure; the 5 ft spine and field spur above it, a map drawing
  convention (a path the whole hamlet uses to its paddy drawn a rank wider than a door path), unless the research finds
  a reason to narrow it - then say so plainly and name it in your handoff so the engine can follow.

Keep every entry under the 20,000-byte question cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="ways"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R10 in progress (ways 020 100) | 2026-09-30"`.
2. Research pass first (`make source-pages`, then `source-reader` in the background), then read the two fragments and their notes; edit the fragments (never the assembled pages).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. Write `specs/291-homestead-grove-sides/briefs/r10-handoff.md` (one `- SECTION=ways/<id>` line per entry and a sentence
   each, and the engine consequence if any), commit only your files (message beginning `291 R10:`), do not push. Your last
   message is one paragraph.
