//! The map's SVG, written as the deleted Python drew the stages through the cut (feature 444 T42; `t42-brief.md` section 4): one
//! foot a unit, the layers in draw order, the palette the Python held.
//!
//! Research:
//!     the SVG writer - NONE: the document's plumbing, writing each shape in the ink and width it is handed; the palette and each
//!     drawn figure are claimed where they are chosen

use std::collections::BTreeMap;
use std::fmt::Write as _;

use crate::field::fan::Pt;

/// The land, the paddy's states, the bunds and the water's inks.
///
/// Research:
///     the palette - CONVENTION: the deleted engine's inks, carried as they stood
///     the wet paddy's tint - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: the wet paddy tinted blue-green, the tint marking the ground
pub mod ink {
    pub const LAND: &str = "#EFE3C2";
    pub const RICE_GREEN: &str = "#A6C398";
    pub const FLOODED: &str = "#93B7AC";
    pub const POND_WATER: &str = "#9CB4C8";
    pub const RIPE_GOLD: &str = "#C9BA79";
    pub const REST_GRASS: &str = "#C8CF92";
    pub const REST_TUFT: &str = "#8FA05E";
    pub const AZE: &str = "#6E4520";
    pub const SUPPLY: &str = "#6C9CBE";
    pub const DRAIN: &str = "#4F7186";
    pub const RIM: &str = "#5C7488";
    pub const SHEEN: &str = "#B6CAD8";
    pub const WEIR_FILL: &str = "#7A6A52";
    pub const WEIR_EDGE: &str = "#4E4232";
    pub const MOUND: &str = "#CFC6B4";
    pub const MOUND_EDGE: &str = "#8C8470";
    pub const STONE: &str = "#9AA1A4";
    pub const STONE_EDGE: &str = "#5A584F";
    pub const BEAN: &str = "#2F6B35";
    pub const REED: &str = "#7FA040";
    pub const REED_TINT: &str = "#C3D0A4";
}

/// The reed cover's tile: the pale wet green with sparse paired ticks, upright, a tile 48 ft square (`Svg::reeds`).
///
/// Research:
///     the reeds' glyph - CONVENTION: the deleted engine's reed cover, a pale wet green with sparse ticks, its tile redrawn here
///     (feature 444 T42, the partial map's look: a flat tint read as meadow)
const REED_TILE: &str = r##"<pattern id="reed-ticks" patternUnits="userSpaceOnUse" width="48" height="48"><rect width="48" height="48" fill="#C3D0A4"/><g stroke="#7FA040" stroke-width="1.6" stroke-linecap="round"><path d="M8 20 L7 11 M11 20 L12 12 M32 42 L31 33 M35 42 L36 34 M24 8 L23 1 M27 8 L28 2"/></g></pattern>"##;

/// The denser reed tile of a bank band: the same reeds, their ticks four times as thick on the ground and a shade darker
/// (`Svg::reed_bank`).
///
/// Research:
///     the bank band's glyph - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: a narrow band of denser, slightly darker reeds lines each bank - a map drawing CONVENTION: the plain reed tile (`REED_TILE`) sets 6 ticks on a 48 ft square over #C3D0A4, this one 6 ticks on a 24 ft square, four times as many to the foot, over the darker #AFC283, its ticks the darker #6A8C32 for the plain tile's #7FA040
const REED_BANK_TILE: &str = r##"<pattern id="reed-bank" patternUnits="userSpaceOnUse" width="24" height="24"><rect width="24" height="24" fill="#AFC283"/><g stroke="#6A8C32" stroke-width="1.6" stroke-linecap="round"><path d="M4 10 L3.5 5 M6 10 L6.5 6 M16 21 L15.5 16 M18 21 L18.5 17 M12 4 L11.5 0 M14 4 L14.5 1"/></g></pattern>"##;

/// The bund's stroke width (ft): the drawing floor of 1.5.
///
/// Research:
///     the bund's stroke - CONVENTION: the deleted `aze_w`, never under 1.5 ft so a bund reads at the map's scale
pub const BUND_W: f64 = 1.5;

