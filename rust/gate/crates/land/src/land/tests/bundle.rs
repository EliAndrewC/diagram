//! A BUNDLE END TO END (451 T141): three small tasks started as one (`make task-start T=T1,T2,T3`), their files judged as one task's by
//! the closing checks (`scripts/gates/closing-checks.sh`, its make a stub), their one section decided in one MODE 4 dispatch, its one
//! verdict recorded, and the three landed and ticked by one landing into the fixture's scratch origin - a landing before the verdict
//! refused on the bundle's blocks.

use std::path::Path;
use std::process::Command;

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_gate_core::write_executable;

use super::{fx, tasks, NOTE};
use crate::Reply;

const BOXES: &str = "# Tasks\n\n- [ ] T1 one\n      verify: \n- [ ] T2 two\n      verify: \n- [ ] T3 three\n      verify: \n- [ ] T4 four\n";
const TEMPLATES: &str = "# Plan\n\nThe fixture's plan.\n\n### T1 (<why>)\n\n- one\n\n### T2 (<why>)\n\n- two\n\n### T3 (<why>)\n\n- three\n\n### T4 the next\n\n- four\n";
const BUNDLE: &str = "# Plan\n\nThe fixture's plan.\n\n### T1, T2, T3 (bundle)\n\n- **Approach**: three small fixes in one pass.\n\n### T1, T2, T3 Approach (checklist part A)\n\n1. **The goal.** T1: one; T2: two; T3: three.\n\n### T4 the next\n\n- four\n";

fn plan(root: &Path, words: &[&str]) -> Reply {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    let none = |_: &[String]| Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    };
    l7r_gate_plan::plan::cli(&owned, root, &none)
}

fn verdict(root: &Path, name: &str, value: &serde_json::Value) -> String {
    let path = root.join(".git").join(name);
    std::fs::write(&path, value.to_string()).unwrap();
    path.to_string_lossy().into_owned()
}

