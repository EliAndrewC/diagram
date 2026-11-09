//! The switches' states, how a malformed file closes, and the idle timer's descent.

use std::collections::BTreeMap;

use super::super::fixtures::{commit, put, repo, scratch};
use super::{ancestors, cli, describe, idle_context, read, refusal, write, Axis, LiveTable, Table};

fn sets(dir: &std::path::Path, name: &str, state: &str) {
    write(dir, name, state, "because", "2026-01-01T00:00:00Z").unwrap();
}

fn ask(dir: &std::path::Path, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
        "2026-01-01T00:00:00Z",
    )
}

#[test]
fn an_absent_file_is_the_defaults_and_refuses_nothing() {
    let dir = scratch("absent");
    let sw = read(&dir);
    assert_eq!(
        (
            sw.remote.state.as_str(),
            sw.claims.state.as_str(),
            sw.port.state.as_str()
        ),
        ("on", "report", "rust-only")
    );
    assert_eq!(refusal(&sw, "ci-check"), None);
    assert!(describe(&sw).contains("(default)"));
}

#[test]
fn an_axis_is_thrown_alone_the_others_kept_and_a_release_returns_the_default() {
    let dir = repo("throw");
    sets(&dir, "remote", "off");
    sets(&dir, "claims", "clean");
    sets(&dir, "port", "integrated");
    let sw = read(&dir);
    assert!(sw.remote_off() && sw.claims.state == "clean" && sw.port.state == "integrated");
    assert_eq!(
        (sw.remote.who.as_str(), sw.remote.why.as_str()),
        ("t", "because")
    );
    sets(&dir, "remote", "on");
    assert!(!read(&dir).remote_off() && read(&dir).claims.state == "clean");
    let text = std::fs::read_to_string(dir.join("dev/switches.json")).unwrap();
    assert!(text.starts_with("{\n  \"remote\": {\n    \"state\": \"on\""));
}

#[test]
fn an_empty_reason_and_an_unknown_state_or_axis_are_refused() {
    let dir = scratch("refuse");
    assert!(write(&dir, "remote", "off", "  ", "u")
        .unwrap_err()
        .contains("a reason is required"));
    assert!(write(&dir, "remote", "maybe", "w", "u")
        .unwrap_err()
        .contains("unknown switch remote=maybe"));
    assert!(write(&dir, "nonsense", "on", "w", "u").is_err());
}

#[test]
fn a_malformed_file_closes_and_a_throw_repairs_it() {
    let dir = repo("bad");
    for body in [
        "not json",
        "[]",
        "{\"remote\": 3}",
        "{\"remote\": {\"state\": \"maybe\"}}",
    ] {
        put(&dir, "dev/switches.json", body);
        let sw = read(&dir);
        assert!(
            sw.remote_off()
                && !sw.error.is_empty()
                && sw.claims.state == "clean"
                && sw.port.state == "rust-only",
            "{body}"
        );
        assert!(describe(&sw).contains("MALFORMED"));
    }
    write(&dir, "remote", "on", "repair", "u").unwrap();
    assert!(read(&dir).error.is_empty());
    assert_eq!(read(&dir).claims.state, "report");
}

#[test]
fn an_unknown_key_is_ignored_and_a_bad_claims_or_port_entry_closes_alone() {
    let dir = repo("unknown");
    put(
        &dir,
        "dev/switches.json",
        "{\"scope\": {\"state\": \"locked\"}}",
    );
    assert!(read(&dir).error.is_empty() && !read(&dir).remote_off());
    put(&dir, "dev/switches.json", "{\"claims\": 3}");
    let sw = read(&dir);
    assert!(
        !sw.remote_off()
            && sw.claims.state == "clean"
            && sw.claims.why.contains("the claims entry is MALFORMED")
    );
    commit(
        &dir,
        "dev/switches.json",
        "{\"port\": {\"state\": \"integrated\"}}",
    );
    put(
        &dir,
        "dev/switches.json",
        "{\"port\": {\"state\": \"nonsense\"}}",
    );
    let closed = read(&dir);
    assert_eq!(closed.port.state, "integrated");
    assert!(
        closed
            .port
            .why
            .contains("the last committed state in force")
            && !closed.remote_off()
    );
}

