//! The viewBox crop (feature 449 T175, `shared.py`'s `ink_bounds`, `_path_points` and `viewbox_cropped`): the bounding box of everything
//! DRAWN, read off the sheet as `ElementTree` reads it ([`crate::etree`]), and each side's margin of empty parchment.
//!
//! Research:
//!     the sheet's ink - NONE: where a sheet draws, read off its elements, deciding nothing about a building

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::split;

use crate::audit::checks::{max_of, min_of};
use crate::etree::{fromstring, Element};
use crate::parse::ParsedPlan;
use crate::py::{fixed, float, max, min};

/// A drawn sheet keeps at most a 25 px border on each side of its viewBox.
///
/// Research:
///     sheet crop margin - CONVENTION: a drawn sheet keeps at most a 25 px border on each side of the viewBox, the checklist's 15-25 px.
pub const CROP_MAX_MARGIN_PX: f64 = 25.0;
/// Slack on the crop margin.
///
/// Research:
///     crop tolerance - NONE: 5 px of slack on the crop margin, an audit pixel tolerance.
pub const CROP_TOL_PX: f64 = 5.0;
/// A rect covering this much of the viewBox is the background, not ink.
///
/// Research:
///     background rect share - NONE: a rect covering 0.9 of the viewBox is the parchment background, not ink, a parser classification.
pub const PARCHMENT_SHARE: f64 = 0.9;
const SKIP_TAGS: [&str; 6] = ["defs", "pattern", "symbol", "clipPath", "mask", "marker"];

static VIEWBOX: LazyLock<Regex> =
    LazyLock::new(|| py(r#"viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*""#));
static TRANSLATE: LazyLock<Regex> =
    LazyLock::new(|| py(r"translate\(\s*(-?[\d.]+)[\s,]*(-?[\d.]+)?\s*\)"));
static LEADING: LazyLock<Regex> = LazyLock::new(|| py(r"^\s*(-?\d+(?:\.\d+)?)"));

/// A value's leading number, or 0 (`_num`: `re.match(r"\s*(-?\d+(?:\.\d+)?)", value or "")`).
fn num(value: Option<&str>) -> f64 {
    LEADING
        .captures(value.unwrap_or_default())
        .ok()
        .flatten()
        .and_then(|m| float(&m[1]).ok())
        .unwrap_or(0.0)
}

/// Python's truth of a string attribute: present and not empty.
fn truthy(value: Option<&str>) -> Option<&str> {
    value.filter(|v| !v.is_empty())
}

/// Every coordinate a path gives, made absolute ([`crate::tagged::path_walk`]): its ink's extent. FEATURE 449 T182: a relative command's
/// offsets were skipped, so a path drawn in relative steps reached no farther than its last absolute point; they are offsets from the
/// segment's start, read as such.
#[must_use]
pub fn path_points(d: &str) -> (Vec<f64>, Vec<f64>) {
    crate::tagged::path_walk(d)
        .into_iter()
        .flat_map(|(_, pts)| pts)
        .unzip()
}

/// One element's ink and its children's, shifted by the translations above it; a caption's width estimated from its length.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.55 (character width figure)
fn visit(
    el: &Element,
    dx: f64,
    dy: f64,
    canvas_area: f64,
    xs: &mut Vec<f64>,
    ys: &mut Vec<f64>,
) -> Result<(), Error> {
    if SKIP_TAGS.contains(&el.tag.as_str()) {
        return Ok(());
    }
    let (mut dx, mut dy) = (dx, dy);
    if let Some(m) = TRANSLATE
        .captures(el.get("transform").unwrap_or_default())
        .ok()
        .flatten()
    {
        dx += float(&m[1])?;
        dy += m.get(2).map_or(Ok(0.0), |g| float(g.as_str()))?;
    }
    match el.tag.as_str() {
        "rect" => {
            let (w, h) = (num(el.get("width")), num(el.get("height")));
            if !(canvas_area != 0.0 && w * h >= PARCHMENT_SHARE * canvas_area) {
                let (x, y) = (num(el.get("x")) + dx, num(el.get("y")) + dy);
                xs.extend([x, x + w]);
                ys.extend([y, y + h]);
            }
        }
        "line" => {
            // A STROKE IS INK HALF ITS WIDTH EITHER SIDE of the centerline (feature 372 wave 103)
            let hw = num(el.get("stroke-width")) / 2.0;
            let (x1, x2) = (num(el.get("x1")), num(el.get("x2")));
            let (y1, y2) = (num(el.get("y1")), num(el.get("y2")));
            xs.extend([min(x1, x2) + dx - hw, max(x1, x2) + dx + hw]);
            ys.extend([min(y1, y2) + dy - hw, max(y1, y2) + dy + hw]);
        }
        "circle" | "ellipse" => {
            let rx = num(truthy(el.get("r")).or(el.get("rx")));
            let ry = num(truthy(el.get("r")).or(el.get("ry")));
            let (cx, cy) = (num(el.get("cx")) + dx, num(el.get("cy")) + dy);
            xs.extend([cx - rx, cx + rx]);
            ys.extend([cy - ry, cy + ry]);
        }
        "text" => {
            let content = split(&el.itertext).join(" ");
            // a caption DECLARED without `x` stands nowhere until the placer seats it inside the view (feature 286)
            if !content.is_empty() && el.get("x").is_some() {
                let size = num(el.get("font-size"));
                let fs = if size == 0.0 { 10.0 } else { size };
                #[expect(
                    clippy::cast_precision_loss,
                    reason = "a caption's length, far inside f64's integers"
                )]
                let w = 0.55 * fs * content.chars().count() as f64;
                let (x, y) = (num(el.get("x")) + dx, num(el.get("y")) + dy);
                let left = match el.get("text-anchor").unwrap_or("start") {
                    "middle" => x - w / 2.0,
                    "end" => x - w,
                    _ => x,
                };
                xs.extend([left, left + w]);
                ys.extend([y - fs, y]);
            }
        }
        "path" => {
            let (px, py) = path_points(el.get("d").unwrap_or_default());
            let stroked = truthy(el.get("stroke")).unwrap_or("none") != "none";
            let hw = if stroked {
                num(el.get("stroke-width")) / 2.0
            } else {
                0.0
            };
            let edges: &[f64] = if hw == 0.0 { &[0.0] } else { &[-hw, hw] };
            xs.extend(
                px.iter()
                    .flat_map(|v| edges.iter().map(move |e| v + dx + e)),
            );
            ys.extend(
                py.iter()
                    .flat_map(|v| edges.iter().map(move |e| v + dy + e)),
            );
        }
        _ => {}
    }
    for child in &el.children {
        visit(child, dx, dy, canvas_area, xs, ys)?;
    }
    Ok(())
}

