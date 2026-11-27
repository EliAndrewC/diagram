//! The derived index against the full parse (feature 451 T443): a log grown, cut anywhere and grown again, rotated, truncated,
//! rewritten in place at the same length, ending in a partial line; two hooks racing to write the index; an index unreadable, torn
//! or of another form - each answered as the full read answers, the index rebuilt where it is not true of the log.

use std::fs::{File, OpenOptions};
use std::io::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::tests::{edged, odd_paths, parse_all, row};
use super::super::CHUNK;
use super::{decode, encode, index_path, load, matching, olds, store, Tie, STALE, WINDOW};

/// A scratch events directory, its log at `<dir>/f.jsonl` holding `text`.
fn world(tag: &str, text: &str) -> (crate::tempdir::TempDir, PathBuf) {
    let d = crate::tempdir::TempDir::new(&format!("guard-reversal-index-{tag}"));
    let log = d.path().join("f.jsonl");
    std::fs::write(&log, text).unwrap();
    (d, log)
}

/// The tripwire's answer for `path` through the index, as the hook asks it.
fn ask(log: &Path, path: &Value) -> Vec<Value> {
    olds(&File::open(log).unwrap(), log, path, CHUNK)
}

/// The bytes the index at the log's index path covers, where it is true of the log; None where it is missing or not.
fn covered(log: &Path) -> Option<u64> {
    load(&index_path(log).unwrap(), &File::open(log).unwrap()).map(|k| k.0)
}

fn append(log: &Path, text: &str) {
    OpenOptions::new()
        .append(true)
        .open(log)
        .unwrap()
        .write_all(text.as_bytes())
        .unwrap();
}

/// A log of many paths' Edits and other lines, `n` rounds of them.
fn busy(n: usize) -> String {
    let mut t = String::new();
    for i in 0..n {
        for p in odd_paths() {
            t.push_str(&row("PreToolUse", "Edit", &p, &format!("o{i}")));
            t.push('\n');
            t.push_str(&row("PostToolUse", "Edit", &p, &format!("post{i}")));
            t.push('\n');
        }
        t.push_str(&row("PreToolUse", "Bash", &json!("/c/docs/usage.md"), "b"));
        t.push('\n');
    }
    t
}

#[test]
fn the_index_answers_as_the_full_parse_cold_and_warm_for_every_path() {
    let text = busy(30);
    let (_d, log) = world("warm", &text);
    for p in odd_paths() {
        assert_eq!(ask(&log, &p), parse_all(&text, &p), "cold {p}");
        assert_eq!(covered(&log), Some(text.len() as u64), "{p}");
        assert_eq!(ask(&log, &p), parse_all(&text, &p), "warm {p}");
    }
    assert!(index_path(&log).unwrap().ends_with("reversal/f.idx"));
    assert_eq!(index_path(Path::new("/")), None);
}

#[test]
fn a_log_cut_at_every_byte_and_grown_again_answers_as_the_full_parse() {
    for p in [json!("/c/docs/usage.md"), json!("/c/a \"quoted\" name.md")] {
        let text = edged(&p);
        for cut in 0..=text.len() {
            let (_d, log) = world("cut", &text[..cut]);
            let (got, want) = (ask(&log, &p), parse_all(&text[..cut], &p));
            assert_eq!(got, want, "{p} prefix {cut}");
            // the index covers the prefix's whole lines only: a partial last line is answered but never kept
            let whole = text[..cut].rfind('\n').map_or(0, |i| i + 1);
            assert_eq!(covered(&log), Some(whole as u64), "{p} {cut}");
            append(&log, &text[cut..]);
            assert_eq!(ask(&log, &p), parse_all(&text, &p), "{p} grown from {cut}");
        }
    }
}

