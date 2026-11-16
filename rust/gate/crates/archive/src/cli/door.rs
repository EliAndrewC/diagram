//! The one door left of those Python's `archive.py` forwarded through (feature 449 T146; FR-003: ONE writer of the archive's working
//! copy, this crate; `ask:449-T86-door`: a name a command can carry goes by command): `push --home H`, which `archive.Archive.push` runs
//! for S4's `semantic_index.py` while that Python holds the archive's lock itself, so it never takes it - taking it again from another
//! process would wait on the caller forever. T147 (S3b) retired the other eight (`ensure`, `place-gm`, `url-row`, `lane`, `settle`,
//! `sync-gm`, `write-row`, `serve`) with the last Python that called them; this one goes with S4.
//!
//! A raise prints `<Kind>: <message>` on stderr and exits 1; the Python forwarder raises the same kind.

use std::path::Path;

use l7r_gate_core::record::args::{parse, Spec};

use super::{raised, reply};
use crate::store::Archive;
use crate::Reply;

/// `push --home H`: git's complaint on stdout, or nothing.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let p = match parse(args, &[Spec::value("--home")]) {
        Ok(p) => p,
        Err(e) => {
            return reply(
                String::new(),
                format!("l7r-gate record archive push: error: {e}\n"),
                2,
            )
        }
    };
    match Archive::new(Path::new(p.text("--home", ".")), None).push() {
        Ok(text) if text.is_empty() => reply(String::new(), String::new(), 0),
        Ok(text) => reply(format!("{text}\n"), String::new(), 0),
        Err(e) => raised(String::new(), &e),
    }
}

#[cfg(test)]
mod tests;
