//! `ledger-hooks` (feature 294, 371; ported from the shell of the same name, feature 449 T027): A `git commit` STAGING THE REVIEW LEDGER WITH A
//! ROW SHORT OF ITS CHECK, ITS CLASS OR ITS COST IS REFUSED, so "is the review pulling its weight" is a total, not an impression (the GM,
//! 2026-10-01). Every check pass with no row is named at each commit, never refused there. A command that appends its rows and commits is
//! judged on the ledger as it will be committed. `LEDGER_LINT_OK` with a reason is the escape.
//!
//! Plan T027's decisions: (a) the guard's reading of the command in-process; (b) what a row owes and what is owed are `ledger_lint.py`,
//! `ledger_owed.py` and `review_cost.py`, phase-3 tools asked by path on a `git commit`.

use std::path::{Path, PathBuf};

use crate::guards::discard_hooks::shlex;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "ledger-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

const LEDGER: &str = "dev/review-ledger.md";

/// What one decision reads.
pub(crate) struct Ctx {
    pub here: PathBuf,
    pub tree: PathBuf,
    pub python: &'static str,
}

impl Ctx {
    /// A review tool: the repository's own copy, else this tree's.
    fn tool(&self, root: &str, name: &str) -> String {
        let own = Path::new(root).join("scripts/reviews").join(name);
        let path = if own.is_file() {
            own
        } else {
            self.tree.join("scripts/reviews").join(name)
        };
        path.to_string_lossy().into_owned()
    }

    fn git(&self, root: &str, args: &[&str]) -> String {
        let all: Vec<&str> = ["-C", root]
            .into_iter()
            .chain(args.iter().copied())
            .collect();
        ask(&self.here, "git", &all, "").out
    }
}

/// The directory a `git commit` in this command runs in, `.` for none named; None when the command commits nothing.
pub(crate) fn commit_root(cmd: &str) -> Option<String> {
    let words = shlex(cmd).unwrap_or_default();
    for (i, _) in words.iter().enumerate().filter(|(_, w)| *w == "git") {
        let (mut j, mut place) = (i + 1, String::new());
        while j < words.len() && words[j].starts_with('-') {
            if words[j] == "-C" && j + 1 < words.len() {
                place.clone_from(&words[j + 1]);
                j += 2;
            } else if words[j] == "-c" && j + 1 < words.len() {
                j += 2;
            } else {
                j += 1;
            }
        }
        if words.get(j).map(String::as_str) == Some("commit") {
            return Some(if place.is_empty() {
                ".".to_owned()
            } else {
                place
            });
        }
    }
    None
}

/// The row a `make append` in this command will write to the ledger, cost cells included for `AGENT=`.
fn appended(cmd: &str, cost_tool: &str, c: &Ctx) -> Option<String> {
    let words = shlex(cmd).unwrap_or_default();
    let at = words
        .windows(2)
        .position(|w| w[0] == "make" && w[1] == "append")?;
    let args: Vec<(&str, &str)> = words[at + 2..]
        .iter()
        .take(4)
        .filter_map(|a| a.split_once('='))
        .collect();
    let value = |k: &str| args.iter().find(|(n, _)| *n == k).map_or("", |(_, v)| *v);
    let line = value("LINE");
    if line.is_empty() || !value("FILE").trim_end_matches('/').ends_with(LEDGER) {
        return None;
    }
    let mut row = line.to_owned();
    if !value("AGENT").is_empty() {
        let said = ask(
            &c.here,
            c.python,
            &[cost_tool, "--agent", value("AGENT"), "--last"],
            "",
        );
        if let Some(cost) = said.out.lines().last().filter(|_| said.ok()) {
            let head = line.trim_end();
            row = format!(
                "{head}{} {cost} |",
                if head.ends_with('|') { "" } else { " |" }
            );
        }
    }
    Some(row)
}

