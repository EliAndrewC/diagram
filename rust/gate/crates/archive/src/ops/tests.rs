//! The archive's housekeeping and lookups (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record), on the research crate's test
//! record and a local archive.

use std::path::Path;

use serde_json::{json, Value};

use super::*;
use crate::testkit::{git, Fake, World, PDF};

/// The world, its one fixture row given the URL every reader of the rows needs.
fn world(tag: &str) -> World {
    let w = World::new(tag);
    put(
        &w,
        "archive/a1/a1b2c3d4e5f6.json",
        r#"{"url": "https://e.org/a", "outcome": "archived", "keys": ["src-a"], "path": "a1/x"}"#,
    );
    w
}

fn put(w: &World, rel: &str, text: &str) {
    l7r_gate_research::fixture::put(&w.research(), rel, text);
}

fn table(w: &World, files: &Value) {
    put(
        w,
        "archive/gm-copies.json",
        &json!({"_about": "x", "files": files}).to_string(),
    );
}

fn s(list: &[&str]) -> Vec<String> {
    list.iter().map(|a| (*a).to_owned()).collect()
}

#[test]
fn a_lines_fields_read_as_pythons_subscript_and_get() {
    assert_eq!(field(&json!({"url": "u"}), "url").unwrap(), "u");
    assert_eq!(field(&json!({}), "url").unwrap_err().message, "'url'");
    assert_eq!(field(&json!([1]), "url").unwrap_err().kind, "TypeError");
    assert_eq!(
        field(&json!("s"), "url").unwrap_err().message,
        "string indices must be integers, not 'str'"
    );
    assert_eq!(
        field(&json!(3), "url").unwrap_err().message,
        "'int' object is not subscriptable"
    );
    assert_eq!(get_text(&json!({"a": 1}), "a").unwrap(), "1");
    assert_eq!(get_text(&json!({}), "a").unwrap(), "");
    assert_eq!(
        get_text(&json!([]), "a").unwrap_err().message,
        "'list' object has no attribute 'get'"
    );
}

#[test]
fn numbers_and_ids_read_as_python_reads_them() {
    assert_eq!(
        (
            decimal('7'),
            decimal('\u{661}'),
            decimal('\u{116da}'),
            decimal('x')
        ),
        (Some(7), Some(1), Some(0), None)
    );
    for (text, want) in [
        (" 12 ", Some(12)),
        ("+3", Some(3)),
        ("-4", Some(-4)),
        ("1_000", Some(1000)),
        ("\u{661}\u{662}", Some(12)),
    ] {
        assert_eq!(py_int(text), want, "{text}");
    }
    for bad in ["", "-", "_1", "1_", "1__0", "x", "1.5"] {
        assert_eq!(py_int(bad), None, "{bad}");
    }
    assert_eq!(py_int("99999999999999999999999"), Some(i64::MAX));
    assert_eq!(
        (
            entry_id("#17"),
            entry_id("H3"),
            entry_id("#H3"),
            entry_id("17")
        ),
        (Some("17"), Some("H3"), Some("H3"), Some("17"))
    );
    for bad in ["#", "H", "#x", "h3", "1a"] {
        assert_eq!(entry_id(bad), None, "{bad}");
    }
    let xs = [1, 2, 3];
    assert_eq!(
        (head(&xs, 2), head(&xs, -1), head(&xs, -9), head(&xs, 9)),
        (vec![1, 2], vec![1, 2], vec![], vec![1, 2, 3])
    );
}

