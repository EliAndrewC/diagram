"""Feature 173's cut tables - one entry per oversize module, read by split_module.py.

Kept beside the mover rather than inside it so the CUTS are reviewable on their own: the cuts are
the only judgment in the split, and everything else is mechanical. Each cut is
(the marquee name that OPENS the submodule, the submodule, the "look here when" line for CLAUDE.md).
"""

PLANS = {
    # ---- waterfields/seams.py: 1,069 -> three ---------------------------------------------------
    # A chain, not a residue bucket: the pockets are found, then planted or traded away, then the
    # whole thing is driven by close_seams. Cuts follow the chain, so every edge points backwards.
    "l7r/diagram/waterfields/seams.py": {
        "kind": "module",
        "doc": '"""Split from waterfields/seams.py by feature 173 - see this package\'s CLAUDE.md for the index."""\n\n',
        "cuts": [
            ("MIN_PLOT_SIDE", "pockets", "a pocket's geometry: despiking, rings, the water body, the outside-command band, and `_absorb` - the merge of a thin pocket into its neighbors"),
            ("_seam_cuts", "plots", "what becomes of a pocket: `_plant` lays plots in it, `_tab_cut`/`_unjog` straighten their edges, `_trade` hands a corner to the neighbor that can use it"),
            ("close_seams", "close", "the driver - `close_seams`, which runs the pass end to end and is the only name the engine calls"),
        ],
    },
}
