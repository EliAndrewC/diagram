<!-- page-load: kind=assertions -->
# Brief - feature 444 T18, the single-field cap. Session C: check and apply

You are a FRESH session. Work in `/diagram/.clones/diagram-backlog`. The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all. Session W wrote 0017's section on how large one paddy tract grows, and its drawing page; read
`specs/444-work-budget-program/briefs/t18-handoff.md` "## Session W" for what changed.

## The procedure (session C)

1. `make record-owed` - every check the change owes (quote-check, source-reader, source-applicability, translation-check,
   record-format, intro-check as named); build each bundle with `make check-bundle`, dispatch each check as `make record-owed` says,
   and apply what each finds, re-running a check on what you change.
2. `make record && make citations`, the record tests and `make quick` green. Commit with messages opening `444 T18: `.
3. Append a `## Session C` section to the handoff (`make append`): each check's verdict, what was applied, and `STILL OWED:` -
   nothing, or what remains.
4. Do not push. Your last message is one paragraph.
