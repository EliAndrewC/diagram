//! The bundle of a scratch clone's hour: its events, transcripts and guard log, and the command line.

use std::path::Path;
use std::process::Command;

use serde_json::{json, Value};

use super::super::tool_yield::tests::put;
use super::*;

fn at(s: u32) -> String {
    format!(
        "2026-11-01T{:02}:{:02}:{:02}Z",
        8 + s / 3600,
        s / 60 % 60,
        s % 60
    )
}

fn t(s: u32) -> f64 {
    ts(&at(s)).unwrap()
}

fn rows(list: &[Value]) -> Vec<Row> {
    list.iter()
        .map(|v| v.as_object().unwrap().clone())
        .collect()
}

fn jsonl(list: &[Value]) -> String {
    list.iter().map(|v| v.to_string() + "\n").collect()
}

#[test]
fn the_small_readers() {
    let r = crate::checks::scratch("sb-small");
    assert!(lines(&r.join("missing")).unwrap().is_empty());
    put(&r, "a.jsonl", "{\"a\": 1}\u{2028}{\"b\": 2}\n[1]\n");
    assert_eq!(lines(&r.join("a.jsonl")).unwrap().len(), 2);
    let locked = r.join("a.jsonl");
    std::fs::set_permissions(&locked, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    assert!(lines(&locked).is_err());
    assert_eq!(iso(t(59) + 0.999_999_7), "2026-11-01 08:01 UTC");
    assert_eq!(iso(-0.000_000_7), "1970-01-01 00:00 UTC");
    assert_eq!(iso(0.5), "1970-01-01 00:00 UTC");
    assert_eq!(compact(t(61) + 0.9), "20261101T080101");
    assert!(replay_time("2026-11-01T08:00:00").is_ok());
    assert!(replay_time("2026-11-01T08:00:00+00:00").is_ok());
    assert!(replay_time("2026-11-01T08:00:00-05:00").is_err());
    assert_eq!(or_none(&[]), "(none)");
    let mut state = Map::new();
    assert!((checkpoint_since(&state, 7200.0) - 3600.0).abs() < f64::EPSILON);
    state.insert("since".to_owned(), json!(5.5));
    assert!((checkpoint_since(&state, 7200.0) - 5.5).abs() < f64::EPSILON);
}

#[test]
fn the_dispatches_and_the_sessions() {
    let e = rows(&[
        json!({"ev": "SubagentStart"}),
        json!({"t": at(1), "ev": "SubagentStart", "aid": "a", "agent": "quote-check", "cat": "c"}),
        json!({"t": at(2), "ev": "SubagentStart", "aid": "b"}),
        json!({"t": at(3), "ev": "SubagentStart", "aid": "a", "agent": "source-reader"}),
        json!({"t": at(99), "ev": "SubagentStart", "aid": "late"}),
        json!({"t": at(70), "ev": "SubagentStop", "aid": "a", "verdict": "READ"}),
        json!({"t": at(71), "ev": "SubagentStop", "aid": "zz"}),
        json!({"t": at(4), "sid": "s2"}),
        json!({"t": at(5), "sid": "s1"}),
        json!({"t": at(6), "sid": "s1"}),
        json!({"t": at(999), "sid": "s3"}),
        json!({"sid": "s4"}),
    ]);
    let d = dispatches(&e, t(0), t(60)).unwrap();
    assert_eq!(
        d,
        [
            "- 08:00 source-reader (): 67 s, READ",
            "- 08:00 ? (): still running"
        ]
    );
    assert_eq!(sessions_of(&e, t(0), t(60)).unwrap(), ["s1", "s2"]);
    let bad = rows(&[json!({"t": "x", "sid": "s"})]);
    assert!(dispatches(&bad, 0.0, 1.0).is_err() && sessions_of(&bad, 0.0, 1.0).is_err());
}

#[test]
fn the_refusals_of_the_sessions_in_the_window() {
    let r = crate::checks::scratch("sb-refusals");
    let log = r.join("guard-log");
    put(
        &log,
        "20261101T080010-a.json",
        r#"{"event": "blocked", "guard": "g", "rule": "r", "detail": "d", "session": "s1"}"#,
    );
    put(
        &log,
        "20261101T080011-a.json",
        r#"{"event": "refused", "sid": "s2"}"#,
    );
    put(
        &log,
        "20261101T080012-a.json",
        r#"{"event": "blocked", "sid": "other"}"#,
    );
    put(
        &log,
        "20261101T080013-a.json",
        r#"{"event": "escaped", "sid": "s1"}"#,
    );
    put(&log, "20261101T080014-a.json", "nope");
    put(&log, "20261101T090000-a.json", r#"{"event": "blocked"}"#);
    put(&log, "20261101T080015-a.txt", r#"{"event": "blocked"}"#);
    std::fs::create_dir_all(log.join("20261101T080016-d.json")).unwrap();
    let sids = ["s1".to_owned(), "s2".to_owned()];
    assert_eq!(
        refusals(&sids, t(0), t(60), &log),
        ["- 08:00 g: r - d", "- 08:00 None:  - "]
    );
    assert_eq!(refusals(&[], t(0), t(60), &log).len(), 3);
}

fn transcript(s: u32) -> String {
    jsonl(&[
        json!({"type": "user", "timestamp": at(s), "message": {"content": [{"type": "tool_result"}]}}),
        json!({"type": "assistant", "timestamp": at(s + 2), "requestId": format!("r{s}"),
               "message": {"content": [{"type": "text", "text": "hi"}], "usage": {"input_tokens": 9}}}),
        json!({"type": "summary"}),
    ])
}

#[test]
fn the_transcripts_of_the_sessions() {
    let r = crate::checks::scratch("sb-transcripts");
    let projects = r.join("projects");
    put(&projects, "p1/s1.jsonl", &transcript(1));
    put(&projects, "p2/s2.jsonl", &transcript(10));
    put(&projects, "p0/s2.jsonl", "");
    let old = std::fs::File::options()
        .write(true)
        .open(projects.join("p0/s2.jsonl"))
        .unwrap();
    old.set_modified(std::time::SystemTime::UNIX_EPOCH).unwrap();
    assert!(transcript_of("", &projects).unwrap().is_none());
    assert!(transcript_of("nope", &projects).unwrap().is_none());
    assert_eq!(
        transcript_of("s1", &projects).unwrap().unwrap(),
        projects.join("p1/s1.jsonl")
    );
    let sids = ["s2".to_owned(), "s1".to_owned(), "gone".to_owned()];
    let (records, read, missing) = records_of(&sids, None, &projects).unwrap();
    assert_eq!(
        (read.len(), missing.as_slice()),
        (2, ["gone".to_owned()].as_slice())
    );
    // a record with no time sorts first, as the Python's key of 0.0 put it
    assert_eq!(records[0]["_sid"], "s2");
    assert!(!records[0].contains_key("timestamp") && records.len() == 6);
    let (alone, read, _) = records_of(&[], Some(&projects.join("p1/s1.jsonl")), &projects).unwrap();
    assert_eq!((alone.len(), read), (3, vec!["s1".to_owned()]));
    let (one, ..) = records_of(&["s1".to_owned()], None, &projects).unwrap();
    assert!(!one[1].contains_key("_sid"));
    put(&projects, "p3/s3.jsonl", "{\"timestamp\": 5}\n");
    assert!(records_of(&["s3".to_owned()], None, &projects).is_err());
    std::os::unix::fs::symlink(r.join("nowhere"), projects.join("p3/s4.jsonl")).unwrap();
    assert!(transcript_of("s4", &projects).is_err());
    let gaps = silent_minutes(&records, t(0), t(900)).unwrap();
    assert_eq!(gaps, ["08:00-08:15"]);
    assert!((model_time(&records, t(0), t(60)).unwrap() - 4.0).abs() < 1e-9);
    assert!(model_time(&rows(&[json!({"timestamp": 1})]), 0.0, 1.0).is_err());
    assert!(silent_minutes(&rows(&[json!({"timestamp": 1})]), 0.0, 1.0).is_err());
}

#[test]
fn the_time_names_each_command_and_fails_where_a_call_took_no_time() {
    let call = |s: u32, id: &str, cmd: &str| json!({"type": "assistant", "timestamp": at(s), "message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": cmd}}]}});
    let done = |s: u32, id: &str| json!({"type": "user", "timestamp": at(s), "message": {"content": [{"type": "tool_result", "tool_use_id": id}]}});
    let r = rows(&[call(0, "a", "make quick"), done(30, "a")]);
    let text = time_md(&r, 2, t(0), t(600)).unwrap();
    assert!(
        text.contains("summed over 2 sessions")
            && text.contains("-   0.5 min x1   make quick (longest 30 s: `make quick`)")
    );
    assert!(time_md(&r, 1, t(0), t(600))
        .unwrap()
        .contains("wall 10 min; the model 0.0 min; tools 0.5 min; the rest"));
    assert!(time_md(&[], 1, t(0), t(0))
        .unwrap()
        .contains("(no tool call in the window)"));
    let same = rows(&[call(0, "a", "ls"), done(0, "a")]);
    assert!(time_md(&same, 1, t(0), t(60))
        .unwrap_err()
        .starts_with("KeyError"));
    let neg = rows(&[call(10, "a", "ls"), done(0, "a")]);
    assert!(time_md(&neg, 1, t(0), t(60)).is_err());
}

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

