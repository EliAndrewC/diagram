# ways - handoff from session 1 (feature 250 T01)

## Changed questions

- SECTION=020 (What vehicle used a village lane, and where could the lane run?) - 19,865 bytes with notes - under the 20,000 cap but only 135 bytes spare, so a note session 2 adds may force a split

## Changed registry keys

- KEY=aze-jawiki - `Used for:` gained "the field path running on the bund at the plot boundary"; no new key

## FR-002 items

- **"It may touch a plot's boundary, since paths hug field margins by design"** (020) - CITATION. The sentence
  is rewritten to what the source says: "It may touch a plot's boundary, since the baulk the path walks on is
  itself heaped up on the boundary between one paddy and the next." New note `aze-jawiki-2` quotes the
  article's opening sentence 「畦（あぜ）は、稲作農業において、水田と水田の境に水田の中の泥土を盛って、水が外に漏れないようにしたものである。」;
  its gloss ties it to the existing `aze-jawiki` note (the aze that serves as a path is the azemichi) and marks
  "may touch a plot's edge" as the page's own rule for the map. A source-reader (sonnet) read the saved page
  and returned READ on the claim; it also offered 「畦の両側の地主が異なる場合、その境界に畦畔を設ける事によって区切られる場合が多い。」
  (the boundary between landholders) as a possible extra quote, not used.
- The stray period after the HTML comment in that sentence was removed (the sentence now ends before the note).

## FR-006 items

- none

## Open

- nothing. `make record`, `make citations` and the four interactive test files are green (257 passed);
  `scripts/check-question-size.py` names nothing.
