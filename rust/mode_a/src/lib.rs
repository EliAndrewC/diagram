//! The Mode A engine (feature 449 T168, the first piece of the engine port's step 1 under `ask:449-engine-order`): the building types
//! ([`types`], `l7r/diagram/buildings/types.py`) and `make building-programs` ([`programs`], `tools/building_programs.py`, deleted); and
//! (T170, the second piece) `make notes-census` ([`census`], `tools/notes_census.py`, deleted) with what it reads of a sheet - the reader
//! ([`sheet`], `interactive/sheet.py`'s), the tagged marks ([`tagged`], `pack_audit/tagged.py`) and the audit's parse ([`parse`],
//! `pack_audit/parse.py`), the Python of those three kept for its importers under the lockstep rule; and (T174, the third piece) `make
//! size-table` ([`size_table`], `scripts/reviews/size_table.py`, deleted) with what it reads - the sized marks ([`size_marks`],
//! `pack_audit/size_marks.py`), the grid measures whole ([`grids`], `pack_audit/grids.py`), the start tags ([`hand_sheet`],
//! `labels/hand_sheet.py`'s `start_tags`) and an XML reading ([`etree`], `ET.fromstring`'s), the Python of the first three kept likewise;
//! and (T175, the fourth piece's libraries) the rest of the audit - its checks, registry and report ([`audit`], `pack_audit/`) and what
//! they read of the compound engine ([`compound`]), the Python kept likewise; and (T175, the fourth piece's wiring) `make pack-audit`
//! ([`audit::report::main`], `pack_audit/__main__.py`, deleted); and (T150, step 2's libraries) the page writer the six sheets' pages are
//! written by - [`page`] (`interactive/page.py` and `extents.py`), [`raster`] (`raster.py`, the `resvg` crate in process, the picture's JPEG
//! encoded in process), [`place`], [`notes`], [`tags`], [`dwellings`] and the sheet's page half ([`sheet::page`]); and (T150, step 2's wiring) the six
//! pool generators' pages written by `sheet-page` ([`sheet::page::cli`], their Python deleted), with the reviewer's two picture measures
//! `picture-diff` and `page-lit` ([`diagnostics`], `tools/picture_diff.py` and `page_lit.py`, deleted) and the files the page read
//! listed for the generation cache ([`reads`]); and (T151, step 3a) the hand sheet's reader ([`labels`], `l7r/diagram/labels/`'s; its
//! placer rebuilt from its derivation by T202, [`caption_place`]) and the country shrine drawn whole by `hand-sheet` ([`sheet::hand`]), its generator a call to it.
//!
//! WHY ITS OWN CRATE AND BINARY: the engine pulls `geo` (since T175, the audit's garden sun) and will pull `resvg` (the plan's steps 2-3), and a gate or guard build that compiled
//! them would put minutes in front of every hook and check edit; so `l7r-mode-a` is built alone by `scripts/gates/l7r-gate.sh mode-a`,
//! as the browser and the embedder are, and nothing of the gate depends on it.
//!
//! Research:
//!     the Mode A engine's command - NONE: dispatch to its tools, deciding nothing about a building

use std::fmt::Write as _;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::Error;

pub mod audit;
pub mod caption_place;
pub mod census;
pub mod compound;
pub mod diagnostics;
pub mod dwellings;
pub mod etree;
pub mod grids;
pub mod hand_sheet;
pub mod labels;
pub mod notes;
pub mod page;
pub mod parse;
pub mod place;
#[cfg(test)]
mod pool_sweep;
pub mod programs;
pub mod py;
pub mod raster;
pub mod reads;
pub mod sheet;
pub mod size_marks;
pub mod size_table;
pub mod tagged;
pub mod tags;
pub mod types;
pub mod work_counts;

const USAGE: &str = "usage: l7r-mode-a building-programs [--check] [--path PATH] | notes-census <manifest.json> [...] | sheet-counts <svg> | stale-sheet-counts <notes> <svg> | stale-counts <notes> <manifest.json> | size-table <plan> [--json JSON] | pack-audit <compound.svg> [...] | sheet-page <map.svg> [--with-raster | --no-raster] [--stdin] | hand-sheet <map.svg> [--placed OUT] | compound <map.compound.json> | sheet-render <map.svg> <out.png> | picture-diff a b [--page PAGE] [--svg SVG] [--threshold N] | page-lit <page.html> <key> [--vector] [--out OUT] | --version\n";

/// The command: `building-programs [--check] [--path PATH]`, `notes-census <manifest.json> [...]` (`make notes-census`), the notes
/// census's two checks and a sheet's counts as commands (the differential's doors onto what the retired pytest sweep once asked in
/// process, feature 449 T170), `size-table <plan> [--json JSON]` (`make size-table`, T174), or `--version` (the differential's cheap build
/// probe), or `pack-audit <compound.svg> [...]` (`make pack-audit`, T175: the report of each sheet, its usage line the Python's own words, a
/// usage `ask:449-usage-text` binds).
#[must_use]
pub fn cli(args: &[String], tree: &Path) -> Reply {
    cli_in(args, tree, &mut std::io::empty())
}

