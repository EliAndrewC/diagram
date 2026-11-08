//! `gate-write-hooks` (feature 385 T02, plan D13; ported from the shell of the same name, feature 449 T024): NO WRITE TO THE WORKING TREE
//! WHILE THIS TREE'S OWN `make done` RUNS. A gate ends by checking that the tree did not move while it ran; a session voided two gates
//! this way, the second an hour after the round arbiter named the slip (the GM, 2026-10-17: "a guard, not a reminder"). A change the gate
//! does not see passes, asked of the gate's own `preflight.py --tree-check` (feature 405 T41). While `make cache-audit` runs, an engine
//! file holds a perturbed literal, so no engine edit and no commit (feature 426 T10). `GATE_WRITE_OK` with a reason is the escape.
//!
//! Plan T024's decisions: (a) the guard and `own-make.sh`'s question in-process, by pid; (b) `preflight.py` is a phase-2 piece, asked by
//! path, only while a gate runs.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;

use crate::guards::finished_run_hooks::runs::{realpath, Procs};
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::{ask, ask_within};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "gate-write-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

const FILE_TOOLS: [&str; 3] = ["Edit", "Write", "NotebookEdit"];

static GIT_WRITE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\bgit\b[^;&|]*\b(commit|add)\b").unwrap_or_else(|e| unreachable!("{e}"))
});
static MAKE_WRITE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\bmake\b[^;&|]*?\b(record-checked|tick|accept)\b")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// What one decision reads.
pub(crate) struct Ctx {
    pub procs: Procs,
    pub top: PathBuf,
    pub python: &'static str,
}

/// Whether a make of this target runs in this tree (`own-make.sh`): the program by its name, the tree by its cwd.
fn runs_here(c: &Ctx, target: &str) -> bool {
    let wanted = format!("make {target}");
    let top = format!("{}/", c.top.display());
    c.procs.pids().into_iter().any(|p| {
        let raw = c.procs.read(p, "cmdline");
        let program = raw.split('\0').next().unwrap_or("");
        let name = program.rsplit('/').next().unwrap_or("");
        let is_make = ["make", "gmake"]
            .iter()
            .any(|m| name == *m || name.starts_with(&format!("{m} ")));
        is_make
            && raw.replace('\0', " ").contains(&wanted)
            && c.procs
                .link(p, "cwd")
                .is_some_and(|d| format!("{}/", d.display()).starts_with(&top))
    })
}

fn running(c: &Ctx, target: &str) -> bool {
    runs_here(c, &format!("--no-print-directory {target}")) || runs_here(c, target)
}

/// The escape's verdict: `Some(answers)` when it decides the call.
fn escaped(event: &Event, session: &Session, cmd: &str) -> Option<Vec<Answer>> {
    match escape_or_refuse(cmd, "GATE_WRITE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "gate-write",
                "escaped",
                &why,
                "gate-write-ok",
                &event.input,
                session,
            );
            Some(Vec::new())
        }
        Escape::Refused(text) => {
            let shown: String = cmd.chars().take(200).collect();
            log::fire(
                "gate-write",
                "blocked",
                &shown,
                "GATE_WRITE_OK-no-reason",
                &event.input,
                session,
            );
            Some(vec![Answer::Refuse(text)])
        }
        Escape::None => None,
    }
}

fn relative_in(top: &Path, file: &str) -> Option<String> {
    realpath(Path::new(file))
        .strip_prefix(realpath(top))
        .ok()
        .map(|r| r.to_string_lossy().into_owned())
}

fn input_field<'a>(event: &'a Event, key: &str) -> &'a str {
    event.input.get("tool_input").map_or("", |t| field(t, key))
}

fn file_of(event: &Event) -> &str {
    Some(input_field(event, "file_path"))
        .filter(|f| !f.is_empty())
        .unwrap_or(input_field(event, "notebook_path"))
}

/// What a running cache audit refuses: an engine edit, even a docstring, and a commit.
fn audit_refusal(event: &Event, c: &Ctx) -> Option<String> {
    let tool = event.tool();
    if FILE_TOOLS.contains(&tool) {
        let rel = relative_in(&c.top, file_of(event))?;
        let first = rel.split('/').next().unwrap_or("");
        return (first == "l7r" || first == "pool").then(|| format!("an {tool} of {rel}"));
    }
    let cmd = input_field(event, "command");
    (tool == "Bash" && GIT_WRITE.is_match(cmd).unwrap_or(false))
        .then(|| "a git commit or add".to_owned())
}

