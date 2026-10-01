# Data model - feature 303

- **Stem** `NNNN-<slug>`: identity (four-digit number, never reused), slug (a heading id). Files: research page
  (optional), drawing page (optional; at least one of the two), each with optional `.notes` and `.originals`.
- **Research page**: one `<h2 id>` heading, then the `tags` marker, then its body. Its id is unique in the record.
- **Drawing page**: one heading; if its stem has a research page it inherits that page's tags and states none; else it
  states `about:` (inherits the named stem's tags) or `tags:` (a drawing-only question), never both.
- **Tags**: subjects (ordered, first primary, >= 1), settings (>= 1), level (exactly 1). Every id in `tags.json`.
- **Vocabulary** (`tags.json`): facets subject / setting / level; each tag id -> name, description; levels ordered.
- **Contents** (`contents.json`): tree of sections; each `id` (unique), `title`, `description`, `takes` (clauses, may be
  empty for a pure container), `sections` (children). Home of a question = first section in depth-first order whose
  clause matches. A section is shown in a half only if it or a descendant homes a page of that half.
- **Mapping** (`moved-303.json`): old fragment path -> new path; old page -> section id; old `<page> NNN` -> `NNNN`.
