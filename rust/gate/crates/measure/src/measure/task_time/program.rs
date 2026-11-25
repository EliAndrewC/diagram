//! What a Bash call that runs no booked make target was (451 T243): its program, so the task time breakdown names every minute.
//!
//! WHY. `make where-time` booked 528.8 of 449's run minutes "other" on 2026-11-25 (`make where-time F=449 SINCE=2026-11-24T13:20Z`). Read
//! with their commands (the session's and its subagents' transcripts) across every clone's logs from 2026-11-24T13:20Z to
//! 2026-11-25T13:20Z, the unbooked Bash calls were 6,481 runs, 3,183 minutes: the main session's `until grep -q '^ALL DONE'
//! .../page-sessions/run-*.log` waits 1,247 (24 runs, in the background), the builders' `until [ -s ... ]` and `sleep N` waits 71, shell
//! reads and file edits 96, `for` loops over `pdftotext`, `make apply-edits` and `make reserve` 72, the builders' scratch `run.sh` cohort
//! sweeps 32, `python3` 12.5, `git` 6.3, and Makefile targets the guard's table does not book (`source-pages` 12.7, `research-search` 11.9,
//! `crate-checks` 8.8, ...), measured 2026-11-25 (a scratch reader over the logs and transcripts, the ends as `where_time::columns` finds
//! them). So the classes below are those, first first: a wait before anything it waits on, a scratch sweep before the makes it runs, a
//! make target before the programs around it.

use super::super::events::re;
use fancy_regex::Regex;
use std::sync::LazyLock;

/// A wait loop: it does no work; the time it holds is booked, as blocking, to what it waited on.
pub const WAIT: &str = "wait loops (held open, no work)";
/// The main session's wait on a detached page-session queue.
pub const PAGE_WAIT: &str = "wait loops on page sessions (held open, no work)";

static WAIT_LOOP: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:\b(?:until|while)\b[\s\S]*\bsleep\b|(?:^|[;&|(]\s*|\s)sleep\s+\d)"));
static SCRATCH: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:l7r-handoffs/\S*-scratch|/tmp/t\d+[a-z]?)/\S*run\.sh"));
static WORD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:^|[\s;&|(`{/])(cargo|l7r-mode-a|l7r-gate(?:\.sh)?|python3?|git|curl|wget|pdftotext|pdftoppm|pdfinfo|convert|rsvg-convert)\b",
    )
});

/// The class a command's run is booked to when it runs no booked make target, and the label it is listed by in the per-target table.
#[must_use]
pub fn class(command: &str) -> (&'static str, String) {
    if matches!(WAIT_LOOP.is_match(command), Ok(true)) {
        return if command.contains("page-sessions/run-") {
            (PAGE_WAIT, "a wait loop on a page session".to_owned())
        } else {
            (WAIT, "a wait loop (until/while/sleep)".to_owned())
        };
    }
    if matches!(SCRATCH.is_match(command), Ok(true)) {
        return (super::book::MAPS, "a scratch run.sh sweep".to_owned());
    }
    let Ok(Some(c)) = WORD.captures(command) else {
        return (
            "shell reads and file edits",
            "shell (grep, sed, cat, ls, ...)".to_owned(),
        );
    };
    let w = c[1].to_owned();
    let cat = match w.as_str() {
        "cargo" => "cargo, called directly",
        "l7r-mode-a" => "the hamlet binary (l7r-mode-a)",
        "l7r-gate" | "l7r-gate.sh" => "the gate binary, called directly",
        "python3" | "python" => "python3",
        "git" => "git",
        _ => "fetching and extracting sources",
    };
    (cat, w)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn each_measured_kind_is_named() {
        for (cmd, cat, label) in [
            ("POLL_OK='x'; until grep -q '^ALL DONE' /d/.git/page-sessions/run-1.log; do sleep 30; done", PAGE_WAIT, "a wait loop on a page session"),
            ("until [ -s /tmp/t432/cutfoot.tsv ]; do sleep 5; done; echo done", WAIT, "a wait loop (until/while/sleep)"),
            ("sleep 400", WAIT, "a wait loop (until/while/sleep)"),
            ("cd /c && .git/l7r-handoffs/T432-scratch/run.sh cutpad > /tmp/x.log", super::super::book::MAPS, "a scratch run.sh sweep"),
            ("cd /c && cargo test -p x", "cargo, called directly", "cargo"),
            ("target/release/l7r-mode-a hamlet 3", "the hamlet binary (l7r-mode-a)", "l7r-mode-a"),
            ("scripts/gates/l7r-gate.sh measure x", "the gate binary, called directly", "l7r-gate.sh"),
            ("python3 - <<'EOF'\nprint(1)\nEOF", "python3", "python3"),
            ("git -C /c log -3", "git", "git"),
            ("for i in 1 2; do pdftotext -f $i x.pdf -; done", "fetching and extracting sources", "pdftotext"),
            ("grep -n x y | head", "shell reads and file edits", "shell (grep, sed, cat, ls, ...)"),
            // a target MENTIONED is no run of it (`shared::make::invoked`): prose in a commit message, a pattern in a grep
            ("git -C /c commit -m \"so we make the plan land\"", "git", "git"),
            ("grep -n 'run make rust-test' Makefile", "shell reads and file edits", "shell (grep, sed, cat, ls, ...)"),
        ] {
            assert_eq!(class(cmd), (cat, label.to_owned()), "{cmd}");
        }
    }
}
