# 292 sweep - vegetation G03 handoff

## Bamboo groves (chikurin)

- SECTION=vegetation/bamboo-groves-chikurin
- RENDERING=rendering/vegetation/how-our-maps-draw-bamboo-when-one-culm-is-too-small-to-see
- OLD=research/vegetation/150-bamboo-how-common-where-it-stood-and-how-to-show-it.html research/vegetation/154-did-every-farmstead-keep-its-own-bamboo-and-on-which-side.html research/vegetation/260-did-a-farmsteads-grove-carry-bamboo-yes---mixed-in-low-under-the-tall-trees-on-its-windward-side.html research/vegetation/640-did-a-village-keep-a-bamboo-thicket-before-modern-times-yes---round-its-houses-on-dry-ground.html research/vegetation/152-how-is-bamboo-drawn-when-one-culm-is-too-small-to-see.html
- MODALS=HomesteadBamboo SharedBambooGrove Windbreak
- BASE=d49d68eb3

No section was held IN PROGRESS by another feature today, so all five were folded (291 R11 wrote vegetation 154 on 2026-09-30 with its checks owed, and that text is what was folded). Cut, with a REMOVED comment: 154's unread 1996 Tonami model homestead (the north-west strip by the kitchen drain); 154's search log of the Hikawa and Iide groves, now kept in a comment; the rosters and pointer paragraphs. Merged as one note: yashikirin-jawiki-4 into -3, and yashikirin-jawiki-8 into -5. The rendering section follows the code, not the superseded text in 152: per-farmstead strips instead of one stand on the cluster's shady north, the thicket on dry ground beyond the back row instead of at the field margin, the 14 ft short-axis floor, and the 8% grove bamboo share. Windbreak's `Entry:` named 260 and now names both new titles. Test comments in tests/interactive/test_classes_docstrings.py and tests/settlement/test_homestead_woods.py still refer to "vegetation/154", "260" and "640" as the sections a past rewrite rested on; I left those historical notes as they were.
