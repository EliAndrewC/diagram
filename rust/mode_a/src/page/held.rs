//! THE PAGE WRITER HELD TO THE PYTHON IT REPLACED (feature 449 T150, the engine port's step 2). Part A held the port to `interactive/page.py`,
//! `raster.py`, `place.py`, `notes.py`, `extents.py`, `tags.py`, `sheet.py`'s page half and `dwellings.py` by running both on the same cases
//! in one lockstep; part B wired the six pool generators to the port and deleted that Python, so its half of the lockstep went with it.
//! What stays:
//!
//! - the cases ([`cases::cases`], part A's, each a function's name and arguments) and the port's half of each ([`call`]);
//! - for every case whose inputs are written in the case itself - the merge, the hit copies, the wrap, the census, the notes, the raster's
//!   documents and tiles, the reader's pieces - the Python's own answer, captured from HEAD's Python before it was deleted
//!   (`python.json`: commit 4596e7032, 2026-11-18; the cases dumped from [`all_cases`] and run through part A's Python half, its
//!   `page_cases`, in a worktree at that commit) and held here exactly, a float by its `repr`;
//! - for every case that reads the live tree (the modal files, the glossary, `place.json`, the pool's and the legacy pool's manifests), its
//!   outcome alone - succeeds, or refuses where it was written to - in the crate's one end-to-end test: a wording edit to a modal must not
//!   turn a test red with no Python left to say what the page should hold. Those cases were last held to the Python's answers byte for
//!   byte by part A's lockstep (2026-11-18: 6 pages, 374 cases, 46 refusals, 13 pictures, none over `picture_diff`'s threshold).
//!
//! Research: the page writer's held cases - NONE: the port's answers compared with the Python's, deciding nothing about a building

use std::path::Path;

use serde_json::Value;

pub mod call;
pub mod cases;
pub mod consts;

/// A JSON value's text field, or empty.
#[must_use]
pub fn text_of(v: &Value) -> String {
    v.as_str().unwrap_or_default().to_owned()
}

/// The cases' world on the real tree: the two vocabularies.
#[must_use]
pub fn world(tree: &Path) -> call::World {
    call::World {
        tree: tree.to_path_buf(),
        hamlet: l7r_gate_registry::about::classes(tree).unwrap(),
        sheet: l7r_gate_registry::about::compound_classes(tree).unwrap(),
    }
}

impl call::World {
    /// Every key of the hamlet vocabulary, or of the sheet's.
    #[must_use]
    pub fn keys(&self, hamlet: bool) -> Vec<String> {
        let reg = if hamlet { &self.hamlet } else { &self.sheet };
        reg.iter().map(|fc| fc.key.clone()).collect()
    }
}

/// The tree this crate's tests read.
#[must_use]
pub fn real() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// Every case, built as part A's lockstep built it.
#[must_use]
pub fn all_cases(w: &call::World) -> Vec<Value> {
    cases::cases(
        &w.keys(true),
        &w.keys(false),
        &crate::parse::fixtures::SHEETS,
    )
}

/// One case's answer in the Python's `tried` shape: `{"ok": value}` or `{"err": the traceback's last line}`.
#[must_use]
pub fn answer(w: &call::World, case: &Value) -> Value {
    match w.call(case) {
        Ok(v) => serde_json::json!({"ok": v}),
        Err(e) => serde_json::json!({"err": crate::py::uncaught(&e).trim_end()}),
    }
}

/// The kinds of case whose inputs are written in the case: their answers are pinned to the Python's (a case that names a file of the
/// tree is not, whatever its kind).
pub const PINNED: [&str; 27] = [
    "merge",
    "hit_copies",
    "wrap",
    "part_of",
    "census",
    "present",
    "notes",
    "section",
    "viewbox",
    "drop_offmap",
    "tile_count",
    "tile_boxes",
    "tile_doc",
    "class_keys",
    "recolor",
    "unpaint",
    "without_text",
    "palette",
    "refuse",
    "data_uri",
    "pieces",
    "title_of",
    "join",
    "hit_regions",
    "hit_layer",
    "keep_clear",
    "lane_default",
];

/// Whether a case's answer is pinned (its inputs all in the case) rather than its outcome alone (it reads the live tree).
#[must_use]
pub fn pinned(case: &Value) -> bool {
    let kind = text_of(&case[0]);
    PINNED.contains(&kind.trim_start_matches('!')) && !case.to_string().contains("\"file\":")
}

/// What the end-to-end test measured of the page writer: the pool pages written, the cases run on the live tree, those refused.
#[derive(Debug, Default)]
pub struct Outcomes {
    pub pages: usize,
    pub cases: usize,
    pub refusals: usize,
}

/// The crate's one end-to-end test's share (feature 449 T150): every case that reads the live tree run on it, each succeeding or refusing
/// as it was written to, and each pool sheet's page written with its picture and id map drawn and its census clean - the Python's own
/// standing demand of a generator's page. On the sheet's own text: its captions are placed by the labels' Python (the engine port's step
/// 3), which a Rust test does not run.
#[must_use]
pub fn outcomes(sheets: &[std::path::PathBuf]) -> Outcomes {
    let w = world(&real());
    let mut m = Outcomes::default();
    for case in all_cases(&w).iter().filter(|c| !pinned(c)) {
        let refuses = text_of(&case[0]).starts_with('!');
        let got = answer(&w, case);
        assert_eq!(got.get("err").is_some(), refuses, "{case}: {got}");
        m.cases += 1;
        m.refusals += usize::from(refuses);
    }
    let pages: Vec<Value> = std::thread::scope(|scope| {
        let w = &w;
        let handles: Vec<_> = sheets
            .iter()
            .map(|path| {
                scope.spawn(move || {
                    let text = std::fs::read_to_string(path).unwrap();
                    call::page_sheet(w, path, &text, false).unwrap()
                })
            })
            .collect();
        handles.into_iter().map(|h| h.join().unwrap()).collect()
    });
    for (path, page) in sheets.iter().zip(&pages) {
        let census = &page["census"]["d"];
        let clean = (
            census[1][1].as_array().map(Vec::len),
            census[2][1].as_array().map(Vec::len),
        );
        assert_eq!(clean, (Some(0), Some(0)), "{}", path.display());
        let html = page["html"].as_str().unwrap_or_default();
        let drawn = (
            html.contains("data:image/jpeg;base64,"),
            html.contains("\"idmap\": \"data:image/png;base64,"),
        );
        assert_eq!(drawn, (true, true), "{}", path.display());
        m.pages += 1;
    }
    m
}

#[cfg(test)]
mod tests;