/// A clone with feature `9-x`'s events, a session's transcript and the guard log, under a scratch home.
fn clone_with_an_hour(r: &Path) -> (PathBuf, Env) {
    let root = r.join("clone");
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q"]);
    put(
        &root,
        ".git/l7r-events/9-x.jsonl",
        &jsonl(&[json!({"t": at(1), "sid": "s1", "ev": "SubagentStart", "aid": "a"})]),
    );
    put(
        &root,
        ".git/l7r-events/other.jsonl",
        &jsonl(&[
            json!({"t": at(2), "sid": "s1"}),
            json!({"t": at(3), "sid": "gone-session"}),
        ]),
    );
    let open = (0..35)
        .map(|i| format!("- [ ] T{i:02}\n"))
        .collect::<Vec<_>>()
        .concat();
    put(&root, "specs/9-x/tasks.md", &format!("- [x] T99\n{open}"));
    let home = r.join("home");
    put(&home, ".claude/projects/p/s1.jsonl", &transcript(1));
    put(
        &home,
        ".claude/guard-log/20261101T080005-a.json",
        r#"{"event": "blocked", "guard": "g", "sid": "s1"}"#,
    );
    (root, Env { home, now: t(3600) })
}

#[test]
fn the_bundle_holds_every_file() {
    let r = crate::checks::scratch("sb-build");
    let (root, env) = clone_with_an_hour(&r);
    let out = r.join("out");
    let manifest = build("hour:9-x@1", &root, &out, (t(0), t(900)), None, &env).unwrap();
    assert_eq!(manifest, out.join("MANIFEST.md"));
    let read = |f: &str| std::fs::read_to_string(out.join(f)).unwrap();
    assert!(
        read("MANIFEST.md").starts_with("# Step-back bundle - hour:9-x@1\n")
            && read("MANIFEST.md")
                .contains("feature 9-x, 2026-11-01 08:00 UTC to 2026-11-01 08:15 UTC.")
    );
    assert!(read("MANIFEST.md").contains("`{\"ruling\": ...,"));
    assert_eq!(
        read("dispatches.md"),
        "# Subagents dispatched\n\n- 08:00 ? (): still running\n"
    );
    assert_eq!(read("refusals.md"), "# Guard refusals\n\n- 08:00 g:  - \n");
    assert_eq!(read("task.md").lines().count(), 32);
    assert!(read("words.md").starts_with("# The sessions' own words\n\nsessions read: s1; left out (no transcript found): gone-ses; NO WORDS FOUND for 08:00-08:15 of the window"));
    assert_eq!(
        read("fix-yield.md"),
        "# Each tooling fix's yield\n\n(no tooling fix ruled)\n"
    );
    let replay = build(
        "hour:9-x@1",
        &root,
        &r.join("out2"),
        (t(0), t(60)),
        Some(&env.home.join(".claude/projects/p/s1.jsonl")),
        &env,
    )
    .unwrap();
    assert!(std::fs::read_to_string(replay.with_file_name("words.md"))
        .unwrap()
        .contains("SAID: hi"));
}

