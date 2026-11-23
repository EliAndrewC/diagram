# Brief - feature 449 T333 and T330's 0116 pointer (0098, 0088, 0116, registry 37100), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your items need, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s
own archive step does what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any
`pool/` file, any `docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`. Read narrowly: grep with
`-o` and a short context, read by line range; send the lookups you know you need in one message.

**Claims first.** The orchestrator claimed 0098 and 0088 for this clone. 0116 is NOT claimed: run
`make research-claims Q=0116`; if no session holds it, `make research-claim Q=0116 FEATURE=449` and do B5; if another
session holds it, leave B5 and report it `LEFT - 0116 held by <holder>`. Do not touch
`0116-...drawing.html` (another builder's edit is in it); B5 is in the two notes files only.

## Your items

- **B1 `0098` takayama-onkura-heritage (UNFETCHABLE).** The live page
  (`https://japan-heritage.bunka.go.jp/ja/culturalproperties/result/2060/`) still serves the Japan Heritage portal's
  maintenance notice (measured 2026-11-22). The archive holds a copy: `make archive-find
  URL='https://japan-heritage.bunka.go.jp/ja/culturalproperties/result/2060/'` names it. Read the copy and check each of
  the four quoted originals of the note (`takayama-onkura-heritage#1`-`#4` in the originals files) against it, verbatim.
  Where the copy carries a passage, the citation stands (say nothing about the maintenance notice on the page). Where it
  lacks one, find the passage on another readable page already cited for the same fact, or drop the passage, and put
  the page on the GM's list with `make download-add FILE=<draft>` (an entry headed `### NEW. <the work>`; read the top
  of `research/to-download.md` by line for the shape). Record the outcome with `make source-outcome`.
- **B2 `0098` note `how-our-maps-draw-storehouses-for-the-tax-rice-2` (UNLINKED-NAME).** It names the Kawashiri database
  page and the Asakusa pages without links. Link each to the page it means (its registry key's note, or its URL, as the
  page's other notes do) - find them by `make archive-find TERMS=...` and `make sources-consulted URL=<u>`; where a
  named page cannot be identified, say only what the search found.
- **B3 `0088` note `yamaguchi-hagi-road-maps`, passage #4.** (a) It romanizes 御国廻御行程記 as "Okunimawari
  Gokoteiki" without the archive's own reading (translation-check CANNOT-TELL). Look for the page's own furigana or
  reading (the archived copy: `make archive-find KEY=yamaguchi-hagi-road-maps`), and the prefectural archives' own
  catalog reading if one is archived; if none gives a reading, drop the romanization or mark it as the record's own
  reading, never a source's. (b) source-reader and quote-check disagreed whether its 横線 runs ACROSS the road. Restate
  the note's and the page's words to what the passage literally says, and the registry entry 37100's `Used for` line
  ("the one mark found across one") to match.
  - **B4 (0088's citation) registry `37100` yamaguchi-hagi-road-maps (long-vowel marks).** It keeps macrons (Bōchō, Sanyōdō) where the
    record's style drops them (Bocho, Sanyodo) - in the registry's own prose, not inside a quoted original. Grep the 0088
    files for the same macrons in prose and fix those too.
- **B5 `0116` notes, note `takayama-jinya-jawiki-6`** (record-format OUTSIDE THE CHANGE, twice): its
  "(as in the courtroom section)" is a pointer a reader cannot follow. Make it a link to the section it means (find the
  section by its heading; the notes' other links show the form) or, if it points nowhere a reader can reach, move it to
  an HTML comment. Both notes files where the note appears.

- **B6 `0113` findings: where the writing room is attested** (the sheet bundle, 2026-11-22). Wherever 0113 (findings,
  notes, drawing page) says the writing room is attested "only at Takayama", restate it to what the record holds: at
  Takayama, and at Iijima's rebuilt jin'ya (a 1993 reconstruction, cited by the record as `iijima-jinya-kakiyaku-beya`
  and `fun-old-japan-iijima`, which counts toward no verdict on the period). Read the current text first: brief A's
  session wrote 0113 today and may already say so; change only what still says "only at Takayama". 0113 is claimed by
  brief A's sessions until its check session releases it: run `make research-claim Q=0113 FEATURE=449` (it is this
  clone's own claim; if another session holds it, leave B6 and B7 and report it).
  - **B7 (0113's drawing page) the clerks' room "behind the dais band".** The drawing page says where the plans draw
    the clerks' room; it should say the plans draw it behind the dais band, and label that from the research pass at
    `.git/l7r-handoffs/T337-pass-behind-the-dais.md` (read it whole; 34 lines): ATTESTED ONLY FOR the Edo town
    magistracies (their 1841 and 1842 plans put the 調之間, by its name an examiners' working room - the pass's
    inference, no source states its use - directly behind the 裁許所 where the magistrate sat); SILENT for an
    intendant's jin'ya (Takayama's 1851 plan unreadable); in China the second hall stood behind the great hall. So the
    clerks' room behind the dais is a GUESS for a county office, bounded by the Edo case. The plan images are readings
    of a drawing, not passages: cite the archived edo.ashigaru pages (archive 66/6644a5eca0a2, already keyed
    `edo-ashigaru-*`) for their text and say "the plan shows" for the room order.
- **B8 `0088` comment on the road's drawing.** A session comment on 0088 (its drawing page or notes) still describes
  the road as dashed or banded; the sheets now draw the road in one flat earth tone (449 T328). Restate the comment to
  the flat tone (grep the 0088 files for `dash` and `band`; change only comments and text describing the current
  drawing, never a quoted passage).

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t330b-handoff.md`: `- SECTION=0098 0088 0116 0113` (drop 0116 or 0113 if you
   left its items), one line per item `B1|...|B8 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed
   under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.
