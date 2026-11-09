//! `conflict-marker-hooks` (feature 241; ported from the shell of the same name, feature 449 T023): A `git add` OR `git commit` THAT WOULD
//! STAGE AN UNRESOLVED MERGE CONFLICT IS REFUSED. Twice in one day a conflicted merge was committed with its markers in it (the GM,
//! 2026-09-13), and history here is never rewritten, so a marker that lands stays. What counts is the TRIPLE `git merge` leaves, in order,
//! at column 0; there is deliberately no fenced-block exemption, because git writes its markers wherever the conflict falls. What a command
//! would stage is asked of git (`add --dry-run`), never enumerated. `CONFLICT_MARKERS_OK` with a reason is the escape, in the command or, for
//! a file that must show a triple, at the start of a line in its first 40.
//!
//! Plan T023's decisions: (a) the guard's half of `lib/hm_conflict.py` in-process; (b) that file stays for the push's `--tracked`, `--list`
//! and `--selftest` until T051.

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::discard_hooks::shlex;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "conflict-marker-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// The file-level exemption's marker.
pub const EXEMPT: &str = "CONFLICT_MARKERS_OK:";
/// How far down a file the exemption may stand.
pub const HEAD_LINES: usize = 40;

static ASSIGNMENT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?:^|[;&|\s])([A-Za-z_][A-Za-z0-9_]*)=([^\s;&|]+)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// A real file-level exemption stands at the START of its line, with two words of reason, not a `<placeholder>`: a mention is no declaration.
pub(crate) fn declares_exemption(line: &str) -> bool {
    exemption_reason(line).is_some()
}

/// The reason a real file-level exemption states, or None.
#[must_use]
pub fn exemption_reason(line: &str) -> Option<String> {
    let start = line.trim_start_matches(|c: char| c.is_whitespace() || "#*:/;-".contains(c));
    let reason = start.strip_prefix(EXEMPT)?.trim();
    (!reason.starts_with('<') && reason.split_whitespace().count() >= 2).then(|| reason.to_owned())
}

/// The triple, in order, at column 0, unless the file claims its exemption.
#[must_use]
pub fn has_conflict(text: &str) -> bool {
    let (open, mid, close) = ("<".repeat(7), "=".repeat(7), ">".repeat(7));
    if text.lines().take(HEAD_LINES).any(declares_exemption) {
        return false;
    }
    let mut state = 0;
    for line in text.lines() {
        if state == 0 && line.starts_with(&open) {
            state = 1;
        } else if state == 1 && line.trim_end() == mid {
            state = 2;
        } else if state == 2 && line.starts_with(&close) {
            return true;
        }
    }
    false
}

/// Which of these carry a conflict; unreadable as text - binary, a directory, gone - is skipped.
#[must_use]
pub fn conflicted(paths: &BTreeSet<String>) -> Vec<String> {
    paths
        .iter()
        .filter(|p| std::fs::read_to_string(p).is_ok_and(|t| has_conflict(&t)))
        .cloned()
        .collect()
}

fn expand(token: &str, vars: &[(String, String)]) -> String {
    vars.iter().fold(token.to_owned(), |t, (k, v)| {
        t.replace(&format!("${{{k}}}"), v)
            .replace(&format!("${k}"), v)
    })
}

fn assignments(cmd: &str) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = Vec::new();
    for caps in ASSIGNMENT.captures_iter(cmd).filter_map(Result::ok) {
        let value = caps[2].trim_matches(|q| q == '"' || q == '\'').to_owned();
        match out.iter_mut().find(|(k, _)| *k == caps[1]) {
            Some(slot) => slot.1 = value,
            None => out.push((caps[1].to_owned(), value)),
        }
    }
    out
}

fn git_lines(repo: &str, args: &[&str]) -> Vec<String> {
    let all: Vec<&str> = ["-C", repo]
        .into_iter()
        .chain(args.iter().copied())
        .collect();
    let dir = if Path::new(repo).is_dir() { repo } else { "." };
    ask(Path::new(dir), "git", &all, "")
        .out
        .lines()
        .filter(|l| !l.is_empty())
        .map(str::to_owned)
        .collect()
}

fn joined(base: &str, tail: &str) -> String {
    Path::new(base).join(tail).to_string_lossy().into_owned()
}

/// What `git add`, by asking its dry run, would stage: `.` stays scoped, a directory expands, and -A and -u mean what git means by them.
fn added(repo: &str, args: &[String]) -> Vec<String> {
    let mut all = vec!["add", "--dry-run", "--ignore-missing"];
    all.extend(args.iter().map(String::as_str));
    git_lines(repo, &all)
        .iter()
        .filter_map(|l| {
            let line = l.trim();
            let tail = line
                .strip_prefix("add '")
                .or_else(|| line.strip_prefix("remove '"))?;
            Some(joined(repo, tail.strip_suffix('\'')?))
        })
        .collect()
}

