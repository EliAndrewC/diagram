# Research: the historical basis behind the /diagram rules

*Every rule about how a place was built, farmed or lived in has its finding recorded here - what the
research found, the decision it drove, and any deliberate departure from literal reality. Since feature
229 (GM 2026-09-12) the pages hold the RULE as well: for a scripted tier the number lives in the engine
at its point of change and the page carries the finding and the decision; for a tier no generator draws
yet the page also carries the specification a map follows, marked `class="spec"` and written in real
feet, which moves into the generator when one is written.*

*Mode A is deliberately NOT like that (GM 2026-09-12: "the original set of markdown rules being separate
from research continues to make sense for the diagrams that we are generating by hand"). A compound plan
is placed by a person rather than by a generator, so [`../buildings.md`](../buildings.md) stays
operational and [`buildings.html`](buildings.html) carries only its reasoning.*

**Load the page for the topic you are changing or questioning** - and, for a hand-authored tier, to
draw. A scripted hamlet needs none of it to run. Pointers link in by stable `#anchor`.

| Research file | What it records |
|---|---|
| [`settlements.html`](settlements.html) | the five tiers: what each is, what a map's page states about it, the facts a map is told at intake, and when a rule may be waived |
| [`archetypes.html`](archetypes.html) | the field archetypes - polder, dike-pond, contour terraces, ribbon valley - and the land-use overlays |
| [`buildings.html`](buildings.html) | Mode A: the reasoning behind the compound and building plans, whose rules stay in [`../buildings.md`](../buildings.md) |
| [`cities/`](cities/) | the city tier: [`capitals.html`](cities/capitals.html), [`defenses.html`](cities/defenses.html), [`fabric.html`](cities/fabric.html), [`government.html`](cities/government.html), [`hinterland.html`](cities/hinterland.html), [`river-cities.html`](cities/river-cities.html), [`sizing.html`](cities/sizing.html) |
| [`fields.html`](fields.html) | cultivated ground: the comb fan, plots, crops, in-field features, the near ring |
| [`homesteads.html`](homesteads.html) | farmhouses and their appurtenances, groves, settlement form |
| [`presentation.html`](presentation.html) | the map's drawing conventions: labels, captions, framing and cropping |
| [`religion-and-death.html`](religion-and-death.html) | shrines, temples, graveyards and the funerary features |
| [`towns.html`](towns.html) | the town tier |
| [`urban-features.html`](urban-features.html) | the vocabulary a town and a city share: boards, justice works, trades, wells, stable yards |
| [`vegetation.html`](vegetation.html) | the shelter belt, groves, commons, scrub and bamboo |
| [`water.html`](water.html) | flow, channels, moats and wetland |
| [`ways.html`](ways.html) | roads, lanes, bridges and planks |

## Every entry carries one of three labels (GM 2026-08-26, constitution XII)

**accurate** (the record says so - cite the finding), **deviation** (drawn other than the record
says, and why: legibility, showing the feature type, L5R canon, a priced trade-off), or **guess**
(the record is silent or has no firm number; this is our reasoning). The interactive HTML map exists since feature 134 (`pool/<tier>/<map>.html`; the class explanations in `l7r/diagram/interactive/classes.py` are written FROM these entries and carry their labels) - and the map the
project is building toward will show a reader exactly this: a player clicks a feature and is told
which of the three it is. An entry that presents reasoning as a finding is the one failure.

## Entry format

Every entry carries the same four fields, in this order - two of them HTML comments, because they are notes
for a session and not for the reader (GM 2026-09-07, feature 209; the reader-facing form is
[`CLAUDE.md`](CLAUDE.md), "Written for the reader"):

```
<h2 id="<stable anchor>">The question a reader would ask from the map - and, often, its answer</h2>
<!-- researched YYYY-MM-DD, feature NNN Tnn -->
<!-- Grounds: the checks, generator methods or constants this finding justifies -->
<!-- Evidence: <one or more classes, see below> -->
<p><strong>Sources:</strong> <a href="..."><code>key</code></a> (what the work contributed), <a href="..."><code>key</code></a></p>

<the finding: what the research found, the decision it drove, and any disclosed departure - every assertion
footnoted (CLAUDE.md, "A reference QUOTES the passage"), every term a reader would not know a glossary tooltip,
nothing addressed to a session outside a comment, nothing about what the entry used to say>
```

Every key in `SOURCES.html` carries the URL where the source can be read (constitution v2.13.0, GM
2026-08-28), or `URL: none - <why>` - and what the work is and why it applies with its limits, the two write-ups
the citations pages derive their works section from.

`Grounds:` is what makes a stale finding visible - if nothing in the codebase matches it any more, the entry
is describing a rule that no longer exists. It is a comment so that it can say so in code's own names; a
knob's code name, a constant or a function in the BODY goes into a comment too (`<!-- _grove_arm_rect -->`
beside the sentence that describes the drawn arm).