#[test]
fn a_partial_last_line_is_answered_and_kept_only_once_its_newline_comes() {
    let p = json!("/c/docs/usage.md");
    let first = format!("{}\n", row("PreToolUse", "Edit", &p, "A"));
    let half = row("PreToolUse", "Edit", &p, "B");
    let (_d, log) = world("partial", &format!("{first}{half}"));
    assert_eq!(ask(&log, &p), [json!("A"), json!("B")]);
    assert_eq!(covered(&log), Some(first.len() as u64));
    append(&log, "\n");
    assert_eq!(ask(&log, &p), [json!("A"), json!("B")]);
}

#[test]
fn a_log_grown_past_stale_rewrites_the_index_and_one_grown_less_only_reads_it() {
    let p = json!("/c/docs/usage.md");
    let text = format!("{}\n", row("PreToolUse", "Edit", &p, "A"));
    let (_d, log) = world("stale", &text);
    ask(&log, &p);
    let small = format!("{}\n", row("PreToolUse", "Edit", &p, "B"));
    append(&log, &small);
    assert_eq!(ask(&log, &p), [json!("A"), json!("B")]);
    assert_eq!(covered(&log), Some(text.len() as u64));
    let filler = format!("{}\n", row("PreToolUse", "Bash", &p, &"x".repeat(500))).repeat(2_200);
    assert!(filler.len() as u64 > STALE);
    append(&log, &filler);
    assert_eq!(ask(&log, &p), [json!("A"), json!("B")]);
    let all = std::fs::metadata(&log).unwrap().len();
    assert_eq!(covered(&log), Some(all));
}

#[test]
fn a_rotated_log_is_not_read_through_the_old_index() {
    let p = json!("/c/docs/usage.md");
    let a = format!("{}\n", row("PreToolUse", "Edit", &p, "A"));
    let (d, log) = world("rotated", &a);
    assert_eq!(ask(&log, &p), [json!("A")]);
    // refile's temporary file and rename: the same length, another inode
    let b = a.replace("\"A\"", "\"Z\"");
    let tmp = d.path().join("f.jsonl.refile");
    std::fs::write(&tmp, &b).unwrap();
    std::fs::rename(&tmp, &log).unwrap();
    assert_eq!(covered(&log), None);
    assert_eq!(ask(&log, &p), [json!("Z")]);
    assert_eq!(covered(&log), Some(b.len() as u64));
}

#[test]
fn a_truncated_log_is_rebuilt() {
    let p = json!("/c/docs/usage.md");
    let text = busy(5);
    let (_d, log) = world("truncated", &text);
    ask(&log, &p);
    let keep = text.split_inclusive('\n').take(3).collect::<String>();
    OpenOptions::new()
        .write(true)
        .open(&log)
        .unwrap()
        .set_len(keep.len() as u64)
        .unwrap();
    assert_eq!(covered(&log), None);
    assert_eq!(ask(&log, &p), parse_all(&keep, &p));
    // truncated, then grown back past the old length with other lines: the windows tell it apart
    let (_e, log) = world("truncated-regrown", &text);
    ask(&log, &p);
    OpenOptions::new()
        .write(true)
        .open(&log)
        .unwrap()
        .set_len(0)
        .unwrap();
    let other = busy(7).replace(":\"o", ":\"n");
    append(&log, &other);
    assert_eq!(covered(&log), None);
    assert_eq!(ask(&log, &p), parse_all(&other, &p));
}

#[test]
fn a_log_rewritten_in_place_at_the_same_length_is_rebuilt() {
    let p = json!("/c/docs/usage.md");
    let text = busy(40);
    assert!(text.len() as u64 > 2 * WINDOW);
    // the whole log rewritten, and one byte changed in either window
    let whole = text.replace(":\"o", ":\"q");
    let mut first = text.clone().into_bytes();
    first[text.find("\"o0\"").unwrap() + 1] = b'w';
    let mut last = text.clone().into_bytes();
    last[text.rfind("\"o39\"").unwrap() + 1] = b'w';
    for (i, after) in [whole.into_bytes(), first, last].into_iter().enumerate() {
        let (_d, log) = world(&format!("rewritten-{i}"), &text);
        ask(&log, &p);
        assert_eq!(after.len(), text.len());
        OpenOptions::new()
            .write(true)
            .open(&log)
            .unwrap()
            .write_all(&after)
            .unwrap();
        assert_eq!(covered(&log), None, "{i}");
        let want = parse_all(std::str::from_utf8(&after).unwrap(), &p);
        assert_eq!(ask(&log, &p), want, "{i}");
    }
}