#[test]
fn the_gms_table_is_written_whole_its_other_fields_kept() {
    let w = world("ops-table");
    std::fs::remove_file(w.research().join("archive/gm-copies.json")).ok();
    let mut t = Map::new();
    t.insert("b.pdf".into(), json!({"keys": []}));
    t.insert("a.pdf".into(), json!({"keys": ["k"]}));
    write_table(&w.root, &t).unwrap();
    let path = w.research().join("archive/gm-copies.json");
    assert_eq!(
        std::fs::read_to_string(&path).unwrap(),
        "{\n \"_about\": \"Feature 309: the GM's downloaded files.\",\n \"files\": {\n  \"a.pdf\": {\n   \"keys\": [\n    \"k\"\n   ]\n  },\n  \
         \"b.pdf\": {\n   \"keys\": []\n  }\n }\n}\n"
    );
    std::fs::write(&path, r#"{"files": {}, "z": 1}"#).unwrap();
    write_table(&w.root, &Map::new()).unwrap();
    assert_eq!(
        std::fs::read_to_string(&path).unwrap(),
        "{\n \"files\": {},\n \"z\": 1\n}\n"
    );
    std::fs::write(&path, "[1]").unwrap();
    assert_eq!(write_table(&w.root, &t).unwrap_err().kind, "TypeError");
    std::fs::write(&path, "{").unwrap();
    assert_eq!(
        write_table(&w.root, &t).unwrap_err().kind,
        "JSONDecodeError"
    );
    std::fs::remove_file(&path).unwrap();
    std::fs::write(w.research().join("archive/x"), "").unwrap();
    std::fs::rename(
        w.research().join("archive"),
        w.research().join("archive-moved"),
    )
    .unwrap();
    std::fs::write(
        w.research().join("archive"),
        "a file where the directory goes",
    )
    .unwrap();
    assert_eq!(write_table(&w.root, &t).unwrap_err().kind, "OSError");
}

#[test]
fn too_big_names_each_file_over_githubs_limit() {
    let w = world("ops-big");
    let big = w.gm.join("big.pdf");
    std::fs::File::create(&big)
        .unwrap()
        .set_len(GITHUB_FILE_LIMIT + 5 * 1024 * 1024)
        .unwrap();
    assert_eq!(too_big(&big), ["big.pdf (105 MB)"]);
    let folder = w.gm.join("folder");
    std::fs::create_dir_all(folder.join("sub")).unwrap();
    std::fs::write(folder.join("small.txt"), "x").unwrap();
    std::fs::File::create(folder.join("sub/huge.bin"))
        .unwrap()
        .set_len(GITHUB_FILE_LIMIT + 1)
        .unwrap();
    std::os::unix::fs::symlink(&folder, folder.join("loop")).unwrap();
    assert_eq!(too_big(&folder), ["huge.bin (100 MB)"]);
    assert!(too_big(&w.gm.join("nothing")).is_empty());
    let line = refused_line("big.pdf", &too_big(&big), &big);
    assert!(line.starts_with("  REFUSED big.pdf: over GitHub's 100 MB file limit (big.pdf (105 MB)), so it is not archived - split the PDF into at least 2 parts"));
    assert!(line.ends_with("then delete the original; it stays in the inbox"));
    std::fs::File::create(&big)
        .unwrap()
        .set_len(433 * 1024 * 1024)
        .unwrap();
    assert!(refused_line("big.pdf", &[], &big).contains("at least 5 parts"));
    assert!(refused_line("folder", &[], &folder).contains("at least 2 parts"));
}

/// The download list and the access states `entry_keys_of` reads, with entry 3 naming no key.
fn download_list(w: &World) {
    put(
        w,
        "source-access.json",
        r#"{"states": [{"id": "open"}], "recorded": {}}"#,
    );
    put(w, "to-download.md", "# T\n\n### 3. A book\n\n- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found\n");
}

#[test]
fn matches_resolve_keys_and_download_list_entries() {
    let w = world("ops-match");
    let refused = resolve_matches(&w.root, &s(&["f=#3"])).unwrap_err();
    assert!(refused.starts_with("access-tags: REFUSED - "), "{refused}");
    download_list(&w);
    let m = resolve_matches(
        &w.root,
        &s(&[
            "d.pdf=#3",
            "a.pdf=k1,,k2",
            "noequals",
            "b.pdf= #3 ",
            "a.pdf=k3",
            "c.pdf=H3x",
        ]),
    )
    .unwrap();
    assert_eq!(
        m.keys,
        [
            ("d.pdf".to_owned(), vec![]),
            ("a.pdf".to_owned(), s(&["k3"])),
            ("b.pdf".to_owned(), vec![]),
            ("c.pdf".to_owned(), s(&["H3x"]))
        ]
    );
    assert_eq!(
        m.downloads,
        [
            ("d.pdf".to_owned(), "3".to_owned()),
            ("b.pdf".to_owned(), "3".to_owned())
        ]
    );
    assert_eq!(
        resolve_matches(&w.root, &s(&["f=#9"])).unwrap_err(),
        "archive: no download-list entry 9 in research/to-download.md"
    );
    let mut t = Map::new();
    t.insert("n".into(), json!("not a mapping"));
    assert_eq!(
        entry_mut(&mut t, "n", json!({})).unwrap_err().message,
        "'str' object does not support item assignment"
    );
}

#[test]
fn the_inbox_archives_confirms_and_removes_what_it_places() {
    let w = world("ops-inbox");
    table(
        &w,
        &json!({"old.pdf": {"keys": ["src-a"], "evidence": "e"}}),
    );
    std::fs::write(w.gm.join("old.pdf"), PDF).unwrap();
    std::fs::write(w.gm.join("new.txt"), "a new download").unwrap();
    std::fs::write(w.gm.join("none.txt"), "copies nothing").unwrap();
    std::fs::create_dir_all(w.gm.join("folder")).unwrap();
    std::fs::write(w.gm.join("folder/a.txt"), "a").unwrap();
    std::fs::write(w.gm.join(".hidden"), "x").unwrap();
    std::fs::write(w.gm.join("TO-DOWNLOAD.md"), "the GM's list").unwrap();
    std::fs::File::create(w.gm.join("huge.pdf"))
        .unwrap()
        .set_len(GITHUB_FILE_LIMIT + 1)
        .unwrap();
    let mut m = Matched {
        downloads: vec![("none.txt".into(), "3".into())],
        ..Matched::default()
    };
    m.set("none.txt", vec![]);
    m.set("folder", s(&["k"]));
    m.set("huge.pdf", s(&["k"]));
    let mut out = String::new();
    inbox(&w.root, &w.store(), &m, &mut out).unwrap();
    assert_eq!(
        out,
        format!(
            "archive: 3 inbox file(s) archived, pushed and removed from {}\n  folder -> gm-copies/folder\n  none.txt -> gm-copies/none.txt\n  \
             old.pdf -> gm-copies/old.pdf\n{}\n  WAITING new.txt: a new download - read its first page, find the source it copies, then `make \
             archive-inbox MATCH='new.txt=<key>'` - or MATCH='new.txt=#<id>' for the download-list entry it answers (feature 313), or \
             NONE='new.txt' if it copies no cited source\n",
            w.gm.display(),
            refused_line("huge.pdf", &too_big(&w.gm.join("huge.pdf")), &w.gm.join("huge.pdf"))
        )
    );
    for gone in ["old.pdf", "none.txt", "folder"] {
        assert!(!w.gm.join(gone).exists(), "{gone}");
    }
    assert!(w.gm.join("new.txt").exists() && w.gm.join(".hidden").exists());
    let t = gm_table(&w.root).unwrap();
    assert_eq!(
        t["none.txt"],
        json!({"evidence": "matched by the session at the inbox (feature 309 FR-012)", "keys": [], "download": "3", "archived": "gm-copies/none.txt"})
    );
    assert_eq!(t["huge.pdf"]["keys"], json!(["k"]));
    // a matched entry over GitHub's limit is placed by neither the inbox nor the copies' sync (feature 449 T160)
    assert!(!w.store().dir.join("gm-copies/huge.pdf").exists());
    assert!(w.gm.join("huge.pdf").exists());
}

/// Split from the test above (feature 449 T160: the two took 2.5 s, most of it the over-limit copy the sync placed): the inbox's
/// refusals, on a world of their own whose archive is cloned first, as the placing above left it.
#[test]
fn a_refused_push_deletes_nothing_and_a_table_entry_that_is_no_mapping_is_refused() {
    let w = world("ops-inbox-refused");
    std::fs::write(w.gm.join("new.txt"), "a new download").unwrap();
    // nothing placed: no lock, no push
    let mut out = String::new();
    inbox(&w.root, &w.store(), &Matched::default(), &mut out).unwrap();
    assert!(out.starts_with("archive: 0 inbox file(s)"));
    // no inbox at all
    let mut gone = w.store();
    gone.gm = w.gm.join("no-such");
    assert_eq!(
        process_inbox(&w.root, &gone, &Matched::default()).unwrap(),
        (vec![], vec![])
    );
    w.store().ensure().unwrap();
    // a refused push deletes nothing, the table written first
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", "/no/such.git"],
    );
    let mut m = Matched::default();
    m.set("new.txt", vec![]);
    let e = process_inbox(&w.root, &w.store(), &m).unwrap_err();
    assert_eq!(e.kind, "RuntimeError");
    assert!(e.message.starts_with(
        "the inbox is archived locally but the push failed, so nothing was deleted: "
    ));
    assert!(w.gm.join("new.txt").exists());
    assert_eq!(
        gm_table(&w.root).unwrap()["new.txt"]["archived"],
        "gm-copies/new.txt"
    );
    // a table entry that is no mapping
    let mut bad = Matched::default();
    bad.downloads.push(("x".into(), "1".into()));
    table(&w, &json!({"x": 5}));
    assert_eq!(
        process_inbox(&w.root, &w.store(), &bad).unwrap_err().kind,
        "TypeError"
    );
    std::fs::write(w.gm.join("y.txt"), "y").unwrap();
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", &w.remote.to_string_lossy()],
    );
    // a name the table places that is no longer there (a link to nothing): nothing placed for it
    std::os::unix::fs::symlink(w.gm.join("gone-away"), w.gm.join("dangling")).unwrap();
    table(&w, &json!({"dangling": {"keys": []}}));
    let (placed, _) = process_inbox(&w.root, &w.store(), &Matched::default()).unwrap();
    assert!(placed.is_empty());
    std::fs::remove_file(w.gm.join("dangling")).unwrap();
    table(&w, &json!({"y.txt": 5}));
    assert_eq!(
        process_inbox(&w.root, &w.store(), &Matched::default())
            .unwrap_err()
            .message,
        "'int' object does not support item assignment"
    );
    let mut bad = Matched::default();
    bad.set("x", vec![]);
    assert_eq!(
        inbox(&w.root, &w.store(), &bad, &mut String::new())
            .unwrap_err()
            .kind,
        "TypeError"
    );
}

