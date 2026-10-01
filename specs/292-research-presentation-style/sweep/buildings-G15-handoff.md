# Handoff - feature 292 sweep, buildings G15 (write)

## Privies (setchin)

- SECTION=buildings/privies-setchin
- RENDERING=rendering/buildings/how-our-maps-place-privies-setchin
- OLD=research/contents.json#compounds research/contents.json#compounds
- MODALS=Latrine SideGate

## Baths (furo)

- SECTION=buildings/baths-furo
- RENDERING=rendering/buildings/how-our-maps-draw-the-bath-furo
- OLD=research/contents.json#compounds
- MODALS=Bath

- BASE=8de57023a

## Left open

- Privies: no section was held by another feature, and no claim was cut. The Sources roster and 310's pointer sentence to 220 went, per the REMOVED comment. kotobank-benjo-3 (310) quoted the same passage as kotobank-benjo-2 (220), so they are one note now. Two findings were quoted in the old notes but not stated in the old prose, and are now bullets: the shared privy building of a compound's row houses (kotobank-benjo), and the back gate kept for night-soil collection (guernica-night-soil-2). The sand-box absence note, keyed to the old section id, is now `privies-setchin`. In the rendering section, three GUESSes carry no footnote because the record holds no search for them: the 5 ft privy, the 15 ft from a well, and the count of about one privy to each part of the compound. The code comments said the same before. The kawaya glossary definition described only the farm privy; it now says the samurai residence's privy was built into the house.
- Baths: no section was held by another feature, and no claim was cut. One finding was added from a note the privies section already quoted: the Yokota house's town history counts one bath and lists a bath room among its additions by about 1868. It is copied here as `nagano-shishi-yokota-4`, because -2 and -3 were taken on the page. It is worded as a question, because the page does not say the counted bath is the added one. A new glossary term `furo` was added (prefix 19300). The Bath modal says the bath is "drawn with a curl of steam", but I found no steam mark in the compound code, so the rendering section does not mention one. entry-drift should look at that.
- Code comments and a test docstring (compound_model.py, compound_parts.py, tests/test_compound.py) now name the new titles in place of "research 0101/320".
