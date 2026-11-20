//! `l7r-mode-a compound <spec.compound.json>`: a generated compound sheet drawn whole (feature 449 T152) - the program read from its spec,
//! composed by the generator, written with its captions declared, the captions placed by the one placer (`crate::caption_place`, T202),
//! the placed sheet written beside the spec as `<map>.svg`, its picture rendered unless `DIAGRAM_SKIP_RENDER=1`, its page written and its
//! census judged - the hand sheet's driver's tail ([`crate::sheet::hand`]). The reply is the hand sheet's: one JSON line with the census, the
//! files read (the spec, the type declaration, the modal files) for the generation cache, and the sheet's rolls and reports; a refusal is
//! `{"error": ...}`, exit 1. `compound-counts <spec>` (the counting build alone) is the generator's counted work on its program, by the
//! derivation's kinds, before any caption is placed - the figure `make budget-sheets PHASE=compound` compares with each sheet's budget.
//! `--out DIR` writes the sheet, its picture and its page into DIR rather than beside the spec, the map's notes still read beside it: the
//! generation cache draws a sheet into its staging folder and publishes the entry from there (feature 449 T221).
//!
//! Research: the compound sheet driver - NONE: the generator's steps in their order, each deciding where it is claimed

use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::Error;
use serde_json::json;

use super::spec::{read, Program};
use crate::raster::Host;
use crate::sheet::hand::{py_list, sheet_registry, Registry};
use crate::types::Band;

/// The command's usage line.
pub const USAGE: &str = "usage: l7r-mode-a compound <map.compound.json> [--out DIR]\n";

/// The spec's suffix; the sheet is written beside it under the map's name.
pub const SUFFIX: &str = ".compound.json";

/// The program and the type's bands its buildings are held to, read from the tree.
///
/// # Errors
/// The spec or the declaration unreadable or refused.
pub fn load(tree: &Path, spec: &str) -> Result<(Program, Vec<(String, Band)>), Error> {
    let src = l7r_gate_core::record::read_text(Path::new(spec))
        .map_err(|e| crate::py::os_error(&e, spec))?;
    crate::reads::note(&std::path::absolute(spec).unwrap_or_default());
    crate::reads::note(&tree.join(crate::types::DECLARATION));
    let program = read(&src)?;
    let bands = crate::types::by_tier("magistracies", tree)?
        .map(|t| {
            t.required
                .into_iter()
                .filter_map(|r| r.kind.map(|k| (k, r.band)))
                .collect()
        })
        .unwrap_or_default();
    Ok((program, bands))
}

/// The rolls a sheet took and what it reported.
pub type Rolled = (Vec<(String, String)>, Vec<String>);

/// The declared sheet's text and the generator's rolls and reports.
///
/// # Errors
/// The program refused.
pub fn compose(program: &Program, bands: &[(String, Band)]) -> Result<(String, Rolled), Error> {
    let (l, s) = super::generate(program, bands)?;
    Ok((super::sheet(program, &l, &s), (s.rolls, s.notes)))
}

/// The sheet drawn: composed, placed, written, rendered unless the switch is set, its page written.
fn draw(
    tree: &Path,
    host: &Host,
    spec: &str,
    out: Option<&Path>,
    registry: &Registry,
) -> Result<(crate::sheet::page::Census, Rolled), Error> {
    let stem = spec.strip_suffix(SUFFIX).ok_or_else(|| {
        Error::new(
            "ValueError",
            format!("a compound spec is named <map>{SUFFIX}, not {spec:?}"),
        )
    })?;
    let (program, bands) = load(tree, spec)?;
    let (text, rolled) = compose(&program, &bands)?;
    let placed = crate::caption_place::placed(&text)?;
    let svg = format!("{stem}.svg");
    let base = stem.rsplit('/').next().unwrap_or(stem);
    let at = |ext: &str| {
        out.map_or_else(
            || std::path::PathBuf::from(format!("{stem}.{ext}")),
            |dir| dir.join(format!("{base}.{ext}")),
        )
    };
    let written = at("svg");
    std::fs::write(&written, &placed)
        .map_err(|e| crate::py::os_error(&e, &written.to_string_lossy()))?;
    if host.var("DIAGRAM_SKIP_RENDER") != Some("1") {
        crate::labels::hand_sheet::render(&placed, &at("png"))?;
    }
    let registry = registry(tree)?;
    let census = crate::sheet::page::write_sheet_page(
        tree,
        host,
        &svg,
        &registry,
        None,
        Some(&placed),
        out,
    )?;
    Ok((census, rolled))
}

/// The command.
#[must_use]
pub fn main(args: &[String], tree: &Path, host: &Host) -> Reply {
    run(args, tree, host, &sheet_registry)
}

/// The command run with `registry` for the sheets' own.
///
/// Research: a sheet with untagged ink or an unknown kind fails - CONVENTION: every drawn element carries a kind the registry knows, else the generator exits 1 naming them (feature 262, FR-006)
pub fn run(args: &[String], tree: &Path, host: &Host, registry: &Registry) -> Reply {
    let (spec, out) = match args {
        [spec] if !spec.starts_with("--") => (spec, None),
        [spec, flag, dir] | [flag, dir, spec] if flag == "--out" && !spec.starts_with("--") => {
            (spec, Some(Path::new(dir)))
        }
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    };
    let _ = crate::reads::take();
    match draw(tree, host, spec, out, registry) {
        Ok((census, (rolls, notes))) => {
            let reads: Vec<String> = crate::reads::take()
                .iter()
                .map(|p| p.to_string_lossy().into_owned())
                .collect();
            let line = json!({
                "counts": census.counts, "unclassed": census.unclassed, "unregistered": census.unregistered, "reads": reads,
                "rolls": rolls, "notes": notes,
            });
            let said: String = notes.iter().flat_map(|n| [n.as_str(), "\n"]).collect();
            if census.unclassed.is_empty() && census.unregistered.is_empty() {
                return reply(format!("{line}\n"), said, 0);
            }
            let base = spec.rsplit('/').next().unwrap_or(spec);
            let said = format!(
                "{said}{base}: untagged ink {}; unknown kinds {}\n",
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

/// The generator's counted work on one program, by key and by the derivation's kinds, before any caption is placed (the counting build).
///
/// # Errors
/// The spec unreadable or the program refused.
#[cfg(feature = "counters")]
pub fn counts(tree: &Path, spec: &str) -> Result<String, Error> {
    use crate::work_counts::{by_kind, ops, reset};
    let (program, bands) = load(tree, spec)?;
    reset();
    let _ = compose(&program, &bands)?;
    let totals = ops();
    let kinds = by_kind(&totals);
    let out = json!({"totals": totals, "by_kind": kinds, "total": kinds.values().sum::<u64>()});
    Ok(format!("{out}\n"))
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}