#[test]
fn an_entry_placed_but_not_on_github_stays_and_a_removal_that_fails_is_its_error() {
    let w = world("ops-inbox-stay");
    std::fs::write(w.gm.join("a.txt"), "a").unwrap();
    let mut m = Matched::default();
    m.set("a.txt", vec![]);
    // a push with nothing to push leaves origin/main without the file only where the copy never pushed: a working copy with no remote
    // branch tracking it
    let store = w.store();
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", &w.remote.to_string_lossy()],
    );
    let (placed, _) = process_inbox(&w.root, &store, &m).unwrap();
    assert_eq!(placed.len(), 1);
    assert!(!w.gm.join("a.txt").exists());
    assert!(on_github(&store, "gm-copies/a.txt").unwrap());
    assert!(!on_github(&store, "gm-copies/none.txt").unwrap());
    // a file the archive holds that will not leave the inbox: its folder read-only
    let ro = w.gm.join("ro");
    std::fs::create_dir_all(&ro).unwrap();
    std::fs::write(ro.join("f.txt"), "f").unwrap();
    let mut m = Matched::default();
    m.set("ro", vec![]);
    let mode = |p: &Path, m: u32| {
        std::fs::set_permissions(p, std::os::unix::fs::PermissionsExt::from_mode(m)).unwrap();
    };
    mode(&ro, 0o500);
    let e = process_inbox(&w.root, &store, &m);
    mode(&ro, 0o700);
    assert_eq!(e.unwrap_err().kind, "OSError");
}

