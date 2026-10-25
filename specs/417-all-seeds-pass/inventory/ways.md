# Inventory - ways (Explore agent on sonnet, 2026-10-25, plan D10; its reply verbatim)

Inventory of `hamletgen/ways/`, `settle/` and `web/`, read directly from the code. All paths below are relative to `/diagram/.clones/diagram-backlog/l7r/diagram/hamletgen/ways/`.

**Scope notes**
- I read every file that repairs, drops, refuses or judges a lane in full. I skimmed `cluster_edge.py`, `dry_exit.py`, `tree_base.py` and `web_counts.py` for decision points only. `checks.py`, `law_water.py`, `arcs.py` and `__init__.py` were read in parts or by grep. No file was left unexamined for the searches above.
- `law.violations` (`law.py:990`) is never called inside `ways/` or elsewhere in `hamletgen` outside `law.py`. The generator reaches the same registry through `keeper.unsettled`, which iterates `law.LAW` (`keeper.py:66`), and through `knots.WebMemo.count` (`law.LAW[name]`, `knots.py:628`).
- `driver.py:277` only catches `WebRefused` and re-raises it with the manifest attached.
- Class P1 is the leftover: a rule with no up-front predicate, which only a later pass catches. Where I list a function under another class and P1 also applies, I say so in the sentence.

## web/stage.py (the order the passes run, `stage_web` 52-410)

- `web/stage.py:stage_web (52)` | P2 | Runs about 25 post-lay repair passes in sequence after `lay_reachable_runs` (245), then hands the finished web to `settle_the_web` (406). Several passes are called twice or three times: `_join_orphan_ways` 258/277, `_bridge_collinear_breaks` 261/275/331, `_touch_junctions` 263/305/309, `_sweep_debris` 312/335, `_sweep_steading_fouls` 318/332, `_sweep_doubled_remnants` 330/333/376, `_sweep_dangling_ends` 334/348, `tidy_lane_ends` 295/370. The comments say why: "A repair pass that runs before the things it repairs is not a repair pass."
- `web/stage.py:stage_web (250)` | P2 | `s.trim_lane_stubs()` is an engine method outside `ways/`; it removes lanes after laying.
- `web/stage.py:stage_web (364)` | P2 | `s.drop_lanes([... len(pts) < 2 or polyline_len(...) < 1.0])` drops husks left by the joins.
- `web/stage.py:stage_web (406)` | P3 | `s.M["meta"]["web_settle"] = {...settle_the_web(s)...}` runs the whole-web settle inside the generator.
- `web/stage.py:resettle_straightened (488)` | P2 | `if straighten_joints(...): ... settle_the_web(s)` re-runs the whole settle after a joint rewrite.
- `web/stage.py:stage_web (396)` | P1 | `a_way_onto_the_bund(s)` runs after the lanes are laid so the paddy is reached at all.
- KEPT: `web/stage.py:lay_reachable_runs (419)` / `_reachable_runs (425)` — one network: a candidate run is drawn only if it comes within `_LANE_JOIN_FT` of the skeleton or an already admitted run. "Decide connectivity before any ink goes down."
- KEPT: `web/stage.py:stage_web (239)` — `clear_runs(line, hard, WEB_HARD_GAP, ..., tight=walls, tight_margin=WEB_FABRIC_GAP)` clips candidates to clear ground before they are drawn.

## settle/stage.py (`STEPS`, 52-69)

`STEPS = settle_husks, square_every_crossing, settle_shapes, settle_way_outs, settle_ends, settle_street_ends, settle_shadows, settle_joins, settle_needles, settle_reach, settle_defer, settle_network, settle_fragments, prune_the_tree, settle_knots, settle_widths, settle_husks`. Each is listed in its own file section below.

- `settle/stage.py:settle_the_web (73)` | P3 | `settled = not n` loops up to `SETTLE_ROUNDS` (8) over `sum(step(s) for step in STEPS)`. It then asks `if not settled or unsettled(s.M, memo_ground(...)): dropped = last_resort(s)` (92-93).
- `settle/stage.py:settle_the_web (96)` | P4 | `refuse_unreached(s.M)` raises `WebRefused` for an unreached house or field.
- `settle/stage.py:settle_reach (25)` | P3 | `if not (unreached_houses(s.M) or law.unreached_targets(s.M) or law.field_unreached(s.M)): return drawn`. It asks the finished-map checks to decide whether to draw more tree lanes.
- `settle/stage.py:settle_husks (41)` | P2 | `law.husks(s.M)` then `s.drop_lanes(gone)`.

