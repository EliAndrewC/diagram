# Contract - a question's files and markers (feature 303; supersedes feature 258's page-directory contract)

- Names: `questions/NNNN-<slug>.html`, `.notes.html`, `.originals.html`, `.drawing.html`, `.drawing.notes.html`,
  `.drawing.originals.html`. Any other name in `questions/` is a refusal naming the file.
- Two stems with one number, or one heading id on two pages: refused.
- Markers (HTML comments, on the line after the heading):
  `<!-- tags: subject=a,b; setting=countryside,town; level=detail -->`
  `<!-- about: NNNN-<slug> -->` (a drawing page with no research page in its stem, about another stem's question)
- Refused, naming the file: no tags where they are owed; an unknown tag; a facet missing; two levels; tags on a page
  that inherits; an `about:` naming no research stem; a question no section's rule takes; a rule taking nothing.
- Links (outside comments): `NNNN-<slug>.html[#id]`, `NNNN-<slug>.drawing.html[#id]`, `../SOURCES.html#<key>`, `#id`
  (same page), external URLs. Any other in-record link, or one naming a missing id, is refused.
- Notes: a reference `<sup class="fn" data-note="k">` resolves in its own page's notes file only.
