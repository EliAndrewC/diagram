//! The sheets the checks' lockstep runs beside the pool's and the red fixtures (feature 449 T175): each a form those do not draw - a map
//! declaration's every manifest shape and refusal, a check's other branch, a report's empty sections - written with its notes and
//! manifest into the test's own directory and run through the Python and this port alike, so no expected value here is derived by hand.
//! A sheet's name gives its tier as the red fixtures' do (`ochiba-` a magistracy, `hoshigaoka-` a country shrine, `plain-` none); one
//! named `-refused-` is one the report refuses on both sides.
//!
//! Research:
//!     the checks' fixture sheets - NONE: test sheets, deciding nothing about a building

use std::path::{Path, PathBuf};

/// The precinct every fixture stands on, unless it draws its own.
const PRECINCT: &str = r#"<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="inner court"/>"#;

/// A walled yard: an opening too narrow, one too wide, one a building spans, a divider with its gate, the hearing court on the far side
/// of it from the main gate, a door floating in its building, tubs adrift and by a kura alone, no privy, a compass, a key and a rose.
const YARD: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="inner court"/>
<g stroke="#2D2A24" stroke-width="9" stroke-linecap="square">
<line x1="20" y1="20" x2="100" y2="20"/><line x1="110" y1="20" x2="380" y2="20"/>
<line x1="20" y1="280" x2="150" y2="280"/><line x1="220" y1="280" x2="380" y2="280"/>
<line x1="20" y1="20" x2="20" y2="120"/><line x1="20" y1="150" x2="20" y2="280"/>
<line x1="380" y1="20" x2="380" y2="100"/><line x1="380" y1="180" x2="380" y2="280"/>
</g>
<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="150" x2="200" y2="150"/><line x1="230" y1="150" x2="380" y2="150"/></g>
<rect x="370" y="100" width="26" height="85" fill="#C9A57A" data-kind="gatehouse"/>
<rect x="10" y="10" width="40" height="40" fill="#C9A57A" data-kind="barracks"/>
<rect x="40" y="40" width="120" height="60" fill="#DDB87A" data-kind="residence"/>
<rect x="60" y="60" width="8" height="8" fill="#2D2A24" data-kind="door"/>
<rect x="300" y="40" width="40" height="30" fill="#F2EFE4" data-kind="storehouse"/>
<rect x="250" y="200" width="60" height="40" fill="url(#oshirasu-sand)"/>
<g data-kind="main gate"><rect x="14" y="125" width="12" height="6"/><rect x="14" y="145" width="12" height="6"/></g>
<g fill="#8FB0C6"><circle cx="345" cy="55" r="3"/><circle cx="200" cy="240" r="4"/><circle cx="100" cy="70" r="4"/></g>
<rectangle x="1" y="1" width="2" height="2"/>
<gid="x"><line x1="1" y1="1" x2="2" y2="2"/></gid>
<g data-id="landing-steps"><circle cx="1" cy="1" r="1"/></g>
<rect x="100" y="230" width="20" height="40" fill="#9C8C70" data-kind="revetment"/>
<rect x="0" y="230" width="50" height="40" fill="#8FB0C6" data-kind="river"/>
<text x="200" y="12" font-size="14" font-weight="bold">THE YARD</text>
<text x="390" y="295" font-size="9">N</text><text x="30" y="295" font-size="9">Key:</text>
<g id="compass-rose"><circle cx="5" cy="5" r="2"/></g>
<path d="M 30 30 A 5 5 0 0 1 40 40 L 45 45" stroke="#000" stroke-width="2" fill="none"/>
</svg>
"##;

