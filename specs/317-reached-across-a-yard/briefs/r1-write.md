# Brief - feature 317 (reached across a yard), group R1: was every house reached by a lane? Session 1: write

You are a FRESH session for one part of feature 317. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-performance`); the project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What the GM asked** (2026-10-02): whether the record truly shows that a network of village lanes reached every house, or whether
some households crossed a neighbor's yard or land - *"if that is what the research bears out, then we should go with it."*

**What the entry says now.** `research/questions/0081-village-lanes.html`, the bullet "Was every house in a clustered village
reached by a lane?" answers *"In the villages we have read about, yes, though no page we read states it as a rule"*, on a survey of
a twentieth-century Manchu village (dry northern plain).

**What a research pass found** (a sonnet agent, 2026-10-02; read these pages yourself before you cite them - `make source-pages`
first, then the `source-reader` agent from a bundle, as the record's CLAUDE.md says):

- J. H. Wigmore, *Materials for the Study of Private Law in Old Japan*, Part V "Property: Civil Customs", Section 8 "Sundry
  Servitudes" (pp. 39-43), Asiatic Society of Japan, 1892 - https://archive.org/details/materialsforstu00japagoog (the scan's
  full text is OCR; quote only words that stand clean on the page). Customary passage over a neighbor's land, province by province:
  - Echigo, Kambara kori: of eight plots, "B has a right to pass out to the highway over A's plot, and C over both B's and A's; B
    pays a rent to A, and C to B, but not C to A." (plots, not said to be houses)
  - Izumo, Shimane kori: "where A's land is so situated that he cannot reach the highway without passing over B's land, A has the
    right to do so, but must pay a rent to B or else give him a piece of land as compensation."
  - Bizen, Kamimichi kori: "where the residents of plot B are accustomed to use a drain or take water from a well in plot A, they
    must pay a compensation for the use of the drain or the passage over the land."
  - Suwo, Kyuka kori: "where those living on plot B are accustomed to use a well on plot A ... Where B cannot reach the highway
    without passing over A's land, A must not close the passage to B; but the expense of maintaining it must be borne by both in
    equal shares." (residents: a dwelling's plot)
  - Izumi, Otori kori, "[in towns]": where a plot of "pouch-land" exists a passage must be made to the main street, and "The
    closing of such outlets has for generations been the subject of a prohibition" (towns; the community kept each plot an outlet).
  - Kaga, "[in towns]": where A's house must be reached over B's land, no rent, but A keeps the passage in repair (find it in
    Section 8; the only entry naming a house).
  - Limits to state: the volume does not itself date the reports - say only what it says; by a reviewer's count of Section 8,
    passage over a neighbor's land in seven provinces (Idzumi, Uzen and Kaga marked towns; Echigo, Idzumo, Suwo, Chikugo unmarked)
    and to a well in three more (Kai, Rikuzen, Bizen) - count them yourself; "plot" is not "house" except where residents are named
    (Bizen, Suwo) or a house (Kaga, a town); Echigo's runs as a chain.
- No source the pass read states as a rule that every house fronted a common lane. Read but silent or partial: Morse, *Japanese
  Homes and Their Surroundings* (1886, Gutenberg 52868: small villages strung along one road; at Enoshima "the narrowest of
  alley-ways leading to the houses in the rear"); Embree, *Suye Mura*; Fei, *Peasant Life in China*; Yang, *A Chinese Village*.
  Cite only what you read; an absence note may say what was searched.

## Your items (one question; at most two new registry keys)

- 0081 (`research/questions/0081-village-lanes.html`): rewrite the bullet "Was every house in a clustered village reached by a
  lane?" from what you read - no page states it as a rule; customary passage over a neighbor's land for land with no way of its
  own is attested in Japan province by province (Wigmore), with the limits above - and, if the Morse passage reads as the
  pass says, the rear houses reached by alleys. Reserve the registry key with `make reserve KIND=registry KEY=<key>` and write the
  source's write-up and tags as the record's CLAUDE.md requires. Do NOT edit the drawing page - what the maps draw is the
  engine's, and a later brief brings it.

Keep the entry under the 20,000-byte question cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0081"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram performance (diagram-performance) | 317 | R1 in progress (0081 every house reached?) | 2026-10-02"`.
2. Read the fragment and its notes; `make archive-find` for each source first (the archive before the web), then
   `make source-pages`, then the source-reader agent from a bundle on every passage you will quote.
3. Edit the fragment (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/317-reached-across-a-yard/briefs/r1-handoff.md` (one `- SECTION=0081/<id>` line and a sentence), commit only your
   files (message beginning `317 R1:`), do not push. Your last message is one paragraph.
