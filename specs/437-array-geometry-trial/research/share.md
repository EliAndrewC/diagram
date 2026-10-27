# Where the geometry time is - the trial's first measurement

Measured 2026-10-27 (`make perf-profile SEED=25 STAGE=<stage> HOUSEHOLDS=40` for the four largest stages by time share at
the 435-start bookend - homesteads, web, field, hinterland - each profile's self time read by function with pstats; the
scripts are `research/share.py` and `research/callers.py`). cProfile inflates call-dense Python most, so the primitives'
true (unprofiled) share is smaller still than below.

## The shared primitives' share of each stage (`settlement/_geom/primitives.py`, self time)

```
== homesteads.prof: total 4.47s; primitives.py self 0.111s (2.5%); math/min/max/abs builtins 0.401s; generator expressions 0.242s (5.4%)
     0.162s self  hamletgen/homesteads/boundary.py:467(_samples)
     0.137s self  settlement/rolling/gap_ways.py:201(flood)
     0.133s self  ~:0(<built-in method builtins.max>)
     0.133s self  settlement/homestead_parts/fixture_seats.py:647(_first)
     0.098s self  settlement/homestead_parts/fixture_seats.py:224(within_reach_of)
     0.094s self  ~:0(<built-in method builtins.min>)
     0.092s self  ~:0(<method 'get' of 'dict' objects>)
     0.085s self  settlement/_geom/indexes.py:276(near)
== web.prof: total 1.90s; primitives.py self 0.108s (5.7%); math/min/max/abs builtins 0.138s; generator expressions 0.100s (5.3%)
     0.171s self  hamletgen/ways/route.py:90(lattice_search)
     0.140s self  ~:0(<method 'get' of 'dict' objects>)
     0.084s self  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
     0.061s self  /home/agent/.local/lib/python3.14/site-packages/shapely/decorators.py:73(wrapped)
     0.051s self  ~:0(<built-in method builtins.min>)
     0.049s self  hamletgen/ways/tails.py:38(along_tail)
     0.049s self  ~:0(<built-in method builtins.max>)
     0.046s self  settlement/_geom/primitives.py:59(seg_closest)
== field.prof: total 2.19s; primitives.py self 0.021s (0.9%); math/min/max/abs builtins 0.165s; generator expressions 0.068s (3.1%)
     0.123s self  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
     0.080s self  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:112(intersection)
     0.075s self  /home/agent/.local/lib/python3.14/site-packages/shapely/constructive.py:136(buffer)
     0.073s self  /home/agent/.local/lib/python3.14/site-packages/shapely/decorators.py:73(wrapped)
     0.055s self  waterfields/banks.py:927(pointed_ring)
     0.048s self  hamletgen/water/brook_course.py:112(_crop_edge)
     0.046s self  waterfields/carve.py:389(buried)
     0.046s self  /home/agent/.local/lib/python3.14/site-packages/shapely/measurement.py:53(distance)
== hinterland.prof: total 1.88s; primitives.py self 0.117s (6.3%); math/min/max/abs builtins 0.145s; generator expressions 0.124s (6.6%)
     0.155s self  /home/agent/.local/lib/python3.14/site-packages/shapely/set_operations.py:463(union_all)
     0.066s self  hamletgen/homesteads/bamboo.py:326(parts_hit)
     0.063s self  settlement/_geom/indexes.py:472(inside_many)
     0.057s self  /home/agent/.local/lib/python3.14/site-packages/shapely/constructive.py:136(buffer)
     0.048s self  settlement/_geom/indexes.py:263(extend)
     0.046s self  ~:0(<built-in method builtins.min>)
     0.046s self  ~:0(<built-in method numpy.asarray>)
     0.043s self  settlement/homestead_parts/bamboo_keepout.py:45(<genexpr>)
```

## The callers of `settlement/_geom/primitives.py`'s functions, by those functions' time under them (top 25; FR-001's search space - every function the module defines, read by file)