#[test]
fn the_urls_read_the_kept_pages_and_what_has_no_row() {
    let w = world("ops-urls");
    let home = w.home.clone();
    std::fs::write(
        home.join("sources-consulted.jsonl"),
        [
            json!({"url": "b.org/x", "raw": "https://www.b.org/x#frag"}),
            json!({"url": "c.org/y", "raw": "c.org/y"}),
            json!({"url": "e.org/a", "raw": "https://e.org/a"}),
            json!({"url": ""}),
        ]
        .iter()
        .map(|r| r.to_string() + "\n")
        .collect::<String>(),
    )
    .unwrap();
    let how = l7r_gate_research::pages::Stored {
        fetched: None,
        exact: true,
        origin: "fetch",
    };
    l7r_gate_research::pages::put(&home, "https://www.b.org/x", "t", &how, &w.research()).unwrap();
    l7r_gate_research::pages::put(&home, "ftp://d.org/z", "t", &how, &w.research()).unwrap();
    std::fs::create_dir_all(home.join("page-cache/00/no-meta")).unwrap();
    assert_eq!(
        consulted_urls(&w.root).unwrap(),
        s(&["https://c.org/y", "https://www.b.org/x"])
    );
    std::fs::write(home.join("sources-consulted.jsonl"), "[1]\n").unwrap();
    assert_eq!(consulted_urls(&w.root).unwrap_err().kind, "AttributeError");
    let meta = l7r_gate_research::pages::entry_dir(&home, "https://www.b.org/x").join("meta.json");
    std::fs::write(&meta, "[]").unwrap();
    assert_eq!(consulted_urls(&w.root).unwrap_err().kind, "AttributeError");
    put(&w, "archive/a1/a1b2c3d4e5f6.json", "{}");
    assert_eq!(consulted_urls(&w.root).unwrap_err().kind, "KeyError");
    assert_eq!(
        unarchived(&w.root, &s(&["x"])).unwrap_err().kind,
        "KeyError"
    );
}

#[test]
fn kept_pages_with_no_row_are_the_only_ones_consulted_archives() {
    let w = world("ops-kept");
    l7r_gate_research::fixture::put(
        &w.root,
        KEPT,
        &(json!({"url": "k.org/1", "raw": "https://k.org/1"}).to_string() + "\n"),
    );
    put(
        &w,
        "sources/040-uncited-works/0100-u.html",
        "<p>(https://u.org/2) and https://e.org/a</p>",
    );
    assert_eq!(
        kept_urls(&w.root).unwrap(),
        s(&["https://k.org/1", "https://u.org/2)", "https://e.org/a"])
    );
    let todo = kept_only(
        &w.root,
        &s(&[
            "https://k.org/1",
            "https://k.org/1#x",
            "https://other.org/3",
            "https://e.org/a",
            "ftp://k.org/1",
        ]),
    )
    .unwrap();
    assert_eq!(todo, s(&["https://k.org/1"]));
    assert_eq!(
        unarchived(&w.root, &s(&["https://u.org/2).", "https://u.org/2"])).unwrap(),
        s(&["https://u.org/2"])
    );
    std::fs::write(
        w.research().join("sources/040-uncited-works/0200-bad.html"),
        [0xff],
    )
    .unwrap();
    assert_eq!(kept_urls(&w.root).unwrap_err().kind, "UnicodeDecodeError");
    l7r_gate_research::fixture::put(&w.root, KEPT, "{}\n");
    assert_eq!(kept_urls(&w.root).unwrap_err().kind, "KeyError");
    assert_eq!(read_text(&w.root.join("nope")).unwrap_err().kind, "OSError");
    assert!(html_files(&w.root.join("nope")).is_empty());
}

