# The GM's request, verbatim

2026-09-07, session "Diagram tooling". The first message asked for an analysis:

> The HTML page for the hamlet of Kuwabata seems a lot more noticeably sluggish than the HTML page for Inashiro.  This leads me to believe there's probably some efficiency improvements we could make, e.g. in the past this has been because of things like doing overlap testing or mouseover checks on every indvidual feature instead of drawing bounding boxes and doing a much cheaper check on those.  For example, a previous feature replaced "see if the mouse has hovered over literally any individual glyph in the scrubland" with "is the mouse over the shape of the outline of the scrublan" which is computationally much more efficient.  Please analyze Kuwabata and see if any similar performance improvements can be made.

The session's analysis (measured in headless Chromium; the numbers are in `research.md`) found one
cause - the page paints the scrub scatter as three `<path>` elements of 61,000 to 87,000 subpaths, and
every hover-driven repaint replays the whole path for every screen tile - and one fix, splitting each
merged scatter path by spatial cell so Chromium can cull whole paths by bounding box. It reported
this and offered: *"Say the word and I'll run the feature end to end: claim the number, spec, review,
implement the tiling in the merge, extend the browser test with the pointer-move timing so the
regression is gated, and push."* The GM's second message:

> Yes please run that feature end to end, thanks.