/// The ridged rows' spacing in a dry plot (ft).
///
/// Research:
///     furrowed rows - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: every dry plot drawn in ridged rows
///     furrow spacing - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html records 5 ft between rows as a guess (the deleted `_draw_furrows`)
pub const ROW_FT: f64 = 5.0;

/// The census's key for a mark drawn with no kind named: a test holds every roll free of it.
pub const UNNAMED: &str = "?";

/// An SVG under construction: the elements in draw order, the box of everything drawn (for the crop), and the ink census - each kind
/// of the registry the marks depict, with how many marks (feature 449 T230: the review owed lookup's legend of a hamlet, which the
/// deleted Python's manifest held as `ink_classes`).
#[derive(Debug, Default)]
pub struct Svg {
    body: String,
    bbox: Option<[f64; 4]>,
    clips: usize,
    kind: String,
    census: BTreeMap<String, usize>,
}

fn f(v: f64) -> String {
    let s = format!("{v:.1}");
    s.strip_suffix(".0").map_or(s.clone(), str::to_owned)
}

fn path(pts: &[Pt], close: bool) -> String {
    let mut d = String::new();
    for (i, p) in pts.iter().enumerate() {
        let _ = write!(
            d,
            "{}{},{}",
            if i == 0 { "M" } else { " L" },
            f(p.0),
            f(p.1)
        );
    }
    if close {
        d.push_str(" Z");
    }
    d
}

impl Svg {
    /// The kind the marks drawn next depict, by the registry's name (`-` for a mark that is no element).
    pub fn kind(&mut self, kind: &str) {
        kind.clone_into(&mut self.kind);
    }

    /// The ink census: each kind drawn and how many marks.
    #[must_use]
    pub fn census(&self) -> &BTreeMap<String, usize> {
        &self.census
    }

    fn inked(&mut self) {
        let kind = if self.kind.is_empty() {
            UNNAMED
        } else {
            &self.kind
        };
        *self.census.entry(kind.to_owned()).or_default() += 1;
    }

    fn grow(&mut self, pts: &[Pt], pad: f64) {
        for p in pts {
            let b = self.bbox.get_or_insert([p.0, p.1, p.0, p.1]);
            *b = [
                b[0].min(p.0 - pad),
                b[1].min(p.1 - pad),
                b[2].max(p.0 + pad),
                b[3].max(p.1 + pad),
            ];
        }
    }

    /// A filled ring, its stroke optional.
    pub fn polygon(&mut self, ring: &[Pt], fill: &str, stroke: Option<(&str, f64)>) {
        if ring.len() < 3 {
            return;
        }
        self.grow(ring, stroke.map_or(0.0, |s| s.1 / 2.0));
        let edge = stroke.map_or_else(String::new, |(c, w)| {
            format!(
                r#" stroke="{c}" stroke-width="{}" stroke-linejoin="round""#,
                f(w)
            )
        });
        self.inked();
        let _ = writeln!(
            self.body,
            r#"<path d="{}" fill="{fill}"{edge}/>"#,
            path(ring, true)
        );
    }

    /// A band between two rings, the inner a hole (even-odd), its edges stroked.
    pub fn band(&mut self, outer: &[Pt], inner: &[Pt], fill: &str, edge: (&str, f64)) {
        if outer.len() < 3 {
            return;
        }
        self.grow(outer, edge.1 / 2.0);
        self.inked();
        let _ = writeln!(
            self.body,
            r#"<path d="{} {}" fill="{fill}" fill-rule="evenodd" stroke="{}" stroke-width="{}"/>"#,
            path(outer, true),
            path(inner, true),
            edge.0,
            f(edge.1)
        );
    }

    /// A stroked line, round-capped.
    pub fn line(&mut self, pts: &[Pt], stroke: &str, w: f64) {
        if pts.len() < 2 {
            return;
        }
        self.grow(pts, w / 2.0);
        self.unframed(pts, stroke, w);
    }

