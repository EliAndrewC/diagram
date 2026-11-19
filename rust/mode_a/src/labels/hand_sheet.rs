//! A hand-drawn Mode A sheet's captions, placed by the ONE placer (feature 449 T151, `labels/hand_sheet.py` but its `start_tags`, which
//! is [`crate::hand_sheet`]'s since T174; feature 266, in the render pipeline since feature 286). A sheet's SVG is the drawing and, for
//! each caption, its declaration - its text, its face and what it names - never where it stands (feature 286, the GM: *"There is no point
//! in having an automated check run against an automated process"*). [`placed`] reads the sheet's drawn shapes ([`read`]), classifies
//! each by its `data-kind` tag ([`classify`]), finds each caption's subject from its declaration and asks [`super::placer::place`] where
//! it goes ([`seat`]), and returns the sheet with every caption written there and its leader drawn; [`render`] draws that text as the
//! sheet's picture.
//!
//! WHERE THIS PORT MAY PART FROM THE PYTHON (the GM 2026-11-17, engine-plan.md: "the resulting maps do NOT need to be bitwise
//! identical"): two shapely calls, each measured on the four caption-placing sheets by `parse/lockstep_labels.rs` - a multi-part
//! subject's union area ([`seat::covers`], over `geo`) and a leader's tip on the ink it names ([`classify::leader_to_ink`], computed
//! exactly, where GEOS rounded a stroke's caps to chords). Everything else is the Python's arithmetic in its order.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3, as the GM's rule amends it for a drawn sheet): `hand_sheet.py` stays for its Python
//! importers (`compound_view.py`, the three magistracies' generators) until step 3b; an edit of it makes the same change here in the same
//! commit, and `parse/lockstep_labels.rs` lists every caption that stands apart.
//!
//! Research: the hand sheet's captions - NONE: a sheet read, its captions' subjects found from their declarations and the placer asked, the rules each decision rests on claimed where it is made

use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::geom::{inside, Pt};
use super::placer::{Cap, Join, Placement};
use super::standard::{CENTER_ABOVE_BASELINE_EM, CHAR_W_EM, WEIGHT_OBSTACLE};
use super::svg::{caption_svg, leader_svg};

pub mod classify;
pub mod read;
pub mod seat;

pub use classify::{classify, leader_blockers, leader_to_ink, soft_index};
pub use read::{read_sheet, Affine, IDENTITY};
pub use seat::{seat, subjects, Seated};

/// An element's attributes, as `ElementTree` keyed them.
pub type Attrs = BTreeMap<String, String>;

/// The kinds a caption may cross at a way's weight (plan P4: roads are stroked paths 18 to 40 px wide).
///
/// Research: way kinds - CONVENTION: a road, river or revetment is a way a caption may cross at a way's weight, read from the six sheets' tag census
pub const WAY_KINDS: [&str; 3] = ["road", "river", "revetment"];

/// The sheets' open ground - free space to a caption (plan P4). An explicit list: a name that merely CONTAINS "court" is not ground
/// (`court divider` is a wall), and a roofed floor on posts (`weighing floor`, the hearing court since feature 267) is built.
///
/// Research: open ground kinds - CONVENTION: the courts, practice ground, gardens, yards, grove and landing are open ground, free to a caption; a roofed floor is built
pub const GROUND_KINDS: [&str; 11] = [
    "outer court",
    "inner court",
    "border court",
    "practice ground",
    "garden",
    "vegetable garden",
    "garden pines",
    "cart yard",
    "rear yard",
    "shrine grove",
    "river landing",
];

/// What ground nested inside the ground a caption names costs (feature 267): a court's name takes the court's own open earth before a
/// garden inside it, and a garden before a building.
///
/// Research: nested ground weight - CONVENTION: ground nested in the ground a caption names weighs a quarter of an obstacle, so a court's name takes its own earth first
pub const WEIGHT_INNER: f64 = WEIGHT_OBSTACLE / 4.0;

/// What covering dark ink costs - a wall, a post, a dark roof (feature 267): black caption ink cannot be read on it.
///
/// Research: dark ink weight - CONVENTION: dark ink weighs two obstacles, so a caption with no free seat takes light ink first
pub const WEIGHT_DARK: f64 = 2.0 * WEIGHT_OBSTACLE;

/// Fills a name cannot be read on even as nested ground: a worked bed's rows run through the letters (feature 283).
///
/// Research: busy fills - CONVENTION: a vegetable bed's rows take no name, however light its ground
pub const BUSY_FILLS: [&str; 1] = ["url(#vegetable-rows)"];

