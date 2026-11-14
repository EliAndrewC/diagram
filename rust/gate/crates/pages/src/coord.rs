//! A coordination file read and written by line - `make lines` and `make append` (feature 274 D5, FR-002). Ported whole from
//! `scripts/pages/coord.py` by feature 449 T137 (`ask:449-phase3-remainder`):
//!
//! ```text
//! l7r-gate coord lines <file> <regex>   the matching lines, numbered, at most MAX, then how many were shown of how many
//! l7r-gate coord append <file>          appends $LINE as one line (the file made if needed); prints only where
//! ```
//!
//! WHY (feature 274, research R1). The research sessions re-read their coordination files whole: 619 reads of the cross-session claims
//! file across 172 sessions (about 30 M tokens carried), 418 of a group's handoff across 254 sessions (about 20 M, though the briefs said
//! "read only your own lines") and 388 of a checks report across 183 sessions (about 12 M), mostly to append one line - about 60 M in
//! all, 5%. Every read stays in the session's context and is paid for again on every later turn. So a session reads only its own lines
//! and appends without reading.
//!
//! The line to append comes from the ENVIRONMENT (`make` exports its command-line variables to the recipe), not from an argument pasted
//! into the recipe, so quotes and `$` in it survive. A relative FILE is taken from the directory `make` ran in, else from the
//! repository root, so the same command works from the clone root or a subdirectory.
//!
//! The ledger row's lint and its cost cells are the `reviews` crate's, asked in process where the Python ran `l7r-gate reviews
//! ledger-lint` and `review-cost` (FR-003). KEY is read as Python's `re` reads it, as far as `fancy_regex` does: a pattern one accepts
//! and the other refuses (`\Z`, possessive quantifiers) is refused by its own words.

use std::io::{Read as _, Seek as _, SeekFrom, Write as _};
use std::path::{Path, PathBuf};

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::{py_name, py_parent, splitlines};

use crate::{py_path, raised, reply};
use l7r_gate_core::Reply;

/// Lines shown at most: a KEY that matches more is too wide, and the count says so.
pub const MAX: usize = 80;
/// The review ledger's measured table, under whose heading a row is linted.
const MEASURED_HEADING: &str = "## Review checks, measured (feature 294 on)";

/// What a run reads of its process, handed in so a test runs in a scratch tree.
pub struct Env<'a> {
    /// The directory `make` ran in.
    pub cwd: PathBuf,
    /// A variable of the environment (`LINE`, `AGENT`, `HOME`).
    pub var: &'a dyn Fn(&str) -> Option<String>,
}

/// FILE as given: absolute; else under the directory make ran in if it (or its parent directory) is there; else under the repository
/// root.
#[must_use]
pub fn resolve(name: &str, cwd: &Path) -> PathBuf {
    let p = py_path(name);
    if p.is_absolute() {
        return p;
    }
    let here = cwd.join(&p);
    if here.exists() || py_parent(&here).is_dir() {
        return here;
    }
    let top = l7r_gate_core::record::repo::git(cwd, &["rev-parse", "--show-toplevel"]);
    let top = strip(&top);
    if top.is_empty() {
        here
    } else {
        Path::new(top).join(p)
    }
}

/// KEY in the regex crate's spelling where Python's differs: `\Z`, Python's end of the text, is `\z` (an escaped backslash is kept as it
/// is; found by the differential, feature 449 T137, where `KEY='\Z'` matched every line in Python and was refused here).
fn py_pattern(key: &str) -> String {
    let mut out = String::new();
    let mut chars = key.chars();
    while let Some(c) = chars.next() {
        out.push(c);
        if c == '\\' {
            match chars.next() {
                Some('Z') => out.push('z'),
                Some(n) => out.push(n),
                None => {}
            }
        }
    }
    out
}

/// The output of `make lines`: each matching line as `<number>: <text>`, then the count line.
///
/// # Errors
///
/// The file cannot be read (`Err(Ok(why))`, the Python's raise), or KEY is no regular expression (`Err(Err(why))`).
pub fn lines(path: &Path, key: &str) -> Result<Vec<String>, Result<String, String>> {
    let text = l7r_guard::shared::speckit::read_text(path).map_err(Ok)?;
    let all = splitlines(&text);
    let rx = Regex::new(&py_pattern(key)).map_err(|e| Err(e.to_string()))?;
    let hits: Vec<String> = all
        .iter()
        .enumerate()
        .filter(|(_, ln)| rx.is_match(ln).unwrap_or(false))
        .map(|(n, ln)| format!("{}: {ln}", n + 1))
        .collect();
    let mut out: Vec<String> = hits.iter().take(MAX).cloned().collect();
    out.push(format!(
        "({} of {} lines shown)",
        hits.len().min(MAX),
        all.len()
    ));
    if hits.len() > MAX {
        out.push(format!("({} more matched - narrow KEY)", hits.len() - MAX));
    }
    Ok(out)
}

/// Append ONE line, never reading the file but its last byte; a newline first only if the file does not already end with one.
///
/// # Errors
///
/// What the directory's making, the open or the write raised.
pub fn append(path: &Path, line: &str) -> Result<(), String> {
    let fail = |e: std::io::Error| format!("{}: {e}", path.display());
    std::fs::create_dir_all(py_parent(path)).map_err(fail)?;
    let mut fh = std::fs::OpenOptions::new()
        .read(true)
        .append(true)
        .create(true)
        .open(path)
        .map_err(fail)?;
    let end = fh.seek(SeekFrom::End(0)).map_err(fail)?;
    let mut lead = "";
    if end > 0 {
        let mut last = [0u8];
        fh.seek(SeekFrom::End(-1)).map_err(fail)?;
        fh.read_exact(&mut last).map_err(fail)?;
        lead = if last[0] == b'\n' { "" } else { "\n" };
    }
    fh.write_all(format!("{lead}{}\n", line.trim_end_matches('\n')).as_bytes())
        .map_err(fail)
}

