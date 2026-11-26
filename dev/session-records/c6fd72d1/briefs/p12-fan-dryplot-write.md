# Brief - feature 449 T432, T428 (0057, 0006, 0011), session 1: write (where a fan's wet ground lies and the deviation that draws a wet side, from a search pass; a dry plot's square to its canal, its grounds and limits restated and its taper at a bend, from a second pass; which end of the canal the last band starts from)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or
tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command;
`git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your files
by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file, the `Makefile` or any pop-up
(`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
read by line range; send the lookups you know you need in one message. Touch no question but the three named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0057, 0006 and 0011 for feature 449 before starting you. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects six to ten, ranked under the passes below. A page over the 20,000-byte prose cap is
SPLIT along its topics, never trimmed (`make question-sizes`); a size edit never drops a claim-bearing word. Every finding
is labeled; no guess is given as a finding. A GUESS about the physical world owes a citation or a dated ABSENCE note
(never a GROUNDS note); a drawing fallback of ours may take a GROUNDS note (`this project's decision`,
`a drawing convention`). Before writing GUESS for a physical figure, search (archive first); if you FIND a figure, write
the finding and report `FOUND` in the handoff.

**An item tag** is EMPTY, inside its `<li>`, just before `</li>`:
`<span class="item" data-item="<slug>" data-label="ATTESTED|GUESS|CONVENTION|DEVIATION" data-guess="<what is guessed>: <why no page says>"></span>`.
The block's own visible words must carry the label (a GUESS block holds the word GUESS; a convention the word convention).
Each new GUESS below takes its OWN `<li>` and its own tag: never fold a guess into a block that already carries a tag.
Do NOT change any existing tag's `data-item`, `data-label` or `data-guess` (the pop-ups that cite it would owe checks).

**Two research passes, read on the page.** Two read-only passes of 2026-11-24 are saved; their passages are LEADS
until you read each on its archived copy (`make archive-find URL=<u>` or `KEY=<k>`) or its URL yourself, and quote it
as YOU read it there:
- `/home/agent/.claude/jobs/c6fd72d1/tmp/passes/pass-449-t432-wet-ground-fan.md` (15 KB; sources A-O, then "Reading",
  about lines 106-128). For item F1.
- `/home/agent/.claude/jobs/c6fd72d1/tmp/passes/pass-449-t428-dry-plot-shape.md` (21 KB; sources 0-8, then "Reading",
  about lines 166-241). For item F2.
`grep -n '^#' <file>` gives each section's line; read by section, not whole. Caveats the passes state, which bind you:
MAFF's Table 7.2 (B) was reassembled from a two-column table's split cells, so quote only a cell you read whole on the
page; the RIHN guide's third passage (I) is stitched around figure labels, so do not quote it as one sentence; the
Tonami booklet's quote (F) had its furigana removed by the pass, so quote the page's own text as the archive holds it.
The pass's own readings - Niiza's 1949 photograph (Fig. 2-9), Santome's base map (Fig. 2), and the link between
Santome's bending road and its plots' distortion - are the pass's inference: never write them as a source's statement.

**Archive and keys.** Every page you cite must have an archived copy (the record build refuses a cited URL with none):
`make archive-find URL=<u>` first; where none is held, reserve the key and then `make archive URL=<u> KEY=<k>`. Grep
`research/sources/010-works-cited/` for each URL (percent-decoded) before any reserve. Already in the registry (reuse,
no new key): `senjochi-jawiki` (ja.wikipedia 扇状地), `maff-nogyoyosui-suiden` (the farm ministry's paddy design
standard, nougyouyousui_suiden-1.pdf), `sakaori-ishizumi` (the Sakaori terraces' water page), `suido-ishizue-yachida`
(ishizue 01/08), `woods-westbrook-2006`, `waju-jawiki` (ja.wikipedia 輪中), `ishizue-musashino`,
`santome-shinden-allotment` (Yamamori 1992, AIJ Transactions no. 436), `saitama-santome-history` (the Saitama page
908-20091216-188 on the Nobidome canal). NEW keys, in the order worth reserving (stop when the finding is carried; at
most ten; if `make reserve` refuses an eleventh, the rest go to a continuation brief - say so in the handoff):
1. https://www.sciengine.com/doi/pdf/85A1ECD0FB5246F783B66610FC0F36BE (Deng and Luo 2011, the Yongding fan's springs and
   lakes on its front margin, Northern Wei to Qing: China first);
2. https://databank.tonamino.jp/sansonkaiteiban (the Tonami booklet: a great fan's sides and toe cleared first);
3. https://suido-ishizue.jp/daichi/part2/03/03.html (the same, a second source);
4. https://www.chikyu.ac.jp/publicity/publications/others/img/yatsu.pdf (RIHN's yatsu guide: seepage where the valley's
   slope meets its floor);
