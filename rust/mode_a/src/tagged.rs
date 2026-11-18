//! Every drawn element of a Mode A sheet with its KIND, the kinds it is a part of, and its inherited paint (feature 449 T170):
//! `l7r/diagram/tools/pack_audit/tagged.py`'s [`marks`], [`Mark`] and [`path_points`] ported, which the notes census counts privies and
//! wells by and the audit's parse finds a tagged hearth by.
//!
//! A `translate(...)` on an ancestor is applied (a glyph authored in local coordinates is ink where its group puts it); any other
//! transform is not, as the parse applies none.
//!
//! THE PYTHON'S MEMO IS NOT CARRIED: `marks` there is an `lru_cache` of 16 because two readers of one sheet each asked it; here the census
//! reads the marks once and hands them to the parse ([`crate::parse::parse_with`]), so no cache is needed and none decides anything.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `tagged.py` stays for `pack_audit`'s Python checks until step 3; an edit of it makes the
//! same change here in the same commit, and `parse/lockstep.rs` holds the two equal on every pool sheet.
//!
//! Research:
//!     the tagged marks - NONE: a sheet's elements read with their tags and paint, deciding nothing about a building

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::collapse;

use crate::py::float;
use crate::sheet::{parse, Node, DEFS};

static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w:-]+)="([^"]*)""#));
static NUM: LazyLock<Regex> = LazyLock::new(|| py(r"-?\d+(?:\.\d+)?"));
static TRANSLATE: LazyLock<Regex> =
    LazyLock::new(|| py(r"translate\(\s*(-?[\d.]+)[\s,]*(-?[\d.]+)?\s*\)"));
static PATH_CMD: LazyLock<Regex> =
    LazyLock::new(|| py(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)"));
static INNER_TAG: LazyLock<Regex> = LazyLock::new(|| py(r"<[^>]*>"));

/// The presentation attributes a child inherits from its group (SVG's own inheritance).
pub const INHERITED: [&str; 6] = [
    "fill",
    "stroke",
    "stroke-width",
    "font-size",
    "font-weight",
    "font-style",
];
const SKIP: [&str; 6] = [DEFS, "pattern", "symbol", "clipPath", "mask", "marker"];

/// One drawn element: its tag, its kind (its own `data-kind`, else its nearest tagged ancestor's), every kind and `data-part-of` above
/// and on it (outermost first), its paint, its box (px) and, for a path or a line, its points.
#[derive(Debug, Clone, PartialEq)]
pub struct Mark {
    pub tag: String,
    pub kind: Option<String>,
    pub lineage: Vec<String>,
    pub x: f64,
    pub y: f64,
    pub w: f64,
    pub h: f64,
    pub pos: i64,
    pub paint: BTreeMap<String, String>,
    pub pts: Vec<(f64, f64)>,
    pub text: String,
    pub ident: String,
    /// false for a caption DECLARED without `x` - the render pipeline places it (feature 286)
    pub placed: bool,
}

impl Mark {
    /// The inherited fill.
    #[must_use]
    pub fn fill(&self) -> &str {
        self.paint.get("fill").map_or("", String::as_str)
    }

    /// The inherited stroke width's leading number, or 0 (the Python's `stroke_width`, which the size marks read, feature 449 T174).
    ///
    /// # Errors
    /// A number the Python's `float()` refuses (none the pattern takes).
    pub fn stroke_width(&self) -> Result<f64, Error> {
        let text = self.paint.get("stroke-width").map_or("", String::as_str);
        match NUM.find(text).ok().flatten().filter(|m| m.start() == 0) {
            Some(m) => float(m.as_str()),
            None => Ok(0.0),
        }
    }

    /// The mark is `kind` or a part of it - drawn inside its group, or tagged `data-part-of` it.
    #[must_use]
    pub fn belongs_to(&self, kind: &str) -> bool {
        self.kind.as_deref() == Some(kind) || self.lineage.iter().any(|k| k == kind)
    }
}

/// Every `name="value"` of a tag, the last of a repeated name kept (a Python `dict` of `findall`).
pub(crate) fn attrs(re: &Regex, text: &str) -> BTreeMap<String, String> {
    re.captures_iter(text)
        .flatten()
        .map(|c| (c[1].to_owned(), c[2].to_owned()))
        .collect()
}

/// Every match of `re` in `text`, as text.
fn found<'t>(re: &Regex, text: &'t str) -> Vec<&'t str> {
    re.find_iter(text).flatten().map(|m| m.as_str()).collect()
}

