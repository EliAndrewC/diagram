//! The digest index's file: what it writes it reads back, anything else it reads as nothing, and a save keeps what is on disk.

use super::super::Version;
use super::{entries, file, header, header_of, read, runs, save, unruns, Index, HEADER};
use crate::checks::scratch;
use crate::plan::sections::digests::{stamp, stamp_of, SOURCES};

fn version(text: &str) -> Version {
    Version::of(text)
}

const ONE: &str = "### T01 x\n\nsection\n\n## A\n\none\n";

fn two() -> Index {
    let mut index = Index::default();
    index.add("c1", &version(ONE));
    index.add("c2", &version("## B key\n\ntwo\n\n## A\n\none\n"));
    index.add("c3", &version("## A\n\none\n"));
    index.add("c3", &version("## Z\n"));
    index
}

#[test]
fn what_it_writes_it_reads_back_and_a_lookup_is_the_version_s_own() {
    let index = two();
    assert!(index.dirty);
    let mut back = Index::decode(&index.encode()).unwrap();
    assert!(!back.dirty);
    back.dirty = true;
    assert_eq!(back, index);
    let a = entries(&version("## A\n\none\n"));
    assert_eq!(index.entries_of(2), a);
    let (_, key, sha) = &a[0];
    assert!(index.holds(true, key, sha, 0) && index.holds(true, key, sha, 2));
    assert!(!index.holds(true, key, sha, 3) && !index.holds(false, key, sha, 0));
    assert!(!index.holds(true, "## none", sha, 0));
    assert_eq!((index.covers("c2"), index.covers("c9")), (Some(1), None));
    assert_eq!(index.last_added(), Some("c3"));
    assert!(index.encode().contains(" 0-2 ## A\n"));
    assert_eq!(runs(&[0, 1, 2, 5, 7, 8]), "0-2,5,7-8");
    assert_eq!(unruns("0-2,5,7-8", 9), Some(vec![0, 1, 2, 5, 7, 8]));
    assert_eq!(Index::default().last_added(), None);
}

#[test]
fn a_key_a_line_cannot_hold_leaves_its_commit_out() {
    let mut index = Index::default();
    let mut bad = version("## A\n");
    let (sha, text) = bad.blocks.values().next().unwrap().clone();
    bad.blocks.insert("a\nb".into(), (sha, text));
    index.add("c1", &bad);
    assert_eq!((index.covers("c1"), index.dirty), (None, false));
}

#[test]
fn anything_but_what_it_writes_is_read_as_nothing() {
    let good = two().encode();
    let h = header();
    assert!(h.starts_with(HEADER) && h.len() == HEADER.len() + 65);
    for bad in [
        String::new(),
        "l7r plan-index 0\n".to_owned(),
        format!("{HEADER} {}\n", "0".repeat(64)),
        format!("{h}\nx y\n"),
        format!("{h}\nnospace\n"),
        format!("{h}\nc c1\nc c1\n"),
        format!("{h}\nc c1\nb sha 0\n"),
        format!("{h}\nc c1\nb sha 0 k\nb sha 0 k\n"),
        format!("{h}\nc c1\nc c2\ns sha 1-0 k\n"),
        format!("{h}\nc c1\nc c2\ns sha 1,0 k\n"),
        format!("{h}\nc c1\ns sha 1 k\n"),
        format!("{h}\nc c1\ns sha x k\n"),
        format!("{h}\nc c1\ns sha 0-x k\n"),
    ] {
        assert_eq!(Index::decode(&bad), None, "{bad}");
    }
    assert!(Index::decode(&good).is_some());
    assert_eq!(
        Index::decode(&format!("{h}\nc c1\ns sha 0 \n")).map(|i| i.holds(false, "", "sha", 0)),
        Some(true)
    );
    let dir = scratch("plan-index-read");
    assert_eq!(read(&dir.join("none.idx")), Index::default());
    std::fs::write(dir.join("bad.idx"), "garbage").unwrap();
    assert_eq!(read(&dir.join("bad.idx")), Index::default());
}

#[test]
fn a_save_keeps_what_another_process_wrote_and_a_failed_write_leaves_nothing() {
    let dir = scratch("plan-index-save");
    let path = file(&dir, "specs/1-x/100%.md");
    assert_eq!(path, dir.join("plan-index/specs%2F1-x%2F100%25.md.idx"));
    let mut theirs = Index::default();
    theirs.add("c0", &version("## Q\n"));
    theirs.add("c1", &version(ONE));
    save(&path, &mut theirs, Index::default());
    assert!(!theirs.dirty);
    let mut mine = two();
    save(&path, &mut mine, read(&path));
    let back = read(&path);
    assert_eq!(back.covers("c0"), Some(3));
    assert_eq!(back.entries_of(3), entries(&version("## Q\n")));
    assert_eq!(back.entries_of(0), entries(&version(ONE)));
    // a rename onto a directory fails: the temporary file is removed and the directory kept
    let blocked = dir.join("plan-index/blocked.idx");
    std::fs::create_dir_all(blocked.join("x")).unwrap();
    save(&blocked, &mut two(), Index::default());
    let left: Vec<_> = std::fs::read_dir(dir.join("plan-index"))
        .unwrap()
        .flatten()
        .map(|e| e.file_name())
        .collect();
    assert_eq!(left.len(), 2);
    save(std::path::Path::new(""), &mut two(), Index::default());
}

/// 451 T474: the header is the stamp of the code that computes the digests, so an index written by a parser whose code differs in
/// any hashed file - though it digest the canary commit alike - reads as nothing.
#[test]
fn an_index_written_by_other_digest_code_reads_as_nothing() {
    let mut other = SOURCES;
    other[1].1 = "fn blocks() {}";
    let theirs = header_of(&stamp_of(&other, char::UNICODE_VERSION));
    assert_ne!(theirs, header());
    assert_eq!(header(), format!("{HEADER} {}", stamp()));
    let written = two().encode().replacen(header(), &theirs, 1);
    assert_eq!(Index::decode(&written), None);
    assert!(Index::decode(&two().encode()).is_some());
}
