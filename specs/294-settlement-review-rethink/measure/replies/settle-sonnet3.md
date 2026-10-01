UNIT: settlement-review--ashigawa   MAP: ashigawa   TIER: hamlet   SCALE: 1 ft/px   OCCASION: map new to the pool

TWIN DETECTOR: Ashigawa is a RE-SKIN of Sawada (error). I could not name three structural facts that tell the two maps apart.
1. `ashigawa.gen.py` carries Sawada's `HamletSpec` verbatim. It has seed=24, households=19, down_deg=225, water_sink=offmap, intake=open, lane_web=alleys, paddy_rest=unsettled and harvest_weather=changeable. Only the name differs.
2. The two renders show the same sheet: the same house cluster and lane comb, the same marsh toe at the left, the same field outline and bund grid, and the same collector with the same strip of racks along the bottom edge.
3. The manifests differ in about 620 diff lines. Most are field-name strings and small `bedz` offsets, and a few unsettled paddies are scattered differently.

DECLARED ECONOMY:
- Rice paddies and drying racks are drawn. The paddy comb sits at the lower left and the racks run along the bottom edge.
- Reed cutting for thatch and mats is declared in `ashigawa.notes.md` and ABSENT (error). The marsh is only the generic reed contour band, the same as Sawada's. No reed stacks, mats or thatch work appear at the houses or the marsh edge.

FIRST IMPRESSION: The eye lands on the paddy comb. The village sits in the top-right corner and its ways read clearly, with one spine lane and spurs. The upper-left quarter is bare marsh tint with nothing in it.

FABRIC: not applicable, since this is not a new tier.

VERDICT: needs-work

ERRORS / QUESTIONABLE / NITPICKS / CONFIRMATIONS:
1. ERROR, F1 (norm: contract item 1, the twin detector): re-skin of Sawada. Giving Ashigawa its own seed or spec parameters (down_deg, intake, lane_web or archetype) would make it structurally different.
2. ERROR, F2 (norm: contract item 2, declared economy): the reed-cutting trade in the notes is not drawn.
3. QUESTIONABLE, F3: the notes make no claim of difference from Sawada. The sparse marsh quarter is a nitpick-level first-impression point (contract item 3).

`make review-paired-gate` printed `green` before the verdict, and again when I re-ran it just before recording.

Verdict line printed: `recorded NEEDS-WORK for settlement-review--ashigawa (engine key NONE - no dispatch recorded, gate green)`
