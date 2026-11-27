//! The read mark (feature 461 T20) on a scratch common directory: each owed line taken once, the mark moved past complete lines
//! only, a mark past the log's end or no number read from the start, nothing created where there is no log, and a reader that cannot
//! get the lock taking nothing.

use std::io::Write as _;
use std::path::Path;

use super::{dir, take_unread, unread, FILE, MARK, MARK_LOCK};
use crate::tempdir::TempDir;

fn append(common: &Path, text: &str) {
    std::fs::create_dir_all(dir(common)).unwrap();
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(dir(common).join(FILE))
        .unwrap();
    f.write_all(text.as_bytes()).unwrap();
}

fn owed(line: &str) -> String {
    format!(
        "{}\n",
        serde_json::json!({"utc": "2026-11-28T03:00:00Z", "event": "owed", "batch": "461-1", "line": line})
    )
}

#[test]
fn each_owed_line_past_the_mark_is_taken_once_and_the_mark_moved() {
    let t = TempDir::new("lane-wake-once");
    append(t.path(), "{\"event\": \"batch\", \"batch\": \"461-1\"}\n");
    append(t.path(), &owed("lane: batch 461-1 landed"));
    append(t.path(), "not json\n");
    assert!(unread(t.path()));
    assert_eq!(take_unread(t.path()), ["lane: batch 461-1 landed"]);
    let len = std::fs::metadata(dir(t.path()).join(FILE)).unwrap().len();
    assert_eq!(
        std::fs::read_to_string(dir(t.path()).join(MARK)).unwrap(),
        len.to_string()
    );
    assert!(!unread(t.path()));
    assert!(take_unread(t.path()).is_empty());
    append(t.path(), &owed("lane: batch 461-2 landed"));
    append(t.path(), &owed("lane: the runner is not running"));
    assert_eq!(
        take_unread(t.path()),
        [
            "lane: batch 461-2 landed",
            "lane: the runner is not running"
        ]
    );
}

#[test]
fn a_torn_last_line_is_left_until_it_is_whole() {
    let t = TempDir::new("lane-wake-torn");
    let whole = owed("lane: batch 461-1 landed");
    let (head, tail) = whole.split_at(20);
    append(t.path(), head);
    assert!(take_unread(t.path()).is_empty());
    assert!(!dir(t.path()).join(MARK).exists());
    append(t.path(), tail);
    assert_eq!(take_unread(t.path()), ["lane: batch 461-1 landed"]);
}

#[test]
fn a_mark_past_the_end_or_no_number_reads_from_the_start() {
    let t = TempDir::new("lane-wake-past");
    append(t.path(), &owed("lane: one"));
    std::fs::write(dir(t.path()).join(MARK), "999999").unwrap();
    assert_eq!(take_unread(t.path()), ["lane: one"]);
    std::fs::write(dir(t.path()).join(MARK), "x").unwrap();
    assert_eq!(take_unread(t.path()), ["lane: one"]);
}

#[test]
fn no_log_takes_nothing_and_creates_nothing() {
    let t = TempDir::new("lane-wake-none");
    assert!(!unread(t.path()));
    assert!(take_unread(t.path()).is_empty());
    assert!(!dir(t.path()).exists());
}

#[test]
fn a_reader_that_cannot_get_the_lock_takes_nothing() {
    let t = TempDir::new("lane-wake-locked");
    append(t.path(), &owed("lane: one"));
    // the lock's path a directory: no reader can open it, as none can get a lock another holds past LOCK_S
    std::fs::create_dir_all(dir(t.path()).join(MARK_LOCK)).unwrap();
    assert!(take_unread(t.path()).is_empty());
    assert!(unread(t.path()));
}
