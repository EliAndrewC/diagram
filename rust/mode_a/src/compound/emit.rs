//! The sheet written (derivation T208, "Writes"): every drawn shape with its kind, in the form the audit and the page read of every Mode A
//! sheet - the precinct rect of each court, the spine's grounds, the buildings with their rooms, bays and interiors, the doors, the parts,
//! the walls broken at their openings - and each caption DECLARED (its words, face, size and what it names), never placed: the one placer
//! seats them afterwards (`crate::caption_place`, feature 449 T202). Feet become pixels here alone, 3 px = 1 ft.
//!
//! Research: the sheet's plumbing - NONE: text, ids, numbers and box geometry; each drawn rule claimed on its unit (the plan scale on each unit that maps feet to pixels)

#![expect(
    clippy::many_single_char_names,
    reason = "geometry in feet: boxes, edges and points named as the derivation names them"
)]
use std::fmt::Write as _;

use super::count;
use super::layout::{back_face, door_specs, Layout, DIVIDER_HALF, DOOR, POST, WALL_HALF};
use super::spec::{Building, Bx, Court, Face, Program, Room};

/// The sheet's margin left of the compound and above it (px): the scale bar and the title stand above it.
///
/// Research: sheet margins - CONVENTION: the compound drawn 21 px in from the sheet's left edge and 45 px down, the title and the scale bar in the band above, the board and its margin below (docs/buildings.md, Framing: crop tight to content)
pub const ORIGIN: (f64, f64) = (21.0, 45.0);
/// The margin below the compound (px), holding the board outside the main gate.
///
/// Research:
///     sheet margins - CONVENTION: the band below the compound holding the board outside the main gate and its margin
pub const FOOT_PX: f64 = 46.0;
/// Pixels to the foot.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
pub const PX: f64 = 3.0;

/// The patterns every sheet's grounds are filled with (docs/buildings.md, Pattern library).
///
/// Research: pattern library - CONVENTION: court earth, sand, river cobbles, garden stipple, vegetable rows, granary slats, practice earth and the colonnade hatch of an open-sided shed (449 T359, ochiba-magistracy.svg's), the hand sheets' patterns and the cobbled court's
pub const DEFS: &str = r##"<defs><pattern id="court-earth" patternUnits="userSpaceOnUse" width="16" height="16"><rect width="16" height="16" fill="#D9C28E"/><circle cx="4" cy="6" r="0.6" fill="#A88E58"/><circle cx="12" cy="2" r="0.6" fill="#A88E58"/></pattern><pattern id="oshirasu-sand" patternUnits="userSpaceOnUse" width="12" height="12"><rect width="12" height="12" fill="#F2EAD0"/><circle cx="3" cy="4" r="0.5" fill="#C9B884"/><circle cx="8" cy="2" r="0.5" fill="#C9B884"/></pattern><pattern id="vegetable-rows" patternUnits="userSpaceOnUse" width="8" height="8"><rect width="8" height="8" fill="#CDBF95"/><rect y="2.5" width="8" height="3" fill="#8FA36A"/></pattern><pattern id="garden-stipple" patternUnits="userSpaceOnUse" width="14" height="14"><rect width="14" height="14" fill="#BFCFA0"/><circle cx="3" cy="3" r="0.8" fill="#7A8C5C"/><circle cx="10" cy="9" r="0.8" fill="#7A8C5C"/></pattern><pattern id="granary-slats" patternUnits="userSpaceOnUse" width="14" height="6"><rect width="14" height="6" fill="#D9B47A"/><line x1="0" y1="0" x2="14" y2="0" stroke="#7A5430" stroke-width="0.8"/><line x1="0" y1="3" x2="14" y2="3" stroke="#A88454" stroke-width="0.5"/></pattern><pattern id="court-cobbles" patternUnits="userSpaceOnUse" width="12" height="12"><rect width="12" height="12" fill="#D8D2C2"/><ellipse cx="3" cy="3" rx="2.2" ry="1.6" fill="#B8B0A0" stroke="#8A8274" stroke-width="0.4"/><ellipse cx="9" cy="8.5" rx="2" ry="1.5" fill="#B8B0A0" stroke="#8A8274" stroke-width="0.4"/></pattern><pattern id="keiko-earth" patternUnits="userSpaceOnUse" width="16" height="16"><rect width="16" height="16" fill="#E2CE9E"/><line x1="0" y1="5" x2="16" y2="5" stroke="#C2A46C" stroke-width="0.5"/><line x1="0" y1="13" x2="16" y2="13" stroke="#C2A46C" stroke-width="0.5"/></pattern><pattern id="colonnade-hatch" patternUnits="userSpaceOnUse" width="10" height="10" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C97A5C"/><line x1="0" y1="0" x2="0" y2="10" stroke="#8C4A30" stroke-width="1.2"/></pattern></defs>"##;

