//! The index built, searched and committed (feature 449 T138), on a world laid out as the real one: the record's fixture pages, the
//! archive's working copy cloned from a local bare remote.

use std::path::Path;

use l7r_gate_archive::testkit::{git, World};

use super::{build, commit, find, must_read, preview, shard_paths, text_at};
use crate::npz::read;
use crate::testkit::{corpus, put, q, Fake};
use crate::{index_dir, DIM};

/// A build's lines, unheard.
fn quiet(_: &str) {}

fn run_build(w: &World, fake: &mut Fake, only: &[&str], limit: i64) -> (Vec<String>, Vec<String>) {
    let mut said = Vec::new();
    let only: Vec<String> = only.iter().map(|s| (*s).to_owned()).collect();
    let got = build(
        &w.store().dir,
        &w.root,
        fake,
        &only,
        limit,
        (0, 0),
        &mut |l| said.push(l.to_owned()),
    )
    .unwrap();
    (got, said)
}

#[test]
fn a_build_embeds_only_what_is_new_and_writes_only_what_changed() {
    let w = World::new("sem-build");
    let dir = w.store().dir;
    corpus(&dir, &w.root);
    let mut fake = Fake::default();
    quiet("the first build");
    let (written, said) = run_build(&w, &mut fake, &[], 0);
    assert_eq!(written, ["ab", "cd", "gm-copies", "record-00", "record-01"]);
    assert_eq!(said[0], "semantic-index: ab - 2 passages, 2 embedded");
    let ab = read(&index_dir(&dir).join("ab.npz")).unwrap().unwrap();
    assert_eq!(
        (ab.dim, ab.paths[1].as_str(), ab.spans[0]),
        (DIM, "ab/abd456/20260101T000000Z/text.txt", [0, 58])
    );
    // again: nothing new, nothing written, nothing embedded
    let calls = fake.calls.borrow().len();
    assert!(run_build(&w, &mut fake, &[], 0).0.is_empty());
    assert_eq!(fake.calls.borrow().len(), calls);
    // one text changed and one added: its shard alone, its new passages alone
    put(
        &dir.join("cd/cde789/20260101T000000Z/text.txt"),
        "Thatched roofs, renewed.",
    );
    put(
        &dir.join("cd/cdf000/20260101T000000Z/text.txt"),
        "Thatched roofs, renewed.",
    );
    put(
        &dir.join("cd/cdf001/20260101T000000Z/text.txt"),
        "the same text twice",
    );
    let (written, said) = run_build(&w, &mut fake, &[], 0);
    assert_eq!(
        (written, said[0].as_str()),
        (
            vec!["cd".to_owned()],
            "semantic-index: cd - 3 passages, 3 embedded"
        )
    );
    let cd = read(&index_dir(&dir).join("cd.npz")).unwrap().unwrap();
    assert_eq!(cd.vecs[..DIM], cd.vecs[DIM..2 * DIM]);
    // one shard named, a limit, a kept passage among new ones
    put(&dir.join("ab/abe111/20260101T000000Z/text.txt"), "new");
    put(&dir.join("cd/cdf002/20260101T000000Z/text.txt"), "newer");
    assert_eq!(run_build(&w, &mut fake, &["cd"], 0).0, ["cd"]);
    assert_eq!(run_build(&w, &mut fake, &[], -1).0, ["ab"]);
}

#[test]
fn a_build_refuses_what_the_python_raised() {
    let w = World::new("sem-build-bad");
    let dir = w.store().dir;
    put(&dir.join("ee/e1/20260101T000000Z/text.txt"), " \n ");
    let mut fake = Fake::default();
    let refused = |fake: &mut Fake| {
        build(
            &dir,
            &w.root,
            fake,
            &["ee".to_owned()],
            0,
            (0, 0),
            &mut quiet,
        )
        .unwrap_err()
        .0
    };
    assert!(refused(&mut fake).contains("need at least one array"));
    put(&dir.join("ee/e1/20260101T000000Z/text.txt"), "words");
    assert!(refused(&mut Fake {
        narrow: true,
        ..Fake::default()
    })
    .contains("no 1024-long vector"));
    assert!(refused(&mut Fake {
        fail: true,
        ..Fake::default()
    })
    .contains("stand-in refused"));
    put(&index_dir(&dir).join("ee.npz"), "not a shard");
    assert!(refused(&mut fake).contains("not a zip"));
    std::fs::create_dir_all(dir.join("ee/e2/x.txt")).unwrap();
    assert!(refused(&mut fake).contains("x.txt"));
    put(&w.root.join(q("1234abc.html")), "<p>x</p>");
    assert!(build(&dir, &w.root, &mut fake, &[], 0, (0, 0), &mut quiet).is_err());
}