```
 0.077s       92 hinterland  convex_hull      settlement/land/cover.py:72(grown)
 0.070s   104239 homesteads  seg_closest      settlement/_geom/primitives.py:68(seg_dist)
 0.063s    97230 web         seg_closest      settlement/_geom/primitives.py:68(seg_dist)
 0.044s    41149 homesteads  seg_dist         settlement/homestead_parts/wood_share.py:408(<genexpr>)
 0.036s     3206 hinterland  point_in_poly    hamletgen/homesteads/bamboo.py:420(<genexpr>)
 0.029s    24326 homesteads  seg_dist         settlement/homestead_parts/wood_share.py:390(corridor_bars)
 0.024s    48528 web         segments_cross   settlement/city/bridges.py:281(undeckable_at)
 0.021s    17508 hinterland  seg_dist         hamletgen/homesteads/bamboo.py:602(<genexpr>)
 0.019s    24060 hinterland  <genexpr>        settlement/_geom/primitives.py:185(convex_hull)
 0.018s      294 homesteads  seg_dists        hamletgen/ways/serve.py:42(shadow_measure)
 0.017s    15267 web         seg_dist         hamletgen/ways/tails.py:38(along_tail)
 0.014s    12750 web         seg_dist         overlap/reserved.py:167(<genexpr>)
 0.013s    18760 hinterland  seg_closest      settlement/_geom/primitives.py:68(seg_dist)
 0.011s     9037 homesteads  <genexpr>        ~:0(<built-in method builtins.min>)
 0.011s    11050 web         seg_dist         hamletgen/ways/serve.py:255(<genexpr>)
 0.011s   103812 web         ccw              settlement/_geom/primitives.py:129(segments_cross)
 0.010s     2376 field       point_in_poly    sitegen/geom.py:107(<genexpr>)
 0.010s     9624 web         seg_dist         hamletgen/ways/tree.py:91(<genexpr>)
 0.010s    13884 hinterland  segments_cross   hamletgen/homesteads/bamboo.py:604(<genexpr>)
 0.010s     7295 web         seg_dist         settlement/_geom/indexes.py:515(edge_within)
 0.009s     9581 web         seg_dist         hamletgen/ways/bund.py:322(<genexpr>)
 0.009s    85014 hinterland  cross            settlement/_geom/primitives.py:185(convex_hull)
 0.009s     7026 homesteads  seg_dist         hamletgen/ways/law/meet.py:213(<genexpr>)
 0.009s     1136 homesteads  edge_dist        settlement/homestead_parts/yards.py:409(<genexpr>)
 0.008s     7388 homesteads  seg_dist         settlement/_geom/primitives.py:182(<genexpr>)
{'homesteads.prof': 4.47, 'web.prof': 1.9, 'field.prof': 2.19, 'hinterland.prof': 1.88}
```

## Reading

- `settlement/_geom/primitives.py` holds 0.36 s of the four stages' 10.4 s profiled (3.5%): 2.5% of homesteads, 5.7% of web,
  0.9% of field, 6.3% of hinterland. Made free, it would save a few percent - the ceiling on vectorizing the shared layer.
- No hotspot: the largest self-time function in any of the four is 3.6% of its stage (`boundary._samples`); the time is in
  hundreds of loops, dictionary lookups (`dict.get`), `min`/`max` and shapely's unions.
- T57's "two thirds of the calls are scalar comparisons" is a count of calls, not of time - feature 435's finding again.
- THE PREDICATE, by FR-001: `seg_dist` (with `seg_closest`, which it calls) - the single-point scalar predicate with the most
  time under its callers (`convex_hull`, first in the table, takes a set of points, not one).
- ITS HOTTEST CALLER: the wood-share corridor test, `WoodShares.corridor_bars` (`settlement/homestead_parts/wood_share.py`):
  its seat test (the generator on line 408, inside `corridor_bars`) 0.044 s and its cell test (line 390) 0.029 s of
  `seg_dist` under it; `corridor_bars` 0.135 s cumulative over 4,199 calls, 3.0% of homesteads profiled.
