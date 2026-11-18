//! The program rules feature 294 moved out of the building-review's sweep into the registry (feature 449 T175,
//! `pack_audit/program_rules.py` whole; plan B16-B20): what the review read off every sheet by eye, asked of the sheet's own tags -
//! [`lodging_entrances`] (B16), [`privies_by_zone`] (B17), [`fire_water_distribution`] (B18), [`size_hierarchy`] (B19),
//! [`sheet_furniture`] (B20) and [`veranda_depths`] (feature 374 wave 112).
//!
//! Research:
//!     the program rules - NONE: a sheet's tags read against the rules whose claims stand on each figure, deciding nothing more

use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::checks::{max_of, min_of};
use super::labels::footprint;
use super::Sheet;
use crate::compound::{tub_by_its_eaves, FtBox};
use crate::grids::FTPX;
use crate::parse::{is_structure, ParsedPlan, KURA_FILLS};
use crate::py::{fixed, min};
use crate::tagged::{gap, Mark};

/// The kinds someone sleeps in (docs/building-programs.md, the residence and lodging rows): a composition rule from the
/// building-review sweep, no number in it. A room of the residence reaches the ground by the block's door.
pub const LODGING: [&str; 10] = [
    "residence",
    "family quarters",
    "lord's quarters",
    "guest quarters",
    "servants' quarters",
    "retainers' quarters",
    "barracks",
    "karo's house",
    "hall and dwelling",
    "the monk's rooms",
];
/// The kinds that ARE an entrance: a door glyph, a formal entrance.
pub const ENTRANCE_KINDS: [&str; 2] = ["door", "genkan"];
/// Two blocks within this of each other are one building (a wing, a corridor, a porch): a MAP DRAWING CONVENTION.
///
/// Research:
///     block join distance - NONE: two blocks within 1 px are one building, which is integer-emit rounding.
pub const JOIN_PX: f64 = 1.0;

fn is_entrance(kind: Option<&str>) -> bool {
    kind.is_some_and(|k| ENTRANCE_KINDS.contains(&k))
}

/// Every built footprint the sheet draws (a rect in a structure fill), entrances excluded.
///
/// # Errors
/// The sheet's marks refused.
pub fn structure_marks<'s>(svg: &'s Sheet) -> Result<Vec<&'s Mark>, Error> {
    Ok(svg
        .marks()?
        .iter()
        .filter(|m| {
            m.tag == "rect"
                && is_structure(m.fill())
                && m.w > 0.0
                && m.h > 0.0
                && !is_entrance(m.kind.as_deref())
        })
        .collect())
}

/// A block's root in the union-find, halving the path as it climbs.
fn root(parent: &mut [usize], mut i: usize) -> usize {
    while parent[i] != i {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    i
}

/// The blocks grouped into buildings: blocks within `join_px` of each other, transitively (the Python's union-find, path halving and
/// its root order kept, so the groups come in its order).
#[must_use]
pub fn components<'m>(blocks: &[&'m Mark], join_px: f64) -> Vec<Vec<&'m Mark>> {
    let mut parent: Vec<usize> = (0..blocks.len()).collect();
    for (i, a) in blocks.iter().enumerate() {
        for (j, b) in blocks.iter().enumerate().skip(i + 1) {
            if gap(a, b) <= join_px {
                let rj = root(&mut parent, j);
                let ri = root(&mut parent, i);
                parent[ri] = rj;
            }
        }
    }
    let mut out: Vec<(usize, Vec<&Mark>)> = Vec::new();
    for (i, b) in blocks.iter().enumerate() {
        let r = root(&mut parent, i);
        match out.iter_mut().find(|(k, _)| *k == r) {
            Some((_, group)) => group.push(b),
            None => out.push((r, vec![b])),
        }
    }
    out.into_iter().map(|(_, g)| g).collect()
}

fn inside(d: &Mark, b: &Mark, tol: f64) -> bool {
    d.x >= b.x + tol && d.x2() <= b.x2() - tol && d.y >= b.y + tol && d.y2() <= b.y2() - tol
}

