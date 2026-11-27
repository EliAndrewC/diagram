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
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>
"#);

/// What the template's "Performance work?" prompt said of a `[perf]` task until feature 451 T410, and what it says since: FR-013's
/// measurement clause named. WHY: the prompt defined performance work only as what makes something faster, and on 2026-11-26/27
/// five plan reviews blocked a round on a section answering "no: a measurement" (T315, T274, T301 and two headed off by brief),
/// against FR-013 - work that measures where the time goes counts as performance work for the ordering. Kept so [`stubs`] still
/// knows a stub written before the change.
const FASTER_WAS: &str = "the builders' loop faster), and for";
const FASTER: &str = "the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for";

/// What `make task-add ... PERF=1` appends to a performance task's section (feature 435, D2; the GM 2026-10-27: the checklist helps "us
/// not forget steps as we work towards our goal, rather than the checklist items being taken as if they are themselves the goal").
pub const PERFORMANCE: &str = r"
### {T} Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>
";

/// The unfilled section `make task-add` writes for `task`, in its two forms: with the performance checklist (`PERF=1`), the longer
/// and so the first, and without - then the same two as they were written before feature 451 T410 changed the "Performance work?"
/// prompt ([`FASTER_WAS`]), which the plans still hold (a stub is matched byte for byte, so a changed template would orphan every
/// stub filed before it). THE ONE STUB TEST (feature 451 T359): `make task-withdraw` removes a section only where it is one
/// of these byte for byte, and the plan gate owes nothing for a withdrawn task's removed block only where it was a block of one
/// ([`stub_block`]) - a section somebody filled in is a decision, whatever form its task's box takes.
#[must_use]
pub fn stubs(task: &str) -> [String; 4] {
    let was = TEMPLATE.replace(FASTER, FASTER_WAS);
    [
        format!("{TEMPLATE}{PERFORMANCE}"),
        TEMPLATE.to_owned(),
        format!("{was}{PERFORMANCE}"),
        was,
    ]
    .map(|t| t.replace("{T}", task))
}

/// Is `block` - a heading line and the text to the next heading - a block of `task`'s unfilled stub ([`stubs`]), byte for byte? The
/// newlines that end it aside: a stub's last block ends where its section does, and a plan's runs on to the next heading.
#[must_use]
pub fn stub_block(task: &str, block: &str) -> bool {
    let bare = |text: &str| text.trim_end_matches('\n').to_owned();
    let stubs = stubs(task);
    let mut theirs = stubs.iter().flat_map(|s| l7r_shared::plan_text::blocks(s));
    theirs.any(|(key, body, _)| key != "preamble" && bare(&body) == bare(block))
}

#[cfg(test)]
mod tests {
    use super::{stub_block, stubs, PERFORMANCE, TEMPLATE};

    #[test]
    fn a_stub_s_blocks_are_the_template_s_with_the_id_filled() {
        let [perf, plain, was_perf, was_plain] = stubs("T07");
        // the prompt names FR-013's measurement clause (451 T410), and a stub written before it did is a stub still
        let prompt = "(a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task";
        assert!(plain.contains(prompt), "{plain}");
        let was = "the builders' loop faster), and for an engine-speed task";
        assert!(was_plain.contains(was) && !plain.contains(was));
        assert_eq!(was_plain.replace(super::FASTER_WAS, super::FASTER), plain);
        assert_eq!(
            was_perf,
            format!("{was_plain}{}", PERFORMANCE.replace("{T}", "T07"))
        );
        let approach = "### T07 Approach (checklist part A)";
        let old_block = &was_plain[was_plain.find(approach).unwrap()..];
        assert!(
            stub_block("T07", old_block) && old_block != &plain[plain.find(approach).unwrap()..]
        );
        assert_eq!(plain, TEMPLATE.replace("{T}", "T07"));
        assert_eq!(
            perf,
            format!("{plain}{}", PERFORMANCE.replace("{T}", "T07"))
        );
        let head = "### T07 Approach (checklist part A)";
        let block = &plain[plain.find(head).unwrap()..];
        assert!(stub_block("T07", block) && stub_block("T07", &format!("{block}\n\n")));
        // the performance form's own block, and the template's last block as that form holds it
        let checklist = &perf[perf.find("### T07 Performance checklist").unwrap()..];
        assert!(
            stub_block("T07", checklist)
                && stub_block(
                    "T07",
                    &perf[perf.find(head).unwrap()..perf.find("\n### T07 Performance").unwrap()]
                )
        );
        // another task's stub, a block filled in, a heading alone and the empty text before a stub's first heading are none
        assert!(!stub_block("T08", block));
        assert!(!stub_block(
            "T07",
            &block.replace("<the place as it should be>", "the wells drawn")
        ));
        assert!(!stub_block("T07", head) && !stub_block("T07", ""));
    }
}