/// Ink this dark (0-1 luma) or darker is dark to a caption.
///
/// Research: dark ink threshold - CONVENTION: ink of luma 0.3 or darker counts as dark to a caption, so a caption reads against it.
pub const DARK: f64 = 0.3;

/// What covering another caption costs: ten drawn obstacles (feature 267) - words on words are the one overlap a reader cannot see past.
///
/// Research: another caption's weight - CONVENTION: covering another caption weighs ten obstacles, the overlap a reader cannot see past
pub const WEIGHT_TEXT: f64 = 10.0 * WEIGHT_OBSTACLE;

/// How far a disc's drawn curve, sampled as a polygon, may stand inside the true curve (px): a leader's end on it lands within its 1 px trim
/// and this of the curve (feature 449 T192).
///
/// Research: a disc's sampled curve - CONVENTION: a disc's drawn curve sampled finely enough that no chord stands more than 0.05 px inside it - a drawn size on the sheet, not in the world; the sample count is the least whose chord sag R(1 - cos(pi / n)) is within it, R bounding the curve's half-axes (the pool's largest disc half-axis is 45 px, 80 samples at the bound)
pub const DISC_SAG_PX: f64 = 0.05;

/// A part big enough to be a block of a building (about 220 sq ft).
///
/// Research: block part size - CONVENTION: a part of 2000 px2 (about 220 sq ft) or more counts as a block of a building to the caption placer, not a sub-part - a calibration of the placer, which changes where a caption is seated
pub const BLOCK_PX: f64 = 2000.0;

/// How much of its box a multi-part subject must fill to be named against the box (feature 283).
///
/// Research: stepped subject fill - CONVENTION: a multi-part subject filling under 0.85 of its box is named against its parts, not the box - a calibration of the placer, which changes where a caption is seated
pub const STEPPED: f64 = 0.85;

/// The largest drawn thing a leader may not end against, in px (a well's curb is 24 x 24).
///
/// Research: leader-end glyph size - CONVENTION: a drawn thing up to 600 px2 (a well curb is 24 x 24) is a glyph a leader may not end against, so a caption's leader names the building.
pub const GLYPH_MAX_PX: f64 = 600.0;

/// A dark stroke this wide (half-width, px) or wider is a wall to a leader.
///
/// Research: wall stroke test - CONVENTION: a dark stroke 2 px or more in half-width is a wall a leader may not cross; sheet walls are 6-9 px, partitions 1 px or less - a calibration of the placer, which changes how a leader is drawn
pub const WALL_HALF_PX: f64 = 2.0;

/// Width per character of a hand sheet's ALL-CAPS captions (feature 267).
///
/// Research: caps caption width - NONE: a hand sheet's all-caps captions run about 0.70 em per character, a text-measuring figure.
pub const CAPS_W_EM: f64 = 0.70;

/// What bold adds per character.
///
/// Research: bold caption width - NONE: bold adds about 0.04 em per character to a caption's width, a text-measuring figure.
pub const BOLD_W_EM: f64 = 0.04;

/// How far from a stranded caption's subject a neighbor is lifted to free a seat for it.
///
/// Research: caption repair reach - CONVENTION: a neighbor within 2 ems of a stranded caption's subject (plus the caption's length) is lifted to free a seat; a calibration of the placer.
pub const REPAIR: f64 = 2.0;

/// A fill this light (0-1 luma) is a caption chosen to read on dark ink; it reads on nothing else.
///
/// Research: light fill threshold - CONVENTION: a fill of luma 0.75 or lighter is a caption chosen to read on dark ink.
pub const LIGHT: f64 = 0.75;

/// The sheets' caption ink.
///
/// Research: the caption ink - CONVENTION: the sheets' captions are written in one dark brown ink, #3A2E1C
pub const DARK_INK: &str = "#3A2E1C";

/// The attributes a placed caption keeps of its own element.
const STYLE: [&str; 6] = [
    "font-style",
    "font-weight",
    "letter-spacing",
    "paint-order",
    "stroke",
    "stroke-width",
];