/// Every entrance glyph: a mark tagged door or genkan, and every small dark door rect the parser finds untagged.
///
/// # Errors
/// The sheet's marks refused.
pub fn entrances(svg: &Sheet, plan: &ParsedPlan) -> Result<Vec<Mark>, Error> {
    let mut out: Vec<Mark> = svg
        .marks()?
        .iter()
        .filter(|m| m.tag == "rect" && is_entrance(m.kind.as_deref()))
        .cloned()
        .collect();
    let seen: BTreeSet<i64> = out.iter().map(|m| m.pos).collect();
    for r in &plan.door_rects {
        if !seen.contains(&r.pos) {
            out.push(Mark {
                tag: "rect".into(),
                kind: None,
                lineage: Vec::new(),
                x: r.x,
                y: r.y,
                w: r.w,
                h: r.h,
                pos: r.pos,
                paint: [("fill".to_owned(), r.fill.clone())].into_iter().collect(),
                pts: Vec::new(),
                text: String::new(),
                ident: String::new(),
                placed: true,
            });
        }
    }
    Ok(out)
}

/// Every building holding a lodging kind has at least one entrance on its OUTER wall: an entrance glyph within `tol` of one of its
/// blocks and not wholly inside any of them (the registry passes `DOOR_FLUSH_TOL_PX`, the floating-door check's flush reach).
///
/// Research:
///     a lodging entered from the ground - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html, research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html, research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html: each barracks dwelling has its earth-floored entry and a servants' quarters is entered by its door or by a door to each dwelling (0097); the residence is entered by its genkan where it stands alone and the household by its own kitchen door (0104); the retainers' long-house, where the karo lodges, gives each dwelling a door of its own on the court (0106).
///     every other lodging entered from the ground - UNRESEARCHED: the guest quarters, a shrine's hall and dwelling and the monk's rooms each reach the ground by a door or genkan on their own outer wall, not only through a building they do not join; no page asks how these were entered.
///
/// # Errors
/// The sheet's marks refused.
pub fn lodging_entrances(svg: &Sheet, plan: &ParsedPlan, tol: f64) -> Result<Vec<String>, Error> {
    let doors = entrances(svg, plan)?;
    let mut out = Vec::new();
    for comp in components(&structure_marks(svg)?, JOIN_PX) {
        let kinds: BTreeSet<&str> = comp
            .iter()
            .flat_map(|b| {
                std::iter::once(b.kind.as_deref().unwrap_or_default())
                    .chain(b.lineage.iter().map(String::as_str))
            })
            .filter(|k| LODGING.contains(k))
            .collect();
        if kinds.is_empty() {
            continue;
        }
        if doors.iter().any(|d| {
            comp.iter().any(|b| gap(d, b) <= tol) && !comp.iter().any(|b| inside(d, b, tol))
        }) {
            continue;
        }
        let x = min_of(comp.iter().map(|b| b.x), 0.0);
        let y = min_of(comp.iter().map(|b| b.y), 0.0);
        out.push(format!(
            "the {} block at svg({},{}) has no door or genkan on its outer wall - a lodging is entered from the ground",
            kinds.into_iter().collect::<Vec<_>>().join(" / "),
            fixed(x, 0),
            fixed(y, 0)
        ));
    }
    Ok(out)
}

/// The palette's latrine / utility fill (SKILL.md, Palette).
///
/// Research:
///     a privy drawn gray - CONVENTION: a privy is known on the sheet by the palette's gray, #7E726A, the map drawing convention research/questions/0101-privies-setchin.drawing.html records; no source gives a privy's color.
pub const PRIVY_FILL: &str = "#7E726A";
/// The court kinds a zone is drawn as.
pub const COURT_KINDS: [&str; 2] = ["inner court", "outer court"];
/// A privy within this of a residence block is attached to the house (0.5 ft: flush, with integer-emit rounding).
pub const ATTACHED_PX: f64 = 0.5 * FTPX;
/// At least this many privies on a county manor: the low end of docs/building-programs.md's "one per functional zone, about three or
/// four" (research 0101), which the record calls the project's guess.
///
/// Research:
///     least privies on a county manor - GUESS research/questions/0101-privies-setchin.drawing.html: at least 3 privies, the low end of the project's three or four per compound; the page records the count as the project's guess.
pub const PRIVY_MIN: usize = 3;

