# Plan: feature 148 - the interactive map's element count

## Constitution Check

- **VI (verification before done)** - measured on both pages before and after: element count, load, scroll,
  zoom, highlight. The first aim of this feature died to exactly this discipline; the second gets it too.
- **X (100% on pure logic)** - `merge_primitives` is pure string work; every branch the change adds is
  reachable from `tests/interactive/test_page.py` without a browser.
- **XII (record the why)** - a RENDERING decision; the why goes at the point of change and in
  `interactive/CLAUDE.md`, and the counting method behind SC-001 goes in `research.md` R2.
- **XIII (no known regressions)** - the picture is the thing that must not regress, and FR-002 plus
  US2's SVG comparison are how that is proved rather than assumed.
- **XVI (build what was asked)** - the GM named element count as the cause; this pulls that lever and
  reports the four costs rather than promising them.

## The mechanism today

`merge_primitives` turns a run of CONSECUTIVE same-styled `<line>` or `<circle>` into one `<path>`. Two
things limit it:

1. **Consecutive only.** Kuwabata's dike emits path, ellipse, circle per tree - a mean run of 2.4 - so
   2,975 circles carrying three styles collapse to almost nothing.
2. **`<ellipse>` is not matched at all**, and the marsh is 1,656 of them on inashiro.

## The change, and the one thing that makes it hard

Gather same-styled primitives across a class group instead of only where they already sit together. That
is safe for the ink itself - same style, same result, any order - but moving an element backwards past a
DIFFERENT element is only invisible when the two do not overlap. So the merge carries a skipped-extent
test: an element joins an earlier bucket only if nothing it must pass overlaps it.

In practice the emission is regular - a tree draws its trunk, then its shadow, then its foliage - so all
the foliage of one style moves ahead of all the foliage of the next, and the within-tree order that
actually paints the crown is preserved. Trees along a dike do not overlap each other, which is why the
headroom is there at all.

## Sequence

Record the counting method (R2), then the merge, then the tests that prove the picture did not move,
then the measurement, then the report - including the load half, handed back if it has not moved.
