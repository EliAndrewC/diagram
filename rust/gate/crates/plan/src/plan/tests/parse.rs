//! 451 T466: a whole-plan judgment parses plan.md's task sections once. `ruled_tasks` asked `task_current` of each section, and each
//! ask parsed the whole plan's sections again to find its own: about 1.8 s a judgment over a 1 MB plan.md of some 300 sections,
//! measured 2026-11-27 (an Instant trace of `l7r-gate tick --land-check` over a scratch clone of diagram-backlog).

use super::super::sections::{digest, parses};
use super::super::status::{judge, judge_in, scope_of};
use super::current;

/// RED FIRST: a plan of five task sections, judged whole and judged for one tick, parses its sections once a judgment.
#[test]
fn a_whole_plan_judgment_parses_its_task_sections_once() {
    let plan: String = (1..=5).fold(
        "# plan\n\n**D1 - a decision.** Each tub by a door.\n".to_owned(),
        |p, n| format!("{p}\n## T0{n} a task\n\n- a well by the kitchen\n"),
    );
    let mut review = current(&[], "CLEAR", &plan);
    review["tasks"]["T02"] =
        serde_json::json!({"verdict": "CLEAR", "section_sha256": digest(b"an older section")});
    let review = review.to_string();
    let before = parses();
    let whole = judge(Some(plan.as_bytes()), Some(&review), None, "");
    assert_eq!((parses() - before, whole), (1, None));
    let (before, scope) = (parses(), scope_of("", &["T03"]));
    let one = judge_in(Some(plan.as_bytes()), Some(&review), None, "", Some(&scope));
    assert_eq!((parses() - before, one), (1, None));
}
