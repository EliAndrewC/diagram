# Brief - feature 269 (research backfill): close out and land

You are a FRESH headless session named `diagram-supplemental`, in `/diagram/.clones/diagram-supplemental`. Every rule of
the root CLAUDE.md applies. You are headless: never background a command. Never end a turn while an agent you dispatched is still running: your session ends with your turn, and its result never reaches you, so wait for every agent to return first. Run the gate in the FOREGROUND (it takes a few
minutes; the tool limit is 10). Read coordination files only with `make lines` / `make append`.

The research is done. The record-finishing queue (FX1-FX4, SP1-SP2, FIN) and the engine groups (E1-E9, K1-K5) have
run. Their results are in `specs/269-research-backfill/briefs/*-checks.md`, `briefs/engine/log.md` and the git log.
Your job is 269's tasks T19-T25 (`specs/269-research-backfill/tasks.md`) and the landing.

1. **Relinks.** `grep -rn "RELINK 269\|RELINK 273" .claude/skills/diagram/research`. Each comment names the section and
   the anchor to link: 272's religion-and-death 210/510/530 point to 270 and 280, and 160 points to 273's 540. Turn
   each plain title back into a link to that anchor, and delete the comment.
2. **274's T12.** In `specs/274-leaner-research-sessions/tasks.md`, turn T12's OPEN post-landing note into a done note:
   "Diagram supplemental told Diagram research, Diagram shrines and Diagram buildings on 2026-09-28 after 825925e73
   reached main; recorded in /diagram/.clones/RESEARCH-PEER-CHECKS.log".
3. **T24 future-work.** For each entry in outcomes.md section 5, move each entry the outcomes close to
   `future-work/closed.md` (one line each), and rewrite each entry they narrow to what remains. Leave open ones as they
   are. Add the engine items that `log.md` marks PARTIAL or NOT-DONE, and the conversion-owed rows of outcomes.md
   section 3, each with its measurement, mechanism and sketch (constitution XIV).
4. **The spec's Decisions Recorded** (spec.md): one line per outcome that changed what a map draws. Label each one
   historically accurate, deliberate deviation, map drawing convention, or guess.
5. **The GM ruled on all five on 2026-09-28** (`specs/269-research-backfill/rulings-2026-09-28.md`); E9 and K5 carried
   them out. Confirm each ruling is in place. The headman's gate (B19) and the village's funerary grounds are recorded
   as OWED AT THE VILLAGE CONVERSION in `future-work/farming-communities.md` and in `migration-plan.md`'s village step:
   the scripted village MUST gate the headman's house. The spec's Decisions Recorded cites the rulings file.
6. **Tick.** Tick every task whose verification exists (`make tick`); the plan review must be CLEAR (`scripts/plan-gate.sh`).
   A task that cannot be ticked is reported, not forced.
7. **`make glossary && make record && make citations`**, then `make done` in the FOREGROUND. Fix every failure, and
   re-run once.
7b. **Settlement review, paired with the green gate** (`pair-hooks.sh`: the pool layouts moved in E1-E8). Dispatch ONE
   `settlement-review` per pool hamlet (inashiro, kashikawa, kuwabata, sawada, mizuguchi), all five in one message,
   the prompts from `make verify`. Wait for all five to return before anything else: you are headless. Apply their
   findings. Re-run the gate if an engine file changed, and then the reviews of the maps that moved. Add one row per
   review to `docs/review-ledger.md`. E2's five reviews came back NOT-REVIEWABLE because no gate was green then; these
   replace them. Findings for the GM go through `escalation-check`.
7c. Then run `scripts/sync-with-main.sh done` from the clone. If a guard refuses the push, read why and fix
   it; use an escape only with a real reason.
8. **Report.** Your last message is one paragraph: the landing hash on main, what was ticked, what is left and where it
   is recorded.
