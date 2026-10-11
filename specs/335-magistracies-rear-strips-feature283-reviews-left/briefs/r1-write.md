# Brief - feature 335, R1: a well on a guest's roji (0104) and the door rule (0117). Session 1: write

You are a FRESH session for one part of feature 335. This brief is the whole of what you need; do not read the feature's spec
or plan. Work in this clone (`/diagram/.clones/diagram-magistracies`); the project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**Why.** Feature 335 redraws the hand-drawn magistracy sheets. Two of its decisions rest on the record, and the record must say
them before the sheets do:

1. Hayakawa's sheet draws a working draw-well at the middle gate's mouth, beside the guest's first stepping stone of the roji to
   the reception (no-genkan form, research 0104). A building review asked: was a draw-well ever on the roji's line? A search pass
   (2026-10-11, archive then web) found NONE on a residence's guest roji; wells stood by the kitchen or bath, or in an official
   compound's front court near the formal entrance; the one tea-roji well curb found (Jo-an, Uraku-en, inscribed 1615) is an
   homage copy of Murata Juko's, not shown to be a working well. Feature 335 will remove the well from the roji's mouth (the
   kitchen's own well stands about 13 ft from the bed it watered). 0104's DRAWING page must carry the finding, so the sheet's
   comment can point at it.
2. Feature 335 settles one door convention for every sheet: a door's block is set WHOLLY INSIDE the building it is the door of,
   flush to the wall it opens through (a map drawing convention; the generated plans already draw it so). Measured 2026-10-11, the
   hand sheets did NOT set it so (59 doors: 24 inside, 26 outside, 9 straddling the wall line); feature 335 redraws them inside.
   0117's drawing page says the program's door "is set flush inside the building's wall, as they set one" - the "as they set one"
   was untrue of the sheets until the redraw - and its rule paragraph says only "touching the wall".

## Your items (two questions; new registry keys at most four)

Questions to edit: 0104 (its drawing page), 0117 (its drawing page)

- **0104 drawing page**: add one bullet in the page's voice, e.g. **A guest's roji carries no well.** Its body: on the roji from
  the middle gate to the veranda the record finds stepping stones and a water basin, and no draw-well; the working wells of
  samurai houses stood by the kitchen or the bath, and at an official's compound one stood in the front court beside the formal
  entrance; so our plans draw a house's working well on its service side or its front court, never on the guest's path. Footnote
  each assertion from the sources below (verbatim, translated and marked as a translation). Where you cannot read a source, drop
  it rather than cite it; the absence half (no page we read puts a well on a guest's roji) is an absence note saying what was
  searched (archive and web: 露地 井戸, 茶庭 井戸 井筒, 武家屋敷 中門 露地 井戸, 塀中門, 旧小関家 井戸; the Edo garden manuals
  Tsukiyama teizoden and Kokon sado zensho vol. 5 are not readable online). Mention the Jo-an well curb only if you cite it, as a
  tea garden's homage piece.
- **0117 drawing page**: the rule bullet **A door glyph sits flush to the wall it opens through.** says the door is set WHOLLY
  INSIDE the building it is the door of, its outer edge on the wall it opens through - never a slab standing outside the wall,
  never straddling the wall line, never floating just inside it - and that this is a map drawing convention every plan follows,
  hand-drawn and generated alike. In the program bullet, keep "as they set one" only if it is true after feature 335's redraw (it
  will be: write it as the one convention both follow). Do not write about what the sheets used to do.

The search pass's sources (read each yourself with `make source-pages` before you quote it; `make archive-find` first):

1. Shiroishi, old Koseki house - already registered as `shiroishi-koseki` (cited on 0104): its roji runs from the middle gate to
   the zashiki's veranda, and its archived text never names a well.
2. Matsue, Shiomi-nawate samurai house (Adachi 2012), https://coc.lib.shimane-u.ac.jp/files/attach/1/1504/SMC002-07.pdf :
   「主屋の東側に井戸が現存している。…台所、あるいは浴室との関係から有りうる配置関係にあると思われる」
3. Iwama jin'ya (Kasama city, from an 1827 drawing), https://www.city.kasama.lg.jp/sp/page/page006384.html :
   「長屋門がありました。ここを通ると白壁に囲まれた役所が置かれ、正面には玄関の式台が、右手には井戸がありました。」
4. Urasenke house (Agency for Cultural Affairs database), https://online.bunka.go.jp/db/heritages/detail/122434 :
   「台所（土間、板間及び事務室、井戸付）」
5. (optional) Jo-an, Uraku-en (Japan Tourism Agency), https://www.mlit.go.jp/tagengo-db/en/R4-00289.html : "The round well cover
   in the southwestern corner was made as an homage to one owned by wabi-cha progenitor Murata Juko".
6. (for the absence) kotobank 庭園: 「茶庭の骨組みをつくっているのは，飛石と手水鉢である。」

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0104"` and the same for `0117`, then
   `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram magistracies (diagram-magistracies) | 335 | R1 in progress (0104, 0117) | 2026-10-11"`.
2. Read the fragments and their notes; reserve each new registry key with `make reserve KIND=registry KEY=<k>`; read every source
   you quote with `make source-pages` and the source-reader agent from a bundle, in the FOREGROUND, before you write the note.
3. Edit the fragments (never a built page). Then `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. Write `specs/335-magistracies-rear-strips-feature283-reviews-left/briefs/r1-handoff.md` (one `- SECTION=<NNNN>/<id>` line per
   question touched and a sentence each), commit only your files (message beginning `335 R1:`), do not push. Your last message is
   one paragraph.