/// (a) a privy is the residence's own - tagged a part of it, or attached to one of its blocks (research 0101); (b) every court the sheet
/// tags has a privy, a ZONE being a court kind however many precinct rects draw it; (c) at least `minimum` in all.
///
/// Research:
///     the residence's own privy - research/questions/0101-privies-setchin.drawing.html: a samurai residence's privies are built into the house, so a privy is tagged a part of the residence or attached to one of its blocks.
///     a privy in each court zone - GUESS research/questions/0101-privies-setchin.drawing.html: each inner and outer court zone the sheet tags holds a privy, the page's about one privy to each part of the compound, which it records as the project's guess; a court zone is the part of the compound its rects draw, buildings and all, not the open courtyard the page keeps every privy out of.
///
/// # Errors
/// The sheet's marks refused.
pub fn privies_by_zone(svg: &Sheet, minimum: usize) -> Result<Vec<String>, Error> {
    let ms = svg.marks()?;
    let privies: Vec<&Mark> = ms
        .iter()
        .filter(|m| m.tag == "rect" && m.belongs_to("latrine") && m.fill() == PRIVY_FILL)
        .collect();
    let house: Vec<&Mark> = structure_marks(svg)?
        .into_iter()
        .filter(|m| m.belongs_to("residence") && !m.belongs_to("latrine"))
        .collect();
    let mut out = Vec::new();
    if !house.is_empty()
        && !privies.iter().any(|p| {
            p.lineage.iter().any(|k| k == "residence")
                || house.iter().any(|b| gap(p, b) <= ATTACHED_PX)
        })
    {
        out.push("no privy is the residence's own - the family's privy is built into the house (tag it data-part-of=\"residence\" and attach it to a block)".to_owned());
    }
    for kind in COURT_KINDS {
        let ground: Vec<&Mark> = ms
            .iter()
            .filter(|m| m.ident == "precinct" && m.kind.as_deref() == Some(kind))
            .collect();
        if let Some(first) = ground.first() {
            let held = ground.iter().any(|c| {
                privies.iter().any(|p| {
                    let (px, py) = (p.x + p.w / 2.0, p.y + p.h / 2.0);
                    c.x <= px && px <= c.x2() && c.y <= py && py <= c.y2()
                })
            });
            if !held {
                out.push(format!(
                    "the {kind} at svg({},{}) has no privy - one stands in each functional zone",
                    fixed(first.x, 0),
                    fixed(first.y, 0)
                ));
            }
        }
    }
    if privies.len() < minimum {
        out.push(format!(
            "{} privies on the sheet - a county manor has at least {minimum} (one per functional zone, about three or four)",
            privies.len()
        ));
    }
    Ok(out)
}

/// The fire-prone wooden buildings a tub must stand by - DECIDED AND RECORDED in `program_rules.py` (feature 294, the scout's note on
/// B18): the buildings docs/building-programs.md names for the tubs and the generator seats one at; guest quarters, the karo's house and
/// the retainers' quarters are NOT on it, the record naming them nowhere for a tub (GUESS).
///
/// Research:
///     which wooden buildings carry a tub - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the office hall, the residence, the barracks, the gatehouse, the compound shrine, the stables, the servants' row, the kitchen and a shrine's hall and dwelling are the major wooden buildings that each carry a tub, and the guest quarters, the karo's house and the retainers' quarters are not; the page puts a tub at each major wooden building and records that no page ranks the buildings for fire water, the ranking the project's reasoning.
pub const TUB_KINDS: [&str; 9] = [
    "office hall",
    "residence",
    "barracks",
    "gatehouse",
    "compound shrine",
    "stables",
    "servants' quarters",
    "kitchen",
    "hall and dwelling",
];
/// The kitchen's tubs: "weighted to the kitchen (2)".
///
/// Research:
///     kitchen tub count - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: the kitchen gets two fire-water tubs, one at each major wooden building and two at the kitchen, whose fire burns all day.
pub const KITCHEN_TUBS: usize = 2;

fn mark_ft_box(m: &Mark) -> FtBox {
    (m.x / FTPX, m.y / FTPX, m.x2() / FTPX, m.y2() / FTPX)
}

