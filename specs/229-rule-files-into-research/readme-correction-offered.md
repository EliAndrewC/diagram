# The `research/README.md` correction, offered to the GM (feature 229) - APPLIED

*The GM authorized it on 2026-09-12: "I authorize you to fix the research readme." Applied that day, with the
Mode A paragraph written to their ruling of the same message. The text below is what was offered.*

A README is the GM's to write (constitution XVII, NON-NEGOTIABLE): *"If a README is factually wrong, say so and
offer the correction rather than making it ... a genuine exception is the GM's to make."* The GM's words on
2026-09-12 were about the rule files and the references to them; they did not name this README, so this feature
did not edit it. `research/README.md` is left exactly as it stands, and `tests/interactive/test_record.py` keeps
it exempt from the retired-file rule until the GM applies or declines what follows.

## What is now wrong in it

1. **The opening paragraph** says the findings ground *"Every rule in the `../settlements/` and `../buildings.md`
   docs"* and that *"The rule files stay operational; this tree is where the reasoning lives"*. The `settlements/`
   rule files no longer exist; each research page now holds the rule as well as the reasoning, and for a tier no
   generator draws yet it holds the specification too. `buildings.md` (Mode A) is unchanged and still operative.
2. **The pairing table** ("Research file | Grounds the rules in") has fifteen rows, fourteen of which point at a
   deleted `../settlements/*.md`. Four research pages are also missing from it, because they did not exist:
   `settlements.html`, `ways.html`, `presentation.html`, `cities/sizing.html`.
3. **"Load a research file when you are CHANGING a rule, questioning one, or adding to the record - never merely
   to draw a map"** is now only half true. It holds for the scripted hamlet tier, whose rules are in the engine.
   For a tier that is still hand-authored, the research page IS the operative document and is loaded to draw.

## The replacement text, if the GM wants it

Replace the opening paragraph, the load line and the table with:

```markdown
# Research: the historical basis behind the /diagram rules

*Every rule about how a place was built, farmed or lived in has its finding recorded here - what the research
found, the decision it drove, and any deliberate departure from literal reality. Since feature 229 the pages
hold the rule as well: for a scripted tier the number lives in the engine at its point of change and the page
carries the finding and the decision; for a tier no generator draws yet the page also carries the
specification a map follows, marked `class="spec"`, which moves into the generator when one is written. Mode A
compound plans keep their operative document, [`../buildings.md`](../buildings.md).*

**Load the page for the topic you are changing or questioning** - and, for a hand-authored tier, to draw.
A scripted hamlet needs none of it to run. Pointers link in by stable `#anchor`.

| Research file | What it records |
|---|---|
| [`settlements.html`](settlements.html) | the five tiers: what each is, what a map's page states about it, the facts a map is told at intake, and when a rule may be waived |
| [`archetypes.html`](archetypes.html) | the field archetypes - polder, dike-pond, contour terraces, ribbon valley - and the land-use overlays |
| [`buildings.html`](buildings.html) | Mode A: the compound and building plans |
| [`cities.md` tier pages](cities/) | `capitals.html`, `defenses.html`, `fabric.html`, `government.html`, `hinterland.html`, `river-cities.html`, `sizing.html` |
| [`fields.html`](fields.html) | cultivated ground: the comb fan, plots, crops, in-field features, the near ring |
| [`homesteads.html`](homesteads.html) | farmhouses and their appurtenances, groves, settlement form |
| [`presentation.html`](presentation.html) | the map's drawing conventions: labels, captions, framing and cropping |
| [`religion-and-death.html`](religion-and-death.html) | shrines, temples, graveyards and the funerary features |
| [`towns.html`](towns.html) | the town tier |
| [`urban-features.html`](urban-features.html) | the vocabulary a town and a city share: boards, justice works, trades, wells, stable yards |
| [`vegetation.html`](vegetation.html) | the shelter belt, groves, commons, scrub and bamboo |
| [`water.html`](water.html) | flow, channels, moats and wetland |
| [`ways.html`](ways.html) | roads, lanes, bridges and planks |
```

(The `cities/` row is written as one line because the seven city pages share a directory; the GM may prefer
seven rows.)

Nothing else in the README is affected: the entry format, the evidence classes, the citing rules and the
"Adding to the record" section are all still accurate.
