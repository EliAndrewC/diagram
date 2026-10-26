# The diagram project's operations: `make help` lists them, `make docs` writes docs/make-targets.html from the `##` lines.
# A target's `##` line is published help text: keep notes and escape markers off it.
# Comments go above a target as `#` lines. A recipe's `: "..."` string is shell, so a backtick or $$( in it RUNS.
# A .PHONY name with no rule still exits 0: retire a target's .PHONY entry with its rule.

.PHONY: modal-bundle modal-prepass done docs static format typecheck test test-full guard perf perf-report maps _reference bypass-audit quick durations test-file page-check tick claim speckit-todo audit guard-edit guard-log perf-gate hooks-test explain citations fragment-move \
	 switches ci-off ci-on _switch \
	 map cohort cohort-landing hamlet cache-audit placement-stages pool-index pool-index-if-stale compound render-sync idle-tests \
	 why-placed   pack-audit     help \
	 notes-census glossary page-lit picture-diff \
	 ci-status ci-check ci-merge ci-measure ci-image commit-permitted \
	 perf-explain perf-confirm perf-audit perf-signoff perf-review perf-profile

# ---- performance: a bookend pair over band 1 is a flag mentioned at landing, never a refusal ----
PERF_REVIEW = python3 -m l7r.diagram.tools.perf_review
perf-explain:   ## [performance] for an investigation of a flagged slowdown: the session's written cause and its evidence     WHY="..." CONTROL=<key> | UNVERIFIED="..." [ENV=local|codebuild]
##  WHY=<text>           the session's written cause for a band-1 increase
##  CONTROL=<key>        a measurements.json key: a recorded run of the same subject with the attributed cause removed
##  UNVERIFIED=<text>    instead of CONTROL - why the attribution was not tested; logged like an escape
##  ENV=local|codebuild  which environment the increase was measured in (default: local)
	@$(PERF_REVIEW) explain --why "$(WHY)" --control "$(CONTROL)" --unverified "$(UNVERIFIED)" --environment "$(or $(ENV),local)" $(if $(UNVERIFIED),&& $(LOGBYPASS) permitted "perf-explain UNVERIFIED: $(UNVERIFIED)",)
perf-confirm:   ## [performance] {internal} an investigation's confirmation of the written cause - the perf-audit SUBAGENT runs this   VERDICT=consistent|inconsistent AS=perf-audit
##  VERDICT=consistent|inconsistent  whether the written cause matches the recorded per-stage delta
##  AS=perf-audit                    who is recording - only the subagent may pass this, and nothing else distinguishes the shells
	@$(PERF_REVIEW) confirm --verdict "$(VERDICT)" --note "$(NOTE)" --as "$(or $(AS),main)" --environment "$(or $(ENV),local)"
perf-audit:     ## [performance] an investigation's adjudication of a slowdown - the subagent records it   VERDICT=justified|not-justified|cannot-determine NECESSARY= COMMENSURATE= NO_WAY_AROUND= AS=perf-audit
##  VERDICT=justified|not-justified|cannot-determine  the band-2 adjudication
##  NECESSARY=<text>                                  is the slowdown necessary?
##  COMMENSURATE=<text>                               is it commensurate with the functionality gained?
##  NO_WAY_AROUND=<text>                              was there no good way around it?
##  AS=perf-audit                                     who is recording - only the subagent may pass this
	@$(PERF_REVIEW) audit --verdict "$(VERDICT)" --necessary "$(NECESSARY)" --commensurate "$(COMMENSURATE)" --no-way-around "$(NO_WAY_AROUND)" --note "$(NOTE)" --as "$(or $(AS),main)" --environment "$(or $(ENV),local)"
perf-arbiter:   ## [performance] an investigation may put a band-3 increase to the round arbiter - nothing waits on it (feature 375 amendment 5)   [ENV=local|codebuild]
	@s="$$($(PERF_REVIEW) arbiter-subject --environment "$(or $(ENV),local)")" || exit 2; \
	 $(MAKE) --no-print-directory arbiter-ask SUBJECT="$$s" WHY="band 3 on $(or $(ENV),local) for $(SPECIFY_FEATURE): accept this performance increase, or keep optimizing? The perf report is perf-report.txt beside this MANIFEST, the band-1 and band-2 records are in dev/perf-log/, and the band-3 standard is the GM's: necessary, commensurate, no way around it" && \
	 $(PERF_REVIEW) show --environment "$(or $(ENV),local)" > "/tmp/l7r-check/arbiter-ask-$$s/perf-report.txt"
perf-signoff:   ## [performance] records a sign-off the GM gave UNPROMPTED, in their words - owed by nothing since feature 375 amendment 5   WHY="..."
##  WHY=<text>  the GM's own words, given unprompted - band 3
	@$(PERF_REVIEW) signoff --why "$(WHY)" --as GM --environment "$(or $(ENV),local)"
perf-review:    ## [performance] each environment's newest bookend pair: its timing band, for information, and its call counts - an increase over the line, or an uncomparable pair, refuses until the round arbiter accepts (the push runs this; feature 427)
	@$(PERF_REVIEW) check
perf-fanout:    ## [performance] the call-volume survey: per stage, the Python calls at each size and their growth, and every chain of HOT calls or more up to the loop it hangs from (feature 427 T01)   [SEED=39] [HOUSEHOLDS="20 40"] [STAGES=all] [HOT=50000] [JOBS=3] [LABEL=adhoc]
	$(RUN).tools.perf_fanout --seed "$(or $(SEED),39)" --households "$(or $(HOUSEHOLDS),20 40)" --stages "$(or $(STAGES),all)" --hot "$(or $(HOT),50000)" --jobs "$(or $(JOBS),3)" --label "$(or $(LABEL),adhoc)"

perf-profile:   ## [performance] tier 2 evidence: cProfile ONE stage of ONE seed   SEED=25 STAGE=web [HOUSEHOLDS=10]
##  SEED=<n>      which seed to profile - e.g. `25`
##  STAGE=<name>  which single stage to cProfile - e.g. `web`
##  HOUSEHOLDS=<n> profile the reference at the scaling roll's size (10, 20, 40), where a growth was measured
	$(RUN).tools.perf_profile --seed "$(SEED)" --stage "$(STAGE)" $(if $(HOUSEHOLDS),--households "$(HOUSEHOLDS)",)

STATE = python3 -m l7r.diagram.ci state

