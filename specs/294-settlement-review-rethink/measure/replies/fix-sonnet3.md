UNIT: fix-check--kashikawa   MAP: kashikawa   COMPLAINT: "two ditches run side by side down the paddies, like a doubled line"
THE GM'S QUESTION AT FIT ZOOM: yes, still. The two parallel channels in the paddy block, running from about (1030,1300) up to (1200,1160) at fit scale, are drawn the same way in main and in the clone. I confirmed this on a full-size crop.
PIXEL COUNT: not applicable. The complaint is not of the form "X inside Y".
DID THE FIX FIRE: NO (error). The SVG diff between main and clone is a render-cache line, one path that loses its first vertex, and a reshuffle of scattered glyphs. The twin channel geometry is unchanged.
RECORDS: `drop_twin_deliveries` returns 0 pairs left over the comb's planned list -> A PROXY (error). It reads the plan, not the drawn channels. The twin that is still drawn was either never in that list or comes from another drawing path.
VERDICT: needs-work

ERRORS / NITPICKS / CONFIRMATIONS:
1. Error. The complaint is still visible at fit zoom. Norm: answer the GM's question first.
2. Error. The fix is claimed but absent from the drawing. Norm: read the drawing, not the intent.
3. Error. The verify note measures the planned list, not the drawn channels. Norm: a record must read the thing complained of.

`make review-verdict` printed: `recorded NEEDS-WORK for fix-check--kashikawa (engine key NONE - no dispatch recorded, gate green)`
