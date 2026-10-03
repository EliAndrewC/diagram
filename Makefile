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
	@printf 'Every documented diagram target is forwarded from here: make done | quick | maps | hooks-test | claims-report | ...\n'
	@printf 'Anything else: (cd %s && make <target>)\n' "$(DIAGRAM)"

# Forwarded verbatim: EVERY documented target of the skill Makefile, DERIVED, never listed (feature 316 follow-up, GM
# 2026-10-03: *"That bug keeps recurring where something gets defined but then not passed through"*). The list was kept by
# hand so a typo would name the route rather than be forwarded into a second "No rule to make target" - and six features
# (197, 274, 285, 295, 313, 316) each added a skill target and forgot it here, while `reference`, renamed `_reference`,
# stayed listed and forwarded into exactly that second failure. `scripts/make-docs.py --forwardable` prints every target
# with a `##` line that is not flagged `{internal}`, the same parse that builds docs/make-targets.html and that the gate's
# `make-docs --check` holds: a target forwards the moment it is documented and stops the moment its line goes, and a typo
# or an undocumented name still fails HERE, naming the route. tests/tooling/test_make_docs.py pins the derivation.
# GUARD_EDIT_OK: feature 316 follow-up - the hand list replaced by the derivation above; nothing the list forwarded is
# lost except the retired `reference`, which forwarded into a second "No rule to make target".
# `help` is the root's own (it names the route); the skill's `help` is reached with `cd .claude/skills/diagram && make help`.
FORWARD := $(filter-out help,$(shell python3 "$(CURDIR)/scripts/make-docs.py" "$(CURDIR)" --forwardable))
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
