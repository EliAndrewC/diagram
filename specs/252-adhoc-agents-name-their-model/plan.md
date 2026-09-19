# Plan - 252 an ad-hoc agent dispatch names its model, or is refused

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## Constitution Check

- **XVI**: spec FAITHFUL at round 1 before the guard is wired; this plan reviewed (MODE 4) before any tick.
- **XVIII**: the guard ships with `scripts/test-agent-model-hooks.sh`; `make hooks-test` runs it.
- **Guard files**: the hook, its suite and `.claude/settings.json` are guard files; every edit carries
  `GUARD_EDIT_OK` with a reason (in the settings file, as a trailing `#` comment on the command, the form the
  file already uses).
- **Route**: `scripts/`, `.claude/settings.json`, `tests/tooling/`, docs -> DIRECT.

## Design

- **P1 the hook** (`scripts/agent-model-hooks.sh pretool`, bash with one python block to read the payload, the
  shape of `review-round-hooks.sh`): fields are tool name, `subagent_type` (an omitted one is
  `general-purpose`), `model`, `cwd`, joined with a UNIT SEPARATOR rather than a tab, because `read` collapses
  whitespace separators and the model is usually empty. Order of tests: not `Agent` -> exit 0 silently; `fork`
  -> `permitted`/`fork-inherits`; a non-empty model -> `permitted`/`model-named` (the model in the detail); an
  agent file `<root>/.claude/agents/<type>.md` -> `permitted`/`pinned-type`, where root is
  `clone-sync-hooks.sh resolve`'s clone, else the git top level of the payload's cwd, else the repository the
  hook lives in; otherwise `blocked`/`no-model`, exit 2. A payload that is not JSON never blocks.
- **P2 the message**: a bold first line naming the type and the SESSION's model, then the body READ from
  `scripts/agent-model-rule.txt` (the rule stated once), then the script's name and the feature. The suite
  asserts root `CLAUDE.md` carries the same two clauses, so the doc and the message cannot drift silently.
- **P3 the suite**: a fixture repository with one agent file; the refusals (general-purpose, omitted type,
  `Explore`, an empty model), the passes (a named model, `fable` named, a pinned type, a fork, a Bash call, a
  broken payload), each branch's log record, the message's content, the unknown mode.
- **P4 wiring and the record**: `.claude/settings.json` gains the hook in the `Agent` matcher's list, FIRST, so a
  refused dispatch is refused before the pair, escalation and review-round guards do their work on it; the
  firing-log test gains a payload row for the new guard; root `CLAUDE.md`'s table and `docs/guards.md` gain its
  row; `docs/make-targets.html` is untouched (no new target).

## Order

T01 the hook, the rule file, the suite -> T02 wiring, the firing-log row, the record -> T03 `make hooks-test`,
`make quick`, prove it fires by deleting the refusal branch, land.
