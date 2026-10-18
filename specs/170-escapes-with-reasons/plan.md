# Plan: Escapes Carry a Reason (feature 170)

The original feature (FR-001 - FR-005) was built from `spec.md` and `tasks.md` alone, before plans were reviewed by block;
this file holds the amendments' decisions.

## Amendment 1 (FR-006)

### T11 - the permit and its command

**D1 - The store.** `scripts/hooks/lib/hm_guard_permit.py`, stdlib only, two commands: `grant <file> <reason>` and
`check <file>` (prints the live permit's reason, else nothing). Permits are JSON lines in `<git-dir>/l7r-guard-permits.jsonl`
of the file's own checkout (`git rev-parse --absolute-git-dir`): per clone, so one session's permit is not another's, and
never committed. Not `$(STATE)` (`l7r.diagram.ci state`): that is engine code, and the store needs nothing of it. A permit is
`{"file": <realpath>, "reason": ..., "at": <epoch>}`; live for `PERMIT_SECONDS = 3600`, the newest one for a file wins, and
`check` drops expired lines as it reads. The clock is injectable (`L7R_PERMIT_NOW`) for the suite.

**D2 - What grant refuses.** A path that is not a guard file - the same test the hook applies (root `Makefile` of its
checkout, `scripts/*-hooks.sh` but not a hook's suite, `.claude/settings.json`, `dev/switches.json`, `tests/rolls.py`) - and a
reason failing `hm_escape.reason_is_enough`. Each refusal prints the command to run, exit 2. A grant prints one line: the file,
the reason, the expiry time.

**D3 - The target.** `guard-edit: export GUARD_WHY = $(WHY)`, then the one-line recipe calling `grant "$(FILE)"` with the reason
read from the environment, so a quote in the reason cannot break the shell line. Its `##` line names the arguments, so `make
help` and `make docs` list it. Checked against `hm_make.classify`: `make guard-edit FILE=Makefile WHY="..."` is `ok` (no
redirect, no `sed -i`, no override variable).

### T12 - the hook accepts the permit, and the Makefile takes no new marker

**D4 - Order in guard-file-hooks.sh.** After the recipe-hazard check and the guard-file `case`, unchanged. Then, new: for the
root Makefile (`is_root_makefile`, the test the Read branch already makes), count `GUARD_EDIT_OK` in the new text against the
text it replaces (`old_string` for Edit; the file on disk for Write); more is refused, message naming `make guard-edit
FILE=Makefile WHY="<reason>"` (slug `makefile-marker`). Then the existing marker branch, unchanged for the other guard files.
Then, before the no-marker refusal: `hm_guard_permit.py check "$FILE"`; a reason back is logged `guard_log guard-file escaped
"<reason>" guard-permit` and permitted.

**D5 - The words.** The root Makefile's Read context says: the file takes no `GUARD_EDIT_OK` comment; run `make guard-edit
FILE=Makefile WHY="<reason>"` first; the reason goes in the guard log and belongs in the commit message. The generic context
and the no-marker refusal add the same command as the other way. The three category lines stay.

### T13 - the backstop, the suite, the docs

**D6 - Tests.** `tests/hooks/test-guard-file-hooks.sh` section 8: a fixture git repo (its root `Makefile`, a hook file) so the
permit store is the fixture's and the real clone's is untouched; cases: no permit -> refused naming `make guard-edit`; grant then
edit -> accepted, logged `guard-permit` with the reason; a permit for another file -> refused; an expired permit (injected
clock) -> refused; a bare or one-word reason -> grant refused; a non-guard file -> grant refused; an Edit adding a marker to the
root Makefile -> refused even with a reason; an Edit whose `old_string` already holds the marker it keeps -> not refused for
it; a hook file with a marker -> still accepted. Section 3's Makefile marker case changes to a hook file, since (c) now refuses
it. Proved by deleting the permit branch and watching section 8 go red. The backstop is
`tests/tooling/test_makefile_recipe_comments.py` gaining one assertion: the root Makefile holds no `GUARD_EDIT_OK`.

**D7 - Docs.** `docs/guards.md`'s guard-file row and its row in the escape table name the permit; nothing else in the docs
describes the Edit route's escape.

### T14 - close

**D8.** `make hooks-test`, `make quick`, `make help`, `make docs` with a clean `git status`, `grep -c GUARD_EDIT_OK Makefile`
is 0; feature report; the feature's status line closed again; landed by `sync-with-main.sh done` (no engine path: direct).
