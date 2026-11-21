//! Every drawn thing on a Mode A plan, in feet, for `size-audit` (feature 251, FR-006): `scripts/reviews/size_table.py` ported and
//! deleted by feature 449 T174, `make size-table PLAN=<svg>` running [`cli::main`].
//!
//! WHY. `size-audit` checks whether the things drawn on a compound plan are the size such things actually were. Its first step was to
//! parse the SVG and convert every rect, gap and stroke from px to feet - arithmetic a model did turn by turn with the whole sheet in
//! context. This does that step exactly and hands the table over; the agent starts from it, checks it against the sheet, adds what it
//! missed, and keeps the part that is judgment.
//!
//! WHAT IT LISTS.
//! - every `<rect>` outside `<defs>`/`<pattern>`/`<symbol>`/`<clipPath>`/`<mask>`/`<marker>`, with the `translate(...)` of its ancestors
//!   applied; any other transform (a rotation, a scale) is NOT applied and the row says so, because a wrong number stated plainly is
//!   worse than a flagged one;
//! - every distinct stroke width on a line, path, polyline, polygon or rect (a wall's thickness is a stroke);
//! - the GAPS between consecutive collinear axis-aligned `<line>` segments of the same stroke - a gate or a door is drawn as the gap
//!   between two wall segments;
//! - and (feature 294 B15c) the sized marks a rect table misses ([`crate::size_marks`]).
//!
//! Each rect is named by its `data-kind` tag - its own or its nearest tagged ancestor's (feature 262) - never by the nearest caption (a
//! hand sheet's captions are placed by the render pipeline, feature 286). THE PAIRING IS THE SHEET'S TAGS (feature 286, D7): the kind
//! comes from [`crate::sheet::element_kinds`], the one rule the audit's band check reads too, keyed by the start tag that
//! [`crate::hand_sheet::start_tags`] lists at the element's place in the XML tree's document order - an index, as the Python paired them,
//! so a sheet where the tag pattern and the XML parser count elements differently reads as the Python read it.
//!
//! The plan is read as XML ([`crate::etree`], `ET.fromstring`'s reading), the tags by the sheet's tokenizer: two readers, as the Python
//! had, each refusing what it refused.
//!
//! Research:
//!     the size table - NONE: a plan's drawn sizes converted to feet at the audit's scale, deciding nothing about a building

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_shared::pyjson::{ascii_string, py_float};

use crate::etree::{fromstring, Element};
use crate::hand_sheet::start_tags;
use crate::py::{float, fmt_g, max, min, round_int, round_to};
use crate::sheet::element_kinds;

pub mod cli;

/// The Mode A scale (`size-audit.md`, Inputs).
///
/// Research:
///     the size table's scale - NONE: 3 px to 1 ft, the Mode A pixel scale the audit reads
pub const PX_PER_FT: f64 = 3.0;
/// Two wall segments share an axis when their fixed coordinate agrees within this, px.
///
/// Research:
///     the segments' alignment - NONE: two wall lines within 1 px of one axis are read as one wall, a drawing tolerance
pub const ALIGN: f64 = 1.0;
/// The elements whose content is referenced, not drawn.
const SKIP: [&str; 6] = ["defs", "pattern", "symbol", "clipPath", "mask", "marker"];
/// The elements whose stroke width is counted.
const STROKED: [&str; 5] = ["line", "path", "polyline", "polygon", "rect"];

