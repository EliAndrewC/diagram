//! `make quick`'s checks over what `make task-add` wrote (feature 451 T19, D16; FR-011): each check line of the `quick:` recipe, read
//! from `make -n quick` so the recipe stays the one list, run as its own process to its own end - the lines side by side - and its
//! failures compared between the run with the line and, on a red, the run without it.
//!
//! WHY (feature 449, 2026-11-19): a task line citing a bare requirement id another feature defines ("FR-023" with no "feature 444")
//! passed `make task-add` and failed `make quick` at the landing. A sequential `make quick` stops at its first red, so a check already
//! red earlier (ruff, say) would hide the line's own failure in a later one (spec-lint): hence each line to its own end. Not
//! `make -i quick`: it would still stamp quick green.
//!
//! A FAILURE is a check's exit (`failed (exit N)`) and each non-blank line it prints, its line and column numbers masked ([`mask`]: the
//! box shifts every later finding of the file it writes), compared as a multiset: a failure the with-line run has and the other lacks
//! is the line's, whatever else is red.

use std::collections::BTreeMap;
use std::path::Path;
use std::process::{Command, Output, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::tick::text::re;

/// The one line of `make -n quick` set aside besides the closing `printf` (D16), by a text of its own line: the stamp, which would mark
/// quick green. Every other line is RUN, so a check added to quick is run here with nothing to update. Not a list of the checks that
/// cannot read what task-add writes: running all seven side by side costs 0.12 s against 0.10 s for the two that read a specs/ file,
/// measured 2026-11-20 (`date +%s%N` around `sh -c`, shell `&` and `wait`, three runs), and such a list goes stale silently when a
/// check's inputs change (the lead's ruling on T19, 2026-11-20).
const STAMP: &str = "state write green-local";

/// A location's numbers: `:12`, `:12:3`, `line 12`, `lines 12`.
static LOCATION: LazyLock<Regex> = LazyLock::new(|| re(r"(?::[0-9]+)+|\blines? [0-9]+"));

/// A recipe line's continuation: the backslash, the newline and the next line's indent.
static CONTINUED: LazyLock<Regex> = LazyLock::new(|| re(r"[ \t]*\\\n[ \t]*"));

/// The make launcher's prefix, shown shorter in a failure's name.
const LAUNCHER: &str = "\"$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" ";

/// One failure: the check's line as shown, what it printed (or its exit), and the two masked as the comparison reads them.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(super) struct Failure {
    check: String,
    finding: String,
}

impl Failure {
    fn key(&self) -> String {
        format!("{}\0{}", self.check, mask(&self.finding))
    }

    /// As a refusal names it.
    pub(super) fn shown(&self) -> String {
        format!("  {}: {}\n", self.check, self.finding)
    }
}

/// A finding with its line and column numbers masked.
pub(super) fn mask(finding: &str) -> String {
    LOCATION
        .replace_all(finding, |c: &fancy_regex::Captures<'_>| {
            if c[0].starts_with(':') {
                ":#".to_owned()
            } else {
                format!("{} #", c[0].split(' ').next().unwrap_or("line"))
            }
        })
        .into_owned()
}

/// The check lines of `make -n quick` in `root` (a line continued by a backslash read as one), the [`STAMP`] and the closing `printf`
/// left out; the error when make cannot list them. The parent make's flags are not handed down: `-n` is asked, never inherited.
pub(super) fn lines(root: &Path) -> Result<Vec<String>, String> {
    let out = Command::new("make")
        .args(["-n", "--no-print-directory", "quick"])
        .current_dir(root)
        .env_remove("MAKEFLAGS")
        .env_remove("MFLAGS")
        .env_remove("MAKELEVEL")
        .stdin(Stdio::null())
        .output()
        .map_err(|e| format!("make -n quick: {e}"))?;
    if !out.status.success() {
        return Err(format!(
            "make -n quick: {}",
            String::from_utf8_lossy(&out.stderr).trim()
        ));
    }
    let text = CONTINUED
        .replace_all(&String::from_utf8_lossy(&out.stdout), " ")
        .into_owned();
    Ok(text
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with("printf ") && !l.contains(STAMP))
        .map(str::to_owned)
        .collect())
}

/// Each line run in `root` by `sh -c`, side by side, to its own end: the failures of those that fail.
pub(super) fn run(root: &Path, lines: &[String]) -> Vec<Failure> {
    let started: Vec<_> = lines
        .iter()
        .map(|line| {
            let child = Command::new("sh")
                .args(["-c", line])
                .current_dir(root)
                .stdin(Stdio::null())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn();
            (line.replace(LAUNCHER, "l7r-gate "), child)
        })
        .collect();
    let mut failures = Vec::new();
    for (check, child) in started {
        let out = child.and_then(std::process::Child::wait_with_output);
        failures.extend(failed(&check, out));
    }
    failures
}

/// A finished check's failures: none when it passed.
fn failed(check: &str, out: std::io::Result<Output>) -> Vec<Failure> {
    let one = |finding: String| Failure {
        check: check.to_owned(),
        finding,
    };
    let out = match out {
        Ok(out) if out.status.success() => return Vec::new(),
        Ok(out) => out,
        Err(e) => return vec![one(format!("could not run: {e}"))],
    };
    let exit = out
        .status
        .code()
        .map_or_else(|| "killed by a signal".to_owned(), |c| format!("exit {c}"));
    let mut all = vec![one(format!("failed ({exit})"))];
    for stream in [&out.stdout, &out.stderr] {
        all.extend(
            String::from_utf8_lossy(stream)
                .lines()
                .filter(|l| !l.trim().is_empty())
                .map(|l| one(l.to_owned())),
        );
    }
    all
}

/// The failures of `with` that `without` does not account for, as a multiset of masked findings.
pub(super) fn introduced(with: &[Failure], without: &[Failure]) -> Vec<Failure> {
    let mut left: BTreeMap<String, usize> = BTreeMap::new();
    for f in without {
        *left.entry(f.key()).or_default() += 1;
    }
    with.iter()
        .filter(|f| {
            let count = left.entry(f.key()).or_default();
            let added = *count == 0;
            *count = count.saturating_sub(1);
            added
        })
        .cloned()
        .collect()
}

#[cfg(test)]
mod tests;
