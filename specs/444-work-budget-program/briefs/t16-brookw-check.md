<!-- page-load: kind=assertions -->
# Brief - feature 444 T16, the brook's drawn width. Session C: check and apply

You are a FRESH session. Work in `/diagram/.clones/diagram-backlog`. The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all. Session W edited the drawing pages of 0059 and 0035 and two hamlet pop-ups; read `specs/444-work-budget-program/briefs/t16-brookw-handoff.md`
"## Session W" for what changed.

## The procedure (session C)

1. `make record-owed` - every check the change owes (record-format, the modal checks and the rest as named); build each bundle
   with `make check-bundle`, dispatch each check as `make record-owed` says, and apply what each finds, re-running a check on what
   you change.
2. `make record && make citations`, the record tests and `make quick` green but for its one known failure
   (`tests/hamletgen/test_pool_261.py::test_every_bamboo_stand_is_on_the_sheet[kashikawa]`, the field session's). Commit with
   messages opening `444 T16: `.
3. Append a `## Session C` section to the handoff (`make append`): each check's verdict, what was applied, and `STILL OWED:` -
   nothing, or what remains.
4. Do not push. Your last message is one paragraph.
