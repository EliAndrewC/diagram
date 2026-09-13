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
