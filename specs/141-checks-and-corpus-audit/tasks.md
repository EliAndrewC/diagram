# Tasks: Which Automated Checks Still Earn Their Keep (feature 141)

- [x] T01 the census tool: inputs per check (registry dataflow), per-stage snapshots (reference + polder), branching readers, fixtures by tier; `make check-census`; the ledger (`ledger.md/.json`)
- [x] T02 the hand pass over every mechanical candidate: RETIRE (placer guarantee + the named placer test), KEEP best-effort, KEEP plausible-but-untested (named), LEGACY-FEATURE vacuous on hamlets (`ledger.json` `hand` / `placer_test`)
- [ ] T03 retirement: whole segments whose every check retires - segment, its check-village tests, its fixtures (trimmed or deleted), the frozen registry rows and check-name fixture updated (`retired.json`)
- [ ] T04 scripted negative fixtures for kept hamlet-tier checks pinned only by hand-era fixtures, or the ledger says why not (FR-004)
- [ ] T05 the doctrine rewritten: `dev/gate.md`, `tests/CLAUDE.md`, the constitution (a bad map becomes a placer unit test first)
- [ ] T06 `make done` green; the before/after numbers (checks, fixtures, gate seconds) in research.md
- [ ] T07 the explanation to the GM: what was retired, what was kept and why, what remains (the plausible-but-untested set, the legacy tiers with the numbers, the held-back bundles); the GM's questions and cuts worked here
- [ ] T99 **the GM accepts** - verbatim; the feature lands only after
