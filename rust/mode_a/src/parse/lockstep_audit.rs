//! THE AUDIT'S LOCKSTEP (`ask:449-engine-order` condition 3, feature 449 T174): the Python's grid measures (`grids.py` whole), sized marks
//! (`size_marks.py` whole) on the same sheets (the start tags' Python deleted with the labels package by feature 449 T152; the Rust `crate::hand_sheet::start_tags` the one reader) the parse's lockstep reads, in the same
//! interpreter (`parse/lockstep.rs`), each figure and refusal equal to this port's - so an edit of those Python files that the Rust did
//! not follow fails there. A float is compared as its `repr`, bit for bit; a mask as one string of 0 and 1 a row.
//!
//! The pool's sheets are measured at the default cell (2 px), their coverage and density at 3 px too, where a float floor division is not
//! exact; the fixtures with every other argument and the perimeter band itself (their grids are small: the band's Python cost the pool
//! 0.46 s of the end-to-end test's time and is read anyway by the hugging and vacant measures, observed 2026-11-17, method: each measure
//! timed alone over the six pool sheets, scratchpad `t174/probe_time.py`).
//!
//! Research:
//!     the audit's lockstep - NONE: the Python and the port compared, deciding nothing about a building

use l7r_guard::shared::pyjson::py_float;
use serde_json::{json, Map, Value};

use super::parse_svg;
use crate::grids::{
    coverage, grids, perimeter_band, perimeter_hugging_pct, region_density, top_vacant_rects, Grid,
    RegionTile, VacantRect, CELL, DENSITY_TILES, FTPX, HUG_DEPTH_FT, VACANT_DEPTH_FT,
    VACANT_MIN_SQFT, VACANT_N,
};
use crate::py::uncaught;
use crate::size_marks::{mark_rows, render, untabled_kinds, MarkRow};

/// The Python half: `audit(text, every)` defined for the parse lockstep's script, which calls it for each sheet (`every` for a fixture).
pub const PYTHON: &str = r#"
from l7r.diagram.tools.pack_audit import grids as G, size_marks as M
def ok(fn):
    # `attempt` without `conv`: what `fn` returns is already JSON (a dict `conv` would write as sorted pairs)
    try:
        return {"ok": fn()}
    except Exception as e:
        return {"err": traceback.format_exception_only(type(e), e)[-1].rstrip("\n")}
def rows(grid):
    return ["".join("1" if c else "0" for c in r) for r in grid]
def grid_defaults():
    # each default argument of the measures, which the port holds as constants (`grids.rs`)
    import inspect
    out = {"FTPX": conv(G.FTPX)}
    for fn in (G.coverage, G.perimeter_hugging_pct, G.top_vacant_rects, G.region_density):
        for p in inspect.signature(fn).parameters.values():
            if p.default is not inspect.Parameter.empty:
                out[f"{fn.__name__}.{p.name}"] = conv(p.default)
    return out
def audit(text, every):
    out = {"mark_rows": attempt(lambda: M.mark_rows(text)),
           "untabled": attempt(lambda: M.untabled_kinds(text)), "render": attempt(lambda: M.render(M.mark_rows(text)))}
    try:
        plan = P.parse_svg(text)
    except Exception:
        return out
    def grid(cell):
        g = G._grids(plan, cell)
        out = {"inside": rows(g.inside), "building": rows(g.building), "occ": rows(g.occ), "divider": rows(g.divider), "w": g.w,
               "h": g.h, "minx": conv(g.minx), "miny": conv(g.miny), "cell": g.cell}
        if every:
            out["band"] = rows(G._perimeter_band(g, 7))
        return out
    vacant = lambda vs: [{"rect": conv(v), "orient": v.orient} for v in vs]
    for cell in (2, 3):
        if every or cell == 2:
            out[f"grids{cell}"] = ok(lambda: grid(cell))
        out[f"coverage{cell}"] = attempt(lambda: G.coverage(plan, cell))
        out[f"density{cell}"] = attempt(lambda: G.region_density(plan, cell=cell))
    out["hugging"] = attempt(lambda: G.perimeter_hugging_pct(plan))
    out["vacant"] = ok(lambda: vacant(G.top_vacant_rects(plan)))
    if every:
        out["hugging3"] = attempt(lambda: G.perimeter_hugging_pct(plan, depth_ft=40.0, cell=3))
        out["vacant_more"] = ok(lambda: vacant(G.top_vacant_rects(plan, n=6, cell=3, min_area_sqft=0.0, perimeter_depth_ft=10.0)))
        out["density_2x4"] = attempt(lambda: G.region_density(plan, rows=2, cols=4))
        out["no_cell"] = attempt(lambda: G.coverage(plan, 0))
    return out
"#;

fn f(x: f64) -> Value {
    json!(format!("f:{}", py_float(x)))
}