## last_resort.py and keeper.py

- `last_resort.py:last_resort (150)` | P4 and P3 | Rounds ran out, so `while bad := lane_violators(s): s.drop_lanes(bad)`. It drops ordinary lanes whole, then re-runs 11 repair steps (164-177), then `s.drop_lanes(carriers)` (181).
- `last_resort.py:lane_violators (137)` | P3 | Whole-web check: ordinary lanes `lanes_breaking(s)` names.
- `last_resort.py:lane_breaches (60)` | P3 | Asks every per-lane rule (hooks, bends, crossing, fabric, connector_hairpins, needle_joins, folded_joints, doubled_tails, dangling_ends, doorstep_ends, needle_loops, way_outs, tree_faults) of the finished web.
- `last_resort.py:refuse_unmended (200)` | P4 | `raise WebRefused("the web's last resort cannot mend it without dropping a tree lane: ...")`. It asks `lane_breaches(s, every=True)`, `law.way_out_carriers` and `unsettled(...)`.
- `last_resort.py:refuse_unreached (225)` | P4 | `raise WebRefused("the settled web leaves unreached what the seating reserved a way for: ...")` on `unreached_houses(M)` or `law.field_unreached(M)`.
- `last_resort.py:ordinary_carriers (144)` | P3 | Whole-web `law.way_out_carriers`, used to decide which lanes to drop.
- `keeper.py:unsettled (58)` | P3 | `{name: v for name, rule in rules.items() if name not in NOT_THE_SETTLES and (v := rule(M))}` — the whole `law.LAW` asked of the web at the settle's exit and by the last resort. `NOT_THE_SETTLES` skips the decks, planks, unreached houses/field/targets.

## settle/shapes.py

- `settle/shapes.py:settle_shapes (204)` | P2 | Cuts what breaks the lane's own shape or crossings: `law.hook_faults` → `reaimed`, `law.kink_faults` → `_unkinked`, `_crossing_fault`, `fouled_segment` → `edits[i] = [q for q in (p[:k+1], p[k+1:]) ...]`. One fault per lane per round.
- `settle/shapes.py:_crossing_fault (137)` | P2 | Cuts a brook crossed twice, off a ford, off square, or where no deck seats. It tries squaring first and cuts only if that fails.
- `settle/shapes.py:_unkinked (188)` | P2 | Drops the shorter arm of a doubled-back run or the two turns of a zigzag.
- `settle/shapes.py:settle_way_outs (253)` | P2 and P3 | Cuts the crossing out of the ordinary lane carrying a way out; if only tree lanes carry it, `s.drop_lanes([carriers[0][0]])`. A tree lane is dropped whole here.
- `settle/shapes.py:reaimed (334)` | P2 | Re-lays an end as a T, or `return seq[:-1]` (drops the last leg) when no vertex works.
- `settle/shapes.py:apply_pieces (50)` | P2 | The shared writer: `if not keep: drops.append(i)`, else cuts and splits lanes via `reshape_lane`.
- KEPT: `settle/shapes.py:fouled_segment (99)` — `house_hit`, `_crosses_fabric(near, gap)`, `law.breaks_through`, `law.over_a_fixture`, `forbidden_segment`. It is the one foul predicate, asked both as a cut and as a candidate test (`Lawful.ground_fault`).

## settle/ends.py