/// The question the gate itself asks: exit 0 when the change is one it does not see.
fn unseen(c: &Ctx, extra: &[&str]) -> bool {
    let top = c.top.to_string_lossy();
    let gate_dir = ask(&c.top, "git", &["rev-parse", "--absolute-git-dir"], "").out;
    let snap = format!("{gate_dir}/gate-tree.json");
    let tool = c.top.join("scripts/gates/preflight.py");
    let mut args = vec![
        tool.to_str().unwrap_or(""),
        "--root",
        top.as_ref(),
        "--tree-check",
        snap.as_str(),
    ];
    args.extend_from_slice(extra);
    ask_within(&c.top, c.python, &args, Duration::from_secs(20)).ok()
}

/// The file's text as this edit would leave it, or None.
fn after_edit(event: &Event, file: &str) -> Option<String> {
    match event.tool() {
        "Write" => Some(input_field(event, "content").to_owned()),
        "Edit" => {
            let current = std::fs::read_to_string(file).ok()?;
            let (old, new) = (
                input_field(event, "old_string"),
                input_field(event, "new_string"),
            );
            let all = event
                .input
                .get("tool_input")
                .and_then(|t| t.get("replace_all"))
                .and_then(serde_json::Value::as_bool)
                .unwrap_or(false);
            Some(if all {
                current.replace(old, new)
            } else {
                current.replacen(old, new, 1)
            })
        }
        _ => None,
    }
}

/// What a running gate refuses: a change it would see.
fn gate_refusal(event: &Event, c: &Ctx) -> Option<String> {
    let tool = event.tool();
    if FILE_TOOLS.contains(&tool) {
        let file = file_of(event);
        let rel = relative_in(&c.top, file).filter(|r| !r.is_empty())?;
        let invisible = after_edit(event, file).is_some_and(|text| {
            let scratch =
                std::env::temp_dir().join(format!("l7r-gate-write-{}", std::process::id()));
            let wrote = std::fs::write(&scratch, text).is_ok();
            let said = wrote
                && unseen(
                    c,
                    &[
                        "--would-write",
                        &rel,
                        "--content",
                        &scratch.to_string_lossy(),
                    ],
                );
            let _ = std::fs::remove_file(&scratch);
            said
        });
        return (!invisible).then(|| format!("an {tool} of {rel}"));
    }
    if tool != "Bash" {
        return None;
    }
    let cmd = input_field(event, "command");
    if GIT_WRITE.is_match(cmd).unwrap_or(false) {
        return (!unseen(c, &["--quiet"])).then(|| "a git commit or add of a change the gate sees (it moves HEAD, or what the gate compares against it)".to_owned());
    }
    let found = MAKE_WRITE.captures(cmd).ok().flatten()?;
    Some(format!("make {} (it writes a tracked record)", &found[1]))
}

/// The working tree a directory stands in, or the directory itself outside one.
pub(crate) fn top_of(here: &Path) -> PathBuf {
    here.ancestors()
        .find(|d| d.join(".git").exists())
        .unwrap_or(here)
        .to_path_buf()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let top = top_of(&here);
    judge(
        event,
        session,
        &Ctx {
            procs: Procs {
                root: PathBuf::from("/proc"),
                mine: std::process::id(),
            },
            top,
            python: "python3",
        },
    )
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Ctx) -> Vec<Answer> {
    let cmd = input_field(event, "command");
    if running(c, "cache-audit") {
        if let Some(answers) = escaped(event, session, cmd) {
            return answers;
        }
        if let Some(what) = audit_refusal(event, c) {
            log::fire(
                "gate-write",
                "blocked",
                &what,
                "write-during-cache-audit",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(format!(
                "\u{1b}[1mBLOCKED (gate-write): {what} while this tree's `make cache-audit` runs.\u{1b}[0m\n\
The audit has a perturbed literal in an engine file until it ends; a commit now carries it (feature 426: 335cfa840).\n\
Wait for its exit (it is a background job: its notification is the end), then make the change.\n\
(feature 426 T10; escape GATE_WRITE_OK=\"<reason>\")"
            ))];
        }
    }
    if !running(c, "done") {
        return Vec::new();
    }
    if let Some(answers) = escaped(event, session, cmd) {
        return answers;
    }
    let Some(what) = gate_refusal(event, c) else {
        return Vec::new();
    };
    log::fire(
        "gate-write",
        "blocked",
        &what,
        "write-during-gate",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\u{1b}[1mBLOCKED (gate-write): {what} while this tree's `make done` runs.\u{1b}[0m\n\
A write during the run voids its verdict (\"the tree moved while the gate ran\") and costs the whole gate again.\n\
Wait for it: `make verify-wait`, run_in_background - its exit is the notification - then make the change.\n\
(feature 385, plan D13; escape GATE_WRITE_OK=\"<reason>\")"
    ))]
}

#[cfg(test)]
mod tests;