/// A number as the sheet writes it: two places at most, no trailing zeros.
#[must_use]
pub fn n(v: f64) -> String {
    let s = format!("{:.2}", (v * 100.0).round() / 100.0);
    let s = s.trim_end_matches('0').trim_end_matches('.');
    if s == "-0" {
        "0".to_owned()
    } else {
        s.to_owned()
    }
}

/// A point in feet as pixels.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
#[must_use]
pub fn px(x: f64, y: f64) -> (f64, f64) {
    (ORIGIN.0 + PX * x, ORIGIN.1 + PX * y)
}

/// The sheet being written: its text, the next shape id and the declared captions.
pub struct Svg {
    /// The text so far.
    pub out: String,
    next: usize,
    caps: Vec<String>,
}

impl Svg {
    /// An empty sheet.
    #[must_use]
    pub fn new() -> Self {
        Self {
            out: String::new(),
            next: 0,
            caps: Vec::new(),
        }
    }

    /// A fresh shape id.
    pub fn id(&mut self) -> String {
        let id = format!("d{}", self.next);
        self.next += 1;
        id
    }

    /// One drawn shape, counted.
    pub fn put(&mut self, s: &str) {
        count("write@compound_emit", 1);
        self.out.push_str(s);
        self.out.push('\n');
    }

    /// A rect in feet, with the attributes after its box.
    ///
    /// Research:
    ///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
    pub fn rect(&mut self, b: Bx, attrs: &str) {
        let (x, y) = px(b.0, b.1);
        let s = format!(
            r#"<rect x="{}" y="{}" width="{}" height="{}" {attrs}/>"#,
            n(x),
            n(y),
            n(PX * (b.2 - b.0)),
            n(PX * (b.3 - b.1))
        );
        self.put(&s);
    }

    /// A line in feet.
    ///
    /// Research:
    ///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
    pub fn line(&mut self, a: (f64, f64), b: (f64, f64), attrs: &str) {
        let (p, q) = (px(a.0, a.1), px(b.0, b.1));
        let s = format!(
            r#"<line x1="{}" y1="{}" x2="{}" y2="{}" {attrs}/>"#,
            n(p.0),
            n(p.1),
            n(q.0),
            n(q.1)
        );
        self.put(&s);
    }

    /// A caption declared: its words, face and what it names; the placer seats it.
    ///
    /// A caption the program gives on several lines (`\n` between them) is declared as its first line and a `data-cont` element for each
    /// further line, the lines its author chose, which the placer keeps.
    ///
    /// Research:
    ///     captions declared, placed last - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: each caption declared and held back, written after every shape, the one placer seating it
    pub fn caption(&mut self, words: &str, kind: &str, face: &str, names: &[String]) {
        count("decl_write@compound_caption", 1);
        let mut lines = words.split('\n');
        let first = lines.next().unwrap_or_default();
        self.caps.push(format!(
            r#"<text {face} data-kind="{}" data-names="{}">{}</text>"#,
            esc(kind),
            names.join(" "),
            esc(first)
        ));
        for more in lines {
            self.caps.push(format!(
                r#"<text {face} data-kind="{}" data-cont="1">{}</text>"#,
                esc(kind),
                esc(more)
            ));
        }
    }

    /// The captions, after every shape.
    ///
    /// Research:
    ///     captions declared, placed last - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the declared captions written after every shape
    #[must_use]
    pub fn finish(mut self) -> String {
        for c in std::mem::take(&mut self.caps) {
            self.out.push_str(&c);
            self.out.push('\n');
        }
        self.out.push_str("</svg>\n");
        self.out
    }
}

impl Default for Svg {
    fn default() -> Self {
        Self::new()
    }
}

/// Text escaped for XML.
#[must_use]
pub fn esc(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
}

/// A building's name's face: bold 10 px, 8 px on a small building.
///
/// Research: label sizes - CONVENTION: building names bold ~10-13 px, a small building's 8 px; sub-labels italic; tiny labels 7-8 px (docs/buildings.md, Label sizes)
pub const NAME: &str = r##"font-size="10" font-weight="bold" fill="#3A2E1C""##;
/// A small building's or a room's name.
///
/// Research:
///     label sizes - CONVENTION: a small building's or a room's name bold 8 px (docs/buildings.md, Label sizes)
pub const SMALL: &str = r##"font-size="8" font-weight="bold" fill="#3A2E1C""##;
/// A ground's name.
///
/// Research:
///     label sizes - CONVENTION: a ground's name italic 11 px (docs/buildings.md, Label sizes)
pub const GROUND: &str = r##"font-size="11" font-style="italic" fill="#5C4318""##;
/// A point's name.
///
/// Research:
///     label sizes - CONVENTION: tiny labels italic 7 px (docs/buildings.md, Label sizes)
pub const POINT: &str = r##"font-size="7" font-style="italic" fill="#3A2E1C""##;