#[test]
fn a_bundle_fails_where_the_python_raised_and_cuts_its_words() {
    let r = crate::checks::scratch("sb-build-bad");
    let (root, env) = clone_with_an_hour(&r);
    std::fs::create_dir_all(r.join("blocked/time.md")).unwrap();
    for name in [
        "dispatches.md",
        "refusals.md",
        "task.md",
        "words.md",
        "fix-yield.md",
        "MANIFEST.md",
    ] {
        let out = r.join(format!("blocked-{name}"));
        std::fs::create_dir_all(out.join(name)).unwrap();
        assert!(build("hour:9-x@1", &root, &out, (t(0), t(60)), None, &env).is_err());
    }
    assert!(build(
        "hour:9-x@1",
        &root,
        &r.join("blocked"),
        (t(0), t(60)),
        None,
        &env
    )
    .is_err());
    let said = "w".repeat(41_000);
    put(
        &env.home,
        ".claude/projects/p/s1.jsonl",
        &jsonl(&[
            json!({"type": "assistant", "timestamp": at(1), "message": {"content": [{"type": "text", "text": said}]}}),
        ]),
    );
    let cut = build(
        "hour:9-x@1",
        &root,
        &r.join("cut"),
        (t(0), t(60)),
        None,
        &env,
    )
    .unwrap();
    assert!(std::fs::read_to_string(cut.with_file_name("words.md"))
        .unwrap()
        .contains("; cut to the cap: the hour's earliest words"));
    put(&r, "file", "");
    assert!(build(
        "hour:9-x@1",
        &root,
        &r.join("file"),
        (t(0), t(60)),
        None,
        &env
    )
    .is_err());
    put(&root, ".git/l7r-events/9-x.jsonl", "{\"t\": \"bad\"}\n");
    assert!(build(
        "hour:9-x@1",
        &root,
        &r.join("out5"),
        (t(0), t(60)),
        None,
        &env
    )
    .is_err());
    assert!(r.join("out5/time.md").is_file() && !r.join("out5/dispatches.md").exists());
    let plain = r.join("plain");
    std::fs::create_dir_all(&plain).unwrap();
    let none = build(
        "hour:nothing@1",
        &plain,
        &r.join("out3"),
        (t(0), t(60)),
        None,
        &env,
    )
    .unwrap();
    assert!(std::fs::read_to_string(none.with_file_name("words.md"))
        .unwrap()
        .contains("sessions read: none"));
    put(&root, "specs/9-x/tasks.md", "");
    std::fs::write(root.join("specs/9-x/tasks.md"), b"\xff").unwrap();
    assert!(build(
        "hour:9-x@1",
        &root,
        &r.join("out4"),
        (t(0), t(60)),
        None,
        &env
    )
    .is_err());
}