- `settle/ends.py:settle_ends (36)` | P2 | Repairs ends from finished-web checks: `law.shallow_crossing_at`, `connector_hairpin_ends`, `needle_ends`, `folded_joint_pairs`, `doubled_tails`, `fronting_ends`. Each is cut or re-aimed, one fix per meeting per round (`claim`).
- `settle/ends.py:settle_dangling (141)` | P2 and P3 | `bad = {... law.dangling_lane_ends(M, ground)}`, trims to service, and `edits[i] = []` ("one its trim cannot mend goes whole") — a P4 drop.
- `settle/ends.py:settle_shadows (166)` | P2 | `shadowed_by` → `apply_pieces(s, {k: []})` drops the shorter ordinary lane when `keeps_the_network` or `left_to_the_tree` or `strands_only_ordinary` allows.
- `settle/ends.py:drop_stranding (186)` | P2 and P3 | Drops lane `k` plus `settle_network`, then re-asks `law.field_unreached` and redraws the field path with `a_way_onto_the_bund`.
- `settle/ends.py:settle_street_ends (201)` | P2 | Cuts a row street's dangling end (`law.dangling_lane_ends`) to its last joint (`end_to_its_joint`).
- `settle/ends.py:settle_joins (242)` | P2 | Carries a free end onto its way (`law.near_misses`). If the join breaks a rule against a tree lane (`tree_faults(with_edits(...))`) or the matrix refuses it, the end is taken back: `sub_run(seq, 0.0, polyline_len(seq) - law.JOIN_REACH_FT - JOIN_BACK_PAD_FT)`. This relaxes a join by dropping it.
- `settle/ends.py:settle_needles (290)` | P2 | `law.needle_loops(M)` → cut the shortest ordinary lane on the needle where `keeps_the_network`, else `weld_corner`. A needle no cut opens "waits for the next round".
- `settle/ends.py:settle_fragments (355)` | P2 | `law.short_fragments(...)[:1]` → `s.drop_lanes(gone)`.
- `settle/ends.py:settle_widths (386)` | P2 | Re-widths lanes to rank, and to the chain's widest member, narrowing where `fouled_segment` is hit.
- `settle/ends.py:settle_network (428)` | P2 and P4 | `gone = [... labels[n] not in roots]; s.drop_lanes(gone)`.
- `settle/ends.py:keeps_the_network (329)` | P3 | Whole-web `law.lane_networks` and `unreached_houses` on a trial manifest. Candidate-shaped, but each call counts over the whole trial web.
- `settle/ends.py:with_edits (318)` | supports P3 | Builds the trial web `settle_joins` hands to `tree_faults`.
- `settle/ends.py:connector_component (347)` | P3 | Whole-web component at `law.JOIN_TOL`.

## settle/lawful.py

- KEPT: `Lawful.ground_fault (115)` / `Lawful.fault (163)` / `Lawful.__call__` / `corridor_on_lawful_ground (198)` — "the ONE question the web asks before it adds a tree lane." It asks hook, kink, crossing fault, foul, off open ground, through a building, needle, fold, connector hairpin, dangling end, doubled tail and (tree) way-out-over-and-back. The seating also asks `corridor_on_lawful_ground` before it admits a house.

## tree.py, reach.py, corridors.py

- KEPT: `tree.py:admits (188)` — the one predicate the seating asks of every corridor, with the full `Lawful`, `needle_loops`, `DOORSTEP_MAX`, `way_out_once`, `tree_shadows` and `walked_shadows` over the whole tree.
- KEPT: `reach.py:settle_targets (39)` and `settle_field (60)` — `next(r for r in spur_runs(...) if lawful(r, ACCESS_WIDTH))` and `fault(q := square(r), BRANCH_WIDTH)` before `_draw_tree_lane`. When none passes: P4, `M["meta"]["field_refusals"] = turned; return 0` (the target or field is left unreached and refused later).
- `tree.py:settle_tree (433)` | P2 | Draws what `owed` says, then `return n + settle_defer(s)`.
- `tree.py:tree_faults (466)` | P3 | Whole-web scan (`needle_ends`, `doubled_tails`, `tree_shadow_cuts`, `needle_loops`, `fronting_ends`) naming ordinary lanes to cut.
- `tree.py:settle_defer (637)` | P2 | Cuts `DEFER_GAP_FT` (30 ft) each side of the fault point. If `strands_the_reach(s.M, i, gap)`, it falls back to `cut_alongside`.
- `tree.py:strands_the_reach (582)` | P3 | `field_unreached(then) > field_unreached(now) or len(unreached_houses(then)) > ...`.
- `tree.py:cut_alongside (596)` | P2 | Trial of whole-web counts (`knots`, `tree_faults`, `lane_networks`, `field_unreached`, `unreached_houses`) before accepting the cut.
- `tree.py:prune_the_tree (669)` | P2 and P3 | Drops the longest tree lane whose removal leaves `unreached_houses`, `lane_networks`, `unreached_targets`, `field_unreached` and `end_faults` no worse.
- `tree.py:left_to_the_tree (383)` | P3 | Whole-web `lane_networks` and `unreached_houses` on a trial.
- `corridors.py:strands_only_ordinary (82)` | P3 | `len(unreached_houses(trial)) <= len(unreached_houses(M))`.

