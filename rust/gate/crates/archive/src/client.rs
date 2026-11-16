//! The browser as `archive.py`'s `Browser` (feature 449 T146): `l7r-browser serve` (the one browser crate, `rust/browser/`) run as a
//! program through `scripts/gates/l7r-gate.sh browser`, so the gate never compiles a browser (`ask:449-phase4-slices` Q4,
//! `ask:449-T80-order`: out of the gate's build path), with the Python's politeness and retries kept here: one request at a time per
//! host, `HOST_GAP_S` between them; a 429 or 503 waits `RETRY_WAIT_S` once; a render tried twice - in the first backfill 5 of ~1,150
//! pages failed to render under load and rendered at once when tried again (observed 2026-10-02, method: the failed URLs rendered alone
//! by the same Browser).

use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::time::{Duration, Instant};

use serde_json::{json, Value};

use crate::fetch::{Client, Fetched};
use crate::{Error, Result};

/// Politeness (plan D8): one request at a time per host, this long between them; a 429 or 503 waits `RETRY_WAIT` once.
pub const HOST_GAP: Duration = Duration::from_secs(1);
pub const RETRY_WAIT: Duration = Duration::from_secs(30);
pub const UA: &str =
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36";
/// The request's own headers (beside the user agent the context sends).
const HEADERS: [(&str, &str); 2] = [
    ("Accept", "*/*"),
    ("Accept-Language", "en,ja;q=0.8,zh;q=0.6"),
];

/// The URL's `netloc`, the host the politeness gap is kept for.
#[must_use]
pub fn netloc(url: &str) -> String {
    l7r_gate_research::verbatim::fetch::urlsplit(url)
        .map(|p| p[1].clone())
        .unwrap_or_default()
}

/// The per-host gap: how long to wait before asking `host` again.
#[derive(Debug, Default)]
pub struct Polite {
    last: HashMap<String, Instant>,
}

impl Polite {
    /// Waits out the gap since the host was last asked, then records this ask.
    pub fn wait(&mut self, url: &str) {
        let host = netloc(url);
        if let Some(at) = self.last.get(&host) {
            let left = HOST_GAP.saturating_sub(at.elapsed());
            if !left.is_zero() {
                std::thread::sleep(left);
            }
        }
        self.last.insert(host, Instant::now());
    }
}

/// A running `l7r-browser serve` and its scratch directory for bodies.
pub struct Process {
    child: Child,
    to: Option<ChildStdin>,
    from: BufReader<ChildStdout>,
    scratch: PathBuf,
    asked: u64,
    pub polite: Polite,
    pub retry_wait: Duration,
}

/// The command that starts the browser: the tree's launcher, as every other tool of the tree is reached.
#[must_use]
pub fn launcher(root: &Path) -> PathBuf {
    l7r_gate_core::record::repo::tree_of(root).join("scripts/gates/l7r-gate.sh")
}

impl Process {
    /// Starts the browser, its context's user agent the archive's and certificate errors ignored, as `archive.py`'s `Browser` made its
    /// context; waits for it to say it is ready.
    ///
    /// # Errors
    /// The browser could not start (Playwright's launch error was an `Error`).
    #[cfg(not(test))]
    pub fn start(root: &Path) -> Result<Self> {
        Self::start_with(&launcher(root))
    }

