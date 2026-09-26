# Implementation Plan: close the record checks

Spec: [`spec.md`](spec.md) (accepted, FAITHFUL at round 3). Request: [`request.md`](request.md).
Inputs: `specs/242-cite-the-unfootnoted-assertions/HANDOFF.md` sections 4 to 8, its thirteen reports,
its `research.md` R12.

## Summary

The spec was accepted on 2026-09-14. Since then the record was split into per-entry fragments (feature
258), the glossary into per-term files (259), the checks were tiered and given script pre-passes (251,
255, 260) and the defined agents stopped loading the project's instruction files (256). None of that
changes WHAT this feature owes; all of it changes WHERE an edit lands and HOW a check is dispatched.
This plan maps the spec's requirements onto the record as it now stands, and takes the work in two
steps: a measured slice first, then the rest.

## Technical Context

- No engine Python. Edits land in `research/<page>/NNN-*.html`, the `.notes.html` beside each,
  `research/sources/010-works-cited/NNNN-<key>.html`, and the glossary's per-term files; `make record`,
  `make citations` and `make glossary` assemble. Route: DIRECT (spec D2).
- Measurement scripts live in `specs/250-close-the-record-checks/measure/`.
- The four record tests (`tests/interactive/test_footnotes.py`, `test_citations.py`, `test_sources.py`,
  `test_record_format.py`) after each page; `make page-check` at the close (SC-010).

## Performance bookends

None owed: no engine code, no map moves.

## Constitution Check

- XII (research): every FR-001 and FR-002 task is `research: physical` and carries the five boxes.
- XIII (no regressions): T01 records the baseline of the four record tests before any edit.
- XVI (the literal thing): D1 and D3 below are the two places this plan could be read as departing
  from the request; both go to `spec-fidelity` with the GM's words before a task is ticked.

## The design

### D1 - The spec's paths are read through the split; the spec's text stays as it is

The spec names `cities/sizing.html`, `SOURCES.html` and `glossary.json` as edit targets. Each is now an
ASSEMBLED file that is never hand-edited (features 258, 259). The requirement on each is unchanged and
is met on the assembled file; the EDIT lands in the fragment that assembles into it. The spec is not
amended for this: a spec records what was decided when (feature 260 D4 took the same position), and an
amendment would reset an accepted review over a change of address.

242's `measure/apply_notes.py` places notes by LINE into a whole page and writes footnote numbers; both
are gone. Notes are hand-placed per the per-entry rule: `<sup class="fn" data-note="<key>"></sup>` in
the fragment, `<li data-note="<key>">` in its `.notes.html`. 242's `measure/worklist.py` reads the
assembled page and still runs (measured 2026-09-21: `cities/sizing.html`, 6 items, FOOTNOTED 1,
LOCATED 5), so SC-001 and SC-006 are judged with it unchanged.

### D2 - A check is dispatched per ENTRY, with its pre-pass, never per page

FR-007 asks for `quote-check` and `record-format` "scoped to the changed notes and sections". After the
split that scope is a file: one agent per changed entry, handed `make quote-verbatim PAGE= SECTION=` or
`make record-prepass PAGE= SECTION=` output and the fragment paths. `source-applicability` is handed
the one registry file of each new key. `source-reader` is handed pages saved by `make source-pages`.
242 measured 340,000 to 720,000 tokens per check when each read two to four whole pages and the
registry (HANDOFF section 7); this is the change that measurement asked for.

### D3 - A measured slice first, then the GM reads the figures (GM 2026-09-21)

The GM, starting this feature: *"begin feature 250, but then only perform a few of its tasks, and then
measure the token usage for the different aspects of each task. For example, how many tokens are eaten
up by the main session, how many by each named subagent, how many by the ad hoc subagents, etc. by
measuring this, we can then check whether we need to make any more structural changes before we proceed
with the rest of the feature."*

So Phase 1 is a slice chosen to run as many of the agents the full feature will run as the smallest
real work allows, and Phase 2 onward waits for the GM. It cannot run all of them: `entry-drift` is owed
only at the close (FR-007), and `source-applicability` runs only if the slice adds or changes a registry
write-up. T10 names every agent the slice did NOT measure, so the figures are not read as complete. `measure/tokens.py` cuts the session into one
window per task (`mark`) and reports the main session, each named agent and each ad-hoc agent per
window, with what each agent read, largest first. The slice:

