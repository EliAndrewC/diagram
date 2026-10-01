# Feature 292 sweep - buildings G12 handoff (session 1: write)

- SECTION=buildings/samurai-residences-and-their-rooms-buke-yashiki
- RENDERING=rendering/buildings/how-our-maps-lay-out-the-residence
- OLD=research/contents.json#compounds research/contents.json#compounds research/contents.json#compounds research/contents.json#compounds research/contents.json#compounds
- MODALS=Residence ServantsQuarters GuestQuarters Kitchen Well Latrine Storehouse ResidenceCorridor LordsQuarters FamilyQuarters InnerRooms ReceptionRoom InnerCourt CompoundGarden RearYard
- BASE=68cc19417

Samurai residences: all five sections folded, none held by another feature. Cut under STYLE.md 4, each in the
REMOVED comment: the five Sources: rosters; 250's note touken-world-buke-madori, which quoted the same three passages
as 260's touken-world-buke-madori-2 and -4 (its one claim now cites those two, and its originals were not copied); 260's
restating "So at the palace scale..." paragraph; 230's pointer sentence to the vegetable-garden section (now a link).
Two new absence notes: samurai-residences-and-their-rooms-buke-yashiki (research, copied to rendering) turns 230's
roster sentence "the rest of the north service strip has no readable source" into an absence note, with a fresh
search of 2026-09-30 (two web searches in Japanese, no page fetched, so nothing on the ledger); how-our-maps-lay-out-the-residence
(rendering) turns 250's "no source read here says how Katsura's halls are joined" into one, dated to 250's research
of 2026-09-27. Both, and the converted kitchen-share-absence and guest-house-absence, want the quote-check's eye.
The brief's note says the 67-tsubo house is the drawn house. The record and compound.py say otherwise: the drawn
house is held to the Yokota house's 49 tsubo, and the Matsue 67-tsubo figure is "not used as a measure" because it
measures a Meiji-era plan. The rendering section says the latter. The "about ten servants" in the rendering is the
plan's own count, labeled a GUESS, as ServantsQuarters labels it. No modal's prose was rewritten, only its Entry, so
entry-drift is owed on all 15. The fixture needed no change: only well and garden are in it, and neither entry named a
folded title. Links re-aimed: 0116 (to the new research section) and 0109 (to the rendering section,
since it pointed at the reasoning that puts the service at the rear); code comments in compound.py and
compound_model.py. The confusable pair with 0118 is in confusables.md.