/// A commit carries what is already staged; `-a` adds tracked changes; named paths add those.
fn committed(repo: &str, args: &[String]) -> Vec<String> {
    let mut out: Vec<String> = git_lines(repo, &["diff", "--cached", "--name-only"])
        .iter()
        .map(|p| joined(repo, p))
        .collect();
    let all = args.iter().any(|f| {
        f == "--all" || (f.starts_with('-') && !f.starts_with("--") && f[1..].contains('a'))
    });
    if all {
        out.extend(
            git_lines(repo, &["diff", "--name-only"])
                .iter()
                .map(|p| joined(repo, p)),
        );
    }
    // a message is not a pathspec: drop the argument of -m and its kin before asking git
    let takes = ["-m", "--message", "-F", "--file", "--author", "--date"];
    let dropped: Vec<&String> = args
        .iter()
        .zip(args.iter().skip(1))
        .filter(|(a, _)| takes.contains(&a.as_str()))
        .map(|(_, v)| v)
        .collect();
    let keep: Vec<&str> = args
        .iter()
        .filter(|a| !a.starts_with('-') && !dropped.contains(a))
        .map(String::as_str)
        .collect();
    if !keep.is_empty() {
        let mut query = vec!["status", "--porcelain", "--"];
        query.extend(keep);
        out.extend(
            git_lines(repo, &query)
                .iter()
                .map(|l| joined(repo, l.get(3..).unwrap_or(""))),
        );
    }
    out
}

/// The files a `git add` or `git commit` in this command would stage, asked of git.
#[must_use]
pub fn staged_by(cmd: &str, base: &str) -> BTreeSet<String> {
    let vars = assignments(cmd);
    let mut here = base.to_owned();
    let mut paths = BTreeSet::new();
    for piece in cmd
        .split("&&")
        .flat_map(|p| p.split("||"))
        .flat_map(|p| p.split([';', '|']))
    {
        let raw =
            shlex(piece).unwrap_or_else(|| piece.split_whitespace().map(str::to_owned).collect());
        let toks: Vec<String> = raw.iter().map(|t| expand(t, &vars)).collect();
        if toks.len() > 1 && toks[0] == "cd" {
            here = joined(&here, &toks[1]);
            continue;
        }
        let Some(g) = toks.iter().position(|t| t == "git") else {
            continue;
        };
        let mut rest = &toks[g + 1..];
        let mut repo = here.clone();
        while rest.len() >= 2 && (rest[0] == "-C" || rest[0] == "-c") {
            if rest[0] == "-C" {
                repo = joined(&here, &rest[1]);
            }
            rest = &rest[2..];
        }
        let Some((sub, tail)) = rest.split_first() else {
            continue;
        };
        let args: Vec<String> = tail
            .iter()
            .filter(|a| *a != "--dry-run" && *a != "-n")
            .cloned()
            .collect();
        match sub.as_str() {
            "add" => paths.extend(added(&repo, &args)),
            "commit" => paths.extend(committed(&repo, &args)),
            _ => {}
        }
    }
    paths
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    judge(event, session, &here.to_string_lossy())
}

pub(crate) fn judge(event: &Event, session: &Session, base: &str) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if cmd.is_empty() {
        return Vec::new();
    }
    match escape_or_refuse(cmd, "CONFLICT_MARKERS_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "conflict-marker",
                "escaped",
                &why,
                "conflict-markers-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            let shown: String = cmd.chars().take(200).collect();
            log::fire(
                "conflict-marker",
                "blocked",
                &shown,
                "CONFLICT_MARKERS_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if !cmd.contains("git") || !(cmd.contains("add") || cmd.contains("commit")) {
        return Vec::new();
    }
    let bad = conflicted(&staged_by(cmd, base));
    if bad.is_empty() {
        return Vec::new();
    }
    log::fire(
        "conflict-marker",
        "blocked",
        if bad.len() > 1 { "git-many" } else { "git-one" },
        "staged-conflict",
        &event.input,
        session,
    );
    let listed = bad
        .iter()
        .map(|p| format!("  {p}"))
        .collect::<Vec<_>>()
        .join("\n");
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mBLOCKED: this would stage a file that still carries a merge conflict.\u{1b}[0m\n{listed}\n\n\
Each file above still holds the triple `git merge` left in it. Resolve them and stage what you\n\
resolved - this guard will not pick which is which, because only you know that.\n\n\
Why this is refused rather than narrowed to the clean files: the harm is the COMMIT. The history\n\
here is never rewritten, so a marker that lands cannot be amended away - it took an hour to redo a\n\
merge from its base on 2026-09-13, and one file went unnoticed on 2026-09-12 until `make\n\
notes-census` could not parse it. `git add -A` is not the problem and is not blocked; an\n\
UNRESOLVED file is.\n\n\
A file that carries a marker on purpose - a fixture, a doc about merges - passes with\n\
CONFLICT_MARKERS_OK=\"<reason>\" in the command.\n"
    ))]
}

#[cfg(test)]
mod tests;
