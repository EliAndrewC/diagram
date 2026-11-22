# Brief - feature 449 task T274 (0123's drawing page: where the manor's own map seats the granary), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, and another page session's research pages); the orchestrating session
commits your files by name. Touch only the files your item needs, and list every file you changed in the handoff.
Never run `scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any
`pool/` file or any pop-up - the orchestrator does the claims. Do not run `make claims-*`. Read narrowly: grep with
`-o` and a short context, `make notes Q=0123 KEYS=<k,k>`, read by line range; send the lookups you know you need in
one message.

First: `make research-claim Q="0123" FEATURE=449` (0090 is read, not edited) (release with `STATUS=done` at the end).

## Your items

No new registry key should be needed: the Pingyao source is already cited on 0123's findings page as the note
`pingyao-yamen` (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html`, line 14), its original in
`0123-...originals.html`: 「在兵、刑、工房后修有公廨房，以北修县仓」 ("Office buildings were built behind the offices of
war, justice and works, and north of them the county granary", translated). Its archived text:
`make archive-find KEY=pingyao-yamen` (or the archive copy under `.specify/source-archive/42/429e9a2d5a67/`).

- T274.1 **0123's drawing page** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.html`).
  Today the page speaks only of the town map's walled box. Its bullet "A county seat draws no separate granary" (line
  11) presumes the granary inside the manor but never says where the MANOR'S OWN MAP (the Mode A compound sheet) draws
  it. The generator's rule, which the page must now state and label:
  - the granary stands in the office (outer) court, never the household's inner court, reached from the office side;
  - it stands at the head of one of the office court's flank columns, its north face on the court divider, beside the
    office hall's end (on the county example: the east wall, 217-267 by 92.5-119.5 ft, the hall 58.5-185.5 by
    92.5-130.5 ft, the divider at 90 ft), its door toward the hall's end;
  - why it is a GUESS: Pingyao seated its granary north of the office buildings that stood behind its war, justice
    and works offices - a seat relative to side-wing offices. Our manor plan has none: its offices are rooms of one
    office hall on the divider (0090's drawing page records the two-court simplification; read it, do not edit it -
    `research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html`, grep `two-court` or the bullet near
    its §9). So the sheet has no side-wing to be north of, and north of the hall is the household's court, which the
    rule refuses. The flank column's north end beside the hall is the office side's nearest ground to Pingyao's seat:
    our own reading, not a seat any source gives. Which flank (east or west) is the sheet's choice; the page names
    none, and 0123's source does not say the offices of war, justice and works stood west, so do not say west.
  Write ONE new bullet, after line 11 or as the opening of a short new group after line 13 with a one-sentence lead
  saying this part is about the manor's own map, not the town map (the page's intro is town-map-only; one clause in
  the intro may widen it). Label it GUESS by the record's four labels. Footnote the Pingyao half to a NEW note in
  `0123-...drawing.notes.html` (the next free `how-our-maps-draw-the-magistrates-manor-on-a-town-map-<n>` key, per the
  record's note-key rules) quoting the passage verbatim from the archived copy (original, then English marked as a
  translation; check with `make quote-verbatim`), and give the GUESS an absence note: what was searched and found -
  the Pingyao passage gives a seat relative to side-wing offices only; no page read places the granary of a seat
  whose offices are one hall (searched: the record's 0090, 0093, 0123 and the archive's Pingyao and Neixiang yamen
  pages, 2026-11-22, feature 449 T274). Add "the granary's seat on the manor's own map" to the line-4
  `<!-- Evidence: ... -->` comment's guess list. Keep findings to the footnote and note; a drawing page states the
  map's rule and its label.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="granary|yamen|magistrate"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>`. No new source should be
   needed.
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and the four labels by the
   record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no page over 20,000 bytes of prose).
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t274-handoff.md`: `- SECTION=0123`, one line
   `T274.1 <DONE|NARROWED|LEFT> - <what the record now says>`, the new note key and the new bullet's heading text
   verbatim, every file you changed under `## Files`, and anything left open and why. Do NOT run the record checks -
   the next session does, fresh. Your last message is one paragraph saying what you wrote.