/// Whether this commit stages the ledger: what is staged, what `-a` takes, what the command's own `git add` names.
fn stages_ledger(cmd: &str, root: &str, row: bool, c: &Ctx) -> bool {
    let spaced = format!(" {cmd} ");
    let has = |w: &[&str]| w.iter().any(|x| spaced.contains(x));
    let mut staged = c.git(root, &["diff", "--cached", "--name-only"]);
    if has(&[" -a ", " -am ", " --all "]) {
        staged.push(' ');
        staged += &c.git(root, &["diff", "--name-only"]);
    }
    if spaced.contains(" add ")
        && (spaced.contains(LEDGER) || has(&[" -A ", " --all ", " -u ", " . ", " dev ", " dev/ "]))
    {
        staged.push(' ');
        staged += &c.git(root, &["diff", "--name-only"]);
        if row {
            staged.push(' ');
            staged += LEDGER;
        }
    }
    staged.contains(LEDGER)
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(
        event,
        session,
        &Ctx {
            here,
            tree,
            python: "python3",
        },
    )
}

/// The escape's verdict, where it decides the call.
fn escaped(cmd: &str, shown: &str, event: &Event, session: &Session) -> Option<Vec<Answer>> {
    match escape_or_refuse(cmd, "LEDGER_LINT_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "ledger",
                "escaped",
                &why,
                "ledger-lint-ok",
                &event.input,
                session,
            );
            return Some(Vec::new());
        }
        Escape::Refused(text) => {
            log::fire(
                "ledger",
                "blocked",
                shown,
                "LEDGER_LINT_OK-no-reason",
                &event.input,
                session,
            );
            return Some(vec![Answer::Refuse(text)]);
        }
        Escape::None => {}
    }
    None
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Ctx) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    let shown: String = cmd.chars().take(200).collect();
    if !cmd.split("git").skip(1).any(|rest| rest.contains("commit")) {
        return Vec::new();
    }
    if let Some(answers) = escaped(cmd, &shown, event, session) {
        return answers;
    }
    let Some(place) = commit_root(cmd) else {
        return Vec::new();
    };
    let place = if place == "." {
        c.here.to_string_lossy().into_owned()
    } else {
        place
    };
    let root = c.git(&place, &["rev-parse", "--show-toplevel"]);
    if root.is_empty() || !Path::new(&root).join(LEDGER).is_file() {
        return Vec::new();
    }
    let row = appended(cmd, &c.tool(&root, "review_cost.py"), c);
    let judged = Path::new(&root).join(LEDGER);
    // the ledger as it will read, judged from a copy removed when this returns (feature 449 T101)
    let dir = crate::shared::tempdir::TempDir::new("ledger");
    let scratch = dir.join("review-ledger.md");
    let ledger = row.as_ref().map_or(judged.clone(), |r| {
        let body = std::fs::read_to_string(&judged).unwrap_or_default();
        let _ = std::fs::write(&scratch, format!("{body}{r}\n"));
        scratch.clone()
    });
    let path = ledger.to_string_lossy().into_owned();
    let owed = ask(
        Path::new(&root),
        c.python,
        &[&c.tool(&root, "ledger_owed.py"), "--ledger", &path],
        "",
    )
    .out;
    let mut out = Vec::new();
    if !owed.is_empty() {
        out.push(Answer::Notice(owed));
    }
    if stages_ledger(cmd, &root, row.is_some(), c) {
        let said = ask(
            &c.here,
            c.python,
            &[&c.tool(&root, "ledger_lint.py"), &path],
            "",
        );
        if !said.ok() {
            log::fire(
                "ledger",
                "blocked",
                &shown,
                "ledger-row-short",
                &event.input,
                session,
            );
            let bad = said
                .out
                .lines()
                .map(|l| format!("  {l}"))
                .collect::<Vec<_>>()
                .join("\n");
            out = vec![Answer::Refuse(format!(
                "\n\u{1b}[1mBLOCKED: the review ledger's measured table has a row short of a cell.\u{1b}[0m\n{bad}\n\n\
Each row names its CHECK, its finding's CLASS (geometric | judgment | paperwork | nothing), whether the author had\n\
missed it, and the run's WALL and TOKENS copied from:\n\n    make review-cost AGENT=<the agent id>\n\n\
(feature 294: the ledger measures every check by itself, so \"is it pulling its weight\" is a total, not an impression.)\n\
A row that genuinely cannot carry a cell: LEDGER_LINT_OK=\"<reason>\" in the command.\n"
            ))];
        }
    }
    let _ = std::fs::remove_file(&scratch);
    out
}

#[cfg(test)]
mod tests;
