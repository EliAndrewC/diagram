//! Every unit in scope at a tree (`tools/claims.all_units`, feature 449 T82): every Rust phase's units, then the procedure sections - in
//! the Python's order, which the form problems print in.
//!
//! No `.py` half (feature 449 T158): the engine's Python is deleted, so a `.py` unit is no longer read, and nothing here starts Python.
//! Until T158 the hamlet scope's `.py` units (their core `CPython`'s `ast.dump`) were asked of `scripts/bundle_door.py` and kept under
//! the common git directory (`ask:449-T82-claims`); the runner, the kept answers and their key left with that Python.

use std::path::Path;

use super::units::{all_rust_units, doc_units, Pair, PROCEDURES};
use crate::record::repo::{read_text, Fail};

/// Every unit in scope at `skill` with its module's errors (`all_units`), its paths relative to `skill`; `reads` puts in each Rust unit's core
/// the crate constants it reads ([`all_rust_units`]).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn all_units(skill: &Path, reads: bool) -> Result<Vec<Pair>, Fail> {
    let mut out = all_rust_units(skill, "", reads)?;
    for (doc, tops) in PROCEDURES {
        let p = skill.join(doc);
        if !p.is_file() {
            continue;
        }
        let text = read_text(&p)?;
        out.extend(
            doc_units(&text, doc, tops)
                .into_iter()
                .map(|u| (u, Vec::new())),
        );
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
