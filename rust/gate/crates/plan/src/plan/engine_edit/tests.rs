//! Is this an engine edit that must wait?

use std::path::Path;

use serde_json::json;

use super::super::tests::{git, repo};
use super::cli;

fn clone_with(file: &str, text: &str) -> l7r_shared::tempdir::TempDir {
    let root = repo();
    for (path, body) in [("scripts/gates/l7r-gate.sh", "x\n"), (file, text)] {
        std::fs::create_dir_all(root.join(path).parent().unwrap()).unwrap();
        std::fs::write(root.join(path), body).unwrap();
    }
    git(&root, &["add", "-A"]);
    root
}

fn ask(root: &Path, path: &Path, tool: &str, input: &serde_json::Value) -> i32 {
    let question =
        json!({"root": root, "path": path, "tool": tool, "tool_input": input}).to_string();
    cli(&mut question.as_bytes()).code
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

/// A `.py` engine file's docstring edit waits since feature 449 T247: the semantic id that let it pass (the GM, 2026-10-27) was
/// `codeid.py`'s, deleted with the last `.py` file (`ask:449-T158-codeid`); a Rust file's comment edit waited before and waits now.
#[test]
fn a_docstring_edit_waits_as_a_code_change_does() {
    let root = clone_with("l7r/diagram/a.py", "\"\"\"Doc.\"\"\"\nX = 1\n");
    let path = root.join("l7r/diagram/a.py");
    let docstring = ask(
        &root,
        &path,
        "Edit",
        &json!({"old_string": "Doc.", "new_string": "Words."}),
    );
    assert_eq!(docstring, 0);
    let code = ask(
        &root,
        &path,
        "Edit",
        &json!({"old_string": "X = 1", "new_string": "X = 2"}),
    );
    assert_eq!(code, 0);
    let rust = clone_with("rust/phases/src/a.rs", "/// Doc.\npub fn f() {}\n");
    let comment = ask(
        &rust,
        &rust.join("rust/phases/src/a.rs"),
        "Edit",
        &json!({"old_string": "Doc.", "new_string": "Words."}),
    );
    assert_eq!(comment, 0);
}

#[test]
fn a_path_that_does_not_exist_is_resolved_as_far_as_it_goes() {
    assert_eq!(
        super::real(Path::new("no/such/path")),
        Path::new("no/such/path")
    );
    assert!(super::real(Path::new("/tmp/no/such")).ends_with("no/such"));
}
