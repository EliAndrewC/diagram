//! The decider over a scratch tree and clone, the attempts written in process to the clone's log (feature 449 T145; `tests/hooks/test-blocked-fetch-hooks.sh`, replayed through the shim, runs the binary).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{archived, clone_of, decide, fetch_of, judge, sans_heredocs, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::blocked::host;
use crate::shared::session::Session;
use crate::shared::sha256;

const LIST: &str = r#"{"domains": [{"domain": "Bad.Example.", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

/// A tree holding the list, and a clone beside it whose attempts log starts with `log`.
fn world(tag: &str, log: &str) -> (crate::shared::tempdir::Held<PathBuf>, String) {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-fetch-{tag}"));
    std::fs::create_dir_all(d.join("tree/research")).unwrap();
    std::fs::create_dir_all(d.join(".clones/c/.git")).unwrap();
    std::fs::create_dir_all(d.join(".clones/c/research")).unwrap();
    std::fs::create_dir_all(d.join("mirror/.git")).unwrap();
    let (keep, d) = {
        let canon = d.canonicalize().unwrap();
        (d, canon)
    };
    std::fs::write(d.join("tree/research/blocked-domains.json"), LIST).unwrap();
    std::fs::write(d.join(".clones/c/research/source-attempts.jsonl"), log).unwrap();
    let clone = d.join(".clones/c").to_string_lossy().into_owned();
    (keep.hold(d), clone)
}

fn event(tool: &str, input: &Value, at: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    }
}

fn run(d: &Path, e: &Event) -> Vec<Answer> {
    let ctx = Ctx {
        here: d.to_path_buf(),
        tree: d.join("tree"),
    };
    judge(e, &Session::from_input(&e.input), &ctx)
}

fn bash(d: &Path, cmd: &str, at: &str) -> Vec<Answer> {
    run(d, &event("Bash", &json!({"command": cmd}), at))
}

fn web(d: &Path, url: &str, at: &str) -> Vec<Answer> {
    run(
        d,
        &event(
            "WebFetch",
            &json!({"url": url, "prompt": " the walls "}),
            at,
        ),
    )
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

/// The attempts the clone's log holds, one JSON line each.
fn logged(d: &Path) -> Vec<Value> {
    std::fs::read_to_string(d.join(".clones/c/research/source-attempts.jsonl"))
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

#[test]
fn a_blocked_domain_is_refused_at_every_route() {
    let (d, at) = world("block", "");
    assert!(refused(&web(&d, "https://bad.example/p", &at), "BLOCKED: this WebFetch refused: https://bad.example/p is on the blocked list (blocked-domains.json: bad.example - machine text; approved 2026-10-02: block it)"));
    assert!(refused(
        &web(&d, "https://www.bad.example/p", &at),
        "blocked list"
    ));
    assert!(refused(
        &bash(&d, "curl -sL https://bad.example/x | head", &at),
        "this Bash refused"
    ));
    assert!(refused(
        &bash(&d, "wget -qO- bad.example/x", &at),
        "blocked list"
    ));
    assert!(refused(
        &bash(&d, "make source-pages URL=https://bad.example/x", &at),
        "blocked list"
    ));
    assert!(refused(
        &bash(
            &d,
            "python3 - <<'EOF'\ns = \" curl -sL https://bad.example/x\"\nEOF",
            &at
        ),
        "blocked list"
    ));
    assert!(logged(&d).is_empty());
}

#[test]
fn what_is_not_a_fetch_of_a_blocked_domain_passes() {
    let (d, at) = world("pass", "");
    assert!(bash(&d, "grep -rn bad.example docs/x.md", &at).is_empty());
    assert!(bash(&d, "ls -la", &at).is_empty());
    assert!(bash(&d, "curl -sL https://notbad.example/x", &at).is_empty());
    assert!(run(&d, &event("Read", &json!({"file_path": "x"}), &at)).is_empty());
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "WebFetch"}),
    };
    assert!(run(&d, &bare).is_empty());
}

