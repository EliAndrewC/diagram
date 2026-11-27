# The diagram project's operations: `make help` lists them, `make docs` writes docs/make-targets.html from the `##` lines.
# A target's `##` line is published help text: keep notes and escape markers off it.
# Comments go above a target as `#` lines. A recipe's `: "..."` string is shell, so a backtick or $$( in it RUNS.
# A .PHONY name with no rule still exits 0, a caller passing having run nothing: retire a target's .PHONY entry with its rule
# (tests/hooks/test-make-only-hooks.sh section 7 fails on one, feature 449 T223).

# FREE TEXT REACHES A RECIPE THROUGH THE ENVIRONMENT, NEVER THROUGH A QUOTED SHELL WORD (feature 449 T186): `--units "$(UNITS)"`
# put a claim key holding `well` in backticks inside a double-quoted shell word, so the shell ran `well` and the bundle refused.
# Each name below is made a simple variable holding its text as given (make no longer expands a $ in it) and exported, and a
# recipe reads it as "$$NAME", which the shell expands once and never reads again. A list (URLS, MATCH, ...) is split by the shell
# with globbing off (`set -f`, then an unquoted $$NAME or a loop over it), one argument a word as before, so a `?` or `*` in a URL
# stays itself. A recipe naming one as $(NAME) outside an $(if ...) test fails tests/hooks/test-make-only-hooks.sh section 6; a
# path, a number, an id or an enum stays $(NAME) (the plan's T186 list).
FREE_TEXT = UNITS WITH KEYS KEY CLASS KIND SUBJECT REASON GROWTH_REASON SPREAD NOTE WHY WORDS TITLE MSG FINDING OLD NEW RESULT \
	FIXED_BY OUTCOME SOUGHT SOURCE STATUS WRITE LINE Q Q_JA Q_ZH Q_KO QUESTION TERMS K MARK URL REVIEW APPROVED REREAD \
	ARBITER_OK PREFLIGHT_OK REF_WHY SET_DOWN_OK HOLD_OK MISSING_OK COVER_OK NOT_OWED_OK PLAN_REVIEW_OK KEY_CAP_OK WRITE_CAP_OK \
	CHECK_ORDER_OK URLS MATCH NONE SHARD EXTRA IMAGES DIRS LAND SUITES PERF_LATER_OK DEFER_FORM_OK QUICK_OK BY OVER
$(foreach v,$(FREE_TEXT),$(if $(filter command line environment,$(origin $(v))),$(eval override $(v) := $$(value $(v)))$(eval export $(v))))

.PHONY: closing-checks audits state-push state-restore modal-bundle modal-prepass done docs static format guard _reference _quick bypass-audit quick page-check tick claim speckit-todo audit guard-edit context-ok guard-log scratch-sweep cache-clean disk-audit hooks-test guard-messages citations fragment-move \
	 switches _switch research-deferred research-open \
	 map maps cohort cohort-landing hamlet placement-stages pool-index pool-index-if-stale compound render-sync idle-tests \
	 pack-audit help \
	 notes-census glossary page-lit picture-diff \
	 ci-status gated-check

# ---- performance: a bookend pair over band 1 is a flag mentioned at landing, never a refusal ----

work-budget:    ## [performance] the counted work of the reference hamlet per stage, from the Rust driver built with its counters, against its budget at 10/20/40/80 households (features 443, 444)   [WRITE=1: replace the standing record dev/work-budget.md]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure work-budget $(if $(WRITE),--write,)

rust-tooling:   ## [tests] every check, hook, gate and make target that reads Python's syntax tree or .py files has its row in dev/rust-tooling.md, saying what it becomes in the Rust phases; a step of hooks-test (feature 443)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check rust-tooling

work-budget-review: ## [performance] the push's ratchet: on a push carrying engine code, every ACCEPTED hamlet stage held to its accepted figure and twice its budget at 40 and 80 households (a form at its own sizes), every pool-sheet stage to twice its budget on each sheet, re-counted only where what it reads moved; a stage nothing counts is printed, never passed silently; no arbiter accept clears it (features 443, 444 FR-022, 449 T224)   ROUTE=<GATED|GATED-LOCAL|DIRECT>
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure work-budget-review "$(ROUTE)"

work-budget-bundle: ## [performance] the work-budget agent's bundle: MODE=budget a stage's derivation (refused holding code or today's counts), MODE=audit the landed code against its counters (feature 443)   MODE=budget|audit PHASE=<stage> [DERIVATION=<file>] [BUDGET=<file>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" work-budget-bundle "$(MODE)" "$(PHASE)" $(if $(DERIVATION),--derivation "$(DERIVATION)",) $(if $(BUDGET),--budget "$(BUDGET)",)

budget-set:     ## [performance] a stage's FIRST work budget, only from a SOUND work-budget MODE BUDGET verdict; refused on a stage already budgeted; the budget is per thing x the derivation's own items at each size (features 443, 444)   PHASE=<stage> PER_THING=<ops> EXPONENT=<e> ITEMS_AT_20=<n> ITEMS_AT_40=<n> ITEMS_AT_80=<n> DERIVATION=<file> VERDICT=<verdict file> | ARBITER=ask:<id> SPREAD="<low>-<high> at <households>" (the round arbiter's accept, feature 444 FR-013) [REASON="<why above today's count at 40>"] [GROWTH_REASON="<why its n is bounded>": past rubric S6's 1.15 from 20 to 80] [LOWER=1: re-pin a budgeted stage, no higher at any size] [RAISE=1: raise a budgeted stage on a SOUND re-derivation naming the work its first missed (444 FR-022) - past twice its first at 40 with SECOND=<an independent MODE BUDGET's SOUND>, never past 10 times it] | a Mode A stage, its derivation sized by `Sizes: pool sheets`: PHASE= DERIVATION= VERDICT= alone, its budget the derivation's Totals line on each sheet (feature 449 T201)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" budget-change set "$(PHASE)" "$(PER_THING)" "$(EXPONENT)" "$(DERIVATION)" "$(VERDICT)" $(if $(ARBITER),--arbiter "$(ARBITER)",) $(if $(SPREAD),--spread "$$SPREAD",) $(if $(ITEMS_AT_10),--items-at-10 "$(ITEMS_AT_10)",) $(if $(ITEMS_AT_20),--items-at-20 "$(ITEMS_AT_20)",) $(if $(ITEMS_AT_40),--items-at-40 "$(ITEMS_AT_40)",) $(if $(ITEMS_AT_80),--items-at-80 "$(ITEMS_AT_80)",) $(if $(REASON),--reason "$$REASON",) $(if $(GROWTH_REASON),--growth-reason "$$GROWTH_REASON",) $(if $(LOWER),--lower,) $(if $(RAISE),--raise,) $(if $(SECOND),--second "$(SECOND)",)

budget-sheets:  ## [performance] a Mode A stage's counted operations against its per-sheet budget (dev/work-budget.json's sheet_stages, set by make budget-set on a pool-sheet derivation): each sheet's ratio, and those past twice it (feature 449 T201)   PHASE=<stage> COUNTS="<sheet>=<ops> <sheet>=<ops> ..."
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" budget-change sheets "$(PHASE)" "$(COUNTS)"

budget-change:  ## [performance] change a budgeted stage's figure with the GM's own words, checked against the session by budget-change-hooks.sh and logged in dev/work-budget-changes.jsonl (feature 443)   PHASE=<stage> TO=<ops per thing> [EXPONENT=<e>] [ITEMS_AT_<h>=<items>, at the stage's own sizes: 20 40 80, a form's 10 20 (449 T253)] [DERIVATION=<file> VERDICT=<SOUND verdict>: re-point it, 444 FR-015] WORDS="<the GM's words>" | a pool-sheet stage: TO="<sheet>=<ops> ..." and/or DERIVATION= VERDICT= (its Totals), WORDS= (449 T243)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" budget-change change "$(PHASE)" "$$TO" $(if $(EXPONENT),--exponent "$(EXPONENT)",) $(if $(ITEMS_AT_10),--items-at-10 "$(ITEMS_AT_10)",) $(if $(ITEMS_AT_20),--items-at-20 "$(ITEMS_AT_20)",) $(if $(ITEMS_AT_40),--items-at-40 "$(ITEMS_AT_40)",) $(if $(ITEMS_AT_80),--items-at-80 "$(ITEMS_AT_80)",) $(if $(DERIVATION),--derivation "$(DERIVATION)",) $(if $(VERDICT),--verdict "$(VERDICT)",) --words "$$WORDS"

budget-accept:  ## [performance] accept a rebuilt phase: its MODE AUDIT verdict WITHIN and its counted operations at its sizes (40 and 80 households; a form at its own) in the newest work-budget run at most its budget (LEEWAY: at most twice it, 444 FR-022), recorded as the figures the push's ratchet holds (feature 444 FR-005)   PHASE=<stage> AUDIT=<MODE AUDIT verdict file, in the repository beside the stage's derivation> [ARBITER=<the round arbiter's accept, when the audit's last round was not WITHIN>] | a pool-sheet stage: COUNTS="<sheet>=<ops> ..." its count on every sheet, held to its budget there (449 T243)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" budget-change accept "$(PHASE)" "$(AUDIT)" $(if $(ARBITER),--arbiter "$(ARBITER)",) $(if $(COUNTS),--counts "$$COUNTS",)

budget-program: ## [performance] set the whole roll's work budget with the GM's own words, checked and logged as budget-change is (feature 443; 444 FR-002)   OPS_AT_40=<ops> EXPONENT=<e> WORDS="<the GM's words>"
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" budget-change program "$(OPS_AT_40)" "$(EXPONENT)" --words "$$WORDS"

counters-inert: ## [performance] the work counters change no map: every Rust test passes in the counting build as in the default one, its counters compiled out (features 443, 444; the GM 2026-11-07: "We should probably run with counters compiled out by default")   [FRESH=1 REASON="..."]
	$(FRESH_ESCAPE)
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust test-counters

# THE RUST CHECKS REUSE A CRATE'S LAST GREEN RESULT BY DEFAULT (feature 449 T93; the GM 2026-11-11: "being able to reuse things which have
# already been compiled, and also the results of tests which have already run so that we don't have to run them again, is exactly what we
# should be doing"): a crate's test, cover, lint and dead run again only when its sources, the crates it builds from, or what its tests
# declare they read moved (`rust/gate/crates/rustc/src/rustc.rs`). Every crate fresh is an escape that states its reason and is recorded
# (`FRESH=1 REASON="..."`), or `make done FULL=1`'s own logged path; `INCREMENTAL=0` and `FULL` on these targets once turned reuse off silently.
FRESH_ESCAPE = $(if $(FRESH),$(LOGESCAPE) FRESH "$$REASON",@:)
static rust-test counters-inert: export L7R_RUST_FRESH := $(if $(FRESH),1,$(L7R_RUST_FRESH))
done: export L7R_RUST_FRESH := $(if $(FULL),1,)

STATE = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" state write

