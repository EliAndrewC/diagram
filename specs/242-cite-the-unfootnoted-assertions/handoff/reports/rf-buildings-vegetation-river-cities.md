# `record-format` report

**Read:** `/diagram/.clones/diagram-research/.claude/skills/diagram/research/buildings.html` (158 ll.), `research/vegetation.html` (564 ll.), `research/cities/river-cities.html` (98 ll.); their citations pages `research/citations/buildings.html` (295 ll.), `research/citations/vegetation.html`, `research/citations/cities/river-cities.html` (170 ll.); the glossary `/diagram/.clones/diagram-research/.claude/skills/diagram/l7r/diagram/interactive/assets/glossary.json` (476 terms); and the `<!-- READ 2026-09-14 by a source-reader (feature 242) -->` band of `research/SOURCES.html` (250 entries, ll. 411-1656, sampled + pattern-scanned end to end).

Two structural notes before the sections. (1) The 2026-09-14 READ markers are themselves already HTML comments at the head of each citation line - nothing to report about them. (2) `research/assets/record.js` builds its glossary regex with flags `giu` (line 58), so **every match is case-insensitive**; that is load-bearing for one defect below.

---

# 1. `research/buildings.html`

## Page head - title, `<h1>`, lead (ll. 6, 14, 15)

**SESSION NOTE** - `Historical grounding: the "why" behind the Mode A realism checks` (the `<title>`, the `<h1>` and, derived, both citations-page headings).
"Realism checks" names the tooling; "Mode A" is the engine's internal name for the compound-plan half of the skill. A reader clicking "See references" meets a heading about our checks rather than about a place. Proposal: **comment** the internal phrasing and retitle for the reader (the session's wording call), e.g. `The magistrate's manor: what a county compound held, and why it is laid out this way`. Note the h1 anchor is `historical-grounding-...`; a rename owes its inbound links (`interactive/classes/` `Entry:` tags and `check-entry-headings.py`).

**VOCABULARY** - `Mode A`
> "The Mode A scale is 3 px = 1 ft" (l. 91 heading); "the Mode A realism checks" (l. 14).