/// The ABSOLUTE points a path visits, in order (M, L, H, V, and the end point of every curve or arc); a relative command's offsets are
/// skipped.
///
/// # Errors
/// A number the Python's `float()` refuses (none the pattern takes, but a digit of another script is read as Python reads it).
pub fn path_points(d: &str) -> Result<Vec<(f64, f64)>, Error> {
    let mut out = Vec::new();
    let (mut x, mut y) = (0.0, 0.0);
    for c in PATH_CMD.captures_iter(d).flatten() {
        let nums = found(&NUM, &c[2])
            .into_iter()
            .map(float)
            .collect::<Result<Vec<f64>, Error>>()?;
        match (&c[1], nums.last()) {
            ("H", Some(&n)) => {
                x = n;
                out.push((x, y));
            }
            ("V", Some(&n)) => {
                y = n;
                out.push((x, y));
            }
            ("M" | "L", _) => {
                for pair in nums.chunks_exact(2) {
                    (x, y) = (pair[0], pair[1]);
                    out.push((x, y));
                }
            }
            ("C" | "S" | "Q" | "T" | "A", _) if nums.len() >= 2 => {
                (x, y) = (nums[nums.len() - 2], nums[nums.len() - 1]);
                out.push((x, y));
            }
            _ => {}
        }
    }
    Ok(out)
}

/// `_num`: the attribute's leading number, or 0.
fn num(a: &BTreeMap<String, String>, key: &str) -> Result<f64, Error> {
    let text = a.get(key).map_or("", String::as_str);
    match NUM.find(text).ok().flatten().filter(|m| m.start() == 0) {
        Some(m) => float(m.as_str()),
        None => Ok(0.0),
    }
}

type Boxed = (f64, f64, f64, f64, Vec<(f64, f64)>);

/// (x, y, w, h, points) of one element, or None for an element that draws nothing a check measures.
fn bounds(
    name: &str,
    a: &BTreeMap<String, String>,
    dx: f64,
    dy: f64,
) -> Result<Option<Boxed>, Error> {
    Ok(Some(match name {
        "rect" => (
            num(a, "x")? + dx,
            num(a, "y")? + dy,
            num(a, "width")?,
            num(a, "height")?,
            Vec::new(),
        ),
        "circle" | "ellipse" => {
            let (rx, ry) = if name == "circle" {
                (num(a, "r")?, num(a, "r")?)
            } else {
                (num(a, "rx")?, num(a, "ry")?)
            };
            (
                num(a, "cx")? + dx - rx,
                num(a, "cy")? + dy - ry,
                2.0 * rx,
                2.0 * ry,
                Vec::new(),
            )
        }
        "line" | "path" | "polyline" | "polygon" => {
            let pts = match name {
                "line" => vec![
                    (num(a, "x1")?, num(a, "y1")?),
                    (num(a, "x2")?, num(a, "y2")?),
                ],
                "path" => path_points(a.get("d").map_or("", String::as_str))?,
                _ => {
                    let nums = found(&NUM, a.get("points").map_or("", String::as_str))
                        .into_iter()
                        .map(float)
                        .collect::<Result<Vec<f64>, Error>>()?;
                    nums.chunks_exact(2).map(|p| (p[0], p[1])).collect()
                }
            };
            if pts.is_empty() {
                return Ok(None);
            }
            let pts: Vec<(f64, f64)> = pts.into_iter().map(|(px, py)| (px + dx, py + dy)).collect();
            let (lo_x, hi_x) = spread(pts.iter().map(|p| p.0));
            let (lo_y, hi_y) = spread(pts.iter().map(|p| p.1));
            (lo_x, lo_y, hi_x - lo_x, hi_y - lo_y, pts)
        }
        "text" => (num(a, "x")? + dx, num(a, "y")? + dy, 0.0, 0.0, Vec::new()),
        _ => return Ok(None),
    }))
}

