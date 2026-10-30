# plan_site, as the logged read found it (feature 444 T19; the round arbiter's ruling on ask:444-T19-plan-site)

Load this file when: you write T19's Rust call into `plan_site` (`l7r/diagram/hamletgen/plan.py`), which the phase-source guard holds.

Recorded 2026-10-30 from one `make phase-read` of `plan.py`, the ruling's Route A: the SitePlan's fields, which `plan_site` rolls,
and where the counts are charged - not its algorithm, which the derivation fixes (`water_frame_greenfield.derivation.md`).

- **The SitePlan** (`class SitePlan`, line ~206) keeps every field name; the port fills the rolled ones from the Rust result.
- **The rolls**: each is `_roll(spec.seed, "<knob>", <choices>)` (line ~336), one independent draw per knob name, unless the spec
  pins the field (`spec.<field> or ...`); `_roll` charges `plan.counted` under `__debug__` (the counted work, 444 T15), and the fall's
  test against the wind is charged at line ~465 (`fall_backs_the_wind`).
- **Rolled in plan_site** (in its order): field_archetype, pond_layout (only for `mulberry_dike_fishpond`, else "grid"), down_deg
  (the falls that back the wind, `fall_backs_the_wind`), settlement_form, cluster_shape, water_sink, lane_skeleton, lane_web, bamboo,
  grove_sides (the flood table on flood ground), grove_flank, row_line ("edge" on flood ground, else rolled), row_sides, row_water,
  row_shelter, well_siting, farm_water, manure_form, copse_siting, kosatsuba_siting, dike_crop, leftover, fry_form, plot_size,
  grain_drift, woodland_patches, fan_aspect, intake, brook_side, head_lead.
- **Not rolled**: windward (the spec's, else `DEFAULT_WINDWARD`, line ~504), harvest_weather (declared, never rolled).
- **Outside water_frame's derivation** (the ruling's point 4: left as they stand, charged where they are, named in the landing
  note): field_archetype and pond_layout (T16's ruling sends the archetype to the field and polder phases), fan_aspect, head_lead
  (the fan's geometry, the field's), dike_crop, leftover and fry_form (the polder's). Which of the rest are the derivation's 20 knobs
  is settled against its Bounds line (the knob names among the reference manifests' `meta` fields at 10 and 20 households) before the
  call is written.
