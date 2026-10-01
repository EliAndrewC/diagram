```
UNIT: fix-check--kashikawa   MAP: kashikawa   COMPLAINT: "two ditches run side by side down the paddies, like a doubled line"
THE GM'S QUESTION AT FIT ZOOM: yes, still - two blue ditches still run side by side down the middle of the paddies; it looks exactly as it did on main.
PIXEL COUNT: not applicable (the complaint is about two lines running side by side, not "X inside Y"). Measured instead: drawn_channels[10], from (3209,3648) to (3440,3369), stays 26 ft from drawn_channels[7] for about 340 ft. The 23-26-26-26... spacing is a constant twin.
DID THE FIX FIRE: the snapshot's `channels`, `field_ditches` and `drawn_channels` in the clone are equal to main's. At the twin, the PNG crop (px 1600-2150 x 1950-2450) looks the same before and after. The only manifest keys that differ are tree_crowns, commons, marshes and ink_classes -> NO (error)
RECORDS: "drop_twin_deliveries returns 0 pairs over the comb's plan" -> A PROXY (error). It reads the planned channel list, not the channels that are drawn, and the drawn manifest still has the 7/10 twin.
VERDICT: needs-work
```

1. **Error**: the GM's complaint is still there at fit zoom (norm: fix-check judge 1, the GM's question first). Channel 10 runs beside channel 7 at a constant 26 ft for about 340 ft, and the crop shows the doubled line.
2. **Error**: the fix did not fire in the drawing (norm: judge 3, the class of failure features 150, 155, 156 and 230 each shipped). Every channel record in the manifest is unchanged from main, and the place complained of looks the same in before and after. Either the filter is not on the path that draws the channels, or it never treats the 7/10 pair as a twin. Its "0 pairs" answer suggests one of the two.
3. **Error**: the verify note is a proxy (norm: judge 4). A count over the plan cannot support a claim about what is drawn. The check has to ask `drawn_channels` in the written manifest.
4. **Nitpick** (no norm beyond the complaint): drawn_channels[9] starts 22-26 ft from [5] at (3406,4566), then spreads to 50-90 ft over about 180 ft. Once the fix reaches the drawing, run this pair through the same twin rule.

Gate re-run immediately before the verdict: `green`.

`make review-verdict` printed: `recorded NEEDS-WORK for fix-check--kashikawa (engine key NONE - no dispatch recorded, gate green)`
