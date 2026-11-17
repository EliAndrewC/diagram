//! `l7r-gate record site [--check]` (`make record`; `tools/record_asset.py`, features 258, 301, 303), `record site-stale --root <tree>`
//! (render-sync's stamped build; `pipeline/record_build.py`'s `rebuild_if_stale`, feature 301) and `record check record|glossary` (the
//! Makefile's `CHECK=1` and the push's rows: [`super::memo`]), ported by feature 449 T148.
//!
//! `make record` writes the site under `research/site/`; `--check` builds it whole in memory and writes nothing, exiting 1 when the
//! record does not build cleanly, naming each refusal (spec FR-011; feature 303).
//!
//! The checks' kept passes and their usage-log rows are `memo_check.py`'s, in [`super::memo`].

use std::fmt::Write as _;
use std::path::Path;

use l7r_gate_core::record::args::{parse, parse_with, Spec};

use super::{said, usage, Run};
use crate::record::site::{self as site, write};
use crate::record::store;
use crate::Error;

/// `os.path.relpath(path)` from `cwd`: the two absolute (the out directory is joined to the working directory), as `relpath` reads them.
fn relpath(path: &Path, cwd: &Path) -> String {
    crate::record::site_links::relpath(&path.to_string_lossy(), &cwd.to_string_lossy())
}

fn refusal(e: &Error) -> bool {
    e.kind == "RecordError"
}

/// `record_asset.py`: the site built from the record at `--research-dir` (default the tree's `research/`), written to `--out` (default its
/// `site/`), or checked; paths printed from `cwd`.
///
/// # Errors
/// What the Python let through: anything but the record's own refusal, which is printed `record: <refusal>`, exit 1.
pub fn run(args: &[String], tree: &Path, cwd: &Path) -> Run {
    let parsed = match parse(
        args,
        &[
            Spec::flag("--check"),
            Spec::value("--research-dir"),
            Spec::value("--out"),
        ],
    ) {
        Ok(p) => p,
        Err(complaint) => return Ok(usage("site", &complaint)),
    };
    let default = tree.join("research").display().to_string();
    let research = cwd.join(parsed.text("--research-dir", &default));
    let out = match parsed.text("--out", "") {
        "" => research.join(site::SITE),
        o => cwd.join(o),
    };
    let check = parsed.on("--check");
    let mut stdout = String::new();
    let built = (|| -> crate::Result<i32> {
        let inline = store::split_originals(&research, !check)?;
        if check && !inline.is_empty() {
            return Err(Error::new(
                "inline",
                format!(
                    "record: an original is still inline - `make record` moves it:\n  {}\n",
                    inline.join("\n  ")
                ),
            ));
        }
        if !inline.is_empty() {
            let _ = writeln!(stdout, "record: moved the originals of {} notes file(s) into their .originals.html (feature 292)", inline.len());
        }
        let files = site::build(&research, tree)?;
        let pages = files.pages();
        if check {
            let _ = writeln!(stdout, "record: builds cleanly ({pages} page(s))");
            return Ok(0);
        }
        write::write(&files, &out)?;
        let _ = writeln!(
            stdout,
            "record: wrote the site, {pages} page(s), to {}/ - open {}",
            relpath(&out, cwd),
            relpath(&out.join("index.html"), cwd)
        );
        Ok(0)
    })();
    match built {
        Ok(code) => Ok(said(stdout, "", code)),
        Err(e) if e.kind == "inline" => Ok(said(stdout, e.message, 1)),
        Err(e) if refusal(&e) => Ok(said(stdout, format!("record: {}\n", e.message), 1)),
        Err(e) => Err(e),
    }
}

/// The push's and `make record CHECK=1`'s check, in process: `--check` over the repository `root`'s record.
///
/// # Errors
/// [`run`]'s.
pub fn check(root: &Path) -> Run {
    run(&["--check".to_owned()], root, root)
}

/// `record site-stale --root <tree>`: render-sync's build of the tree's site when its stamp differs from its inputs, `code` the
/// building program's bytes; prints `rebuilt` or `fresh`.
///
/// # Errors
/// The build's or the write's, which the Python let through to its caller.
pub fn stale(args: &[String], code: &[u8]) -> Run {
    let parsed = match parse_with(args, &[Spec::value("--root")], 0) {
        Ok(p) if p.has("--root") => p,
        Ok(_) => {
            return Ok(usage(
                "site-stale",
                "the following arguments are required: --root",
            ))
        }
        Err(complaint) => return Ok(usage("site-stale", &complaint)),
    };
    let built = write::rebuild_if_stale(Path::new(parsed.text("--root", ".")), code)?;
    Ok(said(if built { "rebuilt\n" } else { "fresh\n" }, "", 0))
}

#[cfg(test)]
mod tests;
