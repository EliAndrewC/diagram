# T08 - four claims findings on `_OVERLAP_EXEMPT`, re-opened by one added key (2026-10-18)

T08 added one key (`pond_bank_trees`) to `overlap/taxonomy.py`'s `_OVERLAP_EXEMPT` dict and its not-geometry set; the dict's
19 claims were re-opened as "code changed" (the unit is the whole dict) and judged in T08's impl-drift round 1. Four came back
DRIFTED, none on the key T08 added:

1. `_OVERLAP_EXEMPT#built on what it serves` - the log_booms entry exempts a floating log boom; 0210 draws moored raft-mats, no
   boom (328's ranking row `settlement/city/waterfront.py::WaterfrontMixin.log_boom#boom pen against the bank` is open on it).
2. `_OVERLAP_EXEMPT#inspection post on the gate` - lets the post overlap the gate furniture; 0147: the buildings at a gate never
   overlap, each about 36 ft clear. Town tier.
3. `_OVERLAP_EXEMPT#merchant storehouses` - kura abutting the shop; 0155 stands them behind the main house. Town tier.
4. `_OVERLAP_EXEMPT#yard, garden and fixtures against the house` - the claim says the wood shed stands about 9.5 ft off a wall;
   0043 says about 6 ft (a ken). 328's ranking row `fixture_seats.py::WOODSHED_STEP_FT#wood shed off its wall` is open on it.

The pool rolls clean on T08's build and the cohort holds 54/54.
