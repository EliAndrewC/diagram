# Brief - feature 452 T002 (0099), session 1: write (the hearing court: what enclosed it, who could watch a hearing, and what faced it, from a research pass)

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

**Claims.** The orchestrating session claimed 0099 for feature 452 before starting you (this clone holds it for 449; the claim sheet names both); if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects four or five, ranked below. A page over the 20,000-byte prose cap is
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
`/home/agent/.claude/jobs/c6fd72d1/tmp/passes/pass-452-t002-hearing-court.md` (58 KB - do NOT read it whole). Read
"Reading, by numbered point" (lines 209-222, four long paragraphs: what enclosed the court; whether a hearing was open to
view; what faced the court; measured examples), then only the source blocks you will cite: `grep -n '^\*\*[CJ][0-9]' <file>`
lists them (C1-C20 China, lines 15-148; J1-J9 Japan, lines 151-208), each with its URL, its archive id where it has one,
its date of evidence and the passage. Its passages are LEADS: read each on the archived copy or the URL yourself before
quoting it. Most of the finding stands on keys that ALREADY exist: `huc-journey-chinese-empire` (C2),
`gujin-tushu-nanyang-wikisource` (C5, chapter 451: Neixiang 1666 and Ye county), `gujin-tushu-jicheng-juan338-zhwikisource`
(C6: Jiexiu 1677, Pingyao), `gujin-xie-yamen` (C7, chapter 1472), `netease-pingyao-yamen` (C8),
`travelchinaguide-pingyao-yamen` (C9), `sohu-yamen-gate` (C10), `bjd-qing-yamen` (C11), `neixiang-yamen-baike-weixin`
(C12), `xianya-zhwiki` (C13), `qing-yamen-tushuo` (C17), `pingyao-yamen` (C19), `neixiang-yamen`, `sina-neixiang-xianya`,
`edo-ashigaru-kitamachi` (J3), `takayama-jinya-viewing-guide` (J4), `shirasu-imidas` (J5), `waraku-nagasaki-bugyosho`
(J8), `kazusa-bugyosho` (J9). NEW keys, ranked - reserve in this order and stop when the finding is carried; the cap is
TEN and you should need four or five:
1. Wang Huizu, Xuezhi yishuo (C1; https://zh.wikisource.org/wiki/學治臆說, or the daizhige copy the pass read): hearings
   in the great hall watched by hundreds - the one premodern Chinese text on whether a hearing was seen;
2. Tani Masayuki 2008 (J1; https://matsuyama-u-r.repo.nii.ac.jp/record/1473/files/KJ00006186679.pdf): shirasu hearings
   not public;
3. Staunton 1797 (C14; https://archive.org/stream/authenticaccount01stau/authenticaccount01stau_djvu.txt): the hall "at
   the end of a paved court, surrounded by galleries";
4. the Edo north magistracy's plan of 1841 itself (J7; the image linked from edo.ashigaru.net) - first see whether it
   belongs on the citation line of `edo-ashigaru-kitamachi` as a second URL (the record's rule for a page image) and
   needs no key;
5. the gazetteer chapter https://zh.wikisource.org/wiki/欽定古今圖書集成/方輿彙編/職方典/第1501卷 (C7, Wuding) - only if
   you cite it; BEFORE any reserve run `make archive-find URL=<it>` and grep the registry for `第1501卷`
   (percent-decoded): a sister session may have reserved it - then reuse its key;
6. to 9., only if a sentence needs them: the Toyo Bunko album caption (C15), the consular report of 1874 (C16), the
   Chinese Repository vol. 4 (C20), the 2023 Neixiang page (C18; the two existing Neixiang keys may carry it).
NOT cited: the blog at note.com/tak744 (J2: unsourced, and contradicted by the plans in the record).

**Sizes at the start** (prose bytes of room under 20,000): 0099 research 5,829; drawing 11,568. If the new section will
not fit, SPLIT along the page's topics (a section moved whole to a new question, a `<a class="moved">` pointer where it
stood) - never trim.

**Not yours.** Whether the county example plan's three junior retainers' doors onto the court change is feature 452
T002's DRAWING step: write no instruction to change a plan, edit no `pool/` file. The existing tags on the drawing page
(`posts-along-open-side`, `mats-arranged`, `mats-sizes-about-6`, `dais-single-dark-block`, `seat-clerks-either-side`,
`seat-clerks-either-side-2`, `county-magistracy-waiting-shed`) keep their `data-item`, `data-label` and `data-guess`.
The findings already on the page (the waiting strip beside the gravel court at Edo; the runners' duty room) stand.

## Cascade expected (for the coordinator; not your work)

- 0099 research page (9 pop-ups, 2 claims). A NEW section; nothing existing is restated. SHOULD re-check:
  `sheet/hearing-court` (the court's own pop-up: a GAPS finding is likely - it does not say the court was enclosed),
  `sheet/outer-court` (it states how parties "crossed it to the office hall's hearing courts" and "In China a county
  office was laid out so by regulation"). SHOULD clear: `sheet/clerks--seats`, `sheet/day-office`, `sheet/genkan`,
  `sheet/kneeling-positions`, `sheet/magistrate-s-dais`, `sheet/office-hall`, `sheet/official-study` (they state the roof,
  the mats, the dais: unchanged); claims `docs/buildings.md` `Outer court#hearing mats` clears,
  `Outer court#hearing court` SHOULD re-check (IN-STEP expected unless it calls the court open to the yard).
- 0099 drawing page (7 pop-ups, 12 claims). The waiting-shed block gains what the finding means for a plan. SHOULD
  re-check: `sheet/hearing-court`, `sheet/outer-court`; claims `compound/emit.rs` `hearing#hearing court posts` and
  `docs/buildings.md` `Outer court#hearing court posts` (they rest on "the court's open side": does a court closed to the
  yard still have one - IN-STEP expected, the open side faces the hall's own yard). SHOULD clear: `sheet/clerks--seats`,
  `sheet/day-office`, `sheet/kneeling-positions`, `sheet/magistrate-s-dais`, `sheet/office-hall`; claims
  `emit.rs` `dais_axis#the mats keyed to the dais`, `hearing#hearing mats`, `zone_paint#sand hearing court`,
  `spec.rs` `FLOORS#sand hearing court`, `docs/building-programs.md` `Magistrate's manor` x4 (clerk positions, dais band
  x2, sand hearing court), `docs/buildings.md` `clerk positions at the dais`, `hearing mat size`.

## Your items

- **K1 `0099` research page: what enclosed a hearing court, who could watch, and what faced it** (`research/questions/0099-the-hearing-court-shirasu.html`; its notes `.notes.html`).
  The page says nothing of what bounded the court or what looked onto it. ADD one short section (an `<h3>` in the page's
  form with its opening line, and three or four bold-opened findings), placed after the waiting-shed section. What it
  says, each part cited from a page you read, each country said by name, premodern evidence told apart from a modern
  account of a rebuilt site:
  - The court was enclosed, in both countries. China: a county office's great-hall court was a courtyard of its own -
    the ceremonial gate on the south (its middle leaves normally shut, side doors for daily use), the six offices' ranges
    down the east and west, the hall on the north (Neixiang as recorded in 1666; Jiexiu 1677; Ye county; Pingyao's gate
    of 1619 as modern accounts give it). Japan: closed by the building and the compound - at Edo's north magistracy on
    the plan of 1841 the gravel court lies inside a block of the building, rooms on all four sides; at Takayama the civil
    court is an earth-floored room. No source read names a fence, a board wall or a palisade round a shirasu: say that as
    a silence (an absence note dated 2026-11-24, the pass's search terms in its comment), not as a finding that there
    was none.
  - Who could watch. China: a hearing in the great hall was seen - Wang Huizu (magistrate at Ningyuan, c.1786-90)
    writes of hundreds standing below the hall and sets it against the inner office, where only the parties were; Huc
    (c.1846) found a county court full of onlookers. Limits the same sources give: confidential cases went to the inner
    halls. Japan: not public (Tani 2008, on the shogunate's courts) - a modern legal historian: say so.
  - What faced the court. Offices and waiting rooms only: in China the six offices on both sides, with the runners',
    gatekeepers' and jailers' rooms on the court or by its gate (whether those rooms were slept in is NOT stated: say
    so); the clerks' lodgings, where a gazetteer places them, stood in a side line or behind the office ranges. In Japan
    hearing rooms and the parties' waiting strip. No source read puts a dwelling's door onto the court - a stated
    silence, with its absence note.
  Do not repeat what the gate, the yamen-layout and the entrance questions already hold (0096, 0163 and 0104 hold the
  ceremonial gate's place, the six offices' place and the Edo entrance): link to them in the record's way where the
  section leans on them.
- **K2 `0099` drawing page: what the finding means for a plan** (`research/questions/0099-the-hearing-court-shirasu.drawing.html`; its notes `.drawing.notes.html`).
  The block "Our county magistracy draws no waiting shed for the parties, and leaves the ground before its hearing court
  open." (tag `county-magistracy-waiting-shed`, GUESS: keep the block's existing sentences, its comment and its tag) says
  the open ground is a GUESS on a silence. Add a NEW `<li>` after it: a hearing court is drawn closed to the outer yard
  - bounded by the hall, by buildings or by a wall, entered through a gate or the building - and no lodging's door opens
  onto it; only offices and waiting places face it. Label it by what K1 found: the enclosure and the offices facing the
  court are accurate to the record in both countries; "no lodging's door" rests on a silence (no source puts one there),
  so that half is a GUESS and the word GUESS is in the block. Word it so the two blocks do not read as a
  contradiction: the block before it says the ground before the court is left OPEN, meaning unbuilt (no waiting shed
  stands on it); the new block says the court is CLOSED to the outer yard, meaning bounded. Say "unbuilt" or "bounded"
  where a reader could take one for the other, without changing the earlier block's lead. Tag:
  `<span class="item" data-item="court-closed-no-lodging-door" data-label="GUESS" data-guess="That no lodging's door opens onto the hearing court: every source read puts only offices and waiting rooms round a court, and none says a dwelling never opened onto one."></span>`.
  If the plans as drawn today do not yet follow this (the county example has junior retainers' doors on the court),
  say nothing about them: the page states the rule; the drawing step is another task's.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p8-court-write.md`: `- SECTION=0099`
   (plus any split page), one line per item `K<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
