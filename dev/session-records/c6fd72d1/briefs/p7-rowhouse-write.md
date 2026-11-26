# Brief - feature 452 T003 (0097), session 1: write (how long a staff rowhouse ran: the 80 to 145 ft range restated from a research pass)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 452's spec, plan or
tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command;
`git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your files
by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file, the `Makefile` or any pop-up
(`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
read by line range; send the lookups you know you need in one message. Touch no question but the one named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0097 for feature 452 before starting you (this clone holds it for 449; the claim sheet names both); if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects up to six. A page over the 20,000-byte prose cap is
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

**The research pass.** A pass of 2026-11-24 is saved at
`/home/agent/.claude/jobs/c6fd72d1/tmp/passes/pass-452-t003-rowhouse-length.md` (29 KB). Read by section, not whole:
its opening ("Where the record's 80-145 ft comes from", lines 1-16), section 1a (Sayama), 1b (Sakai, measured off the
author's scaled redrawings), 1c (the surviving rows, about lines 83-106), 3 (short detached houses), the China section,
and "Reading" (about lines 243-267). `grep -n '^#' <file>` gives the line of each. Its passages are LEADS: read each on
the archived copy or the URL yourself before quoting it. Existing keys the finding uses: `kaibara-jinya-tamba`,
`omori-daikansho-kunishitei`, `shibata-ashigaru-nagaya`, `kanra-ashigaru-nagaya`, `sakai-bugyosho-kachu-nagaya-takaya`,
`sayama-jinya-uematsu`, `hikone-ashigaru`, `touken-world-edo-housing`. NEW keys, in the order worth reserving (stop when
the finding is carried; at most six):
1. https://ja.wikipedia.org/wiki/御城番屋敷 (Matsusaka's castle-guard rows, 90.9 m and 83.6 m: the one quoted length past
   145 ft that does not rest on a measurement of ours);
2. https://www.pref.kagoshima.jp/ba08/documents/101223_20221118114551-1.pdf (Tarumizu, 15 by 3 ken, a guardroom);
3. https://en.wikipedia.org/wiki/Former_Yamauchi_Residence (33.4 by 5.7 m, 1864);
4. https://www.city.hikone.lg.jp/material/files/group/4/43_takigai.pdf (a detached foot soldier's house, only if you
   write the short-house contrast and `hikone-ashigaru` does not carry it);
5. and 6. https://www.mlit.go.jp/tagengo-db/H30-00660.html and `.../H30-00661.html` (Kaga's detached houses, 66-82 sq m:
   only if used).
The Chinese gazetteer chapter https://zh.wikisource.org/wiki/欽定古今圖書集成/方輿彙編/職方典/第1501卷 appears in this pass
and in two sister passes: use it only if you write the China sentence, and BEFORE any reserve run
`make archive-find URL=<it>` and grep the registry for `第1501卷` (percent-decoded) - a sister session may have reserved
it; then reuse its key. Its sister chapters are `gujin-xie-yamen` (1472), `gujin-tushu-jicheng-juan338-zhwikisource`
and `gujin-tushu-nanyang-wikisource`.

**Sizes at the start** (prose bytes of room under 20,000): 0097 research 3,709; drawing 10,426. The research finding may
not fit in 3,709: if `make question-sizes` lists the page, SPLIT it along its topics (a section moved whole to a new
question, `make reserve KIND=question`, a `<a class="moved" href="NNNN-<slug>.html">` pointer left where it stood, as
feature 451 T184 did) - never trim, and never drop a measured figure.

