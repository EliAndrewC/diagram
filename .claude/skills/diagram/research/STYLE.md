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
- **A rendering section's title mirrors its research section's**: "How our maps draw threshing and drying yards (niwa)"
  beside "Threshing and drying yards at farmhouses (niwa)" - so a reader who follows the link knows it is the same
  thing. (inferred - the second pilot's check found the generic "How our maps draw the work yards" vague.)
- **A turn to another region or practice is introduced.** When a section moves from one country's practice to
  another's, a sentence of prose between the lists says what changes ("Rice farmers in south China did the same work on
  different ground ..."), so a bullet about the second is not a non sequitur. (inferred - the second pilot.)
- **A merge is a reorganization, not a concatenation.** Material from the later sections goes where a newcomer
  needs it - often early - and repeated material is said once. (GM: *"possibly reordering some things because that
  other section might have information that should come earlier in the combined section rather than just appending
  everything at the end."*)
- **A topic can be a condition, not a feature.** Where several sections ask about one condition on different features -
  the sun on a yard, on a kitchen bed, on a crop field - they fold into one section on the condition ("Sunlight and
  shade on the farm"), and each feature's own section links to it. (GM, 2026-09-30: *"a section not specifically about
  garden sun, but about shade in general"*)
- **The inciting question appears nowhere** - neither the GM's words nor a paraphrase ("This question asks...").
  (GM: *"I instead do not want the inciting question to appear anywhere in the research write-up section, because I
  think it just confuses things by referring to a conversation whose context the reader will not have."*)
- **A decision is the project's choice, never "the GM ruled".** No ruling, no quotation of the GM, no "the GM" at all
  in the visible text. What the reader is told is what the decision IS and why, in terms of the history: which forms
  the record shows existed, which the evidence suggests were commoner, and how the maps render that variety - for
  example, "we know of farms whose grove took two sides, three or all four; two-sided groves are the form reported in
  the most regions, so this project makes them the commonest, then three, then four". Where the shares are arbitrary,
  say so. The ruling itself - date, words, alternatives declined - is kept for later sessions in an HTML comment beside
  the sentence it produced. (GM, 2026-09-29: *"We should not have anything like this in our research writeup ... it is okay to capture my rulings in our checked-in repository for your own understanding ... you could keep it by having it be hidden. Like, this is in an HTML comment ... when explaining this to a human reading this later, you should not refer to this as a GM ruling. Rather, you should describe it the way this project has chosen to render the variety of settlements that we know existed historically."*)

## 2. It opens with a short plain-English account

- **One or two short paragraphs first** say what the thing was, what it was for, and why it took the form it did -
  with the headline numbers. For the grove: dozens of trees at every farmhouse, of which kinds, planted as a
  windbreak on the sides the damaging wind came from, and why that wind mattered. (GM: *"open with a plain English
  description of what these groves were. And why they existed ... ideally these paragraphs would be relatively
  short."*)
- The opening is footnoted like everything else; it states, it does not tease what the bullets will say. (inferred)
- **The opening rounds; the bullet is exact.** A headline figure in the opening is given plainly ("dozens of trees");
  the exact figure, and any caveat on how it was reached, is said once, in its bullet. (inferred - the first pilot's
  opening gave "about 33" without the bullet's caveat that 33 is this page's arithmetic.)
- **A date a newcomer cannot place is tied once to its period**: "before 1868, in the Edo period". (inferred)

## 3. The findings are lead-line bullets

The list is called **lead-line bullets**, not Q&A: every bullet opens with a bold LEAD LINE, which is a statement or a
question as the finding calls for. (GM: *"I suspect I might have inadvertently biased you towards making these bolded
highlights into questions ... I think that we need to come up with a different name for it."*)

- **One finding per bullet.** A run of findings joined by semicolons is split, each ending in a period. (GM: *"this
  is enough information to be its own bullet point ... end this with a period instead of a semicolon."*)
- **The lead line is bold, on its own line, and the body follows on the next.** It is a one-sentence summary of the
  bullet, and the body says how we know it. A lead-in sentence, where one is needed, opens the body, right after the
  lead line - as in the GM's own example ("**How deep would these groves be?** Having established the *number* of
  trees, how are they arranged..."). (GM: *"a good one sentence summary of what the paragraph can be. And then
  the paragraph goes into detail about how we know the top line sentence."*)
- **A statement when the finding is a straightforward fact; a question when it is not.** A plain fact the sources
  establish - that the groves existed, that they stood on different sides in different regions - is a declarative lead
  line: **Farming communities have had these groves for centuries.** A finding that is complicated, a range or an
  approximation, an educated guess, or a conclusion drawn from thin sourcing is a question: **How tall were they?**
  (a range with an average), **How large would these groves get?** (an educated guess, cited). A question is better
  than a statement of doubt ("We don't know how large...") because there IS a sourced guess. Only a point resting on
  no evidence at all, pure conjecture, goes back to a statement. (GM: *"depends on whether or not there is a
  straightforward fact that we are attempting to convey. If there is, then we make it as a declarative statement. And
  if what we are expressing is complicated or we are explaining a level of uncertainty, and summarizing the conclusions
  that we have made based on our research, then it should be phrased as a question."*)
- **A lead line states no more than its sources.** One source's rule of thumb is attributed, not stated as a fact of
  nature ("A sixth-century Chinese farm manual says an elm's shade reaches as far as the tree is tall", not "A tree's
  shade reaches as far as the tree is tall"); what a source says of one thing (the elm) is not said of all things (any
  tree); and an "only" or a "never" that rests on a search that found nothing is a question ("Were the groves cut back
  to a fixed height?") or says what is recorded ("the only ones recorded as..."). (inferred - the third pilot's checks)
- **A lead line and its body stand on their own, for a reader who skims.** A reader whose eye lands on one bullet should
  follow it without the bullets before it. A year or a concept whose significance the bullet needs is explained in
  place, one of two ways: the lead line says it ("Were groves as large before Japan began to modernize in 1868?"), or
  the word is a glossary tooltip ("1868", "Edo period"). Choose per bullet; a term that recurs across the record wants
  the tooltip. (GM, 2026-09-29: *"it would be good if someone skimming this section were able to read an arbitrary answer that caught their eye without requiring all of the context that came before it. Therefore, when there is an easy way to explain a year or a concept then we should take it ... The first option is to reword the question to include the explanation ... The second option is to make the year 1868 a tooltip."*)
- **A lead line makes sense to a reader who has read only what comes before it.** A date, a name or a term whose
  relevance the reader has not yet been given - "before 1868" before anything has said why that year matters - is
  either explained before it or kept out of the lead line. (GM: *"someone just starting to read this document ...
  would have no idea whatsoever why the year 1868 is being mentioned, or why it would even occur to us to ask."*)
- **A lead-in sentence where the bullet needs context.** When the bullet's figures only make sense against
  something ("Having established the *number* of trees, how are they arranged?"), or a reader would not see why it
  matters, one or two sentences of lead-in come first, in plain terms for a non-expert; when the bullet already flows,
  it has none. (GM: *"I wrote a leading sentence as well as a bolded question
  ... because that helped contextualize the numbers that came after it. The previous bullet points didn't need
  that."*)
- **Not everything is a bullet.** The opening, a ruling, the map's rule (`class="spec"`) and a short join between
  bullets stay prose. (GM: *"not everything needs to be a Q&A style bullet point."*)
- **An aside that carries a real finding is its own bullet**, not a parenthesis or an italic afterthought. (GM, of the
  Okinawa cross-check: *"it deserves its own bullet point and doesn't need to be a parenthetical."*)
- **How the maps draw it is not in the research section at all.** A research section says what the record found. What
  our maps draw - sizes chosen, knobs, conventions, the rule the map follows - is a section of its own in the
  RENDERING collection, `research/rendering/<page>.html` (one page beside each research page), which declares the
  research section it is about in a comment after its heading (`about: <page>.html#<id>`); `make record` then writes
  a link under both headings, "How our maps draw it" and "The history behind it". No link between the two is ever
  typed. A rendering section follows this guide too, and still cites the research it rests on. (GM, 2026-09-29: *"anything that is specifically about how we choose to render the grove or render a map element generally probably belongs in a separate place ... there should probably just be a separate collection of files that have to do with our rendering decisions ... the two of them should definitely link to each other. And I think that linking should be automated rather than something that we write."*)
- **No paragraph over 150 words**, and no bullet whose own text is. A longer one is split, or made a list - a rule
  paragraph of several rules and rationales is a bulleted list, nested where the rules group. The bar is mechanical
  (`make style-prepass`): the GM's accepted opening paragraphs were 133 and 68 words, the rule paragraph they rejected
  364. (GM, 2026-09-29: *"that paragraph is way too long. that looks like it should probably be its own bulleted list
  ... that could probably be a mechanical check"*)

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
- **A claim about what a page we could not read says.** "A yard at Kodaira is given as 70 tsubo, from a page we could not
  read" asserts a page's content that no one here has seen - it may be a figure an early pass took from a search summary,
  or invented. Such a claim does not stand: the page is read and quoted (a page only a person can open goes on the GM's
  download list, `academic-sources/TO-DOWNLOAD.md`), or the claim is removed, its history kept in a comment. An absence
  note supports only a stated silence ("no page we read gives it") or a GUESS of our own. (GM, 2026-09-30: *"we explicitly call out pages that we assert exist and that we further assert contain data, like specific answers, but which we are saying do not load ... why it is that we believe this information is on this page or these pages in the first place if we cannot load the page ... As of now, it looks very suspicious."*)
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
- **No untranslated foreign words in our own text** - footnotes included. A page is named by what it is ("the Japanese
  Wikipedia article on homestead groves", not "ja.wikipedia 屋敷林"). Where the characters themselves are worth showing,
  they take ONE form: `垣根 (kakine, "hedge")` - the characters, then the reading and the English meaning in quotes; a
  reading alone is not a translation. Where they add nothing, they are dropped. The style prepass fails any other kanji in
  our words; `make translation-owed` lists a gloss whose characters or meaning changed, for `translation-check`.
  Quotations and originals keep their own script. (GM, 2026-09-30: *"I don't know what that means, and I presume that 'muyashiki torokunin' is the transliteration, but that doesn't actually help me because a transliteration is not a translation ... if we always ... show a translation in the same format immediately following some kanji, then that would allow us to have a mechanical check"*) (GM, 2026-09-29: *"this still has some
  untranslated foreign words, i.e. '屋敷林' should get translated"*)

- **Number follows the map.** A feature a map has one of is singular - "a settlement's notice board"; a feature it has
  many of is plural - "a settlement's farmhouses", and the homestead groves, one to a farmhouse, are "a map's groves",
  never "a map's grove". A generic singular that plainly means each one ("a grove's trees", "each windward stand")
  stays. (GM, 2026-09-29: *"there are some features on a map for which the map only has a single one ... you would use
  the singular to refer to it to prevent confusion ... when referring to a thing which a map will have many of, you
  would use the plural."*)
- **Not to be confused with** (GM, 2026-09-29; built after the sweep, feature 292 T10): a section whose subject a
  reader could mistake for another's opens, right under its heading, with a list *Not to be confused with:* - each entry
  the other section's title, linked, and the first sentence of that section's opening, which is the record's definition
  of it. The pairs are data, kept once in `research/confusables.json` (`{"a": "<page>#<id>", "b": "<page>#<id>",
  "why": "<the difference>"}`) and always two-way: `make record` writes the list under both sections, and refuses a pair
  naming a section that does not exist. A section that gains a confusable neighbor - a new topic, a renamed one - adds
  its pair to the data file, never a list by hand. Because the list quotes the other section's first sentence, that
  sentence says what the thing IS.

## 6. Units

- **A metric figure in our own prose carries its conversion to feet**, rounded to the nearest foot with a tilde, in
  parentheses after it: "11 to 28 m (~36-92 ft), about 15 m (~49 ft) on average". A quoted passage is never touched -
  a footnote quotes its source as the source wrote it. (GM: *"any time we expressed something in meters, then we also
  convert it to feet and then round to the nearest foot with a tilde ... this rule about units only applies to text
  that we ourselves write."*)
- A figure under a foot converts to inches the same way ("10 cm (~4 in)"), and an area in hectares or square meters to
  acres or square feet. (inferred - rounding 10 cm to the nearest foot gives nothing.)
- The prepass (`make style-prepass`) lists every metric figure in the section's own prose with no conversion beside it.

## 7. Footnotes

- **A translation says `translated`, and English says nothing.** `「English」 (translated; original: 「原文」)`: this project
  is presumed the translator and English the language of an unmarked passage, so neither is stated; another translator
  is named. (GM, 2026-09-29: *"we should presume the source is in English unless ... stated otherwise ... we should
  presume that all translations are done by this project unless explicitly stated otherwise, which allows us to simply
  say 'translated', which improves legibility and makes the footnotes scan better."*)
- **The original is collapsed**, one click away, and stored apart (`make record` moves it).
- **Several passages from one source are a list.** Join them with `; `, and end a passage that introduces others with
  `:`; the page shows one bullet per passage, nested under the one that introduces them. (GM, 2026-09-29: *"anytime we
  are citing multiple things from a source instead of one thing, we should display this as a bulleted list within the
  footnote"*)
- **A footnote's source key opens the work's entry at the foot of the page** - its citation line and what it is - which
  links the source itself (feature 301: a question's page carries the works its notes cite).
- **An absence note opens with one sentence, kept in one place.** The note is written `no publicly readable source`
  followed by an HTML comment holding the search - its date and its terms - and then, visibly, what the search found; the
  page shows "Our research of publicly-available sources couldn't find anything conclusive:" in place of the marker, from
  `record/absence.py`, the one line to change. What was found is a list where it is several things - a finding with its
  sources nested under it. (GM, 2026-09-29: *"Instead of 'no publicly available source' our standard wording should be 'Our research of publicly-available sources couldn't find anything conclusive:' ... the date we searched and what the web searches were is not information the human reader needs to see ... This is another case where a bulleted list would be clearer"*)

## 8. What does not change

Every other rule of the record holds: every assertion footnoted with a quoted passage; the four labels, visible
(a GUESS stays a GUESS, said where the claim stands); absence notes; every decision and the alternatives it declined (as the project's choice, the ruling itself in a comment); the
map's rule in real feet; nothing addressed to a session outside an HTML comment; no history of the document in the
document. Restyling moves and rewords the prose around those; it never drops a footnote, a label or a decision except
where a rule above cuts the sentence that carried it, and then the cut is named.
