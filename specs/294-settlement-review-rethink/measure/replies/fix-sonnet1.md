UNIT: fix-check--kashikawa   MAP: kashikawa   COMPLAINT: "two ditches run side by side down the paddies, like a doubled line"
THE GM'S QUESTION AT FIT ZOOM: yes, still. In the clone PNG, two blue ditches run side by side about 12 px apart in the 2600 px image, from about (1700,2330) to (2180,2050), with a short stub joining them at the lower end. The crop is identical in main and clone.
PIXEL COUNT: not applicable. The complaint is a doubled line, not "X inside Y".
DID THE FIX FIRE: NO (error). The `channels` list in `kashikawa.json` is identical in main and clone. The drawn twin is not in that list, so `drop_twin_deliveries` filtered a list that never held it.
RECORDS: the tasks.md verify note ("0 pairs left") -> A PROXY (error). It counts pairs in the planned channel list, not the ditches drawn in the SVG and PNG.
VERDICT: needs-work
ERRORS / NITPICKS / CONFIRMATIONS:
1. Error (gm-fix contract, item 1): the doubled ditch is still visible at fit zoom.
2. Error (contract, item 3): the fix did not change the drawing. The `channels` list is identical in main and clone, so the filter was applied to the wrong list.
3. Error (contract, item 4): the "0 pairs left" record reads the plan, not the drawn ditches.
4. Nitpick (no norm): the clone PNG differs from main elsewhere. The east marsh-edge ditch gets a cream strip beside it, and the scatter changes. Neither is the fix, and the fix doesn't explain either.

`make review-paired-gate` printed `green` before the verdict, and again just before I recorded it.

Verdict line printed: `recorded NEEDS-WORK for fix-check--kashikawa (engine key NONE - no dispatch recorded, gate green)`
