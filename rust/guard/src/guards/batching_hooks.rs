//! `batching-hooks` (ported from the shell of the same name, feature 449 T020): A RUN OF SINGLE BARE READS IS REFUSED. Each turn is a
//! round trip of the whole context, so lookups a session already knows it needs go together, as parallel tool calls. History is one
//! entry a TURN, `1` for a bare quick read and `0` for anything else (GM 2026-09-26, option A); a notice speaks one turn before the bar
//! on any single call and costs no round trip (feature 249); a refusal clears the window and doubles the bar, which decays as turns
//! batch. An image Read is acting on a result, never recon (GM 2026-08-26).
//!
//! Plan T020's decisions: (a) the state line's format and path unchanged; (b) the notice's log line in-line; (c) a suite's `--only`
//! matches by event alone.

use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "batching-hooks",
    events: &["PreToolUse", "PostToolUse", "status"],
    matcher: "Read|Grep|Glob|Bash",
    decide,
};

const NOT_RECON: [&str; 13] = [
    "<<",
    "&&",
    ";",
    "\\n",
    "pytest",
    "make ",
    "git commit",
    "git add",
    "python -",
    "python3 -",
    "ruff",
    "mypy",
    "pyrefly",
];
const IMAGES: [&str; 6] = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"];

/// The thresholds, and the clock.
pub(crate) struct Config {
    pub threshold: u64,
    pub window: usize,
    pub cheap_ms: u64,
    pub same_turn_ms: u64,
    pub dir: PathBuf,
    pub now_ms: u64,
}

impl Config {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>, now_ms: u64) -> Self {
        let num = |k: &str, d: u64| env(k).and_then(|v| v.parse().ok()).unwrap_or(d);
        Self {
            threshold: num("BATCH_THRESHOLD", 3),
            window: usize::try_from(num("BATCH_WINDOW", 6)).unwrap_or(6),
            cheap_ms: num("BATCH_CHEAP_MS", 2000),
            same_turn_ms: num("BATCH_SAME_TURN_MS", 3000),
            dir: env("BATCH_STATE_DIR")
                .filter(|d| !d.is_empty())
                .map_or_else(|| PathBuf::from("/tmp/claude-batching"), PathBuf::from),
            now_ms,
        }
    }
}

/// The state line: `<last pre> <calls> <rearm> <history>`.
struct State {
    path: PathBuf,
    last_pre: u64,
    calls: u64,
    rearm: u64,
    hist: String,
}

impl State {
    fn read(c: &Config, sid: &str) -> Self {
        let name: String = sid
            .chars()
            .map(|ch| {
                if ch.is_ascii_alphanumeric() || ch == '_' || ch == '-' {
                    ch
                } else {
                    '_'
                }
            })
            .collect();
        let path = c.dir.join(format!("{name}.state3"));
        let line = std::fs::read_to_string(&path).unwrap_or_default();
        let first = line.lines().next().unwrap_or("");
        let mut words = first.split_whitespace();
        let mut next = || words.next().and_then(|w| w.parse::<u64>().ok());
        let (last_pre, calls, rearm) = (next().unwrap_or(0), next().unwrap_or(0), next());
        // a stray token can never be read as serial turns
        let hist: String = first
            .split_whitespace()
            .nth(3)
            .unwrap_or("")
            .chars()
            .filter(|ch| *ch == '0' || *ch == '1')
            .collect();
        Self {
            path,
            last_pre,
            calls,
            rearm: rearm.unwrap_or(c.threshold).max(c.threshold),
            hist,
        }
    }

    fn serial(&self) -> u64 {
        self.hist.chars().filter(|ch| *ch == '1').count() as u64
    }

    fn write(&self, at: u64, hist: &str) {
        let _ = std::fs::write(
            &self.path,
            format!("{at} {} {} {hist}\n", self.calls, self.rearm),
        );
    }
}

fn is_recon(event: &Event, text: &str) -> bool {
    match event.tool() {
        "Read" => {
            let path = event
                .input
                .get("tool_input")
                .map_or("", |t| field(t, "file_path"))
                .to_lowercase();
            !IMAGES.iter().any(|x| path.ends_with(x))
        }
        "Grep" | "Glob" => true,
        "Bash" => !NOT_RECON.iter().any(|n| text.contains(n)),
        _ => false,
    }
}

