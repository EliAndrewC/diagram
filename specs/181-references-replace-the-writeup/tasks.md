# Tasks - feature 181

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 1). Request: [`request.md`](request.md).

Every task is `research: rendering` - a page convention with nothing physical behind it.

- [x] T01 FR-001/FR-002/FR-005: `page.js` - opening the references hides the explanation (a class, not a close); closing them by any route shows it again; shade and pin kept
      research: rendering
      verify: DONE. `openRefs()` adds class `behind` to the explanation before showing the references; the references dialog's `close` listener removes it, so the button, the title link, Escape, `closeDialog` and a fresh `open()` all bring it back through one place. Shade and pin kept (D1)
- [x] T02 FR-003/FR-004: the title "<Name> references" with `<Name>` a link sharing the button's handler; `page.css` for the hidden state and the link
      research: rendering
      verify: DONE. `#r-name` is built as `<a id="r-back">Farmhouse</a> references`; `#r-back` and `#r-close` call one `returnToWriteup()`; CSS `dialog#explain.behind { display: none }` and the link style
- [x] T03 FR-006: the browser test and the page tests updated
      research: rendering
      verify: DONE. The browser test reads `{refs, explain, visible, shade}` after opening, after the title link, after the button and after Escape (explain stays OPEN but not displayed; the pin stays "bund"); `test_page.py` sees the class rule and both handlers in the page. `make test-file` on the browser file: 19 passed; `make quick` clean
- [x] T04 FR-010: the page assets become engine content for the gate key AND the route (Principle XIV)
      research: rendering
      verify: DONE. `("l7r/", (".py", ".js", ".css"))` and `("*.py", "*.js", "*.css")`, with the measurement recorded at both points of change; `test_delta.py` (both assets engine, a `.txt` beside them not) and `test_measured_surface.py` (the census under the skill is exactly `page.css`, `page.js`, and both definitions see them); `CLAUDE.md` x3 and `docs/session-clones.md` updated. Proved by the gate itself: the previous `make done` on this delta said "already verified"; this one ran in full
- [x] T05 FR-007: regenerate the reference hamlet's page and look; `make done` green; the answer to the GM
      research: rendering
      verify: DONE. Reference page regenerated (17.8 s) and the page carries the class rule and both handlers. `make done` GREEN in 549 s, full run, 100% floors held (2,959 passed, 22,618 statements 0 uncovered, hamlet floor 12,446 / 0). `PAIR_OK` given: no drawn ink, manifest or placement moved - the page's modal behavior and the gate key - and the GM reads the page themselves (2026-08-29 ruling)