#[test]
fn find_returns_the_nearest_and_previews_them() {
    let w = World::new("sem-find");
    let dir = w.store().dir;
    let mut fake = Fake::default();
    assert!(find(&dir, "q", &mut fake, 10).unwrap().is_empty());
    assert!(fake.calls.borrow().is_empty());
    corpus(&dir, &w.root);
    run_build(&w, &mut fake, &[], 0);
    let text = "Thatched roofs were replaced every twenty years by the village.";
    let hits = find(&dir, text, &mut fake, 3).unwrap();
    assert_eq!(hits.len(), 3);
    assert_eq!(
        (hits[0].1.as_str(), hits[0].2, hits[0].3),
        ("cd/cde789/20260101T000000Z/text.txt", 0, 63)
    );
    assert!((hits[0].0 - 1.0).abs() < 1e-3);
    assert!(hits[0].0 >= hits[1].0 && hits[1].0 >= hits[2].0);
    let all = find(&dir, text, &mut fake, -1).unwrap();
    assert!(all.len() > 3);
    assert!(find(&dir, text, &mut fake, 0).unwrap().is_empty());
    assert_eq!(
        preview(&dir, &w.root, &hits[0].1, 0, 15, 8).unwrap(),
        "Thatched"
    );
    assert_eq!(
        preview(&dir, &w.root, &q("0102-roofs.html"), 0, 9, 240).unwrap(),
        "Roofs Tha"
    );
    assert!(text_at(&dir, &w.root, "zz/none.txt").is_err());
    assert_eq!(shard_paths(&index_dir(&dir)).len(), 5);
    std::fs::create_dir_all(index_dir(&dir).join("z.npz")).unwrap();
    assert!(must_read(&index_dir(&dir).join("z.npz"))
        .unwrap_err()
        .0
        .contains("AssertionError"));
    assert!(find(
        &dir,
        text,
        &mut Fake {
            fail: true,
            ..Fake::default()
        },
        3
    )
    .is_err());
    assert!(find(&dir, text, &mut fake, 3).is_err());
}

fn subjects(w: &World) -> Vec<String> {
    git(&w.remote, &["log", "--format=%s", "main"])
        .lines()
        .map(str::to_owned)
        .collect()
}

#[test]
fn the_shards_written_are_committed_and_pushed() {
    let w = World::new("sem-commit");
    let store = w.store();
    let mut said = Vec::new();
    let mut say = |l: &str| said.push(l.to_owned());
    assert_eq!(commit(&store, &[], &mut say).unwrap(), "");
    let shards: Vec<String> = (0..9).map(|i| format!("s{i}")).collect();
    for s in &shards {
        put(&index_dir(&store.dir).join(format!("{s}.npz")), s);
    }
    assert_eq!(commit(&store, &shards, &mut say).unwrap(), "");
    assert_eq!(
        subjects(&w)[0],
        "the semantic index (Xenova/bge-m3-int8): 9 shard(s) - s0, s1, s2, s3, s4, s5, s6, s7 ..."
    );
    // written, but the same bytes as committed: nothing to commit, nothing said
    assert_eq!(commit(&store, &["s0".to_owned()], &mut say).unwrap(), "");
    put(&index_dir(&store.dir).join("t.npz"), "t");
    std::fs::remove_dir_all(&w.remote).unwrap();
    let why = commit(&store, &["t".to_owned()], &mut say).unwrap();
    assert!(!why.is_empty());
    assert_eq!(
        said,
        [
            "semantic-index: committed and pushed".to_owned(),
            format!("semantic-index: the push failed - {why}")
        ]
    );
    // git itself refusing: the working copy gone
    std::fs::remove_dir_all(&store.dir).unwrap();
    std::fs::create_dir_all(&store.dir).unwrap();
    assert!(commit(&store, &["t".to_owned()], &mut quiet).is_err());
    let mut locked = store.clone();
    locked.home = Path::new("/proc/no/such").to_path_buf();
    assert!(commit(&locked, &["t".to_owned()], &mut quiet).is_err());
}
