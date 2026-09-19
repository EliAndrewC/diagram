# Feature 251 - subagent checks tiered by model and effort, with the mechanical parts in scripts

**Status:** implemented 2026-09-19 - FAITHFUL at round 2, plan CLEAR on its second review; amended by the
GM's instructions of the same day (see Review history).

## Summary

The GM's ruling of 2026-09-07 put every subagent check on Opus. On 2026-09-19 (`request.md`) the GM
asked whether the checks could cost fewer tokens "without a loss of quality with different levels of
models involved", approved a per-agent tiering by model and by reasoning effort, asked for "the split
for the quote check, and indeed to split out anything that can be split out into a smaller model", and
asked for the whole to be implemented. This feature does that, in the order the proposal gave: measure
first (a token census), move what is mechanical into scripts, set each agent's model and effort, route
later `spec-fidelity` rounds to a medium-effort twin, and prove each downgraded agent against artifacts
with known findings before the downgrade stands. The GM's two standing conditions are kept: judgment
stays on Opus, and no check ever inherits the session's model (the reason for the 2026-09-07 ruling, and
the way scarce Fable usage would leak into a check).

Nothing here is engine code, so the delta takes the DIRECT route.

## User scenarios

**US1 (P1) - the GM sees where the tokens go.** `make agent-census` prints, per agent type, the run
count, the turns, the fresh input, the cached input, the output and the thinking tokens, and the model
each run ACTUALLY used, from the session transcripts. *Independent test:* run it; the table is in
`research.md` R1 with the date it was taken.