fn is_background(event: &Event) -> bool {
    event
        .input
        .get("tool_input")
        .and_then(|t| t.get("run_in_background"))
        == Some(&serde_json::Value::Bool(true))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| u64::try_from(d.as_millis()).unwrap_or(0));
    judge(
        event,
        session,
        &Config::from_env(&|k| std::env::var(k).ok(), now_ms),
    )
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Config) -> Vec<Answer> {
    let _ = std::fs::create_dir_all(&c.dir);
    let sid = Some(field(&event.input, "session_id"))
        .filter(|s| !s.is_empty())
        .unwrap_or("nosession");
    let mut st = State::read(c, sid);
    let text = event.input.to_string();
    match event.name.as_str() {
        "PreToolUse" => pretool(event, session, c, &mut st, &text),
        "PostToolUse" => {
            posttool(event, c, &mut st, &text);
            Vec::new()
        }
        _ => {
            let tool = Some(event.tool())
                .filter(|t| !t.is_empty())
                .unwrap_or("unknown");
            vec![Answer::Print(format!(
                "tool={tool} history={} serial={} calls_this_turn={} threshold={} rearm={} window={} state={}",
                st.hist, st.serial(), st.calls, c.threshold, st.rearm, c.window, st.path.display()
            ))]
        }
    }
}

fn pretool(
    event: &Event,
    session: &Session,
    c: &Config,
    st: &mut State,
    text: &str,
) -> Vec<Answer> {
    st.calls = if st.last_pre > 0 && c.now_ms.saturating_sub(st.last_pre) < c.same_turn_ms {
        st.calls + 1
    } else {
        1
    };
    let n = st.serial();
    let turns = st.hist.len();
    if st.calls == 1 && !is_background(event) && n >= st.rearm && is_recon(event, text) {
        st.rearm = (st.rearm * 2).min(c.window as u64); // a bar above the window could never fire
        st.write(c.now_ms, ""); // clear the window: no deadlock
        let detail = format!(
            "{n} of the last {turns} turns were single bare reads (history {}, bar {})",
            st.hist, st.rearm
        );
        log::fire(
            "batching",
            "blocked",
            &detail,
            "serial-recon",
            &event.input,
            session,
        );
        return vec![Answer::Refuse(format!(
            "BLOCKED (batching): {n} of your last {turns} turns were one quick call each, and this is another bare read.\n\
Send the lookups you already know you need TOGETHER, as parallel tool calls in one message. A folded command (a; b; c) does not count. After a patch MISS, send the corrected patch and its check as one command. Never pad with no-op turns."
        ))];
    }
    let mut out = Vec::new();
    if st.calls == 1 && n + 1 >= st.rearm {
        out.push(Answer::Notice(format!(
            "BATCHING NOTICE: {n} of your last {turns} turns were a single bare read each (a folded command does not count). The next bare Read/Grep/Glob or single-command Bash on its own is refused. Send calls you already know you need as PARALLEL tool calls in one message. Nothing is refused yet."
        )));
        let detail = format!("{n} of the last {turns} turns were single bare reads - at or above one below the bar (history {}, bar {})", st.hist, st.rearm);
        log::fire(
            "batching",
            "reminded",
            &detail,
            "serial-recon-notice",
            &event.input,
            session,
        );
    }
    // a new turn appends its own provisional entry, after the check above has read the window; posttool promotes it
    if st.calls == 1 {
        st.hist.push('0');
        if st.hist.len() > c.window {
            st.hist = st.hist.split_off(st.hist.len() - c.window);
        }
    }
    let hist = st.hist.clone();
    st.write(c.now_ms, &hist);
    out
}

/// EXACTLY ONE history entry per TURN: a second call in the same turn rewrites the entry to `0`, the turn having been batched.
fn posttool(event: &Event, c: &Config, st: &mut State, text: &str) {
    let dur = c.now_ms.saturating_sub(st.last_pre);
    st.hist.pop();
    if st.calls <= 1 && dur < c.cheap_ms && !is_background(event) && is_recon(event, text) {
        st.hist.push('1');
    } else {
        st.hist.push('0');
        if st.rearm > c.threshold {
            st.rearm -= 1; // backoff decays as turns batch
        }
    }
    let hist = st.hist.clone();
    st.write(st.last_pre, &hist);
}

#[cfg(test)]
mod tests;