/// One drawn element, in sheet coordinates (the Python's `Shape`): its tag and kind, its outline (or polyline and stroke half-width), and
/// for a `<text>` the caption it carries - its words, size, lines, its parent's matrix, its place in the document, its declared names and
/// whether it continues the caption before. `attrs` are its element's attributes. (The Python's `angle`, `center` and `within` were
/// written and never read, and are not carried.)
#[derive(Debug, Clone)]
#[expect(
    clippy::struct_excessive_bools,
    reason = "the Python's `Shape`, field for field"
)]
pub struct Shape {
    pub tag: String,
    pub kind: String,
    pub poly: Vec<Pt>,
    pub half: f64,
    pub line: bool,
    pub text: String,
    pub size: f64,
    pub attrs: Option<Attrs>,
    pub leader: bool,
    pub lines: Vec<String>,
    pub group: usize,
    pub frame: Affine,
    pub edge: f64,
    pub texture: bool,
    pub filled: bool,
    pub busy: bool,
    pub dark: bool,
    pub at: usize,
    pub ids: BTreeSet<String>,
    pub names: Vec<String>,
    pub cont: bool,
    /// A stroke's `stroke-linecap`, inherited as SVG inherits it (feature 449 T193).
    pub cap: Cap,
    /// A stroke's `stroke-linejoin`, inherited (feature 449 T194).
    pub join: Join,
    /// A stroke's `stroke-miterlimit`, inherited (SVG's default 4): a sharper corner's miter is drawn as a bevel (T194).
    pub miter: f64,
    /// A stroke a path's `Z` closed: drawn with a join at its start, no caps (T194).
    pub closed: bool,
    /// A stroke's `stroke-dasharray` in sheet px, an even count (empty: solid), inherited (T194).
    pub dash: Vec<f64>,
    /// A stroke's `stroke-dashoffset` in sheet px, inherited (T194).
    pub offset: f64,
}

impl Default for Shape {
    /// The Python's `Shape` defaults: nothing drawn, SVG's stroke defaults (a butt cap, a miter join, a miter limit of 4, solid).
    ///
    /// Research: its drawn sizes - NONE: SVG's default `stroke-miterlimit`, 4
    fn default() -> Self {
        Self {
            tag: String::new(),
            kind: String::new(),
            poly: Vec::new(),
            half: 0.0,
            line: false,
            text: String::new(),
            size: 0.0,
            attrs: None,
            leader: false,
            lines: Vec::new(),
            group: 0,
            frame: (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            edge: 0.0,
            texture: false,
            filled: false,
            busy: false,
            dark: false,
            at: 0,
            ids: BTreeSet::new(),
            names: Vec::new(),
            cont: false,
            cap: Cap::Butt,
            join: Join::Miter,
            miter: 4.0,
            closed: false,
            dash: Vec::new(),
            offset: 0.0,
        }
    }
}

impl Shape {
    /// `el.get(name)` of its element.
    #[must_use]
    pub fn get(&self, name: &str) -> Option<&str> {
        self.attrs.as_ref()?.get(name).map(String::as_str)
    }
}

static LETTER: LazyLock<Regex> = LazyLock::new(|| py(r"\A\p{L}\z"));

/// A `#rgb` or `#rrggbb` fill's luma (0 black, 1 white); anything else - none, a pattern - reads as 0.5.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.114 (Rec.601 luma weight (blue)); 16 (hex base); 0.299 (Rec.601 luma weight (red)); 0.587 (Rec.601 luma weight (green))
#[must_use]
pub fn luma(fill: Option<&str>) -> f64 {
    let fill = l7r_guard::shared::py_text::strip(fill.unwrap_or_default());
    // `re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", fill)`
    let Some(h) = fill
        .strip_prefix('#')
        .filter(|h| matches!(h.len(), 3 | 6) && h.bytes().all(|c| c.is_ascii_hexdigit()))
    else {
        return 0.5;
    };
    let h: String = if h.len() == 3 {
        h.chars().flat_map(|c| [c, c]).collect()
    } else {
        h.to_owned()
    };
    let ch = |i: usize| f64::from(u8::from_str_radix(&h[i..i + 2], 16).unwrap_or(0)) / 255.0;
    0.299 * ch(0) + 0.587 * ch(2) + 0.114 * ch(4)
}

/// How wide a text's characters run, in ems, from its element's face: ALL-CAPS wider, bold wider, letter-spacing its own width.
///
/// Research: a caption's width by its face - NONE: the text metrics of its face applied, caps, bold and letter-spacing
#[must_use]
pub fn char_w_of(attrs: Option<&Attrs>, text: &str, size: f64) -> f64 {
    let letters: Vec<char> = text
        .chars()
        .filter(|c| LETTER.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false))
        .collect();
    let mut w = if !letters.is_empty() && letters.iter().all(|c| c.is_uppercase()) {
        CAPS_W_EM
    } else {
        CHAR_W_EM
    };
    if let Some(a) = attrs {
        if a.get("font-weight").map(String::as_str) == Some("bold") {
            w += BOLD_W_EM;
        }
        if size != 0.0 {
            w += read::attr_f(a, "letter-spacing", 0.0) / size;
        }
    }
    w
}

