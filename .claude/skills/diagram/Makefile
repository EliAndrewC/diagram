# The diagram-skill quality gate (Constitution Principle X). Run `make done` before declaring
# any Python change complete. Runs, in order: lint, format-check, type-check, tests+100% coverage.
#
# The type checker is pyrefly (feature 142, 2026-08-28): a Rust one-shot, ~0.6 s cold for the whole engine
# with nothing resident - it replaced mypy + the dmypy daemon (400-600 MB per clone). Rules in pyproject.toml.

# (GUARD_EDIT_OK: feature 132 adds the iteration switches - a new guard and five new operations)
.PHONY: done lint format typecheck test test-full guard perf perf-report maps reference bypass-audit quick durations test-file audit perf-gate hooks-test explain \
	 switches ci-off ci-on scope-lock scope-unlock _switch \
	 map cohort tripwire hamlet cache-audit regressions placement-stages pool-index pool-index-if-stale compound render-sync idle-tests \
	 gate-manifest why-placed site-justice crop jogs pack-audit scatter-audit sun-audit new-check timings citybudget help \
	 notes-census \
	 ci-status ci-check ci-merge ci-image commit-permitted \
	 perf-explain perf-confirm perf-audit perf-signoff perf-review perf-profile check-census firing-census firing-census-suite

# ---- THE PERFORMANCE BANDS (feature 129 - GUARD_EDIT_OK: adding the review-record operations) ----
# Any increase (total OR any seed, per ENVIRONMENT) owes a written explanation and a perf-audit
# subagent's confirmation; >5% total / >10% seed owes the escalated audit; >10% / >20% owes the GM's
# personal sign-off before the push. `perf-report` and `perf-gate` PRINT the verdict (FR-009b);
# `perf-review` (run by sync-with-main.sh at the push) ENFORCES it. A subagent's shell is not
# distinguishable from the session's (research R1), so confirm/audit PROMPT and decline without
# AS=perf-audit - the declaration is recorded, and the record's content is what a self-grant fakes.
PERF_REVIEW = python3 -m l7r.diagram.tools.perf_review
perf-explain:   ## band 1, first half: the session's written cause     WHY="..." [ENV=local|codebuild]
	@$(PERF_REVIEW) explain --why "$(WHY)" --environment "$(or $(ENV),local)"
perf-confirm:   ## band 1, second half - the perf-audit SUBAGENT runs this   VERDICT=consistent|inconsistent AS=perf-audit
	@$(PERF_REVIEW) confirm --verdict "$(VERDICT)" --note "$(NOTE)" --as "$(or $(AS),main)" --environment "$(or $(ENV),local)"
perf-audit:     ## band 2 - the subagent adjudicates   VERDICT=justified|not-justified|cannot-determine NECESSARY= COMMENSURATE= NO_WAY_AROUND= AS=perf-audit
	@$(PERF_REVIEW) audit --verdict "$(VERDICT)" --necessary "$(NECESSARY)" --commensurate "$(COMMENSURATE)" --no-way-around "$(NO_WAY_AROUND)" --note "$(NOTE)" --as "$(or $(AS),main)" --environment "$(or $(ENV),local)"
perf-signoff:   ## band 3 - the GM, at a terminal   WHY="..."
	@$(PERF_REVIEW) signoff --why "$(WHY)" --as GM --environment "$(or $(ENV),local)"
perf-review:    ## does every environment's newest bookend pair carry the records its band owes? (the push runs this)
	@$(PERF_REVIEW) check
check-census:   ## feature 141: which checks re-measure a placer's guarantee (the ledger)   OUT=specs/141-checks-and-corpus-audit/ledger
	$(RUN).tools.check_census --out "$(or $(OUT),specs/141-checks-and-corpus-audit/ledger)"

firing-census-suite: ## feature 163: the census PLUS the suite sweep - the firing no artifact glob can see
	@rm -rf $(CURDIR)/.firing-journal && mkdir -p $(CURDIR)/.firing-journal
	-@$(MAKE) --no-print-directory test JOURNAL=$(CURDIR)/.firing-journal
	@$(MAKE) --no-print-directory firing-census SUITE=$(CURDIR)/.firing-journal

firing-census:  ## feature 163: which checks does the CURRENT implementation still make fire?   SUITE=<journal dir>
	$(RUN).tools.firing_census --out "$(or $(OUT),specs/163-checks-into-the-placer/firing-census)" $(if $(SUITE),--suite "$(SUITE)",)

perf-profile:   ## tier 2 evidence: cProfile ONE stage of ONE seed   SEED=25 STAGE=web
	$(RUN).tools.perf_profile --seed "$(SEED)" --stage "$(STAGE)"

hamlet-floor:   ## the modules under the 100% hamlet-path floor (feature 145; derived from the scripted rolls' records; GUARD_EDIT_OK: a new operation)
	$(RUN).tools.hamlet_floor --list

hamlet-floor-check:   ## judge the last coverage data against the hamlet-path floor (what test-full's last phase does; GUARD_EDIT_OK: a new operation)
	$(RUN).tools.hamlet_floor

# THE VERIFICATION STATE (feature 130, FR-012 - GUARD_EDIT_OK: adding the CodeBuild gate). Every
# local target that proves something records it in .git/verification-state.json with the content
# hash of the engine's Python at that moment; the dispatcher refuses a paid run unless the most
# recent record is a GREEN local check against EXACTLY the code being pushed. The GM's case: *"make
# done fails, and then they make a change, and then just immediately run make done again without
# running a more targeted test first ... This feels like something that we should be able to
# actually prevent."* A failed gate records failed-gate; a source edit is caught by the hash.
STATE = python3 -m l7r.diagram.ci state

# Runs EVERY phase and reports all failures together (GM 2026-07-25). It used to be
# `done: lint format typecheck test`, which make stops at the first failure - so a lint slip hid a
# type error hid a coverage hole, and each hidden failure cost another full round trip to discover.
# Phases stay in cheap-to-expensive order so the fast ones report first, but none of them short-
# circuits the rest. Exit is non-zero if any phase failed, so this is exactly as strict as before.
# ---- ONE COMMAND, AND IT IS THE CHEAP ONE BY DEFAULT (GM 2026-08-24) -------------------------
#
# `make done` runs the REFERENCE settlement and everything that does not roll another map. That is
# the gate for the normal case, and it is what a reference-only push is verified with.
#
# `make done FULL=1` additionally rolls every live pool map, re-gates each, and runs the seeds 41-44
# ratchet - and it will not do so silently: it PROMPTS for a written justification and appends it to
# dev/bypass-log.jsonl with the date, target and commit. There is no second command to reach for.
#
# WHY THERE IS ONLY ONE (GM 2026-08-24): *"I don't know if I like the idea of there being both a
# make done and a make done reference because that just gives you a way to run the wrong version."*
# That is not hypothetical - during feature 126 three separate guards were added and each was walked
# around by using a command the guard did not cover: `cohort_audit` while `make maps` was gated, then
# `make done` and `make test` while both of those were. A choice between a fast path and a slow path
# is a choice that gets made wrong under pressure, so the choice is gone.
#
# The constitution requires every diagram feature to AUDIT dev/bypass-log.jsonl as a closing step -
# read the entries added during the feature and say, in writing, whether each was justified.
# FULL RUNS THE REFERENCE CHECK TOO (feature 130, FR-034, research R15 - GUARD_EDIT_OK: fixing a
# defect). Before this, `bypass-audit` ran IN PLACE OF `reference` when FULL was set, so a full run
# went prompt -> lint -> ... -> the whole suite with no reference-first stop; the prompt had been
# built as the reference BYPASS. The GM's understanding ("there is no way to short circuit that")
# was true only of reference scope. Now: the prompt authorizes the EXPENSE, then the reference map
# still gates; REF_OK is the one, separate, logged way to skip that step, as for every other target.
done:
	@$(if $(FULL),$(SWITCH) check scope "done FULL=1",true)