/// Research:
///     zone fills - CONVENTION: each ground's pattern and edge (docs/buildings.md, Palette and Pattern library)
///     sand hearing court - research/questions/0099-the-hearing-court-shirasu.drawing.html: the roofed court's floor a knob, white gravel or cobbles from the local riverbed, each plan taking one
fn zone_paint(kind: &str, floor: Option<&str>) -> &'static str {
    match kind {
        "hearing court" if floor == Some("river cobbles") => {
            r##"fill="url(#court-cobbles)" stroke="#5A3F1E" stroke-width="2.0""##
        }
        "garden" => r##"fill="url(#garden-stipple)" stroke="#9C7A40" stroke-width="0.8""##,
        "vegetable garden" => {
            r##"fill="url(#vegetable-rows)" stroke="#9C7A40" stroke-width="0.8""##
        }
        "hearing court" => r##"fill="url(#oshirasu-sand)" stroke="#5A3F1E" stroke-width="2.0""##,
        "practice ground" => r##"fill="url(#keiko-earth)" stroke="#9C7A40" stroke-width="0.8""##,
        _ => r#"fill="url(#court-earth)" stroke="none" stroke-width="0""#,
    }
}

/// The line through the middle of the magistrate's seat over a hearing court: the first dais room of a seated building whose middle
/// stands over the court's span, if any.
///
/// Research:
///     the mats keyed to the dais - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: the accused kneels at the center, a third of the way in from the dais, facing the magistrate; where a court is cut short of the hall's door, so that its middle and the dais's no longer meet, "the center" is read as the line through the dais's middle, the page silent on such a court (449 T354)
fn dais_axis(p: &Program, l: &Layout, z: Bx) -> Option<f64> {
    p.buildings.iter().zip(&l.seats).find_map(|(b, at)| {
        let at = (*at)?;
        b.rooms
            .iter()
            .filter(|r| r.style == "dais")
            .map(|r| at.0 + f64::midpoint(r.bx.0, r.bx.2))
            .find(|&c| z.0 <= c && c <= z.2)
    })
}

