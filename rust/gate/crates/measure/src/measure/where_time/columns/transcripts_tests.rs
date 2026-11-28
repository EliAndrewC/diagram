//! The transcripts are read once a report (462 T544): each main transcript in one pass, its enqueue rows with the rest, and a transcript
//! last written before the window's start (less the slack) not at all.

use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::json;

use super::*;

fn iso(when: SystemTime) -> String {
    let epoch = when.duration_since(UNIX_EPOCH).unwrap().as_secs();
    let (year, mo, day, hour, mi, sec) = l7r_shared::log::civil(epoch);
    format!("{year:04}-{mo:02}-{day:02}T{hour:02}:{mi:02}:{sec:02}Z")
}

fn secs(t: SystemTime) -> f64 {
    t.duration_since(UNIX_EPOCH).unwrap().as_secs_f64()
}

/// A session `s` with an enqueue row and a call in its own transcript, a subagent written now and one last written a day ago.
fn fixture(name: &str, now: SystemTime) -> l7r_shared::tempdir::TempDir {
    let d = crate::checks::scratch(name);
    let at = iso(now);
    let usage = |id: &str, t: &str| json!({"timestamp": t, "message": {"id": id, "model": "m", "usage": {"input_tokens": 1}}});
    let enqueue = json!({"type": "queue-operation", "operation": "enqueue", "timestamp": at, "content": "<tool-use-id>toolu_q</tool-use-id>"});
    let bash = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_b", "name": "Bash", "input": {"command": "make quick"}}]}});
    std::fs::create_dir_all(d.join("p/s/subagents")).unwrap();
    std::fs::write(
        d.join("p/s.jsonl"),
        format!("{enqueue}\n{}\n{bash}\n", usage("m0", &at)),
    )
    .unwrap();
    std::fs::write(
        d.join("p/s/subagents/agent-new.jsonl"),
        format!("{}\n", usage("m1", &at)),
    )
    .unwrap();
    let old = now - Duration::from_secs(86_400);
    let path = d.join("p/s/subagents/agent-old.jsonl");
    std::fs::write(&path, format!("{}\n", usage("m2", &iso(old)))).unwrap();
    std::fs::File::options()
        .write(true)
        .open(&path)
        .unwrap()
        .set_modified(old)
        .unwrap();
    d
}

fn reads() -> HashMap<String, usize> {
    READS.with(|r| {
        r.borrow()
            .iter()
            .map(|(p, n)| (p.file_name().unwrap().to_string_lossy().into_owned(), *n))
            .collect()
    })
}

#[test]
fn each_transcript_is_read_once_and_an_old_one_not_at_all() {
    let now = SystemTime::now();
    let d = fixture("measure-columns-read-once", now);
    READS.with(|r| r.borrow_mut().clear());
    let window = (secs(now) - 3600.0, secs(now) + 60.0);
    let got = read_subagents(&["s".to_owned()], &d, window);
    let n = reads();
    assert_eq!(n.get("s.jsonl"), Some(&1), "{n:?}");
    assert_eq!(n.get("agent-new.jsonl"), Some(&1), "{n:?}");
    assert_eq!(n.get("agent-old.jsonl"), None, "{n:?}");
    // what the pass reads is what the two passes read
    assert!(got.enqueued.contains_key("toolu_q"), "{:?}", got.enqueued);
    assert_eq!(got.commands["toolu_b"], "make quick");
    assert_eq!(
        got.calls,
        HashMap::from([("new".to_owned(), 1), ("old".to_owned(), 0)])
    );
    assert_eq!(got.session["s"].len(), 1);
}

#[test]
fn an_unbounded_window_reads_an_old_transcript() {
    let now = SystemTime::now();
    let d = fixture("measure-columns-read-unbounded", now);
    READS.with(|r| r.borrow_mut().clear());
    let got = read_subagents(&["s".to_owned()], &d, (f64::MIN, f64::MAX));
    let n = reads();
    assert_eq!(n.get("agent-old.jsonl"), Some(&1), "{n:?}");
    assert_eq!(got.calls["old"], 1);
}
