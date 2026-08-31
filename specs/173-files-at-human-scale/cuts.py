"""Feature 173's cut tables - one entry per oversize module, read by split_module.py.

Kept beside the mover rather than inside it so the CUTS are reviewable on their own: the cuts are
the only judgment in the split, and everything else is mechanical. Each cut is
(the marquee name that OPENS the submodule, the submodule, the "look here when" line for CLAUDE.md).
"""

PLANS = {
    # ---- hamletgen/ways.py: 4,369 -> eleven ------------------------------------------------------
    # SOURCE ORDER IS NOT DEPENDENCY ORDER here: the two stage entry points stand at the top of the
    # file and every primitive they call stands below them, so contiguous cuts would be all forward
    # edges. The modules below are LAYERS, emitted bottom-up, and `--plan` proves every edge points
    # backwards. Constants place themselves with their first reader (see assign_by_name).
    "l7r/diagram/hamletgen/ways.py": {
        "kind": "names",
        "doc": '"""Split from hamletgen/ways.py by feature 173 - see this package\'s CLAUDE.md for the index."""\n\n',
        "modules": [
            ("geom", [
                "polyline_len", "_plen", "_drop_collinear", "_turn_deg", "_seg_cross", "_aim_off",
                "_components", "_unretrace", "_reach", "_net_reach", "_nearest_seg",
                "_trim_to_service", "push_out_of", "push_clear_of_fabric", "shadowing_lane",
                "fabric_clearance", "_stop_at_network",
            ], "point and segment math on a bare polyline - lengths, turns, crossings, nearest-thing queries, and the two pushes that move a point off something"),
            ("checks", [
                "stream_segs", "drawn_water_segs", "path_violations", "crossing_lands_on_crop",
                "shallow_crossing", "lanes_share_tread", "served_network", "unreached_houses",
            ], "the questions asked ABOUT a finished network - which houses are unreached, which lanes share a tread, where a way crosses crop or water it should not"),
            ("clearance", [
                "clear_runs", "clip_to_clear", "route_around", "existing_walk", "_clear_touch",
                "_clear_link", "_bends_badly", "may_write", "bowtie_cut", "drop_end_nubs",
            ], "may a way BE here - the clear-run scan, the clip, the span and touch tests, the bend/nub judgments, and `may_write`, the guard every rewrite passes"),
            ("route", ["_ease_corner", "_unjog", "_route"], "the router itself: `_route` finds a way round hard ground, `_unjog` straightens what it found, `_ease_corner` rounds the corners it leaves"),
            ("fabric", [
                "_homestead_polys", "_margin_frame", "_crosses_fabric", "_fabric_hits",
                "_hits_a_steading", "_net_segs", "_pass", "_draw_web", "_pull_back_to_service",
            ], "the settlement fabric a way must respect - the homestead polygons, the margin frame, the fabric-collision probes, and `_draw_web`, the single place a web lane is committed to the map"),
            ("sweeps", [
                "_sweep_doubled_remnants", "_sweep_steading_fouls", "_drop_end_nubs",
                "_keep_the_route_wide", "_sweep_debris", "_bridge_collinear_breaks",
                "_join_orphan_ways",
            ], "the passes that REMOVE or REPAIR after the web is laid - doubled remnants, steading fouls, end nubs, necked routes, debris, collinear breaks, orphaned pieces"),
            ("touch", ["_touch_junctions", "_join_piece"], "how a lane end meets the network - the whole junction-touching pass and the piece-joining it falls back on"),
            ("smooth", ["_smooth_web", "web_pieces", "web_rejoinable", "commit_lane"], "the smoothing pass and the connectivity accounting that decides whether a smoothed lane may be committed"),
            ("serve", ["_lay_web_lane", "_serve_stragglers"], "getting a way to a house that has none - laying one web lane, and the straggler search that runs when the ordinary passes left someone unserved"),
            ("web", ["_lay_skeleton", "stage_web"], "STAGE: the lane web - `stage_web` and the skeleton it starts from. Read this first to see the order the passes above run in"),
            ("track", [
                "stage_seat", "_cluster_gateway", "_cluster_edge_toward", "_thread_the_fabric",
                "stage_track", "connector_track",
            ], "STAGE: the track and the seat - the connector out of the frame, the cluster gateway, and the thread through the fabric"),
        ],
    },

    # ---- hamletgen/hinterland.py: 1,100 -> five --------------------------------------------------
    # Same shape as ways.py: stage_hinterland stands first and calls three things defined below it.
    "l7r/diagram/hamletgen/hinterland.py": {
        "kind": "names",
        "doc": '"""Split from hamletgen/hinterland.py by feature 173 - see this package\'s CLAUDE.md for the index."""\n\n',
        "modules": [
            ("frame", ["content_box", "title_pocket"], "the drawn frame's own geometry - the content box and the pocket the title sits in, which both the bamboo seats and the windbreak must keep clear of"),
            ("parcels", ["parcel_bbox_ok", "fit_square_parcel", "_parcel_outline", "_clear_gap", "_near_line", "open_ground_patches"], "open ground: whether a parcel fits, how big a square one can be, its drawn outline, and `open_ground_patches` - the search that places them all"),
            ("bamboo", ["bamboo_blocked", "bamboo_seats"], "where a bamboo thicket may stand and the seats found for it"),
            ("belt", ["belt_polygon"], "the shelter belt's polygon - the one shape the woodland and windbreak stages both draw from"),
            ("stages", ["stage_hinterland", "stage_bamboo", "stage_woodland", "stage_windbreak"], "STAGES: the four entry points the roll calls, in the order it calls them. Read this first to see what the modules above are for"),
        ],
    },

    # ---- hamletgen/homesteads.py: 1,330 -> five --------------------------------------------------
    "l7r/diagram/hamletgen/homesteads.py": {
        "kind": "names",
        "doc": '"""Split from hamletgen/homesteads.py by feature 173 - see this package\'s CLAUDE.md for the index."""\n\n',
        "modules": [
            ("seats", ["front_row", "lane_frontage", "cluster_aspect", "_seat_allowed"], "where a homestead may sit - the front row, the lane frontage that fronts it, the cluster's aspect ratio, and whether a seat is allowed at all"),
            ("bamboo", ["_strip_blocked", "household_bamboo"], "the household bamboo strip: whether a strip is blocked, and the per-household placement"),
            ("fixtures", ["nearer_own_house", "_roll", "farmstead_fixtures", "_trunk_blocked"], "what stands in a farmstead's yard - the privy/well/heap/coop pass, its weighted roll, and the two ownership and trunk probes it leans on"),
            ("wells", ["well_target", "place_wells"], "the public wells - how many a settlement of this size wants, and the pass that seats them"),
            ("stages", ["stage_homesteads", "stage_appurtenances"], "STAGES 5 and 6 - the homesteads themselves and what stands among them. Read this first"),
        ],
    },

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
