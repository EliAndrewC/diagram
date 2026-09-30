<!-- page-load: kind=assertions -->
# Brief - feature 291 (how many sides a homestead grove takes), group R13: three sentences the reviews found, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** The settlement-reviews of 2026-09-30 found three sentences in the record saying more, or other, than the
record supports. Change each to what its own evidence says; add no new finding.

1. **homesteads/155** ("How was a row village laid out?"): its summary sentence ("on a dike, a levee or a fan's foot ...
   the houses followed its line") goes further than its own bullet on the fan's foot ("That is a row of villages; how
   the houses lay within each is not said"). Bring the summary into line with the bullet: the houses followed the line
   on a natural levee or a dike; a fan's foot carries a row of villages, and the map's reading of a row along it is this
   project's reading.
2. **homesteads, the fields section's water paragraph** (the one citing the dispersed farm's water, footnotes near "the
   dispersed farm, which has its own well"): homesteads/200 now answers that a dispersed farm has its own WATER - on the
   Tonami plain often a channel led into its grounds (accurate), its own well this record's reading (a GUESS). Make the
   paragraph say the same, citing homesteads/200's sources as that entry does or pointing to it.
3. **The spelling of 列村**: the record writes it "ressen" and "retsuson" in homesteads/155 and towns/390. Its attested
   reading is れっそん, resson (kotobank, https://kotobank.jp/word/%E5%88%97%E6%9D%91-878864). Use "resson" in the prose;
   the glossary entry already glosses it under resson with the other two as variants.

## Your items (three places; no new registry key unless kotobank's entry is not yet a key - then one)

- homesteads/155, the homesteads fields-section water paragraph, towns/390: as above. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R13 in progress (homesteads 155, the fields water paragraph, towns 390) | 2026-09-30"`.
2. Find each fragment by grep over its page's directory; edit the fragments (never the assembled pages).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. Write `specs/291-homestead-grove-sides/briefs/r13-handoff.md` (one `- SECTION=<page>/<id>` line per entry, a sentence
   each), commit only your files (message beginning `291 R13:`), do not push. Your last message is one paragraph.
