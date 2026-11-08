//! `gate-hooks` (features 152, 162; ported from `scripts/hooks/gate-hooks.sh`, feature 449 T007): A `-k` SUBSET IS NOT A RUN THE
//! GATE CAN TRUST. A test run that selected some tests of a file arms a flag; a `make done` while it stands is refused once (a
//! re-issued gate goes through), and a whole-file run or a `.py` edit clears it. A command running both `make quick` and `make
//! done` is rewritten to `done` alone, its superset. `GATE_OK` with a reason stands the guard aside. The refusals' words are the
//! shell's; the reasons behind each rule stand in its comments, kept in git history.
//!
//! Plan T007's decisions: (a) `hm_make.py`'s parts it reads are `shared::make`; (b) the command is read as JSON, not the shell's
//! greedy `sed`, so a ` -k ` in another field arms nothing (constitution XIV); (c) `status` prints the flag, as it did.

use std::path::PathBuf;

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::{self, Entry};
use crate::shared::make::{bare_pytest, combine, targets};
use crate::shared::session::Session;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "gate-hooks",
    events: &["PreToolUse", "status"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

/// What a combined command is told (feature 162).
const COMBINED: &str =
    "`make quick` was dropped from this command and `make done` runs alone: done is a superset \
(the same lint, format and typecheck, and a strict superset of the tests), so nothing you \
asked has gone unasked. Combined rather than refused because a refusal would have cost a \
model round trip to save one warm quick (4.1 s measured).";

fn field<'a>(input: &'a Value, k: &str) -> &'a str {
    input.get(k).and_then(Value::as_str).unwrap_or("")
}

/// This session's subset flag: `GATE_STATE_DIR` (else `/tmp/claude-gate`), `<session id>.subset`.
fn state(input: &Value, dir: Option<String>) -> PathBuf {
    let sid = Some(field(input, "session_id"))
        .filter(|s| !s.is_empty())
        .unwrap_or("nosession");
    let safe: String = sid
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '_' || c == '-' {
                c
            } else {
                '_'
            }
        })
        .collect();
    let dir = PathBuf::from(dir.unwrap_or_else(|| "/tmp/claude-gate".to_owned()));
    let _ = std::fs::create_dir_all(&dir);
    dir.join(format!("{safe}.subset"))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(
        event,
        session,
        &state(&event.input, std::env::var("GATE_STATE_DIR").ok()),
    )
}

/// The verdict with the subset flag at `flag`.
fn judge(event: &Event, session: &Session, flag: &std::path::Path) -> Vec<Answer> {
    if event.name == "status" {
        return vec![Answer::Print(std::fs::read_to_string(flag).map_or_else(
            |_| "subset_pending=0".to_owned(),
            |cmd| format!("subset_pending=1 cmd={cmd}"),
        ))];
    }
    let ti = event
        .input
        .get("tool_input")
        .cloned()
        .unwrap_or(Value::Null);
    let cmd = field(&ti, "command");
    let log = |kind: &str, detail: &str, rule: &str| {
        let _ = log::write(&Entry {
            guard: "gate",
            event: kind,
            detail,
            rule,
            context: None,
            input: &event.input,
            session_name: &session.name(),
        });
    };
    let shown: String = cmd.chars().take(200).collect();
    if event.tool() != "Bash" {
        // an edit to Python leaves no earlier test run vouching for the code
        if std::path::Path::new(field(&ti, "file_path"))
            .extension()
            .is_some_and(|x| x == "py")
        {
            let _ = std::fs::remove_file(flag);
        }
        return Vec::new();
    }
    match escape_or_refuse(cmd, "GATE_OK") {
        Escape::Escaped(why) => {
            log("escaped", &why, "gate-ok");
            let _ = std::fs::remove_file(flag);
            return Vec::new();
        }
        Escape::Refused(text) => {
            log("blocked", &shown, "GATE_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    let invoked = targets(cmd);
    if let Some(combined) = combine(cmd) {
        log("rewrote", &shown, "");
        let mut rewritten = ti.clone();
        rewritten["command"] = Value::String(combined);
        return vec![
            Answer::Rewrite(rewritten),
            Answer::Notice(COMBINED.to_owned()),
        ];
    }
    if invoked.contains("done") {
        let Ok(was) = std::fs::read_to_string(flag) else {
            return Vec::new();
        };
        let _ = std::fs::remove_file(flag); // block ONCE - re-issuing the gate goes straight through
        log("blocked", &shown, "k-subset-before-gate");
        let was = if was.is_empty() {
            "pytest -k ...".to_owned()
        } else {
            was
        };
        return vec![Answer::Refuse(refusal(&was))];
    }
    let runs_tests = bare_pytest(cmd)
        || ["test-file", "test", "quick"]
            .iter()
            .any(|t| invoked.contains(*t));
    if runs_tests {
        let subset = [" -k ", " -k=", " K="].iter().any(|k| cmd.contains(k))
            || cmd.find("FILE=").is_some_and(|i| cmd[i..].contains("::"));
        if subset {
            let cut = (0..=cmd.len().min(120))
                .rev()
                .find(|i| cmd.is_char_boundary(*i))
                .unwrap_or(0);
            let _ = std::fs::write(flag, &cmd[..cut]);
        } else {
            let _ = std::fs::remove_file(flag); // a whole-file / whole-suite run vouches for the code
        }
    }
    Vec::new()
}

/// The refusal of a gate after a subset-only run, naming the subset.
fn refusal(was: &str) -> String {
    format!(
        "BLOCKED: the only local test run since your last edit was a `-k` SUBSET ({was}). A subset selects the tests you were \
THINKING about; the ones a change breaks are the ones you were not - which is exactly how a session ran `-k \"kura_side or \
punishment\"`, went to the gate, and lost a whole gate cycle to a test in the SAME file it had not selected. Run the WHOLE test \
file(s) for the modules you touched first - `make test-file FILE=tests/.../test_<mod>.py` - then run the gate. \
(docs/efficiency-tooling.md, 'gate-hooks'. Override, when the whole files did run: `make done  # GATE_OK: <reason>` - a \
comment; `GATE_OK=... make done` is refused as a prompt override.)"
    )
}

#[cfg(test)]
mod tests;
