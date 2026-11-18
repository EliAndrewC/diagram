//! THE LOCKSTEP (`ask:449-engine-order` condition 3, feature 449 T170): the Python's `parse_svg`, `marks` and `element_kinds` on every
//! pool sheet of a Mode A tier and on the fixture sheets (`fixtures.rs`), each field of each record and each refusal equal to this
//! port's, with the constants both read - so an edit of `parse.py`, `tagged.py` or `sheet.py`'s reader that the Rust did not follow fails
//! here. A float is compared as its `repr`, bit for bit. Since T174 the same interpreter runs the audit's grid measures, sized marks and
//! start tags on the same sheets (`lockstep_audit.rs`).
//!
//! Research:
//!     the parse's lockstep - NONE: the Python and the port compared, deciding nothing about a building

use std::path::{Path, PathBuf};

use l7r_guard::shared::pyjson::py_float;
use serde_json::{json, Value};

use super::fixtures::SHEETS;
use super::{
    is_structure, parse_svg, wall_kind, Label, ParsedPlan, Rect, BUILDING_FILLS, BUILDING_PATTERNS,
    CAPS_RATIO, CHAR_W_BOLD, CHAR_W_BOLD_MIXED, CHAR_W_FRAC, COURT_FLOORS, DARK_FILLS,
    DIVIDER_STROKE, DOOR_MAX_AREA_PX, FIRE_WATER_FILL, FURNITURE_MAX_AREA_PX, INTERIOR_FILL,
    MIN_BLDG_AREA_PX, MIN_TREE_R_PX, OPEN_PATTERNS, PRECINCT_ID, ROOF_STROKES, TREE_FILL,
    UTILITY_FILLS, WALL_STROKE, WELL_FILL,
};
use crate::census::PRIVY_FILL;
use crate::py::uncaught;
use crate::sheet::{element_kinds, DEFS};
use crate::tagged::{marks, Mark, INHERITED};