    /// A stroked line that does not frame the crop: a brook runs off the canvas both ways, and the map is framed to the features
    /// it serves, the crop cutting the rest (the deleted `content_view`).
    pub fn unframed(&mut self, pts: &[Pt], stroke: &str, w: f64) {
        if pts.len() < 2 {
            return;
        }
        self.inked();
        let _ = writeln!(
            self.body,
            r#"<path d="{}" fill="none" stroke="{stroke}" stroke-width="{}" stroke-linecap="round" stroke-linejoin="round"/>"#,
            path(pts, false),
            f(w)
        );
    }

    /// A reed cover: the ring filled with the reed tile, unstroked.
    ///
    /// Research:
    ///     the reed glyph - CONVENTION: the deleted engine's reed tile, a repeated reed mark filling the cover
    pub fn reeds(&mut self, ring: &[Pt]) {
        self.polygon(ring, "url(#reed-ticks)", None);
    }

    /// A bank band of denser reeds: the line (two points or more, as `bank_bands` cuts them) stroked `w` wide with the denser reed
    /// tile, butt-ended, framing nothing.
    ///
    /// Research:
    ///     the band's glyph - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: denser, slightly darker reeds along a bank, a CONVENTION (`REED_BANK_TILE`)
    pub fn reed_bank(&mut self, pts: &[Pt], w: f64) {
        self.inked();
        let _ = writeln!(
            self.body,
            r#"<path d="{}" fill="none" stroke="url(#reed-bank)" stroke-width="{}" stroke-linecap="butt" stroke-linejoin="round"/>"#,
            path(pts, false),
            f(w)
        );
    }

    /// A ground kept for what a later stage draws: its ring dashed, unfilled, and its name at its middle - the partial map's mark
    /// for the settlement the homesteads will fill (feature 444 amendment 11, the cut before them); it frames the crop, so the
    /// ground it keeps is on the sheet.
    ///
    /// Research:
    ///     the placeholder - CONVENTION: a dashed outline 4 ft wide (24 on, 16 off) and a serif label 56 ft high at its centroid
    pub fn reserved(&mut self, ring: &[Pt], stroke: &str, name: &str) {
        if ring.len() < 3 {
            return;
        }
        self.grow(ring, 2.0);
        self.inked();
        #[expect(clippy::cast_precision_loss, reason = "a ring of a few corners")]
        let n = ring.len() as f64;
        let (cx, cy) = (
            ring.iter().map(|p| p.0).sum::<f64>() / n,
            ring.iter().map(|p| p.1).sum::<f64>() / n,
        );
        let _ = writeln!(
            self.body,
            r#"<path d="{}" fill="none" stroke="{stroke}" stroke-width="4" stroke-dasharray="24 16"/>"#,
            path(ring, true)
        );
        let _ = writeln!(
            self.body,
            r#"<text x="{}" y="{}" font-family="serif" font-size="56" fill="{stroke}" text-anchor="middle">{name}</text>"#,
            f(cx),
            f(cy)
        );
    }

    /// A channel tapering from `w0` at its head to `w1` at its tail: one piece a segment, each at the width its arc-length middle
    /// carries (`sqrt(w0^2 + (w1^2 - w0^2) t)`, the deleted `taper_w`), one path where the taper is under 0.2 ft.
    ///
    /// Research:
    ///     a channel's taper - UNRESEARCHED: its width squared growing linearly from head to tail, the deleted `taper_w`
    pub fn taper(&mut self, pts: &[Pt], stroke: &str, w0: f64, w1: f64) {
        if (w1 - w0).abs() < 0.2 || pts.len() < 3 {
            self.line(pts, stroke, w0.max(w1));
            return;
        }
        let lens: Vec<f64> = pts
            .windows(2)
            .map(|s| (s[1].0 - s[0].0).hypot(s[1].1 - s[0].1))
            .collect();
        let total: f64 = lens.iter().sum::<f64>().max(1e-9);
        let mut at = 0.0;
        for (s, len) in pts.windows(2).zip(&lens) {
            let t = (at + len / 2.0) / total;
            self.line(
                s,
                stroke,
                (w0 * w0 + (w1 * w1 - w0 * w0) * t).max(0.0).sqrt(),
            );
            at += len;
        }
    }

