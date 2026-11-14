//! A failure read from a session's result, the wait it is owed, and its resumed command.

use serde_json::json;

use super::{clamp, failed, first_line, resume_command, timegm, truthy, wait_for, BACKOFF};

#[test]
fn a_failure_is_an_exit_or_an_error_in_the_result() {
    assert!(failed(1, "{}"));
    assert!(!failed(0, "no json at all"));
    assert!(!failed(0, "{not json}"));
    assert!(!failed(0, "{\"subtype\": \"success\"}\nwarning\n"));
    assert!(!failed(0, "{\"subtype\": null, \"is_error\": 0}"));
    assert!(failed(0, "{\"is_error\": true}"));
    assert!(failed(0, "{\"subtype\": \"error_max_turns\"}"));
    assert!(failed(0, "{\"subtype\": false}"));
    for (v, t) in [
        (json!(null), false),
        (json!(false), false),
        (json!(2), true),
        (json!(0.0), false),
        (json!(""), false),
        (json!("x"), true),
        (json!([]), false),
        (json!([1]), true),
        (json!({}), false),
        (json!({"a": 1}), true),
    ] {
        assert_eq!(truthy(Some(&v)), t, "{v}");
    }
    assert!(!truthy(None));
}

#[test]
fn the_wait_is_the_named_reset_else_the_backoff() {
    let now = 1_763_100_000.0; // 2025-11-14T06:00:00Z
    assert_eq!(wait_for("limit|1763100600 reached", 0, now), 720);
    assert_eq!(wait_for("|1763000000", 0, now), 60);
    assert_eq!(wait_for("|1863000000", 0, now), 21_600);
    // 7am UTC that day is ahead; 5am has passed, so tomorrow's, capped at six hours (each figure Python 3.14's for the same text)
    assert_eq!(wait_for("Your limit resets 7am (UTC)", 0, now), 3720);
    assert_eq!(wait_for("resets at 7:30 AM", 0, now), 5520);
    assert_eq!(wait_for("resets 5am", 0, now), 21_600);
    assert_eq!(wait_for("reset 12pm", 0, now), 21_600);
    assert_eq!(wait_for("reset 6pm", 0, now), 21_600);
    assert_eq!(
        (
            wait_for("x", 0, now),
            wait_for("x", 1, now),
            wait_for("x", 2, now),
            wait_for("x", 9, now)
        ),
        (BACKOFF[0], BACKOFF[1], BACKOFF[2], BACKOFF[2])
    );
    assert_eq!(timegm(2025, 11, 14, 5, 20), 1_763_097_600);
    assert_eq!(timegm(2024, 2, 29, 0, 0), 1_709_164_800);
    assert_eq!((clamp(1.0), clamp(100.9), clamp(1e9)), (60, 100, 21_600));
}

#[test]
fn a_resume_names_the_session_and_its_returned_reports() {
    let cmd: Vec<String> = [
        "claude",
        "-p",
        "go",
        "-n",
        "x",
        "--session-id",
        "s1",
        "--tools",
        "Bash",
    ]
    .map(str::to_owned)
    .to_vec();
    let out = resume_command(&cmd, "s1", None);
    assert_eq!(&out[4..7], ["x", "--resume", "s1"]);
    assert!(
        out[2].starts_with("Continue the work of the brief you were given")
            && !out[2].contains("returned")
    );
    let back = resume_command(&out, "s1", Some("/log/returned.md"));
    assert!(back[2].ends_with("Every report is in /log/returned.md: read it, record each check from it, and do not dispatch them again."));
    // a command with no prompt after `-p` (the Python's IndexError; no queue the launch writes holds one) is left as it was
    let short: Vec<String> = ["claude", "-p"].map(str::to_owned).to_vec();
    assert_eq!(resume_command(&short, "s", None), short);
    assert_eq!(first_line("\n  \n  first one  \nsecond"), "first one");
    assert_eq!(first_line(" \n"), "no output");
    assert_eq!(first_line(&"y".repeat(200)).len(), 160);
}
