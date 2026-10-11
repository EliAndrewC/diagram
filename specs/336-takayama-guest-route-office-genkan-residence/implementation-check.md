# Implementation check - feature 336 (feature 378)

`make impl-check F=336` reports nothing missing: 0104's findings are cited by the checked claims of `_roji_parts`
(`l7r/diagram/compound_parts.py`) and the Mode A procedures (`docs/buildings.md`, `docs/building-programs.md`). This file
records what no claim can reach (plan D3a).

- 0104 (the Ochiba sheet's own route): no code draws it - the sheet is hand-authored SVG
  (`pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg`, its comment at lines 584-585 citing "research 0104,
  Takayama"; `ochiba-magistracy.gen.py` only rasterizes it), and `claims.py` reads no SVG. Its outdoor route - the office's
  rear door, the nakamon, the garden path to the veranda stone - departs from 0104's finding that at an intendant's office
  the record leaves open whether the onward way ran indoors, and places no middle gate against an office hall. Its checked
  counterpart for the generated route is `_roji_parts`'s claim "roji wherever a middle gate stands", DRIFTED (2026-10-11:
  the roji drawn wherever a middle gate and a reception veranda stand, where 0104 records the genkan and the roji as two
  forms a knob should choose). The sheet stays untouched (FR-002, FR-091). Searched: `grep -rn "0104" pool/magistracies/`
  and `make claims-report` for the claims citing 0104.
