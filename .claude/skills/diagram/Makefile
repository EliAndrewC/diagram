# The diagram-skill quality gate (Constitution Principle X). Run `make done` before declaring
# any Python change complete. Runs, in order: lint, format-check, type-check, tests+100% coverage.
#
# The type checker is pyrefly (feature 142, 2026-08-28): a Rust one-shot, ~0.6 s cold for the whole engine
# with nothing resident - it replaced mypy + the dmypy daemon (400-600 MB per clone). Rules in pyproject.toml.

# (GUARD_EDIT_OK: feature 132 adds the iteration switches - a new guard and five new operations)
# GUARD_EDIT_OK: feature 185 - the .PHONY half of `lint` -> `static`, and scope-lock/scope-unlock go.
.PHONY: done static format typecheck test test-full guard perf perf-report maps reference bypass-audit quick durations test-file audit perf-gatehooks-test explain \
	 switches ci-off ci-on _switch \
	 map cohort hamlet cache-audit placement-stages pool-index pool-index-if-stale compound render-sync idle-tests \
	 why-placed crop jogs pack-audit scatter-audit sun-audit timings citybudget help \
	 notes-census \
	 ci-status ci-check ci-merge ci-measure ci-image commit-permitted \
	 perf-explain perf-confirm perf-audit perf-signoff perf-review perf-profile
# GUARD_EDIT_OK: `tripwire` off .PHONY as well as losing its rule - a phony name with no recipe still
# RESOLVES (make treats it as an up-to-date target and exits 0), so leaving it here would have kept a
# dead command silently succeeding. Retired 2026-09-05; see the block comment above the `maps` target.
# GUARD_EDIT_OK: feature 166 - REMOVING operations, never loosening one. The check battery is retired,
# so the seven targets that drove it or its corpus (gate-manifest, regressions, new-check, site-justice,
# check-census, firing-census, firing-census-suite) name tools that no longer exist. A target pointing at
# a deleted module fails with a traceback instead of a refusal, which is the worst kind of guard.

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
	  : "GUARD_EDIT_OK: the SHORT-CIRCUIT re-stamps rather than earns, and that is what kept a bogus" ; \
	  : "record alive: each later gate refreshed its timestamp so it never aged out. No duration floor" ; \
	  : "applies here (0 s is correct for a reuse) but the dry-run refusal does." ; \
	  python3 "$$(git rev-parse --show-toplevel)/scripts/check-run-plausible.py" --reuse $(DONE_NAME) || exit 1; \
	  $(LOGRUN) $(DONE_NAME) reference 0 already-verified; $(STATE) green-local $(DONE_NAME) reused; \
	  printf '\n\033[1mgate green\033[0m (already verified - nothing the gate exercises has changed since the last green run)\n'; exit 0; \
	fi; \
	$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" || exit 1;,) \
	T0=$$(date +%s); fail=""; \
	: "(GUARD_EDIT_OK: feature 168 - THE CHEAP CHECKS RUN FIRST, at the GM's ruling 2026-08-30. The three static phases cost 1.8 s together against the reference roll's 29 s, so a session that has broken something ruff cannot fix hears about it in seconds rather than half a minute. The GM authorized this ON PRINCIPLE and predicted, correctly, that it buys almost nothing: both static phases AUTOCORRECT (ruff check --fix, ruff format), so they rarely fail at all, and only 8 of 317 recorded gate runs failed on one without also failing the suite - about 4 minutes recovered across the entire history. Do not later credit this reorder with a saving it does not deliver. It does not weaken 'the reference settlement gates everything expensive': what moved ahead of the roll is 16x cheaper than it, and every expensive phase still stands behind it.)"; \
	: "GUARD_EDIT_OK: feature 185 - the gate's phase loop, one of the four `lint` -> `static` sites" ; \
	for phase in static format typecheck; do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; \
	  $(MAKE) --no-print-directory $$phase || fail="$$fail $$phase"; \
	done; \
	if [ -n "$$fail" ]; then $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (the static checks run FIRST now, so the map roll has not happened - fix these and re-run)\n' "$$fail"; exit 1; fi; \
	: "(GUARD_EDIT_OK: feature 170 - REF_OK reaches the firing log as well as the bypass log)"; \
	$(if $(REF_OK),$(LOGESCAPE) REF_OK "$(REF_WHY)"; $(LOGBYPASS) permitted "REF_OK - reference step skipped: $(REF_WHY)"; printf '\nreference step SKIPPED (REF_OK, logged to dev/bypass-log/ and the firing log)\n';,$(MAKE) --no-print-directory reference || exit 1;) \
	: "GUARD_EDIT_OK: feature 174 makes the merge gate STRICTER, not looser - the GM's own request (2026-08-31)" ; \
	: "is that a plain make done cannot finish below 100% coverage, 'and there will no longer be any mechanism" ; \
	: "by which this can be accomplished'. The floors live behind COV_FLOORS=1, which is also what switches every" ; \
	: "deselection off, and a deselected test takes its coverage with it - so no arrangement holds a 100% floor" ; \
	: "over a partial suite, and the test phase becomes test-full on BOTH branches. The cost (the gate now runs" ; \
	: "the whole sweep) was stated to the GM rather than used to decline. FULL=1 still adds the perf bookends" ; \
	: "and the L7R_TESTS_FULL signal, which is what still distinguishes it." ; \
	for phase in hooks-test test-full $(if $(FULL),perf-gate,); do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; \
	  if [ "$$phase" = hooks-test ] && root=$$(git rev-parse --show-toplevel 2>/dev/null) && python3 "$$root/scripts/gate-stamp.py" --fresh hooks; then \
	    printf 'hooks-test: already green against exactly these guard scripts - skipped (gate-stamp --fresh hooks; 84 s measured 2026-08-26)\n'; continue; fi; \
	  $(MAKE) --no-print-directory $$phase || fail="$$fail $$phase"; \
	done; \
	if [ -n "$$fail" ]; then $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (every phase ran - fix them together, then re-run once)\n' "$$fail"; exit 1; fi; \
	: "GUARD_EDIT_OK: A RUN TOO FAST TO HAVE WORKED DOES NOT GET TO SAY IT PASSED (found 2026-09-05)." ; \
	: "make runs \$$(MAKE) sub-invocations even under -n, so `make -n done` reached these very lines" ; \
	: "having done nothing and wrote a correctly-hashed GREEN record - which is the whole of what a" ; \
	: "push demands. Two such records are in dev/run-log/ (3 s and 4 s against a 382 s day median)," ; \
	: "and each later gate short-circuited on it and RE-STAMPED it, so it never aged out. The floor is" ; \
	: "10% of the target's PINNED RATCHET BASELINE, so one number serves the ceiling and the floor and" ; \
	: "it tracks the era - this gate's median has been 21 s and 587 s within two weeks." ; \
	root=$$(git rev-parse --show-toplevel 2>/dev/null); \
	python3 "$$root/scripts/check-run-plausible.py" $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" || exit 1; \
	[ -n "$$root" ] && python3 "$$root/scripts/gate-stamp.py" --write diagram || true; \
	$(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" green; \
	: "(GUARD_EDIT_OK: feature 171 - THE RATCHET RUNS AFTER THE RECORD, deliberately: this run is part"; \
	: " of the median it is judged against, and a gate that fails without having logged what it did"; \
	: " would hide the very number the next session needs. It judges the MEDIAN in today's regime, so"; \
	: " one slow run cannot fail the gate - the GM's own worked example is about a sustained level.)"; \
	root=$$(git rev-parse --show-toplevel); \
	: "(GUARD_EDIT_OK: feature 171 FR-009 - LIKE WITH LIKE. The scope is passed, so a reference-scope"; \
	: " run is judged against reference-scope runs. _gatecost already excludes anything that is not"; \
	: " green, which is what keeps a short-circuited 'already-verified' at seconds=0 out of the median"; \
	: " - a naive average over every row would be dragged toward zero and lower everybody's bar.)"; \
	med=$$(python3 "$$root/scripts/_gatecost.py" $(DONE_NAME) "$(if $(FULL),full,reference)" 2>/dev/null | grep -oE '^[0-9]+' | head -1); \
	python3 "$$root/scripts/_ratchet.py" $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" "$${med:-}" || exit 1; \
	$(STATE) green-local $(DONE_NAME); \
	: "GUARD_EDIT_OK: FINDING 2 OF THE NAMING AUDIT - both banners STATED SOMETHING FALSE. Since feature" ; \
	: "174 the phase list is 'hooks-test test-full (+perf-gate under FULL)', so a plain make done runs the" ; \
	: "SAME TESTS as FULL=1 - every pool map, seeds 41-44, the lot. FULL adds the perf bookends, a bypass" ; \
	: "audit and a scope check, and nothing else. The old text told a reader the plain gate had skipped" ; \
	: "work it had in fact done, which is worse than vague (GM 2026-09-05)." ; \
	$(if $(FULL),printf '\n\033[1mgate green (FULL - plus the perf bookends)\033[0m\n',printf '\n\033[1mgate green\033[0m (the whole suite: every pool map, seeds 41-44; `FULL=1` adds only the perf bookends)\n')
	: "GUARD_EDIT_OK: the tail of the same banner still claimed FULL=1 'also rolls the other pool maps'."

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
# (GUARD_EDIT_OK: feature 133 FR-004 - a refused paid target also leaves a would-have-dispatched run-log entry, so
#  remote-off never hides how often money was about to be spent; the check itself is unchanged, ci/ does the write)
REMOTE_OK = @python3 -m l7r.diagram.ci remote-ok "$@"

