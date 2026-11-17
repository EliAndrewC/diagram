//! The manifest and one URL archived (feature 449 T146), on the research crate's test record and a local archive.

use serde_json::{json, Value};

use super::{
    archive_url, capture_base, gm_copies, gm_dir, gm_table, home_of, load_row, now_iso, owed,
    place_gm, read_row, report, row_files, row_path, settle, stamp, sync_gm_copies, write_row,
};
use crate::testkit::{git, Fake, World, PDF};
use l7r_gate_research::record::archive::{url_id, Cited};

fn table(w: &World, files: &Value) {
    std::fs::write(
        w.research().join("archive/gm-copies.json"),
        json!({"files": files}).to_string(),
    )
    .unwrap();
}

#[test]
fn rows_are_sharded_read_and_written_whole() {
    let w = World::new("manifest-rows");
    let u = "https://e.org/a";
    let id = url_id(u);
    assert_eq!(
        row_path(&w.root, u),
        w.research().join(format!("archive/{}/{id}.json", &id[..2]))
    );
    assert_eq!(capture_base(u), format!("{}/{id}", &id[..2]));
    write_row(&w.root, u, &json!({"url": u, "b": [1], "a": "\u{65e5}"})).unwrap();
    assert_eq!(
        std::fs::read_to_string(row_path(&w.root, u)).unwrap(),
        format!("{{\n \"a\": \"\u{65e5}\",\n \"b\": [\n  1\n ],\n \"url\": \"{u}\"\n}}\n")
    );
    for junk in [
        "archive/zz/abc.json",
        "archive/a1/zz.json",
        "archive/a1/.a1.json",
        "archive/a1/abc.txt",
        "archive/abc/abc.json",
    ] {
        l7r_gate_research::fixture::put(&w.research(), junk, "{}");
    }
    std::fs::create_dir_all(w.research().join("archive/a1/ab.json")).unwrap();
    let rows: Vec<String> = row_files(&w.root)
        .iter()
        .map(|p| p.file_name().unwrap().to_string_lossy().into_owned())
        .collect();
    assert_eq!(
        rows,
        vec!["a1b2c3d4e5f6.json".to_owned(), format!("{id}.json")]
            .into_iter()
            .collect::<std::collections::BTreeSet<_>>()
            .into_iter()
            .collect::<Vec<_>>()
    );
    assert_eq!(read_row(&w.root, u).unwrap()["a"], "\u{65e5}");
    assert!(read_row(&w.root, "https://e.org/none").is_none());
    std::fs::write(row_path(&w.root, u), "[1]").unwrap();
    assert!(read_row(&w.root, u).is_none());
    std::fs::write(row_path(&w.root, u), "{bad").unwrap();
    assert!(read_row(&w.root, u).is_none());
    assert_eq!(
        load_row(&row_path(&w.root, u)).unwrap_err().kind,
        "JSONDecodeError"
    );
    std::fs::write(row_path(&w.root, u), b"\xff").unwrap();
    assert_eq!(
        load_row(&row_path(&w.root, u)).unwrap_err().kind,
        "UnicodeDecodeError"
    );
    assert_eq!(load_row(&w.root.join("none")).unwrap_err().kind, "OSError");
    std::fs::write(w.research().join("archive/zz-file"), "x").unwrap();
    let blocked = w.research().join("archive/zz-file/a");
    assert!(std::fs::create_dir_all(&blocked).is_err());
    let mut root2 = w.root.clone();
    root2.push("nowhere");
    std::fs::create_dir_all(root2.join("research")).unwrap();
    std::fs::write(root2.join("research/archive"), "a file").unwrap();
    assert_eq!(
        write_row(&root2, u, &json!({})).unwrap_err().kind,
        "OSError"
    );
    let row = row_path(&w.root, "https://e.org/tmp-dir");
    let tmp = row.with_file_name(format!(
        ".{}.{}.tmp",
        row.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    std::fs::create_dir_all(&tmp).unwrap();
    assert_eq!(
        write_row(&w.root, "https://e.org/tmp-dir", &json!({}))
            .unwrap_err()
            .kind,
        "OSError"
    );
    std::fs::create_dir_all(row_path(&w.root, "https://e.org/dir-row")).unwrap();
    assert_eq!(
        write_row(&w.root, "https://e.org/dir-row", &json!({}))
            .unwrap_err()
            .kind,
        "OSError"
    );
}

#[test]
fn the_gms_table_its_keys_and_a_copy_placed_once() {
    let w = World::new("manifest-gm");
    assert!(gm_table(&w.root).unwrap().is_empty());
    std::fs::write(w.research().join("archive/gm-copies.json"), "{bad").unwrap();
    assert_eq!(gm_table(&w.root).unwrap_err().kind, "JSONDecodeError");
    std::fs::write(w.research().join("archive/gm-copies.json"), "{}").unwrap();
    assert_eq!(gm_table(&w.root).unwrap_err().kind, "KeyError");
    std::fs::write(
        w.research().join("archive/gm-copies.json"),
        "{\"files\": 1}",
    )
    .unwrap();
    assert_eq!(gm_table(&w.root).unwrap_err().kind, "TypeError");
    assert!(gm_copies(&w.root).is_err());
    table(
        &w,
        &json!({"z.pdf": {"keys": ["k1", "k2"]}, "a.pdf": {"keys": ["k1"]}, "n.txt": {}}),
    );
    assert_eq!(
        gm_copies(&w.root).unwrap(),
        vec![
            (
                "k1".to_owned(),
                vec!["a.pdf".to_owned(), "z.pdf".to_owned()]
            ),
            ("k2".to_owned(), vec!["z.pdf".to_owned()])
        ]
    );
    assert!(!gm_dir().as_os_str().is_empty());
    let store = w.store();
    std::fs::write(w.gm.join("a.PDF"), PDF).unwrap();
    std::fs::write(w.gm.join("e.pdf"), b"not a pdf").unwrap();
    std::fs::create_dir_all(w.gm.join("folder")).unwrap();
    std::fs::write(w.gm.join("folder/x"), "x").unwrap();
    assert_eq!(
        place_gm(&store, "a.PDF", &json!({})).unwrap(),
        "gm-copies/a.PDF"
    );
    assert_eq!(
        std::fs::read_to_string(store.dir.join("gm-copies/a.PDF.txt")).unwrap(),
        "Hello PDF\n\u{c}"
    );
    assert_eq!(
        place_gm(&store, "a.PDF", &json!({})).unwrap(),
        "gm-copies/a.PDF"
    );
    assert_eq!(
        place_gm(&store, "e.pdf", &json!({"archived": ""})).unwrap(),
        "gm-copies/e.pdf"
    );
    assert!(!store.dir.join("gm-copies/e.pdf.txt").exists());
    assert_eq!(
        place_gm(&store, "folder", &json!({"archived": "elsewhere/folder"})).unwrap(),
        "elsewhere/folder"
    );
    assert_eq!(place_gm(&store, "missing", &json!({})).unwrap(), "");
    std::fs::write(w.gm.join("sealed.pdf"), PDF).unwrap();
    std::process::Command::new("chmod")
        .arg("000")
        .arg(w.gm.join("sealed.pdf"))
        .status()
        .unwrap();
    assert!(place_gm(&store, "sealed.pdf", &json!({})).is_err());
    std::process::Command::new("chmod")
        .arg("644")
        .arg(w.gm.join("sealed.pdf"))
        .status()
        .unwrap();
    assert_eq!(
        w.subjects()[..2],
        [
            "the GM's downloaded copy: elsewhere/folder",
            "the GM's downloaded copy: gm-copies/e.pdf"
        ]
    );
    std::fs::remove_file(store.dir.join("gm-copies/a.PDF")).unwrap();
    std::fs::create_dir_all(store.dir.join("gm-copies/a.PDF")).unwrap();
    std::fs::remove_file(w.gm.join("e.pdf")).unwrap();
    std::fs::create_dir_all(w.gm.join("e.pdf")).unwrap();
    std::fs::remove_dir_all(store.dir.join("gm-copies/e.pdf")).ok();
    std::fs::remove_file(store.dir.join("gm-copies/e.pdf")).ok();
    assert_eq!(
        place_gm(&store, "e.pdf", &json!({})).unwrap(),
        "gm-copies/e.pdf"
    );
}

#[test]
fn the_times_are_utc() {
    let s = stamp();
    assert_eq!((s.len(), &s[8..9], &s[15..]), (16, "T", "Z"));
    let i = now_iso();
    assert!(i.ends_with("+00:00") && i.len() == 25, "{i}");
    // the mirror's `.specify`, unless the variable moves it
    let home = home_of(&std::path::PathBuf::from("/m/.clones/c"));
    assert_eq!(
        home,
        std::env::var_os("L7R_SOURCES_HOME")
            .map_or_else(|| std::path::PathBuf::from("/m/.specify"), Into::into)
    );
}

#[test]
fn one_url_archived_its_capture_committed_its_gms_copies_placed_and_its_row_written() {
    let w = World::new("manifest-url");
    let store = w.store();
    let mut fake = Fake::default();
    fake.serve("https://e.org/a", 200, "text/html", b"<p>a</p>");
    fake.renders
        .insert("https://e.org/a".into(), ("M".into(), "shown".into()));
    table(&w, &json!({"g.pdf": {"keys": ["src-a"]}}));
    std::fs::write(w.gm.join("g.pdf"), b"x").unwrap();
    let who = Cited {
        keys: vec!["src-a".into()],
        notes: vec!["0001-paddies.notes.html".into()],
    };
    let row = archive_url(&w.root, "https://e.org/a).", &who, &mut fake, &store, true).unwrap();
    assert_eq!(row["outcome"], "archived");
    assert_eq!(row["gm_copies"], json!(["gm-copies/g.pdf"]));
    let path = row["path"].as_str().unwrap().to_owned();
    assert_eq!(row["first"], path.as_str());
    let capture: Value = serde_json::from_str(
        &std::fs::read_to_string(store.dir.join(&path).join("capture.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(capture["keys"], json!(["src-a"]));
    assert_eq!(
        capture.as_object().unwrap().keys().next_back().unwrap(),
        "parts"
    );
    assert_eq!(
        w.subjects()[..2],
        [
            "the GM's downloaded copy: gm-copies/g.pdf",
            "archived: https://e.org/a"
        ]
    );
    assert!(git(&w.remote, &["log", "--format=%s"]).starts_with("the GM's"));
    // again, dead now: no capture, the path and the first kept, the copies kept; the push fails, so the row waits on it
    git(
        &store.dir,
        &["remote", "set-url", "origin", "/no/such/remote.git"],
    );
    fake.gets.clear();
    let again = archive_url(
        &w.root,
        "https://e.org/a",
        &Cited::default(),
        &mut fake,
        &store,
        true,
    )
    .unwrap();
    assert_eq!(
        (again["path"].as_str(), again["first"].as_str()),
        (Some(path.as_str()), Some(path.as_str()))
    );
    assert_eq!(again["held"], "unreachable");
    assert_eq!(again["outcome"], "pending-upload");
    assert!(again["reason"]
        .as_str()
        .unwrap()
        .starts_with("push failed: "));
    assert_eq!(again["gm_copies"], json!(["gm-copies/g.pdf"]));
}

/// What was the tail of the test above, on its world: a dead page with the page cache's text, a blocked URL, a table that will not read.
/// It reads nothing the capture above wrote, so it stands apart on a world of its own - the two together were past FR-008's tenth of a
/// second (feature 449 T167).
#[test]
fn a_dead_page_keeps_the_caches_text_and_a_blocked_url_or_a_bad_table_is_refused() {
    let world = World::new("manifest-dead");
    let w = &world;
    let store = &w.store();
    let fake = &mut Fake::default();
    // unpushed, with the page cache's text kept beside a dead page
    let how = l7r_gate_research::pages::Stored {
        fetched: None,
        exact: true,
        origin: "fetch",
    };
    l7r_gate_research::pages::put(
        &store.home,
        "https://e.org/dead",
        "cached words",
        &how,
        &w.research(),
    )
    .unwrap();
    let dead = archive_url(
        &w.root,
        "https://e.org/dead",
        &Cited::default(),
        fake,
        store,
        false,
    )
    .unwrap();
    assert_eq!(dead["outcome"], "unreachable");
    let first = dead["first"].as_str().unwrap();
    assert_eq!(
        std::fs::read_to_string(store.dir.join(first).join("page-cache-text.txt")).unwrap(),
        "cached words"
    );
    assert_eq!(
        archive_url(
            &w.root,
            "https://grokipedia.com/page/Q",
            &Cited::default(),
            fake,
            store,
            true
        )
        .unwrap_err()
        .kind,
        "Blocked"
    );
    std::fs::write(w.research().join("archive/gm-copies.json"), "{").unwrap();
    assert!(archive_url(
        &w.root,
        "https://e.org/b",
        &Cited::default(),
        fake,
        store,
        true
    )
    .is_err());
}

/// The three rows the copies' sync is told to: one partial, one archived, one keyed elsewhere.
fn three_rows(w: &World) {
    write_row(&w.root, "https://e.org/a", &json!({"url": "https://e.org/a", "keys": ["src-a"], "outcome": "partial", "gm_copies": ["old"]})).unwrap();
    write_row(
        &w.root,
        "https://e.org/x",
        &json!({"url": "https://e.org/x", "keys": ["src-a", "k2"], "outcome": "archived"}),
    )
    .unwrap();
    write_row(
        &w.root,
        "https://e.org/y",
        &json!({"url": "https://e.org/y", "keys": ["other"], "outcome": "unreachable"}),
    )
    .unwrap();
}

#[test]
fn the_gms_copies_told_to_their_rows_the_held_rows_settled_and_the_coverage_reported() {
    let w = World::new("manifest-sync");
    let store = w.store();
    three_rows(&w);
    table(
        &w,
        &json!({"g.pdf": {"keys": ["src-a", "k2"]}, "h.pdf": {"keys": ["k2"]}, "gone.pdf": {"keys": ["other"]}}),
    );
    std::fs::write(w.gm.join("g.pdf"), b"x").unwrap();
    std::fs::write(w.gm.join("h.pdf"), b"y").unwrap();
    assert_eq!(sync_gm_copies(&w.root, &store).unwrap(), 3);
    let a = read_row(&w.root, "https://e.org/a").unwrap();
    assert_eq!(
        (a["outcome"].clone(), a["gm_copies"].clone()),
        (json!("archived-gm-copy"), json!(["gm-copies/g.pdf", "old"]))
    );
    assert_eq!(
        read_row(&w.root, "https://e.org/x").unwrap()["gm_copies"],
        json!(["gm-copies/g.pdf", "gm-copies/h.pdf"])
    );
    assert_eq!(
        read_row(&w.root, "https://e.org/y").unwrap()["outcome"],
        "unreachable"
    );
    assert_eq!(sync_gm_copies(&w.root, &store).unwrap(), 0);
}

/// The sync's failures - a refused push, a row with no outcome, a row that will not read - apart from the test above on a world of
/// their own holding its rows: the four syncs' pushes together were past FR-008's tenth of a second (feature 449 T167).
#[test]
fn a_sync_whose_push_is_refused_or_whose_row_will_not_read_fails() {
    let w = World::new("manifest-sync-fails");
    let store = w.store();
    three_rows(&w);
    git(
        &store.dir,
        &["remote", "set-url", "origin", "/no/such/remote.git"],
    );
    std::fs::write(w.gm.join("new.pdf"), b"z").unwrap();
    table(&w, &json!({"new.pdf": {"keys": ["src-a"]}}));
    let err = sync_gm_copies(&w.root, &store).unwrap_err();
    assert_eq!(err.kind, "RuntimeError");
    write_row(
        &w.root,
        "https://e.org/z",
        &json!({"url": "https://e.org/z", "keys": ["src-a"]}),
    )
    .unwrap();
    assert_eq!(
        sync_gm_copies(&w.root, &store).unwrap_err().message,
        "'outcome'"
    );
    std::fs::write(row_path(&w.root, "https://e.org/z"), "{").unwrap();
    assert!(sync_gm_copies(&w.root, &store).is_err());
    std::fs::remove_file(row_path(&w.root, "https://e.org/z")).unwrap();
}

/// What was the tail of the test above: the held rows settled, what is owed, and the coverage table. None of it runs git, so it stands
/// apart on a world of its own holding the row the sync left standing - the two together were past FR-008's tenth of a second
/// (feature 449 T167).
#[test]
fn the_held_rows_settled_and_the_coverage_reported() {
    let world = World::new("manifest-settle");
    let w = &world;
    write_row(
        &w.root,
        "https://e.org/y",
        &json!({"url": "https://e.org/y", "keys": ["other"], "outcome": "unreachable"}),
    )
    .unwrap();
    // held rows: one waiting with its outcome held, one waiting with none, one done
    write_row(&w.root, "https://e.org/a", &json!({"url": "https://e.org/a", "outcome": "pending-upload", "held": "archived", "reason": "push failed"})).unwrap();
    write_row(
        &w.root,
        "https://e.org/x",
        &json!({"url": "https://e.org/x", "outcome": "pending-upload", "held": ""}),
    )
    .unwrap();
    assert_eq!(settle(&w.root).unwrap(), 1);
    assert_eq!(
        read_row(&w.root, "https://e.org/a").unwrap(),
        json!({"outcome": "archived", "reason": "", "url": "https://e.org/a"})
            .as_object()
            .unwrap()
            .clone()
    );
    let owed_now: Vec<String> = owed(&w.root).unwrap().into_iter().map(|(u, _)| u).collect();
    assert!(
        owed_now.contains(&"https://github.com/x/l7r.md".to_owned())
            && !owed_now.contains(&"https://e.org/a".to_owned())
    );
    write_row(
        &w.root,
        "https://github.com/x/l7r.md",
        &json!({"url": "u", "outcome": null, "reason": 5}),
    )
    .unwrap();
    assert!(owed(&w.root)
        .unwrap()
        .iter()
        .any(|(u, _)| u == "https://github.com/x/l7r.md"));
    write_row(
        &w.root,
        "https://github.com/x/l7r.md",
        &json!({"url": "u", "outcome": "partial", "reason": 5}),
    )
    .unwrap();
    let mut out = String::new();
    assert_eq!(report(&w.root, &mut out).unwrap(), 1);
    assert!(out.starts_with("archive coverage: "), "{out}");
    assert!(out.contains("  partial     https://github.com/x/l7r.md - 5\n"));
    assert!(out.contains("  no row: "), "{out}");
    write_row(&w.root, "https://github.com/x/l7r.md", &json!({"url": "u"})).unwrap();
    assert_eq!(
        report(&w.root, &mut String::new()).unwrap_err().message,
        "'outcome'"
    );
    std::fs::write(row_path(&w.root, "https://github.com/x/l7r.md"), "{").unwrap();
    assert!(report(&w.root, &mut String::new()).is_err());
    assert!(owed(&w.root).is_err());
    assert!(settle(&w.root).is_err());
}