#[test]
fn the_command_line() {
    let r = crate::checks::scratch("sb-cli");
    let (root, env) = clone_with_an_hour(&r);
    let ask = |words: &[&str]| {
        cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &env,
        )
    };
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(ask(&["--bogus"]).code, 2);
    assert_eq!(
        ask(&["round:x"]).stderr,
        "stepback-bundle: the trigger is hour:<feature>@<n>\n"
    );
    let out = r.join("o");
    let (rs, os) = (root.display().to_string(), out.display().to_string());
    let ok = ask(&[
        "hour:9-x@1",
        "--root",
        &rs,
        "--since",
        "2026-11-01T08:00:00",
        "--until",
        "2026-11-01T08:15:00Z",
        "--out",
        &os,
    ]);
    assert_eq!(
        ok.stdout,
        format!("step-back: hour:9-x@1 - dispatch `round-arbiter` on {os}/MANIFEST.md\n")
    );
    let t1 = r.join("projects-x.jsonl");
    put(&r, "projects-x.jsonl", &transcript(1));
    assert_eq!(
        ask(&[
            "hour:9-x@1",
            "--root",
            &rs,
            "--transcript",
            t1.to_str().unwrap(),
            "--out",
            &os
        ])
        .code,
        0
    );
    assert_eq!(
        ask(&["hour:9-x@1", "--root", &rs, "--since", "bad", "--out", &os]).code,
        1
    );
    // the default bundle directory, named by the trigger so no other run's is touched, then removed
    let unique = format!("hour:t120-{}@1", std::process::id());
    let plain = r.join("not-a-repo");
    std::fs::create_dir_all(&plain).unwrap();
    let got = ask(&[&unique, "--root", plain.to_str().unwrap()]);
    assert_eq!(got.code, 0);
    std::fs::remove_dir_all(format!("{OUT}/step-back-t120-{}-1", std::process::id())).unwrap();
}
