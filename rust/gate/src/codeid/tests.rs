//! The tokenizer's shapes and the cache's rules; every tracked file against the Python is `m:t062-content-ids`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{content_ids, git_blob_id, rust_tokens, stated, Cache};

fn tokens(src: &str) -> String {
    String::from_utf8(rust_tokens(src.as_bytes()))
        .unwrap()
        .replace('\0', "|")
}

#[test]
fn comments_go_and_what_runs_stays() {
    assert_eq!(tokens("let a = 1; // gone\n"), "let|a|=|1|;");
    assert_eq!(tokens("/* a /* nested */ b */ x"), "x");
    assert_eq!(tokens("/* unclosed"), "");
    assert_eq!(tokens("/// doc\nfn f() {}"), "fn|f|(|)|{|}");
    assert_eq!(tokens("a // ends with no newline"), "a");
    assert_eq!(tokens("x\t\n y\u{1c}z"), "x|y|z");
}

#[test]
fn literals_are_whole() {
    assert_eq!(tokens(r#"s("a // b\" c")"#), r#"s|(|"a // b\" c"|)"#);
    assert_eq!(tokens(r#"b"x y""#), r#"b"x y""#);
    assert_eq!(tokens(r##"r#"a " b"# z"##), r##"r#"a " b"#|z"##);
    assert_eq!(tokens(r#"br"x" y"#), r#"br"x"|y"#);
    assert_eq!(tokens(r#"r#"open"#), r#"r#"open"#);
    assert_eq!(tokens("rx by b r"), "rx|by|b|r");
    assert_eq!(
        tokens("'a' '\\n' &'b str 'x: 1"),
        "'a'|'\\n'|&|'b|str|'x|:|1"
    );
    assert_eq!(tokens("'\\x"), "'\\x");
    assert_eq!(tokens("\"open"), "\"open");
}

#[test]
fn bytes_that_are_not_text_are_themselves() {
    assert_eq!(rust_tokens(&[0xff, 0x20]), vec![0xff, 0x20]);
    assert_eq!(
        git_blob_id(b"x\n"),
        "587be6b4c3f93f93c489c0111bba5596147a26cb"
    );
}

fn repo(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-gate-codeid-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    assert!(Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    dir
}

fn script(dir: &Path, body: &str) -> String {
    let path = dir.join("fake-python");
    std::fs::write(&path, format!("#!/bin/bash\n{body}\n")).unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}

fn file(path: &str, data: &str) -> (PathBuf, Vec<u8>) {
    (PathBuf::from(path), data.as_bytes().to_vec())
}

#[test]
fn a_rust_id_a_python_id_and_any_other_file() {
    let dir = repo("kinds");
    let python = script(
        &dir,
        "shift; shift; for f in \"$@\"; do echo \"id-of-$f\"; done",
    );
    let mut cache = Cache::at(&dir);
    let files = [
        file("a.rs", "fn f() {} // c"),
        file("b.py", "x = 1"),
        file("c.json", "{}"),
        file("d.py", "y = 2"),
    ];
    let ids = content_ids(&files, &mut cache, &python, Path::new("codeid.py")).unwrap();
    assert_eq!(ids[1], "id-of-b.py");
    assert_eq!(ids[2], git_blob_id(b"{}"));
    assert_eq!(ids[3], "id-of-d.py");
    let comment_free = content_ids(
        &[file("a.rs", "fn f() {}")],
        &mut Cache::at(&dir),
        &python,
        Path::new("c"),
    )
    .unwrap();
    assert_eq!(ids[0], comment_free[0]);
}

#[test]
fn a_kept_id_starts_nothing_and_survives_the_next_reader() {
    let dir = repo("kept");
    let count = dir.join("runs");
    let python = script(
        &dir,
        &format!(
            "echo x >> {}; shift; shift; for f in \"$@\"; do echo \"id-of-$f\"; done",
            count.display()
        ),
    );
    let files = [file("b.py", "x = 1")];
    content_ids(&files, &mut Cache::at(&dir), &python, Path::new("c")).unwrap();
    assert_eq!(
        content_ids(&files, &mut Cache::at(&dir), &python, Path::new("c")).unwrap(),
        ["id-of-b.py"]
    );
    assert_eq!(std::fs::read_to_string(&count).unwrap().lines().count(), 1);
}

#[test]
fn python_that_cannot_answer_fails_the_run_and_keeps_nothing() {
    let dir = repo("fails");
    let files = [file("b.py", "x = 1")];
    let refused = script(&dir, "echo no >&2; exit 1");
    let why = content_ids(
        &files,
        &mut Cache::at(&dir),
        &refused,
        Path::new("codeid.py"),
    )
    .unwrap_err();
    assert!(why.contains("no ids") && why.contains("no"));
    let short = script(&dir, "exit 0");
    assert!(content_ids(&files, &mut Cache::at(&dir), &short, Path::new("c")).is_err());
    assert!(content_ids(
        &files,
        &mut Cache::at(&dir),
        "/no/such/python",
        Path::new("c")
    )
    .unwrap_err()
    .contains("cannot start"));
    let good = script(&dir, "echo right");
    assert_eq!(
        content_ids(&files, &mut Cache::at(&dir), &good, Path::new("c")).unwrap(),
        ["right"]
    );
}

#[test]
fn another_writers_entries_are_kept_and_a_broken_file_is_empty() {
    let dir = repo("merge");
    let path = dir.join(".git/semantic-id-cache-2.json");
    let mut cache = Cache::at(&dir);
    std::fs::write(&path, r#"{"theirs": "1"}"#).unwrap();
    content_ids(
        &[file("a.rs", "fn f() {}")],
        &mut cache,
        "python3",
        Path::new("c"),
    )
    .unwrap();
    let kept: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    assert_eq!(kept["theirs"], "1");
    assert_eq!(kept.as_object().unwrap().len(), 2);
    std::fs::write(&path, "not json").unwrap();
    assert!(Cache::at(&dir).table.is_empty());
}

#[test]
fn no_repository_is_an_empty_cache_nothing_is_written_to() {
    let dir = std::env::temp_dir().join(format!("l7r-gate-norepo-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let mut cache = Cache::at(&dir);
    assert!(cache.path.is_none() || cache.table.is_empty());
    assert_eq!(
        content_ids(&[file("a.rs", "x")], &mut cache, "python3", Path::new("c"))
            .unwrap()
            .len(),
        1
    );
    let mut empty = Cache {
        path: Some(dir.join("no-such-dir/x.json")),
        table: std::collections::BTreeMap::new(),
        dirty: true,
    };
    empty.save();
    assert!(!dir.join("no-such-dir").exists());
}

#[test]
fn an_error_names_what_was_being_done() {
    let refused: Result<(), String> = stated(Err(std::io::Error::other("no")), "reading x");
    assert_eq!(refused, Err("reading x: no".to_owned()));
    assert_eq!(stated(Ok(1), "reading x"), Ok(1));
}