    /// A dry plot: its ring in the crop's fill with its edge, and its ridged rows `ROW_FT` apart at `theta` (radians), each cut
    /// to the plot by a clip path - the deleted `_draw_furrows`.
    ///
    /// Research:
    ///     furrowed rows - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: every dry plot drawn in ridged rows, `ROW_FT` apart (a GUESS there)
    ///     the furrow's stroke - CONVENTION: a 0.8 ft line at 0.8 opacity, so the rows read under the crop's fill
    pub fn furrowed(
        &mut self,
        ring: &[Pt],
        fill: &str,
        edge: (&str, f64),
        furrow: &str,
        theta: f64,
    ) {
        if ring.len() < 3 {
            return;
        }
        self.polygon(ring, fill, Some(edge));
        #[expect(clippy::cast_precision_loss, reason = "a ring of a few corners")]
        let n = ring.len() as f64;
        let c = (
            ring.iter().map(|p| p.0).sum::<f64>() / n,
            ring.iter().map(|p| p.1).sum::<f64>() / n,
        );
        let reach = ring
            .iter()
            .map(|p| (p.0 - c.0).hypot(p.1 - c.1))
            .fold(0.0, f64::max);
        let (dx, dy) = (theta.cos(), theta.sin());
        self.clips += 1;
        let id = format!("dry{}", self.clips);
        let _ = writeln!(
            self.body,
            r#"<clipPath id="{id}"><path d="{}"/></clipPath>"#,
            path(ring, true)
        );
        let _ = write!(
            self.body,
            r#"<g clip-path="url(#{id})" stroke="{furrow}" stroke-width="0.8" opacity="0.8" fill="none">"#
        );
        let mut off = -reach;
        while off <= reach {
            let (ox, oy) = (c.0 - dy * off, c.1 + dx * off);
            let _ = write!(
                self.body,
                r#"<path d="M{},{} L{},{}"/>"#,
                f(ox - dx * reach),
                f(oy - dy * reach),
                f(ox + dx * reach),
                f(oy + dy * reach)
            );
            off += ROW_FT;
        }
        self.body.push_str("</g>\n");
    }