/// The hearing court's posts along its open side, two ken apart, and the parties' mats in the Edo arrangement, the accused's on `cx`.
///
/// Research:
///     hearing court posts - research/questions/0099-the-hearing-court-shirasu.drawing.html: posts along the roofed court's open side, two ken (~12 ft) apart and 1 ft square, their size and spacing a GUESS
///     hearing mats - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: the accused's mat 6 x 3 ft at the center a third of the way in from the dais (on the dais's axis, `dais_axis`, the court's middle where no dais stands over it), the plaintiff's 6 x 3 ft behind to one side, the village officials' 12 ft mat behind to the other
fn hearing(s: &mut Svg, z: Bx, cx: f64) {
    let y = z.1 + (z.3 - z.1) / 3.0;
    let mat = r##"fill="#C8B078" stroke="#7A5430" stroke-width="0.6""##;
    s.put(r##"<g data-kind="kneeling positions"><g fill="#C8B078" stroke="#7A5430" stroke-width="0.6">"##);
    let mut ids = Vec::new();
    for b in [
        (cx - 3.0, y, cx + 3.0, y + 3.0),
        (cx - 16.0, y + 6.0, cx - 10.0, y + 9.0),
        (cx + 10.0, y + 6.0, cx + 22.0, y + 9.0),
    ] {
        let id = s.id();
        s.rect(b, &format!(r#"{mat} data-id="{id}""#));
        ids.push(id);
    }
    s.put("</g></g>");
    s.caption(
        "straw mats",
        "kneeling positions",
        r##"font-size="8" font-style="italic" fill="#7A5C30""##,
        &ids,
    );
    s.put(r##"<g fill="#5A3F1E" data-kind="hearing court">"##);
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a count of bays"
    )]
    let bays = ((z.2 - z.0) / 12.0).round().max(1.0) as usize;
    for k in 0..=bays {
        #[expect(clippy::cast_precision_loss, reason = "a post's ordinal")]
        let x = z.0 + (z.2 - z.0 - 1.0) * k as f64 / bays as f64;
        s.rect((x, z.3 - 1.0, x + 1.0, z.3), "");
    }
    s.put("</g>");
}

/// The precincts, the spine's grounds and their furniture.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
///     office front, residence rear - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: the residence behind the office, the yamen's order and Takayama's (one Japanese case)
///     the inner court to the north - research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.html: the gate faces south where nothing else decides, so the outer court lies south of the divider and the inner court, the residence, north of it (0090's office in front); the sheet's top as the compound's back is a map drawing convention
pub fn grounds(s: &mut Svg, p: &Program, l: &Layout) {
    for (court, b) in [
        (Court::Inner, (0.0, 0.0, p.w, p.divider)),
        (Court::Outer, (0.0, p.divider, p.w, p.h)),
    ] {
        let kind = if court == Court::Inner {
            "inner court"
        } else {
            "outer court"
        };
        let id = s.id();
        s.rect(b, &format!(r#"fill="url(#court-earth)" id="precinct" stroke="none" stroke-width="0" data-kind="{kind}" data-id="{id}""#));
    }
    for z in &p.zones {
        let id = s.id();
        s.rect(
            z.bx,
            &format!(
                r#"{} data-kind="{}" data-id="{id}""#,
                zone_paint(&z.kind, z.floor.as_deref()),
                esc(&z.kind)
            ),
        );
        if let Some(c) = &z.caption {
            s.caption(c, &z.kind, GROUND, &[id]);
        }
        if z.kind == "hearing court" {
            let cx = dais_axis(p, l, z.bx).unwrap_or_else(|| f64::midpoint(z.bx.0, z.bx.2));
            hearing(s, z.bx, cx);
        }
    }
}

/// A building's palette: its fill and stroke.
///
/// Research:
///     the palette's fills - CONVENTION: each palette role's fill and stroke, the hand sheets' palette
#[must_use]
pub fn paint(role: &str) -> (&'static str, &'static str) {
    crate::compound::KINDS
        .iter()
        .find(|(k, _)| *k == role)
        .map_or(("#E8D2A8", "#6B4F2A"), |(_, fs)| *fs)
}

/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
fn room(s: &mut Svg, b: &Building, at: Bx, r: &Room, fill: &str) {
    let bx = (at.0 + r.bx.0, at.1 + r.bx.1, at.0 + r.bx.2, at.1 + r.bx.3);
    let id = s.id();
    let k = esc(&r.kind);
    let (face, outline) = match r.style.as_str() {
        "passage" => {
            s.rect(bx, &format!(r##"fill="#E8D2A8" stroke="none" stroke-width="0" data-kind="{k}" data-id="{id}""##));
            // the passage's dotted edge is drawn once round all its pieces (`passage_ring`)
            (r##"font-size="7" font-weight="bold" fill="#3A2E1C""##, None)
        }
        "engawa" => {
            s.rect(bx, &format!(r##"fill="#E8D2A8" stroke="#5A3F1E" stroke-width="1.2" data-kind="{k}" data-id="{id}""##));
            (SMALL, None)
        }
        "dais" => {
            s.rect(bx, &format!(r##"fill="#8C6F3E" stroke="#4A3318" stroke-width="1" data-kind="{k}" data-id="{id}""##));
            // the hand sheets' dark ink at 7 px, which reads on the dais and off it where the placer seats it (449 T338: a light
            // caption seated off the dais read at about 1.8:1 on the hall's floor)
            (r##"font-size="7" font-weight="bold" fill="#3A2E1C""##, None)
        }
        "seat" => {
            s.put(&format!(r#"<g data-kind="{k}">"#));
            s.rect(
                bx,
                &format!(r##"fill="#B89868" stroke="#5C4830" stroke-width="0.5" data-id="{id}""##),
            );
            s.put("</g>");
            (r##"font-size="7" font-weight="bold" fill="#3A2E1C""##, None)
        }
        _ => {
            s.rect(
                bx,
                &format!(
                    r#"fill="{fill}" stroke="none" stroke-width="0" data-kind="{k}" data-id="{id}""#
                ),
            );
            (SMALL, Some("4 3"))
        }
    };
    if let Some(dash) = outline {
        let line = paint(&b.role).1;
        s.rect(
            bx,
            &format!(r#"fill="none" stroke="{line}" stroke-width="0.8" stroke-dasharray="{dash}""#),
        );
    }
    if let Some(c) = &r.caption {
        s.caption(c, &r.kind, face, &[id]);
    }
}

/// A building drawn: its body, its rooms, its dwelling walls and its interior by rule, its caption naming it.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
///     dwelling walls across the long side - research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.html: a rowhouse divided into dwellings along its length, each wall across its long side
pub fn building(s: &mut Svg, b: &Building, at: Bx) {
    let (fill, stroke) = paint(&b.role);
    let k = esc(&b.kind);
    let face = if b.w * b.h < 450.0 { SMALL } else { NAME };
    let grouped = !b.rooms.is_empty() || !b.bays.is_empty() || b.interior.is_some();
    if !grouped {
        let id = s.id();
        s.rect(
            at,
            &format!(
                r#"fill="{fill}" stroke="{stroke}" stroke-width="2" data-kind="{k}" data-id="{id}""#
            ),
        );
        s.caption(&b.caption, &b.kind, face, &[id]);
        return;
    }
    s.put(&format!(r#"<g data-kind="{k}">"#));
    let mut names = Vec::new();
    if b.rooms.is_empty() {
        let id = s.id();
        let own = if b.interior.is_some() {
            String::new()
        } else {
            format!(r#" data-kind="{k}""#)
        };
        // an open-sided shed's roof hatched over its open sides, as the hand sheets draw a workshop colonnade (449 T359)
        let body = if b.interior.as_deref() == Some(OPEN_SHED) {
            "url(#colonnade-hatch)"
        } else {
            fill
        };
        s.rect(
            at,
            &format!(r#"fill="{body}" stroke="{stroke}" stroke-width="2"{own} data-id="{id}""#),
        );
        names.push(id);
    } else {
        let id = s.id();
        s.rect(
            at,
            &format!(
                r#"fill="{fill}" stroke="none" stroke-width="0" data-kind="{k}" data-id="{id}""#
            ),
        );
        names.push(id);
        for r in b.rooms.iter().filter(|r| r.style != "seat") {
            room(s, b, at, r, fill);
        }
        passage_ring(s, b, at);
    }
    let along_x = b.w >= b.h;
    for &off in &b.bays {
        let (a, c) = if along_x {
            ((at.0 + off, at.1), (at.0 + off, at.3))
        } else {
            ((at.0, at.1 + off), (at.2, at.1 + off))
        };
        s.line(a, c, &format!(r#"stroke="{stroke}" stroke-width="1""#));
    }
    match b.interior.as_deref() {
        Some(STABLES) => stables(s, b, at),
        Some("cell") => cell(s, b, at),
        Some(OPEN_SHED) => shed_posts(s, at),
        _ => {}
    }
    if !b.rooms.is_empty() {
        let id = s.id();
        s.rect(
            at,
            &format!(r#"fill="none" stroke="{stroke}" stroke-width="2" data-id="{id}""#),
        );
        names.push(id);
        // the seats in the front band drawn over the outline, so nothing buries them
        for r in b.rooms.iter().filter(|r| r.style == "seat") {
            room(s, b, at, r, fill);
        }
    }
    s.put("</g>");
    s.caption(&b.caption, &b.kind, face, &names);
}

/// A building's passage pieces drawn as one passage: one dotted ring round their union, where it has any.
///
/// Research: the corridor drawn as one passage - CONVENTION: a corridor in several pieces is drawn as one passage - its pieces a lighter floor each, one dotted edge round them all and one caption (the round arbiter's ask:449-T182-room-layout, the round-trip's sheet)
fn passage_ring(s: &mut Svg, b: &Building, at: Bx) {
    let pieces: Vec<Bx> = b
        .rooms
        .iter()
        .filter(|r| r.style == "passage")
        .map(|r| (at.0 + r.bx.0, at.1 + r.bx.1, at.0 + r.bx.2, at.1 + r.bx.3))
        .collect();
    let mut d = String::new();
    for ring in union_rings(&pieces) {
        for (k, &(x, y)) in ring.iter().enumerate() {
            let (x, y) = px(x, y);
            let _ = write!(d, "{}{} {} ", if k == 0 { "M " } else { "L " }, n(x), n(y));
        }
        d.push_str("Z ");
    }
    if !d.is_empty() {
        let line = paint(&b.role).1;
        s.put(&format!(
            r#"<path d="{}" fill="none" stroke="{line}" stroke-width="0.8" stroke-dasharray="1 2"/>"#,
            d.trim_end()
        ));
    }
}

/// The outline of a union of boxes, as rings of corners (clockwise, y down): the boxes' edges cut into a grid, its filled cells' outer
/// sides chained into rings, straight runs merged.
#[must_use]
pub fn union_rings(boxes: &[Bx]) -> Vec<Vec<(f64, f64)>> {
    let mut xs: Vec<f64> = boxes.iter().flat_map(|b| [b.0, b.2]).collect();
    let mut ys: Vec<f64> = boxes.iter().flat_map(|b| [b.1, b.3]).collect();
    for v in [&mut xs, &mut ys] {
        v.sort_by(f64::total_cmp);
        v.dedup();
    }
    let (nx, ny) = (xs.len().saturating_sub(1), ys.len().saturating_sub(1));
    let filled = |i: usize, j: usize| {
        i < nx
            && j < ny
            && boxes.iter().any(|b| {
                let (cx, cy) = (
                    f64::midpoint(xs[i], xs[i + 1]),
                    f64::midpoint(ys[j], ys[j + 1]),
                );
                b.0 < cx && cx < b.2 && b.1 < cy && cy < b.3
            })
    };
    // each filled cell's open sides, as directed edges between grid corners (column, row)
    let mut edges: Vec<((usize, usize), (usize, usize))> = Vec::new();
    for j in 0..ny {
        for i in 0..nx {
            if !filled(i, j) {
                continue;
            }
            if j == 0 || !filled(i, j - 1) {
                edges.push(((i, j), (i + 1, j)));
            }
            if !filled(i + 1, j) {
                edges.push(((i + 1, j), (i + 1, j + 1)));
            }
            if !filled(i, j + 1) {
                edges.push(((i + 1, j + 1), (i, j + 1)));
            }
            if i == 0 || !filled(i - 1, j) {
                edges.push(((i, j + 1), (i, j)));
            }
        }
    }
    let mut rings = Vec::new();
    while let Some(first) = edges.pop() {
        let mut ring = vec![first.0];
        let mut at = first.1;
        while at != first.0 {
            ring.push(at);
            let k = edges.iter().position(|e| e.0 == at).unwrap_or_default();
            at = edges.swap_remove(k).1;
        }
        // straight runs merged: a corner kept only where the ring turns
        let len = ring.len();
        let turns: Vec<(f64, f64)> = (0..len)
            .filter(|&k| {
                let (a, b, c) = (ring[(k + len - 1) % len], ring[k], ring[(k + 1) % len]);
                !((a.0 == b.0 && b.0 == c.0) || (a.1 == b.1 && b.1 == c.1))
            })
            .map(|k| (xs[ring[k].0], ys[ring[k].1]))
            .collect();
        rings.push(turns);
    }
    rings
}

/// A box in the building's frame measured from its court face: `d0..d1` deep from that face, `a0..a1` along it.
fn from_court(at: Bx, court: Face, d: (f64, f64), a: (f64, f64)) -> Bx {
    match court {
        Face::N => (at.0 + a.0, at.1 + d.0, at.0 + a.1, at.1 + d.1),
        Face::S => (at.0 + a.0, at.3 - d.1, at.0 + a.1, at.3 - d.0),
        Face::W => (at.0 + d.0, at.1 + a.0, at.0 + d.1, at.1 + a.1),
        Face::E => (at.2 - d.1, at.1 + a.0, at.2 - d.0, at.1 + a.1),
    }
}

/// The stable's grooms' room's depth from its court face, and the earth passage's depth behind it (feet).
///
/// Research: the stable's depths - GUESS: the grooms' room 9 ft and the passage 6 ft deep from the court face, the stalls the rest; 0108's drawing page is silent on both depths (it draws the grooms' quarters and the earth-floored passage before the stalls). The search pass of 2026-11-23 (449 T401, keys t401-umaya, t401-umaya-b) found the three-bay warrior's stable gable-entered with its ridge along the stall row, as drawn, the depth of the form with a grooms' room silent, and the stables measured longer than deep only for stables without one, so the depths are not shrunk; its one depth, JAANUS's grooms' room 2 bays across, is not yet on 0108's page and is filed to reach it before this guess moves
pub const STABLE_DEPTHS: (f64, f64) = (9.0, 6.0);

/// The interior that draws a building as a stable: the grooms' room, the passage and the stalls (`layout::door_specs` enters it at a
/// gable into the passage).
///
/// Research: the stables' interior - NONE: the name a program gives a stable's interior, deciding nothing about the place
pub const STABLES: &str = "stables";

/// The stable's interior: the grooms' room on the court side, the earth passage before the stalls, the stalls one ken wide at the back.
///
/// Research:
///     stables - research/questions/0108-stables-umaya.html, research/questions/0108-stables-umaya.drawing.html: a warrior's small stable three bays long, its one-bay stalls on board floors, the earth passage (kusa-no-ma) before them running its length, the grooms' room (tozamurai) across the passage; the depths GUESSES
///     stable stall width - research/questions/0108-stables-umaya.drawing.html: a stall one bay, one ken (~6 ft) wide, by convention
///     grooms' room open to the passage - GUESS: the matted tozamurai opens onto the earth passage (kusa-no-ma), no wall between them, its edge drawn dashed as the passage's edge to the stalls is, the sheet's mark of an edge a body crosses where a solid interior line is a wall; 0108 puts the tozamurai across the kusa-no-ma from the stalls and is silent on what stood between them, and the stable is entered at its gable into the passage (449 T388; building-review 2026-11-23 E1: drawn solid, the grooms' room had no way in; impl-drift 2026-11-23 MISLABELED as a CONVENTION, a choice between built forms)
///     grooms' room toward the court - GUESS: the tozamurai on the stable's court side and the stalls toward its back face; no page we read says which of a stable's long sides faced its court
fn stables(s: &mut Svg, b: &Building, at: Bx) {
    let court = back_face(b).opposite();
    let (len, deep) = if court.along_x() {
        (b.w, b.h)
    } else {
        (b.h, b.w)
    };
    let (grooms, passage) = STABLE_DEPTHS;
    let edge = |s: &mut Svg, d: f64, attrs: &str| {
        let r = from_court(at, court, (d, d), (0.0, len));
        s.line((r.0, r.1), (r.2, r.3), attrs);
    };
    let floor = from_court(
        at,
        court,
        (grooms + 1.0 / 3.0, grooms + passage - 1.0 / 3.0),
        (1.0 / 3.0, len - 1.0 / 3.0),
    );
    let id = s.id();
    s.rect(
        floor,
        &format!(r##"fill="#B8A07A" stroke="none" stroke-width="0" data-id="{id}""##),
    );
    let mut x = 6.0;
    while x < len - 1e-6 {
        let r = from_court(at, court, (grooms + passage, deep), (x, x));
        s.line(
            (r.0, r.1),
            (r.2, r.3),
            r##"stroke="#6B4F2A" stroke-width="1""##,
        );
        x += 6.0;
    }
    let open = r##"stroke="#6B4F2A" stroke-width="0.8" stroke-dasharray="3 2""##;
    edge(s, grooms, open);
    edge(s, grooms + passage, open);
}

/// The cell's lattice: short bars across its court face, linework at visible stroke width, and a bar beside its door wherever the
/// door leaves a margin with none clear of it.
///
/// Research:
///     cell's bars - GUESS: short lattice bars across the cell's court face, 2 ft apart and about 1.3 ft long, linework; no page records a holding cell's bars
///     cell's bars beside its door - CONVENTION: the doors are drawn over the bars, so a margin of 1 ft or more beside a door on the court face with no bar clear of the door takes one at its middle, and the lattice reads on either side of the door (0096's drawing page: a cell drawn with bars across its front; 449 T351, the round arbiter's ask:cell-lattice-hidden-449-T351: on the county's 10 ft face the 6 ft door covered all four bars)
fn cell(s: &mut Svg, b: &Building, at: Bx) {
    let court = back_face(b).opposite();
    let len = if court.along_x() { b.w } else { b.h };
    let bar = |s: &mut Svg, x: f64| {
        let r = from_court(at, court, (0.0, 4.0 / 3.0), (x, x));
        s.line(
            (r.0, r.1),
            (r.2, r.3),
            r##"stroke="#3A2010" stroke-width="0.8""##,
        );
    };
    let mut bars = Vec::new();
    let mut x = 2.0;
    while x < len - 1.0 {
        bar(s, x);
        bars.push(x);
        x += 2.0;
    }
    let half = DOOR.0 / 2.0;
    for d in door_specs(b).iter().filter(|d| d.face == court) {
        let c = (d.at * len).clamp(half, (len - half).max(half));
        for (m0, m1) in [(0.0, c - half), (c + half, len)] {
            if m1 - m0 >= 1.0 && !bars.iter().any(|&x| x > m0 && x < m1) {
                bar(s, f64::midpoint(m0, m1));
            }
        }
    }
}

/// The interior that draws a building as an open-sided shed: a hatched roof on posts, with no door (`layout::door_specs`).
pub const OPEN_SHED: &str = "open shed";

/// An open shed's six posts: one at each corner, set in from it, and one at the middle of each long side.
///
/// Research:
///     the open shed on six posts - GUESS: no page counts or places a workshop shed's posts; six, one at each corner set 10 px (about 3 ft) in from the roof's corners and one at the middle of each long side, follow the hand sheet's cinnabar workshop (ochiba-magistracy.svg) (449 T359)
///     the post mark - CONVENTION: the hand sheet's mark, its roof hatched over open sides and a dark dot for each post, r 3 px (a 1 ft radius, 2 ft across); no page draws a workshop shed's posts (449 T359)
fn shed_posts(s: &mut Svg, at: Bx) {
    let inset = 10.0 / PX;
    let (x0, x1, y0, y1) = (at.0 + inset, at.2 - inset, at.1 + inset, at.3 - inset);
    let (xm, ym) = (f64::midpoint(x0, x1), f64::midpoint(y0, y1));
    let posts = if at.2 - at.0 >= at.3 - at.1 {
        [(x0, y0), (xm, y0), (x1, y0), (x0, y1), (xm, y1), (x1, y1)]
    } else {
        [(x0, y0), (x0, ym), (x0, y1), (x1, y0), (x1, ym), (x1, y1)]
    };
    for (x, y) in posts {
        let (cx, cy) = px(x, y);
        s.put(&format!(
            r##"<circle cx="{}" cy="{}" r="3" fill="#3A1810"/>"##,
            n(cx),
            n(cy)
        ));
    }
}

/// Every building in its seat order, then the doors.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
///     the genkan porch - CONVENTION: drawn as its building's own fill and stroke (1.2 px), captioned "genkan", under its door's glyph, which takes data-kind genkan; the porch's size and seat are layout's (`layout::GENKAN`)
pub fn buildings(s: &mut Svg, p: &Program, l: &Layout) {
    for &i in &l.order {
        if let Some(at) = l.seats[i] {
            building(s, &p.buildings[i], at);
        }
    }
    for d in &l.doors {
        let of = esc(&p.buildings[d.b].kind);
        let kind = if let Some(porch) = d.porch {
            let (fill, stroke) = paint(&p.buildings[d.b].role);
            let id = s.id();
            s.rect(porch, &format!(r#"fill="{fill}" stroke="{stroke}" stroke-width="1.2" data-kind="genkan" data-part-of="{of}" data-id="{id}""#));
            s.caption("genkan", "genkan", SMALL, &[id]);
            "genkan"
        } else {
            "door"
        };
        let id = s.id();
        s.rect(d.bx, &format!(r##"fill="#4A3318" stroke="none" stroke-width="0" data-kind="{kind}" data-part-of="{of}" data-id="{id}""##));
    }
}

/// The title, the scale bar, the walls broken at their openings, the gate posts and the middle gate.
///
/// Research:
///     compound wall stroke - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: 3 ft heavy stroke, each side its own line
///     scale bar - CONVENTION: 90 px bar labeled 30 ft in a top corner of the sheet, where every sheet draws it
///     divider wall - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: ~2 ft true-thickness wall with its own gate, drawn 6 px
///     gate posts - CONVENTION: a gate's posts drawn 2 ft along the wall, each post's inner face on the passage, keeping 0092's drawing page's 2 ft along the wall but lengthened across it to stand 2/3 ft past the 3 ft wall's ink on each face, since a 2 ft square post would vanish inside that ink (docs/buildings.md, Main gate)
///     the middle gate's posts - CONVENTION: the divider gate's posts drawn 2 ft wide, standing about 2/3 ft past the divider's ink on each face so they read as posts
pub fn frame(s: &mut Svg, p: &Program, l: &Layout) {
    let mid = ORIGIN.0 + PX * p.w / 2.0;
    s.put(&format!(r##"<text x="{}" y="18" text-anchor="middle" font-size="20" font-weight="bold" fill="#3A2E1C" data-kind="-">{}</text>"##, n(mid), esc(&p.title)));
    if !p.subtitle.is_empty() {
        s.put(&format!(r##"<text x="{}" y="36" text-anchor="middle" font-size="10" font-style="italic" fill="#6B4F2A" data-kind="-">{}</text>"##, n(mid), esc(&p.subtitle)));
    }
    s.put(r##"<g stroke="#3A2E1C" data-kind="-"><line x1="21" y1="9" x2="111" y2="9" stroke-width="2"/><line x1="21" y1="4" x2="21" y2="14" stroke-width="2"/><line x1="111" y1="4" x2="111" y2="14" stroke-width="2"/><line x1="66" y1="6" x2="66" y2="12" stroke-width="1"/></g>"##);
    s.put(r##"<text x="66" y="25" text-anchor="middle" font-size="10" fill="#3A2E1C" data-kind="-">30 ft</text>"##);
    s.put(r##"<text x="66" y="36" text-anchor="middle" font-size="8" font-style="italic" fill="#5C4830" data-kind="-">(3 px = 1 ft)</text>"##);
    s.put(r##"<g stroke="#2D2A24" stroke-width="9" data-kind="compound wall">"##);
    for face in [Face::N, Face::W, Face::E, Face::S] {
        let (len, at): (f64, &dyn Fn(f64) -> (f64, f64)) = match face {
            Face::N => (p.w, &|a| (a, 0.0)),
            Face::S => (p.w, &|a| (a, p.h)),
            Face::W => (p.h, &|a| (0.0, a)),
            Face::E => (p.h, &|a| (p.w, a)),
        };
        let mut cuts: Vec<(f64, f64)> = p
            .gates
            .iter()
            .filter(|g| g.wall == face)
            .map(|g| (g.at - g.width / 2.0, g.at + g.width / 2.0))
            .collect();
        cuts.sort_by(|a, b| a.0.total_cmp(&b.0));
        let mut from = 0.0;
        for (a, b) in cuts {
            s.line(at(from), at(a), "");
            from = b;
        }
        s.line(at(from), at(len), "");
    }
    s.put("</g>");
    s.put(r##"<g stroke="#3F3A30" stroke-width="6" data-kind="court divider">"##);
    match l.middle {
        Some((a, b)) => {
            s.line((0.0, p.divider), (a, p.divider), "");
            s.line((b, p.divider), (p.w, p.divider), "");
        }
        None => s.line((0.0, p.divider), (p.w, p.divider), ""),
    }
    s.put("</g>");
    // each post stands 2/3 ft past the wall's ink on both faces, as the middle gate's do, so it reads as a post and not as more wall
    let out = WALL_HALF + 2.0 / 3.0;
    for g in &p.gates {
        s.put(&format!(
            r##"<g fill="#2D2A24" data-kind="{}">"##,
            esc(&g.kind)
        ));
        let (a0, a1) = (g.at - g.width / 2.0, g.at + g.width / 2.0);
        for a in [a0 - POST, a1] {
            let b = match g.wall {
                Face::N => (a, -out, a + POST, out),
                Face::S => (a, p.h - out, a + POST, p.h + out),
                Face::W => (-out, a, out, a + POST),
                Face::E => (p.w - out, a, p.w + out, a + POST),
            };
            s.rect(b, "");
        }
        s.put("</g>");
    }
    if let Some((a, b)) = l.middle {
        s.put(r##"<g fill="#3F3A30" data-kind="nakamon" data-part-of="court divider">"##);
        let h = DIVIDER_HALF + 2.0 / 3.0;
        s.rect((a - POST, p.divider - h, a, p.divider + h), "");
        s.rect((b, p.divider - h, b + POST, p.divider + h), "");
        s.put("</g>");
    }
}

/// The sheet's head: the root and the patterns, the background.
///
/// Research:
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama
pub fn head(s: &mut Svg, p: &Program) {
    let (w, h) = (2.0 * ORIGIN.0 + PX * p.w, ORIGIN.1 + PX * p.h + FOOT_PX);
    let _ = writeln!(
        s.out,
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" font-family="Georgia, 'Times New Roman', serif">"#,
        n(w.round()),
        n(h.round())
    );
    s.out.push_str(DEFS);
    s.out.push('\n');
    s.rect(
        (
            (-ORIGIN.0) / PX,
            (-ORIGIN.1) / PX,
            p.w + ORIGIN.0 / PX,
            p.h + FOOT_PX / PX,
        ),
        r##"fill="#EFE3C2" data-kind="-""##,
    );
}
