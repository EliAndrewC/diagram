The 222 numbers are ruled in the table below. One contradicts the record: the notice board is drawn 6 x 1.5 ft, where 0190 draws every gate board 16 x 6 ft. One claim is out of date: the program's Research block still gives the servants' row's old size. Two world questions had no claim or recorded search, and both searches came back SILENT. Nothing was edited. One outcome went on the ledger: the Hikone PDF, recorded as rejected.

## Sources

**Record pages** (`/diagram/research/questions/`)

- **`0190-notice-boards-kosatsuba.drawing.html`** (the measured boards are Edo post-town frames). "A board is drawn as a roofed frame 16 ft long and 6 ft deep, on a stone footing inside a fence. … The size is that of the frames measured at Kanagawa-juku and Totsuka-juku, about 16 to 18 ft along the road and 5 to 6 ft deep." `docs/buildings.md:348` says "every gate board … so drawn". The draft draws a 6 x 1.5 ft board. A sheet at 3 px to the foot has room for the true size, so the page's oversized-marker rule for village and city scale does not apply.
- **`0090-magistrates-compounds-jinya-and-yamen.drawing.html`**: "The notice board stands within about 15 ft of a gate in the wall." The board's edges at 8 and 14 ft west of the gate's edge fall inside this.
- **`0165-martial-training-grounds-and-dojo.drawing.html`**: "About 8 by 2 ft, a GUESS joined from two real things…". Also: "A striking post is drawn as a small marker of where it stands. That is a map drawing convention… Carrying the post to a practice ground outside Satsuma is a GUESS, and so is the number drawn." It says nothing on where the posts stand.
- **`0099-the-hearing-court-shirasu.drawing.html`** (attested at Edo only):
  - Mats: "Our maps draw the accused's mat about 6 by 3 ft, and the village officials' mat 12 ft long… The sizes and the spacing are this project's own figures, a GUESS."
  - Clerks: "No page we read gives how large the clerks' place was, so the seats' size is a GUESS."
- **`0105-baths-furo.drawing.html`**: "On the plans our program draws, past the bath, as far as 20 ft out from the kitchen… Both are a GUESS: no page we read places a samurai kitchen's well."
- **`0101-privies-setchin.drawing.html`**: "The privies away from the house stand against the compound's service walls, near a gate." It gives no distance.
- **`0097-staff-rowhouses-and-barracks-nagaya.drawing.html`**:
  - "The barracks is divided into dwellings, each an earth-floored entry and a raised floor."
  - "…every dwelling with a door of its own."
  - It does not say where along a dwelling's frontage the door stands.
- **`docs/building-programs.md`**:
  - Line 37: "a well for the garden and one for the stables; no page places them."
  - Line 105: "no account places a kitchen's or a stable's well."
- **`docs/buildings.md`**:
  - Line 244: the tub is "about 2.5 ft across (~r3.8 at 3 px = 1 ft)", a GUESS on 0100.
  - Line 371: "most building footprint within ~one building-depth of a wall."
- **Neighbors' existing claims** (in `compound_model.py`):
  - `TUB_MAX_GAP_FT`: "0100 … is silent on the distance."
  - `FLUSH_PRIVY_GAP_FT`: "no page gives it."
  - `FIRE_GAP_FT`: GUESS 0116, 6-8 ft between wooden service buildings.
  - `WELL_HALF_FT`: a GUESS, 7.3 ft against 0196's ~4 ft curb (the gap is T33's).
  - `PRIVY_FT`: GUESS 0101, 5 ft.

**Search pass, question A: where along a rowhouse dwelling's frontage did its door stand?** (affects lines 93, 349 and 377)

- Archive copy of eonet `reference-8.html`, describing Edo townsmen's back tenements after the Kyōhō era (premodern practice, but commoners' tenements, not warriors'): 「入り口をくぐると三尺四方の踏み込みの土間、片隅に竈(かまど)と座り流しに水瓶(みずがめ)が置かれていた。」 (translation) "Through the entrance is a stepping-in earth floor three shaku square, with a hearth and a sink and water jar in one corner." It describes what the entry is, not where it sits along the frontage.
- **SILENT.**
  - Archive terms run: 長屋+戸口, 示現流. My first call ANDed ten terms and was refused.
  - Queries: 新発田藩足軽長屋 間取り 土間 入口; 旧新発田藩足軽長屋 文化遺産オンライン 各戸; 武家長屋 一戸 間取り 入口 土間 片側; 松阪 御城番屋敷 各戸 間取り 玄関; one English query on an ashigaru nagaya's entrance.
  - Pages read: the Hikone 北川家 PDF, rejected because it is a detached ashigaru house, not a rowhouse; the archived kotobank 日本の民家 entry, which is about farmhouses and townhouses.
  - The search results gave only general descriptions: Shibata's 1842 eight-unit row, Matsusaka's 1863 row of 19 dwellings.