    /// An ellipse.
    pub fn ellipse(&mut self, c: Pt, rx: f64, ry: f64, fill: &str, stroke: Option<(&str, f64)>) {
        self.grow(&[(c.0 - rx, c.1 - ry), (c.0 + rx, c.1 + ry)], 0.0);
        self.inked();
        let edge = stroke.map_or_else(String::new, |(s, w)| {
            format!(r#" stroke="{s}" stroke-width="{}""#, f(w))
        });
        let _ = writeln!(
            self.body,
            r#"<ellipse cx="{}" cy="{}" rx="{}" ry="{}" fill="{fill}"{edge}/>"#,
            f(c.0),
            f(c.1),
            f(rx),
            f(ry)
        );
    }

    /// Patches of earth (`patches`: each its middle, its two radii along the sheet and its tone) painted at `opacity` on the ground the
    /// `rings` bound and clipped to it - a band between two rings, or each ring's own ground where they lie apart (even-odd) - so
    /// no patch runs past its band's edge: one mark of the kind named, none where there is no patch.
    ///
    /// Research:
    ///     the mottle's drawing - CONVENTION: each patch an ellipse along the sheet's axes under its band's clip, the patches' own strength so those that overlap darken; the deleted village dike's drawing
    pub fn mottled(&mut self, rings: &[&[Pt]], patches: &[(Pt, f64, f64, &str)], opacity: f64) {
        if patches.is_empty() {
            return;
        }
        self.inked();
        self.clips += 1;
        let id = format!("earth{}", self.clips);
        let ground: Vec<String> = rings.iter().map(|r| path(r, true)).collect();
        let _ = writeln!(
            self.body,
            r#"<clipPath id="{id}"><path d="{}" clip-rule="evenodd"/></clipPath>"#,
            ground.join(" ")
        );
        let _ = write!(
            self.body,
            r#"<g clip-path="url(#{id})" fill-opacity="{opacity}">"#
        );
        for &(c, rx, ry, tone) in patches {
            let _ = write!(
                self.body,
                r#"<ellipse cx="{}" cy="{}" rx="{}" ry="{}" fill="{tone}"/>"#,
                f(c.0),
                f(c.1),
                f(rx),
                f(ry)
            );
        }
        self.body.push_str("</g>\n");
    }

    /// A group opened at an opacity; `close` ends it.
    pub fn group(&mut self, opacity: f64) {
        let _ = writeln!(self.body, r#"<g opacity="{opacity}">"#);
    }

    /// The group opened last, closed.
    pub fn close(&mut self) {
        self.body.push_str("</g>\n");
    }

    /// The box of everything drawn, if anything was.
    #[must_use]
    pub fn bbox(&self) -> Option<[f64; 4]> {
        self.bbox
    }

    /// The document, cropped to what was drawn and `margin` feet round it, inside the canvas `w` by `h`.
    ///
    /// Research:
    ///     the ground's color - CONVENTION: the land drawn in `ink::LAND` beneath everything
    #[must_use]
    pub fn finish(&self, w: f64, h: f64, margin: f64) -> String {
        let [x0, y0, x1, y1] = self.bbox.unwrap_or([0.0, 0.0, w, h]);
        let (x0, y0) = ((x0 - margin).max(0.0), (y0 - margin).max(0.0));
        let (x1, y1) = ((x1 + margin).min(w), (y1 + margin).min(h));
        format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"{} {} {} {}\" width=\"{}\" height=\"{}\">\n<defs>{REED_TILE}{REED_BANK_TILE}</defs>\n<rect x=\"0\" y=\"0\" width=\"{}\" height=\"{}\" fill=\"{}\"/>\n{}</svg>\n",
            f(x0),
            f(y0),
            f(x1 - x0),
            f(y1 - y0),
            f(x1 - x0),
            f(y1 - y0),
            f(w),
            f(h),
            ink::LAND,
            self.body
        )
    }
}

#[cfg(test)]
mod tests {
    use super::{ink, Svg, UNNAMED};

    /// A mark drawn before any kind is named is counted unnamed, so a roll's test sees it.
    #[test]
    fn the_census_counts_each_mark_under_its_kind() {
        let mut s = Svg::default();
        s.ellipse((1.0, 1.0), 1.0, 1.0, ink::BEAN, None);
        s.kind("well");
        s.ellipse((1.0, 1.0), 1.0, 1.0, ink::BEAN, None);
        s.ellipse((2.0, 1.0), 1.0, 1.0, ink::BEAN, None);
        let got: Vec<(&str, usize)> = s.census().iter().map(|(k, v)| (k.as_str(), *v)).collect();
        assert_eq!(got, [(UNNAMED, 1), ("well", 2)]);
    }