/// A tub by the eaves of every listed wooden building the sheet draws (the engine's [`tub_by_its_eaves`]), two at the kitchen, and no
/// tub served by a plaster kura alone (docs/building-programs.md: "none at the plaster kura").
///
/// Research:
///     a tub at each wooden building - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: one fire-water tub at each major wooden building, two at the kitchen, and none at an earth-walled storehouse (dozo), built not to burn, so a tub served by a plaster kura alone is refused.
///
/// # Errors
/// The sheet's marks refused.
pub fn fire_water_distribution(svg: &Sheet, plan: &ParsedPlan) -> Result<Vec<String>, Error> {
    let blocks = structure_marks(svg)?;
    let wooden: Vec<&Mark> = blocks
        .iter()
        .copied()
        .filter(|b| !KURA_FILLS.contains(&b.fill()))
        .collect();
    let kura: Vec<&Mark> = blocks
        .iter()
        .copied()
        .filter(|b| KURA_FILLS.contains(&b.fill()))
        .collect();
    let centers: Vec<(f64, f64)> = plan
        .tubs
        .iter()
        .map(|t| ((t.x + t.w / 2.0) / FTPX, (t.y + t.h / 2.0) / FTPX))
        .collect();
    let mut out = Vec::new();
    for kind in TUB_KINDS {
        let own: Vec<&Mark> = wooden
            .iter()
            .copied()
            .filter(|b| {
                b.kind.as_deref() == Some(kind)
                    || (b.lineage.iter().any(|k| k == kind)
                        && !b.kind.as_deref().is_some_and(|k| TUB_KINDS.contains(&k)))
            })
            .collect();
        let Some(first) = own.first() else {
            continue;
        };
        let n = centers
            .iter()
            .filter(|c| own.iter().any(|b| tub_by_its_eaves(**c, mark_ft_box(b))))
            .count();
        let want = if kind == "kitchen" { KITCHEN_TUBS } else { 1 };
        if n < want {
            out.push(format!(
                "the {kind} at svg({},{}) has {n} fire-water tub(s) by its eaves - it needs {want}",
                fixed(first.x, 0),
                fixed(first.y, 0)
            ));
        }
    }
    for c in &centers {
        if kura.iter().any(|k| tub_by_its_eaves(*c, mark_ft_box(k)))
            && !wooden.iter().any(|b| tub_by_its_eaves(*c, mark_ft_box(b)))
        {
            out.push(format!(
                "a fire-water tub at svg({},{}) stands by a plaster kura alone - a kura carries no tub",
                fixed(c.0 * FTPX, 0),
                fixed(c.1 * FTPX, 0)
            ));
        }
    }
    Ok(out)
}

/// (smaller, larger): the compound's size HIERARCHY, the building-review checklist's pairs - the house out-measures its kitchen, its
/// document storehouse and storehouse, and its shrine (docs/building-programs.md's own reading; the tax archive pair READ from 0116, the
/// rest GUESS); the stables and the cell under the barracks (GUESS); the sanctuary under the hall (docs/building-programs.md).
///
/// Research:
///     the storehouses under the residence - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the tax archive and the other small storehouses stand well below the staff rowhouse, which stands below the residence, the order of the one office measured, at Takayama.
///     the kitchen and the shrine under the residence - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: no kitchen or shrine hall out-sizes the residence, the largest domestic building; the page records the order among them as the project's reading, a guess.
///     the stables under the barracks - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the stable stays smaller than the barracks; the page records its place in the order as a guess.
///     the cell under the barracks - GUESS: a cell stays smaller than the barracks; no page ranks them, and the pages' sizes agree, a cell of about 12 by 10 ft, a guess on research/questions/0096-holding-cells-agariya-and-roya.drawing.html, against a long rowhouse 12 to 24 ft deep on research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html.
///     the sanctuary under the hall and dwelling - research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html: a sanctuary one to three bays of about 6 ft wide stays smaller than the one-roof hall and dwelling of 2,100 to 3,600 sq ft.
pub const HIERARCHY: [(&str, &str); 7] = [
    ("kitchen", "residence"),
    ("tax archive", "residence"),
    ("storehouse", "residence"),
    ("compound shrine", "residence"),
    ("stables", "barracks"),
    ("cell", "barracks"),
    ("sanctuary", "hall and dwelling"),
];

/// Each pair's footprints ([`footprint`], the largest structure tagged with the kind) rank as the list says; a pair is skipped where the
/// sheet draws either kind as no structure.
#[must_use]
pub fn size_hierarchy(plan: &ParsedPlan, pairs: &[(&str, &str)]) -> Vec<String> {
    let mut out = Vec::new();
    for &(small, big) in pairs {
        let (Some(a), Some(b)) = (footprint(plan, small), footprint(plan, big)) else {
            continue;
        };
        let (sa, sb) = (a.area_px() / (FTPX * FTPX), b.area_px() / (FTPX * FTPX));
        if sa >= sb {
            out.push(format!(
                "the {small} ({} sq ft) is not smaller than the {big} ({} sq ft) - the compound ranks its buildings",
                fixed(sa, 0),
                fixed(sb, 0)
            ));
        }
    }
    out
}

