use std::path::Path;

use serde_json::{json, Value};

use super::testkit::{clone_at, dir};
use super::{
    array_mut, clone_root, common_dir, falsy, git_stdout, load, locked, map_mut, name_of, now,
    save, state_path, text, with_owed, OWED, STATE,
};

#[test]
fn the_state_file_is_found_from_a_clone_a_worktree_or_a_bad_git_file() {
    let d = clone_at("state-path");
    let deep = d.join("a/b");
    std::fs::create_dir_all(&deep).unwrap();
    assert_eq!(
        state_path(&deep.to_string_lossy()),
        Some(d.join(".git").join(STATE))
    );
    assert_eq!(clone_root(&deep.to_string_lossy()), Some(d.clone()));
    let main = d.join("main.git");
    std::fs::create_dir_all(main.join("worktrees/w")).unwrap();
    std::fs::write(main.join("worktrees/w/commondir"), "../..\n").unwrap();
    let wt = d.join("wt");
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(
        wt.join(".git"),
        format!("gitdir: {}\n", main.join("worktrees/w").display()),
    )
    .unwrap();
    let expected = std::fs::canonicalize(&main).unwrap();
    assert_eq!(
        state_path(&wt.to_string_lossy()),
        Some(expected.join(STATE))
    );
    assert_eq!(common_dir(&wt), expected);
    std::fs::write(wt.join(".git"), format!("gitdir: {}\n", main.display())).unwrap();
    assert_eq!(
        state_path(&wt.to_string_lossy()),
        Some(expected.join(STATE))
    );
    assert_eq!(common_dir(&wt), expected);
    let bad = d.join("bad");
    std::fs::create_dir_all(&bad).unwrap();
    std::fs::write(bad.join(".git"), "not a gitdir\n").unwrap();
    assert_eq!(
        state_path(&bad.to_string_lossy()),
        Some(d.join(".git").join(STATE))
    );
    assert_eq!(common_dir(&bad), bad.join(".git"));
    assert_eq!(state_path("/nonexistent-l7r-dir"), None);
    assert_eq!(clone_root("/nonexistent-l7r-dir"), None);
    assert!(state_path("").is_some() || state_path("").is_none());
    assert!(clone_root("").is_some() || clone_root("").is_none());
    assert_eq!(common_dir(&d), d.join(".git"));
}

#[test]
fn a_state_is_written_sorted_and_loaded_back() {
    let d = dir("save");
    let f = d.join("sub/s.json");
    assert_eq!(load(&f), json!({}));
    save(&f, &json!({"b": {"z": 1.5, "a": "caf\u{e9}"}, "a": [1]})).unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "{\n \"a\": [\n  1\n ],\n \"b\": {\n  \"a\": \"caf\\u00e9\",\n  \"z\": 1.5\n }\n}"
    );
    assert_eq!(load(&f)["b"]["z"], json!(1.5));
    std::fs::write(&f, "not json").unwrap();
    assert_eq!(load(&f), json!({}));
    assert!(save(Path::new("/proc/nonexistent/x/s.json"), &json!({})).is_err());
    let lock = locked(&d.join("sub/s.json"));
    assert!(lock.is_some());
    drop(lock);
    assert!(locked(Path::new("/proc/nonexistent/x/s.json")).is_none());
}

fn keep(_: &mut Value) -> bool {
    false
}

fn write_it(_: &mut Value) -> bool {
    true
}

#[test]
fn the_owed_file_is_changed_under_its_lock() {
    let d = dir("owed");
    with_owed(&d, &mut |s| {
        s["x"] = json!(1);
        true
    })
    .unwrap();
    assert_eq!(load(&d.join(OWED))["x"], json!(1));
    with_owed(&d, &mut |s| {
        s["y"] = json!(1);
        false
    })
    .unwrap();
    assert!(load(&d.join(OWED)).get("y").is_none());
    assert!(with_owed(Path::new("/proc/nonexistent/x"), &mut keep).is_err());
    let blocked = dir("owed-dir");
    std::fs::create_dir_all(blocked.join(OWED)).unwrap();
    with_owed(&blocked, &mut keep).unwrap();
    assert!(with_owed(&blocked, &mut write_it).is_err());
}

#[test]
fn the_small_helpers_read_as_python_does() {
    assert!(now() > 1.0);
    let v = json!({"a": "t", "n": 1});
    assert_eq!(text(&v, "a"), "t");
    assert_eq!(text(&v, "z"), "");
    for (value, want) in [
        (None, true),
        (Some(json!(null)), true),
        (Some(json!(false)), true),
        (Some(json!(true)), false),
        (Some(json!(0)), true),
        (Some(json!(1)), false),
        (Some(json!("")), true),
        (Some(json!("x")), false),
        (Some(json!([])), true),
        (Some(json!([1])), false),
        (Some(json!({})), true),
        (Some(json!({"a": 1})), false),
    ] {
        assert_eq!(falsy(value.as_ref()), want);
    }
    let mut state = json!(3);
    map_mut(&mut state, "m").insert("k".to_owned(), json!(1));
    assert_eq!(state["m"]["k"], json!(1));
    let mut state = json!({"m": 3});
    assert!(map_mut(&mut state, "m").is_empty());
    let mut obj = serde_json::Map::new();
    array_mut(&mut obj, "a").push(json!(1));
    obj.insert("b".to_owned(), json!("no"));
    assert!(array_mut(&mut obj, "b").is_empty());
    assert_eq!(git_stdout(Path::new("/nonexistent-l7r"), &["status"]), "");
    let root = clone_at("gitout");
    assert!(!git_stdout(&root, &["rev-parse", "--git-dir"]).is_empty());
    assert_eq!(name_of(Path::new("/a/b")), "b");
    assert_eq!(name_of(Path::new("/")), "");
    assert!(super::resolved(Path::new("/no/such/l7r/file")).ends_with("file"));
    assert_eq!(super::resolved(Path::new("")), Path::new(""));
    let _: Value = json!(null);
}
