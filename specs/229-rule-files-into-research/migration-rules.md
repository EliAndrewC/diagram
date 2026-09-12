# Migration rules - how a rule file's content lands on its research page (feature 229)

Every writer works from these rules. The page is HAND-AUTHORED HTML in `research/`; the form is
`research/CLAUDE.md` (auto-loads when you edit there) and `research/README.md` "Entry format". This file is the
short operational version plus what is specific to this sweep.

## What you receive

The rule file (`settlements/<topic>.md`), the research page (`research/<topic>.html`), its citations page
(`research/citations/<topic>.html`), the audit report (`specs/229-rule-files-into-research/audit/<...>.md`) with
the unit-by-unit classes, and this file. You edit the research page and its citations page IN PLACE in the clone
`/diagram/.clones/diagram-research/`. You do not edit the rule file, any engine file, `SOURCES.html`, the glossary
or any other page: you REPORT what those need (below) and the session makes those edits centrally.

## What moves, and what does not

Move, from the audit's classes:

- **D (decision record)** the page lacks: a GM ruling with its date and words, an accepted limitation with its
  cost and the alternatives declined, a fix tried and reverted with its measurement, a project-goal rationale.
- **B rules the engine does NOT encode** (the audit's "B items the engine does not encode" list, and for the
  unscripted tiers nearly every B unit): written as SPECIFICATION paragraphs (below).
- **A finding or research narrative the page does NOT carry** (the audit marks some "B (research content,
  misfiled)" or "unmigrated research"; a knob's value-space grounding; a historical account the rule file tells
  and the page does not): written as the entry's FINDING, under the physical-claim rule below. This is the GM's
  central case - the why must not be lost with the file.
- **The "why" a hamlet-tier rule carried that the engine's comment lacks** (the audit says which; the session's
  `research.md` collects them): written onto the page as the decision's grounds. The number itself stays in the
  engine; you say in the report which engine site should point at your anchor.
