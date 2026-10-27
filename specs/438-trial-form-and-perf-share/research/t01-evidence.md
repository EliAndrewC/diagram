# T01 evidence - make perf-share on feature 437's four kept profiles

Run 2026-10-27, `make perf-share PROFILES=<437's four raw profiles>`, in under a second (the four were read, none profiled):

```
homesteads (seed 25, 40 households): 20261027T205423Z-seed25-homesteads.prof
  profiled 4.47 s; l7r/diagram/settlement/_geom/primitives.py self 0.111 s (2.5%)
  largest self time in the stage:
      0.162 s  hamletgen/homesteads/boundary.py:467(_samples)
      0.137 s  settlement/rolling/gap_ways.py:201(flood)
      0.133 s  ~:0(<built-in method builtins.max>)
      0.133 s  settlement/homestead_parts/fixture_seats.py:647(_first)
      0.098 s  settlement/homestead_parts/fixture_seats.py:224(within_reach_of)
      0.094 s  ~:0(<built-in method builtins.min>)
      0.092 s  ~:0(<method 'get' of 'dict' objects>)
      0.085 s  settlement/_geom/indexes.py:276(near)
  callers of primitives.py, by its time under them (cumulative):
      0.044 s     41,149 calls  seg_dist           from settlement/homestead_parts/wood_share.py:408(<genexpr>)
      0.029 s     24,326 calls  seg_dist           from settlement/homestead_parts/wood_share.py:390(corridor_bars)
      0.018 s        294 calls  seg_dists          from hamletgen/ways/serve.py:42(shadow_measure)
      0.011 s      9,037 calls  <genexpr>          from ~:0(<built-in method builtins.min>)
      0.009 s      7,026 calls  seg_dist           from hamletgen/ways/law/meet.py:213(<genexpr>)
      0.009 s      1,136 calls  edge_dist          from settlement/homestead_parts/yards.py:409(<genexpr>)
      0.007 s      6,068 calls  seg_dist           from settlement/rolling/access.py:88(seg_box_within)
      0.007 s        459 calls  chain_distance     from hamletgen/homesteads/growth.py:342(field_distance)
web (seed 25, 40 households): 20261027T205431Z-seed25-web.prof
  profiled 1.90 s; l7r/diagram/settlement/_geom/primitives.py self 0.108 s (5.7%)
  largest self time in the stage:
      0.171 s  hamletgen/ways/route.py:90(lattice_search)
      0.140 s  ~:0(<method 'get' of 'dict' objects>)
      0.084 s  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
      0.061 s  /home/agent/.local/lib/python3.14/site-packages/shapely/decorators.py:73(wrapped)
      0.051 s  ~:0(<built-in method builtins.min>)
      0.049 s  hamletgen/ways/tails.py:38(along_tail)
      0.049 s  ~:0(<built-in method builtins.max>)
      0.046 s  settlement/_geom/primitives.py:59(seg_closest)
  callers of primitives.py, by its time under them (cumulative):
      0.024 s     48,528 calls  segments_cross     from settlement/city/bridges.py:281(undeckable_at)
      0.017 s     15,267 calls  seg_dist           from hamletgen/ways/tails.py:38(along_tail)
      0.014 s     12,750 calls  seg_dist           from overlap/reserved.py:167(<genexpr>)
      0.011 s     11,050 calls  seg_dist           from hamletgen/ways/serve.py:255(<genexpr>)
      0.010 s      9,624 calls  seg_dist           from hamletgen/ways/tree.py:91(<genexpr>)
      0.010 s      7,295 calls  seg_dist           from settlement/_geom/indexes.py:515(edge_within)
      0.009 s      9,581 calls  seg_dist           from hamletgen/ways/bund.py:322(<genexpr>)
      0.006 s      6,273 calls  seg_dist           from settlement/water_ways/lanes.py:293(<lambda>)
field (seed 25, 40 households): 20261027T205435Z-seed25-field.prof
  profiled 2.19 s; l7r/diagram/settlement/_geom/primitives.py self 0.021 s (0.9%)
  largest self time in the stage:
      0.123 s  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
      0.080 s  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:112(intersection)
      0.075 s  /home/agent/.local/lib/python3.14/site-packages/shapely/constructive.py:136(buffer)
      0.073 s  /home/agent/.local/lib/python3.14/site-packages/shapely/decorators.py:73(wrapped)
      0.055 s  waterfields/banks.py:927(pointed_ring)
      0.048 s  hamletgen/water/brook_course.py:112(_crop_edge)
      0.046 s  waterfields/carve.py:389(buried)
      0.046 s  /home/agent/.local/lib/python3.14/site-packages/shapely/measurement.py:53(distance)
  callers of primitives.py, by its time under them (cumulative):
      0.010 s      2,376 calls  point_in_poly      from sitegen/geom.py:107(<genexpr>)
      0.007 s     12,000 calls  segments_cross     from sitegen/geom.py:104(<genexpr>)
      0.001 s        212 calls  point_in_poly      from hamletgen/water/brook.py:438(clear_of_field)
      0.001 s        172 calls  point_in_poly      from hamletgen/water/comb.py:21(stage_field)
      0.001 s        150 calls  point_in_poly      from hamletgen/water/brook_rules.py:160(<genexpr>)
      0.001 s        480 calls  seg_dist           from settlement/_geom/overlap.py:86(<genexpr>)
      0.000 s        384 calls  seg_dist           from settlement/_geom/overlap.py:89(quad_hits_seg)
      0.000 s        237 calls  seg_dist           from settlement/_geom/indexes.py:378(<genexpr>)
hinterland (seed 25, 40 households): 20261027T205444Z-seed25-hinterland.prof
  profiled 1.88 s; l7r/diagram/settlement/_geom/primitives.py self 0.117 s (6.3%)
  largest self time in the stage:
      0.155 s  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
      0.066 s  hamletgen/homesteads/bamboo.py:326(parts_hit)
      0.063 s  settlement/_geom/indexes.py:472(inside_many)
      0.057 s  /home/agent/.local/lib/python3.14/site-packages/shapely/constructive.py:136(buffer)
      0.048 s  settlement/_geom/indexes.py:263(extend)
      0.046 s  ~:0(<built-in method builtins.min>)
      0.046 s  ~:0(<built-in method numpy.asarray>)
      0.043 s  settlement/homestead_parts/bamboo_keepout.py:45(<genexpr>)
  callers of primitives.py, by its time under them (cumulative):
      0.077 s         92 calls  convex_hull        from settlement/land/cover.py:72(grown)
      0.036 s      3,206 calls  point_in_poly      from hamletgen/homesteads/bamboo.py:420(<genexpr>)
      0.021 s     17,508 calls  seg_dist           from hamletgen/homesteads/bamboo.py:602(<genexpr>)
      0.010 s     13,884 calls  segments_cross     from hamletgen/homesteads/bamboo.py:604(<genexpr>)
      0.003 s      5,889 calls  segments_cross     from settlement/_geom/water_index.py:68(crosses_a_stream)
      0.001 s        904 calls  seg_dist           from settlement/_geom/indexes.py:515(edge_within)
      0.001 s      2,030 calls  segments_cross     from hamletgen/homesteads/bamboo.py:407(<genexpr>)
      0.001 s         34 calls  point_in_poly      from settlement/homestead_parts/grove_fill.py:510(<genexpr>)

l7r/diagram/settlement/_geom/primitives.py: 0.357 s of 10.43 s profiled across 4 stage(s) (3.4%) - cProfile inflates call-dense code most; read it as an upper bound
```

It reproduces feature 437's `research/share.md` (0.357 s of 10.43 s, 3.4%, which 437 rounded to 3.5%), which took two ad-hoc
scripts and about 3 minutes to write.
