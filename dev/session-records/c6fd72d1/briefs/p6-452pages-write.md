# Brief - feature 452 T016 and T012 (0093, 0101, 0220), session 1: write (the gatehouse's two seats, the privy's size narrowed to a samurai house, and a source-applicability reply's three EDITs)

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
read by line range; send the lookups you know you need in one message. Touch no question but the three named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0093, 0101 and 0220 for feature 452 before starting you; if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass is needed for this brief**: two restatements to what the plans do and the record already holds, and
three EDITs a source-applicability check wrote. No new registry key is expected.

**The saved check reply** (item G3) is
`/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/reply-452-t012-source-applicability-0220.md`: a source-applicability reply
of 2026-11-24 on the registry entry `jawiki-yashikigami`, ending in three `EDIT` blocks - two on the entry's fragment
under `research/sources/010-works-cited/` (its file is named for the key), one on the shrine-gateway question's drawing
page. Each block's old text is in the tree today.

**Sizes at the start** (prose bytes of room under 20,000): 0093 drawing 10,097; 0101 drawing 11,679; 0220 drawing 7,218
(its RESEARCH page has 915: write nothing on it).

**Cross-references, read only**: the farm-privy question 0047 (its drawing page opens "Our maps draw a privy on most
farmsteads ... at one of the sizes one village's count of 1885 gives"; the count runs from 5 ft square upward); 0093's
own research page (the finding "Did a gatehouse of its own stand beside the gate or behind it?", note `kitain-bansho`).

## Cascade expected (for the coordinator; not your work)

- 0093 drawing page (4 pop-ups, 7 claims). SHOULD re-check: `sheet/gatehouse` (it says "beside" three times and never
  "behind": DRIFTED or a GAPS finding expected - the coordinator's to restate), `sheet/main-gate` ("a gatekeepers' house
  beside it or a guardroom in the range ... each plan taking one"), the claim `docs/buildings.md`
  `Walls and gates#gatehouse`. SHOULD clear: `sheet/armory`, `sheet/side-gate`; `docs/building-programs.md`
  `Magistrate's manor#garrison emphasis knob`, `#walled enclosure`; `docs/buildings.md` `Scale#yakuimon pillar`,
  `Walls and gates#main gate forms`; `audit/shared.rs` `gate_widths` x2. (The two claims in `compound/layout.rs` on the
  gatehouse's seats cite 0093's RESEARCH page, which does not change: not owed. The claim "behind the gate - GUESS" there
  can afterward cite the new item `gatehouse-behind-setback`.)
- 0101 drawing page (3 pop-ups, 30 claims). SHOULD re-check: `sheet/latrine` (it already says "no source gives a samurai
  house's privy's size, so it takes the smallest farm privy counted": IN-STEP expected) and the three claims that state
  the size - `compound/fixtures.rs` `PRIVY#privy size`, `docs/buildings.md` `Latrines and the rear service strip#privy
  size`, `docs/building-programs.md` `Magistrate's manor#privy size 5 ft square`. SHOULD clear: `sheet/inner-court`,
  `sheet/side-gate` and the other 27 claims (the privies' count, places, hatch, gray).
- 0220 drawing page (4 pop-ups, 10 claims). One sentence added to the block "A compound shrine may have no arch at
  all." SHOULD re-check: `sheet/compound-shrine`, `sheet/torii`; claim `docs/buildings.md`
  `Sacred features#compound shrine arch`. SHOULD clear: `hamlet/household-shrine`, `sheet/approach`; the arch-count and
  arch-pitch claims (`audit/shared/grounds.rs` x4, `docs/building-programs.md` `Country shrine` x4,
  `docs/buildings.md` `Sacred features#arch in plan`).
- The registry entry `jawiki-yashikigami`: the source-applicability check is re-owed on it (the check brief runs it).
  Five pop-ups name the key (`hamlet/household-shrine`, `sheet/compound-shrine`, `sheet/sacred-tree`,
  `sheet/torii`, `sheet/wood-kami-altar`): if an entry's edit reaches them, all SHOULD clear - the edit adds limits and
  changes no fact they state.

## Your items

- **G1 `0093` drawing page: a gatehouse of its own stands beside the gate or behind it, a knob** (`research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html`; its notes `.drawing.notes.html`).
  The block "Where the gatekeepers sit follows the gate's form, the knob chosen for each plan." says "a one-bay gate has
  a gatekeepers' house of its own beside it, a building apart, as the Takayama jin'ya lists its gatekeepers' house apart
  from its gate". The plans roll TWO seats for that house, each plan taking one: against the wall beside the gate, or
  inside, behind the gate - the two places this question's research page records for the one gatehouse that can be
  placed (the Kita-in guardroom: against the gate's side today, inside behind it on a plan of 1841, note
  `kitain-bansho`; a temple gate's guardroom, and the page says so). Restate the block to the knob, citing that finding
  (a link to the research page in the record's way, and the note if this page's notes file needs its own copy - quote
  the passage verbatim from the archived page). Then a NEW `<li>`: how far behind the gate the house stands is a GUESS -
  the plan of 1841 gives no distance; the plans set it back past the clear ground kept before the gate, to one side of
  the way in, so the way from the gate runs past its end. Tag:
  `<span class="item" data-item="gatehouse-behind-setback" data-label="GUESS" data-guess="How far behind the gate a gatehouse of its own stands: the plan of 1841 draws the Kita-in guardroom inside, behind the gate, and gives no distance."></span>`.
  The block's last sentences (no plan draws a gatehouse beside a gate RANGE; note `gatehouse-beside-range-absence`) stand.
- **G2 `0101` drawing page: the 5 ft square privy is a samurai house's, taken from the smallest farm privy** (`research/questions/0101-privies-setchin.drawing.html`; its notes `.drawing.notes.html`).
  The block reads "**A privy is drawn 5 ft square, a one-seat privy - a GUESS.** No source we read gives a privy's size;
  this is this project's choice." (tag `privy-5-ft-square`, GUESS, no `data-guess`: keep the tag exactly). "No source we
  read gives a privy's size" is untrue of the record as a whole: the farm-privy question (0047, bare number, read only)
  holds one village's count of 1885, whose smallest privy is 5 ft square. Narrow the sentence: no source read gives the
  size of a SAMURAI HOUSE's or an office's privy; the plans take the smallest farm privy counted, 5 ft square, and that
  carry-over from a farm to a samurai house is the GUESS. Link the farm-privy question's page in the record's way; cite
  the count through that page's finding (or its note's key, quoted verbatim, if this page's notes need a copy). The lead
  stays a GUESS and keeps the word.
- **G3 `0220` drawing page and one registry entry: apply the saved source-applicability reply** (`research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html`; the registry fragment for `jawiki-yashikigami`).
  The reply's author read the Japanese article through a summarizing fetch and says so. Before applying anything, read
  the archived page yourself (`make archive-find KEY=jawiki-yashikigami`) and confirm the three sentences the reply
  quotes are there as quoted: 「屋敷神の多くは石造か木造の小祠である。」, 「普通の神社のような社殿を持つことはまずない。」 and
  「丁寧に祭祀されている場合は末社程度の規模の社殿を建てられ、鳥居までも持つこともある。」 - and that "stone or wood" is
  said of the small shrine only. If they are, `make apply-edits FROM=<the reply's path, above>` (three EDITs: the
  entry's `What it is` gains the hall of a carefully kept shrine and the limit that the materials describe only the small
  hokora; the entry gains the limit that the article names no shrine in a samurai residence or an office; the drawing
  page's block "A compound shrine may have no arch at all." gains "The page is about household shrines; an office's
  shrine follows it by analogy."). If a sentence is NOT there as quoted, apply nothing that rests on it, fix the quote
  from the page, and report G3 `NARROWED` with the difference. Also add to the entry's `Used for:` line the use the reply
  names as unlisted (on this question: a carefully kept household shrine gets a hall and may have a torii), in that
  line's form. Do not touch 0220's research page.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p6-452pages-write.md`: `- SECTION=0093 0101 0220`
   (plus any split page), one line per item `G<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
