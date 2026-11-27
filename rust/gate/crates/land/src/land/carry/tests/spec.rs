//! The carry's rules for a feature's spec files (451 T300): a plan.md merged by section, a tasks.md whose every open box keeps the
//! line under it, a request.md both sides added a dated section to - each a stop of 2026-11-26 the session resolved by hand.

use std::fmt::Write as _;

use super::super::super::tests::has;
use super::super::{boxes as lines_under, keep_both, sections, Kind};
use super::{carried, commit, git, trees, TASKS_MD};

const PLAN: &str = "specs/451-x/plan.md";
const REQUEST: &str = "specs/451-x/request.md";
const RESEARCH: &str = "      research: rendering\n";

/// A plan of a preamble and the sections named, each `(id, body)`.
fn plan(sections: &[(&str, &str)]) -> String {
    let mut out = "# Plan\n\n## Task sections\n\n".to_owned();
    for (id, body) in sections {
        let _ = write!(out, "### T{id} (task {id}'s title)\n\n{body} {id}\n\n");
    }
    out
}

fn read(root: &std::path::Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap()
}

#[test]
fn a_plan_is_merged_by_section_the_builders_filled_stub_taken_and_the_clones_withdrawn_stub_left_out(
) {
    // RED FIRST (451 T300, 2026-11-26): before `sections::merged` this carry exits 2, "a hunk both sides changed, not only added
    // to" - the stop of T373, T359, T324, T383 and T299's carries. The shape of 781644768b against 1ceb830054's parent: the
    // builder fills its task's stub (T2) and files a task (T5) after the plan's last stub (T3), which the clone meanwhile withdrew
    let (_dir, root, builder) = trees("carry-plan");
    commit(
        &root,
        "the plan",
        &[(PLAN, &plan(&[("1", "done"), ("2", "stub"), ("3", "stub")]))],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    let theirs = plan(&[("1", "done"), ("2", "filled"), ("3", "stub"), ("5", "stub")]);
    commit(
        &builder,
        "T2: built",
        &[("rust/held.rs", "fn held() {}\n"), (PLAN, &theirs)],
    );
    commit(
        &root,
        "T3 withdrawn",
        &[(PLAN, &plan(&[("1", "done"), ("2", "stub")]))],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert_eq!(out.lines().count(), 1);
    has(&out, "; resolved specs/451-x/plan.md (by section)\n");
    assert_eq!(
        read(&root, PLAN),
        plan(&[("1", "done"), ("2", "filled"), ("5", "stub")])
    );
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn a_plan_section_both_sides_changed_stops() {
    let (_dir, root, builder) = trees("carry-plan-both");
    commit(
        &root,
        "the plan",
        &[(PLAN, &plan(&[("1", "done"), ("2", "stub")]))],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T2: built",
        &[(PLAN, &plan(&[("1", "done"), ("2", "the builder's")]))],
    );
    commit(
        &root,
        "T2 here",
        &[(PLAN, &plan(&[("1", "done"), ("2", "the clone's")]))],
    );
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(
        &err,
        "specs/451-x/plan.md (both sides changed T2's section) - nothing was resolved",
    );
}

/// A tasks.md of the open boxes named, each with its research line unless listed in `bare`.
fn boxes(ids: &[&str], bare: &[&str]) -> String {
    let mut out = "# Tasks\n\n".to_owned();
    for id in ids {
        let _ = writeln!(out, "- [ ] T{id} a task");
        if !bare.contains(id) {
            out += RESEARCH;
        }
    }
    out
}

#[test]
fn every_open_box_keeps_the_line_under_it_that_either_side_had() {
    // RED FIRST (451 T300): before `boxes::restored` the carried tasks.md leaves T2 bare. The clone's T2 lost its research line to
    // a hand resolution (seven tasks did on 2026-11-26, the conflict block ending between a box and its line); the builder's tree
    // still has it, and each side files a task after the same box, the last
    let (_dir, root, builder) = trees("carry-boxes");
    commit(
        &root,
        "the tasks",
        &[(TASKS_MD, &boxes(&["1", "2", "9"], &[]))],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T4 filed",
        &[(TASKS_MD, &boxes(&["1", "2", "9", "4"], &[]))],
    );
    commit(
        &root,
        "T3 filed",
        &[(TASKS_MD, &boxes(&["1", "2", "9", "3"], &["2"]))],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert_eq!(
        read(&root, TASKS_MD),
        boxes(&["1", "2", "9", "3", "4"], &[])
    );
    has(
        &out,
        "; resolved specs/451-x/tasks.md (both sides' list lines)\n",
    );
}

/// A request of the dated sections named.
fn request(days: &[&str]) -> String {
    let mut out = "# Request\n\nHis words.\n".to_owned();
    for day in days {
        let _ = write!(out, "\n## 2026-11-26: {day}\n\n> his words on {day}\n");
    }
    out
}

#[test]
fn a_request_both_sides_added_a_dated_section_to_keeps_both() {
    // RED FIRST (451 T300): before the request rule this carry exits 2, "not a tasks.md, plan.md or plan-review.json of a feature"
    // - the stop of T315, T293, T299 and T316's carries
    let (_dir, root, builder) = trees("carry-request");
    commit(&root, "the request", &[(REQUEST, &request(&["one"]))]);
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(&builder, "T3", &[(REQUEST, &request(&["one", "three"]))]);
    commit(&root, "T2", &[(REQUEST, &request(&["one", "two"]))]);
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(
        &out,
        "; resolved specs/451-x/request.md (both sides' dated sections)\n",
    );
    assert_eq!(read(&root, REQUEST), request(&["one", "two", "three"]));
}

#[test]
fn a_request_section_both_sides_wrote_differently_stops_and_one_both_hold_is_not_doubled() {
    let (_dir, root, builder) = trees("carry-request-same");
    commit(&root, "the request", &[(REQUEST, &request(&["one"]))]);
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T3",
        &[(REQUEST, &request(&["one", "two", "three"]))],
    );
    commit(&root, "T2", &[(REQUEST, &request(&["one", "two", "four"]))]);
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert_eq!(
        read(&root, REQUEST),
        request(&["one", "two", "four", "three"])
    );
    // the same heading over different words is a choice between the sides
    commit(
        &builder,
        "T5",
        &[(
            REQUEST,
            &(request(&["one", "two", "three", "five"]) + "more\n"),
        )],
    );
    commit(
        &root,
        "T5 here",
        &[(REQUEST, &request(&["one", "two", "four", "three", "five"]))],
    );
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(
        &err,
        "specs/451-x/request.md (both sides added one section, differently: ## 2026-11-26: five)",
    );
}

#[test]
fn sections_merged_takes_each_side_s_change_and_stops_on_a_choice() {
    let ok = |base: &str, ours: &str, theirs: &str| sections::merged(base, ours, theirs).unwrap();
    let stop =
        |base: &str, ours: &str, theirs: &str| sections::merged(base, ours, theirs).unwrap_err();
    let p = |ids: &[(&str, &str)]| plan(ids);
    let base = p(&[("1", "a"), ("2", "b"), ("3", "c")]);
    // the builder removed T2 (folded into T1, which it filled); the clone added T4 and left the rest alone
    assert_eq!(
        ok(
            &base,
            &p(&[("1", "a"), ("2", "b"), ("3", "c"), ("4", "d")]),
            &p(&[("1", "filled"), ("3", "c")])
        ),
        p(&[("1", "filled"), ("3", "c"), ("4", "d")])
    );
    // the clone changed T3 and removed T2, which the builder left alone; each side added the same T5; the builder's T6 is appended
    assert_eq!(
        ok(
            &base,
            &p(&[("1", "a"), ("3", "more"), ("5", "e")]),
            &p(&[("1", "a"), ("2", "b"), ("3", "c"), ("5", "e"), ("6", "f")])
        ),
        p(&[("1", "a"), ("3", "more"), ("5", "e"), ("6", "f")])
    );
    // both sides wrote one change; a section of several headings is one; a blank line is put before an appended section
    let headed = "# Plan\n\n### T1 (a)\n\none\n\n### T1 Approach\n\n1. same\n";
    assert_eq!(
        ok(
            headed,
            &headed.replace("one", "two"),
            &(headed.replace("one", "two") + "\n### T2\n")
        ),
        headed.replace("one", "two") + "\n### T2\n"
    );
    // the opening: the side that changed it; both the same; a plan of no opening and no section
    let top = |text: &str, to: &str| text.replace("# Plan", to);
    assert_eq!(
        ok(&base, &top(&base, "# Ours"), &base),
        top(&base, "# Ours")
    );
    assert_eq!(
        ok(&base, &base, &top(&base, "# Theirs")),
        top(&base, "# Theirs")
    );
    assert_eq!(
        ok(&base, &top(&base, "# Same"), &top(&base, "# Same")),
        top(&base, "# Same")
    );
    assert_eq!(ok("", "", "### T7\n"), "### T7\n");
    // every choice between the sides stops, named
    let one = |body: &str| p(&[("1", body), ("2", "b"), ("3", "c")]);
    let less = p(&[("2", "b"), ("3", "c")]);
    for (ours, theirs, why) in [
        (
            top(&base, "# Ours"),
            top(&base, "# Theirs"),
            "both sides changed the text before the first task's section",
        ),
        (
            one("ours"),
            one("theirs"),
            "both sides changed T1's section",
        ),
        (
            one("ours"),
            less.clone(),
            "the builder removed T1's section, which the clone changed",
        ),
        (
            less,
            one("theirs"),
            "the builder changed T1's section, which the clone removed",
        ),
        (
            base.clone() + "### T8\n\nours\n",
            base.clone() + "### T8\n\ntheirs\n",
            "both sides wrote T8's section, differently",
        ),
        (
            base.clone() + "### T1 (again)\n",
            base.clone(),
            "the clone's side holds T1's sections in two places",
        ),
        (
            base.clone(),
            base.clone() + "### T1 (again)\n",
            "the builder's side holds T1's sections in two places",
        ),
    ] {
        assert_eq!(stop(&base, &ours, &theirs), why);
    }
    assert_eq!(
        stop(&(base.clone() + "### T1 (again)\n"), &base, &base),
        "the carried commit's parent holds T1's sections in two places"
    );
}

#[test]
fn a_bare_open_box_takes_back_the_lines_a_side_holds_under_it() {
    let full = boxes(&["1", "2"], &[]);
    let physical = full.replace(RESEARCH, "      research: physical\n      - [ ] searched\n");
    // the first side's lines first; a ticked box, a box no side holds lines under and a box with its lines are left alone
    let merged =
        "- [ ] T1 a task\n- [x] T2 a task\n- [ ] T7 a task\n- [ ] T2 a task\n      its own\n";
    assert_eq!(
        lines_under::restored(merged, [&physical, &full]),
        "- [ ] T1 a task\n      research: physical\n      - [ ] searched\n- [x] T2 a task\n- [ ] T7 a task\n- [ ] T2 a task\n      its own\n"
    );
    assert_eq!(lines_under::restored(merged, ["", ""]), merged);
    // a bare box that ends the file without a line end
    assert_eq!(
        lines_under::restored("- [ ] T1 a task", ["", &full]),
        format!("- [ ] T1 a task\n{RESEARCH}")
    );
}

#[test]
fn a_tasks_git_merged_cleanly_beside_a_conflict_keeps_its_boxes_lines_too() {
    // the shape of 42444a9899 against d217a39fad's parent: the plan conflicts, the tasks merge cleanly - the clone's bare T2 kept
    // bare by git, the builder's tree holding its line - and a tasks.md with nothing to restore is left as git merged it
    let (_dir, root, builder) = trees("carry-boxes-clean");
    let other = "specs/452-y/tasks.md";
    let stubs = |ids: &[&str]| plan(&ids.iter().map(|id| (*id, "stub")).collect::<Vec<_>>());
    commit(
        &root,
        "the spec",
        &[
            (TASKS_MD, &boxes(&["1", "2", "9"], &[])),
            (other, &boxes(&["1"], &[])),
            (PLAN, &stubs(&["1", "2"])),
        ],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T4 and T5 filed",
        &[
            (TASKS_MD, &boxes(&["1", "2", "9", "4"], &[])),
            (other, &boxes(&["1", "5"], &[])),
            (PLAN, &stubs(&["1", "2", "4"])),
        ],
    );
    commit(
        &root,
        "T2 withdrawn, T3 filed",
        &[
            (TASKS_MD, &boxes(&["3", "1", "2", "9"], &["2"])),
            (PLAN, &stubs(&["1"])),
        ],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "; resolved specs/451-x/plan.md (by section), specs/451-x/tasks.md (a bare box's lines restored)\n");
    assert_eq!(
        read(&root, TASKS_MD),
        boxes(&["3", "1", "2", "9", "4"], &[])
    );
    assert_eq!(read(&root, other), boxes(&["1", "5"], &[]));
    assert_eq!(read(&root, PLAN), stubs(&["1", "4"]));
}

#[test]
fn keep_both_takes_whole_request_sections_both_sides_added() {
    let hunk = |ours: &str, theirs: &str| {
        format!("top\n<<<<<<< a\n{ours}||||||| o\n=======\n{theirs}>>>>>>> b\nend\n")
    };
    let both = |ours: &str, theirs: &str| keep_both(&hunk(ours, theirs), Kind::Request);
    // the clone's side opening without a blank line (4e198492c0 against ca16aed82a's parent), the builder's with one
    assert_eq!(
        both("## one\n\n> a\n", "\n## two\n\n> b\n"),
        Ok("top\n## one\n\n> a\n\n## two\n\n> b\nend\n".to_owned())
    );
    // each side opening with one (e00df64894 against 1783cf6eed's parent): one blank line between them, not two
    assert_eq!(
        both("\n## one\n\n> a\n", "\n## two\n\n> b\n"),
        Ok("top\n\n## one\n\n> a\n\n## two\n\n> b\nend\n".to_owned())
    );
    // prose that is no section
    assert_eq!(
        both("## one\n", "A paragraph.\n"),
        Err("an added block that is no `## ` section: A paragraph.".to_owned())
    );
    // a side of blank lines only
    assert_eq!(
        both("## one\n", "\n"),
        Ok("top\n## one\n\nend\n".to_owned())
    );
}