    /// [`Process::start`] through the launcher at `launcher` (a test's stand-in).
    ///
    /// # Errors
    /// As [`Process::start`].
    pub fn start_with(launcher: &Path) -> Result<Self> {
        let mut child = Command::new(launcher)
            .args([
                "browser",
                "serve",
                "--user-agent",
                UA,
                "--ignore-https-errors",
            ])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| Error::new("Error", format!("BrowserType.launch: {e}")))?;
        let to = child.stdin.take();
        let out = child.stdout.take().ok_or(Error::new("Error", "no pipe"))?;
        let mut from = BufReader::new(out);
        let mut ready = String::new();
        let _ = from.read_line(&mut ready);
        if !ready.contains("\"ready\"") {
            let mut said = String::new();
            if let Some(mut e) = child.stderr.take() {
                let _ = e.read_to_string(&mut said);
            }
            let _ = child.kill();
            let _ = child.wait();
            return Err(Error::new(
                "Error",
                format!(
                    "BrowserType.launch: {}",
                    l7r_guard::shared::py_text::strip(&said)
                ),
            ));
        }
        let scratch = std::env::temp_dir().join(format!(
            "l7r-archive-bodies-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| d.as_nanos())
        ));
        // a directory that cannot be made fails each body's write, which the browser reports as the request's failure
        let _ = std::fs::create_dir_all(&scratch);
        Ok(Self {
            child,
            to,
            from,
            scratch,
            asked: 0,
            polite: Polite::default(),
            retry_wait: RETRY_WAIT,
        })
    }

    fn ask(&mut self, asked: &Value) -> Value {
        let sent = self
            .to
            .as_mut()
            .is_some_and(|to| writeln!(to, "{asked}").and_then(|()| to.flush()).is_ok());
        let mut line = String::new();
        if !sent || self.from.read_line(&mut line).unwrap_or(0) == 0 {
            return json!({"error": "the browser has closed"});
        }
        serde_json::from_str(&line)
            .unwrap_or_else(|_| json!({"error": "the browser answered no JSON"}))
    }

    /// One request, no politeness or retry: its answer, the body read from the scratch file.
    pub fn get_once(&mut self, url: &str) -> Fetched {
        self.asked += 1;
        let out = self.scratch.join(format!("body-{}", self.asked));
        let got = self.ask(
            &json!({"op": "get", "url": url, "headers": HEADERS, "timeout_ms": 60_000,
                                   "max_redirects": 10, "out": out}),
        );
        let body = std::fs::read(&out).unwrap_or_default();
        let _ = std::fs::remove_file(&out);
        if let Some(e) = got.get("error").and_then(Value::as_str) {
            let first = e.lines().next().unwrap_or_default();
            return Fetched::failed(url, &crate::store::first_chars(first, 200));
        }
        Fetched {
            url: url.to_owned(),
            status: got.get("status").and_then(Value::as_i64),
            final_url: got
                .get("url")
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned(),
            content_type: got
                .get("content_type")
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned(),
            body,
            ..Fetched::default()
        }
    }

    /// One render, no politeness or retry.
    ///
    /// # Errors
    /// The browser's own words for why the page would not render.
    pub fn render_once(&mut self, url: &str) -> std::result::Result<(String, String), String> {
        let got =
            self.ask(&json!({"op": "render", "url": url, "timeout_ms": 60_000, "idle_ms": 10_000}));
        if let Some(e) = got.get("error").and_then(Value::as_str) {
            return Err(e.to_owned());
        }
        let text = |k: &str| {
            got.get(k)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        Ok((text("mhtml"), text("text")))
    }

    /// Closes the browser and waits for it.
    pub fn close(&mut self) {
        let _ = self.ask(&json!({"op": "close"}));
        self.to = None;
        let _ = self.child.wait();
        let _ = std::fs::remove_dir_all(&self.scratch);
    }
}

impl Drop for Process {
    fn drop(&mut self) {
        if self.to.is_some() {
            self.close();
        }
    }
}

impl Client for Process {
    fn get(&mut self, url: &str) -> Fetched {
        let mut first = true;
        loop {
            self.polite.wait(url);
            let got = self.get_once(url);
            if first && matches!(got.status, Some(429 | 503)) {
                first = false;
                std::thread::sleep(self.retry_wait);
                continue;
            }
            return got;
        }
    }

    fn render(&mut self, url: &str) -> (String, String) {
        for _attempt in 1..=2 {
            self.polite.wait(url);
            if let Ok(done) = self.render_once(url) {
                return done;
            }
        }
        (String::new(), String::new())
    }
}

#[cfg(test)]
mod tests;