# (GUARD_EDIT_OK: feature 132 - a FULL run is a pool sweep, so the scope lock refuses it BEFORE the prompt.
#  THE LOCAL SHORT-CIRCUIT (same feature, the GM's amendment): reference scope reuses the verdict in hand when
#  the last record is a green `make done` against exactly this engine
#  content - EXACTLY the dispatcher's two keys, the skill-Python hash and the engine key over tests/pool data; the
#  Makefile, pyproject, lockfiles and scripts/ are NOT in it, as they are not in the remote key (GM 2026-08-25, second
#  amendment: "we were omitting make done results for changes to the hooks or scripts or makefile"). "It's only
#  documentation" then costs seconds, not five minutes. Never for FULL (a different scope). No flag forces either
#  direction (GUARD_EDIT_OK: the fidelity review removed a FORCE= flag as unrequested). ONE shell block, so `exit 0`
#  ends the target before the reference step. Re-stamping is safe because the key includes the stamp's own hash.)
	@if [ -z "$(FULL)" ] && python3 -m l7r.diagram.ci verified-done; then \
	  root=$$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$$root" ] && python3 "$$root/scripts/gate-stamp.py" --write diagram || true; \
	  $(LOGRUN) $(DONE_NAME) reference 0 already-verified; $(STATE) green-local $(DONE_NAME) reused; \
	  printf '\n\033[1mgate green\033[0m (already verified - nothing the gate exercises has changed since the last green run)\n'; exit 0; \
	fi; \
	$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" || exit 1;,) \
	$(if $(REF_OK),$(LOGBYPASS) permitted "REF_OK - reference step skipped: $(REF_WHY)"; printf '\nreference step SKIPPED (REF_OK, logged to dev/bypass-log/)\n';,$(MAKE) --no-print-directory reference || exit 1;) \
	T0=$$(date +%s); fail=""; \
	for phase in lint format typecheck hooks-test $(if $(FULL),test-full perf-gate,test); do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; \
	  if [ "$$phase" = hooks-test ] && root=$$(git rev-parse --show-toplevel 2>/dev/null) && python3 "$$root/scripts/gate-stamp.py" --fresh hooks; then \
	    printf 'hooks-test: already green against exactly these guard scripts - skipped (gate-stamp --fresh hooks; 84 s measured 2026-08-26)\n'; continue; fi; \
	  $(MAKE) --no-print-directory $$phase || fail="$$fail $$phase"; \
	done; \
	if [ -n "$$fail" ]; then $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (every phase ran - fix them together, then re-run once)\n' "$$fail"; exit 1; fi; \
	root=$$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$$root" ] && python3 "$$root/scripts/gate-stamp.py" --write diagram || true; \
	$(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" green; \
	$(STATE) green-local $(DONE_NAME); \
	$(if $(FULL),printf '\n\033[1mgate green (FULL - every pool map re-gated, seeds 41-44 rolled)\033[0m\n',printf '\n\033[1mgate green\033[0m (reference settlement + non-map tests; `make done FULL=1` also rolls the other pool maps)\n')

# THE REFERENCE-HAMLET PERFORMANCE BOOKENDS (constitution VI, GM 2026-08-23).
#
# Deliberately NOT part of `done`. A hamlet takes 30-160s and the reference set is four seeds, so
# folding this into the gate would roughly double a cycle that already runs ~5 minutes - and this
# project's own measurements say iteration latency is the dominant cost of a feature. So the sweep
# is explicit and the CONSTITUTION carries the obligation to run it, at the start of a diagram
# feature and again before it ships.
# ---- ONE COMMAND, WHICH PICKS ITS OWN SCOPE (constitution VI) --------------------------------
#
# `make maps` reads how the LAST run went and decides:
#
#     last run PASSED -> the whole tier, reporting every failure together
#     last run FAILED -> the REFERENCE map alone, stopping at the first problem;
#                        only if it passes does it go on to the rest
#     no last run     -> treated as FAILED
#
# There is deliberately no second command. The rule this replaces ("prove it on the reference
# settlement first, then sweep") was correct, was written into the constitution, and was violated by
# its own author six hours later - five 10-12 minute four-map cycles chasing a defect the reference
# hamlet answered in 67 seconds. A choice is a thing that gets chosen wrong under pressure.
#
# `SCOPE=reference` / `SCOPE=all` says what you mean when you know better.
# ---- THE REFERENCE SETTLEMENT GATES EVERYTHING EXPENSIVE (constitution VI) -------------------
#
# `make reference` rolls ONE seed of ONE map - Inashiro - and nothing else. It is the cheapest
# question in the project (~60 s) and every expensive target now asks it FIRST:
#
#     make test   -> reference, then the suite
#     make done   -> reference, then lint/format/typecheck/test/coverage
#     make maps   -> reference, then (only if clean) the rest of the tier
#
# If the reference settlement is red, those targets STOP THERE. Not a warning, not a slow path -
# they refuse to run the expensive work at all.
#
# WHY (GM 2026-08-24): "our goal here is to start small, get something working, and then expand on
# it ... the very fact that you are capable of running more than that means that our tooling is
# supporting more expensive testing than what I have explicitly said should be permitted."
#
# The measured cost of not having this, in ONE feature: six 20-25 minute cohorts, most launched over
# a tree already known to be broken, plus repeated four-map ratchet runs to diagnose a single failing
# seed. The rule existed in the constitution the whole time and was violated by its own author within
# hours, twice. A guard that lives only in documentation is not a guard, and a guard on one command
# out of four is not a guard either.
#
# ESCAPE HATCH: REF_OK=1 on the command line, for the case where the reference map is legitimately
# expected to fail (you are mid-surgery on it, or bisecting). Deliberately awkward, and it says so.
# ---- BYPASSING THE REFERENCE GATE COSTS A WRITTEN JUSTIFICATION ------------------------------
#
# REF_OK=1 does not simply let the expensive targets run. It demands WHY, in prose, and appends it
# to dev/bypass-log.jsonl with the date, the target and the git HEAD - so a later reader can ask
# whether the reason was any good. That log is the point: a flag you can type is a speed bump, a
# reason someone will READ is a decision you have to defend.
#
# WHY THIS EXISTS (GM 2026-08-24): *"how often I keep saying over and over again to just run the
# quick tests, and then you keep finding ways to run the long tests ... we need to make it either
# literally impossible or so obvious that you should not be doing it that you simply won't."*
# Measured, in one feature: six 20-25 minute cohorts, most over a tree already known to be broken,
# plus repeated four-map ratchet runs to diagnose one seed. Three separate guards were added during
# that feature and each was walked around by using a command the guard did not cover.
#
# LEGITIMATE reasons look like: the reference map is the thing under surgery and is expected to
# fail; you are bisecting and need the suite's verdict on a knowingly-red tree; a check that only
# fires on a non-reference map is the subject. "I want to see everything" is not one.
#
# REF_WHY="..." supplies the reason without the prompt - but ONLY with a terminal attached. A
# non-interactive FULL run with REF_WHY set is REFUSED outright (see bypass-audit), because that
# combination is precisely how feature 126 ran the full gate three times against a standing
# instruction to run only the reference settlement: the prompt defaults to NO, and a backgrounded
# run cannot be asked to reconsider. Every one of those bypasses was logged, and none was stopped -
# which is the whole lesson. An audit trail records a decision; it does not make one.
# ---- THE MIDDLE TIER, AND THE ONE THAT STOPS AT THE FIRST FAILURE ---------------------------
#
# MEASURED 2026-08-24: `quick` is ~4 MINUTES, not "seconds" as this comment and the hook's
# refusal text both claimed. The label was written from intent rather than a stopwatch. It is
# still the right target for an iteration loop - it stops at the first failure - but it is not
# cheap, and a tip that misstates a cost teaches a session to distrust the tips.
#
# `make quick` is what an iteration loop uses once the reference map is clean: lint, types, and
# every test that does NOT roll a map, with pytest's `-x` so it STOPS at the first failure. Seconds,
# not minutes, and it answers "is what I just wrote coherent" rather than "is this safe to ship".
#
# The full suite rolls a dozen-plus maps (test_village_passes_gate regenerates and re-gates every
# live pool map; the ratchet rolls seeds 41-44), which is right for a pre-push gate and wrong for a
# loop. Measured on feature 126: `make done` is ~5 minutes and I ran it repeatedly over a tree I
# already knew was broken.
# QUICK ROLLS NO MAPS AT ALL, and that is the whole contract. It used to run `make reference` first
# (~26 s of map generation) which contradicted its own promise and, with the marker fix below, was
# most of what remained of its cost. FR-014's reference-first ordering binds EXPENSIVE targets - the
# ones that would waste minutes on a tree the 60-second check would have condemned. `quick` rolls
# nothing, so there is nothing for a broken reference map to waste; run `make reference` when you
# want the map checked, which is a separate question from "did I break the code".
#
# MEASURED 2026-08-24: 254 s -> 94 s (marker deselect) -> this. The 254 s version was being pointed
# at by every guard in this feature as the cheap option.
# QUICK ENFORCES ITS OWN BUDGET, because the whole point of this feature is that the target the
# guards point at is actually fast. It was 254 s while every blocked command was being sent to it as
# the cheap option, and nothing said so - a target gets slower one unmarked test at a time and no
# check exists for "this is still quick" unless you write one.
#
# TIMED WITH `date +%s`, NOT `$$SECONDS`: make's default shell is sh, where SECONDS is unset, so the
# first version computed an empty elapsed time and never fired - it passed a 1-second budget on a
# 31-second run. Caught by testing the guard rather than trusting it, which is the same check that
# T034 applies to every other guard in this feature.
#
# 60 s against a measured ~33 s leaves room for a slower machine and for the suite to grow, and still
# fires long before anyone would call it slow. RAISE IT ONLY WITH A MEASUREMENT, and prefer marking
# the slow test instead: the budget is the alarm, not the fix.
# ============================================================================================
# OPERATIONS - every runnable unit of this project's work has a target (FR-001)
#
# "We want make commands for everything" (GM 2026-08-24). Not decoration: `scripts/make-only-hooks.sh`
# refuses a bare interpreter and NAMES the target instead, so an operation without one is an operation
# a session cannot legitimately run. That gap was real - gating bare pytest left "why is this slow"
# with no route but the override, which is precisely how an override becomes routine.
#
# EXPENSIVE targets check the reference settlement FIRST and stop if it fails (FR-014): spending
# minutes on a tree the 26-second check would have condemned is the waste this whole feature is about.
# CHEAP ones (read a recorded artifact rather than produce one) run immediately - prompting there
# would push a session toward regenerating a map, which is the opposite of the point.
#
# REF_OK=1 skips the reference check, and demands a logged reason like every other bypass here.
# ============================================================================================

REF_FIRST = @$(if $(REF_OK),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)",$(MAKE) --no-print-directory reference)
RUN = @python3 -m l7r.diagram

# ---- THE ITERATION SWITCHES (feature 132 - GUARD_EDIT_OK: a new guard, thrown by the GM) ----------
#
# Two committed switches in dev/switches.json, read here and in every Python entry point that can
# roll more than one map. `remote off`: nothing dispatches to CodeBuild and the gated push lands on
# a green local `make done` instead. `scope reference`: no invocation rolls a map other than the
# reference settlement, and none rolls more than one. Thrown and released ONLY by the four targets
# below, each demanding a REASON and committing the file - there is no variable or flag past a
# thrown switch, by design. WHY (GM 2026-08-25): *"not only do we not run the full test suite, but
# we literally cannot because just telling you, please make sure not to run the full tests. In the
# past has frequently resulted in the full tests getting run, and that costs both time and actual
# money now that we are running on AWS."* The doctrine and the priced alternatives: dev/switches.md.
SWITCH = python3 -m l7r.diagram.switches
SWEEP_OK = @$(SWITCH) check scope "$@"
# (GUARD_EDIT_OK: feature 133 FR-004 - a refused paid target also leaves a would-have-dispatched run-log entry, so
#  remote-off never hides how often money was about to be spent; the check itself is unchanged, ci/ does the write)
REMOTE_OK = @python3 -m l7r.diagram.ci remote-ok "$@"

switches:       ## the iteration switches: remote on|off, scope unlocked|reference (feature 132)
	@$(SWITCH) show
ci-off:         ## REMOTE OFF - nothing dispatches to CodeBuild; the gated push lands on a green local make done   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=off MSG="remote off" REASON="$(REASON)"
ci-on:          ## REMOTE ON - the default; the gated route may dispatch again   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=on MSG="remote on" REASON="$(REASON)"
scope-lock:     ## SCOPE LOCKED to the reference settlement - every sweep refuses   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=scope STATE=reference MSG="scope locked" REASON="$(REASON)"
scope-unlock:   ## SCOPE UNLOCKED - the default; sweeps run again (and are owed)   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=scope STATE=unlocked MSG="scope unlocked" REASON="$(REASON)"
_switch:
	@[ -n "$(REASON)" ] || { printf '\n\033[1mREFUSED: a reason is required\033[0m - a reason someone will READ is a decision you have to defend.\n  make <target> REASON="..."\n\n'; exit 1; }
	@$(SWITCH) set $(AXIS) $(STATE) --why "$(REASON)"
	@git add dev/switches.json && git commit -q -m "chore: $(MSG) - $(REASON)" && printf '\ncommitted: %s - %s\n' "$(MSG)" "$(REASON)"

# --- expensive: they generate ---------------------------------------------------------------
verify:         ## THE PAIRED RUN: start the gate and dispatch the settlement-review together (feature 151)
	@printf '\033[1mverify\033[0m: the gate and the independent review run TOGETHER - neither alone (GM 2026-08-29).\n'
	@root=$$(git rev-parse --show-toplevel) && python3 -m l7r.diagram.ci engine-key worktree > "$$root/.git/pairing-key" || true  # NOT $(RUN): it carries a leading @, which is a literal argument once it is not at the start of a recipe line
	@root=$$(git rev-parse --show-toplevel) && printf 'engine key %s\n' "$$(cut -c1-12 "$$root/.git/pairing-key" 2>/dev/null)"
	@root=$$(git rev-parse --show-toplevel); \
	  maps=$$(git -C "$$root" diff --name-only HEAD~1 HEAD -- '.claude/skills/diagram/pool/*/*/*.json' '.claude/skills/diagram/legacy-hand-authored-pool/*/*/*.json' 2>/dev/null | sed 's#.*/##;s#\.json##' | tr '\n' ' '); \
	  printf 'maps whose manifest changed: %s\n' "$${maps:-none}"; \
	  printf '\n\033[1mDISPATCH NOW\033[0m, in the same turn: settlement-review over%s, then let this gate run beside it.\n' " $${maps:-the delta}"
	@printf '\nstarting the gate in the background - its verdict arrives as a task notification.\n\n'
	@root=$$(git rev-parse --show-toplevel); PAIR_OK="started by make verify - the review is dispatched in the same turn" nohup $(MAKE) --no-print-directory done > "$$root/.git/verify-gate.log" 2>&1 &

map: export L7R_STAGE_PROFILE = $(if $(PROFILE),1,)
map:            ## regenerate ONE gen and gate it   GEN=pool/hamlets/inashiro/inashiro.gen.py [PROFILE=1: where the roll spent its time]
	$(REF_FIRST)
	$(RUN).pipeline.regen $(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)
	@$(MAKE) --no-print-directory pool-index-if-stale

cohort:         ## roll N seeds and report every failure      N=48
	$(SWEEP_OK)
	$(REF_FIRST)
	$(RUN).tools.cohort_audit --count $(or $(N),48)

tripwire:       ## the middle tier: reference map, then the tripwire seeds
	$(SWEEP_OK)
	$(RUN).tools.mapcheck $(if $(SCOPE),--scope $(SCOPE),)

hamlet: export L7R_STAGE_PROFILE = $(if $(PROFILE),1,)
hamlet:         ## generate one hamlet from the CLI   ARGS="--name X --seed 4 ..." [PROFILE=1]
	$(REF_FIRST)
	$(RUN).hamletgen $(ARGS)
	@$(MAKE) --no-print-directory pool-index-if-stale

cache-audit:    ## does using the generation cache change any map?
	$(SWEEP_OK)
	$(REF_FIRST)
	$(RUN).tools.cache_audit $(ARGS)
# (GUARD_EDIT_OK: feature 132 - cache-audit and regressions roll many maps, so the scope lock refuses them first)
regressions:    ## rebuild the frozen negative-fixture corpus
	$(SWEEP_OK)
	$(REF_FIRST)
	$(RUN).tools.make_regressions $(ARGS)

placement-stages: ## re-plate the stage-by-stage walk-through page
	$(REF_FIRST)
	$(RUN).tools.placement_stages $(ARGS)

pool-index:     ## rebuild the pool index
	$(RUN).pipeline.pool_index $(ARGS)

# THE INDEX FOLLOWS THE TREE IT IS IN (GM 2026-08-27). pool/index.html is derived and gitignored, so
# a session clone had NO index at all - render-sync only ever wrote main's - and the GM wants one per
# clone as an index of THAT clone's work in progress (a render absent from the clone says "not
# rendered", which is the honest state of the clone). Called from sync-in on every turn and after
# every map-drawing target, so the check must be near-free: it is a single `find -newer` over the
# pool's manifests, renders and notes, and the rebuild (~0.5 s) runs only when one of them is newer
# than the index or the index is missing. mtimes, not hashes: no state file to keep, and a false
# "stale" costs half a second while a false "fresh" is impossible (a rewrite always bumps a mtime).
pool-index-if-stale: ## rebuild the pool index only when a manifest, render or notes file is newer
	@if [ ! -f pool/index.html ] || [ -n "$$(find pool legacy-hand-authored-pool -newer pool/index.html \( -name '*.json' -o -name '*.png' -o -name '*.notes.md' \) -print -quit 2>/dev/null)" ]; then \
	  $(MAKE) --no-print-directory pool-index ARGS=; \
	fi
# (GUARD_EDIT_OK: adds a derived-artifact refresh, no gate or prompt is touched - GM 2026-08-27)

compound:       ## draw a Mode A compound plan                ARGS=<out.svg>
	$(RUN).compound $(ARGS)

# RENDER-SYNC IS REFUSAL-ONLY AND NOT SUBJECT TO REFERENCE-FIRST (FR-009a, adjudicated at spec round
# 3). It runs in MAIN's tree during the stop-work procedure, and CLAUDE.md is explicit that render-sync
# is the ONLY thing a session runs there - "no generators, no tests". A reference check ahead of it
# would be a second generator run in main, which that rule forbids. It also re-renders from main's
# committed tip, which is already gate-verified, so the check would re-prove what the clone proved.
render-sync:    ## regenerate MAIN's renders (called by sync-with-main.sh; not for hand use)
	$(RUN).pipeline.render_cache $(ARGS)

# --- cheap: they READ a recorded artifact ----------------------------------------------------
gate-manifest:  ## run the check battery on an existing manifest   M=pool/hamlets/inashiro/inashiro.json
	$(RUN).check_village $(or $(M),pool/hamlets/inashiro/inashiro.json) $(ARGS)

overlap-audit:  ## does A overlap B on a finished map (records AND drawn ink)   M=pool/hamlets/x/x.json [FAMILIES=...]
	$(RUN).tools.overlap_audit $(M) $(if $(FAMILIES),--families $(FAMILIES),)

polder-probe:   ## the polder block ALONE with its geometry metrics, no map   SEED=21 | SEEDS=21,22 ARCHETYPE=...
	$(RUN).tools.polder_probe $(if $(SEED),--seed $(SEED),)$(if $(SEEDS),--seeds $(SEEDS),)$(if $(ARCHETYPE),--archetype $(ARCHETYPE),)$(if $(LAYOUT),--layout $(LAYOUT),)$(if $(HOUSEHOLDS),--households $(HOUSEHOLDS),)

why-placed:     ## who placed this, and what refused to        GEN=... AT=x,y | REFUSED=x,y
	$(RUN).tools.why_placed $(GEN) $(if $(AT),--at $(AT),)$(if $(REFUSED),--refused $(REFUSED),)

site-justice:   ## where can this feature legally go?
	$(RUN).tools.site_justice $(ARGS)

crop:           ## crop a rendered map in manifest coordinates
	$(RUN).tools.crop_map $(ARGS)

jogs:           ## find bunds that step sideways
	$(RUN).tools.jogs $(ARGS)

pack-audit:     ## empty space and geometry in a Mode A compound SVG
	$(RUN).tools.pack_audit $(ARGS)

scatter-audit:  ## is drawn ground cover standing where keep-outs should have stopped it?
	$(RUN).tools.scatter_audit $(ARGS)

notes-census:   ## refresh the derived counts inside each map's notes census block   M="pool/hamlets/*.json"
	$(RUN).tools.notes_census $(or $(M),$(wildcard pool/*/*/*.json) $(wildcard legacy-hand-authored-pool/*/*/*.json))

sun-audit:      ## the sun rules and the belt's page presence, off the manifest   M=pool/hamlets/inashiro/inashiro.json
	$(RUN).tools.sun_audit $(or $(M),pool/hamlets/inashiro/inashiro.json)

family-census:  ## which feature families one manifest records that another does not   A=pool/hamlets/inashiro/inashiro.json B=pool/hamlets/kuwabata/kuwabata.json
	$(RUN).tools.family_census --a $(or $(A),pool/hamlets/inashiro/inashiro.json) --b $(or $(B),pool/hamlets/kuwabata/kuwabata.json)
	@: "(GUARD_EDIT_OK: feature 150 - a read-only manifest census, the measured answer to 'does the converted map carry every reference-hamlet family')"

new-check:      ## scaffold a gate check: segment stub, sorted fixture entry, test stub   NAME=... FILE=segments_*.py TEST=test_segments_*.py
	@test -n "$(NAME)" -a -n "$(FILE)" -a -n "$(TEST)" || { printf 'make new-check NAME=<check_name> FILE=l7r/diagram/check_village/segments_XX.py TEST=tests/check_village/test_segments_XX.py\n'; exit 2; }
	$(RUN).tools.new_check --name $(NAME) --file $(FILE) --test $(TEST)

timings:        ## where the generation loop's time goes
	$(RUN).tools.timings $(ARGS)

citybudget:     ## the city/capital space-budget planner
	$(RUN).citybudget $(ARGS)

# BOTH BOOKENDS ARE ENFORCED HERE, not requested (constitution VI, GM 2026-08-24: "are we now
# actually requiring at the tool level that -start was run at the beginning of a session and -end was
# run before shipping?"). Until today the answer was no, and the cost is on the record: feature 126
# took a `-start`, never took a `-end`, and shipped a +51% generation slowdown that nobody saw for a
# day. `perf-report` even printed "diagnose before shipping" - and exited 0.
#
# So this refuses to let a feature ship without its opening bookend, and takes the closing one
# itself. You cannot forget the second, and you cannot skip the first without the gate saying so.
#
# THE `-start` MAY BE TAKEN RETROACTIVELY, in a detached worktree at the pre-feature commit - that
# is the same tree the Principle XIII regression baseline uses, and it is measuring the same thing.
# What is NOT allowed is shipping with no baseline at all, because then "did this get slower" has no
# answer and the next session inherits the question.
# EVERY GUARD'S TEST COMPANION ACTUALLY RUNS (standing rule, GM 2026-08-24).
#
# The 2026-08-24 enforcement audit found EIGHT hook scripts, EIGHT test companions, and nothing that
# executed any of them. They were decoration by this project's own definition - the one T034 uses:
# a guard whose test does not fail when the guard is removed is not implemented, and a test nothing
# runs cannot fail at all.
#
# Cheap enough to sit in every `make done`: the whole set is seconds, because a hook test feeds JSON
# to a script and reads an exit code. Nothing here rolls a map.
# A GREEN RUN STAMPS THE `hooks` AREA (gate-stamp.py, 2026-08-25 - GUARD_EDIT_OK: adding a gate).
# scripts/*.sh and scripts/*.py are gated code, and this is the gate that covers them; the push-time
# guard refuses a scripts/ change whose stamp is missing or stale, exactly as it refuses engine
# Python without a green `make done`. Motivating case: a RED hooks-test followed by `commit; procedure`
# landed on main, because nothing at push time knew the guards had been edited.
hooks-test:     ## run every scripts/test-*-hooks.sh, and prove each guard still has a companion
	@root=$$(git rev-parse --show-toplevel); gitdir=$$(git rev-parse --absolute-git-dir); fail=""; n=0; skipped=0; \
	: "(GUARD_EDIT_OK: the freshness cache's directory, asked of git instead of assumed - see the note beside its mkdir below; feature 157)"; \
	for h in $$root/scripts/*-hooks.sh $$root/scripts/review-gate.sh $$root/scripts/gate-stamp.py $$root/scripts/sync-with-main.sh; do \
	  : "(GUARD_EDIT_OK: sync-with-main.sh joins the roster - its route decision is a guard, feature 130 T031)"; \
	  b=$$(basename $$h); case $$b in test-*) continue ;; esac; \
	  t=test-$${b%.py}; case $$t in *.sh) ;; *) t=$$t.sh ;; esac; \
	  if [ ! -f "$$root/scripts/$$t" ]; then \
	    printf '\n\033[1mGUARD WITHOUT A TEST: %s has no scripts/%s\033[0m\n' "$$b" "$$t"; \
	    printf 'A guard ships with its companion. Without one, nothing can tell whether it still\n'; \
	    printf 'fires - or whether it fires on correct work, which is the more expensive failure.\n\n'; \
	    fail="$$fail $$b"; continue; \
	  fi; \
	  deps="$$h $$root/scripts/$$t $$root/scripts/_hookmatch.py $$root/scripts/test_hooks_cases.py $$root/scripts/_guardlog.sh $$root/scripts/_gatecost.py"; \
	  : "(GUARD_EDIT_OK: feature 162 - the two new shared helpers join the freshness key, exactly as _hookmatch.py does: a suite that was green against one version of them is not green against another)"; \
	  case $$b in sync-with-main.sh|review-gate.sh|gate-stamp.py) deps="$$root/scripts/*.sh $$root/scripts/*.py";; esac; \
	  : "(GUARD_EDIT_OK: fixing a guard that FIRES ON CORRECT WORK - the per-suite freshness cache resolved its own path as \$$root/.git/hooks-test, and in a LINKED WORKTREE .git is a FILE, so every one of the 19 suites failed with 'Directory nonexistent'. A detached worktree is exactly where constitution XIII requires the regression baseline to be taken, so the mandated procedure could not produce a green hooks-test on ANY commit. Asking git for the path fixes it in both layouts; the roster, the failure path and the stamp are unchanged. Feature 157.)"; \
	  sha=$$(cat $$deps 2>/dev/null | sha256sum | cut -c1-16); mkdir -p "$$gitdir/hooks-test"; \
	  if [ -z "$(HOOKS_ALL)" ] && [ "$$(cat "$$gitdir/hooks-test/$$b" 2>/dev/null)" = "$$sha" ]; then skipped=$$((skipped+1)); continue; fi; \
	  n=$$((n+1)); \
	  "$$root/scripts/$$t" >/tmp/ht.$$$$ 2>&1 && printf '%s' "$$sha" > "$$gitdir/hooks-test/$$b" || { printf '\n\033[1mHOOK TESTS FAILED: %s\033[0m\n' "$$b"; sed 's/^/  /' /tmp/ht.$$$$; fail="$$fail $$b"; }; \
	  rm -f /tmp/ht.$$$$; \
	done; \
	if [ -n "$$fail" ]; then printf '\n\033[1mhooks-test FAILED:%s\033[0m\n\n' "$$fail"; exit 1; fi; \
	python3 "$$root/scripts/gate-stamp.py" --write hooks; \
	printf 'hooks-test: %s guard suites green, %s unchanged since they last went green (hooks area stamped)\n' "$$n" "$$skipped"
# PER-SUITE FRESHNESS (feature 135, third pass; GUARD_EDIT_OK: the roster and the failure path are unchanged - a suite
# is SKIPPED only when its guard, its test and the shared helpers (`_hookmatch.py`, `test_hooks_cases.py`; for the
# three suites that drive other scripts, all of scripts/) hash to what they hashed when the suite last went GREEN in
# this clone (.git/hooks-test/<guard>). Measured: 90 s to re-run all 13 suites for a one-line edit to one guard;
# `HOOKS_ALL=1` runs every suite regardless. The whole-area stamp (`gate-stamp --write hooks`) is written only when
# every suite is green, exactly as before.
# (GUARD_EDIT_OK: adds gate-stamp.py to the guard roster with a .sh companion, and stamps the hooks area on green)

perf-gate:      ## require the feature's -start bookend, take -end, and FAIL on a regression
	$(SWEEP_OK)
	@: "(GUARD_EDIT_OK: feature 132 - a perf snapshot rolls several seeds, a sweep under the scope lock)"; \
	f="$(or $(FEATURE),$(SPECIFY_FEATURE))"; \
	if [ -z "$$f" ] && [ -f ../../../.specify/feature.json ]; then \
	  f=$$(python3 -c "import json;print(json.load(open('../../../.specify/feature.json'))['feature_directory'].split('/')[-1])" 2>/dev/null); \
	fi; \
	n=$$(printf '%s' "$$f" | grep -oE '^[0-9]+' || true); \
	if [ -z "$$n" ]; then \
	  printf '\n\033[1mPERF GATE: cannot tell which feature this is.\033[0m\n'; \
	  printf 'Set SPECIFY_FEATURE=NNN-slug (spec-kit work) or FEATURE=NNN, so the bookends can be paired.\n\n'; \
	  exit 1; \
	fi; \
	if [ -n "$$CODEBUILD_BUILD_ID" ] && ! ls dev/perf-log/*"$$n"-start*codebuild*.json >/dev/null 2>&1; then \
	  printf '\n\033[1mPERF GATE (in-build): taking the %s-start bookend on the pre-merge main, in a detached worktree.\033[0m\n' "$$n"; \
	  git worktree add -q --detach /tmp/base"$$n" origin/main && ( cd /tmp/base"$$n"/.claude/skills/diagram && $(MAKE) --no-print-directory perf LABEL="$$n-start" ) && cp /tmp/base"$$n"/.claude/skills/diagram/dev/perf-log/*"$$n-start"*.json dev/perf-log/ || exit 1; \
	fi; \
	if ! ls dev/perf-log/*"$$n"-start*.json >/dev/null 2>&1; then \
	  printf '\n\033[1mPERF GATE: no %s-start bookend exists, so a regression cannot be measured.\033[0m\n\n' "$$n"; \
	  printf '(GUARD_EDIT_OK: inside a CodeBuild build both bookends are taken in-run - feature 130, FR-028)\n' >/dev/null; \
	  printf 'Constitution VI wants it taken on UNMODIFIED code, before the first edit. Retroactively is\n'; \
	  printf 'fine and is what the regression baseline already does - take it in a detached worktree at\n'; \
	  printf 'the pre-feature commit:\n\n'; \
	  printf '  git worktree add --detach /tmp/base%s <pre-feature-commit>\n' "$$n"; \
	  printf '  ( cd /tmp/base%s/.claude/skills/diagram && make perf LABEL=%s-start )\n' "$$n" "$$n"; \
	  printf '  cp /tmp/base%s/.claude/skills/diagram/dev/perf-log/*%s-start*.json dev/perf-log/\n\n' "$$n" "$$n"; \
	  printf 'What is NOT allowed is shipping with no baseline: "did this get slower" then has no answer,\n'; \
	  printf 'and feature 126 shipped a +51%% slowdown exactly that way.\n\n'; \
	  exit 1; \
	fi; \
	$(MAKE) --no-print-directory perf LABEL="$$n-end" >/dev/null; \
	$(MAKE) --no-print-directory perf-report AGAINST="$$n-start"

# (GUARD_EDIT_OK: the audit gains "Remote spend" - feature 130, FR-020)
audit:          ## how the gate has actually been used - every run, every bypass, and remote spend
	@python3 -m l7r.diagram.ci remote-spend
# GUARD_EDIT_OK: feature 162 - FIXING A DEFECT FOUND WHILE WORKING (Principle XIV). `make audit` died
# with a KeyError on any bypass entry written by `pair-hooks.sh`, which records `guard`/`reason`/`what`
# rather than `outcome`/`why` (feature 151, 2026-08-29). 63 of the 88 entries in this clone carry that
# schema, so the audit the constitution requires as a feature's closing step has been unrunnable since
# the day pair-hooks landed - and it failed AFTER printing the run log, which is why it read as a
# normal tail of output. Both schemas are read now; neither is rewritten.
	@python3 -c "import json,glob,collections,os; \
rows=sorted((json.load(open(f)) for f in glob.glob('dev/run-log/*.json')),key=lambda r:r.get('utc','')); \
print(chr(10)+'\033[1mGate runs\033[0m (dev/run-log/)'); \
[print(f\"  {r['utc']}  {r['scope']:<9} {r['seconds']:>4}s  {r['result']:<22} {r['commit']}\") for r in rows[-25:]] or print('  (none yet)'); \
c=collections.Counter(r['scope'] for r in rows); \
print(f\"  {len(rows)} runs: \"+', '.join(f'{k}={v}' for k,v in sorted(c.items()))) if rows else None; \
b=sorted((json.load(open(f)) for f in glob.glob('dev/bypass-log/*.json')),key=lambda r:r.get('utc','')); \
print(chr(10)+'\033[1mBypasses\033[0m (dev/bypass-log/) - a FULL run is only justified at the END of a feature'); \
'GUARD_EDIT_OK: feature 162 - read BOTH bypass-log schemas (see the note above this recipe)'; \
[print(f\"  {r['utc']}  {(r.get('outcome') or r.get('guard') or '?'):<10} {(r.get('why') or r.get('reason') or r.get('what') or '')[:76]}\") for r in b[-15:]] or print('  (none yet)'); \
print()"
# GUARD_EDIT_OK: feature 162 adds the GUARD CENSUS to this audit (GM 2026-08-30: *"I notice I've been
# seeing a lot of this in the output of my claude code sessions over time"*). Answering that took a
# replay of 715 MB of transcripts, because no guard recorded when it fired. Now two of them do, and
# the escape rate is the number that matters: a guard escaped more often than it is obeyed is costing
# a round trip to prevent nothing, which is what retired the quick+done refusal.
	@python3 -c "import json,glob,os,collections; \
rows=[json.load(open(f)) for f in glob.glob(os.path.expanduser(os.environ.get('GUARD_LOG_DIR','~/.claude/guard-log')+'/*.json'))]; \
print('\033[1mGuard firings\033[0m (~/.claude/guard-log/) - what each guard did: blocked, rewrote, reminded, escaped'); \
by=collections.defaultdict(collections.Counter); \
[by[r['guard']].update([r['event']]) for r in rows]; \
[print(f\"  {g:<8} \"+', '.join(f'{k}={v}' for k,v in sorted(c.items()))+(f\"   escape rate {c['escaped']/max(1,c['escaped']+c['blocked']):.0%}\" if c['blocked'] or c['escaped'] else '')) for g,c in sorted(by.items())] or print('  (none recorded yet)'); \
print(f\"  {len(rows)} entries\"+(f\", {min(r['utc'] for r in rows)} to {max(r['utc'] for r in rows)}\" if rows else '')); \
print()"
	@printf '\033[1mFiles past the ~1,000-line bar\033[0m (constitution X clause 13 - a QUESTION, not a limit)\n'
	@find l7r tests -name '*.py' -exec wc -l {} + 2>/dev/null | awk '$$1>1000 && $$2!="total"{printf "  %5d  %s\n",$$1,$$2}' | sort -rn | head -12
	@printf '  Each asks: should this become a package of subfiles with its own CLAUDE.md index? An\n'
	@printf '  ordered-data REGISTRY may stay large with an inline justification - the only carve-out,\n'
	@printf '  and it protects rows stating real DECISIONS, never a roster derived from code elsewhere.\n'
	@printf '  Reported rather than gated on purpose: five files already exceed it and the rule prompts\n'
	@printf '  a question rather than forbidding a size.\n\n'

help:           ## list every target with its one-line purpose
	@printf '\n\033[1mOperations\033[0m - everything runs through one of these.\n\n'
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort | awk -F'\t' '{printf "  \033[1m%-18s\033[0m %s\n", $$1, $$2}'
# GUARD_EDIT_OK: feature 162 - the help line stops quoting durations typed in by hand (GM 2026-08-30:
# *"those numbers for `make quick` are wrong and outdated"*; this line still said done ~5.5min while
# the run log's median was 137 s). The one number worth printing is asked of the recorded runs.
	@cost=$$(../../../scripts/_gatecost.py done 2>/dev/null); \
	 printf '\nCheapest first: quick | reference | done (NOT the quick one) | done FULL=1'; \
	 [ -n "$$cost" ] && printf '   -   `make done` median %s s over its recent recorded runs (`make audit`)' "$$cost"; \
	 printf '\n'
	@printf 'Remote (paid, CodeBuild): ci-status (free) | ci-check [FULL=1|TARGET=op] | ci-merge (the push) | ci-image - see dev/loop.md\n\n'

# ---- THE CODEBUILD TARGETS (feature 130 - GUARD_EDIT_OK: adding four new PAID operations) -------
# Every remote run is PAID, so these are the most guarded operations in the repository. The
# dispatcher (l7r/diagram/ci/) checks five conditions locally before any AWS call, runs lint and the
# reference settlement locally with the build parked in parallel, and refuses a re-dispatch after a
# failed gate until a local check is green. `ci-merge` is the push's gated route and is called by
# scripts/sync-with-main.sh - never by hand. `ci-status` is the free "why won't it dispatch".
ci-status:      ## free: delta, route, verification state, verified lookup, remote spend   ROUTE=1 -> just DIRECT|GATED
	$(RUN).ci status $(if $(ROUTE),--route,)
# the verification key of a tree - the build records a green gate under it (GUARD_EDIT_OK: feature 130, keyed by engine content since 2026-08-25)
engine-key:
	@$(RUN).ci engine-key $(or $(REF),HEAD)

ci-check:       ## the iteration check on CodeBuild (PAID)     FULL=1 (prompts) | TARGET=cohort etc. | NO_GO=1 (FR-036 self-abort proof)
	$(REMOTE_OK)
	@$(if $(FULL)$(TARGET),$(SWITCH) check scope "ci-check $(if $(FULL),FULL=1,TARGET=$(TARGET))",true)
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
# (GUARD_EDIT_OK: feature 132 - remote off refuses every ci-check before any AWS call; FULL and TARGET are sweeps under the scope lock)
	$(RUN).ci check $(if $(FULL),--full,) $(if $(TARGET),--target "$(TARGET)",) $(if $(NO_GO),--no-go,) $(if $(COMPUTE),--compute "$(COMPUTE)",)
# (GUARD_EDIT_OK: NO_GO=1 is the FR-036 measurement - the build must abort itself when nobody releases it; feature 130 T076.
#  COMPUTE=BUILD_GENERAL1_2XLARGE is the T028 scaling measurement the GM asked for on 2026-08-25; the default stays xlarge)

ci-merge:       ## the merge action's gated route (PAID) - called by sync-with-main.sh push   FULL=1 (prompts)
	@$(if $(FULL),$(SWITCH) check scope "ci-merge FULL=1",true)
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
# (GUARD_EDIT_OK: feature 132 - FULL is a sweep under the scope lock. Remote-off is NOT checked here: the dispatcher
#  handles it itself, because with remote off it must still produce the LOCAL-GATED verdict the push procedure reads)
	$(RUN).ci merge $(if $(FULL),--full,)

# the operator's `permitted` answer becomes a commit, so the build finds it in the tree it tests (FR-025)
commit-permitted:
	@f=$$(ls -t dev/bypass-log/*.json | head -1); why=$$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['why'][:60])" "$$f"); \
	git add dev/bypass-log && git commit -q -m "chore: authorize FULL sweep - $$why" && echo "committed $$f ($$why)"

ci-image:       ## rebuild the CodeBuild image from Dockerfile.ci and push it to ECR (PAID, ~$$1; prompts)
	$(REMOTE_OK)
	@: "(GUARD_EDIT_OK: feature 132 - remote off refuses the image rebuild before the prompt)"; \
	if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: ci-image is a paid operation and its prompt needs a terminal.\033[0m Run it in the foreground.\n\n'; $(LOGBYPASS) refused "ci-image with no terminal"; exit 1; fi; \
	printf '\n\033[1mAbout to rebuild the CodeBuild image on AWS\033[0m (~$$1, a few minutes). Needed only when\n'; \
	printf 'setup-dev-env.sh, Dockerfile.ci or a lockfile changed. Press Enter to CANCEL.\n\nReason to continue (Enter cancels): '; \
	if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: this prompt has no terminal to answer it\033[0m - a backgrounded or piped run cannot be asked; run it in the foreground, or use the target that does not prompt.\n\n'; exit 1; fi; read why || true; \
	if [ -z "$$why" ]; then $(LOGBYPASS) cancelled "(ci-image backed out at the prompt)"; printf 'Cancelled.\n'; exit 1; fi; \
	$(LOGBYPASS) permitted "$$why"; git add dev/bypass-log; git commit -q -m "chore: authorize image rebuild - $$why" || true
	$(RUN).ci image


# THE LOG RECORDS WHAT HAPPENED, NOT ONLY WHAT WAS ALLOWED (FR-012). Without `outcome`, a session
# that read the warning and backed out is indistinguishable from one that never tried - so the log
# cannot answer the question it exists for. The GM's own use for it: a rising count of `cancelled`
# is the early signal that the cheap path has stopped being sufficient, at which point the answer is
# to make the fast path better rather than to keep refusing.
#
# The 2026-08-24 audit of the pre-guard entries found 3 of 5 unjustified, and the log had recorded
# all five and stopped none - an audit trail records a decision, it does not make one.
# NO LEADING `@`: that is a make RECIPE PREFIX, meaningful only at the start of a line. Expanded
# mid-recipe it is a literal character and the shell tries to run `@python3`, so the first version
# logged nothing at all while every other part of the prompt behaved correctly - a silent failure in
# the one component whose entire job is to leave a record.
# EVERY GATE RUN IS LOGGED, not only the bypassed ones (GM 2026-08-24): *"if there exists a make done
# that can be run in order to run the full tests, do we still have the ability to audit that it is
# only being run when we have fully completed a feature? ... not just confirming that in the moment,
# but also being able to audit after the fact."*
#
# The honest answer was no. `dev/bypass-log.jsonl` recorded FULL=1 attempts and nothing else, so
# there was no way to ask afterwards how often the 5-minute gate ran or whether each run was near a
# push. That matters here more than most places: the measured cost of getting this wrong, over three
# days, is hours - and the pattern that cost them was a session running the long gate repeatedly
# while believing each run was justified.
#
# `make audit` reads it back. Elapsed time is recorded too, so a target that has quietly got slower
# shows up in the history rather than in someone's memory.
LOGRUN = python3 -c "import json,os,subprocess,sys,time; \
  h=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip(); \
  ts=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'%06d'%(time.time_ns()//1000%1000000); \
  os.makedirs('dev/run-log',exist_ok=True); \
  open(f'dev/run-log/{ts}-{os.getpid()}.json','w').write(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'target':sys.argv[1],'scope':sys.argv[2],'seconds':int(sys.argv[3]),'result':sys.argv[4],'commit':h},indent=2)+chr(10))"

# THE TARGET RECORDS THE SCOPE (feature 130 - GUARD_EDIT_OK: the build-side door keys on it). `done`
# with FULL=1 logs as `done FULL`, `ci-merge FULL=1` as `ci-merge FULL`: the entry is what the build
# reads to decide whether the full scope was authorized, and "done" alone could not say.
LOGBYPASS = python3 -c "import json,os,subprocess,sys,time; \
  h=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip(); \
  ts=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'%06d'%(time.time_ns()//1000%1000000); \
  os.makedirs('dev/bypass-log',exist_ok=True); \
  open(f'dev/bypass-log/{ts}-{os.getpid()}.json','w').write(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'target':'$(MAKECMDGOALS)$(if $(FULL), FULL,)','commit':h,'outcome':sys.argv[1],'why':sys.argv[2]},indent=2)+chr(10))"

QUICK_BUDGET = 60

# WHERE THE SUITE'S TIME GOES. Exists because the question could not be asked any other way once
# bare pytest was gated: a session needing to know why a target is slow had no route to the answer
# except the override, which is precisely the shape that trains a session to reach for overrides.
# A gate that blocks a legitimate question without providing the route is a gate that gets bypassed.
#
# N=<count> for a longer list; MARK=rolls_map to profile the map-rolling tests instead.
# ONE TEST FILE, WHOLE. Deliberately takes a FILE and not a `-k` expression: the project's own rule
# is to run the whole affected file, because a filter selects the tests you were thinking about and a
# change breaks the ones you were not (scripts/gate-hooks.sh enforces the same thing against the
# gate). Exists because gating bare pytest left "re-run the file I just changed" with no route, and a
# guard that blocks a legitimate action without offering the alternative is one that gets worked
# around - the same gap `make durations` filled for "why is this slow".
# (GUARD_EDIT_OK: a green test-file records green-local - feature 130, FR-012)
tooling:        ## run every `tooling` test (make/ci/pipeline, exhaustive) and record them green so `make quick` skips them until the tooling changes
	@$(GATE_EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) -q --no-cov -m tooling && python3 -m l7r.diagram.ci tooling-green

test-file:      ## run ONE test file, whole              FILE=tests/pipeline/test_gencache.py
	@python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal -q --no-cov $(FILE) && $(STATE) green-local test-file

# WHICH LINES DOES THIS TEST ACTUALLY REACH? (feature 146, and it is an ITERATION-LOOP target rather than a
# gate one - CLAUDE.md, "iterations are expensive in terms of wall clock time"). Writing a test for an
# uncovered branch and then finding out from `make test-full` costs 10 minutes per answer, and the answer is
# routinely "you covered the guard ABOVE the one you were aiming at" - measured on this feature: two full
# runs spent discovering that `_in_blocked` had already refused the seat the byre and garden tests meant to
# have refused one line further down. This asks the same question in about a second. Serial (-n0) on purpose:
# xdist's coverage combine is the slow half, and one file does not need workers.
cov-file:       ## which lines of MOD does ONE test file reach?   FILE=tests/settlement/test_houses.py MOD=l7r/diagram/settlement/houses.py
	@python3 -m pytest -n0 -q --no-header -p no:cacheprovider --cov=$(MOD) --cov-report=term-missing $(FILE)
# (worksteal, feature 135: two 50 s rollers landing on one worker under the default scheduler doubled a file's wall clock)

# WHY EVERY CHECK FAILED ON THE REFERENCE MAP, in detail rather than by name.
#
# `make reference` prints the failing check NAMES, which is the right amount when you want a verdict.
# It is not enough when the reference map is the thing you are operating on - and at that moment
# every other target refuses to run, because they all check the reference map first and it is red.
# The REF_OK escape exists for exactly that case and is itself refused by the command-shape hook, so
# a session mid-surgery had NO route to the detail at all.
#
# Third time in one feature that a guard blocked a legitimate question without providing an
# alternative (after `make durations` and `make test-file`), and the answer is the same each time:
# supply the route. A gate that blocks a question you are entitled to ask is a gate that gets
# bypassed.
#
# Deliberately NOT reference-first: it IS the reference map, and gating it behind itself is the
# circularity this target exists to break.
explain:        ## why a map is failing - every check with its message.   SEED=27 for a cohort seed
	@SEED=$(or $(SEED),4) python3 .explain.py

durations:
	@python3 -m pytest -n $(XDIST_WORKERS) -q --no-cov $(if $(FULL),,--ignore=tests/full) $(if $(MARK),-m "$(MARK)",-m "not rolls_map") --durations=$(or $(N),12) 2>&1 | grep -E "^[0-9.]+s (call|setup)|passed|failed" | head -$$(( $(or $(N),12) + 2 ))
# (FULL=1 profiles the full tree too; the coverage carriers live there now, so `coverage_only` no longer needs deselecting - feature 135)

quick:
	@python3 -m ruff check --fix l7r/ tests/ && python3 -m ruff format l7r/ tests/ && $(TYPECHECK)
	@start=$$(date +%s); $(EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal $(TESTMON) -q --no-cov -x --ff -m "not rolls_map" $(TIER_SELECT) $(QUICK_TREE); ec=$$?; \
	  el=$$(( $$(date +%s) - start )); \
	  if [ $$ec -ne 0 ]; then exit $$ec; fi; \
	  if [ $$el -gt $(QUICK_BUDGET) ]; then \
	    printf '\n\033[1mquick took %ss, over its %ss budget.\033[0m\n' "$$el" "$(QUICK_BUDGET)"; \
	    printf 'Something slow is running that should not be. Find it:  \033[1mmake durations\033[0m\n'; \
	    printf 'A test near the top of that list without @pytest.mark.rolls_map is the cause.\n\n'; \
	    exit 1; \
	  fi
	@printf '\n\033[1mquick: clean\033[0m - the %s map-rolling tests were NOT run; `make done` before pushing.\n' "$$(grep -rho --include='*.py' '@pytest.mark.rolls_map' tests | wc -l)"
# (the count used to come from a SECOND pytest collection of the whole suite, ~2 s of every quick - GM 2026-08-26, T25)
	@$(STATE) green-local quick
# (GUARD_EDIT_OK: a green quick records green-local - feature 130, FR-012)

# THE BUILD-SIDE DOOR (feature 130, FR-025, research R11 - GUARD_EDIT_OK: a second door that opens
# only to a COMMITTED answer). Inside a CodeBuild build there is no terminal to answer the prompt,
# and the answer must not come from an environment variable (the tier-2 override with extra steps).
# So the build accepts the full scope only if the tree it tests carries a `permitted` entry in
# dev/bypass-log/ whose commit is an ancestor of HEAD and NOT of origin/main - the operator's
# answer at the LOCAL prompt, committed by `commit-permitted` and shipped with the work. Locally,
# with CODEBUILD_BUILD_ID unset, every line below behaves exactly as before (FR-026).
bypass-audit:
	@if [ -n "$$CODEBUILD_BUILD_ID" ]; then python3 -m l7r.diagram.ci door && exit 0; printf '\n\033[1mREFUSED: the FULL scope in a build needs the committed answer to the local prompt.\033[0m\n\n'; exit 1; fi; \
	why="$(REF_WHY)"; \
	if [ -n "$$why" ] && [ ! -t 0 ]; then \
	  printf "\n\033[1mREFUSED: a FULL run with REF_WHY set, with nothing attached to answer for it.\033[0m\n\n"; \
	  printf "The prompt below exists because its default answer is NO. Passing REF_WHY on the\n"; \
	  printf "command line skips it, and a backgrounded run cannot be asked to reconsider - which is\n"; \
	  printf "exactly how feature 126 ran the full gate THREE times against a standing instruction to\n"; \
	  printf "run only the reference settlement. Every bypass was logged and none was stopped.\n\n"; \
	  printf "  \033[1mmake reference\033[0m   Inashiro seed 4 alone, ~60 s - almost always what you want\n"; \
	  printf "  \033[1mmake done\033[0m        reference + lint/types + the suite (NOT the quick one)\n\n"; \
	  : "(GUARD_EDIT_OK: feature 162 - the prompt stops quoting a hand-typed 5.5 min; make audit has the real history)"; \
	  printf "If you truly need the FULL set, run it in the FOREGROUND and answer the prompt.\n\n"; \
	  $(LOGBYPASS) refused "$$why"; \
	  exit 1; \
	fi; \
	if [ -z "$$why" ]; then \
	  printf '\n\033[1mAbout to run the FULL test set.\033[0m\n\n'; \
	  printf 'The reference settlement rebuilds in ~60 s. The full set additionally rolls every\n'; \
	  printf 'live pool map, re-gates each, and rolls seeds 41-44 - minutes, not seconds.\n\n'; \
	  printf '\033[1mMost of the time the right answer here is to back out.\033[0m Press Enter to CANCEL\n'; \
	  printf 'and run the reference-scope gate instead - that is the default and it is usually right.\n\n'; \
	  printf 'Legitimate reasons to continue: the reference map is itself under surgery and expected\n'; \
	  printf 'to fail; you are bisecting a knowingly-red tree; the subject is a check that only fires\n'; \
	  printf 'on a non-reference map; you are about to push and need the full pre-push verdict.\n'; \
	  printf 'Not legitimate: wanting to see everything, impatience, or "while I am here".\n\n'; \
	  printf 'Reason to continue (Enter cancels): '; \
	  if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: this prompt has no terminal to answer it\033[0m - a backgrounded or piped run cannot be asked; run it in the foreground, or use the target that does not prompt.\n\n'; exit 1; fi; read why || true; \
	fi; \
	if [ -z "$$why" ]; then \
	  $(LOGBYPASS) cancelled "(no reason given - backed out at the prompt)"; \
	  printf '\n\033[1mCancelled - good call.\033[0m Nothing expensive ran.\n'; \
	  printf 'Run `make done` on its own for the reference-scope gate.\n\n'; \
	  exit 1; \
	fi; \
	mkdir -p dev; \
	$(LOGBYPASS) permitted "$$why"; \
	printf '\nlogged to dev/bypass-log/ - proceeding\n\n'
# (GUARD_EDIT_OK: the message named a file that does not exist - the log is a directory; feature 130 T073, Principle XIV)

reference:
	@python3 -c "import sys; sys.path.insert(0, '.'); 	from l7r.diagram import hamletgen as hg; 	from l7r.diagram.pipeline import rollcache; 	r, how = rollcache.report(hg.HamletSpec(name='Inashiro', seed=4, households=15, down_deg=90, water_sink='pond')); 	print('\033[1mreference settlement (Inashiro, seed 4): ' + ('CLEAN\033[0m' if r.ok else 'FAILING\033[0m -> ' + ', '.join(r.failures)) + ' [' + how + (' - served from the roll cache: nothing the roll executes changed; GATE_NO_CACHE=1 rolls it' if how == 'HIT' else '') + ']'); 	sys.exit(0 if r.ok else 1)" || { 	  printf '\n\033[1mSTOPPING HERE.\033[0m The reference settlement is red, so nothing more expensive runs.\n'; 	  printf 'Fix Inashiro first - it rebuilds in about a minute. Everything else is 4x to 25x that,\n'; 	  printf 'and none of it can tell you anything useful while the one map you iterate on is broken.\n'; 	  printf 'To REGENERATE it and read every failure in full: \033[1mmake maps\033[0m (reference only under the lock).\n'; \
	  printf 'Do not reach for REF_OK=1 - it prompts, and a prompt with no terminal is refused.\n\n'; exit 1; }
	@$(STATE) green-local reference
# (GUARD_EDIT_OK: a green reference records green-local - feature 130, FR-012)

# THE IDLE RUN (feature 136, D1 - GUARD_EDIT_OK: a new target, the one an idle session's detached timer runs;
# the GM: "a test which is relatively expensive in terms of me having to wait for it time becomes very cheap
# because it is largely going to run unattended"). One target so the GM can change WHAT an idle session
# runs in one place. It is `maps`: the reference map, the tripwire seeds, the tier sweep - under an
# unlocked scope; under the lock, the reference alone (the lock admits no override, D1b). It writes no
# `done` stamp under the idle run's own name (`idle-done`, DONE_NAME below), so it neither grants nor revokes a
# push (FR-006b c). The GM (2026-08-28): "I do want it to be more than just the reference map tests. I do not
# want to run the full test suite, which is to say the one that we reserve for AWS. However, I would like to
# run the lengthier test suite" - so it is `done` (the 21-minute unlocked gate), never `done FULL=1`, and the
# scope lock is RELAXED for it by `switches.read` when the caller descends from the timer. Never by hand.
IDLE_CTX = $(shell $(SWITCH) idle 2>/dev/null)
DONE_NAME = $(if $(filter 1,$(IDLE_CTX)),idle-done,done)
idle-tests:     ## what an idle session runs unattended (feature 136): the whole gate, scope relaxed, never FULL
# THE PAIRING'S ONE-SIDED CASE, TAKEN RATHER THAN CARVED OUT (feature 151): a detached timer has no
# session to dispatch a settlement-review from, so it supplies the override with its reason and the
# bypass log carries it like any other. An exemption inside the guard is the shape the spec review struck.
	@PAIR_OK="idle run: no session attached to dispatch a review" $(MAKE) --no-print-directory done

maps:
	@$(if $(filter all,$(SCOPE)),$(SWITCH) check scope "maps SCOPE=all",true)
	@python3 -m l7r.diagram.tools.mapcheck
	@$(MAKE) --no-print-directory pool-index-if-stale
# (GUARD_EDIT_OK: feature 132 - `maps SCOPE=all` is refused under the lock; mapcheck itself never widens while locked)

perf:
	$(SWEEP_OK)
	@python3 -m l7r.diagram.tools.perf_snapshot --record --label "$(or $(LABEL),adhoc)"

perf-report:
	@python3 -m l7r.diagram.tools.perf_snapshot --report $(if $(AGAINST),--against $(AGAINST),)

# Refuse to run from the MAIN tree (CLAUDE.md "Session clones": main is the integration point,
# never a workspace - work runs in .clones/<session-name>). Every target depends on this. GM
# override for a deliberate main-tree run: GM_ASSISTANT_ALLOW_MAIN=1.
# MAIN IS THE TREE THAT CONTAINS `.clones/` (feature 131, 2026-08-25 - GUARD_EDIT_OK: the split
# needs one Makefile that works at /gm-assistant and at /diagram). A clone or a detached worktree
# has no .clones/ of its own (it is gitignored), so the rule is: refuse when the git top level of
# the cwd holds a .clones/ directory and the cwd is not itself inside one. No path is hardcoded.
guard:
	@top=$$(git rev-parse --show-toplevel 2>/dev/null); \
	case "$(CURDIR)" in */.clones/*) exit 0 ;; esac; \
	if [ -n "$$top" ] && [ -d "$$top/.clones" ] && [ "$$GM_ASSISTANT_ALLOW_MAIN" != 1 ]; then \
	    echo "ERROR: this ran from the MAIN tree ($$top). Main is the integration point, never a workspace."; \
	    echo "Check CLAUDE.md, section 'Session clones' (reload CLAUDE.md if it has fallen out of your context"; \
	    echo "window): create or reuse .clones/<kebab-cased-session-name>, sync it in with 'git pull origin main',"; \
	    echo "and run this same command from inside that clone. (GM override: GM_ASSISTANT_ALLOW_MAIN=1)"; \
	    exit 1; \
	fi

lint format typecheck test: | guard

# LINT AND FORMAT AUTOCORRECT, THEY DO NOT FAIL (GM 2026-08-26: *"having linters autocorrect everything is a
# standard practice ... having every run of the linter simply fix linting errors rather than failing on them
# seems like it is what we want"*). Three of one day's red gates were import order and formatting - each a
# 75 s gate plus a model turn spent on something with no decision in it. `ruff check --fix` applies every
# safe fix and still exits non-zero on what it cannot fix (a real finding); `ruff format` rewrites in place
# (black-compatible; the gate key is semantic, so a reformat never re-opens it).
lint:
	python3 -m ruff check --fix .
	python3 ../../../scripts/check-duplicate-defs.py --selftest
	python3 ../../../scripts/check-duplicate-defs.py ../../..

format:
	python3 -m ruff format .

typecheck:
	$(TYPECHECK)

# parallel across cores when pytest-xdist is installed (~1 min vs ~5 min serial, measured
# 2026-07-20 on 22 cores), plain serial pytest otherwise - xdist is a speedup, not a requirement.
# The coverage gate combines worker data, so the coverage requirement holds either way.
#
# COVERAGE IS ENFORCED PER-MODULE since the 2026-08-16 legacy freeze (migration-plan.md "The
# accepted trade"): the hand-authored pool maps are frozen and their gens never run, so the
# above-hamlet wings of settlement.py (towns, cities, the capital) are exercised by nothing until
# those tiers convert to scripted generation. Every other measured module holds 100%; settlement.py
# holds a RATCHET floor - the same discipline as the retired mypy per-module ratchet. RAISE the
# floor as each tier converts (village -> town -> city re-cover their wings); NEVER lower it.
# 94 = measured 94.4% (447 of 8043 statements unreached) on 2026-08-16, the day of the freeze:
# the scripted hamlets + unit tests already reach everything but the town/city/capital wings.
SETTLEMENT_COV_FLOOR = 94

# The `coverage combine --append` below sweeps in the gate-cache parallel data files (hit replays
# and miss-subprocess recordings, feature 026) that pytest-cov's own end-of-session combine may or
# may not have consumed already - the explicit combine is deterministic either way, and a no-op
# when there is nothing left to merge.
# THE FULL TREE (feature 135, GM 2026-08-27: "one directory for our quick tests, one directory for our done
# tests, and one directory for our lengthy AWS tests ... the directory into which we added is the thing that
# inherently determines When and under what circumstance that test is run"). `tests/full/` holds the pool
# sweep, the seed sweeps, the coverage carriers and the real-map cache round trip; the gate does not COLLECT
# it, `test-full` does. This replaces the deselect LIST that used to name two files - and had gone stale: it
# still named `tests/hamletgen/test_driver.py` after 133 T29 moved the cohort ratchet to `tests/gate/`, so the
# FULL-only "seeds 41-44 ratchet" ran in every unlocked reference gate and seven cheap tests in the old file
# were silenced (research R6). A tree cannot go stale that way. `L7R_TESTS_FULL=1` tells the conftest it is
# the full run (the tooling tests then never skip - the ci package owes its 100% there).
FULL_TREE_IGNORE = $(if $(COV_FLOORS),,--ignore=tests/full)
FULL_ENV = $(if $(COV_FLOORS),L7R_TESTS_FULL=1,)
# COVERAGE FOLLOWS THE DIFF at reference scope (feature 135, second pass; the why is on `delta.coverage_scope`):
# the gate traces only the engine modules the diff touched - `uncovered-in-diff.py` needs no more - and nothing
# when none changed; measured 9 s of a 25 s locked gate. FULL traces everything (the floors). An empty answer
# (no git, an error) leaves pytest's own addopts in force, i.e. full tracing - the safe direction.
COV_SCOPE = $(if $(COV_FLOORS),,$(shell python3 -m l7r.diagram.ci cov-scope 2>/dev/null))
# THE LOCK DEFERS THE MAP-ROLLING TESTS TOO (GM 2026-08-26, feature 133 T11). Measured that day: under
# `scope reference`, `make done`'s pytest phase took 233 s of a 4.5 min gate, and the time was the
# `rolls_map` tests - a 48-seed cohort, polder hamlets, the real pool through the gen cache - i.e. maps
# other than the reference, rolled through the suite the lock was meant to stop ("no invocation rolls a
# map other than the reference settlement"). So while the scope is locked the `test` phase deselects
# `rolls_map`, and the record it writes carries the scope: `already_verified` refuses it once the lock is
# released, so the first `make done` after `scope-unlock` runs them - owed at unlock, exactly like the
# sweeps and the perf bookends. Never under COV_FLOORS (test-full is refused under the lock anyway).
# Alternatives priced: keep running them (four minutes per cycle spent on maps the period says not to
# roll); deselect only the NON-reference rollers (no marker tells them apart, and the reference map is
# already rolled by `make reference` in the same gate). The reference-rolling tests are covered at unlock.
SCOPE_STATE = $(shell $(SWITCH) state scope 2>/dev/null)
ROLL_DESELECT = $(if $(COV_FLOORS),,$(if $(filter reference,$(SCOPE_STATE)),-m "not rolls_map",))
# TIER RELEVANCE (GM 2026-08-26, feature 133 T17): the reference settlement is a hamlet, so while scope is
# locked the suite skips tests tagged for other tiers only (`tiers` marker, tests/conftest.py). The tier is
# named here, once; never under COV_FLOORS.
REFERENCE_TIER = hamlet
# WORKERS: 8 ON A SHARED BOX, EVERY CORE ON CODEBUILD (GM 2026-08-26, T23). Measured on the 22-core dev
# container: the quick set is as fast on 8 workers as on 22 (9.9 vs 10.1 s - each worker costs ~0.17 s to
# spawn and collect, and past 8 that buys back the parallel gain), while the GM runs several sessions at
# once on the laptop, so flooding every core only slows the others. CodeBuild is dedicated to the run, so
# it takes `auto` (36 vCPU on the xlarge). CODEBUILD_BUILD_ID is set in every CodeBuild build and nowhere
# else - the inverse of "is this the laptop", and it needs no hostname.
# ...and never more workers than the box has cores (GM 2026-08-26: "I wouldn't want to run eight workers on a
# machine that only has four cores") - min(8, nproc). CPU_COUNT is overridable so the small-box branch is testable.
CPU_COUNT ?= $(shell nproc 2>/dev/null || echo 8)
XDIST_WORKERS = $(if $(CODEBUILD_BUILD_ID),auto,$(shell [ "$(CPU_COUNT)" -lt 8 ] && echo "$(CPU_COUNT)" || echo 8))
# EXHAUSTIVE=1 (GM 2026-08-26, T19): tests that sweep seeds / kinds / cardinals run the FULL sweep instead of
# their documented quick subset (tests/_scope.py). `make quick EXHAUSTIVE=1`; `make done EXHAUSTIVE=1`.
EXHAUSTIVE_ENV = $(if $(EXHAUSTIVE),L7R_TESTS_EXHAUSTIVE=1,)
# CHANGE-BASED SELECTION IN QUICK (GM 2026-08-26, T28): pytest-testmon records, per test, the code it executed, and
# on the next run selects only the tests whose executed code changed - the GM's long-run idea, off the shelf.
# `--testmon-forceselect`, because plain `--testmon` silently stops selecting whenever `-m` is used (its own help).
# Measured: nothing changed -> "no tests ran" in 3.3 s; a one-line engine edit -> 10 tests in 6.7 s; the first
# run after a fresh clone pays ~3 s to build `.testmondata`. Data files (fixtures, manifests, SVGs) are NOT
# tracked - a test that reads one re-runs only when its code changes - which is why the GATE never uses
# testmon and runs everything. `make quick ALL=1` runs every quick test regardless.
TESTMON = $(if $(ALL),--no-testmon,--testmon-forceselect)
# THE QUICK TREE (GM 2026-08-26, T29): `tests/` IS the quick suite; everything that is not quick lives in its own
# tree and is not even COLLECTED by quick - tests/tier_town and tests/tier_city (relevant to other tiers),
# tests/gate (the corpus, the coverage carriers, the map-rolling tests) and tests/tooling (collected only when the
# tooling changed since the last record, `ci tooling-fresh`). The gate collects all of `tests/`. Collection is
# paid per worker, so ~1,000 fewer items is ~0.4 s of a 3.3 s floor - and the layout says what each test is.
QUICK_TREE = tests --ignore=tests/tier_town --ignore=tests/tier_city --ignore=tests/gate --ignore=tests/full $(shell python3 -m l7r.diagram.ci tooling-fresh >/dev/null 2>&1 && echo --ignore=tests/tooling)
# THE TYPE CHECK IS ONE-SHOT pyrefly (feature 142, GM 2026-08-28). History, so nobody re-adds a daemon: mypy needed
# 12.7 s cold, so it ran through dmypy - which held 380-600 MB of RSS per clone, could not be shared across clones,
# and nothing ever stopped (five daemons, 2.3 GB, one for a session that had ended). pyrefly checks the whole engine
# cold in ~0.6 s (ty: ~0.5 s, but it has no rule for a missing annotation, research 142 R3), so there is nothing to
# keep warm and no sweep to run. Same command on CodeBuild. Measurements: specs/142-rust-type-checker/research.md R2.
TYPECHECK = pyrefly check
# THE GATE IS ALWAYS EXHAUSTIVE (constitution v2.9.0, GM 2026-08-26): `make quick` runs each test's quick form,
# `make done` its full form - the corpus, the full matrices, the full-size canvases, the tooling tests.
GATE_EXHAUSTIVE_ENV = L7R_TESTS_EXHAUSTIVE=1 $(if $(COV_FLOORS),L7R_COV_FLOORS=1,)  # GUARD_EDIT_OK: feature 133 T92's env, kept for any test that reads it; feature 135's own full-run signal is L7R_TESTS_FULL
# ...and the other tiers' TREES are not even collected under the lock (feature 135, third pass): every xdist
# worker collected ~700 town/city items to deselect them a moment later; the ignore is the same decision made
# before collection instead of after it.
TIER_SELECT = $(if $(COV_FLOORS),,$(if $(filter reference,$(SCOPE_STATE)),--tier $(REFERENCE_TIER) --ignore=tests/tier_town --ignore=tests/tier_city,))

# THE FIRING CENSUS SWEEP (feature 163). A check can be made to FAIL by a test's inline hand-BUILT
# manifest, which no glob over pool/ can see - `gardens_clear_of_channels` is the specimen: the
# artifact census reads it NEVER-FIRES while tests/check_village/test_segments_04_homesteads.py
# makes it fail on every run. So the sweep runs the SUITE with the gate's verdict journal on.
# It changes what is RECORDED and nothing else (feature 132's rule); the guard that says so is
# tests/check_village/test_verdict_journal.py, which asserts the verdicts are identical either way.
JOURNAL_ENV = $(if $(JOURNAL),DIAGRAM_VERDICT_JOURNAL=$(JOURNAL),)

# (GUARD_EDIT_OK: feature 132 - test-full rolls every pool map, so the scope lock refuses it before `test` starts)
test-full:
	$(SWEEP_OK)
	@$(MAKE) --no-print-directory test COV_FLOORS=1

# A DESELECTED TEST TAKES ITS COVERAGE WITH IT, so the reference scope CANNOT hold the 100% floor
# (measured 2026-08-24, the first green-path run of this restructure). Deselecting
# tests/test_villages.py and tests/hamletgen/test_driver.py drops `hamletgen/driver.py` to 52% and
# the whole tree to 99% - on code nothing changed. Enforcing a global floor against a deliberately
# partial suite reports a hole that is not there, and it does it on EVERY run, which is the fastest
# way to teach a session to read a red gate as normal.
#
# So the floors belong to the scope that can actually meet them, and the two scopes verify different
# things ON PURPOSE:
#
#   make done          - did *I* break anything? Every test that does not roll another map, plus
#                        `uncovered-in-diff.py`, which names any line in the working diff that no
#                        test reaches. That is the question a working session keeps asking.
#   make done FULL=1   - is the TREE whole? Adds the pool maps and the seeds 41-44 ratchet, and
#                        enforces both coverage floors. This is the pre-push sweep, and the
#                        constitution's mandatory once-at-the-end full run (Principle VI).
#
# WHAT THIS COSTS, said plainly: a coverage hole in code the reference scope does not execute
# survives until the FULL run. It is not silent - the diff check still catches uncovered lines you
# wrote, which is where holes actually come from - but the global invariant is a FULL-run guarantee
# now, not a per-run one. That is the price of having a cheap gate at all, and it was paid
# deliberately rather than by leaving a floor in place that could never be met.
COV_FLOORS =

test:
	@$(if $(ROLL_DESELECT),printf '\033[1mmap-rolling tests DEFERRED\033[0m (scope locked to the reference settlement) - owed at `make scope-unlock`\n';,)
# --dist worksteal (GM 2026-08-26, the make quick profile): the default `load` scheduler hands each worker a
# fixed slice up front, so on a suite whose tests range from 5 ms to 4 s the last worker finishes ~5 s after
# the rest; worksteal lets idle workers take from busy ones. Measured on quick: 27.5 s -> 22.0 s wall.
	@$(if $(COV_SCOPE),printf 'coverage: %s\n' "$(COV_SCOPE)";,)
	@if python3 -c "import xdist" >/dev/null 2>&1; then $(GATE_EXHAUSTIVE_ENV) $(FULL_ENV) $(JOURNAL_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal $(COV_SCOPE) $(FULL_TREE_IGNORE) $(ROLL_DESELECT) $(TIER_SELECT); else $(GATE_EXHAUSTIVE_ENV) $(FULL_ENV) $(JOURNAL_ENV) python3 -m pytest $(COV_SCOPE) $(FULL_TREE_IGNORE) $(ROLL_DESELECT) $(TIER_SELECT); fi; ec=$$?; \
	traced=$(if $(filter --no-cov,$(COV_SCOPE)),,1); \
	if [ $$ec -ne 0 ]; then [ -n "$$traced" ] && { python3 ../../../scripts/uncovered-in-diff.py || true; }; exit $$ec; fi; \
	if [ -z "$(COV_FLOORS)" ]; then \
	  printf '\033[1mcoverage floors: deferred to `make done FULL=1`\033[0m (a deselected test takes its coverage with it - see the Makefile comment)\n'; \
	  [ -n "$$traced" ] && { python3 -m coverage combine --append >/dev/null 2>&1 || true; python3 ../../../scripts/uncovered-in-diff.py || true; }; \
	  exit 0; \
	fi; \
	python3 -m coverage combine --append >/dev/null 2>&1 || true; \
	cov_ec=0; \
	python3 -m coverage report -m --omit='*/settlement/*,*/waterfields/*,*/interactive/*,*/check_village/*' --fail-under=100 || { echo "COVERAGE: a module other than settlement/, waterfields/, interactive/ and check_village/ is under 100% - the table above names it and its missing lines (those four are judged by the settlement ratchet and the hamlet-path floor below; check_village joined them under feature 145 - its city and capital segments lost their coverage carriers with feature 141 s corpus cut, and the GM ruled on 2026-08-28 that other tiers owe no floor while nothing exercises them)"; cov_ec=1; }; \
	python3 -m coverage report --include='*/settlement/*' --fail-under=$(SETTLEMENT_COV_FLOOR) || { echo "COVERAGE: settlement/ (package combined) fell below its $(SETTLEMENT_COV_FLOOR)% ratchet floor (see the comment above SETTLEMENT_COV_FLOOR in this Makefile; 'python3 -m coverage report -m --include=*/settlement/*' shows the missing lines)"; cov_ec=1; }; \
	python3 -m l7r.diagram.tools.hamlet_floor || cov_ec=1; \
	exit $$cov_ec
# ALL THREE FLOORS REPORT TOGETHER (GUARD_EDIT_OK: feature 145) - the same rule as the test phase: a first floor that
# `exit 1`s hides every floor after it, and on 2026-08-28 that made the hamlet floor UNREACHABLE while the global one was
# red on pre-existing tooling misses. Each records its own failure; the phase exits non-zero once, at the end.
# THE HAMLET-PATH FLOOR (GUARD_EDIT_OK: feature 145 adds a new gate phase - GM 2026-08-28: "one hundred percent code
# coverage on the scripted procedure and anything related to it ... automatic rather than something that we just
# remember to maintain"): every module the scripted rolls execute - derived from the roll cache's records of the
# reference, the three gate polders and the cohort's ratchet seeds, never a hand list - must be at 100%; town/city-only
# modules owe nothing here, and the settlement ratchet above stays. The module set: `make hamlet-floor`. The why:
# tools/hamlet_floor.py.