/// Is the innermost filled shape under a point dark?
///
/// Research: a light name on light ground - CONVENTION: a caption in light ink reads only on dark ink, so set down on light ground it is written in the sheets' dark ink (feature 267)
fn on_dark(pt: Pt, shapes: &[Shape]) -> bool {
    let under = shapes.iter().filter(|s| {
        s.tag != "text"
            && !s.line
            && s.get("fill").is_some_and(|f| !f.is_empty())
            && inside(pt.0, pt.1, &s.poly)
    });
    let least = under.fold(None, |m: Option<&Shape>, s| match m {
        Some(b) if seat::area(&b.poly) <= seat::area(&s.poly) => Some(b),
        _ => Some(s),
    });
    least.is_some_and(|s| luma(s.get("fill")) < 1.0 - LIGHT)
}

/// The byte offset of each code point (and of the end), so the Python's code-point offsets cut the source where it cut.
fn byte_offsets(src: &str) -> Vec<usize> {
    src.char_indices()
        .map(|(i, _)| i)
        .chain(std::iter::once(src.len()))
        .collect()
}

/// Where the element whose start tag spans `a..b` (bytes) ends: past its own end tag, found by the start tag's own name - `</text>`, or
/// `</s:text>` for a caption written with a prefix bound to the SVG namespace (feature 449 T184: the Python looked for `</text>` alone,
/// and so refused a prefixed caption, or wrote it over through the next caption's end).
///
/// # Errors
/// No end tag of that name after it, which a sheet the XML reader read whole never lacks.
fn element_end(src: &str, a: usize, b: usize) -> Result<usize, Error> {
    let name = tag_name(src, a, b);
    let close =
        l7r_guard::shared::regex::build(&format!(r"</{}[ \t\r\n]*>", fancy_regex::escape(&name)))
            .expect("an escaped name");
    match close.find_from_pos(src, b) {
        Ok(Some(m)) => Ok(m.end()),
        _ => Err(Error::new(
            "ValueError",
            format!("the caption's <{name}> has no end tag"),
        )),
    }
}

/// The name the start tag spanning `a..b` (bytes) is written under - `text`, or `s:text` with a prefix.
fn tag_name(src: &str, a: usize, b: usize) -> String {
    src[a + 1..b]
        .chars()
        .take_while(|c| !c.is_whitespace() && !matches!(c, '/' | '>'))
        .collect()
}

/// A written caption or leader ([`caption_svg`], [`leader_svg`]) under the prefix its own element was written with, its colon kept (`s:`):
/// a caption declared as `<s:text>` on a sheet binding SVG only to `s` is written back as `<s:text>`, its lines `<s:tspan>` and its leader
/// `<s:line>` (feature 449 T188: written as a plain `<text>`, it fell into no namespace and was drawn by no renderer). The writer's own text
/// escapes every `<` it carries, so each `<` opens one of its three elements.
fn in_prefix(svg: &str, prefix: &str) -> String {
    if prefix.is_empty() {
        return svg.to_owned();
    }
    let open =
        l7r_guard::shared::regex::build(r"<(/?)(text|tspan|line)\b").expect("a fixed pattern");
    open.replace_all(svg, format!("<${{1}}{prefix}${{2}}").as_str())
        .into_owned()
}

