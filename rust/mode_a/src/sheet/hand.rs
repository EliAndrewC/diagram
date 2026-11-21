//! `l7r-mode-a hand-sheet`: a hand-drawn Mode A sheet drawn whole - its captions placed, its picture rendered and its page written - the
//! one command a hand sheet's generator runs (feature 449 T151, the engine port's step 3a; the country shrine's generator first, the three
//! caption-placing magistracies' since T202, with the placer rebuilt). It does what the generator did in Python: the tracked sheet read, its captions placed by the
//! one placer ([`crate::caption_place::placed`], feature 286; rebuilt from its derivation by feature 449 T202), the picture rendered from the placed text unless
//! `DIAGRAM_SKIP_RENDER=1` ([`crate::labels::hand_sheet::render`]), the page written from the placed text ([`super::page::write_sheet_page`],
//! feature 277), and the census judged: ink with no kind, or a kind nobody wrote up, fails the sheet (exit 1, its line on stderr).
//!
//! The reply on stdout is one JSON line, as `sheet-page`'s ([`super::page::cli`]): the census and `reads`, every data file the command read
//! or looked for (a miss is a read, [`crate::reads`]), the tracked sheet among them - what the pool's generation cache holds the sheet's
//! entry against (`make map`, `rust/gate/crates/pool`'s `cache`, feature 449 T221, which replaced the Python generators that called this).
//! A refusal is `{"error": {"kind", "message"}}` with exit 1 and the traceback's last line on stderr.
//! `--placed OUT` also writes the placed text: what the audit is run on to judge the sheet as drawn (T151's checks). `--out DIR` writes the
//! picture and the page into DIR rather than beside the sheet, the map's notes still read beside it: the generation cache draws a sheet into
//! its staging folder and publishes the entry from there (feature 449 T221).
//!
//! Research: the hand sheet driver - NONE: the generator's four steps in its order, each deciding where it is claimed

use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::Error;
use serde_json::json;

use crate::caption_place::placed;
use crate::labels::hand_sheet::render;
use crate::raster::Host;

/// The command's usage line.
pub const USAGE: &str = "usage: l7r-mode-a hand-sheet <map.svg> [--placed OUT] [--out DIR]\n";

/// What the command was asked: the sheet's path, where to write the placed text, and the folder its picture and page go to, if given.
pub(crate) type Asked<'a> = (&'a str, Option<&'a str>, Option<&'a str>);

/// The arguments read: one sheet, and each of `--placed OUT` and `--out DIR` at most once, in any order.
pub(crate) fn parse(args: &[String]) -> Option<Asked<'_>> {
    let (mut path, mut placed, mut out) = (None, None, None);
    let mut words = args.iter().map(String::as_str);
    while let Some(w) = words.next() {
        let slot = match w {
            "--placed" => &mut placed,
            "--out" => &mut out,
            flag if flag.starts_with("--") => return None,
            _ if path.is_none() => {
                path = Some(w);
                continue;
            }
            _ => return None,
        };
        if slot.is_some() {
            return None;
        }
        *slot = Some(words.next()?);
    }
    Some((path?, placed, out))
}

/// The sheet the arguments name, drawn whole; the registry the sheets' own (`compound_classes`, the modal files `compound_kinds` reads).
#[must_use]
pub fn main(args: &[String], tree: &Path, host: &Host) -> Reply {
    run(args, tree, host, &sheet_registry)
}

/// The sheets' registry, every kind's modal file noted as read: the generator imported `COMPOUND_CLASSES`, whose reading of those files
/// the generation cache saw, so an edit of one re-keyed the sheet; with the registry read here, the cache is told of them (feature 449
/// T151: the shrine's recorded files at HEAD measured against the wired tree's, the 99 sheet modals the one gap).
pub(crate) fn sheet_registry(tree: &Path) -> Result<Vec<FeatureClass>, Error> {
    use l7r_gate_registry::about::{compound_classes, modal_rel};
    use l7r_gate_registry::kinds::SHEET_REGISTRY;
    let classes = compound_classes(tree)?;
    for (_, kind) in SHEET_REGISTRY.kinds() {
        crate::reads::note(&tree.join(modal_rel(&SHEET_REGISTRY, kind.key)));
    }
    Ok(classes)
}

/// The registry's reader, handed in: a test's tree holds no modal files.
pub(crate) type Registry = dyn Fn(&Path) -> Result<Vec<FeatureClass>, Error>;

/// `['a', 'b']`: a list of strings as Python's `print` showed the generator's census.
pub(crate) fn py_list(items: &[String]) -> String {
    let shown: Vec<String> = items.iter().map(|s| l7r_shared::py_text::repr(s)).collect();
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
    (path, placed_out, out): Asked<'_>,
    registry: &Registry,
) -> Result<super::page::Census, Error> {
    let svg = l7r_gate_core::record::read_text(Path::new(path))
        .map_err(|e| crate::py::os_error(&e, path))?;
    crate::reads::note(&std::path::absolute(path).unwrap_or_default()); // empty only for an empty path, refused above
    let text = placed(&svg)?;
    if let Some(at) = placed_out {
        std::fs::write(at, &text).map_err(|e| crate::py::os_error(&e, at))?;
    }
    if host.var("DIAGRAM_SKIP_RENDER") != Some("1") {
        let stem: String = path
            .chars()
            .take(path.chars().count().saturating_sub(4))
            .collect();
        let png = out.map_or_else(
            || std::path::PathBuf::from(format!("{stem}.png")),
            |dir| {
                let base = stem.rsplit('/').next().unwrap_or(&stem);
                Path::new(dir).join(format!("{base}.png"))
            },
        );
        render(&text, &png)?;
    }
    let registry = registry(tree)?;
    super::page::write_sheet_page(
        tree,
        host,
        path,
        &registry,
        None,
        Some(&text),
        out.map(Path::new),
    )
}

/// The command run with `registry` for the sheets' own.
///
/// Research: a sheet with untagged ink or an unknown kind fails - CONVENTION: every drawn element carries a kind the registry knows, else the generator exits 1 naming them, as loudly as the pool test (feature 262, FR-006)
fn run(args: &[String], tree: &Path, host: &Host, registry: &Registry) -> Reply {
    let Some(asked) = parse(args) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let path = asked.0;
    let _ = crate::reads::take(); // this run's reads alone
    match draw(tree, host, asked, registry) {
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