## serve.py

- KEPT: `serve.py:_lay_web_lane (133)` — `if _near > 0.6 * len(run) or _worst_ft > BUNDLE_PITCH: return False` (shadow), the belt test (inside > 60 ft refused), and the join. A run whose join is not walkable: `return False`, "the run is not drawn" (P4).
- KEPT: `serve.py:lay_door_paths (443)` and `door_path (634)` — `Lawful(s, tree=True)`, `over_a_fixture`, `forbidden_segment`, `closes_a_needle(...)`, `_crosses_fabric(path, walls/bands)`, all before `_draw_web`. When `door_path` returns None the farm gets no path: P4 (`continue`).
- KEPT: `serve.py:closes_a_needle (625)` — `len(needle_loops({... path})) > len(needle_loops({...}))`, a whole-web predicate asked of a candidate.
- `serve.py:shadowed_by (62)` / `runs_beside (75)` / `shadow_measure (39)` | P3 and TWICE | See the TWICE section.
- `serve.py:street_arrives (531)` / `street_anchors (547)` | P1 | Rule "does a way already arrive at this farm" is answered per farm before a path is laid; the street trim reuses it.

## sweeps.py (post-lay removal and repair)

- `sweeps.py:_bridge_collinear_breaks (92)` | P2 | Lays missing lane to close a break. It routes with `_route`, then `if not span or polyline_len(span) > _PATH_DIRECTNESS * max(gap, 1.0): continue  # ...the interruption is honest`. It also skips when `existing_walk <= _BRIDGE_DETOUR * gap` and when `_draw_web` refuses (P4).
- `sweeps.py:_join_orphan_ways (248)` | P2 | Links orphan components. Per round it takes the nearest 40 candidates (`cands[:40]`), refuses an even brook-crossing count, and `if link is None or best is None: return made` (P4, gives up).
- `sweeps.py:_sweep_doubled_remnants (429)` | P2 | `shadowing_lane(...) is None and shadow_share(...) < _DOUBLED_SHARE: continue`, refused if it strands a house (`_reach > WEB_REACH_FT`) or raises `_components`; else `ln["pts"] = []; s.drop_lanes(gone)`.
- `sweeps.py:_sweep_steading_fouls (504)` | P2 | `while len(pts) >= 2 and _hits_a_steading(s, pts[-2:], width): pts.pop()`, empties the lane if the foul is mid-run.
- `sweeps.py:_drop_end_nubs (551)` | P2 | `drop_end_nubs(ways)` then `may_write(...)` and `s.reshape_lane` refuse it if worse.
- `sweeps.py:_keep_the_route_wide (594)` | P2 | Joins two cart-width ends within `_LANE_JOIN_FT` (25 ft) of each other that meet only through a footpath.
- `sweeps.py:_sweep_dangling_ends (662)` / `_walk_in (779)` / `carry_to_dooryard (834)` | P2 | Walks a non-serving end in 4 ft at a time; `pts = []` if under `_WEB_MIN_FT` and not held; restored whole and carried to a dooryard if a house would lose its way.
- `sweeps.py:_sweep_debris (860)` | P2 | Drops a lone fragment under `_WEB_MIN_FT` unless a house it serves has no other way (`_near(h, mine) <= _SERVE_FT < _near(h, others)`).
- `sweeps.py:trim_free_stub (357)` | P2 | Removes a hook at a free end (last leg ≤ `_FREE_STUB_FT`, turn ≥ `_HOOK_DEG`).
- `sweeps.py:cut_past_connector (396)` | P2 | Cuts a loose tail < `_PAST_CONNECTOR_FT` (40) past a crossing of the connector.
- `sweeps.py:on_the_way (385)` / `held_at (825)` / `brook_crossings (239)` | support | Helpers for the repairs above.

## tails.py

- `tails.py:_sweep_doubled_tails (163)` | P2 | `k = along_tail(pts, op)` with the default `deg=_ALONG_DEG` (25) → `cut_at_tail`, then `cut_keeps_network` or `s.admits` can refuse.
- `tails.py:cut_keeps_network (115)` | P3 | `pieces(after) <= pieces(before)` over the lanes.
- `tails.py:reseat_on_way (139)` | P2 | Carries a stranded lane's end onto the way within `_RESEAT_FT`.
- `tails.py:along_tail (40)` / `tail_doubled (71)` / `cut_at_tail (79)` | shared | `tail_doubled` is the pair test of `law.doubled_tails` (at `_DOUBLED_DEG` = 15). See TWICE.