#[test]
fn a_change_in_place_between_the_windows_at_the_same_length_is_the_one_it_cannot_see() {
    // the module's stated limit, pinned so a change to it is seen: no writer of the log does this (they append or rename)
    let p = json!("/c/docs/usage.md");
    let text = busy(40);
    let (_d, log) = world("between", &text);
    ask(&log, &p);
    let mut after = text.clone().into_bytes();
    after[text.find("\"o20\"").unwrap() + 1] = b'w';
    OpenOptions::new()
        .write(true)
        .open(&log)
        .unwrap()
        .write_all(&after)
        .unwrap();
    assert_eq!(covered(&log), Some(text.len() as u64));
    assert_eq!(ask(&log, &p), parse_all(&text, &p));
}

#[test]
fn two_hooks_racing_to_write_the_index_lose_at_most_one_rebuild() {
    let p = json!("/c/docs/usage.md");
    let text = busy(20);
    let (d, log) = world("race", &text);
    // hook A read no index and scanned the first half; hook B wrote the whole log's index; A's older index lands over it
    let half = text[..text.len() / 2].rfind('\n').unwrap() + 1;
    let f = File::open(&log).unwrap();
    let mut rows = Vec::new();
    for l in text[..half].lines() {
        super::indexed(l.as_bytes(), &mut rows);
    }
    ask(&log, &p);
    store(
        &index_path(&log).unwrap(),
        &Tie::of(&f, half as u64).unwrap(),
        &rows,
    );
    assert_eq!(covered(&log), Some(half as u64));
    assert_eq!(ask(&log, &p), parse_all(&text, &p));
    // eight real threads at once on a log with no index: every answer the full parse's, one whole index left, no temporary file
    std::fs::remove_dir_all(d.path().join("reversal")).unwrap();
    let answers: Vec<Vec<Value>> = std::thread::scope(|s| {
        let hs: Vec<_> = (0..8).map(|_| s.spawn(|| ask(&log, &p))).collect();
        hs.into_iter().map(|h| h.join().unwrap()).collect()
    });
    assert!(answers.iter().all(|a| *a == parse_all(&text, &p)));
    assert_eq!(covered(&log), Some(text.len() as u64));
    let left: Vec<_> = std::fs::read_dir(d.path().join("reversal"))
        .unwrap()
        .map(|e| e.unwrap().file_name())
        .collect();
    assert_eq!(left, ["f.idx"]);
}

#[test]
fn an_index_unreadable_torn_or_of_another_form_is_rebuilt() {
    let p = json!("/c/docs/usage.md");
    let text = busy(10);
    let want = parse_all(&text, &p);
    for i in 0..10 {
        // each torn index is made from the true index of its own log, so only the tear can refuse it
        let (_e, log) = world(&format!("torn-{i}"), &text);
        ask(&log, &p);
        let idx = index_path(&log).unwrap();
        let t = torn(&std::fs::read(&idx).unwrap()).swap_remove(i);
        std::fs::write(&idx, &t).unwrap();
        assert_eq!(covered(&log), None, "{i}");
        assert_eq!(ask(&log, &p), want, "{i}");
        assert_eq!(covered(&log), Some(text.len() as u64), "{i}");
    }
    // an index that is a directory, or a directory that cannot be written: answered by the full scan, nothing kept
    let (_f, log) = world("dir", &text);
    std::fs::create_dir_all(index_path(&log).unwrap()).unwrap();
    assert_eq!(ask(&log, &p), want);
    assert_eq!(covered(&log), None);
    // the failed rename leaves no temporary file behind
    let dir = index_path(&log).unwrap().parent().unwrap().to_path_buf();
    let left: Vec<_> = std::fs::read_dir(dir)
        .unwrap()
        .map(|e| e.unwrap().file_name())
        .collect();
    assert_eq!(left, ["f.idx"]);
}