    #[test]
    fn a_mottle_is_its_patches_clipped_to_their_ground_as_one_mark() {
        let mut svg = Svg::default();
        svg.kind("perimeter dike");
        let ring = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)];
        svg.mottled(&[&ring], &[], 0.4);
        assert!(svg.census().is_empty(), "no patch, no mark");
        svg.mottled(&[&ring], &[((3.0, 2.0), 2.0, 1.0, "#A8895A")], 0.4);
        let drawn = svg.finish(20.0, 20.0, 0.0);
        assert!(drawn.contains(
            r#"<clipPath id="earth1"><path d="M0,0 L10,0 L10,10 Z" clip-rule="evenodd"/>"#
        ));
        assert!(drawn.contains(
            r##"fill-opacity="0.4"><ellipse cx="3" cy="2" rx="2" ry="1" fill="#A8895A"/></g>"##
        ));
        assert_eq!(svg.census().get("perimeter dike"), Some(&1));
    }

    #[test]
    fn the_document_is_cropped_to_what_is_drawn() {
        let mut s = Svg::default();
        assert!(s.bbox().is_none());
        s.polygon(&[(10.0, 10.0), (20.0, 10.0)], ink::RICE_GREEN, None);
        assert!(s.bbox().is_none(), "a ring of two points draws nothing");
        s.polygon(
            &[(10.0, 10.0), (20.0, 10.0), (20.0, 30.0)],
            ink::RICE_GREEN,
            Some((ink::AZE, 1.5)),
        );
        s.line(&[(0.0, 0.0)], ink::SUPPLY, 2.0);
        s.unframed(&[(0.0, 0.0)], ink::SUPPLY, 2.0);
        s.unframed(&[(0.0, 0.0), (90.0, 90.0)], ink::SHEEN, 2.0);
        s.taper(
            &[(10.0, 10.0), (15.0, 10.0), (20.0, 10.0)],
            ink::SUPPLY,
            2.0,
            4.0,
        );
        s.taper(&[(10.0, 10.0), (20.0, 10.0)], ink::DRAIN, 2.0, 2.1);
        s.group(0.5);
        s.ellipse(
            (15.0, 15.0),
            2.0,
            1.0,
            ink::POND_WATER,
            Some((ink::RIM, 1.0)),
        );
        s.ellipse((15.0, 15.0), 1.0, 0.5, ink::SHEEN, None);
        s.close();
        let doc = s.finish(100.0, 100.0, 5.0);
        let mut b = Svg::default();
        b.band(
            &[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)],
            &[(2.0, 2.0), (8.0, 2.0), (8.0, 8.0)],
            "#B79B68",
            ("#9C8150", 1.0),
        );
        b.band(&[(0.0, 0.0)], &[], "#B79B68", ("#9C8150", 1.0));
        assert!(b.finish(20.0, 20.0, 0.0).matches("evenodd").count() == 1);
        let mut d = Svg::default();
        d.furrowed(
            &[(0.0, 0.0), (20.0, 0.0), (20.0, 10.0), (0.0, 10.0)],
            "#C9B57A",
            ("#A98C58", 1.4),
            "#9C8650",
            0.0,
        );
        d.furrowed(
            &[(0.0, 0.0), (1.0, 1.0)],
            "#C9B57A",
            ("#A98C58", 1.4),
            "#9C8650",
            0.0,
        );
        let dd = d.finish(100.0, 100.0, 0.0);
        assert!(dd.contains(r#"<clipPath id="dry1">"#) && !dd.contains("dry2"));
        assert!(dd.matches("<path d=\"M").count() > 4);
        assert!(doc.starts_with("<svg"));
        assert!(doc.contains(r#"viewBox="3.7 3.2 23.1 32.6""#));
        let drawn = doc.split("</defs>").nth(1).unwrap_or_default();
        assert_eq!(drawn.matches("stroke-width=\"").count(), 6);
        let mut r = Svg::default();
        r.reserved(&[(0.0, 0.0), (1.0, 0.0)], "#000", "x");
        assert!(r.bbox().is_none() && r.body.is_empty());
        r.reserved(
            &[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)],
            "#000",
            "the settlement",
        );
        assert!(
            r.bbox() == Some([-2.0, -2.0, 12.0, 12.0])
                && r.body.contains(r#"x="6.7""#)
                && r.body.contains("dasharray")
        );
        r.reeds(&[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]);
        assert!(r.body.contains("url(#reed-ticks)"));
        assert!(r
            .finish(20.0, 20.0, 0.0)
            .contains(r#"<pattern id="reed-ticks""#));
        assert!(Svg::default()
            .finish(50.0, 40.0, 5.0)
            .contains(r#"viewBox="0 0 50 40""#));
    }
}