static LEAD: LazyLock<Regex> = LazyLock::new(|| py(r"\s*(-?\d+(?:\.\d+)?)"));
static CALL: LazyLock<Regex> = LazyLock::new(|| py(r"(\w+)\s*\(([^)]*)\)"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| py(r"-?\d+(?:\.\d+)?"));

/// One rect's row.
#[derive(Debug, Clone, PartialEq)]
pub struct RectRow {
    pub x_px: f64,
    pub y_px: f64,
    pub w_ft: f64,
    pub h_ft: f64,
    /// the Python's `round()`, an integer held as the float it equals
    pub area_sqft: f64,
    pub kind: String,
    pub note: &'static str,
}

/// One opening between two collinear wall segments.
#[derive(Debug, Clone, PartialEq)]
pub struct Gap {
    pub axis: &'static str,
    pub at_px: f64,
    pub from_px: f64,
    pub gap_ft: f64,
    pub wall_ft: f64,
}

/// The table: the rects largest first, each stroke width's count by width, the wall gaps.
#[derive(Debug, Clone, PartialEq)]
pub struct Table {
    pub rects: Vec<RectRow>,
    pub strokes_ft: Vec<(f64, usize)>,
    pub gaps: Vec<Gap>,
}

/// An attribute's leading number (`re.match`), or 0.
fn num(value: Option<&str>) -> Result<f64, Error> {
    let text = value.unwrap_or("");
    match LEAD.captures(text).ok().flatten() {
        Some(c) if c.get(0).is_some_and(|m| m.start() == 0) => float(&c[1]),
        _ => Ok(0.0),
    }
}

/// `(dx, dy, whether something other than translate was present)` for one `transform` attribute; every `translate` in it summed, its
/// missing second number 0.
fn shift_of(transform: Option<&str>) -> Result<(f64, f64, bool), Error> {
    let text = transform.unwrap_or("");
    let (mut dx, mut dy, mut other) = (0.0, 0.0, false);
    for c in CALL.captures_iter(text).map_while(Result::ok) {
        if &c[1] == "translate" {
            let mut vals = NUMBER
                .find_iter(&c[2])
                .map_while(Result::ok)
                .map(|m| float(m.as_str()))
                .collect::<Result<Vec<f64>, Error>>()?;
            vals.extend([0.0, 0.0]);
            (dx, dy) = (dx + vals[0], dy + vals[1]);
        } else {
            other = true;
        }
    }
    Ok((dx, dy, other))
}

/// One drawn element as the walk reaches it: its place in the tree's document order, its shift, whether another transform was skipped,
/// and its stroke and width, its own or inherited (SVG inherits both: a wall's thickness is usually set once on its group).
struct Item<'e> {
    el: &'e Element,
    order: usize,
    dx: f64,
    dy: f64,
    other: bool,
    stroke: String,
    width: String,
}

/// Every drawn element, definitions skipped (their elements still counted in the document order the kinds are paired by).
fn walk(root: &Element) -> Result<Vec<Item<'_>>, Error> {
    struct Above<'s> {
        dx: f64,
        dy: f64,
        other: bool,
        stroke: &'s str,
        width: &'s str,
    }
    fn visit<'e>(
        el: &'e Element,
        above: &Above<'_>,
        order: &mut usize,
        out: &mut Vec<Item<'e>>,
    ) -> Result<(), Error> {
        if SKIP.contains(&el.tag.as_str()) {
            *order += el.elements().len();
            return Ok(());
        }
        let (ex, ey, eo) = shift_of(el.get("transform"))?;
        let own = |name: &str, inherited: &str| {
            el.get(name)
                .filter(|v| !v.is_empty())
                .unwrap_or(inherited)
                .to_owned()
        };
        let item = Item {
            el,
            order: *order,
            dx: above.dx + ex,
            dy: above.dy + ey,
            other: above.other || eo,
            stroke: own("stroke", above.stroke),
            width: own("stroke-width", above.width),
        };
        *order += 1;
        let (stroke, width) = (item.stroke.clone(), item.width.clone());
        let below = Above {
            dx: item.dx,
            dy: item.dy,
            other: item.other,
            stroke: &stroke,
            width: &width,
        };
        out.push(item);
        for c in &el.children {
            visit(c, &below, order, out)?;
        }
        Ok(())
    }
    let mut out = Vec::new();
    let top = Above {
        dx: 0.0,
        dy: 0.0,
        other: false,
        stroke: "",
        width: "",
    };
    visit(root, &top, &mut 0, &mut out)?;
    Ok(out)
}

/// Pixels to feet, to a tenth.
#[must_use]
pub fn ft(px: f64) -> f64 {
    round_to(px / PX_PER_FT, 1)
}

/// A stroked line: its ends shifted, its stroke and its width's number.
type Line = (f64, f64, f64, f64, String, f64);

