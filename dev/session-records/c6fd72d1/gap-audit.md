# Gap audit of 451's convergence rules (read-only, 2026-11-23)

Scope: the landed code at d601eee011 plus the clone's uncommitted T184/T193/T194 work (WIP); nothing written or run. "Filed?" greps 451's tasks.md, tasks-done.md and found.jsonl. Not audited: T190's `apply_edits/settled.rs`. One order, by likely cost.

## The gaps

1. **A dead page session's watcher spins forever, unseen.**
   - What goes wrong: the runner writes `ALL DONE` only when it succeeds (`pages/src/runner/work.rs:340,423`; `runner.rs:425-428`). The waiter it prints is `until grep -q '^ALL DONE'` (`runner.rs:57`). So a runner that raises, or is killed, leaves the waiter running for good.
   - Why nothing notices:
     - The detector exists: `finished_run_hooks.rs:283`, "A WAITER IS SPINNING ON A DEAD PRODUCER". But it runs only at a prompt, a Stop or a SessionStart. At the turn's Stop the runner is still alive.
     - The idle check is the one thing that runs later. It never calls `stale_waiters`. It reads a listed shell as live and stays silent. T193's `stalls.rs` skips every id with no transcript.
   - Cost: hours of silent idling (the GM's complaint). Not filed.
2. **T193's accepted limit assumes a next idle check that never comes.** (WIP; inferred, since it rests on how the harness wakes sessions)
   - Where: `set_down_hooks/idle.rs:62-71`. `live` is copied from the Stop's input before the 300 s sleep, so it is stale when judged.
   - Why a builder is missed: `STALL_SECS` (600) is longer than `IDLE_SECS` (300). A builder that goes silent at the coordinator's last Stop still reads as live at that check.
   - The plan (T193 point 32) accepts this as "named only at the session's next idle check". But in the case T193 targets, a builder's notice is lost and nothing wakes the coordinator, so that next Stop never comes.
   - The test covers only a later Stop (`tests/stalls.rs:60`). Cost: the T184 hour again. Not filed.
3. **Both triage reply parsers fail open.**
   - The parsers: `owed/.../triage.rs:29-30,680` and `claims/triage.rs:34,722` match a line only once whitespace and backticks are stripped.
   - What slips through: a `- TOUCHES` bullet, `**TOUCHES**`, or a separator other than the ASCII " - ".
   - The result: every pop-up or claim left unnamed is recorded as "triage: untouched" or "triaged", durably. That includes a wrong or truncated reply file.
   - The only refusal is for an empty reply, and only on the claims side (`claims/commands.rs:633`).
   - Cost: pop-up and claim checks skipped without anyone knowing (how often is inferred). Not filed.
4. **T184's refusal teaches a split that T185 cannot see.** (WIP)
   - The mismatch:
     - `checks/question_size.rs:134-141` counts a token as kept if it stands on any `href="NNNN-...html"` page.
     - Its refusal (line 151) says only "keeps a sentence linking to it".
     - The triage honors only `<a class="moved">` (`triage/change.rs:28`).
   - No contract or rules file names the `moved` form (grep: research/CLAUDE.md, docs/, page-session-rules.md, agents). Only the MANIFEST says it, after the fact.
   - The result: a split made as the refusal says, for example by a page session, passes T184. It then re-owes every moved block as removed: the 21-pop-up cascade plus the claims, about 60 units. Not filed.
5. **Claims do not follow T185's pointers.**
   - Where: `claims/index.rs:126,169,196` (`findings_of`, `page_blocks`, `research_fp`) and `claims/bundle.rs:292` (`cited_pages`). These read only the page a claim cites. Pop-ups have `modals::followed`.
   - After a split:
     - An edit to a moved block on the target page never re-owes the claim. That is a silent miss.
     - impl-drift reads a source page that no longer holds the support. It then returns a false DRIFTED or NEEDS-RESEARCH, costing a round.
   - Live case: `rust/phases/src/field/brook.rs::brook#the intake's siting` cites 0059, now split to 0333. Not filed.
6. **The claims MANIFEST shows a moved-with-edit block as "Removed".**
   - The WIP T194 change gives only the pop-up MANIFEST its "Moved with edits" section (`owed/.../triage.rs:191`). The claims `Moved::shown` still lists `removed`, and those blocks are in it.
   - The claims-triage contract says "A removed block that a claim's note leaned on does", so these claims get sent on wrongly.
   - Of T194's defects, the claims triage shares only number 2 (the echo, in the shared `change.rs`, fixed in the WIP for both). It reads no note keys, so it never had number 1.
   - Cost: false impl-drift dispatches on every split. Not filed.
7. **A later scoped round never pairs a change on a pointer's target page.**
   - Where: `bundle/src/arbiter/bundle/marks.rs:317-345` (`subject_files`, which has no `followed`), and `earlier.rs:147`, which tells the reviewer "judge ONLY ... re-open nothing".
   - Example: 0333 restated "An official handbook" as "A Japanese encyclopedia". That change sits in the bundle but is never paired, so a factual edit goes unjudged. Not filed.
8. **An edit to `data-guess` text is never reviewed.**
   - `pages::words` drops markup (`research/src/record/items.rs:12-13`), so the modal triage and record-owed both clear the edit.
   - `faults` checks only that the attribute is non-empty (`items.rs:122`).
   - Yet that sentence is the very Guesses bullet the pop-up shows. T192 will add about 670 of them. Cost: a wrong Guesses line ships. Not filed.
9. **Mixed trees make durable answers.**
   - `scripts/gates/l7r-gate.sh` builds from the clone's working tree, so triage and apply-edits use other builders' uncommitted code. The answers land in the common git dir with no build id.
   - land-alone isolates the landing's code but trusts those answers.
   - Seen today: T184's first two triage runs ran T185/T186 code that had not landed (t184-cascade.md section 1).
   - The guards in `scripts/hooks/l7r-guard.sh:26,31` also build from `$CLAUDE_PROJECT_DIR`. So the WIP idle check is live for sessions rooted in this clone (inferred).
   - Partly filed: T152 and T121 cover the closing checks and formatting, not recorded answers.
10. **Derived files are caught only by `make done`'s preflight.**
    - Where: `measure/src/preflight.rs:22` covers docs, building-programs and glossary.
    - `make quick` does not check them. `make static` checks only docs (`make-docs --check`).
    - So closing-checks still passes a stale `docs/building-programs.md` or glossary, the same miss as building-programs.md today. Cost: one red `make done`, about an hour each time. Not filed.
11. **T188 does not reach building-review.**
    - The task line names "building-review severities". But the plan (plan-done, T188) records "no change".
    - So fixing a nitpick moves the sheet's fingerprint and owes a full building-review round, which the GM's rule forbids. Not filed.
12. **Low, each:**
    - An EDIT written `` EDIT `p` (TRUTH) `` is silently dropped (`guard/shared/src/checks/reply.rs:9-12`; tested with Python `re` on the same pattern). apply-edits refuses only a reply with no EDIT at all (`apply_edits.rs:420`).
    - `{NNNN#id}` and a claim's `#id` are tied to a page number (`registry/src/items.rs:95`; `claims/item_labels.rs`), so moving a tagged item fails loudly.
    - `modals::followed` goes only one hop (`owed/src/record/modals.rs:213`) (inferred).
    - Mode A tells the cache only the Entry: and Drawing: pages (`mode_a/src/page/explain.rs:87-100`), so a reference to a question listed in neither goes stale (inferred to be rare).
13. **Already filed.** The pop-up fingerprint hashes raw page text, tags included (`modals.rs:514`, `page_words`). So tagging owes a triage run, though the tool clears it with no agent. This is T192's "strip item tags from ... page_words".
14. **Rules not yet tested on a real case:**
    - T187 a synthetic page; T189 none yet, its `seen/` store starts empty (inferred); T190 three replayed put-backs; T193 one fixture.
    - Items 4 to 7 would surface on the next split, as T194 did.
