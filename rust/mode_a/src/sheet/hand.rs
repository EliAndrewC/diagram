//! `l7r-mode-a hand-sheet`: a hand-drawn Mode A sheet drawn whole - its captions placed, its picture rendered and its page written - the
//! one command a hand sheet's generator runs (feature 449 T151, the engine port's step 3a; the country shrine's generator first, the three
//! caption-placing magistracies at step 3b). It does what the generator did in Python: the tracked sheet read, its captions placed by the
//! one placer ([`crate::labels::hand_sheet::placed`], feature 286), the picture rendered from the placed text unless
//! `DIAGRAM_SKIP_RENDER=1` ([`crate::labels::hand_sheet::render`]), the page written from the placed text ([`super::page::write_sheet_page`],
//! feature 277), and the census judged: ink with no kind, or a kind nobody wrote up, fails the sheet (exit 1, its line on stderr).
//!
//! The reply on stdout is one JSON line, as `sheet-page`'s ([`super::page::cli`]): the census and `reads`, every data file the command read,
//! the tracked sheet first among them - the generation cache learns a generator's data files by spying on Python's `open()`, which cannot
//! see this process, so `interactive/sheet.py`'s `draw_hand_sheet` opens each for reading in the generator's own process (feature 449
//! T150's `reads.rs`). A refusal is `{"error": {"kind", "message"}}` with exit 1 and the traceback's last line on stderr.
//! `--placed OUT` also writes the placed text: what the audit is run on to judge the sheet as drawn (T151's checks).
//!
//! Research: the hand sheet driver - NONE: the generator's four steps in its order, each deciding where it is claimed

use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::Error;
use serde_json::json;

use crate::labels::hand_sheet::{placed, render};
use crate::raster::Host;

/// The command's usage line.
pub const USAGE: &str = "usage: l7r-mode-a hand-sheet <map.svg> [--placed OUT]\n";

/// What the command was asked: the sheet's path and where to write the placed text, if anywhere.
fn parse(args: &[String]) -> Option<(&str, Option<&str>)> {
    match args {
        [path] if !path.starts_with("--") => Some((path, None)),
        [path, flag, out] | [flag, out, path] if flag == "--placed" && !path.starts_with("--") => {
            Some((path, Some(out)))
        }
        _ => None,
    }
}

/// The sheet the arguments name, drawn whole; the registry the sheets' own (`compound_classes`, the modal files `compound_kinds` reads).
#[must_use]
pub fn main(args: &[String], tree: &Path, host: &Host) -> Reply {
    run(args, tree, host, &sheet_registry)
}

/// The sheets' registry, every kind's modal file noted as read: the generator imported `COMPOUND_CLASSES`, whose reading of those files
/// the generation cache saw, so an edit of one re-keyed the sheet; with the registry read here, the cache is told of them (feature 449
/// T151: the shrine's recorded files at HEAD measured against the wired tree's, the 99 sheet modals the one gap).
fn sheet_registry(tree: &Path) -> Result<Vec<FeatureClass>, Error> {
    use l7r_gate_registry::about::{compound_classes, modal_rel};
    use l7r_gate_registry::kinds::SHEET_REGISTRY;
    let classes = compound_classes(tree)?;
    for (_, kind) in SHEET_REGISTRY.kinds() {
        crate::reads::note(&tree.join(modal_rel(&SHEET_REGISTRY, kind.key)));
    }
    Ok(classes)
}

/// The registry's reader, handed in: a test's tree holds no modal files.
type Registry = dyn Fn(&Path) -> Result<Vec<FeatureClass>, Error>;

/// `['a', 'b']`: a list of strings as Python's `print` showed the generator's census.
fn py_list(items: &[String]) -> String {
    let shown: Vec<String> = items
        .iter()
        .map(|s| l7r_guard::shared::py_text::repr(s))
        .collect();
    format!("[{}]", shown.join(", "))
}

/// The sheet drawn: placed, rendered unless the switch is set, its page written, and its census returned.
///
/// # Errors
/// The sheet unreadable, the placer's refusals, the render's or the page's.
///
/// Research: the picture skipped under the render switch - CONVENTION: `DIAGRAM_SKIP_RENDER=1` skips the sheet's picture as it skips every map's (feature 208), the page still written
fn draw(
    tree: &Path,
    host: &Host,
    path: &str,
    out: Option<&str>,
    registry: &Registry,
) -> Result<super::page::Census, Error> {
    let svg = l7r_gate_core::record::read_text(Path::new(path))
        .map_err(|e| crate::py::os_error(&e, path))?;
    crate::reads::note(&std::path::absolute(path).unwrap_or_default()); // empty only for an empty path, refused above
    let text = placed(&svg)?;
    if let Some(out) = out {
        std::fs::write(out, &text).map_err(|e| crate::py::os_error(&e, out))?;
    }
    if host.var("DIAGRAM_SKIP_RENDER") != Some("1") {
        let stem: String = path
            .chars()
            .take(path.chars().count().saturating_sub(4))
            .collect();
        render(&text, Path::new(&format!("{stem}.png")))?;
    }
    let registry = registry(tree)?;
    super::page::write_sheet_page(tree, host, path, &registry, None, Some(&text))
}

/// The command run with `registry` for the sheets' own.
///
/// Research: a sheet with untagged ink or an unknown kind fails - CONVENTION: every drawn element carries a kind the registry knows, else the generator exits 1 naming them, as loudly as the pool test (feature 262, FR-006)
fn run(args: &[String], tree: &Path, host: &Host, registry: &Registry) -> Reply {
    let Some((path, out)) = parse(args) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let _ = crate::reads::take(); // this run's reads alone
    match draw(tree, host, path, out, registry) {
        Ok(census) => {
            let reads: Vec<String> = crate::reads::take()
                .iter()
                .map(|p| p.to_string_lossy().into_owned())
                .collect();
            let line = json!({
                "counts": census.counts, "unclassed": census.unclassed, "unregistered": census.unregistered, "reads": reads,
            });
            if census.unclassed.is_empty() && census.unregistered.is_empty() {
                return reply(format!("{line}\n"), String::new(), 0);
            }
            let base = path.rsplit('/').next().unwrap_or(path);
            let said = format!(
                "{base}: untagged ink {}; unknown kinds {}\n",
                py_list(&census.unclassed),
                py_list(&census.unregistered)
            );
            reply(format!("{line}\n"), said, 1)
        }
        Err(e) => {
            let line = json!({"error": {"kind": e.kind, "message": e.message}});
            reply(format!("{line}\n"), crate::py::uncaught(&e), 1)
        }
    }
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

#[cfg(test)]
mod tests;