fn attempt<T>(r: Result<T, l7r_gate_research::Error>, show: impl FnOnce(T) -> Value) -> Value {
    match r {
        Ok(v) => json!({"ok": show(v)}),
        Err(e) => json!({"err": uncaught(&e).trim_end()}),
    }
}

fn rows(grid: &Grid) -> Value {
    json!(grid
        .iter()
        .map(|r| r
            .iter()
            .map(|c| if *c { '1' } else { '0' })
            .collect::<String>())
        .collect::<Vec<_>>())
}

fn mark_row(r: &MarkRow) -> Value {
    json!({"tag": r.tag, "kind": r.kind, "x_px": f(r.x_px), "y_px": f(r.y_px), "w_ft": f(r.w_ft), "h_ft": f(r.h_ft),
           "length_ft": f(r.length_ft), "stroke_ft": f(r.stroke_ft)})
}

fn vacant(vs: &[VacantRect]) -> Value {
    json!(vs
        .iter()
        .map(|v| json!({"rect": {"w_ft": f(v.w_ft), "h_ft": f(v.h_ft), "area_sqft": v.area_sqft, "x": f(v.x), "y": f(v.y),
                                 "zone": v.zone}, "orient": v.orient()}))
        .collect::<Vec<_>>())
}

fn density(ts: &[RegionTile]) -> Value {
    json!(ts
        .iter()
        .map(|t| json!({"row": t.row, "col": t.col, "coverage_pct": f(t.coverage_pct), "interior_sqft": t.interior_sqft}))
        .collect::<Vec<_>>())
}

/// The constants that stand for the Python's default arguments, named as `grid_defaults()` names them.
pub fn defaults() -> Value {
    let cell = json!(CELL);
    json!({
        "FTPX": f(FTPX), "coverage.cell": cell, "perimeter_hugging_pct.depth_ft": f(HUG_DEPTH_FT), "perimeter_hugging_pct.cell": cell,
        "top_vacant_rects.n": VACANT_N, "top_vacant_rects.cell": cell, "top_vacant_rects.min_area_sqft": f(VACANT_MIN_SQFT),
        "top_vacant_rects.perimeter_depth_ft": f(VACANT_DEPTH_FT), "region_density.rows": DENSITY_TILES.0,
        "region_density.cols": DENSITY_TILES.1, "region_density.cell": cell,
    })
}

/// This port's reading of one sheet, as `audit(text, every)` reads it.
pub fn reading(text: &str, every: bool) -> Value {
    let mut out = Map::new();
    out.insert(
        "mark_rows".into(),
        attempt(mark_rows(text), |rs| {
            json!(rs.iter().map(mark_row).collect::<Vec<_>>())
        }),
    );
    out.insert(
        "untabled".into(),
        attempt(untabled_kinds(text), |k| json!(k)),
    );
    out.insert(
        "render".into(),
        attempt(mark_rows(text), |rs| json!(render(&rs))),
    );
    let Ok(plan) = parse_svg(text) else {
        return Value::Object(out);
    };
    for cell in [2, 3] {
        if every || cell == 2 {
            out.insert(
                format!("grids{cell}"),
                attempt(grids(&plan, cell), |g| {
                    let mut v = json!({"inside": rows(&g.inside), "building": rows(&g.building), "occ": rows(&g.occ),
                                       "divider": rows(&g.divider), "w": g.w, "h": g.h, "minx": f(g.minx), "miny": f(g.miny),
                                       "cell": g.cell});
                    if every {
                        v["band"] = rows(&perimeter_band(&g, 7));
                    }
                    v
                }),
            );
        }
        out.insert(format!("coverage{cell}"), attempt(coverage(&plan, cell), f));
        out.insert(
            format!("density{cell}"),
            attempt(
                region_density(&plan, DENSITY_TILES.0, DENSITY_TILES.1, cell),
                |t| density(&t),
            ),
        );
    }
    out.insert(
        "hugging".into(),
        attempt(perimeter_hugging_pct(&plan, HUG_DEPTH_FT, CELL), f),
    );
    out.insert(
        "vacant".into(),
        attempt(
            top_vacant_rects(&plan, VACANT_N, CELL, VACANT_MIN_SQFT, VACANT_DEPTH_FT),
            |v| vacant(&v),
        ),
    );
    if every {
        out.insert(
            "hugging3".into(),
            attempt(perimeter_hugging_pct(&plan, 40.0, 3), f),
        );
        out.insert(
            "vacant_more".into(),
            attempt(top_vacant_rects(&plan, 6, 3, 0.0, 10.0), |v| vacant(&v)),
        );
        out.insert(
            "density_2x4".into(),
            attempt(region_density(&plan, 2, 4, 2), |t| density(&t)),
        );
        out.insert("no_cell".into(), attempt(coverage(&plan, 0), f));
    }
    Value::Object(out)
}
