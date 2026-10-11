# Handoff - feature 335, R1 (0104, 0117), session 1 -> session 2

Saved pages: `/tmp/l7r-335r1/sr/<urasenke|adachi|kasama|teien|shiroishi>/` (one source-reader bundle each; all READ,
recorded with `make record-checked CHECK=source-reader Q=0104 NOTES=...`). One new registry key, `urasenke-jutaku`
(source-applicability owed). Jo-an (Uraku-en) is not cited or named: this session did not read it. The
claims sheet row was made with `make research-claim Q="0104 0117" FEATURE=335` (feature 376), not by appending to the sheet.
Corrected on the way, from the source-reader: `adachi-matsue-bukeyashiki`'s "so late Edo" (the source says only within
200 years of 2012) and "kitchen and bath" (it says kitchen or bath).

## Changed questions

- SECTION=0104/how-our-maps-draw-the-formal-entrance-and-a-guests-arrival-genkan - (drawing page) a new bullet "A guest's roji carries no well.": the tea garden's framework is stepping stones and a water basin, no page read puts a well on the roji from a middle gate to a veranda (absence note `roji-well-absence`), a house's well stands by its kitchen or bath (Matsue, Urasenke) and an official's inside the gate before the office (Iwama jin'ya), so plans draw it on the service side or in the front court; four cited notes and one absence note are new.
- SECTION=0117/how-our-maps-draw-doors - (drawing page) the door rule now says a door is set wholly inside its building, its outer edge on the wall it opens through (never outside, straddling or floating), a map drawing convention every plan follows (grounds note `door-flush-grounds`); the opening paragraph and the generated-lodging bullet say the same.

## Owed checks (session 2)

`make record-owed` names them (it lists answered units too; the five source-reader units are answered): quote-check
on 0104's new notes and on 0117's drawing page, translation-check on 0104's new notes, record-format on both drawing
pages, modal-depiction on the sheet modals that point at these drawing pages, source-applicability on `urasenke-jutaku` and on the changed write-ups of `adachi-matsue-bukeyashiki`,
`kasama-iwama-jinya` and `kotobank-teien`.

`make claims-owed` names no claim on 0104 or 0117 (drawing pages only changed). The `Grounds:` comment on 0104's drawing page is unchanged: no engine kind places a well on the roji.
