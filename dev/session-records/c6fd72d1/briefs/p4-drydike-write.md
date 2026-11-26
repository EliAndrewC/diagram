# Brief - feature 449 T425 (0006, 0011, 0013, 0027), session 1: write (guesses the field code makes that no page records: a dry plot off the water, the last band's start, a resting plot's one state, the willow's crown and the rows' gap; and, from 449 T423 and T421, a dry plot's taper at a canal's bend and a barley hamlet's one band of the toe)

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
read by line range; send the lookups you know you need in one message. Touch no question but the four named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0006, 0011, 0013 and 0027 for feature 449 before starting you; if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects none. A page over the 20,000-byte prose cap is
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

**No research pass was run for this brief**: its items record guesses the field code already makes and no page states.
Five are drawing fallbacks of ours (GROUNDS notes; two of them item D5, added 2026-11-24 from feature 449 T423 and T421); ONE is a physical figure - a dike willow's crown - and for that you
search before writing GUESS (archive first, `make archive-find TERMS=...`; then the web if the archive is silent). No
new registry key is expected unless that search finds a crown width.

**Left alone on purpose.** On 0027's drawing page the block "The band changes in width and is mottled, never a ruled
line." (its sentence "mottled with patches of earth of different ages, as repairs are") is a placeholder of feature 449
T422, whose builder is still working. Do NOT touch that block; a later brief carries it if T422 reports a page
correction. (An earlier plan had the coordinator fill it first: superseded.) Also untouched: 0006's RESEARCH page (85
bytes under the cap); every existing tag's `data-item`, `data-label` and `data-guess` (among them
`clearing-starts-plots-nearest`, `two-four-whole-plots`, `resting-plots-lie-toward`, `fan-s-toe-taken`). On 0006's
drawing page the block "A dry plot beside a canal stands square to it." carries the GM's ruling of 2026-07 in its HTML
comment ("dry plots are rectangles laid out against the canal"): keep the comment and the block's rule; item D5 adds one
clause to it and no more.

**Already recorded - do not add again**: the mulberry bush's crown (4.4 to 7 ft across, a GUESS) is on the dike-pond
question's drawing page (0018, tag `bush-few-feet-across`) and the pond-dike crops question's (0026); on 0027 a link to
one of them is enough.

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment counts and a
tag's `data-guess` does not; 0006 now takes three new blocks, D1 and D5's two - keep each to two or three sentences):
0006 drawing 3,863; 0011 drawing 14,774; 0013 drawing 15,746;
0027 drawing 10,903 (its research page 1,430: not needed).

## Cascade expected (for the coordinator; not your work)

Every item ADDS a guess beside blocks that stand, so few units state what changes.

