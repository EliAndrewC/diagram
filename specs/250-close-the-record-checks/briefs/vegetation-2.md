# Brief - feature 250, page `vegetation` (T32), session 2 of 2: check, apply and close

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=vegetation SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "vegetation <step>" --marks specs/250-close-the-record-checks/measure/marks-vegetation.json

Session 1 has written this page's notes and committed them. Its handoff, `specs/250-close-the-record-checks/briefs/vegetation-handoff.md`, lists the questions
and registry keys it changed - read it first; it is your work list.

## The procedure (session 2: check, apply, close)

5. **Check, one agent per changed question or key, all in one message, in the background.** For each question:
   `make check-bundle PAGE=vegetation SECTION=<NNN>`, then `quote-check` and `record-format`, each naming the
   MANIFEST.md it printed and nothing else (the MANIFEST holds every copy inline). For each new or changed key:
   `make check-bundle KEY=<key>` and `source-applicability`. Each replies with its counts first, then only what
   you must act on.
6. **Apply** every finding (a glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then
   `make glossary`), then re-run the record commands and tests.
7. **Re-check only what moved.** If you changed a note on a check's finding, re-check THAT note alone:
   `make check-bundle PAGE=vegetation SECTION=<NNN> NOTES=<key,key>` and one `quote-check` naming its MANIFEST.
8. **Close.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py vegetation.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T=T32 BOXES=1 NOTE="<what closed, with the counts>"`. Do NOT run
   `scripts/sync-with-main.sh done`.
9. **Report.** One paragraph: items closed per form, FR-006 items confirmed or worked, the agents run, anything
   left open and why. A finding that needs the GM (the record contradicts itself, a rule would change) is not
   decided: leave the text and say so.
