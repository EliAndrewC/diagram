# G7 handoff - the map-story kinds (session 1: research and write, 2026-09-27)

## Sections and keys for the check sessions

- SECTION=buildings/590
- SECTION=buildings/600
- SECTION=buildings/610
- SECTION=buildings/620
- KEY=inukai-kotobank
- KEY=takagari-jawiki
- KEY=kishuken-jawiki
- KEY=inugoya-jawiki
- KEY=shosai-kotobank
- KEY=kyoto-ga-sanshisuimeisho
- KEY=chinesepen-shuzhai
- KEY=wakan-kotobank
- KEY=kyakhta-trade-enwiki
- KEY=madoken-odoguchi
- KEY=hongofuji-koiwai
- KEY=s-kent-kuratomae

## Outcomes

- R48 ACCURATE (the dogs) / SILENT (the kennel) - buildings/590: warrior households hunted with dogs (hawking dogs kept by dog-handlers under the chief falconer, hawking widespread among the daimyo, boar hunted with dogs, a domain lord nursing his own hunting dog), and dogs housed inside an official's compound are attested once (Kitami, 1693, as dogs in care, beside the office, gatehouse and kitchen); no page gives a household kennel's form, size or place, nor ties it to the stables - `kennel` (U): the kind's Note should say hunting dogs at a samurai household are ACCURATE and cited (`takagari-jawiki`, `kishuken-jawiki`, `inukai-kotobank`), the kennel's form, ~11 ft square size and seat beside the stables stay a GUESS; `Entry:` becomes `research/buildings.html - 'Did a samurai household keep hunting dogs, and where were they kept?'`; its label can stay `guess` (the drawn thing is the building, which is still unattested) and `Sources:` gains the three keys.
- R49 ACCURATE (the form) / SILENT (at an official's compound, and its size) - buildings/600: a study could be a room or a building (`shosai-kotobank`); Rai San'yō built a detached study-cum-tea room on his Kyoto estate in 1828 and it alone survives, garden on its west (`kyoto-ga-sanshisuimeisho`); the Chinese study stood in the quiet part of the compound beside the rear garden (`chinesepen-shuzhai`); no page gives a detached study at an official's compound or a detached study's size - `writing pavilion` (U): the Note's "the research record has no entry on one" is now wrong; it should say the detached garden study is an attested form (a scholar's estate, a Chinese compound) while putting one in a magistrate's inner garden, and its 18 x 14 ft size, are a GUESS; `Entry:` becomes the 600 heading; label may stay `guess` (placement at a magistracy) or the orchestrator may judge it `accurate` for the form - I recommend keeping `guess` because the sheet's claim is the magistrate's pavilion.
- R50 SILENT - buildings/610: no page describes a room across a border line or a meeting on the line itself; the two attested forms of regular dealing across a border both keep each party on its own ground - a post on each side facing each other (Kyakhta and Maimaicheng, `kyakhta-trade-enwiki`) or a compound the host sets aside with its reception hall adjoining (the Japan House at Choryang, `wakan-kotobank`) - `parley room`, `parley mats` (U): both stay `deviation`; their Notes can now name what history had instead (paired posts, or a set-aside compound) and point `Entry:` at `research/buildings.html - 'Did two sides ever meet in a room built across their border?'` (keep the 'Drawing a clan border' pointer for the drawn line). Ubame's `.notes.md` line 40 says meeting on the line "is the standard practice wherever two jurisdictions must transact regularly" - nothing read supports it; that sentence is unsourced and should be cut or rewritten to the 610 finding (it is the map's design notes, not the record, so it is the orchestrator's call; the inventory's "For the GM" item on "meeting on the border line is standard practice" is answered on the history side: not attested).
- R51 ACCURATE - buildings/620: an ordinary door was up to half a ken (~3 ft; this project's reading of the big door's definition, marked as such), a farmhouse's everyday earth-floor entrance a one-ken (~6 ft) sliding door with a wicket in it, a storehouse's hinged leaves 3.5 x 6 shaku each; no page gives a kitchen door, a guest entrance or a storehouse opening; the drawn doors (measured, 3 px = 1 ft) run 3.3-10 ft, the kitchen and lodging doors 8-8.7 ft - `door` (O H U): the kind's Note and Caveat both say "No source gives a drawn door's width" - now wrong; they should say a drawn door's width is a CONVENTION (drawn two to three times an ordinary half-ken door so it reads) and end with the real widths (~3 ft ordinary, ~6 ft a one-ken main door, a storehouse leaf ~3.5 ft); `Sources:` gains `madoken-odoguchi`, `hongofuji-koiwai`, `s-kent-kuratomae`; `Entry:` gains the 620 heading. The duplicated Note/Caveat sentence in `grounds.py` `Door` should be said once. Whether the 8-8.7 ft katteguchi/lodging doors and Hayakawa's 8.7 ft karo's side door (3.3 ft on the other two sheets) should be redrawn narrower is a map question for the orchestrator; the record supports either calling them a convention or narrowing them.

## Left open, and why

- No correction to an existing section was owed: nothing on the do-not-edit list, and no other section was found wrong.
- `scripts/_source_pages.py` numbered a third save's files from the manifest's row count, which a retried failed pointer does not raise, so the third save overwrote retried pages of the same host (it lost the jawiki 引き戸 page here, re-saved as 25). Fixed in this session: `next_index` numbers past every row and every file; `tests/tooling/test_source_pages.py::test_a_third_save_numbers_past_a_retried_page`.
- The clone carried uncommitted glossary changes at the start of this session (`assets/glossary.json` modified; `glossary/9590-inu-bashiri.json`, `glossary/9600-Five Highways.json` untracked) from another group; not mine, left unstaged. `make record` did not touch them.
- The saved pages are in `/tmp/l7r-check/g7-pages` (MANIFEST.txt; the 引き戸 line is marked OVERWRITTEN).
