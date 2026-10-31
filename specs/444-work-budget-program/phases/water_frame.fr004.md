# FR-004 for T19's port - the keys water_frame writes, before and after (measured 2026-10-31)

The rulings on ask:444-T19-output-keys and ask:444-T19-outside-charges: the set of meta keys the stage writes must match before and
after the port, on the reference seeds at 10, 20 and 40 households and on a seed per settlement form; the values may move (D7).

Method: `make hamlet ARGS="--name Inashiro --seed <s> --households <h> [--form <f>] --out <path> --no-render"`, in a detached
worktree of origin/main ("main") and in the clone with the port ("port"), for seeds 4, 25, 39, 47 at 10, 20, 40 and seed 4 at 20 with
each form pinned; each finished manifest's `meta` read against the 31 keys of `water_frame.keys.json`.

```
main s25-h10 nucleated 31/31
main s25-h20 nucleated 31/31
main s39-h10 nucleated 31/31
main s39-h20 nucleated 31/31
main s4-h20-dispersed dispersed 31/31
main s4-h20-nucleated nucleated 31/31
main s47-h10 nucleated 31/31
main s47-h20 nucleated 31/31
port s25-h10 dispersed 31/31
port s25-h20 dispersed 31/31
port s39-h10 nucleated 31/31
port s39-h20 nucleated 31/31
port s4-h10 dispersed 31/31
port s4-h20-dispersed dispersed 31/31
port s4-h20-linear linear 31/31
port s4-h20 dispersed 31/31
port s47-h10 linear 31/31
port s47-h20 linear 31/31
```

Every finished roll writes all 31 keys, in both trees; the port's rolls cover all three forms (nucleated, dispersed, linear). The
rolls that refused, in either tree, refused in later stages (the field's and the web's known refusals), on different seeds because the
maps differ: main s4-h10 WebRefused;main s4-h20-linear WebRefused;main s4-h20 WebRefused;port s4-h20-nucleated WebRefused;.

The SitePlan's fields: the same, but one added - `counted_for` (compare=False, repr=False), the per-owner record of the plan's
rolls other stages read (ask:444-T19-outside-charges); no stage reads it as a fact about the map.
