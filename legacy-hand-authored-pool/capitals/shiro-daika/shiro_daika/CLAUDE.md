# `shiro_daika/` - the domain capital of the Daika house, part by part

**`legacy-hand-authored-pool/capitals/shiro-daika` is the exhibit of a hand pass the GM dropped on 2026-10-07**: the capital goes straight to a
scripted generator, so this map is kept as it stands, not finished (`../shiro-daika.notes.md` has the record).

`../shiro-daika.gen.py` is the entry point, a short driver; importing this package draws the map.

**A LINEAR SCRIPT, not a library: importing a part EXECUTES it.** Each part imports `s` from the part IMMEDIATELY above
it, which is what enforces the order; `__init__.py` states the same order readably, behind `# isort: off`. The table
below is in execution order.

**Don't let isort touch the part list in `__init__.py`.** Sorted alphabetically, `fields` (which holds `s.finish()`) ran
fourth of seven and the wharf, the yashiki band and the trade works drew into a map already written to disk - with the
gate green, because no test rolls a frozen exhibit.

## Look here when

| file | look here when |
|---|---|
| `frame.py` | the wall and what it is an OUTPUT of - the budget, the rampart and its four gates, the river, the moat and patrol road, the ways and the kagi-no-te, the ote-suji |
| `castle.py` | the castle and the sovereign ground around it - its two gates, the circulating moat, the aqueduct and towpath, the bridges, the government ward, the Imperial Magistrate's compound, the eight lineage compounds, the two sovereign temples and the teramachi rim |
| `wharf.py` | the collecting-and-disbursing end of the domain's rice - the wharf, its jetties and granaries, the quay face, and the budget reconciliation |
| `housing.py` | the machi street mesh and the yashiki band - 53 walled compounds of Ranks 8-12 wrapping the castle, and the retainer terraces |
| `trades.py` | the private dojos, the merchant estates, the trade works and the gate caravan program, and the castle's firebreak ring |
| `civic.py` | what the packs must flow around - the kido mesh, the fire towers, and the public wells on their derived grids |
| `fields.py` | the farmland outside the wall - the comb fields, the ring fields, the furrows and topographic channels, and the finish |
| `__init__.py` | the engine bootstrap and the part order - the only two things that are not drawing |
