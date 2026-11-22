# Brief - feature 449 task T197, group G2 (the village shrine), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, Makefile, docs/ and Python deletions); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit `docs/building-programs.md`, any `Research:` claim, `dev/claims-index.json`, any pop-up under
`l7r/diagram/interactive/assets/modals/` or any `pool/` file - the orchestrator does the claims. Read narrowly: grep
with `-o` and a short context, `make notes Q=<NNNN> KEYS=<k,k>`, read by line range; send the lookups you know you need
in one message. The sheet these rows describe is `pool/country-shrines/hoshigaoka-shrine/` (its `.svg`, `.png` and
`.notes.md`; read the notes by grep, and the PNG to see the glyphs).

First: `make research-claim Q="0221 0222 0223" FEATURE=449` (they are unclaimed; release with `STATUS=done` at the end).

## Your items

Each is a correction T187's checks found: a citation that does not support its sentence, a sentence with no footnote,
or a thing the map draws that no drawing page records.

- G2.1 **0222's main page, `0222`** (`research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html`
  and its `.notes.html`):
  (a) "small temple halls of the Edo period that have been measured run from about 21 to 35 ft on a side" disagrees with
  the page's own figures - the Chikusei (Saishoji) side hall of about 13 ft a side and Ehime's of about 32 by 35 ft - and
  its 21 ft low end with the drawing page's 18 ft from Hie Shrine's hall. Restate the range from the page's own cited
  figures, each footnoted, so the main page and the drawing page agree (the drawing page draws the band 18 to 35 by 12 to
  35 ft; do not change the band).
  (b) "a subsidiary hall, not one where a village gathered" has no footnote: cite what says it, or narrow it, or label it.
  (c) in the notes, `chikusei-saishoji-yakushido`'s 「According to the ridge plaque, ...」 becomes "ridge tag", as the drawing
  page's notes have it (the same quotation; check both against the source with `make quote-verbatim Q=0222`).
- G2.2 **0223's drawing page, `0223`** (`research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.html`):
  the procedure's claim "no fence along the approach" (a GUESS) cites this page, but the page does not record the
  decision. 0223 attests Yasuda Hachiman's late-Edo stone fence lining its approach, the one fence from before 1868 found
  at an ordinary shrine. Record on the drawing page that our maps draw no fence along the approach, labeled - a GUESS
  that one attested example does not make a rule, or a knob under its own rule if the record makes it one - with the why.
- G2.3 **Two depiction rows, on drawing pages**, each recorded as found (cited) or as a map drawing convention (said so,
  with the real thing searched for and its absence noted):
  (a) how a shrine dwelling's kitchen is drawn - Hoshigaoka draws the kitchen end with a stippled floor and a hearth
  glyph: is it an earth floor (doma), and is the hearth a kamado or an irori? Record it on `0221`'s drawing page
  (`research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html`), the
  dwelling's page; research 0107 (kitchens) already holds that the kamado stood on the doma in Edo houses - search the
  record first (`grep` over `research/questions/0107-*`, `0221-*`).
  (b) the sanctuary's vermilion fill and the gray strip before it, as Hoshigaoka draws them: record on `0222`'s drawing
  page what each stands for and its label (a found finish, or a convention of the map).

## The procedure (session 1: research and write)

1. **Canon once** where an item is the setting's: `make canon TERMS="vermilion|sanctuary|shrine keeper"`.
2. **Search the record, then the archive, before the web** (feature 309): `make archive-inbox`, then `make archive-find
   KEY=<k> | URL=<u> | TERMS="a|b"` for every source before any fetch. Every page read goes through `make source-pages
   OUT=/tmp/l7r-check/t197-g2-pages URL=<u> QUESTION=<NNNN> SOUGHT="<what>"`, and its outcome through `make source-outcome`.
   A search that finds nothing is an outcome: an absence note with what was searched and when.
3. **Read through `source-reader`** only where a NEW passage is to be cited: one dispatch, in the FOREGROUND, on a bundle
   (`make check-bundle ... NEW="<claim>"`), never a path under `/diagram`. Write only what it returns READ with a quote.
   At most ten new registry keys (`make reserve` refuses the eleventh: then write the unreached items to `$L7R_CONTINUE`
   as a brief of this shape and stop).
4. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes, glossary and the four labels by
   the record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make
   record`, `make glossary` if a term was added, and `make question-sizes`.
5. **Hand off.** Write `specs/449-rust-codebase/briefs/t197-g2-handoff.md`: one line per changed question as
   `- SECTION=<NNNN>`, one per new or changed registry key as `- KEY=<key>`, one line per item `G2.<n> <DONE|NARROWED|LEFT>
   - <what the record now says>`, every file you changed under `## Files`, and anything left open and why. Do NOT run
   the record checks - the next session does, fresh. Your last message is one paragraph saying what you wrote.
