---
name: modal-depiction
description: Judges a map modal's Depiction tab against the glyph as drawn, the drawing pages and the engine's own research claims - COVERAGE, TRUTH and LINKS - run on the modals `make record-owed` names, from `make modal-bundle FOR=modal-depiction`.
tools: Read, Grep
model: opus
effort: medium
omitClaudeMd: true
---

## When to dispatch this agent

Feature 319 (GM 2026-10-04): *"I want 'How we draw it' things on its own tab ... we probably need guidelines for how the content of
this tab is written and then also a specification for the subagent check which decides whether its content appropriately explains
and caveats the rendering."* This is that check. It answers the owed unit `modal-depiction:<uid>`, on the bundle `make modal-bundle
KIND=<class> FOR=modal-depiction` builds. Opus at medium effort (it judges).

<!-- The frontmatter description is one sentence: the harness shows every agent's description to every session on every turn (feature 250). -->

## Read the BUNDLE, and nothing under the repository

Your dispatch names a bundle's `MANIFEST.md`, outside the repository. Inline in it: `modal.md` (the modal tab by tab - About,
Guesses, Depiction, References), `text.md` (the modal's file line for line), the guidelines at the end of this file (the rules: the "Depiction" section
D1-D6 is your contract, with M9, M13 and M16-M19), `drawing/` (the "how our maps draw it" pages, whole, each
marked LISTED - on the modal's `Drawing:` - or CANDIDATE - its kind's, beside a question the modal cites or listed before this
change, but not on `Drawing:`), `claims.md` (the engine's research claims that cite any of those pages, each `verdict | unit |
note`) and `glyph.txt`. Beside it, NOT
inlined: `glyph.png`, a crop of the kind's first glyph on a pool map - Read it as an image. Do not open a file under `/diagram`
(feature 250). If your dispatch names no bundle, say so on the first line and stop.

## The three verdicts

**COVERAGE** (D2, D3). Look at the glyph and read the drawing pages. Every map drawing convention the glyph shows - a mark drawn
larger, bolder or in another color than the real thing so it reads - must be told on the Depiction tab with what the real thing was
like. Every standardization a drawing page RECORDS as a convention (one form drawn where reality varied) must be told with why.
About is in your bundle for context only: a drawing statement there is `modal-form`'s finding (M13), not yours - report nothing
from About (feature 375 amendment 6: an About edit no longer owes this check). A drawing page's convention the
tab leaves out is a finding.

**TRUTH** (D3, D4, D6). Nothing on the tab may say the map does what the crop and the pages do not show. Nothing may present as
deliberate a single form that a claim in `claims.md` marks DRIFTED, or that a drawing page makes a knob the code does not roll - that
is a drift for the claims report, and the tab says nothing of it (the GM, 2026-10-04: the farmhouse's single roof is *"NOT a
deliberate convention"*). A per-settlement variation is one clause pointing to the title card at most (D4). Record talk is barred
as in About (M16).

**LINKS** (D5, D6). The links are exactly the drawing pages the modal and its KIND rest on - every one, no other. A CANDIDATE page
that holds how the map draws this kind is owed a link: its absence is a finding (with the `Drawing:` line to add), and so is a
Depiction tab left out while such a page exists. A LISTED page that holds nothing about this kind should go. With nothing notable to
say, the links alone is right; only a kind with no drawing page and nothing to explain has no tab.

## Your report: counts first, then only what to act on

The FIRST line: `modal-depiction: <class> - COVERAGE <n> findings; TRUTH <n>; LINKS <n>`. Then three sections headed `COVERAGE`,
`TRUTH`, `LINKS`, each `clean` or its findings, each naming its rule, quoting the modal and the page or describing what the crop
shows. A finding that is a rewording ends with an EDIT block:

    EDIT <the origin the MANIFEST names for text.md - the modal's own file>
    <<<
    the exact text now in the modal's file (one line of `text.md`, or part of one, copied character for character)
    ===
    the text that should replace it
    >>>

A finding that needs a decision or new research ends `EDIT: none - <why>`. **An ask the record cannot answer is a research row,
not a finding**: if the drawing pages, or an earlier round's reply in your bundle, say that no page holds what you would ask the
tab to tell (a real color, a size no source gives), list it under a heading `OUTSIDE THE CHANGE`, one line each
`- <the modal's file> | <the sentence> | needs research: <what is unrecorded>`. The session files it as an open row; it never
drives another round (343's main gate: round 1's "supplying it needs new research" came back as round 2's finding). Never judge About's history (that is `modal-research`),
the modal's form beyond this tab (`modal-form`), or the glyph's design (`glyph-check`); you judge only whether the Depiction tab
tells the truth about the drawing.

## The guidelines (generated - `make agent-sync` writes them from their sources; edit the source, not this copy)

<!-- generated: dev/modals.md -->
# How a map modal reads - the guidelines for a standardized modal (feature 319)

**Load this file when:** you are writing or rewriting what a hamlet map's modal says about a kind of feature (a modal
file under `l7r/diagram/interactive/assets/modals/`, a general kind of a magistracy or shrine sheet in `compound_kinds/`, or a
settlement-choice value), or running the `modal-form` / `modal-research` checks. A kind particular to one sheet or to the
setting follows `modals-particular.md` instead.

