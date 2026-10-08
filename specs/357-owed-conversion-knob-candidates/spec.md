# Feature Specification: OWED AT CONVERSION and knob candidates (feature 280, the modern-only sweep, 2026-09-29)

**Status**: Filed - from future-work/farming-communities.md, "OWED AT CONVERSION and knob candidates (feature 280, the modern-only sweep, 2026-09-29)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

The GM's rule of 2026-09-28: anything attested only in modern times is eliminated. The scripted hamlets were brought into
line in feature 280 (`specs/280-modern-only-sweep/outcomes.md`, one row per item); what is left is open here.

- **Wayside stones: no scripted hamlet draws them yet.** The record (0226, the row retitled "Wayside
  stones"; 520 dates a paired dosojin set at a settlement's entrance to 1695, Ueda) supports stones at a hamlet's
  entrance and at its crossings. Sketch: a placer that seats one to three stones where the connector leaves the web
  and at the busiest crossing, as `farm_fixtures[kind=wayside_stone]` with a class and a caption group.
- **The frozen hamlets' modern-only forms, by map** (never retrofitted - fixed by CONVERSION, `docs/migration-plan.md`):
  Akagahara, Ikegami, Moritono, Tanada, Yatsuda - M34 (the reed edge grounded on a modern survey); Enokida - M54 (the
  110 ft polder cell; three mu is 190 ft), M57 (a sluice per dike pond), M58 (the 0.80 water share; 0.62 at the 23 ft
  inset), M34; Honda - M56 (a pond grid other than the mosaic), M58, M34; Shimizu - M34.
- **The frozen villages' owed forms**: Hoshigaoka - M12 (the pond sized by command area), M65 and M81 (the sanctuary fence),
  M66 (the swept collars), M68 (a hamlet's own burial ground),
  M70 (the roofed pyre ground, platform and hut), M71 (six jizo at a cremation ground alone), M80 (the basin's roof,
  drawn plain, its roof a guess); Kikuta - M56, M58. (M50, M52, M53 and M64 were kept by the GM on 2026-09-29.)
- **M13, the homestead grove**: no pool hamlet draws one; `_find_grove_arms` (the arms-only L) serves the legacy maps
  only. Owed: the grove's premodern size at conversion, or the arms retired with the last legacy map.
- **M38, a knob candidate**: the bare dike-pond bank is attested (turfed or trodden), and so is a bank planted sparse
  with mulberry. Sketch: roll `bank_form` per settlement in `consts.POLDER_FABRIC`, the mulberry rows thinned on the
  second form.
- **M93, a knob candidate**: the communal windbreak is premodern; a ring around the settlement and a belt on the
  windward side alone are both read. Sketch: roll `windbreak_form` (ring / windward) in `SitePlan` and let the belt
  placer take an arc.
