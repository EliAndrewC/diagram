//! The decider on the suite's shapes (`tests/hooks/test-main-tree-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::json;

use super::{decide, judge, mirror};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn tree(tag: &str) -> (std::path::PathBuf, std::path::PathBuf) {
    crate::shared::log::quiet();
    let d = std::env::temp_dir()
        .join(format!("l7r-guard-mt-{tag}-{}", std::process::id()))
        .join("diagram");
    let _ = std::fs::remove_dir_all(&d);
    let clone = d.join(".clones/mine");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(clone.join(".git")).unwrap();
    std::fs::create_dir_all(d.join(".clones/.session-clones")).unwrap();
    std::fs::write(
        d.join(".clones/.session-clones/sid"),
        clone.to_string_lossy().as_bytes(),
    )
    .unwrap();
    (d, clone)
}

fn run(cmd: &str, dir: &Path, main: &Path, sid: &str) -> Vec<Answer> {
    let input = json!({"session_id": sid, "cwd": dir.to_string_lossy(), "tool_name": "Bash", "tool_input": {"command": cmd}});
    let mut s = Session::from_input(&input);
    s.main_seam = Some(main.to_string_lossy().into_owned());
    judge(
        &Event {
            name: "PreToolUse".to_owned(),
            input,
        },
        &s,
        Some(dir),
        "/h",
    )
}

#[test]
fn a_write_standing_in_the_mirror_is_moved_to_the_clone() {
    let (m, c) = tree("move");
    let got = run("git commit -q", &m, &m, "sid");
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == format!("cd {} && git commit -q", c.display()) && n.contains("standing in"))
    );
    assert!(run("ls", &m, &m, "sid").is_empty());
    assert!(run("", &m, &m, "sid").is_empty());
}

#[test]
fn naming_the_mirror_and_an_unresolvable_clone_are_refused() {
    let (m, _c) = tree("refuse");
    let named = run(&format!("git -C {} commit", m.display()), &m, &m, "sid");
    assert!(
        matches!(&named[..], [Answer::Refuse(w)] if w.contains("names a path inside the mirror"))
    );
    let unclaimed = run("git commit", &m, &m, "nobody");
    assert!(matches!(&unclaimed[..], [Answer::Refuse(w)] if w.contains("cannot be resolved")));
}

#[test]
fn main_tree_ok_stands_aside_with_a_reason_and_refuses_without() {
    let (m, _c) = tree("escape");
    assert!(run(
        "git commit  # MAIN_TREE_OK: render-sync by hand",
        &m,
        &m,
        "sid"
    )
    .is_empty());
    assert!(
        matches!(&run("git commit  # MAIN_TREE_OK", &m, &m, "sid")[..], [Answer::Refuse(w)] if w.contains("MAIN_TREE_OK with no reason"))
    );
}

#[test]
fn the_mirror_is_the_work_trees_top_cut_at_its_clones() {
    let (m, c) = tree("mirror");
    assert_eq!(mirror(&c.join("x")), Some(m.clone()));
    assert_eq!(mirror(&m), Some(m.clone()));
    assert_eq!(mirror(Path::new("/")), None);
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "git commit"}}),
    };
    assert!(judge(
        &none,
        &Session::from_input(&json!({})),
        Some(Path::new("/")),
        "/h"
    )
    .is_empty());
    assert!(decide(&none, &Session::from_input(&json!({}))).len() <= 1);
}
