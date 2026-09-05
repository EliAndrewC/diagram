# Feature 184 - no dotted underlines beneath the page's links

**Status**: FAITHFUL (`spec-fidelity`, round 1 of 5) - cleared for implementation (constitution XVI). The
review measured the set (the three rules are the only dotted underlines on a link anywhere in the engine)
and graded D1 the literal reading. Its aside: the *"See references (N)"* link carries the browser's
default SOLID underline and always has - outside this request, reported to the GM.
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessors**: features 134 (the sibling links), 180 (the question links), 181 (the title link)

## Summary

The interactive page's links carry `text-decoration: underline dotted`. The GM does not like it: the
links keep their color and hover color and lose the dotted underline, nothing else.

## Functional requirements

- **FR-001** The three link styles in `interactive/assets/page.css` - `a.sib` (the "Not to be confused
  with" sibling links), `a.q` (the question links in the references modal) and `a.back` (the name in
  the references modal's title, the GM's example) - MUST lose `text-decoration: underline dotted` and
  MUST otherwise be unchanged: same color, same hover color. No underline of any kind replaces it (a
  browser's default solid underline would be a style the GM did not ask for), so the rule becomes
  `text-decoration: none`.
- **FR-002** Everything else about the links is unchanged: what they do, where they go, their text.
- **FR-003** The browser test asserts the computed `text-decoration-line` of each of the three link kinds
  is `none` on a rendered page.
- **FR-004** The SVG and the PNG are untouched (feature 134 FR-010); only `page.css` changes.

### What this feature does not do

- **FR-005** The glossary term's dotted line (`.gl`, a `border-bottom: 1px dotted`) is NOT a link and is
  NOT removed: it marks a word that has a definition on hover, and the GM asked about links. Recorded as
  D1 so it is a decision, not an oversight; it is one line if the GM wants it gone too.

## Decisions Recorded

- **D1 - the glossary term keeps its dotted mark.** The GM's request is about *"our links"*, with the
  title link as the example. A glossary term is not a link - clicking it does nothing, hovering it shows
  a definition - and its dotted line is the only signal that a definition exists. Left as is and
  reported; removing it is `border-bottom` off one rule.
- **D2 - `text-decoration: none`, not the browser default.** Removing the declaration would leave a
  solid underline (the user-agent default for `<a>`), which is a new style, not "otherwise unchanged".
