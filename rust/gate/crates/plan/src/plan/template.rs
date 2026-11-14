//! The plan section `make task-add` writes (feature 426 D6, feature 435 D2): the template, its red exit and the performance checklist.
//! Here since feature 449 T135 (`ask:449-phase3-remainder`): `task-add.py`'s port (`l7r-gate task-add`, the `task` crate) writes them,
//! and the approach gate reads the template's own wording of items 6 and 9 in process ([`crate::plan`]'s sections), where it read
//! `task-add.py`'s source text for them; the lint's hint is the same red exit (one text, FR-003).

/// Checklist item 6's red exit (feature 426, D6): the wording T48's and T50's plan reviews each blocked a round on. Generic, never one
/// feature's: the first form copied feature 417's D35 ("FR-008 green ... placed correctly ... (D11, D35)"), and feature 427's first plan
/// review blocked on that text in a profiling tool's section (2026-10-26).
pub const RED_EXIT: &str = "Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.";

/// The section `make task-add` writes when no `SECTION=` is given (feature 426, D6): the alone-off table and checklist item 6's red exit
/// already in place, the two things the plan reviews kept asking for. `{T}` is the id.
pub const TEMPLATE: &str = concat!(r#"### {T} (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### {T} Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. "#, "Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.", r#"
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>
"#);

/// What `make task-add ... PERF=1` appends to a performance task's section (feature 435, D2; the GM 2026-10-27: the checklist helps "us
/// not forget steps as we work towards our goal, rather than the checklist items being taken as if they are themselves the goal").
pub const PERFORMANCE: &str = r"
### {T} Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: `make perf-profile` time beside `make phase-calls` / `make perf-fanout` calls>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <calls; `make perf-ab` best of N with each arm's spread,
   the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>
";