switches:       ## the iteration switches: remote on|off, scope unlocked|reference (feature 132)
	@$(SWITCH) show
ci-off:         ## REMOTE OFF - nothing dispatches to CodeBuild; the gated push lands on a green local make done   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=off MSG="remote off" REASON="$(REASON)"
ci-on:          ## REMOTE ON - the default; the gated route may dispatch again   REASON="..."
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=on MSG="remote on" REASON="$(REASON)"
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
	$(REF_FIRST)
	$(RUN).tools.cohort_audit --count $(or $(N),48)

# GUARD_EDIT_OK: `tripwire` RETIRED as a target (GM 2026-09-05), folded into `maps`. It ran the same
# `mapcheck` with the same auto scope, so with no SCOPE set it was `maps` minus the index refresh -
# and its help line, "the middle tier: reference map, then the tripwire seeds", could not be true:
# mapcheck's scopes are auto|reference|all and there is no `tripwire` among them. The tripwire seeds
# (27, 33, 37, 41, 47) are a rung INSIDE the auto state machine, not a scope you can ask for, and
# they keep that name where it is accurate - in `mapcheck.TRIPWIRE_SEEDS`.
# The repo's own doctrine already said there should be one command here: *"Use `make maps`, which
# picks its own scope ... There is no second command on purpose - the earlier two-command version
# relied on the session choosing right, and it did not."* There were two. Now there is one.
# `_invocation.py`'s operation registry names `maps` now, so `ci-check TARGET=maps` still dispatches
# mapcheck - the operation name must equal a make target, because run.sh runs `make $MAKE_TARGET`.

hamlet: export L7R_STAGE_PROFILE = $(if $(PROFILE),1,)
hamlet:         ## generate one hamlet from the CLI   ARGS="--name X --seed 4 ..." [PROFILE=1]
	$(REF_FIRST)
	$(RUN).hamletgen $(ARGS)
	@$(MAKE) --no-print-directory pool-index-if-stale

cache-audit:    ## does using the generation cache change any map?
	$(REF_FIRST)
	$(RUN).tools.cache_audit $(ARGS)
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
overlap-audit:  ## does A overlap B on a finished map (records AND drawn ink)   M=pool/hamlets/x/x.json [FAMILIES=...]
	$(RUN).tools.overlap_audit $(M) $(if $(FAMILIES),--families $(FAMILIES),)

polder-probe:   ## the polder block ALONE with its geometry metrics, no map   SEED=21 | SEEDS=21,22 ARCHETYPE=...
	$(RUN).tools.polder_probe $(if $(SEED),--seed $(SEED),)$(if $(SEEDS),--seeds $(SEEDS),)$(if $(ARCHETYPE),--archetype $(ARCHETYPE),)$(if $(LAYOUT),--layout $(LAYOUT),)$(if $(HOUSEHOLDS),--households $(HOUSEHOLDS),)

