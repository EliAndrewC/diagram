//! The browser as a program (feature 449 T146): a stand-in for `l7r-gate.sh browser serve` speaking its protocol - since T273 this
//! test binary started again as [`the_stand_in_server`] alone, where a Python program stood (SC-005).

use std::io::{BufRead, Write};
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{launcher, netloc, Polite, Process, HOST_GAP};
use crate::fetch::Client;

/// Set in the started copy's environment: the copy is the stand-in.
const MARKER: &str = "L7R_TEST_SERVE_STAND_IN";

/// A `browser serve` that answers from the URL: `slow` 429 then 200, `boom` a failure, `fail` a render that will not, `junk` no JSON,
/// `die` gone before it answers. Its answers go to fd 3, the launcher's stdout, so the test harness's own lines (on its stdout, which
/// the launcher sends to `/dev/null`) never reach the client.
#[test]
fn the_stand_in_server() {
    if std::env::var_os(MARKER).is_none() {
        return;
    }
    let mut out = std::fs::OpenOptions::new()
        .write(true)
        .open("/dev/fd/3")
        .unwrap();
    let mut say = |line: &str| {
        let _ = writeln!(out, "{line}");
    };
    say(&json!({"ready": true}).to_string());
    let mut seen: std::collections::HashMap<String, u32> = std::collections::HashMap::new();
    for line in std::io::stdin().lock().lines().map_while(Result::ok) {
        let m: Value = serde_json::from_str(&line).unwrap();
        let op = m["op"].as_str().unwrap_or_default();
        let url = m["url"].as_str().unwrap_or_default();
        if op == "close" {
            break;
        }
        if url.contains("junk") {
            say("not json");
            continue;
        }
        if url.contains("die") {
            std::process::exit(0);
        }
        if op == "get" {
            let count = seen.entry(url.to_owned()).or_default();
            *count += 1;
            if url.contains("boom") {
                say(&json!({"error": "APIRequestContext.get: boom\nCall log:\n - x"}).to_string());
                continue;
            }
            let status = if url.contains("slow") && *count == 1 {
                429
            } else {
                200
            };
            std::fs::write(
                m["out"].as_str().unwrap_or_default(),
                format!("body of {url}"),
            )
            .unwrap();
            say(&json!({"status": status, "url": format!("{url}#final"), "content_type": "text/html"}).to_string());
        } else {
            // the client asks `get`, `render` and `close` alone, so what is not a `get` here is a render
            let answer = if url.contains("fail") {
                json!({"error": "nope"})
            } else {
                json!({"mhtml": format!("M {url}"), "text": "T"})
            };
            say(&answer.to_string());
        }
    }
}

/// The stand-in's launcher: a shell running this test binary again as [`the_stand_in_server`] alone, fd 3 its answers.
fn stand_in() -> String {
    let exe = std::env::current_exe().unwrap();
    format!("#!/bin/sh\n{MARKER}=1 exec '{}' --exact client::tests::the_stand_in_server --nocapture -q 3>&1 >/dev/null\n", exe.display())
}

fn launcher_at(dir: &Path, body: &str) -> PathBuf {
    let at = dir.join("serve");
    // by `install`, never this process: one it wrote itself can be "Text file busy" when run while another test thread's fork holds it
    // open (feature 449 T160)
    l7r_gate_core::write_executable(&at, body);
    at
}

/// The spacing a test waits, where the archive waits `HOST_GAP` (feature 449 T160): long enough to measure, short of FR-008's bar.
const GAP: Duration = Duration::from_millis(5);

#[test]
fn a_request_and_a_render_through_the_browser_retried_and_spaced() {
    let dir = TempDir::new("archive-client");
    let mut p = Process::start_with(&launcher_at(dir.path(), &stand_in())).unwrap();
    // no retry wait: the elapsed time below is the gap's alone, as 900 ms of the old run's second was beyond its 10 ms retry wait
    p.retry_wait = Duration::ZERO;
    p.polite.gap = GAP;
    let got = p.get("http://h/page");
    assert_eq!(
        (got.status, got.final_url.as_str(), got.body.as_slice()),
        (
            Some(200),
            "http://h/page#final",
            &b"body of http://h/page"[..]
        )
    );
    // the same host again waits out the gap (the archive's second, nine tenths of it measured, as before)
    let start = Instant::now();
    assert_eq!(p.get("http://h/slow").status, Some(200));
    assert!(start.elapsed() >= GAP * 9 / 10);
    assert_eq!(p.get("http://h/boom").error, "APIRequestContext.get: boom");
    assert_eq!(
        p.render("http://g/r"),
        ("M http://g/r".to_owned(), "T".to_owned())
    );
    assert_eq!(p.render("http://g/fail"), (String::new(), String::new()));
    assert_eq!(p.get("http://h/junk").error, "the browser answered no JSON");
    assert_eq!(p.get("http://h/die").error, "the browser has closed");
    assert_eq!(
        p.render_once("http://h/x").unwrap_err(),
        "the browser has closed"
    );
    p.close();
    drop(p);
}

/// Split from the test above (feature 449 T160): its own browser, so neither test starts two.
#[test]
fn a_browser_dropped_while_running_is_closed_then() {
    let dir = TempDir::new("archive-client-drop");
    let running = Process::start_with(&launcher_at(dir.path(), &stand_in())).unwrap();
    drop(running);
}

/// The gap the archive keeps is a second, unless a caller sets its own (feature 449 T160).
#[test]
fn the_gap_between_two_asks_of_a_host_is_a_second() {
    assert_eq!(HOST_GAP, Duration::from_secs(1));
    assert_eq!(Polite::default().gap, HOST_GAP);
}

#[test]
fn a_browser_that_will_not_start_is_an_error() {
    let dir = TempDir::new("archive-client-dead");
    let err = Process::start_with(&launcher_at(
        dir.path(),
        "#!/bin/sh\necho 'no chromium here' >&2\nexit 1\n",
    ))
    .err()
    .unwrap();
    assert_eq!(
        (err.kind, err.message.as_str()),
        ("Error", "BrowserType.launch: no chromium here")
    );
    assert!(Process::start_with(&dir.path().join("missing")).is_err());
    assert_eq!(
        launcher(Path::new("/r")).file_name().unwrap(),
        "l7r-gate.sh"
    );
    assert_eq!(
        (netloc("http://u@h:8/x"), netloc("not a url")),
        ("u@h:8".to_owned(), String::new())
    );
    let mut polite = Polite::default();
    polite.wait("http://a/");
    polite.wait("http://b/");
}
