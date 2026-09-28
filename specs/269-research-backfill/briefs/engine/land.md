# Brief - feature 269 (research backfill): close out and land

You are a FRESH headless session named `diagram-supplemental`, in `/diagram/.clones/diagram-supplemental`. Every rule of
the root CLAUDE.md applies. You are headless: never background a command. Run the gate in the FOREGROUND (it takes a few
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
5. **The GM's items** are in `/diagram/.clones/.tools/logs/269-gm-items-reviewed.md`, and escalation-check is done. The
   rows waiting on the GM (B32 duck pen, B33, B34, B35, the B19 gate) are recorded in future-work as waiting on the GM's
   ruling, with the reviewed wording. They are not implemented.
6. **Tick.** Tick every task whose verification exists (`make tick`); the plan review must be CLEAR (`scripts/plan-gate.sh`).
   A task that cannot be ticked is reported, not forced.
7. **`make glossary && make record && make citations`**, then `make done` in the FOREGROUND. Fix every failure, and
   re-run once. Then run `scripts/sync-with-main.sh done` from the clone. If a guard refuses the push, read why and fix
   it; use an escape only with a real reason.
8. **Report.** Your last message is one paragraph: the landing hash on main, what was ticked, what is left and where it
   is recorded.
