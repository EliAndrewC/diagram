//! ONE POOL SHEET THROUGH ITS TIER'S CHECKS (feature 449 T252): `l7r-mode-a sweep <map>...`, the reference step of `make maps`' Mode A
//! row. The pool sweep ([`crate::pool_sweep`], a test) puts every Mode A sheet through every registered check its declared tier owes;
//! this is the same judge on the sheets named, so a session mid-fix proves one sheet in well under a second before the whole crate's
//! tests run (measured 2026-11-22: one sheet's audit 0.09 s, the crate's tests about 25 s fresh). A declared generated exception is
//! composed in process from its `<map>.compound.json` and its captions placed, as `l7r-mode-a compound` writes it, never read from
//! its svg on disk; a hand sheet is read as tracked. Each finding is a line, `<map>: <check>: <finding> - fix: <fix>`.
//!
//! Research:
//!     the one-sheet sweep - NONE: a pool sheet put through the registered checks, deciding nothing about a building

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_gate_research::Error;

use crate::audit::onmap::read_on_map;
use crate::audit::registry::{run_checks, Context};
use crate::audit::report::read_form;
use crate::types::{by_tier, tiers};

/// The command's usage.
pub const USAGE: &str =
    "usage: l7r-mode-a sweep <map>... (a Mode A pool map's folder, a file in it, or its name)\n";

const NO_SVG: &str =
    "no svg and not a declared generated exception - draw it, or declare it generated";

/// One pool sheet as the checks read it: its tier, its svg's path (its notes beside it), its text, and whether it was composed.
#[derive(Debug)]
pub struct Sheet {
    pub tier: String,
    pub svg: PathBuf,
    pub text: String,
    pub generated: bool,
}

/// `m`'s sheet: composed where its tier declares it a generated exception, else its svg read.
///
/// # Errors
/// The spec does not compose, or there is no svg to read.
pub fn sheet(tree: &Path, m: &l7r_gate_pool::Map) -> Result<Sheet, Error> {
    let generated =
        by_tier(&m.tier, tree)?.is_some_and(|t| t.generated_exceptions.contains(&m.name));
    let svg = m.file(".svg");
    let text = if generated {
        compose(tree, &m.file(".compound.json"))?
    } else {
        l7r_gate_core::record::read_text(&svg)
            .map_err(|_| Error::new("FileNotFoundError", format!("{}: {NO_SVG}", m.name)))?
    };
    Ok(Sheet {
        tier: m.tier.clone(),
        svg,
        text,
        generated,
    })
}

/// A generated exception's sheet as `l7r-mode-a compound` writes it: composed from its spec, its captions placed.
///
/// # Errors
/// The spec does not load or compose, or its captions cannot be placed.
pub fn compose(tree: &Path, spec: &Path) -> Result<String, Error> {
    let (program, bands) = crate::compound::cli::load(tree, &spec.to_string_lossy())?;
    let (text, _) = crate::compound::cli::compose(&program, &bands)?;
    crate::caption_place::placed(&text)
}

/// A sheet's context: `text` read as the sheet at `svg` (its notes' form and map declaration beside it) under `tier`, handed to `f`.
///
/// # Errors
/// The sheet does not parse, the tier's type does not read, or `f` fails.
pub fn with_context<T>(
    tree: &Path,
    tier: &str,
    svg: &Path,
    text: &str,
    f: impl FnOnce(&Context) -> Result<T, Error>,
) -> Result<T, Error> {
    let shown = svg.to_string_lossy();
    let plan = crate::parse::parse_svg(text)?;
    let btype = by_tier(tier, tree)?;
    let (form, on_map) = (read_form(&shown)?, read_on_map(&shown)?);
    let ctx = Context::new(
        &plan,
        text,
        btype.as_ref(),
        form.as_deref(),
        on_map.as_ref(),
        tree,
    );
    f(&ctx)
}

/// Every check `tier` owes, run on the sheet: each finding as `<check>: <finding> - fix: <fix>`. Empty is a pass.
///
/// # Errors
/// As [`with_context`], or a check fails to run.
pub fn judge(tree: &Path, tier: &str, svg: &Path, text: &str) -> Result<Vec<String>, Error> {
    with_context(tree, tier, svg, text, |ctx| {
        Ok(run_checks(ctx, Some(tier))?
            .into_iter()
            .flat_map(|(ch, found)| {
                found
                    .into_iter()
                    .map(move |f| format!("{}: {f} - fix: {}", ch.name, ch.fix))
            })
            .collect())
    })
}

/// A map's lines - each finding, or its clean line - and whether it failed.
#[must_use]
pub fn listed(name: &str, found: &[String]) -> (String, bool) {
    if found.is_empty() {
        return (format!("{name}: clean\n"), false);
    }
    let out = found.iter().fold(String::new(), |mut out, f| {
        let _ = writeln!(out, "{name}: {f}");
        out
    });
    (out, true)
}

/// `sweep <map>...`: each map named judged; exit 1 where any finding was made or a sheet could not be read, 2 where a name is no
/// Mode A pool map.
#[must_use]
pub fn main(args: &[String], tree: &Path) -> Reply {
    let said = |stdout: String, stderr: String, code: i32| Reply {
        stdout,
        stderr,
        code,
    };
    if args.is_empty() {
        return said(String::new(), USAGE.to_owned(), 2);
    }
    let w = l7r_gate_pool::walk(tree);
    let declared = tiers(tree).unwrap_or_default();
    let (mut out, mut failed) = (String::new(), false);
    for a in args {
        let m = match l7r_gate_pool::map::resolve(tree, &w, a) {
            Ok(m) if declared.contains(&m.tier) => m,
            Ok(m) => {
                let why = format!("sweep: {} is in {}, not a Mode A tier ({declared:?}) - a hamlet's check is `hamlet --check <spec>`\n", m.name, m.tier);
                return said(out, why, 2);
            }
            Err(why) => {
                return said(
                    out,
                    format!("{}\n", why.replacen("make map", "sweep", 1)),
                    2,
                )
            }
        };
        let judged = sheet(tree, m).and_then(|s| judge(tree, &s.tier, &s.svg, &s.text));
        let found = match judged {
            Ok(found) => found,
            Err(e) => return said(out, crate::py::uncaught(&e), 1),
        };
        let (lines, bad) = listed(&m.name, &found);
        out.push_str(&lines);
        failed |= bad;
    }
    said(out, String::new(), i32::from(failed))
}

#[cfg(test)]
mod tests;
