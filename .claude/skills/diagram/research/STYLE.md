# How a research section reads - the style guide (feature 292)

The record's other rules (footnotes that quote, the four labels, the glossary, no session notes in the visible text)
say what a section must CONTAIN. This guide says how it is PRESENTED to its reader: a curious RPG player who clicked
through from a map and knows nothing about the subject. It was generalized from the GM's worked example of
2026-09-29 (their words are in `specs/292-research-presentation-style/request.md`; the rules quote them). The
`record-style` check holds it.

Each rule says where it comes from: **GM** (the GM said it), or **inferred** (the session's generalization from
the GM's example, awaiting the GM's confirmation in the pilot).

## 1. A section is a topic, not a question

- **The title names the topic in plain English**, with the native term in parentheses where there is one:
  "Groves of trees around farmhouses (yashikirin)". Not a question, not a question and its answer, not a phrase
  from the session that raised it. (GM: *"distill it into a title that is written in plain English and conveys the
  information that this section is about."*)
- **One topic, one section.** Sections that grew one per question on the same subject are merged. (GM: *"asking a
  new question about a grove created a new section about a grove ... it probably makes sense to combine some of these
  sections into a single larger section."*)
- **A merge is a reorganization, not a concatenation.** Material from the later sections goes where a newcomer
  needs it - often early - and repeated material is said once. (GM: *"possibly reordering some things because that
  other section might have information that should come earlier in the combined section rather than just appending
  everything at the end."*)
- **The inciting question appears nowhere** - neither the GM's words nor a paraphrase ("This question asks...").
  (GM: *"I instead do not want the inciting question to appear anywhere in the research write-up section, because I
  think it just confuses things by referring to a conversation whose context the reader will not have."*) A GM
  RULING - a decision, with the alternatives it declined - stays; that is a finding about the maps, not the question.

## 2. It opens with a short plain-English account

- **One or two short paragraphs first** say what the thing was, what it was for, and why it took the form it did -
  with the headline numbers. For the grove: dozens of trees at every farmhouse, of which kinds, planted as a
  windbreak on the sides the damaging wind came from, and why that wind mattered. (GM: *"open with a plain English
  description of what these groves were. And why they existed ... ideally these paragraphs would be relatively
  short."*)
- The opening is footnoted like everything else; it states, it does not tease what the bullets will say. (inferred)

## 3. The findings are short bullets, most led by a question

- **One finding per bullet.** A run of findings joined by semicolons is split, each ending in a period. (GM: *"this
  is enough information to be its own bullet point ... end this with a period instead of a semicolon."*)
- **A bullet opens with a bold lead line on its own line** - usually the question a reader would ask
  (**What was the average number of trees per farmhouse?**), sometimes a plain statement of the point
  (**Our maps draw every canopy tree.**). The body follows on the next line. (GM, both forms in their example.)
- **A lead-in sentence where the bullet needs context.** When the bullet's figures only make sense against
  something ("Having established the *number* of trees, how are they arranged?"), or a reader would not see why it
  matters, one or two sentences of lead-in come first, in plain terms for a non-expert; when the bullet already flows,
  it has none. (GM: *"I wrote a leading sentence as well as a bolded question
  ... because that helped contextualize the numbers that came after it. The previous bullet points didn't need
  that."*)
- **Not everything is a Q&A bullet.** The opening, a ruling, the map's rule (`class="spec"`) and a short join between
  bullets stay prose. (GM: *"not everything needs to be a Q&A style bullet point."*)
- **An aside that carries a real finding is its own bullet**, not a parenthesis or an italic afterthought. (GM, of the
  Okinawa cross-check: *"it deserves its own bullet point and doesn't need to be a parenthetical."*)
- **The map comes after the history.** What the record found comes first; what our maps draw, and which knobs they
  roll, follows it in bullets of its own, each saying which finding it rests on. (inferred - the GM's example
  mixes the two within bullets, and they kept both kinds; separating them lets a reader who wants only the history stop.)

## 4. What is cut

- **Framing the whole record presumes.** "Historical scale - the real numbers" and "to scale" said of one topic -
  every section is to scale and uses real numbers. (GM: *"a sentence like this serves no purpose."*)
- **A restatement of a number already given.** "A substantial STAND, not a few trees" after the tree count. (GM:
  *"if we are already saying the number of trees ... a separate sentence ... is a pointless thing to say."*)
- **A statement that says nothing about the thing or the research, only what is visible on the map**: "the grove
  is the largest thing on the homestead - bigger than the farmhouse". The half of such a sentence that DOES carry a
  finding stays. (GM: *"It's not really conveying anything about the groves themselves, or anything about our
  research; it's just stating what is plainly visible on the map. Whereas the second half of the sentence IS
  useful."*) A statement of HOW the map draws something, and why - every crown at its real size, a glyph by
  convention - is kept: the GM called that one *"More great stuff, love it."*
- **The `Sources:` roster.** The footnotes carry every citation, and a footnote's hover links the work's entry on the
  citations page. Before a roster is removed, every key it named is cited by a footnote of the section, every
  passage its own footnote quoted is quoted by one, and anything the roster says that the section does not (a work's
  gloss, say) is carried into the text - a removal never loses a citation or a fact. (GM: *"we should never be
  removing a citation ... keep that information just not in a sources section."*)
- **Pointer paragraphs between merged sections** ("The size ... is at X; this question asks which ...") - after a
  merge there is nothing to point at. (inferred)
- **Shouted emphasis.** Capitals for emphasis (STAND, LARGEST, EVERY) become plain words, or bold where a number
  truly needs it. (inferred)

## 5. Terms

- **A term a newcomer would not know is explained once, everywhere, as a glossary tooltip** - "knob", "canopy tree"
  - rather than inline in each section. An inline lead-in explains a term only where the explanation is itself the
  point. (GM: *"we could also use a tooltip to explain this context ... since we could apply the tooltip everywhere
  that we use the term."*)
- Project jargon ("arm", "belt", "appurtenance", "roll", "footprint", "tier") is replaced by the plain word where one
  exists, and glossed where it must stay. (inferred)

## 6. What does not change

Every other rule of the record holds: every assertion footnoted with a quoted passage; the four labels, visible
(a GUESS stays a GUESS, said where the claim stands); absence notes; GM rulings with the alternatives declined; the
map's rule in real feet; nothing addressed to a session outside an HTML comment; no history of the document in the
document. Restyling moves and rewords the prose around those; it never drops a footnote, a label or a ruling except
where a rule above cuts the sentence that carried it, and then the cut is named.
