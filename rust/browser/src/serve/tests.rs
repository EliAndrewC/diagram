//! `l7r-browser serve` (feature 449 T146): each op answered a line at a time, on the tests' Chromium.

use std::io::Write;

use l7r_shared::tempdir::TempDir;
use serde_json::Value;

use super::serve;
use crate::page::{Browser, Options};
use crate::testkit::{fake_chrome, var_for};

fn browser(dir: &std::path::Path) -> Browser {
    let options = Options {
        width: 1280,
        height: 720,
        user_agent: None,
        ignore_https_errors: true,
    };
    Browser::open(&var_for(&fake_chrome(dir)), options).unwrap()
}

#[test]
fn each_line_is_answered_until_close() {
    let dir = TempDir::new("browser-serve");
    let mut b = browser(dir.path());
    let out = dir.path().join("body");
    let asked = format!(
        "{}\n{}\n{}\n{}\nnot json\n{}\n{}\n",
        serde_json::json!({"op": "render", "url": "http://x/page"}),
        serde_json::json!({"op": "render", "url": "http://x/neterr", "timeout_ms": 1000, "idle_ms": 10}),
        serde_json::json!({"op": "get", "url": "ftp://x/", "headers": [["Accept", "*/*"], ["bad"]], "out": out}),
        serde_json::json!({"op": "nope"}),
        serde_json::json!({"op": "close"}),
        serde_json::json!({"op": "render", "url": "http://x/after"}),
    );
    let mut said = Vec::new();
    serve(&mut b, "UA", &mut asked.as_bytes(), &mut said);
    let lines: Vec<Value> = String::from_utf8(said)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(lines.len(), 6);
    assert_eq!(lines[0]["ready"], true);
    assert_eq!(lines[1]["mhtml"], "MHTML of http://x/page");
    assert_eq!(lines[1]["text"], "the text of http://x/page");
    assert_eq!(
        lines[2]["error"],
        "page.goto: net::ERR_ABORTED at http://x/neterr"
    );
    assert!(lines[3]["error"]
        .as_str()
        .unwrap()
        .contains("Protocol \"ftp:\""));
    assert_eq!(lines[4]["error"], "unknown op \"nope\"");
    assert_eq!(lines[5]["error"], "unknown op \"\"");
}

/// A writer that takes this many bytes, then fails.
struct Broken(usize);

impl Write for Broken {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        if buf.len() > self.0 {
            return Err(std::io::Error::other("closed"));
        }
        self.0 -= buf.len();
        Ok(buf.len())
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

/// A reader that always fails.
struct Unreadable;

impl std::io::Read for Unreadable {
    fn read(&mut self, _: &mut [u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("unreadable"))
    }
}

#[test]
fn a_get_answers_its_status_and_an_output_that_fails_ends_the_loop() {
    let dir = TempDir::new("browser-serve-out");
    let mut b = browser(dir.path());
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    std::thread::spawn(move || {
        if let Ok((mut s, _)) = listener.accept() {
            let mut buf = [0u8; 4096];
            let _ = std::io::Read::read(&mut s, &mut buf);
            let _ = s.write_all(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\nConnection: close\r\n\r\nhi");
        }
    });
    let out = dir.path().join("body");
    let asked = format!(
        "{}\n",
        serde_json::json!({"op": "get", "url": format!("http://127.0.0.1:{port}/"), "out": out})
    );
    let mut said = Vec::new();
    serve(&mut b, "UA", &mut asked.as_bytes(), &mut said);
    let last: Value =
        serde_json::from_str(String::from_utf8(said).unwrap().lines().last().unwrap()).unwrap();
    assert_eq!(last["status"], 200);
    assert_eq!(last["content_type"], "text/plain");
    assert_eq!(std::fs::read(&out).unwrap(), b"hi");
    let twice = "{\"op\": \"nope\"}\n{\"op\": \"nope\"}\n";
    serve(&mut b, "UA", &mut twice.as_bytes(), &mut Broken(0));
    serve(&mut b, "UA", &mut twice.as_bytes(), &mut Broken(20));
    serve(
        &mut b,
        "UA",
        &mut std::io::BufReader::new(Unreadable),
        &mut Vec::new(),
    );
}
