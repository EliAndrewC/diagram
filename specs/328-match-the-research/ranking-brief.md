# Ranking audit (feature 328): estimate the implementation work per finding

You rank claims-index findings by how much IMPLEMENTATION work it takes to make the implementation match the research
the claim cites. You do not fix anything and you edit no file in the repository. Read-only.

Repository: /diagram/.clones/digram-backlog. Paths in keys are relative to it (a key is `<file>::<unit>#<claim>`; for a
Mode A procedure the unit is a section heading of the markdown file). The `Research:` lines in the unit's docstring (or
the procedure section's claim block) name the cited question, a pointer `research/questions/NNNN-<id>.html` under
`.claude/skills/diagram/research/`, with how our maps draw it in the `.drawing.html` beside it. `note` is the reason the
checker (impl-drift) gave.

For EACH finding in your batch file: open the unit's code (or procedure section), read its Research line for that claim,
and read just enough of the cited question / drawing page to see what the matching implementation would be. Then judge:

Tiers (implementation work, easiest first):
- E0: the claim alone - the implementation already matches the research; only the claim's label (GUESS/CONVENTION/
  UNRESEARCHED/DEVIATION/pointer), citation or wording is wrong. MISLABELED usually lands here.
- E1: one value - one number, size, count or band in code or procedure text changes; the logic stands.
- E2: one rule - one function's logic or one procedure paragraph changes, within one module or one section.
- E3: a form or several places - a new rolled knob or new element, a change across modules, a hand-drawn Mode A sheet
  (an SVG under the pool) redrawn, or a change that ripples into placement / overlap / several generators.
- E4: research first - the record does not say what the implementation should be (NEEDS-RESEARCH, CANNOT-TELL, two
  cited pages that disagree, or a fix needing a fact no page has).
UNCLAIMED: the fix is adding a claim for the decision named; tier it E0 if an existing question plainly backs the code as
it stands, otherwise by the work to make the code match what the record says (or E4 if the record is silent).

The direction is fixed by the GM: the implementation moves to the research ("I'm not sure there's any reason for our
implementation to not match for anything"). Never propose rewriting the research to fit the code, and never "record a
DEVIATION" as the fix; if that looks like the only sane fix, tier it by the implementation work anyway and set
`flag: "deviation-tempting"` with one clause why.

Write your answer as JSON Lines to the OUT file named in your dispatch (one object per finding, the same order as the
batch file, every finding exactly once):
{"key": "...", "tier": "E0|E1|E2|E3|E4", "fix": "<one line: what changes, to what value/rule>", "files": ["<path>", ...],
 "after": ["<key this must follow>", ...], "flag": ""}
Keep `fix` to one line and concrete (a value, the rule). `files` is relative to the repository root. `after` only for a
real dependency (the same constant, or a rule the other fix changes).

Your final reply to the session is SHORT: counts per tier, how many flags, and the OUT path. Nothing else.