- **E (unscripted tier / setting canon)**: setting canon is stated as such (`<!-- Evidence: setting-canon -->`,
  and the body says it rests on the GM's setting notes); it needs no footnote.

Do NOT move:

- **A (restated)**: the page already has it. Do not write it twice. If the rule file's wording was better, improve
  the existing entry in place; never a second entry on the same finding.
- **C (hand procedure)**: draw order, "load this file when", how to call a generator method, `.gen.py` recipes,
  validator step lists, review-pass instructions. Gone.
- **F (stale)**: a deleted check, a retired knob, a dead fixture path, a mechanism that no longer exists. Gone.
  A check NAME is never written on the page - not visibly, and not as the rule's identity. If a stale unit wraps
  a live decision (the audit marks these "F + D"), the decision moves and the mechanism does not.
- A rule the engine encodes WITH its why (FR-004). The report lists these as "preserved by the engine at
  file:line", nothing on the page.

## The form of an entry

```
<h2 id="<anchor>">The question a reader would ask from the map - and, often, its answer</h2>
<!-- researched YYYY-MM-DD, feature 229; moved from settlements/<topic>.md "<heading or first words>" -->
<!-- Grounds: <the generator methods, constants or knobs this justifies, or "none yet - the tier is unscripted"> -->
<!-- Evidence: attested | corroborated | analog | interpolated | reconstruction | setting-canon | liberty | researched -->
<p><strong>Sources:</strong> ...</p>
<p>...the finding, the decision, the ruling...</p>
<p class="spec"><strong>The rule the map follows:</strong> ...</p>
```

- **Heading**: the question a casual RPG reader would ask looking at the map ("Does a shelter belt wrap the
  settlement?", "How far outside the wall does the execution ground stand?"). Its `id` follows the record's
  anchor rule: the heading text lowercased; every character that is not a letter, digit, space, hyphen or
  underscore dropped; spaces to hyphens (so ` - ` becomes `---`). **Never change an existing heading or id** - the
  maps and the engine link to them. A new decision that belongs under an existing question goes INTO that
  section as a paragraph, not as a new heading.
- **Bookkeeping is a comment**: the date, "feature 229", the rule file it came from, `Grounds:`, `Evidence:`,
  any engine identifier (a constant, a function, a knob's code name, a check name, a module path), any pixel
  figure, any fetch verdict. The gate fails a page whose VISIBLE text contains `feature NNN`, `Tnn`, `specs/`,
  `Corrected 20xx`, `re-read`, `READ`/`SUMMARY-ONLY`/`UNFETCHABLE`/`NOT-FOUND`/`CONTRADICTED`, `used to say`,
  or `Grounds:`/`Evidence:` - so those words never appear outside a comment.
- **No history of the document**: never "this used to say", "corrected on", "the earlier note claimed", "the
  first draft". A finding that changed is written as the finding. What IS kept: a fix that was TRIED on the map
  and reverted, with its measurement, because that is a decision the next session needs - write it as "a wider
  window was tried and measured; it bought one clump on one map and was not kept", not as document history.
- **The GM's ruling stays quoted, with its date**: *the GM ruled on 2026-08-29: "..."*. The declined
  alternatives stay named. A measurement that decided something keeps its numbers. Every decision carries one of
  the four labels, in the record's words: **accurate** (the record says so), **deviation** (the setting differs
  from the history it is based on), **a map drawing convention** (a glyph scaled or colored for the eye), or
  **guess** (the record is silent). The reader must never be told a guess or a calibration is a finding.
- **Sources roster**: only keys the registry (`research/SOURCES.html`) already has, each written as a link
  exactly as the page already writes it. When an entry rests on no work - a GM ruling, a project measurement -
  the roster says so: `<p><strong>Sources:</strong> the GM's ruling of 2026-08-29; this project's measurement of the
  five scripted hamlets</p>`. **Never write a bare key, never coin a key, never write a URL you did not fetch,
  never write a footnote** (`<sup class="fn">` / `<li id="fn-n">`). Footnotes are added by the session after the
  source-reader pass.
- **A physical claim with no footnote** - a claim about how a place was built, farmed or lived in that the rule
  file stated without a citation - is written, and marked for the pass with a comment on the same line:
  `<!-- FN-PENDING: <the source the rule file named, or "none named"> -->`. Label it honestly NOW: if the rule
  file gave no source, the sentence says the record was not checked - "(this rests on general reading; no source
  is cited)" - and the footnote pass will replace that with a citation or an absence note. Do not present it as
  attested.
- **Glossary**: a term the reader would not know (tsubo, kido, sando, wengcheng, guan-xiang, hokora, ...) is
  wrapped automatically from the shared glossary. Do not wrap by hand. List every term you used that the glossary
  may lack in your report; the session adds them.
- **Real feet on the page** (D7): the tier's scale is hamlet/town 1 ft per px, village 2 ft, city and capital
  3 ft. Convert every pixel figure the rule file gives to real feet (or acres / m² where the rule file already
  reasoned in those) and put the pixel figure with its scale in a comment beside it: `about 35 ft
  <!-- 35 px at 1 ft/px -->`. Where a rule was written in px at an unstated scale, say which tier it was written
  for and convert at that tier's scale; if you cannot tell, keep the px figure visible and say "on the town
  sheet, 35 px" and flag it in the report.
- **A specification paragraph** is `<p class="spec"><strong>The rule the map follows:</strong> ...</p>`, one per
  rule or tight family of rules, directly under the question whose finding grounds it (or under a new question
  when none does). It states what a map of that tier draws, in the reader's terms, with the thresholds in feet
  and counts. It names no engine identifier and no check in its visible text. Where the rule had no "why" at
  all, the paragraph says so in the record's honest form: *a convention chosen so the feature reads at map
  scale*, *calibrated against the three drawn cities, not derived from a source*, or *a guess*. A rule the
  audit marks as tier-specific says which tier.
- **House style**: hyphens only, never an em-dash or en-dash (except inside a quotation of someone else's
  words); American spelling; "people" only for samurai or in narrative voice - use "inhabitants",
  "households", "humans" in analytical prose; "domain" never "demesne"; they/them for a generic office-holder.

## The page's own pointers to the rule file

Every research page opens with a line like *"The research behind the rules in `../settlements/<topic>.md`"*
and carries comments naming the rule file. Replace the opening line with:

```
<p><em>The findings behind the <topic words> on these maps, the decisions they drove, and - where no
generator draws the feature yet - the rules a map follows.</em></p>
```

and reword or delete every comment that names `settlements/<topic>.md` or `settlements.md` (a comment may say
"moved from the retired rule file" once, at the top). The gate will fail any surviving mention.

## A new page

`ways.html`, `presentation.html`, `settlements.html` and `cities/sizing.html` do not exist. A new page copies
`research/towns.html`'s `<head>` exactly (charset, viewport, title, `assets/record.css`, `assets/glossary.js`,
`citations/<name>.js`, `assets/record.js`; from `cities/` the asset paths start `../`), one `<main>` with an
`<h1>` whose id is the anchor of its text, the opening line above, an `<hr>`, the entries, and the closing
`<section class="citations">` line linking to its citations page. Its citations page copies
`research/citations/towns.html`'s head and `<h1>`, the intro paragraph, an EMPTY works section between the two
markers exactly as they appear in that file (`<!-- works-cited: DERIVED by ... -->` and `<!-- /works-cited -->`),
and an empty `<section class="footnotes"><ol></ol></section>`. The session runs `make citations`, which writes the
`.js`; you do not.

## Contradictions (FR-001)

Apply the FR-001 item for your page before writing anything else that touches it, and apply the page's OWN
label where the rule file disagreed with it (a GUESS on the page stays a GUESS; a struck claim is not revived).
Where you find a disagreement the spec does not list, resolve it toward the measured or ruled truth and put it
in the report.

## Your report (returned to the session; the session writes `research.md` from it)

1. **Decision map**: each audit D item (by its number in the audit) -> the anchor that now holds it (or "already
   on the page at <anchor>" / "dropped: <reason>").
2. **Specification map**: each rule you wrote as a `<p class="spec">` -> its anchor; and each B rule you did
   NOT move, with the reason (preserved by the engine at file:line; a deleted mechanism with no map behavior;
   a duplicate of another rule).
3. **Physical claims pending**: each `FN-PENDING` you placed - the anchor, the claim's sentence, the source the
   rule file named (author, title, year, URL if given) or "none named".
4. **Contradictions** you applied or found.
5. **Engine pointers wanted**: file:line of an engine comment that should point at one of your anchors, and the
   anchor.
6. **Glossary terms** used that the glossary may lack, each with a one-sentence definition drafted from the text.
7. **Pixel figures you could not convert** (unknown scale), if any.
8. Anything from the rule file you judged worth preserving that the audit did not class D or B, and where you put
   it.
