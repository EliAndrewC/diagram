# research/ - the historical record, and who it is written for

This file auto-loads when a research entry is being written or changed - which is exactly when the
rule below applies. The entry FORMAT, the evidence classes, the citing rules and the table of which
research file grounds which rule file are in [`README.md`](README.md); this file carries the one thing
that is not a format rule: who the reader is.

## Who the record is for, and how it is organized for them (GM 2026-09-05, feature 180)

The reader this record ultimately serves is not the next session - it is the person looking at an
interactive map. The GM's description of them: *"casual RPG enthusiasts who might be interested to
learn a little more about why these settlements are the way that they are. You know, like the different
types of crops that are grown, that kind of thing."* They are curious, not scholarly, and *"they are not
immediately presented with an overwhelming amount of third party sources that they could go read to
become an expert."*

**So the record is organized as QUESTIONS**, and the reader reaches it through a chain with one step per
level of curiosity:

1. **The map.** They hover a feature and click it; the modal says what it is and why it stands there.
2. **"See references."** The references modal lists the questions we asked while working out that kind
   of feature - the headings of the research sections its explanation was written from, each a link.
3. **The answer.** A question links to its section on the public GitHub rendering of the research file
   (`https://github.com/EliAndrewC/diagram/blob/main/.claude/skills/diagram/research/<file>.md#<anchor>`),
   where the well-formatted markdown gives the finding, the decision it drove and any disclosed liberty.
4. **The sources.** Every section ends in a `**Sources:**` line, and every key in [`SOURCES.md`](SOURCES.md)
   carries the URL where the work can be read (constitution v2.13.0), so a reader who truly wants to
   check can - *"which both demonstrates that this was based on actual research and also gives them the
   ability to go read Wikipedia or whatever other public source we have linked to."*

The sources are deliberately one click further out than the questions. A reader who stops at step 2 has
learned what was looked into; one who stops at step 3 has the answer; the works themselves are for the
reader who asks for them.

**What this asks of an entry:**

- **Its heading is the question a reader might ask from the map**, and the answer may follow in the same
  line - *"How close does a farmhouse stand to the paddy? Up against it - but never on the bund"*, *"Is
  every farmhouse reached by a lane, and in what FORM?"*. A heading is the line the reader sees on the
  modal, so write it for them. The trailing bookkeeping - *"(researched 2026-08-27, feature 133 T41)"* -
  stays in the record and is stripped from the modal's text by `interactive/sources.py` (it is for us,
  not for them).
- **Its anchor is stable** (already the rule in README's "Adding to the record"): the modal links to the
  heading's GitHub anchor, so a rename must fix its inbound links - the rule files, and the class entries
  in `interactive/classes.py` that quote the heading.
- **A class's explanation names the entries it was written from** (`interactive/classes.py`, the `entry`
  field), and that pointer is the whole of what puts a question on a modal: the page resolves it at
  write time, so a new section reaches every map the moment a class entry names it. Nothing is re-typed.
- **The questions the GM has said they will add** are of this kind, in their words: *"how many farmers
  lived in each farmhouse, or why are there more rice plots than there are farmhouses, and how many rice
  plots were farmed by each farmhouse, or how many different types of crops were grown, that kind of
  thing."* Each is a research entry with its citations first, and only then a line on a modal. Feature
  180 added none of them - it shows only the questions the record already held (*"For now, you can just
  limit yourself to the questions that we already have"*); the GM will say at a later time which new
  questions they want added to what is shown.

## Four labels, and the GM's line between two of them (GM 2026-09-05, feature 183)

An entry's finding, and the class explanation written from it, carries one of FOUR labels (constitution
XII; `README.md` still lists the original three and is the GM's to update): **accurate**, **deviation**,
**convention**, **guess**. The GM's rule for the two in the middle, verbatim: a deviation is *"our
fictional setting being different from the actual history and historical places it is based on"*; a map
drawing convention is *"rendering glyphs on a map which are differently scaled or differently colored than
what the features would be in order to make the map more readable and legible to human eyes."* So the
oversized wellhead, the 6 ft hokora, the stand-level bamboo glyph, the dark bund beads and a stream drawn
by rank are CONVENTIONS; a hamlet with no headman, the 6:4 dike reading and the 30 ft trunk road are
DEVIATIONS. A convention's modal note is written in the GM's form - *"Note: we have rendered the bund
beans as ... in order to make them visible on the map at this scale"* - and ends with the real size or
color from the record, or says in so many words that it was searched for and not found. Write the word
the same way in the entry, the rule file, the code comment and the map's notes: since feature 183 the
record says "a map drawing convention" wherever it used to say "a deviation for legibility".

The mechanics of the page side - the anchor rule, the ordering, the button - are in
[`../l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md), "The references modal
lists QUESTIONS".
