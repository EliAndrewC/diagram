# Brief - feature 452 T001 (0331, 0097), session 1: write (where an office's menservants lodged and how many there were, from a research pass; one pointer on 0097; a download-list entry)

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
read by line range; send the lookups you know you need in one message. Touch no question but the two named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0331 and 0097 for feature 452 before starting you (this clone holds both for 449; the claim sheet names both features); if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects two or three. A page over the 20,000-byte prose cap is
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
`/home/agent/.claude/jobs/c6fd72d1/tmp/passes/pass-452-t001-menservants.md` (36 KB - read by section). Read "Reading"
(lines 207-238: headcount, single or family, room size, the contrast with the junior officials' quarters), then only
the source blocks you will cite, found with `grep -n '^#\|^\*\*' <file>` (section (2), lines 101-153, and (3), lines
154-194, hold the rooms). Its passages are LEADS: read each on the archived copy or the URL yourself before quoting it.
Existing keys the finding uses: `fuchu-joge-pamphlet` and `fuchu-joge-jinya` (Joge's plan of 1869),
`sano-jinya-fukushige` (already cited on the page), `gujin-tushu-jicheng-juan338-zhwikisource` (Jiexiu 1677, Pingyao),
`pingyao-yamen`, `gujin-xie-yamen` (the Yunnan runners' rooms, chapter 1472), `kochi-hantei-jstage` (a domain's Kyoto
residence, 1795: a neighbor, not an office), `boso-jinya-chiba-kiyo`, `bushijyoshi-daikan-jinya`. NEW keys expected, two
or three: the Chaoxian gazetteer of the Daoguang reign, chapter 4 (https://zh.wikisource.org/wiki/道光巢縣志/卷04);
Nishizawa 1988 (https://hosei.ecats-library.jp/da/repository/00011026/shigaku_40_nishizawa.pdf: an intendant's clerical
staff of 12 to 20 in the 1830s) if you write the headcount sentence; and the gazetteer chapter
https://zh.wikisource.org/wiki/欽定古今圖書集成/方輿彙編/職方典/第1501卷 only if you cite it - BEFORE any reserve run
`make archive-find URL=<it>` and grep the registry for `第1501卷` (percent-decoded): the rowhouse or the hearing-court
session may have reserved it - then reuse its key.

**The book only the GM can fetch.** Ch'u T'ung-tsu, Local Government in China under the Ch'ing (1962), chapters IV
(Government Runners, pp. 56-73) and V (Personal Servants, pp. 74-92), is where numbers and lodging of a magistrate's
servants are likely given; the Project MUSE page shows a table of contents only. The book is ALREADY entry 141 of
`research/to-download.md`, asked there for another figure (a county's population) and unmarked. The list is append-only:
do not edit entry 141. Append a NEW entry with `make download-add FILE=<draft.md>` (the draft outside `research/`, e.g.
under `/tmp/`): headed `### NEW. Ch'u T'ung-tsu, Local Government in China under the Ch'ing (1962), chapters IV-V
(pp. 56-92)`, its link line (https://muse.jhu.edu/book/75612, or the publisher's page entry 141 gives), a `- Fallback:`
line, `- **Rests on it:**` naming `research/questions/0331-where-an-offices-staff-lived.html` and what is wanted (how
many runners and personal servants a county magistrate kept, and where they lodged), saying in words "the same book as
entry 141, a different part", and `- Blocked by:` (a book; the open page gives its contents only). Read
`research/downloads.md` for the draft's form if the target refuses it. Cite nothing from the book.

**Sizes at the start** (prose bytes of room under 20,000): 0331 research 13,029 (it has no drawing page); 0097 research
about 3,700 BEFORE the rowhouse session's edit - measure it (`make question-sizes`) before adding a byte.

**Order.** This session runs AFTER the rowhouse pair (feature 452 T003) is committed: that pair rewrote 0097's finding
"How big was a staff rowhouse?". You touch 0097 in ONE place only, item M2.

## Cascade expected (for the coordinator; not your work)

- 0331 research page (3 pop-ups, 1 claim). SHOULD re-check: `sheet/barracks` (it says who else of an office's staff
  lived on its grounds is not recorded, and that servants below the foot soldiers lived in large common rooms: a GAPS
  finding is possible - Joge's 3-mat manservants' room) and `sheet/retainers--quarters` (names the junior officials'
  quarters at an intendant's office: IN-STEP expected). SHOULD clear: `sheet/karo-s-house`; the claim
  `docs/building-programs.md` `Magistrate's manor (county magistracy)#staff housing knob` SHOULD re-check only if it
  says the record is silent on servants' rooms (else clear). Note for the coordinator: `sheet/servants--quarters` does
  NOT cite 0331 today; if the Joge room should reach that pop-up, that is a pop-up edit, not a cascade.
- 0097 research page (9 pop-ups, 2 claims), one pointer sentence in the "lord's common rooms" finding. SHOULD re-check:
  `sheet/servants--quarters` (its common-room form rests on that finding; IN-STEP expected: the finding still says no
  page gives a lord's common room's size). SHOULD clear: the other eight (`sheet/armory`, `barracks`, `door`,
  `gatehouse`, `granary`, `karo-s-house`, `main-gate`, `retainers--quarters`) and both claims.

## Your items

- **M1 `0331` research page: the menservants - no count tied to a room, one measured room, named rooms in China** (`research/questions/0331-where-an-offices-staff-lived.html`; its notes `.notes.html`).
  The finding "Did all the staff of a rural intendant's office live on its grounds?" says "No page we read counts who
  lived inside one, or says whether all its staff did.", and the Sano finding ends "and none but the keeper inside".
  Both stand. ADD two or three bold-opened findings (or one, if it reads better), each part cited from a page you read:
  - The one servants' room measured at an office: at Joge, a branch office of three officials in 1867, the plan of 1869
    (after the Edo period: say so) shows a manservants' room of 3 mats, and a maidservants' room of 3 mats, in the
    building's southern block, inside the compound.
  - China: a county office gave each group of menials a NAMED room by its gates or in its front ranges - Jiexiu as
    recorded in 1677; Pingyao (1709, 1791, 1827, as its gazetteers are reported); Chaoxian after 1827, with the lictors'
    room outside the main gate. No text read says whether such a room was a duty room or a lodging: state that silence;
    the modern Pingyao account's word "dwelling-place" is a modern account's and is said to be.
  - No source read ties a number of menservants to a room. Headcounts exist only as establishment quotas (China) and as
    whole-office totals that include menials (Japan): give at most the two or three figures you can quote (for example
    Joge's three officials; Nishizawa's 12 to 20 clerical staff in the 1830s; a Chinese quota from the gazetteer you
    read), and say plainly that none counts the menservants of an intendant's office. Whether a menial lodged with a
    family inside an office's compound: no source read says either way - a stated silence with an absence note dated
    2026-11-24, the pass's search terms (its section "What was searched", lines 239-257) in the note's comment.
  - Leave out the Kochi domain's Kyoto residence unless one sentence, labeled a domain residence and not an office,
    earns its place.
  Then the download entry for Ch'u T'ung-tsu, as above; name its new number in the handoff.
- **M2 `0097` research page: one pointer from the lord's common rooms to the Joge room** (`research/questions/0097-staff-rowhouses-and-barracks-nagaya.html`).
  The finding reads "**How big were a lord's common rooms, and how many men shared one?** No page we read says." (note
  `staff-rowhouses-and-barracks-nagaya-4`). It stays TRUE - Joge is an intendant's branch office, not a lord's seat - so
  do not restate it. Add one sentence after it pointing to the one servants' room the record does measure, at an office:
  3 mats at Joge, with a link to `0331-where-an-offices-staff-lived.html` in the record's way. If the page will not hold
  the sentence under the cap after the rowhouse session's edit, or the sentence would mislead (a 3-mat room is not a
  common room), leave the page untouched and report M2 `LEFT` with the reason. Touch nothing else on the page, and not
  its drawing page (the tag `many-bays-does-common` keeps its words).

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p9-servants-write.md`: `- SECTION=0331 0097`
   (plus any split page), one line per item `M<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