- 0006 drawing page (9 pop-ups, 41 claims at 9162aa3953). No pop-up states the off-the-water rule. SHOULD re-check, for
  item D5: `hamlet/barley`, `hamlet/buckwheat`, `hamlet/millet` (each Depiction says "a hem of small rectangular plots"
  and that "the plots keep to its toe": IN-STEP expected, the page's opening keeps "small rectangular plots"),
  `choice/fan_middle--wild` ("its dry fields keep to the toe": IN-STEP; a GAPS finding is possible, the one band drawn
  in full), `choice/winter_crop--barley`. SHOULD clear: `choice/fan_middle--cleared`, `choice/grain_drift`,
  `hamlet/farm-holding`, `hamlet/soy`. Claims SHOULD re-check, in `rust/phases/src/`: `field/dry.rs` `refused#off the
  water`, `hem.rs` `CLEAR_FT#off the water`, `driver/check.rs` `check#no dry plot on the water` (then restated to cite
  `dry-plot-off-water`); perhaps `dry.rs` `refused#a plot onto rice dropped` and `hem#a plot onto rice dropped` (the
  block beside the new one); and for D5 `field/dry.rs` `Canal.frame#square to the canal` and `hem#square to the canal`
  (both quote the block D5 adds a clause to: IN-STEP expected), `PINCH_SHARE#the pinch` and `pinched#the pinch` (each
  says the page is "silent on how far a plot may taper": the tool will probably clear them unread - a DIRECTED check;
  then restated to cite `dry-plot-taper-at-bend`), `field/build.rs` `TOE_SHARE#the toe` and `hem_bounds#the toe's band
  whatever the grain asks` (then citing `barley-hamlet-toe-band`). SHOULD clear: the other 30 or so. State D5's facts
  and cite ANOTHER page (the coarse-grain question's drawing page, 0011, also a stem of this brief, so re-owed only if
  the block they rest on moves - a DIRECTED check with `PAGES=<0006's drawing page>`): `field/dry.rs` `hem#a column's
  climb ends` (the pinch), `field/build.rs` `build#the hem's line`, `hem_in#the hem's line` and `hem_bounds#the hem's
  climb` (the toe's one band).
- 0011 drawing page (10 pop-ups, 13 claims). SHOULD re-check: `choice/fan_middle--wild` and `choice/winter_crop--none`
  (both state "from the plots nearest the toe first: no source says from which end": IN-STEP expected, the block keeps
  that); claims `field/dry.rs` `hem#the last band from the canal's start` and `field/build.rs` `build#the climb's order`.
  SHOULD clear: the other eight pop-ups and 11 claims.
- 0013 drawing page (3 pop-ups, 11 claims). SHOULD re-check: claims `field/states.rs` `states#a resting plot from the
  green` (the one that states it), perhaps `REST_PLOTS#resting plots`; pop-up `hamlet/fallow` (the resting plot's own
  pop-up; IN-STEP expected). SHOULD clear: `choice/paddy_rest--settled`, `--unsettled`, and the other nine claims.
- 0027 drawing page (5 pop-ups, 14 claims). SHOULD re-check: `hamlet/perimeter-dike` (states the 8.5 ft and 4.4 ft
  spacings and "crowns read as touching trees": IN-STEP expected), `choice/field_archetype--polder_grid` (the same
  sentence); claims `field/dike.rs` `CROWN_FT#the crowns`, `GAP_HALF_FT#the gap`, `dike#the rows cut at the gaps`,
  `driver/polder.rs` `draw_polder#the band cut where a channel crosses`. SHOULD clear: `choice/dikepond_split--0.5`,
  `choice/field_archetype--mulberry_dike_fishpond`, `hamlet/sluice-gate`, and the other 10 claims.

## Your items

- **D1 `0006` drawing page: a dry plot keeps off every water** (`research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html`; its notes `.drawing.notes.html`).
  The blocks "The plots keep to the dry side of the canal, behind a bare bank." and "A plot that would lap onto another
  canal's rice is dropped." stand. No page says what the maps also do: a dry plot that would come within its clearance of
  ANY drawn water (a canal, a ditch, the brook, a pond), or that would hold the end of one, is dropped. Add a NEW `<li>`
  after those two, labeled a GUESS - a drawing fallback of ours, the easier of dropping the plot or reshaping it; no page
  read says what a farmer did with a plot a ditch ran into (GROUNDS note, `this project's decision`). Tag:
  `<span class="item" data-item="dry-plot-off-water" data-label="GUESS" data-guess="That a dry plot coming within its clearance of any water is dropped rather than reshaped: no page read says how a dry plot met a ditch it did not belong to."></span>`.
- **D2 `0011` drawing page: where the last band of the clearing starts** (`research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html`; its notes `.drawing.notes.html`).
  The block "The clearing starts from the plots nearest the toe. That order is a GUESS: no page we read says from which
  end the clearing went." (tag `clearing-starts-plots-nearest`, note `where-a-farming-hamlet-grew-its-coarse-grain-2`)
  covers the order of the bands. Uncovered: the LAST band, the one the need only part-fills, is laid from the canal's
  start along it until the need is met. Add that clause to the SAME block, inside its GUESS (it is the same guess: which
  end the clearing went from); change no tag. This is the ONE stated exception to the rule above that a new guess takes
  its own `<li>`: it widens a guess already tagged, and the tag carries no `data-guess` to go stale. Only if on reading the block you find it a second, separate guess, give it
  a NEW `<li>` with tag `data-item="last-band-from-canal-start"`, `data-label="GUESS"` instead, and say which you did.
- **D3 `0013` drawing page: a resting plot is never one already drawn in another state** (`research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html`; its notes `.drawing.notes.html`).
  The blocks "A settlement given the unsettled form rests two to four whole plots in each field." and "The resting plots
  favor the far end of the water's run." stand, tags and all. No page says: a plot chosen to rest is taken only from the
  plots still drawn green - never one already drawn wet, flooded or gold. Add a NEW `<li>`, labeled a GUESS: a fallback
  of ours so that no plot carries two states; no page read says a resting plot could not also be flooded (GROUNDS note).
  Tag: `data-item="resting-plot-one-state"`, `data-label="GUESS"`, a `data-guess` in the standard form. Use the page's
  own words for the states (read how it names them); name no engine identifier in visible text.
- **D4 `0027` drawing page: the willow's crown, and the gap in the rows at a crossing channel** (`research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html`; its notes `.drawing.notes.html`).
  - The block "The willows are drawn about 8.5 ft apart, looser than the Willow Palisade's planting." gives the spacing
    and says the crowns "read as a run of touching trees". The crown's own size is on no page: a willow is drawn 7 to
    11 ft across (a radius of 3.5 to 5.5 ft). This is a physical figure: search for the crown width of a dike or
    pollard willow (the archive first; this question's research page and its sources, among them `willow-palisade`). If a
    page read gives one, write the finding with its citation and report `FOUND`; if none, a NEW `<li>` after that block
    recording the 7 to 11 ft as a GUESS, with an absence note dated today. Tag `data-item="willow-crown-size"`,
    `data-label="GUESS"`. For the mulberry's crown, one linked clause to where it is recorded (above), no new guess.
  - The block "Where a channel crosses the dike, the band is cut, and the rows stop with it." gives the cut, not how
    far the rows stand back: they stop about 15 ft to each side of the channel's middle line. Add a NEW `<li>` after it,
    labeled a GUESS, a fallback of ours (room for the sluice and its banks; no page read gives the bare stretch beside a
    sluice) with a GROUNDS note. Tag `data-item="rows-gap-at-channel"`, `data-label="GUESS"`.

- **D5 `0006` drawing page: a plot tapers at a canal's bend, and a barley hamlet's dry fields are the toe's one band** (the same two files as D1; added 2026-11-24 from feature 449 T423 and T421).
  **COORDINATOR'S OVERRIDE (2026-11-24, corrected the same evening): write ONLY the barley hamlet's toe band (`barley-hamlet-toe-band`). Do NOT add the clause excepting a bend and do NOT write `dry-plot-taper-at-bend`: what a dry plot's shape is along its canal and at a bend is feature 449 T428's research question, not yet answered. ALSO, on the block "A dry plot beside a canal stands square to it": its HTML comment says "the GM's ruling, 2026-07: dry plots are rectangles laid out against the canal". The GM made no such ruling (docs/gm-rulings.md, "NOT a ruling", his words of 2026-11-24). REMOVE that comment and put nothing in its place; do not change the block's visible words, whose label is the page's own (its Evidence line: reconstruction). Report the removal. Wherever this brief names the taper item, the bend clause or that comment as the GM's ruling, this paragraph overrides it.**
  - The block "A dry plot beside a canal stands square to it." reads: "The plots are laid end to end along the canal's
    own curving line, and each is a rectangle square to the canal where it stands, so neighbors abut continuously along
    the canal, nothing is sheared or stepped, and only the outer, upslope edge is ragged." Since feature 449 T423 that
    is not true at a bend: where the canal bends toward its dry side, the strips standing square to it converge as they
    climb, and a plot there is drawn tapered - its narrower end no shorter than half a plot's length; where a strip
    would pinch below that, it ends, and no sliver is drawn. Keep the block's rule and the GM's comment, and add ONE
    clause to its sentence that excepts a bend and points to the block below. Then a NEW `<li>` after it, labeled a
    GUESS, a fallback of ours: the page draws small rectangular plots of about a sixth of an acre and no page read says
    how a strip of plots met a bend in its canal; half a plot's length is where a strip stops reading as a plot (GROUNDS
    note, `this project's decision`). Tag:
    `<span class="item" data-item="dry-plot-taper-at-bend" data-label="GUESS" data-guess="How far a dry plot may taper where its canal bends, to half a plot's length: no page read says how a strip of plots met a bend; past half its length a strip reads as a sliver, not a plot."></span>`.
    Name no engine identifier in visible text (the code's own account, read only: the claims `PINCH_SHARE#the pinch`
    and `hem#a column's climb ends` in `rust/phases/src/field/dry.rs`). Report in the handoff, as `OPEN` for the coordinator, one line: the GM's
    ruling of 2026-07 reads "dry plots are rectangles laid out against the canal", and the page now records a taper at a
    bend as what the map draws.
  - The block "Each map decides at random whether an alluvial fan's dry middle is left wild." says "where the middle
    stays wild the hem keeps to the fan's toe and leaves the middle to scrub", and the block "A fan's toe is taken to
    begin two-thirds of the way down the slope from its head." (tag `fan-s-toe-taken`: leave it) says where the toe
    begins. Neither says how much of the toe a hamlet draws when its coarse grain is winter barley on the paddy (the
    coarse-grain question's drawing page, 0011, in this brief, keeps such a hamlet's dry fields on the toe: read its
    block before you write). What the map draws since feature 449 T421: such a hamlet's dry fields are ONE band of plots along the canal,
    from the point where the toe begins down to the foot, drawn in full whatever grain the barley leaves owed - before,
    the band held only the grain still owed, so a hamlet whose barley met its whole need drew no dry field at all. Add a
    NEW `<li>` after the two-thirds block, labeled a GUESS, a fallback of ours: no page read says how much dry ground
    such a hamlet kept on the toe (GROUNDS note). Tag `data-item="barley-hamlet-toe-band"`, `data-label="GUESS"`, a
    `data-guess` in the standard form (it may hold the measurement: 209 of 209 such rolls drew no dry field before,
    over 450 rolls of seeds 1 to 150, measured 2026-11-24). Link 0011's drawing page; do not restate its rule.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p4-drydike-write.md`: `- SECTION=0006 0011 0013 0027`
   (plus any split page), one line per item `D<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