#[test]
fn a_fetch_is_recorded_and_its_earlier_attempts_come_back() {
    let before = r#"{"url": "a.org/1", "raw": "https://a.org/1", "key": "", "question": "0012", "sought": "the dike", "outcome": "not-found", "date": "2026-10-01", "feature": "312", "route": "webfetch"}"#;
    let (d, at) = world("seen", &format!("{before}\n"));
    let got = web(&d, "https://a.org/1", &at);
    assert!(
        matches!(&got[..], [Answer::Notice(t)] if t == "attempts: https://a.org/1 - 1 earlier attempt(s):\n  2026-10-01 Q 0012: not-found - the dike")
    );
    let said = logged(&d);
    assert_eq!(said.len(), 2);
    assert_eq!(said[1]["sought"], "the walls");
    assert_eq!(said[1]["route"], "webfetch");
    assert_eq!(said[1]["question"], "unknown");
    let (d2, at2) = world("first", "");
    assert!(web(&d2, "https://a.org/1", &at2).is_empty());
    assert!(run(
        &d2,
        &event("WebFetch", &json!({"url": "https://a.org/2"}), &at2)
    )
    .is_empty());
    assert_eq!(logged(&d2)[1]["sought"], "(no prompt)");
    bash(&d2, "curl -sL http://a.org/p; ls", &at2);
    let last = logged(&d2).pop().unwrap();
    assert_eq!(
        (last["route"].as_str(), last["raw"].as_str()),
        (Some("bash"), Some("http://a.org/p"))
    );
}

#[test]
fn what_the_guard_does_not_record() {
    let (d, at) = world("norec", "");
    bash(&d, "make source-pages URL=https://a.org/b", &at);
    bash(
        &d,
        "python3 - <<'EOF'\ns = \" curl -sL https://a.org/h\"\nEOF",
        &at,
    );
    bash(
        &d,
        "for n in 3 9; do curl -sL https://a.org/p-$n.pdf; done",
        &at,
    );
    web(&d, "https://a.org/c", &d.join("mirror").to_string_lossy());
    web(&d, "", &at);
    bash(&d, "wget -qO- a.org/x", &at);
    assert!(logged(&d).is_empty());
}

#[test]
fn an_archived_page_is_pointed_at_the_archive() {
    let (d, at) = world("arch", "");
    let uid = sha256::hex(b"https://held.org/p&x");
    let dir = Path::new(&at).join("research/archive").join(&uid[..2]);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join(format!("{}.json", &uid[..12])), "{}").unwrap();
    assert!(
        matches!(&web(&d, "https://held.org/p&amp;x", &at)[..], [Answer::Notice(t)] if t.contains("make archive-find URL='https://held.org/p&amp;x'"))
    );
    assert!(archived(Path::new(&at), "https://held.org/p&x#frag"));
    assert!(archived(Path::new(&at), "https://held.org/p&x.,"));
    assert!(!archived(Path::new(&at), "https://held.org/(p)"));
}

#[test]
fn a_list_that_cannot_be_trusted_or_a_failed_read_passes() {
    let (d, at) = world("list", "");
    std::fs::write(
        Path::new(&at).join("research/source-attempts.jsonl"),
        b"\xff\n",
    )
    .unwrap();
    assert!(web(&d, "https://a.org/1", &at).is_empty());
    std::fs::remove_file(d.join("tree/research/blocked-domains.json")).unwrap();
    assert!(web(&d, "https://bad.example/1", &at).is_empty());
    std::fs::write(
        d.join("tree/research/blocked-domains.json"),
        r#"{"domains": [{"domain": "x.org", "reason": "y"}]}"#,
    )
    .unwrap();
    assert!(web(&d, "https://x.org/1", &at).is_empty());
    std::fs::write(
        d.join("tree/research/blocked-domains.json"),
        r#"{"domains": [{"domain": "", "reason": "y", "approved": {"date": "d", "words": "w"}}]}"#,
    )
    .unwrap();
    assert!(web(&d, "https://x.org/1", &at).is_empty());
    std::fs::write(d.join("tree/research/blocked-domains.json"), "{").unwrap();
    assert!(web(&d, "https://x.org/1", &at).is_empty());
    std::fs::write(d.join("tree/research/blocked-domains.json"), "{}").unwrap();
    assert!(web(&d, "https://x.org/1", &at).is_empty());
}

