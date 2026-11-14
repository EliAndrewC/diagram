//! A session that failed, and how long to wait before resuming it (`page_session_runner.py`'s `failed`, `wait_for`, `resume_command`
//! and `first_line`, ported by feature 449 T137).
//!
//! THE USAGE LIMIT (2026-09-27, the GM: "if that happens, then we automatically resume once the window refreshes ... it's really
//! important to me that we try to get this done without just kind of stopping for hours and hours"). A session that fails - the plan's
//! five-hour window spent, an overloaded API, a crash - used to be logged and the NEXT brief started, which fails the same way at once,
//! so one spent window burned the whole rest of the queue. Now a failed session is RESUMED (`--resume <id>`, so it carries on with its
//! own context) after a wait: until the reset time the message names when it names one, else a backoff of 15, 30, then 60 minutes, for
//! up to [`RETRIES`] attempts (~11 hours).
//!
//! RETRY EVERY 15 MINUTES AT MOST (feature 280, 2026-09-28): the loop used to sleep the whole wait [`wait_for`] computed, up to six
//! hours, after a usage-limit failure. When the GM resets the limit early, every queue then sat idle for the rest of that wait - 88
//! minutes on two queues on 2026-09-28. So one sleep is capped at [`RETRY_EVERY`]: a resume before the real reset fails at once and
//! waits again, which costs one short failed call a quarter hour. RETRIES rose from 14 to 44 so the reach stays about 11 hours (44 x
//! 15 min) - the cap shortens each wait, not how long a queue holds on.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use l7r_guard::shared::speckit::splitlines;
use serde_json::Value;

pub const RETRIES: u32 = 44;
pub const RETRY_EVERY: f64 = 15.0 * 60.0;
const BACKOFF: [i64; 3] = [15 * 60, 30 * 60, 60 * 60];
const RESUME: &str = "Continue the work of the brief you were given, from where you stopped - an error or the usage limit ended your last turn.";
/// The resume's words when its agents' reports were written to a file (`{path}`, `returned_file`); why in `watch.rs`.
const RETURNED: &str = " Your background agents returned while you waited - a headless session is not woken by them, and the notice that they did not finish is wrong. Every report is in {path}: read it, record each check from it, and do not dispatch them again.";

// `\d` read as ASCII digits, and Python's whitespace for `\s`: a reset time in other digits is a message no service writes
static EPOCH: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\|([0-9]{10})\b").unwrap_or_else(|e| unreachable!("{e}")));
static RESETS: LazyLock<Regex> = LazyLock::new(|| {
    let s = format!("[{SPACE_CLASS}]");
    Regex::new(&format!(
        r"(?i)resets?{s}+(?:at{s}+)?([0-9]{{1,2}})(?::([0-9]{{2}}))?{s}*([ap]m)"
    ))
    .unwrap_or_else(|e| unreachable!("{e}"))
});

/// A JSON value as Python's `bool()` reads what `json.loads` made of it.
pub(crate) fn truthy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => false,
        Some(Value::Bool(b)) => *b,
        Some(Value::Number(n)) => n.as_f64().is_some_and(|f| f != 0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
    }
}

/// Whether a session ended in failure: a non-zero exit, or the JSON result (up to its last `}`) says it was an error.
#[must_use]
pub fn failed(rc: i32, text: &str) -> bool {
    if rc != 0 {
        return true;
    }
    let cut = text.rfind('}').map_or("", |i| &text[..=i]);
    let body = if cut.is_empty() { "{}" } else { cut };
    let Ok(got) = serde_json::from_str::<Value>(body) else {
        return false;
    };
    let subtype = got.get("subtype");
    truthy(got.get("is_error"))
        || (!matches!(subtype, None | Some(Value::Null))
            && subtype.and_then(Value::as_str) != Some("success"))
}

/// `calendar.timegm` of a UTC date at `hour:minute:00`.
fn timegm(y: i64, m: u32, d: u32, hour: i64, minute: i64) -> i64 {
    let (m, d) = (i64::from(m), i64::from(d));
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let doy = (153 * (m + if m > 2 { -3 } else { 9 }) + 2) / 5 + d - 1;
    let days = era * 146_097 + (yoe * 365 + yoe / 4 - yoe / 100 + doy) - 719_468;
    days * 86_400 + hour * 3600 + minute * 60
}

/// `int(min(max(x, 60), 6 * 3600))`.
#[allow(
    clippy::cast_possible_truncation,
    reason = "clamped to a minute and six hours first, as the Python's int() of it"
)]
fn clamp(x: f64) -> i64 {
    x.clamp(60.0, 6.0 * 3600.0) as i64
}

/// Seconds to wait before resuming: two minutes past the reset the message names (an epoch after a `|`, or `resets <h>am|pm` in UTC),
/// else the backoff for this attempt. Never under a minute, never over six hours.
#[must_use]
#[allow(
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "epoch seconds, well inside an f64's integers, as the Python's float arithmetic"
)]
pub fn wait_for(text: &str, attempt: u32, now: f64) -> i64 {
    if let Some(c) = EPOCH.captures(text).ok().flatten() {
        let at: i64 = c[1].parse().unwrap_or(0);
        return clamp(at as f64 - now + 120.0);
    }
    if let Some(c) = RESETS.captures(text).ok().flatten() {
        let (y, mo, d, _, _, _) = l7r_guard::shared::log::civil(now as u64);
        let pm = c[3].eq_ignore_ascii_case("pm");
        let hour = c[1].parse::<i64>().unwrap_or(0) % 12 + if pm { 12 } else { 0 };
        let minute = c.get(2).map_or(0, |m| m.as_str().parse().unwrap_or(0));
        let mut target = timegm(y, mo, d, hour, minute) as f64;
        if target <= now {
            target += 86_400.0;
        }
        return clamp(target - now + 120.0);
    }
    BACKOFF[(attempt as usize).min(BACKOFF.len() - 1)]
}

/// The same session's command, resumed: `--session-id <sid>` becomes `--resume <sid>`, the prompt a continue - naming the file of its
/// agents' reports where the runner wrote one.
#[must_use]
pub fn resume_command(cmd: &[String], sid: &str, returned: Option<&str>) -> Vec<String> {
    let mut out = cmd.to_vec();
    if let Some(i) = out.iter().position(|a| a == "--session-id") {
        out.splice(
            i..(i + 2).min(out.len()),
            [String::from("--resume"), sid.to_owned()],
        );
    }
    let words = format!(
        "{RESUME}{}",
        returned.map_or_else(String::new, |p| RETURNED.replace("{path}", p))
    );
    let at = out
        .iter()
        .position(|a| a == "-p")
        .map_or(out.len(), |i| i + 1);
    if let Some(slot) = out.get_mut(at) {
        *slot = words;
    }
    out
}

/// The first line of `text` that is not blank, stripped and cut at 160 characters, else `no output`.
#[must_use]
pub fn first_line(text: &str) -> String {
    splitlines(text)
        .iter()
        .map(|l| strip(l))
        .find(|l| !l.is_empty())
        .map_or_else(|| "no output".to_owned(), |l| l.chars().take(160).collect())
}

#[cfg(test)]
mod tests;
