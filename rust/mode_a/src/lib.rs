//! The Mode A engine (feature 449 T168, the first piece of the engine port's step 1 under `ask:449-engine-order`): the building types
//! ([`types`], `l7r/diagram/buildings/types.py`) and `make building-programs` ([`programs`], `tools/building_programs.py`, deleted); and
//! (T170, the second piece) `make notes-census` ([`census`], `tools/notes_census.py`, deleted) with what it reads of a sheet - the reader
//! ([`sheet`], `interactive/sheet.py`'s), the tagged marks ([`tagged`], `pack_audit/tagged.py`) and the audit's parse ([`parse`],
//! `pack_audit/parse.py`), the Python of those three kept for its importers under the lockstep rule; and (T174, the third piece) `make
//! size-table` ([`size_table`], `scripts/reviews/size_table.py`, deleted) with what it reads - the sized marks ([`size_marks`],
//! `pack_audit/size_marks.py`), the grid measures whole ([`grids`], `pack_audit/grids.py`), the start tags ([`hand_sheet`],
//! `labels/hand_sheet.py`'s `start_tags`) and an XML reading ([`etree`], `ET.fromstring`'s), the Python of the first three kept likewise.
//!
//! WHY ITS OWN CRATE AND BINARY: the engine will pull `geo` and `resvg` (the plan's steps 2-3), and a gate or guard build that compiled
//! them would put minutes in front of every hook and check edit; so `l7r-mode-a` is built alone by `scripts/gates/l7r-gate.sh mode-a`,
//! as the browser and the embedder are, and nothing of the gate depends on it.
//!
//! Research:
//!     the Mode A engine's command - NONE: dispatch to its tools, deciding nothing about a building

use std::fmt::Write as _;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::Error;

pub mod census;
pub mod etree;
pub mod grids;
pub mod hand_sheet;
pub mod parse;
pub mod programs;
pub mod py;
pub mod sheet;
pub mod size_marks;
pub mod size_table;
pub mod tagged;
pub mod types;

const USAGE: &str = "usage: l7r-mode-a building-programs [--check] [--path PATH] | notes-census <manifest.json> [...] | sheet-counts <svg> | stale-sheet-counts <notes> <svg> | stale-counts <notes> <manifest.json> | size-table <plan> [--json JSON] | --version\n";

/// The command: `building-programs [--check] [--path PATH]`, `notes-census <manifest.json> [...]` (`make notes-census`), the notes
/// census's two checks and a sheet's counts as commands (the differential's doors onto what `tests/test_mode_a_sheets.py` once asked in
/// process, feature 449 T170), `size-table <plan> [--json JSON]` (`make size-table`, T174), or `--version` (the differential's cheap build
/// probe).
#[must_use]
pub fn cli(args: &[String], tree: &Path) -> Reply {
    let rest = args.get(1..).unwrap_or_default();
    match (args.first().map(String::as_str), rest.len()) {
        (Some("building-programs"), _) => programs::main(rest, tree),
        (Some("notes-census"), _) => census::main(rest),
        (Some("size-table"), _) => size_table::cli::main(rest),
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
    }
}
