# W1 handoff - water: kinds (B21-B23), session 1: research and write (2026-09-27)

- SECTION=water/290
- SECTION=water/300
- SECTION=water/310
- SECTION=water/270
- SECTION=water/070
- KEY=kotobank-marukibashi
- KEY=kotobank-ipponbashi
- KEY=zhwiki-dumuqiao
- KEY=xinhua-jiahou-muqiao
- KEY=suido-ishizue-iseki
- KEY=kotobank-jakago
- KEY=hrr-agagawa-dento
- KEY=people-zhishui-2025
- KEY=pwsannong-quxi
- KEY=pwsannong-gudai-shuili
- KEY=thepaper-guangai
- KEY=unesco-xidi-hongcun
- KEY=zhwiki-hongcun
- KEY=zhwiki-chengkan
- KEY=ly-likeng

(`dobashi-jawiki` is an existing key, newly cited on the water page as `dobashi-jawiki` and `dobashi-jawiki-2` in 290. Its
registry write-up says nothing about the new use, which is the rarity of plank bridges. The check session should decide
whether its "Used for" line owes a clause.)

B21 KNOB - three forms of crossing over small water are attested, but the record cannot say which was laid over a paddy ditch: a single log or board (JA dictionaries, ZH wiki), logs under trodden earth (the Edo majority of bridges), and a planked deck (the "important few"). The width at which a ditch was bridged and the spacing of crossings are SILENT, with an absence note dated 2026-09-27, so the 2.0 ft line stays the GM's ruling - `Footbridge` (`classes/water_and_ways.py`) should stop being a bare guess. Its docstring is written from water/290 (`Entry:` should name it beside 070). The generator should roll the crossing form per settlement, evenly (the evenness is a guess), among a single-log glyph, an earth-decked log glyph and the present plank glyph. Placement and width rules are unchanged.

B22 KNOB - two sections.
- water/300: a weir on small water was built of what lay to hand, and four forms are read: a stake-and-woven-reed "grass weir", stakes and logs packed with clay (Kodera), a timber frame weighted with stone, and gabions (baskets 40-60 cm in diameter). No village weir's thickness is recorded (SILENT, absence note).
- water/310: the intake mouth at village scale is attested only as "an entrance" in the bank. Gates, slotted boards and timbers laid across a weir are recorded only on great works. The choice between a weir and none follows the brook's level, in both Japan and China. No proportion between the two is found, so the even roll in `INTAKE_FORMS` stays a guess, but its reason is now the missing level variable, not an absence of any rule.
- For the maps:
  - The weir glyph becomes a knob of four forms, each at its own drawn thickness: the fence at the ~1.5 ft visibility floor (a convention), gabions ~2 ft (read), and frame or crib 5 ft (`WEIR_THICK_FT`, still a guess).
  - The head race should open OUT of the brook's bank, not end in a rounded cap laid on the stream. This is the `fc:2371` misread, "What a reader takes for the river at the tap", and the width and hue findings there are untouched.
  - No gate is drawn.
  - The weir class's `Entry:` should add water/300 and the intake's should add water/310.

B23 KNOB - at a stream's scale both forms are attested. Xidi (UNESCO) and Likeng (a travel diary, the weakest source) are built along both banks, joined by bridges. Hongcun (UNESCO, zhwiki) and Chengkan (zhwiki) stand beside theirs, and Hongcun also has a dug channel through it, the way Harie does. So water/270's "the record shows the opposite at this scale" is now "the record supports either", and the one-bank rule is labeled a guess because the maps fix one form of a knob. The generator draws nothing differently until lanes can cross a brook. When they can, the bank is rolled per hamlet (beside it or astride it), and an astride hamlet needs bridges linking its two banks. `seat_cluster` / `_far_bank`'s reasoning comments should cite 270's new wording.

## Left open, and why

- **water/250 was NOT edited**, though B22 names it. It is 39.7 kB with its notes, twice the 20,000-byte cap, so touching it obliges a split along its topics. That is a larger job than this group's items, and it would move another feature's footnotes. 300 and 310 point at it; it does not yet point back. Whoever next works water/250 splits it and adds the two pointers: at "each hamlet rolls one or the other with an even chance" -> 310, and at "its thickness is drawn at five feet, a guess" -> 300. 250's own statements are still true as written.
- The 290 knob and the 300 knob each rest on an even roll, which is a guess. The class labels are in the text.
- `check-question-size.py` still reports `homesteads/210` at 20,060 bytes. That is not W1's section (group H3 / F-groups of this feature), it was over before this session, and it is recorded here only so the next gate run is not a surprise.
- Nothing in this group owes a correction to 265, 267 or 268. `ways/030` ("What is a plank bridge") is not in 265's list. It still names the crossing an itabashi without the other two forms, and whoever rewrites the `Footbridge` modal should add a pointer from ways/030 to water/290.
- No claims by other sessions touched B21-B23 (RESEARCH-CLAIMS.md read 2026-09-27).
- Nothing was added to TO-DOWNLOAD.md. The one PDF that might give a crib frame's size, the Kanto office's Hamura weir leaflet (ktr.mlit.go.jp .../000099135.pdf), has no text layer here. It is river-scale in any case.