## touch.py

- `touch.py:_touch_junctions (110)` | P2 | Extends every near end to touch the way. Per move it asks `_may_write`. The `final` branch also cuts overruns < 40 ft ("`if (math.dist(...) <= _TOUCH_GAP and polyline_len(...) < 40.0)`"). Ends over `reach` or links over `_LINK_DIRECTNESS * d` are skipped (`continue`).
- `touch.py:_one_network (315)` | P2 and P4 | Joins orphan pieces, or drops them: `if all(serves(h, _others, _built) for h in _served): lanes[i]["pts"] = []; s.drop_lanes(_dropped_idx)`. If a house would be stranded the piece is kept and counted in `meta.lane_orphans`.
- `touch.py:_join_piece (468)` | P2 | Splices the link, refusing it if `_clear_of_fabric` is worse or `_bends_badly` adds a fold; the refused splice is drawn as its own lane.
- `touch.py:_detour_links (28)` / `_fine_lattice_links (85)` | P2 | The ladder's rungs for a stranded piece.
- `touch.py:serves (625)` | TWICE | See below.

## smooth.py

- `smooth.py:_smooth_web (156)` | P2 | String-pulls, cuts hairpin arms < `_ARM_FT`, gathers knots, empties shadows (`_commit(i, [])`), and cuts bow-tie tails (`bowtie_cut`). Every rewrite goes through `_commit` → `commit_lane`.
- `smooth.py:commit_lane (88)` | P3 and KEPT | Writes `lanes[m]["pts"] = new_pts`, then `if web_pieces(lanes) > before and not web_rejoinable(...): lanes[m]["pts"] = old; return False`. It asks `admit` first, writes, tests the whole web, and reverts.
- `smooth.py:web_pieces (36)` / `web_rejoinable (48)` | P3 | Whole-web piece count and "will the touch pass close it".
- `smooth.py:string_pull_chord_ok (120)` | KEPT | `_clear_link`, or `_clear_touch` plus every skipped vertex within `_JOG_FT` of the chord.

## joints.py

- `joints.py:straighten_joints (258)` | P2 | `_one_hook` / `_one_joint`: hook removed, fold becomes a T (`tee`), jog pulled straight, joint moved back (`_joint_moved_back`).
- `joints.py:center_lane_ends (521)` | P2 | Slides an end onto the other tread's centerline (`centered_end`).
- `joints.py:meet_end_to_end (551)` | P2 | Moves a free end onto another end within `_MEET_FT` (25).
- `joints.py:split_at_crossings (596)` | P2 | Cuts a lane at a mid-run crossing into two records.
- `joints.py:fold_the_connector_hairpin (664)` | P2 | Re-lays a lane to meet the connector as a T.
- KEPT: `joints.py:keeps_the_web (194)` — "Every other lane end that touched `old` must still touch... pieces no more... every farmhouse some way served still served", asked of the candidate before `commit_lane`. Also KEPT: `arrives_off (387)` (a joint is not moved off its farm).

## bund.py

- `bund.py:run_lanes_on_to_the_bund (237)` | P2 | Pulls an end in the crop out and carries a reaching-nothing end to the bund.
- `bund.py:a_way_onto_the_bund (296)` | P1 | Runs after the lanes are laid: `joined`, or `run_on`, or `branch`, or the string "none: every straight way ... crosses water, the marsh or a steading" (P4, gives up).
- `bund.py:cut_past_the_junction (462)` / `cut_stub_ends (490)` | P2 | Cuts a free end's run < `_PAST_JUNCTION_FT` (40) past its first junction.
- KEPT: `bund.py:RunOnBlocks.clear (172)`, `turns_back (103)`, `off_the_fixtures (221)`, `tip_onto_the_bund (115)`, `carry_on (393)` — candidate run-ons are asked before being drawn (`blocks.clear`, `turns_back`, `off_the_fixtures`, `s.admits_lane`).

## squaring.py, weld.py, knots.py

