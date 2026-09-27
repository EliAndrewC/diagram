# Brief - feature 250, T23: the map modals still owed an `entry-drift` on `buildings`, group 6 of 10

You are a FRESH session with one job: check the map modals below against the research questions they were written
from, and bring each back in step. Work in this clone (`/diagram/.clones/diagram-research-1`); the project's CLAUDE.md files still apply to you.
Read narrowly - you need no question's whole text; the agents read the bundles.

**Measure.** Before each numbered step: `python3 specs/250-close-the-record-checks/measure/tokens.py mark "owed buildings 6 <step>" --marks specs/250-close-the-record-checks/measure/marks-owed-buildings.json`

**Your pairs** (a modal and ONE question it is owed from - a modal owed from two questions is two pairs, each
checked and recorded on its own): KIND=Cell (SECTION=040), KIND=Cell (SECTION=100), KIND=HearingCourt (SECTION=090), KIND=HearingCourt (SECTION=100), KIND=HearingCourt (SECTION=190), KIND=SideGate (SECTION=120), KIND=SideGate (SECTION=220), KIND=Well (SECTION=230)

1. **Check, all in one message, in the background.** For each PAIR:
   `make check-bundle PAGE=buildings SECTION=<its NNN> NO_QUOTES=1 FOR=entry-drift KIND=<its class> OUT=/tmp/l7r-check/owed-<class>-<NNN>` (in
   `.claude/skills/diagram`) and one `entry-drift` naming its MANIFEST.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>`; the refused
   blocks and any `EDIT: none` finding by hand, all in ONE message of parallel `Edit` calls.
3. **Re-check ONCE, only what moved**: one `entry-drift` on each rewritten modal's bundle again; a drift left after it
   is labeled honestly in the modal's `Note:`, not checked a third time.
4. **Record the verdicts.** Append one line per PAIR to `specs/250-close-the-record-checks/owed-verdicts.md`:
   `- <class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. A modal found
   IN-STEP stays on `_entry_owed.py`'s list (only a rewrite clears it), and the push discharges exactly those lines;
   a CANNOT-TELL is NOT discharged - say what the agent needed, and the closing session answers it before the push.
5. In `.claude/skills/diagram`: `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py"`;
   commit naming your modals. Do NOT tick, do NOT push. Report in one paragraph: each modal's verdict.
