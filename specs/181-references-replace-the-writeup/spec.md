# Feature 181 - the references modal REPLACES the writeup, and its title is the way back

**Status**: FAITHFUL (`spec-fidelity`, round 1 of 5) - cleared for implementation (constitution XVI).
The review graded FR-002/D1 a necessary consequence rather than an addition (the explanation's `close`
event is what drops the shade and the pin, and the one shade is shared by both dialogs) and D3 the
literal reading of *"the word 'Farmhouse' is a link"*. Its aside - that the hiding class must be
cleared on every path that closes the references, including `closeDialog` and a fresh `open()` - is met
by clearing it in the references dialog's own `close` listener, one place. **Round 2** was a narrow
re-check of FR-010/D4, the Principle XIV fix found during implementation (the gate had short-circuited on
this feature's own asset-only delta): FAITHFUL - a real defect, found in this work, fixed at the right
size and disclosed as the one unrequested thing.
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessor**: feature 180 (the references modal lists questions; its button says "Return to <Name> writeup")

## Summary

Two changes to the interactive map's references modal, for every feature's modal alike (the GM:
*"I mean this for all of the references modals, not just the specific one"*).

1. **Opening the references HIDES the explanation** instead of stacking on top of it. Today the two
   dialogs are both open, the references above; when the references modal is smaller than the
   explanation the edges of the one behind show around it - *"it just looks really weird."* The
   explanation reappears when the references modal closes, by any of the ways it closes.
2. **The title becomes "<Name> references"**, with `<Name>` a link that does exactly what the "Return to
   <Name> writeup" button does.

## Functional requirements

- **FR-001** When the references modal opens, the explanation modal MUST disappear from view. When the
  references modal closes - by the "Return to <Name> writeup" button, by the title link (FR-004), or by
  Escape - the explanation modal MUST reappear as it was: same feature, same scroll position not
  required, same content. Nothing is rebuilt; the explanation is hidden and shown.
- **FR-002** While the references modal is open, the map behind keeps the state the explanation gave it:
  the shade stays, and the open feature's highlight stays pinned. Only the explanation's box goes away.
  (Closing the explanation itself - the shade click, its Close button - still closes everything, as today.)
- **FR-003** The references modal's title MUST read *"<Name> references"* - *"Farmhouse references"*,
  *"Bund references"*, and on the title placard the settlement's name - in place of today's
  *"References - <Name>"*. `<Name>` is capitalized as the explanation's own title is.
- **FR-004** `<Name>` in that title MUST be a link, and clicking it MUST do exactly what clicking the
  "Return to <Name> writeup" button does: close the references modal and bring the explanation back.
  One handler, two triggers.
- **FR-005** Escape keeps its meaning: with the references open it closes the references (and so brings
  the explanation back); with only the explanation open it closes the explanation.
- **FR-006** The browser test MUST assert the new behavior in place of the old: today it asserts *"the
  references modal opens ON TOP of the explanation, which stays open"*, which FR-001 reverses. It MUST
  check that the explanation is not displayed while the references are open, that it is displayed again
  after the button, again after the title link, and again after Escape; and that the title reads
  *"<Name> references"* with the name as a link.
- **FR-007** The SVG and the PNG are untouched (feature 134 FR-010). Only `interactive/assets/page.js`,
  `page.css` and the markup `page.py` writes change; no other engine module does (engine in the ROUTE's
  sense, `l7r/**/*.py` outside `ci/` - FR-010's edit to `ci/delta.py` is tooling, which the coverage
  floor measures but the route does not count).

### What this feature does not do

- **FR-008** It does not change what either modal SAYS: the questions, the lead-in, the button's text
  ("Return to <Name> writeup"), the explanation's sections are all as feature 180 left them.
- **FR-009** It does not change hover, highlight, zoom, the place card or the glossary.

### A defect found while doing this (constitution Principle XIV)

- **FR-010** **The interactive page's assets were not engine content, so the gate did not see them
  change.** `make done` on this feature's delta - which was `page.js`, `page.css`, a test and docs -
  answered *"already verified - nothing the gate exercises has changed since the last green run"*, and
  the push route would have been DIRECT, with no gate at all. Both definitions of engine content -
  `scripts/gate-stamp.py`'s diagram area (`*.py`) and `ci/delta.py`'s `_ENGINE_DIRS` (`l7r/` + `.py`) -
  omitted the two assets, which are inlined into every HTML map and executed by the browser test.
  Both MUST include `.js` and `.css` under the skill (only the two assets exist), a test MUST prove the
  two definitions agree on them, and the four documentation sites that state the rule MUST say so.
  **This is the one thing in this feature the GM did not ask for**, fixed here rather than filed because
  it is the exact mechanism that was supposed to verify this feature and did not.

## Decisions Recorded

- **D1 - "disappear" is HIDE, not CLOSE.** The explanation dialog's `close` event is what releases the
  pinned highlight and the shade (`page.js` `dialog.addEventListener("close", ...)`), and the GM asked
  for the explanation to REAPPEAR, which a closed-and-reopened dialog would do only by rebuilding it. So
  the explanation is hidden with a class while the references are open and shown again when they close;
  the map keeps the feature lit and shaded throughout (FR-002), because the reader has not left the
  feature - they have gone one level deeper into it. Rendering decision; nothing physical behind it.
- **D2 - the title link and the button share one handler.** The GM: *"Clicking on that link is the same
  as clicking the return to farmhouse write up button."* Two elements calling the same function is the
  only way "the same" stays true when one of them changes.
- **D3 - the title link is `<a href="#">` styled as a link, and the whole title is not a link.** The GM
  named *"the word 'Farmhouse'"* as the link; the trailing word "references" is plain text.
- **D4 - the assets join the engine key by SUFFIX, not by path.** `("l7r/", (".py", ".js", ".css"))`
  and `("*.py", "*.js", "*.css")` rather than naming `interactive/assets/` - a future asset (a second
  stylesheet, a script split out of `page.js`) is then engine content the day it lands, on the same
  principle as the coverage surface (constitution X clause 5: "if you add a file under `l7r/`, it is
  measured"). Cost: the gate-stamp glob crosses `/`, so a `.js` anywhere under the skill would be hashed;
  today the two assets are the only ones, and the test pins that census so a third is a decision.
  Consequence: every stamp and verified record taken before this fix is keyed on a file set that lacked
  the assets, so the key moves and the next `make done` runs for real - which is the point.
