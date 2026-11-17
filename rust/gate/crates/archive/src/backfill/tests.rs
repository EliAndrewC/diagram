//! The backfill's lanes (feature 449 T146).

use std::sync::Mutex;

use super::{backfill, lane, lanes, Lane};
use crate::fetch::Client;
use crate::testkit::{Fake, World};
use crate::Error;

#[test]
fn every_url_of_a_host_is_in_one_lane() {
    let urls: Vec<String> = [
        "http://a/1",
        "http://b/1",
        "http://a/2",
        "http://c/1",
        "http://a/3",
        "http://b/2",
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    assert_eq!(
        lanes(&urls, 2),
        vec![
            vec!["http://a/1", "http://a/2", "http://a/3"],
            vec!["http://b/1", "http://b/2", "http://c/1"]
        ]
    );
    assert_eq!(lanes(&urls, 0).len(), 1);
    assert_eq!(lanes(&urls, 9).len(), 3);
}

#[test]
fn a_lane_archives_its_urls_recycles_its_browser_and_pushes_past_the_limit() {
    let w = World::new("backfill-lane");
    let store = w.store();
    let said = Mutex::new(Vec::new());
    let starts = Mutex::new(0);
    let start = |_: &std::path::Path| -> crate::Result<Box<dyn Client>> {
        *starts.lock().unwrap() += 1;
        Ok(Box::new(Fake::default()))
    };
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let urls: Vec<String> = (0..=super::RECYCLE_EVERY)
        .map(|n| format!("https://e.org/n{n}"))
        .collect();
    let who = vec![(
        "https://e.org/n1".to_owned(),
        l7r_gate_research::record::archive::Cited {
            keys: vec!["src-a".into()],
            notes: vec![],
        },
    )];
    std::fs::write(w.home.join("source-archive.unpushed"), "999999999999").unwrap();
    let how = Lane {
        root: &w.root,
        who: &who,
        start: &start,
        say: &say,
    };
    let rows = lane(&how, &urls[..1], &store).unwrap();
    assert_eq!(rows[0]["outcome"], "unreachable");
    assert_eq!(
        said.lock().unwrap()[0],
        format!("{:26} https://e.org/n0", "unreachable")
    );
    // past the limit with a remote that refuses: the failure said, the lane goes on
    std::fs::write(w.home.join("source-archive.unpushed"), "999999999999").unwrap();
    crate::testkit::git(
        &store.dir,
        &["remote", "set-url", "origin", "/no/such/remote.git"],
    );
    store
        .put("x/T", &[("f".to_owned(), b"1".to_vec())], "one")
        .unwrap();
    std::fs::write(w.home.join("source-archive.unpushed"), "999999999999").unwrap();
    let rows = lane(&how, &urls, &store).unwrap();
    assert_eq!(rows.len(), super::RECYCLE_EVERY + 1);
    assert_eq!(rows[1]["keys"], serde_json::json!(["src-a"]));
    assert_eq!(*starts.lock().unwrap(), 1 + 2);
    assert!(said
        .lock()
        .unwrap()
        .iter()
        .any(|l| l.starts_with("push failed: ")));
    let fail = |_: &std::path::Path| -> crate::Result<Box<dyn Client>> {
        Err(Error::new("Error", "no browser"))
    };
    let broken = Lane {
        root: &w.root,
        who: &who,
        start: &fail,
        say: &say,
    };
    assert_eq!(
        lane(&broken, &urls, &store).unwrap_err().message,
        "no browser"
    );
    assert!(lane(&broken, &urls[..0], &store).is_err());
}

#[test]
fn the_backfill_runs_its_lanes_pushes_settles_and_reports() {
    let w = World::new("backfill-all");
    // the blocked entry out: a cited URL on a blocked domain raises in the lane, as the Python's did
    std::fs::remove_file(w.research().join("sources/010-works-cited/0030-grok.html")).unwrap();
    let store = w.store();
    let said = Mutex::new(Vec::new());
    let start =
        |_: &std::path::Path| -> crate::Result<Box<dyn Client>> { Ok(Box::new(Fake::default())) };
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let mut err = String::new();
    let code = backfill(&w.root, 2, &start, &say, &mut err, &store).unwrap();
    let lines = said.lock().unwrap().clone();
    assert!(
        lines[0].starts_with("archive: ")
            && lines[0].ends_with(" cited URL(s) owed a copy, in up to 2 lane(s)")
    );
    assert!(lines.last().unwrap().starts_with("archive coverage: "));
    assert_eq!((code, err.as_str()), (0, ""));
    // a push that fails at the end keeps the captures and says where
    crate::testkit::git(
        &store.dir,
        &["remote", "set-url", "origin", "/no/such/remote.git"],
    );
    l7r_gate_research::fixture::put(
        &w.research(),
        "sources/010-works-cited/0040-more.html",
        "<h3 id=\"more\"><code>more</code></h3>\n<p>https://e.org/more</p>\n",
    );
    assert_eq!(
        backfill(&w.root, 1, &start, &say, &mut err, &store).unwrap(),
        1
    );
    assert!(err.starts_with("archive: the final push failed - "));
    let fail = |_: &std::path::Path| -> crate::Result<Box<dyn Client>> {
        Err(Error::new("Error", "no browser"))
    };
    l7r_gate_research::fixture::put(
        &w.research(),
        "sources/010-works-cited/0050-again.html",
        "<h3 id=\"again\"><code>again</code></h3>\n<p>https://e.org/again</p>\n",
    );
    assert_eq!(
        backfill(&w.root, 1, &fail, &say, &mut err, &store)
            .unwrap_err()
            .message,
        "no browser"
    );
    std::fs::remove_dir_all(w.research().join("sources")).unwrap();
    assert!(backfill(&w.root, 1, &start, &say, &mut err, &store).is_err());
    let mut gone = w.store();
    gone.home = w.dir.path().join("file");
    std::fs::write(&gone.home, "x").unwrap();
    assert!(backfill(&w.root, 1, &start, &say, &mut err, &gone).is_err());
}
