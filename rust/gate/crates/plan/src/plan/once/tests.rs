//! RED FIRST (462 T543): `make plan-delta` reads each file once a call - plan.md, the review record, tasks.md, request.md, spec.md,
//! and every archived record, flat or in parts - where it read plan-done.md eleven times a call and plan-review.json twice.

use std::path::Path;

use serde_json::json;

use super::super::tests::{feature_at, git, repo, run};
use super::{held, read, reads};

const PLAN: &str = concat!(
    "# plan\n\n### T05 (the bath)\n\n- **Approach**: one tub by the door.\n\n### T05 Approach (checklist part A)\n\n",
    "1. **The goal.** a bath\n",
    "6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.\n",
    "\n### T06 (the well)\n\n- **Approach**: one well by the kitchen.\n\n",
    "### T06 Approach (checklist part A)\n\n1. **The goal.** a well\n",
    "6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.\n"
);
const DONE: &str = "# plan done\n\n### T01 (the gate)\n\n- **Approach**: a gate.\n\n### T01 Approach (checklist part A)\n\n1. **The goal.** a gate\n";
const BOXES: &str = "# Tasks\n\n- [ ] T05 the bath\n- [ ] T06 the well\n";
const TICKED: &str = "# Tasks done\n\n- [x] T01 the gate\n";

/// A feature whose plan's two sections changed since a commit, a block its record judged now removed, and its archive flat.
fn changed(root: &Path) -> std::path::PathBuf {
    let review = json!({"blocks": {"### T04 (the shed)": {"sha256": "0", "verdict": "CLEAR", "text": "### T04 (the shed)\n"}}, "tasks": {}});
    let dir = feature_at(root, Some(PLAN), Some(&review), "375-x");
    std::fs::write(dir.join("tasks.md"), BOXES).unwrap();
    std::fs::write(dir.join("spec.md"), "# spec\n\n**FR-001** a bath.\n").unwrap();
    std::fs::write(dir.join("plan-done.md"), DONE).unwrap();
    std::fs::write(dir.join("tasks-done.md"), TICKED).unwrap();
    git(root, &["add", "-A"]);
    git(root, &["commit", "-q", "-m", "plan"]);
    std::fs::write(
        dir.join("plan.md"),
        PLAN.replace("one tub", "two tubs")
            .replace("one well", "two wells"),
    )
    .unwrap();
    dir
}

/// Each file `make plan-delta` read through `once`, read once; plan-done's text among them.
fn read_once(root: &Path) {
    reads();
    let got = run(root, &["delta", "375"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("MODE 4"), "{}", got.stdout);
    let counted = reads();
    let archived = counted
        .keys()
        .any(|p| p.to_string_lossy().contains("plan-done"));
    assert!(archived, "{counted:?}");
    assert!(counted.values().all(|n| *n == 1), "{counted:?}");
}

#[test]
fn plan_delta_reads_each_file_once_flat_and_split() {
    let root = repo();
    let dir = changed(&root);
    read_once(&root);
    l7r_shared::speckit::archive::fold(&dir, true).unwrap();
    assert!(dir.join("archive").is_dir());
    read_once(&root);
}

#[test]
fn a_read_outside_a_hold_goes_to_disk_each_time_and_a_hold_ends_with_its_call() {
    let root = repo();
    let path = root.join("x.md");
    std::fs::write(&path, "one").unwrap();
    reads();
    assert_eq!(read(&path).as_deref(), Some("one"));
    assert_eq!(read(&path).as_deref(), Some("one"));
    assert_eq!(reads()[&path], 2);
    let inside = held(|| {
        let first = read(&path);
        std::fs::write(&path, "two").unwrap();
        (first, read(&path), read(&root.join("none.md")))
    });
    assert_eq!(
        inside,
        (Some("one".to_owned()), Some("one".to_owned()), None)
    );
    assert_eq!(reads()[&path], 1);
    assert_eq!(read(&path).as_deref(), Some("two"));
    let unwound = std::panic::catch_unwind(|| held(|| panic!("inside")));
    assert!(unwound.is_err());
    assert_eq!(read(&path).as_deref(), Some("two"));
    assert_eq!(reads()[&path], 2);
}
