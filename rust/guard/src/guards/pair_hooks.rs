//! `pair-hooks` (feature 151; ported from `scripts/hooks/pair-hooks.sh`, feature 449 T006): THE GATE AND THE INDEPENDENT REVIEW RUN
//! TOGETHER, OR NEITHER RUNS. A gate invocation runs as typed, its engine key recorded; a review check's dispatch is held to one unit
//! an agent, a decided plan, a glyph unit's hour, its prerequisites, the round cap and a green gate for the content it reviews; the
//! step-back refuses both past its hour; a turn may not end with a refused dispatch never re-sent. The reasons behind each rule
//! stand in the shell's comments, kept in git history; the refusals' words are the shell's.
//!
//! Plan T006's decisions: (a) the tools it consults - the checkpoint, the plan gate, `review_prereq`, `review_owed`, the gate stamp,
//! `make engine-key`, the arbiter, `hm_dropped` - stay theirs, asked by path, until phase 3 ports them; a plain Bash call asks none;
//! (b) the engine key is asked only on the branches that read it; (c) its own state is in-process (`state`).

mod review;
mod state;

use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log::{self, Entry};
use crate::shared::session::Session;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "pair-hooks",
    events: &["PreToolUse", "Stop"],
    matcher: "Bash|Agent",
    decide,
};

/// The five review checks, each owed on its occasion (feature 294).
pub(crate) const REVIEW_AGENTS: [&str; 5] = [
    "settlement-review",
    "building-review",
    "glyph-check",
    "size-audit",
    "fix-check",
];

/// What one decision reads: the hook input, the session, the clone it judges and the tree the guard runs from.
pub(crate) struct Ctx<'a> {
    pub event: &'a Event,
    pub session: &'a Session,
    pub clone: PathBuf,
    pub tree: PathBuf,
    /// The interpreter the consulted tools run under: `python3`; `sh` for a test's fakes (FR-008).
    pub python: &'a str,
    /// No clone resolved and the shell's tree is main's (feature 231's amendment): said in the refusal that judges it.
    pub fell_back: bool,
}

impl Ctx<'_> {
    pub fn field(&self, k: &str) -> &str {
        self.event
            .input
            .get("tool_input")
            .and_then(|t| t.get(k))
            .and_then(Value::as_str)
            .unwrap_or("")
    }

    /// Record a firing under the shell's name for this guard, `pair`.
    pub fn log(&self, event: &str, detail: &str, rule: &str) {
        let _ = log::write(&Entry {
            guard: "pair",
            event,
            detail,
            rule,
            context: None,
            input: &self.event.input,
            session_name: &self.session.name(),
        });
    }
}

/// `<interpreter> <script> args` asked in `dir` - `python3`, the tools being Python; a test's fakes are `sh`.
pub(crate) fn python(
    interpreter: &str,
    dir: &Path,
    script: &Path,
    args: &[&str],
    stdin: &str,
) -> crate::shared::tool::Said {
    let s = script.to_string_lossy();
    let all: Vec<&str> = std::iter::once(s.as_ref())
        .chain(args.iter().copied())
        .collect();
    ask(dir, interpreter, &all, stdin)
}

/// The tree the guard runs from: `L7R_GUARD_TREE`, which the wrapper and the suites' shim export, else `cwd`.
fn tree(seam: Option<String>, cwd: &Path) -> PathBuf {
    seam.map_or_else(|| cwd.to_path_buf(), PathBuf::from)
}

/// THIS SESSION'S CLONE, the work tree `cwd` stands in only when none resolves (`find_root`, features 204 and 231), and whether that
/// fell back onto main's tree.
fn find_root(session: &Session, cwd: &Path) -> Option<(PathBuf, bool)> {
    if let Some(c) = session.clone_dir().filter(|c| c.join(".git").exists()) {
        return Some((c.to_path_buf(), false));
    }
    let top = cwd
        .ancestors()
        .find(|d| d.join(".git").exists())?
        .to_path_buf();
    let main = !top.to_string_lossy().contains("/.clones/") && top.join(".clones").is_dir();
    Some((top, main))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cwd = std::env::current_dir().unwrap_or_default();
    resolved(event, session, &cwd, std::env::var("L7R_GUARD_TREE").ok())
}

