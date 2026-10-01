# buildings G22 - handoff (session 1: write)

## Merchants' townhouses (machiya)
- SECTION=buildings/merchants-townhouses-machiya
- RENDERING=rendering/buildings/how-our-maps-draw-a-merchants-townhouse
- OLD=research/contents.json#compounds
- MODALS=

## Chinese courtyard houses (siheyuan)
- SECTION=buildings/chinese-courtyard-houses-siheyuan
- RENDERING=rendering/buildings/how-our-maps-choose-between-the-courtyard-house-and-the-japanese-house
- OLD=research/contents.json#compounds
- MODALS=

## Inns (hatago and carters' inns)
- SECTION=buildings/inns-hatago-and-carters-inns
- RENDERING=rendering/buildings/how-our-maps-draw-an-inn
- OLD=research/contents.json#compounds
- MODALS=

- BASE=6b744fcaa

## Left open

Merchants' townhouses: nothing was held by another feature (280's B3 claim on 0184 closed as done on 2026-09-29). The plan said "rendering: none", but 790 carried a map rule, so it got a rendering section, as G21 did for 770. 760's Japanese townhouse half (kotobank-machiya, machiya-shoka-jawiki - the rich townsman's dwelling behind the shop) moved here; 790's Chinese street shop (qixian-cnr-2) was merged into 760's qixian-cnr, which quotes the same passage, and is told once at the courtyard topic (REMOVED comment). 790's visible search for the split form's link to wealth became an absence note in the rendering section. 0119's link now points at the new section. The pair with cities/fabric/220 is logged as a confusable.

Chinese courtyard houses: 760's absence note named a Pingyao museum page "said to sort its houses" by household, which no one could fetch; that claim is now only in the note's search comment (REMOVED comment). 760's "a settlement follows one tradition or the other" and "What it means for a map" moved to the rendering section, which also carries the Chinese half of 790's rule; 0090's link to the old anchor now points at the new rendering section. No generator rolls a settlement's house form, so the rule stays a spec.

Inns: the title departs from the plan's "Inns (hatago and kezhan)". No source the record quotes names the Chinese inn kezhan, and the registry key kezhan-zhwiki is reserved but never written in diagram-research-5 (`make reserve` refused it here), so the title names the carters' inn that the sources describe. The two old-form absence notes were converted: one stays at the research section (a Chinese inn's size), and the one on where the bath and privy stood became `how-our-maps-draw-an-inn-2` in the rendering section. The ken-conversion grounds note is copied to both pages. The confusable pairs with 0186 (honjin) and towns/040 (flophouse) are logged. The existing `caravan_inn_form` knob (towns/050) is a separate rule, noted in a comment.
