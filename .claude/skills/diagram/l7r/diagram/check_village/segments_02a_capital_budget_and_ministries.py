"""Gate segments (capital budget and ministries; keys 0097-0106_026) - bodies verbatim, registry order preserved."""


# WELLS, TROUGHS, AND HITCHING POSTS NEVER OVERLAP ONE ANOTHER (GM 2026-07-25). The motivating
# defect was Nagahara's flophouse yard: a hitching rail drawn straight ACROSS a wellhead, with
# the trough cluster stacked on both - three glyphs on one spot, where a reader can no longer
# tell which is which, and the layout it implies is nonsense (nobody draws water through a rail,
# and no yard ties its animals over its own draw-point). They collide because they are placed at
# three different moments - the wells long before the yard exists, the rails when it draws, the
# cluster after - so nothing had ever measured the pair. This check is deliberately GEOMETRIC
# and glyph-level: it demands only that the DRAWN extents not intersect, not any working
# clearance, because the troughs are SUPPOSED to hug their well (the bucket-pour relay,
# stable_troughs_beside_well) and animals are supposed to stand between rail and trough. Near is
# right; on top of is not. Extents come from the shared quad builders in settlement.py, the same
# ones s._stable_yard places against (with YARD_GLYPH_SLACK of margin), so placement and check
# can never drift apart. Every pair on the map is tested, ACROSS yards as well as within one -
# the cross-yard hole is what the dung-heap rule had to be widened for twice.


# WALL TOWER COVERAGE by the city's DEFENSE POSTURE (GM 2026-07-22): the interlocking-flanking-fire rule
# (侧射; Shen Kuo's 11th-c. 矢石相及 - adjacent mamian's fields of fire overlap so an attacker at the base
# is hit from >=2 towers). TUNABLE per city (meta wall_defense): `siege` = aimed-lethal bowshot (60 m /
# 197 ft), >=2 towers everywhere; `garrison` = full war-bow reach (100 m / 328 ft), >=2; `peaceful` = the
# sparser Xi'an spacing, >=1 flanking tower within aimed-lethal range everywhere (midpoints get 2). Every
# point on the wall CURTAIN must have >= the tier's min-count of towers within the tier's arrow range;
# the gate OPENING itself is exempt (a defended chokepoint with its own gate tower + guard, not open
# curtain). Both mural and gate towers count. See settlements.md 'Historical grounding'.


# THE CAPITAL TIER IS SIZED BUDGET-FIRST TOO (feature 018, specs/018-capital-space-budget).
# The sibling of city_wall_matches_budget above, at the SAME tolerances - inherited
# deliberately rather than re-derived, because they are pinned by the shipped-Tango /
# rejected-Nagahara pair and nothing about a capital argues for different slack.


# THE RATCHET (FR-015). A rule gated on an optional declaration is optional in practice:
# three separate times in this engine's history a check silently never RAN while the gate
# stayed green, because the map declared nothing. So a capital that declares no budget
# FAILS here rather than skipping its conformance check. Model: settlement_declares_a_land_fall.


# ---- feature 020: the ground-reserving layer ------------------------------------------
# THE GOVERNMENT WARD. Both anchor traditions put the domain ministries OUTSIDE the
# castle, flanking the ceremonial approach: Beijing's Six Ministries lined the Corridor of
# a Thousand Steps outside Chengtianmen, and a jokamachi's offices spilled out of the
# ninomaru into the town as they grew. So a capital shows its six ministries fronting the
# ote-suji - the avenue from the castle's front gate to the through-road - with the House
# Chancellery and the domain school on the same axis (settlements/capitals.md, "The
# government ward"; the research trail is research/cities/capitals.md).


# NO House Chancellery compound: the council of lineage representatives meets IN the
# castle (GM 2026-08-09, researched: Edo's Hyojosho and the Roju council sat within Edo
# castle, and China's Grand Secretariat sat inside the palace - the split both anchors
# agree on is EXECUTIVE ministries out, the ruler's COUNCIL in). A chancellery compound
# outside is therefore a defect, not a requirement; the council chamber is part of the
# castle's implied goten. research/cities/capitals.md, "The chancellery meets IN the castle".


# The approach avenue: the way that leaves the castle's front gate. Membership questions
# below are judged center-to-line with tolerances that dwarf the footprints - the
# ASSOCIATION/reach family (CLAUDE.md, "Centers, footprints, and aggregates").


# A government office stands in its own ground - the provincial rule restated at this
# tier, because the scale=="city" block does not run here and a capital has no governor's
# yamen. Same 14px standoff, same funerary exclusion (a clan crypt against a bureau is a
# real adjacency), same registry-driven victim list.


# THE LINEAGE COMPOUNDS are what make a capital read as a SPECIFIC domain's seat: named
# walled yashiki whose size tracks how many of each lineage actually LIVE here - never the
# rank of its head (the kurogi rule: a full chancellor on a visibly smaller plot because
# his people are out in his province). The ruling lineage gets NO compound - its seat IS
# the castle. settlements/capitals.md, "Shiro Daika's lineage compounds".


# The FR-015 ratchet again: without the declaration every lineage check below SKIPS while
# showing green, so the missing declaration is itself the failure.

# `wells_troughs_rails_clear_of_each_other` RETIRED WITH ITS WHOLE DERIVATION (feature 141's cut; the
# residue removed here in 146). It built a quad for every wellhead, trough cluster and hitching rail on
# the map and ran a pairwise separating-axis test over the lot, failing when two drawn extents
# intersected: the three stand SIDE BY SIDE at a watering point (the troughs hug their well, the animals
# stand between rail and trough), and stacked they read as one unidentifiable smear that also implies a
# yard tying its stock across its own draw-point. Feature 141 cut it as a check that re-measures what the
# placer guarantees - `_stable_yard`'s `_glyph_free` seats those three against each other and cannot
# return an overlapping trio - and this feature removes the six segments (97-102) that went on deriving
# the quads and running the O(n^2) comparison on every gate with nothing reading the result.
