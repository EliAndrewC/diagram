//! 451 T501: `l7r-gate plan section <feature> <task[,task]> [--cited]` prints exactly a task's plan sections and no other task's, so a
//! builder reads its own sections instead of grepping the whole plan into context (451 T499: 3.68 MB of plan text in builders' tool
//! results over two days, 14.7% of them, by grep 49.7% and sed ranges 32.7%).

use super::super::sections::parses;
use super::super::show::cited;
use super::{feature_at, repo, run};

const PLAN: &str = "# plan\n\n**D1 - a decision.**\n\n## Tasks\n\n### T05 (the bath)\n\n- the bath, beside T06, 451 T08 and 449 T92; T11 and T99 too\n\n### T05 Approach (checklist part A)\n\n1. **The goal.** a bath\n\n### T06 (the wells, left by T05)\n\n- a well, by T11 and 449\n  T92\n\n### T07, T08 Approach (checklist part A)\n\n1. **Shared.** both\n\n### T08 (its own)\n\n- eight\n\n### T09 (mentions T10 only)\n\n- nine\n\n### T92 (this feature's own T92)\n\n- not 449's\n\n### T05 part B (2026-11-27T07:20Z)\n\n- the bath again\n";
const DONE: &str = "# the plan's finished sections\n\n<!-- plan-archive: archived 2026-11-20 -->\n### T11 (archived)\n\n- eleven\n<!-- plan-archive: archived 2026-11-21 -->\n";

fn shown(words: &[&str]) -> (i32, String, String) {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN), None, "451-x");
    std::fs::write(dir.join("plan-done.md"), DONE).unwrap();
    let mut all = vec!["section", "451"];
    all.extend_from_slice(words);
    let got = run(&root, &all);
    (got.code, got.stdout, got.stderr)
}

#[test]
fn a_task_s_sections_and_no_other_task_s() {
    let before = parses();
    let (code, out, _) = shown(&["T05"]);
    assert_eq!(code, 0);
    assert!(
        out.starts_with("==> T05 (plan.md)\n### T05 (the bath)\n"),
        "{out}"
    );
    assert!(out.contains("### T05 Approach (checklist part A)"));
    assert!(out.contains("### T05 part B (2026-11-27T07:20Z)"));
    for other in [
        "### T06", "### T07", "### T08", "### T09", "### T92", "## Tasks", "D1",
    ] {
        assert!(!out.contains(other), "{other} in {out}");
    }
    // the archive is read only for a task the live plan has no section of
    assert_eq!(parses() - before, 1);
    // a bare number is the task's id
    assert_eq!(shown(&["92"]).1, shown(&["T92"]).1);
    assert!(shown(&["92"]).1.starts_with("==> T92 (plan.md)\n"));
}

#[test]
fn a_bundle_s_heading_is_each_of_its_tasks_and_printed_once() {
    let (_, alone, _) = shown(&["T08"]);
    assert!(alone.contains("### T07, T08 Approach") && alone.contains("### T08 (its own)"));
    let (_, both, _) = shown(&["T07,T08"]);
    assert_eq!(both.matches("### T07, T08 Approach").count(), 1);
    assert!(both.contains("==> T07 (plan.md)\n### T07, T08 Approach"));
    assert!(both.contains("==> T08 (plan.md)\n### T08 (its own)"));
    let (_, turned, _) = shown(&["T08, T07"]);
    assert_eq!(turned.matches("### T07, T08 Approach").count(), 1);
    assert!(
        turned.ends_with("==> T07 (plan.md): its sections are printed above\n"),
        "{turned}"
    );
}

#[test]
fn an_archived_task_from_plan_done_and_a_missing_one_in_a_line() {
    let before = parses();
    let (code, out, _) = shown(&["T11"]);
    assert_eq!(code, 0);
    assert_eq!(
        out,
        "==> T11 (plan-done.md)\n### T11 (archived)\n\n- eleven\n"
    );
    assert_eq!(parses() - before, 2);
    // a task only another task's heading names has no section of its own: T09's is never printed for it
    let (_, out, _) = shown(&["T10"]);
    assert_eq!(
        out,
        "T10: no section of its own in plan.md or plan-done.md\n"
    );
}

#[test]
fn cited_adds_the_sections_named_one_level_and_nothing_else() {
    let (code, out, _) = shown(&["T05", "--cited"]);
    assert_eq!(code, 0);
    assert!(out.contains("==> T06 (plan.md, cited by T05)\n### T06 (the wells"));
    assert!(out.contains("==> T08 (plan.md, cited by T05)\n### T07, T08 Approach"));
    assert!(out.contains("==> T11 (plan-done.md, cited by T05)\n### T11 (archived)"));
    // another feature's T92 is not this one's, and one level only: T06 names T05, T09 is named by no printed section
    assert!(!out.contains("### T92") && !out.contains("### T09"));
    assert_eq!(out.matches("### T05 (the bath)").count(), 1);
    assert!(
        out.ends_with("cited with no section of its own: T99\n"),
        "{out}"
    );
}

#[test]
fn cited_over_several_tasks_prints_each_once_under_its_first_naming_task() {
    let (_, out, _) = shown(&["T05,T06", "--cited"]);
    assert_eq!(out.matches("### T11 (archived)").count(), 1);
    assert!(out.contains("==> T11 (plan-done.md, cited by T05)"));
    // the requested tasks are never cited, though each names the other; a wrapped "449\n  T92" is 449's
    assert!(!out.contains("==> T05 (plan.md, cited") && !out.contains("==> T06 (plan.md, cited"));
    assert!(!out.contains("### T92"));
    let (_, alone, _) = shown(&["T06", "--cited"]);
    assert!(alone.contains("==> T05 (plan.md, cited by T06)") && !alone.contains("### T92"));
}

#[test]
fn a_bad_feature_or_word_is_refused_with_the_usage() {
    let (code, _, err) = shown(&["T05", "--all"]);
    assert_eq!(code, 2);
    assert!(err.contains("section <feature> <task[,task]> [--cited]"));
    let root = repo();
    assert_eq!(run(&root, &["section", "999", "T05"]).code, 2);
    feature_at(&root, None, None, "452-y");
    let (code, err) = {
        let got = run(&root, &["section", "452", "T05"]);
        (got.code, got.stderr)
    };
    assert_eq!(code, 2);
    assert!(err.contains("no single specs/452* directory with a plan.md"));
}

#[test]
fn another_feature_s_number_carries_across_a_list_of_its_ids() {
    // 451 T501's plan review (round 1): in "449 T92, T93" the T93 is 449's too, and a list ends at any other word or a `;`
    let text = "by 449 T92, T93 and T94,\n  T95; T96, also 451 T97 or T98 - T99 then T100";
    let skip = ["T100".to_owned()];
    assert_eq!(cited(text, "451", &skip), ["T96", "T97", "T98", "T99"]);
}
