//! Three marks a hand sheet draws by a rule the record or the doc settles (feature 449 T175, `pack_audit/marks_drawn.py` whole; feature
//! 335): the landing steps cut into the revetment ([`steps_past_revetment`]), a door set inside the wall it opens through
//! ([`doors_off_their_walls`]), and a torii drawn in plan ([`arches_not_in_plan`]).
//!
//! Research:
//!     the drawn marks - NONE: three marks' geometry read off a sheet, deciding nothing the claims on their rules do not

use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;

use crate::grids::FTPX;
use crate::parse::{ParsedPlan, Rect};
use crate::py::{float, half_sum, min};

static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w:-]+)="([^"]*)""#));
static WORD: LazyLock<Regex> = LazyLock::new(|| py(r"^\w"));

// THE THREE TAG PATTERNS, SCANNED (feature 449 T175): `<rect\b([^>]*)/?>`, `<g\b[^>]*data-id="landing-steps"[^>]*>(.*?)</g>` (`re.S`)
// and its torii twin are read by hand as Python's `re` reads them - a tag's name, Python's word boundary after it, its attributes up
// to the first `>`, a group's body up to the first `</g>`. Compiled, the boundary is a look-around that runs the backtracking engine at
// every offset of the sheet: the three cost the lockstep 0.52 s over the red fixtures (observed 2026-11-17, method: each check timed in
// the test), as T170's `\b` did.

/// Each start tag `<name ...>` from `from`: its offset, its attributes (up to the first `>`, a self-closing `/` among them) and the
/// offset past its `>`; a name a word character continues (`<rectangle`) is no such tag.
fn start_tags<'t>(text: &'t str, name: &str, from: usize) -> Option<(usize, &'t str, usize)> {
    let open = format!("<{name}");
    let mut at = from;
    while let Some(i) = text.get(at..).and_then(|t| t.find(&open)).map(|i| at + i) {
        let after = i + open.len();
        if WORD.is_match(&text[after..]).unwrap_or(false) {
            at = i + 1;
            continue;
        }
        let gt = after + text[after..].find('>')?;
        return Some((i, &text[after..gt], gt + 1));
    }
    None
}

/// Every `<rect>`'s attributes, in order (`_RECT.finditer`).
fn rects(text: &str) -> Vec<&str> {
    let (mut out, mut at) = (Vec::new(), 0);
    while let Some((_, attrs, end)) = start_tags(text, "rect", at) {
        out.push(attrs);
        at = end;
    }
    out
}

/// Each group whose start tag carries `attr`: its offset and its body up to the first `</g>`, from `from`.
fn groups<'t>(text: &'t str, attr: &str, from: usize) -> Option<(usize, &'t str, usize)> {
    let mut at = from;
    while let Some((i, attrs, end)) = start_tags(text, "g", at) {
        if attrs.contains(attr) {
            let close = end + text[end..].find("</g>")?;
            return Some((i, &text[end..close], close + 4));
        }
        at = i + 1;
    }
    None
}

/// A door's edge within this of its building's wall is ON the wall (the stroke's half-width, as `floating_doors` allows).
///
/// Research:
///     door on wall tolerance - NONE: a door's edge within 1.5 px of its building's wall is on the wall, the stroke's half-width.
pub const DOOR_WALL_TOL_PX: f64 = 1.5;

/// A box `(x, y, x2, y2)` px.
type PxBox = (f64, f64, f64, f64);

/// A rect's box from its attributes (the last of a repeated name), each missing one 0; None where a number does not read.
fn rect_box(attrs: &str) -> Option<PxBox> {
    let named = crate::tagged::attrs(&ATTR, attrs);
    let get = |k: &str| float(named.get(k).map_or("0", String::as_str)).ok();
    let (left, top) = (get("x")?, get("y")?);
    let (width, height) = (get("width")?, get("height")?);
    Some((left, top, left + width, top + height))
}

/// The first `<rect>` carrying `data-kind="<kind>"` itself, or the first rect inside a group so tagged.
fn tagged_rect(text: &str, kind: &str) -> Option<PxBox> {
    let tag = format!("data-kind=\"{kind}\"");
    if let Some(attrs) = rects(text).into_iter().find(|a| a.contains(&tag)) {
        return rect_box(attrs);
    }
    let (_, body, _) = groups(text, &tag, 0)?;
    rects(body).first().and_then(|a| rect_box(a))
}

