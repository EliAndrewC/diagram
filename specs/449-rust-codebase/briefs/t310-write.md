# Brief - feature 449 bundle T302 (the record's leftover findings), session 3: write (0091, 0113, 0123, 0093)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0091 0113 0123 0093" FEATURE=449` (release with `STATUS=done` at the end).

## What a research pass found (2026-11-22) - for T311

A 箭道 in a Qing official's compound was a straight archery strip. Read each passage yourself before citing it (archive first:
`make archive-find`; the pass saved its pages under `/tmp/l7r-pass/`):

- **The same Jiexiu entry** (古今圖書集成 職方典 卷338, the registry's `gujin-tushu-jicheng-juan338-zhwikisource`, archived
  `5a/5a06a30df294`): 「東西角門，門內西為把門、皂隸、禁卒房。東為武庫，為獄箭道，在協亭西。知縣王填建箭廳，匾曰「觀德。」」 ("East and
  west side gates. Inside them, on the west, the rooms of the gate-keepers, the yamen runners and the jailers. On the east the armory,
  the jail and the archery strip, west of the 協亭. Magistrate Wang Tian built an archery hall and named its board 'Observing
  Virtue'", translated). NOTE: the archived text reads 武庫, 把門、皂隸 and 協亭; check the record's present quotation and translation of
  this passage (note `gujin-tushu-jicheng-juan338-zhwikisource-3`, 0123's notes) against the archived text and correct any word that
  differs. The board's name is the Liji's archery phrase (禮記·射義 「此可以觀德行矣」).
- **河陽 county office** (same compendium, 卷1486, https://zh.wikisource.org/wiki/欽定古今圖書集成/方輿彙編/職方典/第1486卷; 1698):
  「署右建花廳三間，水亭一座，箭道一區。」 ("On the office's right he built a flower hall of three bays, a water pavilion, and an archery
  strip", translated).
- **zdic** (https://www.zdic.net/hans/箭道, a modern dictionary): 「旧时官府设立的射箭练习场地。」 ("formerly, an archery practice
  ground set up by a government office", translated).
- **北東園筆錄四編 卷2** (https://zh.wikisource.org/wiki/北東園筆錄四編/卷2; the Fogang sub-prefecture, set up 1813):
  「衙署甚寬敞，有東西兩箭道，為訓練考拔之所。」 ("its office was spacious, with east and west archery strips, places for training and
  for testing", translated).
- No county office's 箭道 has a stated size.

## Your items (four questions)

- **T311 - 0123** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html`
  and notes): the Jiexiu bullet and note `gujin-tushu-jicheng-juan338-zhwikisource-3` say "arrow lane" (箭道) with no definition.
  Name it the archery strip (箭道) and say in a clause what it was (a straight strip for practice archery inside the office's walls,
  with an archery hall beside it at Jiexiu), footnoted to the Jiexiu passage and one of the definitions above (register a new key with
  `make reserve` where you cite a new source); add a GLOSSARY entry for the term (`make reserve KIND=glossary`) so the pop-up tooltip
  reads it. Its size unsaid. Keep 0123 under its byte cap (`make question-sizes`).
- **T310 - 0113** (`research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html` L12 and `.drawing.html` L8, and both
  absence notes `the-office-hall-and-its-clerks-goyakusho` and `how-our-maps-draw-the-office-hall-and-its-clerks-goyakusho`): they say,
  unqualified, that no page gives an office hall's length and depth, while the genkan page cites the Sayama domain's council hall (評定所),
  梁行2間・桁行10.5間 (about 12 by 63 ft), built 1775 (read only: `make notes Q=<the genkan page> KEYS=sayama-jinya-uematsu-2` - the genkan page, question one-oh-four, not yours to edit). Name the Sayama hall - a small domain's
  jin'ya council hall, not an intendant's office - with its two dimensions, footnoted to the same source, and narrow the silence to an
  intendant's or a county office's hall. On the drawing page, say in a clause how the drawn 20-45 ft depth stands against Sayama's
  ~12 ft (deeper), without changing the band.
- **T305.8 - 0091** (`research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.notes.html` and `.drawing.notes.html`):
  the `kaminoyama-miwa-ke` and `adachi-matsue-bukeyashiki` notes join their passages with `) and 「` around framing glosses, not the
  record's `; `: rejoin them in the record's form (a gloss that carries meaning goes in the parenthetical after the passage). Also
  registry `research/sources/*/16370-jta-aoyagi-kakunodate.html`: its "Used for" omits 0091, which cites it: add it.
- **T308 - 0093** (`research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html`, and its Evidence comment): the
  bullet "The gatekeepers sit in a gatehouse beside the gate, or in a guardroom inside the gate range, a knob chosen for each plan"
  treats the place as a knob of its own, but a one-bay gate has no range to hold a guardroom, and no source puts a gatehouse of its own
  beside a gate range. Restate it: where the gatekeepers sit follows the gate's form, itself the knob - a guardroom inside a gate range
  (Kaibara's), a gatehouse of their own beside a one-bay gate (Takayama's gatekeepers' house, listed apart from its gate); a gatehouse
  beside a gate range is drawn by no plan, no source found showing one (a research pass, 2026-11-22: Kaibara, Omori's gate range - the
  gatekeepers' station, rebuilt 1815 - and the Joge post's drawing of 1869 all put the guardroom in or against the range; the one
  freestanding guardhouse found is Edo castle's). The Omori passage, if you add it, is archived `bd/bd904effa88a`
  (「瓦葺き平屋建ての表門とその左右に付随する門長屋建物が現存する」) and on https://ja.wikipedia.org/wiki/石見銀山資料館
  (「門番詰所や仮牢などに使用されていた門長屋（1815年再建）が現存」); cite only what you read. Restate the Evidence comment's "the two
  places the gatekeepers sat, each a knob between attested forms" to match. One or two sentences.

## The procedure (session 3: write)

1. **Canon once**: `make canon TERMS="archery|council hall|gatekeeper|gatehouse"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>`. Register each new source with its write-ups
   (`make reserve` for keys).
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and labels by the record's rules; no history in
   the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t310-handoff.md`: `- SECTION=0123`, `- SECTION=0113`, `- SECTION=0091`,
   `- SECTION=0093`, one line per item `<item> <DONE|NARROWED|LEFT> - <what the record now says>`, the new keys and notes, every file
   you changed under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.
