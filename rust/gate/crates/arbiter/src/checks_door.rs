//! `l7r-gate checks-close`: what `make check-closed` runs (feature 449 T86). Its file kept the name of `l7r-gate checks-door`, the Python
//! callers' door to the check state and the arbiter (`ask:449-T86-door`), which left with its last caller, `review_snapshot.py`, when
//! feature 449 T132 ported it (`ask:449-phase3-remainder` Q2 task B): every verb's Rust stays where the guards call it; the doors' loop
//! left `core` with `owed-door`, the last door (feature 449 T149).

use l7r_shared::checks;
use l7r_shared::checks::handle;

use crate::Reply;

/// `make check-closed SUBJECT= REASON= [AGENT=]`.
#[must_use]
pub fn close_cli(args: &[String]) -> Reply {
    close_in(&std::env::current_dir().unwrap_or_default(), args)
}

/// [`close_cli`] on the tree at `root`, whose check state it reads and writes: a test's is a scratch one, never that of the tree the
/// tests run in (451 T309).
fn close_in(root: &std::path::Path, args: &[String]) -> Reply {
    if !matches!(args.len(), 2 | 3) {
        return Reply {
            stdout: String::new(),
            stderr: "usage: l7r-gate checks-close <subject> <reason> [agent]\n".to_owned(),
            code: 2,
        };
    }
    let (code, stdout, stderr) = handle::close(
        root,
        &args[0],
        &args[1],
        checks::now(),
        args.get(2).map_or("", String::as_str),
    );
    Reply {
        stdout,
        stderr,
        code,
    }
}

#[cfg(test)]
mod tests;