- The doors at each dwelling's middle are therefore the project's own. The off-middle doors (0.17 and 0.8) are the draft's own collision fixes, as their code comments say.

**Search pass, question B: where on a practice ground did the striking posts stand?** (affects line 661)

- Archive copy of `bujutsukarate.com/zouho/10.htm`, an undated modern commentary on the practice it describes: 「２メートル強ほどの丸太を７０センチほど垂直に地中に埋め込み」 (translation) "a log of a little over 2 m sunk upright about 70 cm into the ground". It gives one post's form, not how many posts or how far apart.
- Archive copy of `nodachi.jimdofree.com`, a modern lineage page: 「稽古場は、露天・素足を基本とし」 (translation) "the practice ground is basically open-air and barefoot". It does not say where the posts stand.
- **SILENT.**
  - Archive terms run: 立木打, 立木.
  - Archive texts read: ja.wikipedia 示現流 and 剣術, kotobank 立木打ち. None bears on count or spacing.
  - Queries: 立木打ち 稽古場 立木 何本 並べ 間隔; one English Jigen-ryu tategi query. Neither found anything that bears.

**Two things the session should fix:**

1. **Stale claim.** `county_magistracy_program`'s "servants' row" claim says "76 x 15 ft and the five dwellings… five of ~15.2 ft". The code has 60 x 15 ft with four 15 ft bays (15, 30, 45), and the `servants_row` docstring agrees with the code.
2. **Labels that conflict with this task's rule.** The zones' claims label the outer yard's bounds CONVENTION and the rear and service yards' bounds "a drawing convention". But spine zones are obstacles the placer keeps clear (`compound.py:144,163`), so their extents are sizes in the world. I ruled them GUESS by their claims, against the reviewer's suggestion of CONVENTION; the session should relabel one or the other.

**Tidy items:**
- `3.65`, `7.3` and `2.5` repeat `WELL_HALF_FT` and `PRIVY_FT` as literals (lines 598, 720-728).
- `1.35` (lines 400-401) is (10 − 7.3)/2, left over from the old corner seat 5 ft in from the garden's edges (commit d83994d00).