- `squaring.py:square_every_crossing (79)` | P2 | Re-squares every lane at every brook or channel crossing after laying, via `squared_against`.
- `squaring.py:square_run (117)` | KEPT | The same squaring applied to a candidate run before judging or drawing (seating, tree).
- `squaring.py:cut_at_shallow_crossing (133)` | P2 | Cuts a lane crossing another under `law.NEEDLE_DEG`, only if `keeps_the_web`.
- `weld.py:weld_corner (41)` | P2 | Moves a sliver's corner onto the other tread, under `WELD_PX` (2 px).
- `knots.py:settle_knots (632)` | P2 with KEPT `judge` | Gathers knots. `judge` (675) asks, before applying: web components and the connector component (`memo.web`), `lawful(p, w, skip=i)` per moved lane, and the `_WHOLE_RULES` counts of the trial.
- `knots.py:next_gather (419)` | P2 | Searches forms: `moved_onto`, `teed_onto`, `tails_cut_back`, `teed_back`, `onto_cut_back`, `joiner_first_meeting`.
- `knots.py:knots (130)` / `lane_knots (771)` / `WebMemo (508)` | P3 and TWICE | See below.

## web/tidy.py, web/skeleton.py, street.py, fabric.py

- `web/tidy.py:tidy_lane_ends (76)` | P2 | Final trim of every lane to service. It runs `_trim_to_service`, `run_lanes_on_to_the_bund`, `kept_connector`, and drops `_nowhere` lanes via `unsplitting_drops`.
- `web/tidy.py:_drop_collapsed (28)` / `cut_the_overruns (51)` / `unsplitting_drops (182)` | P2 | Husk drop, hook and past-connector cut, network-preserving drop.
- KEPT: `web/tidy.py:kept_connector (200)` — `list(pts) if law.breaks_through(pulled, solid) else pulled`.
- `web/skeleton.py:_lay_skeleton (84)` | KEPT | Clips an arm (`clip_to_clear`), trims it (`served_arm`), refuses `_arm_crossing_accidental`, and lays `s.admitted_runs(arm, 5)` pieces ≥ `_WEB_MIN_FT`. The rest is dropped (P4).
- `street.py:trim_streets (469)` | P2 | Cuts a further street to its joints (`to_its_joints`).
- KEPT: `street.py:lay_row_streets (255)` / `unneedled (336)` — `Lawful(s, tree=True)`, `closes_a_needle`, `adds_a_needle` on the join before drawing; if both fail, a lawful `door_path` or none (P4).
- `fabric.py:_pull_back_to_service (418)` | P2 | Walks a connector's inner end to the network.
- KEPT: `fabric.py:_draw_web (357)` — `if joins and _hits_a_steading(...): return False`, `if not s.admits_lane(pts, width): return False`, `earns` short-run floor. A run that earns nothing is not drawn (P4).
- `geom.py:_trim_to_service (504)` | P2 | The shared trim; at draw time (`_lay_web_lane`, `served_arm`) it acts on a candidate, after laying (`tidy_lane_ends`, `settle_dangling`) on a lane.

## track.py, gateway.py, thread.py, dry_exit.py (connector and spur)

- KEPT: `track.py:connector_keeps_the_law (704)` — `law.breaks_through`, `law.bends_badly`, `forbidden_segment`, brook crossed at most once.
- `track.py:connector_dry_exit (737)` | P4 | `if path is None: raise NoDryExit(f"no dry way out of the frame from the gateway at ...")`.
- `track.py:_connector_through (659)` | P4 | If the threaded run fails `connector_keeps_the_law`, it takes the dry exit; as a last resort `st.reserved.release_seats_along(run, CONNECTOR_WIDTH)` gives up reserved wood seats (a rule relaxed).
- `gateway.py:gateway_track (22)` / `turned_gateway_track (47)` | P4 | Falls back through `GATEWAY_TURNS_DEG`, then `raise NoDryExit("no dry way out ... on any bearing off the cluster")`.
- `track.py:connector_track (487)` | P4 | `assert best is not None; if best[0][:2] == (0, 0): return best[1]; return connector_dry_exit(...)`. The least-bad bearing is kept only where dry and clear.
- `thread.py:_thread_the_fabric (112)` | P4 | After route, clip and swing it returns `[]` ("hands back nothing: the spur is then recorded as dropped").
- `thread.py:spur_cut_at_the_fold (51)` | P4 | `return cut, "folded back short of the field - ..."` and the spur is not drawn.
- `track.py:stage_track (214)` | P4 | The spur is skipped with `meta.field_spur_swept` reasons ("overlap matrix refuses the spur", "runs in the worked ground end to end", etc.).