/// A flight of landing steps reaching `past_ft` past the revetment's water-side face, at its center (px).
#[derive(Debug, Clone, PartialEq)]
pub struct StepsPast {
    pub x: f64,
    pub y: f64,
    pub past_ft: f64,
}

/// Research 0176: the steps of a stepped landing are CUT INTO the revetment, so no part of the flight declared
/// `data-id="landing-steps"` may stand past the revetment's water-side face - the side facing the sheet's `river`.
#[must_use]
pub fn steps_past_revetment(text: &str) -> Vec<StepsPast> {
    let m = groups(text, "data-id=\"landing-steps\"", 0);
    let rev = tagged_rect(text, "revetment");
    let river = tagged_rect(text, "river");
    let (Some((_, body, _)), Some(rev), Some(river)) = (m, rev, river) else {
        return Vec::new();
    };
    let Some(steps) = rects(body).first().and_then(|a| rect_box(a)) else {
        return Vec::new();
    };
    let east = half_sum(river.0, river.2) > half_sum(rev.0, rev.2);
    let past = if east {
        steps.2 - rev.2
    } else {
        rev.0 - steps.0
    };
    if past <= 0.0 {
        return Vec::new();
    }
    vec![StepsPast {
        x: half_sum(steps.0, steps.2),
        y: half_sum(steps.1, steps.3),
        past_ft: past / FTPX,
    }]
}

/// A door rect that is not set inside a building flush to its wall: `how` is "outside" or "floating".
#[derive(Debug, Clone, PartialEq)]
pub struct DoorOffWall {
    pub x: f64,
    pub y: f64,
    pub how: &'static str,
}

fn inside(d: &Rect, b: &Rect) -> bool {
    d.x >= b.x - DOOR_WALL_TOL_PX
        && d.y >= b.y - DOOR_WALL_TOL_PX
        && d.x2() <= b.x2() + DOOR_WALL_TOL_PX
        && d.y2() <= b.y2() + DOOR_WALL_TOL_PX
}

fn on_its_wall(d: &Rect, b: &Rect) -> bool {
    min(
        min(
            min((d.x - b.x).abs(), (b.x2() - d.x2()).abs()),
            (d.y - b.y).abs(),
        ),
        (b.y2() - d.y2()).abs(),
    ) <= DOOR_WALL_TOL_PX
}

/// The one door convention (feature 335, research 0117's drawing page, docs/buildings.md): every `data-kind="door"` rect is set WHOLLY
/// INSIDE a building, its outer edge on the wall it opens through. Read by TAG, whatever the fill.
#[must_use]
pub fn doors_off_their_walls(plan: &ParsedPlan) -> Vec<DoorOffWall> {
    let doors: Vec<&Rect> = plan
        .fills
        .iter()
        .filter(|r| plan.label_kinds.get(&r.pos).map(String::as_str) == Some("door"))
        .collect();
    let held: BTreeSet<i64> = doors.iter().map(|d| d.pos).collect();
    let hosts: Vec<&Rect> = plan
        .structures
        .iter()
        .filter(|s| !held.contains(&s.pos))
        .collect();
    let mut out = Vec::new();
    for d in doors {
        let around: Vec<&&Rect> = hosts
            .iter()
            .filter(|b| inside(d, b) && b.area_px() > d.area_px())
            .collect();
        let how = if around.is_empty() {
            "outside"
        } else if !around.iter().any(|b| on_its_wall(d, b)) {
            "floating"
        } else {
            continue;
        };
        out.push(DoorOffWall {
            x: d.x + d.w / 2.0,
            y: d.y + d.h / 2.0,
            how,
        });
    }
    out
}

/// docs/buildings.md "Arch (torii) and approach" (feature 268): a Mode A arch is drawn IN PLAN, its group declaring the invisible
/// `id="arch"` rect the checks read. The 1-based line of every `data-kind="torii"` group that declares none (an elevation silhouette).
#[must_use]
pub fn arches_not_in_plan(text: &str) -> Vec<usize> {
    let (mut out, mut at) = (Vec::new(), 0);
    while let Some((i, body, end)) = groups(text, "data-kind=\"torii\"", at) {
        if !body.contains("id=\"arch\"") {
            out.push(text[..i].matches('\n').count() + 1);
        }
        at = end;
    }
    out
}