5. https://www.maff.go.jp/j/nousin/keityo/kankyo/attach/pdf/suiden_seibi_kaisetu-29.pdf (the catch channel along a hill
   foot against cold seepage);
6. https://www.city.niiza.lg.jp/uploaded/attachment/7104.pdf (Shinbori p. 56; Nobidome village p. 54);
7. https://www.city.niiza.lg.jp/uploaded/attachment/7103.pdf (p. 14: no strips where the same canal irrigated);
8. https://adeac.jp/mizuho-lib/texthtml/d100070/mp000070-100070/ht000830 (Shimo-Moro'oka, a strip widening to its back);
9. the Ehime prefectural history of 1988, 扇状地と集落立地 (the pass gives only its archive id, 47/478a16705d8b: find its
   URL with `make archive-find TERMS="扇状地と集落立地"`).
10. https://www.city.niiza.lg.jp/uploaded/attachment/7105.pdf (ch. 2 section 4, p. 1: the canal used from its digging
   for drinking and household water) - ONLY if neither the `ishizue-musashino` note nor 7103.pdf p. 14, as you read
   them, carries the drinking-water statement F2 needs.
Drop, if the cap bites: 9, then 8, then 3. Each new key's write-up states its limits
(a modern synthesis, a modern standard, one district) as the passes give them.