## forced.py

- `forced.py:forced_turn (91)` / `forced_meeting (97)` | P4 | Relax the angle rules: a kink, hook, fold or needle whose straighter way "is not lawful ground" is not a fault. Used by `law.kink_faults`, `hook_faults`, `needle_ends`, `folded_joint_pairs`, `connector_hairpin_ends`. A rule is waived where ground blocks, rather than room being sought.

## route.py

- `route.py:_route (162)` | P4 | "Returns [] when there is genuinely no way through" (and `return []` at the crop check, ~line 285).
- `route.py:_unjog (298)` / `_ease_corner (361)` | P2 (on a routed candidate, before commit) and TWICE | Hardcode `>= 140.0`, `>= 50.0` and `<= 40.0`; see TWICE.

## TWICE (a rule coded in two or more places)

1. **Doubled tail and side-by-side angle.** `tails.py:_sweep_doubled_tails (189)` calls `along_tail(pts, op)` at default `_ALONG_DEG` = 25. `law.doubled_tails (437)` → `tails.tail_doubled`, `settle/ends.py:settle_ends (115)`, `settle/lawful.py:fault (191)` and `tree.py:tree_faults (489)` all use `deg=_DOUBLED_DEG` = 15. The sweep cuts at 25; the rule is 15. A third value, `knots._SIDE_BY_SIDE_DEG = 20` (`knots.py:187`), equals `law.NEEDLE_DEG` = 20 (`law.py:211`).
2. **No way drawn twice (shadow).** Four formulations:
   - `serve.py:_lay_web_lane (208)` — 60% of samples within `WEB_SHADOW_FT` or an unbroken stretch > `BUNDLE_PITCH`.
   - `serve.py:runs_beside (75)` — only the unbroken-stretch clause.
   - `sweeps.py:_sweep_doubled_remnants (466)` — `shadowing_lane` (both ends on one other way within `_LANE_JOIN_FT`) or `shadow_share` ≥ `_DOUBLED_SHARE` (50%) at `_DOUBLED_GAP_FT` = 8.
   - `smooth.py:_smooth_web` step 2b (343) — every vertex within the other stroke's half-width + 1.
   The fraction clause of the placer is absent from `law.LAW`; `law.LAW` has a "shadows" name only in `WebMemo.count`.
3. **Hook.** `law.hooked (274)`, `clearance.py:drop_end_nubs/nub_at_head (209)`, `sweeps.py:trim_free_stub (357)`, `joints.py:unhooked (220)` and `geom.py:door_unhooked (245)` each test "last leg ≤ `_HOOK_FT`, turn ≥ `_HOOK_DEG`". They share the two constants but have five bodies with different guards (free end only, junction foot kept, touches every way the old end touched).
4. **Bend: hairpin and zigzag.** `clearance.kink_spans (355)` / `_bends_badly (387)` is the named single body. `route.py:_unjog (302, 314)` and `_ease_corner (381)` write `>= 140.0`, `>= 50.0` and `<= 40.0` as literals instead of `_HAIRPIN_DEG`, `_ZIGZAG_DEG`, `_ZIGZAG_RUN_FT`. `joints.py:_SHORT_LEG_FT = 40.0` is another copy of the run bound.
5. **Tail beyond a crossing or junction (< 40 ft).** Six copies:
   - `sweeps.py:_PAST_CONNECTOR_FT`
   - `bund.py:_PAST_JUNCTION_FT`
   - `settle/shapes.py:_CROSSING_TAIL_FT`
   - `clearance.py:_ARM_FT` (via `smooth._arm_cuttable`)
   - `touch.py:287` literal `40.0`
   - `serve.py:234` literal `40.0`
