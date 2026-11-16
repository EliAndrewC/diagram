//! The combined search (feature 449 T138).

use std::collections::BTreeSet;

use l7r_gate_archive::testkit::World;

use super::{
    files_with, fuse, load_index, meaning, render, search, seen_path, source_of, text, Hit, Index,
};
use crate::index::build;
use crate::testkit::{corpus, put, q, Fake};
use crate::{index_dir, Result};

fn hit(src: &str, rel: &str, s: i64) -> Hit {
    (src.to_owned(), rel.to_owned(), s, s + 10)
}

fn built(tag: &str) -> World {
    let w = World::new(tag);
    corpus(&w.store().dir, &w.root);
    build(
        &w.store().dir,
        &w.root,
        &mut Fake::default(),
        &[],
        0,
        (0, 0),
        &mut |_| (),
    )
    .unwrap();
    w
}

fn strings(v: &[&str]) -> Vec<String> {
    v.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn sources_and_the_fusion_of_ranks() {
    assert_eq!(source_of(&q("0101-paddy-size.html")), "record 0101");
    assert_eq!(source_of("ab/abc123/2026/text.txt"), "ab/abc123");
    assert_eq!(source_of("gm-copies/book.txt"), "gm-copies/book.txt");
    let rows = fuse(
        &[vec![
            hit("a", "a/1", 0),
            hit("a", "a/1", 20),
            hit("a", "a/1", 40),
            hit("b", "b/1", 0),
        ]],
        &[
            vec![hit("b", "b/1", 5), hit("a", "a/2", 0)],
            vec![hit("c", "c/1", 0), hit("c", "c/1", 0)],
        ],
    );
    let order: Vec<&str> = rows.iter().map(|r| r.source.as_str()).collect();
    assert_eq!(order, ["a", "b", "c"]);
    assert_eq!(rows[0].index.len(), 2);
    assert_eq!(rows[0].text, [("a/2".to_owned(), 0, 10)]);
    assert_eq!(
        rows[0].by.iter().copied().collect::<Vec<_>>(),
        ["index", "text"]
    );
    assert!((rows[0].score - (1.0 / 61.0 + 1.0 / 62.0)).abs() < 1e-15);
    assert_eq!(
        seen_path(std::path::Path::new("/h"), "a b/../é!x"),
        std::path::Path::new("/h/search-seen/a-b-..-x.json")
    );
}

#[test]
fn the_meaning_search_keeps_two_passages_of_thirty_sources() {
    let w = built("search-meaning");
    let ix = load_index(&index_dir(&w.store().dir)).unwrap();
    let mut fake = Fake::default();
    assert_eq!(meaning(&ix, &[], &mut fake, 30).unwrap().len(), 0);
    assert_eq!(
        meaning(&Index::default(), &strings(&["q"]), &mut fake, 30).unwrap(),
        [Vec::<Hit>::new()]
    );
    let lists = meaning(&ix, &strings(&["Thatched roofs", "paddy"]), &mut fake, 2).unwrap();
    assert_eq!(lists.len(), 2);
    let sources: BTreeSet<&str> = lists[0].iter().map(|h| h.0.as_str()).collect();
    assert_eq!(sources.len(), 2);
    assert!(lists[0]
        .iter()
        .all(|h| lists[0].iter().filter(|o| o.0 == h.0).count() <= 2));
    assert!(meaning(
        &ix,
        &strings(&["q"]),
        &mut Fake {
            fail: true,
            ..Fake::default()
        },
        30
    )
    .is_err());
}

#[test]
fn the_text_search_finds_files_holding_every_term() -> Result<()> {
    let w = built("search-text");
    let dir = w.store().dir;
    let got = files_with(&dir, &w.root, "TWENTY")?;
    assert_eq!(
        got.into_iter().collect::<Vec<_>>(),
        [
            "cd/cde789/20260101T000000Z/text.txt".to_owned(),
            "gm-copies/book.txt".to_owned(),
            q("0102-roofs.html")
        ]
    );
    assert!(files_with(&dir.join("none"), &w.root.join("none"), "x")?.is_empty());
    assert!(super::files_with_by("/no/such/grep", &dir, &w.root, "x")
        .unwrap_err()
        .0
        .starts_with("grep: "));
    let lists = text(
        &dir,
        &w.root,
        &[strings(&["twenty", "village"]), strings(&["Twenty"])],
    )?;
    assert_eq!(
        lists[0].iter().map(|h| h.0.as_str()).collect::<Vec<_>>(),
        ["cd/cde789", "record 0102"]
    );
    assert_eq!(lists[1].len(), 3);
    // one mention each: the sources in name order
    assert_eq!(lists[1][0].0, "cd/cde789");
    // a term the visible text lacks (in a tag only): found by grep, placed at the start
    put(
        &w.root.join(q("0103-tag.html")),
        "<p class=\"zebra\">no such word</p>",
    );
    assert_eq!(
        text(&dir, &w.root, &[strings(&["zebra"])])?[0],
        [("record 0103".into(), q("0103-tag.html"), 0, 12)]
    );
    Ok(())
}

#[test]
fn a_search_prints_record_pages_first_and_remembers_under_a_key() -> Result<()> {
    let w = built("search-all");
    let dir = w.store().dir;
    let home = w.home.clone();
    let mut fake = Fake::default();
    let q = strings(&["Thatched roofs every twenty years"]);
    let terms = vec![strings(&["twenty"])];
    let f = search(&dir, &w.root, &home, &q, &terms, &mut fake, "", (15, 5))?;
    assert!(f.rows[0].source.starts_with("record "));
    assert_eq!((f.found, f.held), (f.rows.len(), 0));
    let f = search(&dir, &w.root, &home, &q, &terms, &mut fake, "k", (1, 1))?;
    assert_eq!(f.rows.len(), 2);
    let again = search(&dir, &w.root, &home, &q, &terms, &mut fake, "k", (15, 5))?;
    assert_eq!(again.held, 2);
    let seen = std::fs::read_to_string(seen_path(&home, "k")).unwrap();
    assert!(seen.starts_with("[\"") && seen.contains("\", \""), "{seen}");
    // a stale key forgets; a broken one is refused
    let old = std::fs::File::options()
        .write(true)
        .open(seen_path(&home, "k"))
        .unwrap();
    old.set_modified(std::time::SystemTime::now() - std::time::Duration::from_secs(2 * 86_400))
        .unwrap();
    assert_eq!(
        search(&dir, &w.root, &home, &q, &terms, &mut fake, "k", (15, 5))?.held,
        0
    );
    std::fs::write(seen_path(&home, "k"), "{").unwrap();
    assert!(search(&dir, &w.root, &home, &q, &terms, &mut fake, "k", (15, 5)).is_err());
    // terms alone read no index and start no embedder
    let calls = fake.calls.borrow().len();
    search(&dir, &w.root, &home, &[], &terms, &mut fake, "", (15, 5))?;
    assert_eq!(fake.calls.borrow().len(), calls);
    std::fs::write(seen_path(&home, "k2"), "[]").unwrap();
    std::fs::set_permissions(
        seen_path(&home, "k2"),
        std::os::unix::fs::PermissionsExt::from_mode(0o000),
    )
    .unwrap();
    assert!(search(&dir, &w.root, &home, &[], &terms, &mut fake, "k2", (15, 5)).is_err());
    std::fs::create_dir_all(seen_path(&home, "k3")).unwrap();
    let refused = search(&dir, &w.root, &home, &[], &terms, &mut fake, "k3", (15, 5))
        .err()
        .unwrap();
    assert!(refused.0.contains("k3.json"), "{}", refused.0);
    std::fs::write(home.join("search-seen-file"), "").unwrap();
    assert!(search(
        &dir,
        &w.root,
        &home.join("search-seen-file"),
        &[],
        &terms,
        &mut fake,
        "k",
        (15, 5)
    )
    .is_err());
    Ok(())
}

#[test]
fn render_shows_each_source_s_passages_and_measures() -> Result<()> {
    let w = built("search-render");
    let dir = w.store().dir;
    let mut fake = Fake::default();
    let terms = vec![strings(&["charcoal"])];
    let f = search(
        &dir,
        &w.root,
        &w.home,
        &strings(&["paddy tan"]),
        &terms,
        &mut fake,
        "",
        (15, 5),
    )?;
    // the copy grown past what its passages show: its measure is shown apart
    let long = format!(
        "A copy of a book about charcoal yards{} twenty yards square fields.",
        " filler".repeat(60)
    );
    put(&dir.join("gm-copies/book.txt"), &long);
    let lines = render(&dir, &w.root, &f.rows, &strings(&["yards"]))?;
    assert_eq!(lines[0], "-- the record's pages (already answered?) --");
    assert!(lines.iter().any(|l| l == "-- the archive's sources --"));
    assert!(lines.iter().any(|l| l.starts_with(" 1. record ")));
    assert!(lines.iter().any(|l| l.starts_with("    meaning: ")));
    assert!(lines.iter().any(|l| l.starts_with("    text: ")));
    assert!(lines
        .iter()
        .any(|l| l.starts_with("    measure: gm-copies/book.txt [338:485]")));
    put(&dir.join("gm-copies/book.txt"), "");
    std::fs::remove_file(dir.join("gm-copies/book.txt")).unwrap();
    assert!(render(&dir, &w.root, &f.rows, &[]).is_err());
    Ok(())
}

#[test]
fn tied_copies_print_the_one_at_the_lowest_index() {
    // the round arbiter's ask:449-T138-ties, term 1: among exactly tied hits - one fingerprint, one vector - the copy at the lowest
    // index position prints (the shards in name order, their rows in order)
    let w = World::new("search-ties");
    let dir = w.store().dir;
    let same = "The same passage, archived three times.";
    for stamp in ["20260103T000000Z", "20260101T000000Z", "20260102T000000Z"] {
        put(&dir.join(format!("dd/ddd111/{stamp}/text.txt")), same);
    }
    build(
        &dir,
        &w.root,
        &mut Fake::default(),
        &["dd".to_owned()],
        0,
        (0, 0),
        &mut |_| (),
    )
    .unwrap();
    let ix = load_index(&index_dir(&dir)).unwrap();
    let lists = meaning(&ix, &strings(&[same]), &mut Fake::default(), 30).unwrap();
    let shown: Vec<&str> = lists[0].iter().map(|h| h.1.as_str()).collect();
    assert_eq!(
        shown,
        [
            "dd/ddd111/20260101T000000Z/text.txt",
            "dd/ddd111/20260102T000000Z/text.txt"
        ]
    );
    let hits = crate::index::find(&dir, same, &mut Fake::default(), 1).unwrap();
    assert_eq!(hits[0].1, "dd/ddd111/20260101T000000Z/text.txt");
}
