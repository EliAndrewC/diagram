---
kind: adopted
title: the audit register and its check
for: every optimization or procedure that costs time or tokens arrives with its measurement and its falsifier, and is re-audited on its cadence instead of standing forever
measured: 2026-11-25
measurement: the check replayed over the last 20 landings on main (each tick commit of make land against the one before): with the five detectors over the tooling crates (2026-11-26), 9 detections in 6 landings, each a real mechanism (451 T233's push check gm-attributions, T246's SNAPSHOT_DAYS, T245's EVERY and FREE_PCT, T242's COMMIT_POLL_MS, COMMIT_TRIES and HANDOFF_FRESH_S, T234's LINK_WORDS, T244's research_switch_hooks.rs), no false fire; with the first four (2026-11-25), 3 of those; before the name-word filter T245 also fired on GB (a unit) and LARGEST (a display count); over 1,000 commits back to 2026-11-20 with the first four, 34 detections; the whole tree at 2026-11-26, 267 mechanisms, 254 of them no entry's (make audits' BACKFILL, 451 T260); a run takes 0.17 to 0.18 s (2026-11-26; 0.10 s with the first four)
command: scripts/gates/l7r-gate.sh check audit-register --range <previous landing> <landing> --root "$PWD" --empty-register (each landing; without --empty-register against the register at that landing); make audits
falsifier: it refuses correct work - a landing adding nothing that costs time or tokens - or sessions escape it instead of writing entries
threshold: more than 1 false fire in 20 landings, or AUDIT_ENTRY_OK escapes past 1 in 5 of its refusals (make guard-log GUARD=audit-register) (GUESS)
cost: make static's and the push's row (0.17 to 0.18 s a run, measured 2026-11-26; 0.10 s with the first four detectors, 2026-11-25); an entry's writing at each new mechanism
last-audited: 2026-11-25
cadence-days: 30
covers: push check audit-register selftest
covers: push check audit-register
---

451 T259, the GM 2026-11-25 (agenda item 13): "a list of all of the auditable optimizations and processes and procedures, and then
each one would know the last time that it was audited ... re-audit to see if they still make sense or if they need to be tweaked or
redone or eliminated". `rust/gate/crates/checks/src/checks/audit_register.rs` and `audit_register/detect.rs` say exactly what the
check detects. What it does not detect - a rule line in a CLAUDE.md or `docs/` that tells a session to wait or always do a step, a
mandatory review round, a standing order in an agent file already there - enters the initial backfill by agenda item 13's sources
(451 T260) and after it is added as found, as the GM asked ("we can backfill as we
go, as we find things that we missed"), because a check that fired on prose would fire on correct work.
