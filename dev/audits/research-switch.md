---
kind: adopted
title: the research switch
for: while the GM defers research, no procedure starts a research pass or a page session by itself - a physical task's decision is drawn as a best guess labeled UNRESEARCHED onto make research-backlog instead
measured: unmeasured
first-audit: when the GM turns research back on (make research-open), the deferred guesses on make research-backlog searched: how many changed what a map shows, against the research-pass and page-session minutes the deferral kept out of the builders' way; and the escapes (make guard-log GUARD=research-switch)
measurement: none of its cost or saving measured; the GM's ruling of 2026-11-25 that none of the queued research was blocking or likely to change the scripted generation much ("I would like to essentially defer all of it until at least tomorrow")
command: make switches; make research-backlog; make guard-log GUARD=research-switch
falsifier: the deferred guesses, once searched, change what maps show often enough that drawing them as guesses cost more rework than the research would have
threshold: more than 1 in 5 deferred UNRESEARCHED decisions changing a map visibly once searched, or RESEARCH_OK escapes past 1 in 3 of the guard's refusals (GUESS)
cost: make task-time's research-pass and page-session rows (the minutes not spent while deferred); the guard's refusals in make guard-log
last-audited: never
cadence-days: 7
covers: rust/guard/src/guards/research_switch_hooks.rs
---

451 T244: a `research` state in `dev/switches.json` beside claims and port (`open` or `deferred`), thrown with the GM's words by
`make research-deferred` / `make research-open`. While deferred: a physical task's research boxes take `deferred: UNRESEARCHED`; a
port stage's end lists its backlog (`make research-backlog STAGE=`) instead of searching it; a `research-pass` dispatch and a
`make page-session` start are refused naming the switch (`RESEARCH_OK="<reason>"` escapes, recorded). A malformed or missing entry
reads `open`, so a broken file never silently defers research.