- **FR-001 whole** - `cities/sizing`: two entries, five bare items. Runs `source-reader`, the note
  writing, `source-applicability` on any new key, `quote-check` and `record-format` per entry.
- **FR-003 for one entry** - the vocabulary findings of one entry, with a `record-format` re-check. No
  reader; the contrast case (edits and one check).

The slice is real work and stays. It is not pushed: a feature with an open task lands nothing but its
`specs/` claim, so the record edits wait in the clone for the feature's close.

### D4 - FR-002's count is derived by a script over the reports

`measure/assertions.py` lists, per report, page and section, the bullets under each "assertions with no
footnote" listing. The listing has no one shape (the plan review measured it, 2026-09-21): five of the
six reports open it with a markdown heading, worded differently each time, and
`qc-fields-religion-archetypes.md` opens it three times mid-document with a plain bold line
(`Unfootnoted real-world assertions, by section:`, once per page) and no heading at all. The script is
written and was run on the six reports (2026-09-21), and this decision states what it does, which its
docstring carries beside the code:

- **The opener** is a LINE, heading or not, wherever it falls, carrying "assertion" and "footnote"
  (which "unfootnoted" contains), case-blind, that is NOT itself a bullet or a table row - a listing's
  own bullet (`hw-quotecheck.md` line 123) and the summary tables' count rows carry both words and
  would otherwise open a block.
- **The block ends** at the next horizontal rule or the next heading at the opener's level or above -
  never at a blank line, because `hw-quotecheck.md` puts one between every item.
- **An item** is a top-level bullet in the block, except one beginning "Skipped", "Nothing else" or
  "Other sections" - the reports' notes of what they passed over.
- **The page** comes from a deeper heading inside the block naming `<page>.html` (the fabric and
  river-cities reports), else the nearest bold line (`hw-quotecheck.md`), else the opener
  (`qc-buildings-vegetation.md`), else the nearest heading above it (`qc-fields-...`); the one report
  about a single page names it nowhere and is mapped by file name. **The section** comes from the
  nearest bold-only line above the item inside the block, else the item's own leading italic prefix,
  else a trailing `("...")`.
- **Two guards.** A report with no opener FAILS the run. Where a report's summary table states its own
  count the script compares and fails on a mismatch (one report states a bare total, measured equal;
  `qc-buildings-vegetation.md` states "7 (buildings) + 5 (vegetation)", which the script does not parse
  and which was compared by hand: equal).

