//! A task built inside another's section: the line read, and the host found in plan.md or plan-done.md with its verdict.

use serde_json::json;

use super::{box_suffix, built_inside, built_inside_box, named, Host};
use crate::checks::scratch;
use crate::plan::sections::{digest, task_sections};
use crate::plan::template::{stubs, without_stub};

const HOST: &str = "### T10 (the host)\n\n- **Approach**: one change.\n\nBuilt here: T11 - the half it absorbed\n- Built here: T12 - a list item\nBuilt here: T13 -\n\n";

fn review_of(plan: &str, task: &str) -> serde_json::Value {
    let sec = task_sections(plan).remove(task).unwrap();
    json!({"tasks": {task: {"verdict": "CLEAR", "section_sha256": digest(sec.as_bytes())}}})
}

#[test]
fn a_built_here_line_is_its_own_line_naming_a_task_and_what() {
    let found = named(HOST);
    let ids: Vec<&str> = found.iter().map(|(_, t, _)| t.as_str()).collect();
    assert_eq!(ids, ["T11", "T12"]);
    assert_eq!(found[0].2, "the half it absorbed");
    assert_eq!(&HOST[found[0].0..found[0].0 + 11], "Built here:");
    assert!(named("it says Built here: T11 - mid-line\n").is_empty());
}

#[test]
fn the_host_is_found_with_its_verdict_wherever_its_section_stands() {
    let dir = scratch("built-inside");
    let d = dir.path();
    let stub = stubs("T11")[1].clone();
    // the stub before the host, after it, and last in the file: the host's section and its verdict are the same in each
    for plan in [
        format!("{stub}\n{HOST}### T20 (other)\n\ntext\n"),
        format!("{HOST}{stub}\n### T20 (other)\n\ntext\n"),
        format!("### T20 (other)\n\ntext\n\n{HOST}{stub}"),
    ] {
        std::fs::write(d.join("plan.md"), &plan).unwrap();
        assert_eq!(built_inside(d, "T11").map(|h| h.clear), Some(false));
        std::fs::write(
            d.join("plan-review.json"),
            review_of(&plan, "T10").to_string(),
        )
        .unwrap();
        let want = Host {
            task: "T10".to_owned(),
            what: "the half it absorbed".to_owned(),
            clear: true,
            archived: false,
        };
        assert_eq!(built_inside(d, "T11"), Some(want.clone()));
        // ...and still current once the stub is gone
        let left = without_stub(&plan, "T11").unwrap().unwrap();
        std::fs::write(d.join("plan.md"), &left).unwrap();
        assert_eq!(built_inside(d, "T11"), Some(want));
        std::fs::remove_file(d.join("plan-review.json")).unwrap();
    }
    // a task no section names, and a section naming its own task
    assert_eq!(built_inside(d, "T14"), None);
    std::fs::write(
        d.join("plan.md"),
        "### T14 (self)\n\nBuilt here: T14 - itself\n",
    )
    .unwrap();
    assert_eq!(built_inside(d, "T14"), None);
    // the host archived to plan-done.md at its tick, before this task's
    let done = format!("## archived\n\n{HOST}");
    std::fs::write(d.join("plan.md"), &stub).unwrap();
    std::fs::write(d.join("plan-done.md"), &done).unwrap();
    std::fs::write(
        d.join("plan-review.json"),
        review_of(&done, "T10").to_string(),
    )
    .unwrap();
    let host = built_inside(d, "T12").unwrap();
    assert!(host.clear && host.archived && host.task == "T10");
}

#[test]
fn a_built_inside_box_is_ticked_and_ends_with_the_tick_s_words() {
    let line = format!("- [x] T11 the half{}", box_suffix("T10"));
    assert_eq!(built_inside_box(&line), Some("T10"));
    assert_eq!(built_inside_box(&format!("{line}\n")), Some("T10"));
    assert_eq!(
        built_inside_box("- [X] T11 b built inside T9a"),
        Some("T9a")
    );
    // open, the words mid-line (a title saying them), or no id after them: none
    assert_eq!(
        built_inside_box("- [ ] T11 the half built inside T10"),
        None
    );
    assert_eq!(
        built_inside_box("- [x] T11 a task built inside T10 is refused"),
        None
    );
    assert_eq!(built_inside_box("- [x] T11 built inside another"), None);
}

/// RED FIRST: `make decide` holds each `Built here:` line to an open box with an unfilled stub, or one already ticked built inside
/// the section's own task (a section decided again).
#[test]
fn make_decide_holds_a_built_here_line_to_an_open_task_with_an_unfilled_stub() {
    let dir = scratch("built-here-decide");
    let d = dir.path();
    let section = "### T10 (host)\n\nBuilt here: T11 - one\nBuilt here: T12 - two\nBuilt here: T13 - three\nBuilt here: T14 - four\nBuilt here: T10 - self\nBuilt here: T15 - five\n";
    let tasks = "- [ ] T10 host\n- [ ] T11 open, stub\n- [ ] T12 open, filled\n- [x] T13 ticked by a landing\n";
    std::fs::write(d.join("tasks.md"), tasks).unwrap();
    std::fs::write(
        d.join("tasks-done.md"),
        format!("- [x] T15 five{}\n", box_suffix("T10")),
    )
    .unwrap();
    let plan = format!(
        "{section}\n{}\n### T12 (filled)\n\nthe wells drawn\n",
        stubs("T11")[0]
    );
    std::fs::write(d.join("plan.md"), plan).unwrap();
    let members = ["T10".to_owned()];
    let found = super::decide_findings(d, section, &members);
    let said: Vec<&str> = found.iter().map(|(_, w)| w.as_str()).collect();
    assert_eq!(said.len(), 4, "{said:?}");
    assert!(
        said[0].starts_with("T12's plan section has been filled in")
            && said[0].ends_with("'Built here: T12 - two'")
    );
    assert!(said[1].starts_with("T13 is ticked, and not built inside"));
    assert!(said[2].starts_with("T14 is no filed task"));
    assert!(said[3].starts_with("T10 is a task this section itself decides"));
    assert_eq!(
        &section[found[0].0 .0..found[0].0 .1],
        "Built here: T12 - two"
    );
    // through the lint's report, its rule said once with each finding placed
    let report = crate::plan::lint::decide_refusal(
        section,
        section,
        &crate::plan::lint::decide_findings(d, section, &members),
        None,
    );
    assert!(
        report.contains("cannot close as built inside this section")
            && report.contains("T14 is no filed task"),
        "{report}"
    );
    // T15 built inside another task: ticked, and not this one's
    assert_eq!(
        super::decide_findings(d, section, &["T20".to_owned()])
            .iter()
            .filter(|(_, w)| w.starts_with("T15"))
            .count(),
        1
    );
}
