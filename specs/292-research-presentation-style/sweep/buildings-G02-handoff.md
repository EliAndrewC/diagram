# Feature 292 sweep - buildings G02 handoff (session 1: write)

## The size of a compound and the rank of its buildings

- SECTION=buildings/the-size-of-a-compound-and-the-rank-of-its-buildings
- RENDERING=rendering/buildings/how-our-maps-size-a-compound-and-its-buildings
- OLD=research/buildings/180-the-compound-has-a-size-hierarchy-not-just-individual-sizes.html research/buildings/700-which-is-the-biggest-building-in-a-magistrates-compound.html research/buildings/190-packing-a-jinya-is-mostly-open-and-the-fix-for-too-much-empty-space-is-consolidation-not-a-smaller-envelope.html
- MODALS=Residence Kitchen Stables CompoundShrine OfficeHall Barracks OuterCourt HearingCourt CartYard
- BASE=533407c0e

No section was held by another feature (267's line in the claims file is its finished G2 work on 180, and 280's buildings groups did not touch these three). Here is what is still open:

- **The first rendering page for buildings.** This is the first rendering section on the buildings page, so the session created `research/rendering/buildings/` from new `_front`/`_tail`/`_citations-*` templates copied from the homesteads ones, and raised the page count in `tests/interactive/test_citations.py` from 20 to 21.
- **Modals.** The brief named only Barracks and OfficeHall, but seven more modals named the folded headings. All nine now name the new research title and the rendering title. The fixture `classes_before_189.json` held none of them.
- **Claims cut** (each in the section's REMOVED comment):
  - 190's 3,000-tsubo site / 1,000-tsubo built figure. It came from a search summary, and its primary, the Takayama site report, is item 143 on the download list and has not been read.
  - 180's one-bay stall width. It is quoted at buildings 390, which is where T23 (stables) takes it.
  - 190's "residence and kitchen under the Takayama office's continuous roofs". It was narrowed to what the source says.
  - 180's GUESS that an office hall out-sized its residence. It is superseded by 700's measured Takayama figures, not cut.
- **A note with no quoted passage.** The old `takayama-jinya-city-13` note quoted nothing ("same passage as fn-65"). It now carries the site and plaza passages copied from `takayama-jinya-city-10` (buildings 140), with its originals. Only the gloss is new: the 12.6% is the two figures divided.
- **Links.** 380's link to "the size hierarchy" now points at the rendering section. cities/sizing 020's "how open a compound is" now points at the research section.
- **Maps still carrying the old anchors.** The generated pool pages `pool/magistracies/ochiba-roundtrip-test` and `county-magistracy-example` (and their `.gencache` copies) still hold the old anchors until they are regenerated.
