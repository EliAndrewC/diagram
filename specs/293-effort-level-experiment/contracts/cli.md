# Contracts: feature 293's commands and the grader

## `make page-session ... EFFORT=<level>`

The existing target gains `EFFORT` and `AGENTS` (a JSON file); when set, `--effort <level>` and `--agents <the file's JSON>` are appended
to every session the runner starts (after `--model`, if any). Unset, the command line is byte-identical to today's (tested).

## `make effort-run TASK=R|I RUN=<run-id> ARM=medium|xhigh COMMIT=<sha> [ORDER=<n> SEED=<s>]`

1. Refuses if another effort run is live (a run record with no `ended`), if the rubrics changed since their freeze commit, or if the prompt
   files differ from the hashes recorded for this task's earlier run.
2. `git clone /diagram /diagram/.clones/diagram-exp-<run-id>`, checks out `COMMIT` detached-free (a fresh `main` reset to it in the new
   clone), and copies the sources snapshot to `<clone>/.git/effort-sources/` (R6 D4).
3. Starts the run detached: task R through the page-session runner with the two briefs, `--effort <arm>` and the same `--agents` JSON; task I as one
   `claude -p <prompts/I.md> -n diagram-exp-<run-id> --session-id <uuid> --effort <arm> --permission-mode bypassPermissions
   --agents <json> --output-format json`, the appended system prompt the same as an interactive session's. `CLAUDE_CODE_EFFORT_LEVEL` is
   removed from the environment; `L7R_SOURCES_HOME` is set.
4. After a task R run ends, appends the claims release line (R6 D5). Writes `runs/<run-id>.json` (with `shared_state`, R6 D6) and prints the session ids, transcripts and log directories. Returns at once.

## `make effort-measure RUN=<run-id>`

Reads the run record; writes `measurements/<run-id>.json`; prints a one-screen summary (counts first). Marks the run `void` on exit 137.
Idempotent.

## `make effort-blind TASK=R|I SEED=<s>`

Exports each valid run's output for the task - R: the question's fragment, its `.notes.html`, and every new source and glossary file, as
files; I: `git diff <start>..HEAD` of the run clone, the moved maps' PNGs and `.notes.md`, and the run's final `make done` summary -
strips the run id, clone path, session names, commit trailers and any occurrence of the arm names, labels them A/B from the seed, writes
the bundle and `MANIFEST.md` outside the repository, and the key under `.git/effort-keys/`. Prints the bundle path only.

## Agent `effort-grader` (`.claude/agents/effort-grader.md`)

Frontmatter: `model: opus`, `effort: high`, `omitClaudeMd: true`, tools `Read, Grep`. Input: a bundle's `MANIFEST.md`. Contract: grade A and
B against the rubric in the bundle, criterion by criterion, 0-4 with the anchor quoted, then a preference and what it rests on, then how the
two differ (depth, correctness, missed items, a better approach). It must not read outside the bundle and must not guess which arm is which.
Reply: counts first (the two totals, the preference), then the per-criterion table. Registered in `test_agent_models.py`'s tier table.