#[expect(
    clippy::unnecessary_wraps,
    reason = "a browser's start, as the lanes take it: this one always starts"
)]
fn browser(_: &Path) -> crate::Result<Box<dyn crate::fetch::Client>> {
    let mut fake = Fake::default();
    for u in ["https://k.org/1", "https://k.org/2", "https://j.org/3"] {
        fake.serve(u, 200, "text/plain", b"a kept page");
    }
    Ok(Box::new(fake))
}

fn no_browser(_: &Path) -> crate::Result<Box<dyn crate::fetch::Client>> {
    Err(Error::new("Error", "BrowserType.launch: none"))
}

#[test]
fn consulted_archives_the_kept_pages_in_lanes() {
    let w = world("ops-consulted");
    kept_three(&w);
    let said = std::sync::Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = w.store();
    let reach = Reach {
        start: &browser,
        say: &say,
        store: &store,
    };
    assert_eq!(consulted(&w.root, 2, 2, &reach).unwrap(), 0);
    let lines = said.lock().unwrap().clone();
    assert_eq!(lines[0], "archive: 2 kept uncited URL(s) with no copy yet, in up to 2 lane(s) (feature 312: only what the filter kept)");
    assert_eq!(lines.len(), 3);
    assert!(row_files(&w.root).len() >= 3);
}

/// Three kept pages, two of one host.
fn kept_three(w: &World) {
    let kept: String = ["https://k.org/1", "https://k.org/2", "https://j.org/3"]
        .iter()
        .map(|u| json!({"url": l7r_guard::shared::consulted::norm(u), "raw": u}).to_string() + "\n")
        .collect();
    l7r_gate_research::fixture::put(&w.root, KEPT, &kept);
}

/// No limit and no lane count: every kept page in one lane; and a lane whose browser will not start is the run's error. Apart from the
/// limited run above, on a world of its own - the two runs' pushes together were past FR-008's tenth of a second (feature 449 T167).
#[test]
fn consulted_with_no_limit_takes_every_page_and_a_browser_that_will_not_start_fails_it() {
    let w = world("ops-consulted-all");
    kept_three(&w);
    let said = std::sync::Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = w.store();
    let reach = Reach {
        start: &browser,
        say: &say,
        store: &store,
    };
    assert_eq!(consulted(&w.root, 0, 0, &reach).unwrap(), 0);
    // a lane whose browser will not start is the run's error
    l7r_gate_research::fixture::put(
        &w.root,
        KEPT,
        &(json!({"url": "n.org/1", "raw": "https://n.org/1"}).to_string() + "\n"),
    );
    let reach = Reach {
        start: &no_browser,
        say: &say,
        store: &store,
    };
    assert_eq!(
        consulted(&w.root, 0, 1, &reach).unwrap_err().message,
        "BrowserType.launch: none"
    );
}

/// The last push refused: exit 1. Apart from the test above, whose archive it never read, on a world of its own: the two together
/// pushed past FR-008's tenth of a second (feature 449 T167).
#[test]
fn consulted_whose_last_push_is_refused_exits_one() {
    let w = world("ops-consulted-refused");
    let said = std::sync::Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = w.store();
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", "/no/such.git"],
    );
    l7r_gate_research::fixture::put(
        &w.root,
        KEPT,
        &(json!({"url": "k.org/2", "raw": "https://k.org/2"}).to_string() + "\n"),
    );
    std::fs::remove_file(crate::manifest::row_path(&w.root, "https://k.org/2")).ok();
    let reach = Reach {
        start: &browser,
        say: &say,
        store: &store,
    };
    assert_eq!(consulted(&w.root, 0, 1, &reach).unwrap(), 1);
}

#[test]
fn the_cited_pages_read_are_archived_with_one_browser() {
    let w = world("ops-archive-urls");
    let store = |_: &Path| w.store();
    // a page the record cites: archived with who cites it
    put(
        &w,
        "sources/010-works-cited/0060-k.html",
        "<h3 id=\"k\"><code>k</code></h3>\n<p>https://k.org/1</p>\n",
    );
    let mut err = String::new();
    archive_urls(
        &w.root,
        &s(&["https://e.org/a", "ftp://x"]),
        &browser,
        &store,
        &mut err,
    )
    .unwrap();
    assert!(err.is_empty());
    archive_urls(
        &w.root,
        &s(&["https://k.org/1", "https://dead.org/x"]),
        &browser,
        &store,
        &mut err,
    )
    .unwrap();
    assert_eq!(
        err.lines().collect::<Vec<_>>(),
        [
            "archive: archived - https://k.org/1",
            "archive: unreachable - https://dead.org/x"
        ]
    );
    let e = archive_urls(
        &w.root,
        &s(&["https://k.org/2"]),
        &no_browser,
        &store,
        &mut err,
    )
    .unwrap_err();
    assert_eq!(e.kind, "Error");
    let blocked = archive_urls(
        &w.root,
        &s(&["https://grokipedia.com/x"]),
        &browser,
        &store,
        &mut err,
    )
    .unwrap_err();
    assert_eq!(blocked.kind, "Blocked");
    std::fs::remove_dir_all(w.research().join("sources")).unwrap();
    assert!(archive_urls(
        &w.root,
        &s(&["https://k.org/3"]),
        &browser,
        &store,
        &mut err
    )
    .is_err());
}