/// Steps past a revetment the river lies west of, a torii drawn as a silhouette, a road with a repeated point that ends at an arch and at
/// a well, a stable's stalls, a well's gear in each wrong form, two compound shrines and a crown of none.
const GROUNDS: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="outer court"/>
<rect x="100" y="230" width="20" height="40" fill="#9C8C70" data-kind="revetment"/>
<rect x="0" y="230" width="50" height="40" fill="#8FB0C6" data-kind="river"/>
<g data-id="landing-steps"><rect x="90" y="240" width="15" height="10" fill="#9C8C70"/></g>
<g data-kind="torii"><rect x="150" y="30" width="20" height="4"/></g>
<rect x="200" y="30" width="12" height="12" id="arch" fill="#8C6F3E"/>
<g data-kind="road" stroke="#B8A27A" stroke-width="12" fill="none"><path d="M 206 36 L 206 36 L 260 90 L 300 100"/>
<line x1="350" y1="250" x2="370" y2="250"/></g>
<text x="10" y="200">plain</text>
<rect x="295" y="95" width="20" height="20" fill="#9C8C70" data-kind="well"/>
<g data-kind="well" data-gear="beam pulley" data-at="305,105"><line x1="300" y1="105" x2="310" y2="105"/></g>
<g data-kind="well" data-roof="1" data-at="305,105"><rect x="294" y="94" width="22" height="22" fill="#8C6F3E"/></g>
<rect x="40" y="120" width="60" height="50" fill="#C9A57A" data-kind="kitchen"/>
<rect x="55" y="130" width="20" height="20" fill="#9C8C70" data-kind="well"/>
<g data-kind="well" data-gear="sweep" data-at="65,140"><line x1="60" y1="140" x2="70" y2="140"/></g>
<g data-kind="well" data-roof="1" data-at="65,140"><rect x="54" y="129" width="22" height="22" fill="none"/></g>
<rect x="330" y="200" width="20" height="20" fill="#9C8C70" data-kind="well"/>
<g data-kind="well" data-roof="1" data-at="340,210"><circle cx="331" cy="201" r="1"/><circle cx="349" cy="201" r="1"/><circle cx="331" cy="219" r="1"/><circle cx="349" cy="219" r="1"/><path d="M 330 200 H 350 V 220 H 330 Z" fill="none"/></g>
<rect x="240" y="200" width="20" height="20" fill="#9C8C70" data-kind="well"/>
<g data-kind="well" data-gear="pulley frame" data-at="250,210"><line x1="245" y1="210" x2="255" y2="210"/></g>
<g data-kind="stables"><rect x="130" y="150" width="60" height="60" fill="#C9A57A" stroke="#6B4F2A"/>
<line x1="130" y1="168" x2="190" y2="168" stroke="#6B4F2A"/><line x1="130" y1="186" x2="190" y2="186" stroke="#6B4F2A"/></g>
<g data-kind="stables"><rect x="200" y="150" width="30" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<line x1="210" y1="150" x2="210" y2="190" stroke="#6B4F2A"/></g>
<g data-kind="compound shrine"><rect x="260" y="140" width="20" height="16" fill="#C9876C"/></g>
<g data-kind="compound shrine"><rect x="290" y="140" width="10" height="10" fill="#C9876C"/>
<circle cx="200" cy="60" r="8" fill="#7A8C5C" data-kind="sacred tree"/></g>
<text x="200" y="14" font-size="14" font-weight="bold">THE GROUNDS</text>
</svg>
"##;

/// The country shrine's declared features out of place: the sanctuary before the hall and off the axis, the arch inside and off the
/// approach, the well on the approach, a fence about the hall, a wall at the edge, the hall between the dwelling's rooms, two trees as one.
const SHRINE: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="40" y="140" width="300" height="20" fill="url(#keiko-earth)"/>
<rect id="hall" x="120" y="60" width="150" height="50" fill="#DDB87A"/>
<g data-part-of="hall and dwelling"><g data-kind="kitchen"><rect x="120" y="60" width="30" height="50" fill="#DDB87A"/></g>
<g data-kind="the monk's rooms"><rect x="240" y="60" width="30" height="50" fill="#DDB87A"/></g></g>
<rect id="sanctuary" x="100" y="120" width="20" height="20" fill="#C9876C"/>
<rect id="arch" x="200" y="200" width="10" height="10" fill="#8C6F3E"/>
<rect id="well" x="60" y="145" width="10" height="10" fill="#9C8C70"/>
<g id="fence"><line x1="110" y1="50" x2="280" y2="50"/><line x1="110" y1="50" x2="110" y2="120"/><line x1="280" y1="50" x2="280" y2="120"/><line x1="110" y1="120" x2="280" y2="120"/></g>
<g stroke="#2D2A24" stroke-width="9"><line x1="20" y1="280" x2="380" y2="280"/></g>
<circle cx="320" cy="60" r="10" fill="#7A8C5C"/><circle cx="321" cy="60" r="10" fill="#7A8C5C"/>
<text x="200" y="14" font-size="14" font-weight="bold">THE SHRINE</text>
</svg>
"##;

