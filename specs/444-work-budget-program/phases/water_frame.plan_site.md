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

## The derivation's 20 knobs against plan_site's rolls (measured 2026-10-30, one-shot: the knob registry's names, `Knob("<name>"` under `l7r/diagram`, and plan_site's `_roll` names, each against `pool/hamlets/inashiro/inashiro.json`'s `meta`, Inashiro being the reference spec at 15 households)

- plan_site rolls 30 fields; 27 are `meta` keys; less the fall (a bearing) and the five the ruling sets outside (field_archetype,
  pond_layout, dike_crop, leftover, fry_form), 21: settlement_form, cluster_shape, water_sink, lane_skeleton, lane_web, bamboo,
  grove_sides, grove_flank, row_line, row_sides, row_water, row_shelter, well_siting, farm_water, manure_form, copse_siting,
  kosatsuba_siting, plot_size, grain_drift, intake, brook_side.
- The registry's knob names in that `meta`: 19 - bamboo, byre_form, cluster_shape, family_form, fan_middle, field_archetype,
  footbridge_form, grain_drift, kosatsuba_seat, lane_skeleton, lane_web, paddy_rest, plot_regularity, plot_size, settlement_form,
  town_nearness, weir_form, windbreak_belt, winter_crop (the derivation's 20 at 10 and 20 households is this list's reading).
- Only 8 are in both: bamboo, cluster_shape, grain_drift, lane_skeleton, lane_web, plot_size, settlement_form, field_archetype.
