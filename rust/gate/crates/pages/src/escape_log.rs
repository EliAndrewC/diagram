//! An escape taken outside a hook, read and recorded the way the guards record theirs (feature 274). Ported whole from
//! `scripts/pages/escape_log.py` by feature 449 T137 (`ask:449-phase3-remainder`): the page-session runner asks [`escape`] in process,
//! and `scripts/record/reserve-prefix.py`, which stays Python, asks `l7r-gate escape take` once, where it imported the module.
//!
//! WHY. The write cap on a page session (`WRITE_CAP_OK`, the runner) and the key cap on `make reserve` (`KEY_CAP_OK`) are refused outside
//! a hook, and the guard doctrine asks that every escape state a reason of two words or more and be counted by `make audit`. So the
//! reason is held to the floor every hook uses (the guard's `shared::escape::enough`, which `l7r-gate escape reason-ok` serves the shell),
//! and the entry is written in `~/.claude/guard-log/`'s own format, one file per entry, renamed into place by the guard's one writer of
//! that file (`shared::log::place`). The entry's text is Python's `json.dumps(entry, indent=2)`, every non-ASCII character escaped, as
//! the Python wrote it and `make audit` reads it.

use std::path::{Path, PathBuf};
use std::time::SystemTime;

use l7r_guard::shared::escape::enough;
use l7r_guard::shared::log::civil;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Value};

use crate::reply;
use l7r_gate_core::Reply;

/// What the process reads of its environment for one escape, handed in so a test runs without touching the process's own.
pub struct Env<'a> {
    /// A variable of the environment (`os.environ.get`).
    pub var: &'a dyn Fn(&str) -> Option<String>,
    /// The working directory (`Path.cwd()`), whose name is the entry's `session_name`.
    pub cwd: PathBuf,
    /// The caller's command line, as `" ".join(sys.argv)` gave it.
    pub command: String,
}

impl Env<'_> {
    /// The process's own: its environment, its working directory and its command line.
    #[must_use]
    pub fn of_process() -> Env<'static> {
        Env {
            var: &|k| std::env::var(k).ok(),
            cwd: std::env::current_dir().unwrap_or_default(),
            command: std::env::args().collect::<Vec<_>>().join(" "),
        }
    }
}

/// The refusal when `token` is set with too little to audit.
fn no_reason(token: &str) -> String {
    format!(
        "{token} needs a REASON, not just a value - two words and eight characters; say why this case is legitimate"
    )
}

/// True when `token` is set in the environment with a reason, having logged it; false when it is not set.
///
/// # Errors
///
/// The refusal when it is set with too little to audit: the missing thing is the session's reasoning, which no tool can supply, so that
/// is a refusal rather than a pass (the doctrine the guards' `escape_or_refuse` states). The refusal is logged first.
pub fn escape(
    token: &str,
    guard: &str,
    rule: &str,
    context: Option<&Value>,
    env: &Env,
) -> Result<bool, String> {
    let reason = (env.var)(token).unwrap_or_default();
    let reason = strip(&reason);
    if reason.is_empty() {
        return Ok(false);
    }
    if !enough(reason) {
        log(
            guard,
            "blocked",
            reason,
            &format!("{token}-no-reason"),
            context,
            env,
        );
        return Err(no_reason(token));
    }
    log(guard, "escaped", reason, rule, context, env);
    Ok(true)
}

/// The log's directory: `GUARD_LOG_DIR` unless unset or empty, else `~/.claude/guard-log` (the Python's `or`, which an empty value fell
/// through).
fn log_dir(env: &Env) -> PathBuf {
    match (env.var)("GUARD_LOG_DIR").filter(|d| !d.is_empty()) {
        Some(d) => PathBuf::from(d),
        None => Path::new(&(env.var)("HOME").unwrap_or_default()).join(".claude/guard-log"),
    }
}

/// One guard-log entry; never fails - a failed log must not take the caller down with it.
pub fn log(guard: &str, event: &str, detail: &str, rule: &str, context: Option<&Value>, env: &Env) {
    log_at(guard, event, detail, rule, context, env, SystemTime::now());
}

fn log_at(
    guard: &str,
    event: &str,
    detail: &str,
    rule: &str,
    context: Option<&Value>,
    env: &Env,
    now: SystemTime,
) {
    let since = now
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap_or_default();
    let (year, month, day, hour, min, sec) = civil(since.as_secs());
    let sid = ["L7R_PAGE_SESSION", "CLAUDE_SESSION_ID"]
        .iter()
        .find_map(|k| (env.var)(k).filter(|v| !v.is_empty()))
        .unwrap_or_else(|| "unknown".to_owned());
    let entry = json!({
        "utc": format!("{year:04}-{month:02}-{day:02}T{hour:02}:{min:02}:{sec:02}Z"), "guard": guard, "event": event, "rule": rule,
        "session": sid, "session_name": l7r_guard::shared::speckit::py_name(&env.cwd), "cwd": env.cwd.to_string_lossy(), "tool": "",
        "transcript": "", "detail": detail.chars().take(200).collect::<String>(), "command": env.command,
        "context": context.cloned().unwrap_or(Value::Null),
    });
    let _ = l7r_guard::shared::log::place(&log_dir(env), &dumps(&entry, Some(2), true), now);
}

const USAGE: &str = "usage: l7r-gate escape take --token TOKEN --guard GUARD --rule RULE [--context JSON] [--command TEXT]\n";

/// `l7r-gate escape take --token T --guard G --rule R [--context JSON] [--command TEXT]`: exit 0 when `T` is set with a reason (logged),
/// 1 when it is not set, 3 with the refusal on stderr when it is set with too little to audit (logged), 2 on a command line it cannot
/// read. `--command` is the caller's own command line, so `make audit` names the tool that took the escape, as the Python's
/// `" ".join(sys.argv)` did in process; without it, this command's.
#[must_use]
pub fn cli(args: &[String], env: &Env) -> Reply {
    use l7r_gate_core::record::args::{parse, Spec};
    let specs = [
        Spec::value("--token"),
        Spec::value("--guard"),
        Spec::value("--rule"),
        Spec::value("--context"),
        Spec::value("--command"),
    ];
    let usage = |why: &str| {
        reply(
            String::new(),
            format!("{USAGE}l7r-gate escape take: error: {why}\n"),
            2,
        )
    };
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let (token, guard, rule) = (
        p.text("--token", ""),
        p.text("--guard", ""),
        p.text("--rule", ""),
    );
    if token.is_empty() || guard.is_empty() || rule.is_empty() {
        return usage("--token, --guard and --rule are required");
    }
    let context: Option<Value> = match p
        .has("--context")
        .then(|| serde_json::from_str(p.text("--context", "")))
    {
        Some(Ok(v)) => Some(v),
        Some(Err(e)) => return usage(&format!("--context is not JSON: {e}")),
        None => None,
    };
    let env = Env {
        var: env.var,
        cwd: env.cwd.clone(),
        command: if p.has("--command") {
            p.text("--command", "").to_owned()
        } else {
            env.command.clone()
        },
    };
    match escape(token, guard, rule, context.as_ref(), &env) {
        Ok(true) => reply(String::new(), String::new(), 0),
        Ok(false) => reply(String::new(), String::new(), 1),
        Err(why) => reply(String::new(), format!("{why}\n"), 3),
    }
}

#[cfg(test)]
mod tests;
