# 292 sweep water G07 - handoff (session 1: write)

## Field drains (akusuiro)

- SECTION=water/field-drains-akusuiro
- RENDERING=rendering/water/how-our-maps-draw-field-drains
- OLD=research/contents.json#water research/contents.json#fields research/contents.json#fields research/contents.json#water
- MODALS=DrainageDitch
- BASE=0f92beb3e

All four sections were folded; no other feature held any of them in progress. No finding was cut: the REMOVED comment names only the four Sources: rosters, 260's inciting-question paragraph, fields 080's pointer to the taper finding and one restating sentence. The duplicate shonairyo-akusuiro-jawiki notes were merged into one, and four keys were renamed because the same keys were already on the water page (suido-ishizue-minuma-2, matsuura-2017-minuma-4, kaogongji-wikisource-2, hattori-site-yayoiken-2). The two old-form absence notes were converted. Kanji were dropped from two note glosses (akusuiro-kotobank's dictionary name, maff-nogyoyosui-suiden-2's channel names) to pass the prepass. The map rules (the drain's head width, the declined angle rule and readability fixes, the discharge-end attribution and the trimmed in-wall drain) moved to the rendering section, with each ruling in a comment. The DrainageDitch class has no entry in tests/fixtures/classes_before_189.json, so the fixture is unchanged. The links in 0014 and 0059, and the comment in hamletgen/sink.py, now point at the new sections. The Minuma layout (0053) and the tanning yard on a field drain (urban-features 064) are cross-linked. One confusable pair was appended: field drains / irrigation canals.
