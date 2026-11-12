//! The event log's command line: a hook payload appended in a scratch clone, a transcript converted, the usage.

use super::cli;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_hook_payload_is_appended_and_never_refused() {
    let d = crate::checks::scratch("measure-event-log");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    let payload = format!(
        r#"{{"hook_event_name": "Stop", "session_id": "s", "cwd": "{}"}}"#,
        d.display()
    );
    let r = cli(&args(&["hook"]), &mut payload.as_bytes());
    assert_eq!((r.code, r.stdout.as_str(), r.stderr.as_str()), (0, "", ""));
    let logs = std::fs::read_dir(d.join(".git/l7r-events"))
        .unwrap()
        .count();
    assert_eq!(logs, 1);
    for input in [&b"not json"[..], b"", b"\xff", b"[1]"] {
        assert_eq!(cli(&args(&["hook"]), &mut &input[..]).code, 0);
    }
}

#[test]
fn a_transcript_prints_as_events() {
    let d = crate::checks::scratch("measure-event-log-transcript");
    let t = d.join("t.jsonl");
    std::fs::write(&t, r#"{"type": "user", "timestamp": "2026-11-01T08:00:00Z", "sessionId": "s", "message": {"content": "hi"}}"#).unwrap();
    let r = cli(
        &args(&["from-transcript", &t.display().to_string()]),
        &mut &b""[..],
    );
    assert_eq!(
        r.stdout,
        "{\"t\":\"2026-11-01T08:00:00Z\",\"sid\":\"s\",\"ev\":\"UserPromptSubmit\",\"gm\":true}\n"
    );
    assert_eq!(
        cli(&args(&["from-transcript", "/nonexistent"]), &mut &b""[..]).code,
        1
    );
    std::fs::write(&t, "[1]\n").unwrap();
    assert!(cli(
        &args(&["from-transcript", &t.display().to_string()]),
        &mut &b""[..]
    )
    .stderr
    .starts_with("Traceback"));
    assert_eq!(cli(&args(&["from-transcript"]), &mut &b""[..]).code, 2);
    assert_eq!(cli(&[], &mut &b""[..]).code, 2);
}
