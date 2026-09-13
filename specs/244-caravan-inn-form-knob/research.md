# Feature 244 - research notes

## R1 - the stable-behind-the-inn passage has a page, and it is weaker than the record implied (2026-09-13)

Feature 238's R2a kept one passage for the arrangement the town maps draw - inn in front, stable behind -
as *"a dictionary usage example"*, without recording which page carried it. A `source-reader` found it:
**kotobank's 馬宿 page, in the 精選版 日本国語大辞典 block, sense ③**, public at HTTP 200 with no login
wall. The page's own characters carry ruby readings the record had dropped:
「表は旅人宿(はたごや)で、裏には大きい厩(うまや)があって馬宿(ウマヤド)もする」.

**What it attests, exactly.** The dictionary defines the sense - 「自分の馬に乗って旅をする人が宿屋に泊まる
とき、その馬を宿で預かること。また、そういう設備のある宿屋。」, an inn taking a traveler's own horse into its
keeping, or an inn with the facilities to - and cites the sentence as 初出の実例, the word's EARLIEST
ATTESTED EXAMPLE, from Mori Ōgai's *Nagashi* of **1913**. So it is evidence of the word's meaning and of
a 1913 novelist's picture of such an inn, not a description of an Edo-period building. The Digital
Daijisen block on the same page agrees on the definition and carries no example.

**What that does to the spec.** The draft of FR-004 and D4 said a large stable behind a Japanese
travelers' inn *"IS attested"* on this passage. That overstates it. What is attested is that a Japanese
inn keeping travelers' horses was a recognized kind with a name of its own, and that the front-inn,
back-stable picture was natural enough in 1913 to be the dictionary's illustration. The `hatago` form's
stable stays labeled as it must be: the arrangement rests on a definition plus a literary sentence,
and the cart yard and feeding trough on nothing Japanese at all.

**A lead, not taken here.** Weblio's page for the same word carries a national cultural-property entry,
「奥会津の山村生産用具及び民家（馬宿）」 - an 1801 farmhouse in Minamiaizu with a two-stall stable and a
hearth for boiling fodder. A physical horse-keeping inn of the period, not fetched, and the first thing
a later pass on this section should read.

<!-- The reader's full report: two kotobank fetch prompts agreed character for character on sense ③ and
     the example; Weblio has the Daijisen senses and the Fukushima entry but not the Ōgai citation. -->

## R2 - the roll has a home, and the plan's push has a tangle (2026-09-13)

**The roll.** The first spec deferred it to a future town generator on the claim that a glyph has no
seed. The spec review found the precedent three files away: `byre_form`, a two-value form knob
registered with a default and resolved INSIDE its drawing method by `Settlement.resolve()` - pinned,
else rolled from the map's seed, else the default - and declared to the manifest's `meta` so the gate
can hold the drawing to it. `caravan_inn_form` takes that shape. Over seeds 1 to 12 the unpinned roll
produces both values, which the test asserts, because a knob one value of which never rolls is a
ruling wearing a knob's name.

**The drawing.** `wagon` is the glyph as it stood after 2026-09-12. `hatago` draws an upper row of the
lattice windows under the roof, the eave between the floors, and the ground-floor row above the noren.
The plan review noted, accurately, that the pre-2026-09-12 shape was ONE raised row under a band that
merely read as a second story; two rows and a band read as one without the reader having to infer it,
which is what the spec asked for.

**The push tangle.** This clone's delta carries 242's accepted amendment (its D1 ruling) beside 244's
engine work, and 242 has twenty-two open tasks. The push refuses any delta that touches an in-progress
feature's `specs/` unless it is that directory ALONE, so the combined delta cannot land in either order.
The way through that rewrites no history: before 244's push, restore `specs/242` to main's state in a
forward commit (the amendment stays in this clone's history); land 244; then re-apply the amendment
from that commit and push it as 242's `specs/` alone. Three pushes' worth of mechanics for one
sentence of the GM's - recorded so the next session that amends a spec while another feature is
mid-flight in the same clone knows to commit the two on different days, or to push the amendment
before opening the engine work.

## R3 - what the checks found on the rewritten section (2026-09-13)

**`quote-check`.** fn-30's two kotobank passages are VERBATIM on the page, ruby parentheticals
included; the definition SUPPORTS the sentence it hangs on in full. Two PARTIALs, both applied: the
sentence on the post-station inn generalized to the type where the note supports one building, so it
now says the inn is *drawn* two-story *on its own analogue*; and the prose called the 1913 sentence the
earliest example of the WORD where the page dates older senses to 1677 and 1682 - it is the earliest
example of that SENSE, and says so now. The roster's "what a post-station inn does not have" claimed
evidence from silence and now says silence.

**The one unfootnoted assertion, and why it matters beyond this section.** The section's first
sentence - a county seat sits on its trade route and keeps a caravan inn for it - carried no footnote,
only a roster disclosure. That sentence is homesteads report item 148, and feature 242's work-list
filter subtracts it as *"the caravan inn (one bare item ... closed by 238)"*. 238 closed the inn's
story count; it never footnoted the premise. So the subtraction was true of the glyph and false of the
sentence. It carries an absence note now (fn-31), in the never-searched form - no query of its own was
run for it here, and a knob feature is not the place to invent one - which puts it where it belongs:
in 242's D1 population, the never-searched notes the GM ruled in scope, rather than dropped between
two features. 242's `hedged-worklist-max` bound still holds (a subtracted item stays subtracted; it
returns as a D1 note instead of a bare sentence).

**fn-22 and fn-25 came back NOT-READABLE**, the Jilin Daily host refusing an automated fetch on the
HTTPS upgrade of a plain-HTTP link. The record's rule stands - public is the GM's test, not the
container's - but a page served only over plain HTTP will fail this check every time it is run. Nothing
changed here; noted so the next reader does not spend a round on it.

**`record-format`.** Seven vocabulary items: `post-station` did not match the glossary's `post station`
(a hyphen; five occurrences got no tooltip), fixed as a variant of `shukuba`; `wagon inn`, `Tokaido`,
`knob` and `Taisho` added; `Minamiaizu` and `Sanuki` taken out of the write-up by rewording rather than
defined, since the record says nothing about where either is. One session note in the new write-up -
*"known and not yet read"*, a fetch state - moved into a comment with its substance kept visible. No
history in the visible prose. Two things outside the brief it flagged and this feature fixed under
Principle XIV: the `hatago` glossary definition described only the humble shophouse form and pulled
against "Tokaido hatago", now widened; and the neighboring `okabe-hatago-jawiki` write-up narrated why
the source was sought, which is document history, now cut.

**One collision the glossary term caused.** The synthetic record page the browser tests run on used
"knob" as filler text; wrapping it broke a hardcoded expectation. The filler word changed, not the term.