6. **Ends within 25 ft joined.** `smooth._KNOT_FT` (= `gap_ways.KNOT_FT`), `knots._KNOT_FT` imported from `smooth`, `knots._KNOT_MARGIN` (= 1.0, redefined at 762 though `KNOT_MARGIN` is imported), `joints._MEET_FT = 25.0`, `fabric._LANE_JOIN_FT = 25.0`, `consts_ways.LANE_JOIN_FT = 25.0`, `law.JOIN_REACH_FT = _LANE_JOIN_FT`. The knot verdict itself exists in two bodies: `knots.knots (130)` (placer search, `end_nodes` + `_fixed`) and `knots.lane_knots (771)` (finished-map verdict).
7. **End reaches a farmhouse or steading.** Three bodies for 60 ft / 12 ft: `geom.end_serves (469)` (house centre + `ring_within` steadings), `law.reach_to_steading (150)` (house body + recorded parts of the same household), `touch.serves (625)` (60 ft + built-ground polygons within 12 ft). `law.HOUSE_REACH_FT`/`STEADING_REACH_FT` duplicate `WAY_END_REACH_FT`/`STEADING_ARRIVAL_FT`.
8. **A way serves a house within 100 ft.** `checks.unreached_houses (398)` uses `WEB_REACH_FT`; `sweeps._SERVE_FT = 100.0` (used in `_sweep_debris`, `cut_past_connector`, `joints.keeps_the_web`) is a separate constant restating it; `_sweep_doubled_remnants` and `tidy_lane_ends` use `WEB_REACH_FT` directly.
9. **One network.** `_components` is asked at different tolerances: `sweeps._join_orphan_ways (281)` grows `main` at `_net_reach <= _LANE_JOIN_FT` (25 ft); `touch._one_network (339)`, `smooth.web_pieces (44)`, `tidy.unsplitting_drops (192)` and `sweeps._sweep_debris (888)` use 4.0; `law.lane_networks`, `settle.connector_component` use `JOIN_TOL`. `checks.served_network` uses `_TOUCH_GAP`. The orphan joiner's 25 ft test and the law's 4 ft test differ.
10. **Fabric foul.** `settle/shapes.py:fouled_segment (99)` is the full predicate. `sweeps.py:_sweep_steading_fouls (531)` asks only `_hits_a_steading`, and `fabric._draw_web (397)` asks `_hits_a_steading` only `if joins`. `serve.door_path.ok/kept` hand-roll `_crosses_fabric(walls, 0.0)` and bands next to `lawful(...)`.
11. **Dangling end.** `law.dangling_lane_ends (704)` filters ways by `_walked_to`; `geom._trim_to_service (555)` filters by far end within `_TOUCH_GAP`; `sweeps._sweep_dangling_ends._reaches (713)` uses its own filter. All share `end_serves` and differ in the "way it left" rule.
12. **A street's end cut to its joints.** `street.trim_streets (469)` / `to_its_joints (402)` at the web stage and `settle/ends.py:settle_street_ends (201)` / `end_to_its_joint` (438) in the settle.
13. **Link takes its way's width.** `serve.join_width (106)`, `sweeps._join_orphan_ways (339)` (inline max), `touch._join_piece (480)`, `settle_widths (386)`, `law.width_steps (657)`.
14. **Spur reaches the field.** `thread.SPUR_REACH_FT = 6.0` and `law.FIELD_REACH_FT = 6.0`; the comment says "a test holds them equal."
15. **Debris floor.** `fabric._WEB_MIN_FT` = 30 (`_draw_web`, `tidy_lane_ends`, `_sweep_debris`, `served_arm`, `_sweep_dangling_ends`) and `law.FRAGMENT_FT = _WEB_MIN_FT` (`short_fragments`, which adds three extra no-worse tests the sweeps do not).
16. **Past connector, `law.BREAK_SPAN_FT` (60) vs `sweeps._BREAK_SPAN_FT` (150).** Same name, different rules (mid-run break vs bridgeable gap). Listed only because the names collide.

## Notes on P1 (no up-front predicate)

- The up-front-asked predicates are `fouled_segment` / `Lawful` / `admits` / `end_serves` / `connector_keeps_the_law` / `meets_clean` / `_clear_link` / `may_write`. Rules with only a post-lay reading are: the doubled-band 60% clause (`_lay_web_lane` only), `_sweep_doubled_remnants`' 8 ft / 50% (sweep only), `law.near_misses` (join stops short; asked at tree admit by `as_joined` but not at the web's `_touch_junctions`), `law.width_steps`, and `law.doorstep_ends` (asked at tree admit via `ends.with_one_more`, but not when ordinary lanes are laid).
- `law.LAW` names with no placer predicate before laying an ordinary web lane: `husks`, `shallow_crossings`, `needle_loops` (except in `closes_a_needle` for door paths/streets), `over_and_back`, `off_ford`, `oblique_*`, `unbridged`, `undeckable`, `short_decks`, `planks`.