## Table
Values that share a ruling on one line share a row, as earlier passes did. Files are under `l7r/diagram/` (pack_audit means `tools/pack_audit/`).

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| compound::composition_plan | 254 | 8 | CONVENTION | title band above the precinct |
| compound::emit_svg | 547 | 8 | CONVENTION | title band above the precinct |
| compound::emit_svg | 609 | 0.25, 0.8 | NONE | text box descent/ascent per font size |
| compound::emit_svg | 624 | 20, 9 | CONVENTION | title font; title 9 ft above the precinct |
| compound::emit_svg | 629 | 0.8 | CONVENTION | zone outline stroke |
| compound::emit_svg | 631 | 11 | CONVENTION | zone caption font |
| compound::emit_svg | 638 | 0.6 | CONVENTION | mat stroke |
| compound::emit_svg | 642 | 8 | CONVENTION | mats caption font |
| compound::emit_svg | 659 | 0.8 | CONVENTION | rack stroke |
| compound::emit_svg | 659 | 8 | GUESS 0165-…dojo.drawing.html | weapon rack 8 ft long ("About 8 by 2 ft, a GUESS") |
| compound::emit_svg | 660 | 8 | CONVENTION | posts caption font |
| compound::emit_svg | 660 | 5.7, 13.3, 11.4, 14.4 | NONE | caption box round both posts (their places ±0.7) |
| compound::emit_svg | 661 | 5, 14, 27 | GUESS 0165-…dojo.drawing.html; SILENT (pass B) | posts' places on the ground (±5 ft across, 14 and 27 ft in) |
| compound::emit_svg | 663 | 0.7, 1.4 | CONVENTION | post marker's obstacle box (0165: "a small marker") |
| compound::emit_svg | 669 | 12 | CONVENTION | scale bar 12 ft above the precinct |
| compound::emit_svg | 671 | 45, 5 | CONVENTION | scale bar mid tick, end ticks |
| compound::emit_svg | 673 | 16, 45 | CONVENTION | scale bar label |
| compound::emit_svg | 674 | 27, 45 | CONVENTION | scale note label |
| compound::emit_svg | 675 | 30, 6, 92 | CONVENTION | scale bar's obstacle box |
| compound::_draw_buildings | 701 | 6, 8 | CONVENTION | name fit margin, smaller font |
| compound::_draw_buildings | 721 | 0.25 | CONVENTION | stable passage fill inset |
| compound::_draw_buildings | 723 | 0.8 | CONVENTION | stall stroke |
| compound::_draw_buildings | 742 | 8 | CONVENTION | room caption font |
| compound::_draw_buildings | 747 | 1.2 | CONVENTION | veranda stroke |
| compound::_draw_buildings | 751 | 8 | CONVENTION | dais caption font |
| compound::_draw_buildings | 759 | 7 | CONVENTION | clerk caption font |
| compound::_draw_buildings | 765 | 0.9 | CONVENTION | "every room named" test for where the name goes |
| compound::_draw_buildings | 766 | 5 | CONVENTION | name goes in a rear alley at least 5 ft wide |
| compound::_draw_walls_and_gates | 815 | 4.5 | CONVENTION | half the 9 px wall stroke (WALL_INK_FT, 0092) |
| compound_example::garden_zones | 74 | 14, 40 | GUESS 0109-…saien.drawing.html | plot's corner in the kitchen yard (site cited, place in it ours) |
| compound_example::garden_zones | 74 | 54, 25, 26, 62 | GUESS (unit's "service yard" claim) | service yard's bounds by the kitchen |
| compound_example::garden_zones | 75 | 14, 25, 66, 62 | GUESS (unit's "service yard" claim) | whole kitchen yard when the plot is off-site |
| compound_example::servants_row | 86 | 60 | GUESS 0097/0115 (docstring; program claim stale at 76) | row length |
| compound_example::servants_row | 87 | 15 | GUESS 0115-…hokonin.drawing.html | row depth ("the 15 ft depth 0115's") |
| compound_example::servants_row | 90 | 6 | NOT-ABOUT-THE-WORLD | placement order |
| compound_example::servants_row | 93 | 0.375, 0.625, 0.875 | GUESS 0097-…nagaya.drawing.html; SILENT (pass A) | door at each 15 ft dwelling's middle |
| compound_example::servants_row | 93 | 0.17 | GUESS (code comment); SILENT (pass A) | west door moved off its middle for the privy |
| compound_example::servants_row | 94 | 15, 30, 45 | GUESS 0097-…nagaya.drawing.html | walls of four 15 ft dwellings (claim stale: five) |
| compound_example::servants_row | 96 | 60, 15 | GUESS 0097/0115 | common-room form's size |
| compound_example::servants_row | 96 | 6 | NOT-ABOUT-THE-WORLD | placement order |
| compound_example::county_magistracy_program | 169 | 102, 35.5 | GUESS 0091-…buke-yashiki.drawing.html | garden's corner at the house's garden face (the veranda line) |
| compound_example::county_magistracy_program | 169 | 46.5 | GUESS 0091-…buke-yashiki.drawing.html | garden depth to y 82 (claim says 46) |
| compound_example::county_magistracy_program | 179 | 22 | GUESS 0091 (claim calls the bounds a drawing convention) | rear yard depth |
| compound_example::county_magistracy_program | 188 | 50.5, 131 | GUESS 0099-…shirasu.drawing.html | hearing court centered on the hall, at its south face (90 + 38 + 2.5 stand-off) |
| compound_example::county_magistracy_program | 193 | 130, 166 | GUESS 0104-…genkan.drawing.html | forecourt's corner inside the gate, east of the gatehouse |
| compound_example::county_magistracy_program | 202 | 190, 126 | CITED 0165-…dojo.drawing.html (21 ft gap ours) | practice ground beside the barracks ("beside its guards' quarters") |
| compound_example::county_magistracy_program | 208 | 130.5, 131, 57.5 | GUESS (outer-yard claim, labeled CONVENTION) | yard from the hearing court's east end |
| compound_example::county_magistracy_program | 213 | 188, 177 | GUESS 0116-…rank.drawing.html | cart yard's corner before the service gate |
| compound_example::county_magistracy_program | 257 | 0.3, 0.35, 0.4 | GUESS 0107-…daidokoro.drawing.html | residence rear door at the kitchen end |
| compound_example::county_magistracy_program | 271 | 13 | NOT-ABOUT-THE-WORLD | placement order |
| compound_example::county_magistracy_program | 284 | 0.3, 0.7 | GUESS 0107 (kitchen-ell claim: door west) | fallback places along the west face |
| compound_example::county_magistracy_program | 284 | 11 | NOT-ABOUT-THE-WORLD | placement order |
| compound_example::county_magistracy_program | 314 | 41, 72 | GUESS 0113-…goyakusho.drawing.html | official study's width and place ("room sizes GUESSES") |
| compound_example::county_magistracy_program | 320 | 0.7, 0.8 | GUESS 0104-…genkan.drawing.html | end-face doors on the front room |
| compound_example::county_magistracy_program | 349 | 0.085, 0.274, 0.482, 0.689, 0.896 | GUESS 0097-…nagaya.drawing.html; SILENT (pass A) | door at each bay's middle (one door each, cited) |
| compound_example::county_magistracy_program | 350 | 48, 65 | CITED 0097/0106 (staff long-house claim) | walls between the 14 ft and 17 ft bays |
| compound_example::county_magistracy_program | 377 | 0.125, 0.375, 0.625 | GUESS 0097-…nagaya.drawing.html; SILENT (pass A) | barracks doors at bay middles |
| compound_example::county_magistracy_program | 377 | 0.8 | GUESS (code comment); SILENT (pass A) | last door moved off its middle for the cell |
| compound_example::county_magistracy_program | 378 | 35, 52.5 | GUESS 0097-…nagaya.html ("four a GUESS") | walls of four 17.5 ft dwellings |
| compound_example::county_magistracy_program | 387 | 0.3 | SEARCHED-SILENT (T36 pass P7, cell-door claim) | cell door toward its west end |
| compound_example::county_magistracy_program | 403 | 5 | NOT-ABOUT-THE-WORLD | placement order |
| compound_parts::_lattice | 145 | 1.5 | CONVENTION | bar length of the cell's lattice front (0096 "bars across its front") |
| compound_parts::_lattice | 147 | 1.5 | CONVENTION | the same, on an east or west face |
| compound_parts::_clerk_seats | 210-213 | 5 | GUESS 0099-…shirasu.drawing.html | clerk seat depth |
| compound_parts::_mats | 221 | 16, 22, 6, 9 | GUESS 0099-…shirasu.drawing.html | plaintiff's and officials' mats' places ("spacing … a GUESS") |
| compound_parts::_flush_privy | 268 | 5 | NOT-ABOUT-THE-WORLD | threshold for a building "standing by" a side wall |
| compound_parts::garden_well | 400, 401 | 1.35 | NOT-ABOUT-THE-WORLD | leftover arithmetic, (10 − 7.3)/2; the well itself SEARCHED-SILENT building-programs.md:37 |
| compound_parts::beside_door_fracs | 435 | 0.15 | NONE | slack past a face's end |
| compound_parts::round_the_corner | 448 | 2.5 | GUESS 0100 (TUB_MAX_GAP_FT: "silent on the distance") | tub's distance off the face |
| compound_parts::_shrine_tree | 494 | 0.15, 0.85 | GUESS 0218-…yashikigami.drawing.html (unit's "tree's seat" claim) | tree seats toward the corner |
| compound_parts::_point_features | 560 | 1.5 | CONVENTION | bath stroke |
| compound_parts::_point_features | 561 | 8 | CONVENTION | bath caption font |
| compound_parts::_point_features | 570 | 7 | CONVENTION | tree caption font |
| compound_parts::_point_features | 578 | 20 | GUESS 0105-…furo.drawing.html | kitchen well as far as 20 ft out |
| compound_parts::_point_features | 578 | 6, 9, 12, 15 | NOT-ABOUT-THE-WORLD | well's search ladder (stables' well SEARCHED-SILENT building-programs.md:37) |
| compound_parts::_point_features | 579 | 7.3 | GUESS (WELL_HALF_FT claim; T33's gap against 0196) | well curb square |
| compound_parts::_point_features | 579 | 0.2, 0.3, 0.7, 0.8 | NOT-ABOUT-THE-WORLD | well beside the door, not before it (no page places one, building-programs.md:105) |
| compound_parts::_point_features | 598 | 3.65 | GUESS (WELL_HALF_FT, a repeated literal) | well boxes privies keep off |
| compound_parts::_point_features | 645, 650 | 0.15, 0.85 | GUESS 0101-…setchin.drawing.html | privy toward the wall end ("against the compound's service walls") |
| compound_parts::_point_features | 651 | 3.5, 4.5, 7 | GUESS 0101 (no distance; FLUSH_PRIVY_GAP "no page gives it") | privy center off the building's face |
| compound_parts::_point_features | 678 | 0.15, 0.85 | GUESS 0100 (place "at the entrance"; end face ours) | tub fallback toward the court |
| compound_parts::_point_features | 685, 687, 691 | 2.6 | GUESS 0100 (buildings.md:244 ~2.5 ft) | tub's seat size |
| compound_parts::_point_features | 685, 687, 691 | 2.5 | GUESS 0100 (TUB_MAX_GAP_FT) | tub's distance off the face |
| compound_parts::_point_features | 688 | 2.5, 2.6 | GUESS 0100 | as above |
| compound_parts::_point_features | 688 | 0.03, 0.05, 0.15, 0.4, 0.6, 0.85, 0.95, 0.97 | NOT-ABOUT-THE-WORLD | fallback seat order along the court face |
| compound_parts::_draw_point_parts | 720 | 3.65, 7.3 | GUESS (WELL_HALF_FT) | drawn curb |
| compound_parts::_draw_point_parts | 720 | 1.2 | CONVENTION | curb stroke |
| compound_parts::_draw_point_parts | 721 | 3.65 | CONVENTION | gear glyph drawn at the curb's size |
| compound_parts::_draw_point_parts | 722 | 3.65, 7.3 | GUESS (WELL_HALF_FT) | caption box is the curb |
| compound_parts::_draw_point_parts | 722 | 8 | CONVENTION | well caption font |
| compound_parts::_draw_point_parts | 724 | 2.5, 5 | GUESS 0101 (PRIVY_FT, a repeated literal) | drawn privy |
| compound_parts::_draw_point_parts | 724 | 0.8 | CONVENTION | privy stroke |
| compound_parts::_draw_point_parts | 725 | 2.5 | GUESS 0101 (PRIVY_FT) | privy box for the hatch test |
| compound_parts::_draw_point_parts | 728 | 2.5, 5 | GUESS 0101 (PRIVY_FT) | caption box is the privy |
| compound_parts::_draw_point_parts | 728 | 7 | CONVENTION | latrine caption font |
| compound_parts::_draw_point_parts | 734 | 1.27, 2.54 | GUESS 0100 (buildings.md:244, r 3.8 px) | tub's registered box |
| compound_parts::_draw_point_parts | 739 | 1.27, 2.54 | GUESS 0100 | tubs caption box |
| compound_parts::_draw_point_parts | 739 | 7 | CONVENTION | tubs caption font |
| compound_parts::_draw_point_parts | 741 | 14, 8 | CITED 0090-…yamen.drawing.html ("within about 15 ft of a gate") | board 8-14 ft west of the gate's edge |
| compound_parts::_draw_point_parts | 741 | 4.5 | CONTRADICTED 0190-…kosatsuba.drawing.html | board's far edge (3 + 1.5 ft depth; the record draws 6 ft deep) |
| compound_parts::_draw_point_parts | 742 | 14 | CITED 0090-…yamen.drawing.html | board's place |
| compound_parts::_draw_point_parts | 742 | 6, 1.5 | CONTRADICTED 0190-…kosatsuba.drawing.html | board 6 x 1.5 ft, against the 16 x 6 ft drawn ("16 to 18 ft … 5 to 6 ft deep") |
| compound_parts::_draw_point_parts | 742 | 0.6 | CONVENTION | board stroke |
| compound_parts::_draw_point_parts | 743 | 14 | CITED 0090 | caption box at the board |
| compound_parts::_draw_point_parts | 743 | 6, 1.5 | CONTRADICTED 0190 | caption box is the board's wrong size |
| compound_parts::_draw_point_parts | 743 | 7 | CONVENTION | board caption font |
| compound_parts::_roji_parts | 769 | 0.67 | GUESS (unit's "stepping stones" claim, 2 x 1.33 ft) | stone half-depth |
| compound_parts::_roji_parts | 771 | 0.8 | CONVENTION | shoe-stone stroke |
| pack_audit/checks::aligned_gaps | 533, 546 | 30, 15 | NOT-ABOUT-THE-WORLD | reporting window: 10 ft shared edge, gaps from 5 ft |
| pack_audit/checks::aligned_gaps | 561 | 15 | NONE | dedupe radius |
| pack_audit/checks::gap_tag | 570 | 8 | GUESS 0116 (FIRE_GAP_FT: 6-8 ft wooden) | wooden gap over 8 ft is loose |
| pack_audit/grids::perimeter_hugging_pct | 151 | 25 | GUESS docs/buildings.md:371 (0116 ring) | "one building-depth" from a wall |
| pack_audit/grids::top_vacant_rects | 195 | 150 | NOT-ABOUT-THE-WORLD | smallest vacant rect reported |
| pack_audit/grids::top_vacant_rects | 196 | 25 | GUESS docs/buildings.md:371 | perimeter band depth |
| pack_audit/mapmatch::load_map | 169 | 8 | NONE | cache size |
| pack_audit/mapmatch::frame | 199 | 5 | NONE | regex group range |
| pack_audit/parse::_parse_labels | 262 | 0.78 | NONE | font ascent figure |
| pack_audit/parse::parse_svg | 425, 433, 443 | 5 | NONE | regex group range |
| pack_audit/roads::_frame | 115 | 5 | NONE | regex group range |
| pack_audit/shared::_path_points | 127 | 6, 7 | NONE | SVG arc arguments |
| pack_audit/shared::ink_bounds | 194 | 0.55 | NONE | character width figure |
| pack_audit/shared::viewbox_cropped | 219 | 5 | NONE | regex group range |
| pack_audit/shared::well_gear | 644 | 15 | CONVENTION | smallest curb marker read as a well (px) |
| pack_audit/sun::sun_at | 78 | 15, 12 | NONE | degrees per hour, solar noon |
| pack_audit/sun::lit_hours | 102 | 24 | NONE | hours in a day |
| pack_audit/sun::casters | 150 | 16 | NONE | circle buffer resolution |
| pack_audit/sun::shaders | 157 | 24 | NONE | hours in a day |
| pack_audit/tagged::marks | 131 | 16 | NONE | cache size |

## Leads not followed
- The repair report for Matsusaka's 旧松坂御城番長屋 (1863) or the Shibata 足軽長屋 (1842) would show where a dwelling's door stood. The [allabout](https://allabout.co.jp/gm/gc/29071/2/) and [kankomie](https://www.kankomie.or.jp/spot/3145.html) pages were not read.
- 菊地ひと美『江戸で部屋さがし』 has a chapter on lower samurai's group houses.
- Running `make archive-find TERMS="雪隠"` would show whether anything archived gives a detached privy's distance from its building.
- [Nagaya (architecture), en.wikipedia](https://en.wikipedia.org/wiki/Nagaya_(architecture)) appeared in the search results but was not read.

Sources:
- [Hikone 北川家 PDF](https://www.city.hikone.lg.jp/material/files/group/4/55_kitagawa.pdf)
- [tabi-mag Shibata](https://tabi-mag.jp/ng0063/)
- [niigata-kankou](https://niigata-kankou.or.jp/spot/5512)
- [allabout Matsusaka](https://allabout.co.jp/gm/gc/29071/2/)
- [kankomie 御城番屋敷](https://www.kankomie.or.jp/spot/3145.html)
- [Nagaya, Wikipedia](https://en.wikipedia.org/wiki/Nagaya_(architecture))
- [jigen-ryu.com](https://www.jigen-ryu.com/?p=2037)
- [kumanichi 示現流史料館](https://www.kumanichi.com/articles/1120230)