/// The table of `svg_text`.
///
/// # Errors
/// The Python's, in its order: a sheet that is not XML (`ParseError`), one the tokenizer refuses (`ValueError`), a rect's area or a
/// segment's axis that is no number (`OverflowError`, `ValueError`), a rect the start tags do not reach (`IndexError`).
pub fn table(svg_text: &str) -> Result<Table, Error> {
    let root = fromstring(svg_text)?;
    let items = walk(&root)?;
    let kinds = element_kinds(svg_text)?;
    let starts: Vec<usize> = start_tags(svg_text).into_iter().map(|(a, _)| a).collect();
    // FEATURE 449 T182: a rect is paired with its start tag by its index, so the two lists must be one length - an entity that expands to
    // markup draws an element the source writes no tag for, and every later rect would take the wrong tag's kind
    if starts.len() != root.elements().len() {
        return Err(Error::new("ValueError", "the sheet's elements and its start tags disagree - an entity that expands to markup draws an element the source does not write; write the element out"));
    }
    let (mut rects, mut strokes, mut lines) =
        (Vec::new(), Vec::<(f64, usize)>::new(), Vec::<Line>::new());
    for it in &items {
        let kind = it.el.tag.as_str();
        if !it.width.is_empty() && STROKED.contains(&kind) {
            let key = ft(num(Some(&it.width))?);
            // Python's dict: a key equal to one held counts there, a negative zero and a zero one key (the first kept)
            match strokes.iter_mut().find(|(k, _)| order(*k, key).is_eq()) {
                Some((_, n)) => *n += 1,
                None => strokes.push((key, 1)),
            }
        }
        if kind == "rect" {
            let x = num(it.el.get("x"))? + it.dx;
            let y = num(it.el.get("y"))? + it.dy;
            let (w, h) = (num(it.el.get("width"))?, num(it.el.get("height"))?);
            if w <= 0.0 || h <= 0.0 {
                continue;
            }
            let area_sqft = round_int(ft(w) * ft(h))?;
            // every element has its start tag, checked above
            let kind = i64::try_from(starts[it.order])
                .ok()
                .and_then(|s| kinds.get(&s))
                .cloned()
                .unwrap_or_default();
            rects.push(RectRow {
                x_px: round_to(x, 1),
                y_px: round_to(y, 1),
                w_ft: ft(w),
                h_ft: ft(h),
                area_sqft,
                kind,
                note: if it.other {
                    "transform not applied"
                } else {
                    ""
                },
            });
        } else if kind == "line" && !it.other {
            let at = |name: &str| num(it.el.get(name));
            lines.push((
                at("x1")? + it.dx,
                at("y1")? + it.dy,
                at("x2")? + it.dx,
                at("y2")? + it.dy,
                it.stroke.clone(),
                num(Some(&it.width))?,
            ));
        }
    }
    // the Python's `sort(key=lambda r: -r["area_sqft"])`: stable, an area always a whole number
    rects.sort_by(|a, b| order(b.area_sqft, a.area_sqft));
    strokes.sort_by(|a, b| order(a.0, b.0));
    Ok(Table {
        rects,
        strokes_ft: strokes,
        gaps: gaps(&lines)?,
    })
}

/// Python's comparison of two floats in a sort: a negative zero equal to zero (a NaN, which no sorted figure here can be, as equal).
fn order(a: f64, b: f64) -> std::cmp::Ordering {
    a.partial_cmp(&b).unwrap_or(std::cmp::Ordering::Equal)
}