why-placed:     ## who placed this, and what refused to        GEN=... AT=x,y | REFUSED=x,y
	$(RUN).tools.why_placed $(GEN) $(if $(AT),--at $(AT),)$(if $(REFUSED),--refused $(REFUSED),)

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
	: "(GUARD_EDIT_OK: feature 172 - one work directory for the fan-out's logs and exit codes)"; \
	work=$$(mktemp -d); trap 'rm -rf "$$work"' EXIT; \
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
	  : "(GUARD_EDIT_OK: feature 172 - THE DEPENDENCY SET IS DERIVED, TRANSITIVELY. It was a fixed list"; \
	  : " naming all four shared helpers for every suite, so a one-line _gatecost.py fix re-ran 21 suites"; \
	  : " when two reference it. scripts/_hookdeps.py follows the real reference graph, and follows it"; \
	  : " THROUGH helpers: _guardlog.sh calls _hookmatch.py since feature 170, so a guard naming only the"; \
	  : " former still depends on the latter. Direct-only would UNDER-run and pass a suite a change had"; \
	  : " broken, which is worse than the over-running it replaces. Measured in specs/172/research.md:"; \
	  : " _gatecost.py 21 -> 2, test_hooks_cases.py 21 -> 3, and _hookmatch.py/_guardlog.sh still 20/19,"; \
	  : " which is why this feature also runs the suites in parallel.)"; \
	  deps=$$(python3 "$$root/scripts/_hookdeps.py" --deps "$$b" | sed "s|[^ ]*|$$root/scripts/&|g"); \
	  : "(GUARD_EDIT_OK: fixing a guard that FIRES ON CORRECT WORK - the per-suite freshness cache resolved its own path as \$$root/.git/hooks-test, and in a LINKED WORKTREE .git is a FILE, so every one of the 19 suites failed with 'Directory nonexistent'. A detached worktree is exactly where constitution XIII requires the regression baseline to be taken, so the mandated procedure could not produce a green hooks-test on ANY commit. Asking git for the path fixes it in both layouts; the roster, the failure path and the stamp are unchanged. Feature 157.)"; \
	  sha=$$(cat $$deps 2>/dev/null | sha256sum | cut -c1-16); mkdir -p "$$gitdir/hooks-test"; \
	  if [ -z "$(HOOKS_ALL)" ] && [ "$$(cat "$$gitdir/hooks-test/$$b" 2>/dev/null)" = "$$sha" ]; then skipped=$$((skipped+1)); continue; fi; \
	  n=$$((n+1)); printf '%s %s %s\n' "$$b" "$$t" "$$sha" >> "$$work/todo"; \
	done; \
	: "(GUARD_EDIT_OK: feature 172 - FAN OUT, THEN COLLECT. The suites ran one after another for 94 s"; \
	: " against 17 s for the whole Python suite, which pytest runs in parallel. Each builds its fixtures"; \
	: " in its own mktemp -d and, since feature 170, isolates its own GUARD_LOG_DIR; the three that use"; \
	: " HOME point it at their own temp; nothing writes host-wide state. Each job writes its own log and"; \
	: " its own exit code, so every failure is still reported together, with the suite that produced it."; \
	: " A suite that turns out to need serializing gets serialized - never retried, because a retry"; \
	: " hides a real race behind a green result.)"; \
	if [ -s "$$work/todo" ]; then \
	  mkdir -p "$$gitdir/hooks-test"; \
	  xargs -P $(HOOKS_JOBS) -L1 -a "$$work/todo" "$$root/scripts/_hookrun.sh" "$$work" "$$gitdir" || true; \
	  for rc in "$$work"/*.rc; do \
	    [ -f "$$rc" ] || continue; \
	    b=$$(basename "$$rc" .rc); \
	    if [ "$$(cat "$$rc")" != ok ]; then \
	      printf '\n\033[1mHOOK TESTS FAILED: %s\033[0m\n' "$$b"; sed 's/^/  /' "$$work/$$b.log"; fail="$$fail $$b"; \
	    fi; \
	  done; \
	fi; \
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
	if [ -n "$$CODEBUILD_BUILD_ID" ] && ! $(PERF_REVIEW) has-start --feature "$$n" >/dev/null 2>&1; then \
	  : "GUARD_EDIT_OK: FIXING A GUARD THAT NEVER FIRED CORRECTLY (feature 179, FR-017). The old test was" ; \
	  : "ls dev/perf-log/*<n>-start*codebuild*.json - a FILENAME test, but snapshots are named" ; \
	  : "{stamp}-{label}-{clone}.json and 0 of the 44 on record contain 'codebuild', so it was always" ; \
	  : "false and every remote build re-took a bookend it may already have had. has-start asks the" ; \
	  : "SNAPSHOT for its recorded machine identity, which is also STRICTER: the filename test would" ; \
	  : "have paired an XLARGE -start with an 8-vCPU -end. The no-baseline refusal below is untouched." ; \
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
'GUARD_EDIT_OK: feature 168 - the census gains the RULE breakdown; everything else prints as before.'; \
'The by-rule line is SUPPRESSED when it carries nothing the line above did not: entries recorded before'; \
'this feature default their rule to their event, so a guard whose whole history predates the slug would'; \
'otherwise print `by rule: blocked=16, permitted=4` directly under `blocked=16, permitted=4`. A census'; \
'line that restates the line above it trains a reader to skip both. (GUARD_EDIT_OK: this is the'; \
'display half of FR-004, and it changes what the census PRINTS, never what any guard does.)'; \
rules=collections.defaultdict(collections.Counter); \
[rules[r['guard']].update([r.get('rule') or r['event']]) for r in rows]; \
[ (print(f\"  {g:<12} \"+', '.join(f'{k}={v}' for k,v in sorted(c.items()))+(f\"   escape rate {c['escaped']/max(1,c['escaped']+c['blocked']):.0%}\" if c['blocked'] or c['escaped'] else '')), \
   (print('               by rule: '+', '.join(f'{k}={v}' for k,v in rules[g].most_common(4))) if len(rules[g])>1 and set(rules[g])-set(c) else None)) for g,c in sorted(by.items())] or print('  (none recorded yet)'); \
'GUARD_EDIT_OK: repairing my own break - a trailing `# comment` appended to the line above landed'; \
'MID-EXPRESSION, between the list comprehension and its `or print(...)`, because the whole census is'; \
'one python -c continuation. Nothing in a python -c block takes a shell comment; the reason lives in'; \
'the bare-string lines above instead.'; \
'GUARD_EDIT_OK: feature 170 - THE REASONS, which is the report the GM asked for: we have no way to'; \
'audit later when this workaround was taken and whether the stated reasons were valid use cases.'; \
'Every escape entry carries the session s stated reason as its detail now, so the census shows them.'; \
'Newest first, capped at eight so the census stays a census; the log itself holds the rest.'; \
esc=[r for r in rows if r['event']=='escaped']; \
[print('\033[1m  escapes taken, with what the session said\033[0m')] and [print(f\"    {r['utc'][5:16]}  {r['guard']:<12} {(r['detail'] or '(no reason recorded)')[:88]}\") for r in sorted(esc,key=lambda r:r['utc'],reverse=True)[:8]] if esc else None; \
print(f\"  {len(rows)} entries\"+(f\", {min(r['utc'] for r in rows)} to {max(r['utc'] for r in rows)}\" if rows else '')); \
print()"
# GUARD_EDIT_OK: feature 173 - this section stops being a REPORT of a question and becomes the audit
# of a GATED rule. Three things were wrong with it, and all three are why the drift went unnoticed
# long enough for the GM to find it from their own laptop: it said "five files already exceed it"
# when TEN did; it said "Reported rather than gated on purpose", which is the sentence the GM retired
# on 2026-08-31; and it scanned `l7r tests` only, so `wip/shiro-daika.gen.py` at 1,592 lines and all
# of `scripts/` were invisible to the very report meant to catch this. It asks the CHECKER now, over
# the checker's own scope, so the report and the gate can never again disagree about what is over.
	@printf '\033[1mFiles past the ~1,000-line bar\033[0m (constitution X clause 13 - GATED since feature 173)\n'
	@python3 ../../../scripts/check-file-scale.py --list ../../..
	@printf '  A file over the bar FAILS `make lint`, and so `make done` and the push. The one way out\n'
	@printf '  is clause 13'"'"'s ordered-data carve-out, stated IN the file as `FILE_SIZE_OK: <reason>` and\n'
	@printf '  listed above with its reason - a carve-out nobody can enumerate is one nobody revisits.\n'
	@printf '  If the bulk is a roster restating code elsewhere, clause 14 says DERIVE it, do not split.\n\n'

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

# GUARD_EDIT_OK: FINDING 4 - both ci-* help lines described PRE-REPOINT behavior. A remote run is
# `make soak` now, not `make done`, so this is no longer "the iteration check" and ci-merge is no
# longer a merge queue. The names are fine; the descriptions had gone stale (GM 2026-09-05).
ci-check:       ## run the SOAK suite on CodeBuild (PAID)      FULL=1 (prompts) | TARGET=cohort etc. | NO_GO=1 (FR-036 self-abort proof)
	$(REMOTE_OK)
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
# (GUARD_EDIT_OK: feature 132 - remote off refuses every ci-check before any AWS call; FULL and TARGET are sweeps under the scope lock)
	$(RUN).ci check $(if $(FULL),--full,) $(if $(TARGET),--target "$(TARGET)",) $(if $(NO_GO),--no-go,) $(if $(COMPUTE),--compute "$(COMPUTE)",)
# (GUARD_EDIT_OK: NO_GO=1 is the FR-036 measurement - the build must abort itself when nobody releases it; feature 130 T076.
#  COMPUTE=BUILD_GENERAL1_2XLARGE is the T028 scaling measurement the GM asked for on 2026-08-25; the default is large, 8 vCPU, feature 179)
# (GUARD_EDIT_OK: a forward-looking statement of the CURRENT default, falsified by feature 179's compute change - FR-005)

# GUARD_EDIT_OK: FINDING 4, second half - see the ci-check comment above.
ci-merge:       ## the push's gated route (PAID) - runs the SOAK suite; no longer a merge queue. Called by sync-with-main.sh   FULL=1 (prompts)
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
# (GUARD_EDIT_OK: feature 132 - FULL is a sweep under the scope lock. Remote-off is NOT checked here: the dispatcher
#  handles it itself, because with remote off it must still produce the LOCAL-GATED verdict the push procedure reads)
	$(RUN).ci merge $(if $(FULL),--full,)

# the operator's `permitted` answer becomes a commit, so the build finds it in the tree it tests (FR-025)
commit-permitted:
	@f=$$(ls -t dev/bypass-log/*.json | head -1); why=$$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['why'][:60])" "$$f"); \
	git add dev/bypass-log && git commit -q -m "chore: authorize FULL sweep - $$why" && echo "committed $$f ($$why)"

# GUARD_EDIT_OK: feature 177 - ONE prompt opens the FULL door here, deliberately. LOGBYPASS writes the
# target as MAKECMDGOALS plus " FULL" when FULL is set, so with FULL=1 this recipe's own entry already
# reads "ci-measure FULL" - and door.check asks only that the target CONTAIN FULL, that the entry be
# `permitted`, and that its commit be an ancestor of HEAD and not of origin/main. `ci-check` calls
# `commit-permitted` after `bypass-audit` because bypass-audit does not commit its entry; this recipe
# commits its own, so calling it too would run `git commit` with nothing staged and fail the target.
# (A shell-level version of this note was tried first and broke the recipe: a make-escaped
# dollar-paren inside a `: "..."` no-op is command substitution to /bin/sh. Prose belongs here.)
# GUARD_EDIT_OK: feature 178 FR-017 - a paid target gains the COMPUTE knob `ci-check` already has
# (feature 130 T028). It widens nothing: the dispatch still passes every condition it passed before,
# and the compute type only chooses which instance runs it. It is required because the GM asked for
# measurements on smaller servers and `ci-check` cannot be asked without an engine delta.
ci-measure:     ## MEASURE what the remote gate costs (PAID, prompts)   FULL=1 | COMPUTE=BUILD_GENERAL1_LARGE
	$(REMOTE_OK)
	@: "(GUARD_EDIT_OK: feature 177 - a NEW paid target, in the same class as ci-image: it prompts, it"; \
	: " logs, and it cancels by default. It is the only route that may dispatch with NO engine delta,"; \
	: " which is why it prompts at all - `ci-check` is gated by a delta it computes and cannot be asked"; \
	: " for on a whim. What it CANNOT do is buy a merge credential: buildspec/measure.yml sets MODE"; \
	: " measure and run.sh writes no verified/ record and pushes nothing.)"; \
	if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: ci-measure is a paid operation and its prompt needs a terminal.\033[0m Run it in the foreground.\n\n'; $(LOGBYPASS) refused "ci-measure with no terminal"; exit 1; fi; \
	printf '\n\033[1mAbout to MEASURE the remote gate on AWS\033[0m (a build, billed by the minute). This buys a\n'; \
	printf 'number and nothing else - no verified record, no push. Press Enter to CANCEL.\n\nReason to continue (Enter cancels): '; \
	read why || true; \
	if [ -z "$$why" ]; then $(LOGBYPASS) cancelled "(ci-measure backed out at the prompt)"; printf 'Cancelled.\n'; exit 1; fi; \
	: "GUARD_EDIT_OK feature 177 - repairing my own edit: those explanatory no-op lines carried a make"; \
	: "escape for a dollar-paren expansion, which /bin/sh read as command substitution and died on"; \
	: "-- Syntax error: unexpected close paren. The note now lives in a make comment above the target,"; \
	: "where no shell ever parses it. ONE prompt opens the FULL door here on purpose - see there."; \
	$(LOGBYPASS) permitted "$$why"; git add dev/bypass-log; git commit -q -m "chore: authorize a remote measurement - $$why" || true
	$(RUN).ci measure $(if $(FULL),--full,) $(if $(COMPUTE),--compute "$(COMPUTE)",)
# GUARD_EDIT_OK: feature 178 - repairing my own edit. A `: "..."` no-op line was placed BEFORE the
# line above, which put a continuation in front of $(RUN) - and $(RUN) begins with `@`, a make RECIPE
# PREFIX that is only meaningful at the start of a line. Mid-recipe it is a literal character, so the
# shell tried to run `@python3` and the dispatch died with "not found". This file already carries that
# exact warning beside LOGBYPASS, where the same mistake made the bypass log silently record nothing.
# The marker for the COMPUTE knob lives in the comment block above the target, where no shell parses it.

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

# GUARD_EDIT_OK: feature 170 - REF_OK IS AN ESCAPE, SO IT REACHES THE FIRING LOG TOO. It recorded to
# `dev/bypass-log/` only, and `make audit` reads `~/.claude/guard-log/`, so the one escape that skips
# the reference settlement was invisible to the census the GM asked to be able to audit. Round 3 of
# this feature's review caught it and the ruling was two records rather than a weaker success
# criterion: the bypass-log entry stays, and this adds the firing-log one with REF_WHY as its detail.
# It also holds REF_WHY to the same floor as every other escape - two words, eight characters.
LOGESCAPE = @root=$$(git rev-parse --show-toplevel) && bash -c '. "$$0/scripts/_guardlog.sh"; \
  printf "%s" "$$2" | python3 "$$0/scripts/_hookmatch.py" reason-ok >/dev/null || { \
    printf "BLOCKED: %s needs a REASON (two words, eight characters) - it is what a later audit reads.\n" "$$1" >&2; \
    guard_log make blocked "$$2" "$$1-no-reason"; exit 2; }; \
  guard_log make escaped "$$2" "$$(printf "%s" "$$1" | tr "[:upper:]_" "[:lower:]-")"' "$$root"

# GUARD_EDIT_OK: feature 172, corrected - how many guard suites run at once, FOLLOWING THE SAME RULE
# AS `XDIST_WORKERS` (GM 2026-08-30, who asked whether it did: it did not). It shipped as a flat 8,
# which over-subscribes a box with fewer cores and, worse, leaves the 36-vCPU CodeBuild builder using
# 8 - a knob that ignores the machine it is on in both directions.
#
# `xargs -P` needs a NUMBER where pytest accepts `auto`, so the remote arm is `CPU_COUNT` rather than
# the literal `auto` that `XDIST_WORKERS` uses; the local arm is the same `min(CPU_COUNT, 8)`.
#
# There is a ceiling this shares with nothing else: more jobs than SUITES buys nothing, and past that
# the wall clock is the longest single suite (measured: 194 s serial, 63 s at 8 - not 24 s, because
# `test-sync-with-main.sh` and `test-clone-sync-hooks.sh` build real git trees and dominate the tail).
# HOOKS_JOBS=1 is the old serial behavior exactly, which is how to bisect a suite that misbehaves
# under concurrency.
HOOKS_JOBS ?= $(if $(CODEBUILD_BUILD_ID),$(CPU_COUNT),$(shell [ "$(CPU_COUNT)" -lt 8 ] && echo "$(CPU_COUNT)" || echo 8))

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
# GUARD_EDIT_OK: RETIRED WITH THE BATTERY IT REPORTED (feature 166's leftover, found 2026-08-31 by the
# first remote build since 2026-08-25). `make explain` was "why a map is failing - every check with its
# message", and it ran `check_village`'s gate; feature 166 deleted that battery and its five tools and
# seven targets, and missed this one because it is a DOTFILE (`.explain.py`, hidden so
# `gencache.engine_files()` prunes it) and so matched no sweep. Nothing replaces it: a rule about a map
# is a test of the placer now, and the per-map questions go to `make why-placed`, `make overlap-audit`
# and `make sun-audit`.
#
# WHY NOBODY NOTICED FOR A DAY: `l7r/diagram/check_village/` survived on disk in every existing clone as
# an empty-but-for-`__pycache__` directory. That is an importable PEP 420 namespace package, so
# `from l7r.diagram import check_village` still RESOLVED locally while failing in a fresh clone -
# `tests/test_package_surfaces.py` passed here and failed on CodeBuild. A deleted package leaves a
# phantom behind; deleting the tracked files is not the same as removing the directory.

durations:
	@python3 -m pytest -n $(XDIST_WORKERS) -q --no-cov $(if $(FULL),,--ignore=tests/full) $(if $(MARK),-m "$(MARK)",-m "not rolls_map") --durations=$(or $(N),12) 2>&1 | grep -E "^[0-9.]+s (call|setup)|passed|failed" | head -$$(( $(or $(N),12) + 2 ))
# (FULL=1 profiles the full tree too; the coverage carriers live there now, so `coverage_only` no longer needs deselecting - feature 135)

quick:
	@python3 -m ruff check --fix l7r/ tests/ && python3 -m ruff format l7r/ tests/ && $(TYPECHECK)
	@: "(GUARD_EDIT_OK: feature 171 - capture whether testmon was warm BEFORE the run, so the ratchet below judges like with like)"; \
	warm=$$([ -f .testmondata ] && echo yes || echo no); start=$$(date +%s); $(EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal $(TESTMON) -q --no-cov -x --ff -m "not rolls_map" $(TIER_SELECT) $(QUICK_TREE); ec=$$?; \
	  el=$$(( $$(date +%s) - start )); \
	  if [ $$ec -ne 0 ]; then exit $$ec; fi; \
	  : "(GUARD_EDIT_OK: feature 171 - the RATCHET, which is the same check against a number that means"; \
	  : " something. IT JUDGES A WARM, SELECTIVE RUN ONLY, and that is FR-009's own principle - 'judges"; \
	  : " only runs that did the work and compares like with like' - applied to the other direction. The"; \
	  : " GM stated 15 s against 'make quick is currently at eleven seconds', which is the WARM figure;"; \
	  : " a cold run rebuilds .testmondata and is recorded at 25.3 s, and ALL=1 turns selection off"; \
	  : " entirely. Judging either against a warm baseline would fail on the first run in every new"; \
	  : " clone - a guard firing on correct work, which is how guards get routed around.)"; \
	  root=$$(git rev-parse --show-toplevel); \
	  if [ "$$warm" = yes ] && [ -z "$(ALL)" ]; then python3 "$$root/scripts/_ratchet.py" quick "$$el" || exit 1; \
	  elif [ $$el -ge 15 ]; then printf '\nquick took %ss, but this run was %s - not judged against the 15s bar (feature 171).\n' "$$el" "$$([ "$$warm" = yes ] && echo "ALL=1, so unselective" || echo "COLD: it built .testmondata")"; fi; \
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
# GUARD_EDIT_OK: A FAILING PROBE MUST NOT UPGRADE A RUN'S AUTHORITY (found 2026-09-05).
# `2>/dev/null` swallows every error from the probe, so if `switches idle` fails for ANY reason - a
# syntax error mid-edit, a missing import, a broken interpreter - IDLE_CTX came back empty and
# DONE_NAME fell back to `done`. That is backwards: `ci/state.py`'s GREEN_TARGETS deliberately OMITS
# `idle-done`, and that omission is the entire mechanism by which an unattended idle gate neither
# grants nor revokes a push (feature 136 D1/FR-006b). So a broken probe was silently PROMOTING an
# idle run to one whose record the push honors - a failure that increases trust instead of reducing
# it. Now the probe's failure is distinguishable from its answer, and an unreadable answer fails
# toward `idle-done`, which is the direction that can only ever withhold authority.
IDLE_CTX = $(shell $(SWITCH) idle 2>/dev/null || echo unreadable)
DONE_NAME = $(if $(filter 0,$(IDLE_CTX)),done,idle-done)
idle-tests:     ## what an idle session runs unattended (feature 136): the whole gate, scope relaxed, never FULL
# THE PAIRING'S ONE-SIDED CASE, TAKEN RATHER THAN CARVED OUT (feature 151): a detached timer has no
# session to dispatch a settlement-review from, so it supplies the override with its reason and the
# bypass log carries it like any other. An exemption inside the guard is the shape the spec review struck.
	@PAIR_OK="idle run: no session attached to dispatch a review" $(MAKE) --no-print-directory done

maps:
	@python3 -m l7r.diagram.tools.mapcheck
	@$(MAKE) --no-print-directory pool-index-if-stale
# (GUARD_EDIT_OK: feature 132 - `maps SCOPE=all` is refused under the lock; mapcheck itself never widens while locked)

perf:
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

# GUARD_EDIT_OK: feature 185 - `lint` -> `static` (GM 2026-09-05). It has not been linting for some
# time: it is ruff plus three custom guards (duplicate-defs, file-scale, stale-dirs), while `format`
# is whitespace alone. THIS target-position line is one of four sites and the one most easily missed:
# rename only the recipe below and `make lint` STILL RESOLVES here - declared with an order-only
# prerequisite and no recipe - and exits 0 silently, which is the trap feature 184 hit with tripwire.
static format typecheck test: | guard

# LINT AND FORMAT AUTOCORRECT, THEY DO NOT FAIL (GM 2026-08-26: *"having linters autocorrect everything is a
# standard practice ... having every run of the linter simply fix linting errors rather than failing on them
# seems like it is what we want"*). Three of one day's red gates were import order and formatting - each a
# 75 s gate plus a model turn spent on something with no decision in it. `ruff check --fix` applies every
# safe fix and still exits non-zero on what it cannot fix (a real finding); `ruff format` rewrites in place
# (black-compatible; the gate key is semantic, so a reformat never re-opens it).
# GUARD_EDIT_OK: feature 185 - the recipe half of the `lint` -> `static` rename (see the comment on
# the target-position line above; four sites in this file, all of them required).
static:         ## the static checks: ruff, duplicate-defs, file-scale, stale-dirs (was `lint`)
	python3 -m ruff check --fix .
	python3 ../../../scripts/check-duplicate-defs.py --selftest
	python3 ../../../scripts/check-duplicate-defs.py ../../..
# GUARD_EDIT_OK: feature 173 - THE ~1,000-LINE BAR IS GATED (GM 2026-08-31: *"one of the things that
# can run whenever we do a make done can be to check the size of our files ... then we fail the
# gate"*). It sits in `lint` beside check-duplicate-defs because it is the same class of thing - a
# repo-wide static structural rule with a selftest that runs first - and because `lint` runs FIRST at
# the gate (feature 168), so an oversize file is reported before the map roll is paid for. It costs
# 0.04 s over the tree. Closes half of the constitution's own v1.6.1 deferred TODO; the other half,
# clause 12's expression count on FUNCTIONS, is still owed.
	python3 ../../../scripts/check-file-scale.py --selftest
	python3 ../../../scripts/check-file-scale.py ../../..
	: "GUARD_EDIT_OK: a directory left with nothing but __pycache__ is still an importable PEP 420" ; \
	: "namespace package, so a long-lived clone passes what a fresh clone fails - silently, and in the" ; \
	: "direction that hides the bug. Four of them were live when this landed (GM 2026-09-05). It runs" ; \
	: "in lint, beside its two siblings, because the gate runs lint FIRST and this costs 5 ms."
	python3 ../../../scripts/check-stale-dirs.py --selftest
	python3 ../../../scripts/check-stale-dirs.py ../../..

format:
	python3 -m ruff format .

typecheck:
	$(TYPECHECK)

# parallel across cores when pytest-xdist is installed (~1 min vs ~5 min serial, measured
# 2026-07-20 on 22 cores), plain serial pytest otherwise - xdist is a speedup, not a requirement.
# The coverage gate combines worker data, so the coverage requirement holds either way.
#
# COVERAGE IS ONE FLOOR OVER THE WHOLE TREE (GUARD_EDIT_OK: feature 174 - this is the STRICTER
# arrangement, and retiring a ratchet is the thing the GM asked for first: "we have some ratchets
# somewhere that enforce less than one hundred percent, but I think we want to enforce one hundred
# percent coverage in whatever the relevant place is", 2026-08-31).
#
# WHAT WAS HERE, and why it is gone. From the 2026-08-16 legacy freeze (migration-plan.md "The
# accepted trade") settlement/ held a RATCHET floor of 94, and settlement/, waterfields/,
# interactive/ and overlap/ were omitted from the 100% report: the hand-authored pool maps were
# frozen, so the above-hamlet wings were exercised by nothing. The freeze's own terms said RAISE the
# floor as each tier converts and never lower it - and feature 174 converted the lot by TESTS rather
# than by tiers. Measured on its green run: settlement/ 10,342 statements 0 missing; waterfields/ +
# interactive/ + overlap/ 3,015 statements 0 missing. A ratchet whose condition is met is no longer a
# ratchet, it is a hole - settlement/ could have shed ~620 statements and still passed - so both
# retired the day they could. Do not reintroduce either: bring the code up, or take the GM's ruling.

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
# GUARD_EDIT_OK: feature 185 - both were defined through SCOPE_STATE, so with the axis gone they
# expand empty unconditionally. Kept as empty definitions rather than deleted, so every recipe that
# references them (`make quick` among them) needs no edit.
ROLL_DESELECT =
# TIER RELEVANCE (GM 2026-08-26, feature 133 T17): the reference settlement is a hamlet, so while scope is
# locked the suite skips tests tagged for other tiers only (`tiers` marker, tests/conftest.py). The tier is
# named here, once; never under COV_FLOORS.
REFERENCE_TIER = hamlet
# WORKERS: 8 ON A SHARED BOX, EVERY CORE ON CODEBUILD (GM 2026-08-26, T23). Measured on the 22-core dev
# container: the quick set is as fast on 8 workers as on 22 (9.9 vs 10.1 s - each worker costs ~0.17 s to
# spawn and collect, and past 8 that buys back the parallel gain), while the GM runs several sessions at
# once on the laptop, so flooding every core only slows the others. CodeBuild is dedicated to the run, so
# it takes `auto` (8 vCPU on the large, since feature 179 - which is where this comment's own 8-vs-22
# finding pointed all along). CODEBUILD_BUILD_ID is set in every CodeBuild build and nowhere
# (GUARD_EDIT_OK: a forward-looking statement of the worker count the remote run takes, which moves with the box - FR-005)
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
TIER_SELECT =

# GUARD_EDIT_OK: feature 166 - the firing census sweep is retired with the battery it counted. It ran
# the SUITE with the gate's verdict journal on, because a check could be made to fail by a test's
# inline hand-BUILT manifest that no glob over pool/ could see. There are no checks to count.
JOURNAL_ENV =

# (GUARD_EDIT_OK: feature 132 - test-full rolls every pool map, so the scope lock refuses it before `test` starts)
# GUARD_EDIT_OK: DOCUMENTATION ONLY - `test-full` had no `##` string, so it was invisible in `make help`
# while `measure-hooks.sh` refuses a second one by name and `tests/CLAUDE.md` names it as a tree's runner.
# A target a session is told about only by a REFUSAL is one it will misunderstand: this session described
# it to the GM as running less than the full suite, having read `tests/CLAUDE.md`'s "done FULL=1 and the
# AWS check only" row, when in fact COV_FLOORS=1 switches every deselection OFF. Nothing executable changes.
# GUARD_EDIT_OK: feature 178 FR-004/FR-005 - a green test-full records green-local, as `done`, `quick`,
# `reference` and `test-file` already do. It is the STRONGEST local proof there is (every tree, every
# floor, nothing deselected) and it was the only one that could not satisfy the paid route's
# `green-local-since-edit`, while a `make quick` that selected nothing and reported "no tests ran in
# 0.97s" could. Feature 177 hit that and recorded it as R15; GM 2026-09-03: *"Yes I agree this sounds
# like a quick small fix, so please make that fix too."* It records ONLY on success - the `&&` is the
# whole of that - and names its own target so an audit can tell which run vouched.
# GUARD_EDIT_OK: FINDING 3 - "nothing deselected" became FALSE the day tests/soak/ was deselected.
test-full:      ## the gate's whole test phase + all three coverage floors (everything except tests/soak/, which only `make soak` runs)
	@$(MAKE) --no-print-directory test COV_FLOORS=1 && $(STATE) green-local test-full

# GUARD_EDIT_OK: THE TIER ABOVE THE GATE (GM 2026-09-05) - a new target, and the one a REMOTE run
# GUARD_EDIT_OK: the last two stale `sweep` strings in this file - both FALSE as written, since
# make_target returns `soak` and tests/sweep/ does not exist. Caught by the spec review, not by me.
# dispatches (`ci/dispatch.py make_target()` returns `soak`, not `done`). Doctrine, the membership
# rule and why the directory is empty: tests/soak/CLAUDE.md.
#
# IT REFUSES ON AN EMPTY SUITE, deliberately. A remote build that goes green having executed zero
# tests is worse than one that goes red: it is evidence of nothing while looking like evidence. This
# project's rule is that non-vacuity is ASSERTED, never assumed (dev/gate.md - a seed test whose
# subject list is empty passes). So the count is checked first and the refusal says what to do.
#
# GUARD_EDIT_OK: the last stale `sweep` in the suite sense, three lines above the comment explaining
# why the suite is NOT called that. Found by the spec review's second pass, not by my own grep.
# No coverage flags: a soak test covers nothing the gate does not already cover - that IS the
# membership rule - so tracing it would only slow it down.
# GUARD_EDIT_OK: RENAMED sweep -> soak, caught by the naming audit the same day it landed. This repo
# GUARD_EDIT_OK: the last literal mention of the retired macro, removed because the DERIVED escape
# census scans the tree for every `*_OK` token and fails on one it cannot classify - so a comment
# naming a macro that no longer exists is not free. Caught by that census, exactly as intended.
# already used SWEEP for a run that rolls many MAPS - the scope-lock check was the guard (retired
# `switches.py` says a locked scope is one where "every sweep refuses" - so a target named `sweep`
# with the lock in feature 185) - so a target of that name sat three lines from the guard asserting a
# target is NOT one. `soak` is the standard
# term for the thing this actually is: the same code held under realistic load for an extended run.
soak:           ## the tier ABOVE the gate: the same code over many seeds and larger maps (tests/soak/)
	@n=$$(ls tests/soak/*.py 2>/dev/null | wc -l); \
	if [ "$$n" -eq 0 ]; then \
	  : "GUARD_EDIT_OK: the rest of the sweep -> soak rename (see the block comment above this target)" ; \
	  printf '\n\033[1mmake soak: the soak suite is EMPTY, so there is nothing to prove.\033[0m\n\n'; \
	  printf 'tests/soak/ is declared and deliberately unfilled - the home of the tier above the gate\n'; \
	  printf '(the same code over many seeds and larger, more realistic maps), kept as structure so that\n'; \
	  printf 'when that work arrives there is no argument about where it goes.\n\n'; \
	  printf 'Running it now would report a GREEN build having executed zero tests. Read\n'; \
	  printf 'tests/soak/CLAUDE.md - it carries the membership rule (a test belongs there if removing\n'; \
	  printf 'it does not change coverage) and the honest statement of when this tier earns its keep.\n\n'; \
	  exit 1; \
	fi; \
	$(GATE_EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal -q --no-cov tests/soak \
	  && $(STATE) green-local soak

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
#
# SUPERSEDED FOR `make done` BY FEATURE 174 (GUARD_EDIT_OK: the gate gets STRICTER; GM 2026-08-31).
# The reasoning above is kept because it is still TRUE - it is the argument the GM overruled, not one
# that was wrong. Their request was for the floor at the merge gate itself: "we literally cannot
# complete our make done in order to merge back into main, and there will no longer be any mechanism
# by which this can be accomplished." The two facts above (a deselected test takes its coverage with
# it; the reference scope deselects) mean the only way to hold a 100% floor is to stop deselecting -
# so `done`'s test phase is `test-full` on both branches. `COV_FLOORS` stays the switch and stays
# empty by default, because `make test` is still run directly and by `make quick`, which the GM
# exempted in the same request ("I don't think we need to do this for our make quick").
COV_FLOORS =

test:
	: "GUARD_EDIT_OK: feature 185 - the map-rolling DEFERRED notice went with the scope lock. It fired" ; \
	: "only when ROLL_DESELECT was non-empty, and that variable was defined through the retired axis." ; \
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
	python3 -m coverage report -m --fail-under=100 || { echo "COVERAGE: a module is under 100% - the table above names it and its missing lines. GUARD_EDIT_OK: feature 174 makes this STRICTER. It used to omit settlement/, waterfields/, interactive/ and overlap/ and hand them to a 94% ratchet, which is precisely what the GM asked to end (2026-08-31: 'we have some ratchets somewhere that enforce less than one hundred percent, but I think we want to enforce one hundred percent coverage in whatever the relevant place is'). The omit list and SETTLEMENT_COV_FLOOR both retired the day their own condition was met - measured on this feature's green run, settlement/ 10,342 statements 0 missing, the other three trees 3,015 statements 0 missing. The hamlet-path floor below STAYS: it is a finer check (feature 145), not a weaker one"; cov_ec=1; }; \
	python3 -m l7r.diagram.tools.hamlet_floor || cov_ec=1; \
	exit $$cov_ec
# ALL THREE FLOORS REPORT TOGETHER (GUARD_EDIT_OK: feature 145) - the same rule as the test phase: a first floor that
# `exit 1`s hides every floor after it, and on 2026-08-28 that made the hamlet floor UNREACHABLE while the global one was
# red on pre-existing tooling misses. Each records its own failure; the phase exits non-zero once, at the end.
# THE HAMLET-PATH FLOOR (GUARD_EDIT_OK: feature 145 adds a new gate phase - GM 2026-08-28: "one hundred percent code
# coverage on the scripted procedure and anything related to it ... automatic rather than something that we just
# remember to maintain"): every module the scripted rolls execute - derived from the roll cache's records of the
# reference, the three gate polders and the cohort's ratchet seeds, never a hand list - must be at 100%; town/city-only
# modules owe nothing here. (GUARD_EDIT_OK: feature 174 - this line used to end "and the settlement ratchet above
# stays"; that ratchet is retired, so what stays above is the flat 100% floor over the whole tree, and this finer
# per-module check sits UNDER it rather than beside it.) The module set: `make hamlet-floor`. The why:
# tools/hamlet_floor.py.
