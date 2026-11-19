//! The parts written (derivation T208, "Writes"): the bath, the wells with their rolled gear and roofs, the privies and their hatches, the
//! fire-water tubs, the notice board, the shrine's tree, the practice ground's gear and the roji - each with its kind, each declaring its
//! caption.
//!
//! Research: the parts written - NONE: each part drawn as docs/buildings.md's vocabulary draws it, its claims where its seat is decided

use super::emit::{n, px, Svg, POINT, SMALL};
use super::parts::Seated;
use super::spec::Bx;

/// The well's gear drawn over its curb: the sweep's post and pole, or the pulley frame's two posts and beam; and the roof's outline on
/// four posts.
///
/// Research:
///     well glyph - research/questions/0196-communal-wells-ido.drawing.html: a square curb with its lifting gear over it - a sweep or a pulley frame - and a roof drawn as an unfilled outline on four corner posts
fn well(s: &mut Svg, b: Bx, gear: &str, roof: bool) -> String {
    let id = s.id();
    s.rect(b, &format!(r##"fill="#9C8C70" stroke="#5C4830" stroke-width="1.2" data-kind="well" data-id="{id}""##));
    let (cx, cy) = px(f64::midpoint(b.0, b.2), f64::midpoint(b.1, b.3));
    let at = format!("{},{}", n(cx), n(cy));
    if roof {
        let (x0, y0, x1, y1) = (cx - 14.95, cy - 14.95, cx + 14.95, cy + 14.95);
        let post = |x: f64, y: f64| {
            format!(
                r##"<circle cx="{}" cy="{}" r="1.6" fill="#6B5836"/>"##,
                n(x),
                n(y)
            )
        };
        s.put(&format!(
            r##"<g data-kind="well" data-roof="1" data-at="{at}"><path d="M {} {} h 29.9 v 29.9 h -29.9 z" fill="none" stroke="#6B5836" stroke-width="1.1" stroke-dasharray="3 2"/>{}{}{}{}</g>"##,
            n(x0),
            n(y0),
            post(x0, y0),
            post(x0, y1),
            post(x1, y0),
            post(x1, y1)
        ));
    }
    let body = if gear == "sweep" {
        format!(
            r##"<circle cx="{}" cy="{}" r="1.6" fill="#5A3F1E"/><line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#5A3F1E" stroke-width="1.6"/>"##,
            n(cx + 12.95),
            n(cy + 12.95),
            n(cx + 12.95),
            n(cy + 12.95),
            n(cx - 2.54),
            n(cy - 2.54)
        )
    } else {
        format!(
            r##"<circle cx="{}" cy="{}" r="1.6" fill="#5A3F1E"/><circle cx="{}" cy="{}" r="1.6" fill="#5A3F1E"/><line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#5A3F1E" stroke-width="2"/>"##,
            n(cx - 12.95),
            n(cy),
            n(cx + 12.95),
            n(cy),
            n(cx - 12.95),
            n(cy),
            n(cx + 12.95),
            n(cy)
        )
    };
    s.put(&format!(
        r#"<g data-kind="well" data-gear="{gear}" data-at="{at}">{body}</g>"#
    ));
    id
}

/// Every part, in the order the parts were seated.
///
/// Research:
///     each part drawn - CONVENTION: each part drawn as docs/buildings.md's vocabulary draws it - fills, strokes, a tub r 3.8 px, a roji stone an ellipse of radii 3 and 2 px (6 x 4 px), their captions' faces
///     the plan scale - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 3 px = 1 ft, set so drawn compounds fall between Joge and Takayama - the shrine tree's crown drawn at its seated radius in feet times 3 px
pub fn parts(s: &mut Svg, seated: &Seated) {
    if let Some(b) = seated.bath {
        let id = s.id();
        s.rect(b, &format!(r##"fill="#C9A57A" stroke="#6B4F2A" stroke-width="1.5" data-kind="bath" data-id="{id}""##));
        s.caption("bath", "bath", SMALL, &[id]);
    }
    if let Some((x, y, r)) = seated.tree {
        let (cx, cy) = px(x, y);
        s.put(&format!(
            r##"<g data-kind="sacred tree" data-part-of="compound shrine" fill="#7A8C5C" stroke="#3E5230" stroke-width="1.4"><circle cx="{}" cy="{}" r="{}" data-id="shrine-tree"/></g>"##,
            n(cx),
            n(cy),
            n(super::emit::PX * r)
        ));
        s.caption(
            "shrine tree",
            "sacred tree",
            r##"font-size="7" font-style="italic" fill="#3A4A28""##,
            &["shrine-tree".to_owned()],
        );
    }
    practice(s, seated);
    if !seated.roji.is_empty() {
        s.put(r##"<g data-kind="garden"><g fill="#B8B0A0" stroke="#7A7060" stroke-width="0.5">"##);
        for &(x, y) in &seated.roji {
            let (cx, cy) = px(x, y);
            s.put(&format!(
                r#"<ellipse cx="{}" cy="{}" rx="3" ry="2"/>"#,
                n(cx),
                n(cy)
            ));
        }
        if let Some(b) = seated.shoe {
            let id = s.id();
            s.rect(b, &format!(r##"fill="#9C9488" id="shoe-stone" stroke="#5C5448" stroke-width="0.8" data-id="{id}""##));
        }
        s.put("</g></g>");
    }
    for w in &seated.wells {
        let id = well(s, w.bx, &w.gear, w.roof);
        s.caption(
            "well",
            "well",
            r##"font-size="8" font-style="italic" fill="#3A2E1C""##,
            &[id],
        );
    }
    for pr in &seated.privies {
        let id = s.id();
        let of = if pr.house {
            r#" data-part-of="residence""#
        } else {
            ""
        };
        s.rect(pr.bx, &format!(r##"fill="#7E726A" stroke="#4A3318" stroke-width="0.8" data-kind="latrine"{of} data-id="{id}""##));
        if let Some(h) = pr.hatch {
            let hid = s.id();
            s.rect(h, &format!(r##"fill="#4A3318" stroke="none" stroke-width="0" data-kind="latrine" data-id="{hid}""##));
        }
        s.caption("latrine", "latrine", POINT, &[id]);
    }
    if !seated.tubs.is_empty() {
        s.put(
            r##"<g fill="#8FB0C6" stroke="#3A5060" stroke-width="1" data-kind="fire-water tubs">"##,
        );
        let mut ids = Vec::new();
        for (k, &(x, y)) in seated.tubs.iter().enumerate() {
            let (cx, cy) = px(x, y);
            s.put(&format!(
                r#"<circle cx="{}" cy="{}" r="3.8" data-id="tub-{k}"/>"#,
                n(cx),
                n(cy)
            ));
            ids.push(format!("tub-{k}"));
        }
        s.put("</g>");
        s.caption(
            "fire-water tubs",
            "fire-water tubs",
            r##"font-size="7" font-style="italic" fill="#3A5060""##,
            &ids,
        );
    }
    if let Some(b) = seated.board {
        let id = s.id();
        s.rect(b, &format!(r##"fill="#4A3318" stroke="#2D2A24" stroke-width="0.6" data-kind="notice board" data-id="{id}""##));
        s.caption("notice board", "notice board", POINT, &[id]);
    }
}

/// The practice ground's rack and striking posts, in the ground's group.
///
/// Research:
///     the practice ground drawn - CONVENTION: the rack's dark-wood fill, the striking posts as r 2 px markers, the caption's face
fn practice(s: &mut Svg, seated: &Seated) {
    if seated.rack.is_none() && seated.posts.is_empty() {
        return;
    }
    s.put(r#"<g data-kind="practice ground">"#);
    if let Some(b) = seated.rack {
        let id = s.id();
        s.rect(b, &format!(r##"fill="#8C6F3E" stroke="#4A3318" stroke-width="0.8" data-kind="weapon rack" data-id="{id}""##));
    }
    let mut ids = Vec::new();
    for (k, &(x, y)) in seated.posts.iter().enumerate() {
        let (cx, cy) = px(x, y);
        s.put(&format!(
            r##"<circle cx="{}" cy="{}" r="2" fill="#7A5430" stroke="#4A3318" stroke-width="0.8" data-kind="striking posts" data-id="post-{k}"/>"##,
            n(cx),
            n(cy)
        ));
        ids.push(format!("post-{k}"));
    }
    s.put("</g>");
    if !ids.is_empty() {
        s.caption(
            "striking posts",
            "striking posts",
            r##"font-size="8" font-style="italic" fill="#5C4830""##,
            &ids,
        );
    }
}