#[test]
fn a_rows_url_and_the_entries_of_a_folder() {
    let w = world("ops-rows");
    assert_eq!(
        row_url(&w.research().join("archive/a1/a1b2c3d4e5f6.json")).unwrap(),
        "https://e.org/a"
    );
    std::fs::write(w.gm.join(".h"), "").unwrap();
    std::fs::write(w.gm.join("v"), "").unwrap();
    assert_eq!(sorted_entries(&w.gm, true).len(), 2);
    assert_eq!(sorted_entries(&w.gm, false).len(), 1);
    assert_eq!(
        urls_in("see https://a.org/x and http://b.org/y."),
        s(&["https://a.org/x", "http://b.org/y."])
    );
    assert_eq!(
        os_error(&std::io::Error::other("o"), Path::new("p")).message,
        "o: 'p'"
    );
}

fn row(w: &World, url: &str, v: &Value) {
    crate::manifest::write_row(&w.root, url, v).unwrap();
}

#[test]
fn find_answers_by_url_key_and_words() {
    let w = world("ops-find");
    let store = w.store();
    row(
        &w,
        "https://k.org/1",
        &json!({"url": "https://k.org/1", "outcome": "archived", "keys": ["k1", "k2"], "path": "ab/x//T/",
                                         "gm_copies": ["gm-copies/a.pdf"]}),
    );
    row(
        &w,
        "https://k.org/2",
        &json!({"url": "https://k.org/2", "outcome": 7, "keys": ["k1"]}),
    );
    table(
        &w,
        &json!({"b.pdf": {"keys": ["k1"], "archived": "gm-copies/b.pdf"}, "a.pdf": {"keys": ["k1"]}, "c.pdf": {"keys": ["k9"], "archived": ""}}),
    );
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "https://www.k.org/1/", "", "", &mut out).unwrap(),
        0
    );
    let dir = store.dir.display();
    assert!(out.starts_with("attempts: https://www.k.org/1/ - no earlier attempt\n"),);
    assert!(out.contains(&format!("archived                   https://k.org/1\n  local: {dir}/ab/x/T\n  keys: k1, k2\n  the GM's copy: {dir}/gm-copies/a.pdf\n")));
    let log = std::fs::read_to_string(w.research().join("source-attempts.jsonl")).unwrap();
    assert!(
        log.contains("\"route\": \"archive-find\"")
            && log.contains("is it in the archive (make archive-find)")
    );
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "k1", "", &mut out).unwrap(),
        0
    );
    assert!(out.contains("                         7 https://k.org/2\n  local: (no copy)\n  keys: k1\nattempts: https://k.org/2 - "));
    assert!(out.ends_with(&format!("the GM's copy of k1: {dir}/gm-copies/b.pdf\n")),);
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "nokey", "", &mut out).unwrap(),
        1
    );
    assert_eq!(out, "archive: nothing held - search the web (a page you cite is archived by `make source-outcome OUTCOME=cited:<key>`)\n");
    row(
        &w,
        "https://k.org/3",
        &json!({"url": "https://k.org/3", "outcome": null, "keys": ["k3"]}),
    );
    assert_eq!(
        find::find(&w.root, &store, "", "k3", "", &mut String::new())
            .unwrap_err()
            .kind,
        "TypeError"
    );
    row(
        &w,
        "https://k.org/4",
        &json!({"outcome": "archived", "keys": ["k4"]}),
    );
    assert_eq!(
        find::find(&w.root, &store, "https://x.org", "", "", &mut String::new())
            .unwrap_err()
            .kind,
        "KeyError"
    );
    std::fs::remove_file(crate::manifest::row_path(&w.root, "https://k.org/4")).unwrap();
    std::fs::remove_file(crate::manifest::row_path(&w.root, "https://k.org/3")).unwrap();
    row(
        &w,
        "https://k.org/5",
        &json!({"url": "https://k.org/5", "keys": ["k5"]}),
    );
    assert_eq!(
        find::find(&w.root, &store, "", "k5", "", &mut String::new())
            .unwrap_err()
            .kind,
        "KeyError"
    );
    std::fs::remove_file(crate::manifest::row_path(&w.root, "https://k.org/5")).unwrap();
    std::fs::write(w.research().join("blocked-domains.json"), "{").unwrap();
    assert!(find::find(&w.root, &store, "https://x.org", "", "", &mut String::new()).is_err());
}

