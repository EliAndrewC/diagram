# Handoff - feature 250, page `vegetation` (T32), session 1 -> session 2

Session 1 located, read and wrote on 2026-09-26. One `source-reader` read all the claims against the pages saved in
`/tmp/l7r-check/vegetation-pages/` (Meadow, Scythe, Windbreak, Cryptomeria, Coppicing en; 竹林, タケ, 雑木林, 屋敷林, 鎌
ja; PMC7538448). The result: 5 READ, 5 NOT-FOUND, 0 CONTRADICTED. `make record`, `make citations` and the four record
tests are green (257 passed).

## Changed questions

- SECTION=020 (three groves): new note `what-are-the-villages-three-groves---the-windbreak-belt-the-water-mouth-cluster-and-the-dooryard-copse-3`
- SECTION=060 (forest density and crown size): new note `forest-density-and-crown-size-3`
- SECTION=090 (crop margin): new notes `meadow-enwiki` and `the-crop-margin---scrub-stands-6-ft-off-every-field-edge-4`; `meadow-enwiki` added to the Sources roster
- SECTION=110 (cut bank): new note `the-cut-bank---scrub-stands-6-ft-off-every-irrigation-channels-drawn-edge`
- SECTION=150 (bamboo): new notes `chikurin-jawiki-2` and `take-jawiki`

## Registry keys

- KEY=meadow-enwiki: NEW, `research/sources/010-works-cited/9240-meadow-enwiki.html`. It owes `source-applicability`.
- KEY=chikurin-jawiki and KEY=take-jawiki: already registered, now cited for new passages. Their write-ups are unchanged.

## FR-002 items and their forms

1. "with occasional wider emergents" (060): ABSENCE. The only standards on a page read are European (Coppicing en). 雑木林 gives stump regrowth only.
2. "Constant cutting is why woody scrub could not establish within about a scythe's swath (~1-2 m) of a field edge" (090):
   - The causal half is a CITATION, `meadow-enwiki`: land no longer cut or grazed goes to scrub. The note's gloss says the page is general and Western, and says nothing of a field edge.
   - The swath figure is an ABSENCE, `...-edge-4`: no page gives a swath width.
3. "6 ft = one scythe swath" (110): ABSENCE.
4. "A working belt about 10 m tall" (020): ABSENCE. There is no belt height on any page. Cryptomeria's 60 m is the species; its 5-10 m is an ornamental cultivar, so neither is borrowed.
5. "the take-yabu ... at the village edge, harvested like a coppice" (150): two CITATIONS.
   - `chikurin-jawiki-2` supports the edge: the buffer zone between the plain and the satoyama. The gloss says this is framed as the present day and dates widespread groves to the 16th century and after.
   - `take-jawiki` supports the harvest: shoots from the rhizome, plus 竹林's "cutting it moderately". The gloss says the coppice likeness is this page's own inference.

## FR-006

- Item 19 (L0 TOO-SHORT; report `religion-vegetation-and-urban-features.md` V24, the Ryukyu / 300-years half of the Fukugi quotation): CONFIRMED FOOTNOTED.
  - Found by grepping "Ryukyu" in `130-does-scrub-stand-under-a-village-wood-...html` line 34.
  - The sentence carries `pmc7898781-fukugi`, and that note quotes the Ryukyu sentence verbatim: 「It is believed that such rural landscapes ... designed based on Feng Shui concepts in the Ryukyu Kingdom, around 300 years ago.」
  - The mark sits mid-quotation, before the "...". The note covers both halves. No edit was made.

## Left open

- **The "scythe" wording in 090 and 110 is doubtful for the setting.** ja 鎌 says Japanese draws no distinction between scythe and sickle, and no page says scythes mowed Japanese bunds. The prose was not reworded: FR-002 asks for a note, not a rewrite. Session 2's quote-check may raise it; if it does, a rewrite to "a sickle's reach" or to plain "about 1-2 m" is the candidate, and it is the page's own wording to settle.
- None of the three absence notes is `settled`: this is one pass.