/// A review-ledger row judged by the ledger's own lint BEFORE it is appended (feature 383 amendment 2, a defect found on the way: `make
/// append ... && git commit` in one command had the commit's ledger hook judge the ledger before the row existed, so a row with a wrong
/// class word was committed and only a tooling test caught it). Any other file: nothing to judge. The row is judged under the measured
/// table's heading, as `ledger_lint.problems` judged it in memory and the Python's scratch file did since feature 449 T83.
#[must_use]
pub fn ledger_row_problems(path: &Path, line: &str) -> Vec<String> {
    if py_name(path) != "review-ledger.md" || py_name(&py_parent(path)) != "dev" {
        return Vec::new();
    }
    l7r_guard::shared::ledger::problems(&format!("{MEASURED_HEADING}\n{line}\n"))
        .iter()
        .map(|p| p.split_once(": ").map_or(p.as_str(), |(_, r)| r).to_owned())
        .collect()
}

/// A ledger row closed with its cost cells: `line` (its cells up to `acted on`) then `wall | tokens |`.
#[must_use]
pub fn with_cost(line: &str, cells: &str) -> String {
    let head = line.trim_end_matches(l7r_guard::shared::py_text::is_space);
    let bar = if head.ends_with('|') { "" } else { " |" };
    format!("{head}{bar} {cells} |")
}

/// The latest return's cost cells of review agent `agent` (`l7r-gate reviews review-cost --last`, in process) - the one place they are
/// read.
///
/// WHY (the round arbiter on hour:374-match-the-research-continued@1): a session composing the cells through a shell variable
/// (`C=$(make review-cost ...)`, then `LINE="... $C |"`) had its row judged by the ledger hook before the shell expanded it - about
/// fourteen refusals in a window, one taking the reply file written before it down too.
///
/// # Errors
///
/// The cost's own message, or that there is none.
pub fn agent_cells(agent: &str, home: &str) -> Result<String, String> {
    let args = ["--agent", agent, "--last"].map(str::to_owned);
    let out = l7r_gate_reviews::reviews::ledger::cost_cli(&args, home);
    let last = splitlines(strip(&out.stdout))
        .last()
        .map_or_else(String::new, |l| (*l).to_owned());
    if out.code != 0 || last.is_empty() {
        // `stderr.strip() or f"no cost for agent {agent}"`
        let (why, fallback) = (strip(&out.stderr), format!("no cost for agent {agent}"));
        return Err(Some(why)
            .filter(|w| !w.is_empty())
            .map_or(fallback, str::to_owned));
    }
    Ok(last)
}

const USAGE: &str =
    "usage: l7r-gate coord lines <file> <regex> | l7r-gate coord append <file>  (the line in $LINE)\n";

/// `l7r-gate coord lines <file> <regex>` and `coord append <file>`: exit 2 on a refusal (no file, a KEY that is no pattern, no LINE or
/// more than one, no cost for AGENT, a ledger row the lint refuses), with the Python's `make lines:` and `make append:` words.
#[must_use]
pub fn cli(args: &[String], env: &Env) -> Reply {
    match (args.first().map(String::as_str), args.len()) {
        (Some("lines"), 3) => lines_cli(&args[1], &args[2], env),
        (Some("append"), 2) => append_cli(&args[1], env),
        _ => reply(String::new(), USAGE.to_owned(), 2),
    }
}

fn lines_cli(file: &str, key: &str, env: &Env) -> Reply {
    let path = resolve(file, &env.cwd);
    if !path.is_file() {
        return reply(
            String::new(),
            format!("make lines: no file {}\n", path.display()),
            2,
        );
    }
    match lines(&path, key) {
        Ok(out) => reply(format!("{}\n", out.join("\n")), String::new(), 0),
        Err(Ok(why)) => raised("coord", String::new(), &why),
        Err(Err(why)) => reply(
            String::new(),
            format!("make lines: KEY is not a regular expression - {why}\n"),
            2,
        ),
    }
}

fn append_cli(file: &str, env: &Env) -> Reply {
    let mut line = (env.var)("LINE").unwrap_or_default();
    if strip(&line).is_empty() || line.trim_matches('\n').contains('\n') {
        return reply(
            String::new(),
            "make append: LINE=<text> is required, and it is ONE line\n".to_owned(),
            2,
        );
    }
    let path = resolve(file, &env.cwd);
    // `make append ... AGENT=<id>`: the row's cost cells filled from the agent's own transcript
    if let Some(agent) = (env.var)("AGENT").filter(|a| !a.is_empty()) {
        match agent_cells(&agent, &(env.var)("HOME").unwrap_or_default()) {
            Ok(cells) => line = with_cost(&line, &cells),
            Err(why) => {
                return reply(
                    String::new(),
                    format!("make append: AGENT={agent} - {why}\n"),
                    2,
                )
            }
        }
    }
    let bad = ledger_row_problems(&path, &line);
    if !bad.is_empty() {
        return reply(
            String::new(),
            format!(
                "make append: the ledger row was NOT appended - {}\n",
                bad.join("; ")
            ),
            2,
        );
    }
    match append(&path, &line) {
        Ok(()) => reply(
            format!("appended to {}\n", path.display()),
            String::new(),
            0,
        ),
        Err(why) => raised("coord", String::new(), &why),
    }
}

#[cfg(test)]
mod tests;
