//! The browser as a program (feature 449 T146): a stand-in for `l7r-gate.sh browser serve` speaking its protocol.

use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use l7r_guard::shared::tempdir::TempDir;

use super::{launcher, netloc, Polite, Process};
use crate::fetch::Client;

/// A `browser serve` that answers from the URL: `slow` 429 then 200, `boom` a failure, `fail` a render that will not, `junk` no JSON.
const SERVE: &str = r##"#!/usr/bin/env python3
import json, sys
print(json.dumps({"ready": True}), flush=True)
seen = {}
for line in sys.stdin:
    m = json.loads(line)
    op, url = m.get("op"), m.get("url", "")
    if op == "close":
        break
    if "junk" in url:
        print("not json", flush=True)
        continue
    if "die" in url:
        sys.exit(0)
    if op == "get":
        seen[url] = seen.get(url, 0) + 1
        if "boom" in url:
            print(json.dumps({"error": "APIRequestContext.get: boom\nCall log:\n - x"}), flush=True)
            continue
        status = 429 if "slow" in url and seen[url] == 1 else 200
        open(m["out"], "wb").write(b"body of " + url.encode())
        print(json.dumps({"status": status, "url": url + "#final", "content_type": "text/html"}), flush=True)
    elif op == "render":
        print(json.dumps({"error": "nope"} if "fail" in url else {"mhtml": "M " + url, "text": "T"}), flush=True)
"##;

fn launcher_at(dir: &Path, body: &str) -> PathBuf {
    let at = dir.join("serve.py");
    std::fs::write(&at, body).unwrap();
    std::process::Command::new("chmod")
        .arg("+x")
        .arg(&at)
        .status()
        .unwrap();
    at
}

#[test]
fn a_request_and_a_render_through_the_browser_retried_and_spaced() {
    let dir = TempDir::new("archive-client");
    let mut p = Process::start_with(&launcher_at(dir.path(), SERVE)).unwrap();
    p.retry_wait = Duration::from_millis(10);
    let got = p.get("http://h/page");
    assert_eq!(
        (got.status, got.final_url.as_str(), got.body.as_slice()),
        (
            Some(200),
            "http://h/page#final",
            &b"body of http://h/page"[..]
        )
    );
    let start = Instant::now();
    assert_eq!(p.get("http://h/slow").status, Some(200));
    assert!(start.elapsed() >= Duration::from_millis(900));
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
    // dropped while running: closed then
    let running = Process::start_with(&launcher_at(dir.path(), SERVE)).unwrap();
    drop(running);
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
