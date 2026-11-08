//! The decider on a fixture archive (`tests/hooks/test-archive-first-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{cited, decide, held, judge};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::sha256::hex;

const URL: &str = "https://example.org/page";

/// A repository whose archive holds `URL`, and a store with its text.
fn world(tag: &str) -> PathBuf {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-archive-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    let uid: String = hex(URL.as_bytes()).chars().take(12).collect();
    let (row, cap) = (
        d.join("repo/research/archive").join(&uid[..2]),
        d.join("store/ab/capture"),
    );
    std::fs::create_dir_all(&row).unwrap();
    std::fs::create_dir_all(d.join("repo/.git")).unwrap();
    std::fs::create_dir_all(&cap).unwrap();
    std::fs::write(
        row.join(format!("{uid}.json")),
        json!({"path": "ab/capture", "captured": "2026-10-02T12:00:00+00:00"}).to_string(),
    )
    .unwrap();
    std::fs::write(cap.join("text.txt"), "text\n").unwrap();
    d
}

fn fetch(d: &Path, url: &str, agent: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"session_id": "s", "agent_id": agent, "tool_name": "WebFetch", "tool_input": {"url": url}}),
    };
    let store = d.join("store").to_string_lossy().into_owned();
    judge(
        &e,
        &Session::from_input(&e.input),
        &d.join("repo"),
        &d.join("state"),
        Some(&store),
    )
}

#[test]
fn a_url_is_cited_as_the_manifest_ids_it() {
    assert_eq!(cited("https://x/a#frag"), "https://x/a");
    assert_eq!(cited("https://x/a.,;:"), "https://x/a");
    assert_eq!(cited("https://x/a_(b)"), "https://x/a_(b)");
    assert_eq!(cited("https://x/a)"), "https://x/a");
    assert_eq!(cited("https://x/?a=1&amp;b=2"), "https://x/?a=1&b=2");
}

#[test]
fn the_first_fetch_is_refused_and_the_same_actors_second_passes() {
    let d = world("first");
    let got = fetch(&d, URL, "a");
    assert!(
        matches!(&got[..], [Answer::Refuse(t)] if t.contains("captured 2026-10-02") && t.contains("capture/text.txt") && t.contains("fetch the same URL again"))
    );
    assert!(fetch(&d, URL, "a").is_empty());
    assert!(matches!(&fetch(&d, URL, "")[..], [Answer::Refuse(_)]));
    assert!(fetch(&d, URL, "").is_empty());
    assert!(matches!(&fetch(&d, URL, "a/b")[..], [Answer::Refuse(_)]));
    let other = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "WebSearch", "tool_input": {"url": URL}}),
    };
    assert!(judge(
        &other,
        &Session::from_input(&other.input),
        &d.join("repo"),
        &d.join("state"),
        None
    )
    .is_empty());
}

#[test]
fn what_the_archive_does_not_hold_passes() {
    let d = world("unheld");
    assert!(fetch(&d, "https://example.org/other", "a").is_empty());
    assert!(fetch(&d, "ftp://example.org/page", "a").is_empty());
    assert!(held(URL, &d.join("repo"), Some("/no/such/store")).is_none());
    let text = d.join("store/ab/capture/text.txt");
    std::fs::write(&text, "").unwrap();
    assert!(fetch(&d, URL, "a").is_empty());
}

#[test]
fn a_clone_finds_its_mirrors_store_and_the_entry_runs() {
    let d = world("mirror");
    let clone = d.join("repo/.clones/x");
    let uid: String = hex(URL.as_bytes()).chars().take(12).collect();
    let row = clone.join("research/archive").join(&uid[..2]);
    std::fs::create_dir_all(&row).unwrap();
    std::fs::write(
        row.join(format!("{uid}.json")),
        json!({"path": "p"}).to_string(),
    )
    .unwrap();
    let text = d.join("repo/.specify/source-archive/p");
    std::fs::create_dir_all(&text).unwrap();
    std::fs::write(text.join("text.txt"), "t").unwrap();
    let found = held(URL, &clone, None).unwrap();
    assert!(found.0.contains(".specify/source-archive/p/text.txt") && found.1.is_empty());
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"url": "ftp://x"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