/// A run's key: its axis, its fixed coordinate in `ALIGN`s (Python's `round()`, an integer), its stroke and its width.
type RunKey = (&'static str, f64, String, f64);

/// The openings between consecutive collinear axis-aligned segments of one stroke.
///
/// # Errors
/// A fixed coordinate that is no number: Python's `round()` refusal.
pub fn gaps(lines: &[Line]) -> Result<Vec<Gap>, Error> {
    let mut runs: Vec<(RunKey, Vec<(f64, f64)>)> = Vec::new();
    for (x1, y1, x2, y2, stroke, width) in lines {
        let (key, span) = if (y1 - y2).abs() <= ALIGN && (x1 - x2).abs() > ALIGN {
            (
                ("h", (y1 + y2) / 2.0 / ALIGN),
                (min(*x1, *x2), max(*x1, *x2)),
            )
        } else if (x1 - x2).abs() <= ALIGN && (y1 - y2).abs() > ALIGN {
            (
                ("v", (x1 + x2) / 2.0 / ALIGN),
                (min(*y1, *y2), max(*y1, *y2)),
            )
        } else {
            continue;
        };
        // `+ 0.0`: Python's `round()` gives the integer 0 for -0.4, never a negative zero
        let key: RunKey = (key.0, round_int(key.1)? + 0.0, stroke.clone(), *width);
        match runs.iter_mut().find(|(k, _)| {
            k.0 == key.0 && order(k.1, key.1).is_eq() && k.2 == key.2 && order(k.3, key.3).is_eq()
        }) {
            Some((_, spans)) => spans.push(span),
            None => runs.push((key, vec![span])),
        }
    }
    runs.sort_by(|(a, _), (b, _)| {
        a.0.cmp(b.0)
            .then(order(a.1, b.1))
            .then(a.2.cmp(&b.2))
            .then(order(a.3, b.3))
    });
    let mut out = Vec::new();
    for ((axis, fixed, _, width), mut spans) in runs {
        spans.sort_by(|a, b| order(a.0, b.0).then(order(a.1, b.1)));
        for pair in spans.windows(2) {
            let (end, start) = (pair[0].1, pair[1].0);
            if start - end > ALIGN {
                out.push(Gap {
                    axis,
                    at_px: fixed * ALIGN,
                    from_px: round_to(end, 1),
                    gap_ft: ft(start - end),
                    wall_ft: ft(width),
                });
            }
        }
    }
    Ok(out)
}

/// The table as the size-audit reads it.
#[must_use]
pub fn render(name: &str, data: &Table) -> String {
    let mut lines = vec![
        format!(
            "size-table: {name} - 3 px = 1 ft; {} rects, {} wall gaps",
            data.rects.len(),
            data.gaps.len()
        ),
        format!(
            "{:>7}{:>7}{:>8}  {:<14}{:<44}note",
            "w ft", "h ft", "sq ft", "at px", "kind (data-kind)"
        ),
    ];
    for r in &data.rects {
        let kind: String = r.kind.chars().take(42).collect();
        lines.push(format!(
            "{:>7}{:>7}{:>8}  {:<14}{:<44}{}",
            py_float(r.w_ft),
            py_float(r.h_ft),
            format!("{:.0}", r.area_sqft),
            format!("{},{}", py_float(r.x_px), py_float(r.y_px)),
            if kind.is_empty() { "(untagged)" } else { &kind },
            r.note
        ));
    }
    let gaps: Vec<String> = data
        .gaps
        .iter()
        .map(|g| {
            format!(
                "{} ft {}@{} from {} (wall {} ft)",
                py_float(g.gap_ft),
                g.axis,
                fmt_g(g.at_px),
                fmt_g(g.from_px),
                py_float(g.wall_ft)
            )
        })
        .collect();
    lines.push(format!(
        "wall gaps (openings between collinear segments): {}",
        if gaps.is_empty() {
            "none found - check gates drawn another way".to_owned()
        } else {
            gaps.join("; ")
        }
    ));
    let strokes: Vec<String> = data
        .strokes_ft
        .iter()
        .map(|(k, v)| format!("{} ({v})", py_float(*k)))
        .collect();
    lines.push(format!(
        "stroke widths in ft (count): {}",
        strokes.join(", ")
    ));
    lines.join("\n")
}

/// A float as `json.dumps` writes it: `Infinity`, `-Infinity` and `NaN` for what is no finite number.
fn json_float(v: f64) -> String {
    if v.is_nan() {
        "NaN".to_owned()
    } else if v.is_infinite() {
        if v > 0.0 { "Infinity" } else { "-Infinity" }.to_owned()
    } else {
        py_float(v)
    }
}

/// `json.dumps(data, indent=1) + "\n"`: an area, an integer, written whole however large.
#[must_use]
pub fn to_json(data: &Table) -> String {
    let object = |fields: &[(&str, String)], pad: &str| {
        let inner: Vec<String> = fields
            .iter()
            .map(|(k, v)| format!("{pad} {}: {v}", ascii_string(k, true)))
            .collect();
        format!("{{\n{}\n{pad}}}", inner.join(",\n"))
    };
    let list = |items: Vec<String>| {
        if items.is_empty() {
            "[]".to_owned()
        } else {
            format!("[\n{}\n ]", items.join(",\n"))
        }
    };
    let rects = data
        .rects
        .iter()
        .map(|r| {
            let fields = [
                ("x_px", json_float(r.x_px)),
                ("y_px", json_float(r.y_px)),
                ("w_ft", json_float(r.w_ft)),
                ("h_ft", json_float(r.h_ft)),
                ("area_sqft", format!("{:.0}", r.area_sqft)),
                ("kind", ascii_string(&r.kind, true)),
                ("note", ascii_string(r.note, true)),
            ];
            format!("  {}", object(&fields, "  "))
        })
        .collect();
    let gaps = data
        .gaps
        .iter()
        .map(|g| {
            let fields = [
                ("axis", ascii_string(g.axis, true)),
                ("at_px", json_float(g.at_px)),
                ("from_px", json_float(g.from_px)),
                ("gap_ft", json_float(g.gap_ft)),
                ("wall_ft", json_float(g.wall_ft)),
            ];
            format!("  {}", object(&fields, "  "))
        })
        .collect();
    let strokes = if data.strokes_ft.is_empty() {
        "{}".to_owned()
    } else {
        let fields: Vec<(String, String)> = data
            .strokes_ft
            .iter()
            .map(|(k, v)| (json_float(*k), v.to_string()))
            .collect();
        let borrowed: Vec<(&str, String)> = fields
            .iter()
            .map(|(k, v)| (k.as_str(), v.clone()))
            .collect();
        object(&borrowed, " ")
    };
    let mut out = String::new();
    let _ = write!(
        out,
        "{{\n \"rects\": {},\n \"strokes_ft\": {strokes},\n \"gaps\": {}\n}}\n",
        list(rects),
        list(gaps)
    );
    out
}

#[cfg(test)]
mod tests;
