//! The `DevTools` protocol over Chromium's pipe (feature 449 T146): Chromium started with `--remote-debugging-pipe` reads commands on its
//! fd 3 and writes replies and events on its fd 4, one JSON message each, NUL-terminated - the transport Playwright drove it by (its
//! launch line, observed 2026-11-16 with `DEBUG=pw:browser`). A shell puts the child's stdin on fd 3 and its stdout on fd 4 before
//! it execs Chromium, so no `unsafe` `dup2` is needed here.
//!
//! A reader thread splits the stream into messages; [`Cdp::call`] waits for its reply by id and keeps the events that arrive meanwhile
//! for [`Cdp::wait_event`].

use std::collections::VecDeque;
use std::io::{BufRead, BufReader, Read, Write};
use std::path::Path;
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc::{channel, Receiver, RecvTimeoutError};
use std::time::{Duration, Instant};

use serde_json::{json, Value};

/// How long a protocol command may take to answer. A command that waits on the page (a navigation, an evaluation that awaits a promise)
/// has its own deadline; this one only bounds a browser that stopped answering.
pub const ANSWER: Duration = Duration::from_secs(90);

/// The events kept for [`Cdp::wait_event`] at most: the oldest are dropped past it (an event nobody waits for, from a long page).
#[cfg(not(test))]
const KEPT_EVENTS: usize = 20_000;
#[cfg(test)]
const KEPT_EVENTS: usize = 2;
/// How long a closing browser has to answer and then to exit before it is killed.
#[cfg(not(test))]
const CLOSE_WAIT: Duration = Duration::from_secs(5);
#[cfg(test)]
const CLOSE_WAIT: Duration = Duration::from_millis(300);

/// Moves fd 0 to 3 and fd 1 to 4, then execs the browser with its arguments (`$0` and `$@`).
const EXEC_ON_PIPES: &str = "exec 3<&0 4>&1 </dev/null >/dev/null; exec \"$0\" \"$@\"";

/// A running browser and the pipe to it.
pub struct Cdp {
    child: Child,
    to: Option<ChildStdin>,
    from: Receiver<Value>,
    next: u64,
    events: VecDeque<Value>,
    /// `CLOSE_WAIT`; a field so the test of a browser that will not close waits milliseconds (feature 449 T160: it waited out 300 ms twice,
    /// 1.2 s against FR-008's tenth of a second), every other close - the real Chromium's in its end-to-end test among them - its own.
    pub(crate) close_wait: Duration,
}

/// Splits the browser's output into messages and sends each on; ends when the browser closes its end.
fn read_messages(out: impl Read, to: &std::sync::mpsc::Sender<Value>) {
    let mut reader = BufReader::new(out);
    let mut raw = Vec::new();
    while reader.read_until(0, &mut raw).is_ok_and(|n| n > 0) {
        if raw.last() == Some(&0) {
            raw.pop();
        }
        // a message that is not JSON (a lone surrogate in a page's text, which `serde_json` refuses) is dropped: its command then
        // fails at its deadline, as a page that will not render
        if let Ok(message) = serde_json::from_slice::<Value>(&raw) {
            let _ = to.send(message);
        }
        raw.clear();
    }
}

impl Cdp {
    /// Starts `exe` with `args` (which must hold `--remote-debugging-pipe`), its stderr discarded.
    ///
    /// # Errors
    /// The shell or the browser cannot be started.
    pub fn launch(exe: &Path, args: &[String]) -> Result<Self, String> {
        Self::launch_with(Path::new("/bin/sh"), exe, args, None)
    }