/// Ten tears of a true index `good`: not an index, empty, not UTF-8, cut short, a row appended, another version, a wrong row count,
/// a header short a number, a last row with no newline, and a byte inserted inside a row.
fn torn(good: &[u8]) -> Vec<Vec<u8>> {
    let good = good.to_vec();
    let nl = good.iter().position(|&b| b == b'\n').unwrap();
    let mut bad_count = good.clone();
    bad_count[nl - 1] = b'9';
    let short_header = String::from_utf8(good[..nl].to_vec())
        .unwrap()
        .rsplit_once(' ')
        .unwrap()
        .0
        .to_owned();
    let mut no_newline = good[..good.len() - 1].to_vec();
    no_newline.push(b'x');
    let mut inside = good[..good.len() - 1].to_vec();
    inside.extend_from_slice(b"x\n");
    vec![
        b"garbage".to_vec(),
        Vec::new(),
        b"\xff\xfe\n".to_vec(),
        good[..good.len() - 40].to_vec(),
        [good.clone(), b"extra\n".to_vec()].concat(),
        good.replacen(b"index 1", b"index 2"),
        bad_count,
        [short_header.as_bytes(), &good[nl..]].concat(),
        no_newline,
        inside,
    ]
}

/// `replacen` for bytes: the first `from` in `self` replaced by `to`.
trait Replacen {
    fn replacen(&self, from: &[u8], to: &[u8]) -> Vec<u8>;
}

impl Replacen for Vec<u8> {
    fn replacen(&self, from: &[u8], to: &[u8]) -> Vec<u8> {
        let at = memchr::memmem::find(self, from).unwrap();
        [&self[..at], to, &self[at + from.len()..]].concat()
    }
}

#[test]
fn the_rows_round_trip_and_a_row_with_no_tab_is_passed_over() {
    let tie = Tie {
        dev: 1,
        ino: 2,
        covered: 3,
        head: b"abc".to_vec(),
        tail: b"c\n".to_vec(),
    };
    let mut rows = Vec::new();
    for p in odd_paths() {
        super::row(&mut rows, &p, &json!({"o": p}));
    }
    // a path with no directory or name is no index: nothing written
    store(Path::new("/"), &tie, &rows);
    let text = encode(&tie, &rows);
    assert_eq!(decode(&text), Some((tie, &rows[..])));
    for p in odd_paths() {
        let mut out = Vec::new();
        matching(&rows, &p, &mut out);
        assert_eq!(out, [json!({"o": p})], "{p}");
    }
    let mut out = Vec::new();
    matching(
        b"no tab here\n\"/c/docs/usage.md\"\t\"A\"\n",
        &json!("/c/docs/usage.md"),
        &mut out,
    );
    assert_eq!(out, [json!("A")]);
    // a line the full read would not keep makes no row: not UTF-8, no Edit, not JSON, another event or tool, no path key
    let mut none = Vec::new();
    for l in [
        &b"\xff\"Edit\""[..],
        &b"\xff\"Edit\" \"PreToolUse\""[..],
        br#"{"ev":"PreToolUse","tool":"Bash","path":"/a"}"#,
        br#"not json "Edit""#,
        br#"not json "Edit" "PreToolUse""#,
        br#"{"ev":"PostToolUse","tool":"Edit","path":"/a"}"#,
        br#"{"ev":"PreToolUse","tool":"Edit"}"#,
    ] {
        super::indexed(l, &mut none);
    }
    assert!(none.is_empty());
    super::indexed(
        br#"{"ev":"PreToolUse","tool":"Edit","path":null}"#,
        &mut none,
    );
    assert_eq!(none, b"null\tnull\n");
}

