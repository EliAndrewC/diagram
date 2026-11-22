# Brief - feature 449 tasks T262, T266, T270, T272, group G2 (the village shrine), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, Makefile, docs/ and Python deletions); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit `docs/building-programs.md`, any `Research:` claim, `dev/claims-index.json`, any `pool/` file,
or any pop-up but the three named below - the orchestrator does the claims. Do not run `make claims-*`. Leave the
armory pop-up and `docs/building-programs.md`'s manor rows alone (another builder's). Read narrowly: grep with `-o`
and a short context, `make notes Q=<NNNN> KEYS=<k,k>`, read by line range; send the lookups you know you need in one
message.

First: `make research-claim Q="0221 0222 0229" FEATURE=449` (release with `STATUS=done` at the end).

## Your items

No new registry key should be needed; if one is, `make reserve` it.

- G2.1 (T266) **0222's notes and drawing page** say what its corrected findings no longer do:
  (a) the absence note `inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai` in
  `research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.notes.html`
  (line 17) ends "No village hall three bays square of the Edo period was found.", where the findings page now speaks of
  a village shrine's WORSHIP hall (a Saitama hall, cited elsewhere on the page, contradicts the wider wording). Read the
  findings sentence that cites the note and restate the note to it. The same note says what "a town's pages on Himemiya
  Shrine in Saitama" and "the town's survey report" give - a claim from pages no note quotes (a check ruled it
  CLAIM-FROM-UNREAD). Look them up on the ledger (`make sources-consulted URL=<u>` or `make archive-find TERMS="Himemiya|姫宮"`):
  if the archive holds them, quote what they say verbatim or narrow to what was searched; if not, the note says only
  what was searched and when, without what the pages say.
  (b) `...0222-....drawing.html` calls the Ehime shrine "the one village sanctuary we found measured" (line 7) and "The
  one village sanctuary we found described" (line 8), and its Evidence comment (line 4) "the one village sanctuary
  read"; the findings page calls it a rural shrine. Reword each to the findings page's term.
  (c) `kuri-jawiki`: `make quote-verbatim Q=0221` reports the note DIFFERS (the Wikipedia sentence was reworded since: the
  page now has 「大規模な寺院では独立した建物であるが、一般の寺院では寺の事務を扱う寺務所と兼用されていることが多く、一般の民家によく似た建物も多い。」)
  on BOTH 0221's main notes (fn-9) and its drawing notes (fn-13), and a `kuri-jawiki` passage 「寺院の僧侶の居住する場所」
  is NOT-ON-PAGE on 0221's main page (fn-8). Restate each to the page's current text (archive first, then
  `make source-pages ... QUESTION=0221` for the live page if the archived copy is old), the English translation to
  match, and the sentence each supports if the meaning moved. `make quote-verbatim Q=0221` and `Q=0222` must then show
  no DIFFERS or NOT-ON-PAGE but reference-marker-only ones (`[only the page's reference markers differ]`, which the
  record leaves: its quotations never carry the page's [1] markers).
- G2.2 (T270, the record half) **0222 (`Q=0222`): the wood-kami altar's drawn size**: the Ubame magistracy sheet
  (`pool/magistracies/ubame-magistracy/ubame-magistracy.svg`, around line 579; read only, 3 px = 1 ft) draws the altar a
  16 px square (about 5 ft) in plain wood color `#C9A57A`, larger than life so it can be seen, where the record's one
  measured household shrine is about 16 in across. Record this on 0222's drawing page as a map drawing CONVENTION (its
  why, what it costs: the mark reads larger than a real altar), in a bullet that fits the page's own structure, with
  its Evidence comment updated. Then check `l7r/diagram/interactive/assets/modals/sheet/wood-kami-altar.md`'s Depiction
  says the same, and that it names the drawing page in its `Drawing:` line (it does today).
- G2.3 (T270, the pop-up half) **`sheet/approach.md`'s Guesses** lacks 0223's GUESS "No fence is drawn along the
  approach" (`research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.html` line 8). Add a
  Guesses bullet saying it, briefly, in the pop-up's voice, from that bullet's words (one fence attested before 1868,
  not enough to say how common).
- G2.4 (T272) **0222 (`Q=0222`): `sheet/sanctuary.md`'s Guesses** lacks 0222's drawing page GUESS on the stone plinth under a village
  sanctuary ("no page we read describes what a village sanctuary stood on"); its Depiction names the gray strip the
  plinth's front. Add a Guesses bullet for the plinth.
- G2.5 (T262) **0229's canon comment** (`research/questions/0229-village-temples-tera.html` line 8) quotes l7r.md's
  "each village district is established to have a single "country monk" on a plot of tax-free land" but not the next
  sentence, which the hall-and-dwelling pop-up rests on: "The monk may have a few acolytes to help farm the land, which
  they may do on a part-time basis on loan from larger families in the village." (`/host-l7r-repo/setting/l7r.md`,
  "What is a village" - verify the line with one grep; never edit `/host-l7r-repo`). Add the sentence to the comment's
  quotation; and, because a check reading the built page may not see a comment, add one short visible clause to the
  paragraph saying that the monk may have a few acolytes, lent part-time by the village's larger families, to help farm
  the land (the setting's canon, labeled as the paragraph labels it). Do not edit `sheet/hall-and-dwelling.md`.

The pop-ups follow `dev/modals.md` (read only its Guesses and Depiction rules). Do not run the modal checks; session 2
does.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="acolyte|country monk|tax-free"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k> | URL=<u> | TERMS="a|b"` for every
   source before any fetch. Every page read goes through `make source-pages OUT=/tmp/l7r-check/t254-g2-pages URL=<u>
   QUESTION=<NNNN> SOUGHT="<what>"`, and its outcome through `make source-outcome`.
3. **Read through `source-reader`** only where a NEW passage is to be cited: one dispatch, in the FOREGROUND, on a bundle
   (`make check-bundle ... NEW="<claim>"`). Write only what it returns READ with a quote.
4. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and the four labels by the
   record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
5. **Hand off.** Write `specs/449-rust-codebase/briefs/t254-g2-handoff.md`: one line per changed question as
   `- SECTION=<NNNN>`, one per changed registry key as `- KEY=<key>`, one per changed pop-up as `- MODAL=<kind>/<name>`,
   one line per item `G2.<n> <DONE|NARROWED|LEFT> - <what the record now says>`, every file you changed under
   `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.
