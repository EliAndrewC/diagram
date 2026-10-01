# Sweep water G05 - handoff (session 1: write)

- SECTION=water/which-way-water-flows-and-how-channels-bend-and-join
- RENDERING=rendering/water/how-our-maps-draw-bends-junctions-and-the-run-of-the-water
- OLD=research/contents.json#water research/contents.json#water research/contents.json#water research/contents.json#water research/contents.json#field-archetypes research/contents.json#river-cities research/contents.json#river-cities
- MODALS=
- BASE=4470bc01a

Which way water flows, and how channels bend and join: all seven sections folded (no claim held any of them). 020 and 600 were folded in, not cross-linked. Cut, each with a REMOVED comment: 190's unsearched "lower bound below 30 degrees" silence; 190's "a drawn junction has to say which of the two it is" (moot once modern figures are not the map's warrant); 020's tilt history (22 and 10 degrees). 020's unsourced sentence on tributaries and drainage returns pointing downstream now stands as a labeled GUESS. The two IGNOU notes that 190 and 020 both quoted are one note each, taken from 020's fuller copies, with the keys swapped so that `ignou-silt-control` is the river case and `-2` the canal case. No modal's `Entry:` named a folded section. Links re-aimed: 0146 (twice, to the research section), 0059 (to the rendering section), and code comments in hamletgen/consts.py, settlement/water_ways/water.py and settlement/city/moat.py, plus the legacy nagahara.gen.py. Left open for the checker: the rendering keeps both the downstream lean of a branch offtake (the Edo slanting weir) and the square moat-to-river junctions (no period angle). That is how the folded sections had it, but a reader may see a tension, and moat.py's docstring still says the moat's feet tilt with the current.