/// The verdict where the hook runs in `cwd` with the tree `seam` names: none where no clone resolves.
fn resolved(event: &Event, session: &Session, cwd: &Path, seam: Option<String>) -> Vec<Answer> {
    find_root(session, cwd).map_or_else(Vec::new, |(clone, fell_back)| {
        judge(&Ctx {
            event,
            session,
            clone,
            tree: tree(seam, cwd),
            python: "python3",
            fell_back,
        })
    })
}

/// The verdict on one event, its clone and tree resolved.
fn judge(cx: &Ctx) -> Vec<Answer> {
    if cx.event.name == "Stop" {
        return stop(cx);
    }
    pretool(cx)
}

static HEREDOC: std::sync::LazyLock<Regex> =
    std::sync::LazyLock::new(|| Regex::new(r"(?s)<<\s*.?(\w+).?.*?\n\1").unwrap());
static QUOTED: std::sync::LazyLock<Regex> =
    std::sync::LazyLock::new(|| Regex::new(r#"'[^']*'|"[^"]*""#).unwrap());
static INVOKES_GATE: std::sync::LazyLock<Regex> = std::sync::LazyLock::new(|| {
    Regex::new(r#"(^|[;&|(]|[[:space:]])make([[:space:]]+[A-Za-z0-9_=./"-]+)*[[:space:]]+(done|maps)([[:space:]]|$)"#).unwrap()
});

/// An INVOCATION of the gate, not a mention of one (`is_gate_invocation`): heredocs and quoted strings blanked, a dry run excepted,
/// the pattern matched line by line as `grep -E` matches it.
#[must_use]
pub fn is_gate_invocation(cmd: &str) -> bool {
    let a = HEREDOC.replace_all(cmd, " ");
    let stripped = QUOTED.replace_all(&a, " ");
    let padded = format!(" {stripped} ");
    let dry = [
        "-n",
        "--dry-run",
        "--just-print",
        "--recon",
        "-q",
        "--question",
    ];
    if dry.iter().any(|f| padded.contains(&format!(" make {f} "))) {
        return false;
    }
    stripped
        .lines()
        .any(|l| INVOKES_GATE.is_match(l).unwrap_or(false))
}

fn pretool(cx: &Ctx) -> Vec<Answer> {
    let tool = cx.event.tool();
    let (cmd, atype) = (cx.field("command"), cx.field("subagent_type"));
    let gate = tool == "Bash" && is_gate_invocation(cmd);
    if gate || tool == "Agent" {
        let script = cx.clone.join("scripts/reviews/checkpoint.py");
        let due = python(
            cx.python,
            &cx.clone,
            &script,
            &[
                "due",
                "--root",
                &cx.clone.to_string_lossy(),
                "--tool",
                tool,
                "--agent",
                atype,
            ],
            "",
        );
        if !due.out.is_empty() {
            cx.log(
                "refused",
                &format!("{tool} {}", if atype.is_empty() { cmd } else { atype }),
                "step-back-due",
            );
            return vec![Answer::Refuse(format!(
                "\n\x1b[1mBLOCKED: {}\x1b[0m\n",
                due.out
            ))];
        }
    }
    if gate {
        let key = state::engine_key(&cx.clone);
        if !key.is_empty() {
            state::write_pairing(&cx.clone, "gate_key", &key);
        }
        cx.log("permitted", cmd, "gate-as-typed");
        return Vec::new();
    }
    if tool == "Agent" && REVIEW_AGENTS.contains(&atype) {
        return review::dispatch(cx, atype);
    }
    Vec::new()
}

/// A turn may not END with a refused dispatch never re-sent (feature 375; `hm_dropped.py stop`), and it asks no review lookup.
fn stop(cx: &Ctx) -> Vec<Answer> {
    let script = cx.tree.join("scripts/hooks/lib/hm_dropped.py");
    let said = python(
        cx.python,
        &cx.clone,
        &script,
        &["stop", "--root", &cx.clone.to_string_lossy()],
        &cx.event.input.to_string(),
    );
    if said.ok() {
        return Vec::new();
    }
    cx.log("blocked", "stop", "dispatch-dropped");
    vec![Answer::Refuse(said.err)]
}

#[cfg(test)]
mod tests;