#[test]
fn find_by_words_takes_every_word_and_says_which_hold_each_alone() {
    let w = world("ops-find-words");
    let store = w.store();
    let text = |rel: &str, t: &str| {
        let p = store.dir.join(rel);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, t).unwrap();
    };
    text("ab/x/T/text.txt", "Alpha beta");
    text("ab/x/T/served.pdf.txt", "alpha gamma");
    text("cd/y/T/text.txt", "alpha only");
    text(".git/z/text.txt", "alpha beta in git");
    row(
        &w,
        "https://k.org/1",
        &json!({"url": "https://k.org/1", "outcome": "archived", "path": "ab/x/T"}),
    );
    row(
        &w,
        "https://k.org/0",
        &json!({"url": "https://k.org/0", "outcome": "archived", "path": "ab/x/T/"}),
    );
    let dir = store.dir.display();
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "", " alpha | beta |", &mut out).unwrap(),
        0
    );
    assert_eq!(
        out.lines().take(2).collect::<Vec<_>>(),
        [
            format!("text holds alpha + beta: {dir}/ab/x/T/text.txt"),
            "  url: https://k.org/1".to_owned()
        ]
    );
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "", "alpha", &mut out).unwrap(),
        0
    );
    assert!(out.contains(&format!("text holds alpha: {dir}/cd/y/T/text.txt\n")),);
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "", "alpha|zeta|beta|alpha", &mut out).unwrap(),
        1
    );
    assert_eq!(
        out,
        "archive: no text holds ALL of alpha + zeta + beta + alpha (TERMS are all required). Texts holding each alone: alpha 2, zeta 0, \
         beta 1 - ask one term at a time: `make archive-find TERMS=\"alpha\"`\n"
    );
    let mut out = String::new();
    assert_eq!(
        find::find(&w.root, &store, "", "", "zeta|eta9", &mut out).unwrap(),
        1
    );
    assert!(out.starts_with("archive: nothing held"));
    let mut gone = w.store();
    gone.dir = w.home.join("no-such");
    assert_eq!(
        find::find(&w.root, &gone, "", "", "alpha", &mut String::new()).unwrap(),
        1
    );
    row(
        &w,
        "https://k.org/2",
        &json!({"outcome": "archived", "path": "cd/y/T"}),
    );
    assert_eq!(
        find::find(&w.root, &store, "", "", "alpha", &mut String::new())
            .unwrap_err()
            .kind,
        "KeyError"
    );
}

#[test]
fn the_relayout_moves_the_first_captures_and_their_rows() {
    let w = world("ops-relayout");
    let store = w.store();
    let wc = w.home.join("source-archive");
    for rel in [
        "src-a/0123456789ab/T1/text.txt",
        "notes/0123456789ab/T2/text.txt",
        "k/gm-copy/old.pdf",
        "k/gm-copy/also.pdf",
        "deep/a/b/c.txt",
        "src-a/keep/f.txt",
    ] {
        let p = wc.join(rel);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, rel).unwrap();
    }
    git(&wc, &["add", "-A"]);
    git(&wc, &["commit", "-q", "-m", "old"]);
    // empty folders git does not hold, removed deepest first
    std::fs::create_dir_all(wc.join("src-a/zz/yy")).unwrap();
    put(
        &w,
        "archive/0234.json",
        &json!({"url": "https://k.org/flat3", "path": "missing/x/T"}).to_string(),
    );
    put(
        &w,
        "archive/0345.json",
        &json!({"url": "https://k.org/flat4", "path": "src-a/0123456789ab/T9"}).to_string(),
    );
    let url = "https://k.org/flat";
    let base = crate::manifest::capture_base(url);
    put(&w, "archive/0123456789ab.json", &json!({"url": url, "outcome": "archived", "path": "src-a/0123456789ab/T1",
                                                 "first": "notes/0123456789ab/T2", "gm_copies": ["k/gm-copy/old.pdf", "x/y"]}).to_string());
    put(&w, "archive/abcdef.json", &json!({"url": "https://k.org/flat2", "path": format!("{}/T", crate::manifest::capture_base("https://k.org/flat2")), "first": "", "gm_copies": []}).to_string());
    table(
        &w,
        &json!({"old.pdf": {"keys": ["k", "k"], "archived": "elsewhere"}, "also.pdf": {"keys": ["k", "z"]}, "x": 5}),
    );
    assert_eq!(relayout::relayout(&w.root, &store).unwrap(), 4);
    let moved = crate::manifest::read_row(&w.root, url).unwrap();
    assert_eq!(moved["path"], json!(format!("{base}/T1")));
    assert_eq!(moved["first"], json!(format!("{base}/T2")));
    assert_eq!(moved["gm_copies"], json!(["gm-copies/old.pdf", "x/y"]));
    assert!(
        wc.join(format!("{base}/T1/text.txt")).is_file()
            && wc.join(format!("{base}/T2/text.txt")).is_file()
    );
    assert!(
        wc.join("gm-copies/old.pdf").is_file()
            && wc.join("src-a/keep/f.txt").is_file()
            && !wc.join("src-a/zz").exists()
            && !wc.join("src-a/0123456789ab").exists()
            && !wc.join("k").exists()
    );
    let t = gm_table(&w.root).unwrap();
    assert_eq!(
        (
            t["old.pdf"]["archived"].clone(),
            t["also.pdf"]["archived"].clone()
        ),
        (json!("gm-copies/old.pdf"), json!("gm-copies/also.pdf"))
    );
    assert!(!w.research().join("archive/0123456789ab.json").exists());
    assert_eq!(w.subjects()[0], "relayout: captures sharded by the URL id's first two hex digits, the GM's copies under gm-copies/");
    // nothing to move: nothing committed, the push clean
    assert_eq!(relayout::relayout(&w.root, &store).unwrap(), 0);
}