# done runs every phase and reports every failure together, cheapest phase first.
# A run too fast to have worked is not stamped green (check-run-plausible.py): make runs $(MAKE)
# sub-invocations even under -n, so a dry run once wrote a green record the push honored.
done:            ## [tests] tier 3, the whole gate: lint, the static checks, the reference map, every test and the 100% floors; run once at the end, backgrounded   FULL=1 INCREMENTAL=0
	$(if $(ARBITER_OK),$(LOGESCAPE) ARBITER_OK "$(ARBITER_OK)",@h="$$(git rev-parse --show-toplevel)/scripts/hooks/lib/hm_arbiter.py"; [ ! -f "$$h" ] || python3 "$$h" gate-held || exit 1)
	@l="$$(git rev-parse --show-toplevel)/scripts/gates/gate_lock.py"; [ ! -f "$$l" ] || python3 "$$l" acquire "$$(git rev-parse --absolute-git-dir)" "$$PPID"
	$(if $(PREFLIGHT_OK),$(LOGESCAPE) PREFLIGHT_OK "$(PREFLIGHT_OK)",@:)
	@$(if $(PREFLIGHT_OK),:,p="$$(git rev-parse --show-toplevel)/scripts/gates/preflight.py"; tp=$$(date +%s); [ ! -f "$$p" ] || python3 "$$p" --root "$$(git rev-parse --show-toplevel)" --workers "$(XDIST_WORKERS)" --no-coverage || { touch "$$(git rev-parse --absolute-git-dir)/gate-preflight-red"; printf '\n\033[1mGATE FAILED: preflight\033[0m (fix it and re-run; nothing expensive has run)\n'; exit 1; }; $(RUNSTATS) phase-pre "$$(git rev-parse --absolute-git-dir)" preflight $$(( $$(date +%s) - tp )) 2>/dev/null || true)
	@p="$$(git rev-parse --show-toplevel)/scripts/gates/preflight.py"; [ ! -f "$$p" ] || python3 "$$p" --root "$$(git rev-parse --show-toplevel)" --tree-snap "$$(git rev-parse --absolute-git-dir)/gate-tree.json"
	@if [ -z "$(FULL)" ] && python3 -m l7r.diagram.ci verified-done; then \
	  root=$$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$$root" ] && python3 "$$root/scripts/gates/gate-stamp.py" --write diagram || true; \
	  python3 "$$(git rev-parse --show-toplevel)/scripts/gates/check-run-plausible.py" --reuse $(DONE_NAME) || exit 1; \
	  if ! python3 "$$root/scripts/gates/gate-stamp.py" --fresh hooks >/dev/null 2>&1; then echo "make done: ...but the hooks stamp is stale (a scripts/ or tests/hooks/ change) - running make hooks-test first"; $(MAKE) --no-print-directory hooks-test FROM_DONE= ||{ $(LOGRUN) $(DONE_NAME) reference 0 failed:hooks-test; $(COMMIT_RUN_RECORD) failed; exit 1; }; fi; \
	  $(LOGRUN) $(DONE_NAME) reference 0 already-verified; $(STATE) green-local $(DONE_NAME) reused; $(COMMIT_RUN_RECORD) already-verified; \
	  printf '\n\033[1mgate green\033[0m (already verified - nothing the gate exercises has changed since the last green run)\n'; exit 0; \
	fi; \
	$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" || exit 1;,) \
	T0=$$(date +%s); fail=""; \
	rm -f "$$(git rev-parse --absolute-git-dir)/roll-cache-class"; \
	G=$$(git rev-parse --absolute-git-dir); $(RUNSTATS) start "$$G" 2>/dev/null || true; export L7R_GATE_FAILURES="$$G/gate-failures"; \
	for phase in static format typecheck; do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; ts=$$(date +%s); \
	  $(MAKE) --no-print-directory $$phase || { fail="$$fail $$phase"; $(RUNSTATS) fail "$$G" $$phase 2>/dev/null; }; \
	  $(RUNSTATS) phase "$$G" $$phase $$(( $$(date +%s) - ts )) 2>/dev/null || true; \
	done; \
	if [ -n "$$fail" ]; then RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (the static checks run FIRST now, so the map roll has not happened - fix these and re-run)\n' "$$fail"; exit 1; fi; \
	tr=$$(date +%s); $(if $(REF_OK),$(LOGESCAPE) REF_OK "$(REF_WHY)"; $(LOGBYPASS) permitted "REF_OK - reference step skipped: $(REF_WHY)"; printf '\nreference step SKIPPED (REF_OK, logged to dev/bypass-log/ and the firing log)\n';,$(MAKE) --no-print-directory _reference || { $(RUNSTATS) fail "$$G" reference 2>/dev/null; RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed: reference"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); exit 1; };) $(RUNSTATS) phase "$$G" reference $$(( $$(date +%s) - tr )) 2>/dev/null || true; \
	for phase in hooks-test test-full $(if $(FULL),perf-gate,); do \
	  printf '\n\033[1m== %s ==\033[0m\n' "$$phase"; \
	  if [ "$$phase" = hooks-test ] && root=$$(git rev-parse --show-toplevel 2>/dev/null) && python3 "$$root/scripts/gates/gate-stamp.py" --fresh hooks; then \
	    printf 'hooks-test: already green against exactly these guard scripts - skipped (gate-stamp --fresh hooks; 84 s measured 2026-08-26)\n'; continue; fi; \
	  ts=$$(date +%s); $(MAKE) --no-print-directory $$phase FROM_DONE=1 || { fail="$$fail $$phase"; $(RUNSTATS) fail "$$G" $$phase 2>/dev/null; }; \
	  $(RUNSTATS) phase "$$G" $$phase $$(( $$(date +%s) - ts )) 2>/dev/null || true; \
	done; \
	if [ -n "$$fail" ]; then RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed:$$fail"; $(COMMIT_RUN_RECORD) red; $(STATE) failed-gate $(DONE_NAME); printf '\n\033[1mGATE FAILED:%s\033[0m (every phase ran - fix them together, then re-run once)\n' "$$fail"; exit 1; fi; \
	root=$$(git rev-parse --show-toplevel 2>/dev/null); \
	mode=$$(python3 -m l7r.diagram.ci incremental mode 2>/dev/null || echo full); sel=$$(python3 -m l7r.diagram.ci incremental selected 2>/dev/null || true); \
	[ -z "$$root" ] || [ ! -f "$$root/scripts/gates/preflight.py" ] || python3 "$$root/scripts/gates/preflight.py" --root "$$root" --tree-check "$$(git rev-parse --absolute-git-dir)/gate-tree.json" || { RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" "failed: tree moved"; $(STATE) failed-gate tree-moved; $(COMMIT_RUN_RECORD) failed; exit 1; }; \
	python3 "$$root/scripts/gates/check-run-plausible.py" $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" "$$mode" || exit 1; \
	[ -n "$$root" ] && python3 "$$root/scripts/gates/gate-stamp.py" --write diagram && python3 "$$root/scripts/gates/gate-stamp.py" --write page || true; \
	$(if $(BROWSER_SKIP),,[ -n "$$root" ] && python3 "$$root/scripts/gates/gate-stamp.py" --write browser || true;) \
	RUN_MODE="$$mode" RUN_SELECTED="$$sel" RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" $(LOGRUN) $(DONE_NAME) "$(if $(FULL),full,reference)" "$$(( $$(date +%s) - $$T0 ))" green "$$(cat "$$(git rev-parse --absolute-git-dir)/roll-cache-class" 2>/dev/null || true)"; $(COMMIT_RUN_RECORD) green; \
	root=$$(git rev-parse --show-toplevel); \
	cls=$$(cat "$$(git rev-parse --absolute-git-dir)/roll-cache-class" 2>/dev/null || true); \
	scp="$(if $(FULL),full,reference)"; \
	med=$$(python3 "$$root/scripts/measure/gatecost.py" $(DONE_NAME) "$$scp" "$${cls:-}" 2>/dev/null | grep -oE '^[0-9]+' | head -1); \
	n=$$(python3 -c "import sys; sys.path.insert(0,'$$root/scripts/measure'); import gatecost as _gatecost; print(_gatecost.class_count('$(DONE_NAME)', '$$scp', None, '$$cls' or None))" 2>/dev/null || echo 0); \
	if [ "$$mode" = incremental ]; then printf 'ratchet: incremental run (%s tests) - not judged; the median is over full runs\n' "$$sel"; else python3 "$$root/scripts/measure/ratchet.py" $(DONE_NAME) "$$(( $$(date +%s) - $$T0 ))" "$${med:-}" "$${cls:-}" "$$scp" "$$n" || exit 1; fi; \
	$(STATE) green-local $(DONE_NAME); \
	$(if $(FULL),printf '\n\033[1mgate green (FULL - plus the perf bookends)\033[0m\n',printf '\n\033[1mgate green\033[0m (the whole suite and every pool map; `FULL=1` adds only the perf bookends)\n')

COHORT_FRESH = 4
REF_FIRST = @$(if $(REF_OK),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)",$(MAKE) --no-print-directory _reference)

# RUN carries make's @ prefix, so a $(RUN) line must start its recipe line, never follow a `\` continuation.
RUN = @python3 -m l7r.diagram

# ---- iteration switches (dev/switches.json) ----
SWITCH = python3 -m l7r.diagram.switches
REMOTE_OK = @python3 -m l7r.diagram.ci remote-ok "$@"

switches:       ## [project] the iteration switch: remote on|off, with reason, who and when (feature 132)
	@$(SWITCH) show
ci-off:         ## [remote] REMOTE OFF - nothing dispatches to CodeBuild; the gated push lands on a green local make done   REASON="..."
##  REASON=<text>  why remote is being switched off - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=off MSG="remote off" REASON="$(REASON)"
ci-on:          ## [remote] REMOTE ON - the default; the gated route may dispatch again   REASON="..."
##  REASON=<text>  why remote is being switched back on - recorded with who and when
	@$(MAKE) --no-print-directory _switch AXIS=remote STATE=on MSG="remote on" REASON="$(REASON)"
_switch:
	@[ -n "$(REASON)" ] || { printf '\n\033[1mREFUSED: a reason is required\033[0m - a reason someone will READ is a decision you have to defend.\n  make <target> REASON="..."\n\n'; exit 1; }
	@$(SWITCH) set $(AXIS) $(STATE) --why "$(REASON)"
	@git add dev/switches.json && git commit -q -m "chore: $(MSG) - $(REASON)" && printf '\ncommitted: %s - %s\n' "$(MSG)" "$(REASON)"

# ---- expensive: they generate ----
verify:         ## [tests] THE PAIRED RUN: start the gate and dispatch the settlement-review together (feature 151)
	@printf '\033[1mverify\033[0m: the gate and the independent review run TOGETHER - neither alone (GM 2026-08-29).\n'
	@root=$$(git rev-parse --show-toplevel) && python3 -m l7r.diagram.ci engine-key worktree > "$$root/.git/pairing-key" || true  # NOT $(RUN): it carries a leading @, which is a literal argument once it is not at the start of a recipe line
	@root=$$(git rev-parse --show-toplevel) && printf 'engine key %s\n' "$$(cut -c1-12 "$$root/.git/pairing-key" 2>/dev/null)"
	  @root=$$(git rev-parse --show-toplevel); undeclared=$$(python3 "$$root/scripts/reviews/review_owed.py" --root "$$root" --check-declared); \
	  [ -z "$$undeclared" ] || printf '\n\033[1mOCCASIONS NOT DECLARED\033[0m: %s\n' "$$undeclared"
	  @root=$$(git rev-parse --show-toplevel); \
	  maps=$$(python3 "$$root/scripts/reviews/review_owed.py" --root "$$root" | tr '\n' ' ' | sed 's/ $$//'); \
	  why=$$(python3 "$$root/scripts/reviews/review_owed.py" --root "$$root" --why); \
	  if [ -z "$$maps" ]; then \
	    printf '\n\033[1mNO REVIEW CHECK OWED\033[0m: %s (feature 294: a check is owed on its occasion, never because a manifest moved). The gate runs alone; the GM looks at the map.\n' "$$why"; \
	  else \
	    mirror=""; case "$$root" in */.clones/*) mirror="$${root%%/.clones/*}";; esac; \
	    for gen in $$(python3 "$$root/scripts/reviews/review_snapshot.py" --root "$$root" --stale-renders $$maps); do \
	      case "$$gen" in sheet:*) svg="$${gen#sheet:}"; printf 'verify: %s has no generator and no render - make sheet-render SHEET=%s OUT=%s, then make verify again\n' "$$svg" "$$svg" "$${svg%.svg}.png" >&2; exit 2;; esac; \
	      printf 'verify: rendering %s (its render was missing or older than its map)\n' "$$gen"; $(MAKE) --no-print-directory map GEN="$$gen" >/dev/null || { printf 'verify: make map GEN=%s failed - run it by hand, then make verify again\n' "$$gen" >&2; exit 2; }; done; \
	    snap=$$(python3 "$$root/scripts/reviews/review_snapshot.py" --root "$$root" $${mirror:+--mirror "$$mirror"} --key "$$(cat "$$root/.git/pairing-key" 2>/dev/null)" $$maps); \
	    n=$$(printf '%s\n' $$maps | wc -l); \
	    printf 'owed: %s\n%s\n' "$$why" "$$snap"; \
	    printf '\n\033[1mWHEN THE GATE IS GREEN, dispatch %s review agent(s), ONE PER UNIT\033[0m - each Agent call is the unit'"'"'s check (its slug begins with it) and takes the contents of its prompt file named above (.git/review-snapshot/<unit>/dispatch.md). A dispatch beside a running gate, or naming more than one unit, is refused (feature 294); a turn may not end with the gate green and an owed unit undispatched.\n' "$$n"; \
	  fi
	  @bash "$$(git rev-parse --show-toplevel)/scripts/gates/one-gate.sh"
	@printf '\nstarting the gate in the background, in a log of its own (.git/verify-gate.log links to it): WAIT WITH `make verify-wait`, run_in_background - its exit is the notification.\n\n'
	  @root=$$(git rev-parse --show-toplevel); log="$$root/.git/verify-gate-$$(date +%s).log"; ln -sfn "$$log" "$$root/.git/verify-gate.log"; \
	  PAIR_OK="started by make verify - the review is dispatched in the same turn" nohup $(MAKE) --no-print-directory done > "$$log" 2>&1 &

verify-wait:    ## [tests] wait for the gate `make verify` started, on ITS OWN log, and print its verdict - run it with run_in_background (exit 0 green, 1 red, 3 no log, 4 timed out, 5 the gate died)
	@bash "$$(git rev-parse --show-toplevel)/scripts/gates/verify_wait.sh"

map: export L7R_STAGE_PROFILE = $(if $(PROFILE),1,)
map:            ## [maps] regenerate ONE gen and gate it   GEN=pool/hamlets/inashiro/inashiro.gen.py [PROFILE=1: where the roll spent its time]
##  GEN=<gen path>  which generator to re-run (default: `pool/hamlets/inashiro/inashiro.gen.py`)
##  PROFILE=1       also print where the roll spent its time, stage by stage
##  REGEN_FROZEN=1  re-render a FROZEN legacy exhibit anyway - only on the GM's say-so (regen's --frozen-ok)
	$(if $(filter pool/hamlets/inashiro/inashiro.gen.py,$(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)),,$(REF_FIRST))
	$(RUN).pipeline.regen $(if $(REGEN_FROZEN),--frozen-ok,) $(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)
	@g="$(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)"; s="$${g%.gen.py}"; \
	if [ -f "$$s.json" ] && { [ ! -f "$$s.png" ] || [ ! -f "$$s.html" ]; }; then \
	  echo "map: the cached entry carries no render (a gate filed it with rendering skipped) - rolling it uncached to draw one"; \
	  $(patsubst @%,%,$(RUN)).pipeline.regen --no-cache "$$g"; \
	fi
	@g="$(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)"; s="$${g%.gen.py}"; \
	if [ -f "$$s.html" ] && [ -n "$$(find l7r/diagram/interactive/assets -type f -newer "$$s.html" -print -quit)" ]; then \
	  echo "map: a modal or page asset changed since the page was written - rolling it uncached to write the page again"; \
	  $(patsubst @%,%,$(RUN)).pipeline.regen --no-cache "$$g"; \
	fi
	@$(MAKE) --no-print-directory pool-index-if-stale
	@python3 scripts/measure/maps_moved.py --only "$(or $(GEN),pool/hamlets/inashiro/inashiro.gen.py)"

maps-moved:     ## [maps] which pool manifests differ from HEAD - the comparison a wave records, never a scratch copy (feature 429)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/maps_moved.py" --root "$$(git rev-parse --show-toplevel)"

cohort:         ## [maps] roll N seeds and report every failure      N=10 [SEED=<first seed>] [JOBS=<workers>] [HOUSEHOLDS=<n>]
##  N=<seeds>   how many seeds to roll, besides the six pinned rows (default: 10 - the GM, 2026-10-12, on the per-seed record: `make cohort-seeds`)
##  SEED=<n>    the FIRST seed to roll (default: 1) - `N=1 SEED=15` reproduces the cohort's own Audit-15
##  JOBS=<n>    worker processes (default: cpus - 2) - each holds a roll, ~0.5 GB; the containers share a 10 GB cap
##  FRESH=<n>   fresh seeds rolled beside the fixed ones, a rate never a pass/fail (default: COHORT_FRESH; 0 rolls none) - feature 386
##  FAILED_FIRST=1  roll the seeds that failed last run on this seed block first; LAST_FAILED=1 only those (feature 426)
##  EXITFIRST=1     stop at the first seed that fails (feature 426); a run that skips seeds is partial, never a landing record
	$(REF_FIRST)
	$(RUN).tools.cohort_audit --count $(or $(N),10) $(if $(SEED),--seed $(SEED),) $(if $(JOBS),--jobs $(JOBS),) $(if $(HOUSEHOLDS),--households $(HOUSEHOLDS),) $(if $(FAILED_FIRST),--failed-first,) $(if $(LAST_FAILED),--last-failed,) $(if $(EXITFIRST),--exitfirst,) $(if $(EXITFIRST_AGAINST),--exitfirst-against $(EXITFIRST_AGAINST),) $(if $(filter-out 0,$(or $(FRESH),$(COHORT_FRESH))),--fresh $(or $(FRESH),$(COHORT_FRESH)) --fresh-from $$(python3 scripts/gates/cohort_gate.py fresh-seed),); rc=$$?; python3 scripts/measure/cohort_known.py --root . --stamp; $(COMMIT_RUN_RECORD) "$$([ $$rc = 0 ] && echo pass || echo fail)" last-cohort-record; [ $$rc = 0 ] || python3 scripts/measure/cohort_known.py --root .; exit $$rc

probe:          ## [maps] what a change does to every seed and pool map against HEAD: the landing cohort, HEAD's fresh block and the pool in WT, every seed beside HEAD's stored verdict (feature 426)   [WT=<worktree>] [EXITFIRST=1] [JOBS=<n>]
	@python3 scripts/measure/probe.py --root . $(if $(WT),--wt $(WT),) $(if $(EXITFIRST),--exitfirst,) $(if $(JOBS),--jobs $(JOBS),)

cohort-landing: ## [maps] the landing cohort a gated push requires: main's baseline first when its engine has none, then seeds 1-48 and the pinned rows (the 48-seed fresh block, a rate never a refusal, rolls after the push - feature 415) - and what the push will say
	@if python3 scripts/gates/cohort_gate.py needs-baseline; then \
	  b=$$(mktemp -d)/base; echo "cohort-landing: main's engine has no 48-seed record - rolling main's baseline first, in a detached worktree ($$b)"; \
	  git fetch -q origin 2>/dev/null; git worktree add -q --detach "$$b" origin/main && { $(MAKE) --no-print-directory -C "$$b" cohort N=48 FRESH=0; git worktree remove --force "$$b"; }; \
	fi
	-@$(MAKE) --no-print-directory cohort N=48 FRESH=0
	@python3 scripts/gates/cohort_gate.py check

hamlet: export L7R_STAGE_PROFILE = $(if $(PROFILE),1,)
hamlet:         ## [maps] generate one hamlet from the CLI   ARGS="--name X --seed 4 ..." [PROFILE=1]
##  ARGS=<cli args>  passed to the hamletgen CLI - e.g. `"--name Foo --seed 4 --households 15"`
##  PROFILE=1        also print where the roll spent its time, stage by stage
	$(REF_FIRST)
	$(RUN).hamletgen $(ARGS)
	@$(MAKE) --no-print-directory pool-index-if-stale

cache-audit:    ## [maps] does using the generation cache change any map?
	$(REF_FIRST)
	$(RUN).tools.cache_audit $(ARGS)
placement-stages: ## [maps] re-plate the stage-by-stage walk-through page
	$(REF_FIRST)
	$(RUN).tools.placement_stages $(ARGS)

placement-stages-if-classes: ## [maps] {internal} re-plate the walk-through page only if the class registry moved (sync-in runs it)
	$(RUN).pipeline.render_cache --page-if-classes --no-allow-main

pool-index:     ## [maps] rebuild the pool index
	$(RUN).pipeline.pool_index $(ARGS)

pool-index-if-stale: ## [maps] {internal} rebuild the pool index only when a manifest, render or notes file is newer
	@if [ ! -f pool/index.html ] || [ -n "$$(find pool legacy-hand-authored-pool -newer pool/index.html \( -name '*.json' -o -name '*.png' -o -name '*.notes.md' \) -print -quit 2>/dev/null)" ]; then \
	  $(MAKE) --no-print-directory pool-index ARGS=; \
	fi

compound:       ## [maps] compose a DRAFT Mode A compound plan from a feet-based program - a starting point the GM then refines by hand
##  ARGS=<out.svg>  where to write the composed draft
	$(RUN).compound $(ARGS)

render-sync:    ## [maps] {internal} regenerate MAIN's renders (called by sync-with-main.sh; not for hand use)
	$(RUN).pipeline.render_cache $(ARGS)

# ---- cheap: they read a recorded artifact ----
why-placed:     ## [diagnostics] who placed this, and what refused to        GEN=... AT=x,y | REFUSED=x,y
##  GEN=<gen path>  the map to ask about
##  AT=x,y          what was PLACED at this point, and by which stage
##  REFUSED=x,y     what was REFUSED here, and which rule refused it
	$(RUN).tools.why_placed $(GEN) $(if $(AT),--at $(AT),)$(if $(REFUSED),--refused $(REFUSED),)

pack-audit:     ## [diagnostics] empty space and geometry in a HAND-DRAWN Mode A compound SVG   ARGS=<in.svg>
##  ARGS=<in.svg>  the Mode A compound SVG to measure
	$(RUN).tools.pack_audit $(ARGS)

scatter-bases:  ## [diagnostics] where a map's ground-cover scatter stands: base points per family, parsed from its SVG   MAP=pool/hamlets/sawada [BOX=x0,y0,x1,y1]
##  MAP=<pool map>      the map's folder, its stem, or its .svg
##  BOX=x0,y0,x1,y1     also list the bases inside this world-coordinate window
	@if [ -z "$(MAP)" ]; then printf 'make scatter-bases: MAP=<pool map> is required - e.g. make scatter-bases MAP=pool/hamlets/sawada BOX=600,1600,1300,2000\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/scatter_bases.py" "$(MAP)" $(if $(BOX),--box "$(BOX)",)

sheet-render:   ## [maps] render a hand-drawn Mode A sheet with its captions placed by the ONE placer (feature 286)   SHEET=<svg> OUT=<png>
##  SHEET=<svg>         the hand-drawn sheet (its drawing and its captions' declarations)
##  OUT=<png>           the picture to write
	@if [ -z "$(SHEET)" ] || [ -z "$(OUT)" ]; then printf 'make sheet-render: SHEET=<svg> and OUT=<png> are required - e.g. make sheet-render SHEET=pool/<tier>/<map>/<map>.svg OUT=/tmp/<map>.png\n' >&2; exit 2; fi
	@python3 -m l7r.diagram.labels.hand_sheet "$(SHEET)" "$(OUT)"

page-lit:       ## [diagnostics] light ONE class on a map's page and report which classes' pixels change   MAP=<page.html> CLASS="<key>" [VECTOR=1] [OUT=lit.png]
##  the reviewer's page measurement (feature 231): raster mode at the opening view, VECTOR=1 past the switch
	@if [ -z "$(MAP)" ] || [ -z "$(CLASS)" ]; then printf 'make page-lit: MAP=<page.html> CLASS="<class key>" are required - e.g. make page-lit MAP=pool/hamlets/kuwabata/kuwabata.html CLASS="mulberry dike"\n' >&2; exit 2; fi
	$(RUN).tools.page_lit "$(MAP)" "$(CLASS)" $(if $(VECTOR),--vector,) $(if $(OUT),--out "$(OUT)",)

picture-diff:   ## [diagnostics] two renders compared: the differing share, the max delta, the bbox, and whose ink   A=<png|svg> B=<png|svg> [PAGE=<the new .html>]
##  the reviewer's picture measurement (feature 231); an SVG argument is rendered by the engine's own rasterizer,
##  and PAGE names the rendered page whose own id map says which class each differing pixel lies on
	@if [ -z "$(A)" ] || [ -z "$(B)" ]; then printf 'make picture-diff: A=<render> B=<render> are required - e.g. make picture-diff A=main.png B=pool/hamlets/kuwabata/kuwabata.svg PAGE=pool/hamlets/kuwabata/kuwabata.html\n' >&2; exit 2; fi
	$(RUN).tools.picture_diff "$(A)" "$(B)" $(if $(PAGE),--page "$(PAGE)",) $(if $(SVG),--svg "$(SVG)",)

notes-census:   ## [diagnostics] refresh the derived counts inside each map's notes census block   M="pool/hamlets/*/*.json"
##  M=<glob>  which manifests to refresh (default: every manifest in both pool trees)
	$(RUN).tools.notes_census $(or $(wildcard $(M)),$(wildcard pool/*/*/*.json) $(wildcard legacy-hand-authored-pool/*/*/*.json))

building-programs: ## [docs] render each declared Mode A type's required-items table into docs/building-programs.md from l7r/diagram/buildings/types.json (feature 254)   CHECK=1: exit 1 if stale
	$(RUN).tools.building_programs $(if $(CHECK),--check,)

glossary:       ## [docs] assemble interactive/assets/glossary.json from its per-term files, then write research/assets/glossary.js from it - the ONE glossary the map's modals and the record's pages share (features 209, 259)   CHECK=1: exit 1 if either is stale   SPLIT=1: the one-time split into per-term files
	$(if $(CHECK),@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/memo_check.py" glossary,$(RUN).tools.glossary_asset $(if $(SPLIT),--split,))

footnote-census: ## [docs] count the record's footnotes by kind - cited, grounds, ABSENT, settled. The ABSENT column is the backlog and the only one anybody has to act on (feature 235)
	$(RUN).tools.footnote_census

citations:      ## [docs] the same as `make record` (feature 301: the record's site carries the notes; kept as a name)   CHECK=1: as `make record CHECK=1`
	@$(MAKE) --no-print-directory record $(if $(CHECK),CHECK=1,)

record:         ## [docs] build the record's site, research/site/, from its questions (features 258, 301, 303) - a page per question, a page per section of each half and per tag, the whole record on one page   CHECK=1: build in memory and exit 1 on any refusal, writing nothing
	$(if $(CHECK),@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/memo_check.py" record,$(RUN).tools.record_asset)
	$(if $(CHECK),,@python3 "$$(git rev-parse --show-toplevel)/scripts/record/sources.py" mark-filled)

money-conversions: ## [docs] copy gm-assistant's money conversion table into research/assets/money-conversions.json, which the record's build converts each marked amount of money from (feature 413)   CHECK=1: write nothing, exit 1 while the copy is stale
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/money_conversions.py" $(if $(CHECK),--check,)

money-candidates: ## [docs] every amount of money in the record not yet marked for the conversion tooltip, those within 25 years of a built era first; each is marked or passed over with its reason in specs/413-money-tooltip-on-the-record/backfill.md (feature 413)   CHECK=1: exit 1 while one is neither
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/money_candidates.py" $(if $(CHECK),--check,) $(if $(ALL),--all,) $(if $(Q),--stem $(Q),) $(if $(CONTEXT),--context,)

source-tags-contract: ## [docs] derive research/source-tags.json's values and explanations into the source-applicability agent's contract (feature 305) - run after editing the vocabulary; a test fails while the block is stale   CHECK=1: write nothing, exit 1 while stale
	$(RUN).tools.source_tags_contract $(if $(CHECK),--check,)

fragment-move:  ## [docs] rename or renumber a question - every file of its stem - and rewrite every pointer to it - the record's own links, about: markers, confusables, the Entry: lines, the code and docs (features 301, 303)   FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html
	@test -n "$(FROM)" -a -n "$(TO)" || { echo "make fragment-move FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html" >&2; exit 2; }
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/fragment_move.py" "$(FROM)" "$(TO)" --root "$$(git rev-parse --show-toplevel)"

# The suites fan out in parallel. A suite that turns out to race is serialized, never retried: a retry hides the race.
hooks-test:     ## [tests] run every tests/hooks/test-*-hooks.sh, and prove each guard still has a companion
	@root=$$(git rev-parse --show-toplevel); gitdir=$$(git rev-parse --path-format=absolute --git-common-dir); fail=""; n=0; skipped=0; \
	work=$$(mktemp -d); trap 'rm -rf "$$work"' EXIT; \
	roster=$$(for h in $$root/scripts/hooks/*-hooks.sh $$root/scripts/gates/review-gate.sh $$root/scripts/gates/entry-gate.sh $$root/scripts/gates/claims-gate.sh $$root/scripts/gates/plan-gate.sh $$root/scripts/gates/gate-stamp.py $$root/scripts/gates/check-tool-signals.py $$root/scripts/sync-with-main.sh $$root/scripts/land-tooling.sh; do basename $$h; done); \
	traced=" $$(if [ -z "$(HOOKS_ALL)" ]; then python3 "$$root/tests/hooks/hooktrace.py" fresh "$$gitdir" "$$root" $$roster 2>/dev/null; fi | tr '\n' ' ') "; \
	export HOOKS_SHIM="$$(python3 "$$root/tests/hooks/hooktrace.py" shim "$$gitdir" 2>/dev/null)" HOOKS_ROOT="$$root"; \
	keys=$$(python3 "$$root/tests/hooks/hookdeps.py" --keys $$roster); \
	for h in $$root/scripts/hooks/*-hooks.sh $$root/scripts/gates/review-gate.sh $$root/scripts/gates/entry-gate.sh $$root/scripts/gates/claims-gate.sh $$root/scripts/gates/plan-gate.sh $$root/scripts/gates/gate-stamp.py $$root/scripts/gates/check-tool-signals.py $$root/scripts/sync-with-main.sh $$root/scripts/land-tooling.sh; do \
	  b=$$(basename $$h); case $$b in test-*) continue ;; esac; \
	  t=test-$${b%.py}; case $$t in *.sh) ;; *) t=$$t.sh ;; esac; \
	  if [ ! -f "$$root/tests/hooks/$$t" ]; then \
	    printf '\n\033[1mGUARD WITHOUT A TEST: %s has no tests/hooks/%s\033[0m\n' "$$b" "$$t"; \
	    printf 'A guard ships with its companion. Without one, nothing can tell whether it still\n'; \
	    printf 'fires - or whether it fires on correct work, which is the more expensive failure.\n\n'; \
	    fail="$$fail $$b"; continue; \
	  fi; \
	  case "$$traced" in *" $$b "*) skipped=$$((skipped+1)); continue ;; esac; \
	  sha=$$(printf '%s\n' "$$keys" | awk -v b="$$b" '$$1 == b { print $$2 }'); mkdir -p "$$gitdir/hooks-test"; \
	  [ -n "$$sha" ] || sha=unkeyed-$$RANDOM; \
	  if [ -z "$(HOOKS_ALL)" ] && [ "$$(cat "$$gitdir/hooks-test/$$b" 2>/dev/null)" = "$$sha" ]; then skipped=$$((skipped+1)); continue; fi; \
	  n=$$((n+1)); printf '%s %s %s\n' "$$b" "$$t" "$$sha" >> "$$work/todo"; \
	done; \
	if [ -s "$$work/todo" ]; then \
	  mkdir -p "$$gitdir/hooks-test"; \
	  ns=$$(wc -l < "$$work/todo"); [ "$$ns" -gt $(HOOKS_JOBS) ] && ns=$(HOOKS_JOBS); pm=$$(( $(CPU_COUNT) / (ns > 0 ? ns : 1) )); \
	  [ "$$pm" -gt 8 ] && pm=8; [ "$$pm" -lt 1 ] && pm=1; export PARTS_MAX=$$pm; \
	  xargs -P $(HOOKS_JOBS) -L1 -a "$$work/todo" "$$root/tests/hooks/hookrun.sh" "$$work" "$$gitdir" || true; \
	  for rc in "$$work"/*.rc; do \
	    [ -f "$$rc" ] || continue; \
	    b=$$(basename "$$rc" .rc); \
	    if [ "$$(cat "$$rc")" != ok ]; then \
	      printf '\n\033[1mHOOK TESTS FAILED: %s\033[0m\n' "$$b"; sed 's/^/  /' "$$work/$$b.log"; fail="$$fail $$b"; \
	    fi; \
	  done; \
	fi; \
	uh="$$HOME/.claude/hooks/test-missing-program-hook.sh"; \
	uk=$$(cat "$$uh" "$$HOME/.claude/hooks/missing-program-hook.sh" 2>/dev/null | sha256sum | cut -c1-16); \
	if [ -f "$$uh" ] && [ -z "$(HOOKS_ALL)" ] && [ "$$(cat "$$gitdir/hooks-test/missing-program-hook" 2>/dev/null)" = "$$uk" ]; then skipped=$$((skipped+1)); \
	elif [ -f "$$uh" ]; then \
	  if bash "$$uh" > "$$work/missing-program-hook.log" 2>&1; then n=$$((n+1)); printf '%s' "$$uk" > "$$gitdir/hooks-test/missing-program-hook"; \
	  else printf '\n\033[1mHOOK TESTS FAILED: missing-program-hook (user-level, %s)\033[0m\n' "$$uh"; sed 's/^/  /' "$$work/missing-program-hook.log"; fail="$$fail missing-program-hook"; fi; \
	fi; \
	if [ -z "$(FROM_DONE)" ]; then \
	  pyt=$$(grep -rlE '/ *"scripts[/"]|"scripts" */|join\([^)]*"scripts"' tests --include='test_*.py' --exclude-dir=hooks | sort | tr '\n' ' '); \
	  stale=$$(if [ -n "$(HOOKS_ALL)" ]; then echo $$pyt; else python3 "$$root/tests/hooks/hookdeps.py" --pystale "$$gitdir" $$pyt; fi | tr '\n' ' '); \
	  if [ -n "$(HOOKS_PYTEST_SKIP)" ]; then stale=$$(for f in $$stale; do case $$f in $(HOOKS_PYTEST_SKIP)*) ;; *) printf '%s ' "$$f" ;; esac; done); fi; \
	  if [ -n "$$(echo $$stale)" ]; then \
	    if L7R_TEST_DEPS=$${L7R_TEST_DEPS:-record} python3 -m pytest -p tests.tooling._test_deps -n 4 --dist worksteal -q --no-cov $$stale > "$$work/pytest-scripts.log" 2>&1; then \
	      python3 "$$root/tests/hooks/hookdeps.py" --pystamp "$$gitdir" $$stale; n=$$((n+1)); \
	    else printf '\n\033[1mHOOK TESTS FAILED: the pytest files that test scripts/\033[0m\n'; tail -40 "$$work/pytest-scripts.log" | sed 's/^/  /'; fail="$$fail pytest-scripts"; fi; \
	  else skipped=$$((skipped+1)); fi; \
	fi; \
	if ! python3 "$$root/scripts/gates/check-tool-signals.py"; then fail="$$fail check-tool-signals"; fi; \
	if [ -n "$$fail" ]; then printf '\n\033[1mhooks-test FAILED:%s\033[0m\n\n' "$$fail"; exit 1; fi; \
	python3 "$$root/scripts/gates/gate-stamp.py" --write hooks; \
	printf 'hooks-test: %s guard suites green, %s unchanged since they last went green (hooks area stamped)\n' "$$n" "$$skipped"; \
	ran=$$(for s in "$$work"/*.s; do [ -f "$$s" ] && printf '%s %s\n' "$$(cat "$$s")" "$$(basename "$$s" .s)"; done | sort -rn | awk '{printf "%s%s %ss", (NR>1?", ":""), $$2, $$1}'); \
	[ -z "$$ran" ] || printf 'hooks-test: ran %s\n' "$$ran"

perf-gate:      ## [performance] require the feature's -start bookend, take -end, and print the comparison - its timings for information, its call counts judged as the push judges them (feature 427)
	@f="$(or $(FEATURE),$(SPECIFY_FEATURE))"; \
	if [ -z "$$f" ] && [ -f .specify/feature.json ]; then \
	  f=$$(python3 -c "import json;print(json.load(open('.specify/feature.json'))['feature_directory'].split('/')[-1])" 2>/dev/null); \
	fi; \
	n=$$(printf '%s' "$$f" | grep -oE '^[0-9]+' || true); \
	if [ -z "$$n" ]; then \
	  printf '\n\033[1mPERF GATE: cannot tell which feature this is.\033[0m\n'; \
	  printf 'Set SPECIFY_FEATURE=NNN-slug (spec-kit work) or FEATURE=NNN, so the bookends can be paired.\n\n'; \
	  exit 1; \
	fi; \
	if [ -n "$$CODEBUILD_BUILD_ID" ] && ! $(PERF_REVIEW) has-start --feature "$$n" >/dev/null 2>&1; then \
	  printf '\n\033[1mPERF GATE (in-build): taking the %s-start bookend on the pre-merge main, in a detached worktree.\033[0m\n' "$$n"; \
	  git worktree add -q --detach /tmp/base"$$n" origin/main && ( cd /tmp/base"$$n" && $(MAKE) --no-print-directory perf LABEL="$$n-start" ) && cp /tmp/base"$$n"/dev/perf-log/*"$$n-start"*.json dev/perf-log/ || exit 1; \
	fi; \
	if ! ls dev/perf-log/*"$$n"-start*.json >/dev/null 2>&1; then \
	  printf '\n\033[1mPERF GATE: no %s-start bookend exists, so a regression cannot be measured.\033[0m\n\n' "$$n"; \
	  printf 'Constitution VI wants it taken on UNMODIFIED code, before the first edit. Retroactively is\n'; \
	  printf 'fine and is what the regression baseline already does - take it in a detached worktree at\n'; \
	  printf 'the pre-feature commit:\n\n'; \
	  printf '  git worktree add --detach /tmp/base%s <pre-feature-commit>\n' "$$n"; \
	  printf '  ( cd /tmp/base%s && make perf LABEL=%s-start )\n' "$$n" "$$n"; \
	  printf '  cp /tmp/base%s/dev/perf-log/*%s-start*.json dev/perf-log/\n\n' "$$n" "$$n"; \
	  printf 'What is NOT allowed is shipping with no baseline: "did this get slower" then has no answer,\n'; \
	  printf 'and feature 126 shipped a +51%% slowdown exactly that way.\n\n'; \
	  exit 1; \
	fi; \
	$(MAKE) --no-print-directory perf LABEL="$$n-end" >/dev/null; \
	$(MAKE) --no-print-directory perf-report AGAINST="$$n-start"

guard-edit: export GUARD_WHY = $(WHY)
guard-edit:     ## [project] permit edits to one guard file for an hour, the reason recorded in the guard log - the root Makefile takes no marker comment (feature 170 amendment 1)   FILE=Makefile WHY="<why the edit is legitimate>"
	@python3 "$$(git rev-parse --show-toplevel)/scripts/hooks/lib/hm_guard_permit.py" grant "$(abspath $(FILE))" "$$GUARD_WHY"

guard-log:      ## [project] the guard firings, listed - GUARD=<name> SINCE=YYYY-MM-DD EVENT=blocked|rewrote|escaped|reminded FULL=1
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/guard-log.py" $(if $(GUARD),--guard $(GUARD)) $(if $(SINCE),--since $(SINCE)) $(if $(EVENT),--event $(EVENT)) $(if $(FULL),--full)

audit:          ## [project] how the gate has actually been used - every run, every bypass, and remote spend
	@python3 -m l7r.diagram.ci remote-spend
	@python3 -c "import json,glob,collections,os; \
rows=sorted((json.load(open(f)) for f in glob.glob('dev/run-log/**/*.json',recursive=True)),key=lambda r:r.get('utc','')); \
print(chr(10)+'\033[1mGate runs\033[0m (dev/run-log/)'); \
[print(f\"  {r['utc']}  {r['scope']:<9} {r['seconds']:>4}s  {r['result']:<22} {r['commit']}  {(r.get('mode','')+' '+r.get('selected','')).strip()}\") for r in rows[-25:]] or print('  (none yet)'); \
c=collections.Counter(r['scope'] for r in rows); \
print(f\"  {len(rows)} runs: \"+', '.join(f'{k}={v}' for k,v in sorted(c.items()))) if rows else None; \
b=sorted((json.load(open(f)) for f in glob.glob('dev/bypass-log/**/*.json',recursive=True)),key=lambda r:r.get('utc','')); \
print(chr(10)+'\033[1mBypasses\033[0m (dev/bypass-log/) - a FULL run is only justified at the END of a feature'); \
[print(f\"  {r['utc']}  {(r.get('outcome') or r.get('guard') or '?'):<10} {(r.get('why') or r.get('reason') or r.get('what') or '')[:76]}\") for r in b[-15:]] or print('  (none yet)'); \
print()"
	@python3 -c "import json,glob,os,collections; \
rows=[json.load(open(f)) for f in glob.glob(os.path.expanduser(os.environ.get('GUARD_LOG_DIR','~/.claude/guard-log')+'/*.json')) if os.path.getsize(f)]; \
print('\033[1mGuard firings\033[0m (~/.claude/guard-log/) - what each guard did: blocked, rewrote, reminded, escaped'); \
by=collections.defaultdict(collections.Counter); \
[by[r['guard']].update([r['event']]) for r in rows]; \
rules=collections.defaultdict(collections.Counter); \
[rules[r['guard']].update([r.get('rule') or r['event']]) for r in rows]; \
[ (print(f\"  {g:<12} \"+', '.join(f'{k}={v}' for k,v in sorted(c.items()))+(f\"   escape rate {c['escaped']/max(1,c['escaped']+c['blocked']):.0%}\" if c['blocked'] or c['escaped'] else '')), \
   (print('               by rule: '+', '.join(f'{k}={v}' for k,v in rules[g].most_common(4))) if len(rules[g])>1 and set(rules[g])-set(c) else None)) for g,c in sorted(by.items())] or print('  (none recorded yet)'); \
esc=[r for r in rows if r['event']=='escaped']; \
[print('\033[1m  escapes taken, with what the session said\033[0m')] and [print(f\"    {r['utc'][5:16]}  {r['guard']:<12} {(r['detail'] or '(no reason recorded)')[:88]}\") for r in sorted(esc,key=lambda r:r['utc'],reverse=True)[:8]] if esc else None; \
print(f\"  {len(rows)} entries\"+(f\", {min(r['utc'] for r in rows)} to {max(r['utc'] for r in rows)}\" if rows else '')); \
print()"
	@printf '\033[1mFiles past the ~1,000-line bar\033[0m (constitution X clause 13 - GATED since feature 173)\n'
	@python3 scripts/gates/check-file-scale.py --list .
	@printf '  A file over the bar FAILS `make lint`, and so `make done` and the push. The one way out\n'
	@printf '  is clause 13'"'"'s ordered-data carve-out, stated IN the file as `FILE_SIZE_OK: <reason>` and\n'
	@printf '  listed above with its reason - a carve-out nobody can enumerate is one nobody revisits.\n'
	@printf '  If the bulk is a roster restating code elsewhere, clause 14 says DERIVE it, do not split.\n\n'
	@printf '\033[1mFiles allowed to carry a conflict triple\033[0m (feature 241 - the file-level exemption)\n'
	@python3 scripts/hooks/lib/hm_conflict.py --list .
	@printf '  Declaring it makes the WHOLE file invisible to the hook and to the backstop, so a real\n'
	@printf '  conflict committed into one of these is caught by nothing - which is why the reason must be\n'
	@printf '  argued, must open its line, and is listed here with the file that claims it.\n\n'
	@printf '\033[1mClass entries with no research section\033[0m (feature 234 - the declared-silence form)\n'
	@python3 -c "import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts'); from l7r.diagram.interactive.classes import CLASSES; import importlib.util as u; sp=u.spec_from_file_location('ceh','scripts/gates/check-entry-headings.py'); m=u.module_from_spec(sp); sp.loader.exec_module(m); rows=[(k,fc.entry) for k,fc in sorted(CLASSES.items()) if m.SILENT.search(fc.entry)]; [print(f'  {k:<22} {e}') for k,e in rows]; print(f'  {len(rows)} of {len(CLASSES)} entries name no section; the other {len(CLASSES)-len(rows)} must RESOLVE, checked at the gate and the push.')"
	@printf '  A broken heading and a deliberate silence are told apart by this FORM, never by a non-match.\n\n'
	@python3 -c "import json,os,pathlib,subprocess; \
root=pathlib.Path(subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip()); \
mirror=root.parent.parent if root.parent.name=='.clones' else root; \
p=mirror/'.specify'/'feature-numbers.jsonl'; \
rows=[json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.is_file() else []; \
print('\033[1mFeature numbers claimed\033[0m ('+str(p)+' - make claim, feature 197)'); \
[print(f\"  {r.get('utc','?'):<20} {r.get('number',0):>4}  {r.get('slug','?'):<40} {r.get('clone','?')}\") for r in rows[-10:]] or print('  (none yet - every claim made by make claim lands here)'); \
print(f'  {len(rows)} claims recorded') if rows else None; print()"
	@python3 -c "from tests import rolls; print('\033[1mHamlets the gate may roll\033[0m (tests/rolls.py, feature 213 - one roll each per gate, enforced by the roll census)'); [print(f'  {r.spec.name:<16} seed={r.spec.seed:<3} {r.carries[:96]}') for r in rolls.ROLLS]; print(f'  {len(rolls.ROLLS)} rostered rolls; {len(rolls.DUPLICATES)} stated duplicate(s); {len(rolls.POOL_GENS)} pool gen(s), rolled only when their key moved; {len(rolls.IN_PROCESS)} in-process exception(s)'); print('  make roll-audit: the engine lines each roll alone reaches (feature 216)'); print()"

docs:           ## [project] regenerate docs/make-targets.html from this Makefile's own `##` lines
	@python3 scripts/make-docs.py . --write

help:           ## [project] list every target with its one-line purpose
	@printf '\n\033[1mOperations\033[0m - everything runs through one of these.\n\n'
	@grep -hE '^[a-z][a-z0-9-]*:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort | awk -F'\t' '{printf "  \033[1m%-18s\033[0m %s\n", $$1, $$2}'
	@cost=$$(scripts/measure/gatecost.py done 2>/dev/null); \
	 printf '\nCheapest first: quick | reference | done (NOT the quick one) | done FULL=1'; \
	 [ -n "$$cost" ] && printf '   -   `make done` median %s s over its recent recorded runs (`make audit`)' "$$cost"; \
	 printf '\n'
	@printf 'Remote (paid, CodeBuild): ci-status (free) | ci-check [FULL=1|TARGET=op] | ci-merge (the push) | ci-image - see dev/loop.md\n\n'

# ---- CodeBuild: every remote run is paid ----
ci-status:      ## [remote] free: delta, route, verification state, verified lookup, remote spend   ROUTE=1 -> just DIRECT|GATED
##  ROUTE=1  print just DIRECT|GATED instead of the whole condition table
	$(RUN).ci status $(if $(ROUTE),--route,)
engine-key:      ## [project] the content hash the gate and the push key on   REF=<commit>
##  REF=<commit>  which commit to key (default: HEAD)
	@$(RUN).ci engine-key $(or $(REF),HEAD)

ci-check:       ## [remote] run the SOAK suite on CodeBuild (PAID)      FULL=1 (prompts) | TARGET=cohort etc. | NO_GO=1 (FR-036 self-abort proof)
##  FULL=1                full scope instead of reference; PROMPTS, and cancels by default
##  TARGET=<make target>  which target the build runs - e.g. `cohort` (default: the soak suite)
##  NO_GO=1               prove the self-abort path: start the build and never send the go signal
	$(REMOTE_OK)
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
	$(RUN).ci check $(if $(FULL),--full,) $(if $(TARGET),--target "$(TARGET)",) $(if $(NO_GO),--no-go,) $(if $(COMPUTE),--compute "$(COMPUTE)",)

ci-merge:       ## [remote] the push's gated route (PAID) - runs the SOAK suite; no longer a merge queue. Called by sync-with-main.sh   FULL=1 (prompts)
##  FULL=1  full scope; PROMPTS, and cancels by default
	@$(if $(FULL),$(MAKE) --no-print-directory bypass-audit REF_WHY="$(REF_WHY)" && $(MAKE) --no-print-directory commit-permitted,true)
	$(RUN).ci merge $(if $(FULL),--full,)

commit-permitted: ## [project] commit the most recent bypass-log entry, which is how a paid FULL run is authorized
	@f=$$(find dev/bypass-log -name '*.json' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-); why=$$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['why'][:60])" "$$f"); \
	git add dev/bypass-log && git commit -q -m "chore: authorize FULL sweep - $$why" && echo "committed $$f ($$why)"

ci-measure:     ## [remote] MEASURE what the remote gate costs (PAID, prompts)   FULL=1 | COMPUTE=BUILD_GENERAL1_LARGE
##  FULL=1                    measure the full-scope pair as well as reference
##  COMPUTE=<codebuild type>  which instance size to measure on - e.g. `BUILD_GENERAL1_LARGE`
	$(REMOTE_OK)
	@if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: ci-measure is a paid operation and its prompt needs a terminal.\033[0m Run it in the foreground.\n\n'; $(LOGBYPASS) refused "ci-measure with no terminal"; exit 1; fi; \
	printf '\n\033[1mAbout to MEASURE the remote gate on AWS\033[0m (a build, billed by the minute). This buys a\n'; \
	printf 'number and nothing else - no verified record, no push. Press Enter to CANCEL.\n\nReason to continue (Enter cancels): '; \
	read why || true; \
	if [ -z "$$why" ]; then $(LOGBYPASS) cancelled "(ci-measure backed out at the prompt)"; printf 'Cancelled.\n'; exit 1; fi; \
	$(LOGBYPASS) permitted "$$why"; git add dev/bypass-log; git commit -q -m "chore: authorize a remote measurement - $$why" || true
	$(RUN).ci measure $(if $(FULL),--full,) $(if $(COMPUTE),--compute "$(COMPUTE)",)

ci-image:       ## [remote] rebuild the CodeBuild image from Dockerfile.ci and push it to ECR (PAID, ~$$1; prompts)
	$(REMOTE_OK)
	@if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: ci-image is a paid operation and its prompt needs a terminal.\033[0m Run it in the foreground.\n\n'; $(LOGBYPASS) refused "ci-image with no terminal"; exit 1; fi; \
	printf '\n\033[1mAbout to rebuild the CodeBuild image on AWS\033[0m (~$$1, a few minutes). Needed only when\n'; \
	printf 'setup-dev-env.sh, Dockerfile.ci or a lockfile changed. Press Enter to CANCEL.\n\nReason to continue (Enter cancels): '; \
	if [ ! -t 0 ]; then printf '\n\033[1mREFUSED: this prompt has no terminal to answer it\033[0m - a backgrounded or piped run cannot be asked; run it in the foreground, or use the target that does not prompt.\n\n'; exit 1; fi; read why || true; \
	if [ -z "$$why" ]; then $(LOGBYPASS) cancelled "(ci-image backed out at the prompt)"; printf 'Cancelled.\n'; exit 1; fi; \
	$(LOGBYPASS) permitted "$$why"; git add dev/bypass-log; git commit -q -m "chore: authorize image rebuild - $$why" || true
	$(RUN).ci image

LOGRUN = python3 -c "import json,os,subprocess,sys,time; \
  h=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip(); \
  ts=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'%06d'%(time.time_ns()//1000%1000000); \
  d='dev/run-log/'+time.strftime('%Y-%m',time.gmtime()); os.makedirs(d,exist_ok=True); \
  open(f'{d}/{ts}-{os.getpid()}.json','w').write(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'target':sys.argv[1],'scope':sys.argv[2],'seconds':int(sys.argv[3]),'result':sys.argv[4],'commit':h,**({'cache':sys.argv[5]} if len(sys.argv)>5 and sys.argv[5] in ('warm','cold') else {}),**({'mode':os.environ['RUN_MODE'],'selected':os.environ.get('RUN_SELECTED','')} if os.environ.get('RUN_MODE') else {}),**json.loads(os.environ.get('RUN_STATS') or '{}')},indent=2)+chr(10)); \
  g=subprocess.run(['git','rev-parse','--absolute-git-dir'],capture_output=True,text=True).stdout.strip(); \
  g and open(os.path.join(g,'last-run-record'),'w').write(os.path.abspath(f'{d}/{ts}-{os.getpid()}.json'))"

RUNSTATS = python3 "$$(git rev-parse --show-toplevel)/scripts/measure/runstats.py"
COMMIT_RUN_RECORD = bash "$$(git rev-parse --show-toplevel)/scripts/gates/commit-run-record.sh"

LOGBYPASS = python3 -c "import json,os,subprocess,sys,time; \
  h=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip(); \
  ts=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'%06d'%(time.time_ns()//1000%1000000); \
  d='dev/bypass-log/'+time.strftime('%Y-%m',time.gmtime()); os.makedirs(d,exist_ok=True); \
  open(f'{d}/{ts}-{os.getpid()}.json','w').write(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'target':'$(MAKECMDGOALS)$(if $(FULL), FULL,)','commit':h,'outcome':sys.argv[1],'why':sys.argv[2]},indent=2)+chr(10))"

LOGESCAPE = @root=$$(git rev-parse --show-toplevel) && bash -c '. "$$0/scripts/hooks/lib/guardlog.sh"; \
  printf "%s" "$$2" | python3 "$$0/scripts/hooks/lib/hookmatch.py" reason-ok >/dev/null || { \
    printf "BLOCKED: %s needs a REASON (two words, eight characters) - it is what a later audit reads.\n" "$$1" >&2; \
    guard_log make blocked "$$2" "$$1-no-reason"; exit 2; }; \
  guard_log make escaped "$$2" "$$(printf "%s" "$$1" | tr "[:upper:]_" "[:lower:]-")"' "$$root"

HOOKS_JOBS ?= $(if $(CODEBUILD_BUILD_ID),$(CPU_COUNT),$(shell [ "$(CPU_COUNT)" -lt 8 ] && echo "$(CPU_COUNT)" || echo 8))

QUICK_BUDGET = 60

tooling:        ## [tests] run every `tooling` test (make/ci/pipeline, exhaustive) and record them green so `make quick` skips them until the tooling changes
	@$(GATE_EXHAUSTIVE_ENV) L7R_TEST_DEPS=$${L7R_TEST_DEPS:-$(if $(FULL),record,reuse)} python3 -m pytest -p tests.tooling._test_deps -n $(XDIST_WORKERS) -q --no-cov -m tooling && python3 -m l7r.diagram.ci tooling-green

page-check:     ## [tests] the interactive tests + the browser test, then the `page` stamp - what an asset edit owes at push
	@python3 -m pytest -n $(XDIST_WORKERS) --dist loadgroup -q --no-cov tests/interactive tests/full/interactive/page_browser \
	  && root=$$(git rev-parse --show-toplevel) && python3 "$$root/scripts/gates/gate-stamp.py" --write page \
	  && python3 "$$root/scripts/gates/gate-stamp.py" --write browser \
	  && printf '\n\033[1mpage-check green\033[0m (the page and browser stamps are written; an asset-only delta may push)\n' \
	  && { root=$$(git rev-parse --show-toplevel); python3 "$$root/scripts/record/entry_owed.py" --root "$$root" --why; python3 "$$root/scripts/record/entry_owed.py" --root "$$root" | sed 's/^/  /'; true; }

fix-yield:      ## [project] did each tooling fix save what it was meant to: its measure's rate before its ruling and since it was made (feature 385 T119)   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make fix-yield: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/fix_yield.py" "$(F)" --root "$$(git rev-parse --show-toplevel)"

tool-yield:     ## [project] every tool measured: how often it runs, how often it changed something, its misfires and what the record cannot see yet (feature 406)   [KIND=guard|target|check|step|review]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/tool_yield.py" --root "$$(git rev-parse --show-toplevel)" $(if $(KIND),--kind $(KIND))

where-time:     ## [project] where a feature's time went, by task: the time by bucket and the agents by kind (feature 385 T77); BY=tick books each tick-to-tick window (T115)   F=<feature> [SINCE=<ISO UTC>] [BY=tick]
	@if [ -z "$(F)" ]; then printf 'make where-time: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/where_time.py" "$(F)" $(if $(SINCE),--since "$(SINCE)",) $(if $(filter tick,$(BY)),--by-tick,)

set-down: export SET_DOWN_WHY = $(WHY)
set-down:       ## [project] set a feature's work down, so a turn may end with tasks open (feature 385 T70); refused while an open task's part B has no arbiter ruling since (405), or while the 7-day usage is under the weekly soft cap (a goal's, where one is still armed) unless the arbiter ruled a set-down ask (GM 2026-10-23, 10-24): F=385 WHY="awaiting the GM on the cohort trend" [SET_DOWN_OK="<reason>"]
	@if [ -z "$(F)" ]; then printf 'make set-down: F=<feature> is required\n' >&2; exit 2; fi
	$(if $(SET_DOWN_OK),$(LOGESCAPE) SET_DOWN_OK "$(SET_DOWN_OK)",@:)
	@SET_DOWN_OK="$(SET_DOWN_OK)" python3 "$$(git rev-parse --show-toplevel)/scripts/set-down.py" "$(F)"

found-list:     ## [project] a feature's open findings (found.jsonl), numbered - what is not yet filed as a task or settled (405 T29)   F=405
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/found.py" list --feature "$$(ls -d specs/$(F)-* | head -1)"
found-close:    ## [project] close found.jsonl rows: FILED as a task, or SETTLED with a reason (405 T29)   F=405 ROWS=3,7 TASK=T61 | WHY="..."
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/found.py" close --feature "$$(ls -d specs/$(F)-* | head -1)" --rows "$(ROWS)" $(if $(TASK),--task "$(TASK)",) $(if $(WHY),--why "$(WHY)",)

task-add: export TASK_TITLE = $(TITLE)
task-add:       ## [project] file a task box (and its plan section) with the next free id: F=385 TITLE="..." [SECTION=<file with {T} for the id>] [RESEARCH=physical]
	@if [ -z "$(F)" ]; then printf 'make task-add: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/task-add.py" "$(F)" $(if $(SECTION),--section "$(abspath $(SECTION))",) $(if $(filter physical,$(RESEARCH)),--physical,)

tick: export TICK_NOTE = $(NOTE)
tick: export PLAN_REVIEW_OK := $(PLAN_REVIEW_OK)
tick:           ## [project] tick a task: F=188 T=T03 NOTE="what was verified" [BOXES=1 ticks the research boxes]
##  F=<feature>  the feature number or slug - e.g. `188`
##  T=<task>     the task id - e.g. `T03`
##  NOTE=<text>  what was VERIFIED, which is what the tick is asserting
##  BOXES=1      also tick the three physical-research boxes (only legitimate on a `research: physical` task)
##  PLAN_REVIEW_OK=<reason>  tick although the plan has no current CLEAR review (feature 243) - recorded
	@python3 "$$(git rev-parse --show-toplevel)/scripts/tick-task.py" "$(F)" "$(T)" --note-from-env $(if $(BOXES),--boxes,)

plan-verdict:   ## [project] {internal} record a plan review - the spec-fidelity SUBAGENT runs this; ARBITER=<trigger> applies the round arbiter's accept past the plan-round cap   F=243 FILE=<json> AS=spec-fidelity | F=<n> ARBITER=<trigger>
##  F=<feature>        the feature number or slug whose plan.md was reviewed
##  FILE=<json>        the reviewer's JSON: plan_sha256, decisions, verdict (feature 243 plan P3)
##  AS=spec-fidelity   who is recording - only the subagent may pass this, and nothing else distinguishes the shells
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" $(if $(ARBITER),arbiter-accept "$(F)" "$(ARBITER)",$(if $(BLOCKS),record-blocks "$(F)",$(if $(TASK),record-task "$(F)" "$(TASK)",record "$(F)")) "$(abspath $(FILE))" --as "$(or $(AS),main)")

plan-delta:     ## [project] the review a plan owes since amendment 11: only its blocks changed since their CLEAR verdict, on a lean bundle (feature 375 FR-043)   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make plan-delta: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" delta "$(F)"

plan-archive:   ## [project] move a plan's finished sections (every task ticked, CLEAR) into plan-done.md, which no review reads (feature 375 FR-044)   F=<feature>
	@if [ -z "$(F)" ]; then printf 'make plan-archive: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" archive "$(F)"

check-closed:   ## [project] close the checks in flight on a page or pop-up whose agent went silent (the freeze names it)   SUBJECT=q:0105|modal:sheet/bath REASON="<why>" [AGENT=<id> a check you stopped yourself, closed though not silent]
	@if [ -z "$(SUBJECT)" ] || [ -z "$(REASON)" ]; then printf 'make check-closed: SUBJECT=<q:NNNN or modal:<registry>/<slug>> and REASON="<why>" are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/hooks/lib/hm_checks.py close "$(SUBJECT)" "$(REASON)" $(if $(AGENT),"$(AGENT)",)

arbiter-bundle: ## [project] what the round arbiter reads to rule on a tripwire or a round cap: the rounds marked new/repeated/reversing, the edits, the cascade, the oscillation (feature 375)   TRIGGER=<id the guard named> [OUT=<dir>]
	@if [ -z "$(TRIGGER)" ] && [ -z "$(BATCH)" ]; then printf 'make arbiter-bundle: TRIGGER=<the trigger the refusal named>, or BATCH=1 for every owed round trigger at once\n' >&2; exit 2; fi
	$(if $(MISSING_OK),$(LOGESCAPE) MISSING_OK "$(MISSING_OK)",@:)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/arbiter_bundle.py" $(if $(BATCH),--batch $(if $(TRIGGERS),--triggers "$(TRIGGERS)",),"$(TRIGGER)") --root "$$(git rev-parse --show-toplevel)" $(if $(OUT),--out "$(OUT)",) $(if $(MISSING_OK),--missing-ok "$(MISSING_OK)",)

arbiter-ruled:  ## [project] {internal} record the round arbiter's ruling - the round-arbiter SUBAGENT runs this   TRIGGER=<id> FILE=<json> AS=round-arbiter  (or BATCH=1 FILE=<json> for a batch)
	@if [ -z "$(FILE)" ] || { [ -z "$(TRIGGER)" ] && [ -z "$(BATCH)" ]; }; then printf 'make arbiter-ruled: FILE= and TRIGGER= (or BATCH=1) are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/hooks/lib/hm_arbiter.py $(if $(BATCH),ruled-batch,ruled "$(TRIGGER)") "$(abspath $(FILE))" --as "$(or $(AS),main)"

arbiter-nit:  ## [project] answer an accepted unit again after the wording fix its ruling asked for   TRIGGER=<id> OLD="<words>" NEW="<words>"
	@if [ -z "$(TRIGGER)" ] || [ -z "$(OLD)" ] || [ -z "$(NEW)" ]; then printf 'make arbiter-nit: TRIGGER=, OLD= and NEW= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/hooks/lib/hm_arbiter.py nit "$(TRIGGER)" "$(OLD)" "$(NEW)"

arbiter-fix-done:  ## [project] the round arbiter's tooling fix is MADE: what was built and its test (feature 379); LAND= lands its files first, TICK= ticks the task after   ID="<trigger> [<trigger> ...]" NOTE="<what was built>" TEST=tests/... [LAND="<the fix's files>"] [F=<feature> TICK=<Txx>]
	@if [ -z "$(ID)" ] || [ -z "$(NOTE)" ] || [ -z "$(TEST)" ]; then printf 'make arbiter-fix-done: ID=, NOTE= and TEST= are required\n' >&2; exit 2; fi
	@if [ -n "$(TICK)" ] && [ -z "$(F)" ]; then printf 'make arbiter-fix-done: TICK= ticks a task of F=<feature> - name the feature\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && $(if $(LAND),scripts/land-tooling.sh $(LAND) $(TEST) && git fetch -q origin &&,) ARBITER_FIX_ENGINE="$(ENGINE)" python3 scripts/hooks/lib/hm_arbiter.py fix done "$(ID)" "$(NOTE)" "$(TEST)"$(if $(TICK), && $(MAKE) --no-print-directory tick F="$(F)" T="$(TICK)" NOTE="$(NOTE)",)

use-feature:  ## [project] make F the clone's active feature for the hooks (.specify/feature.json) - instead of writing the file by hand (the round arbiter on hour:396@1)   F=<feature number>
	@if [ -z "$(F)" ]; then printf 'make use-feature: F=<feature number> is required - e.g. make use-feature F=396\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && d=$$(ls -d specs/$(F)-* 2>/dev/null | head -1) && [ -n "$$d" ] || { printf 'make use-feature: no specs/$(F)-* directory\n' >&2; exit 2; }; printf '{\n  "feature_directory": "%s"\n}\n' "$$d" > .specify/feature.json && printf 'use-feature: .specify/feature.json names %s; export SPECIFY_FEATURE=%s\n' "$$d" "$${d#specs/}"

step-back:  ## [project] the feature's hourly checkpoint: open it and build the round arbiter's step-back bundle (feature 383)   [TRIGGER=hour:<f>@<n> TRANSCRIPT=<jsonl> SINCE=<ISO> UNTIL=<ISO>: replay an hour]
	@cd "$$(git rev-parse --show-toplevel)" && if [ -n "$(TRIGGER)" ]; then python3 scripts/reviews/stepback_bundle.py "$(TRIGGER)" --root "$$(pwd)" $(if $(TRANSCRIPT),--transcript "$(TRANSCRIPT)",) $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(OUT),--out "$(OUT)",); else t=$$(python3 scripts/reviews/checkpoint.py open) && python3 scripts/reviews/stepback_bundle.py "$$t" --root "$$(pwd)"; fi

arbiter-ask: export ARBITER_WHY = $(WHY)
arbiter-ask: export ARBITER_REVIEW = $(REVIEW)
arbiter-ask:  ## [project] put a PROCESS question (a cap, a waiver, a stuck choice of route) to the round arbiter before the GM (feature 379)   SUBJECT=<short id> WHY="<the question>" [FILES="<the measurements it cites>"] [REVIEW=spec|plan|claims:<key>;<key>: an accept then stands as that review's verdict, 409; claims' since 2026-10-24]
	@if [ -z "$(SUBJECT)" ] || [ -z "$$ARBITER_WHY" ]; then printf 'make arbiter-ask: SUBJECT= and WHY= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/reviews/arbiter_bundle.py --check-ask "$$ARBITER_WHY" --evidence "$(FILES)" && python3 scripts/hooks/lib/hm_arbiter.py ask "$(SUBJECT)" "$$ARBITER_WHY" "$$ARBITER_REVIEW" && python3 scripts/reviews/arbiter_bundle.py "ask:$(SUBJECT)" --root "$$(pwd)" --evidence "$(FILES)"

land-tooling:  ## [project] land the named TOOLING files on main by themselves, mid-feature (feature 379)   FILES="scripts/x.py tests/tooling/test_x.py"
	@"$$(git rev-parse --show-toplevel)/scripts/land-tooling.sh" $(FILES)

arbiter-fix-declined:  ## [project] the round arbiter's tooling fix OVERHAULS a process: declined, never filed - a question for the GM owed escalation-check (features 379, 432)   ID=<trigger> REASON="<why>"
	@if [ -z "$(ID)" ] || [ -z "$(REASON)" ]; then printf 'make arbiter-fix-declined: ID= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/hooks/lib/hm_arbiter.py fix declined "$(ID)" "$(REASON)"

step-back-off:  ## [project] suspend the hourly step-back, not remove it: the hour comes due for nothing until step-back-on; the tripwire rulings stay (feature 405 T43)   REASON="..."
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/reviews/checkpoint.py switch off --why "$(REASON)" && git add dev/step-back.json && git commit -q -m "chore: the hourly step-back suspended - $(REASON)" -- dev/step-back.json && echo "committed dev/step-back.json"
step-back-on:   ## [project] resume the hourly step-back (feature 405 T43)   REASON="..."
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/reviews/checkpoint.py switch on --why "$(REASON)" && git add dev/step-back.json && git commit -q -m "chore: the hourly step-back resumed - $(REASON)" -- dev/step-back.json && echo "committed dev/step-back.json"
land: export LAND_NOTE = $(NOTE)
land: export LAND_BOXES = $(BOXES)
land: export COVER_OK := $(COVER_OK)
land:           ## [project] land one task or several and tick them: every cheap refusal first and together (the changed modules' coverage among them), then make done and make cohort-landing where needed, the push, the ticks (feature 405 T33)   F=405 T="T12 [T13]" NOTE="what was verified" [BOXES=1 ticks a physical task's research boxes] [COVER_OK="<reason>"]
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make land: F=<feature> and T="<task ids>" are required\n' >&2; exit 2; fi
	$(if $(COVER_OK),$(LOGESCAPE) COVER_OK "$(COVER_OK)",@:)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/land.py" "$(F)" "$(T)"

cover-changed:  ## [tests] the coverage floor on the engine modules the change touched, in seconds: every line of each changed module the floor's tests leave unrun, the floor's carried coverage honored (the GM 2026-10-24; feature 430 T03)   [BASE=origin/main]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/cover_changed.py" --base "$(or $(BASE),origin/main)"

gate-costs:     ## [performance] what a gate run costs here, from the run records: each run's mode, selection and phases, the fit (fixed + per selected test), the selection's growth between full runs (feature 415)   [SINCE=<utc prefix>]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/gate_costs.py" $(if $(SINCE),--since "$(SINCE)",)

land-stop:       ## [project] stop this tree's running `make land` cleanly - its gate and cohort stop with it (405 T90)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/land.py" --stop

land-batch: export LAND_NOTE = $(NOTE)
land-batch:     ## [project] the same command as make land (feature 385 T117's name, kept)   F=385 T="T106 T108" NOTE="what was verified"
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make land-batch: F=<feature> and T="<task ids>" are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/land.py" "$(F)" "$(T)"

task-start:     ## [project] name the task you are starting, so its checks wait for its decisions' verdict (feature 375)   F=375 T=T13
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make task-start: F=<feature> and T=<task id> are required\n' >&2; exit 2; fi
	$(if $(HOLD_OK),$(LOGESCAPE) HOLD_OK "$(HOLD_OK)",@:)
	@HOLD_OK="$(HOLD_OK)" python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" task-start "$(F)" "$(T)"

decide:         ## [project] the spec-fidelity dispatch that rules on one task's plan section before its checks (feature 375)   F=375 T=T13
	@if [ -z "$(F)" ] || [ -z "$(T)" ]; then printf 'make decide: F=<feature> and T=<task id> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" decide "$(F)" "$(T)"

section-sha:    ## [project] {internal} the digest of one task's plan section, which a decision preflight records   F=375 T=T13
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/plan_gate.py" section-sha "$(F)" "$(T)"

hookbench:      ## [project] replay the frozen command window through a guard decision, in process   GUARD=house-style [AGAINST=<ref>] | REFRESH=1
##  GUARD=<name>         a guard whose decision is importable (feature 239 FR-001); others are refused by name
##  AGAINST=<ref>        also print the verdict diff against the guard as it stood at <ref> - what an exemption change owes
##  REFRESH=1            freeze a new dated window of real commands into tests/hooks/fixtures/ instead
	@python3 "$$(git rev-parse --show-toplevel)/tests/hooks/hookbench.py" $(if $(REFRESH),--refresh,$(GUARD) $(if $(AGAINST),--against $(AGAINST),))

figures:        ## [project] re-run every recorded measurement and report what moved   [SPEC=specs/NNN-slug; default every spec with a measurements.json]
##  a moved COUNT fails; a timing outside its band is reported and never fails; the file is restored after
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/figures.py" $(SPEC)

spec-harness:   ## [project] run a feature's measurement harness (its harness.py) as a test node   SPEC=specs/NNN-slug OUT=<json>
##  SPEC=<dir>   the feature directory holding `harness.py`
##  OUT=<json>   where the harness writes its figures (default: the harness's own default)
	@root=$$(git rev-parse --show-toplevel); src="$$root/$(SPEC)/harness.py"; [ -f "$$src" ] || { echo "spec-harness: no harness.py in $(SPEC)" >&2; exit 2; }; \
	cp "$$src" tests/test_zz_spec_harness_tmp.py; \
	HARNESS_OUT="$(OUT)" python3 -m pytest -q -p no:cacheprovider --no-cov -p no:randomly tests/test_zz_spec_harness_tmp.py; ec=$$?; \
	rm -f tests/test_zz_spec_harness_tmp.py; exit $$ec

claim:          ## [project] claim the next spec-kit feature number under the host-wide lock   SLUG=kebab-slug | RENUMBER=specs/NNN-slug [PEEK=1: look, claim nothing]
##  SLUG=<slug>          lower-case kebab; the directory becomes specs/NNN-<slug>/ in THIS clone
##  RENUMBER=<specs/dir> instead of a slug: MOVE that existing directory to the next number (a deduplication, GM 2026-09-07)
##  PEEK=1               print what the claim would be and create or move nothing
	@if [ -z "$(SLUG)$(RENUMBER)" ]; then printf 'make claim: SLUG=<kebab-slug> is required (or RENUMBER=specs/NNN-slug to move an existing directory) - e.g. make claim SLUG=cheaper-widgets\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/claim-feature.py" $(if $(PEEK),--dry-run,) $(if $(RENUMBER),--renumber "$(RENUMBER)",-- "$(SLUG)")

speckit-todo:   ## [project] list the spec-kit features not yet closed - filed, planned, in progress - by the stage each is owed at   [ALL=1: also the closed; BY=affects: by tag; CHECK=1: refuse missing or unknown tags]
##  ALL=1   also list the closed features and the reason each is closed
##  BY=affects  group the open features by their `**Affects**:` tags (.specify/affects.json) instead of by stage
##  AFFECTS=tooling  only the features carrying that tag, same layout (several: AFFECTS="tooling, magistracy")
##  CHECK=1 exit 1, with the line to add, when an open feature's spec has no `**Affects**:` tag or an unknown one
	@python3 "$$(git rev-parse --show-toplevel)/scripts/speckit-todo.py" --root "$$(git rev-parse --show-toplevel)" $(if $(ALL),--all,) $(if $(filter affects,$(BY)),--by-affects,) $(if $(AFFECTS),--affects "$(AFFECTS)",) $(if $(CHECK),--check,)

replay-owing:   ## [project] replay recorded commits through the old owing and the new: modal-depiction units and impl-drift claims owed, per commit and in total (feature 375 SC-001)   REVS="<sha> ..." [OUT=<dir>]
	@if [ -z "$(REVS)" ]; then printf 'make replay-owing: REVS="<commit> ..." is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/replay_owing.py" $(REVS) $(if $(OUT),--out "$(OUT)",) $(if $(TRIAGE),--triage,)

preflight:      ## [tests] the gate's first phase, in seconds: the derived files regenerated, the record and its pointers, make quick - and, here only (not in the gate, 405 T47), the changed engine lines a quick test runs (feature 375)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/preflight.py" --root "$$(git rev-parse --show-toplevel)" --workers "$(XDIST_WORKERS)"

gm-review:      ## [project] what waits on the GM: the questions escalation-check KEPT (his decisions, the one source - feature 432), the questions OWED escalation-check (the session's), rows waiting on other work, and per feature the TO REVIEW rows (he may overturn) - feature 375   [F=<NNN> that feature's rows] [EXPLAIN=1 what needs the GM, or with F= each row in full] [ROW=<n>]
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/gm_review.py $(if $(EXPLAIN),explain $(F) $(ROW),list $(F))

gm-question:    ## [project] put a question to the GM: written OWED escalation-check, it reaches him only once kept (feature 432)   F=<NNN> Q="<the question>" SOURCE="<what raised it>"
	@if [ -z "$(F)" ] || [ -z "$(Q)" ] || [ -z "$(SOURCE)" ]; then printf 'make gm-question: F=, Q= and SOURCE= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/gm_review.py question "$(F)" "$(Q)" "$(SOURCE)"

gm-escalated:   ## [project] record escalation-check's verdict on an owed question: KEEP holds it for the GM (name it in the turn's final message), CUT closes it with the reason (feature 432)   F=<NNN> ROW=<n> VERDICT=KEEP|CUT REASON="<escalation-check's reason>"
	@if [ -z "$(F)" ] || [ -z "$(ROW)" ] || [ -z "$(VERDICT)" ] || [ -z "$(REASON)" ]; then printf 'make gm-escalated: F=, ROW=, VERDICT= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/gm_review.py escalated "$(F)" "$(ROW)" "$(VERDICT)" "$(REASON)"

accept:         ## [project] accept a finding with a reason - the work goes on, and the GM may overturn it after landing (feature 375)   F=375 FINDING="<what>" REASON="<why it can stand>"
	@if [ -z "$(F)" ] || [ -z "$(FINDING)" ] || [ -z "$(REASON)" ]; then printf 'make accept: F=, FINDING= and REASON= are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/gm_review.py accept "$(F)" "$(FINDING)" "$(REASON)"

gm-reviewed: export GM_WORDS = $(WORDS)
gm-reviewed:    ## [project] the GM has reviewed a feature's rows; OVERTURN=<row> TO=<feature> turns one into an open row there (feature 375); ROW=<n> marks that one row alone; WORDS= his words when a session marks a row he discussed   F=375 [OVERTURN=<n> TO=<NNN> | ROW=<n>] [WORDS="<the GM's words>"]
	@if [ -z "$(F)" ]; then printf 'make gm-reviewed: F=<feature> is required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && $(if $(ROW),python3 scripts/gm_review.py reviewed-row "$(F)" "$(ROW)",python3 scripts/gm_review.py reviewed "$(F)" $(if $(OVERTURN),"$(OVERTURN)" "$(TO)",))

feature-report: ## [project] where a feature's time and dispatches went, as a table, from the event log, the run log and git   F=375 [TRANSCRIPT="<jsonl> ..."] [SINCE=<ISO>] [UNTIL=<ISO>] [WRITE=1]
##  F=<NNN>            the feature
##  TRANSCRIPT=<files> session transcripts to convert where the event log has no lines (a feature before 375)
##  SINCE= UNTIL=      ISO UTC bounds on the events read (a transcript holding more than this feature)
##  WRITE=1            also write specs/NNN-*/report.md, which every closing route asks for
	@if [ -z "$(F)" ]; then printf 'make feature-report: F=<feature number> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/feature_report.py" --root "$$(git rev-parse --show-toplevel)" "$(F)" $(foreach t,$(TRANSCRIPT),--transcript "$(t)") $(if $(SINCE),--since "$(SINCE)",) $(if $(UNTIL),--until "$(UNTIL)",) $(if $(WRITE),--write,)

agent-sync:     ## [project] write into each agent file the text every dispatch of that check shares (the modal guidelines), from its source (feature 383 amendment 6)
	@python3 scripts/reviews/agent_sync.py

agent-census:   ## [project] what each subagent check has cost, from the session transcripts   [SINCE=YYYY-MM-DD] [OUT=<json>]
##  SINCE=<date>   only the runs that started on or after it
##  OUT=<json>     also write the rows to this file
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/agent_census.py" $(if $(SINCE),--since "$(SINCE)",) $(if $(OUT),--json "$(abspath $(OUT))",)

quote-verbatim: ## [project] is every quoted passage on the page it cites, character for character - run BEFORE quote-check   Q=0412 | IN=homesteads [NOTES=1-4] [OUT=<json>]
##  Q=<NNNN>       one or more questions, by number (both pages) or a page's file name; its own notes are read beside it
##  IN=<id>        every question of a section (its id in research/contents.json) or carrying a tag
##  NOTES=<n,n-m>  only these notes of each page, by the number its page shows them under
##  OUT=<json>     write the report the quote-check agent is handed (default: the scratch file the run names)
	@if [ -z "$(Q)" ] && [ -z "$(IN)" ]; then printf 'make quote-verbatim: Q=<question number> or IN=<section or tag> is required - e.g. make quote-verbatim Q=0041\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/quote_verbatim.py" --root "$$(git rev-parse --show-toplevel)" $(if $(Q),"$(Q)",--in "$(IN)") $(if $(NOTES),--notes "$(NOTES)",) $(if $(OUT),--json "$(abspath $(OUT))",)

record-prepass: ## [project] the session notes and vocabulary candidates a pattern can find on a question - run BEFORE record-format   Q=0412 | IN=homesteads | Q=SOURCES
##  Q=<NNNN>       one or more questions, by number (both pages) or a page's file name; `SOURCES` for the registry
##  IN=<id>        every question of a section (its id in research/contents.json) or carrying a tag
	@if [ -z "$(Q)" ] && [ -z "$(IN)" ]; then printf 'make record-prepass: Q=<question number> or IN=<section or tag> is required - e.g. make record-prepass Q=0041\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/record_prepass.py" --root "$$(git rev-parse --show-toplevel)" $(if $(Q),"$(Q)",--in "$(IN)")

claims-owed: ## [project] every research claim of the engine or the Mode A procedures owed an impl-drift check (no index row, or its code or cited research moved since), and why
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" owed

claims-bundle: ## [project] the bundle impl-drift reads, copied out of the repository - dispatch it on the MANIFEST printed   MODULE=<file> | OWED=1 | UNITS="<key>,<key>"   [OUT=<dir>] [REASON="<why>" for claims not owed] [WITH="<path>::<qualname>,..." context] [PAGES="<question file>,..."]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" bundle $(if $(OWED),--owed,) $(if $(MODULE),--module "$(MODULE)",) $(if $(UNITS),--units "$(UNITS)",) $(if $(OUT),--out "$(abspath $(OUT))",) $(if $(REASON),--reason "$(REASON)",) $(if $(WITH),--with "$(WITH)",) $(if $(PAGES),--pages "$(PAGES)",)

claims-checked: ## [project] record an impl-drift reply into the claims index, at the fingerprints its bundle read   BUNDLE=<dir> REPLY=<file holding the agent's reply>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make claims-checked: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" record --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

claims-coverage: ## [project] every unit with no research claim, a malformed claim or a pointer to no question - the gate's coverage test, narrowed   [IN=<part of a file path>]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" coverage $(if $(IN),--path "$(IN)",)

claims-report: ## [project] the claims index: counts by verdict, every finding (drifted, needs research, mislabeled, unclaimed, undecided) and every UNRESEARCHED claim
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" report

tunables: ## [project] every claim whose value is ours - GUESS (searched, silent), UNRESEARCHED, CONVENTION - with its figure: a goal and a knob a fixing pass may move (feature 417 T28)   [UNDER=<file or dir>] [ALL=1 keeps claims with no figure] [COUNT=1] [INLINE=1 lists the numbers inside functions no claim states]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/tunables.py" --root "$$(git rev-parse --show-toplevel)" $(if $(UNDER),--path $(UNDER),) $(if $(filter 1,$(ALL)),--all,) $(if $(filter 1,$(COUNT)),--count,) $(if $(filter 1,$(INLINE)),--inline,)

impl-check: ## [project] a research-record feature's changed questions, each with the claims citing it and their verdicts, and what its close still owes (feature 378)   F=<n>
	@if [ -z "$(F)" ]; then printf 'make impl-check: F=<feature number> is required - e.g. make impl-check F=343\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/impl_check.py" "$(F)"

claims-triage: ## [project] the claims owed only a TRIAGE (a page they cite moved, the blocks they rest on stand): one bundle of the new or changed blocks for one agent   [OUT=<dir>]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" triage $(if $(OUT),--out "$(abspath $(OUT))",)

claims-triaged: ## [project] record a triage reply: a claim it names (TOUCHES) is owed impl-drift, every other claim of the bundle is cleared   BUNDLE=<dir> REPLY=<file>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make claims-triaged: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" triaged --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

claims-carry: ## [project] file every carried claims finding (a page edit's, on unchanged code) as an open task of the active feature, so the push lands (feature 385 FR-013)   F=<feature> [T=<open task to file into>] [KEYS="<k>;<k>" RULING=<arbiter trigger>: findings a ruling carried]
	@if [ -z "$(F)" ]; then printf 'make claims-carry: F=<feature> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" carry --feature "$(F)" $(if $(T),--task "$(T)",) $(if $(KEYS),--keys "$(KEYS)",) $(if $(RULING),--ruling "$(RULING)",)

claims-known:  ## [project] record every known drift (a DRIFTED claim naming the open task that fixes it) for the GM, in its task's feature's gm-review.jsonl, so the push lands it - make land runs it (feature 430 T06)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" known

claims-backfill: ## [project] give every index row checked at today's research the pages it was checked at, so a later edit to them is triaged, not re-judged in full
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" backfill

claims-rekey:   ## [project] carry each claim's index row to the file its unit moved to with its code intact - a file split at the 1,000-line bar (405 T58); make land runs it
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" rekey

claims-backfill-sections: ## [project] re-key every procedure-section claim to its own line (feature 375), owing nothing that was not owed: run once, at the change
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/claims.py" --root "$$(git rev-parse --show-toplevel)" backfill-sections

translation-owed: ## [project] the translated quotations new or changed since the merge base - each owes a translation-check   [Q=0412]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/translation_owed.py" --root "$$(git rev-parse --show-toplevel)" $(if $(Q),--q "$(Q)",)

record-owed: ## [project] every record check this delta owes (intro-check, record-format, source-reader, quote-check, source-applicability, translation-check, entry-drift), with the command that answers each   [Q=0412] [UNANSWERED=1] [BETWEEN="<a> <b>"]
##  Q=<NNNN>        only that question's units
##  UNANSWERED=1    only the units with no current answer record (what the push refuses)
##  BETWEEN="a b"   the units revision b owes against revision a (a replay; no entry-drift)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/record_owed.py" --root "$$(git rev-parse --show-toplevel)" $(if $(Q),--q "$(Q)",) $(if $(UNANSWERED),--unanswered,) $(if $(BETWEEN),--between $(BETWEEN),)

record-checked: ## [project] record that a record check returned on the units it read - what answers an owed unit at the push   CHECK=<check> RESULT="<counts>" (BUNDLE=<dir> | Q=<NNNN> NOTES=<k,k> for source-reader | ... REASON="<why>")
##  BUNDLE=<dir>    the bundle the check read: its units, at the content it read
##  Q= NOTES= KEY= KIND=  the units the tree owes on that subject, at today's content - source-reader on named notes, or any check with REASON= (written to dev/bypass-log/)
##  REPLY=<file>    the check's reply: its OUTSIDE THE CHANGE findings are filed as open rows of the feature (feature 375)
##  FIXED_BY="<check>: <its finding>"  CHECK=quote-check Q= NOTES=: a fix made by hand for ANOTHER check's finding, outside the quotation and its claim - the tool verifies both unchanged, else refuses (feature 399); no RESULT needed
	@if [ -z "$(CHECK)" ] || { [ -z "$(RESULT)" ] && [ -z "$(FIXED_BY)" ]; }; then printf 'make record-checked: CHECK=<check> and RESULT="<its counts>" are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/record_owed.py" --root "$$(git rev-parse --show-toplevel)" --answer "$(CHECK)" --result "$(RESULT)" $(if $(FIXED_BY),--fixed-by "$(FIXED_BY)",) $(if $(BUNDLE),--bundle "$(abspath $(BUNDLE))",) $(if $(Q),--q "$(Q)",) $(if $(NOTES),--notes "$(NOTES)",) $(if $(KEY),--key "$(KEY)",) $(if $(KIND),--kind "$(KIND)",) $(if $(REASON),--reason "$(REASON)",) $(if $(REPLY),--reply "$(abspath $(REPLY))",)

style-prepass: ## [project] the style guide's mechanical half for one question - metric figures with no feet, and every lead line to rule on - run BEFORE record-style   Q=0412
##  Q=<NNNN>       the question, by number (both pages) or a page's file name
	@if [ -z "$(Q)" ]; then printf 'make style-prepass: Q=<question number> is required - e.g. make style-prepass Q=0041\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/style_prepass.py" --root "$$(git rev-parse --show-toplevel)" "$(Q)"

question-sizes: ## [project] every research question over the size cap (question + notes, feature 250 D14), largest first - make quick fails on one a change touched
	@python3 "$$(git rev-parse --show-toplevel)/scripts/gates/check-question-size.py" --report

open-questions: ## [project] every guess and every unfound source, read from the record and the tracked files now - the research still owed, with the map features each touches (feature 285)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/open_questions.py" --root "$$(git rev-parse --show-toplevel)"

notes: ## [project] print the named notes of ONE question and only the blocks of its page that carry them - for editing a few notes without reading the whole file (feature 250)   Q=0041 KEYS=kyuhi-jawiki,kyuhi-jawiki-2
	@if [ -z "$(Q)" ] || [ -z "$(KEYS)" ]; then printf 'make notes: Q=<question number or page file> KEYS=<key,key> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/check_bundle.py" --root "$$(git rev-parse --show-toplevel)" "$(Q)" --notes "$(KEYS)" --print-notes

lines: ## [project] print ONLY a coordination file's matching lines - the claims file, a handoff, a checks report - numbered, with how many were shown of how many; never read one whole (feature 274)   FILE=<file> KEY=<regex>
	@if [ -z "$(FILE)" ] || [ -z "$(KEY)" ]; then printf 'make lines: FILE=<file> KEY=<regex> are required - e.g. make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="^- 269"\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/pages/coord.py" lines "$(FILE)" "$$KEY"

append: ## [project] append ONE line to a coordination file without reading or printing it (feature 274)   FILE=<file> LINE="<text>"
	@if [ -z "$(FILE)" ]; then printf 'make append: FILE=<file> LINE="<text>" are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/pages/coord.py" append "$(FILE)"

research-claim: ## [project] claim research questions for this clone, refused when another session holds one; STATUS=done releases (feature 376)   Q="0060 0246" FEATURE=<n> [STATUS="in progress"] [RELEASE=<owner> WHY="<reason>"]
	@if [ -z "$(Q)" ] || [ -z "$(FEATURE)" ]; then printf 'make research-claim: Q="<question numbers>" FEATURE=<n> are required - e.g. make research-claim Q="0060 0246" FEATURE=376\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/pages/research_claims.py" claim "$(Q)" --feature "$(FEATURE)" $(if $(STATUS),--status "$(STATUS)",) $(if $(RELEASE),--release "$(RELEASE)" --why "$$WHY",)

research-claims: ## [project] the live claims on research questions, and nothing else of the sheet (feature 376)   Q="0060 0246"
	@if [ -z "$(Q)" ]; then printf 'make research-claims: Q="<question numbers>" is required - e.g. make research-claims Q="0060 0246"\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/pages/research_claims.py" query "$(Q)"

reserve: ## [project] reserve the next glossary, registry-entry or question number under a host-wide lock and write the file's stub - prints its path; fill it in (feature 265 FR-010: parallel queues never collide; feature 274: a write session's 11th registry key is refused; feature 303: a question's stub carries a tags marker to fill)   KIND=glossary|registry|question KEY=<term, key or heading id> [KEY_CAP_OK='<reason>']
	@if [ -z "$(KIND)" ] || [ -z "$(KEY)" ]; then printf 'make reserve: KIND=glossary|registry|question KEY=<term, key or heading id> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/reserve-prefix.py" "$(KIND)" "$(KEY)" $(if $(URL),--url "$(URL)",) $(if $(TAGS),--tags "$(TAGS)",)

canon: ## [project] search the GM's setting canon for EVERY term of a claim in one call - each hit with its file, line and heading (feature 250 D16; a direct read of a canon file is refused)   TERMS="imperial road|merchant share|artisan"
	@if [ -z "$(TERMS)" ]; then printf 'make canon: TERMS="<a>|<b>|<c>" is required - every term of the claim at once\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/canon.py" "$(TERMS)"

apply-edits: ## [project] apply a quote-check or record-format report's EDIT and GLOSSARY blocks in one command - each only where its old text occurs once in a record file; the rest are listed REFUSED for you (feature 250 D15)   FROM=<the agent's output_file or a saved reply> [SKIP=2,5: EDIT and GLOSSARY blocks counted together, in reply order] [DRY=1]
	@if [ -z "$(FROM)" ]; then printf 'make apply-edits: FROM=<the output_file the agent dispatch named> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/apply_edits.py" "$(FROM)" --root "$$(git rev-parse --show-toplevel)" $(if $(SKIP),--skip "$(SKIP)",) $(if $(DRY),--dry-run,)

page-session: ## [project] start ONE page's work in a FRESH headless session, detached, from written briefs, one after another - absolute paths; a then:<script> step queues the briefs it prints (feature 250 D7, R3); a write brief over four questions is refused (feature 274)   BRIEF="<file> then:<script>" [NAME=<session name, default this clone's>] [MODEL=<model>] [EFFORT=<level>] [AGENTS=<agents.json>] [WRITE_CAP_OK='<reason>']
	@if [ -z "$(BRIEF)" ]; then printf 'make page-session: BRIEF=<file> is required - e.g. make page-session BRIEF=specs/250-close-the-record-checks/briefs/homesteads.md\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && scripts/pages/page-session.sh "$(BRIEF)" "$(NAME)" "$(MODEL)" "$(EFFORT)" "$(AGENTS)"

modal-bundle: ## [project] the files a modal check reads (modal-form, modal-research or modal-depiction), copied out of the repository with the prepass and, for modal-research, the Entry pages, the candidates and the question record for grep; for modal-depiction, the drawing pages, the claims citing them and a crop of the glyph - feature 319; refused while a check before it in the order (form, research, depiction) is owed - feature 375 amendment 3   KIND=<class or key> FOR=modal-form|modal-research|modal-depiction [OUT=<dir>] [CHECK_ORDER_OK="<why>"]
	@if [ -z "$(KIND)" ]; then printf 'make modal-bundle: KIND=<class name or key> is required - e.g. make modal-bundle KIND=Farmhouse FOR=modal-form\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/record/modal_bundle.py "$(KIND)" --for "$(or $(FOR),modal-form)" $(if $(OUT),--out "$(OUT)",) $(if $(REASON),--reason "$(REASON)",)

modal-triage: ## [project] the triage bundle for every pop-up owed only because a page it names moved: the changed blocks beside the kinds naming them, for the modal-triage agent (feature 375; its own agent since 383 amendment 6)   [OUT=<dir>]
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/record/modal_triage.py --root . bundle $(if $(OUT),--out "$(OUT)",)

modal-triaged: ## [project] record a pop-up triage reply: a kind it names (TOUCHES) is sent on to its checks, every other unit of the bundle answered `triage: untouched`   BUNDLE=<dir> REPLY=<file>
	@if [ -z "$(BUNDLE)" ] || [ -z "$(REPLY)" ]; then printf 'make modal-triaged: BUNDLE=<dir> and REPLY=<file> are required\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/record/modal_triage.py --root . record --bundle "$(abspath $(BUNDLE))" --reply "$(abspath $(REPLY))"

modal-prepass: ## [project] the mechanical half of the modal checks for one About-form modal - word band, barred phrases, guesses, Entry files - feature 319   KIND=<class or key>
	@if [ -z "$(KIND)" ]; then printf 'make modal-prepass: KIND=<class name or key> is required - e.g. make modal-prepass KIND=Farmhouse\n' >&2; exit 2; fi
	@cd "$$(git rev-parse --show-toplevel)" && python3 scripts/record/modal_bundle.py "$(KIND)" --prepass

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
	@if [ -z "$(KEY)" ] && [ -z "$(KEYS)" ] && [ -z "$(Q)" ] && [ -z "$(QS)" ]; then printf 'make check-bundle: Q=<question number> (or KEY=<registry key>, KEYS="<k> <k>", or QS= with FOR=intro-check) is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/check_bundle.py" --root "$$(git rev-parse --show-toplevel)" $(if $(KEYS),--keys "$(KEYS)",) $(if $(KEY),--key "$(KEY)",$(if $(Q),"$(Q)",)) $(if $(OUT),--out "$(abspath $(OUT))",) $(if $(EXTRA),--extra $(EXTRA),) $(if $(NO_QUOTES),--no-quotes,) $(if $(KIND),--kind "$(KIND)",) $(if $(NOTES),--notes "$(NOTES)",) $(if $(FOR),--for "$(FOR)",) $(if $(WHOLE),--whole,) $(if $(QUESTION),--question "$(QUESTION)",) $(if $(QS),--qs "$(QS)",) $(if $(NOT_OWED_OK),--not-owed-ok "$(NOT_OWED_OK)",) $(if $(NEW),--new "$(NEW)",) $(if $(IMAGES),--images $(IMAGES),)

source-pages: ## [project] save the full visible text of the named pointers, with a manifest - run BEFORE source-reader, which greps the PAGE where a fetch gives an extract   OUT=<dir> URL=<u1>  (several: URLS="<u1> <u2>")
##  OUT=<dir>      where the pages and MANIFEST.txt go (a scratch directory)
##  URL=<u>        one pointer; URLS="<u1> <u2>" for several - make keeps only the LAST of a repeated URL=
##  QUESTION=<q>   the research question the pages are read for (its number, NNNN - feature 303), recorded on the sources-consulted ledger
##  REFRESH=1      fetch again even where the page cache holds a copy younger than seven days
	@if [ -z "$(OUT)" ] || [ -z "$(URL)$(URLS)" ]; then printf 'make source-pages: OUT=<dir> and URL=<u> (or URLS="<u1> <u2>") are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/source_pages.py" "$(abspath $(OUT))" $(foreach u,$(URL) $(URLS),"$(u)") $(if $(or $(QUESTION),$(Q)),--question "$(or $(QUESTION),$(Q))",) $(if $(SOUGHT),--sought "$(SOUGHT)",) $(if $(REREAD),--reread "$(REREAD)",)

source-outcome: ## [project] record what came of reading a source page on the host-wide sources-consulted ledger and the attempts log - every page a research pass reads (features 288, 312)   URL=<u> OUTCOME=cited:<key>|rejected:<why>|nothing-found|unreadable|pending [QUESTION=<NNNN>] [SOUGHT=<what was looked for>]
	@if [ -z "$(URL)" ] || [ -z "$(OUTCOME)" ]; then printf 'make source-outcome: URL=<u> OUTCOME=<cited:key|rejected:why|nothing-found|unreadable|pending> are required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/sources.py" outcome "$(URL)" "$(OUTCOME)" $(if $(QUESTION),--question "$(QUESTION)",) $(if $(SOUGHT),--sought "$(SOUGHT)",)

uncited: ## [project] the uncited pages judged once, and the kept ones written up - DO=set (count; OUT= writes the URLs) | rule | fetch [LIMIT=n] | bundle OUT=<dir> [LIMIT=n] [START=n] | apply DIRS="<bundle> ..." | score DIR=<bundle> ANSWERS=<labels.json> | draft OUT=<dir> [START=n] | install DIRS="<draft> ..." | merge KEY=<dup> INTO=<kept key> | dedupe [DRY=1] | unkeep URL=<u> REASONS=<r,r> NOTE=<why> | requeue URL=<u> | copy-verdicts | stands URL=<u> NOTE=<why> | retire-cited KEY=<k> ACCESS=<state> NOTE=<why> | report (feature 312)   DO=<step>
	@if [ -z "$(DO)" ]; then printf 'make uncited: DO=set|rule|fetch|bundle|apply|score|draft|install|merge|dedupe|unkeep|requeue|copy-verdicts|stands|retire-cited|report is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/uncited.py" $(DO) $(if $(filter set,$(DO)),$(if $(OUT),--write "$(abspath $(OUT))",),) $(if $(filter bundle draft,$(DO)),"$(abspath $(OUT))" $(if $(START),--start $(START),),) $(if $(filter fetch bundle,$(DO)),$(if $(LIMIT),--limit $(LIMIT),),) $(if $(filter apply install,$(DO)),$(DIRS),) $(if $(filter score,$(DO)),"$(DIR)" "$(ANSWERS)",) $(if $(filter merge,$(DO)),"$(KEY)" "$(INTO)",) $(if $(filter dedupe,$(DO)),$(if $(DRY),--dry,),) $(if $(filter unkeep,$(DO)),"$(URL)" "$(REASONS)" "$(NOTE)",) $(if $(filter requeue,$(DO)),"$(URL)",) $(if $(filter stands,$(DO)),"$(URL)" "$(NOTE)",) $(if $(filter retire-cited,$(DO)),"$(KEY)" "$(ACCESS)" "$(NOTE)",)

cite-uncited: ## [project] an uncited source's entry moved to the works cited, keeping its number, when a footnote first cites it - then write its Used for: line (feature 312)   KEY=<registry key>
	@if [ -z "$(KEY)" ]; then printf 'make cite-uncited: KEY=<the uncited entry'"'"'s key> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/uncited.py" cite "$(KEY)"

attempts: ## [project] what a source was tried for and what came of it, and the filter's verdict on it - by URL, registry key, or question - BEFORE you read it again (feature 312)   URL=<u> | KEY=<k> | Q=<NNNN>
	@if [ -z "$(URL)$(KEY)$(Q)" ]; then printf 'make attempts: URL=<u>, KEY=<k> or Q=<NNNN> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/attempts.py" show $(if $(URL),--url "$(URL)",$(if $(KEY),--key "$(KEY)",--q "$(Q)"))

archive: ## [project] archive ONE cited URL now into the private source archive - the served bytes, the whole page, its text - and write its manifest row (feature 309; the record build refuses a cited URL with none)   URL=<u> [KEY=<registry key not yet written>]
	@if [ -z "$(URL)" ]; then printf 'make archive: URL=<u> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/archive.py" url "$(URL)" $(if $(KEY),--key "$(KEY)",)

archive-sources: ## [project] archive every cited URL with no copy yet (resumable; run it in the background) - or REPORT=1, the coverage table without fetching; GM=1, the GM's matched files copied in; CONSULTED=1, the uncited pages feature 312's filter KEPT, and no other (features 309, 312)   [WORKERS=4] [REPORT=1] [GM=1] [CONSULTED=1 [LIMIT=<n>]]
	@if [ -n "$(CONSULTED)" ]; then python3 "$$(git rev-parse --show-toplevel)/scripts/record/archive_ops.py" consulted $(if $(LIMIT),--limit $(LIMIT),) --workers $(or $(WORKERS),4); else python3 "$$(git rev-parse --show-toplevel)/scripts/record/archive.py" $(if $(REPORT),report,$(if $(GM),gm-copies,backfill --workers $(or $(WORKERS),4))); fi

archive-inbox: ## [project] the GM's downloads in /host-l7r-repo/academic-sources/ archived, the push confirmed, then removed from it - run at the start of every research pass; a NEW download waits until you give its keys (feature 309)   [MATCH="<file>=<key>[,<key>] ..."] [NONE="<file> ..."]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/archive_ops.py" inbox $(foreach m,$(MATCH),--match "$(m)") $(foreach n,$(NONE),--none "$(n)")

archive-find: ## [project] does the archive already hold it? by URL, registry key, or words in the archived text - names each copy's local path; exit 1 when nothing is held (feature 309: look here BEFORE the web)   URL=<u> | KEY=<k> | TERMS="a|b" (every term required; one term per call to try alternatives)
	@if [ -z "$(URL)$(KEY)$(TERMS)" ]; then printf 'make archive-find: URL=<u>, KEY=<k> or TERMS="a|b" is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/archive_ops.py" find $(if $(URL),--url "$(URL)",) $(if $(KEY),--key "$(KEY)",) $(if $(TERMS),--terms "$(TERMS)",)

downloads-ingest: ## [project] on the GM's word "ingest": the marks in the GM's copy of the download list recorded in research/to-download.md, then the inbox archived (feature 313)   [KEEP="<ids>"] [DROP="<ids>"] [MARK="<id>=<downloaded|partial|paywalled|not-found> ..."]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/downloads.py" ingest --keep "$(KEEP)" --drop "$(DROP)" --mark "$(MARK)"

downloads-sync: ## [project] on the GM's word "sync": the GM's copy of the download list replaced from research/to-download.md - refused while it holds anything not ingested (feature 313)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/downloads.py" sync

downloads-tag: ## [project] tag every download-list entry [money] or [diagram] after its number, derived from the questions its Rests-on line points at (the GM, 2026-10-20); download-add tags a new entry itself
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/downloads.py" tag

download-add: ## [project] append a source only the GM can fetch at the end of the canonical download list, under the next number taken under a host-wide lock (feature 313)   FILE=<draft.md, entries headed "### NEW. <the work>">
	@if [ -z "$(FILE)" ]; then printf 'make download-add: FILE=<draft.md> is required - entries headed "### NEW. <the work>", each with a link line, "- Fallback:", "- **Rests on it:**" naming research/questions/<file>, and "- Blocked by:"\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/downloads.py" add "$(FILE)"

access-tags: ## [project] what can be got of each source - open, gm-full, gm-partial, paywalled, bot-refused, down, gone, never-read - derived from the archive, the registry and the GM's marks (feature 313)   [KEY=<key|download:ID>] [JSON=1] | SET=<state> KEY= DATE=<YYYY-MM-DD> REASON="<what it rests on>"
	@if [ -n "$(SET)" ]; then python3 "$$(git rev-parse --show-toplevel)/scripts/record/access_tags.py" set "$(KEY)" "$(SET)" "$(DATE)" "$(REASON)"; \
	else python3 "$$(git rev-parse --show-toplevel)/scripts/record/access_tags.py" report $(if $(KEY),--key "$(KEY)",) $(if $(JSON),--json,); fi

sources-consulted: ## [project] every earlier read of a source page, with its outcome, from the sources-consulted ledger - by URL, or by registry key (feature 288)   URL=<u> | KEY=<regex>
	@if [ -z "$(URL)$(KEY)" ]; then printf 'make sources-consulted: URL=<u> or KEY=<regex> is required\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/sources.py" lookup $(if $(URL),--url "$(URL)",) $(if $(KEY),--key "$(KEY)",)

sources-import: ## [project] ONE TIME, idempotent: seed the sources-consulted ledger from the 2026-09-29 measurement and import the /tmp/l7r-check saves into the page cache (feature 288)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/record/sources.py" import

stale-terms:    ## [project] after a value changed in a feature's spec, where does the OLD value still stand - look BEFORE a later review round   F=253 [AGAINST=<git ref>]
##  F=<feature>    the feature number or directory name under specs/
##  AGAINST=<ref>  compare with the feature directory at this git ref (default: what the previous review round saw)
	@if [ -z "$(F)" ]; then printf 'make stale-terms: F=<feature> is required - e.g. make stale-terms F=253\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/stale_terms.py" "$(F)" --clone "$$(git rev-parse --show-toplevel)" $(if $(AGAINST),--against "$(AGAINST)",); test $$? -le 1

size-table:     ## [project] every drawn rect, wall gap and stroke of a Mode A plan in feet (3 px = 1 ft) - run BEFORE size-audit   PLAN=pool/<subject>.svg
##  PLAN=<svg>     the plan's SVG, relative to the skill directory or absolute
	@if [ -z "$(PLAN)" ]; then printf 'make size-table: PLAN=<plan svg> is required - e.g. make size-table PLAN=pool/<tier>/<name>/<name>.svg\n' >&2; exit 2; fi
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/size_table.py" "$(abspath $(PLAN))"

review-accept:  ## [project] record a review finding as deliberately LEFT, with a reason - logged like an escape   MAP=<map> FINDING=<id> REASON="..."
##  MAP=<map>        the pool map whose last settlement-review verdict raised the finding
##  FINDING=<id>     the finding's id, as that verdict record names it
##  REASON="..."     why it is left; at least two words and eight characters
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/review_prereq.py" accept --clone "$$(git rev-parse --show-toplevel)" --map "$(MAP)" --finding "$(FINDING)" --reason "$(REASON)" && $(LOGBYPASS) permitted "review-accept $(MAP) $(FINDING): $(REASON)"

review-paired-gate:  ## [project] the settlement-review's paired gate - green, running or red (exit 1 on red)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/review_prereq.py" gate-state --clone "$$(git rev-parse --show-toplevel)"

ledger-owed:     ## [project] every check pass logged in this clone with no row in the review ledger, each with the row to add (feature 371); WRITE= writes them from each reply   [WRITE="<where you recorded what you did>"]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/ledger_owed.py" --ledger "$$(git rev-parse --show-toplevel)/dev/review-ledger.md" $(if $(WRITE),--write "$(WRITE)",)

dispatch-dropped: ## [project] record that a dispatch a guard refused is no longer wanted, so the turn may end (feature 385 T22)   TYPE=<agent type> BUNDLE=<path> WHY="<reason>"
	@python3 "$$(git rev-parse --show-toplevel)/scripts/hooks/lib/hm_dropped.py" drop --root "$$(git rev-parse --show-toplevel)" --type "$(TYPE)" --bundle "$(BUNDLE)" --why "$(WHY)"

review-cost:     ## [project] a finished review agent's wall time and tokens - the ledger's cost cells (feature 294)   AGENT=<agent id>
##  AGENT=<id>  the agent id the Agent tool's result names
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/review_cost.py" --agent "$(AGENT)"

review-census:   ## [project] is each review check pulling its weight? the ledger's totals by check (feature 294)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/review_census.py" --root "$$(git rev-parse --show-toplevel)"

review-verdict:  ## [project] a review check's LAST act - write the unit's verdict record   UNIT=<unit> VERDICT=PASS|NEEDS-WORK|NOT-REVIEWABLE [FINDINGS=<json file>]
##  UNIT=<unit>        the owed unit reviewed (its prompt's UNIT: line; MAP= is the same field)
##  VERDICT=<v>        PASS, NEEDS-WORK or NOT-REVIEWABLE
##  FINDINGS=<file>    a JSON list of {"id", "severity", "what"}; ids default to F1, F2, ...
	@python3 "$$(git rev-parse --show-toplevel)/scripts/reviews/review_prereq.py" verdict --clone "$$(git rev-parse --show-toplevel)" --unit "$(or $(UNIT),$(MAP))" --verdict "$(VERDICT)" $(if $(FINDINGS),--findings-file "$(FINDINGS)",)

test-file:      ## [tests] run test files whole, or a targeted subset   FILE=tests/pipeline/test_gencache.py [K="expr"]
##  FILE=<paths>  the test file(s), a directory, or a node id (`tests/x/test_y.py::test_z`) to run
##  K=<expr>      a pytest `-k` expression - a SUBSET, which owes a whole-file run before the gate
	@if [ -z "$(strip $(FILE))" ]; then echo "test-file: no FILE given - run \`make test-file FILE=tests/<path>\` (the variable is FILE, not F); \`make test-full\` runs every test" >&2; exit 2; fi
	@"$$(git rev-parse --show-toplevel)/scripts/format-changed.sh"
	@L7R_TEST_DEPS=$${L7R_TEST_DEPS:-record} python3 -m pytest -p tests.tooling._test_deps -n $(XDIST_WORKERS) --dist worksteal -q --no-cov $(if $(K),-k "$(K)",) $(FILE) && $(STATE) green-local test-file

dead-closure:   ## [diagnostics] what a deletion leaves dead and which deleted name a file still calls (frozen exhibits included), against BASE (feature 388)   [BASE=HEAD]
	@python3 scripts/measure/dead_closure.py --base "$(or $(BASE),HEAD)"

sweep:          ## [tests] run a random-equivalence test over more seeds than its default, the file unchanged   FILE=tests/hamletgen/ways/test_web_counts.py SEEDS=2000
##  FILE=<paths>  the test file(s) whose sweeps read `tests/_sweep.py`
##  SEEDS=<n>     how many seeds each sweep takes (`L7R_SWEEP_SEEDS`)
	@if [ -z "$(strip $(FILE))" ] || [ -z "$(SEEDS)" ]; then echo "sweep: FILE=<test file> and SEEDS=<n> are required" >&2; exit 2; fi
	@L7R_SWEEP_SEEDS=$(SEEDS) $(MAKE) --no-print-directory test-file FILE="$(FILE)"

roll-audit:     ## [tests] per rolling context of the gate baseline, the engine lines NO other context reaches   MIN_LINES=2000 (the tier knob)
	$(RUN).tools.roll_audit --min-lines $(or $(MIN_LINES),2000)

roll-census:    ## [tests] the roll census of the LAST test phase, judged against tests/rolls.py   FULL=1: a stale roster row counts
	@L7R_ROLL_CENSUS="$(ROLL_CENSUS)" python3 -m l7r.diagram.ci rollcensus verdict $(if $(FULL),full,)

cov-file:       ## [tests] which lines of MOD does ONE test file reach?   FILE=tests/settlement/test_houses.py MOD=l7r/diagram/settlement/houses.py
##  FILE=<test path>   the test file to run
##  MOD=<module path>  the module to report coverage for - e.g. `l7r/diagram/settlement/houses.py`
	@python3 -m pytest -n0 -q --no-header -p no:cacheprovider --cov=$(MOD) --cov-report=term-missing $(FILE)

parts-sweep:     ## [tests] run each split guard suite at 1, 2, 3 and 8 parts and report any count whose result differs - after a suite's cases change; never in the gate   [SUITES="test-pair-hooks.sh ..."]
	@bash tests/hooks/parts_sweep.sh $(SUITES)

subagent-cache:  ## [project] what subagents write to the prompt cache fresh, per agent type, and the repeated text in their bundles (feature 383 amendment 6)   [SINCE=YYYY-MM-DD]
	@python3 scripts/measure/subagent_cache.py $(if $(SINCE),--since $(SINCE),)

wave-report:     ## [project] a workflow wave's cost - each agent's first-request cache read and write, the main session's wakes - against the last hand-launched wave (feature 383 amendment 7)   [WF=<.../workflows/wf_*>]
	@python3 scripts/measure/wave_report.py $(if $(WF),--run $(WF),)

collect-cost:    ## [tests] where a run's time goes before any test runs: as make runs it, no workers, collection alone (feature 383 amendment 3)   TREE=quick|tooling
	@python3 scripts/measure/collect_cost.py --tree $(or $(TREE),quick) $(if $(JSON),--json $(JSON),)

durations:       ## [tests] where the suite's time goes - run when a target feels slow
##  FULL=1        also profile `tests/full/` (default: it is ignored, so this is the quick tree only)
##  MARK=<expr>   a pytest `-m` marker expression, e.g. `tooling` (default: `not rolls_map`)
##  N=<rows>      how many of the slowest rows to print (default: 12)
	@python3 -m pytest -n $(XDIST_WORKERS) -q --no-cov $(if $(FULL),,--ignore=tests/full) $(if $(MARK),-m "$(MARK)",-m "not rolls_map") --durations=$(or $(N),12) 2>&1 | grep -E "^[0-9.]+s (call|setup)|passed|failed" | head -$$(( $(or $(N),12) + 2 ))

# Timed with date +%s, not $$SECONDS: make's shell is sh, where SECONDS is unset.
# The ratchet and the budget judge warm, selective runs only; raise the budget only with a measurement.
# The house-style scan is a phase, not a test: testmon selects tests by changed code and would never pick it.
quick:           ## [tests] tier 2: lint, types and every test that rolls no map; change-selected, stops at the first failure   ALL=1
##  ALL=1  run EVERY quick test, not just the ones whose code changed (default: change-selected via testmon)
	@python3 scripts/gates/check-function-cap.py && python3 -m ruff check --fix l7r/ tests/ && python3 -m ruff format l7r/ tests/ && $(TYPECHECK)
	@python3 scripts/gates/check-house-style-delta.py --selftest >/dev/null
	@python3 scripts/gates/check-house-style-delta.py .
	@python3 scripts/gates/check-question-size.py
	@python3 scripts/gates/check-file-scale.py .
	@python3 scripts/gates/spec-lint.py --delta .
	@python3 scripts/gates/check-partial-citations.py .
	@if [ -n "$$(git status --porcelain -- tests)" ] || ! git diff --quiet "$$(git merge-base HEAD origin/main 2>/dev/null || echo HEAD)" -- tests; then L7R_TESTS_EXHAUSTIVE=1 python3 -m pytest -q --no-cov -p no:randomly tests/test_markers.py >/dev/null 2>&1 || { printf 'quick: a test that rolls a map lacks @pytest.mark.rolls_map (tests/test_markers.py):\n'; L7R_TESTS_EXHAUSTIVE=1 python3 -m pytest -q --no-cov tests/test_markers.py; exit 1; }; fi
	@warm=$$([ -f .testmondata ] && echo yes || echo no); start=$$(date +%s); $(EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal $(TESTMON) -q --no-cov -x --ff -m "not rolls_map and not tooling" $(TIER_SELECT) $(QUICK_TREE); ec=$$?; \
	  el=$$(( $$(date +%s) - start )); \
	  if [ $$ec -ne 0 ]; then exit $$ec; fi; \
	  root=$$(git rev-parse --show-toplevel); \
	  if [ -n "$(FROM_PREFLIGHT)" ]; then [ $$el -lt 15 ] || printf '\nquick took %ss inside the preflight - not judged here (feature 375).\n' "$$el"; \
	  elif [ "$$warm" = yes ] && [ -z "$(ALL)" ]; then python3 "$$root/scripts/measure/ratchet.py" quick "$$el" || exit 1; \
	  elif [ $$el -ge 15 ]; then printf '\nquick took %ss, but this run was %s - not judged against the 15s bar (feature 171).\n' "$$el" "$$([ "$$warm" = yes ] && echo "ALL=1, so unselective" || echo "COLD: it built .testmondata")"; fi; \
	  if [ -z "$(FROM_PREFLIGHT)" ] && [ "$$warm" = yes ] && [ -z "$(ALL)" ] && [ $$el -gt $(QUICK_BUDGET) ]; then \
	    printf '\n\033[1mquick took %ss, over its %ss budget.\033[0m\n' "$$el" "$(QUICK_BUDGET)"; \
	    printf 'Something slow is running that should not be. Find it:  \033[1mmake durations\033[0m\n'; \
	    printf 'A test near the top of that list without @pytest.mark.rolls_map is the cause.\n\n'; \
	    exit 1; \
	  fi
	@readers=$$(python3 scripts/gates/pool-readers.py changed); \
	  if [ -n "$$readers" ]; then printf 'quick: the hamlet manifests moved - running the tests that read them\n'; \
	    python3 -m pytest -n $(XDIST_WORKERS) -q --no-cov -x -m "not rolls_map and not tooling" $$readers || exit 1; fi; \
	  python3 scripts/gates/pool-readers.py stamp
	@printf '\n\033[1mquick: clean\033[0m - the %s map-rolling tests were NOT run; `make done` before pushing.\n' "$$(grep -rho --include='*.py' '@pytest.mark.rolls_map' tests | wc -l)"
	@$(STATE) green-local quick

bypass-audit:    ## [project] every escape token taken, with the reason its user gave   (the FULL prompt reads this)
	@if [ -n "$$CODEBUILD_BUILD_ID" ]; then python3 -m l7r.diagram.ci door && exit 0; printf '\n\033[1mREFUSED: the FULL scope in a build needs the committed answer to the local prompt.\033[0m\n\n'; exit 1; fi; \
	why="$(REF_WHY)"; \
	if [ -n "$$why" ] && [ ! -t 0 ]; then \
	  printf "\n\033[1mREFUSED: a FULL run with REF_WHY set, with nothing attached to answer for it.\033[0m\n\n"; \
	  printf "The prompt below exists because its default answer is NO. Passing REF_WHY on the\n"; \
	  printf "command line skips it, and a backgrounded run cannot be asked to reconsider - which is\n"; \
	  printf "exactly how feature 126 ran the full gate THREE times against a standing instruction to\n"; \
	  printf "run only the reference settlement. Every bypass was logged and none was stopped.\n\n"; \
	  printf "  \033[1mmake maps\033[0m        the pool, scoped by how the last run went - the reference alone after a failure\n"; \
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
	@python3 -c "import sys; sys.path.insert(0, '.'); 	from l7r.diagram import hamletgen as hg; 	from l7r.diagram.pipeline import rollcache; 	r, how = rollcache.report(hg.HamletSpec(name='Inashiro', seed=4, households=15, down_deg=90, water_sink='pond', settlement_form='nucleated')); 	print('\033[1mreference settlement (Inashiro, seed 4): ' + ('CLEAN\033[0m' if r.ok else 'FAILING\033[0m -> ' + ', '.join(r.failures)) + ' [' + how + (' - served from the roll cache: nothing the roll executes changed' if how == 'HIT' else '') + ']'); 	__import__('os').environ.get('L7R_REF_NO_CLASS') or open(__import__('os').path.join(__import__('subprocess').run(['git','rev-parse','--absolute-git-dir'],capture_output=True,text=True).stdout.strip() or '.git','roll-cache-class'),'w').write('warm' if how.startswith('HIT') or how.startswith('BYPASS-SHARED') else 'cold'); 	sys.exit(0 if r.ok else 1)" || { 	  printf '\n\033[1mSTOPPING HERE.\033[0m The reference settlement is red, so nothing more expensive runs.\n'; 	  printf 'Fix Inashiro first - it rebuilds in about a minute. Everything else is 4x to 25x that,\n'; 	  printf 'and none of it can tell you anything useful while the one map you iterate on is broken.\n'; 	  printf 'To REGENERATE it and read every failure in full: \033[1mmake maps\033[0m.\n'; \
	  printf 'Do not reach for REF_OK=1 - it prompts, and a prompt with no terminal is refused.\n\n'; exit 1; }

IDLE_CTX = $(eval IDLE_CTX := $(shell $(SWITCH) idle 2>/dev/null || echo unreadable))$(IDLE_CTX)
DONE_NAME = $(if $(filter 0,$(IDLE_CTX)),done,idle-done)
idle-tests:     ## [tests] {inactive: arming is disabled - the GM turned it off 2026-09-06; the target still runs by hand} what an idle session runs unattended (feature 136): the whole gate, never FULL, recorded as `idle-done`
	@PAIR_OK="idle run: no session attached to dispatch a review" $(MAKE) --no-print-directory done INCREMENTAL=0; rc=$$?; \
	  python3 "$$(git rev-parse --show-toplevel)/scripts/hooks/lib/usage_log.py" record --tool idle-tests --kind target --outcome "$$( [ $$rc -eq 0 ] && echo passed || echo failed )"; \
	  exit $$rc

maps:            ## [maps] regenerate and check the pool, picking its own scope from how the last run went   SCOPE=reference|all
##  SCOPE=reference|all  override the scope; by default it picks its own - the reference hamlet alone after a failed run, the whole tier after a clean one
	@python3 -m l7r.diagram.tools.mapcheck
	@$(MAKE) --no-print-directory pool-index-if-stale

perf:            ## [performance] take a performance snapshot of the reference hamlet across its seeds, with the machine's state at both ends   LABEL=<NNN>-start|-end [SCALING=1]
##  LABEL=<NNN>-start|<NNN>-end  which bookend this snapshot is (default: `adhoc`, which counts as neither)
##  SCALING=1                    add the 10-, 20- and 40-household legs - for investigating the algorithm, not routine work
	@python3 -m l7r.diagram.tools.perf_snapshot --record --label "$(or $(LABEL),adhoc)" $(if $(SCALING),--scaling,)

census:           ## [performance] the overlap census: comparisons per call of every check the pool's rolls run, the ones over the flag named
	@python3 -m l7r.diagram.tools.overlap_census

.PHONY: review-yield cohort-seeds task-add set-down where-time land-batch fix-yield
review-yield:     ## [performance] each review check's passes, findings acted on / dismissed / deferred, author-missed, hours and tokens, from the ledger   [SINCE=2026-09-26]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/review_yield.py" $(if $(SINCE),--since $(SINCE),)

fresh-tally:      ## [performance] seeds nobody has used: the failed share pooled, by form and by cause (feature 417)   [COMMIT=<sha prefix>] [SINCE=<UTC stamp>]
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/fresh_tally.py" $(if $(COMMIT),--commit "$(COMMIT)",) $(if $(SINCE),--since "$(SINCE)",)

cohort-seeds:     ## [performance] which cohort seeds found which failure, over how many changes, and the fewest first seeds that find them all (dev/cohort-log/)
	@python3 "$$(git rev-parse --show-toplevel)/scripts/measure/cohort_seeds.py"

perf-report:    ## [performance] the trend, and which BAND the newest bookend pair reaches   AGAINST=<NNN>-start ENV=local|codebuild
##  AGAINST=<NNN>-start  compare the newest snapshot against this bookend
##  ENV=local|codebuild  which environment's band-1 line to judge against (default: local)
	@python3 -m l7r.diagram.tools.perf_snapshot --report $(if $(AGAINST),--against $(AGAINST),)

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

static format typecheck test: | guard

static:         ## [static] the static checks: ruff, duplicate-defs, file-scale, stale-dirs (was `lint`)
	python3 scripts/gates/check-function-cap.py --selftest >/dev/null && python3 scripts/gates/check-function-cap.py
	python3 -m ruff check --fix .
	python3 scripts/gates/check-duplicate-defs.py --selftest
	python3 scripts/gates/check-duplicate-defs.py .
	python3 scripts/gates/check-file-scale.py --selftest
	python3 scripts/gates/check-file-scale.py .
	python3 scripts/gates/spec-lint.py --selftest
	python3 scripts/gates/spec-lint.py --delta .
	python3 scripts/hooks/lib/hm_conflict.py --selftest
	python3 scripts/hooks/lib/hm_conflict.py --tracked .
	python3 scripts/make-docs.py . --check
	python3 scripts/gates/check-stale-dirs.py --selftest
	python3 scripts/gates/check-stale-dirs.py .
	bash scripts/reviews/layout_carry.sh --selftest

format:          ## [static] ruff format over the tree
	python3 -m ruff format .

typecheck:       ## [static] pyrefly over the engine, one-shot, no daemon (feature 142)
	$(TYPECHECK)

FULL_TREE_IGNORE = $(if $(COV_FLOORS),,--ignore=tests/full)
FULL_ENV = $(if $(COV_FLOORS),L7R_TESTS_FULL=1,)
BROWSER_SKIP = $(shell root=$$(git rev-parse --show-toplevel 2>/dev/null); [ -n "$$root" ] && python3 "$$root/scripts/gates/gate-stamp.py" --fresh browser >/dev/null 2>&1 && echo --ignore=tests/full/interactive/page_browser)
COV_SCOPE = $(if $(COV_FLOORS),,$(shell python3 -m l7r.diagram.ci cov-scope 2>/dev/null))
ROLL_DESELECT =
REFERENCE_TIER = hamlet
CPU_COUNT ?= $(shell nproc 2>/dev/null || echo 8)

# loadgroup, not worksteal: worksteal ignores xdist_group, and the browser package's modules must share one Chromium.
DIST ?= loadgroup
XDIST_WORKERS = $(if $(CODEBUILD_BUILD_ID),auto,$(shell [ "$(CPU_COUNT)" -lt 6 ] && echo "$(CPU_COUNT)" || echo 6))
EXHAUSTIVE_ENV = $(if $(EXHAUSTIVE),L7R_TESTS_EXHAUSTIVE=1,)
TESTMON = $(if $(ALL),--no-testmon,--testmon-forceselect)
QUICK_TREE = tests --ignore=tests/tier_town --ignore=tests/tier_city --ignore=tests/gate --ignore=tests/full --ignore=tests/tooling

# One-shot pyrefly; don't bring back a resident type-check daemon (dmypy held 380-600 MB per clone).
TYPECHECK = pyrefly check --python-interpreter-path "$$(command -v python3)"
GATE_EXHAUSTIVE_ENV = L7R_TESTS_EXHAUSTIVE=1 $(if $(COV_FLOORS),L7R_COV_FLOORS=1,)
TIER_SELECT =

JOURNAL_ENV =

test-full:      ## [tests] the gate's whole test phase + all three coverage floors (everything except tests/soak/, which only `make soak` runs)
	@$(MAKE) --no-print-directory test COV_FLOORS=1 $(if $(FROM_DONE),,INCREMENTAL=0) && $(STATE) green-local test-full

soak:           ## [tests] the tier ABOVE the gate, run by nothing ordinary (constitution VI v2.23.0): the tests that roll more than the floor needs; REFUSES when empty rather than reporting a vacuous green and larger maps (tests/soak/)
	@n=$$(ls $(SOAK_DIR)/*.py 2>/dev/null | wc -l); \
	if [ "$$n" -eq 0 ]; then \
	  printf '\n\033[1mmake soak: the soak suite is EMPTY, so there is nothing to prove.\033[0m\n\n'; \
	  printf 'tests/soak/ is declared and deliberately unfilled - the home of the tier above the gate\n'; \
	  printf '(the same code over many seeds and larger, more realistic maps), kept as structure so that\n'; \
	  printf 'when that work arrives there is no argument about where it goes.\n\n'; \
	  printf 'Running it now would report a GREEN build having executed zero tests. Read\n'; \
	  printf 'tests/soak/CLAUDE.md - it carries the membership rule (a test belongs there if removing\n'; \
	  printf 'it does not change coverage) and the honest statement of when this tier earns its keep.\n\n'; \
	  exit 1; \
	fi; \
	$(GATE_EXHAUSTIVE_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist worksteal -q --no-cov $(SOAK_DIR) \
	  && $(STATE) green-local soak
SOAK_DIR ?= tests/soak

# A deselected test takes its coverage with it, so the 100% floors need the whole suite: done's test phase is test-full.
COV_FLOORS =

# PATHS is a shell variable, not a make one: the recipe is one line, so a make expansion would run before the plan exists.
# Every floor reports: one that exits first would hide the floors after it.
test:            ## [tests] {internal} the pytest phase itself (internal - `done` and `test-full` call it, not you)
	@$(if $(COV_SCOPE),printf 'coverage: %s\n' "$(COV_SCOPE)";,)
	@$(if $(COV_FLOORS),$(if $(NO_CUTOFF),INCR_NO_CUTOFF=1 ,)python3 -m l7r.diagram.ci incremental plan $(if $(INCR_FORCE),full "$(INCR_FORCE)",) || exit 1;,) \
	$(if $(COV_FLOORS),paths=$$(python3 -m l7r.diagram.ci incremental paths 2>/dev/null);,) \
	$(if $(COV_FLOORS),rm -f "$(ROLL_CENSUS)" "$(ROLL_CENSUS).renders";,) \
	$(if $(BROWSER_SKIP),printf 'browser tests: already green against exactly what they read - skipped (gate-stamp --fresh browser; make page-check runs them on demand)\n';,) \
	tpy=$$(date +%s); if python3 -c "import xdist" >/dev/null 2>&1; then $(GATE_EXHAUSTIVE_ENV) $(FULL_ENV) $(JOURNAL_ENV) $(INCR_ENV) python3 -m pytest -n $(XDIST_WORKERS) --dist $(DIST) $(COV_SCOPE) $(INCR_ARGS) $(FULL_TREE_IGNORE) $(BROWSER_SKIP) $(ROLL_DESELECT) $(TIER_SELECT) $${paths:-}; else $(GATE_EXHAUSTIVE_ENV) $(FULL_ENV) $(JOURNAL_ENV) $(INCR_ENV) python3 -m pytest $(COV_SCOPE) $(INCR_ARGS) $(FULL_TREE_IGNORE) $(BROWSER_SKIP) $(ROLL_DESELECT) $(TIER_SELECT) $${paths:-}; fi; ec=$$?; \
	$(if $(COV_FLOORS),$(RUNSTATS) phase "$$(git rev-parse --absolute-git-dir)" pytest $$(( $$(date +%s) - tpy )) 2>/dev/null || true; tfl=$$(date +%s);,) \
	traced=$(if $(filter --no-cov,$(COV_SCOPE)),,1); \
	if [ $$ec -ne 0 ]; then [ -n "$$traced" ] && { python3 scripts/measure/uncovered-in-diff.py || true; }; exit $$ec; fi; \
	if [ -z "$(COV_FLOORS)" ]; then \
	  printf '\033[1mcoverage floors: deferred to `make done`\033[0m (a deselected test takes its coverage with it)\n'; \
	  [ -n "$$traced" ] && { python3 -m coverage combine --append >/dev/null 2>&1 || true; python3 scripts/measure/uncovered-in-diff.py || true; }; \
	  exit 0; \
	fi; \
	python3 -m coverage combine --append >/dev/null 2>&1 || true; \
	python3 -m l7r.diagram.ci incremental merge || exit 1; \
	python3 -m l7r.diagram.ci incremental carry || exit 1; \
	cov_ec=0; \
	python3 -m coverage report -m --fail-under=100 || { echo "COVERAGE: a module is under 100% - the table above names it and its missing lines."; cov_ec=1; python3 scripts/measure/uncovered_marks.py || true; }; \
	L7R_ROLL_CENSUS="$(ROLL_CENSUS)" python3 -m l7r.diagram.tools.hamlet_floor || cov_ec=1; \
	rc_mode=$$(python3 -m l7r.diagram.ci incremental mode 2>/dev/null || echo full); \
	L7R_ROLL_CENSUS="$(ROLL_CENSUS)" python3 -m l7r.diagram.ci rollcensus verdict $$([ "$$rc_mode" = full ] && echo full) || cov_ec=1; \
	[ $$cov_ec -eq 0 ] && { python3 -m l7r.diagram.ci incremental save-baseline || cov_ec=1; }; \
	$(RUNSTATS) phase "$$(git rev-parse --absolute-git-dir)" floors $$(( $$(date +%s) - tfl )) 2>/dev/null || true; \
	exit $$cov_ec

INCR_FORCE = $(if $(FULL),FULL=1 requested,$(if $(filter 0,$(INCREMENTAL)),INCREMENTAL=0 requested,))
ROLL_CENSUS = $(shell git rev-parse --absolute-git-dir 2>/dev/null)/roll-census.jsonl
TOOLING_GATE_ARGS = $(if $(COV_FLOORS),$(if $(INCR_FORCE),,-p tests.tooling._test_deps),)
INCR_ARGS = $(if $(COV_FLOORS),--cov-context=test -p l7r.diagram.ci.gate_plugin -p l7r.diagram.ci.rollcensus $(TOOLING_GATE_ARGS),)
INCR_ENV = $(if $(COV_FLOORS),L7R_GATE_SELECT="$(shell python3 -m l7r.diagram.ci incremental where 2>/dev/null)" L7R_ROLL_CENSUS="$(ROLL_CENSUS)" $(if $(TOOLING_GATE_ARGS),L7R_TEST_DEPS=gate,),)

# EVERY MAKE INVOCATION RECORDS ITS RUN (feature 406 T02, D161; the GM 2026-10-19: "it is notionally possible for us to see how
# often a tool is used"). The event log sees a target only when a session's Bash call runs it; one run from another target's
# recipe, from a script or from the idle timer left no trace. Each parse records its goals `ran` in <git dir>/tool-usage.jsonl
# (the default goal's name when none is given); `make -n` and `make -q` run nothing and record nothing. `make tool-yield` counts
# a target's runs from these lines alone and reads their outcomes from the event log.
ifeq (,$(findstring n,$(filter-out --%,$(firstword $(MAKEFLAGS))))$(findstring q,$(filter-out --%,$(firstword $(MAKEFLAGS)))))
_TOOL_YIELD_RAN := $(shell python3 "$(dir $(abspath $(firstword $(MAKEFILE_LIST))))scripts/hooks/lib/usage_log.py" goals $(or $(MAKECMDGOALS),$(.DEFAULT_GOAL)) >/dev/null 2>&1)
endif