/// The sheet with every caption written where the placer put it, and its leader drawn after it (feature 286, plan D5): what a sheet's
/// picture and page are rendered from. The tracked sheet is the drawing and the declarations; this is a function of them alone.
///
/// # Errors
/// The Python's refusals, word for word: a sheet that is no XML, a caption that names nothing, a continuation with no caption before it.
///
/// Research: a caption written where it is seated - CONVENTION: each caption written in its own text's parent frame where the placer seats it, its own face kept, a light name on light ground in the sheets' dark ink, and its leader drawn after it (feature 286, plan D5)
pub fn placed(src: &str) -> Result<String, Error> {
    let (shapes, view) = read_sheet(src)?;
    let tags = crate::hand_sheet::start_tags(src);
    // FEATURE 449 T182: a caption is paired with its start tag by its index, so the two lists must be one length - an entity that expands to
    // markup draws an element the source writes no tag for, and every later caption would be written at the wrong tag
    if tags.len() != crate::etree::fromstring(src)?.elements().len() {
        return Err(Error::new("ValueError", "the sheet's elements and its start tags disagree - an entity that expands to markup draws an element the source does not write; write the element out"));
    }
    let bytes = byte_offsets(src);
    let mut edits: Vec<(usize, usize, String)> = Vec::new();
    for (caps, p, per, _) in seat(&shapes, view)? {
        let head = &shapes[caps[0]];
        let fill = head
            .get("fill")
            .filter(|f| !f.is_empty())
            .unwrap_or(DARK_INK)
            .to_owned();
        let sizes: Vec<f64> = caps.iter().map(|&c| shapes[c].size).collect();
        let counts: Vec<usize> = per.iter().map(Vec::len).collect();
        let centers = seat::line_centers(&p, &sizes, &counts);
        let mut news: Vec<(usize, usize, String)> = Vec::new();
        // the prefix the caption's texts are written with: its last text's, under which its leader is written too
        let mut prefix = String::new();
        for ((&ci, cap_lines), &(cx, cy)) in caps.iter().zip(&per).zip(&centers) {
            let cap = &shapes[ci];
            let style = STYLE.iter().fold(String::new(), |mut out, a| {
                if let Some(v) = cap.get(a).filter(|v| !v.is_empty()) {
                    let _ = write!(out, " {a}=\"{v}\"");
                }
                out
            });
            // a one-text caption takes the placement's LINES - the standard may wrap it
            let lines = if caps.len() == 1 {
                p.lines.clone()
            } else {
                cap_lines.clone()
            };
            // written in the text's PARENT frame: a caption inside a translated group is written in that group's coordinates
            let (lx, ly) = read::apply(read::inverse(cap.frame), (cx, cy));
            let at = Placement {
                x: lx,
                y: ly + CENTER_ABOVE_BASELINE_EM * cap.size,
                angle: p.angle - read::angle(cap.frame),
                lines,
                leader: None,
                ..p.clone()
            };
            let mut ink = cap.get("fill").unwrap_or(&fill).to_owned();
            if luma(Some(&ink)) > LIGHT && !on_dark((cx, cy), &shapes) {
                DARK_INK.clone_into(&mut ink); // a light name chosen for a dark roof, set down on light ground (feature 267)
            }
            // every element has its start tag, checked above
            let (a, b) = tags[cap.at];
            let end = element_end(src, bytes[a], bytes[b])?;
            let name = tag_name(src, bytes[a], bytes[b]);
            name.find(':')
                .map_or("", |k| &name[..=k])
                .clone_into(&mut prefix);
            // a text carrying its OWN tag keeps it (it is its own group); one taking its tag from a group stays untagged
            let kind = if cap.get("data-kind").is_some_and(|k| !k.is_empty()) {
                cap.kind.as_str()
            } else {
                ""
            };
            news.push((
                bytes[a],
                end,
                in_prefix(&caption_svg(&at, cap.size, &style, &ink, kind, ""), &prefix),
            ));
        }
        if let Some((l0, l1)) = p.leader {
            let inv = read::inverse(head.frame);
            let local = Placement {
                leader: Some((read::apply(inv, l0), read::apply(inv, l1))),
                ..p.clone()
            };
            let kind = if head.get("data-kind").is_some() {
                head.kind.as_str()
            } else {
                ""
            };
            if let Some(last) = news.last_mut() {
                last.2 = format!(
                    "{}\n    {}",
                    last.2,
                    in_prefix(&leader_svg(&local, head.size, &fill, kind, true), &prefix)
                );
            }
        }
        edits.extend(news);
    }
    edits.sort();
    let mut out = src.to_owned();
    for (a, end, new) in edits.into_iter().rev() {
        out.replace_range(a..end, &new);
    }
    Ok(out)
}

/// The arguments every sheet's picture is drawn with (`resvg --width 2400 --serif-family "DejaVu Serif"`).
///
/// Research: the sheets' face and width - CONVENTION: every sheet's picture is drawn 2400 px wide, its serif lettering in `DejaVu Serif` - a display choice of the sheets, not of the world
#[must_use]
pub fn render_args() -> Vec<String> {
    ["--width", "2400", "--serif-family", "DejaVu Serif"]
        .map(str::to_owned)
        .to_vec()
}

/// Render a sheet's placed text to `png` with resvg, as every sheet's gen does - the `resvg` crate in process (`raster/render.rs`, the
/// binary the Python ran, as a library), where the Python wrote a temporary file beside the picture for the binary to read.
///
/// # Errors
/// The renderer's refusal, or the picture that could not be written (Python's `OSError`, its class and words).
pub fn render(src: &str, png: &std::path::Path) -> Result<(), Error> {
    let bytes = crate::raster::render::png(src, &render_args())?;
    std::fs::write(png, bytes).map_err(|e| crate::py::os_error(&e, &png.to_string_lossy()))
}

#[cfg(test)]
mod ink_tests;
#[cfg(test)]
mod leader_tests;
#[cfg(test)]
mod stroke_tests;
#[cfg(test)]
mod tests;
