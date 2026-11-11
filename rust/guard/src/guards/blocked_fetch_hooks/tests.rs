//! The decider with `attempts.py` stubbed by a shell script (`tests/hooks/test-blocked-fetch-hooks.sh`, replayed through the shim, runs the real one).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{archived, clone_of, decide, fetch_of, host, judge, sans_heredocs, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::sha256;

const LIST: &str = r#"{"domains": [{"domain": "Bad.Example.", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

const NOTHING: &str = r#"[{"lines": [], "plain": "x"}]"#;

/// A tree holding the list and a stubbed `attempts.py`, and a clone beside it. The stub prints `reply` and keeps its arguments.
fn world(tag: &str, reply: &str) -> (crate::shared::tempdir::Held<PathBuf>, String) {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-fetch-{tag}"));
    std::fs::create_dir_all(d.join("tree/research")).unwrap();
    std::fs::create_dir_all(d.join("tree/scripts/record")).unwrap();
    std::fs::create_dir_all(d.join(".clones/c/.git")).unwrap();
    std::fs::create_dir_all(d.join("mirror/.git")).unwrap();
    let (keep, d) = {
        let canon = d.canonicalize().unwrap();
        (d, canon)
    };
    std::fs::write(d.join("tree/research/blocked-domains.json"), LIST).unwrap();
    let body = format!(
        "echo \"$@\" > {}/args\nprintf '%s' '{reply}'\n",
        d.display()
    );
    std::fs::write(d.join("tree/scripts/record/attempts.py"), body).unwrap();
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
        python: "sh",
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

fn args(d: &Path) -> String {
    std::fs::read_to_string(d.join("args")).unwrap_or_default()
}

#[test]
fn a_blocked_domain_is_refused_at_every_route() {
    let (d, at) = world("block", NOTHING);
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
    assert_eq!(args(&d), "");
}

#[test]
fn what_is_not_a_fetch_of_a_blocked_domain_passes() {
    let (d, at) = world("pass", NOTHING);
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
    let (d, at) = world(
        "seen",
        r#"[{"lines": ["attempts: u - 1 earlier attempt(s):", "  the dike"], "plain": "x"}]"#,
    );
    let got = web(&d, "https://a.org/1", &at);
    assert!(
        matches!(&got[..], [Answer::Notice(t)] if t == "attempts: u - 1 earlier attempt(s):\n  the dike")
    );
    let said = args(&d);
    assert!(
        said.contains("seen --root")
            && said.contains("--sought=the walls --route webfetch --record -- https://a.org/1")
    );
    let (d2, at2) = world("first", NOTHING);
    assert!(web(&d2, "https://a.org/1", &at2).is_empty());
    assert!(run(
        &d2,
        &event("WebFetch", &json!({"url": "https://a.org/2"}), &at2)
    )
    .is_empty());
    assert!(args(&d2).contains("--sought=(no prompt) "));
    bash(&d2, "curl -sL http://a.org/p; ls", &at2);
    assert!(args(&d2).contains("--route bash --record -- http://a.org/p"));
}

#[test]
fn what_the_guard_does_not_record() {
    let (d, at) = world("norec", NOTHING);
    bash(&d, "make source-pages URL=https://a.org/b", &at);
    assert!(!args(&d).contains("--record") && args(&d).contains("https://a.org/b"));
    bash(
        &d,
        "python3 - <<'EOF'\ns = \" curl -sL https://a.org/h\"\nEOF",
        &at,
    );
    assert!(!args(&d).contains("--record"));
    std::fs::remove_file(d.join("args")).unwrap();
    bash(
        &d,
        "for n in 3 9; do curl -sL https://a.org/p-$n.pdf; done",
        &at,
    );
    assert_eq!(args(&d), "");
    web(&d, "https://a.org/c", &d.join("mirror").to_string_lossy());
    web(&d, "", &at);
    bash(&d, "wget -qO- a.org/x", &at);
    assert_eq!(args(&d), "");
}

#[test]
fn an_archived_page_is_pointed_at_the_archive() {
    let (d, at) = world("arch", r#"[{"lines": [], "plain": "https://held.org/p"}]"#);
    let uid = sha256::hex(b"https://held.org/p");
    let dir = Path::new(&at).join("research/archive").join(&uid[..2]);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join(format!("{}.json", &uid[..12])), "{}").unwrap();
    assert!(
        matches!(&web(&d, "https://held.org/p", &at)[..], [Answer::Notice(t)] if t.contains("make archive-find URL='https://held.org/p'"))
    );
    assert!(archived(Path::new(&at), "https://held.org/p#frag"));
    assert!(archived(Path::new(&at), "https://held.org/p.,"));
    assert!(archived(Path::new(&at), "https://held.org/p)"));
    assert!(!archived(Path::new(&at), "https://held.org/(p)"));
}

#[test]
fn a_list_that_cannot_be_trusted_or_a_failed_read_passes() {
    let (d, at) = world("list", "not json");
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
    let e = event("Bash", &json!({"command": "ls"}), "/");
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
