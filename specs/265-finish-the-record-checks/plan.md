# Plan - feature 265, finish the record checks

## Decisions

### D1 - The method is feature 250's, unchanged

Every page is worked by `specs/250-close-the-record-checks/measure/brief.py <page> <task>` and the `make
page-session` line it prints: a split session for each item question over the cap, a write session, check groups
packed by load (questions, owed modals, registry keys; `GROUP_BYTES` 28,000), owed modals folded in, reports applied
by `make apply-edits`, the canon by `make canon`. The task a brief closes is this feature's own (`F=265-...`): the
check brief's close step ticks it. No page is measured round against round; `tokens.py summary` is run once per page
for the closing report.

### D2 - Prefixes under a lock (FR-010, T12-T13)

`scripts/reserve-prefix.py`, `make reserve KIND=glossary|registry KEY=<key>`, modeled on `scripts/claim-feature.py`:
`fcntl.flock` on `<mirror>/.specify/prefixes.lock`; the next prefix is 10 past the highest held by the mirror's tree,
every clone under `<mirror>/.clones/`, and the ledger `<mirror>/.specify/prefixes.jsonl` (the ledger covers a number
reserved and not yet visible); the file is created - a stub the caller then fills - before the lock is released, so
the next caller's scan sees it; it prints the path. `_apply_edits.apply_term` reserves its glossary prefix the same
way. `new-file-hooks.sh` (PreToolUse on Write) refuses a Write that CREATES a file in the glossary directory or the
registry's `010-works-cited/` whose prefix the ledger does not hold, printing the `make reserve` command; registered
in the fallback form, its suite proved red on a mutated copy. A test runs two reservations at once in processes and
asserts different prefixes.

### D3 - Queues in sibling clones (FR-010, T14)

`make page-queue N=<n> BRIEF="..."` clones this clone to `.clones/diagram-research-<n>` (or reuses it, fast-forwarded
from this clone), and starts `make page-session` there - its sessions named after that clone, so the clone guard
routes them. When the queue ends, `scripts/pull-queue.sh <n>` pulls the sibling's commits back here (a local `git
pull`, never a push), and where the merge conflicts only in regenerated files (the assembled research and citations
pages, `SOURCES.html`, the glossary bundles) it rebuilds them with `make record`, `make citations` and `make glossary`
and commits; a conflict anywhere else stops and is resolved by hand. The briefs are written in THIS clone and name
their files by absolute path, so a queue's sessions read them from here; their `SECTION`/`KEY` derivation reads the
queue clone's own commits (`changed_since`).

### D4 - Three queues

Up to three queues at a time, balanced by work (items, FR-006 items, over-cap questions): A - `urban-features` (12
FR-002, 6 FR-006, five splits); B - `towns` (10) then `ways` (1); C - `cities/river-cities` (8), `buildings` (7), then
`cities/capitals` (7 FR-006). This clone dispatches; each queue runs in its own sibling.

### D5 - After the pages: the sweeps, the download list, the close

FR-003 to FR-005 (T07-T09) run here after every queue is pulled back, since they touch every page; then FR-008 (T10)
and T11: FR-007's checks over what the sweeps changed, every owed pair answered (`brief.py owed-check`), the closing
report, `make page-check`, `make done`, the push.
