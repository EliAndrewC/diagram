//! The decider over a fixture store (`tests/hooks/test-agent-prefix-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::json;

use super::{decide, finding, judge, lines_kept, shared_runs, switches, verdict, Said, SHARED};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn store(tag: &str) -> crate::shared::tempdir::TempDir {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-prefix-{tag}"));
    d
}

fn event(kind: &str, prompt: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "session_id": "s1", "tool_input": {"subagent_type": kind, "prompt": prompt}}),
    }
}

fn block() -> String {
    let lines: Vec<String> = (0..130)
        .map(|i| format!("Context line {i}: what every check needs to know about it."))
        .collect();
    lines.join("\n") + "\n"
}

fn at(d: &Path, kind: &str, prompt: &str, now: f64) -> Said {
    verdict(&event(kind, prompt), d, now, false)
}

#[test]
fn a_repeated_block_is_refused_wherever_it_sits_and_a_whole_identical_prompt_passes() {
    let d = store("repeat");
    let shared = block();
    assert_eq!(at(&d, "m", &format!("One.\n{shared}"), 100.0), Said::Pass);
    assert!(
        matches!(at(&d, "m", &format!("Two.\n{shared}"), 200.0), Said::Repeat(t) if t.contains("repeat an earlier `m` dispatch's, from character 5: `Context line 0"))
    );
    assert!(matches!(
        at(&d, "m", &format!("{shared}Three."), 300.0),
        Said::Repeat(_)
    ));
    assert_eq!(at(&d, "m", &format!("One.\n{shared}"), 400.0), Said::Pass);
    assert_eq!(
        at(&d, "other", &format!("Two.\n{shared}"), 500.0),
        Said::Pass
    );
    assert_eq!(at(&d, "m", "short", 600.0), Said::Pass);
}

#[test]
fn the_escape_needs_a_reason() {
    let d = store("escape");
    let shared = block();
    at(&d, "m", &format!("One.\n{shared}"), 100.0);
    assert_eq!(
        at(
            &d,
            "m",
            &format!("Two. AGENT_PREFIX_OK: a seeded run\n{shared}"),
            200.0
        ),
        Said::Escaped
    );
    assert!(matches!(
        at(&d, "m", &format!("Three. AGENT_PREFIX_OK\n{shared}"), 300.0),
        Said::Repeat(_)
    ));
}

#[test]
fn a_fourth_launch_within_the_window_is_a_wave() {
    let d = store("wave");
    for n in 0..3 {
        assert_eq!(
            at(
                &d,
                "quote-check",
                &format!("unit {n}"),
                100.0 + f64::from(n)
            ),
            Said::Pass
        );
    }
    assert_eq!(
        at(&d, "quote-check", "unit 3", 103.0),
        Said::Wave("quote-check".to_owned())
    );
    assert_eq!(
        verdict(&event("quote-check", "as a unit"), &d, 103.0, true),
        Said::Pass
    );
    assert_eq!(
        at(&d, "quote-check", "go WAVE_OK: a seeded batch", 103.5),
        Said::Pass
    );
    assert_eq!(at(&d, "other", "another type", 103.5), Said::Pass);
    assert_eq!(at(&d, "quote-check", "later", 200.0), Said::Pass);
}

#[test]
fn the_refusals_name_the_way_out_and_a_headless_wave_passes() {
    let d = store("text");
    let e = event("quote-check", "unit x");
    let s = Session::from_input(&e.input);
    for n in 0..3 {
        judge(
            &event("quote-check", &format!("u{n}")),
            &s,
            &d,
            100.0,
            false,
            false,
        );
        judge(
            &event("spec-fidelity", &format!("u{n}")),
            &s,
            &d,
            100.0,
            false,
            false,
        );
    }
    let said =
        |kind: &str, headless: bool| judge(&event(kind, "next"), &s, &d, 101.0, false, headless);
    assert!(
        matches!(&said("quote-check", false)[..], [Answer::Refuse(t)] if t.contains("name: \"check-wave\"") && t.contains("agentType: \"quote-check\""))
    );
    assert!(
        matches!(&said("spec-fidelity", false)[..], [Answer::Refuse(t)] if t.contains("not one of check-wave's authorized jobs"))
    );
    assert!(said("quote-check", true).is_empty());
    let shared = block();
    judge(
        &event("m", &format!("One.\n{shared}")),
        &s,
        &d,
        200.0,
        false,
        false,
    );
    assert!(
        matches!(&judge(&event("m", &format!("Two.\n{shared}")), &s, &d, 300.0, false, false)[..], [Answer::Refuse(t)] if t.contains(".claude/agents/<name>.md"))
    );
    assert!(judge(
        &event("m", &format!("Six. AGENT_PREFIX_OK: seeded here\n{shared}")),
        &s,
        &d,
        400.0,
        false,
        false
    )
    .is_empty());
}

#[test]
fn the_comparison_counts_characters_by_line() {
    assert_eq!(
        lines_kept("a\nb\r\nc\rd\u{2028}e"),
        ["a\n", "b\r\n", "c\r", "d\u{2028}", "e"]
    );
    assert_eq!(shared_runs("x\ny\nz\n", "y\nz\nw\n", 4), [(4, 2)]);
    assert_eq!(shared_runs("x\n", "y\n", 1), []);
    let long = "é".repeat(SHARED);
    assert_eq!(
        finding(&format!("a\n{long}\n"), &format!("b\n{long}\n")),
        Some((SHARED + 1, 2))
    );
    assert_eq!(finding("same", "same"), None);
}

#[test]
fn another_tool_an_unreadable_store_or_no_repository_passes() {
    let d = store("other");
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert_eq!(verdict(&bash, &d, 1.0, false), Said::Pass);
    let e = event("m", "first");
    at(&d, "m", "first", 1.0);
    let dir = std::fs::read_dir(d.join("l7r-agent-prompts"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    std::fs::write(&dir, "{\"key\": \"m|\"}\nnot json\n").unwrap();
    assert_eq!(verdict(&e, &d, 2.0, false), Said::Pass);
    let outside = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": "/no/such/place"}),
    };
    assert!(decide(&outside, &Session::from_input(&outside.input)).is_empty());
}

#[test]
fn a_prompt_of_blank_tail_shows_no_line() {
    let d = store("blank");
    let spaces = format!("{}\n", " ".repeat(SHARED));
    at(&d, "m", &format!("One.\n{spaces}"), 1.0);
    assert!(
        matches!(at(&d, "m", &format!("Two.\n{spaces}"), 100.0), Said::Repeat(t) if t.ends_with("``"))
    );
}

#[test]
fn inside_a_repository_the_decider_is_reached() {
    let d = crate::shared::tempdir::TempDir::new("guard-decide-pref");
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": d}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}

#[test]
fn the_switches_are_read_from_the_environment() {
    let set = |k: &str| match k {
        "L7R_AGENT_NOW" => Some("12.5".to_owned()),
        "L7R_WAVE_UNIT" => Some("1".to_owned()),
        _ => Some("d1".to_owned()),
    };
    assert_eq!(switches(&set), (Some(12.5), true, true));
    assert_eq!(switches(&|_| None), (None, false, false));
}