/// A kitchen garden half-shaded by a building and walls, and a half-shade bed that only trees shade.
const GARDEN: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect x="60" y="100" width="40" height="30" fill="url(#vegetable-rows)" data-kind="vegetable garden"/>
<rect x="44" y="104" width="16" height="16" fill="#C9A57A" data-kind="stables"/>
<rect x="30" y="40" width="100" height="62" fill="#DDB87A" data-kind="residence"/>
<path d="M 330 30 A 5 5 0 0 1 340 40 L 345 45" stroke="#000" stroke-width="2" fill="none"/>
<rect x="102" y="100" width="20" height="20" fill="#C9A57A" data-kind="bath"/>
<rect x="40" y="132" width="9" height="9" fill="#7E726A" data-kind="latrine"/>
<rect x="200" y="100" width="40" height="30" fill="url(#vegetable-rows)" data-kind="vegetable garden" data-bed="half-shade"/>
<circle cx="220" cy="90" r="9" fill="#7A8C5C"/><circle cx="250" cy="115" r="9" fill="#7A8C5C"/>
<rect x="260" y="160" width="40" height="30" fill="url(#vegetable-rows)" data-kind="vegetable garden" data-bed="half-shade"/>
<rect x="240" y="120" width="80" height="38" fill="#DDB87A" data-kind="kitchen"/>
<rect x="330" y="120" width="20" height="20" fill="#DDB87A" data-kind="kitchen"/>
<g stroke="#2D2A24" stroke-width="9"><line x1="300" y1="190" x2="380" y2="190"/></g>
<rect x="320" y="240" width="10" height="10" fill="url(#vegetable-rows)" data-kind="vegetable garden"/>
<text x="200" y="14" font-size="14" font-weight="bold">THE GARDEN</text>
</svg>
"##;

/// A half-shade bed only trees shade, its hours counted with no shadow at all.
const SHADE: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect x="200" y="100" width="40" height="30" fill="url(#vegetable-rows)" data-kind="vegetable garden" data-bed="half-shade"/>
<circle cx="220" cy="90" r="9" fill="#7A8C5C"/>
</svg>
"##;

/// The country shrine on a north-south approach: the sanctuary nearer the arch than the hall, the hall standing on its end with its
/// dwelling's rooms all but meeting, and a compound wall within the precinct.
const SHRINE_UPRIGHT: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="40" width="20" height="240" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="60" width="40" height="120" fill="#DDB87A"/>
<g data-part-of="hall and dwelling"><g data-kind="kitchen"><rect x="150" y="60" width="40" height="60" fill="#DDB87A"/></g>
<g data-kind="the monk's rooms"><rect x="150" y="125" width="40" height="55" fill="#DDB87A"/></g></g>
<rect id="sanctuary" x="190" y="200" width="20" height="20" fill="#C9876C"/>
<rect id="arch" x="190" y="270" width="20" height="10" fill="#8C6F3E"/>
<g stroke="#2D2A24" stroke-width="9"><line x1="100" y1="150" x2="140" y2="150"/></g>
<text x="200" y="14" font-size="14" font-weight="bold">UPRIGHT</text>
</svg>
"##;

/// The ink's four extremes, each set by one element `ElementTree` reads its own way: a caption of `<tspan>`s with the space between them
/// and an entity, captions anchored at their middle and end, an ellipse, a translated group.
fn ink(extreme: &str) -> String {
    format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="100" y="100" width="200" height="100" fill="url(#court-earth)"/>
{extreme}
</svg>
"#
    )
}

/// A sheet whose viewBox `float()` refuses.
const BAD_VIEWBOX: &str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="1.2.3 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<g data-kind="road" stroke-width="6"><line x1="30" y1="30" x2="60" y2="60"/></g>
</svg>
"#;

/// A precinct the ink is all of (the crop's "nothing drawn"), its grid empty of buildings.
const BARE: &str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<rect id="precinct" x="0" y="0" width="100" height="100" fill="url(#court-earth)"/>
</svg>
"#;

/// A divider unbroken, a vertical one, a hearing court with no gate in the wall: the zoning's other refusals, one sheet each.
fn zoning(divider: &str, court: bool, wall: &str) -> String {
    format!(
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
{PRECINCT}
<g stroke="#3F3A30" stroke-width="6">{divider}</g>
{}
<g stroke="#2D2A24" stroke-width="9" stroke-linecap="square">{wall}</g>
<text x="200" y="14" font-size="14" font-weight="bold">ZONES</text>
</svg>
"##,
        if court {
            r#"<rect x="250" y="200" width="60" height="40" fill="url(#court-cobbles)"/>"#
        } else {
            ""
        }
    )
}

