//! The tokenizer's shapes and the cache's rules (a `.py` file's id its blob id since feature 449 T247).

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{content_ids, gate_tree, git_blob_id, rust_tokens, stated, Cache};

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

fn repo(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = l7r_shared::tempdir::TempDir::new(&format!("gate-codeid-{tag}"));
    assert!(Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    dir
}

fn file(path: &str, data: &str) -> (PathBuf, Vec<u8>) {
    (PathBuf::from(path), data.as_bytes().to_vec())
}

#[test]
fn a_rust_id_and_any_other_file_a_python_one_among_them() {
    let dir = repo("kinds");
    let mut cache = Cache::at(&dir);
    let files = [
        file("a.rs", "fn f() {} // c"),
        file("b.py", "\"\"\"Doc.\"\"\"\nx = 1"),
        file("c.json", "{}"),
    ];
    let ids = content_ids(&files, &mut cache);
    let python_blob = git_blob_id(b"\"\"\"Doc.\"\"\"\nx = 1");
    assert_eq!(ids[1], python_blob);
    assert_eq!(ids[2], git_blob_id(b"{}"));
    let comment_free = content_ids(&[file("a.rs", "fn f() {}")], &mut Cache::at(&dir));
    assert_eq!(ids[0], comment_free[0]);
}

#[test]
fn a_python_blob_s_kept_id_is_not_read() {
    let dir = repo("kept-py");
    let path = dir.join(".git/semantic-id-cache-2.json");
    let data = b"x = 1";
    let raw = git_blob_id(data);
    std::fs::write(&path, format!(r#"{{"{raw}": "an-ast-id"}}"#)).unwrap();
    let ids = content_ids(
        &[(PathBuf::from("b.py"), data.to_vec())],
        &mut Cache::at(&dir),
    );
    assert_eq!(ids, [raw]);
}

#[test]
fn a_kept_rust_id_survives_the_next_reader() {
    let dir = repo("kept");
    let files = [file("a.rs", "fn f() {}")];
    let first = content_ids(&files, &mut Cache::at(&dir));
    let cache = Cache::at(&dir);
    let raw = git_blob_id(b"fn f() {}");
    let kept = cache.kept(&raw).map(str::to_owned);
    assert_eq!(kept, Some(first[0].clone()));
    assert_eq!(content_ids(&files, &mut Cache::at(&dir)), first);
}

#[test]
fn another_writers_entries_are_kept_and_a_broken_file_is_empty() {
    let dir = repo("merge");
    let path = dir.join(".git/semantic-id-cache-2.json");
    let mut cache = Cache::at(&dir);
    std::fs::write(&path, r#"{"theirs": "1"}"#).unwrap();
    content_ids(&[file("a.rs", "fn f() {}")], &mut cache);
    let kept: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    assert_eq!(kept["theirs"], "1");
    assert_eq!(kept.as_object().unwrap().len(), 2);
    std::fs::write(&path, "not json").unwrap();
    assert!(Cache::at(&dir).table.is_empty());
}

#[test]
fn no_repository_is_an_empty_cache_nothing_is_written_to() {
    let dir = l7r_shared::tempdir::TempDir::new("gate-norepo");
    let mut cache = Cache::at(&dir);
    assert!(cache.path.is_none() || cache.table.is_empty());
    let ids = content_ids(&[file("a.rs", "x")], &mut cache);
    assert_eq!(ids.len(), 1);
    let mut empty = Cache {
        path: Some(dir.join("no-such-dir/x.json")),
        table: std::collections::BTreeMap::new(),
        dirty: true,
    };
    empty.save();
    assert!(!dir.join("no-such-dir").exists());
}

#[test]
fn the_gate_tree_is_the_wrapper_s_or_the_root() {
    let root = Path::new("/a/root");
    let tree = gate_tree(root);
    let expected = std::env::var_os("L7R_GATE_TREE").map_or(root.to_path_buf(), PathBuf::from);
    assert_eq!(tree, expected);
}

#[test]
fn an_error_names_what_was_being_done() {
    let refused: Result<(), String> = stated(Err(std::io::Error::other("no")), "reading x");
    assert_eq!(refused, Err("reading x: no".to_owned()));
    assert_eq!(stated(Ok(1), "reading x"), Ok(1));
}