    /// [`Cdp::launch`] through the shell at `shell`, its temporary files under `tmp` where one is named.
    ///
    /// # Errors
    /// As [`Cdp::launch`].
    pub fn launch_with(
        shell: &Path,
        exe: &Path,
        args: &[String],
        tmp: Option<&Path>,
    ) -> Result<Self, String> {
        let mut cmd = Command::new(shell);
        if let Some(t) = tmp {
            cmd.env("TMPDIR", t);
        }
        let mut child = cmd
            .arg("-c")
            .arg(EXEC_ON_PIPES)
            .arg(exe)
            .args(args)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|e| format!("could not start {}: {e}", exe.display()))?;
        let to = child.stdin.take();
        let out = child.stdout.take();
        let (send, from) = channel();
        if let Some(out) = out {
            std::thread::spawn(move || read_messages(out, &send));
        }
        Ok(Self {
            child,
            to,
            from,
            next: 0,
            events: VecDeque::new(),
            close_wait: CLOSE_WAIT,
        })
    }

    /// Sends `method` with `params` (to the page `session`, or the browser) and returns its result.
    ///
    /// # Errors
    /// The protocol's own error message, or that the browser closed or stopped answering within `wait`.
    pub fn call_within(
        &mut self,
        method: &str,
        params: &Value,
        session: Option<&str>,
        wait: Duration,
    ) -> Result<Value, String> {
        self.next += 1;
        let id = self.next;
        let mut message = json!({"id": id, "method": method, "params": params});
        if let Some(s) = session {
            message["sessionId"] = json!(s);
        }
        let mut bytes = message.to_string().into_bytes();
        bytes.push(0);
        let sent = self
            .to
            .as_mut()
            .is_some_and(|to| to.write_all(&bytes).and_then(|()| to.flush()).is_ok());
        if !sent {
            return Err(format!("{method}: the browser has closed"));
        }
        let deadline = Instant::now() + wait;
        loop {
            let left = deadline.saturating_duration_since(Instant::now());
            match self.from.recv_timeout(left) {
                Ok(m) if m.get("id").and_then(Value::as_u64) == Some(id) => {
                    return match m.get("error") {
                        Some(e) => Err(format!(
                            "{method}: {}",
                            e.get("message").and_then(Value::as_str).unwrap_or("error")
                        )),
                        None => Ok(m.get("result").cloned().unwrap_or(Value::Null)),
                    };
                }
                Ok(m) => self.keep(m),
                Err(RecvTimeoutError::Timeout) => {
                    return Err(format!("{method}: no answer within {}s", wait.as_secs()))
                }
                Err(RecvTimeoutError::Disconnected) => {
                    return Err(format!("{method}: the browser has closed"))
                }
            }
        }
    }

    /// [`Cdp::call_within`] with the usual deadline.
    ///
    /// # Errors
    /// As [`Cdp::call_within`].
    #[expect(
        clippy::needless_pass_by_value,
        reason = "every caller builds its params inline with `json!`, which a reference would only make it borrow"
    )]
    pub fn call(
        &mut self,
        method: &str,
        params: Value,
        session: Option<&str>,
    ) -> Result<Value, String> {
        self.call_within(method, &params, session, ANSWER)
    }

    fn keep(&mut self, event: Value) {
        if event.get("method").is_some() {
            if self.events.len() >= KEPT_EVENTS {
                self.events.pop_front();
            }
            self.events.push_back(event);
        }
    }

    /// The first event (kept or arriving) that `want` accepts, taken off the queue; none once `deadline` passes or the browser closes.
    pub fn wait_event(
        &mut self,
        deadline: Instant,
        want: impl Fn(&Value) -> bool,
    ) -> Option<Value> {
        if let Some(at) = self.events.iter().position(&want) {
            return self.events.remove(at);
        }
        loop {
            let left = deadline.checked_duration_since(Instant::now())?;
            match self.from.recv_timeout(left) {
                Ok(m) if m.get("method").is_some() && want(&m) => return Some(m),
                Ok(m) => self.keep(m),
                Err(_) => return None,
            }
        }
    }

    /// Asks the browser to close, then waits for it (killing it after a few seconds).
    pub fn close(&mut self) {
        let _ = self.call_within("Browser.close", &json!({}), None, self.close_wait);
        self.to = None;
        let deadline = Instant::now() + self.close_wait;
        while Instant::now() < deadline {
            if !matches!(self.child.try_wait(), Ok(None)) {
                return;
            }
            std::thread::sleep(Duration::from_millis(20));
        }
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

impl Drop for Cdp {
    fn drop(&mut self) {
        if matches!(self.child.try_wait(), Ok(None)) {
            self.close();
        }
    }
}

#[cfg(test)]
mod tests;