/// The map declaration's sheet: a precinct the subject, a road out of it, trees, a well and an arch outside it, a manifest key mistaken
/// for an id, and the main gate's posts.
const MAPPED: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="100" y="100" width="200" height="100" fill="url(#court-earth)"/>
<g data-kind="main gate"><rect x="190" y="194" width="6" height="12"/><rect x="214" y="194" width="6" height="12"/></g>
<g data-kind="road" stroke="#B8A27A" stroke-width="12" fill="none"><path d="M 205 200 L 205 290 L 390 290"/></g>
<circle cx="40" cy="40" r="9" fill="#7A8C5C"/><circle cx="360" cy="40" r="9" fill="#7A8C5C"/>
<rect id="well" x="40" y="250" width="10" height="10" fill="#9C8C70"/>
<rect id="arch" x="200" y="230" width="12" height="12" fill="#8C6F3E"/>
<rect id="houses" x="330" y="230" width="20" height="20" fill="#DDB87A"/>
<rect id="building" x="20" y="120" width="30" height="30" fill="#DDB87A"/>
<g stroke="#2D2A24" stroke-width="9"><line x1="110" y1="150" x2="130" y2="150"/></g>
<text x="200" y="14" font-size="14" font-weight="bold">MAPPED</text>
</svg>
"##;

/// A manifest the mapped sheet agrees with: the subject's place, size and gate, and a lane under its road.
const AGREED: &str = r#"{"meta": {"ftpx": 1.0},
 "religious": ["junk", {"cx": 1, "cy": 1}, {"x": 900, "y": 900}, {"x": 500, "y": 500, "w": 67, "h": 33, "gate": [502, 517], "gate_dir": "S", "gate_w": 6}],
 "lane": [[501.67, 516], [501.67, 547], [564, 547]]}"#;

/// Numbers `json.load` reads that a double does not hold, a pond of two numbers and a record of no shape.
const KEPT: &str = r#"{"meta": {"ftpx": 1.0},
 "religious": [{"x": 500, "y": 500, "w": 67, "h": 33}],
 "houses": [{"x": 545, "y": 545, "w": NaN, "h": 123456789012345678901234567890}],
 "pond": [1, 2], "streams": [{"z": 1}], "wells": [{"cx": 1e400, "cy": -1e400}]}"#;

/// The manifest the mapped sheet declares: the subject at (500, 500) at 1 ft a px, with a gate, every recorded shape a class reads.
const MANIFEST: &str = r#"{
 "meta": {"ftpx": 1.0},
 "religious": [{"x": 510, "y": 505, "w": 60, "h": 40, "gate": [600, 600], "gate_dir": "north", "gate_w": "4"}, "not a record"],
 "tree_crowns": [460.0, 460.0, 3.0, 700.0, 700.0, 2.0, 1.0],
 "village_groves": [{"clumps": [[540, 460], [9]], "r": 2}, {"r": "3"}, 7],
 "torii": [[502, 548], "x"],
 "lane": [[501, 530], [501, 560], [560, 563]],
 "roads": [{"pts": [[480, 520], [480, 520], [480, 600]]}, {"poly": [[1, 1]]}],
 "road": [],
 "pond": [470, 470, 4, 4],
 "streams": [{"cx": 455, "cy": 545, "r": true}, {"x": 520, "y": 470, "w": 0, "h": 0}, {"x": 499, "y": 540, "w": 5, "h": 5}],
 "wells": [{"cx": 449.0, "cy": 551.0}],
 "houses": [{"x": 545, "y": 545, "w": 6, "h": 6}],
 "cemeteries": [{"pts": [[400, 400], [400, 400], [420, 420]]}]
}"#;

