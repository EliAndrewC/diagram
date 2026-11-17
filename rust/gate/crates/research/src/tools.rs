//! The record's site and its small tools as commands (feature 449 T148, phase 4's S5, `ask:449-phase4-slices`): `record_asset.py` (`make
//! record`), `glossary_asset.py` (`make glossary`), `footnote_census.py` (`make footnote-census`), `source_tags_contract.py` (`make
//! source-tags-contract`), `pipeline/record_build.py` (render-sync's stamped build) and `scripts/gates/memo_check.py`'s two presets (the
//! Makefile's `CHECK=1` and the push's rows), ported whole. `l7r-gate record <verb>` (the `record` crate) dispatches here, and the push
//! asks [`site::check`] and [`glossary::check`] in process.
//!
//! Each command returns [`Run`]: `Ok` a reply as the Python's `main` returned, `Err` an exception the Python raised past its `main` (a
//! traceback, exit 1), whose words no caller binds (`ask:449-usage-text`) and which [`reply`] prints as one line.

use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;

use crate::Error;

pub mod census;
pub mod contract;
pub mod glossary;
pub mod memo;
pub mod site;

/// A command's outcome: its reply, or the exception the Python's `main` let through.
pub type Run = std::result::Result<Reply, Error>;

#[must_use]
pub fn said(stdout: impl Into<String>, stderr: impl Into<String>, code: i32) -> Reply {
    Reply {
        stdout: stdout.into(),
        stderr: stderr.into(),
        code,
    }
}

/// argparse's own refusal, as `ask:449-usage-text` rules it: exit 2, nothing on stdout, one line naming the verb and the complaint.
#[must_use]
pub fn usage(verb: &str, complaint: &str) -> Reply {
    said(
        "",
        format!("l7r-gate record {verb}: error: {complaint}\n"),
        2,
    )
}

/// A run as the command prints it: an exception the Python did not catch is one line on stderr naming its kind, exit 1, where the
/// traceback was. A `KeyError`'s line keeps the quotes Python's `str()` gives it (T144's plan review: a caller that prints a `KeyError`
/// keeps them), which the library's messages carry where the Python's `KeyError` had a key, and lack where it had a sentence.
#[must_use]
pub fn reply(run: Run) -> Reply {
    run.unwrap_or_else(|e| {
        // a child Python's own traceback, as its process printed it (`memo::RAISED`)
        let text = if e.kind == memo::RAISED {
            e.message.clone()
        } else {
            format!("{}: {}\n", e.kind, py_str(&e))
        };
        said("", text, 1)
    })
}

/// `str(e)` of the exception the Python raised: a `KeyError` prints the `repr` of its argument, which a key's message already is.
#[must_use]
pub fn py_str(e: &Error) -> String {
    let quoted = e.message.len() >= 2
        && ((e.message.starts_with('\'') && e.message.ends_with('\''))
            || (e.message.starts_with('"') && e.message.ends_with('"')));
    if e.kind == "KeyError" && !quoted {
        l7r_guard::shared::py_text::repr(&e.message)
    } else {
        e.message.clone()
    }
}

/// The program that runs, as a key of what it would answer: its path and its file's inode, size and time, which a rebuild writes anew
/// (the push's kept self-tests key the binary the same way, feature 449 T109) - hashing its 27 MB a run would cost more than it saves.
#[must_use]
pub fn program_id() -> String {
    use std::os::unix::fs::MetadataExt as _;
    let exe = std::env::current_exe().unwrap_or_default();
    let meta = std::fs::metadata(&exe)
        .map(|m| format!("{} {} {} {}", m.ino(), m.len(), m.mtime(), m.mtime_nsec()))
        .unwrap_or_default();
    format!("{}\0{meta}", exe.display())
}

/// The repository a command runs in: `git rev-parse --show-toplevel` from `cwd`, or `cwd` outside one - where the Python's modules sat,
/// whose paths (`RESEARCH_DIR`, the glossary's `_HERE`) are the tree's.
#[must_use]
pub fn tree_of(cwd: &Path) -> PathBuf {
    let out = std::process::Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .current_dir(cwd)
        .output();
    out.ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .filter(|t| !t.is_empty())
        .map_or_else(|| cwd.to_path_buf(), PathBuf::from)
}

#[cfg(test)]
mod tests;