#[test]
fn a_refusal_names_the_reason_the_release_and_the_local_route() {
    let mut sw = read(&scratch("r"));
    sw.remote = Axis {
        state: "off".to_owned(),
        why: "budget".to_owned(),
        who: String::new(),
        utc: "U".to_owned(),
    };
    let text = refusal(&sw, "ci-check").unwrap();
    assert!(
        text.contains("since U by ?: budget")
            && text.contains("make ci-on REASON=...")
            && text.contains("a green local `make done`")
    );
    assert!(describe(&sw).contains("since U by ?: budget"));
}

#[derive(Default)]
struct Pretend(BTreeMap<u32, (Option<u32>, &'static str)>);

impl Table for Pretend {
    fn parent(&self, pid: u32) -> Option<u32> {
        self.0.get(&pid).and_then(|(p, _)| *p)
    }

    fn cmdline(&self, pid: u32) -> String {
        self.0.get(&pid).map_or("", |(_, c)| c).to_owned()
    }
}

#[test]
fn the_walk_ends_at_init_at_a_vanished_process_and_at_its_depth_cap() {
    let mut t = Pretend::default();
    t.0.insert(5, (Some(4), ""));
    t.0.insert(4, (Some(1), ""));
    assert_eq!(ancestors(5, &t), [4, 1]);
    assert_eq!(ancestors(9, &t), Vec::<u32>::new());
    t.0.insert(7, (Some(0), ""));
    assert_eq!(ancestors(7, &t), Vec::<u32>::new());
    let mut deep = Pretend::default();
    for pid in 2..100 {
        deep.0.insert(pid, (Some(pid + 1), ""));
    }
    assert_eq!(ancestors(2, &deep).len(), 64);
}

#[test]
fn idle_needs_the_marker_an_ancestor_and_the_timer_s_command_line() {
    let dir = scratch("idle");
    let mut t = Pretend::default();
    t.0.insert(5, (Some(4), ""));
    t.0.insert(4, (Some(1), "l7r-guard --idle-tests timer x"));
    assert!(!idle_context(&dir, 5, &t));
    std::fs::create_dir_all(dir.join(".git")).unwrap();
    std::fs::write(dir.join(".git/idle-tests.running"), "4\n").unwrap();
    assert!(idle_context(&dir, 5, &t));
    assert!(!idle_context(&dir, 9, &t));
    t.0.insert(4, (Some(1), "something else"));
    assert!(!idle_context(&dir, 5, &t));
    assert!(!LiveTable.cmdline(std::process::id()).is_empty());
    assert_eq!(LiveTable.parent(u32::MAX), None);
    assert!(LiveTable.parent(std::process::id()).is_some());
}

#[test]
fn the_command_line_answers_bare_for_the_makefile_and_refuses() {
    let dir = repo("cli");
    assert_eq!(ask(&dir, &["state", "port"]).stdout, "rust-only\n");
    assert_eq!(ask(&dir, &["state", "claims"]).stdout, "report\n");
    assert_eq!(ask(&dir, &["state", "remote"]).stdout, "on\n");
    assert_eq!(ask(&dir, &["idle"]).stdout, "0\n");
    assert!(ask(&dir, &["show"])
        .stdout
        .starts_with("switches (dev/switches.json):"));
    assert_eq!(ask(&dir, &["check", "remote", "ci-check"]).code, 0);
    assert!(ask(&dir, &["set", "remote", "off", "--why", "w"])
        .stdout
        .contains("off"));
    let refused = ask(&dir, &["check", "remote", "ci-check"]);
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.contains("REFUSED"));
    assert!(ask(&dir, &["set", "remote", "off", "--why", " "])
        .stderr
        .starts_with("switches: REFUSED"));
    assert_eq!(ask(&dir, &["nonsense"]).code, 2);
}