#[test]
fn an_unreadable_index_file_is_answered_by_the_full_scan() {
    use std::os::unix::fs::PermissionsExt as _;
    let p = json!("/c/docs/usage.md");
    let text = busy(4);
    let (_d, log) = world("perm", &text);
    ask(&log, &p);
    let idx = index_path(&log).unwrap();
    std::fs::set_permissions(&idx, std::fs::Permissions::from_mode(0o000)).unwrap();
    // root reads it whatever its mode; anyone else rebuilds it by rename, which the mode does not stop
    assert_eq!(ask(&log, &p), parse_all(&text, &p));
    assert!(std::fs::read(&idx).is_ok());
}

#[test]
fn the_build_parses_only_a_line_holding_both_the_tool_and_the_event_as_text() {
    // 451 T458: a PostToolUse Edit line and another tool's line holding "Edit" are dropped as text; a PreToolUse Edit line is kept
    // whatever the writer puts round the colon, as the full parse keeps it
    let p = json!("/c/docs/usage.md");
    let mut text = String::new();
    for i in 0..5 {
        text.push_str(&row("PreToolUse", "Edit", &p, &format!("o{i}")));
        text.push('\n');
        text.push_str(&row("PostToolUse", "Edit", &p, &format!("post{i}")));
        text.push('\n');
        text.push_str(&row("PostToolUse", "Bash", &json!("Edit"), "b"));
        text.push('\n');
    }
    text.push_str(
        r#"{"ev" : "PreToolUse", "tool" : "Edit", "path" : "/c/docs/usage.md", "old" : "spaced"}"#,
    );
    text.push('\n');
    let mut rows = Vec::new();
    let parsed = text
        .lines()
        .filter(|l| super::indexed(l.as_bytes(), &mut rows))
        .count();
    assert_eq!(parsed, 6);
    let mut got = Vec::new();
    matching(&rows, &p, &mut got);
    assert_eq!(got, parse_all(&text, &p));
    assert_eq!(got.last(), Some(&json!("spaced")));
    let (_d, log) = world("screen", &text);
    assert_eq!(ask(&log, &p), parse_all(&text, &p));
}

#[test]
fn a_parsed_line_that_is_no_pre_tool_use_edit_makes_no_row() {
    let mut rows = Vec::new();
    let line = br#"{"ev":"PostToolUse","tool":"Edit","path":"/c/a.md","note":"PreToolUse"}"#;
    assert!(super::indexed(line, &mut rows));
    assert!(rows.is_empty());
}

/// A hook killed between the temporary write and its rename leaves its temporary file, which the next write of an index in that
/// directory sweeps once it is older than [`super::SWEEP_AGE`] (451 T459); a younger one may be a running writer's, and is kept, as is
/// any file of another form, and nothing is swept by a hook that only reads.
#[test]
fn a_killed_hook_s_temporary_file_is_swept_at_the_next_write_once_it_is_old() {
    let p = json!("/c/docs/usage.md");
    let text = busy(3);
    let (d, log) = world("sweep", &text);
    ask(&log, &p);
    let dir = d.path().join("reversal");
    let aged = |name: &str, age: u64| {
        let f = dir.join(name);
        std::fs::write(&f, "x").unwrap();
        let then = std::time::SystemTime::now() - std::time::Duration::from_secs(age);
        File::options()
            .write(true)
            .open(&f)
            .unwrap()
            .set_modified(then)
            .unwrap();
        f
    };
    let old = super::SWEEP_AGE.as_secs() + 60;
    let killed = aged(".f.idx.4242.0.tmp", old);
    let other = aged(".g.idx.4243.7.tmp", old);
    let young = aged(".f.idx.4244.1.tmp", 5);
    let kept = [
        aged("notes.tmp", old),
        aged(".f.idx.tmp", old),
        aged("f.idx.1.2.tmp", old),
    ];
    // a hook that only reads the index sweeps nothing
    ask(&log, &p);
    assert!(killed.exists());
    std::fs::remove_file(index_path(&log).unwrap()).unwrap();
    assert_eq!(ask(&log, &p), parse_all(&text, &p));
    assert!(!killed.exists() && !other.exists());
    assert!(young.exists() && kept.iter().all(|k| k.exists()));
    assert_eq!(covered(&log), Some(text.len() as u64));
}
