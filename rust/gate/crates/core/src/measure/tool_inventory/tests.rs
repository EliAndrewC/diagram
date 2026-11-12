//! The inventory read from a scratch repository, and each read that fails where `tool_yield.py` raised.

use std::path::Path;

use serde_json::json;

use super::*;
use crate::checks::scratch;

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

#[test]
fn a_recipe_and_what_the_entry_targets_reach() {
    let make = "quick: lint\n\t@true\ndone: lint # note\n\t@true\nlint:\n\t@$(MAKE) --no-print-directory sub; x\nsub:\n\t@true\nx := 1\n";
    assert_eq!(
        recipe(make, "lint"),
        "lint:\n\t@$(MAKE) --no-print-directory sub; x\n"
    );
    assert_eq!(recipe(make, "nope"), "");
    let seen = reached(make);
    assert!(
        seen.contains("lint")
            && seen.contains("sub")
            && seen.contains("quick")
            && seen.contains("tick")
    );
    assert!(!seen.contains("note"));
    let names = targets_of(make);
    assert!(names.contains("lint") && !names.contains("x"));
}

#[test]
fn python_iteration_and_get_hold_their_shapes() {
    assert_eq!(py_iter(&json!([1])).unwrap(), vec![json!(1)]);
    assert_eq!(py_iter(&json!({"a": 1})).unwrap(), vec![json!("a")]);
    assert_eq!(py_iter(&json!("ab")).unwrap(), vec![json!("a"), json!("b")]);
    assert!(py_iter(&json!(3)).is_err());
    let d = json!(0);
    assert_eq!(py_get(&json!({"k": 2}), "k", &d).unwrap(), &json!(2));
    assert_eq!(py_get(&json!({}), "k", &d).unwrap(), &json!(0));
    assert!(py_get(&json!([]), "k", &d).is_err());
    assert_eq!(
        py_join(Path::new("/r"), "scripts/./x//y.py"),
        Path::new("/r/scripts/x/y.py")
    );
}

#[test]
fn the_inventory_of_a_scratch_repository() {
    let r = scratch("inventory");
    put(
        &r,
        ".claude/settings.json",
        r#"{"hooks":{"PreToolUse":[{"hooks":[{"command":"scripts/hooks/foo-hooks.sh x"}]}],"Stop":[]}}"#,
    );
    put(&r, "Makefile", "done: lint\n\t@true\nlint:\n\t@python3 scripts/tools/lint.py scripts/hooks/h.py scripts/./tools/gone.py\n");
    put(
        &r,
        "scripts/gates/a.py",
        "if __name__ == \"__main__\":\n    pass\n",
    );
    put(&r, "scripts/gates/b.py", "import x\n");
    put(&r, "scripts/gates/c.sh", "\r\n");
    put(&r, "scripts/tools/lint.py", "");
    put(&r, "scripts/hooks/h.py", "");
    put(
        &r,
        "scripts/sync-with-main.sh",
        "run scripts/tools/lint.py\n",
    );
    put(
        &r,
        "scripts/tool-registry.json",
        r#"{"tools":{"s":{"kind":"step"}}}"#,
    );
    assert_eq!(
        hook_guards(&r).unwrap().into_iter().collect::<Vec<_>>(),
        ["foo"]
    );
    let paths = check_paths(&r).unwrap();
    let rel: Vec<String> = paths
        .iter()
        .map(|p| p.strip_prefix(&*r).unwrap().display().to_string())
        .collect();
    assert_eq!(
        rel,
        [
            "scripts/gates/a.py",
            "scripts/gates/c.sh",
            "scripts/tools/lint.py"
        ]
    );
    assert!(targets(&r).unwrap().contains("lint"));
    assert!(registry(&r).unwrap().contains_key("s"));
    assert_eq!(read_lossy(&r.join("scripts/gates/c.sh")), "\n");
    assert_eq!(read_lossy(&r.join("nope")), "");
    std::fs::remove_file(r.join("scripts/tool-registry.json")).unwrap();
    assert!(registry(&r).unwrap().is_empty());
}

#[test]
fn each_read_fails_where_the_python_raised() {
    let r = scratch("inventory-bad");
    assert!(hook_guards(&r).is_err());
    assert!(targets(&r).is_err());
    assert!(check_paths(&r).is_err());
    for bad in [
        "nope",
        "[]",
        r#"{"hooks":[]}"#,
        r#"{"hooks":{"x":3}}"#,
        r#"{"hooks":{"x":["s"]}}"#,
        r#"{"hooks":{"x":[{"hooks":[{"command":1}]}]}}"#,
    ] {
        put(&r, ".claude/settings.json", bad);
        assert!(hook_guards(&r).is_err());
    }
    put(&r, "scripts/gates/a.py", "");
    std::fs::write(r.join("scripts/gates/a.py"), b"\xff").unwrap();
    assert!(check_paths(&r).is_err());
    std::fs::remove_file(r.join("scripts/gates/a.py")).unwrap();
    put(&r, "Makefile", "done:\n\t@true\n");
    std::fs::create_dir_all(r.join("rust/gate/crates/cohort/src")).unwrap();
    std::fs::write(r.join("rust/gate/crates/cohort/src/push.rs"), b"\xff").unwrap();
    assert!(check_paths(&r).is_err());
    for bad in ["nope", "[]", r#"{"tools":[]}"#] {
        put(&r, "scripts/tool-registry.json", bad);
        assert!(registry(&r).is_err());
    }
}