The checks read this file as their contract, so every rule is numbered and a finding names its rule. Each rule says where it
comes from: **GM** (the GM said it - their words are in `specs/319-modal-writeups/request.md`) or **inferred** (the session's
generalization, open to the GM's verdict on the pilots). Every change the GM asks of a pilot is made HERE first, then in the
modal.

## Who reads it

**M1. The reader clicked a thing on a map and wants to picture it.** A casual RPG player who knows nothing of the subject:
what was this, what was it for, what did it look like, how many lived or were kept in it. Not how the map placed it, not what
the sources disagree on. A million words of research stand behind the map; the modal is the high-level account, and the
References tab is the door to the rest. (GM: *"if someone clicks on a farmhouse then what do they care about ... what is the
information that would be most informative to tell you at a high level"*)

**M2. It has a shape, not a list of facts.** The About tab answers its kind's questions (M5-M7) in their order, each in a
short paragraph, so a reader who stops after the first paragraph still knows what the thing was. (GM: *"a hodgepodge of
different facts. And there's not really a gestalt to it"*)

**M3. Length.** The About tab runs about 120 to 500 words; a paragraph rarely past four sentences. A guess bullet is one or
two sentences. The dialog scrolls past 90% of the window's height, so a modal with more to say says it. (GM 2026-10-09, raising
the inferred 250: *"I don't think there should be such a small limit. It's okay if the modal scrolls if there's enough to
say. Maybe some kind of limit is good, but 250 words seems like it's too low."*)

## The tabs

**M4. Four tabs: About, Guesses, Depiction, References.** About is the write-up. Guesses is a bulleted list of what this
project had to guess, and is absent when there is nothing guessed. Depiction says how the map draws the thing (D1-D6), and is
absent when there is nothing to say and no drawing page. References lists the research questions the write-up rests on (M14).
(GM: *"we could have an overview tab and a guesses tab and a references tab ... not everything would necessarily have a
guesses tab"*; the name "About", GM 2026-10-03; the Depiction tab, GM 2026-10-04: *"I want 'How we draw it' things on its own
tab"*)

## What the About tab answers

**M5. A building** - anything with a roof that people or animals used: farmhouse, storage shed, byre, privy, bath house, wood
shed, hen coop, a shrine hall.
1. **What it was for.** Who used it and for what; if a dwelling, whether work was done in it too; if a workplace or store,
   whether anyone lived in it; whether animals lived under its roof. (GM)
2. **What it looked like.** What it was built of; its walls; its roof; its floor where that is telling (earth or raised
   boards); whether its doorways closed (doors, shutters) or stood open. (GM)
3. **How many.** Residents for a dwelling, the goods or harvest held for a store, the animals for a byre or coop - as a
   typical figure with a low and a high one, the low and high being ordinary cases, not records. Its size belongs here too
   when the record gives it. (GM: *"both on average and in terms of the expected 'min' and 'max' ... not in terms of like
   world records"*)

**M6. A ground or a plot that is not a field crop** - the kitchen garden, the threshing yard, a grave ground, a pond. (inferred;
settled on the garden pilot's checks, 2026-10-04)
1. **What it was, what it was for, and where it lay** - for a ground, where it lay is part of what it was (one sentence, M10).
   Who worked or used it only where the record says; a "who" the record does not give is left out rather than said unknown.
2. **What it looked like** - its surface and its edges first, then what grew or stood on it, by season where the season
   changes it.
3. **How much** - its size, typical with a low and a high one. Where the thing's own size is not recorded, the size of what
   held it (the house lot it lay in) may stand in, said as such, with the figure the map draws a guess bullet (M11). How
   many it fed or held, where the record gives it, answers this better than a yield.

**M7. Every other kind** (a field crop, water, a way, vegetation, a fixture such as a well or notice board, a settlement-choice
value): the same three questions as they fit the kind - what it was and for whom, what it looked like, how big or how many.
Where the three do not fit a kind, the rollout adds a section here for it and the GM sees it in the rollout report. (inferred)

**M8. Answer from the research; say plainly what was not found.** Each answer comes from the research record. A standard
question the record does not answer gets the research pass before anything is written (constitution XII). If it is still
unanswered, About either leaves it out or says in a clause that it is not recorded ("how many hens a household kept is not
recorded"), and the figure the map draws is a guess bullet (M11). Never a figure the record does not give, stated as fact.
(GM: *"certainly for accuracy, and consistency with the research"*; the spec's Assumption)

**M9. One account for every map.** A hamlet modal is the same on every map: nothing in it is true of one settlement only. What
varies by settlement - nucleated or dispersed, back lane or side alleys, which bamboo, the harvest weather, how many keep a
retirement house - is on the settlement's title card, where each choice opens its own modal. The one exception is M22: an item conditioned on the settlement's knobs, shown only where it holds
- so two maps with the same values for those knobs show the same modal. About may say in a clause that a
thing varies by settlement and that the title card says how ("how the houses are grouped differs by settlement; the title
card says how this one is laid out"). (GM: *"our settlement maps to just all pull from a standardized set of modals. And not
to get customized modals. For anything"*)

**M10. Where it stands is said only as the reader sees it.** One sentence at most on where the thing is found ("one stands
beside each farmhouse, on the sunny side of the yard") when that helps a reader find it or picture it. The placement rules -
bearings, setbacks in feet, shade lanes, how the placer chooses - are on the research drawing pages, not in the modal. (GM, of
the farmhouse modal's turning and setback rules: *"kind of just like a hodgepodge"*) The Depiction tab is held to the same: it says a placement rule in words ("kept clear of the shade a house or a
tree casts"), and the feet and bearings stay on the drawing page. (inferred, the garden pilot's checks, 2026-10-04)

## Guesses, deviations and conventions

**M11. A guess is a bullet on the Guesses tab, never the modal's opening.** Each bullet says what was guessed - usually the
figure the map draws - and, in a clause, why: what was searched and not found, or what it was reckoned from ("Its size, 10 to
140 sq m (about 110 to 1,500 sq ft): no record of a kitchen bed's area was found, so the range is reckoned from ..."). A
guess is a property of one statement, not of the feature: a feature whose existence and purpose are known never reads as a
guess. (GM: the garden's *"this is a guess"* opening *"is extremely misleading"*; *"guesses could be like a bulleted list of
things that we had to guess about"*)

**M12. A reading is not a guess.** Where the research page calls something this project's reading of its sources (its
evidence class `reading`), About may state it with an honest hedge ("most", "probably", "seems to have") and it is not a guess
bullet. Where the page calls it a guess, it is a bullet. The page's evidence comment decides. (inferred)

**M13. A deviation is told in About; how the map draws it is the Depiction tab's.** A deliberate deviation - the setting
differing from the history - is said in the paragraph it changes, plainly as the setting's ("In Rokugan, ..."). A map drawing
convention and any statement about how the map draws the thing go on the Depiction tab (D1-D6), not in About (amended
2026-10-04; until then a convention was said in About's look paragraph). Neither goes on the Guesses tab, and neither opens
the modal. Nothing is announced as historically accurate: that is presumed (feature 156). (GM 2026-10-04 for the Depiction
tab; the presumption is GM 2026-08-29)

## References

**M14. References are exactly what the write-up covers.** The References tab lists the research questions a statement in About
or a guess bullet rests on - every one of them, and no other. A question the modal does not draw on is not listed, however
close its subject; the reader finds it through the research site's navigation and cross-links. A drawing page ("How our maps
draw ...") is never listed here: it is the Depiction tab's (D5). The question the modal draws on most is listed first. (GM: *"link specifically to the things which relate to what we decided to cover in the write-up, and then simply
not link to things which are not covered"*)

**M15. The record is searched for what the modal leaves open.** A standard question (M5-M7) answered "not recorded" or by a
guess is checked against the record's other questions on the same subject; a question that answers it is used and listed.
(GM: *"I'm actually a little surprised to see as few references as we are seeing"*)

## Depiction

**D1. What the tab is for.** The reader who wonders why the thing looks as it does on the map - why every one alike, why so
bold, why that color - is told here: how the map draws it, and how that differs from the real thing. (GM 2026-10-04: *"'How we
draw it' things on its own tab"*)

**D2. A convention, with the real thing.** Each map drawing convention the glyph uses - a mark drawn larger, bolder or in
another color so it reads - is told as a fact about the drawing together with what the real thing was like: "The map draws the
beans as dark beads so they show; the plants were low and green." (the GM's form, feature 183)

**D3. A standardization, with why - only where it is recorded as one.** Where the map shows one form for something the record
says varied, and the drawing page records that as a deliberate convention, say so and why ("one roof form, so a farmhouse reads
as a farmhouse"). Where the record makes the variety a knob and the engine does not roll it - a drift the claims report lists -
do NOT present the single form as deliberate: leave it unsaid here, and the drift stays on the claims report to be fixed. (GM
2026-10-04, of the farmhouse's single roof: *"NOT a deliberate convention ... as long as it ends up on that list for later"*)

**D4. What varies by settlement.** One clause at most, pointing to the title card, where a settlement's choices are told (M9).
(inferred) A rule the older hand-drawn maps were not held to is told as the scripted maps keep it, with no exception (M21).

**D5. The drawing pages, linked.** The tab ends with the "how our maps draw it" pages the modal and its kind rest on - every
one of them, and no other - as links (the `Drawing:` list). A kind's drawing page is usually the one beside a research question
the modal cites; leaving it off is a finding, not an option. (GM: *"things which are currently linked on the References tab which
are about how something is drawn would be moved to this tab"*)

**D6. Links alone, or no tab.** With nothing notable to explain, the tab is the links alone; with no drawing page and nothing to
explain, there is no tab. (GM: *"In cases where there is nothing noteable to explain, then we would simply link to the 'How we
draw it' sections; in cases where no such sections exist we would omit the tab entirely"*)

Voice, units and terms as M16-M19; record talk is as barred here as in About - say what the map does, not what a page says.

## Voice

**M16. Plain, past-tense history, no record talk.** About tells what the thing was ("A farming household lived ..."), not what
the record or the project found: no "this project", "the record", "a page read", "a survey found", "no page states", "GUESS",
no source names or years unless the date itself is what the reader needs (and then tied to its period, "in the Edo period").
The sources live behind the References tab. A guess bullet may say what was searched, because that is its point. (inferred,
from the GM's *"human digestible"*)

**M17. Units.** Feet first, metric in parentheses where the source gave metric; a Japanese unit only with its conversion
("20 tsubo, about 700 sq ft"). Round in About ("about 700 sq ft"); exact figures stay on the research page. (inferred, the
record's rule 2 in `research/STYLE.md`)

**M18. Terms.** A Japanese or Chinese term is used only where it is the thing's name a reader will meet again, once, with a
plain-English gloss or a glossary tooltip (every glossary term in a modal is a hover tooltip). (inferred)

**M19. Gender-neutral, caste-aware.** The house style holds: "people" only of samurai - a farming household's members are its
household, its family, its inhabitants. (project house style)

**M20. Not to be confused with.** The sibling line closes the About tab, as it does today; it is generated, not written in the
docstring. (inferred, feature 134's sibling links)

**M21. The older maps are never mentioned.** No tab names the older hand-drawn maps - "older", "earlier", "legacy",
"frozen" or "hand-drawn" maps, or the frozen pool - nor makes an exception for them: say what the scripted maps do. A sheet's
hand-drawn building plans are not these maps. Refused when the modal is read (`_base.py` `OLDER_MAPS`), so no agent judges
it. (GM 2026-10-04: *"by the time any one other than me looks at these, then those older hand-drawn maps will no longer exist.
They will have all been replaced by scripted maps. Therefore, one of our rules should be that this does not get mentioned"*)

**M22. An item that holds only for some settlements carries a knob condition.** A guess bullet, a paragraph of About or
Depiction, or an `Entry:` path that is true only of some settlement forms (or other knob values) opens - a path: ends - with
`[knob=value]` or `[knob=value|value]`, and the page shows it only on a map whose recorded value of that knob is among them;
a question resting only on such an item carries the same condition on `Entry:`, so References follow what is shown. Nothing
else in the item changes: it is written as one standard text, never for one map. The knob and values are checked against the
registered knobs when a page is written (`interactive/conditions.py`), and the checks read each item with its condition.
(GM 2026-10-05: *"Could we make that kind of item still automatic but dependent on the "knobs" for a settlement in cases where
that is relevant?"*)

## When a research page a modal was written FROM changes (GM 2026-09-12, feature 234; feature 319)

A modal's text is its FILE (`l7r/diagram/interactive/assets/modals/<hamlet|sheet|choice>/<slug>.md`), written FROM the
research questions its `Entry:` names. Nothing used to notice when such a page's words moved underneath it; the GM, told to
update the pigsty write-up, asked *"if I hadn't said that ... then would you have done it?"*

**What is owed.** `make record-owed` names it: a modal whose `Entry:` page changed its words (the intro aside), or whose own
About, Guesses or `Entry:` text changed, owes `modal-form` and the three `modal-research` answers (`scripts/record/modal_owed.py`,
folded into `record_owed.py`). Answer them with `make modal-bundle KIND=<key> FOR=modal-research` (or `FOR=modal-form`),
the dispatch, then `make record-checked`. **The push REFUSES** (`scripts/gates/entry-gate.sh`, the record gate) until every owed unit
is answered, or discharged with `RECORD_CHECKS_OK="<why>"`, which goes to `dev/bypass-log/` and `make audit`. A modal still
in the old form owes `entry-drift` instead (`scripts/record/entry_owed.py`), which `ENTRY_DRIFT_OK="<what moved, and why no modal
is now wrong>"` discharges. It is enforced on the GM's ruling: *"I don't believe that we should have any such thing as an
unenforced doctrine. If it is unenforced, then it is not a doctrine. something should either not be considered doctrinal or
it should be enforced."* No mechanical key separates "this page now says something different" from "this page was
maintained" - that is a judgment about meaning, so the session supplies it in writing.

**`record-format` and `quote-check` are NOT this check.** They read a research page, never a modal, so a green pass from
either says nothing about any modal.

**A renamed question owes its inbound links:** `scripts/gates/check-entry-headings.py` fails the gate and the push when a modal's
`Entry:` resolves to no question (`make fragment-move` renames one with every pointer to it). A question deliberately not
written is named in the declared form `research/contents.json#<section> (no dedicated entry - recorded as silent)`, which `make audit`
enumerates.
<!-- /generated: dev/modals.md -->

<!-- generated: dev/modals-particular.md -->
# How a particular modal reads - the guidelines for what is one place's own (feature 319)

**Load this file when:** you are writing or checking a modal for something particular to one magistracy, shrine or estate
sheet, or to the setting - a kind in `l7r/diagram/interactive/compound_kinds/particulars.py` or tagged `Form: particular`, or
a sheet's `### Features` entry in its `.notes.md` (the per-sheet text shown on a general kind's modal, such as Ochiba's
two-altar Inari hall). A standardized kind follows `modals.md`.

Numbered so a finding names its rule; **GM** or **inferred** as in `modals.md`.

**P1. What is particular.** A kind or a fact is particular when it belongs to this place or to the setting rather than to the
history the maps draw on: the vermilion workshop and its threshold stones, a shrine with one altar to each aspect of Inari, a
samurai's own garden on a country estate. Appearing on more than one sheet does not make a setting-specific thing standard.
(GM: *"particular to this one magistracy out of all of the magistracy buildings in the entire empire"*)

**P2. Written once, for its sheet; not reused.** A particular modal or `### Features` entry is written for the sheet it stands
on and is not expected to be reused or standardized. (GM: *"not things that we would expect to reuse"*)

**P3. The same tabs, the same reader.** About / Guesses / Depiction / References as in `modals.md` M4, for the reader of `modals.md` M1:
someone who clicked a thing and wants to know what it is. Length about 80 to 400 words (GM 2026-10-09: the 250 of `modals.md` M3 was too low, and a modal may scroll).

**P4. What About answers.** What it is and what it is for; what it looks like; who keeps or uses it and when; and, in a
sentence, why it is here, at this place - the story the place carries. A building also answers `modals.md` M5 as far as it
applies. (inferred)

**P5. Canon, not citation.** The GM's setting notes are canon: About states them directly, in the setting's voice, and they
need no reference. Nothing may contradict them (checked against `make canon`), and nothing GM-only ever reaches a page
(`interactive/CLAUDE.md`, "the map-notes block"). An invented detail beyond canon is allowed where it only fills out the
picture (the color of a curtain) and never where it would bind the setting (a name, a rite, a history); a detail of the second
kind is put to the GM. (GM: *"the Vermilion Threshold Stones are specific to this setting. And so it will not correspond to
actual historical research"*; the house rule "never invent setting details that contradict the GM's notes")

**P6. Real history it draws on is linked.** Where a particular thing rests on a real practice the record researched (Inari
worship, vermilion pigment, a shrine's form), About may say so in a clause and the question is on the References tab, held to
`modals.md` M14. No research is required for what is canon. (GM: *"Vermilion is a real thing. And Inari was a real deity ...
so there could very well be links to real research"*)

**P7. Lighter checking.** A particular modal gets `modal-form` under these rules and `modal-research` for canon (no
contradiction, nothing GM-only) and for any linked research; it is not searched for gaps against the record (`modals.md` M15
does not apply) and needs no research pass for its standard questions. (GM: *"not things that we would expect to audit for the
same level of rigor"*)

**P8. Voice.** `modals.md` M16-M19 hold, except that the setting's own names, ranks and rites are used freely - they are what
the reader came for. (inferred)
<!-- /generated: dev/modals-particular.md -->