Measured: every item the script returns carries both a page and a section - 0 without, over six
reports and fifteen pages, 72 items (the script's own last line prints all three). The task list names
no count; the closing report prints the script's.

### D5 - FR-006's items are found by their own words, grepped over the page's fragments

`worklist.py` prints a section label beside each item, and the label is NOT the record section the
sentence lives in: `section_of` returns the last `###` heading of the inventory REPORT above the item.
Measured by the plan review, 2026-09-21: on `cities/sizing` three of the six items carry a heading from
another page or the other entry, and on `fields` a NOT-LOCATED item carries an empty label and three
carry a heading no fragment of `research/fields/` has. So the label is a hint and nothing more. Each
NOT-LOCATED, TOO-SHORT or AMBIGUOUS item is found by grepping its distinctive words - a figure, a proper
noun, a term - over `research/<page>/*.html`, and the fragment the grep names is the one opened. An item
whose words no fragment carries is recorded as such, with the words tried, and is then searched by its
subject; it is never confirmed against a fragment the grep did not name.

### D6 - A record check reads a BUNDLE outside the repository (GM 2026-09-26)

The GM, on the measurement of D3 (research R1) and its three recommendations: *"Do not move tooling fixes
to another clone or make them a standalone fix. Just go ahead and make them as part of your work here. And
yes, I agree that all of those recommendations should be implemented. So please keep going and implement all
of them. And then after they are all implemented, we can move forward with testing them by resuming some of
the research itself to compare the token usage of the next subset of research tasks with the token usage
from the previous set of research tasks."*

R1 finding 2: an agent that reads a file under the repository is handed every `CLAUDE.md` above it, about
28,400 tokens under `research/`, which `omitClaudeMd` does not stop. So `make check-bundle PAGE= SECTION=`
(or `KEY=`) copies what one check reads - the fragment, its notes, the prepass, the quote-verbatim report,
the registry entries its notes cite, the variant index - to `/tmp/l7r-check/`, with a `MANIFEST.md` naming
each copy's origin. The contracts of `quote-check`, `record-format`, `source-applicability` and
`source-reader` read the bundle and nothing under `/diagram`; `check-bundle-hooks.sh` refuses a dispatch of
one of them that points into the repository and prints the command. `entry-drift` is left out: its input is
a modal's explanation in the engine's assets, and the slice did not measure it.

**Does a check still find what it found?** A check that loses the CLAUDE.md files loses nothing its contract
does not carry (feature 256's position), but that is a claim, and the tier rule measures it: seeded-fault runs,
THREE a leg. `record-format` and `quote-check`: one entry with planted faults, three runs in the tree and three
from its bundle, each leg judged on whether it names every planted fault. `source-applicability`: the recorded
case of the slice (`edo-enwiki` before its limit was added, where the in-tree run found the missing limit),
three runs from the bundle against that recorded verdict. Recorded as R2. A leg that loses a finding the other
catches is a regression, and the bundle is not adopted for that agent.

### D7 - One page per session, started fresh from a brief (GM 2026-09-26)

R1 finding 3: the main session was 87% of the input. `make page-session BRIEF=<file>` starts a headless
`claude -p` in this clone - named like it, so the hooks route it here; with the project's appended system
prompt; with a session id chosen in advance, so its transcript is known - detached, and returns at once. The
brief carries the page's items (derived: `measure/brief.py` reads `assertions.py` and `worklist.py`) and the
procedure (D2, D5, D6, D8), so the session does not read the spec and plan to orient. It commits and does not
push; the parent session does not edit the clone while it runs.

### D8 - A check's report goes to a file; its reply is one line

R1 finding 3: thirteen whole reports sat in the main session's context and were re-read on every later turn.
The four contracts D6 names gain the `Write` tool and one rule: the whole report goes to `REPORT.md` in the
bundle, the reply is one line of counts naming it. The report is opened when the line says there is something
to apply. The contract limits the one write to the bundle; no guard enforces it, because a hook cannot tell
an agent's write from the session's.

### D9 - The comparison (research R2)

The next subset is FR-002 and FR-006 for `homesteads`: five FR-002 items (the slice had five) and three FR-006
items, worked in one page session (D7) with bundled checks (D6, D8). Measured with `measure/tokens.py` over the
child session's transcript, and set against the slice (R1) three ways: the whole; per item closed; and per check
run, split into the floor an agent carries before it reads and what it read. The FR-006 items are their own
window, so the like-for-like figure can be taken without them. The seeded-fault runs (D6) are measured as their
own line and are not part of either side.

### D10 - The route is GATED, not DIRECT

Spec D2 expected no engine Python. The slice fixed `tools/record_asset.py` (constitution XIV), so the delta
carries engine code and the push takes the gated route on a green `make done`. The spec is not amended for
it: D2 recorded an expectation, and the route is chosen from the delta by `sync-with-main.sh`, never by a spec.

## Phases

0. Baseline and the meter (T01, T02).
1. **The measured slice** (T03 to T09), ending in the measurement report (T10). STOP for the GM - who ruled
   on 2026-09-26 (D6).
1b. **The token work** (T11 to T16): the fixes, the bundle and the guard (D6, D8), the page session (D7), the
   seeded-fault runs (D6), and the comparison (D9) - which is phase 2's first page.
2. FR-002 page by page, one page per session; FR-006 beside it, since both open the same fragments.
3. FR-003, FR-004, FR-005 (the cosmetic sweeps).
4. FR-007's owed checks over what phases 2 and 3 changed; FR-008; FR-009; the close.

## Complexity Tracking

Measurement scripts under `measure/`; one operation (`check-bundle`), one launcher (`page-session`) and one guard (`check-bundle-hooks.sh`), each the smallest form of a recommendation the GM adopted (D6-D8).
