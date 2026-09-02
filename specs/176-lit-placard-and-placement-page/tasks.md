# Tasks: The Lit Placard Keeps Its Name; the Placement Page Catches Up (feature 176)

Every task is `research: rendering` - a highlight color and a walk-through page are map conventions
with nothing physical behind them, so no task carries the physical checkboxes. The GM's words are in
[`request.md`](request.md).

- [x] T01 FR-001/FR-002: `page.css` - the placard's name keeps `--ink` while its class is lit, a
      rule placed after the gold fill rules so it wins, scoped to `g.f.on.f-place text`, with the
      contrast ratio recorded at the point of change
      research: rendering
      verify: a headless-browser check on the regenerated Inashiro page - the card's rect computes to
      the highlight gold and the name's text to the ink, and a screenshot of the lit card reads

- [x] T02 FR-005: `tests/tools/test_placement_stages.py` - every stage in `STAGES` has a `NOTES`
      entry and every `NOTES` key is a stage; shown RED on the tree before T03
      research: rendering
      verify: fails naming the three unnoted stages before T03, green after

- [x] T03 FR-003/FR-004: the three notes (`stage_waterward`, `stage_pond_stock`, `stage_labels`) and
      the notice board's note reconciled with the label phase that follows it
      research: rendering
      verify: T02 green; the page text names both rules the GM asked for

- [x] T04 D3: the `stage_waterward` docstring no longer says it is called from the hinterland
      research: rendering
      verify: the docstring matches `STAGES`

- [x] T05 FR-006: `make placement-stages` re-plates the page; the committed HTML has no
      "(no note yet)" and eighteen stages
      research: rendering
      verify: grep the committed page

- [x] T06 `make quick`, then `make done` in the background; commit; `sync-with-main.sh done`
      research: rendering
      verify: green gate, feature complete before the push