/// [`cli`] with the process's standard input, which `sheet-page --stdin` reads (feature 449 T150: a sheet's text with its captions
/// placed, handed by its generator).
#[must_use]
pub fn cli_in(args: &[String], tree: &Path, input: &mut dyn std::io::Read) -> Reply {
    let rest = args.get(1..).unwrap_or_default();
    match (args.first().map(String::as_str), rest.len()) {
        (Some("sheet-page"), _) => {
            sheet::page::cli::main(rest, tree, &raster::Host::current(), input)
        }
        (Some("hand-sheet"), _) => sheet::hand::main(rest, tree, &raster::Host::current()),
        // a hand sheet's picture with its captions placed, to look at (`make sheet-render`; the Python's deleted by feature 449 T152)
        (Some("sheet-render"), 2) => door(|| {
            let text = caption_place::placed(&read(&rest[0])?)?;
            labels::hand_sheet::render(&text, Path::new(&rest[1]))?;
            Ok(String::new())
        }),
        // a generated compound sheet drawn whole from its spec (feature 449 T152)
        (Some("compound"), _) => compound::cli::main(rest, tree, &raster::Host::current()),
        (Some("picture-diff"), _) => {
            diagnostics::picture_diff::main(rest, &raster::Host::current())
        }
        (Some("page-lit"), _) => {
            diagnostics::page_lit::main(rest, &tree.join("scripts/gates/l7r-gate.sh"))
        }
        (Some("building-programs"), _) => programs::main(rest, tree),
        (Some("notes-census"), _) => census::main(rest),
        (Some("size-table"), _) => size_table::cli::main(rest),
        (Some("pack-audit"), _) => audit::report::main(rest, tree),
        (Some("sheet-counts"), 1) => door(|| {
            let counts = census::sheet_counts(&read(&rest[0])?)?;
            Ok(counts.iter().fold(String::new(), |mut out, (k, v)| {
                let _ = writeln!(out, "{k} {v}");
                out
            }))
        }),
        (Some("stale-sheet-counts"), 2) => door(|| {
            let notes = notes(&rest[0])?;
            Ok(lines(&census::stale_sheet_counts(
                &notes,
                &read(&rest[1])?,
            )?))
        }),
        (Some("stale-counts"), 2) => door(|| {
            let manifest = read(&rest[1])?;
            let m = l7r_guard::shared::pyjson::loads(&manifest)
                .map_err(|e| Error::new("json.decoder.JSONDecodeError", e.to_string()))?;
            Ok(lines(&census::stale_counts(&notes(&rest[0])?, &m)?))
        }),
        // the placer's counted work per caption, in the counting build alone (feature 449 T198)
        #[cfg(feature = "counters")]
        (Some("caption-counts"), 1) => {
            door(|| labels::hand_sheet::counted::report(&read(&rest[0])?))
        }
        // the compound generator's counted work on one program, in the counting build alone (feature 449 T152)
        #[cfg(feature = "counters")]
        (Some("compound-counts"), 1) => door(|| compound::cli::counts(tree, &rest[0])),
        (Some("--version"), _) => {
            reply(format!("l7r-mode-a {}\n", env!("CARGO_PKG_VERSION")), "", 0)
        }
        _ => reply(String::new(), USAGE, 2),
    }
}

/// A door's reply: its lines, or the uncaught exception's traceback line and exit 1, as the Python driver it is compared with.
fn door(f: impl FnOnce() -> Result<String, Error>) -> Reply {
    match f() {
        Ok(out) => reply(out, "", 0),
        Err(e) => reply(String::new(), &py::uncaught(&e), 1),
    }
}

/// One line each.
fn lines(found: &[String]) -> String {
    found.iter().fold(String::new(), |mut out, l| {
        let _ = writeln!(out, "{l}");
        out
    })
}

/// `open(path, encoding="utf-8").read()`.
fn read(path: &str) -> Result<String, Error> {
    l7r_gate_core::record::read_text(Path::new(path)).map_err(|e| py::os_error(&e, path))
}

/// A sheet's notes as the sweep read them: the file's text, or nothing where there is no file.
fn notes(path: &str) -> Result<String, Error> {
    if Path::new(path).is_file() {
        read(path)
    } else {
        Ok(String::new())
    }
}

fn reply(stdout: String, stderr: &str, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: stderr.to_owned(),
        code,
    }
}

#[cfg(test)]
mod tests {
    use super::cli;

