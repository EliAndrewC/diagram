# Tasks - feature 187

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 2). Request: [`request.md`](request.md).

This file landed EMPTY in commits `42f810ae` and `795030ff`: the line that recorded the verdict wrote it as
`open(q, "w").write(open(q).read().replace(...))`, which truncates the file before the read that was meant
to feed it. Restored from the session's own draft; history is not rewritten.

- [x] T01 FR-001: `render_cache.engine_fingerprint()` takes `.js` and `.css` beside `.py`, with the why at the point of change (gencache untouched - D3)
      research: rendering
      verify: DONE. `is_asset = name.endswith((".js", ".css"))` beside the `.py` filter, under the same directory prunes, with the GM's question and the 186 incident at the point of change; gencache untouched (D3)
- [x] T02 FR-003: test - an asset edit moves the fingerprint; a tests/ or pool edit does not
      research: rendering
      verify: DONE. `test_engine_fingerprint_moves_on_a_page_asset`: a css edit moves it, a js edit moves it again, a `.css` under tests/ or a `.js` under wip/ does not. `make quick` clean
- [x] T03 FR-004: `make done` green; push; confirm render-sync regenerated Inashiro and its page carries `text-decoration: none`
      research: rendering
      verify: DONE. `make done` GREEN in 275 s: 2,976 passed, 22,622 statements 0 uncovered 100%, hamlet floor 100%. Pushed at 18:07; render-sync regenerated all 10 live maps (the fingerprint's file set changed) and the mirror's `inashiro.html` was rewritten at 18:07:13 with 0 `underline dotted` rules and 3 `text-decoration: none` - checked on the file, not inferred