**US2 (P1) - a research entry's quotations are checked exactly, by no model.** `make quote-verbatim
PAGE=<name>` fetches each cited page once and reports per footnote whether the quoted passage is on it
character for character. *Independent test:* a fixture page quoted with a hyphen where the source has an
em-dash reports DIFFERS and shows the source's text; the same passage quoted exactly reports VERBATIM.

**US3 (P1) - every check runs on the tier the GM approved, and none inherits.** Each agent file pins a
model and an effort; the gate fails on a file that pins neither, pins `inherit`, or disagrees with the
recorded tier table. *Independent test:* delete one `effort:` line and watch the test go red.

**US4 (P2) - a downgrade is proven, not assumed.** For each agent whose model or effort went DOWN, the
new tier is run on artifacts whose findings are already known and the hits and false alarms are counted
against the recorded Opus result. An agent that misses a finding the recorded result caught goes back
up - to Opus when its model was lowered, one effort step when only its effort was (FR-011) - and the
spec records it. *Independent test:* `research.md` R5 holds one row per
downgraded agent per artifact.

**US5 (P2) - a later `spec-fidelity` round runs at medium effort without the session choosing it.** The
hook that already rewrites a later round into MODE 3 also routes it to `spec-fidelity-verify`.

### Edge cases

- A cited page is a PDF, refuses the fetch, or is in an encoding the script cannot decode: the footnote
  is reported NOT-CHECKED with the reason and handed to the `quote-check` agent, which keeps its fetch
  tools for exactly that residue. Nothing the old agent checked goes unchecked.
- A translated quotation (feature 202): the script checks the ORIGINAL against the page; the translation
  against the original is judgment and stays with the agent.
- An absence note or a grounds note has nothing to fetch: the script classifies it and checks nothing;
  the agent still judges whether a grounds note is dressing a physical claim.
- A later `spec-fidelity` round with no snapshot (the hook's `history-without-snapshot` branch) is not
  rewritten today and is not routed; the session dispatches `spec-fidelity-verify` by hand, and the
  hook's message says so.
- A session dispatches an ad-hoc agent (`general-purpose`) with no `model`: it would inherit the
  session's model. FR-010 states the rule against it and measures how often it happened.
- A session dispatches `spec-fidelity-verify` BY HAND: the round guard treats it as a round of the same
  review - it takes and refreshes the snapshot and counts the round - so the round after it still has
  something to diff against (FR-008).

## Functional requirements

**FR-001 - the census.** `scripts/_agent_census.py`, run as `make agent-census` (`SINCE=YYYY-MM-DD`
optional), reads every subagent transcript under `~/.claude/projects/` whose project is this repository
or one of its clones (`*/subagents/agent-*.jsonl` with its `.meta.json`), and prints one row per agent
type: runs, assistant turns, fresh input (uncached plus cache-creation), cached input, output, thinking,
and the models the runs actually used as recorded on the assistant messages (the dispatch's `model`
field is an override and is absent on most runs, so it is not the source). Usage is taken ONCE per
assistant message id, as the largest figure recorded for it, because a streamed message is written
several times with a growing count. The first run is recorded in `research.md` R1 and
`measurements.json` with its date; it is the baseline a later session compares per-run means against.
Task zero: it runs before any tier is changed, and its result may reorder the work - R1 says whether it
did.

**FR-002 - the tier table is one recorded thing, and the gate holds every agent file to it.**
`tests/test_agent_models.py` replaces `test_every_agent_pins_opus` with a per-agent table of `(model,
effort)` and asserts, deriving the roster from the directory: every agent file carries `model:` and
`effort:`; the model is `opus` or `sonnet`, never `inherit`, never absent, never `fable`; the effort is
one of `low`, `medium`, `high`, `xhigh`, `max`; both equal the table's entry; and an agent file with no
entry fails, so a new agent owes its tier the day it lands. The table:

| agent | model | effort |
|---|---|---|
| `record-format` | opus | high |
| `source-reader` | opus | high |
| `quote-check` | opus | medium |
| `entry-drift` | opus | medium |
| `escalation-check` | opus | medium |
| `spec-fidelity-verify` | opus | high |
| `spec-fidelity` | opus | high |
| `source-applicability` | opus | high |
| `size-audit` | opus | high |
| `building-review` | opus | high |
| `settlement-review` | opus | high |
| `perf-audit` | opus | high |

A row changed by FR-011's result is changed in the table, in the file and in this spec together. THREE
WERE (2026-09-19, `research.md` R5): the proposal had `record-format` on sonnet / medium, `source-reader` on
sonnet / high and the twin at medium; each missed a finding a recorded Opus run had caught and went back
up. The table above is what landed.

**FR-003 - the verbatim check is a script.** `scripts/_quote_verbatim.py`, run as `make quote-verbatim
PAGE=<name>` (`cities/<name>` for a city page), reads the research page and its citations page and
writes a report (text on stdout, JSON beside the feature or to `OUT=`) with one entry per footnote: its
id, key, link, the quoted passage, the original when the quote is a marked translation, the ASSERTION it
is attached to (the sentence carrying the `<sup class="fn">`), and its class - citation, absence note or
grounds note. For each distinct link of a citation it fetches the page once - one attempt per host, a
bounded timeout, a refused host recorded and never retried, the page's declared or sniffed encoding
honored (Shift_JIS pages read correctly) - strips the markup to visible text, and gives the quotation
verdict by EXACT substring match after collapsing whitespace and removing only the quotation marks that
delimit the passage: `VERBATIM`; `DIFFERS`, with the closest passage on the page and the differing
characters shown; `NOT-ON-PAGE`; `UNFETCHABLE` with how; or `NOT-CHECKED` with why (a PDF, an
undecodable page). No other normalization: a hyphen for a dash or an American spelling for a British one
IS a difference (GM 2026-09-06). Readability: a citation whose passage was found on a page fetched with
no credentials is `READABLE`; one whose link is this project's own registry, or whose page was fetched
and does not carry the passage, is `NOT-READABLE` with which; an unfetchable or not-checked one is left
to the agent. The script decides nothing about support and never edits.

**FR-004 - `quote-check` judges what is left.** The agent's contract is rewritten around the script's
report, which the dispatching session runs first and names in the prompt: it takes each footnote's
quotation and readability verdicts from the report as given, fetches only the NOT-CHECKED and
UNFETCHABLE residue itself, and judges Support, the faithfulness of a translation against its original,
a grounds note carrying a physical claim, and the unfootnoted assertions per section. Its output format
is unchanged, so every consumer of a quote-check report reads it as before. `research/CLAUDE.md`, the
root `CLAUDE.md` and `docs/research-doctrine.md` say the script runs first. Model and effort per FR-002.

**FR-005 - `record-format` gets a pre-pass.** `scripts/_record_prepass.py`, run as `make record-prepass
PAGE=<name>`, works on the page's VISIBLE text (comments and tags removed) and lists per section, with
the sentence: the session-note patterns a regular expression can find (a `Grounds:` or `Evidence:`
field, a feature number, a task id, a `specs/` path, a make target, a script or module path, an engine
identifier in code markup, a fetch verdict word) and the vocabulary CANDIDATES (a run of CJK characters,
an italicized or romanized term, a Latin binomial) that no glossary term or variant covers. The agent is
handed the list, confirms or dismisses each candidate, and still reads the page for what a pattern
cannot find - history passages, instructions to a future session, vocabulary in plain English. Its
output format is unchanged. Model and effort per FR-002.

**FR-006 - `size-audit` is handed the feet.** `scripts/_size_table.py`, run as `make size-table
PLAN=<pool svg>`, lists every rect, every gap between collinear wall segments and every stroke width in
the plan, each converted at 3 px = 1 ft and labeled with the nearest text label, as a table. The agent's
Method step 1 starts from the table and checks it against the sheet rather than building it; anchors,
ratios, the proportion sweep and the packing sweep are unchanged and remain its own.

**FR-007 - the remaining tiers are set in the files.** `source-reader` moves to Sonnet at high effort;
`entry-drift` and `escalation-check` stay on Opus at medium; `source-applicability`, `size-audit`,
`building-review`, `settlement-review`, `perf-audit` and `spec-fidelity` stay on Opus at high. Each
agent file's description and body say its tier and the one-line reason, replacing "on Opus like every
subagent check"; `source-reader`'s "Model" section is rewritten to the present ruling with no account of
the earlier ones.

**FR-008 - later `spec-fidelity` rounds go to a medium-effort twin.** A new agent file,
`.claude/agents/spec-fidelity-verify.md` (Opus, medium, the same tools), carries MODE 3, the FIGURES
rule, the round-limit note and "What you do NOT do" - and nothing of MODES 1, 2 and 4. Its instructions
stay strictly about the previous verdict's items and the diff. `scripts/review-round-hooks.sh`, on the
branch where it rewrites a dispatch into MODE 3, also sets `subagent_type` to `spec-fidelity-verify` in
the `updatedInput` it returns, and its `history-without-snapshot` message names the twin. The guard
fires on a dispatch of EITHER type: a hand dispatch of the twin gets the same preamble, snapshot and
round count, and is not re-routed. `spec-fidelity`
keeps its MODE 3 section as a pointer to the twin. Every place that recognizes a `spec-fidelity`
dispatch or verdict recognizes the twin's as the same review: the list is ENUMERATED in `plan.md` from
a grep of the agent's name over `scripts/`, the Makefiles, `.claude/settings.json` and the tests (the
review gate, the plan gate, the round counter, the prerequisite check, the escalation and pair guards,
`spec-lint.py`, the standing authorization in `container-scripts/append-system-prompt.md`), and each is
either changed or recorded as not keyed on the type, with a test for each one changed.

**FR-009 - splits that were declined stay declined.** No translation-only checker, no lighter
`perf-audit`, no `entry-drift` split, no medium-effort `settlement-review` for delta runs (the proposal
deferred that one to a later measurement; R1's per-run figures for `settlement-review` are recorded so
that measurement has a baseline).

**FR-010 - an ad-hoc agent never inherits.** The rule, in the root `CLAUDE.md` where "Every subagent
runs on Opus" now stands: a named check runs on the tier its file pins; an ad-hoc agent is dispatched
with an explicit `model` - `sonnet` for reading, fetching, translating and extracting, `opus` for
anything that judges - and never with none. R1 records how many past ad-hoc runs inherited, and on
which model. This feature states the rule and takes the measurement; it builds no guard for it
(`spec-fidelity` round 1: a guard was in neither proposal). Whether a hook should fill a missing model
is put to the GM with R1's count once the feature works.

**FR-011 - the seeded-fault test gates each downgrade.** The downgraded agents are `record-format`
(model and effort), `source-reader` (model), `quote-check`, `entry-drift`, `escalation-check` (effort,
from the unset default) and `spec-fidelity-verify` (effort). For each, `research.md` R5 names at least
two artifacts with KNOWN findings - taken at the commit before the fix, from `git`, or from a recorded
report (the feature 232 entry-drift pairs; the feature 242 handoff reports for `record-format` and
`quote-check`; past CONTRADICTED verdicts for `source-reader`; a recorded later round for the twin; a
recorded escalation draft) - and at least one artifact known CLEAN. The new tier is run on each, one
artifact per agent, in the background. Per run R5 records: findings the recorded result had, findings
hit, findings missed, new findings and whether each is real or a false alarm, and the run's tokens
beside the agent's recorded per-run mean. The rule: a MISS of a finding the recorded result caught
returns a MODEL-downgraded agent (`record-format`, `source-reader`) to Opus at the effort it ran at
before, and returns an EFFORT-only downgrade (`quote-check`, `entry-drift`, `escalation-check`,
`spec-fidelity-verify`) one effort step up; in either case the run is repeated at the new tier, and the
table, the agent file and FR-002 change together. A false alarm does not fail the agent; more false
alarms than the recorded result had is recorded as a cost. The agents pinned to Opus at `high` are not
downgraded and owe no test: an agent file with no `effort:` runs at the SESSION's effort (Assumptions),
the configured session effort is `high`, so `high` is what they ran at, now pinned rather than
inherited.

**FR-012 - the record says what is now true.** The root `CLAUDE.md` (the review-subagents bullet and the
gate row naming `test_agent_models.py`), `docs/spec-kit-and-reviews.md`, `docs/research-doctrine.md`,
`docs/guards.md` (the review-round guard's row, which now routes), `docs/efficiency-tooling.md` (the census and the three scripts),
`research/CLAUDE.md`, `container-scripts/append-system-prompt.md` (the twin joins the authorized list),
and the session memory `feedback_subagent_checks_on_opus.md` are updated to the tiering, each stating
the present rule only. Every new script has a test companion run by `make hooks-test` or `make quick`,
and every new make target is listed where the others are.

## Key entities

- **Tier table** - agent -> (model, effort); lives in `tests/test_agent_models.py`, mirrored in each
  agent file's frontmatter and in FR-002.
- **Verbatim report** - per footnote: id, key, link, passage, original, assertion, class, quotation
  verdict, readability verdict; the hand-off from script to agent.
- **Census row** - agent type, runs, turns, token columns, actual models, date taken.

## Success criteria

- **SC-001** The census table exists in `research.md` with its date, and accounts for every agent type
  the transcripts hold.
- **SC-002** On the verbatim fixtures, the script's verdicts are exact: every seeded character
  difference is reported DIFFERS and no exact quotation is.
- **SC-003** No agent file inherits or omits a model or an effort, and the gate proves it.
- **SC-004** Every downgraded agent has an R5 row set, and each either missed nothing the recorded
  result caught or was stepped back up and re-run.
- **SC-005** R5 states, per downgraded agent, tokens per seeded run against the recorded per-run mean -
  the first measurement of what the tiering saves.
- **SC-006** `make hooks-test` and `make quick` are green; nothing under `l7r/` or `pool/` changed.

## Assumptions

- `effort:` is a supported frontmatter key for a subagent file in the installed Claude Code (verified
  2026-09-19 in the 2.1.278 binary: the agent-definition schema carries `effort` with the five levels,
  and the changelog names "`effort:` frontmatter on custom commands, skills, and subagents").
- An agent file with no `effort:` runs at the session's effort (verified 2026-09-19 in the same binary:
  the subagent's effort is read as the definition's value, else the session's layered effort), and the
  configured session effort is `high` (`~/.claude/settings.json`, `effortLevel`). A session whose effort
  was raised by hand ran its checks higher; the transcripts do not record it, so it is not claimed.
- A hook's `updatedInput` may change `subagent_type` as it may change `prompt`; `plan.md` verifies this
  before FR-008 relies on it, and if it cannot, the hook instead prepends the instruction and the
  session re-dispatches - recorded as the fallback, raised with the GM after.
- The seeded runs cost tokens once; the GM approved "test before trusting" as the acceptance.
- The container can fetch public pages from a script as `curl` does today.

## Review history

- **Round 1 (2026-09-19) - CHANGES REQUIRED, three items, all applied.** (1) FR-010's guard was
  unrequested: the rule and the measurement stay, the hook is dropped and goes to the GM as a question
  once the feature works. (2) FR-011's "one step back" left a Sonnet agent that missed on Sonnet: a
  model downgrade that misses now returns to Opus; an effort-only downgrade goes one step up; US4
  aligned. (3) The exemption for the Opus-high agents rested on an unstated default: established (an
  unset effort is the session's, configured `high`) and stated in Assumptions. The reviewer's aside -
  a hand dispatch of the twin took no snapshot - is now in FR-008 and the edge cases.
- **Round 2 (2026-09-19) - FAITHFUL.** All three items and the aside verified resolved; nothing new
  introduced. The reviewer's aside for the plan: the session model is Fable, so R1 reports which past
  ad-hoc runs inherited Fable specifically.
- **Amendments by the GM's instruction, 2026-09-19, after acceptance** (their words are in `request.md`,
  messages four and five). (1) The seeded runs were CUT DOWN - slices of the large recorded runs, seventeen
  small runs in all - where FR-011 had said "at least two artifacts ... and at least one known CLEAN" per
  agent with no bound on their size; `quote-check` got no separate clean page (the no-finding notes inside
  its slice serve), because the page chosen cites only the GM's canon. (2) FR-011's "the run is repeated at
  the new tier" was NOT done for the three agents that missed: the GM asked to land the tiers that passed
  and to choose the further experiments together, so each returned to its known-good tier, for which the
  recorded runs are the result. (3) FR-007's Sonnet tiers and the twin's medium did not survive FR-011, as
  FR-002 now shows.
