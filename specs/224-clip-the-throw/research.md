# Research - 224 clip the throw, the glossary scan, and the drop's last pass

## R1 - the before (from specs/223 research R2 and this feature's own measurements, 2026-09-11)

After feature 223, seconds per pool hamlet (inashiro / kashikawa / kuwabata / mizuguchi / sawada): regen 9.7 /
12.1 / 10.3 / 8.4 / 14.3; `stage_hinterland` 1.3 / 1.8 / 1.4 / 1.1 / 1.8; `flush_blade_groups` 0.17 / 0.21 /
0.16 / 0.14 / 0.23; `drop_offmap` 0.22 / 0.21 / 0.15 / 0.20 / 0.20; the explanations step 0.35 / 0.32 / 0.38 /
0.32 / 0.30. The commons scatter under cProfile (2026-09-10, Kuwabata): `commons` 3.15 s profiled, `_sparse`
143,604 calls at 1.7 s profiled, `random.uniform` 1.0 million calls; Inashiro's SVG held 259,978 blade subpaths
before 223's cull and 49,465 after it - the ~80% culled were thrown, keep-out-tested and drawn for nothing.

The explanations step, profiled on Inashiro's manifest: `explanations` 0.005 s, `place_card` 0.001 s,
`json.dumps` 0.000 s, `glossary_for` 0.333 s - 729 `re.search` calls (0.276 s in the pattern searches, 0.053 s
compiling them) over the joined explanations text, for 44 glossary terms present of the vocabulary's.

The frame against the content: on the five pool maps the view reaches 19-194 px past the bounding box of the
houses, the fields and the pond (`title_band` None, no outside title pocket on any) - the dry hem, the
farm-yard rects and the crop's 48 px margin account for it; the prediction of FR-001 reads the crop's own
boxes, so its overhang is what R2 measures.

## R2 - the after

(filled at T04)
