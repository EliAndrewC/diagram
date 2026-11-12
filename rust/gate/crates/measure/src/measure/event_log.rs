//! `l7r-gate measure event-log hook | from-transcript <jsonl>`: `scripts/measure/event_log.py`'s command line (feature 375 FR-008, plan D7
//! and D8; ported by feature 449 T119, `ask:449-T83-scope`). Both halves are the guard's: the line and its append are `event_log_hooks`
//! (T012), the reading and the transcript's events `event_log_hooks::read`, the one reader the report and the arbiter's bundle share.
//!
//! ```text
//! l7r-gate measure event-log hook                        read one hook payload on stdin, append its line
//! l7r-gate measure event-log from-transcript <jsonl>     print the transcript's events as lines
//! ```

use std::fmt::Write as _;
use std::io::Read;
use std::path::Path;

use l7r_guard::guards::event_log_hooks::read::{from_transcript, read_jsonl};
use l7r_guard::guards::event_log_hooks::record;
use serde_json::Value;

use super::reply;
use crate::Reply;

const USAGE: &str = "    l7r-gate measure event-log hook                        read one hook payload on stdin, append its line\n    l7r-gate measure event-log from-transcript <jsonl>     print the transcript's events as lines\n\n";

/// The command line: `hook` never refuses and never prints (a hook on every tool call must not be able to stop one), `from-transcript`
/// prints one JSON line an event, and anything else is the usage, exit 2.
#[must_use]
pub fn cli(args: &[String], stdin: &mut dyn Read) -> Reply {
    match (args.first().map(String::as_str), args.get(1)) {
        (Some("hook"), _) => {
            let mut text = String::new();
            if stdin.read_to_string(&mut text).is_ok() {
                let text = if text.is_empty() { "{}" } else { text.as_str() };
                if let Ok(payload) = serde_json::from_str::<Value>(text) {
                    record(&payload);
                }
            }
            reply(String::new(), String::new(), 0)
        }
        (Some("from-transcript"), Some(path)) => match read_jsonl(Path::new(path))
            .map_err(|e| format!("OSError: {path}: {e}"))
            .and_then(|rows| from_transcript(&rows))
        {
            Ok(events) => {
                let mut out = String::new();
                for e in events {
                    let _ = writeln!(out, "{}", Value::Object(e));
                }
                reply(out, String::new(), 0)
            }
            Err(why) => reply(
                String::new(),
                format!("Traceback (most recent call last):\n  l7r-gate measure event-log from-transcript\n{why}\n"),
                1,
            ),
        },
        _ => reply(String::new(), USAGE.to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