/// Each fixture: its file name, its sheet, its notes (`{MANIFEST}` the path of its manifest) and its manifest.
#[expect(clippy::too_many_lines, reason = "the fixtures' one list")]
fn fixtures() -> Vec<(String, String, Option<String>, Option<String>)> {
    let notes = |line: &str| Some(format!("# notes\n\n**Form**: one roof\n{line}\n"));
    let map_notes = |key: &str, at: &str, id: &str| {
        notes(&format!(
            "**On map**: {{MANIFEST}} - {key} at {at} = `{id}`"
        ))
    };
    let manifest = |text: &str| Some(text.to_owned());
    let mut out = vec![
        ("ochiba-check-yard.svg".to_owned(), YARD.to_owned(), notes("**Form**: two roofs"), None),
        ("plain-check-yard.svg".to_owned(), YARD.to_owned(), None, None),
        ("plain-check-grounds.svg".to_owned(), GROUNDS.to_owned(), None, None),
        ("ochiba-check-grounds.svg".to_owned(), GROUNDS.to_owned(), None, None),
        ("hoshigaoka-check-shrine.svg".to_owned(), SHRINE.to_owned(), notes("**On map**: none - apart"), None),
        ("plain-check-garden.svg".to_owned(), GARDEN.to_owned(), None, None),
        ("plain-check-shade.svg".to_owned(), SHADE.to_owned(), None, None),
        ("plain-check-ink-tspans.svg".to_owned(),
         ink(r#"<text x="150" y="40" font-size="12"><tspan x="150">Gate &amp; yard</tspan> <tspan x="150" dy="12">the  &#233;t&#233;   way</tspan></text>"#),
         None, None),
        ("plain-check-ink-anchors.svg".to_owned(),
         ink(r#"<text x="390" y="290" font-size="14" text-anchor="end">East</text><text x="105" y="295" text-anchor="middle">West wing</text>"#),
         None, None),
        ("plain-check-ink-ellipse.svg".to_owned(), ink(r##"<ellipse cx="30" cy="150" rx="12" ry="40" fill="#8FB0C6"/>"##), None, None),
        ("plain-check-ink-group.svg".to_owned(),
         ink(r##"<g transform="translate(250, 150)"><g transform="translate(100)"><rect x="10" y="10" width="20" height="20" fill="#DDB87A"/></g></g>"##),
         None, None),
        ("hoshigaoka-check-upright.svg".to_owned(), SHRINE_UPRIGHT.to_owned(), None, None),
        ("ochiba-check-tiny.svg".to_owned(),
         r#"<svg viewBox="0 0 50 50"><rect id="precinct" x="10" y="10" width="30" height="30" fill="url(#court-earth)"/></svg>"#.to_owned(), None, None),
        ("plain-check-refused-divider.svg".to_owned(), format!(
            r##"<svg viewBox="0 0 50 50"><rect id="precinct" x="10" y="10" width="30" height="30" fill="url(#court-earth)"/><g stroke="#3F3A30" stroke-width="6"><line x1="{}" y1="20" x2="5" y2="20"/></g></svg>"##,
            "1".repeat(400)), None, None),
        ("plain-check-refused-line.svg".to_owned(), format!(
            r##"<svg viewBox="0 0 50 50"><rect id="precinct" x="10" y="10" width="30" height="30" fill="url(#court-earth)"/><g stroke="#3F3A30" stroke-width="6"><line x1="{0}" y1="20" x2="{0}" y2="50"/></g></svg>"##,
            "1".repeat(400)), None, None),
        ("plain-check-refused-noprecinct.svg".to_owned(), r#"<svg><rect x="1" y="1" width="2" height="2"/></svg>"#.to_owned(), None, None),
        ("plain-check-refused-viewbox.svg".to_owned(), BAD_VIEWBOX.to_owned(), None, None),
        ("ochiba-check-bare.svg".to_owned(), BARE.to_owned(), None, None),
        ("plain-check-refused-zero.svg".to_owned(),
         r#"<svg><rect id="precinct" x="20" y="20" width="-5" height="9" fill="url(#court-earth)"/></svg>"#.to_owned(), None, None),
        ("plain-check-refused-notes.svg".to_owned(), BARE.to_owned(), notes("**On map**: somewhere"), None),
        ("plain-check-unbroken.svg".to_owned(), zoning(r#"<line x1="20" y1="150" x2="380" y2="150"/>"#, true, ""), None, None),
        ("plain-check-nocourt.svg".to_owned(),
         zoning(r#"<line x1="20" y1="150" x2="200" y2="150"/><line x1="230" y1="150" x2="380" y2="150"/>"#, false, ""), None, None),
        ("plain-check-nogate.svg".to_owned(),
         zoning(r#"<line x1="20" y1="150" x2="200" y2="150"/><line x1="230" y1="150" x2="380" y2="150"/>"#, true,
                r#"<line x1="20" y1="20" x2="380" y2="20"/>"#), None, None),
        ("plain-check-vertical.svg".to_owned(),
         zoning(r#"<line x1="200" y1="20" x2="200" y2="120"/><line x1="200" y1="150" x2="200" y2="280"/>"#, true,
                r#"<line x1="20" y1="20" x2="100" y2="20"/><line x1="130" y1="20" x2="380" y2="20"/>"#), None, None),
        ("plain-check-near.svg".to_owned(),
         zoning(r#"<line x1="20" y1="150" x2="200" y2="150"/><line x1="230" y1="150" x2="380" y2="150"/>"#, true,
                r#"<line x1="20" y1="280" x2="100" y2="280"/><line x1="130" y1="280" x2="380" y2="280"/>"#), None, None),
    ];
    // the map declaration: a manifest the sheet agrees with in part, and each refusal and silence of it
    let maps: [(&str, &str, &str, &str, &str); 17] = [
        ("map", "religious", "(500, 500)", "precinct", MANIFEST),
        ("map-agreed", "religious", "(500, 500)", "precinct", AGREED),
        ("map-kept", "religious", "(500, 500)", "precinct", KEPT),
        (
            "map-circle",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"cx": 500, "cy": 500, "r": 5}]}"#,
        ),
        (
            "map-short",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500, "gate": [1], "gate_dir": "up"}]}"#,
        ),
        (
            "map-dir",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500, "gate_dir": 7}]}"#,
        ),
        ("map-nofile", "religious", "(500, 500)", "precinct", ""),
        (
            "map-noscale",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 0}, "religious": []}"#,
        ),
        (
            "map-nosubject",
            "religious",
            "(900, 900)",
            "precinct",
            MANIFEST,
        ),
        ("map-noid", "religious", "(500, 500)", "hall", MANIFEST),
        (
            "map-nometa",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"religious": [{"x": 500, "y": 500}]}"#,
        ),
        (
            "refused-map-meta",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": [1]}"#,
        ),
        (
            "refused-map-list",
            "religious",
            "(500, 500)",
            "precinct",
            "[1, 2]",
        ),
        (
            "refused-map-float",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500, "w": 9}], "wells": [{"x": "abc", "y": 1}]}"#,
        ),
        (
            "refused-map-key",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500}], "wells": [{"cx": 1}]}"#,
        ),
        (
            "refused-map-iter",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500}], "village_groves": [{"clumps": 3}]}"#,
        ),
        (
            "refused-map-none",
            "religious",
            "(500, 500)",
            "precinct",
            r#"{"meta": {"ftpx": 1}, "religious": [{"x": 500, "y": 500}], "tree_crowns": [null, 1, 2]}"#,
        ),
    ];
    for (name, key, at, id, json) in maps {
        out.push((
            format!("hoshigaoka-check-{name}.svg"),
            MAPPED.to_owned(),
            map_notes(key, at, id),
            (!json.is_empty()).then(|| manifest(json)).flatten(),
        ));
    }
    // a sheet with no main gate, its record a gate
    out.push((
        "hoshigaoka-check-map-nogate.svg".to_owned(),
        MAPPED.replace(r#"<g data-kind="main gate"><rect x="190" y="194" width="6" height="12"/><rect x="214" y="194" width="6" height="12"/></g>"#, ""),
        map_notes("religious", "(500, 500)", "precinct"),
        manifest(AGREED),
    ));
    // a road wholly within the subject: no sample of it is compared
    out.push((
        "hoshigaoka-check-map-inside.svg".to_owned(),
        MAPPED.replace(
            r#"<path d="M 205 200 L 205 290 L 390 290"/>"#,
            r#"<path d="M 150 120 L 250 120"/>"#,
        ),
        map_notes("religious", "(500, 500)", "precinct"),
        manifest(AGREED),
    ));
    // a sheet with no viewBox, its declaration laid on nothing
    out.push((
        "hoshigaoka-check-map-noview.svg".to_owned(),
        MAPPED.replace(r#" viewBox="0 0 400 300""#, ""),
        map_notes("religious", "(500, 500)", "precinct"),
        manifest(MANIFEST),
    ));
    // (T177, T182) the sheets of step 1's defect fixes
    for (name, svg) in super::fix_fixtures::sheets() {
        out.push((name.to_owned(), svg.to_owned(), None, None));
    }
    out
}

/// Writes every check fixture (its sheet, and its notes and manifest where it has them) into `dir`; the sheets' paths.
pub fn write(dir: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for (name, svg, notes, manifest) in fixtures() {
        let path = dir.join(&name);
        let stem = name.trim_end_matches(".svg");
        let json = dir.join(format!("{stem}.json"));
        std::fs::write(&path, svg).unwrap();
        if let Some(text) = manifest {
            std::fs::write(&json, text).unwrap();
        }
        if let Some(text) = notes {
            let text = text.replace("{MANIFEST}", &json.to_string_lossy());
            std::fs::write(dir.join(format!("{stem}.notes.md")), text).unwrap();
        }
        out.push(path);
    }
    out
}