    #[test]
    fn the_command_names_its_tools() {
        let tree = std::path::Path::new("/nonexistent");
        // (feature 449 T150) the page and the two picture measures: each arm reached, each refusing a bare call as its own usage does
        // (T151) and the hand sheet driver
        for tool in [
            "sheet-page",
            "picture-diff",
            "page-lit",
            "hand-sheet",
            "compound",
        ] {
            let r = cli(&[tool.to_owned()], tree);
            let own = format!("usage: l7r-mode-a {tool} ");
            assert_eq!((r.code, r.stderr.starts_with(&own)), (2, true));
        }
        let r = cli(&["--version".to_owned()], tree);
        assert_eq!((r.code, r.stdout.starts_with("l7r-mode-a ")), (0, true));
        let r = cli(&[], tree);
        assert_eq!(
            (r.code, r.stderr.starts_with("usage: l7r-mode-a")),
            (2, true)
        );
        let r = cli(&["building-programs".to_owned(), "--x".to_owned()], tree);
        assert_eq!(r.code, 2);
    }

    /// `sheet-render`: a hand sheet's picture with its captions placed (feature 449 T152, `make sheet-render`), and its refusal.
    #[test]
    fn a_hand_sheet_renders_with_its_captions_placed() {
        let dir = l7r_guard::shared::tempdir::TempDir::new("mode-a-sheet-render");
        let at = |name: &str| dir.path().join(name).to_string_lossy().into_owned();
        let svg = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20"><rect x="0" y="0" width="40" height="20" fill="#EFE3C2" data-kind="-"/><rect x="5" y="5" width="30" height="10" fill="#DDB87A" data-kind="well" data-id="w"/><text font-size="3" data-kind="well" data-names="w">well</text></svg>"##;
        std::fs::write(at("s.svg"), svg).unwrap();
        let tree = std::path::Path::new("/nonexistent");
        let r = cli(&["sheet-render".to_owned(), at("s.svg"), at("s.png")], tree);
        assert_eq!((r.code, dir.path().join("s.png").exists()), (0, true));
        let r = cli(
            &["sheet-render".to_owned(), at("none.svg"), at("n.png")],
            tree,
        );
        assert_eq!(
            (r.code, r.stderr.starts_with("FileNotFoundError: ")),
            (1, true)
        );
    }

    #[test]
    fn the_doors_answer_as_the_python_drivers_did() {
        let dir = l7r_guard::shared::tempdir::TempDir::new("mode-a-doors");
        let at = |name: &str| dir.path().join(name).to_string_lossy().into_owned();
        let svg = r##"<svg><rect id="precinct" x="0" y="0" width="9" height="9" fill="#fff"/><g fill="#8FB0C6"><circle cx="1" cy="1" r="1"/></g></svg>"##;
        std::fs::write(at("s.svg"), svg).unwrap();
        std::fs::write(at("s.notes.md"), "3 tubs and 2 wells").unwrap();
        std::fs::write(at("m.json"), r#"{"byres": [1]}"#).unwrap();
        std::fs::write(at("bad.json"), "{").unwrap();
        let tree = std::path::Path::new("/nonexistent");
        let run = |words: &[&str]| {
            cli(
                &words.iter().map(|w| (*w).to_owned()).collect::<Vec<_>>(),
                tree,
            )
        };
        assert_eq!(
            run(&["sheet-counts", &at("s.svg")]).stdout,
            "tubs 1\nprivies 0\nwells 0\n"
        );
        assert_eq!(
            run(&["stale-sheet-counts", &at("s.notes.md"), &at("s.svg")]).stdout,
            "'3 tubs' - the sheet draws 1 tubs\n'2 wells' - the sheet draws 0 wells\n"
        );
        assert_eq!(
            run(&["stale-sheet-counts", &at("none.md"), &at("s.svg")]).stdout,
            ""
        );
        assert_eq!(
            run(&["stale-counts", &at("s.notes.md"), &at("m.json")]).stdout,
            "'2 wells' - the map ships 0 wells\n"
        );
        let r = run(&["stale-counts", &at("s.notes.md"), &at("bad.json")]);
        assert_eq!(
            (
                r.code,
                r.stderr.starts_with("json.decoder.JSONDecodeError: ")
            ),
            (1, true)
        );
        let r = run(&["stale-sheet-counts", &at("s.notes.md"), &at("m.json")]);
        assert_eq!(
            (r.code, r.stderr.starts_with("ValueError: no rect marked")),
            (1, true)
        );
        let r = run(&["sheet-counts", &at("none.svg")]);
        assert_eq!(
            (r.code, r.stderr.starts_with("FileNotFoundError: ")),
            (1, true)
        );
        assert_eq!(run(&["sheet-counts"]).code, 2);
        assert_eq!(run(&["notes-census"]).code, 2);
        // the audit's arm (feature 449 T175): its own usage line, not the command's, so a missing arm reads red here
        let r = run(&["pack-audit"]);
        assert_eq!(
            (r.code, r.stderr.as_str()),
            (
                2,
                "usage: python3 -m l7r.diagram.tools.pack_audit <compound.svg> [more.svg ...]\n"
            )
        );
        let r = run(&["pack-audit", &at("none.svg")]);
        assert_eq!(
            (r.code, r.stderr.starts_with("FileNotFoundError: ")),
            (1, true)
        );
    }
}