#[test]
fn the_small_readers() {
    assert_eq!(
        host("HTTPS://user@WWW.Bad.example:8080/p?q#f"),
        "www.bad.example"
    );
    assert_eq!(host("bad.example/x"), "bad.example");
    assert_eq!(host("http://[::1]:80/x"), "::1");
    assert_eq!(sans_heredocs("a <<EOF | b\nc\nEOF\nd"), "a \nd");
    assert_eq!(clone_of("/no/such", Path::new("/")), None);
    let call = |c: &str| fetch_of(&event("Bash", &json!({"command": c}), "/"));
    assert!(
        call("xh a.org").is_some()
            && call("python3 -m urllib a.org").is_some()
            && call("make -Cdir reserve KEY=x").is_some()
    );
    assert!(call("echo curl").is_none());
    // feature 451 T02: a fetching target read by the one make detector - a mention is none, a timed run is one
    assert!(call("echo make archive").is_none());
    assert!(call("(timeout 60 make reserve KEY=x) &").is_some());
    let e = event("Bash", &json!({"command": "ls"}), "/");
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

#[test]
fn a_url_tried_many_times_says_its_first_attempt_and_the_command_for_the_rest() {
    let head = "attempts: https://a.org/1 - 40 earlier attempt(s):".to_owned();
    let verdict = "  filter verdict: KEEP".to_owned();
    let tried: Vec<String> = (1..=40)
        .map(|i| format!("  2026-10-01 Q 00{i:02}: not-found - the dike"))
        .collect();
    let said = super::attempts_said(
        "https://a.org/1",
        &[vec![head.clone(), verdict.clone()], tried.clone()].concat(),
    );
    assert_eq!(
        said,
        [
            head.clone(),
            verdict,
            tried[0].clone(),
            "  and 39 more: `make attempts URL='https://a.org/1'`".to_owned()
        ]
        .join("\n")
    );
    let one = super::attempts_said("https://a.org/1", &[head.clone(), tried[0].clone()]);
    assert_eq!(one, [head, tried[0].clone()].join("\n"));
    assert_eq!(super::attempts_said("https://a.org/1", &[]), "");
}

/// 451 T170: a command fetching several URLs tried before says the first one's attempts and keeps every one's in a file.
#[test]
fn several_urls_tried_before_say_the_first_and_keep_the_rest() {
    let row = |n: u32| {
        format!(
            r#"{{"url": "a.org/{n}", "raw": "https://a.org/{n}", "key": "", "question": "0012", "sought": "the dike", "outcome": "not-found", "date": "2026-10-01", "feature": "312", "route": "webfetch"}}"#
        )
    };
    let (d, at) = world("several", &format!("{}\n{}\n", row(1), row(2)));
    let got = bash(&d, "curl -sL https://a.org/1 https://a.org/2", &at);
    let first_and_kept = |t: &str| {
        let kept = t
            .split("more URL(s)' attempts: `cat ")
            .nth(1)
            .unwrap_or_default()
            .trim_end_matches('`');
        t.starts_with("attempts: https://a.org/1 - 1 earlier attempt(s):")
            && !t.contains("a.org/2 -")
            && std::fs::read_to_string(kept)
                .unwrap_or_default()
                .contains("attempts: https://a.org/2 - 1 earlier attempt(s):")
    };
    let said = matches!(&got[..], [Answer::Notice(t)] if first_and_kept(t));
    assert!(said, "{got:?}");
}

/// 451 T170: a URL tried before and archived says both, the archive's pointer on a line of its own after the attempts.
#[test]
fn a_url_tried_before_and_archived_says_its_attempts_then_the_archive() {
    let row = r#"{"url": "held.org/q", "raw": "https://held.org/q", "key": "", "question": "0012", "sought": "the dike", "outcome": "not-found", "date": "2026-10-01", "feature": "312", "route": "webfetch"}"#;
    let (d, at) = world("arch-tried", &format!("{row}\n"));
    let uid = sha256::hex(b"https://held.org/q");
    let dir = Path::new(&at).join("research/archive").join(&uid[..2]);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join(format!("{}.json", &uid[..12])), "{}").unwrap();
    let got = web(&d, "https://held.org/q", &at);
    let said = matches!(&got[..], [Answer::Notice(t)] if t.starts_with("attempts: https://held.org/q - 1 earlier attempt(s):")
        && t.contains("\narchive: a copy of https://held.org/q is archived"));
    assert!(said, "{got:?}");
}
