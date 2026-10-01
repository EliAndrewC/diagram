Ashigawa needs work: it is a copy of Sawada, an existing hamlet in the pool, not a place of its own.

```
UNIT: settlement-review--ashigawa   MAP: ashigawa   TIER: hamlet   SCALE: 1.0 ft/px   OCCASION: map new to the pool
TWIN DETECTOR: 1. The generator spec is the same as sawada.gen.py's, argument for argument except the name: seed 24, 19 households, land falling 225 (northwest), drain leaving off the map, open intake, alley lanes, unsettled paddy rest, changeable autumn weather.
               2. The manifests match: houses, wells, bridges, threshing yards, gardens, groves, marsh, byres, commons and farm fixtures are identical. The metadata differs only in the name and the count of rested paddies (3 against 4).
               3. The two renders differ only in the title and where the rested paddy patches sit; the notes even repeat Sawada's subject line.
               -> RE-SKIN of sawada (error)
DECLARED ECONOMY: rice -> drawn (the paddy comb south-centre, dry plots and barley strip along the collector)
                  reed-cutting for thatch and mats -> drawn only as the marsh toe in the northwest half; nothing shows it is worked, and no way leads from the houses to the marsh (questionable)
FIRST IMPRESSION: the reed marsh fills about 40% of the sheet, the eye lands on the paddy comb, and the houses are pressed into the northeast corner. It reads as a marsh-edge hamlet, but the layout is Sawada's.
FABRIC: not applicable (no new tier)
VERDICT: needs-work
```

1. **Error, against the twin detector (judge 1 of my contract): a re-skin of Sawada.** No structural fact tells the two maps apart. The fix is a seed and spec that make a different place (another slope direction, water sink, lane pattern or cluster shape), or taking Ashigawa out of the pool.
2. **Questionable, against the declared-economy check (judge 2), measured against the notes' "What it is here to show".** The reed-cutting trade appears only as the marsh itself. The map's own metadata says no field path exists, because every way from the lanes crosses water, the marsh or a farmstead. Whether the generator has any element that shows reeds being cut is a question about the generator, not this map.
3. **Nitpick (no rule to measure against).** The sheet's layout is inherited unchanged from Sawada.
4. **Confirmations.** The notes file is present. The name's kanji check out: 芦 *ashi* "reed" + 川 *gawa* "river". The water flows northwest, as the notes say. The gate read `green` at the start and again just before the verdict, and this unit had no previous verdict.

The verdict command printed: `recorded NEEDS-WORK for settlement-review--ashigawa (engine key NONE - no dispatch recorded, gate green)`

The "engine key NONE" matches the dispatch, which said the engine key was not computed. The findings file is outside the repository, at `/tmp/claude-1000/-diagram/68560146-7086-4e5b-a430-f5b48028631d/scratchpad/t34/ashigawa-findings.json`.
