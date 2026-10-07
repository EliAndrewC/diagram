# Feature 328 wave 1: findings the claims gate counts as introduced

Load this file when: the push of feature 328's wave 1 is refused by `claims-gate.sh`, or a later wave picks up these rows.

Wave 1 corrected claim lines only (tier E0). Re-checking the units it touched made `impl-drift` read decisions nobody
had checked before - new claim lines, and units whose reason strings or claims changed - and it found these mismatches.
None is a change wave 1 made to what the code does: each is the implementation as it stood, now measured. The gate
calls them introduced (the base index held the unit IN-STEP or had no row). Each is a row of `ranking.json` with
`found: wave 1 re-check` (from `audit/found-wave1.jsonl`), tiered by its implementation work, so a later wave fixes it
in easiest-first order. They land with CLAIMS_OK naming this file, as feature 318's did.

- `buildings/programs.md::Magistrate's manor (county magistracy)#manor kitchen garden by the sun` (DRIFTED, E3): every
  residence keeps a garden, its site and size rolled knobs (0109 drawing); the procedure makes it optional.
- `buildings/programs.md::...#posting wealth knob` (DRIFTED, E1): the poor end's look is a GUESS on 0091's drawing page;
  the procedure calls it historically genuine.
- `buildings/programs.md::...#rear service strip` (DRIFTED, E3): where servants lodge is a two-form knob (gate range,
  rear hut; 0091); the procedure fixes the rear.
- `buildings/programs.md::...#staff housing knob` (DRIFTED, E2): option (c), retainers in town, is attested only at an
  urban magistracy (0114); restrict it to urban tiers.
- `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#mill beside its stream` (DRIFTED, E1): the wheel sits in a mill
  race led off the stream (0064), not in the drain or stream.
- `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#yard, garden and fixtures against the house` (DRIFTED, E2): the wood
  shed stands about 6 ft off a wall (0043), not against the house.
- `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#sluice standoff` (CANNOT-TELL, E1): the sluice is
  30 px from the tap point, perhaps about 57 ft beyond the rim where 0146 says about 90 ft; measure and set it.

The other findings the wave's re-checks surfaced in the same units were findings already (the gate lists them as
pre-existing), or were fixed within the wave (three rounds of claim corrections), or are recorded in `ranking.json` as
moved rows (`audit/overrides.json`: the rank step, the merchant kura size, the universal shrine) or found rows.