## Evidence classes

The vocabulary is fixed, and an entry may carry several (they compose - a finding can be `attested` in one tradition, `corroborated` by the other, and still applied as a `liberty`):

| Class | Means |
|---|---|
| `attested` | A specific historical instance, figure or statute is named. The strongest class. |
| `corroborated` | Both reference traditions agree (China-first with Japan agreeing, or the reverse). |
| `analog` | The figure is borrowed from an adjacent domain and flagged as such - e.g. the Willow Palisade spacing standing in for a polder dike, where no polder-specific statute was found. Treat as weaker than `attested`. |
| `interpolated` | Reasoned from a related or aggregate figure rather than a direct one - e.g. a national average narrowed to one village type. |
| `reconstruction` | Reasoned from norms with no direct source. Honest inference, not evidence. |
| `setting-canon` | Rests on `l7r.md` / `budgets.md` rather than on history. Not weaker - just a different authority, and it outranks history where the two disagree. |
| `liberty` | A deliberate, disclosed departure from the historical answer, taken for legibility or game reasons. Always paired with whatever the history actually said. |
| `researched` | Research was done in-session but its class was never recorded. A backlog marker: sharpen it when the entry is next revisited. |

The classes were seeded from each entry's own language and hand-set for the entries reviewed closely; **correct one when you revisit its entry** rather than trusting it blindly.

## Citing

Sources live in [`SOURCES.html`](SOURCES.html) with stable keys; an entry cites by key, in a footnote whose note is on the page's citations page (`citations/<name>.html`; the research page keeps the reference and loads the derived `citations/<name>.js` for the hover - run `make citations` after a note changes). Every registry entry a footnote cites carries two write-ups after its citation line - `<p><em>What it is:</em> ...</p>` and `<p><em>Why it applies, and its limits:</em> ...</p>` - written once and derived into the works section of every citations page that cites it; a key without them fails the gate, and the `source-applicability` agent judges the source before its numbers reach a map and when its write-ups land ([`CLAUDE.md`](CLAUDE.md), "The notes live on a CITATIONS PAGE"). **Never add a citation that has not actually been consulted** - if a finding's source was not written down at the time, its `**Sources:**` line says `not recorded` and that is the correct, honest state. Feature 143 (2026-08-28) re-sourced every entry that said so - 73 of them, plus 44 that had no sources line - so no entry says `not recorded` any more; where a page could not be read the line says what was searched and labels the claim SUMMARY-ONLY or a guess, and `SOURCES.md`'s queue lists those. A new entry never says `not recorded`: it cites, or it says what was searched and not found.

Named real-world measurements (Suzugamori, Pingyao, Himeji, Fushimi...) are *anchors* rather than works - they are listed in a separate table in `SOURCES.html` and cited inline by name.

## Adding to the record

Keep the four fields. Anchors are stable - rules link to `#slug`, so rename a heading only if you also fix its inbound links. Citations belong here rather than in the rule file: per project policy the *why* is mandatory and explicit sources are optional, so a bare finding is fine and a cited one is better. When a finding CHANGES, rewrite the entry to say the finding - never annotate it with what it used to say or when it was corrected (feature 209): the old wording lives in git, and `tests/interactive/test_record_format.py` fails on the shapes of that annotation. A new term gets its definition in `interactive/glossary.py` and a `make glossary`.