/// The bounding box of everything DRAWN: rects, text, lines, circles, ellipses and the absolute points of every path, each shifted by its
/// ancestors' `translate(...)`; definitions skipped, and a rect covering most of the canvas is the parchment. None for a sheet `ElementTree`
/// refuses or that draws nothing.
///
/// Research:
///     the sheet's ink bounds - NONE: the extremes of what [`visit`] reads, deciding nothing about the place
///
/// # Errors
/// A `translate` number `float()` refuses, which the Python did not catch.
pub fn ink_bounds(
    text: &str,
    _plan: &ParsedPlan,
    canvas_area: f64,
) -> Result<Option<(f64, f64, f64, f64)>, Error> {
    let Ok(root) = fromstring(text) else {
        return Ok(None);
    };
    let (mut xs, mut ys) = (Vec::new(), Vec::new());
    visit(&root, 0.0, 0.0, canvas_area, &mut xs, &mut ys)?;
    if xs.is_empty() || ys.is_empty() {
        return Ok(None);
    }
    Ok(Some((
        min_of(xs.iter().copied(), 0.0),
        min_of(ys.iter().copied(), 0.0),
        max_of(xs.iter().copied(), 0.0),
        max_of(ys.iter().copied(), 0.0),
    )))
}

/// The viewBox is cropped to the ink: no side leaves more than the checklist's border of empty parchment.
///
/// Research:
///     the crop's margins - NONE: each side's empty parchment measured against the margin and tolerance whose claims stand on them, deciding nothing more
///
/// # Errors
/// A viewBox or `translate` number `float()` refuses.
pub fn viewbox_cropped(
    text: &str,
    plan: &ParsedPlan,
    max_margin_px: f64,
    tol_px: f64,
) -> Result<Vec<String>, Error> {
    let Some(m) = VIEWBOX.captures(text).ok().flatten() else {
        return Ok(vec!["no viewBox on the sheet".to_owned()]);
    };
    let (vx, vy, vw, vh) = (float(&m[1])?, float(&m[2])?, float(&m[3])?, float(&m[4])?);
    let Some((left, top, right, bottom)) = ink_bounds(text, plan, vw * vh)? else {
        return Ok(vec!["nothing drawn to crop to".to_owned()]);
    };
    let margins = [
        ("left", left - vx),
        ("top", top - vy),
        ("right", (vx + vw) - right),
        ("bottom", (vy + vh) - bottom),
    ];
    Ok(margins
        .iter()
        .filter(|(_, px)| *px > max_margin_px + tol_px)
        .map(|(side, px)| {
            format!(
                "{side} margin is {} px of empty parchment - crop the viewBox to ~{} px",
                fixed(*px, 0),
                fixed(max_margin_px, 0)
            )
        })
        .collect())
}
