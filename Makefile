# Root Makefile - there is no engine here; every target lives in .claude/skills/diagram/Makefile.
#
# WHY THIS FILE EXISTS (feature 133 T33, 2026-08-27). A session ran `make done` from the clone root,
# in the background, piped through a grep - and read the grep's exit 0 as "gate green". Without a
# Makefile here, make printed one line to a log nobody read, and a task was closed against a gate
# that had never run. Twice in one session. So the root FORWARDS the diagram targets to the skill's
# Makefile: the command that used to fail silently now does the right thing, and anything else
# names the route instead of guessing.

DIAGRAM := .claude/skills/diagram

.PHONY: help
help:
	@printf 'This is the repository root; the engine and its targets live in %s.\n' "$(DIAGRAM)"
	@printf 'The diagram targets are forwarded from here: make done | quick | maps | reference | hooks-test | ...\n'
	@printf 'Anything else: (cd %s && make <target>)\n' "$(DIAGRAM)"

# Forwarded verbatim. Kept as an explicit list, not a %-rule, so a typo names the route rather
# than being forwarded into a second "No rule to make target".
# GUARD_EDIT_OK: feature 185 - `scope-lock`/`scope-unlock` retired with the lock. `gate-manifest`
# and `new-check` went with the check battery in feature 166 and were never removed here (FR-004a):
# a stale forward resolves, forwards into the skill, and dies naming the WRONG file - the exact
# second-order failure the comment above says this explicit list exists to prevent.
# GUARD_EDIT_OK: feature 197 - `claim` forwards too; it is the specify step's first command and runs from the clone root.
FORWARD := done quick maps reference hooks-test tooling durations page-check tick claim \
           switches ci-status ci-off ci-on perf-report perf-review audit
# GUARD_EDIT_OK: feature 197 - FIXING A FORWARD THAT BROKE ON CORRECT WORK (Principle XIV, found while ticking
# this feature's own tasks). `$(MAKEOVERRIDES)` expanded to the raw `NOTE=<text>` and was pasted UNQUOTED into
# the recipe, so `make tick NOTE="green; every case"` from the repository root ran `tick NOTE=green` and then
# tried to execute `every case` as a command (exit 127) - four of eight ticks landed with their notes cut at
# the first `;`, and four with `(` failed outright. GNU make already hands command-line variable definitions to
# a sub-make through MAKEFLAGS, correctly quoted, so the explicit paste was redundant as well as wrong.
# Verified: `make tick ... NOTE="a; b (c)"` and `make claim SLUG=x PEEK=1` both reach the skill Makefile intact.
.PHONY: $(FORWARD)
$(FORWARD):
	@$(MAKE) --no-print-directory -C $(DIAGRAM) $@
