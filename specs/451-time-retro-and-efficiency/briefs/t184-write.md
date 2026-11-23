# Brief - feature 451 T184 (0009, 0059), session 1: write (restore the size trims, split each page)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 451's spec,
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
need in one message. Touch no question but 0009, 0059 and the two new questions you reserve.

**Claims.** The orchestrator claimed 0009 and 0059 for this clone (feature 451); claim your two new questions with
`make research-claim Q="<NNNN> <NNNN>" FEATURE=451` once reserved.

**Why this work.** On 2026-11-23 (commit cce80ca436) both pages were cut under the 20,000-byte prose cap, and the cut
dropped content. The GM's rule (2026-11-23): *"no edit to maintain entry size should ever be substantive"* - a page
over the cap is SPLIT, never trimmed. The same commit also carried accuracy corrections (449 T371), which STAY. So you
restore the lost words INTO THE CURRENT TEXT; you never revert a page to its old text. The pre-trim text is
`git -C /diagram/.clones/diagram-backlog show cce80ca436^:<path>` if you need a sentence whole.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited. A restored sentence keeps the footnote it had and needs no new source; if
you add any claim, look in the archive first (`make archive-find`) and put every page read on the ledger
(`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself. A defect is a wrong outcome:
restate rather than invent.

## Your items

- **K1 Restore 0009's losses** (`research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html`).
  Into the current text, keeping the footnotes cce80ca436 added (`qimin-yaoshu-enwiki`, `horikawa-2011-nakaboshi-6`, the
  Qimin Yaoshu link):
  1. Lead paragraph: "a Chinese farm manual of 544 drains to firm the roots and again before ripening" back to "a Chinese
     farm manual of 544 already lets the water out to firm the roots and again before the rice ripens" (the footnote
     after 544 stays).
  2. Block "In some places a hamlet settled its whole year's transplanting schedule in advance.": "The survey found ...
     even the menu of its meals." back to "A survey of customary transplanting made in 1975-76, reported for Wakayama,
     found ... even the menu of the meals for the period."
  3. Block "Where valley water could be drawn at any hour ...": "so transplanting not seldom exceeded" back to "so the
     transplanting period was long and not seldom exceeded" (the heading keeps "not seldom", the source's words).
  4. Block "A sixth-century Chinese farm manual drains the paddy ...": "That is the shape of today's calendar." back to
     "That is the shape of today's calendar: a drain in the growing season, water as the weather needs it, and a last
     drain before the harvest."
  5. Block "Was any depth of paddy water recorded before modern times?": restore "So every depth above is modern
     extension guidance." after the footnote, before "That the plant's need ...".
  6. Block "Today the drain lasts about a week.": "It varies by region, and is not an Edo figure." back to "About a week
     is the present-day guide, varying by region, not an Edo figure." (footnote unchanged).
  7. Block "On many paddies, rice in summer was followed by barley or wheat ...": "then drained in winter and worked" back
     to "then the water was let off in winter and it was worked".
  8. Block "Barley could not grow in a wet paddy.": "Barley is weak to damp." back to "Barley is weak to damp and cannot
     be grown in a wet paddy."
- **K2 Restore 0059's losses** (`research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html`
  and its `.notes.html`), keeping 449 T371's corrections ("advisable", "some joints", "a natural intake, one with no
  weir", the 1974 intake's dam, "1902", the 戦国未 note, the Ueno passage):
  1. Block "The water was divided among the fields on the dug canal ...": restore the source's term - "is tapped by
     secondary canals at division works on it, and passes on into lesser canals" back to "is passed on into secondary
     and lesser canals, which tap it at diversion works on the main canal" (note `tabayashi-1987-6` quotes "diversion
     works on the main canals").
  2. Block "The brook runs on below the intake.": "a weir mostly closed only half the river" back to "the closures
     across a river were mostly half-river closures".
  3. Block heading "The same lecture sets the intake where the current's deepest line runs against the bank." back to
     "A Japanese engineering lecture sets the intake ..." (the lecture is named, not inferred from block order).
  4. Block "Were stake weirs woven with reed before 1868?" back to "Were stake weirs woven with reed before Japan began
     to modernize in 1868?"
  5. Block "Until the late sixteenth century most intake works were small cribs ...": its body "So says a Japanese
     engineering lecture on head works, of the works up to the end of the Sengoku period." back to "A Japanese
     engineering lecture on head works says intake works up to the end of the Sengoku period, in the late sixteenth
     century, were mostly small, of timber frames packed with stone." (footnote `shimane-toshuko-lecture` unchanged).
  6. Block "Diversion weirs of the Edo period were built of timber frames, of stone or of reed.": its heading back to
     "The weirs of large rivers in the Edo period were timber frames weighted with stone." and its last sentence "The
     frames were built as the old intakes were, a crib of timber and stone." back to "These are large-river works, but
     the build is the crib of timber and stone the old village intakes were made of." (the new heading's "of reed"
     calls a bank-protection work a weir; the old heading is the claim the notes carry).
  7. Blocks "The first weirs could stand only on small streams." and "Weirs on small mountain streams are more than two
     thousand years old.": "Built of nearby wood and stone, they were fragile, so they stood only on mountain streams of
     small flow" back to "Held back with nearby wood and stone, they were fragile, so they were built only on mountain
     streams with small flow"; "placed in the Yayoi period, over two thousand years ago" back to "placed in the Yayoi
     period, so weirs have been built for over two thousand years".
  8. Notes: the absence note `where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki-6` - "No page
     we read counts ..." back to "The Chinese articles divide intakes into the two forms without counting them, and no
     page we read counts village intakes with and without a weir."
- **K3 Split each page under the cap, along its topics** (docs/research-record-rules.md, "A question has a size", the
  split rules; research/CLAUDE.md lines 84-87). The restored pages will be over 20,000 bytes of prose. Split; never cut.
  - 0059: move the section "A weir on small water was built of what lay to hand." (its intro paragraph and every block
    under it, from "The first weirs could stand only on small streams." to "How thick was a village weir?") to a NEW
    question, `make reserve KIND=question KEY="<heading>"` - a heading a reader asks from the map, e.g. "How a village
    weir was built: stakes, cribs, frames and gabions". Keep on 0059 the blocks two engine claims cite (the one-bank
    intake, the offtake's siting) and everything above that section.
  - 0009: move the "after the harvest" sections (from "Once the rice was reaped and threshed ..." through the rape
    section's "Did rape ever stand beside growing rice?") to a NEW question, e.g. "After the rice harvest: the straw
    ricks and the winter crop", and the lead's second paragraph ("After the harvest the threshed straw ...") becomes its
    lead, 0009 keeping a pointer.
  - Each new page: its own `<h2>`, tags marker filled from `research/tags.json`, an opening account, its own
    `.notes.html` (and `.originals.html` where its notes carry originals); a note moves with the sentence that cites it,
    and no note is in two places (a note both pages cite stays on one and the other cites it there, as the record
    already does across pages - check how with `grep -rn "data-note=" research/questions | head`).
  - The source page keeps a POINTER where the section was: one sentence and a link to the new page saying what it
    holds (the GM: "as long as the original page being linked to directs a reader to the other page where the full
    information can be found, then nothing needs to cascade simply because a split occurs"). A pointer never restates
    the moved evidence.
  - The drawing pages (`.drawing.html`) stay where they are; if a drawing page block cites a moved note, follow the
    record's cross-page citation form so `make record CHECK=1` passes.
  - Pop-ups that name 0009 or 0059 on their `Entry:` line are NOT edited (another builder's); list in the handoff
    those whose content now lives on a new page (grep `weir_form--` and `winter_crop--`).

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed). Both source pages and both new pages under
   20,000 bytes of prose, with every restored sentence present.
2. **Hand off.** Write `specs/451-time-retro-and-efficiency/briefs/t184-handoff.md`: `- SECTION=0009 0059 <new> <new>`,
   one line per item `K<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, each page's prose size before and after,
   every file you changed under `## Files`, and anything left open and why. Do NOT run the record checks - the next
   session does, fresh. Your last message is one paragraph saying what you wrote.
