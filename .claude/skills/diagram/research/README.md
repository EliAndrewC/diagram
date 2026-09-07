# Research: the historical basis behind the /diagram rules

*Every rule in the [`../settlements/`](../settlements/) and [`../buildings.md`](../buildings.md) docs that came out of historical research has its finding recorded here - what the research found, the decision it drove, and any deliberate departure from literal reality. The rule files stay operational; this tree is where the reasoning lives, and where citations and deeper historical context get added as they accumulate.*

**Load a research file when you are CHANGING a rule, questioning one, or adding to the record** - never merely to draw a map. Rules link in by stable `#anchor`.

| Research file | Grounds the rules in |
|---|---|
| [`archetypes.html`](archetypes.html) | [`../settlements/archetypes.md`](../settlements/archetypes.md) |
| [`buildings.html`](buildings.html) | [`../buildings.md`](../buildings.md) |
| [`cities/capitals.html`](cities/capitals.html) | [`../settlements/capitals.md`](../settlements/capitals.md) |
| [`cities/defenses.html`](cities/defenses.html) | [`../settlements/cities/defenses.md`](../settlements/cities/defenses.md) |
| [`cities/fabric.html`](cities/fabric.html) | [`../settlements/cities/fabric.md`](../settlements/cities/fabric.md) |
| [`cities/government.html`](cities/government.html) | [`../settlements/cities/government.md`](../settlements/cities/government.md) |
| [`cities/hinterland.html`](cities/hinterland.html) | [`../settlements/cities/hinterland.md`](../settlements/cities/hinterland.md) |
| [`cities/river-cities.html`](cities/river-cities.html) | [`../settlements/cities/river-cities.md`](../settlements/cities/river-cities.md) |
| [`fields.html`](fields.html) | [`../settlements/fields.md`](../settlements/fields.md) |
| [`homesteads.html`](homesteads.html) | [`../settlements/homesteads.md`](../settlements/homesteads.md) |
| [`religion-and-death.html`](religion-and-death.html) | [`../settlements/religion-and-death.md`](../settlements/religion-and-death.md) |
| [`towns.html`](towns.html) | [`../settlements/towns.md`](../settlements/towns.md) |
| [`urban-features.html`](urban-features.html) | [`../settlements/urban-features.md`](../settlements/urban-features.md) |
| [`vegetation.html`](vegetation.html) | [`../settlements/vegetation.md`](../settlements/vegetation.md) |
| [`water.html`](water.html) | [`../settlements/water.md`](../settlements/water.md) |

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
2026-08-28), or `URL: none - <why>`.

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

Sources live in [`SOURCES.md`](SOURCES.md) with stable keys; an entry cites by key. **Never add a citation that has not actually been consulted** - if a finding's source was not written down at the time, its `**Sources:**` line says `not recorded` and that is the correct, honest state. Feature 143 (2026-08-28) re-sourced every entry that said so - 73 of them, plus 44 that had no sources line - so no entry says `not recorded` any more; where a page could not be read the line says what was searched and labels the claim SUMMARY-ONLY or a guess, and `SOURCES.md`'s queue lists those. A new entry never says `not recorded`: it cites, or it says what was searched and not found.

Named real-world measurements (Suzugamori, Pingyao, Himeji, Fushimi...) are *anchors* rather than works - they are listed in a separate table in `SOURCES.md` and cited inline by name.

## Adding to the record

Keep the four fields. Anchors are stable - rules link to `#slug`, so rename a heading only if you also fix its inbound links. Citations belong here rather than in the rule file: per project policy the *why* is mandatory and explicit sources are optional, so a bare finding is fine and a cited one is better. When a finding CHANGES, rewrite the entry to say the finding - never annotate it with what it used to say or when it was corrected (feature 209): the old wording lives in git, and `tests/interactive/test_record_format.py` fails on the shapes of that annotation. A new term gets its definition in `interactive/glossary.py` and a `make glossary`.
