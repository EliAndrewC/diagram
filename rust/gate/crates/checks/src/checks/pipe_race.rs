//! No shell file under `tests/` or `scripts/` pipes into an early-exit grep (feature 451 T253, from T252's self-grep in
//! `tests/hooks/test-closing-checks.sh`). Under pipefail, `printf '%s' "$OUT" | grep -q X` failed when grep matched early and exited
//! while its writer still had text to write: the writer died of SIGPIPE, the pipeline returned 141, a line the printed text showed read
//! absent and a negated check passed on a line that is there (T252: 1 in 3,000 at real size pinned to one CPU; 50 of 50 for every
//! writer, a variable, a list of arguments or a command, on a line followed by 1.3 MB, measured 2026-11-25). The fix is a here-string:
//! `seen VAR <args>` in a suite (`tests/hooks/seen.sh`), `grep <args> <<< "$x"` in a script, a command captured first.
//!
//! Every shell file is read, pipefail or not: a sourced file runs under its caller's (`scripts/hooks/lib/failed-open-log.sh`, sourced
//! by `l7r-guard.sh`), and a file that gains pipefail later would arm the race silently. `head` and `sed q` are not refused: every
//! such pipe in these files fed a failure message or an unchecked assignment, so its status was never read (451 T253, measured
//! 2026-11-25). Run by every `make hooks-test`, in its tail, which no unchanged suite skips. A run is recorded under `USAGE_LOG_TOOL`.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::{git_text, Outcome};

pub(super) const USAGE_LOG_TOOL: &str = "check-pipe-race";
/// The trees read, as `git ls-files` pathspecs.
const SCOPE: [&str; 2] = ["tests", "scripts"];
/// A line's escape, for text that is never run as a pipe (a command a suite feeds a guard as payload): its reason, two words or more.
const ESCAPE: &str = "# pipe-ok:";

fn pattern(text: &str) -> Regex {
    l7r_shared::regex::build(text).unwrap()
}

/// A pipe (not `||`) into grep, and the grep's words up to the next separator.
static PIPE_GREP: LazyLock<Regex> = LazyLock::new(|| pattern(r"(?:^|[^|])\|\s*grep\b([^|;&)]*)"));
/// A grep flag that exits before its input ends: quiet, a file's name, a count of matches.
static EARLY: LazyLock<Regex> = LazyLock::new(|| {
    pattern(
        r"(?:^|\s)(?:-[A-Za-z]*[qlm][A-Za-z0-9]*|--(?:quiet|silent|max-count|files-with-matches))(?=\s|=|$)",
    )
});
static SHEBANG: LazyLock<Regex> = LazyLock::new(|| pattern(r"^#!.*\b(?:ba)?sh\b"));

/// Does this line escape the check, with a reason of two words or more?
fn escaped(line: &str) -> bool {
    line.split_once(ESCAPE)
        .is_some_and(|(_, why)| why.split_whitespace().count() >= 2)
}

/// Does this (joined) line pipe into an early-exit grep?
fn races(line: &str) -> bool {
    PIPE_GREP
        .captures_iter(line)
        .map_while(Result::ok)
        .any(|c| {
            c.get(1)
                .is_some_and(|words| EARLY.is_match(words.as_str()).unwrap_or(false))
        })
}

/// The 1-based numbers and text of a shell text's lines that pipe into an early-exit grep. A comment line is a mention; a line ending
/// in a pipe (with or without its backslash) is read with the next, where its grep stands.
pub(super) fn scan(text: &str) -> Vec<(usize, String)> {
    let mut out = Vec::new();
    let mut held: Option<(usize, String)> = None;
    for (i, raw) in text.lines().enumerate() {
        if raw.trim_start().starts_with('#') {
            continue;
        }
        let (at, line) = match held.take() {
            Some((at, mut before)) => {
                before.push(' ');
                before.push_str(raw.trim_start());
                (at, before)
            }
            None => (i + 1, raw.to_owned()),
        };
        let end = line.trim_end().trim_end_matches('\\').trim_end();
        if end.ends_with('|') && !end.ends_with("||") {
            held = Some((at, end.to_owned()));
            continue;
        }
        if races(&line) && !escaped(&line) {
            out.push((at, line.trim().to_owned()));
        }
    }
    out
}

/// Is this tracked file a shell file: `.sh`, or a sh or bash shebang?
fn shell(root: &Path, file: &str) -> Option<String> {
    let text = std::fs::read_to_string(root.join(file)).ok()?;
    let first = text.lines().next().unwrap_or_default();
    (super::has_ext(file, "sh") || SHEBANG.is_match(first).unwrap_or(false)).then_some(text)
}

fn problems(root: &Path) -> Vec<String> {
    let listed = git_text(root, &["ls-files", "--", SCOPE[0], SCOPE[1]]);
    let mut out = Vec::new();
    for file in listed.lines() {
        if let Some(text) = shell(root, file) {
            for (at, line) in scan(&text) {
                let shown: String = line.chars().take(160).collect();
                out.push(format!("{file}:{at}: {shown}"));
            }
        }
    }
    out
}

/// `l7r-gate check pipe-race [--root ROOT]`.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    let root = args
        .iter()
        .position(|a| a == "--root")
        .and_then(|at| args.get(at + 1))
        .map_or(root, |r| Path::new(r));
    let bad = problems(root);
    if bad.is_empty() {
        return Outcome::out(
            "pipe-race: no shell file under tests/ or scripts/ pipes into an early-exit grep\n"
                .to_owned(),
        );
    }
    let mut err = String::new();
    for b in &bad {
        let _ = writeln!(err, "pipe-race: {b}");
    }
    let _ = writeln!(
        err,
        "pipe-race: {} line(s) pipe into grep -q/-l/-m, which under pipefail reads a present line absent when the writer dies of SIGPIPE (451 T253) - grep a here-string instead: in a suite `seen VAR -q <pattern>` (source tests/hooks/seen.sh), in a script `grep -q <pattern> <<< \"$VAR\"`; a command's text captured first, `o=$(cmd) && seen o -q <pattern>`; a line never run as a pipe (a guard's payload) takes `{ESCAPE} <why, two words or more>`",
        bad.len()
    );
    Outcome::refuse(err)
}

#[cfg(test)]
mod tests;