**Left alone on purpose.** Every existing tag's `data-item`, `data-label` and `data-guess`, with ONE stated exception
below (F1's own tag). On 0057's drawing page the blocks "The marsh is as wide as the fields above it, with 90 ft more on
each side." (except the one word F1 fixes in it) and "The marsh's upper edge follows the foot of the fields, point by
point." stand. On 0006's drawing page, the block "Why square the plots to the canal rather than to the paddy's slope?"
and its HTML comment (the GM's 2026-07 pricing of the softened shear) stand word for word; `dry-plot-off-water` and
`barley-hamlet-toe-band` stand. 0006's research page (85 bytes of room) is not touched. 449 T432's code change (cutting
the drawn wet ground off at the fields' lower corners) comes AFTER this pair, from what the page then says: do not write
that the code will change, and do not write that the wet side SHOULD be cut.

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment counts and a
tag's `data-guess` does not): 0057 research 2,717; 0057 drawing 8,129; 0006 drawing 2,442; 0011 drawing 14,661.

## Cascade expected (for the coordinator; not your work)

What cites the changed pages at 7cb42eb6d1, which of them STATE the thing changed, and which need a DIRECTED check
(`make claims-bundle UNITS=... REASON=... PAGES=...`: a claim is re-owed only by a page it cites, and one saying "the page
is silent" is cleared unread when the page gains a new block). Claim paths are under `rust/phases/src/`.

- 0057 research page (5 pop-ups, 0 claims) and drawing page (3 pop-ups, 5 claims). SHOULD re-check: `hamlet/marsh` (its
  About says "along the springs where the water that sank into an [alluvial fan]..."; Depiction "its upper edge following
  the foot of the fields": IN-STEP expected, a GAPS finding possible - the valley-wall finding),
  `choice/cluster_position--valley_mouth`, `choice/cluster_position--on_rise` (both cite both pages; the "perimeter" fix
  is in a block they may rest on); claims `driver/toe.rs` `toe_band#toe band edge`, `PAD#toe band edge` (IN-STEP; T432
  will owe them again). SHOULD clear: `choice/fan_middle--wild`, `choice/fan_middle--cleared` (research page only: unless
  they quote "edge of permeable fans"), `toe_band#toe band width`, `PAD#toe band width`, `toe_band#flaring flanks`.
  DIRECTED (state the wet ground's extent, cite another page): `seat/margins.rs` `ranked#not on the wet toe` (cites 0058),
  `seat.rs` `open_at_an_end#a seat astride the brook leaves by its open bank` (cites 0035, 0081; it says "its windward
  flank on the wet toe"), `driver.rs` `stage_seat#the way out's walls` (cites 0081), `seat/margins.rs`
  `SQUARE_EPS#the square end in` (cites no page; states the fall square to the wind) - each with `PAGES=<0057's drawing
  and research pages>`.
- 0006 drawing page (9 pop-ups, 41 claims). SHOULD re-check: `field/dry.rs` `Canal.frame#square to the canal` and
  `hem#square to the canal` (they quote "each plot a rectangle square to the canal where it stands": DRIFTED fix: claim
  likely, the bend clause), `driver/check.rs` `check#no dry plot on the water`; pop-ups `hamlet/barley`,
  `hamlet/buckwheat`, `hamlet/millet` ("small rectangular plots": IN-STEP expected, GAPS possible at the bend),
  `choice/winter_crop--barley`, `hamlet/farm-holding` (if it states the strips' frame). DIRECTED (say "silent on how far
  a plot may taper"): `field/dry.rs` `PINCH_SHARE#the pinch`, `pinched#the pinch` (then restated to cite
  `dry-plot-taper-at-bend`), and `hem#a column's climb ends` (cites 0011; states the pinch). SHOULD clear: the other
  four pop-ups (`choice/grain_drift`, `fan_middle--wild`, `fan_middle--cleared`, `hamlet/soy`) and about 35 claims.
- 0011 drawing page (10 pop-ups, 20 claims). SHOULD re-check: `field/dry.rs` `hem#the last band from the canal's start`
  (DRIFTED and held since P4: says "silent" - restate to cite `clearing-starts-plots-nearest` with "the toe end"),
  `field/build.rs` `build#the climb's order` (IN-STEP). SHOULD clear: all 10 pop-ups (none states which end the last band
  starts from) and the other 18 claims.
- After this pair: 449 T428 closes with no code change if the check session agrees (its handoff says so in a named
  line); 449 T432's code takes its rule from F1's block and the check session's applicability ruling.

## Your items

- **F1 `0057`: where a fan's wet ground lies, and the deviation that draws a wet side** (research page
  `research/questions/0057-marshes-and-wetlands-shitchi.html` and its drawing page `.drawing.html`, with their notes and
  originals).
  1. THE FINDING, on the research page (its findings page; 0 claims cite it), in the section "Much of the wet ground below
     a village's fields lies at the foot of an alluvial fan.", as new `<li>` blocks after "Villages and paddy have
     gathered along a fan's spring line since ancient times.": (a) on a fan the springs and the wet ground lie at its toe
     and front margin - China first (Deng and Luo 2011: the Yongding fan's spring belt and the lakes in its fan-margin
     depressions, from the Northern Wei to the Qing), then Japan (`senjochi-jawiki`: the water table deep except near the
     toe; the Ehime history, if reserved); (b) no source read puts seepage or marsh along a fan's SIDES, and two Japanese
     sources class a great fan's sides, with its toe, as the watered ground cleared first for paddy (Tonami; ishizue
     03/03) - farmed ground, not ground kept off; (c) a wet side is attested ONLY for a valley floor whose fields run
     against a hill or terrace foot, in Japan: seepage comes out where the slope meets the floor (RIHN; the design
     standard's valley-floor row), only along the steep side at Sakaori, and it was still farmed, as cold wet paddy with
     a catch channel along the hill foot (MAFF 承水路; Sakaori's teaze); China has only hill-foot springs and cold
     spring-soaked hill fields, with no side position (the pass's M and N: cite them only if you read them); and no
     source read says hamlets kept off that strip. Label each: ATTESTED ONLY FOR its case; SILENT on building there. If
     the blocks do not fit the research page's 2,717 bytes, put (c) on the drawing page as its own `<li>` just before
     the deviation block, and say so. Also the wording fix in the research page's block "How wide is the wet ground below
     an alluvial fan?" (line 19 at HEAD, footnote `woods-westbrook-2006`, "often found on the edge of highly permeable
     fans"): the study says wetlands "are found on the perimeter of
     highly permeable alluvial fans", and the one it studied lies at the fan's base and toe - write "perimeter", and that
     its own wetland lay at the base and toe, from the page you read.
  2. THE DRAWING PAGE. The same "edge" -> "perimeter" fix in the block "The marsh is as wide as the fields above it, with
     90 ft more on each side." (line 8, "slope wetlands are found on the edge of permeable fans"): that word only, and
     the clause it needs to stay true. Then the block "Where the fields narrow inward downhill, the wet ground climbs
     their side." (line 12, tag `toe-on-tapering-flank`): KEEP its label (DEVIATION), its first sentence (what the point-
     by-point edge draws), "drawing it so is easier than cutting the marsh off at the fields' lower corners", and its last
     sentence (a house, a cluster and a track keep off it; the link to 0031's drawing page). RESTATE its grounds: the
     sources put a fan's springs at its toe and its sides among its early-cleared farmland (link the research page's new
     blocks), so on a fan the wet side is a deviation; a wet side is attested only along a valley floor against a hill
     foot, and there it was farmed as cold wet paddy, not left as reed. STATED EXCEPTION to "do not change an existing
     tag's `data-guess`": rewrite this tag's `data-guess`, keeping its `data-item` and `data-label`, to "That the wet
     ground climbs a side of the fields that narrows downhill: the sources read put a fan's springs at its toe and its
     sides among its early-cleared land; a wet side is attested only for a valley floor against a hill foot." (no pop-up
     cites this slug: grep at 7cb42eb6d1). Do NOT rule whether a hamlet's narrowing side is a valley wall: that is the
     check session's applicability check; write the valley-wall case as what the sources attest, not as this map's case.
  3. Bring the drawing page's `Evidence:` comment in line in a few words (the deviation's grounds).
- **F2 `0006` drawing page: the dry plot squared to its canal - its grounds, its limits, and the bend**
  (`research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html`; its notes and originals).
  1. The block "A dry plot beside a canal stands square to it." (line 42; no tag) says "each is a rectangle square to the
     canal where it stands, so neighbors abut continuously along the canal, nothing is sheared or stepped". At a bend the
     map does not draw a rectangle (item 3): add a clause excepting the bend that points to item 3's block, and no more.
  2. The block "Were strips squared to their canals Edo-period work?" (line 44; no tag) - the frame's grounds. Keep it a
     RECONSTRUCTION. Restate: the Edo Musashino row villages' household strips (house lot, fields, woodland) were laid
     square to a straight settlement road (Yamamori 1992, `santome-shinden-allotment`, p. 97: the plan principle), in
     some villages a road running beside the canal - at Shinbori, in Nishibori village, opened 1661, the strips meet a
     road parallel to the Nobidome canal at right angles (Niiza 7104.pdf p. 56) - and that canal was dug for drinking
     water (cite the page you read it on: 7103.pdf p. 14, the `ishizue-musashino` note, or key 10; `ishizue-musashino`'s
     own words are "canals dug along the highways", so the block's "the canals that watered them" goes). State the frame's two limits: at Nobidome village itself the highway crosses the canal, so the
     strips there ran ALONG the canal (7104.pdf p. 54); and where the same canal irrigated, no strips formed (7103.pdf
     p. 14). Strips' boundaries were straight and sharp (Yamamori p. 99); name the known departures in one clause (a
     strip widening toward its back, Shimo-Moro'oka, if reserved; irregular plots at Gōbara and Torisu, Yamamori's table).
     Keep "squaring them to a paddy's canal is this project's own". No premodern source in either country gives the shape
     of a single dry plot beside an irrigation canal: say so.
  3. NEW `<li>` after the "Were strips squared ..." block: how the drawn plots meet a canal's bend. Read the code first
     (read only, at HEAD: `git -C /diagram/.clones/diagram-backlog show HEAD:rust/phases/src/field/dry.rs`, about lines
     55-65 `PINCH_SHARE`, 95-105 `hem`'s climb, 300-315 `pinched`): each strip stays square to the canal where it stands,
     so where the canal bends toward the dry side the strips converge as they climb and taper; a strip whose inner or outer
     edge would run under half a plot's length is not drawn, and that column's climb ends there. Say it in words a map
     reader follows; name no engine identifier. A GUESS about the physical world: an ABSENCE note dated 2026-11-24 - both
     countries are silent on a canal's bend; the nearest analogues are a bending boundary road with split or detached
     shares (Santome) and converging roads made good with irregular land elsewhere (Shimo-Moro'oka), neither showing a
     wedge-shaped or curved strip. Tag: `<span class="item" data-item="dry-plot-taper-at-bend" data-label="GUESS" data-guess="That where a canal bends a dry strip stays square to it and tapers, and is not drawn once an edge runs under half a plot's length: no source read in either country says what a strip did at a canal's bend."></span>`.
  4. Bring the page's `Evidence:` comment (line 6, "reconstruction (strips square to a canal, from the Edo Musashino
     villages' line along the canals ...") in line, and add the taper to its guess list.
  If `make question-sizes` lists the page after items 1-4, do NOT split it on your own (no section is chosen for a
  move, and 41 claims cite the page): stop, leave the edits in place, and report F2 `OPEN` with the page's size and the
  bytes over; never cut. This closes 449 T428's page half; T428 needs no code change unless the check session finds the code does
  not do what item 3 says.
- **F3 `0011` drawing page: which end of the canal the last band starts from**
  (`research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html`).
  The block "The clearing starts from the plots nearest the toe." (line 10, tag `clearing-starts-plots-nearest`, no
  `data-guess`) says "The last band ... is laid from the canal's start along it until the need is met." In the code the
  hem's line runs from the fan's FOOT up the flank (P4's cascade read it: `field/build.rs` `hem_in`, k = 0 at the foot;
  `dry.rs` keeps that order), so "the canal's start" is its TOE end - the opposite of where its water enters, at the
  head, which is how a reader takes "start". Reword to "is laid from the toe end of the canal, up along it, until the
  need is met". Nothing else in the block changes; the tag stays as it is.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p12-fan-dryplot-write.md`: `- SECTION=0057 0006 0011`
   (plus any split page), one line per item `F<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
