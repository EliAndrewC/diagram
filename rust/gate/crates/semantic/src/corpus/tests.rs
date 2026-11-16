//! The corpus in the Python's order (feature 449 T138): `sorted(rglob("*.txt"))` compares paths part by part (`a/b.txt` before
//! `a-b/z.txt`), takes hidden files, links to files and folders named `*.txt`, and enters no linked folder (observed 2026-11-16 on a tree
//! of each case through `CPython` 3.14.4's `pathlib`).

use l7r_guard::shared::tempdir::TempDir;

use super::{files, groups, record_shard, text_of, File};
use crate::testkit::{put, q};

#[test]
fn the_archive_then_the_record_in_python_s_order() {
    let dir = TempDir::new("corpus");
    let a = dir.path().join("archive");
    let root = dir.path().join("repo");
    for rel in [
        "a/.a.txt",
        "a/.h/x.txt",
        "a/real/y.txt",
        "a-b/z.txt",
        "a/b.txt",
        "top.txt",
        "a/B.TXT",
        ".git/q/r.txt",
        "semantic-index/s/t.txt",
    ] {
        put(&a.join(rel), "text");
    }
    std::fs::create_dir_all(a.join("d.txt/inner")).unwrap();
    std::os::unix::fs::symlink("real", a.join("a/link")).unwrap();
    std::os::unix::fs::symlink("../top.txt", a.join("a/l.txt")).unwrap();
    put(&root.join(q("0201-x.html")), "<p>x</p>");
    put(&root.join(q("0099-y.html")), "<p>y</p>");
    put(&root.join(q("0099-y.originals.html")), "<p>o</p>");
    put(&root.join(q("notes.html")), "<p>n</p>");
    put(&root.join(q("readme.txt")), "not a page");
    let got: Vec<(String, String)> = files(&a, &root)
        .unwrap()
        .into_iter()
        .map(|f| (f.shard, f.rel))
        .collect();
    let want = [
        ("a", "a/.a.txt"),
        ("a", "a/.h/x.txt"),
        ("a", "a/b.txt"),
        ("a", "a/l.txt"),
        ("a", "a/real/y.txt"),
        ("a-b", "a-b/z.txt"),
    ];
    let mut want: Vec<(String, String)> = want.map(|(s, r)| (s.to_owned(), r.to_owned())).to_vec();
    for (s, name) in [
        ("record-00", "0099-y.html"),
        ("record-02", "0201-x.html"),
        ("record-00", "notes.html"),
    ] {
        want.push((s.to_owned(), q(name)));
    }
    assert_eq!(got, want);
    // the record's last page is a second run of `record-00`, as `groupby` makes it
    let runs: Vec<(String, usize)> = groups(files(&a, &root).unwrap())
        .into_iter()
        .map(|(s, r)| (s, r.len()))
        .collect();
    assert_eq!(runs.iter().filter(|(s, _)| s == "record-00").count(), 2);
    // no archive at all: the record alone
    assert_eq!(files(&dir.path().join("none"), &root).unwrap().len(), 3);
}

#[test]
fn a_page_s_shard_and_text() {
    assert_eq!(record_shard("1234-x.html").unwrap(), "record-12");
    assert_eq!(record_shard("12ab-x.html").unwrap(), "record-00");
    assert!(record_shard("1234abc.html")
        .unwrap_err()
        .0
        .contains("invalid literal"));
    let dir = TempDir::new("corpus-text");
    let page = dir.path().join("p.html");
    put(&page, "<p>a &amp; b</p>");
    let f = |record| File {
        shard: "s".into(),
        rel: "p".into(),
        path: page.clone(),
        record,
    };
    assert_eq!(text_of(&f(true)).unwrap(), "a & b");
    assert_eq!(text_of(&f(false)).unwrap(), "<p>a &amp; b</p>");
}