#[test]
fn a_three_task_bundle_starts_closes_decides_and_lands_as_one() {
    let mut fx = fx("land-bundle");
    let root = fx.root.clone();
    // the feature's three small tasks as `make task-add` filed them, their templates reviewed at the plan stage
    put(&root, ".gitignore", ".specify/\n");
    put(&root, "specs/449-x/tasks.md", BOXES);
    put(&root, "specs/449-x/plan.md", TEMPLATES);
    put(
        &root,
        "specs/449-x/request.md",
        "# the request\n\n> the GM's words\n",
    );
    let whole = serde_json::json!({"plan_sha256": l7r_shared::sha256::hex(TEMPLATES.as_bytes()), "decisions": [], "verdict": "CLEAR"});
    let staged = verdict(&root, "plan.json", &whole);
    let recorded = plan(&root, &["record", "449", &staged, "--as", "spec-fidelity"]);
    assert_eq!(recorded.code, 0, "{}", recorded.stderr);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the three tasks filed"]);
    git(&root, &["push", "-q", "origin", "main"]);
    git(&root, &["fetch", "-q", "origin"]);
    // START: the bundle marked under its first task
    let start = l7r_gate_task::task_start::cli(&tasks(&["449", "T1,T2,T3"]), &root);
    assert_eq!(start.code, 0, "{}", start.stderr);
    let mark = std::fs::read_to_string(root.join(".git/active-task")).unwrap();
    assert!(
        mark.contains("\"task\": \"T1\", \"tasks\": [\"T1\", \"T2\", \"T3\"]"),
        "{mark}"
    );
    // the builder's work: the three templates made one bundle section, and each task's file
    put(&root, "specs/449-x/plan.md", BUNDLE);
    for (t, f) in [
        ("T1", "docs/one.md"),
        ("T2", "docs/two.md"),
        ("T3", "docs/three.md"),
        ("T4", "docs/four.md"),
    ] {
        put(&root, f, t);
    }
    // CLOSING CHECKS: every member's edit judged as the bundle's, the other task's file apart
    let events = root.join(".git/l7r-events");
    let now = "2099-01-01T00:00:00.000Z";
    let line = |f: &str, t: &str| {
        format!("{{\"t\":\"{now}\",\"ev\":\"PostToolUse\",\"tool\":\"Edit\",\"cat\":\"edit\",\"path\":\"{}/{f}\",\"task\":\"{t}\"}}\n", root.display())
    };
    let lines = [
        line("docs/one.md", "T1"),
        line("docs/two.md", "T2"),
        line("docs/three.md", "T3"),
        line("docs/four.md", "T4"),
    ]
    .concat();
    put(&events, "449-x.jsonl", &lines);
    let make = root.join(".git/stub-make");
    write_executable(&make, "#!/usr/bin/env bash\necho \"output of $2\"\n");
    let script =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../scripts/gates/closing-checks.sh");
    let closed = Command::new("bash")
        .arg(&script)
        .current_dir(&root)
        .env("CLOSING_MAKE", &make)
        .env("CLOSING_TASK", "T1,T2,T3")
        .env("CLOSING_FEATURE", "449")
        .env("L7R_EVENTS_DIR", &events)
        .output()
        .unwrap();
    let said = String::from_utf8_lossy(&closed.stdout).into_owned();
    assert!(closed.status.success(), "{said}");
    assert!(said.contains("judged as T1,T2,T3's"), "{said}");
    let run = std::fs::read_link(root.join(".git/closing-checks/latest")).unwrap();
    let others =
        std::fs::read_to_string(root.join(".git/closing-checks").join(run).join("others")).unwrap();
    assert_eq!(others, "docs/four.md\tT4@449-x\n");
    // the work committed but T4's, which lands later
    std::fs::remove_file(root.join("docs/four.md")).unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the bundle's work"]);
    // a landing before the bundle's verdict is refused on its blocks, nothing ticked
    let refused = fx
        .land
        .land(&root.join("specs/449-x"), &tasks(&["T1", "T2", "T3"]), NOTE);
    assert_ne!(refused, Ok(0));
    let open = std::fs::read_to_string(root.join("specs/449-x/tasks.md")).unwrap();
    assert!(open.contains("- [ ] T2 two"), "{open}");
    // DECIDE: one MODE 4 dispatch judging every task in it, and its one verdict recorded under the first task
    let decided = plan(&root, &["decide", "449", "T1,T2,T3"]);
    assert_eq!(decided.code, 0, "{}", decided.stderr);
    let dispatches = decided.stdout.matches("MODE 4: PLAN REVIEW").count();
    assert_eq!(dispatches, 1, "{}", decided.stdout);
    assert!(
        decided
            .stdout
            .contains("this one section is the plan of T1, T2, T3"),
        "{}",
        decided.stdout
    );
    let sha = plan(&root, &["section-sha", "449", "T1,T2,T3"])
        .stdout
        .trim()
        .to_owned();
    let review = serde_json::json!({"section_sha256": sha, "decisions": []});
    let file = verdict(&root, "verdict.json", &review);
    let kept = plan(
        &root,
        &["record-task", "449", "T1", &file, "--as", "spec-fidelity"],
    );
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    for t in ["T1", "T2", "T3"] {
        let stop = plan(&root, &["decided", &root.to_string_lossy(), "449-x", t]);
        assert_eq!(stop.code, 0, "{t}: {}", stop.stdout);
    }
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the bundle's verdict"]);
    // LAND: the three ticked by one landing, pushed to the scratch origin
    fx.land.said = Some(std::cell::RefCell::default());
    let landed = fx
        .land
        .land(&root.join("specs/449-x"), &tasks(&["T1", "T2", "T3"]), NOTE);
    let (out, err) = fx.said();
    assert_eq!(landed, Ok(0), "{out}{err}");
    let done = std::fs::read_to_string(root.join("specs/449-x/tasks-done.md")).unwrap();
    for t in ["- [x] T1 one", "- [x] T2 two", "- [x] T3 three"] {
        assert!(done.contains(t), "{t}: {done}");
    }
    let left = std::fs::read_to_string(root.join("specs/449-x/tasks.md")).unwrap();
    assert!(left.contains("- [ ] T4 four"), "{left}");
    assert!(
        fx.subjects().contains("449-x: T1 T2 T3 ticked (make land)"),
        "{}",
        fx.subjects()
    );
}
