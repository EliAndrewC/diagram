# fields G06 handoff (feature 292 sweep, session 1: write)

- SECTION=fields/how-much-farmland-a-settlement-works-and-in-what-tracts
- RENDERING=rendering/fields/how-our-maps-size-a-settlements-farmland
- OLD=research/fields/110-plot-sizes-pond-sizing-and-acreage-from-population.html research/fields/120-tract-sizes---no-settlement-class-cap.html
- MODALS=

- SECTION=fields/farmland-around-towns-and-cities
- RENDERING=rendering/fields/how-our-maps-draw-the-farmland-around-a-town-or-a-city
- OLD=research/fields/130-what-is-the-farmland-around-a-town-or-a-city-made-of.html research/cities/hinterland/020-why-is-a-city-ringed-by-farmland-on-every-side.html
- MODALS=

- BASE=b2856c5e0

How much farmland a settlement works, and in what tracts: no section was held by another feature. 110's pond-sizing paragraph (the Hoshigaoka pond and the storage-per-hectare absence note) sits in this topic's rendering section, since water T3 has not folded; T3 may take it and leave a pointer. Cut with a REMOVED comment: 120's Li Bozhong "ten mu per farmer" (the eh.net review does not state it), the ~1.5 acres a Chinese household it gave, and the mu-land-enwiki note that only converted it (its glossary term "Beiyang government" was then used nowhere and was deleted), 120's sentence on Buck's unread parcel counts, and 120's unsourced county-seat and post-town claims. The household band now reckons from the setting's household of about five (linked to settlements) where 120 used an unsourced 4.5. Kanji dropped from five note glosses in our own words (the to, the Yamakawa dictionary, the Edo illustrated reference, Britannica, Nipponica) to pass the prepass. fields/650's two links now point at the rendering section; the code comments in houses.py, palette.py, hill.py and both test_villages.py files that named 110 for the plot size now name 'How our maps draw rice paddies and their plots (suiden)', and comb.py's field_fall comment names this rendering section.

Farmland around towns and cities: no section was held by another feature. towns/400 (the town's night-soil vegetable edge) was left out as outside this brief's list, and could fold here later. Cut with a REMOVED comment: the "garrison" half of hinterland 020's opening (this page's own words). The hinterland shizen-teibo-jawiki and kohai-shicchi-jawiki notes became -2 on the fields page, where fields 160 already holds different passages under those keys. nearring.py's two docstrings now name the rendering section.