Draft definition (from this page l. 95 and the skill's own division): *"Mode A - the building-plan half of these maps: one walled compound drawn at three times the detail of a settlement map (a compound sheet at a third of a foot per pixel, a hamlet or town at one, a village at two, a city at three)."* The glossary already carries project terms of this class (`tier`, `the pool`, `knob`, `fit zoom`), so a term is the consistent fix; dropping the phrase from the visible headings is the alternative.

**VOCABULARY** - `L7R`
> "the Japanese civilian form leads, scaled to L7R demographics" (l. 24); "Scaled to an L7R county (~6,800 inhabitants ...)" (l. 46); "The L7R numbers force the same conclusion from inside the setting" (l. 142).

Draft: *"L7R - the GM's own edition of the Legend of the Five Rings setting these maps are drawn for; its demographic notes are the record's canon rather than its evidence."* The glossary defines `Rokugan` in that role already, so replacing `L7R` with `the setting` / `Rokugan` in prose is the cheaper fix.

**HISTORY** - none. **DEFECTS** - none here.

## "Administrative culture is JAPAN-first for compound interiors" (ll. 20-24)

**VOCABULARY** - none owed (`daikansho`, `jin'ya`, `machi-bugyōsho`, `yamen`, `kura` are all in the glossary; `machi-bugyosho` carries the macron variant).
**SESSION NOTE** - none visible (`Grounds:`/`Evidence:` are comments, l. 21-22 ✓).
**HISTORY** - none visible (`<!-- re-sourced 2026-08-28, feature 143 -->` is a comment ✓).
**DEFECTS** - see the file-wide roster-shape item at the end of this file.

## "Office in front, residence behind - the two-court split is universal" (ll. 25-29)

**DEFECT** - untranslated foreign quotation in visible prose.
> `<code>neixiang-yamen-zhwiki</code></a> ("前衙后邸…前朝后寝制度" - office in front, residence behind, as regulation)` (l. 28)

The record's own rule gives the English translation first, marked as one, with the original following as the checker's anchor. The marked translation already exists on the citations page (`citations/buildings.html` fn-8: 「the county yamen's architectural layout of "office in front, residence behind" fully embodies the ancient system of "court in front, sleeping quarters behind"」 ... original: 「县衙的前衙后邸的建筑格局充分体现了古代的前朝后寝制度」). Proposal: carry that English in the roster and drop the raw string (or move it into a comment).

**VOCABULARY / SESSION NOTE / HISTORY** - none.

## "Every administrative compound keeps a shrine" (ll. 30-35)

**DEFECT** - a wrong tooltip fires on a proper noun.
> "Ochiba's two-altar hall is the deliberate exception, justified by its priest-magistrate." (l. 34; also "Ochiba 267×200 ft" l. 95 and "Ochiba's cell and barracks" l. 121)

`glossary.json` defines **`ochiba`** = *"Fallen leaves: the forest litter raked off a coppice wood's floor and carried to the paddies as fertilizer"*, and `record.js` matches case-insensitively, so the manor's name is wrapped with the leaf-litter definition in three places on this page. Proposal for the session: decide between narrowing the `ochiba` variants (it is also used correctly, as `forest litter (ochiba)` in `vegetation.html` l. 382) and leaving the collision; either way it is a reader-visible wrong answer today, not a wording matter.

**VOCABULARY** - `Inari-sha` and `yamen-god, earth-god, jail-god`: `defined inline` (`Inari` is in the glossary and matches inside `Inari-sha`).
**SESSION NOTE / HISTORY** - none visible (the 2026-08-28 re-sourcing note is a comment, l. 35 ✓).

## "Cells are remand, not punishment" (ll. 36-41)

**DEFECT** - a work named to the reader only in Japanese.
> "(<a ...>ja.wikipedia 伝馬町牢屋敷</a> names 永牢 (*eiro*) and 過怠牢 (*katairo*) as real, if exceptional, prison-as-sentence categories ...)" (l. 40)

The link text is the only name the reader gets; the registry's own write-up calls it "the Tenmacho jail" (`citations/buildings.html` l. 36). Proposal: `ja.wikipedia, the Tenmachō jail (伝馬町牢屋敷)`. `eiro` and `katairo` are both in the glossary ✓.

**VOCABULARY** - none further (`daikan`, `eiro`, `katairo` ✓).
**SESSION NOTE** - none visible.
**HISTORY** - none visible; the correction of 2026-08-28 is a comment (l. 41 ✓).

## "Clerks are few, local, and heimen" (ll. 42-47)

**VOCABULARY** - none owed (`tedai`, `heimen`, `koku` ✓); `L7R` as above.
**SESSION NOTE / HISTORY** - none visible (the struck "second sons" gloss is a comment, l. 47 ✓).

## "Staff housing spans a real spectrum" (ll. 48-52)

**VOCABULARY** - none owed (`yoriki`, `doshin`, `kumi-yashiki`, `jin'ya`, `nagaya` ✓).
**DEFECT** - roster run-on (file-wide item, l. 51).
**SESSION NOTE / HISTORY** - none visible.

## "A compound wall is a building, not a boundary line" (ll. 53-59)

**DEFECT** - a clause with no main verb of its own, reading as an unfinished edit.
> "Buildings ringing a jin'ya court back onto that wall - eaves nearly touching, rear wall a foot or two off it so the two roofs shed separately and the wall stays reachable for patching - they touch the wall and never cross into it." (l. 57)

As it would then read: *"Buildings ringing a jin'ya court back onto that wall: eaves nearly touching, the rear wall a foot or two off it so the two roofs shed separately and the wall stays reachable for patching. They touch the wall and never cross into it."*

**VOCABULARY** - `neribei`, `dobei`, `tsuijibei` all covered by one glossary entry ✓; `shaku`, `coping` ✓.
**SESSION NOTE** - none visible; the `pack_audit.structures_on_walls` pointer and the 2026-07-24 incident are comments (ll. 54, 57 ✓).
**HISTORY** - none visible; the CONTRADICTED note is a comment (l. 58 ✓). The GM ruling of 2026-08-28 (l. 59) is the decision the reader is owed - **keep**.

## "The granary is a staging node, not the terminal store" (ll. 60-64)

**VOCABULARY** - `Hida`
> "Remote, high-transport-cost territory kept large on-site granary rows instead (Takayama's onkura, staged for all of Hida - the staging is unsourced)." (l. 64)

Draft (from `citations/buildings.html` l. 24, the `takayama-jinya-jawiki` write-up): *"Hida - the mountain province of central Japan, held under direct shogunal rule and administered from Takayama, whose intendancy is the one such compound that survives."*

`onkura` is a variant of `kura` ✓; `bailey` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none beyond the roster shape (l. 63).

## "The courtroom is a room of the office hall, not a freestanding stage" (ll. 65-69)

**VOCABULARY** - `goyakusho`, `ohiroma`, `shirasu`: `defined inline` (l. 68 glosses the four terms in order; `genkan`, `ginmisho`, `goyōba` and `shirasu` (under `oshirasu`) are in the glossary besides).
**DEFECT** - raw Japanese run in the roster (grouped in the file-wide translation item).
**SESSION NOTE / HISTORY** - none.

## "No interrogation room" (ll. 70-74)

**DEFECT** - untranslated foreign quotation in visible prose.
> `("吟味所、白州はグリ石敷で屋根のあることが特徴的である" - the examination room beside the roofed court)` (l. 73)

The marked translation exists at `citations/buildings.html` fn-37: 「The examination room (ginmisho) and the shirasu (white-gravel court) are distinctive in being paved with guri stone (cobbles) and in being roofed.」 Proposal as for l. 28.

**SESSION NOTE** - the `Grounds:` line "a deliberate omission - do not re-add; GM decision 2026-07" is already a comment (l. 71 ✓) - correct, and worth noting as the model for the rest.
**VOCABULARY / HISTORY** - none.

## "Poverty texture is historically genuine" (ll. 75-80)

**SESSION NOTE** - none. The roster's "none found (searched 2026-08-28: 代官 借財 役所経費 不足, daikan debt - ... ) - a GUESS" is the honest label on a guess and the record of a search: **not** a session note, keep as is.
**VOCABULARY / HISTORY / DEFECTS** - none.

## "Guest doors feed courts, not flanks" (ll. 81-85)

**VOCABULARY** - `postern`, `genkan` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none visible (the Hayakawa first-draft story and the "natural `guest_doors_feed_courts` check" are in a comment, l. 85 ✓).

## "An ancestral alcove ... only at a LINEAGE-HELD posting" (ll. 86-90)

**VOCABULARY** - `mingguanci`: `defined inline` ("a STATE hall for meritorious local officials, not a shrine inside the yamen"). `lineage` is in the glossary ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none.

## "The Mode A scale is 3 px = 1 ft" (ll. 91-95)

**VOCABULARY** - `Mode A` (above).
**DEFECT** - untranslated quotation in the roster: `(the designated site, "員数 11,219.05平方メートル" - ~9,800 m2 without the front plaza)` (l. 93). `citations/buildings.html` fn-65 carries the marked translation and the whole parcel derivation; the roster can read `(the designated site's extent, 11,219.05 m2 - ~9,800 m2 without the front plaza)`.
**SESSION NOTE / HISTORY** - none visible (the 2026-08-28 re-sourcing note is a comment, l. 94 ✓).

## "The granary holds grain, not just rice" (ll. 96-100)

**VOCABULARY** - `commutation` / "cash commutation"
> "so cash commutation is LESS common than in Edo Japan - the dry-field share of a Rokugani county's tax arrives IN KIND ..." (l. 100)

Draft (from this section's own text): *"commutation - paying in coin a tax assessed in grain; the dry-field share of an Edo land tax was usually settled that way, which is what put money in a farming village."*

**VOCABULARY** - `NTA`
> "(searched 2026-08-28: the NTA 租税史料 page returned unreadable text and zh.wikipedia 常平仓 is silent on grain composition)" (l. 99)

This sits inside a permitted search record, so the fix is not a tooltip but spelling it out: *"Japan's National Tax Agency"*. (The raw search strings are what was tried - keep.)
`hata-ei`, `kura`, `daizu`/soybean ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none beyond the roster shape.

## "Fire discipline: halls burn, kura endure" (ll. 101-105)

**DEFECT** - the reader meets two versions of one fact.
> roster: "(the Sado magistracy burned and was rebuilt five times)" (l. 104) against body: "(the Sado magistracy burned and was rebuilt over and over)" (l. 105).

The quoted source gives five (`citations/buildings.html` fn-43). Proposal: one figure in both places.
**VOCABULARY / SESSION NOTE / HISTORY** - none.

## "Fire-water is distributed to the halls, not the kura" (ll. 106-110)

**DEFECT** - footnote marks inside a term's emphasis.
> `the Forbidden City's 308 <em>taiping-gang<sup class="fn">47</sup><sup class="fn">46</sup></em> / <em>men-hai</em> ("gate-sea", unsourced) water vats` (l. 110)

The reader sees the italic term with two numbers welded to it, and the marks are inside the `<em>` that the term's own emphasis owns. Proposal: move both `<sup>` elements after `</em>`.

**VOCABULARY** - `tensuioke`, `taiping-gang`, `kamado`, `hinomi-yagura` ✓; `men-hai` `defined inline`.
**SESSION NOTE** - none visible (`settlement.py`, `s.fire_tower(...)`, the r3.8/r5 glyph history and the pixel-noise figure are all comments ✓ - this paragraph is the file's best example of the rule applied).
**HISTORY** - none visible.

## "The compound has a size HIERARCHY, not just individual sizes" (ll. 111-115)

**DEFECT** - untranslated measurement phrase with no gloss anywhere on the page.
> "the three anchors are unsourced - Izumo's 二間四方 (searched 2026-08-28: genbu.net unreadable; ...)" (l. 114)

The body gives "~2×2 ken" (l. 115) but never ties the two. Proposal: `Izumo's two ken square (二間四方)`.
**VOCABULARY** - `tsubo`, `ken`, `haiden`, `daidokoro` ✓.
**SESSION NOTE / HISTORY** - none visible.

## "Packing: a jin'ya is mostly open ..." (ll. 116-121)

**HISTORY** - a past state of a sheet surviving as a bare number.
> "A cart-and-draft-animal loading apron is ~15-20 ft, not 24; and a region that reads sparse because it holds the oshirasu, a garden or the forecourt is a FEATURE." (l. 121)

Still USEFUL and kept: the 15-20 ft figure and its footnote. History and goes: `, not 24` - the trace of Ochiba's ~24 ft void, whose whole story is already in the comment at the end of the same line. As it would then read: *"A cart-and-draft-animal loading apron is ~15-20 ft; and a region that reads sparse because it holds the oshirasu, a garden or the forecourt is a FEATURE."*

**DEFECT** - the glossary misses the hyphenated form the page uses. `fire-gap` / `fire-gaps` occurs five times on l. 121 (and "a ~6-8 ft fire-gap", "a ~6-10 ft fire-gap", "stands at fire-gaps (9 ft / 6.7 ft)"); the glossary entry is `fire gap` with variants `fire gap`, `fire gaps` only, and the matcher requires the exact variant, so **no tooltip fires anywhere in this section**. Proposal: add `fire-gap`, `fire-gaps` as variants.
**DEFECT (low, invisible)** - the `Grounds:` comment carries a half-written Markdown link: `+ [tools/pack_audit.py](../pack_audit.py -->` (l. 117) - a broken pointer for the next session.
**VOCABULARY** - `oshirasu`, `siheyuan`, `buke-yashiki`, `daikansho` ✓.
**SESSION NOTE** - none visible (the pack_audit internals, the top-N/per-region fix and the feature-007 narrative are all comments ✓).

## "Rendering / layout is checked automatically, because it is geometry not judgment" (ll. 122-137)

**SESSION NOTE** - the heading is addressed to the maintainer, not the reader.
> "Rendering / layout is checked automatically, because it is geometry not judgment" (l. 122)

Nothing a reader asks from a map is answered by "we check this automatically"; the body under it (l. 126) is a fine reader's answer about draw order, label placement and door glyphs. Proposal: **comment** the "checked automatically" framing (it is the tooling's rationale) and give the section a question heading over the same body, e.g. *"Why do the labels, glyphs and doors sit where they do?"*. The seven-check body is already a comment (ll. 127-137 ✓).
**VOCABULARY** - `glyph`, `kosatsu`(as `kosatsuba`) ✓. `Sources: not applicable - a rendering and tooling decision with nothing physical behind it` (l. 125) is the honest label - keep.
**HISTORY / DEFECTS** - none visible.

## "A dojo is a city institution; county training is courtyard keiko" (ll. 138-143)

**DEFECT** - a dash and a period with nothing between them, the residue of a removed clause.
> "Marking the GROUND and its GEAR rather than labeling a building is the honest form of the finding - rural practice left equipment, not architecture - ." (l. 142)

As it would then read: *"... is the honest form of the finding - rural practice left equipment, not architecture."*

**HISTORY** - a note about a claim that appears nowhere else in the entry.
> "The "boom of 1830-1860" date range was found in no page read." (l. 143)

No sentence on the page asserts a boom of 1830-1860; the sentence exists only to record that a figure the entry once carried was not supported. Useful half: nothing the reader can use. Proposal: **drop** (the search itself is preserved in the section's own absence notes and in git). If the session wants to keep the warning for itself, it goes in a comment beside the dojo-dating sentence.

**VOCABULARY** - `Toshi Ranbo`
> "the setting notes' own dojo references all sit (Toshi Ranbo's "many dojos", the train-at-a-dojo-in-every-clan pilgrimage vow)" (l. 142)

Draft: *"Toshi Ranbo - a city of the setting, cited here for the GM's own notes on its many dojos."* Alternatively rephrase to "one of the setting's cities". `dojo`, `keiko`, `kata`, `bugeijo`, `han`, `hanko`, `drill ground`, `bakufu` are all in the glossary ✓; `chorenjo` is `defined inline`.
**SESSION NOTE** - none visible; "*The scope of what is read:*" (l. 143) is the honest limit on a negative claim - keep.

## "Privies attach to the house; night-soil drives their placement" (ll. 144-148)

**DEFECT** - stray punctuation inside a parenthetical.
> "was built INTO the house (at the rear of the guest parlor,; the pull-out sand box under the master's for health inspection is unsourced)" (l. 148)

Proposal: `(at the rear of the guest parlor; the pull-out sand box ...)`.

**HISTORY** - an argument against guidance the page used to give.
> "and servants'/outer privies line service walls near a gate - A rule of one inner and one outer privy would under-provision a compound of the size the staff-housing section above describes, and would let the residence privy float as a detached block." (l. 148)

The hidden comment on the same line confirms it ("the prior guidance said exactly that; both corrected"). Still USEFUL and kept: the positive rule - the count scales with occupancy, ~3-4 at a county manor, the residence privy attached with its cesspit to the service wall, outer privies on service walls near a gate. History and goes: the whole "A rule of one inner and one outer privy would ..." clause (which also begins mid-sentence with a capital). As it would then read: *"The decision: privy count scales with occupancy (~1 per functional zone, ~3-4 at a county manor), the residence privy attaches to the house with its cesspit to the rear/service wall, and servants'/outer privies line service walls near a gate."*

**VOCABULARY** - `setchin` is a variant of `kawaya` ✓; `fertilizer boat`, `night soil`, `kawaya` ✓. `房総のむら (the Boso-no-Mura museum)` and `雪隠 (the privy)` are glossed inline ✓.

## "The shady rear is the service strip" (ll. 149-153)

**VOCABULARY** - none owed (`buke`, `nagayamon`, `nagaya` ✓).
**SESSION NOTE / HISTORY / DEFECTS** - none visible (the "both were carrying the empty band before 2026-07" note is a comment ✓).

## File-wide defects, `buildings.html`

- **Roster run-on.** Seven `**Sources:**` lines end a sentence (usually an absence note) and then append one or two more keys after a comma, so the reader meets `... - not found for Takayama), jinya-jawiki`: ll. 45, 51, 63, 99, 109, 147, 152. Proposal: keep the keys together at the head of the roster and put the absence sentence last.
- **Footnote references out of order.** Reference pairs are written high-then-low throughout (l. 24 `2` then `1`; l. 29 `11` then `10`; l. 57 `30` then `29`; l. 110 `47` then `46`; l. 40 `21` then `20`, `17` then `16`, `19` then `18`), so a reader hovering left to right meets the later note first. Not a content error - flagged as a mechanical one, one decision for the session across the file.
- **Raw CJK in visible prose** (ll. 28, 40, 51, 63, 68, 73, 89, 93, 99, 114, 119, 147, 152): titles, terms and two quotations. The two quotations (28, 73) and the one unglossed measurement (114) are the ones a reader actually needs; the rest carry an English gloss beside them.

---

# 2. `research/vegetation.html`

## Page head and lead (ll. 14-15)

**SESSION NOTE** - "and - where no generator draws the feature yet - the rules a map follows" (l. 15, and identically `river-cities.html` l. 15). "Generator" is engine vocabulary; the reader's version of the same sentence is *"and, where the map is drawn by hand, the rule it follows."* Proposal: **comment** or reword; the `<p class="spec">` paragraphs themselves are correctly visible under feature 229.

## "The fengshui forest - real scale, and why ours is honest" (ll. 20-33)

**VOCABULARY** - `동구숲` (the Korean term)
> "the nearest analogue is the Korean village-entrance grove (동구숲), the analogue of the water-mouth grove" (l. 26)

The English precedes it, so a tooltip is not owed; but per the translation rule the hangul is an anchor rather than the name a reader reads, and the glossary has `sugumagi` for the Korean form beside it. Report as `defined inline`, with a note that the record's own convention elsewhere is `donggusup (동구숲)` (`citations/vegetation.html` fn-72 uses exactly that).

**VOCABULARY** - everything else in this dense paragraph is covered: `stem density`, `basal area`, `transect`, `GIS`, `houlongshan`, `mu`, `understory`, `Buyi`, `Pearl delta`, `natural village` ✓.

**SESSION NOTE** - none visible: the "re-searched 2026-09-07, feature 196" note, the `village_grove` identifier, the px² figures and the Lingtou correction are all comments (ll. 26, 27, 31 ✓).
**HISTORY** - none visible in this section (the two correction notes are comments ✓).
**DEFECT (mechanical)** - a second reference to note 73 carries no `id`:
> `the Korean groves hold 「less than 10 to more than 100」 each,<sup class="fn"><a href="citations/vegetation.html#fn-73">73</a></sup>` (l. 26)

The note's `back` link targets `#fnref-73`, which is the earlier reference, so this one cannot be returned to. Proposal: give it a distinct id or accept the shared one deliberately.

## "What are the village's three groves ...?" (ll. 34-97)

**DEFECT** - a Chinese phrase in visible prose with neither translation nor romanization.
> "Where the high side is the windward side, and under 背山面水 it usually is, the back grove is also the wind wall." (l. 45)

The glossary defines **`beishan mianshui`** (*"'Back to the hill, facing the water': the fengshui seat that puts a house or a village with high ground behind it and open water in front"*) - but the page writes the characters, which the matcher cannot see, so the reader gets four characters and no help. Proposal: `under beishan mianshui (背山面水) it usually is`, which both reads and fires the tooltip.

**VOCABULARY** - `后龙林` and `水口林` (ll. 43, 46). Both sit beside their English names ("The back-village belt (后龙林)", "The water-mouth cluster (水口林)"), so: `defined inline`; but the glossary's `houlongshan` and `water-mouth`/`shuikou` entries will not fire on the characters. Same proposal as above - give the romanization beside the characters.

**SESSION NOTE** - an instruction and an engine measurement in the reader's text.
> "*A smaller reservation was tried and measured:* reserving only about seven tenths of that radius fell roughly fifteen percent of a clump short, and a blob's corner clipped a small farmhouse on one map." (ll. 72-74)

This is a failed fix recorded against our own placer (the point-of-change doctrine), not something a reader of the map can use; the keep-out rule in the sentence before it is. Proposal: **comment** the whole sentence beside the rule (the hidden comment on l. 74 already carries the numbers).

**SESSION NOTE** - "Both rules come from one post-mortem: a hamlet whose belt outline ran through its northern house row had most of the clumps it could have grown thrown away as landing on a building, and sixteen farmhouses ended up sheltered by eleven crowns." (ll. 75-78). "One post-mortem" is session-speak about our own run. Useful to the reader: the rule and its reason (a belt set back off the houses, drawn 80-120 ft deep, because a 30 ft band reads as scattered blobs). Proposal: **comment** the post-mortem clause, keep the rule sentence that follows it.

**HISTORY / DEFECTS** - none further; the two `<p class="spec">` rules (ll. 89-97) are correctly visible.

## "Does a shelter belt wrap the settlement? No - it stands on one or two windward sides" (ll. 98-165)

**VOCABULARY** - `igune`, `tsuijimatsu`, `yashikirin`, `fetch`, `Meiji`, `knob` ✓; `katabatic` appears only as a source key ✓.
**SESSION NOTE** - none that survives reading: "The question had been posed wrongly" (l. 108) is about the research question, not about the document, and the GM's two quoted rulings plus the declined knob (ll. 103-153) are exactly the decision record the reader is owed - **keep, including "The full-ring form stays recorded here and undrawn."**
**HISTORY** - borderline, reported for the session's judgment:
> "Nothing had to change for the ruling, and that was checked rather than assumed." (l. 154)

This is a statement about our own verification pass rather than about the world; the measurement that follows it (the five belts' arcs, 102-146 degrees) is a fact about the maps and worth keeping. Proposal: **drop** the framing clause, keep from "The regional-against-local rule ..." onward.
**DEFECTS** - none.

## "Why does the belt run off the edge of the sheet ...?" (ll. 166-213)

This is the section carrying the most session-facing text on the page.

**SESSION NOTE** - "Measured on the two maps that a widened reading first failed" (ll. 181-182). "A widened reading" is a change to a gate check. Proposal: **drop** the clause - *"Measured on two maps: on one, the footprint spans 747 ft ..."*.

**SESSION NOTE** - an instruction to a future session.
> "It was reverted, because a belt that appears to stop short is usually a belt whose short end is off the page: measure that before reaching for the planting." (ll. 190-192)

Proposal: **comment** the imperative ("measure that before reaching for the planting"); the rest - an alternative priced and reverted, with what it bought - is the decision record and stays.

**SESSION NOTE** - the gate's own coverage discussed in the reader's text.
> "Why the test is asymmetric on purpose, and what that costs." (l. 193) ... "The symmetric form was priced - credit a clump only where its crown reaches the view. It fails one hamlet at a 60 ft bare run ..." (l. 194) ... "The guarantee is weaker than it looks - delete that hamlet's copse and the test still passes." (l. 202)

"The test", "it fails one hamlet", "the scan for holes" (l. 185) are the gate's vocabulary. The reader-facing half of the same argument is already here and excellent ("Nothing beyond the frame is drawn, and nothing beyond the frame is counted against the map"). Proposal: **comment** the three test-shaped sentences (l. 193 heading phrase, l. 194's verdict, l. 202's guarantee), keeping the accepted limitation and its cost as prose about the map.

**SESSION NOTE** - "What is still open." (ll. 203-209), including "the rule stands as written until the GM says otherwise" and "it exists because a wellhead seated inside a belt suppressed the clumps around it and took a 40 ft band from six clumps to one, and because a lane web crossed a belt and removed some 45 ft of wall" and "One hamlet carries three bare runs of 40-50 ft in belt the reader can see". These are a question queued for the GM, two engine incidents and a defect census - all addressed to a session. Proposal: **comment** the paragraph, or keep only the sentence a reader can use: that the GM's ruling and the no-holes rule meet head-on where a feature inside a belt suppresses its planting, and the rule stands.

**VOCABULARY / HISTORY / DEFECTS** - none.

## "Why is the hillside past the grove open scrub rather than more forest?" (ll. 214-246)

**VOCABULARY** - `masson pine`, `China fir`, `satoyama`, `coppice` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none. "an early version drawn as a filled quad read as a literal rhombus lying on the hillside" (l. 236) is a declined form with its reason - keep.

## "Forest density and crown size" (ll. 247-255)

**VOCABULARY** - `Castanopsis`, `emergent`, `DBH`-adjacent terms ✓.
**SESSION NOTE** - none visible: `CANOPY_SPACING_FT` / `CANOPY_R_FT` and the SUMMARY-ONLY leftover are comments (ll. 251, 253 ✓). The roster's "the 500-800 stems/ha band and the 5-8 m crowns are a GUESS taken from their abstracts, which no readable page supports" (l. 250) is the honest label - keep.
**HISTORY / DEFECTS** - none.

## "The belt's crowns are the same real size as the woods'" (ll. 256-265)

**SESSION NOTE / HISTORY** - none visible, and this section is the model: the entire "It was not / measured before and after / fixed at the source" narrative is in the comment at l. 265 ✓, while the visible text states the current fact and answers the GM's question.
**VOCABULARY / DEFECTS** - none.

## "No canopy tree stands under another's crown" (ll. 266-281)

**SESSION NOTE** - none visible (the pre-rule measurement, the seating predicate and the dominants-first note are comments ✓).
**VOCABULARY** - `crown shyness` appears only as a key; `understory` ✓.
**HISTORY / DEFECTS** - none.

## "The crop margin - scrub stands 6 ft off every field edge" (ll. 282-291)

**VOCABULARY** - `keihan`, `aze`, `tian'geng`, `azemichi`, `green manure`, `conservation headland` ✓ (`aze` under `bund`, so not reported).
**SESSION NOTE / HISTORY / DEFECTS** - none visible; `_CROP_MARGIN_FT`, the blade-lean measurements and the settlement-review date are comments ✓.

## "Scrub stays off open water - including the comb laterals' drawn width" (ll. 292-305)

**VOCABULARY** - `comb`, `lateral`, `head race` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none visible; the `M['channels']` / `_watercourse_segs` history and the open-decision sketch are comments (ll. 300-304 ✓). `Sources: not applicable - a rendering rule; nothing physical asserted` - keep.

## "The cut bank - scrub stands 6 ft off every irrigation channel's drawn edge" (ll. 306-314)

**VOCABULARY** - `berm`, `hem`, `sluice`, `riparian` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none visible (`_BANK_MARGIN_FT`, the scatter internals and the 2026-08-16 review praise are comments ✓).

## "The marsh margin: reed -> sedge/grass -> dry ground; ... never pine - ACCURATE" (ll. 315-368)

**SESSION NOTE** - an evidence label in the heading itself.
> "The marsh margin: reed -&gt; sedge/grass -&gt; dry ground; woody at a reed edge is alder or willow, never pine - ACCURATE" (l. 315)

`ACCURATE` is the classification field, which belongs in the `<!-- Evidence: ... -->` comment; and a heading is the line a reader meets on the references modal, where by the GM's own 2026-08-29 ruling accuracy is never announced. Proposal: **comment** the label. As it would then read: *"The marsh margin: reed -> sedge/grass -> dry ground; woody at a reed edge is alder or willow, never pine"* - with the same treatment for the two in-body labels: "the hard exclusion stands as ACCURATE", "Grass grading into the reeds over the margin: ACCURATE" (l. 346). The remaining "unsourced, and labeled so" clauses are honest labels and stay.

**DEFECT** - raw Japanese plant-community names in visible prose, untranslated.
> "the national river-vegetation classification names ヨシ群落, マコモ群落 and タチヤナギ群落 as the low-wetland communities and ハンノキ林 as the eutrophic-mire woodland" (ll. 335-336)

The citations page renders these in English (fn-66: "alder-woodland wetland / Alder swamp"; the MLIT write-up names "the tachiyanagi willow association"), so the English exists. Proposal: *"names the reed, wild-rice and tachiyanagi-willow communities (ヨシ群落, マコモ群落, タチヤナギ群落) as the low-wetland communities, and the alder woodland (ハンノキ林) as the eutrophic-mire woodland."* The same treatment is owed at ll. 323-326 (ヨシ, スゲ, ハンノキ林, タチヤナギ群落 - each already has an English name beside it, so those are `defined inline`), l. 342 (アカマツ ✓ glossed "Red pine") and l. 352 (ヨシ刈り, 茅場 - unglossed; `thatch field` is in the glossary but cannot fire on 茅場).

**VOCABULARY** - `hydrosere`: `defined inline` ("the zonation from open water to dry land that every lowland wetland shows in space"). `Phragmites`, `Carex`, `Calamagrostis`, `Spiraea`, `carr`, `littoral`, `mire`, `eutrophication`, `emergent` ✓. `Alnus japonica`, `Pinus densiflora` carry their common names ✓.

**HISTORY** - borderline: "on one hamlet only four scrub bases now stand inside its marshes" (l. 356) - "now" leans on the pre-rule count (3,370), which is correctly in a comment. Proposal: drop "now". The three-forms narrative around it (ll. 353-364) is two declined forms with the GM's own words - **keep**.

## "Does scrub stand under a village wood? ..." (ll. 369-407)

**DEFECT** - a duplicated clause.
> "The coppice patches take the same rule - the coppice IS the worked wood, so every woodland commons keeps scrub out too - so every woodland commons keeps scrub out too." (ll. 394-395)

As it would then read: *"The coppice patches take the same rule - the coppice IS the worked wood - so every woodland commons keeps scrub out too."*

**DEFECT (the most serious on the page)** - **a nested HTML comment leaks a session note and a stray `-->` into the reader's text.**
> l. 440 opens `<!-- Sources (read): International Journal of the Commons ... (the 1000 m strip grants and dry fields)<!-- the founding year and the 1664 survey are NOT on it -->. Pointers, not read: the Indiana DLC "Village Commons in Japan"; Totman, The Green Archipelago; Takeuchi et al., Satoyama (Springer). Unsourced: "described by ridge, stream and path". -->`

HTML comments do not nest: the comment ENDS at the first `-->`, so a reader sees, as body text at the end of the section, `. Pointers, not read: the Indiana DLC "Village Commons in Japan"; Totman, The Green Archipelago; Takeuchi et al., Satoyama (Springer). Unsourced: "described by ridge, stream and path". -->`. That is a fetch-verdict list plus a literal `-->`. Proposal: **comment** properly (remove the inner `<!-- ... -->` or split into two comments); nothing there is meant to be visible.

**VOCABULARY** - `EUNIS`, `forest litter`/`ochiba`, `konara`, `kunugi`, `coppice`, `fukugi`, `satoyama` ✓; `Quercus serrata`/`Quercus acutissima` carry their Japanese names ✓; `Krautsaum / Strauchgürtel / Waldmantel` are inside a marked translation with the English first ✓.
**VOCABULARY** - `AGRIS`
> "From <a ...>Uehara et al. 2009, AGRIS</a>: a managed coppice stand held 42 plant species ..." (l. 383)

Draft (from `citations/vegetation.html` l. 92): *"AGRIS - the FAO's international agricultural research database, where a paper's bibliographic record and abstract can be read when the article itself cannot."*
**SESSION NOTE** - "the EUNIS habitat factsheet's own wording ... has no publicly readable source - searched 2026-08-28: the E5.2 factsheet page was gone" (l. 390) is the permitted absence form - keep. The UNVERIFIED/NOT-FOUND notes are comments ✓.
**HISTORY** - none visible beyond the leak above.

## "How is a coppice lot bounded? By ridge, stream and path - never by a page axis" (ll. 408-441)

**HISTORY** - a note about a sentence the document itself used to assert.
> "UNSOURCED: the sentence that iriai boundaries were "described by ridge, stream and path", is NOT in that article and no source for it has been found; it stands as a claim of unknown provenance." (ll. 421-423)

The claim is in the section's own HEADING ("By ridge, stream and path"), so the useful half is real and must stay - the honest label on a claim of unknown provenance. What is history: nothing, once the sentence is read as a label rather than as a report on a past edit; **but** the roster says the same thing a second time (l. 411: "the 'bounded by ridge, stream and path' sentence is unsourced and of unknown provenance"). Proposal: keep one of the two - the roster's - and reduce the body to the label.
**DEFECT** - stray comma: `"described by ridge, stream and path",<sup>42</sup> is NOT in that article` reads `... and path"42 is NOT ...`. Proposal: drop the comma.
**SESSION NOTE** - "Totman *The Green Archipelago* and the Indiana DLC paper not read" (l. 411). `not read` is a fetch verdict, and a list of works we did not read tells the reader nothing. Proposal: **drop** from the visible roster (the registry keeps the record); as it would then read: *"... the "bounded by ridge, stream and path" sentence is unsourced and of unknown provenance."*
**VOCABULARY** - `iriai`, `usufruct`, `shinden`, `zokibayashi` ✓.

## "Bamboo: how common, where it stood, and how to show it" (ll. 442-526)

**SESSION NOTE** - a list of what we did not read.
> "Unread, and carrying no weight here: that a typical Edo farmstead kept "a grove where they could harvest bamboo" (Kids Web Japan - no readable page, searched 2026-08-27; no corroborating snippet found); the broader list of uses (Highlighting Japan)." (ll. 464-467)

A claim the record does not rest on, named only so a session does not re-fetch it. Proposal: **comment** the sentence; the next sentence ("So: a lowland paddy hamlet in a temperate province has bamboo as a matter of course ... that half is sourced") carries everything the reader needs.

**SESSION NOTE** - a knob's raw value in the reader's text.
> "So the presence rate is a GUESS - 0.6, "one of several secondary species" read as common but not universal, set like the shed's - labeled as such." (ll. 515-516)

`0.6` is the engine's probability (`HOUSEHOLD_BAMBOO_PREVALENCE`, already in the comment beside it) and "set like the shed's" points at another knob. Proposal: keep the GUESS label, give the reader the rate in words - *"So the presence rate is a GUESS: about three farmsteads in five keep a stand, read from "one of several secondary species" as common but not universal."*

**SESSION NOTE** - "THAT is the axis of variance the project wants: two attested forms, varied from settlement to settlement." (l. 469) - project doctrine (the knob rule) rather than a finding. Proposal: **drop** the first clause: *"Two attested forms, so the map varies it from settlement to settlement."*

**HISTORY** - what this page used to place where.
> "on the Tonami plain the bamboo stood on the SOUTH side with the storehouses and fruit trees, its roots planted to hold the soil, so this page's earlier placing of it on the shady N/W service strip is on no page read" (l. 471)

Useful and kept: the finding (south side, with the storehouses and fruit trees; roots against washout) and the honest note that the N/W placement is on no page read. History and goes: "this page's earlier placing of it". As it would then read: *"... its roots planted to hold the soil; the shady N/W service strip is on no page read (the homestead research)."* The same phrase recurs twice more and should go the same way: "the record's "N/W strip" read that way" (l. 488) and ""north = the shady side" is a reading of the record's "N/W strip", recorded as a reading" (ll. 495-496) - both are pointers to a wording this record no longer carries; the reader's version is *"north is drawn as the shady side, the side the house shades - a reading, recorded as one."*

**SESSION NOTE** - "As built (the GM, 2026-08-27: "make that change in the manner that you had previously proposed")." (l. 484). The GM's ruling stays; "in the manner that you had previously proposed" refers to a proposal in a chat the reader cannot see, and the proposal itself is in the comment at l. 483. Proposal: keep the quotation (it is the GM's own words) and let the sentence that follows carry the content - no change owed if the session prefers verbatim.

**VOCABULARY** - `culm`, `madake`, `moso`, `take-yabu`, `geta`, `shakuhachi`, `GSI`, `kainyo`, `asunaro`, `fit zoom`, `satoyama`, `thatch field`, `secondary forest` ✓. `zelkova`
> "the kainyo 「is centered on cedar, with ate (asunaro), zelkova, oaks, bamboo, persimmon, chestnut and others besides」" (l. 503)

`zelkova` is NOT in the glossary; the glossary's `keyaki` is defined as *"Zelkova, a tall broadleaf timber tree of the homestead grove's planting list"* but its only variant is `keyaki`. Proposal: add `zelkova` (and `Japanese zelkova`, which `citations/vegetation.html` l. 125 uses) as variants of `keyaki`. The word is inside a quoted passage, which the wrap does not disturb.
**VOCABULARY** - `sasa`: `defined inline` ("the bamboo-grass (笹地, sasa) symbol", l. 523).
**DEFECT** - 竹林 / 広葉樹林 / 針葉樹林 / 笹地 are each glossed in English first ✓ - no defect; 「」 quotations all carry translation notes ✓.

## "How does a flat map show that the ground slopes?" (ll. 527-559)

**VOCABULARY** - `hachure`, `Meiji` ✓; `estate map` appears only as a key.
**SESSION NOTE / HISTORY / DEFECTS** - none. The rejected-shading paragraph and the spec are correctly visible.

---

# 3. `research/cities/river-cities.html`

## Page head and lead (ll. 14-15)

**SESSION NOTE** - "where no generator draws the feature yet" (l. 15) - as in `vegetation.html`.

## "Most provincial cities sit on a river" (ll. 19-30)

**DEFECT** - footnote mark inside a term's emphasis.
> "the river-city version of the gate market (<em>guan-xiang<sup class="fn">8</sup></em>)" (l. 25)

Proposal: move the `<sup>` after `</em>` (the same shape as `buildings.html` l. 110).

**VOCABULARY** - `shuimen`
> "The ONE way water legitimately enters the walls is a **water gate** (*shuimen*) admitting a navigable CANAL, not the river" (l. 25)

`water gate` is in the glossary; `shuimen` is not among its variants, so the italicized Chinese term gets nothing. Proposal: add `shuimen` (and `水门`) as variants of `water gate`. `guanxiang`/`guan-xiang`, `gate market`, `jetty`, `sluice`, `abutment`, `frontage` ✓.

**VOCABULARY** - `Imperial spine`
> "A river city has no Imperial spine through it: its highway passes off the sheet, so what the map owes instead is a road net that leaves the view in at least two directions." (l. 29)

Half-explained by the clause after it. Draft: *"Imperial spine - the Imperial road where it runs through a settlement as its main street, the axis a map's road net is hung on; a river city has none, its highway passing off the sheet."* (Drawn from this sentence and the `presentation`/`ways` record's treatment of Imperial roads.) `Tango` (l. 25) and `Shiro Daika` (l. 89) are map names - the glossary's `the pool` covers the idea, so no term is owed.

**SESSION NOTE / HISTORY** - none visible: the 2026-08-28 flood correction and "the two specifications below were moved from the retired rule file" are comments (ll. 27-28 ✓).

## "Which way does an offtake leave a river, and why?" (ll. 31-39)

**HISTORY** - what the map used to draw, and a "now".
> "The two junction arms met the river as parallel right angles, and the GM asked whether they should not angle with the flow. They were parallel only because each open end of the moat was projected onto the river by dropping a perpendicular - an artifact of how the arc was closed, never a decision anyone made. The answer splits by end ...: the outlet now sweeps about 22 degrees off square ..." (l. 37)

Still USEFUL and kept: the GM's question and ruling, the two angles with their directions, the GUESS label on the angles, and the one prohibition ("an inlet swept downstream is the one shape the map must not draw"). History and goes: the past drawing and how it came about, and the word "now". As it would then read: *"**The decision** (the GM, 2026-07-24), on whether the junction arms should angle with the flow rather than meet the river square. The answer splits by end, in the way the hydrology above splits: the outlet sweeps about 22 degrees off square, pointing downstream, and the inlet tilts only about 10 degrees, upstream of square ..."*

**VOCABULARY** - `separation zone` / "the zone of separated flow"
> "widening the angle at which the side channel enters enlarges the zone of separated flow inside the junction, and raises the greatest bed shear stress there by 59% between 30 and 115 degrees" (l. 36)

Not in the glossary and not explained. Draft (from this section and `citations/cities/river-cities.html` l. 52): *"separated flow - the pocket of slack, recirculating water that forms just inside the mouth where one channel enters another; the wider the junction angle, the larger it is."* Everything else here is covered: `offtake`, `distributary`, `headworks`, `regulator`, `sill`, `skimmer wall`, `bedload`, `bed shear stress`, `river stage`, `intake`, `weir` ✓.

**SESSION NOTE** - none visible; the feature-235 instruction ("Do not "fix" it") is correctly a comment (l. 38 ✓), and the accepted-limitation paragraph above it is exactly the record the reader is owed.

## "Does a city's canal open its own mouth on the river?" (ll. 40-46)

**HISTORY** - a past state of one map used as the question's setup.
> "A cargo canal that opens its own river tap some 36 ft from the moat's downstream junction and then rides collinearly inside the moat arm for the whole bank crossing reads as a smeared doubled channel with a sliver fork at the mouth, which is what put the question." (l. 45)

Useful and kept: the reason - two mouths side by side spoil each other's reading, and a second mouth would have had to cross the moat's arc at grade. History and goes: the measured description of what the sheet used to show and "which is what put the question". As it would then read: *"A cargo canal that taps the river a few tens of feet from the moat's downstream junction and then runs collinearly inside the moat arm reads as a smeared doubled channel with a sliver fork at the mouth. The answer the record supports MERGES the two mouths ..."*

**VOCABULARY** - `dock basin`, `at grade`: both plain enough in context; `water gate` ✓.
**SESSION NOTE / DEFECTS** - none.

## "The wharf's working face: piers, quays and stepped landings" (ll. 47-93)

**VOCABULARY** - `matou`, `kashi`, `gangi`, `kura`, `takasebune`, `Heian`, `revetment`, `cribbing`, `quay`, `towpath` ✓ (`matou` is a variant of `gangi`).
**VOCABULARY** - `mole` is used on the citations page ("the projecting mole", works l. 101 and fn-31) but not here; no action on this page.
**SESSION NOTE / HISTORY / DEFECTS** - none visible; the `settlement.quay(pts, steps=N)` pointer and the "as first written" note are comments (ll. 90, 93 ✓). The GM's 2026-08-11 question and the "Keep the three piers" decision are the record's own content - keep.

---

# 4. `research/citations/buildings.html`

The works section (ll. 15-175, derived by `make citations`) and the notes (ll. 177-291).

## The works section

**SESSION NOTE** - none in visible text; the two forward-looking notes are comments (l. 61 "a conservation report ... would be the closer source", l. 97 "Tajima is the primary layer a future pass should cite directly" ✓).
**HISTORY** - none.
**VOCABULARY** - `sun` (the unit)
> "with medieval walls as thin as three to seven sun before firearms spread in the late Sengoku period and pushed them to seven sun (about 210 mm) and beyond" (l. 56; also fn-32, l. 209)

Half-defined by the metric conversion. **Do not add a glossary term for `sun`**: the matcher is case-insensitive on word boundaries, so a `sun` entry would fire on every ordinary "sun" in the record (`vegetation.html` ll. 82-88 alone carry "afternoon sun", "sun corridor"; `buildings.html` l. 153 "the sunny SOUTH side"). Proposal: gloss it in place - *"three to seven sun (a sun is a tenth of a shaku, about 30 mm)"*.
**VOCABULARY** - `Dacheng gate` (l. 65, and fn-42) - a reader meets it cold. Draft: *"Dacheng gate - the main gate of a Chinese Confucian temple precinct, outside which the shrines to worthy officials and local worthies stood."* `tertiary source`, `tsubo`, `nagayamon`, `chugen`, `iroha-gumi`, `gundai`, `zhang`, `Six Chambers`, `shizai` ✓; `gokumon`, `geshunin`, `kosen`-type terms are `defined inline` inside their quotations.
**DEFECT** - untranslated titles in the citation lines, which are the works list a reader meets. Roughly twenty of this page's works are named only in Japanese or Chinese: ll. 19 (高山陣屋跡), 23, 35, 47, 51, 55, 59 (攻城団, お城の基礎講座 40. 土塀の種類), 63, 71 (防火対策の歴史), 79, 83, 87, 111, 115, 119, 123, 127, 131, 135, 139, 143, 147, 151, 155, 159, 163, 171. Two entries on the same page do it right - l. 75/76 gives 这口大缸能防火？！ with its English, and ll. 99/103 carry full translation notes - so the fix is the page's own convention applied throughout. (This is the same defect as in the registry; see §6.)

## The notes

**DEFECT** - **a duplicated English rendering after the marked translation**, in five notes. The note gives 「English translation」 (translated from the X by this project; original: 「CJK」) and then repeats the same passage in plain double quotes:
- fn-14 (l. 191): `... ("Edo-period jails had four functions: 1. hold unsentenced prisoners; 2. detain the convicted until execution of sentence..." / "it was closer in nature to today's detention house ...")`
- fn-15 (l. 192): `... ("because eiro and katairo, the equivalents of today's imprisonment, were exceptionally imposed punishments" / "at Tenmacho beheading ... were carried out" - flogging and execution are on the page; exile and fines are not named on it.)`
- fn-22 (l. 199): `... ("embodying the traditional ritual ideas of the old yamen: facing south, civil left and military right ..." / "the first courtyard has functional buildings on both sides ..." - south by regulation, west side by placement; "corner" is not the page's word.)`
- fn-42 (l. 219): `... ("The Mingguan shrine is one of the important components ..." / "It mostly stands outside the Dacheng gate ...")`
- fn-62 (l. 239): `... ("the example of two separate privies in one house was given above ..." / (kotobank) "in post-Meiji urban houses ...")`

Proposal in each: **drop** the duplicated rendering, keeping any gloss clause that says something new (fn-15's "exile and fines are not named on it", fn-22's ""corner" is not the page's word" - both are real limits and stay).

**DEFECT** - malformed parenthetical `((English).`:
- fn-13 (l. 190): `「Behind Yinbin Guesthouse is a courtyard ...」 ((English). The chinadaily page has the same: ...)`
- fn-58 (l. 235): `「A local farmer used regularly to bring along a cart ...」 ((English). Corroborated on sinyoken-madori: ...)`

Proposal: `(English; the chinadaily page has the same: ...)`.

**DEFECT** - fn-51 (l. 228): two things at once.
> `「The gundai office was rebuilt in 1816 (Bunka 13) in such parts as the entrance, the examination room, the office and the great hall. || Storehouses no. 1 to no. 4 and no. 9 to no. 12, and the book storehouse.」 ... and 「Storehouses no. 1 to no. 4 ...」 ... ((as in the courtroom section))`

(i) a machine joiner `||` stands inside a 「」 quotation (and inside its original), which a reader can neither read nor find on the page; (ii) the second passage is quoted twice in the same note; (iii) `((as in the courtroom section))` is double-parenthesized. Proposal: two separate quotations, no `||`, one set of parentheses.

**SESSION NOTE** - a bare verification remark.
> fn-25 (l. 202): `... (this page supports it.)`

That is the source-reader's verdict, not a gloss for a reader. Proposal: **drop** (or comment).

**SESSION NOTE** - an instruction to a future session inside an absence note.
> fn-79 (l. 256): "It is the reason the drawn guest doors open into courts rather than against a building's flank, so the rule rests on this and the record should say so"

Useful and kept: that the staged arrival is what the drawn guest doors rest on. Session-facing and goes: "and the record should say so". As it would then read: *"... no page read sets it out. It is the reason the drawn guest doors open into courts rather than against a building's flank, so the rule rests on nothing a reader can check."*

**HISTORY** - none visible; the feature-238 and feature-195 notes, and "the note had cited the SUMMARY-ONLY ... entry instead", are all comments (ll. 183, 190, 212, 217, 220, 224, 248, 253-257, 271 ✓). The absence notes searched 2026-09-14 (fn-81, 84, 87-110) are the permitted form and carry no verdict language in visible text ✓.

---

# 5. `research/citations/vegetation.html`

## The works section (ll. 15-~200)

**SESSION NOTE** - fetch verdicts and a stray "used for" tail inside a citation line the reader meets.
> l. 23: "... (https://...; the full text is paywalled: doi 10.1016/j.biocon.2011.01.023; **unsupported by any readable page until then**) - **the ABSTRACT is public on that page and was read** - **3403 plants/ha, 49.1 m2/ha, 32 well-protected patches, one 1200 m² transect each**"

Three problems in one line: "unsupported by any readable page until then" is a verdict fragment whose "then" refers to nothing a reader can see; "was read" is a fetch verdict; and the figure list is the registry's old `Used for:` tail, which the works section is not supposed to carry (the two write-ups below it already say all of this properly). Proposal: **comment** the verdict and the tail. As it would then read: *"Hu, Li, Guo et al., "Values of village fengshui forest patches in biodiversity conservation in the Pearl River Delta, China", Biological Conservation 144 (2011) (https://...; the full text is paywalled, the abstract public)."*

The same tail shape, smaller, at: l. 31 ("- the concept (...), regional totals and the 57-village survey mentioned;" - note the trailing semicolon), l. 103 ("- describes the edge generically ... and does NOT carry the herb-fringe / shrub-belt / forest-mantle layers", which the write-up at l. 105 already says better), l. 119, l. 135 ("- the Wiley page shows the full text to a reader with no subscription" - a readability verdict), ll. 143, 155, 159 ("- Korean analogue").

**DEFECT** - dangling trailing dash on two citation lines: l. 19 `... DOI 10.3390/f11121286) -` and l. 27 `...-fengshui-forests.pdf) -`. Proposal: drop the dash.

**HISTORY** - what this record used to claim.
> l. 61: "It is the source that reversed this record's own claim, which had a fluctuating table resisting alder when fluctuation is where it expands."

Useful and kept: the finding itself (reed on permanently inundated ground; alder unable to establish where water stands 0.4 m or more above the ground; alder spreading where the table is below the surface and swings). History and goes: the sentence about the record's own reversed claim. As it would then read: *"Its limits: one mire in the coldest part of Japan ..."* - and the paragraph's closing caution ("Read the two figures together and not separately: the paper's abstract gives ... and its body gives ...") should stay, since it is about the SOURCE and a reader hovering the note needs it.

**VOCABULARY** - `hydrosere` (l. 137): `defined inline`. `ほ場整備` (l. 39) is untranslated in a citation line - proposal: "Aomori prefecture's field-consolidation (ほ場整備) standard drawing set". `sugumagi`, `batter`, `subgrade`, `species richness`, `basal area`, `flume` (under `kakehi`), `GIS` ✓. `maeulsup`/`Maeulsoop` appear only inside work titles ✓.

## The notes (ll. ~250-380)

**HISTORY** - a correction of a past byline in visible text.
> fn-64 (l. 325): `... (the paper's byline is Chris Coggins and Jesse Minor, not "Chen & Coggins")`

The correct byline is already in the note's own key link and in the works entry (l. 27). Useful: nothing beyond the correct byline. Proposal: **drop** the parenthetical (the reversal is in git and in the comment at `vegetation.html` l. 31). As it would then read: the quotation and its section pointer alone.

**SESSION NOTE / DEFECTS** - none else: the `<!-- pdftotext -->` markers, "mdpi.com refuses automated fetches", "the journal host refuses this container", "a prior pass had read this abstract as giving 25 years" and the feature-238/194/235 notes are all comments (ll. 325-340, 369 ✓); every non-English passage carries its translation note with the original following ✓; no `((`, no `||`, no duplicated renderings on this page.

---

# 6. `research/citations/cities/river-cities.html`

## The works section (ll. 15-123)

**VOCABULARY** - `mole`
> "It gives the projecting mole and the flight of steps as the two forms of a landing, which this page draws" (l. 101; also fn-31, l. 155)

Draft: *"mole - a solid stone or earth pier run out from the bank into the water, the other form a landing takes beside a flight of steps."*
**VOCABULARY** - `sogamae` ✓ glossary; `Republican-era` (l. 121) - plain enough; `revetment`, `quay`, `takasebune`, `koku` ✓.
**SESSION NOTE / HISTORY / DEFECTS** - none. The `ignou-silt-control` write-up's closing clause ("a certificate warning in front of it, and an OCR layer that damages the very degree signs the finding turns on", l. 57) is a limit a reader needs, and the "checked against the rendered page" note is a comment ✓.

## The notes (ll. 125-166)

**DEFECT** - a sentence quoted twice inside one note.
> fn-5 (l. 130): `「It consists of a section of the old Suzhou City Wall that includes two separate gates ... It is thus sometimes known as Suzhou's Land and Water Gate.」 「It is thus sometimes known as Suzhou's Land and Water Gate.」 (English)`

Proposal: drop the second 「」.

**DEFECT** - duplicated English rendering after the marked translations, twice:
- fn-8 (l. 133): `... ("the streets outside the city gate and the area near them"; "in antiquity, the lodges near a city's walls". Supports guan-xiang = the district outside a gate; that it was a MARKET is a GUESS ...)`
- fn-12 (l. 136): `... ("from the Edo period, wholesale merchants and their storehouses (kura) gathered at the kashi ..."; "at the center of a kashi was the kashi-donya ...". "Directly behind the bank street" is not stated)`

Proposal: drop the repeats, keep the limit clauses ("that it was a MARKET is a GUESS ...", ""Directly behind the bank street" is not stated") - those are the honest labels.

**VOCABULARY** - `hiro` (fn-27, l. 151, inside a quotation: "Bottom length 12 hiro 1 shaku (about 22.20 m)"): `defined inline` by the metric conversion; `jo`, `shaku`, `koku`, `ton'ya`/`tonya` ✓. `Guanzi` (fn-38, l. 162: "the Guanzi's siting rule stood behind a security page") is unexplained - draft: *"Guanzi - the classical Chinese compilation whose chapter on city building gives the rule for siting a settlement between hill and water."*
**SESSION NOTE / HISTORY** - none visible; the feature-238 notes are comments ✓, and the absence notes (fn-14, 18, 21, 22, 35, 38, searched 2026-09-12/14) are the permitted form.

---

# 7. `research/SOURCES.html` - the 250 entries marked `<!-- READ 2026-09-14 by a source-reader (feature 242) -->`

The markers run every five lines from l. 411 to l. 1656 (250 entries: `<h3>` key, citation line carrying the marker, `What it is:`, `Why it applies, and its limits:`, `Used for:`).

**The marker itself is correct** - it is an HTML comment at the head of the citation line, invisible, exactly where a fetch verdict belongs. Nothing to report on it.

**SESSION NOTE** - none in the visible text of the sampled entries (ll. 411-460 read in full; the whole band pattern-scanned for `SUMMARY-ONLY`, `NOT-FOUND`, `CONTRADICTED`, `unfetched`, `not re-read`, `leftover`, `re-sourced`, `feature NNN`, `T<nn>`). Every hit in the band is inside a comment; the only visible verdict language in the registry is the permitted form *"Not cited: no publicly readable page carries the passage the record relied on."* Two notes for the session rather than findings: (i) `Used for:` is the registry's own field, kept out of the derived works section, so it stays; (ii) the registry's front matter (l. 21) carries a visible session ledger - *"**Feature 143 (2026-08-28) worked the whole queue and every `not recorded` entry**"* - and l. 26 a visible "(feature 143 leftover)". Those are outside the READ-2026-09-14 band, and spec 209 D6 holds the registry out of rules 2 and 3; I report them only so the session knows they exist.

**HISTORY** - none in the band's visible text.

**DEFECT** - **untranslated foreign titles in the citation lines, which the works section puts in front of the reader.** Of the 250 marked entries, 70 citation lines carry Chinese or Japanese in the title, and the great majority give no English at all: e.g. l. 431 `吴钩, <em>1000年前的小区围墙是怎样被推倒的</em>, 儒家网`; l. 441 `ミツカン 水の文化センター (Mizkan Water Culture Center), <em>木で作られた水道管 ～江戸時代のインフラを支えた上水道のかたち～</em>`; l. 446 `上下水道情報plus, 連載<em>水道の話いろいろ</em>(7) 江戸明治の上水`; l. 486, 511, 516, 521, 531, 546, 551, 571, 601, 606, 611 and on. The record's own better practice is present in the same file (l. 471 `《大清律例》兵律, article 夜禁 (the Great Qing Code, the night prohibition)`, l. 526 `《周禮·冬官考工記》 (the Zhouli, Kaogongji chapter)`) and in `citations/vegetation.html` l. 155, which gives a Korean title as a marked translation. Proposal (one decision, mechanical afterwards): every citation line gives the work's title in English with the original beside it, as the feature-202 rule gives every other foreign passage.

**VOCABULARY** - the band's write-ups are written for the reader and lean on glossary terms that exist (`yamen`, `lifang`, `kurayashiki`, `zicheng`, `luocheng`, `tulou`, `gangi`, `sogamae`, `koku`, `tsubo` ✓). Three terms recur in them with no entry and no inline gloss: `Baidu Baike` (l. 421-423 - an open-edit Chinese encyclopedia, and the entry itself says so ✓ `defined inline`), `eGyanKosh` (l. 55 of the river-cities works, the Indian university repository - `defined inline`), and `J-STAGE` (`citations/vegetation.html` l. 60: "free on J-STAGE"). Draft for the last: *"J-STAGE - Japan's national platform for scholarly journals, where many Japanese papers are free to read."*

---

# Summary tables

### `research/buildings.html` (24 sections)

| section (line) | VOCAB | SESSION | HISTORY | DEFECT |
|---|---|---|---|---|
| head / h1 / lead (6, 14, 15) | 2 (`Mode A`, `L7R`) | 1 | 0 | 0 |
| Japan-first interiors (20) | 0 | 0 | 0 | 0 |
| Office front, residence behind (25) | 0 | 0 | 0 | 1 (untranslated quote) |
| Every compound keeps a shrine (30) | 0 (1 inline) | 0 | 0 | 1 (`Ochiba` wrong tooltip) |
| Cells are remand (36) | 0 | 0 | 0 | 1 (Japanese-only work name) |
| Clerks are few (42) | 0 | 0 | 0 | 0 |
| Staff housing (48) | 0 | 0 | 0 | (roster, file-wide) |
| A compound wall (53) | 0 | 0 | 0 | 1 (dangling clause) |
| Granary as staging node (60) | 1 (`Hida`) | 0 | 0 | 0 |
| Courtroom is a room (65) | 0 (3 inline) | 0 | 0 | 0 |
| No interrogation room (70) | 0 | 0 | 0 | 1 (untranslated quote) |
| Poverty texture (75) | 0 | 0 | 0 | 0 |
| Guest doors (81) | 0 | 0 | 0 | 0 |
| Ancestral alcove (86) | 0 (1 inline) | 0 | 0 | 0 |
| Mode A scale (91) | (`Mode A`) | 0 | 0 | 1 (untranslated figure) |
| Granary holds grain (96) | 2 (`commutation`, `NTA`) | 0 | 0 | 0 |
| Fire discipline (101) | 0 | 0 | 0 | 1 (five times vs. over and over) |
| Fire-water (106) | 0 (1 inline) | 0 | 0 | 1 (footnote inside `<em>`) |
| Size hierarchy (111) | 0 | 0 | 0 | 1 (二間四方 unglossed) |
| Packing (116) | 0 | 0 | 1 (`not 24`) | 2 (`fire-gap` no tooltip; broken MD link in comment) |
| Rendering / layout checked (122) | 0 | 1 (heading) | 0 | 0 |
| A dojo is a city institution (138) | 1 (`Toshi Ranbo`) | 0 | 1 (`boom of 1830-1860`) | 1 (`- .`) |
| Privies (144) | 0 | 0 | 1 (one-inner-one-outer rule) | 1 (`parlor,;`) |
| Shady rear (149) | 0 | 0 | 0 | 0 |
| **file-wide** | - | - | - | 3 (roster run-on ×7; footnote order; raw CJK ×13) |
| **totals** | **6** | **2** | **3** | **15 + 3 file-wide** |

### `research/vegetation.html` (17 sections)

| section (line) | VOCAB | SESSION | HISTORY | DEFECT |
|---|---|---|---|---|
| lead (15) | 0 | 1 (`generator`) | 0 | 0 |
| The fengshui forest (20) | 1 inline (`동구숲`) | 0 | 0 | 1 (fn-73 no id) |
| The three groves (34) | 2 (背山面水, 后龙林/水口林 forms) | 2 | 0 | 1 (背山面水 untranslated) |
| Does a belt wrap? (98) | 0 | 0 | 1 (borderline, l. 154) | 0 |
| Belt off the sheet (166) | 0 | 4 | 0 | 0 |
| Hillside past the grove (214) | 0 | 0 | 0 | 0 |
| Forest density (247) | 0 | 0 | 0 | 0 |
| Belt's crowns (256) | 0 | 0 | 0 | 0 |
| No canopy under a crown (266) | 0 | 0 | 0 | 0 |
| Crop margin (282) | 0 | 0 | 0 | 0 |
| Scrub off open water (292) | 0 | 0 | 0 | 0 |
| The cut bank (306) | 0 | 0 | 0 | 0 |
| Marsh margin (315) | 1 inline (`hydrosere`) | 3 (`ACCURATE` ×3, incl. heading) | 1 (`now`) | 1 (raw plant-community names) |
| Scrub under a village wood (369) | 1 (`AGRIS`) | 0 | 0 | 2 (duplicated clause; **nested comment leak**) |
| Coppice lot bounded (408) | 0 | 1 (`not read`) | 1 (duplicated provenance label) | 1 (stray comma) |
| Bamboo (442) | 1 (`zelkova` variant) | 3 | 3 (`this page's earlier placing`, `the record's "N/W strip"` ×2) | 0 |
| Flat map / slope (527) | 0 | 0 | 0 | 0 |
| **totals** | **6** | **14** | **6** | **6** |

### `research/cities/river-cities.html` (5 sections)

| section (line) | VOCAB | SESSION | HISTORY | DEFECT |
|---|---|---|---|---|
| lead (15) | 0 | 1 (`generator`) | 0 | 0 |
| Most cities sit on a river (19) | 2 (`shuimen`, `Imperial spine`) | 0 | 0 | 1 (footnote inside `<em>`) |
| Which way does an offtake leave (31) | 1 (`separated flow`) | 0 | 1 (parallel right angles / `now`) | 0 |
| One mouth on the river (40) | 0 | 0 | 1 (the 36 ft doubled channel) | 0 |
| The wharf's working face (47) | 0 | 0 | 0 | 0 |
| **totals** | **3** | **1** | **2** | **1** |

### The citations pages and the registry

| page | VOCAB | SESSION | HISTORY | DEFECT |
|---|---|---|---|---|
| `citations/buildings.html` | 2 (`sun` gloss, `Dacheng gate`) | 2 (fn-25 verdict; fn-79 instruction) | 0 | 9 (5 duplicated renderings; 2 `((English).`; fn-51's `\|\|` + double quote + `((...))`; ~20 untranslated titles) |
| `citations/vegetation.html` | 1 (`J-STAGE`) + 1 inline | 7 (the `hu-2011` line's 3; 4 `used for` tails) | 1 (`reversed this record's own claim`) | 3 (2 dangling dashes; ほ場整備 untranslated) |
| `citations/cities/river-cities.html` | 2 (`mole`, `Guanzi`) | 0 | 0 | 3 (fn-5 doubled quote; fn-8 and fn-12 duplicated renderings) |
| `SOURCES.html`, the 250 `READ 2026-09-14` entries | 1 (`J-STAGE`); rest covered | 0 in the band (2 in the file's front matter, outside it) | 0 | 1 class, ~70 lines (untranslated titles, derived into every works section) |

### Glossary terms to add (`l7r/diagram/interactive/assets/glossary.json`)

| term | variants | draft definition |
|---|---|---|
| `Mode A` | `Mode A` | The building-plan half of these maps: one walled compound drawn at three times the detail of a settlement map - a compound sheet at a third of a foot per pixel, a hamlet or town at one, a village at two, a city at three. |
| `L7R` | `L7R`, `L7R's` | The GM's own edition of the Legend of the Five Rings setting these maps are drawn for; its notes are the record's canon rather than its evidence. |
| `Hida` | `Hida` | The mountain province of central Japan, held under direct shogunal rule and administered from Takayama, whose intendancy is the one such compound that survives. |
| `commutation` | `commutation`, `cash commutation`, `commuted` | Paying in coin a tax assessed in grain; the dry-field share of an Edo land tax was usually settled that way, which is what put money in a farming village. |
| `Imperial spine` | `Imperial spine` | The Imperial road where it runs through a settlement as its main street, the axis a map's road net hangs on; a river city has none, its highway passing off the sheet. |
| `separated flow` | `separated flow`, `separation zone`, `zone of separated flow` | The pocket of slack, recirculating water just inside the mouth where one channel enters another; the wider the junction angle, the larger it is. |
| `mole` | `mole`, `moles` | A solid stone or earth pier run out from the bank into the water - one of the two forms a landing takes, the other being a flight of steps. |
| `Guanzi` | `Guanzi` | The classical Chinese compilation whose chapter on city building gives the rule for siting a settlement between hill and water. |
| `Dacheng gate` | `Dacheng gate` | The main gate of a Chinese Confucian temple precinct, outside which the shrines to worthy former officials and to local worthies stood. |
| `AGRIS` | `AGRIS` | The FAO's international agricultural research database, where a paper's bibliographic record and abstract can be read when the article itself cannot. |
| `J-STAGE` | `J-STAGE` | Japan's national platform for scholarly journals, where many Japanese papers are free to read. |
| `Toshi Ranbo` | `Toshi Ranbo` | A city of the setting, cited here for the GM's own notes on its many dojos. |

**Variants to add to existing entries:** `fire gap` += `fire-gap`, `fire-gaps` (five misses on `buildings.html` l. 121); `keyaki` += `zelkova`, `Japanese zelkova`; `water gate` += `shuimen`, `水门`.

**Not a glossary term, by measurement:** `sun` (the tenth of a shaku) - a case-insensitive entry would fire on every ordinary "sun" in the record; gloss it in place instead.

**One collision to decide, not to add:** `ochiba` (fallen leaves) fires on the manor named **Ochiba** at `buildings.html` ll. 34, 95, 121.