# done runs every phase and reports every failure together, cheapest phase first.
# A run too fast to have worked is not stamped green (`l7r-gate check run-plausible`): make runs $(MAKE)
# sub-invocations even under -n, so a dry run once wrote a green record the push honored.
done:            ## [tests] tier 3, the whole gate: lint, the static checks, the reference map, every test and the 100% floors; run once at the end, backgrounded   FULL=1 INCREMENTAL=0
	$(DISK_FLOOR)
	$(if $(ARBITER_OK),$(LOGESCAPE) ARBITER_OK "$$ARBITER_OK",@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" arbiter gate-held || exit 1)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" lock acquire "$$(git rev-parse --absolute-git-dir)" "$$PPID"
	$(if $(PREFLIGHT_OK),$(LOGESCAPE) PREFLIGHT_OK "$$PREFLIGHT_OK",@:)
	@$(if $(PREFLIGHT_OK),:,if [ -z "$(FULL)" ] && "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" state verified-done >/dev/null 2>&1; then :; else tp=$$(date +%s); "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" preflight --root "$$(git rev-parse --show-toplevel)" --no-coverage || { touch "$$(git rev-parse --absolute-git-dir)/gate-preflight-red"; printf '\n\033[1mGATE FAILED: preflight\033[0m (fix it and re-run; nothing expensive has run)\n'; exit 1; }; $(RUNSTATS) phase-pre "$$(git rev-parse --absolute-git-dir)" preflight $$(( $$(date +%s) - tp )) "$(CURDIR)" 2>/dev/null || true; fi)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" preflight --root "$$(git rev-parse --show-toplevel)" --tree-snap "$$(git rev-parse --absolute-git-dir)/gate-tree.json"
	@if [ -z "$(FULL)" ] && "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" state verified-done; then \
	  root=$$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$$root" ] && "$$root/scripts/gates/l7r-gate.sh" stamp --write diagram || true; \
	  "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check run-plausible --reuse $(DONE_NAME) || exit 1; \
	  if ! "$$root/scripts/gates/l7r-gate.sh" stamp --fresh hooks >/dev/null 2>&1; then echo "make done: ...but the hooks stamp is stale (a scripts/ or tests/hooks/ change) - running make hooks-test first"; $(MAKE) --no-print-directory hooks-test FROM_DONE= ||{ $(LOGRUN) $(DONE_NAME) reference 0 failed:hooks-test; $(COMMIT_RUN_RECORD) failed; exit 1; }; fi; \
	  $(LOGRUN) $(DONE_NAME) reference 0 already-verified; $(STATE) green-local $(DONE_NAME) reused; $(COMMIT_RUN_RECORD) already-verified; \
	  printf '\n\033[1mgate green\033[0m (already verified - nothing the gate exercises has changed since the last green run)\n'; exit 0; \
	fi; \
	$(if $(FULL),$(MAKE) --no-print-directory bypass-audit || exit 1;,) \
	T0=$$(date +%s); fail=""; \
	rm -f "$$(git rev-parse --absolute-git-dir)/roll-cache-class"; \
	G=$$(git rev-parse --absolute-git-dir); $(RUNSTATS) start "$$G" 2>/dev/null || true; \
	statics() { for phase in static format $(if $(filter rust-only,$(PORT)),seeds,); do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; ts=$$(date +%s); \
	  $(MAKE) --no-print-directory $$phase || { fail="$$fail $$phase"; $(RUNSTATS) fail "$$G" $$phase 2>/dev/null; }; \
	  $(RUNSTATS) phase "$$G" $$phase $$(( $$(date +%s) - ts )) "$(CURDIR)" 2>/dev/null || true; \
	done; }; \
	: "THE STATIC CHECKS BESIDE THE TESTS AT rust-only (feature 444 T36; the GM 2026-11-07: \"Can static checks run in parallel with everything else?\"): they ran first so a red one stopped the gate before the reference map was rolled, and at rust-only no map is rolled - so they run in the background, their output kept and shown after the tests, both groups' failures reported together"; \
	par=$(if $(filter rust-only,$(PORT)),yes,); \
	if [ -n "$$par" ]; then ( statics; printf '%s' "$$fail" > "$$G/static-fail" ) > "$$G/static.log" 2>&1 & spid=$$!; else statics; fi; \
	if [ -z "$$par" ] && [ -n "$$fail" ]; then RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (the static checks run FIRST now, so the map roll has not happened - fix these and re-run)\n' "$$fail"; exit 1; fi; \
	tr=$$(date +%s); $(if $(filter rust-only,$(PORT)),printf '\nreference step SKIPPED - the port switch stands at rust-only (feature 444 FR-023): make done rolls no map\n';,$(if $(REF_OK),$(LOGESCAPE) REF_OK "$$REF_WHY"; $(LOGBYPASS) permitted "REF_OK - reference step skipped: $$REF_WHY"; printf '\nreference step SKIPPED (REF_OK, logged to dev/bypass-log/ and the firing log)\n';,$(MAKE) --no-print-directory _reference || { $(RUNSTATS) fail "$$G" reference 2>/dev/null; RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed: reference"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); exit 1; };)) $(RUNSTATS) phase "$$G" reference $$(( $$(date +%s) - tr )) "$(CURDIR)" 2>/dev/null || true; \
	for phase in hooks-test counters-inert; do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; \
	  if [ "$$phase" = hooks-test ] && root=$$(git rev-parse --show-toplevel 2>/dev/null) && "$$root/scripts/gates/l7r-gate.sh" stamp --fresh hooks; then \
	    printf 'hooks-test: already green against exactly these guard scripts - skipped (gate-stamp --fresh hooks; 84 s measured 2026-08-26)\n'; continue; fi; \
	  ts=$$(date +%s); $(MAKE) --no-print-directory $$phase FROM_DONE=1 || { fail="$$fail $$phase"; $(RUNSTATS) fail "$$G" $$phase 2>/dev/null; }; \
	  $(RUNSTATS) phase "$$G" $$phase $$(( $$(date +%s) - ts )) "$(CURDIR)" 2>/dev/null || true; \
	done; \
	if [ -n "$$par" ]; then wait $$spid; cat "$$G/static.log"; fail="$$(cat "$$G/static-fail" 2>/dev/null)$$fail"; rm -f "$$G/static.log" "$$G/static-fail"; fi; \
	if [ -n "$$fail" ]; then RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (every phase ran - fix them together, then re-run once)\n' "$$fail"; exit 1; fi; \
	root=$$(git rev-parse --show-toplevel 2>/dev/null); \
	mode=incremental; sel=; \
	[ -z "$$root" ] || "$$root/scripts/gates/l7r-gate.sh" preflight --root "$$root" --tree-check "$$(git rev-parse --absolute-git-dir)/gate-tree.json" || { RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed: tree moved"; $(STATE) failed-gate tree-moved; $(COMMIT_RUN_RECORD) failed; exit 1; }; \
	"$$root/scripts/gates/l7r-gate.sh" check run-plausible $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" "$$mode" || exit 1; \
	[ -n "$$root" ] && "$$root/scripts/gates/l7r-gate.sh" stamp --write diagram && "$$root/scripts/gates/l7r-gate.sh" stamp --write page || true; \
	$(if $(BROWSER_SKIP),,[ -n "$$root" ] && "$$root/scripts/gates/l7r-gate.sh" stamp --write browser || true;) \
	RUN_MODE="$$mode" RUN_SELECTED="$$sel" RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" green "$$(cat "$$(git rev-parse --absolute-git-dir)/roll-cache-class" 2>/dev/null || true)"; $(COMMIT_RUN_RECORD) green; \
	root=$$(git rev-parse --show-toplevel); \
	cls=$$(cat "$$(git rev-parse --absolute-git-dir)/roll-cache-class" 2>/dev/null || true); \
	scp="$(if $(FULL),full,reference)"; \
	med=$$("$$root/scripts/gates/l7r-gate.sh" measure gatecost $(DONE_NAME) "$$scp" "$${cls:-}" 2>/dev/null | grep -oE '^[0-9]+' | head -1); \
	n=$$("$$root/scripts/gates/l7r-gate.sh" measure gatecost --count $(DONE_NAME) "$$scp" "$${cls:-}" 2>/dev/null || echo 0); \
	if [ "$$mode" = incremental ]; then printf 'ratchet: incremental run (%s tests) - not judged; the median is over full runs\n' "$$sel"; else "$$root/scripts/gates/l7r-gate.sh" measure ratchet $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" "$${med:-}" "$${cls:-}" "$$scp" "$$n" || exit 1; fi; \
	$(STATE) green-local $(DONE_NAME); \
	$(if $(FULL),printf '\n\033[1mgate green (FULL - plus the perf bookends)\033[0m\n',printf '\n\033[1mgate green\033[0m (the whole suite and every pool map; `FULL=1` adds only the perf bookends)\n')

COHORT_FRESH = 4

# ---- iteration switches (dev/switches.json) ----
SWITCH = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" switches

switches:       ## [project] the iteration switches: claims, port and research, with reason, who and when (feature 132; research 451 T244)
	@$(SWITCH) show
claims-report-only: ## [project] CLAIMS AT REPORT - a claims finding refuses no landing and files no task; it is checked and listed by make claims-report (feature 445; the shipped state)   REASON="..."
##  REASON=<text>  why claims go to report - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=claims STATE=report MSG="claims at report"
claims-clean:   ## [project] CLAIMS CLEAN - a landing refuses while make claims-report lists any open finding, so a finding is fixed where it is noticed (feature 445)   REASON="..."
##  REASON=<text>  why claims go clean - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=claims STATE=clean MSG="claims clean"
port-integrated: ## [project] PORT INTEGRATED - make done rolls the map-rolling tests, the reference map and the floors, and make land the landing cohort, as before feature 444 amendment 8; thrown when the last stage is Rust (FR-023)   REASON="..."
##  REASON=<text>  why the port goes integrated - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=port STATE=integrated MSG="port integrated"
port-rust-only: ## [project] PORT RUST-ONLY - the default while any stage is Python: no landing waits on the Python stages after the Rust front, make done rolls no map, make land lands on the Rust stage gate alone (feature 444 FR-023)   REASON="..."
##  REASON=<text>  why the port goes rust-only - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=port STATE=rust-only MSG="port rust-only"
research-deferred: ## [project] RESEARCH DEFERRED - no research-pass dispatch and no make page-session starts unasked (RESEARCH_OK="<reason>" escapes, recorded); a physical task's boxes may be answered `deferred: UNRESEARCHED`; a port stage's end lists its backlog, unsearched (feature 451 T244)   REASON="<the GM's words>"
##  REASON=<text>  why research is deferred - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=research STATE=deferred MSG="research deferred"
research-open:  ## [project] RESEARCH OPEN - the shipped rules: a search pass runs when a decision needs it, and each port stage's end searches the backlog it touched (feature 451 T244)   REASON="..."
##  REASON=<text>  why research reopens - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=research STATE=open MSG="research open"
_switch:
	@[ -n "$$REASON" ] || { printf '\n\033[1mREFUSED: a reason is required\033[0m - a reason someone will READ is a decision you have to defend.\n  make <target> REASON="..."\n\n'; exit 1; }
	@$(SWITCH) set $(AXIS) $(STATE) --why "$$REASON"
	@git add dev/switches.json && git commit -q -m "chore: $$MSG - $$REASON" && printf '\ncommitted: %s - %s\n' "$$MSG" "$$REASON"

# ---- expensive: they generate ----
# THE OWED LIST IS READ AGAIN AFTER THE REDRAW (449 T289, 2026-11-22): a compound not current has no legend now, so the list read before
# `make map` redrew it held none of the units its new elements owe; the snapshot took that list and dropped the genkan's glyph-check
# and size-audit and the round-trip's ten. Don't snapshot the first reading once a map was redrawn.
# THE REVIEW TREE (451 T164, 2026-11-22): the gate and the snapshot judged the clone's shared working tree, so three builders' half-done
# edits turned the 449 T312 bundle's gate red or "tree moved" four times and seven finished verdicts NOT-REVIEWABLE. Both build in a
# worktree at a temporary commit of the bundle's own files on HEAD (scripts/gates/review-tree.sh, which keeps the redraw rule above);
# each unit is judged by that gate's record, never the clone's stamp.
verify:        ## [tests] THE PAIRED RUN: the gate and the review snapshot built together in the review tree, a worktree at a commit of the bundle's own files (feature 151; 451 T164)   T=<task(s)> [F=<feature>] [FILES="<paths no task's edit names>"] [REVIEW_TREE_OK="<why>"]
##  T=<task(s)>      the bundle whose work is reviewed: the files lines filed under its tasks name go into the review commit
##  F=<feature>      the tasks' feature (default: $SPECIFY_FEATURE)
##  FILES="<paths>"  the bundle's files no task's line names (a make target's write), taken in too
	@printf '\033[1mverify\033[0m: the gate and the independent review run TOGETHER - neither alone (GM 2026-08-29).\n'
	@if [ -z "$(T)" ]; then printf 'make verify: T= is required - the task(s) whose work is reviewed, so the review tree holds their files and no other builder'"'"'s (451 T164): make verify T=<task(s)> [F=<feature>] [FILES="<paths>"]\n' >&2; exit 2; fi
	@f="$(or $(F),$(SPECIFY_FEATURE))"; [ -n "$$f" ] || { printf 'make verify: F= is required (no SPECIFY_FEATURE exported): make verify F=<feature> T=$(T)\n' >&2; exit 2; }; \
	  REVIEW_TREE_OK="$(REVIEW_TREE_OK)" bash "$$(git rev-parse --show-toplevel)/scripts/gates/review-tree.sh" "$$f" "$(T)" $(FILES)

verify-wait:    ## [tests] wait for the gate `make verify` started, on ITS OWN log, and print its verdict - run it with run_in_background (exit 0 green, 1 red, 3 no log, 4 timed out, 5 the gate died)
	@bash "$$(git rev-parse --show-toplevel)/scripts/gates/verify_wait.sh"

# ONE RUST DRIVER FOR EVERY POOL MAP (feature 449 T221, rebuilt from specs/449-rust-codebase/derivations/T219-pipeline.md): the walk's kind
# names the engine and the spec, the generation cache (rust/gate/crates/pool/src/cache.rs) serves the map or draws it. The two
# `--no-cache` stanzas this recipe had are its keep now: an entry drawn with the picture skipped serves only a run that skips it, and a
# modal or page asset is one of the reads every sheet reports (a miss among them), its change regenerating the sheets that read it.
map:            ## [maps] draw ONE pool map through the generation cache (Rust since 449 T221) - a hamlet, a generated compound or a hand sheet - and say CACHED, REGENERATED (with why) or FROZEN   MAP=pool/<tier>/<map> (or a file in it, or its name; --all: every live map)
##  MAP=<folder|spec>  the map: its folder pool/<tier>/<map>, any file in it (its .spec.json, .compound.json or .svg), or its bare name
	@if [ -n "$(GEN)" ]; then printf 'make map: GEN= went with the .gen.py files (feature 449 T221) - name the map: make map MAP=%s\n' "$$(dirname "$(GEN)")" >&2; exit 2; fi
	@if [ -z "$(MAP)" ]; then printf 'make map: MAP= is required - the map'\''s folder, a file in it, or its name, e.g. make map MAP=pool/magistracies/ubame-magistracy, make map MAP=pool/hamlets/sawada/sawada.spec.json, or make map MAP=--all for every live map\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" pool map "$(MAP)"
	@$(MAKE) --no-print-directory pool-index-if-stale
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure maps-moved $(if $(filter --all,$(MAP)),,--only "$(MAP)")

# THE ONE SELF-SCOPING COMMAND (Constitution VI, GM 2026-08-23; rebuilt in Rust by feature 449 T252 on the GM's 2026-11-22 ruling): the
# scope is read from how the last run went (.git/maps-state.json), never chosen by the session - the tier table and why are
# rust/gate/crates/pool/src/maps.rs
maps:           ## [maps] draw and check the pool, picking its own scope from how the last run went: after a failure (or none) each tier's reference map alone, stopping at the first problem and widening once clean; after a pass every tier whole, every failure reported (449 T252)   [SCOPE=reference|all] [TIER=hamlets|mode-a]
##  SCOPE=reference|all  override the scope; by default it picks its own - the reference maps alone after a failed run, every tier whole after a clean one
##  TIER=<row>           one row of the tier table (hamlets, mode-a)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" pool maps $(if $(SCOPE),--scope "$(SCOPE)",) $(if $(TIER),--tier "$(TIER)",)
	@$(MAKE) --no-print-directory pool-index-if-stale

maps-moved:     ## [maps] which live maps' drawings (the generation cache's artifacts) moved against HEAD's - the mirror's render-sync drawing, wherever HEAD's inputs for a map are the mirror's; else NOT COMPARED with why, never unchanged (feature 429; 449 T230)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure maps-moved --root "$$(git rev-parse --show-toplevel)"

backup:         ## [project] save the clone's commits to backup/<clone> on GitHub without landing them - no gate runs (the GM 2026-11-07: "stop landing things until we've gotten this time down")
	@"$$(git rev-parse --show-toplevel)/scripts/sync-with-main.sh" backup

# THE DRIVER RUN BY CARGO ITSELF, NO PYTHON BETWEEN (feature 444 T36; the GM 2026-11-07: "Why does `make hamlet` run Python at
# all?"): `l7r-gate rust hamlet` only put the command together - the shared target directory, the toolchain's cargo - and its
# start was ~20 ms of a ~110 ms map (measured 2026-11-07); cargo still decides whether the binary is fresh. Same directory, so
# the gate's builds and these share one cache
HAMLET_RUN = CARGO_TARGET_DIR="$${CARGO_TARGET_DIR:-$$HOME/.cache/l7r-cargo-target/$(notdir $(CURDIR))}" "$$([ -x "$$HOME/.cargo/bin/cargo" ] && echo "$$HOME/.cargo/bin/cargo" || echo cargo)" run --release --quiet --manifest-path rust/phases/Cargo.toml --bin hamlet --

seeds:          ## [maps] NO FIXED SEEDS: the known-failing pool (dev/known-seeds.txt) rolled again - a seed that now rolls clean dropped - and N fresh seeds of each field form from a start the clock draws, a failing one added to the pool; refuses while any fails. make done runs it at rust-only (feature 444 T36; the GM 2026-11-07)   [N=200]
	@$(HAMLET_RUN) --seeds "$(CURDIR)/dev/known-seeds.txt" $(or $(N),200)

cohort-seeds:   ## [maps] which seeds found which failure, the fewest first seeds that find them all, and the fresh-seed rate (feature 375, 386)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" cohort seeds

cohort:         ## [maps] roll N cohort seeds through the Rust driver, one line a seed, each refusal or broken rule named, the time taken (feature 444 T42)   [N=48] [SEED=1] [FIELD=polder_grid|mulberry_dike_fishpond]
	@$(call TIMED,cohort,cohort,$(HAMLET_RUN) --cohort $(or $(SEED),1) $(or $(N),48) $(FIELD))

# THE LANDING COHORT HAS NO ROLLER WHILE THE PORT SWITCH STANDS AT rust-only (feature 449 T223): its recipe rolled the Python cohort and
# wrote the dev/cohort-log/ record `l7r-gate cohort check` reads, and went with the Python driver (feature 444 T39), leaving a .PHONY name
# with no rule - `make land` at `integrated` ran it, passed having rolled nothing, and landed. `make cohort` (the Rust driver) writes no
# such record, so it cannot stand in. Feature 444 FR-023 brings the landing cohort back when the switch is thrown to `integrated`; until a
# roller writes that record, the target refuses rather than pass. At rust-only nothing calls it: `make land` skips it, cohort-gate.sh notes it.
cohort-landing: ## [maps] the landing cohort a GATED landing owes at the port switch's `integrated` (feature 386, 444 FR-023): REFUSES - no roller writes its dev/cohort-log/ record since the Python driver was deleted (444 T39); at rust-only nothing owes it (449 T223)
	@printf 'cohort-landing: REFUSED - no landing cohort can be rolled. The Python driver that rolled it and wrote its dev/cohort-log/ record is deleted (feature 444 T39), and `make cohort` (the Rust driver) writes no record `l7r-gate cohort check` reads.\nThe port switch stands at %s. At rust-only no landing owes the cohort (444 FR-023) and nothing runs this; at integrated a landing owes it, so a roller writing that record is owed before one can land (or the switch goes back to rust-only: make switches).\n' "$$("$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" cohort port)" >&2; exit 2

hamlet:         ## [maps] roll one pool hamlet with the Rust driver (feature 444 T42): its map and record written beside the spec, the wall time printed   SPEC=pool/hamlets/<name>/<name>.spec.json
	@if [ -z "$(SPEC)" ]; then printf 'make hamlet: SPEC=pool/hamlets/<name>/<name>.spec.json is required\n' >&2; exit 2; fi
	@$(HAMLET_RUN) "$(abspath $(SPEC))"

placement-stages: ## [maps] the stage-by-stage walk-through page - FROZEN (feature 444 amendment 11): generated from the deleted Python engine, kept as the Rust port's reference until a page from the Rust driver replaces it
	@printf 'placement-stages: FROZEN - dev/placement-stages-frozen/hamlet-placement.html was generated on 2026-10-31 from main'\''s Python hamlet engine, since deleted, and is kept as the temporary reference the Rust port is judged against (feature 444 amendment 11, FR-024 part 1); nothing regenerates it until a page from the Rust driver replaces it\n'

placement-stages-if-classes: ## [maps] {internal} a no-op since the walk-through page froze (feature 444 amendment 11); sync-in still calls it
	@:

pool-index:     ## [maps] write the pool index, pool/index.html: every map of both trees, grouped by tree and tier, from the Rust pool walk (449 T220); rewritten only when it differs, and a folder the walk cannot classify named
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" pool index

# THE WALK IS THE STALENESS CHECK (feature 449 T220): the index is composed from one listing of each pool directory and written only when
# it differs from the page on disk, so this is the same command as pool-index, quiet; the name stays because sync-with-main.sh calls it.
# It runs the gate binary there is, stale or not (L7R_GATE_STALE_OK): sync-in runs on every prompt, and a merge that moved a gate source
# would otherwise rebuild l7r-gate there (tens of seconds) for an index; 0.02 s with the binary built (measured 2026-11-19). A stale
# binary older than the `pool` verb fails, and only then is the gate built.
pool-index-if-stale: ## [maps] {internal} the pool index, written only when it differs (sync-in calls it)
	@g="$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh"; L7R_GATE_STALE_OK=1 "$$g" pool index >/dev/null 2>&1 || "$$g" pool index >/dev/null

compound:       ## [maps] compose a Mode A compound sheet from its feet-based program, drawn whole by the compound generator (Rust since 449 T152, `l7r-mode-a`) - a starting point the GM then refines by hand   SPEC=<map>.compound.json
##  SPEC=<map>.compound.json  the program; the sheet, its picture and its page are written beside it as <map>.svg, .png, .html
	@if [ -z "$(SPEC)" ]; then printf 'make compound: SPEC=<map>.compound.json is required - e.g. make compound SPEC=pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a compound "$(SPEC)"

# MAIN'S RENDERS, THE RUST ONLY (feature 449 T222): every live map drawn or served through the generation cache, then the pool index, then
# the record's site built when its stamp differs from its inputs - the three duties render_cache.py held, its log's three lines. A map that
# fails stops neither later step (the driver draws every other map first; the index and the site do not depend on one map), and the
# recipe exits 1 at the end, so the runner's status file says FAILED. `guard` keeps it out of main's tree but under DIAGRAM_ALLOW_MAIN=1,
# which sync-with-main.sh sets under the sync lock. It renders the tree it runs in: render_cache's ARGS (--skill-dir/--main-repo) are taken
# only where they name that tree - a clone's sync-with-main.sh not yet merged past T222 still passes main's own path - and refused otherwise.
render-sync: guard ## [maps] {internal} regenerate MAIN's renders (called by sync-with-main.sh; not for hand use): every live map, the pool index, the record site
	@here="$$(cd "$$(git rev-parse --show-toplevel)" && pwd -P)"; set -- $(ARGS); while [ $$# -gt 0 ]; do \
	  case "$$1" in --skill-dir|--main-repo) [ "$$(cd "$${2:-/nonexistent}" 2>/dev/null && pwd -P)" = "$$here" ] || { printf 'render-sync: ARGS names %s %s, not this tree - it renders the tree it runs in (feature 449 T222): cd there and run it with no ARGS\n' "$$1" "$${2:-<nothing>}" >&2; exit 2; }; shift 2 ;; \
	  *) printf 'render-sync: ARGS holds %s, which it does not take - it renders the tree it runs in (feature 449 T222): cd there and run it with no ARGS\n' "$$1" >&2; exit 2 ;; esac; done
	@g="$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh"; root="$$(git rev-parse --show-toplevel)"; failed=""; \
	"$$g" pool map --all || failed="$$failed a map (above)"; \
	"$$g" pool index || failed="$$failed the pool index"; \
	if site=$$("$$g" record site-stale --root "$$root"); then printf "render-sync: the record's site %s (research/site/index.html)\n" "$$site"; else failed="$$failed the record's site"; fi; \
	[ -z "$$failed" ] || { printf 'render-sync: FAILED -%s; every other step ran\n' "$$failed" >&2; exit 1; }

# ---- cheap: they read a recorded artifact ----

pack-audit:     ## [diagnostics] empty space and geometry in a HAND-DRAWN Mode A compound SVG (Rust since 449 T175, `l7r-mode-a`)   ARGS=<in.svg>
##  ARGS=<in.svg>  the Mode A compound SVG to measure
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a pack-audit $(ARGS)

sheet-render:   ## [maps] render a hand-drawn Mode A sheet with its captions placed by the ONE placer (feature 286; Rust since 449 T152, `l7r-mode-a`)   SHEET=<svg> OUT=<png>
##  SHEET=<svg>         the hand-drawn sheet (its drawing and its captions' declarations)
##  OUT=<png>           the picture to write
	@if [ -z "$(SHEET)" ] || [ -z "$(OUT)" ]; then printf 'make sheet-render: SHEET=<svg> and OUT=<png> are required - e.g. make sheet-render SHEET=pool/<tier>/<map>/<map>.svg OUT=/tmp/<map>.png\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a sheet-render "$(SHEET)" "$(OUT)"

page-lit:       ## [diagnostics] light ONE class on a map's page and report which classes' pixels change   MAP=<page.html> CLASS="<key>" [VECTOR=1] [OUT=lit.png]
##  the reviewer's page measurement (feature 231): raster mode at the opening view, VECTOR=1 past the switch (Rust since 449 T150, `l7r-mode-a`, the browser `l7r-browser lit`)
	@if [ -z "$(MAP)" ] || [ -z "$$CLASS" ]; then printf 'make page-lit: MAP=<page.html> CLASS="<class key>" are required - e.g. make page-lit MAP=pool/hamlets/kuwabata/kuwabata.html CLASS="mulberry dike"\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a page-lit "$(MAP)" "$$CLASS" $(if $(VECTOR),--vector,) $(if $(OUT),--out "$(OUT)",)

picture-diff:   ## [diagnostics] two renders compared: the differing share, the max delta, the bbox, and whose ink   A=<png|svg> B=<png|svg> [PAGE=<the new .html>]
##  the reviewer's picture measurement (feature 231); an SVG argument is rendered by the engine's own rasterizer,
##  and PAGE names the rendered page whose own id map says which class each differing pixel lies on (Rust since 449 T150, `l7r-mode-a`)
	@if [ -z "$(A)" ] || [ -z "$(B)" ]; then printf 'make picture-diff: A=<render> B=<render> are required - e.g. make picture-diff A=main.png B=pool/hamlets/kuwabata/kuwabata.svg PAGE=pool/hamlets/kuwabata/kuwabata.html\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a picture-diff "$(A)" "$(B)" $(if $(PAGE),--page "$(PAGE)",) $(if $(SVG),--svg "$(SVG)",)

notes-census:   ## [diagnostics] refresh the derived counts inside each map's notes census block (Rust since 449 T170, `l7r-mode-a`)   M="pool/hamlets/*/*.json"
##  M=<glob>  which manifests to refresh (default: every manifest in both pool trees)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a notes-census $(or $(wildcard $(M)),$(wildcard pool/*/*/*.json) $(wildcard legacy-hand-authored-pool/*/*/*.json))

building-programs: ## [docs] render each declared Mode A type's required-items table into docs/building-programs.md from l7r/diagram/buildings/types.json (feature 254; Rust since 449 T168, `l7r-mode-a`)   CHECK=1: exit 1 if stale
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a building-programs $(if $(CHECK),--check,)

glossary:       ## [docs] assemble interactive/assets/glossary.json from its per-term files, then write research/assets/glossary.js from it - the ONE glossary the map's modals and the record's pages share (features 209, 259)   CHECK=1: exit 1 if either is stale   SPLIT=1: the one-time split into per-term files
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record $(if $(CHECK),check glossary,glossary $(if $(SPLIT),--split,))

footnote-census: ## [docs] count the record's footnotes by kind - cited, grounds, ABSENT, settled. The ABSENT column is the backlog and the only one anybody has to act on (feature 235)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record footnote-census

citations:      ## [docs] the same as `make record` (feature 301: the record's site carries the notes; kept as a name)   CHECK=1: as `make record CHECK=1`
	@$(MAKE) --no-print-directory record $(if $(CHECK),CHECK=1,)

record:         ## [docs] build the record's site, research/site/, from its questions (features 258, 301, 303) - a page per question, a page per section of each half and per tag, the whole record on one page   CHECK=1: build in memory and exit 1 on any refusal, writing nothing
	@$(call TIMED,record,$(if $(CHECK),check,site),"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record $(if $(CHECK),check record,site))
	$(if $(CHECK),,@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record sources mark-filled)

money-conversions: ## [docs] copy gm-assistant's money conversion table into research/assets/money-conversions.json, which the record's build converts each marked amount of money from (feature 413)   CHECK=1: write nothing, exit 1 while the copy is stale
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record money-conversions $(if $(CHECK),--check,)

money-candidates: ## [docs] every amount of money in the record not yet marked for the conversion tooltip, those within 25 years of a built era first; each is marked or passed over with its reason in specs/413-money-tooltip-on-the-record/backfill.md (feature 413)   CHECK=1: exit 1 while one is neither
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record money-candidates $(if $(CHECK),--check,) $(if $(ALL),--all,) $(if $(Q),--stem "$$Q",) $(if $(CONTEXT),--context,)

source-tags-contract: ## [docs] derive research/source-tags.json's values and explanations into the source-applicability agent's contract (feature 305) - run after editing the vocabulary; a test fails while the block is stale   CHECK=1: write nothing, exit 1 while stale
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record source-tags-contract $(if $(CHECK),--check,)

fragment-move:  ## [docs] rename or renumber a question - every file of its stem - and rewrite every pointer to it - the record's own links, about: markers, confusables, the Entry: lines, the code and docs (features 301, 303)   FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html
	@test -n "$(FROM)" -a -n "$(TO)" || { echo "make fragment-move FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html" >&2; exit 2; }
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record fragment-move "$(FROM)" "$(TO)" --root "$$(git rev-parse --show-toplevel)"

# The suites fan out in parallel. A suite that turns out to race is serialized, never retried: a retry hides the race.
hooks-test:     ## [tests] run every tests/hooks/test-*-hooks.sh, and prove each guard still has a companion
	@root=$$(git rev-parse --show-toplevel); gitdir=$$(git rev-parse --path-format=absolute --git-common-dir); fail=""; n=0; skipped=0; \
	work=$$(mktemp -d); trap 'rm -rf "$$work"' EXIT; \
	roster=$$(for h in $$root/scripts/hooks/*-hooks.sh $$root/scripts/gates/review-gate.sh $$root/scripts/gates/entry-gate.sh $$root/scripts/gates/claims-gate.sh $$root/scripts/gates/cohort-gate.sh $$root/scripts/gates/plan-gate.sh $$root/scripts/gates/closing-checks.sh $$root/scripts/gates/l7r-gate.sh $$root/scripts/sync-with-main.sh $$root/scripts/land-tooling.sh $$root/scripts/state-sync.sh $$root/scripts/hooks/l7r-guard.sh $$root/tests/hooks/parts.sh $$(find $$root/tests/hooks -maxdepth 1 -lname guard-shim.sh | sort); do basename $$h; done | sort -u); \
	: "A SUITE'S STAMP IS A SET OF KEYS (feature 451 T304): one key a suite in the common git directory let each tree's green run replace the key another tree's content went green at, so trees run in turn reran each other's suites; its stamp is one line a kept key, newest first (hookrun.sh, HOOKS_STAMP_KEEP), a fresh trace names the key it was kept at, and a suite is skipped at any kept key with its rendering"; \
	: "THE GUARD BUILT FIRST, OR NOTHING RUNS (feature 451 T449): with no fresh guard binary every fixture that execs it failed for a cause no suite named (2026-11-27: test-parts.3.sh 14 FAIL, an exec of an empty path; test-context-cap-hooks.sh on the old rules), so the run stops on the build log's first error; this first call builds outside any hook, so it takes 600 s, not a hook's 45 s, and a loaded machine does not cut it"; \
	gfresh=$$(L7R_GUARD_BUILD_SECS=600 L7R_GUARD_PRINT_FRESH=1 "$$root/scripts/hooks/l7r-guard.sh" 2> "$$work/guard-fresh" </dev/null) || { echo "hooks-test: the guard does not build - $$(head -1 "$$work/guard-fresh")" >&2; exit 1; }; \
	traced=$$(if [ -z "$(HOOKS_ALL)" ]; then "$$root/scripts/hooks/l7r-guard.sh" trace fresh "$$gitdir" "$$root" $$roster 2>/dev/null; fi); \
	kept_at() { [ -n "$$1" ] || return 1; for f in "$$gitdir/hooks-test/rendered/$$b@$$1.jsonl" "$$gitdir/hooks-test/rendered/$$b".[0-9]*"@$$1.jsonl"; do [ -f "$$f" ] && return 0; done; return 1; }; \
	export HOOKS_SHIM="$$("$$root/scripts/hooks/l7r-guard.sh" trace shim "$$gitdir" 2>/dev/null)" HOOKS_ROOT="$$root"; \
	: "THE LAUNCHERS' BINARIES BUILT AND CHECKED ONCE A RUN (feature 449 T205): each call of l7r-gate.sh or l7r-guard.sh walked its Rust sources to see whether to build, about 1,400 and 2,000 paths, and under the read recorder each path was a line of the suite's log - sync-with-main's run wrote 1,260,877 lines; with the fresh binaries named here a call skips the walk and hookrun.sh records the sources once a suite (an empty gate name, where its build failed, leaves every call to walk as before; the guard's is never empty here, the run having stopped above, 451 T449)"; \
	export L7R_GATE_FRESH="$$(L7R_GATE_PRINT_FRESH=1 "$$root/scripts/gates/l7r-gate.sh" 2>/dev/null </dev/null)" L7R_GUARD_FRESH="$$gfresh"; \
	: "THIS TREE'S STORE OF RENDERED MESSAGES (feature 451 T281), under its own git directory: a green job writes it (hookrun.sh), the check below reads it"; \
	HOOKS_MESSAGES="$$("$$root/scripts/hooks/l7r-guard.sh" messages store "$$root")"; export HOOKS_MESSAGES; [ -n "$$HOOKS_MESSAGES" ] || { echo "hooks-test: no store of rendered messages (l7r-guard messages store $$root said nothing)" >&2; exit 1; }; \
	: "A SPLIT SUITE'S SHARDS ARE KEYED TOO (feature 451 T20, plan D17): deps seeds a guard's key from test-<name>.sh, which a split suite no longer has, so each shard is keyed as a name of its own and the suite's sha is its guard's key and its shards' keys hashed together - an edited shard reruns the suite"; \
	shards=$$(for f in "$$root"/tests/hooks/test-*.[0-9]*.sh; do [ -f "$$f" ] && basename "$$f"; done); \
	keys=$$("$$root/scripts/hooks/l7r-guard.sh" deps --keys $$roster $$shards); \
	owned=$$(for b in $$roster; do t=test-$${b%.py}; case $$t in *.sh) ;; *) t=$$t.sh ;; esac; printf '%s ' "$$t"; done); \
	pairs=$$("$$root/tests/hooks/hookrun.sh" --jobs "$$root/tests/hooks" $$owned); \
	for h in $$root/scripts/hooks/*-hooks.sh $$root/scripts/gates/review-gate.sh $$root/scripts/gates/entry-gate.sh $$root/scripts/gates/claims-gate.sh $$root/scripts/gates/cohort-gate.sh $$root/scripts/gates/plan-gate.sh $$root/scripts/gates/closing-checks.sh $$root/scripts/gates/l7r-gate.sh $$root/scripts/sync-with-main.sh $$root/scripts/land-tooling.sh $$root/scripts/state-sync.sh $$root/scripts/hooks/l7r-guard.sh $$root/tests/hooks/parts.sh $$(find $$root/tests/hooks -maxdepth 1 -lname guard-shim.sh | sort); do \
	  b=$$(basename $$h); case $$b in test-*) continue ;; esac; case " $$seen " in *" $$b "*) continue ;; esac; seen="$$seen $$b"; \
	  t=test-$${b%.py}; case $$t in *.sh) ;; *) t=$$t.sh ;; esac; \
	  jobs=$$(printf '%s\n' "$$pairs" | awk -v t="$$t" '$$1 == t { $$1 = ""; print substr($$0, 2) }'); \
	  if [ "$$jobs" = "!" ]; then fail="$$fail $$b"; continue; fi; \
	  if [ -z "$$jobs" ]; then \
	    printf '\n\033[1mGUARD WITHOUT A TEST: %s has no tests/hooks/%s, nor its shards tests/hooks/%s.<k>.sh\033[0m\n' "$$b" "$$t" "$${t%.sh}"; \
	    printf 'A guard ships with its companion. Without one, nothing can tell whether it still\n'; \
	    printf 'fires - or whether it fires on correct work, which is the more expensive failure.\n\n'; \
	    fail="$$fail $$b"; continue; \
	  fi; \
	  : "A SUITE IS SKIPPED ONLY WITH ITS MESSAGES KEPT (feature 451 T170): the budget check reads each suite's last green renderings, so a suite with none reruns"; \
	  : "... AND KEPT AT THE KEY ITS STAMP HOLDS (feature 451 T281): the stamps are every worktree's, the store of renderings each tree's own (one store in the common git directory let a tree's run replace another's renderings, and judged a tree on a guard only another holds), so a skipped suite's renderings are the ones a green job left beside the stamp, named by its key (hookrun.sh), which messages gather copies into this tree's store after the fan-out"; \
	  stf="$$gitdir/hooks-test/$$b"; st=$$(printf '%s\n' "$$traced" | awk -v b="$$b" '$$1 == b { print $$2; exit }'); \
	  if [ -n "$$st" ] && kept_at "$$st" && { [ "$$jobs" = "$$t" ] || [ "$$(awk -v k="$$st" '$$1 == k { $$1 = ""; print substr($$0, 2); exit }' "$$stf" 2>/dev/null)" = "$$jobs" ]; }; then skipped=$$((skipped+1)); printf '%s %s\n' "$$b" "$$st" >> "$$work/held"; continue; fi; \
	  sha=$$(printf '%s\n' "$$keys" | awk -v b="$$b" '$$1 == b { print $$2 }'); mkdir -p "$$gitdir/hooks-test"; \
	  [ -n "$$sha" ] || sha=unkeyed-$$RANDOM; \
	  if [ "$$jobs" != "$$t" ]; then sha=$$( { echo "$$sha"; for j in $$jobs; do printf '%s\n' "$$keys" | awk -v b="$$j" '$$1 == b { print $$2 }'; done; } | sha256sum | cut -c1-16); fi; \
	  if [ -z "$(HOOKS_ALL)" ] && kept_at "$$sha" && awk -v k="$$sha" '$$1 == k { f = 1 } END { exit !f }' "$$stf" 2>/dev/null; then skipped=$$((skipped+1)); printf '%s %s\n' "$$b" "$$sha" >> "$$work/held"; continue; fi; \
	  printf '%s\n' "$$b" >> "$$work/held"; \
	  n=$$((n+1)); for j in $$jobs; do printf '%s %s %s\n' "$$b" "$$j" "$$sha" >> "$$work/todo"; done; \
	  [ "$$jobs" = "$$t" ] || printf '%s %s %s\n' "$$b" "$$sha" "$$jobs" >> "$$work/close"; \
	done; \
	"$$root/tests/hooks/hookrun.sh" --orphans "$$root/tests/hooks" $$owned || fail="$$fail shard-without-its-suite"; \
	: "THE LONGEST SUITES START FIRST (feature 449 T125): in roster order the run ended on idle-tests, 36 s started 19.6 s in; ordered by each suite's last seconds (hookrun.sh keeps them in .git/hooks-test/<suite>.s), a suite never timed first, the full run measured 52.4 s against 59.6 s (2026-11-12)"; \
	: "THE USER-LEVEL SELF-TEST RUNS BESIDE THE SUITES (feature 449 T122): run after the fan-out it added its 3.8 s to every full run alone, against a wall of about 35 s (2026-11-17); its pass, its failure and its stamp are read after the fan-out as before"; \
	uh="$$HOME/.claude/hooks/test-missing-program-hook.sh"; mph=""; \
	uk=$$(cat "$$uh" "$$HOME/.claude/hooks/missing-program-hook.sh" 2>/dev/null | sha256sum | cut -c1-16); \
	if [ -f "$$uh" ] && [ -z "$(HOOKS_ALL)" ] && [ "$$(cat "$$gitdir/hooks-test/missing-program-hook" 2>/dev/null)" = "$$uk" ]; then skipped=$$((skipped+1)); \
	elif [ -f "$$uh" ]; then { bash "$$uh" > "$$work/missing-program-hook.log" 2>&1; echo $$? > "$$work/missing-program-hook.exit"; } < /dev/null & mph=$$!; fi; \
	if [ -s "$$work/todo" ]; then \
	  while read -r b t sha; do k=$${t%.sh}; k=$${k##*.}; case $$k in ''|*[!0-9]*) id=$$b ;; *) id=$$b.$$k ;; esac; printf '%s %s %s %s\n' "$$(cat "$$gitdir/hooks-test/$$id.s" 2>/dev/null || echo 9999)" "$$b" "$$t" "$$sha"; done < "$$work/todo" | sort -s -k1,1 -rn | cut -d' ' -f2- > "$$work/todo.sorted" && mv "$$work/todo.sorted" "$$work/todo"; \
	  mkdir -p "$$gitdir/hooks-test"; \
	  ns=$$(wc -l < "$$work/todo"); [ "$$ns" -gt $(HOOKS_JOBS) ] && ns=$(HOOKS_JOBS); pm=$$(( $(CPU_COUNT) / (ns > 0 ? ns : 1) )); \
	  [ "$$pm" -gt 8 ] && pm=8; [ "$$pm" -lt 1 ] && pm=1; export PARTS_MAX=$$pm; \
	  : "KILLED RUNNERS' LEFTOVERS SWEPT ONCE A RUN, BEFORE THE FAN-OUT (feature 451 T372): each job globbed the whole temp directory for them, 16.5 ms a suite under a /tmp of 5,443 entries, 4,051 suite runs on 2026-11-26; the jobs are told (--swept) and list nothing"; \
	  : "A FAILED SUITE'S WHOLE LOG OUTLIVES THE RUN (feature 451 T414): this work directory goes on exit, and with it the only copy of the red state-sync run's log of 2026-11-26, so hookrun.sh keeps each red job's log under the common git directory (l7r-hooks-failed/), its name in the FAIL line below and in the suite's event line; the sweep bounds them to HOOKS_FAILED_KEEP, once, before any job keeps one"; \
	  "$$root/tests/hooks/hookrun.sh" --sweep "$$gitdir"; xargs -P $(HOOKS_JOBS) -L1 -a "$$work/todo" "$$root/tests/hooks/hookrun.sh" --swept "$$work" "$$gitdir" || true; \
	  if [ -s "$$work/close" ]; then while read -r b sha js; do "$$root/tests/hooks/hookrun.sh" --close "$$work" "$$gitdir" "$$b" "$$sha" $$js; done < "$$work/close"; fi; \
	  : "EACH SUITE'S PHASE LINE, ONE CALL FOR ALL (feature 451 T153; the GM 2026-11-22: \"make the hook suites measure their time so they won't be missing\"): hookrun.sh leaves each job's span, and the one Phase writer writes them all in one process (one a suite cost 6.9 s for 57, 2026-11-20); they feed the task time breakdown (make task-time, 451 T243)"; \
	  spans=$$(for f in "$$work"/*.span; do [ -f "$$f" ] || continue; read -r a b c < "$$f"; id=$$(basename "$$f" .span); kl=$$(cat "$$work/$$id.kept" 2>/dev/null); printf 'suite:%s:%s:%s:%s%s ' "$$a" "$$b" "$$c" "$$id" "$${kl:+:$$kl}"; done); \
	  [ -z "$$spans" ] || "$$root/scripts/gates/l7r-gate.sh" measure event-log phase --root "$$root" --src hooks $$spans >/dev/null 2>&1 || true; \
	  for rc in "$$work"/*.rc; do \
	    [ -f "$$rc" ] || continue; \
	    b=$$(basename "$$rc" .rc); \
	    if [ "$$(cat "$$rc")" != ok ]; then \
	      kl=$$(cat "$$work/$$b.kept" 2>/dev/null); printf '\n\033[1mHOOK TESTS FAILED: %s%s\033[0m\n' "$$b" "$${kl:+ (whole log kept: $$gitdir/$$kl)}"; sed 's/^/  /' "$$work/$$b.log"; fail="$$fail $$b"; \
	    fi; \
	  done; \
	fi; \
	if [ -n "$$mph" ]; then wait "$$mph"; \
	  if [ "$$(cat "$$work/missing-program-hook.exit" 2>/dev/null)" = 0 ]; then n=$$((n+1)); printf '%s' "$$uk" > "$$gitdir/hooks-test/missing-program-hook"; \
	  else kl=$$("$$root/tests/hooks/hookrun.sh" --keep "$$gitdir" missing-program-hook "$$work/missing-program-hook.log" 2>/dev/null); printf '\n\033[1mHOOK TESTS FAILED: missing-program-hook (user-level, %s)%s\033[0m\n' "$$uh" "$${kl:+ (whole log kept: $$gitdir/$$kl)}"; sed 's/^/  /' "$$work/missing-program-hook.log"; fail="$$fail missing-program-hook"; fi; \
	fi; \
	if ! "$$root/scripts/gates/l7r-gate.sh" check tool-signals; then fail="$$fail check-tool-signals"; fi; \
	if ! "$$root/scripts/gates/l7r-gate.sh" check rust-tooling --root "$$root"; then fail="$$fail rust-tooling"; fi; \
	: "NO SHELL FILE PIPES INTO AN EARLY-EXIT GREP (feature 451 T253): under pipefail the writer died of SIGPIPE when grep -q exited on its match, and a present line read absent - every suite and script, here where no unchanged suite skips it"; \
	if ! "$$root/scripts/gates/l7r-gate.sh" check pipe-race --root "$$root"; then fail="$$fail pipe-race"; fi; \
	: "EVERY GUARD MESSAGE WITHIN ITS BUDGET AND REVIEWED (feature 451 T170): the suites' renderings against dev/guard-messages.tsv"; \
	if ! "$$root/scripts/hooks/l7r-guard.sh" messages gather "$$gitdir/hooks-test/rendered" "$$HOOKS_MESSAGES" "$$work/held"; then fail="$$fail guard-messages-store"; fi; \
	if ! "$$root/scripts/hooks/l7r-guard.sh" messages check "$$HOOKS_MESSAGES" "$$root/dev/guard-messages.tsv"; then fail="$$fail guard-messages"; fi; \
	if [ -n "$$fail" ]; then printf '\n\033[1mhooks-test FAILED:%s\033[0m\n\n' "$$fail"; exit 1; fi; \
	"$$root/scripts/gates/l7r-gate.sh" stamp --write hooks; \
	printf 'hooks-test: %s guard suites green, %s unchanged since they last went green (hooks area stamped)\n' "$$n" "$$skipped"; \
	ran=$$(for s in "$$work"/*.s; do [ -f "$$s" ] && printf '%s %s\n' "$$(cat "$$s")" "$$(basename "$$s" .s)"; done | sort -rn | awk '{printf "%s%s %ss", (NR>1?", ":""), $$2, $$1}'); \
	[ -z "$$ran" ] || printf 'hooks-test: ran %s\n' "$$ran"

guard-messages: ## [tests] the guard messages the suites rendered that owe a review or a cut (451 T170); BUNDLE=1 writes message-check's units; KEY= VERDICT=PASS|FAIL BY="<agent id>" [OVER="<why>"] records a verdict, VERDICT=BASELINE BY="<its measured characters a session>" leaves a newly rendered wording unreviewed under T177's break-even (451 T174); REHEAD=1 writes every stored head again with its paths masked, no other column moved   [BUNDLE=1] [KEY= VERDICT= BY= OVER=] [REHEAD=1]
	@root=$$(git rev-parse --show-toplevel); g="$$root/scripts/hooks/l7r-guard.sh"; c=$$("$$g" messages store "$$root") || exit 1; r="$$root/dev/guard-messages.tsv"; \
	if [ -n "$$KEY" ]; then "$$g" messages verdict "$$c" "$$r" "$$KEY" "$(VERDICT)" "$$BY" $${OVER:+"$$OVER"}; \
	elif [ -n "$(BUNDLE)" ]; then mkdir -p /tmp/l7r-check/guard-messages && "$$g" messages owed "$$c" "$$r" /tmp/l7r-check/guard-messages/MANIFEST.md; \
	elif [ -n "$(REHEAD)" ]; then "$$g" messages rehead "$$c" "$$r"; \
	else "$$g" messages check "$$c" "$$r"; fi

inline-census:  ## [tests] phase 1's share of feature 449's second census: every inline Python site under scripts/hooks/ and tests/hooks/, each under a group FR-001 names; a site outside them fails
	@bash "$$(git rev-parse --show-toplevel)/scripts/measure/inline-census.sh"

guard-edit: export GUARD_WHY = $(WHY)
guard-edit:     ## [project] permit edits to one guard file for an hour, the reason recorded in the guard log - the root Makefile takes no marker comment (feature 170 amendment 1)   FILE=Makefile WHY="<why the edit is legitimate>"
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" permit grant "$(abspath $(FILE))" "$$GUARD_WHY"

# D9's per-agent permit (feature 451 T13): the key is the clone's top level, not a bare `context-cap:<id>`, so the permit store is found.
context-ok: export CONTEXT_WHY = $(WHY)
context-ok:     ## [project] let one builder past the context cap for an hour, after its resume was escaped with CONTEXT_OK - each call it lets through recorded in the guard log (feature 451 T13, plan D9)   AID=<agent id> WHY="<why this builder goes on past the cap>"
	@[ -n "$(AID)" ] && [ -n "$$CONTEXT_WHY" ] || { echo 'Usage: make context-ok AID=<agent id> WHY="<why this builder goes on past the cap>"' >&2; exit 2; }
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" permit grant "$$(git rev-parse --show-toplevel)/context-cap:$(AID)" "$$CONTEXT_WHY"

# The sweep a prompt starts once a day (rust/guard/src/guards/scratch_sweep_hooks.rs), run now; DRY=1 takes no lock and stamps nothing.
scratch-sweep:  ## [project] remove finished sessions' scratch under /tmp/claude-<uid> now - idle 3 days, held by no live process, never this session's (449 T103), and the clones' review snapshots idle a week and dead .gencache stores (451 T246); DRY=1 lists what it would remove and the total   [DRY=1]
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep $(if $(DRY),dry,now)

# THE DISK AND THE BUILD CACHE (451 T158, rust/guard/src/guards/scratch_sweep_hooks/disk.rs; the GM 2026-11-22: "make sure that we clean
# up after ourselves in terms of the file system"): the cache's share of the sweep alone, idle past HOURS (12, a GUESS knob), never while a
# cargo or rustc process runs; DISK_FLOOR, the first line of make done, make land and make closing-checks, refuses below the free-space
# floor (L7R_DISK_FLOOR_GB, 15, a GUESS knob), naming the largest build directories and the scratch worktrees; DISK_OK="<reason>" escapes,
# recorded. make land, once it lands, removes the landed tasks' own /tmp/t<N> scratch (`landed`; left to the age rule where another
# feature started a task of that number within the day) and names every scratch worktree (a clone's worktree outside /diagram/.clones)
# with the command removing it. The day's sweep (make scratch-sweep, and a session's first prompt) takes /tmp/t<N> and /tmp/tmp.* idle a
# day, task outputs idle a day, and past the cache's size budget (L7R_CACHE_BUDGET_GB, 100) what in the cache is not in use, whatever its age.
# THE BUDGET HELD (451 T245, sweep/evict.rs): past the budget, live trees' profiles idle HOURS go, an idle tree's first and the least
# recently built first, until the cache is within it; a removed worktree's build directory goes with it (no idle wait); below
# L7R_DISK_FREE_PCT (20, a GUESS knob) of the disk free, a prompt starts the same eviction (at most hourly) and the next prompt says
# what it freed.
cache-clean:    ## [project] free the build cache (~/.cache/l7r-cargo-target): a build directory proven dead (no code path builds into its name, every tree its dep-info names gone), what at its root is no build directory once idle (a loose file, a shell of cargo's markers alone; 451 T523), past the budget (L7R_CACHE_BUDGET_GB, 100) live trees' profiles idle HOURS (12), an idle tree's first, and a crate's variants past its newest 16, never while a build runs; and inside every live profile no process holds, a crate's builds unread L7R_CACHE_STALE_HOURS (48) before the profile's last use, the newest of each kind kept, a build elsewhere or not (451 T515); names the scratch worktrees to remove (451 T158, T245)   [DRY=1] [HOURS=<n>]
	@$(if $(HOURS),L7R_CACHE_IDLE_HOURS="$(HOURS)" ,)"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep $(if $(DRY),cache-dry,cache) </dev/null
# THE AUDIT REGISTER (451 T259): one entry per optimization or procedure that costs time or tokens, each with its measurement and its
# falsifier; `make static` and the push refuse a new guard module, threshold, gate-chain target or agent file that no entry names.
audits:         ## [project] the audit register (dev/audits/): every entry, the overdue first by its cadence, each with its falsifier, threshold and last audit (451 T259)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check audit-register --list --root "$$(git rev-parse --show-toplevel)"
disk-audit:     ## [project] every place this container writes - the build cache by tree, /tmp/claude-<uid> by session, /tmp/l7r-*, the rest of /tmp, this project's transcripts, the guard log, the clones, the mirror, ~/.cache, and within the clones their tasks' .git/t<N>, handoff folders, review snapshots and .gencache - each with its size, owner, age and budget, the total against the disk, the host's podman storage named as the host's, and what the low-disk eviction would free now; removes nothing (451 T245, T246)
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep audit </dev/null
done land closing-checks: export DISK_OK := $(DISK_OK)
# THE FLOOR BUILDS A NEVER-BUILT GUARD (451 T286): its call is often a tree's first of its own guard binary (hooks run the mirror's), and
# past the hook limit (45 s, passed by a cold build at load 56 on 2026-11-26) it died with none built; L7R_GUARD_COLD_SECS (600, a GUESS
# knob: ten times the slowest cold build the guard suite has measured, 60.0 s on 2026-11-11) bounds the wait and the build instead.
DISK_FLOOR = $(if $(DISK_OK),$(LOGESCAPE) DISK_OK "$$DISK_OK",@L7R_GUARD_COLD_SECS="$${L7R_GUARD_COLD_SECS:-600}" "$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep floor </dev/null)
SCRATCH_TREES = "$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep trees </dev/null

guard-log:      ## [project] the guard firings, listed - GUARD=<name> SINCE=YYYY-MM-DD EVENT=blocked|rewrote|escaped|reminded FULL=1
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure guard-log $(if $(GUARD),--guard $(GUARD)) $(if $(SINCE),--since $(SINCE)) $(if $(EVENT),--event $(EVENT)) $(if $(FULL),--full)

audit:          ## [project] how the gate has actually been used - every run and every bypass
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure audit runs
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure audit guards
	@printf '\033[1mFiles past the ~1,000-line bar\033[0m (constitution X clause 13 - GATED since feature 173)\n'
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check file-scale --list .
	@printf '  A file over the bar FAILS `make lint`, and so `make done` and the push. The one way out\n'
	@printf '  is clause 13'"'"'s ordered-data carve-out, stated IN the file as `FILE_SIZE_OK: <reason>` and\n'
	@printf '  listed above with its reason - a carve-out nobody can enumerate is one nobody revisits.\n'
	@printf '  If the bulk is a roster restating code elsewhere, clause 14 says DERIVE it, do not split.\n\n'
	@printf '\033[1mFiles allowed to carry a conflict triple\033[0m (feature 241 - the file-level exemption)\n'
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check conflict --list .
	@printf '  Declaring it makes the WHOLE file invisible to the hook and to the backstop, so a real\n'
	@printf '  conflict committed into one of these is caught by nothing - which is why the reason must be\n'
	@printf '  argued, must open its line, and is listed here with the file that claims it.\n\n'
	@printf '\033[1mClass entries with no research section\033[0m (feature 234 - the declared-silence form)\n'
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" registry silent --root "$$(git rev-parse --show-toplevel)"
	@printf '  A broken heading and a deliberate silence are told apart by this FORM, never by a non-match.\n\n'
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure audit claims

docs:           ## [project] regenerate docs/make-targets.html from this Makefile's own `##` lines
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" make-docs . --write

help:           ## [project] list every target with its one-line purpose
	@printf '\n\033[1mOperations\033[0m - everything runs through one of these.\n\n'
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort | awk -F'\t' '{printf "  \033[1m%-18s\033[0m %s\n", $$1, $$2}'
	@cost=$$("$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure gatecost done 2>/dev/null); \
	 printf '\nCheapest first: quick | reference | done (NOT the quick one) | done FULL=1'; \
	 [ -n "$$cost" ] && printf '   -   `make done` median %s s over its recent recorded runs (`make audit`)' "$$cost"; \
	 printf '\n'

# ---- the push ----
ci-status:      ## [project] the delta, the route and a gated push's conditions   ROUTE=1 -> just DIRECT|GATED
##  ROUTE=1  print just DIRECT|GATED instead of the whole condition table
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" ci status $(if $(ROUTE),--route,)
engine-key:      ## [project] the content hash the gate and the push key on   REF=<commit>
##  REF=<commit>  which commit to key (default: HEAD)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" delta key $(or $(REF),HEAD)

gated-check:    ## [project] {internal} a gated push may land: its conditions, refused unless each holds. Called by sync-with-main.sh
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" ci gated-check

LOGRUN = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" log run

RUNSTATS = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure runstats
# A STEP TIMED INTO ITS PHASE LINE (feature 451 T153; the GM 2026-11-22: "we want everything measured so we know where our time goes"):
# $(call TIMED,<src>,<step>,<command>) runs the command, then hands its span and exit to the one Phase writer, and exits as it did
# (its lines feed the task time breakdown, make task-time, 451 T243)
TIMED = t0=$$(date +%s.%N); $(3); rc=$$?; "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure event-log phase --root "$$(git rev-parse --show-toplevel)" --src $(1) "$(2):$$t0:$$(date +%s.%N):$$rc" >/dev/null 2>&1; exit $$rc
COMMIT_RUN_RECORD = bash "$$(git rev-parse --show-toplevel)/scripts/gates/commit-run-record.sh"

LOGBYPASS = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" log bypass '$(MAKECMDGOALS)$(if $(FULL), FULL,)'

LOGESCAPE = @root=$$(git rev-parse --show-toplevel) && bash -c '. "$$0/scripts/hooks/lib/guardlog.sh"; \
  printf "%s" "$$2" | "$$0/scripts/gates/l7r-gate.sh" escape reason-ok >/dev/null || { \
    printf "BLOCKED: %s needs a REASON (two words, eight characters) - it is what a later audit reads.\n" "$$1" >&2; \
    guard_log make blocked "$$2" "$$1-no-reason"; exit 2; }; \
  guard_log make escaped "$$2" "$$(printf "%s" "$$1" | tr "[:upper:]_" "[:lower:]-")"' "$$root"

HOOKS_JOBS ?= $(shell [ "$(CPU_COUNT)" -lt 8 ] && echo "$(CPU_COUNT)" || echo 8)

QUICK_BUDGET = 60

page-check:     ## [tests] write the `page` and `browser` stamps - what an asset edit owes at push (its Python tests were deleted, feature 449 FR-001b)
	@root=$$(git rev-parse --show-toplevel) && "$$root/scripts/gates/l7r-gate.sh" stamp --write page && "$$root/scripts/gates/l7r-gate.sh" stamp --write browser

fix-yield:      ## [project] did each tooling fix save what it was meant to: its measure's rate before its ruling and since it was made (feature 385 T119)   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make fix-yield: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure fix-yield "$(F)" --root "$$(git rev-parse --show-toplevel)"

tool-yield:     ## [project] every tool measured: how often it runs, how often it changed something, its misfires and what the record cannot see yet (feature 406)   [KIND=guard|target|check|step|review]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure tool-yield --root "$$(git rev-parse --show-toplevel)" $(if $(KIND),--kind "$$KIND")

events-refile:  ## [project] re-file the event-log lines written before 451 T26 under the feature of the task each carries (its dispatch's brief, else its task id), idempotent, its counts printed (feature 451 T26); FROM=<events dir> refiles another directory's logs into this clone's (451 T76); RETASK="<session id> ..." re-books those page sessions' lines, within their log, to the task their brief names (451 T168)   [DRY=1] [FROM=<dir>] [RETASK="<session id> ..."]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure event-log refile --root "$$(git rev-parse --show-toplevel)" $(if $(DRY),--dry-run,) $(foreach s,$(RETASK),--retask $(s)) $(if $(FROM),--dir "$$(git rev-parse --show-toplevel)/.git/l7r-events" --from "$(FROM)",)

task-time:      ## [project] the task time breakdown: each task landed in the window, across features, by category and by make target or program - minutes and blocking minutes, each % of the task and of the window; a landed task's tables carry its whole time, read BACK hours before the window (451 T243); it opens with the window's one table, a line a landed task and the second tier's section, a batch landing booked to no task; SINCE=last runs from the end of the last report SINCE=last made and moves that marker, a plain SINCE= does not (451 T298)   [SINCE=24h|<N>h|last|<ISO UTC>] [UNTIL=<ISO UTC>] [F=<feature>] [BACK=48h]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure task-time --root "$$(git rev-parse --show-toplevel)" --since "$(or $(SINCE),24h)" $(if $(UNTIL),--until "$(UNTIL)",) $(if $(F),--feature "$(F)",) $(if $(BACK),--back "$(BACK)",)

task-progress:  ## [project] the tasks in flight NOW: a block each pool tree's builders - task, tree, minutes since dispatch, context against the 300k cap, the step open at this moment (the open make run and its last finished phase, else a model turn) and their minutes so far by the task time breakdown's categories - a block each landing in flight, a line each page session, free tree and task carried but not landed; reads only (451 T293)   [BACK=<N>h] [AT=<ISO UTC>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure task-progress --root "$$(git rev-parse --show-toplevel)" $(if $(BACK),--back "$(BACK)",) $(if $(AT),--at "$(AT)",)

where-time:     ## [project] where a feature's time went, by task: the time by bucket and the agents by kind (feature 385 T77); BY=tick books each tick-to-tick window (T115); feeds the task time breakdown (make task-time)   F=<feature> [SINCE=<ISO UTC>] [UNTIL=<ISO UTC>] [BY=tick]
	@if [ -z "$(F)" ]; then printf 'make where-time: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure where-time "$(F)" $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(filter tick,$(BY)),--by-tick,)

set-down: export SET_DOWN_WHY = $(WHY)
set-down:       ## [project] set a feature's work down, so a turn may end with tasks open (feature 385 T70); refused while an open task's part B has no arbiter ruling since (405), or while the 7-day usage is under the weekly soft cap (a goal's, where one is still armed) unless the arbiter ruled a set-down ask (GM 2026-10-23, 10-24): F=385 WHY="awaiting the GM on the cohort trend" [SET_DOWN_OK="<reason>"]
	@if [ -z "$(F)" ]; then printf 'make set-down: F=<feature> is required\n' >&2; exit 2; fi
	$(if $(SET_DOWN_OK),$(LOGESCAPE) SET_DOWN_OK "$$SET_DOWN_OK",@:)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" set-down "$(F)"

found-list:     ## [project] a feature's open findings (found.jsonl), numbered - what is not yet filed as a task or settled (405 T29)   F=405
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record found list --feature "$$(ls -d specs/$(F)-* | head -1)"
found-close:    ## [project] close found.jsonl rows: FILED as a task, or SETTLED with a reason (405 T29)   F=405 ROWS=3,7 TASK=T61 | WHY="..."
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record found close --feature "$$(ls -d specs/$(F)-* | head -1)" --rows "$(ROWS)" $(if $(TASK),--task "$(TASK)",) $(if $(WHY),--why "$$WHY",)

task-add: export TASK_TITLE = $(TITLE)
task-add:       ## [project] file a task box (and its plan section) with the next free id: F=385 TITLE="..." [SECTION=<file with {T} for the id>] [RESEARCH=physical] [PERF=1: a performance task, docs/performance-checklist.md's questions appended]; make quick's checks run over what it wrote and a line they newly fail withdrawn and refused (451 T19), escape QUICK_OK="<reason>"
	@if [ -z "$(F)" ]; then printf 'make task-add: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" task-add "$(F)" $(if $(SECTION),--section "$(abspath $(SECTION))",) $(if $(filter physical,$(RESEARCH)),--physical,) $(if $(PERF),--performance,)

tick: export TICK_NOTE = $(NOTE)
tick: export PLAN_REVIEW_OK := $(PLAN_REVIEW_OK)
tick:           ## [project] tick a task: F=188 T=T03 NOTE="what was verified" [BOXES=1 ticks the research boxes]
##  F=<feature>  the feature number or slug - e.g. `188`
##  T=<task>     the task id - e.g. `T03`
##  NOTE=<text>  what was VERIFIED, which is what the tick is asserting
##  BOXES=1      also tick the three physical-research boxes (only legitimate on a `research: physical` task)
##  PLAN_REVIEW_OK=<reason>  tick although the plan has no current CLEAR review (feature 243) - recorded
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" tick "$(F)" "$(T)" --note-from-env $(if $(BOXES),--boxes,)

plan-verdict:   ## [project] {internal} record a plan review - the spec-fidelity SUBAGENT runs this; ARBITER=<trigger> applies the round arbiter's accept past the plan-round cap   F=243 FILE=<json> AS=spec-fidelity | F=<n> ARBITER=<trigger>
##  F=<feature>        the feature number or slug whose plan.md was reviewed
##  FILE=<json>        the reviewer's JSON: plan_sha256, decisions, verdict (feature 243 plan P3)
##  AS=spec-fidelity   who is recording - only the subagent may pass this, and nothing else distinguishes the shells
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan $(if $(ARBITER),arbiter-accept "$(F)" "$(ARBITER)",$(if $(BLOCKS),record-blocks "$(F)",$(if $(TASK),record-task "$(F)" "$(TASK)",record "$(F)")) "$(abspath $(FILE))" --as "$(or $(AS),main)")

plan-delta:     ## [project] the review a plan owes since amendment 11: only its blocks changed since their CLEAR verdict, on a lean bundle (feature 375 FR-043); a found-and-left deferral without its form refused, escape DEFER_FORM_OK="<reason>" (451 T17); the push's spec lint over the feature's every changed file beside it (451 T527)   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make plan-delta: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan delta "$(F)"

plan-section:   ## [project] print exactly a task's plan sections (its every own heading, a bundle heading naming it) from plan.md, or plan-done.md for an archived task; CITED=1 adds the sections they name by task id, one level - what a builder reads in place of grep or sed over the plan (451 T501)   T=<task[,task]> [F=<feature>, default SPECIFY_FEATURE] [CITED=1]
	@if [ -z "$(or $(F),$(SPECIFY_FEATURE))" ] || [ -z "$(T)" ]; then printf 'make plan-section: T=<task[,task]> and F=<feature> (or SPECIFY_FEATURE) are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan section "$(or $(F),$(SPECIFY_FEATURE))" "$(T)" $(if $(CITED),--cited,)

plan-archive:   ## [project] move a plan's finished sections (every task ticked, CLEAR) into plan-done.md, which no review reads (feature 375 FR-044), and the ticked tasks into tasks-done.md (449 T142) - the tick does both; this runs it by hand   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make plan-archive: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan archive "$(F)"

check-closed:   ## [project] close the checks in flight on a page or pop-up whose agent went silent (the freeze names it)   SUBJECT=q:0105|modal:sheet/bath REASON="<why>" [AGENT=<id> a check you stopped yourself, closed though not silent]
	@if [ -z "$$SUBJECT" ] || [ -z "$$REASON" ]; then printf 'make check-closed: SUBJECT=<q:NNNN or modal:<registry>/<slug>> and REASON="<why>" are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh checks-close "$$SUBJECT" "$$REASON" $(if $(AGENT),"$(AGENT)",)

arbiter-bundle: ## [project] what the round arbiter reads to rule on a tripwire or a round cap: the rounds marked new/repeated/reversing, the edits, the cascade, the oscillation (feature 375)   TRIGGER=<id the guard named> [OUT=<dir>]
	@if [ -z "$(TRIGGER)" ] && [ -z "$(BATCH)" ]; then printf 'make arbiter-bundle: TRIGGER=<the trigger the refusal named>, or BATCH=1 for every owed round trigger at once\n' >&2; exit 2; fi
	$(if $(MISSING_OK),$(LOGESCAPE) MISSING_OK "$$MISSING_OK",@:)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" arbiter bundle $(if $(BATCH),--batch $(if $(TRIGGERS),--triggers "$(TRIGGERS)",),"$(TRIGGER)") --root "$$(git rev-parse --show-toplevel)" $(if $(OUT),--out "$(OUT)",) $(if $(MISSING_OK),--missing-ok "$$MISSING_OK",)

arbiter-ruled:  ## [project] {internal} record the round arbiter's ruling - the round-arbiter SUBAGENT runs this   TRIGGER=<id> FILE=<json> AS=round-arbiter  (or BATCH=1 FILE=<json> for a batch)
	@if [ -z "$(FILE)" ] || { [ -z "$(TRIGGER)" ] && [ -z "$(BATCH)" ]; }; then printf 'make arbiter-ruled: FILE= and TRIGGER= (or BATCH=1) are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh arbiter $(if $(BATCH),ruled-batch,ruled "$(TRIGGER)") "$(abspath $(FILE))" --as "$(or $(AS),main)"

arbiter-nit:  ## [project] answer an accepted unit again after the wording fix its ruling asked for   TRIGGER=<id> OLD="<words>" NEW="<words>"
	@if [ -z "$(TRIGGER)" ] || [ -z "$$OLD" ] || [ -z "$$NEW" ]; then printf 'make arbiter-nit: TRIGGER=, OLD= and NEW= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh arbiter nit "$(TRIGGER)" "$$OLD" "$$NEW"

arbiter-fix-done:  ## [project] the round arbiter's tooling fix is MADE: what was built and its test (feature 379); LAND= lands its files first, TICK= ticks the task after; a fix in rust/ committed with its task takes LANDING= instead, settled as make land of that task pushes (451 T182)   ID="<trigger> [<trigger> ...]" NOTE="<what was built>" TEST=<its test> [LAND="<the fix's files>"] [F=<feature> TICK=<Txx>] | [LANDING=<Txx> FILES="<the fix's files>" F=<feature>]
	@if [ -z "$(ID)" ] || [ -z "$$NOTE" ] || [ -z "$(TEST)" ]; then printf 'make arbiter-fix-done: ID=, NOTE= and TEST= are required\n' >&2; exit 2; fi
	@if [ -n "$(TICK)" ] && [ -z "$(F)" ]; then printf 'make arbiter-fix-done: TICK= ticks a task of F=<feature> - name the feature\n' >&2; exit 2; fi
	@if [ -n "$(LANDING)" ] && [ -n "$$LAND$(TICK)" ]; then printf 'make arbiter-fix-done: LANDING= settles the fix as make land F=<feature> T=$(LANDING) pushes - drop LAND= and TICK=\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && $(if $(LAND),set -f && scripts/land-tooling.sh $$LAND $(TEST) && set +f && git fetch -q origin &&,) scripts/gates/l7r-gate.sh arbiter fix done "$(ID)" "$$NOTE" "$(TEST)"$(if $(LANDING), --landing "$(LANDING)" --files "$$FILES"$(if $(F), --feature "$(F)",),)$(if $(TICK), && $(MAKE) --no-print-directory tick F="$(F)" T="$(TICK)",)

use-feature:  ## [project] make F the clone's active feature for the hooks (.specify/feature.json) - instead of writing the file by hand (the round arbiter on hour:396@1)   F=<feature number>
	@if [ -z "$(F)" ]; then printf 'make use-feature: F=<feature number> is required - e.g. make use-feature F=396\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && d=$$(ls -d specs/$(F)-* 2>/dev/null | head -1) && [ -n "$$d" ] || { printf 'make use-feature: no specs/$(F)-* directory\n' >&2; exit 2; }; printf '{\n  "feature_directory": "%s"\n}\n' "$$d" > .specify/feature.json && printf 'use-feature: .specify/feature.json names %s; export SPECIFY_FEATURE=%s\n' "$$d" "$${d#specs/}"

step-back:  ## [project] the feature's hourly checkpoint: open it and build the round arbiter's step-back bundle (feature 383)   [TRIGGER=hour:<f>@<n> TRANSCRIPT=<jsonl> SINCE=<ISO> UNTIL=<ISO>: replay an hour]
	@cd "$$(git rev-parse --show-toplevel)" && if [ -n "$(TRIGGER)" ]; then scripts/gates/l7r-gate.sh measure step-back "$(TRIGGER)" --root "$$(pwd)" $(if $(TRANSCRIPT),--transcript "$(TRANSCRIPT)",) $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(OUT),--out "$(OUT)",); else t=$$(scripts/gates/l7r-gate.sh reviews checkpoint open) && scripts/gates/l7r-gate.sh measure step-back "$$t" --root "$$(pwd)"; fi

arbiter-ask: export ARBITER_WHY = $(WHY)
arbiter-ask: export ARBITER_REVIEW = $(REVIEW)
arbiter-ask:  ## [project] put a PROCESS question (a cap, a waiver, a stuck choice of route) to the round arbiter before the GM (feature 379)   SUBJECT=<short id> WHY="<the question>" [FILES="<the measurements it cites>"] [REVIEW=spec|plan|claims:<key>;<key>: an accept then stands as that review's verdict, 409; claims' since 2026-10-24]
	@if [ -z "$$SUBJECT" ] || [ -z "$$ARBITER_WHY" ]; then printf 'make arbiter-ask: SUBJECT= and WHY= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh arbiter bundle --check-ask "$$ARBITER_WHY" --evidence "$(FILES)" && scripts/gates/l7r-gate.sh arbiter ask "$$SUBJECT" "$$ARBITER_WHY" "$$ARBITER_REVIEW" && scripts/gates/l7r-gate.sh arbiter bundle "ask:$$SUBJECT" --root "$$(pwd)" --evidence "$(FILES)"

land-tooling:  ## [project] land the named TOOLING files on main by themselves, mid-feature (feature 379)   FILES="scripts/x.py tests/tooling/test_x.py"
	@"$$(git rev-parse --show-toplevel)/scripts/land-tooling.sh" $(FILES); rc=$$?; \
	  if [ $$rc = 0 ]; then "$$(git rev-parse --show-toplevel)/scripts/state-sync.sh" push --detach || :; fi; exit $$rc

# THE TOOLING STATE (feature 451 T258): a landing's own push made, the clone's check answers and event logs follow it to the private
# tooling-state repository, detached - the landing's exit is its own, and a failed state push is one line at the next landing.
state-push:     ## [project] push this clone's check answers and event logs (.git/record-checks, .git/l7r-events) to the private tooling-state repository, on the clone's branch - what make land and make land-tooling run, detached, after their own push; never a refusal (feature 451 T258)
	@"$$(git rev-parse --show-toplevel)/scripts/state-sync.sh" push
state-restore:  ## [project] bring the check answers and event logs back from the private tooling-state repository into this clone (a fresh clone, a lost container's replacement): merged, an answer by its record's utc and a log by the lines it lacks, nothing newer here overwritten (feature 451 T258)   [FROM=<another clone's name>]
	@"$$(git rev-parse --show-toplevel)/scripts/state-sync.sh" restore $(FROM)

arbiter-fix-declined:  ## [project] the round arbiter's tooling fix OVERHAULS a process: declined, never filed - a question for the GM owed escalation-check (features 379, 432)   ID=<trigger> REASON="<why>"
	@if [ -z "$(ID)" ] || [ -z "$$REASON" ]; then printf 'make arbiter-fix-declined: ID= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh arbiter fix declined "$(ID)" "$$REASON"

step-back-off:  ## [project] suspend the hourly step-back, not remove it: the hour comes due for nothing until step-back-on; the tripwire rulings stay (feature 405 T43)   REASON="..."
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh reviews checkpoint switch off --why "$$REASON" && git add dev/step-back.json && git commit -q -m "chore: the hourly step-back suspended - $$REASON" -- dev/step-back.json && echo "committed dev/step-back.json"
step-back-on:   ## [project] resume the hourly step-back (feature 405 T43)   REASON="..."
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh reviews checkpoint switch on --why "$$REASON" && git add dev/step-back.json && git commit -q -m "chore: the hourly step-back resumed - $$REASON" -- dev/step-back.json && echo "committed dev/step-back.json"
# THE LANDING (feature 449 T121, `ask:449-T83-scope`): `l7r-gate land`, the Rust port of `scripts/land.py`, the same in `make land`,
# `make land-batch` and `make land-stop`. The commit deleting `land.py` was the last the Python landed, run from its saved copy.
LAND_RUN = "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" land
land: export LAND_NOTE = $(NOTE)
land: export LAND_BOXES = $(BOXES)
land:           ## [project] land one task or several and tick them: each task's done commit carried first (make builder-done's, 451 T397; make carry kept for a carry by hand or a stopped one), then every cheap refusal together, then make done and make cohort-landing where needed (neither cohort on a counter-only delta, feature 446; no coverage run beside them, gone with the Python tests, 449 FR-001b), the push, the ticks (feature 405 T33); T= takes commas or spaces (451 T18)   F=405 T="T12 [T13]" (or T=T12,T13) NOTE="what was verified" [BOXES=1 ticks a physical task's research boxes]
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make land: F=<feature> and T="<task ids>" are required\n' >&2; exit 2; fi
	$(DISK_FLOOR)
	@$(LAND_RUN) "$(F)" "$(T)"; rc=$$?; \
	  if [ $$rc = 0 ]; then "$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --scratch-sweep landed "$(F)" "$$(git rev-parse --path-format=absolute --git-common-dir)/task-starts.jsonl" $(T) </dev/null; fi; \
	  if [ $$rc = 0 ] || [ $$rc = 3 ]; then "$$(git rev-parse --show-toplevel)/scripts/state-sync.sh" push --detach || :; fi; \
	  if [ $$rc = 0 ] || [ $$rc = 3 ]; then "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree landed "$(F)" $(T) || printf 'make land: the landed task'"'"'s pool tree was not released (the landing stands) - make builder-tree-release T="$(T)"\n' >&2; fi; \
	  $(SCRATCH_TREES); exit $$rc

# THE BUILDER POOL (feature 451 T285, the GM 2026-11-26: "whatever tooling we use to create worktrees automatically enforces and
# performs the correct behavior"): a builder's worktree is one of the clone's standing pool, so its build cache is warm (a cold
# tree's first closing checks: 14-30 minutes against about one, 2026-11-26). `rust/gate/crates/task/src/builder_tree.rs`; a hand
# `git worktree add` under the clones directory, and the removal of a pool tree or its cache, are refused by `builder_pool_hooks`.
.PHONY: builder-tree builder-trees builder-tree-release builder-tree-adopt builder-tree-drop
builder-tree: export DISCARD := $(DISCARD)
builder-tree:   ## [project] a builder's worktree from the clone's standing pool: a free tree brought to the clone's HEAD and held by the task, its path printed; none free, ONE more made up to the cap (L7R_BUILDER_POOL, 4), said to be cold, its guard built; make land releases it (feature 451 T285); refused for a task whose own make builder-done commit is not yet carried, the make carry to run printed (451 T398); a warm handout pre-warms the tree in the background - the test builds of the crates moved since its last handout, starting a crate only while a build slot is spare and never cutting one in flight (451 T336), L7R_PREWARM=0 for none (451 T316); every handout starts the clone's memory sampler where none runs, L7R_SAMPLER=0 for none (451 T274)   T=<task(s)> [F=<feature>] [DISCARD="<why a free tree's uncommitted work may go>"]
	@if [ -z "$(T)" ]; then printf 'make builder-tree: T=<task> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree take "$(T)" "$(or $(F),$(SPECIFY_FEATURE))"
builder-trees:  ## [project] the builder pool: each tree, the task holding it, since when, its build cache's size (feature 451 T285); then each commit make builder-done kept that the clone's HEAD does not hold yet, with its make carry (451 T394)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree list
builder-tree-release:  ## [project] free the pool tree a task holds, the tree and its build cache left in place - what make land does for a landed task (feature 451 T285)   T=<task(s)> [F=<feature>]
	@if [ -z "$(T)" ]; then printf 'make builder-tree-release: T=<task> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree release "$(T)" "$(F)"
builder-tree-adopt:  ## [project] a builder's worktree made before the pool joins it under its own name, its build cache as warm as it was (a rename chills it: 0.1 s to 66 s, 2026-11-26; feature 451 T285)   TREE=<path> [T=<task holding it>] [F=<feature>]
	@if [ -z "$(TREE)" ]; then printf 'make builder-tree-adopt: TREE=<path> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree adopt "$(TREE)" "$(T)" "$(or $(F),$(SPECIFY_FEATURE))"
builder-tree-drop: export REASON := $(REASON)
builder-tree-drop:  ## [project] the ONE way a pool tree and its build cache are removed, the reason on the pool's log (feature 451 T285)   TREE=<path> REASON="<two words or more>"
	@if [ -z "$(TREE)" ]; then printf 'make builder-tree-drop: TREE=<path> and REASON="<why>" are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree drop "$(TREE)"

# THE MEMORY AND LOAD SAMPLER (feature 451 T274): the builder count is certified against the container's 10 GiB limit from samples,
# and on 2026-11-26 those were a shell loop the session started by hand, so the three- and four-at-once batches ran unsampled. One
# detached sampler a clone, started by every make builder-tree; `rust/gate/crates/measure/src/measure/sampler.rs`,
# `dev/audits/memory-sampler.md`.
.PHONY: sampler sampler-start sampler-stop sampler-report
sampler:        ## [project] the clone's memory and load sampler: running or not, its samples file's lines and size, its log's last line (feature 451 T274)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure sampler status
sampler-start:  ## [project] start the clone's memory and load sampler, detached, where none is running (make builder-tree does at every handout): a JSON line every L7R_SAMPLE_S seconds (10) to <git common dir>/l7r-events/samples/mem-samples.jsonl - cgroup anon, memory.current, memory.peak, memory.max, memory and CPU stall, load, OOM kills, rustc processes, who holds each pool tree; it ends after L7R_SAMPLE_MAX_H hours (12) or past 4 MiB, and a start past that bound begins a new file (feature 451 T274)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure sampler start
sampler-stop:   ## [project] stop the clone's memory and load sampler, its samples left in place (feature 451 T274)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure sampler stop
sampler-report: ## [project] the samples of a window as a table, a row for each count of pool trees held: anonymous memory median / 95th / peak against memory.max, samples over the margin (L7R_MEM_MARGIN_GIB, 7: a GUESS knob), memory and CPU stall seconds, load against the cores, rustc max, OOM kills; LOG= reads sample logs instead, the hand logs of 2026-11-26 too (dev/measurements/2026-11-26/builder-count/mem-samples-*.log), a table a file (feature 451 T274)   [SINCE=<ISO UTC>] [UNTIL=<ISO UTC>] [LOG="<file> ..."]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure sampler report $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(LOG),--log "$(LOG)",)

# THE STANDING PART OF A BUILDER'S BRIEF COMES FROM THE TOOLING (feature 451 T334, the GM 2026-11-26: "I just want to make sure that
# we're putting the instructions in the right place"): the sizing rules of scripts/container/builder-brief.md were broken five times
# on 2026-11-26 with nothing refusing. `rust/gate/crates/task/src/builder_brief.rs` sizes the brief, takes the pool tree and prints the
# block; `builder_brief_hooks` refuses a builder's dispatch without the block's marker.
.PHONY: builder-brief
builder-brief: export SIZING_OK := $(SIZING_OK)
builder-brief:  ## [project] the standing block of a builder's brief, printed to paste at the brief's head: sized first (JOBS at most 3, a measurement's MEASURES at most 6, a new mechanism never one fix - each refusal naming the commands to run instead), then the task's pool tree taken as make builder-tree takes it, a bundle T=a,b briefed as one builder on the one tree held for it; its first line is the marker the builder-brief guard holds a dispatch to (feature 451 T334)   T=<task(s)> KIND=fix|measurement|build-half|closing-half [F=<feature>] [JOBS=<n>] [MEASURES=<things measured>] [CRATE="<crate dirs>"] [BLOCKS="<feature> T<n>"] [LOAD=1] [ENTRY=<k>, the queue entry it serves as make builder-next prints it, logged for make builder-done (451 T313)] [SIZING_OK="<why a fix whose line names a mechanism is one builder>"]
	@if [ -z "$(T)" ] || [ -z "$$KIND" ]; then printf 'make builder-brief: T=<task(s)> and KIND=fix|measurement|build-half|closing-half are required   [F=<feature>] [JOBS=<n>] [MEASURES=<n>] [CRATE="<crate dirs>"] [BLOCKS="<feature> T<n>"] [LOAD=1]\n' >&2; exit 2; fi
	$(if $(SIZING_OK),$(LOGESCAPE) SIZING_OK "$$SIZING_OK",@:)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-brief "$(T)" "$(or $(F),$(SPECIFY_FEATURE))" "$$KIND" "$(JOBS)" "$(MEASURES)" "$(CRATE)" "$(BLOCKS)" "$(LOAD)" "$(ENTRY)"

# A POOL TREE GOES TO ITS NEXT TASK AS SOON AS ITS BUILDER'S WORK IS COMMITTED (451 T394; the GM, 2026-11-27: "if our tooling
# indicates that we have spent over 2 hours blocking on the second tier then that's a HUGE problem"): the three warm trees stood
# idle 23% of an eight-hour window with the queue never short, the session working a builder's end as commit, carry, resolve,
# check, land and only then the next brief (dev/measurements/2026-11-27/tree-idle/results.md). MSG and GUARD are free text: the
# binary reads them from the environment, never from the recipe. `rust/gate/crates/task/src/builder_done.rs`.
.PHONY: builder-done
builder-done:   ## [project] a builder's end in one command, the HAND-IN (feature 461 T08, l7r-gate land --hand-in): the task's pool tree (found in the registry) applied onto where work lands (HAND_IN_BASE: clone, the clone's HEAD, phase 1; origin, origin/main after a fetch) by the carry's rules, uncommitted - a conflict no rule resolves left in the tree with its files named, resolved and resumed by running this again - then the landing's first pass in its hand-in mode (each refusal printed with its fixing command, nothing committed; no coverage, no gate), then committed on that base - MSG the subject, the guard-edit reason's line from GUARD=, the co-author trailer - kept under refs/l7r/done/<feature>-<task> and on the pool's log, the tree released, the next dispatch printed and "handed in to the lane"; refused with nothing done on an unfinished cherry-pick or merge, an unmerged path, a conflict's markers, nothing to commit, a guard file changed with no GUARD= (the re-run printed), or the task's earlier done commit not yet carried; it never lands or pushes (feature 451 T394, 461 T07)   T=<task(s)> MSG="<the commit's subject>" [F=<feature>] [GUARD="<guard-edit reason>"] [HAND_IN_BASE=clone|origin]
	@if [ -z "$(T)" ] || [ -z "$$MSG" ]; then printf 'make builder-done: T=<task(s)> and MSG="<the commit'"'"'s subject>" are required   [F=<feature>] [GUARD="<guard-edit reason>"]\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" land --hand-in "$(T)" "$(or $(F),$(SPECIFY_FEATURE))"

# THE BUILDERS' QUEUE IS A FILE CODE READS, AND THE TOOLING NAMES THE NEXT TASK (451 T313, T395, T297; the GM, 2026-11-26: "what
# you are doing sounds like something that we want our tooling to actually enforce. Because otherwise you just have to remember to
# keep our tasks in flight"): specs/<feature>/queue.txt, one entry a line, each state computed and never typed. The format, the
# states and the overlap rule: rust/guard/shared/src/builder_queue.rs; the commands: rust/gate/crates/task/src/builder_queue.rs;
# the Stop refusal over them: rust/guard/src/guards/pool_idle_hooks.rs. NOTE, CRATE, FILES and WAITS are free text or word
# lists: the binary reads NOTE from the environment, and the lists reach the recipe as "$$NAME".
.PHONY: queue queue-add builder-next
queue:          ## [project] the builders' queue, specs/<feature>/queue.txt (every queue of the clone with no F=), each entry with its state computed: landed (its box ticked), built (its make builder-done commit made - the carry or the landing owed), in flight (a pool tree held for it), waiting on what, READY; a malformed line is an error naming the line (feature 451 T313, T395)   [F=<feature>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" queue "$(or $(F),$(SPECIFY_FEATURE))"
queue-add:      ## [project] append one entry to the feature's queue, read back through the queue's own parser before it is written, refused for a task with no box; a plain edit of queue.txt does as well (feature 451 T313)   T=<task(s)> KIND=fix|measurement|build-half|closing-half [F=<feature>] [JOBS=<1-3>] [MEASURES=<things measured>] [LOAD=1] [CRATE="<crate dirs>"] [FILES="<paths or prefixes>"] [WAITS="<T<n> GM alone>"] [NOTE="<a note>"]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" queue-add "$(T)" "$(or $(F),$(SPECIFY_FEATURE))" "$$KIND" "$(JOBS)" "$(MEASURES)" "$$CRATE" "$$FILES" "$$WAITS" "$(LOAD)"
builder-next:   ## [project] the next task to hand a pool tree: among the queue's READY entries whose crates and files overlap no task holding a tree, an open performance task's first (FR-013), then the queue's order (a shared crate or path, or one under the other by whole path components; waits=alone only with no tree held), with its exact make builder-brief command (its ENTRY=, which names the entry on the done line), each READY entry passed over and why, and the pool's count against L7R_BUILDERS (3); with none, why - what make builder-done prints as its first step and the pool-idle Stop guard refuses a turn's end over (feature 451 T313, T297)   [F=<feature>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-next "$(or $(F),$(SPECIFY_FEATURE))"
lane:           ## [project] the landing lane as it stands, computed from the pool's log, the done refs, origin/main and the lane's log (l7r-lane/lane.jsonl in the git common directory): each hand-in on the lane with its state (waiting, in batch, ejected -> repair), each open batch with its state, the last landed batch and the repairs open; reads only, no fetch (feature 461 T11)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" lane status

lane-start:     ## [project] start the landing lane's runner, detached (l7r-gate lane --work, a session and process group of its own), one a clone by its flock on l7r-lane/lane.lock in the git common directory - a second start says the first's pid; it resumes the log's last open batch, and ends after LANE_IDLE_S (3600, a GUESS knob) with no hand-in; every hand-in starts it from phase 2's base (HAND_IN_BASE=origin) (feature 461 T12)   [LANE_IDLE_S=<seconds>] [LANE_POLL_S=<seconds>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" lane start

lane-stop:      ## [project] stop the landing lane's runner: after the batch in flight (waited for up to 10 s, then left asked), or with NOW=1 at once - its process group ended and its stop line written, its open batch resumed at the next make lane-start (feature 461 T12)   [NOW=1]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" lane stop $(if $(NOW),--now,)

coverage-exempt: ## [tests] the engine files the Rust port replaces, exempt from the coverage floor (dev/coverage-exempt.json; feature 448, the GM 2026-11-02); PRUNE=1 drops the stale entries   [PRUNE=1]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" coverage-exempt list $(if $(PRUNE),--prune,)


# A BUILDER'S WORK REACHES THE CLONE BY ONE COMMAND (451 T292): three landings ran over a hand cherry-pick left unfinished on a
# conflict (451 T235, T262, T270), which `make land` now refuses; this carries the commit, keeps both sides of the conflicts every
# parallel carry-over met (a tasks.md list line each side added, plan-review.json), stops on any other, and verifies its end.
carry:           ## [project] carry a builder worktree's HEAD commit (or COMMIT=) into this tree by cherry-pick: both sides kept where each only added a specs/*/tasks.md list line (a filed task's box whole, 451 T289; a bare open box given back the lines a side holds under it) or a specs/*/request.md dated section, a specs/*/plan.md merged by `### T<n>` section, each keyed by its whole heading line (the builder's filled stub taken, its removed one dropped, the clone's kept, its new one placed after its task's last, then each task's sections put together; one section both changed stops, 451 T300, T419) and a plan-review.json by the record's merge; outside the spec files (451 T300 part 2) docs/make-targets.html regenerated and never merged, a prose hunk - a .md line, a Makefile comment or `##` help line, a .rs comment line - merged by words against the merge base (overlapping changes stop), two Makefile target blocks or two .md bullets added at one place kept both, the clone's first, and a .jsonl's records kept (each side's appended, what either pruned dropped; 451 T399); any other conflict stopped with the files and the next command; ends verified - nothing in progress, unmerged or staged, the commit's non-spec files in HEAD - its last line naming each file resolved and its rule (451 T292); COMMIT= alone carries a commit this clone's own objects hold, as make builder-done keeps one, and the ref it was kept under is deleted at the carry's verified end, an empty pick's too (451 T397), where the carry runs in the clone - in a linked worktree it is kept (451 T404)   FROM=<builder's worktree> [COMMIT=<sha>] | COMMIT=<sha>
	@if [ -z "$(FROM)" ] && [ -z "$(COMMIT)" ]; then printf 'make carry: FROM=<the builder worktree> is required   [COMMIT=<sha>; its HEAD otherwise] - or COMMIT=<sha> alone, a commit this clone holds (make builder-trees lists the done commits)\n' >&2; exit 2; fi
	@$(LAND_RUN) --carry "$(if $(FROM),$(abspath $(FROM)))" $(COMMIT)

land-stop:       ## [project] stop this tree's running `make land` cleanly - its gate and cohort stop with it (405 T90)
	@$(LAND_RUN) --stop

land-batch: export LAND_NOTE = $(NOTE)
land-batch:     ## [project] the same command as make land (feature 385 T117's name, kept)   F=385 T="T106 T108" NOTE="what was verified"
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make land-batch: F=<feature> and T="<task ids>" are required\n' >&2; exit 2; fi
	@$(LAND_RUN) "$(F)" "$(T)"; rc=$$?; \
	  if [ $$rc = 0 ] || [ $$rc = 3 ]; then "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" builder-tree landed "$(F)" $(T) || printf 'make land-batch: the landed tasks'"'"' pool trees were not released (the landing stands) - make builder-tree-release T="$(T)"\n' >&2; fi; \
	  exit $$rc

phase-read:     ## [project] let ONE of a started phase task's held old-code files be read for ten minutes (to replace the stage's thin Python function, say), the reason logged - the phase-source guard's escape for the Read tool (feature 444)   FILE=<path> WHY="<reason>"
	@if [ -z "$(FILE)" ] || [ -z "$$WHY" ]; then printf 'make phase-read: FILE=<path> and WHY="<reason>" are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" phase-read allow "$(FILE)" "$$WHY"

task-start:     ## [project] name the task you are starting, so its checks wait for its decisions' verdict; a phase task's old code is held from reading until it is ticked (features 375, 444); refused while an open [perf] task waits in an active feature (451 FR-013), escape PERF_LATER_OK="<reason>", recorded by the tool; T=a,b,c starts a bundle under its first task (451 T141)   F=375 T=T13 (or T=T13,T14,T15)
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make task-start: F=<feature> and T=<task id> are required\n' >&2; exit 2; fi
	$(if $(HOLD_OK),$(LOGESCAPE) HOLD_OK "$$HOLD_OK",@:)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" task-start "$(F)" "$(T)"

task-unstart:   ## [project] undo a make task-start made by mistake in THIS tree: its mark removed and an unstart row logged, which every reader of the start log takes with its start as no start; another tree's mark refused, naming the command to run there; a bundle goes whole under its first task (451 T359)   F=451 T=T13
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make task-unstart: F=<feature> and T=<task id> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" task-unstart "$(F)" "$(T)"

task-withdraw: export TASK_WHY = $(WHY)
task-withdraw:  ## [project] close a filed task found to be a duplicate or no defect, with no landing: its box ticked with ' Withdrawn <date>: <why>' appended, its UNFILLED plan stub removed, who and why in the feature's event log; nothing committed, the changed paths printed; refused, all reasons together, for a task started in any tree, already ticked, with a filled or reviewed plan section, with a commit of its own since origin/main, or the feature's last open box (451 T359)   F=451 T="T322 T323" WHY="<two words or more>"
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make task-withdraw: F=<feature>, T=<task id(s)> and WHY="<reason>" are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" task-withdraw "$(F)" "$(T)"

decide:         ## [project] the spec-fidelity dispatch that rules on one task's plan section before its checks (feature 375); a found-and-left deferral without its reason, filed task and order, or naming no open task, refused, escape DEFER_FORM_OK="<reason>" (451 T17); T=a,b,c decides a bundle's one section in one dispatch (451 T141); the push's spec lint over the feature's every changed file beside it (451 T527)   F=375 T=T13 (or T=T13,T14,T15)
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make decide: F=<feature> and T=<task id> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan decide "$(F)" "$(T)"

# THE SHARED DIFFERENTIAL RUNNER (feature 449 T161; the GM 2026-11-16 and 2026-11-11): every port's comparison runs here, not through a
# hand-written driver loop. The default reruns only the sides whose key moved; VERIFY=1 reruns every new side and writes the report a
# plan's case count cites (`make decide` refuses an uncited one); ALL=1 takes a REASON, which the runner itself refuses short and records
# in the guard log, so a direct `l7r-gate diff-run --all` is held the same (docs/diff-run.md). JOBS=n runs the owed sides on n workers,
# each in its own world (feature 449 T173: T170's verify spent 381 of its 392.6 s building and removing worlds, one after another).
diff-run:       ## [project] run a differential's cases on both sides, rerunning only what a fix touched (feature 449 T161; docs/diff-run.md)   CASES=<cases file> [ONLY=<case name>] [VERIFY=1] [TWICE=1] [ALL=1 REASON="..."] [JOBS=n]
	@if [ -z "$(CASES)" ]; then printf 'make diff-run: CASES=<cases file> is required (docs/diff-run.md has the format)\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" diff-run "$(CASES)" $(if $(ONLY),--only "$(ONLY)",) $(if $(VERIFY),--verify,) $(if $(TWICE),--twice,) $(if $(ALL),--all --reason "$$REASON",) $(if $(JOBS),--jobs "$(JOBS)",)

section-sha:    ## [project] {internal} the digest of one task's plan section, which a decision preflight records   F=375 T=T13
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" plan section-sha "$(F)" "$(T)"

hookbench:      ## [project] replay the frozen command window through a guard decision, in process   GUARD=house-style [AGAINST=<ref>] | REFRESH=1
##  GUARD=<name>         any guard of the l7r-guard binary, with or without its -hooks
##  AGAINST=<ref>        also print the verdict diff against the guard as it stood at <ref> - what an exemption change owes
##  REFRESH=1            freeze a new dated window of real commands into tests/hooks/fixtures/ instead
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" bench $(if $(REFRESH),--refresh,$(GUARD) $(if $(AGAINST),--against $(AGAINST),))

figures:        ## [project] re-run every recorded measurement and report what moved   [SPEC=specs/NNN-slug; default every spec with a measurements.json]
##  a moved COUNT fails; a timing outside its band is reported and never fails; the file is restored after
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure figures $(SPEC)

trial-review:   ## [project] a trial's ONE review: its brief, request and research bundled, and the dispatch printed - check each figure against its recorded output, re-run only what is missing (feature 442)   F=<trial number>
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" trial-review "$(F)"

trial: export TRIAL_APPROVED = $(APPROVED)
trial:          ## [project] start a TRIAL - a question a measurement answers: claims a number and writes the trial brief (**Form**: trial), measured first, reviewed once when Done (features 438, 440; docs/spec-kit-and-reviews.md)   SLUG=kebab-slug [APPROVED="<the GM's words, verbatim>"]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" trial-start "$(SLUG)"

claim:          ## [project] claim the next spec-kit feature number under the host-wide lock   SLUG=kebab-slug | RENUMBER=specs/NNN-slug [PEEK=1: look, claim nothing]
##  SLUG=<slug>          lower-case kebab; the directory becomes specs/NNN-<slug>/ in THIS clone
##  RENUMBER=<specs/dir> instead of a slug: MOVE that existing directory to the next number (a deduplication, GM 2026-09-07)
##  PEEK=1               print what the claim would be and create or move nothing
	@if [ -z "$(SLUG)$(RENUMBER)" ]; then printf 'make claim: SLUG=<kebab-slug> is required (or RENUMBER=specs/NNN-slug to move an existing directory) - e.g. make claim SLUG=cheaper-widgets\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claim $(if $(PEEK),--dry-run,) $(if $(RENUMBER),--renumber "$(RENUMBER)",-- "$(SLUG)")

speckit-todo:   ## [project] list the spec-kit features not yet closed - filed, planned, in progress - by the stage each is owed at   [ALL=1: also the closed; BY=affects: by tag; CHECK=1: refuse missing or unknown tags]
##  ALL=1   also list the closed features and the reason each is closed
##  BY=affects  group the open features by their `**Affects**:` tags (.specify/affects.json) instead of by stage
##  AFFECTS=tooling  only the features carrying that tag, same layout (several: AFFECTS="tooling, magistracy")
##  CHECK=1 exit 1, with the line to add, when an open feature's spec has no `**Affects**:` tag or an unknown one
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" speckit-todo --root "$$(git rev-parse --show-toplevel)" $(if $(ALL),--all,) $(if $(filter affects,$(BY)),--by-affects,) $(if $(AFFECTS),--affects "$(AFFECTS)",) $(if $(CHECK),--check,)

preflight:      ## [tests] the gate's first phase, in seconds: the derived files regenerated, the record and its pointers, make quick - and, here only (not in the gate, 405 T47), the changed engine lines a quick test runs (feature 375)
	@$(call TIMED,preflight,preflight,"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" preflight --root "$$(git rev-parse --show-toplevel)")

gm-review:      ## [project] what waits on the GM: the questions escalation-check KEPT (his decisions, the one source - feature 432), the questions OWED escalation-check (the session's), rows waiting on other work, and per feature the TO REVIEW rows (he may overturn) - feature 375   [F=<NNN> that feature's rows] [EXPLAIN=1 what needs the GM, or with F= each row in full] [ROW=<n>]
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh gm-review $(if $(EXPLAIN),explain $(F) $(ROW),list $(F))

gm-question:    ## [project] put a question to the GM: written OWED escalation-check, it reaches him only once kept (feature 432)   F=<NNN> Q="<the question>" SOURCE="<what raised it>"
	@if [ -z "$(F)" ] || [ -z "$$Q" ] || [ -z "$$SOURCE" ]; then printf 'make gm-question: F=, Q= and SOURCE= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh gm-review question "$(F)" "$$Q" "$$SOURCE"

gm-escalated:   ## [project] record escalation-check's verdict on an owed question: KEEP holds it for the GM (name it in the turn's final message), CUT closes it with the reason (feature 432)   F=<NNN> ROW=<n> VERDICT=KEEP|CUT REASON="<escalation-check's reason>" [SUPERSEDED_BY=<a later question row>: CUT a kept question the GM has not reviewed, its premise overturned]
	@if [ -z "$(F)" ] || [ -z "$(ROW)" ] || [ -z "$(VERDICT)" ] || [ -z "$$REASON" ]; then printf 'make gm-escalated: F=, ROW=, VERDICT= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh gm-review escalated "$(F)" "$(ROW)" "$(VERDICT)" "$$REASON" "$(SUPERSEDED_BY)"

accept:         ## [project] accept a finding with a reason - the work goes on, and the GM may overturn it after landing (feature 375)   F=375 FINDING="<what>" REASON="<why it can stand>"
	@if [ -z "$(F)" ] || [ -z "$$FINDING" ] || [ -z "$$REASON" ]; then printf 'make accept: F=, FINDING= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh gm-review accept "$(F)" "$$FINDING" "$$REASON"

gm-reviewed: export GM_WORDS = $(WORDS)
gm-reviewed:    ## [project] the GM has reviewed a feature's rows; OVERTURN=<row> TO=<feature> turns one into an open row there (feature 375); ROW=<n> marks that one row alone; WORDS= his words when a session marks a row he discussed   F=375 [OVERTURN=<n> TO=<NNN> | ROW=<n>] [WORDS="<the GM's words>"]
	@if [ -z "$(F)" ]; then printf 'make gm-reviewed: F=<feature> is required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && $(if $(ROW),scripts/gates/l7r-gate.sh gm-review reviewed-row "$(F)" "$(ROW)",scripts/gates/l7r-gate.sh gm-review reviewed "$(F)" $(if $(OVERTURN),"$(OVERTURN)" "$(TO)",))

feature-report: ## [project] where a feature's time and dispatches went, as a table, from the event log, the run log and git (its timing columns read the lines that feed the task time breakdown, make task-time, 451 T243)   F=375 [TRANSCRIPT="<jsonl> ..."] [SINCE=<ISO>] [UNTIL=<ISO>] [WRITE=1]
##  F=<NNN>            the feature
##  TRANSCRIPT=<files> session transcripts to convert where the event log has no lines (a feature before 375)
##  SINCE= UNTIL=      ISO UTC bounds on the events read (a transcript holding more than this feature)
##  WRITE=1            also write specs/NNN-*/report.md, which every closing route asks for
	@if [ -z "$(F)" ]; then printf 'make feature-report: F=<feature number> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure feature-report --root "$$(git rev-parse --show-toplevel)" "$(F)" $(foreach t,$(TRANSCRIPT),--transcript "$(t)") $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(WRITE),--write,)

agent-sync:     ## [project] write into each agent file the text every dispatch of that check shares (the modal guidelines), from its source (feature 383 amendment 6)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews agent-sync

agent-census:   ## [project] what each subagent check has cost, from the session transcripts   [SINCE=YYYY-MM-DD] [OUT=<json>]
##  SINCE=<date>   only the runs that started on or after it
##  OUT=<json>     also write the rows to this file
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record agent-census $(if $(SINCE),--since "$(SINCE)",) $(if $(OUT),--json "$(abspath $(OUT))",)

quote-verbatim: ## [project] is every quoted passage on the page it cites, character for character - run BEFORE quote-check   Q=0412 | IN=homesteads [NOTES=1-4] [OUT=<json>]
##  Q=<NNNN>       one or more questions, by number (both pages) or a page's file name; its own notes are read beside it
##  IN=<id>        every question of a section (its id in research/contents.json) or carrying a tag
##  NOTES=<n,n-m>  only these notes of each page, by the number its page shows them under
##  OUT=<json>     write the report the quote-check agent is handed (default: the scratch file the run names)
	@if [ -z "$$Q" ] && [ -z "$(IN)" ]; then printf 'make quote-verbatim: Q=<question number> or IN=<section or tag> is required - e.g. make quote-verbatim Q=0041\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record quote-verbatim --root "$$(git rev-parse --show-toplevel)" $(if $(Q),"$$Q",--in "$(IN)") $(if $(NOTES),--notes "$(NOTES)",) $(if $(OUT),--json "$(abspath $(OUT))",)

record-prepass: ## [project] the session notes and vocabulary candidates a pattern can find on a question - run BEFORE record-format   Q=0412 | IN=homesteads | Q=SOURCES
##  Q=<NNNN>       one or more questions, by number (both pages) or a page's file name; `SOURCES` for the registry
##  IN=<id>        every question of a section (its id in research/contents.json) or carrying a tag
	@if [ -z "$$Q" ] && [ -z "$(IN)" ]; then printf 'make record-prepass: Q=<question number> or IN=<section or tag> is required - e.g. make record-prepass Q=0041\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record record-prepass --root "$$(git rev-parse --show-toplevel)" $(if $(Q),"$$Q",--in "$(IN)")

claims-owed: ## [project] every research claim of the engine or the Mode A procedures owed an impl-drift check (no index row, or its code or cited research moved since), and why
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" owed

claims-bundle: ## [project] the bundle impl-drift reads, copied out of the repository - dispatch it on the MANIFEST printed   MODULE=<file> | OWED=1 | UNITS="<key>,<key>"   [OUT=<dir>] [REASON="<why>" for claims not owed] [WITH="<path>::<qualname>,..." context] [PAGES="<question file>,..."]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" bundle $(if $(OWED),--owed,) $(if $(MODULE),--module "$(MODULE)",) $(if $(UNITS),--units "$$UNITS",) $(if $(OUT),--out "$(abspath $(OUT))",) $(if $(REASON),--reason "$$REASON",) $(if $(WITH),--with "$$WITH",) $(if $(PAGES),--pages "$(PAGES)",)

claims-checked: ## [project] record an impl-drift reply into the claims index, at the fingerprints its bundle read; a finding that says the pages are silent is held, unrecorded and unfiled, until the record's three nearest pages for its words are in the bundle - it names them and the claims-bundle PAGES= call (451 T218)   BUNDLE=<dir> REPLY=<file holding the agent's reply>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make claims-checked: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" record --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

claims-coverage: ## [project] every unit with no research claim, a malformed claim or a pointer to no question - the gate's coverage test, narrowed   [IN=<part of a file path>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" coverage $(if $(IN),--path "$(IN)",)

claims-report: ## [project] the claims index: counts by verdict, every finding (drifted, needs research, mislabeled, unclaimed, undecided) and every UNRESEARCHED claim; DEFERRED findings, and a MISLABELED its claim's relabel answered (451 T221), are counted, not listed   [ALL=1 lists them]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" report $(if $(filter 1,$(ALL)),--all,)

tunables: ## [project] every claim whose value is ours - GUESS (searched, silent), UNRESEARCHED, CONVENTION - with its figure: a goal and a knob a fixing pass may move (feature 417 T28)   [UNDER=<file or dir>] [ALL=1 keeps claims with no figure] [COUNT=1] [INLINE=1 lists the numbers inside functions no claim states]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" tunables --root "$$(git rev-parse --show-toplevel)" $(if $(UNDER),--path $(UNDER),) $(if $(filter 1,$(ALL)),--all,) $(if $(filter 1,$(COUNT)),--count,) $(if $(filter 1,$(INLINE)),--inline,)

research-backlog: ## [project] the research backlog: every UNRESEARCHED claim and page item (not yet searched, a guess drawn meanwhile - distinct from a GUESS, searched and silent), by the code file it belongs to; a port stage works its own at its end - while the research switch is deferred, lists them and does not search (feature 451 T236, T244, the GM 2026-11-25)   [STAGE=<a hamlet stage, e.g. seat, or a path glob>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" research-backlog --root "$$(git rev-parse --show-toplevel)" $(if $(STAGE),--stage "$(STAGE)",)

impl-check: ## [project] a research-record feature's changed questions, each with the claims citing it and their verdicts, and what its close still owes (feature 378)   F=<n>
	@if [ -z "$(F)" ]; then printf 'make impl-check: F=<feature number> is required - e.g. make impl-check F=343\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" impl-check "$(F)"

claims-triage: ## [project] the claims owed only a TRIAGE (a page they cite moved, the blocks they rest on stand): one bundle of the new or changed blocks for one agent   [OUT=<dir>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" triage $(if $(OUT),--out "$(abspath $(OUT))",)

claims-triaged: ## [project] record a triage reply: a claim it names (TOUCHES) is owed impl-drift, every other claim of the bundle is cleared   BUNDLE=<dir> REPLY=<file>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make claims-triaged: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" triaged --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

claims-carry: ## [project] file every carried claims finding (a page edit's, on unchanged code) as an open task of the active feature, so the push lands (feature 385 FR-013)   F=<feature> [T=<open task to file into>] [KEYS="<k>;<k>" RULING=<arbiter trigger>: findings a ruling carried]
	@if [ -z "$(F)" ]; then printf 'make claims-carry: F=<feature> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" carry --feature "$(F)" $(if $(T),--task "$(T)",) $(if $(KEYS),--keys "$$KEYS",) $(if $(RULING),--ruling "$(RULING)",)

claims-known:  ## [project] record every known drift (a DRIFTED claim naming the open task that fixes it) for the GM, in its task's feature's gm-review.jsonl, so the push lands it - make land runs it (feature 430 T06)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" known

claims-backfill: ## [project] give every index row checked at today's research the pages it was checked at, so a later edit to them is triaged, not re-judged in full
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" backfill

claims-rekey:   ## [project] carry each claim's index row to the file its unit moved to with its code intact - a file split at the 1,000-line bar (405 T58) - and onto its port where dev/claims-ports.json maps a deleted .py unit to the unit it became, owed a full check (449 T166), and drops the rows of a deleted .py unit its `retired` map names (449 T184) or of a deleted .py file its `rebuilt` map names (449 T152); make land runs it
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" rekey

claims-refingerprint: ## [project] carry each claim's index row to the current fingerprint - the star re-exports (417 T54), a Rust unit's constant reads (449 T166) - where its code is otherwise unchanged, recorded in dev/claims-refingerprint.jsonl - run once, at the change
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" refingerprint

claims-backfill-sections: ## [project] re-key every procedure-section claim to its own line (feature 375), owing nothing that was not owed: run once, at the change
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" backfill-sections

translation-owed: ## [project] the translated quotations new or changed since the merge base - each owes a translation-check   [Q=0412]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record translation-owed --root "$$(git rev-parse --show-toplevel)" $(if $(Q),--q "$$Q",)

record-owed: ## [project] every record check this delta owes (intro-check, record-format, source-reader, quote-check, source-applicability, translation-check, entry-drift), with the command that answers each   [Q=0412] [UNANSWERED=1] [BETWEEN="<a> <b>"]
##  Q=<NNNN>        only that question's units
##  UNANSWERED=1    only the units with no current answer record (what the push refuses)
##  BETWEEN="a b"   the units revision b owes against revision a (a replay; no entry-drift)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record record-owed --root "$$(git rev-parse --show-toplevel)" $(if $(Q),--q "$$Q",) $(if $(UNANSWERED),--unanswered,) $(if $(BETWEEN),--between $(BETWEEN),)

record-checked: ## [project] record that a record check returned on the units it read - what answers an owed unit at the push   CHECK=<check> RESULT="<counts>" (BUNDLE=<dir> | Q=<NNNN> NOTES=<k,k> for source-reader | ... REASON="<why>")
##  BUNDLE=<dir>    the bundle the check read: its units, at the content it read
##  Q= NOTES= KEY= KIND=  the units the tree owes on that subject, at today's content - source-reader on named notes, or any check with REASON= (written to dev/bypass-log/)
##  REPLY=<file>    the check's reply: its OUTSIDE THE CHANGE findings are filed as open rows of the feature (feature 375), each only where it names the wrong outcome a reader of the map, sheet or page meets, or a tool's user - `| effect: <map|sheet|page|tool> - ...`; the rest, and its NOTED, NOT FILED lines, are printed and kept in the feature's noted.jsonl, never filed (451 T219, T229)
##  FIXED_BY="<check>: <its finding>"  CHECK=quote-check Q= NOTES=: a fix made by hand for ANOTHER check's finding, outside the quotation and its claim - the tool verifies both unchanged, else refuses (feature 399); no RESULT needed
	@if [ -z "$(CHECK)" ] || { [ -z "$$RESULT" ] && [ -z "$$FIXED_BY" ]; }; then printf 'make record-checked: CHECK=<check> and RESULT="<its counts>" are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record record-owed --root "$$(git rev-parse --show-toplevel)" --answer "$(CHECK)" --result "$$RESULT" $(if $(FIXED_BY),--fixed-by "$$FIXED_BY",) $(if $(BUNDLE),--bundle "$(abspath $(BUNDLE))",) $(if $(Q),--q "$$Q",) $(if $(NOTES),--notes "$(NOTES)",) $(if $(KEY),--key "$$KEY",) $(if $(KIND),--kind "$$KIND",) $(if $(REASON),--reason "$$REASON",) $(if $(REPLY),--reply "$(abspath $(REPLY))",)

style-prepass: ## [project] the style guide's mechanical half for one question - metric figures with no feet, and every lead line to rule on - run BEFORE record-style   Q=0412
##  Q=<NNNN>       the question, by number (both pages) or a page's file name
	@if [ -z "$$Q" ]; then printf 'make style-prepass: Q=<question number> is required - e.g. make style-prepass Q=0041\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record style-prepass --root "$$(git rev-parse --show-toplevel)" "$$Q"

question-sizes: ## [project] every research question over the size cap by its prose (no item tag or money mark counted; the measure the size-edit rule reads, 451 T238; feature 250 D14), largest first - make quick fails on one a change touched, make static on any (449 T385)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check question-size --report

open-questions: ## [project] every guess and every unfound source, read from the record and the tracked files now - the research still owed, with the map features each touches (feature 285)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record open-questions --root "$$(git rev-parse --show-toplevel)"

notes: ## [project] print the named notes of ONE question and only the blocks of its page that carry them - for editing a few notes without reading the whole file (feature 250)   Q=0041 KEYS=kyuhi-jawiki,kyuhi-jawiki-2
	@if [ -z "$$Q" ] || [ -z "$$KEYS" ]; then printf 'make notes: Q=<question number or page file> KEYS=<key,key> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record check-bundle --root "$$(git rev-parse --show-toplevel)" "$$Q" --notes "$$KEYS" --print-notes

lines: ## [project] print ONLY a coordination file's matching lines - the claims file, a handoff, a checks report - numbered, with how many were shown of how many; never read one whole (feature 274)   FILE=<file> KEY=<regex>
	@if [ -z "$(FILE)" ] || [ -z "$$KEY" ]; then printf 'make lines: FILE=<file> KEY=<regex> are required - e.g. make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="^- 269"\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" coord lines "$(FILE)" "$$KEY"

append: ## [project] append ONE line to a coordination file without reading or printing it (feature 274)   FILE=<file> LINE="<text>"
	@if [ -z "$(FILE)" ]; then printf 'make append: FILE=<file> LINE="<text>" are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" coord append "$(FILE)"

research-claim: ## [project] claim research questions for this clone, refused when another session holds one; STATUS=done releases (feature 376)   Q="0060 0246" FEATURE=<n> [STATUS="in progress"] [RELEASE=<owner> WHY="<reason>"]
	@if [ -z "$$Q" ] || [ -z "$(FEATURE)" ]; then printf 'make research-claim: Q="<question numbers>" FEATURE=<n> are required - e.g. make research-claim Q="0060 0246" FEATURE=376\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" research-claims claim "$$Q" --feature "$(FEATURE)" $(if $(STATUS),--status "$$STATUS",) $(if $(RELEASE),--release "$(RELEASE)" --why "$$WHY",)

research-claims: ## [project] the live claims on research questions, and nothing else of the sheet (feature 376)   Q="0060 0246"
	@if [ -z "$$Q" ]; then printf 'make research-claims: Q="<question numbers>" is required - e.g. make research-claims Q="0060 0246"\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" research-claims query "$$Q"

reserve: ## [project] reserve the next glossary, registry-entry or question number under a host-wide lock and write the file's stub - prints its path; fill it in (feature 265 FR-010: parallel queues never collide; feature 274: a write session's 11th registry key is refused; feature 303: a question's stub carries a tags marker to fill)   KIND=glossary|registry|question KEY=<term, key or heading id> [KEY_CAP_OK='<reason>']
	@if [ -z "$$KIND" ] || [ -z "$$KEY" ]; then printf 'make reserve: KIND=glossary|registry|question KEY=<term, key or heading id> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record reserve "$$KIND" "$$KEY" $(if $(URL),--url "$$URL",) $(if $(TAGS),--tags "$(TAGS)",)

canon: ## [project] search the GM's setting canon for EVERY term of a claim in one call - each hit with its file, line and heading (feature 250 D16; a direct read of a canon file is refused)   TERMS="imperial road|merchant share|artisan"
	@if [ -z "$$TERMS" ]; then printf 'make canon: TERMS="<a>|<b>|<c>" is required - every term of the claim at once\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record canon "$$TERMS"

apply-edits: ## [project] apply a quote-check or record-format report's EDIT and GLOSSARY blocks in one command - each only where its old text occurs once in a record file; the rest are listed REFUSED for you (feature 250 D15)   FROM=<the agent's output_file or a saved reply> [SKIP=2,5: EDIT and GLOSSARY blocks counted together, in reply order] [DRY=1] [RERUN_OK="<reason>": apply a re-run's wording EDITs on a pop-up answered before at its text, else held and listed in noted.jsonl - 451 T232]
	@if [ -z "$(FROM)" ]; then printf 'make apply-edits: FROM=<the output_file the agent dispatch named> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record apply-edits "$(FROM)" --root "$$(git rev-parse --show-toplevel)" $(if $(SKIP),--skip "$(SKIP)",) $(if $(DRY),--dry-run,) $(if $(RERUN_OK),--rerun-ok "$$RERUN_OK",)

page-session: ## [project] start ONE page's work in a FRESH headless session, detached, from written briefs, one after another - absolute paths; a then:<script> step queues the briefs it prints (feature 250 D7, R3); a write brief over four questions is refused (feature 274)   BRIEF="<file> then:<script>" [NAME=<session name, default this clone's>] [MODEL=<model>] [EFFORT=<level>] [AGENTS=<agents.json>] [WRITE_CAP_OK='<reason>']
	@if [ -z "$(BRIEF)" ]; then printf 'make page-session: BRIEF=<file> is required - e.g. make page-session BRIEF=specs/250-close-the-record-checks/briefs/homesteads.md\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/pages/page-session.sh "$(BRIEF)" "$(NAME)" "$(MODEL)" "$(EFFORT)" "$(AGENTS)"

modal-bundle: ## [project] the files a modal check reads (modal-form, modal-research or modal-depiction), copied out of the repository with the prepass and, for modal-research, the Entry pages, the candidates and the question record for grep; for modal-depiction, the drawing pages, the claims citing them and a crop of the glyph - feature 319; refused while a check before it in the order (form, research, depiction) is owed - feature 375 amendment 3   KIND=<class or key> FOR=modal-form|modal-research|modal-depiction [OUT=<dir>] [CHECK_ORDER_OK="<why>"]
	@if [ -z "$$KIND" ]; then printf 'make modal-bundle: KIND=<class name or key> is required - e.g. make modal-bundle KIND=Farmhouse FOR=modal-form\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh record modal-bundle "$$KIND" --for "$(or $(FOR),modal-form)" $(if $(OUT),--out "$(OUT)",) $(if $(REASON),--reason "$$REASON",)

modal-triage: ## [project] the triage bundle for every pop-up owed only because a page it names moved: the changed blocks beside the kinds naming them, for the modal-triage agent (feature 375; its own agent since 383 amendment 6)   [OUT=<dir>]
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh record modal-triage --root . bundle $(if $(OUT),--out "$(OUT)",)

modal-triaged: ## [project] record a pop-up triage reply: a kind it names (TOUCHES) is sent on to its checks, every other unit of the bundle answered `triage: untouched`   BUNDLE=<dir> REPLY=<file>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make modal-triaged: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh record modal-triage --root . record --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

modal-prepass: ## [project] the mechanical half of the modal checks for one About-form modal - word band, barred phrases, guesses, Entry files - feature 319   KIND=<class or key>
	@if [ -z "$$KIND" ]; then printf 'make modal-prepass: KIND=<class name or key> is required - e.g. make modal-prepass KIND=Farmhouse\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/gates/l7r-gate.sh record modal-bundle "$$KIND" --prepass

check-bundle: ## [project] the files ONE check agent reads, copied out of the repository with its prepass output - dispatch quote-check, record-format, source-applicability or source-reader with the MANIFEST it prints   Q=0087 | KEY=edo-enwiki
##  Q=<NNNN>         one question (both pages; a page's file name for one): pages, notes, prepass, quote-verbatim, cited registry entries, the variant index
##  KEY=<key>        one source: its registry entry and its saved page
##  OUT=<dir>        default /tmp/l7r-check/q-<question> or /tmp/l7r-check/key-<key>   EXTRA="<path> ..."   NO_QUOTES=1 skips the fetches   KIND=<modal class> adds its docstring, for entry-drift   NOTES=<key,key> a RE-check of those notes only   FOR=quote-check|record-format|entry-drift only that check's parts   WHOLE=1 with KEY= the whole page in parts, for source-reader (D19)
##  QUESTION=<q>     with KEY= WHOLE=1: the research question the page is read for, on the sources-consulted ledger (feature 288)
##  FEATURE 311 - a bundle for a check nothing owes is REFUSED (`make record-owed` lists what is owed); FOR=quote-check with no NOTES= holds only the owed notes
##  NOT_OWED_OK="<why>"  build it anyway (a backfill, an audit the GM asked for), recorded in the MANIFEST
##  NEW="<the claim>"    with KEY= WHOLE=1: a source-reader read for a claim not yet in the record
##  IMAGES="<file|dir> ..."  with KEY= or Q=: a scanned source's page images, copied into images/ and listed by name (feature 395)
##  FOR=intro-check [QS="<n> <n> ..."]  the intro-check bundle, one question or a batch
##  KEYS="<k> <k> ..."  several sources in one source-applicability bundle (the uncited write-ups, feature 312)
	@if [ -z "$$KEY" ] && [ -z "$$KEYS" ] && [ -z "$$Q" ] && [ -z "$(QS)" ]; then printf 'make check-bundle: Q=<question number> (or KEY=<registry key>, KEYS="<k> <k>", or QS= with FOR=intro-check) is required\n' >&2; exit 2; fi
	@set -f; "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record check-bundle --root "$$(git rev-parse --show-toplevel)" $(if $(KEYS),--keys "$$KEYS",) $(if $(KEY),--key "$$KEY",$(if $(Q),"$$Q",)) $(if $(OUT),--out "$(abspath $(OUT))",) $(if $(EXTRA),--extra $$EXTRA,) $(if $(NO_QUOTES),--no-quotes,) $(if $(KIND),--kind "$$KIND",) $(if $(NOTES),--notes "$(NOTES)",) $(if $(FOR),--for "$(FOR)",) $(if $(WHOLE),--whole,) $(if $(QUESTION),--question "$$QUESTION",) $(if $(QS),--qs "$(QS)",) $(if $(NOT_OWED_OK),--not-owed-ok "$$NOT_OWED_OK",) $(if $(NEW),--new "$$NEW",) $(if $(IMAGES),--images $$IMAGES,)

source-pages: ## [project] save the full visible text of the named pointers, with a manifest - run BEFORE source-reader, which greps the PAGE where a fetch gives an extract   OUT=<dir> URL=<u1>  (several: URLS="<u1> <u2>")
##  OUT=<dir>      where the pages and MANIFEST.txt go (a scratch directory)
##  URL=<u>        one pointer; URLS="<u1> <u2>" for several - make keeps only the LAST of a repeated URL=
##  QUESTION=<q>   the research question the pages are read for (its number, NNNN - feature 303), recorded on the sources-consulted ledger
##  REFRESH=1      fetch again even where the page cache holds a copy younger than seven days
	@if [ -z "$(OUT)" ] || [ -z "$$URL$$URLS" ]; then printf 'make source-pages: OUT=<dir> and URL=<u> (or URLS="<u1> <u2>") are required\n' >&2; exit 2; fi
	@set -f; "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record source-pages "$(abspath $(OUT))" $(if $(URL),"$$URL",) $$URLS $(if $(or $(QUESTION),$(Q)),--question "$${QUESTION:-$$Q}",) $(if $(SOUGHT),--sought "$$SOUGHT",) $(if $(REREAD),--reread "$$REREAD",)

source-outcome: ## [project] record what came of reading a source page on the host-wide sources-consulted ledger and the attempts log - every page a research pass reads (features 288, 312)   URL=<u> OUTCOME=cited:<key>|rejected:<why>|nothing-found|unreadable|pending [QUESTION=<NNNN>] [SOUGHT=<what was looked for>]
	@if [ -z "$$URL" ] || [ -z "$$OUTCOME" ]; then printf 'make source-outcome: URL=<u> OUTCOME=<cited:key|rejected:why|nothing-found|unreadable|pending> are required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record sources outcome "$$URL" "$$OUTCOME" $(if $(QUESTION),--question "$$QUESTION",) $(if $(SOUGHT),--sought "$$SOUGHT",)

uncited: ## [project] the uncited pages judged once, and the kept ones written up - DO=set (count; OUT= writes the URLs) | rule | fetch [LIMIT=n] | bundle OUT=<dir> [LIMIT=n] [START=n] | apply DIRS="<bundle> ..." | score DIR=<bundle> ANSWERS=<labels.json> | draft OUT=<dir> [START=n] | install DIRS="<draft> ..." | merge KEY=<dup> INTO=<kept key> | dedupe [DRY=1] | unkeep URL=<u> REASONS=<r,r> NOTE=<why> | requeue URL=<u> | copy-verdicts | stands URL=<u> NOTE=<why> | retire-cited KEY=<k> ACCESS=<state> NOTE=<why> | report (feature 312)   DO=<step>
	@if [ -z "$(DO)" ]; then printf 'make uncited: DO=set|rule|fetch|bundle|apply|score|draft|install|merge|dedupe|unkeep|requeue|copy-verdicts|stands|retire-cited|report is required\n' >&2; exit 2; fi
	@set -f; "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record uncited $(DO) $(if $(filter set,$(DO)),$(if $(OUT),--write "$(abspath $(OUT))",),) $(if $(filter bundle draft,$(DO)),"$(abspath $(OUT))" $(if $(START),--start $(START),),) $(if $(filter fetch bundle,$(DO)),$(if $(LIMIT),--limit $(LIMIT),),) $(if $(filter apply install,$(DO)),$$DIRS,) $(if $(filter score,$(DO)),"$(DIR)" "$(ANSWERS)",) $(if $(filter merge,$(DO)),"$$KEY" "$(INTO)",) $(if $(filter dedupe,$(DO)),$(if $(DRY),--dry,),) $(if $(filter unkeep,$(DO)),"$$URL" "$(REASONS)" "$$NOTE",) $(if $(filter requeue,$(DO)),"$$URL",) $(if $(filter stands,$(DO)),"$$URL" "$$NOTE",) $(if $(filter retire-cited,$(DO)),"$$KEY" "$(ACCESS)" "$$NOTE",)

cite-uncited: ## [project] an uncited source's entry moved to the works cited, keeping its number, when a footnote first cites it - then write its Used for: line (feature 312)   KEY=<registry key>
	@if [ -z "$$KEY" ]; then printf 'make cite-uncited: KEY=<the uncited entry'"'"'s key> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record uncited cite "$$KEY"

attempts: ## [project] what a source was tried for and what came of it, and the filter's verdict on it - by URL, registry key, or question - BEFORE you read it again (feature 312)   URL=<u> | KEY=<k> | Q=<NNNN>
	@if [ -z "$$URL$$KEY$$Q" ]; then printf 'make attempts: URL=<u>, KEY=<k> or Q=<NNNN> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record attempts show $(if $(URL),--url "$$URL",$(if $(KEY),--key "$$KEY",--q "$$Q"))

archive: ## [project] archive ONE cited URL now into the private source archive - the served bytes, the whole page, its text - and write its manifest row (feature 309; the record build refuses a cited URL with none)   URL=<u> [KEY=<registry key not yet written>]
	@if [ -z "$$URL" ]; then printf 'make archive: URL=<u> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record archive url "$$URL" $(if $(KEY),--key "$$KEY",)

archive-sources: ## [project] archive every cited URL with no copy yet (resumable; run it in the background) - or REPORT=1, the coverage table without fetching; GM=1, the GM's matched files copied in; CONSULTED=1, the uncited pages feature 312's filter KEPT, and no other (features 309, 312)   [WORKERS=4] [REPORT=1] [GM=1] [CONSULTED=1 [LIMIT=<n>]]
	@if [ -n "$(CONSULTED)" ]; then "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record archive consulted $(if $(LIMIT),--limit $(LIMIT),) --workers $(or $(WORKERS),4); else "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record archive $(if $(REPORT),report,$(if $(GM),gm-copies,backfill --workers $(or $(WORKERS),4))); fi

archive-inbox: ## [project] the GM's downloads in /host-l7r-repo/academic-sources/ archived, the push confirmed, then removed from it - run at the start of every research pass; a NEW download waits until you give its keys (feature 309)   [MATCH="<file>=<key>[,<key>] ..."] [NONE="<file> ..."]
	@set -f; set --; for m in $$MATCH; do set -- "$$@" --match "$$m"; done; for n in $$NONE; do set -- "$$@" --none "$$n"; done; \
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record archive inbox "$$@"

semantic-index: ## [project] build or update the semantic index of the record and the archive - only new or changed passages embedded, its shards committed to the archive and pushed (feature 447; BGE-M3, run locally, half the cores; Rust since 449 T138)   [SHARD=<s>] [LIMIT=<n>]
	@set -f; set --; for s in $$SHARD; do set -- "$$@" --shard "$$s"; done; \
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record semantic build "$$@" $(if $(LIMIT),--limit "$(LIMIT)",)

semantic-find: ## [project] the passages of the record and the archive nearest a question by meaning, in any language - each with its file, place and opening words; beside archive-find, never in its place (feature 447)   Q="<question>" [K=<n>]
	@if [ -z "$$Q" ]; then printf 'make semantic-find: Q="<question>" is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record semantic find "$$Q" $(if $(K),--k "$$K",)

research-search: ## [project] THE local search before the web: the meaning search (a question per language) and the text search (term sets, every term required) over the record and the archive in one call, merged by source, each printed once with its best passage and what found it; a call prints a batch and counts the rest, and under KEY= the next call prints the next batch, never one already shown (feature 447 amendment 3)   Q="<english>" [Q_JA="<日本語>"] [Q_ZH="<中文>"] [Q_KO="<한국어>"] [TERMS="a|b;c|d"] [KEY=<question key>] [LIMIT=<archive sources, 15>] [RECORD_LIMIT=<pages, 5>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record search $(if $(Q),--q "$$Q",) $(if $(Q_JA),--q "$$Q_JA",) $(if $(Q_ZH),--q "$$Q_ZH",) $(if $(Q_KO),--q "$$Q_KO",) $(if $(TERMS),--terms "$$TERMS",) $(if $(KEY),--key "$$KEY",) $(if $(LIMIT),--limit "$(LIMIT)",) $(if $(RECORD_LIMIT),--record-limit "$(RECORD_LIMIT)",)

archive-find: ## [project] does the archive already hold it? by URL, registry key, or words in the archived text - names each copy's local path; exit 1 when nothing is held (feature 309: look here BEFORE the web)   URL=<u> | KEY=<k> | TERMS="a|b" (every term required; one term per call to try alternatives)
	@if [ -z "$$URL$$KEY$$TERMS" ]; then printf 'make archive-find: URL=<u>, KEY=<k> or TERMS="a|b" is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record archive find $(if $(URL),--url "$$URL",) $(if $(KEY),--key "$$KEY",) $(if $(TERMS),--terms "$$TERMS",)

downloads-ingest: ## [project] on the GM's word "ingest": the marks in the GM's copy of the download list recorded in research/to-download.md, then the inbox archived (feature 313)   [KEEP="<ids>"] [DROP="<ids>"] [MARK="<id>=<downloaded|partial|paywalled|not-found> ..."]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record downloads ingest --keep "$(KEEP)" --drop "$(DROP)" --mark "$$MARK"

downloads-sync: ## [project] on the GM's word "sync": the GM's copy of the download list replaced from research/to-download.md - refused while it holds anything not ingested (feature 313)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record downloads sync

downloads-tag: ## [project] tag every download-list entry [money] or [diagram] after its number, derived from the questions its Rests-on line points at (the GM, 2026-10-20); download-add tags a new entry itself
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record downloads tag

download-add: ## [project] append a source only the GM can fetch at the end of the canonical download list, under the next number taken under a host-wide lock (feature 313)   FILE=<draft.md, entries headed "### NEW. <the work>">
	@if [ -z "$(FILE)" ]; then printf 'make download-add: FILE=<draft.md> is required - entries headed "### NEW. <the work>", each with a link line, "- Fallback:", "- **Rests on it:**" naming research/questions/<file>, and "- Blocked by:"\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record downloads add "$(FILE)"

access-tags: ## [project] what can be got of each source - open, gm-full, gm-partial, paywalled, bot-refused, down, gone, never-read - derived from the archive, the registry and the GM's marks (feature 313)   [KEY=<key|download:ID>] [JSON=1] | SET=<state> KEY= DATE=<YYYY-MM-DD> REASON="<what it rests on>"
	@if [ -n "$(SET)" ]; then "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record access-tags set "$$KEY" "$(SET)" "$(DATE)" "$$REASON"; \
	else "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record access-tags report $(if $(KEY),--key "$$KEY",) $(if $(JSON),--json,); fi

sources-consulted: ## [project] every earlier read of a source page, with its outcome, from the sources-consulted ledger - by URL, or by registry key (feature 288)   URL=<u> | KEY=<regex>
	@if [ -z "$$URL$$KEY" ]; then printf 'make sources-consulted: URL=<u> or KEY=<regex> is required\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record sources lookup $(if $(URL),--url "$$URL",) $(if $(KEY),--key "$$KEY",)

sources-import: ## [project] ONE TIME, idempotent: seed the sources-consulted ledger from the 2026-09-29 measurement and import the /tmp/l7r-check saves into the page cache (feature 288)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record sources import

stale-terms:    ## [project] after a value changed in a feature's spec, where does the OLD value still stand - look BEFORE a later review round   F=253 [AGAINST=<git ref>]
##  F=<feature>    the feature number or directory name under specs/
##  AGAINST=<ref>  compare with the feature directory at this git ref (default: what the previous review round saw)
	@if [ -z "$(F)" ]; then printf 'make stale-terms: F=<feature> is required - e.g. make stale-terms F=253\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record stale-terms "$(F)" --clone "$$(git rev-parse --show-toplevel)" $(if $(AGAINST),--against "$(AGAINST)",); test $$? -le 1

size-table:     ## [project] every drawn rect, wall gap and stroke of a Mode A plan in feet (3 px = 1 ft) - run BEFORE size-audit (Rust since 449 T174, `l7r-mode-a`)   PLAN=pool/<subject>.svg
##  PLAN=<svg>     the plan's SVG, relative to the skill directory or absolute
	@if [ -z "$(PLAN)" ]; then printf 'make size-table: PLAN=<plan svg> is required - e.g. make size-table PLAN=pool/<tier>/<name>/<name>.svg\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a size-table "$(abspath $(PLAN))"

review-accept:  ## [project] record a review finding as deliberately LEFT, with a reason - logged like an escape   MAP=<map> FINDING=<id> REASON="..."
##  MAP=<map>        the pool map whose last settlement-review verdict raised the finding
##  FINDING=<id>     the finding's id, as that verdict record names it
##  REASON="..."     why it is left; at least two words and eight characters
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews prereq accept --clone "$$(git rev-parse --show-toplevel)" --map "$(MAP)" --finding "$$FINDING" --reason "$$REASON" && $(LOGBYPASS) permitted "review-accept $(MAP) $${FINDING}: $$REASON"

review-paired-gate:  ## [project] the settlement-review's paired gate - green, running or red (exit 1 on red); UNIT= a unit's own, its review tree snapshot's gate where `make verify` took one (451 T164)   [UNIT=<unit>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews prereq gate-state --clone "$$(git rev-parse --show-toplevel)" $(if $(UNIT),--unit "$(UNIT)",)

ledger-owed:     ## [project] every check pass logged in this clone with no row in the review ledger, each with the row to add (feature 371); WRITE= writes them from each reply   [WRITE="<where you recorded what you did>"]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews ledger-owed --ledger "$$(git rev-parse --show-toplevel)/dev/review-ledger.md" $(if $(WRITE),--write "$$WRITE" --by-hand $(if $(CLAUDE_CODE_SESSION_ID),--session "$(CLAUDE_CODE_SESSION_ID)",),)

dispatch-dropped: ## [project] record that a dispatch a guard refused is no longer wanted, so the turn may end (feature 385 T22)   TYPE=<agent type> BUNDLE=<path> WHY="<reason>"
	@"$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" dropped drop --root "$$(git rev-parse --show-toplevel)" --type "$(TYPE)" --bundle "$(BUNDLE)" --why "$$WHY"

review-cost:     ## [project] a finished review agent's wall time and tokens - the ledger's cost cells (feature 294)   AGENT=<agent id>
##  AGENT=<id>  the agent id the Agent tool's result names
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews review-cost --agent "$(AGENT)"

review-census:   ## [project] is each review check pulling its weight? the ledger's totals by check (feature 294)
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews census --root "$$(git rev-parse --show-toplevel)"

review-verdict:  ## [project] a review check's LAST act - write the unit's verdict record   UNIT=<unit> VERDICT=PASS|NEEDS-WORK|NOT-REVIEWABLE [FINDINGS=<json file>] [SCOPE=change]
##  UNIT=<unit>        the owed unit reviewed (its prompt's UNIT: line; MAP= is the same field)
##  VERDICT=<v>        PASS, NEEDS-WORK or NOT-REVIEWABLE
##  FINDINGS=<file>    a JSON list of {"id", "severity", "what"}; ids default to F1, F2, ...
##  SCOPE=change       a change-scoped round's verdict (`make review-fixed`): written into the record as `scoped`, carrying it if clean
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews prereq verdict --clone "$$(git rev-parse --show-toplevel)" --unit "$(or $(UNIT),$(MAP))" --verdict "$(VERDICT)" $(if $(FINDINGS),--findings-file "$(FINDINGS)",) $(if $(SCOPE),--scope "$(SCOPE)",)

review-fixed:    ## [project] a sheet edit that fixed ONLY building-review nitpicks owes a change-scoped adversarial round, not a full one: writes its prompt (451 T199)   UNIT=<unit> FINDING="<ids>"
##  UNIT=<unit>        the owed building-review unit, after `make verify` snapshotted the sheet as edited
##  FINDING="<ids>"    the nitpick ids of its last verdict the edit fixed; refused if any is not a nitpick, or an error or questionable one is open
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews prereq fixed --clone "$$(git rev-parse --show-toplevel)" --unit "$(or $(UNIT),$(MAP))" --finding "$$FINDING"

review-discharge: ## [project] the round arbiter's accept recorded as the discharge of owed glyph-checks, each bound to its kind's marks as drawn now: the owed list drops them while those marks stay so (449 T377)   RULING=<trigger> UNITS="<unit> ..."
##  RULING=<trigger>   the arbiter's ruling, an `accept` in a specs/*/arbiter.jsonl (e.g. ask:glyph-occasions-emit-449-T351)
##  UNITS="<u> ..."    the owed glyph-check units it accepts; all or none are recorded
	@if [ -z "$(RULING)" ] || [ -z "$$UNITS" ]; then printf 'make review-discharge: RULING=<trigger> and UNITS="<unit> ..." are required - e.g. make review-discharge RULING=ask:glyph-occasions-emit-449-T351 UNITS="glyph-check--well--county-magistracy-example"\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" reviews discharge --root "$$(git rev-parse --show-toplevel)" --ruling "$(RULING)" $$UNITS

parts-sweep:     ## [tests] run each split guard suite at 1, 2, 3 and 8 parts and report any count whose result differs - after a suite's cases change; never in the gate   [SUITES="test-pair-hooks.sh ..."]
	@set -f; bash tests/hooks/parts_sweep.sh $$SUITES

subagent-cache:  ## [project] what subagents write to the prompt cache fresh, per agent type, and the repeated text in their bundles (feature 383 amendment 6)   [SINCE=YYYY-MM-DD]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure subagent-cache $(if $(SINCE),--since $(SINCE),)

wave-report:     ## [project] a workflow wave's cost - each agent's first-request cache read and write, the main session's wakes - against the last hand-launched wave (feature 383 amendment 7)   [WF=<.../workflows/wf_*>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure wave-report $(if $(WF),--run $(WF),)

# Timed with date +%s, not $$SECONDS: make's shell is sh, where SECONDS is unset.
# The ratchet and the budget judge warm, selective runs only; raise the budget only with a measurement.
quick:           ## [tests] tier 2: the fast tree checks (no Python test remains since feature 449 T211; pytest is gone since T213, ruff since T158)
	@$(call TIMED,quick,quick,$(MAKE) --no-print-directory _quick)

# make quick's checks, timed whole by `quick` into its Phase line (feature 451 T153)
# THE DERIVED FILES (451 T198): each file `make done`'s preflight regenerates is checked here too, so a stale one fails a builder's
# closing checks naming its regenerate command instead of costing a red `make done` (0.05-0.11 s each; pinned by `derived_quick.rs`).
_quick:
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check house-style-delta --selftest >/dev/null
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check house-style-delta .
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check question-size
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check file-scale .
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check spec-lint --delta .
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" make-docs . --check
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" mode-a building-programs --check
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" record check glossary
	@if "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check needs partial-citations; then "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check partial-citations .; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check gm-attributions .
	@printf '\n\033[1mquick: clean\033[0m - `make done` before pushing.\n'
	@$(STATE) green-local quick

# THE CLOSING CHECKS AT ONCE (feature 451 T55): a builder's three closing checks ran one after another while it wrote its plan section,
# decide and report, none of which needs their result; started in the background the moment the code is done, they run side by side.
# One run of `make static` for static-runs-hooks; FRESH=1 REASON= and HOOKS_ALL=1 reach the checks as on their own targets.
# THE CALLER'S TASK (451 T86): T= (F= when two features share a task number) judges the files and crates that task changed, another
# task's red in the same clone reported apart and not counted (the script's header); with no T= the whole clone, as before.
closing-checks:  ## [tests] make static, make hooks-test and make quick at once, one combined result (each verdict and log; red if any is): start it with run_in_background once the code is done, then write the plan section and run make decide while it runs (451 T55); T= judges that task's files and crates, another task's red reported apart, not counted (451 T86); T=a,b,c judges a bundle's files as one task's (451 T141); without F= the task's feature is SPECIFY_FEATURE, else the pool registry's holder of this tree, else this tree's start mark, else refused with the command, as is a run that sets files apart while none is one the task's own edits name (451 T303)   T=<task> [F=<feature>] [FRESH=1 REASON="..."] [HOOKS_ALL=1]
	$(DISK_FLOOR)
	@CLOSING_TASK="$(T)" CLOSING_FEATURE="$(F)" "$$(git rev-parse --show-toplevel)/scripts/gates/closing-checks.sh"

bypass-audit:    ## [project] every escape token taken, with the reason its user gave   (the FULL prompt reads this)
	@why="$$REF_WHY"; \
	if [ -n "$$why" ] && [ ! -t 0 ]; then \
	  printf "\n\033[1mREFUSED: a FULL run with REF_WHY set, with nothing attached to answer for it.\033[0m\n\n"; \
	  printf "The prompt below exists because its default answer is NO. Passing REF_WHY on the\n"; \
	  printf "command line skips it, and a backgrounded run cannot be asked to reconsider - which is\n"; \
	  printf "exactly how feature 126 ran the full gate THREE times against a standing instruction to\n"; \
	  printf "run only the reference settlement. Every bypass was logged and none was stopped.\n\n"; \
	  printf "  \033[1mmake rust-test CRATE=rust/mode_a\033[0m  the pool sweep: every pool sheet through its tier's checks\n"; \
	  printf "  \033[1mmake done\033[0m        reference + lint/types + the suite (NOT the quick one)\n\n"; \
	  printf "If you truly need the FULL set, run it in the FOREGROUND and answer the prompt.\n\n"; \
	  $(LOGBYPASS) refused "$$why"; \
	  exit 1; \
	fi; \
	if [ -z "$$why" ]; then \
	  printf '\n\033[1mAbout to run the FULL test set.\033[0m\n\n'; \
	  printf 'The reference settlement rebuilds in ~60 s. The full set additionally rolls every\n'; \
	  printf 'live pool map and re-gates each - minutes, not seconds.\n\n'; \
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

_reference:
	@:

IDLE_CTX = $(eval IDLE_CTX := $(shell $(SWITCH) idle 2>/dev/null || echo unreadable))$(IDLE_CTX)
DONE_NAME = $(if $(filter 0,$(IDLE_CTX)),done,idle-done)
idle-tests:     ## [tests] {inactive: arming is disabled - the GM turned it off 2026-09-06; the target still runs by hand} what an idle session runs unattended (feature 136): the whole gate, never FULL, recorded as `idle-done`
	@PAIR_OK="idle run: no session attached to dispatch a review" $(MAKE) --no-print-directory done INCREMENTAL=0; rc=$$?; \
	  "$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" log usage --tool idle-tests --kind target --outcome "$$( [ $$rc -eq 0 ] && echo passed || echo failed )"; \
	  exit $$rc

builder-status:  ## [project] each builder of an open task the session reads as running, said working or stalled, and each dead-producer waiter, by the idle check's own reading: the session's last Stop list, re-read now (451 T193) - the coordinator's status of a builder, never its last message   [TRANSCRIPT=<the session's .jsonl; default the newest under ~/.claude/projects/-diagram>]
	@t="$(TRANSCRIPT)"; [ -n "$$t" ] || t=$$(ls -t "$$HOME"/.claude/projects/-diagram/*.jsonl 2>/dev/null | head -1); \
	  "$$(git rev-parse --show-toplevel)/scripts/hooks/l7r-guard.sh" --builder-status "$$t"

.PHONY: builder-status
.PHONY: review-yield cohort-seeds task-add task-unstart task-withdraw set-down where-time task-time task-progress land-batch fix-yield
review-yield:     ## [performance] each review check's passes, findings acted on / dismissed / deferred, author-missed, hours and tokens, from the ledger   [SINCE=2026-09-26]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure review-yield $(if $(SINCE),--since $(SINCE),)

fresh-tally:      ## [performance] seeds nobody has used: the failed share pooled, by form and by cause (feature 417)   [COMMIT=<sha prefix>] [SINCE=<UTC stamp>]
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" measure fresh-tally $(if $(COMMIT),--commit "$(COMMIT)",) $(if $(SINCE),--since "$(SINCE)",)

guard:           ## [static] {internal} refuse to run in main's tree - main is the integration point, never a workspace
	@top=$$(git rev-parse --show-toplevel 2>/dev/null); \
	case "$(CURDIR)" in */.clones/*) exit 0 ;; esac; \
	if [ -n "$$top" ] && [ -d "$$top/.clones" ] && [ "$$DIAGRAM_ALLOW_MAIN" != 1 ]; then \
	    echo "ERROR: this ran from the MAIN tree ($$top). Main is the integration point, never a workspace."; \
	    echo "Check CLAUDE.md, section 'Session clones' (reload CLAUDE.md if it has fallen out of your context"; \
	    echo "window): create or reuse .clones/<kebab-cased-session-name>, sync it in with 'git pull origin main',"; \
	    echo "and run this same command from inside that clone. (GM override: DIAGRAM_ALLOW_MAIN=1)"; \
	    exit 1; \
	fi

static format test: | guard

# THE CLAIMS FORM BEFORE THE LANDING (feature 449 T169): `claims coverage --rust` names a walked crate's unit with no `Research:` claim,
# which T168 met only at `make claims-owed`, before lint; it reads the Rust alone, 0.05 s over every walked crate (measured 2026-11-17).
# NO CRATE BUILDS ON THE GUARD (feature 451 T66): `check guard-deps` refuses a manifest under rust/ naming `l7r_guard`, but the guard's,
# so a hook edit keeps rebuilding the guard alone (T58: 1 crate where the dependents made it 32); it names `l7r_shared` instead.
static:        ## [static] the static checks: file-scale, the Rust crates' checks (was `lint`), each crate's kept green result reused while its inputs stand (449 T93)   [FRESH=1 REASON="..."]
	$(FRESH_ESCAPE)
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check file-scale --selftest
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check file-scale .
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check question-size --all
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" claims --root "$$(git rev-parse --show-toplevel)" coverage --rust
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust lint
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust format --check
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust cover
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust dead
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check spec-lint --selftest
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check spec-lint --delta .
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check audit-register --selftest
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check audit-register --delta "$$(git rev-parse --show-toplevel)"
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check conflict --selftest
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check conflict --tracked .
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" check guard-deps --root "$$(git rev-parse --show-toplevel)"
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" make-docs . --check
	bash scripts/reviews/layout_carry.sh --selftest

rust-test:       ## [project] cargo test over the Rust phases' crates (or CRATE=<dir>), in the shared target directory - a bare cargo is refused like a bare pytest (feature 444 T17); only the crates whose sources, test binary or declared reads moved since their last green run, the rest's result reused (449 T93); ONLY= hands its words to the test binaries as name filters, a builder's run of the tests its change reaches, kept as no crate's green (451 T435)   [CRATE=tests/fixtures/rust/fixture] [ONLY="<module::path> ..."] [FRESH=1 REASON="..."]
	$(FRESH_ESCAPE)
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust test $(if $(CRATE),--crate "$(CRATE)",) $(if $(ONLY),--only "$$ONLY",)

# THE EDIT LOOP OF A TASK'S CRATES IN ONE COMMAND (451 T170): static-runs' refusal (451 FR-007) names this with the delta's crates
# said once, where it named four commands a crate and reached builders at up to 7,909 characters; each step runs every crate at once.
crate-checks:    ## [static] a task's crate-scoped checks while iterating - test, lint, format --check and cover, each over every crate CRATE= names, all reported, red if any is - the edit loop in place of a third make static (451 FR-007, T170)   CRATE="<dir> ..."
	@if [ -z "$(CRATE)" ]; then printf 'make crate-checks: CRATE="<crate dir> ..." is required - e.g. make crate-checks CRATE="rust/guard rust/guard/shared"\n' >&2; exit 2; fi
	@g="$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh"; rc=0; \
	for step in test lint "format --check" cover; do "$$g" rust $$step $(foreach c,$(CRATE),--crate "$(c)") || rc=1; done; exit $$rc

# THE FIRST TIER (feature 451 T308, the GM 2026-11-26: the full rigor belongs where work reaches main, not where a builder's tree
# reaches the session clone). A builder's tree runs this and nothing heavier: the changed crates' tests, lint and format - no coverage
# build, no hook-suite fan-out. Measured 2026-11-26: of a three-builder run's compile minutes coverage builds were 57.9 and coverage
# runs 19.8 against lint 33.2 and test builds 6.2, and every memory and compiler peak fell where three trees were in a coverage build
# at once. The second tier is the landing's gate (make land), once over the batch carried into the clone.
builder-checks:  ## [static] the FIRST TIER, a builder's checks in its own tree - test, lint and format --check over every crate CRATE= names, and the push's audit-register row over the tree's delta (451 T527), all reported, red if any is; no coverage and no hook suites: those run once at the landing's gate over the batch (451 T308)   CRATE="<dir> ..."
	@if [ -z "$(CRATE)" ]; then printf 'make builder-checks: CRATE="<crate dir> ..." is required - e.g. make builder-checks CRATE="rust/guard rust/guard/shared"\n' >&2; exit 2; fi
	@top="$$(git rev-parse --show-toplevel)"; g="$$top/scripts/gates/l7r-gate.sh"; rc=0; \
	for step in test lint "format --check"; do "$$g" rust $$step $(foreach c,$(CRATE),--crate "$(c)") || rc=1; done; \
	"$$g" check audit-register --delta "$$top" || rc=1; exit $$rc

# FR-008's timer (feature 449 T169): T99's method - each test alone, best of three, a fresh TMPDIR, timed around the process - which
# T160, T164, T167 and T168 each ran by hand. It reports and never refuses: time is never a gate (the GM's performance rule).
test-times:      ## [project] each test of a crate timed alone by T99's method (best of three, a fresh TMPDIR, around the process), those over FR-008's tenth of a second listed, a declared end-to-end test marked; reports, never refuses (449 T169)   CRATE=<dir>
	@if [ -z "$(CRATE)" ]; then printf 'make test-times: CRATE=<crate dir> is required - e.g. make test-times CRATE=rust/mode_a\n' >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust test-times --crate "$(CRATE)"

format:         ## [static] rustfmt over the Rust phases' crates (feature 444 T17), or over CRATE=<dir>'s alone, or FILE=<path>'s alone - that file, not its mod children, with its crate's edition (451 T34)   [CRATE=<dir>] [FILE="<path> ..."]
	"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh" rust format $(foreach c,$(CRATE),--crate "$(c)") $(foreach f,$(FILE),--file "$(f)")

# THE PORT SWITCH (feature 444 amendment 8, FR-023; the GM 2026-11-07: "the functionality of a make done or a make land are both
# going to have to change temporarily"): at rust-only, make done rolls no map - no map-rolling test, no reference map, no floor that
# rolls a settlement - so nothing waits on the Python stages after the Rust front. `make port-integrated` throws it back.
PORT = $(eval PORT := $(shell $(SWITCH) state port 2>/dev/null || echo rust-only))$(PORT)
CPU_COUNT ?= $(shell nproc 2>/dev/null || echo 8)

# PYTEST IS GONE (feature 449 T213, after T211 deleted the last Python test and FR-001b, the GM 2026-11-10: "Yes delete everything except
# that group, please."): the gate's test phase (`test`, `test-full`), `test-file`, `durations` and `soak` ran pytest and are retired with
# it; the Rust crates' tests run under `make rust-test` and `make static`, the guard suites under `make hooks-test`.

# EVERY MAKE INVOCATION RECORDS ITS RUN (feature 406 T02, D161; the GM 2026-10-19: "it is notionally possible for us to see how
# often a tool is used"). The event log sees a target only when a session's Bash call runs it; one run from another target's
# recipe, from a script or from the idle timer left no trace. Each parse records its goals `ran` in <git dir>/tool-usage.jsonl
# (the default goal's name when none is given); `make -n` and `make -q` run nothing and record nothing. `make tool-yield` counts
# a target's runs from these lines alone and reads their outcomes from the event log. The line is the gate's (`l7r-gate log goals`,
# feature 449 T129), where a Python start on every parse was `usage_log.py`'s; a build the gate owes runs here first, as for any target.
ifeq (,$(findstring n,$(filter-out --%,$(firstword $(MAKEFLAGS))))$(findstring q,$(filter-out --%,$(firstword $(MAKEFLAGS)))))
_TOOL_YIELD_RAN := $(shell L7R_GATE_STALE_OK=1 "$(dir $(abspath $(firstword $(MAKEFILE_LIST))))scripts/gates/l7r-gate.sh" log goals $(or $(MAKECMDGOALS),$(.DEFAULT_GOAL)) >/dev/null 2>&1)
endif