static COMPASS_TEXT: LazyLock<Regex> = LazyLock::new(|| py(r"(?i)^\s*(?:N|North)\s*$"));
static KEY_TEXT: LazyLock<Regex> = LazyLock::new(|| py(r"(?i)^\s*(?:Key|Legend)\s*:?\s*$"));
static FURNITURE_ATTR: LazyLock<Regex> =
    LazyLock::new(|| py(r#"(?i)\s(?:id|data-kind)="([^"]*(?:compass|rose|legend)[^"]*)""#));

/// SKILL.md 'Title block' and 'Orientation' (map drawing conventions): a title - the sheet's largest bold text, placed, its baseline above
/// the precinct's top edge (its SIZE varies by sheet and is not held); no compass rose (north-at-top is invariant, GM 2026-07); no key
/// box - by text, and by an id or a kind on ANY element (attributes, never comments).
///
/// Research:
///     the sheet's furniture - CONVENTION: the sheet's largest text is a bold title above the compound, and it draws no compass rose (north is always up) and no key box; research/questions/0241-the-map-sheet-its-title-legend-frame-and-margins.drawing.html records the no-compass and no-key conventions for a settlement sheet, and the title's place is the building plans' own; nothing about a building.
///
/// # Errors
/// The sheet's marks refused.
pub fn sheet_furniture(svg: &Sheet) -> Result<Vec<String>, Error> {
    let ms = svg.marks()?;
    let texts: Vec<&Mark> = ms
        .iter()
        .filter(|m| m.tag == "text" && m.placed && !m.text.is_empty())
        .collect();
    let precinct: Vec<f64> = ms
        .iter()
        .filter(|m| m.ident == "precinct")
        .map(|m| m.y)
        .collect();
    let top = (!precinct.is_empty()).then(|| min_of(precinct, 0.0));
    let mut sizes = Vec::new();
    for m in &texts {
        sizes.push(m.font_size()?);
    }
    let biggest = max_of(sizes.iter().copied(), 0.0);
    #[expect(
        clippy::float_cmp,
        reason = "the Python's `m.font_size == biggest`, the size it took the largest of"
    )]
    let titled = texts.iter().zip(&sizes).any(|(m, size)| {
        m.paint.get("font-weight").map(String::as_str) == Some("bold")
            && *size == biggest
            && top.is_none_or(|t| m.y <= t)
    });
    let mut out = Vec::new();
    if !titled {
        out.push(
            "no title block - the sheet's largest text, bold, centered just above the compound"
                .to_owned(),
        );
    }
    for m in ms.iter().filter(|m| m.tag == "text") {
        if COMPASS_TEXT.is_match(&m.text).unwrap_or(false) {
            out.push(format!(
                "a compass mark ('{}') at svg({},{}) - north is always up; the sheet draws no compass rose",
                m.text,
                fixed(m.x, 0),
                fixed(m.y, 0)
            ));
        } else if KEY_TEXT.is_match(&m.text).unwrap_or(false) {
            out.push(format!(
                "a key box ('{}') at svg({},{}) - the sheet labels its features in place, with no key",
                m.text,
                fixed(m.x, 0),
                fixed(m.y, 0)
            ));
        }
    }
    for c in FURNITURE_ATTR.captures_iter(svg.text).flatten() {
        out.push(format!(
            "an element marked '{}' - the sheet draws no compass rose and no key box",
            &c[1]
        ));
    }
    Ok(out)
}

/// A veranda's depth in feet: half a ken to one ken, the widths of Katsura's verandas, ACCURATE; free to change from face to face.
///
/// Research:
///     veranda depth band - research/questions/0102-verandas-and-storm-shutters-engawa-and-amado.drawing.html: a drawn veranda is 3 to 6 ft deep, half a ken to one ken, the widths of Katsura's verandas.
pub const VERANDA_FT: (f64, f64) = (3.0, 6.0);
/// Half a pixel either side: a strip is drawn on whole or half pixels at 3 px to the foot.
///
/// Research:
///     veranda depth tolerance - NONE: half a pixel either side, since strips are drawn on whole or half pixels.
pub const VERANDA_TOL_PX: f64 = 0.5;

/// Every veranda strip (a rect tagged `engawa`, or inside a group so tagged) is `band` ft deep across its short side.
///
/// # Errors
/// The sheet's marks refused.
pub fn veranda_depths(svg: &Sheet, band: (f64, f64)) -> Result<Vec<String>, Error> {
    let (lo, hi) = (
        band.0 * FTPX - VERANDA_TOL_PX,
        band.1 * FTPX + VERANDA_TOL_PX,
    );
    let mut out = Vec::new();
    for m in svg.marks()? {
        let depth = min(m.w, m.h);
        if m.tag == "rect" && m.kind.as_deref() == Some("engawa") && !(lo <= depth && depth <= hi) {
            out.push(format!(
                "the veranda at svg({},{}) is {} ft deep - the band is {}-{} ft",
                fixed(m.x, 0),
                fixed(m.y, 0),
                fixed(depth / FTPX, 1),
                fixed(band.0, 0),
                fixed(band.1, 0)
            ));
        }
    }
    Ok(out)
}