/// Python's `min(xs)` and `max(xs)` of a non-empty run: the first of equals, a later value taking the place only when strictly beyond.
fn spread(values: impl Iterator<Item = f64>) -> (f64, f64) {
    let mut out: Option<(f64, f64)> = None;
    for v in values {
        out = Some(out.map_or((v, v), |(lo, hi)| {
            (if v < lo { v } else { lo }, if v > hi { v } else { hi })
        }));
    }
    out.unwrap_or_default()
}

/// What a child inherits from the walk above it.
struct Above<'k> {
    kind: Option<&'k str>,
    lineage: Vec<String>,
    paint: BTreeMap<String, String>,
    dx: f64,
    dy: f64,
}

fn visit(node: &Node<'_>, above: &Above<'_>, out: &mut Vec<Mark>) -> Result<(), Error> {
    if node.name.is_empty() || SKIP.contains(&node.name) {
        return Ok(());
    }
    let a = attrs(&ATTR, node.open);
    let own = node.kind().or(above.kind);
    let mut lineage = above.lineage.clone();
    lineage.extend(
        [node.part_of(), node.kind()]
            .into_iter()
            .flatten()
            .map(str::to_owned),
    );
    let mut paint = above.paint.clone();
    for k in INHERITED {
        if let Some(v) = a.get(k) {
            paint.insert(k.to_owned(), v.clone());
        }
    }
    let (mut dx, mut dy) = (above.dx, above.dy);
    if let Some(c) = TRANSLATE
        .captures(a.get("transform").map_or("", String::as_str))
        .ok()
        .flatten()
    {
        dx += float(&c[1])?;
        dy += c.get(2).map_or(Ok(0.0), |m| float(m.as_str()))?;
    }
    if let Some((x, y, w, h, pts)) = bounds(node.name, &a, dx, dy)? {
        let text = if node.name == "text" {
            collapse(&INNER_TAG.replace_all(&node.source(), " "))
        } else {
            String::new()
        };
        out.push(Mark {
            tag: node.name.to_owned(),
            kind: own.map(str::to_owned),
            lineage: lineage.clone(),
            x,
            y,
            w,
            h,
            pos: node.start,
            paint: paint.clone(),
            pts,
            text,
            ident: a.get("id").cloned().unwrap_or_default(),
            placed: node.name != "text" || a.contains_key("x"),
        });
    }
    if node.name != "text" {
        let below = Above {
            kind: own,
            lineage,
            paint,
            dx,
            dy,
        };
        for child in &node.children {
            visit(child, &below, out)?;
        }
    }
    Ok(())
}

/// Every drawn element of the sheet in document order (definitions skipped), each with its kind and lineage; a sheet the reader refuses
/// has none (the Python's report tests fed `parse_svg` fragments with no balanced root).
///
/// Research:
///     its marks - NONE: every drawn element read once in document order, an ancestor's translate applied and nothing cached (the Python's memo of 16 not carried); a number an attribute lacks reads 0, deciding nothing about the place
///
/// # Errors
/// A `translate` or a number in it that the Python's `float()` refuses: its `ValueError`, which the Python's `marks` did not catch.
pub fn marks(svg: &str) -> Result<Vec<Mark>, Error> {
    let Ok(root) = parse(svg) else {
        return Ok(Vec::new());
    };
    let mut out = Vec::new();
    let top = Above {
        kind: None,
        lineage: Vec::new(),
        paint: BTreeMap::new(),
        dx: 0.0,
        dy: 0.0,
    };
    for child in &root.children {
        visit(child, &top, &mut out)?;
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
