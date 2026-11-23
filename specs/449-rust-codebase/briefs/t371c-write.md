# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0113, 0099, 0059), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message. Do not touch 0104, 0123, 0090, 0009, 0097, 0096, 0103 or 0107 (the other briefs').

**Claims.** The orchestrator claimed 0113, 0099 and 0059 (with the bundle's other questions) for this clone (feature
449); `make research-claims Q="0113 0099 0059"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). Look in the archive before the web (`make archive-find`, `make research-search`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page or
its archived copy, never from a pass's report; a reading of a plan's image you check against the image as the report
did. Each new source takes its registry key (`make reserve KIND=registry KEY=<k> TAGS="..."`, at most ten new keys this
session). A defect is a wrong outcome: restate a record line to what its sources and the sheets say rather than invent.
Where the record is silent, the line says it is this project's GUESS, with an absence note listing what was searched
(and when). A figure measured on our own maps carries its date and method in the page's HTML comment.

**The two passes these items record** (research-pass, 2026-11-23; full reports with each source's URL, archived copy,
verbatim passage and translation - read them first, by line):
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t381-study-seat.md` (KEY t381-study-seat) - ATTESTED: on
  the Edo North Town Magistracy's plan of 1841 and the South's of 1842 (edo.ashigaru.net ?eid=23, ?eid=21, ?eid=20 and the
  full-size plan images; the record already cites `edo-ashigaru-bugyosho`, `edo-ashigaru-minami-plan`) the magistrate's
  own working room (用部屋, yobeya) stands at the join of office and residence - the household's inner entrance (内玄関)
  one corridor north of it at North, adjoining it at South, the court-side rooms beyond it; at Takayama the official
  viewing guide (`takayama-jinya-viewing-guide`) and site say the intendant ordinarily worked in a living room (居間) inside
  the residence, entered by the naka-no-kuchi, not in the office hall. The plans' labels are a modern blogger's
  transcription onto the NDL's drawings: say so where you cite them.
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t382-koshikake.md` (KEY t382-koshikake) - ATTESTED ONLY FOR
  the shogunate's Edo courts (the North and South town magistracies, the Hyojosho): a waiting shed for summoned parties,
  the koshikake (腰掛, 公事人腰掛), from at least 1694; before the gate (Heibonsha, 94 tsubo for the South's) or within the
  grounds or before the gate (Wikipedia); an inner and an outer one at the Hyojosho after 1769; on the plans, South 1842 a
  large shed outside the front line at its north-east corner, North 1841 a 腰掛 bay in the front range beside the main gate,
  and both a 公事人溜 inside on the approach to and along the court, and a separate 非人腰掛; the parties lodged at
  licensed inns (公事宿) and came when summoned. SILENT for an intendant's office (jin'ya): Takayama names no waiting place;
  the one jin'ya-side institution found is the 郷宿, the inn at an intendant's seat. China: no waiting shed; the 班房 a
  runners' room also used to hold parties under guard.

**What the plans draw** (measured 2026-11-23 by the orchestrator, method: each sheet's SVG room rects by `data-kind` and
their x, at 3 px to the foot; you may re-read `pool/magistracies/<map>/<map>.svg` read-only): the office hall's back row,
west to east - the county example (`county-magistracy-example`) and Ochiba (`ochiba-magistracy`): the armory, the writing
rooms (the writing and binding rooms), the clerks' room, the day office, the official study; Hayakawa (`hayakawa-magistracy`)
and the Ochiba round-trip test plan (`ochiba-roundtrip-test`), mirrored by 449 T367: the official study, the day office,
the clerks' room, the writing rooms, the armory; Ubame (`ubame-magistracy`): the writing rooms, the clerks' room, the day
office, the official study, with no armory in the hall (its armory a building of its own, 40 x 36 px). On the round-trip
test plan the study stands at the hall's west end about 90 ft from the household's door on the east face, so the
magistrate's way from the house to it runs over his own dais or through the back rooms (building-review 2026-11-23 of
ochiba-roundtrip-test, Q1, method: the review's reading of the regenerated svg at 3 px a ft). The county example leaves
open ground of about 117 x 21 ft before its hearing court (building-review 2026-11-23 of county-magistracy-example, O1).

## Your items

- **C1 (T373, T381) `0113`: the back row as each plan draws it, and the study's seat.** First the findings
  (`0113-the-office-hall-and-its-clerks-goyakusho.html`, near its account of the Edo plans' rooms or the day office): the
  magistrate's working room at the join of office and residence on both Edo plans, the inner entrance one corridor away or
  adjoining; Takayama's intendant working in his residence's living room, not the office hall - cited. Then the drawing
  page (`.drawing.html`): line 11's bullet "Along the office hall's back row our plans draw, from west to east, the armory,
  the writing room, the binding room, the clerks' room, the day office and the official study" is true of two plans only;
  restate it to the three orders above (keep the writing and binding rooms' seats a GUESS with its absence note and its
  cited Takayama and Iijima sentences). Its closing clause "the official study's seat at the back row's east end, east of
  the day office, ... a GUESS on the record's silence" is no longer silent: restate the study's seat as the record now
  bounds it - the record puts the working room at the household's join (Edo) or in the residence (Takayama); our plans seat
  the study at a back row's end, beside the day office, a GUESS that departs from the record where the study stands apart
  from the household's door, as on the round-trip test plan (the measurement above, dated). Do not invent where the
  household's door stands on the other plans: say only what is measured, or read each plan's door marks yourself
  (read-only) and give the date and method. Also line 9's bullet if it states the study's seat, the Grounds comment (line
  3) and the Evidence comment (line 4) to match. Keep 0113 and its drawing page under the cap.
- **C2 (T382) `0099`: the waiting shed.** Put the koshikake on 0099's findings (`0099-the-hearing-court-shirasu.html`), cited:
  attested at the shogunate's Edo courts as above, with where it stood and the inside waiting strip (公事人溜); the parties
  lodged at inns and came when summoned; nothing found for an intendant's office, an absence note naming the searches (KEY
  t382-koshikake, 2026-11-23); the China check in one sentence if it fits. Then the drawing page: a bullet saying our county
  magistracy draws no waiting shed and leaves the ground before its hearing court open, as drawn - the shed attested only at
  the shogunate's Edo courts, a city's, and the record silent for an intendant's office, which our county seat follows (0099
  line 5 says our maps draw a county magistrate's court, not the Edo town magistrates'), so the open ground is a GUESS on
  that silence. Whether the Edo finding applies to a county seat is the record's to rule: rule it here, in one sentence,
  with the reason. Keep 0099 under the cap.
- **C3 (T385) `0059`: under the 20,000-byte cap.** `research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html`
  is 20,065 bytes of prose (measured 2026-11-23, `make question-sizes`; the cap counts the question file alone, a money mark
  counted as its words; notes are not counted). Bring it to 19,800 bytes or below by cutting words, not findings: tighten
  repeated phrasing, cut a sentence that restates another. Do not drop a finding, a footnote, a figure, a label (GUESS,
  convention) or the why of a rule; if no such cut reaches the target, split along a topic instead (a part its own question
  with its own heading, `make reserve KIND=question`, the joins pointing, not restating). Say in the handoff what you cut,
  and the bytes before and after.

## The procedure (session 1: write)

1. **Write.** Read the two reports and the line ranges you need, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (0059 must not be listed, nor 0113 or 0099).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371c-handoff.md`: `- SECTION=0113 0099 0059`, one line per item
   `C1|C2|C3 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, the registry keys
   you reserved, the searches you ran, and anything left open and why. Do NOT run the record checks - the next session
   does, fresh. Your last message is one paragraph saying what you wrote.
