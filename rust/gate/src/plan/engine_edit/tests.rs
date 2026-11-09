//! Is this an engine edit that must wait?

use std::path::Path;

use serde_json::json;

use super::super::tests::{git, repo};
use super::cli;

fn clone_with(file: &str, text: &str) -> std::path::PathBuf {
    let root = repo();
    for (path, body) in [("l7r/diagram/ci/delta.py", "x\n"), (file, text)] {
        std::fs::create_dir_all(root.join(path).parent().unwrap()).unwrap();
        std::fs::write(root.join(path), body).unwrap();
    }
    git(&root, &["add", "-A"]);
    root
}

fn ask(root: &Path, path: &Path, tool: &str, input: &serde_json::Value) -> i32 {
    let question =
        json!({"root": root, "path": path, "tool": tool, "tool_input": input}).to_string();
    cli(&mut question.as_bytes(), "python3").code
}

#[test]
fn an_engine_edit_waits_and_anything_else_passes() {
    let root = clone_with("l7r/diagram/a.py", "X = 1\n");
    let path = root.join("l7r/diagram/a.py");
    assert_eq!(ask(&root, &path, "NotebookEdit", &json!({})), 0);
    let other = root.join("docs.md");
    std::fs::write(&other, "x").unwrap();
    assert_eq!(ask(&root, &other, "Edit", &json!({})), 1);
    assert_eq!(
        ask(&root, Path::new("/etc/hostname"), "Edit", &json!({})),
        1
    );
}

#[test]
fn a_tree_that_is_not_the_diagram_is_not_this_guard_s() {
    let root = repo();
    std::fs::create_dir_all(root.join("l7r")).unwrap();
    std::fs::write(root.join("l7r/a.py"), "x").unwrap();
    assert_eq!(ask(&root, &root.join("l7r/a.py"), "Edit", &json!({})), 1);
}

#[test]
fn an_edit_that_cannot_be_applied_or_a_file_that_cannot_be_read_waits() {
    let root = clone_with("l7r/diagram/a.py", "X = 1\n");
    let path = root.join("l7r/diagram/a.py");
    assert_eq!(
        ask(
            &root,
            &path,
            "Edit",
            &json!({"old_string": "no such text", "new_string": "y"})
        ),
        0
    );
    assert_eq!(
        ask(
            &root,
            &root.join("l7r/diagram/missing.py"),
            "Write",
            &json!({"content": "y"})
        ),
        0
    );
}

#[test]
fn the_edit_applied_once_or_everywhere() {
    let edited =
        |tool, input| super::edited(b"a a", tool, &input).map(|b| String::from_utf8(b).unwrap());
    assert_eq!(
        edited("Edit", json!({"old_string": "a", "new_string": "b"})).as_deref(),
        Some("b a")
    );
    assert_eq!(
        edited(
            "Edit",
            json!({"old_string": "a", "new_string": "b", "replace_all": true})
        )
        .as_deref(),
        Some("b b")
    );
    assert_eq!(
        edited("Write", json!({"content": "c"})).as_deref(),
        Some("c")
    );
}

#[test]
fn only_a_docstring_changed_passes_and_a_code_change_waits() {
    let root = clone_with("l7r/diagram/a.py", "\"\"\"Doc.\"\"\"\nX = 1\n");
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    std::env::set_var("L7R_GATE_TREE", &tree);
    let path = root.join("l7r/diagram/a.py");
    assert_eq!(
        ask(
            &root,
            &path,
            "Edit",
            &json!({"old_string": "Doc.", "new_string": "Words."})
        ),
        1
    );
    assert_eq!(
        ask(
            &root,
            &path,
            "Edit",
            &json!({"old_string": "X = 1", "new_string": "X = 2"})
        ),
        0
    );
}

#[test]
fn an_area_hashed_by_its_bytes_always_waits_and_an_unreadable_id_waits() {
    assert_eq!(
        super::semantic(
            b"x = 1
",
            Path::new("/no/such"),
            "/no/such/python"
        ),
        None
    );
    let root = clone_with(
        "l7r/diagram/interactive/classes/a.py",
        "\"\"\"Doc.\"\"\"\nX = 1\n",
    );
    let path = root.join("l7r/diagram/interactive/classes/a.py");
    assert!(crate::stamp::in_raw_area(
        &root,
        "l7r/diagram/interactive/classes/a.py"
    ));
    assert_eq!(
        ask(
            &root,
            &path,
            "Edit",
            &json!({"old_string": "Doc.", "new_string": "Words."})
        ),
        0
    );
}

#[test]
fn a_path_that_does_not_exist_is_resolved_as_far_as_it_goes() {
    assert_eq!(
        super::real(Path::new("no/such/path")),
        Path::new("no/such/path")
    );
    assert!(super::real(Path::new("/tmp/no/such")).ends_with("no/such"));
}