**Not yours.** The pop-up `sheet/retainers--quarters` states "about 80 to 145 ft long": it is the coordinator's to
restate after this lands. Another session (the servants' brief) will add one pointer to this question's "How big were a
lord's common rooms" finding after your pair is committed: leave that finding as it is. Existing tags on the drawing
page (`big-dwelling-junior-retainers`, `long-barracks`, `many-bays-does-common` and the rest) keep their `data-item`,
`data-label` and any `data-guess` exactly.

## Cascade expected (for the coordinator; not your work)

- 0097 research page (9 pop-ups, 2 claims). SHOULD re-check: `sheet/retainers--quarters` ("A rowhouse ran about 80 to
  145 ft long and 12 to 24 ft deep" - DRIFTED expected: the ceiling is no longer the record's), `sheet/barracks` ("The
  rowhouses measured ran about 80 to 145 ft" - DRIFTED expected), `sheet/servants--quarters` ("ran about 145 by 24 ft":
  that is Shibata's own size and should stay IN-STEP). SHOULD clear: `sheet/armory`, `sheet/door`, `sheet/gatehouse`,
  `sheet/granary`, `sheet/karo-s-house` ("a long, narrow, single-story building": true of a row still),
  `sheet/main-gate`; claims `docs/building-programs.md` `Magistrate's manor#staff housing knob` and `docs/buildings.md`
  (neither states a length).
- 0097 drawing page (4 pop-ups, 7 claims). SHOULD re-check: `sheet/retainers--quarters`, `sheet/barracks` (as above; and
  "long, narrow ... never squat" if they echo it), the claim `docs/buildings.md` `Outer court#barracks` (if it gives the
  barracks' limits). SHOULD clear: `sheet/door`, `sheet/servants--quarters`; `audit/program_rules.rs`
  `COMMON_ROOM_KIND`, `HIERARCHY`, `ROW_KINDS`, `lodging_entrances` x2; `compound/emit.rs` `building#dwelling walls
  across the long side` (none states a length).

## Your items

- **R1 `0097` research page: how long a staff rowhouse ran** (`research/questions/0097-staff-rowhouses-and-barracks-nagaya.html`; its notes `.notes.html`).
  The finding "How big was a staff rowhouse?" opens "On these measurements, 12 to 24 ft deep and 80 to 145 ft long, ..."
  and the page's opening paragraph says "Five rowhouses of warriors and officials survive or are measured: ...". The
  pass found the range is not the record's range. Restate the finding (and the opening paragraph's count, if you add
  buildings) so the page says, each part cited from a page you read:
  - What the 80 and 145 ft rest on: the floor is Kaibara's GATE range (about 81 ft) and Omori's gate ranges (about
    108 ft) sit between; Shibata's foot soldiers' row (about 143 ft) is the one DWELLING row of the three.
  - Rows LONGER than 145 ft are recorded twice: Matsusaka's castle-guard rows, 90.9 m and 83.6 m along the ridge
    (about 298 and 274 ft), ten and nine dwellings, built about 1863 (quoted figures, new key 1); and the Sakai town
    magistracy's doshin rows on the plans of 1711-1729, fifteen or sixteen dwellings at a QUOTED 3 ken each, so 45 to
    48 ken, about 270 to 290 ft - the count of dwellings is THIS PROJECT'S, taken off the author's scaled redrawing: say
    so in those words, and give the arithmetic in an HTML comment.
  - Rows of 15 to 17.5 ken (about 90 to 105 ft): Tarumizu, 15 by 3 ken, 1611, a samurai guardroom not dwellings;
    the Yamauchi residence's row, 33.4 by 5.7 m, 1864.
  - No MEASURED rowhouse under about 60 ft was found at an office. The nearest: Sakai's two-dwelling block for retainers
    of higher standing, about 70 by 45 ft on the scale bar (this project's measurement; squat, about 1.5 to 1); and at
    Sayama the rows are SAID to hold four dwellings, the author allowing that they held two - on that reading a foot
    samurai's row is 8 by 2.5 ken, about 48 by 15 ft, an inference of the author's from shared wells, not a measured
    building. Label each for what it is. What IS recorded short is the detached one-household house of a foot soldiers'
    quarter (Hikone, 4.5 by 5 ken), which is not a row and not at an office: one sentence, or leave it out.
  - China, if it fits: the gazetteers count clerks' and runners' rooms in bays and give no bay's width, so no length.
    One sentence at most, or an HTML session note.
  The depth (12 to 24 ft) and the bay (12 to 18 ft) stand: do not change them, nor the Shibata and Obata figures.
- **R2 `0097` drawing page: the 145 ft ceiling, "never squat", and the 48 ft row** (`research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html`; its notes `.drawing.notes.html`).
  - The block "The barracks is a long, narrow building, never a square or squat block." says: "It is drawn 12 to 24 ft
    deep, built of bays about 12 to 18 ft wide, and up to about 145 ft long. That form and those limits are accurate:
    every rowhouse measured is long and narrow, from ... Omori, about 108 by 13 ft, to ... Shibata, about 143 by 24 ft".
    Restate it truthfully: what OUR MAPS draw stays (long and narrow, up to about 145 ft); "those limits are accurate" does
    not - the 145 ft is the longest row this project's plans draw, the size of Shibata's, not the record's ceiling (rows
    of about 270 to 300 ft are recorded, R1), and one measured block at an office is squat (Sakai's, for retainers of
    higher standing). Say which part is accurate (the form: every DWELLING row measured for foot soldiers and junior
    officials is long and narrow) and label the ceiling for what it is - this project's choice for a county office, a
    deliberate limit; give it its own `<li>` and tag if it is a guess or a deviation by the record's labels:
    `data-item="barracks-length-ceiling"`.
  - The block "How big is a dwelling of the junior retainers' quarters?" says "12 by 24 ft on the county plan, four
    dwellings in a row of 48 ft: ... That size is a GUESS." (tag `big-dwelling-junior-retainers`: keep). Make the words
    say that the ROW's length, 48 ft, is a GUESS too: no measured row under about 60 ft was found at an office, and the
    one reading that gives 48 ft (Sayama, two dwellings of 4 ken) is an author's inference. A sentence in that block, or
    a NEW `<li>` with tag `data-item="row-of-48-ft"`, `data-label="GUESS"` and a `data-guess` saying so - your judgment
    which reads better; the existing tag is not changed either way.
  - "How long is the barracks drawn?" (tag `long-barracks`) stands.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p7-rowhouse-write.md`: `- SECTION=0097`
   (plus any split page), one line per item `R<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
