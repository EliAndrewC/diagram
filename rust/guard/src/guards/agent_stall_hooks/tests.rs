//! The decider on the suite's shapes (`tests/hooks/test-agent-stall-hooks.sh`, replayed through the shim, is the verdict).

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use serde_json::json;

use super::{cli, decide, judge, last_type, report, scan, Limits};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn dir(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-stall-{tag}"));
    let d = root.join("sess/subagents");
    std::fs::create_dir_all(&d).unwrap();
    root.hold(d)
}

/// A transcript ending on a record of `kind`, last written `age` seconds ago.
fn agent(d: &Path, id: &str, kind: &str, age: u64) {
    let p = d.join(format!("agent-{id}.jsonl"));
    std::fs::write(
        &p,
        format!("{{\"type\":\"assistant\"}}\n{{\"type\":\"{kind}\"}}\n"),
    )
    .unwrap();
    let f = std::fs::File::options().write(true).open(&p).unwrap();
    f.set_modified(SystemTime::now() - Duration::from_secs(age))
        .unwrap();
}

fn limits() -> Limits {
    Limits::from_env(&|_| None)
}

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_limits_read_the_environment() {
    let l = limits();
    assert!(l.stale == 300 && l.recent == 172_800 && l.ticks.is_none());
    let set = Limits::from_env(&|k| {
        (k == "AGENT_STALE_S" || k == "AGENT_TICK_S" || k == "AGENT_WATCH_TICKS")
            .then(|| "2".to_owned())
    });
    assert!(set.stale == 2 && set.ticks == Some(2));
}

#[test]
fn only_a_transcript_ending_on_a_user_record_and_standing_still_is_stalled() {
    let d = dir("shape");
    agent(&d, "stall", "user", 600);
    agent(&d, "done", "assistant", 600);
    agent(&d, "live", "user", 0);
    agent(&d, "old", "user", 259_200);
    std::fs::write(d.join("notes.txt"), "").unwrap();
    let got = report(&d, &limits(), None);
    assert!(
        got.len() == 1
            && got[0].contains("STALLED stall:")
            && got[0].contains("TaskStop")
            && got[0].ends_with(&format!("ack {} stall", d.display()))
    );
    assert!(report(Path::new("/no/such/dir"), &limits(), None).is_empty());
}

#[test]
fn an_acked_stall_is_silent_and_a_watch_says_each_stall_once() {
    let d = dir("once");
    agent(&d, "a", "user", 600);
    let mut seen = HashSet::new();
    assert_eq!(report(&d, &limits(), Some(&mut seen)).len(), 1);
    assert!(report(&d, &limits(), Some(&mut seen)).is_empty());
    agent(&d, "a", "user", 0);
    assert!(report(&d, &limits(), Some(&mut seen)).is_empty() && seen.is_empty());
    agent(&d, "a", "user", 600);
    assert_eq!(report(&d, &limits(), Some(&mut seen)).len(), 1);
    assert_eq!(cli(&args(&["ack", d.to_str().unwrap(), "a"])).code, 0);
    assert!(report(&d, &limits(), None).is_empty());
}

#[test]
fn the_last_record_is_read_whole_from_the_end() {
    let d = dir("last");
    let long = format!(
        "{{\"type\":\"user\",\"x\":\"{}\"}}\n\n",
        "y".repeat(200_000)
    );
    let p = d.join("agent-long.jsonl");
    std::fs::write(&p, format!("{{\"type\":\"assistant\"}}\n{long}")).unwrap();
    assert_eq!(last_type(&p).as_deref(), Some("user"));
    let only = d.join("agent-only.jsonl");
    std::fs::write(&only, "{\"type\":\"user\"}").unwrap();
    assert_eq!(last_type(&only).as_deref(), Some("user"));
    for (name, text) in [
        ("empty", ""),
        ("bad", "{"),
        ("untyped", "{}"),
        ("blank", "{\"type\":\"\"}"),
    ] {
        let q = d.join(name);
        std::fs::write(&q, text).unwrap();
        assert_eq!(last_type(&q), None);
    }
    assert_eq!(last_type(&d.join("missing")), None);
    let folder = d.join("agent-folder.jsonl");
    std::fs::create_dir(&folder).unwrap();
    assert_eq!(last_type(&folder), None);
    assert!(scan(&d, 0, u64::MAX)
        .iter()
        .any(|(id, _, kind)| id == "folder" && kind == "-"));
}

#[test]
fn a_prompt_reports_the_sessions_stalls_and_records_them() {
    let d = dir("prompt");
    let top = d.parent().unwrap().to_string_lossy().into_owned();
    let event = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({"transcript_path": format!("{top}.jsonl")}),
    };
    let s = Session::from_input(&event.input);
    let l = limits();
    assert!(judge(&event, &s, &l).is_empty());
    agent(&d, "s", "user", 600);
    let got = judge(&event, &s, &l);
    assert!(
        matches!(&got[..], [Answer::Print(t)] if t.starts_with("agent-stall: STALLED s:") && t.ends_with("(scripts/hooks/agent-stall-hooks.sh)."))
    );
    let none = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({}),
    };
    assert!(decide(&none, &Session::from_input(&none.input)).is_empty());
}

#[test]
fn the_command_line_answers_each_mode() {
    let d = dir("cli");
    let at = d.to_str().unwrap();
    agent(&d, "w", "user", 600);
    agent(&d, "f", "assistant", 600);
    let check = cli(&args(&["check", at]));
    assert!(
        check.code == 0 && check.stdout.starts_with("STALLED w:") && check.stdout.ends_with('\n')
    );
    assert_eq!(cli(&args(&["pending", at])).stdout, "w\n");
    assert_eq!(cli(&args(&["ack", "/proc/nope/x", "i"])).code, 1);
    std::env::set_var("AGENT_WATCH_TICKS", "2");
    std::env::set_var("AGENT_TICK_S", "0");
    assert_eq!(cli(&args(&["watch", at])).code, 0);
    assert_eq!(cli(&args(&["ack", at])).code, 2);
    assert_eq!(cli(&args(&[])).code, 2);
}