/// A refused push, after the table is written, and a row with no URL: apart from the test above on a world of their own holding the
/// capture the row names - the three relayouts' pushes together were past FR-008's tenth of a second (feature 449 T167).
#[test]
fn a_relayout_whose_push_is_refused_says_so_and_a_row_with_no_url_is_refused() {
    let w = world("ops-relayout-refused");
    let store = w.store();
    let wc = w.home.join("source-archive");
    std::fs::create_dir_all(wc.join("deep/a/b")).unwrap();
    std::fs::write(wc.join("deep/a/b/c.txt"), "deep/a/b/c.txt").unwrap();
    git(&wc, &["add", "-A"]);
    git(&wc, &["commit", "-q", "-m", "old"]);
    git(&wc, &["remote", "set-url", "origin", "/no/such.git"]);
    put(
        &w,
        "archive/0f.json",
        &json!({"url": "https://k.org/f3", "path": "deep/a"}).to_string(),
    );
    let e = relayout::relayout(&w.root, &store).unwrap_err();
    assert!(
        e.message.starts_with("relayout committed but not pushed: "),
        "{}",
        e.message
    );
    put(&w, "archive/0e.json", "{}");
    assert_eq!(
        relayout::relayout(&w.root, &store).unwrap_err().kind,
        "KeyError"
    );
}

#[test]
fn the_file_helpers_refuse_as_the_python_did() {
    let w = world("ops-helpers");
    std::fs::write(w.gm.join("f"), "x").unwrap();
    assert!(mkdir(&w.gm.join("f/g")).is_err());
    std::fs::create_dir_all(w.gm.join("d/e")).unwrap();
    assert!(rmdir(&w.gm.join("d")).is_err());
    assert!(unlink(&w.gm.join("nope")).is_err());
    assert!(rmtree(&w.gm.join("nope")).is_err());
    assert!(write_file(&w.gm.join("d"), "x").is_err());
    assert_eq!(
        find::spawn_failed(std::io::Error::other("gone")).message,
        "gone: 'grep'"
    );
    assert_eq!(relayout::split_last("//x"), ("/", "x"));
    assert_eq!(relayout::split_last("a//b"), ("a", "b"));
    assert_eq!(relayout::split_last("b"), ("", "b"));
}

#[test]
fn a_folders_files_in_rglobs_own_order() {
    // `rglob("*")`'s walk (CPython 3.14's `select_recursive`): the root's files, then each of its directories' files as the root lists
    // them, then the stack worked last in, first out - a deeper directory's files after its parent's siblings', in reverse - and a
    // symlinked directory never entered
    let w = world("ops-rglob");
    let r = w.gm.join("folder");
    for f in ["a.txt", "d1/x", "d1/d1a/q", "d2/y", "d2/e/z", "d3/w"] {
        let p = r.join(f);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, f).unwrap();
    }
    std::os::unix::fs::symlink(r.join("d1"), r.join("d3/link")).unwrap();
    std::os::unix::fs::symlink(r.join("d2/y"), r.join("flink")).unwrap();
    let listed: Vec<String> = std::fs::read_dir(&r)
        .unwrap()
        .map(|e| e.unwrap().file_name().to_string_lossy().into_owned())
        .collect();
    let dirs: Vec<&String> = listed.iter().filter(|n| n.starts_with('d')).collect();
    let mut want: Vec<String> = listed
        .iter()
        .filter(|n| !n.starts_with('d'))
        .cloned()
        .collect();
    let first = |d: &str| match d {
        "d1" => "d1/x",
        "d2" => "d2/y",
        _ => "d3/w",
    };
    want.extend(dirs.iter().map(|d| first(d).to_owned()));
    want.extend(dirs.iter().rev().filter_map(|d| match d.as_str() {
        "d1" => Some("d1/d1a/q".to_owned()),
        "d2" => Some("d2/e/z".to_owned()),
        _ => None,
    }));
    let mut got = Vec::new();
    files_under(&r, &mut got);
    let got: Vec<String> = got
        .iter()
        .map(|p| p.strip_prefix(&r).unwrap().to_string_lossy().into_owned())
        .collect();
    assert_eq!(got, want);
}
