//! `l7r-gate record glossary [--check] [--split] [--path P]` (`make glossary`; `tools/glossary_asset.py`, features 209, 259 and 301;
//! ported by feature 449 T148): assemble `interactive/assets/glossary.json` from its per-term files and write the variant index beside the
//! record's assets; `--check` writes nothing and exits 1 while either is stale. The site's script `glossary.js` is derived into the site
//! by `make record`; `--path` writes it somewhere on request.
//!
//! THE SOURCE IS ASSEMBLED FIRST, AND THE ASSET IS DERIVED FROM IT (feature 259): the terms are read again after an assembly that changed
//! the JSON, as the Python reloaded `glossary.py`, so a derivation is never of the file as it stood one edit ago.

use std::path::Path;

use l7r_gate_core::record::args::{parse, Spec};

use super::{said, usage, Run};
use crate::glossary::{self as g, source};

/// The command, in the repository `tree`, a `--path` resolved from `cwd`.
///
/// # Errors
/// What the Python let through: the glossary unreadable or not JSON (at its import, before the arguments are read), a term file refused
/// (`GlossaryError`), a file it cannot write.
pub fn run(args: &[String], tree: &Path, cwd: &Path) -> Run {
    // the Python's `GLOSSARY` was built at import, before `main` read a word of its arguments
    let mut terms = g::load(tree)?;
    let parsed = match parse(
        args,
        &[
            Spec::flag("--check"),
            Spec::flag("--split"),
            Spec::value("--path"),
        ],
    ) {
        Ok(p) => p,
        Err(complaint) => return Ok(usage("glossary", &complaint)),
    };
    let base = tree.join(source::HERE);
    if parsed.on("--split") {
        let written = source::write_term_files(&base)?;
        return Ok(said(
            format!(
                "glossary: split into {} term file(s); they assemble back to the same bytes\n",
                written.len()
            ),
            "",
            0,
        ));
    }
    let check = parsed.on("--check");
    let stale = source::check(&base)?;
    if check && !stale.is_empty() {
        return Ok(said(
            "",
            format!(
                "glossary.json: STALE against its per-term files - run `make glossary` ({})\n",
                stale.join(", ")
            ),
            1,
        ));
    }
    if check {
        return Ok(said(
            format!("glossary: in sync ({} terms)\n", terms.len()),
            "",
            0,
        ));
    }
    if source::write_source(&base)? == 1 {
        terms = g::load(tree)?;
    }
    source::write_index(&base)?;
    let path = parsed.text("--path", "");
    if path.is_empty() {
        return Ok(said(
            format!(
                "glossary: assembled ({} terms) - `make record` derives the site's script from it\n",
                terms.len()
            ),
            "",
            0,
        ));
    }
    let at = cwd.join(path);
    std::fs::write(&at, g::record_glossary_js(&terms))
        .map_err(|e| crate::Error::new("OSError", format!("{e}: '{path}'")))?;
    Ok(said(
        format!("wrote {path} ({} terms)\n", terms.len()),
        "",
        0,
    ))
}

/// The push's and `make glossary CHECK=1`'s check, in process: `--check` in the repository `root`.
///
/// # Errors
/// [`run`]'s.
pub fn check(root: &Path) -> Run {
    run(&["--check".to_owned()], root, root)
}

#[cfg(test)]
mod tests;
