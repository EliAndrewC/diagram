# Research: The effort-level experiment (feature 293)

Phase 0 of the plan. Every item is `research: rendering`-free tooling research: how Claude Code and this repository behave,
read from the docs and the code, with what the implementing session must still MEASURE marked as such.

## R1 - How is an ad-hoc subagent's effort set? (spec US2 AS3, FR-005)

**Found** (a `claude-code-guide` read of the Claude Code docs, 2026-09-29, quoting
<https://code.claude.com/docs/en/sub-agents> "Supported frontmatter fields"): `effort` - "Effort level when this subagent is
active. Overrides the session effort level. Default: inherits from session." A definition with no `effort` - which is every
ad-hoc dispatch here (`general-purpose`, `claude`, `Explore`, `Plan`) - therefore runs at the SESSION's effort: an ad-hoc judging
agent in the `xhigh` arm judges at `xhigh`, in the `medium` arm at `medium`. Left alone, that is exactly the confound the
handoff's "pin the effort of the checker/reviewer subagents" exists to remove.

The Agent tool documents a per-dispatch `model` and no per-dispatch `effort`; the statusline page mentions an effort "set ... on
the individual invocation", undocumented elsewhere. `CLAUDE_CODE_EFFORT_LEVEL` beats both `--effort` and frontmatter effort
(<https://code.claude.com/docs/en/model-config>), so it would force one level on every subagent - the defined checkers included.

**Decisions**:

- **D1 - the arm is set with `--effort` and NEVER with `CLAUDE_CODE_EFFORT_LEVEL`.** The environment variable would override the
  checkers' pinned frontmatter effort and break the control the spec most depends on. The launcher unsets it in the run's
  environment and records that it did.
- **D2 - ad-hoc judging goes to one session-scoped judge pinned by definition.** Every SESSION of every run - task I's one session
  and task R's write and check-and-apply page sessions alike (the page sessions have the `Agent` tool and `page-session-rules.md`
  lets them dispatch ad-hoc `opus` judges) - is launched with the same `--agents` JSON defining `adhoc-judge` (model `opus`, `effort: high` - the tier of the defined judging checkers, eight of twelve), and the
  byte-identical prompt (and both R briefs) tells the run to dispatch any ad-hoc work that checks or judges to `adhoc-judge`, and ad-hoc reading,
  fetching, translating or extracting as it normally would. The instruction names no effort level and is identical across arms.
  Frontmatter effort overrides the session's (the docs above), so `adhoc-judge` runs at `high` in both arms. The run record carries the
  JSON's hash per session, and the launcher refuses a session whose hash differs.
- **D2a - the fallback is an agent FILE, not the unmet branch.** If P0 (a) shows `--agents` cannot carry the effort in `claude -p`, an
  agent file `.claude/agents/adhoc-judge.md` (`model: opus`, `effort: high`, `omitClaudeMd: true`), registered in `test_agent_models.py`'s
  tier table, lands on main BEFORE `START`, so every run clone has it identically by construction; it is retired after the report. The
  spec's unmet branch (US2 AS3) is used only if that too is measured not to pin the effort.
- **D3 - what the run did anyway is counted and listed.** `effort-measure` counts, per arm, the ad-hoc dispatches that were NOT to a
  defined agent or `adhoc-judge`, split by the model named, and LISTS every one with its description, so the report's reader can check
  the classification (a judging dispatch sent on `sonnet` would otherwise slip past a model-only rule); any on `opus`, or any the list
  shows judging, (the project's rule: opus "for anything that judges") is reported
  as an ad-hoc judging dispatch at the session effort - the control unmet for that many dispatches (spec US2 AS3's measured branch).
- **MEASURE FIRST (P0)**: (a) that a `--agents` agent with `effort` in `claude -p` is dispatchable and its transcript's meta or
  records show the effort or at least the model; (b) whether a subagent transcript or `meta.json` records effort at all; (c)
  whether the Agent tool accepts an `effort` input (the statusline hint). If (c) works it is recorded and NOT used - the prompt stays
  as D2, since steering the run's dispatch shape by effort would differ by arm. If (a) fails, apply D2a (the agent file) and re-measure; the spec's measured branch (ad-hoc judging counted per arm, the control
  listed as unmet) applies only if that too fails.

**P0 MEASURED (T07, observed 2026-09-29, one-shot, method: one `claude -p --effort medium --agents <the launcher's JSON>` session in
a scratch directory, `CLAUDE_CODE_EFFORT_LEVEL` unset, told to dispatch `adhoc-judge` and to list the Agent tool's parameters; cost
$0.15):**
- (a) `--agents` carries the pinned judge in `claude -p`: the dispatch ran, `meta.json` names `agentType: adhoc-judge`. **D2 is in
  force; D2a's agent file is not needed.**
- (b) Effort IS recorded: every assistant record carries an `effort` field (and `perTurnEffort`). The session's records read
  `medium`; the judge's read `high` - the frontmatter pin beat the session's level, as the docs say. So `effort-measure` counts each
  run's efforts per message for the main sessions and per subagent type: the arm and every checker's tier are MEASURED from the
  transcripts, and a mismatch is visible in the report rather than assumed away.
- (c) The Agent tool offers `description`, `isolation`, `model`, `prompt`, `run_in_background`, `subagent_type` - no per-dispatch
  `effort`. Nothing to record or avoid.
- (d) Under an `xhigh` session the pin holds too (observed 2026-09-29, one-shot, method: the same probe with `--effort xhigh`, cost
  $0.12): the session's records read `xhigh`, the judge's `high`.

**Alternatives priced**: a hook in the run clones rewriting ad-hoc opus dispatches - rejected, it changes the guard set between the
experiment and normal work; a committed agent file - the FALLBACK (D2a), not the first choice only because `--agents` needs no landing
and no retirement.

## R2 - Where do a run's transcripts live?

`~/.claude/projects/<mangled cwd>/<session-id>.jsonl` per session and `~/.claude/projects/<mangled cwd>/<session-id>/subagents/agent-<id>.jsonl`
with `agent-<id>.meta.json` naming the agent type (`scripts/_agent_census.py` docstring; `ls` of `~/.claude/projects/-diagram/`,
2026-09-29). The mangled cwd is the clone path with `/` and `.` replaced by `-` (`page-session.sh`). The launcher chooses every
session id (`--session-id`, as `_page_session_runner.py` already does) so the run record names each transcript before it starts.

## R3 - How is usage counted?

As `_agent_census.py` does and for the reason its docstring gives (its research R2): a transcript holds one record per content block,
each repeating the message id and its usage as it stood, so usage is folded per message id as the per-field MAXIMUM. `effort-measure`
imports that fold rather than re-deriving it. Fields: `input_tokens`, `output_tokens`, `cache_read_input_tokens`,
`cache_creation_input_tokens`. The `claude -p --output-format json` result (`result.json`, written by the runner) also carries usage
and cost per session; it is recorded beside the transcript sum as a cross-check, and a disagreement over two percent (a GUESS threshold, no measured basis) is reported.

**Usage-limit share**: not observable from inside a `-p` session (no documented field). The report says "unobserved" unless the GM
reads the account's usage page before and after each run, which the quickstart offers and does not require.

## R4 - Where is each rework signal recorded? (FR-007)

| signal | source | how it is tied to a run |
|---|---|---|
| guard firings (refusal / correction / escape / reminder) | `~/.claude/guard-log/*.json`, one file per firing, with `session`, `cwd`, `guard`, `event`, `rule` | `session` in the run's session ids, or `cwd` under the run clone |
| check and review verdicts | the subagent transcripts: the last assistant text of each `quote-check`, `record-format`, `source-reader`, `source-applicability`, `entry-drift`, `settlement-review`, `spec-fidelity*`, `escalation-check` run | the run's subagent directories |
| review rounds | the count of dispatches per (agent type, subject) | same |
| failed test / gate runs before the last green | `Bash` tool results in the session transcripts whose command runs `make quick\|done\|test-file` and whose output reports a failure | the run's session transcripts |
| fix / revert commits | `git log <start>..HEAD` in the run clone, subjects matching the project's own words (`fix`, `revert`, `round-N changes`) | the run clone |
| escalations | `escalation-check` dispatches, and any turn that ends asking the GM (the `-p` result's final text ends in a question) | transcripts, `result.json` |

Each is a count, derived by the script; nothing is counted by hand (SC-001). Where a pattern is a heuristic (the failing-run match, the
fix-commit match) the measurement lists the matched lines so the report's reader can check them.

## R5 - Memory and sequencing

Containers share a 9 GB cap; memwatch warns at 8 GB (the handoff). A `make done` alone reaches ~3.2 GiB at its test-phase peak (observed 2026-09-13, one-shot, method: the gate RAM profile; memory
note of 2026-09-13). **D7 - strictly sequential, gated on headroom** (the GM, 2026-09-29: "run these tests sequentially rather than in parallel for memory
reasons"). The launcher refuses to start a run while any other effort run's session is live (its record has a start and no
`result.json`), and refuses while the container's WORKING SET, plus the OFFSET measured below, is above **4.5 GB**. The working set is `memory.current` less `inactive_file` from
`/sys/fs/cgroup/memory.stat` - the memory the kernel cannot simply drop, the figure container tools report as usage. The raw
`memory.current` is NOT the gate: it counts page cache, and read 9.23 GB against memwatch's 8.3 GB for the same minute (observed
2026-09-29 19:41 UTC, one-shot, method: the amendment review's `cat` of `memory.current` and `grep` of `memory.stat`, 2.40 GB of it
page cache) - a gate on it could stay shut on a quiet host. Nor is this cgroup's own limit the cap: `memory.max` is 10 GiB, while the
9.0 GB cap is the shared one memwatch reports. At 19:43 UTC the working set read 6.98 GB against a `memory.current` of 7.90 GB
(observed 2026-09-29, one-shot, method: `memory.current` less `inactive_file`). The launcher also refuses while a memwatch warning newer than 15 minutes (a GUESS: long enough that a warning raised by the previous run's tail or another session's gate has passed, short enough not to stall the experiment for an old one) stands in
`~/.claude/memwatch/events/`. The threshold is a GUESS with its arithmetic: the 9.0 GB cap less a run's own peak (a `make done`'s
test phase, above, plus the run's session and its subagents' processes at about 0.5 GB each - observed 2026-09-29, one-shot, method: the memwatch warning of 15:34 listing the four biggest processes) leaves roughly
4.5 GB for everything else. A run's peak is on the same footing: a run's peak is anonymous memory (the gate's
test workers and the `claude` processes), which the working set counts and page cache does not add to. The threshold is on memwatch's scale - the 9.0 GB cap is the
figure memwatch reports - and memwatch's figure cannot be read by the launcher: memwatch publishes a figure only inside a warning, when
the containers pass 8 GB (`~/.claude/hooks/memwatch-hook.sh`; its `latest` file holds an event number and a time). So the gate converts
the working set to memwatch's scale with an OFFSET measured at the minute of a warning, where both figures exist: at 19:41 UTC memwatch
reported diagram at 8.3 GB while the working set was about 7.4 GB (9.23 GB `memory.current` less 1.81 GB `inactive_file` - the
same subtraction the gate makes, not the whole 2.40 GB of page cache; observed 2026-09-29, one-shot,
method: the memwatch event of 15:41 local and the amendment review's `memory.stat` reading), an offset of **0.9 GB**. The gate is
therefore working set + 0.9 GB <= 4.5 GB. In pre-flight (T09) the offset is re-measured at the next memwatch warning that falls in a
working session (the event's figure beside a working-set reading taken within its minute), and the larger of the two offsets is used; no
quiet-host memwatch figure is sought, since none is published. The working set alone IS readable on a quiet host, and T09 records it
there: if that quiet reading plus the offset is above the threshold, the gate could never open, so the implementing session raises it
with the GM before any run rather than changing the threshold on its own.
The refusal prints the figure and the wait is logged in `interventions.md`; the implementing session
retries on its next turn rather than polling. While a run is live the implementing session runs nothing memory-heavy of its own: the
measurement of the previous run, the blinding and the grading are done between runs, one at a time, and the tooling is built and gated
before the first run. Other sessions' work is the implementing session's to schedule around (the quickstart says to run when the host
is otherwise quiet); a memwatch warning DURING a run does not stop it, and is logged. A run that ends with exit 137 is marked void
by `effort-measure` from its `result.json`/`stderr.txt`, and re-launched with the same prompt and a new run id.

## R6 - Shared state a run reads or writes outside its clone

- **The sources-consulted ledger and page cache** (`<mirror>/.specify/`, host-wide, feature 288). `make source-pages` prints each page's
  EARLIER reads - so the second research run would see the first run's reads and outcomes. `_sources.home()` honors
  `L7R_SOURCES_HOME`. **D4**: before the first run, snapshot the ledger and cache once; each run gets its own copy under its run
  directory via `L7R_SOURCES_HOME`. Both arms therefore start from the same state and neither sees the other. The winner's new ledger
  lines are appended to the real ledger at landing.
- **The research claims file** (`/diagram/.clones/RESEARCH-CLAIMS.md`): a research run appends its claim; the next run would read the
  question as claimed. **D5**: the launcher appends a release line after each R run ends (`effort experiment run <id> ended - claim
  released`), which the page-session rules' reading of the file treats as the end of that claim. MEASURE in P0 that the rules read it
  so; if not, point the run at a per-run copy of the file by the same means as D4 (an env override added to the claims reader, tested).
  **T08, checked 2026-09-29:** the page-session rules (`container-scripts/page-session-rules.md`) say only HOW the file is read
  and written; what a claim blocks is the BRIEF's to say, and task R's write brief said "a section another feature holds" - which
  a second run could read as covering the first run's feature-293 lines. So the write brief now says plainly that "Effort
  experiment | 293" lines the run did not write are not claims on its work (identical in both arms). The release line stays, as a
  record; no per-run copy of the file is needed.
- **`make reserve`** allocates registry and glossary prefixes under a host-wide lock; both runs reserve, the loser's reservations are
  simply unused numbers. Accepted, no cost but a gap in numbering.
- **The guard log** is shared but per-firing and tagged with session and cwd (R4); nothing to isolate.
- **D6 - the run record lists the shared state.** Each run's record carries `shared_state`: the sources snapshot's hash at start, the claims file's sha256 at launch with the lines naming the run's question or open against it
  (under D5's per-run-copy path, the copy's hash),
  the ledger lines the run appended to its copy, the claims-file lines it wrote and the release line the launcher wrote, and the prefixes
  it reserved - what it found at start and what it left for a later run (spec US2 AS6, the shared-resource edge case).
- **`make claim`**: neither run claims a feature number (the prompts say the run is a task under feature 293); a run that tries is
  counted and the claim released.

## R7 - Task R as page sessions

The project runs a research page as two fresh headless sessions, write then check-and-apply, from briefs (`make page-session`). Task R's
"prompt" is therefore two briefs, `prompts/R-write.md` and `prompts/R-check.md`, byte-identical across arms, run by the existing runner
with `EFFORT=` (spec FR-003: every session the run starts at the arm effort). The write brief carries one question (the servants'
quarters), under the four-question cap. The check brief is the project's standard check-and-apply brief shape for that question.

## R8 - Feature 287 and task I

Feature 287 (placer guarantees) is open with tasks touching `hamletgen/burial.py` (T46) and the lane predicates (`ways/law.py`, T03).
Task I's runs start from a fixed commit and are unaffected while they run. The pre-flight (P0) re-reads the future-work entry at the start
commit and greps main for a burial-ground way; if 287 has landed one, the task is replaced after asking the GM (spec edge case). The
landing merge is the implementing session's, counted apart (spec US4 AS3).
