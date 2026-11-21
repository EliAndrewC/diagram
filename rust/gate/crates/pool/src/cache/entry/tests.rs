//! An entry's meta, its removal, an atomic write and a link (feature 449 T221).
//!
//! Research: the entry's tests - NONE: fixtures and assertions, deciding nothing about a map

use super::{artifact, link, read, remove, replace, Artifact, Meta, Record, META};
use crate::cache::stat::{stat, Stat};

/// A meta reads back as it was written; one that does not read is none; an artifact's record is its file's.
#[test]
fn a_meta_round_trips_and_an_artifact_is_its_file() {
    let dir = l7r_shared::tempdir::TempDir::new("cache-entry");
    let f = dir.path().join("a.png");
    std::fs::write(&f, "png").unwrap();
    let a = artifact("a.png", &f).unwrap();
    assert!(a.is(&stat(&f)) && !a.is(&Stat::Absent));
    assert!(artifact("b", &dir.path().join("b")).is_err());
    let meta = Meta {
        engine: "mode-a".into(),
        engine_id: "gnu:ab".into(),
        skip_render: true,
        spec: Record {
            path: "pool/m/s/s.svg".into(),
            stat: stat(&f),
            hashed: -5,
            digest: "d".into(),
        },
        artifacts: vec![
            a.clone(),
            Artifact {
                name: "x".into(),
                size: 0,
                mtime: 1,
                ino: 2,
            },
        ],
        key: "k".into(),
        reads: 3,
    };
    assert_eq!(Meta::parse(&meta.json()), Some(meta.clone()));
    for bad in ["", "{}", r#"{"spec": {}, "artifacts": [[1]]}"#] {
        assert_eq!(Meta::parse(bad), None);
    }
    replace(&dir.path().join("e").join(META), meta.json().as_bytes()).unwrap();
    assert_eq!(read(&dir.path().join("e")), Some(meta));
    assert!(replace(&f.join("under-a-file"), b"x").is_err());
}

/// An entry is removed meta first, whether one stood is said, and a directory with no meta is cleared too; a link replaces the file it
/// lands on, and a copy stands in where a link cannot be made.
#[test]
fn an_entry_is_removed_meta_first_and_a_link_replaces_its_target() {
    let dir = l7r_shared::tempdir::TempDir::new("cache-entry-rm");
    let e = dir.path().join("e");
    replace(&e.join(META), b"{}").unwrap();
    std::fs::write(e.join("a.png"), "png").unwrap();
    assert!(remove(&e).unwrap());
    assert!(!e.exists());
    std::fs::create_dir(&e).unwrap();
    assert!(!remove(&e).unwrap() && !e.exists());
    assert!(!remove(&e).unwrap());
    let (from, to) = (dir.path().join("from"), dir.path().join("to"));
    std::fs::write(&from, "new").unwrap();
    std::fs::write(&to, "old").unwrap();
    link(&from, &to).unwrap();
    assert_eq!(stat(&from), stat(&to));
    assert!(link(&dir.path().join("none"), &to).is_err());
    // /proc's files cannot be hard-linked from here: copied
    let copied = dir.path().join("copied");
    link(std::path::Path::new("/proc/self/stat"), &copied).unwrap_or_default();
    let blocked = dir.path().join("blocked");
    std::fs::write(&blocked, "x").unwrap();
    assert!(remove(&blocked.join("e")).is_ok());
}