fn real() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// The Python's reading of each sheet named on stdin (a JSON list of paths), every dataclass by its own fields, so a field added there
/// shows here; and the constants this port carries.
const DUMP_HEAD: &str = r#"
import dataclasses, json, os, sys, traceback
sys.path.insert(0, sys.argv[1])
from l7r.diagram.tools.pack_audit import parse as P, program_rules as R, tagged as T
from l7r.diagram.interactive import sheet as S
def conv(v):
    if v is None or isinstance(v, (bool, int, str)):
        return v
    if isinstance(v, float):
        return "f:" + repr(v)
    if dataclasses.is_dataclass(v):
        return {f.name: conv(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if isinstance(v, (set, frozenset)):
        return sorted(conv(x) for x in v)
    if isinstance(v, dict):
        return sorted([conv(k), conv(x)] for k, x in v.items())
    return [conv(x) for x in v]
def attempt(fn):
    try:
        return {"ok": conv(fn())}
    except Exception as e:
        return {"err": traceback.format_exception_only(type(e), e)[-1].rstrip("\n")}
"#;

/// The loop over the sheets and the constants, after the audit's half (`lockstep_audit.rs`, feature 449 T174) is defined.
const DUMP_TAIL: &str = r#"
out = {}
for path in json.load(sys.stdin):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    T.marks.cache_clear()
    out[path] = {"parse": attempt(lambda: P.parse_svg(text)), "marks": attempt(lambda: T.marks(text)),
                 "kinds": attempt(lambda: S.element_kinds(text)),
                 "audit": audit(text, os.path.basename(path).startswith("fixture-"))}
names = ("INTERIOR_FILL BUILDING_FILLS BUILDING_PATTERNS COURT_FLOORS ROOF_STROKES OPEN_PATTERNS MIN_BLDG_AREA_PX PRECINCT_ID "
         "DIVIDER_STROKE FIRE_WATER_FILL TREE_FILL MIN_TREE_R_PX CHAR_W_FRAC CHAR_W_BOLD CHAR_W_BOLD_MIXED CAPS_RATIO WELL_FILL "
         "WALL_STROKE DARK_FILLS FURNITURE_MAX_AREA_PX DOOR_MAX_AREA_PX UTILITY_FILLS STRUCTURE_FILLS WALL_KIND").split()
consts = {n: conv(getattr(P, n)) for n in names}
consts.update(INHERITED=conv(T.INHERITED), SKIP=conv(T._SKIP), DEFS=S.DEFS, PRIVY_FILL=R.PRIVY_FILL, GRIDS=grid_defaults())
print(json.dumps({"sheets": out, "consts": consts}))
"#;

fn f(x: f64) -> Value {
    json!(format!("f:{}", py_float(x)))
}

fn sorted_strings<'a>(items: impl IntoIterator<Item = &'a str>) -> Value {
    let mut v: Vec<&str> = items.into_iter().collect();
    v.sort_unstable();
    json!(v)
}

fn rect(r: &Rect) -> Value {
    json!({"x": f(r.x), "y": f(r.y), "w": f(r.w), "h": f(r.h), "fill": r.fill, "pos": r.pos, "ident": r.ident})
}

fn label(l: &Label) -> Value {
    json!({"x": f(l.x), "y": f(l.y), "w": f(l.w), "h": f(l.h), "text": l.text, "pos": l.pos})
}

fn plan(p: &ParsedPlan) -> Value {
    let rs = |v: &[Rect]| v.iter().map(rect).collect::<Vec<_>>();
    json!({
        "interior": rs(&p.interior), "buildings": rs(&p.buildings), "open_features": rs(&p.open_features), "glyphs": rs(&p.glyphs),
        "dividers": rs(&p.dividers), "tubs": rs(&p.tubs), "labels": p.labels.iter().map(label).collect::<Vec<_>>(),
        "wall_segs": rs(&p.wall_segs), "wells": rs(&p.wells), "door_rects": rs(&p.door_rects), "wall_bands": rs(&p.wall_bands),
        "structures": rs(&p.structures), "fills": rs(&p.fills), "furniture": rs(&p.furniture),
        "ids": sorted_strings(p.ids.iter().map(String::as_str)), "trees": rs(&p.trees), "fence_segs": rs(&p.fence_segs),
        "label_kinds": p.label_kinds.iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>(),
        "kinds": sorted_strings(p.kinds.iter().map(String::as_str)), "gate_posts": rs(&p.gate_posts),
        "roofed_courts": rs(&p.roofed_courts),
    })
}

fn mark(m: &Mark) -> Value {
    json!({
        "tag": m.tag, "kind": m.kind, "lineage": m.lineage, "x": f(m.x), "y": f(m.y), "w": f(m.w), "h": f(m.h), "pos": m.pos,
        "paint": m.paint.iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>(),
        "pts": m.pts.iter().map(|&(x, y)| json!([f(x), f(y)])).collect::<Vec<_>>(), "text": m.text, "ident": m.ident,
        "placed": m.placed,
    })
}

fn attempt<T>(r: Result<T, l7r_gate_research::Error>, show: impl FnOnce(T) -> Value) -> Value {
    match r {
        Ok(v) => json!({"ok": show(v)}),
        Err(e) => json!({"err": uncaught(&e).trim_end()}),
    }
}

fn rust_reading(text: &str, fixture: bool) -> Value {
    json!({
        "parse": attempt(parse_svg(text), |p| plan(&p)),
        "marks": attempt(marks(text), |ms| json!(ms.iter().map(mark).collect::<Vec<_>>())),
        "kinds": attempt(element_kinds(text), |k| json!(k.iter().map(|(p, v)| json!([p, v])).collect::<Vec<_>>())),
        "audit": super::lockstep_audit::reading(text, fixture),
    })
}

fn consts() -> Value {
    let mut structures: Vec<&str> = BUILDING_FILLS
        .iter()
        .chain(&BUILDING_PATTERNS)
        .chain(&UTILITY_FILLS)
        .copied()
        .collect();
    structures.sort_unstable();
    structures.dedup();
    assert!(structures.iter().all(|s| is_structure(s)) && !is_structure("#000"));
    let kinds: Vec<Value> = [WALL_STROKE, DIVIDER_STROKE]
        .iter()
        .map(|s| json!([s, wall_kind(s)]))
        .collect();
    assert_eq!(wall_kind("#000"), None);
    json!({
        "INTERIOR_FILL": INTERIOR_FILL, "BUILDING_FILLS": sorted_strings(BUILDING_FILLS), "BUILDING_PATTERNS": sorted_strings(BUILDING_PATTERNS),
        "COURT_FLOORS": sorted_strings(COURT_FLOORS), "ROOF_STROKES": sorted_strings(ROOF_STROKES), "OPEN_PATTERNS": sorted_strings(OPEN_PATTERNS),
        "MIN_BLDG_AREA_PX": f(MIN_BLDG_AREA_PX), "PRECINCT_ID": PRECINCT_ID, "DIVIDER_STROKE": DIVIDER_STROKE,
        "FIRE_WATER_FILL": FIRE_WATER_FILL, "TREE_FILL": TREE_FILL, "MIN_TREE_R_PX": f(MIN_TREE_R_PX), "CHAR_W_FRAC": f(CHAR_W_FRAC),
        "CHAR_W_BOLD": f(CHAR_W_BOLD), "CHAR_W_BOLD_MIXED": f(CHAR_W_BOLD_MIXED), "CAPS_RATIO": f(CAPS_RATIO), "WELL_FILL": WELL_FILL,
        "WALL_STROKE": WALL_STROKE, "DARK_FILLS": sorted_strings(DARK_FILLS), "FURNITURE_MAX_AREA_PX": f(FURNITURE_MAX_AREA_PX),
        "DOOR_MAX_AREA_PX": f(DOOR_MAX_AREA_PX), "UTILITY_FILLS": sorted_strings(UTILITY_FILLS), "STRUCTURE_FILLS": structures,
        "WALL_KIND": kinds, "INHERITED": INHERITED, "SKIP": ["clipPath", "defs", "marker", "mask", "pattern", "symbol"], "DEFS": DEFS,
        "PRIVY_FILL": PRIVY_FILL, "GRIDS": super::lockstep_audit::defaults(),
    })
}

/// Where two readings first part, by key path, with the two values there, or nothing where they agree (a whole sheet's reading is
/// megabytes, too long to read in a failed assertion, feature 449 T174).
fn first_difference(python: &Value, rust: &Value, at: &str) -> String {
    match (python, rust) {
        (Value::Object(a), Value::Object(b)) => {
            let keys: std::collections::BTreeSet<&String> = a.keys().chain(b.keys()).collect();
            keys.into_iter()
                .find(|k| a.get(*k) != b.get(*k))
                .map_or_else(String::new, |k| {
                    first_difference(
                        a.get(k).unwrap_or(&Value::Null),
                        b.get(k).unwrap_or(&Value::Null),
                        &format!("{at}/{k}"),
                    )
                })
        }
        (Value::Array(a), Value::Array(b)) if a.len() == b.len() => a
            .iter()
            .zip(b)
            .position(|(x, y)| x != y)
            .map_or_else(String::new, |i| {
                first_difference(&a[i], &b[i], &format!("{at}/{i}"))
            }),
        _ => format!("at {at}: python {python} - rust {rust}"),
    }
}

/// Every pool sheet of a declared Mode A tier, on disk (a generated exception's sheet where it has been drawn).
fn pool_sheets() -> Vec<PathBuf> {
    let tree = real();
    let mut out = Vec::new();
    for tier in crate::types::tiers(&tree).unwrap() {
        // a declared tier with no folder yet has no sheet
        for dir in std::fs::read_dir(tree.join("pool").join(&tier))
            .into_iter()
            .flatten()
            .flatten()
        {
            let name = dir.file_name().to_string_lossy().into_owned();
            let svg = dir.path().join(format!("{name}.svg"));
            if svg.is_file() {
                out.push(svg);
            }
        }
    }
    out.sort();
    out
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the Python's parse of the six pool sheets and the fixtures in one interpreter,
/// held equal to this port's, and the sheets' typed counts held to what they draw; its time is in this task's record (`make test-times`).
#[test]
fn the_parse_is_the_python_s_on_every_pool_sheet_and_fixture() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("mode-a-lockstep");
    let mut paths = pool_sheets();
    assert!(paths.len() >= 4);
    // B15b over the same sheets (`census/pool_check.rs`): alone it was a second test over the bar
    crate::census::pool_check::every_pool_sheet_s_notes_type_the_counts_it_draws(&paths);
    for (i, (_, text)) in SHEETS.iter().enumerate() {
        let p = dir.path().join(format!("fixture-{i}.svg"));
        std::fs::write(&p, text).unwrap();
        paths.push(p);
    }
    let names: Vec<String> = paths
        .iter()
        .map(|p| p.to_string_lossy().into_owned())
        .collect();
    let mut child = std::process::Command::new("python3")
        .args([
            "-I",
            "-c",
            &format!("{DUMP_HEAD}{}{DUMP_TAIL}", super::lockstep_audit::PYTHON),
        ])
        .arg(real())
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    std::io::Write::write_all(
        child.stdin.as_mut().unwrap(),
        json!(names).to_string().as_bytes(),
    )
    .unwrap();
    let out = child.wait_with_output().unwrap();
    let failed = String::from_utf8_lossy(&out.stderr);
    assert_eq!((out.status.success(), failed.as_ref()), (true, ""));
    let python: Value = serde_json::from_slice(&out.stdout).unwrap();
    assert_eq!(python["consts"], consts());
    // the fixture with every form on it, and the one with text of more than one byte before its ink, parse on both sides: an error
    // there would compare equal and prove nothing
    for fixture in &names[names.len() - SHEETS.len()..][..2] {
        assert!(python["sheets"][fixture]["parse"]["ok"].is_object());
    }
    // and (T174) the grid measures' fixture and the sized marks' measure on both sides, a refusal there proving nothing either
    for (i, (name, _)) in SHEETS.iter().enumerate() {
        if name.starts_with("measured:") {
            let audit = &python["sheets"][&names[names.len() - SHEETS.len() + i]]["audit"];
            let measured = [&audit["vacant_more"], &audit["mark_rows"]];
            assert_eq!(measured.map(|m| m["ok"].is_array()), [true; 2], "{name}");
        }
    }
    let fixtures = names.len() - SHEETS.len();
    // every pool sheet is measured on both sides, not refused alike
    for name in &names[..fixtures] {
        let audit = &python["sheets"][name]["audit"];
        let measured = [
            audit["grids2"]["ok"].is_object(),
            audit["vacant"]["ok"].is_array(),
        ];
        assert_eq!(measured, [true; 2], "{name}");
    }
    for (i, (name, path)) in names.iter().zip(&paths).enumerate() {
        let text = l7r_gate_core::record::read_text(path).unwrap();
        let rust = rust_reading(&text, i >= fixtures);
        assert_eq!(first_difference(&python["sheets"][name], &rust, name), "");
    }
}

#[test]
fn where_two_readings_part_is_named() {
    let a = json!({"x": [1, {"y": 2}], "z": 1});
    assert_eq!(first_difference(&a, &a.clone(), "s"), "");
    let b = json!({"x": [1, {"y": 3}], "z": 1});
    assert_eq!(
        first_difference(&a, &b, "s"),
        "at s/x/1/y: python 2 - rust 3"
    );
    let c = json!({"x": [1]});
    assert_eq!(
        first_difference(&a, &c, "s"),
        "at s/x: python [1,{\"y\":2}] - rust [1]"
    );
}
