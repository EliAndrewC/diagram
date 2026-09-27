# Brief - feature 250, page `cities/government` (T50), session 2b of 2: check and apply, group 2 of 2

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=cities/government SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "cities/government <step>" --marks specs/250-close-the-record-checks/measure/marks-cities-government.json

Session 1 wrote this page's notes and committed them; its handoff is `specs/250-close-the-record-checks/briefs/cities-government-handoff.md`. You check and apply
ONE GROUP of the questions it changed - a fresh session per group keeps every context small (feature 250 R3,
recommendation 2). Read only your own lines of the handoff.

**Your questions:** SECTION=080, SECTION=081
**Your registry keys:** none - another group has them

## The procedure (check, apply and close the page)

5. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE=cities/government SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format` - each bundle holds only what that check reads - each agent naming its own MANIFEST.md and
   nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`. And the map's modals: run
   `python3 scripts/_entry_owed.py` from the clone root; for each class it names whose entry is one of YOUR
   questions, `make check-bundle PAGE=cities/government SECTION=<NNN> NO_QUOTES=1 FOR=entry-drift KIND=<class>` and `entry-drift` naming its
   MANIFEST (a drifted modal is owed at the push, so it is checked here, with the question it was written from).
6. **Apply ONE REPORT PER TURN.** Every finding of one report goes in ONE message: all its edits as parallel
   `Edit` calls (or one patch), never one finding a turn - every turn re-reads your whole context. Then run
   `make record && make citations` and the four record tests ONCE for everything applied, not once per report.
   A glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then `make glossary`.
7. **Re-check ONCE, only what moved.** A note changed on a check's finding: `make check-bundle PAGE=cities/government
   SECTION=<NNN> NOTES=<key,key> FOR=quote-check` and one `quote-check` naming its MANIFEST. A modal rewritten: one `entry-drift`
   on its bundle again. That is the only re-check round: a PARTIAL left after it is not re-checked again - label it
   honestly in the note (what the quote carries and what it does not, or the assertion narrowed to the quote) and
   move on (feature 250 R4: one group re-checked a question three times, a third of its session).
8. **Close the page.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py cities/government.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T=T50 BOXES=1 NOTE="<what closed on the page, with the counts>"`.
   Do NOT run `scripts/sync-with-main.sh done`.
9. **Report.** One paragraph: what your group closed, the agents run, anything left open and why. A finding that
   needs the GM (the record contradicts itself, a rule would change) is not decided: leave the text and say so.
