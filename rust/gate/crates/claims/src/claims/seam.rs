//! Which open claims findings a Rust stage's landing answers for (`scripts/record/claims_scope.py`'s `split`, ported by feature 449 T82;
//! feature 444 FR-021 as amended 2026-11-01). Its `file_left`, which only `land.py` reached through the claims door and never with its
//! filing asked for, left with `land.py` (feature 449 T121's landing commit).
//!
//! No `.py` half (feature 449 T158): the units a seam imports and a changed Python module's unit spans were read by Python's syntax tree,
//! through the runner (`ask:449-T82-claims`); with the engine's Python deleted there are none, so a finding in a changed Rust file is the
//! landing's own and one in any other changed file is left, as a changed module whose units could not be read always was.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::record::units::re;

static FINDING: LazyLock<Regex> =
    LazyLock::new(|| re(r"\A\s+([A-Z][A-Z-]+)\s+(\S[^:]*?)::(\S+?)#"));
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 1] = [&FINDING];

/// The open findings the landing answers for, and the rest in the files it changes, each a report line.
pub fn split(report: &str, changed: &[String]) -> (Vec<String>, Vec<String>) {
    let (mut own, mut left) = (Vec::new(), Vec::new());
    for ln in super::units::splitlines(report) {
        let Some(m) = FINDING.captures(&ln).ok().flatten() else {
            continue;
        };
        let path = &m[2];
        if !changed.iter().any(|c| c == path) {
            continue;
        }
        let line = l7r_shared::py_text::strip(&ln).to_owned();
        if path.starts_with("rust/") {
            own.push(line);
        } else {
            left.push(line);
        }
    }
    (own, left)
}

#[cfg(test)]
mod tests;
