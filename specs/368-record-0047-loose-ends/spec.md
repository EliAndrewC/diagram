# Feature 368: Loose ends in the privy record (0047), and two of 0006's

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: In progress - spec under review

**Affects**: research record

**Input**: `request.md` (the five items as filed, and the GM's word to take them up, 2026-10-10)

## Why

Feature 328's record checks found five defects outside its scope. Items 1-3 are on the privy question, 0047; items 4 and 5
are on the paddy question, 0006. They wait for a batch of 0006 edits, and this is that batch.

**Item 1, measured** (observed 2026-10-10; method: `measure/privy_reach.py` over the five pool hamlets' recorded
manifests, its output `measure/privy-reach.txt`). The page's table (48, 58, 66 ft) and its 72 ft paragraph come from
August runs (feature 152's acceptance review, 2026-08-29), on an engine that has changed since. At today's 48 ft reach, the
five maps seat 72 privies:
- 22 of them (30.6%) in the sunny-side sector, 112.5 to 202.5 degrees, against the page's "about 46 in 100";
- none nearer another house than its own;
- 9 beyond 45 ft.

## Requirements

- **FR-001 - Item 1, the privy figures.** 0047's drawing page gives today's figures at the current reach, from the script
  and with its method, in place of the August table. The August runs at the `58, 66 and 72 ft` reaches are kept only as dated history
  (feature 152's acceptance review, 2026-08-29), as the reason the reach is `48 ft`. The paragraph, the table and the
  "how often on the sunny side" bullet agree with each other and with today's maps.
- **FR-002 - Item 2, one quotation spelled two ways.** `wang-ochiai-2022-5` reads the paper's own spelling in both
  `.drawing.notes.html` and `.notes.html`, read on the paper (Kyoto repository PDF, p.2242; the archive's copy first).
- **FR-003 - Item 3, "Type V1".** `wang-ochiai-2022-2`'s "Type V1" is glossed from the paper's own definition where it
  stands, or the quotation is cut at its "..." so the label drops out.
- **FR-004 - Item 4, 0006 points to the row village's holdings.** 0006's visible text gains a clause pointing to 0033's
  holdings, so a reader following the farm-holding modal's link to 0006 is not told the holding is ruled out.
- **FR-005 - Item 5, the dry plot's outline.** 0006's drawing page records what the tan-brown stroke round every dry plot
  stands for (a field edge, a path or a balk, read from the code that draws it) and whether it is drawn wider than real,
  so the crop modals can tell it.
- **FR-006 - Its checks.** The record checks the edits owe (`make record-owed`: quote-check for items 2 and 3,
  record-format, entry-drift, and the modal depiction checks item 5 re-owes) are run and answered.
- **FR-007 - The implementation check** (feature 378): `make impl-check F=368` reports nothing missing at close. A claim
  the new figures contradict is recorded DRIFTED and shown in `make claims-report`; the code is not changed.

## Success Criteria

- **SC-001** (FR-001): 0047's drawing page's figures match `measure/privy-reach.txt`, and its paragraph, table and bullet
  agree.
- **SC-002** (FR-002, FR-003): the two copies of the quotation read the same, as the page reads; "Type V1" is glossed or
  cut; quote-check confirms both.
- **SC-003** (FR-004, FR-005): 0006 points to 0033's holdings, and its drawing page says what the dry plot's stroke is.
- **SC-004** (FR-006, FR-007): `make record-owed` is answered and `make impl-check F=368` reports nothing missing.

## Decisions Recorded

- **D1 - Today's maps, not a re-run of August's reaches.** The page draws what the maps draw today, read from their
  recorded manifests. Re-rolling the five maps at the `58, 66 and 72 ft` reaches would change a generator constant for a measurement of
  a reach no map uses. The August figures stay as dated history of why the reach is `48 ft`.
- **D2 - The sector is the engine's** (112.5 to 202.5 degrees in the house's frame, `fixture_seats.py`), so the share
  measures what the code seats.

## The entry, as filed

## What is wrong

1. **The 48 ft paragraph against its table** (`.drawing.html`): "Beyond 48 ft, privies stray out of their own farmsteads"
   is backed by a run at 72 ft, while the table shows only 48, 58 and 66 ft - and its 48 ft row already shows three
   privies standing nearer a neighbor's house. The figures need re-deriving from the sample maps' runs, and the paragraph
   and table brought into agreement.
2. **One quotation spelled two ways**: `wang-ochiai-2022-5` reads "earthfloored" in `.drawing.notes.html` and
   "earth-floored" in `.notes.html`. Read the paper (Kyoto repository PDF, p.2242) and make both copies the page's spelling;
   a quote-check confirms.
3. **"Type V1" undefined** (`.notes.html`, `wang-ochiai-2022-2`): the paper's own name for a farmstead layout type, which a
   reader cannot place. Gloss it from the paper's definition where it stands, or cut the quotation at its "..." so the label
   drops out (a quotation change: quote-check).
4. **0006 never points to the row village's holdings** (added by feature 328 wave 65 - a 0006 loose end, not 0047's): its
   visible text tells every dry plot as the hem and says "No grain plot is drawn beside a house", while the farm-holding
   modal links it for its crops - a reader following that link meets a page that seems to rule the holding out. Add a
   visible clause pointing to 0033's holdings (modal-depiction on farm-holding, 2026-10-09); it re-owes 0006's record checks
   and its nine modals' depiction checks, so it waits for a batch of 0006 edits.
5. **The dry plot's outline is untold** (added by feature 328 wave 65): every dry plot is drawn with a tan-brown stroke,
   the seam between two plots included, and 0006 names only the bare bank between plots and canal; record on 0006's
   drawing page what the stroke stands for (a field edge, a path, a balk) and whether it is drawn wider than real, so the
   crop modals can tell it (modal-depiction on soy, 2026-10-09). Batched with item 4.

## Review history
