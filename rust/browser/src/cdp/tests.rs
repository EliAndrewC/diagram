//! The pipe (feature 449 T146), against the tests' Chromium and a few scripts that misbehave.

use std::path::Path;
use std::time::{Duration, Instant};

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::Cdp;
use crate::testkit::{fake_chrome, script};

#[test]
fn a_command_gets_its_reply_and_the_events_wait_for_whoever_asks() {
    let dir = TempDir::new("browser-cdp");
    let mut cdp = Cdp::launch(&fake_chrome(dir.path()), &[]).unwrap();
    let v = cdp.call("Browser.getVersion", json!({}), None).unwrap();
    assert_eq!(v["product"], "FakeChrome/1");
    assert_eq!(
        cdp.call("Fail.me", json!({}), None).unwrap_err(),
        "Fail.me: no such method"
    );
    assert_eq!(
        cdp.call_within("Silent.me", &json!({}), None, Duration::from_millis(10))
            .unwrap_err(),
        "Silent.me: no answer within 0s"
    );
    // a navigation's reply comes before its events; the frame's one is kept (the others past the cap dropped) for a later wait
    cdp.call("Page.navigate", json!({"url": "http://x/"}), Some("S1"))
        .unwrap();
    cdp.call("Browser.getVersion", json!({}), None).unwrap();
    let soon = Instant::now() + Duration::from_secs(5);
    let is = |name: &'static str| move |e: &Value| e["params"]["name"] == name;
    // the first load (of loader L0) was dropped past the cap of two kept events
    assert!(cdp
        .wait_event(Instant::now() + Duration::from_millis(5), |e| e["params"]
            ["loaderId"]
            == "L0")
        .is_none());
    assert!(cdp.wait_event(soon, is("networkIdle")).is_some());
    cdp.call("Page.navigate", json!({"url": "http://y/"}), Some("S1"))
        .unwrap();
    assert!(cdp.wait_event(soon, is("networkIdle")).is_some());
    assert!(cdp.wait_event(Instant::now(), is("never")).is_none());
    cdp.close();
    assert_eq!(
        cdp.call("Browser.getVersion", json!({}), None).unwrap_err(),
        "Browser.getVersion: the browser has closed"
    );
}

/// A browser that reads the command and dies before it answers: the write went through, the reply never comes (feature 449 T167, the
/// call's second "closed" path, which the test above reached only when its sleep ran short).
#[test]
fn a_browser_that_dies_under_a_command_has_closed() {
    let dir = TempDir::new("browser-cdp-dies");
    let dies = script(dir.path(), "dies", "head -c 1 <&3 >/dev/null; exit 0");
    let mut cdp = Cdp::launch(&dies, &[]).unwrap();
    assert_eq!(
        cdp.call("Browser.getVersion", json!({}), None).unwrap_err(),
        "Browser.getVersion: the browser has closed"
    );
}

#[test]
fn a_browser_that_dies_or_never_starts_is_an_error() {
    let dir = TempDir::new("browser-cdp-dead");
    let gone = script(
        dir.path(),
        "gone",
        r#"printf '{"method":"E"}\0' >&4; exit 0"#,
    );
    let mut cdp = Cdp::launch(&gone, &[]).unwrap();
    // the script gone before the call, waited for rather than slept on: its pipe out ended (the wait's end), so its pipe in, which a
    // process closes first, is shut and the write fails - a fixed 20 ms sleep left which of the call's two "closed" paths ran to the
    // host's load, and the coverage run took the other one (feature 449 T167)
    assert!(cdp
        .wait_event(Instant::now() + Duration::from_secs(1), |e| e["method"]
            == "X")
        .is_none());
    let said = cdp.call("Browser.getVersion", json!({}), None).unwrap_err();
    assert!(said.ends_with("the browser has closed"), "{said}");
    drop(cdp);
    let err = Cdp::launch_with(Path::new("/no/such/shell"), &gone, &[], None)
        .err()
        .unwrap();
    assert!(err.starts_with("could not start"), "{err}");
}

#[test]
fn a_message_that_is_not_json_is_dropped_and_the_last_needs_no_terminator() {
    let dir = TempDir::new("browser-cdp-raw");
    // it ends when its second message comes, not after a two-second sleep (feature 449 T160: 2.0 s against FR-008's tenth of a
    // second): each bash `read -d ''` takes one NUL-ended message (dash, `script`'s shell, has no `-d`), and the stream's end then
    // delivers the unterminated id 2
    let talk = dir.path().join("talk");
    crate::testkit::executable(
        &talk,
        r#"#!/bin/bash
exec 0<&3; read -r -d '' _; printf '{"id":1,"result":{"a":1}}\0not json\0{"method":"E"}\0{"id":2,"result":{"b":2}}' >&4; read -r -d '' _
"#,
    );
    let mut cdp = Cdp::launch(&talk, &[]).unwrap();
    assert_eq!(cdp.call("One", json!({}), None).unwrap(), json!({"a": 1}));
    assert!(cdp
        .wait_event(Instant::now() + Duration::from_secs(2), |e| e["method"]
            == "E")
        .is_some());
    let mut later = Cdp::launch(&talk, &[]).unwrap();
    later.call("One", json!({}), None).unwrap();
    // id 2 arrives with no terminator after it: read when the stream ends
    assert_eq!(
        later
            .call_within("Two", &json!({}), None, Duration::from_secs(5))
            .unwrap(),
        json!({"b": 2})
    );
}

#[test]
fn a_browser_that_will_not_close_is_killed() {
    let dir = TempDir::new("browser-cdp-stubborn");
    let stubborn = script(dir.path(), "stubborn", "exec sleep 30");
    let mut cdp = Cdp::launch(&stubborn, &[]).unwrap();
    // its own short wait, where every other close waits `CLOSE_WAIT` (feature 449 T160)
    cdp.close_wait = Duration::from_millis(20);
    let start = Instant::now();
    cdp.close();
    assert!(start.elapsed() < Duration::from_secs(5));
    // dropped once closed: nothing more to do
    drop(cdp);
    let mut still = Cdp::launch(&stubborn, &[]).unwrap();
    still.close_wait = Duration::from_millis(20);
    drop(still);
}
