//! The sheets the lockstep runs beside the pool's (feature 449 T170): each a form the pool's six sheets do not draw - a rotated or
//! wrapped caption, a rectilinear path, a translated glyph, a non-ASCII text before the ink (the offsets), and every refusal - run
//! through the Python and this port alike, so no expected value here is derived by hand.
//!
//! Research:
//!     the lockstep's fixture sheets - NONE: test sheets, deciding nothing about a building

/// A sheet with every reader's form on it, wrapped in `<svg>` with a precinct.
const FULL: &str = r##"<?xml version="1.0"?>
<!-- the author's note -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<defs><pattern id="p"><circle cx="1" cy="1" r="5" fill="#7A8C5C"/></pattern></defs>
<rect id="precinct" x="10" y="10" width="380" height="280" fill="url(#court-earth)"/>
<rect x="20" y="20" width="60" height="40" fill="#DDB87A" data-kind="office hall"/>
<rect x="25" y="25" width="20" height="10" fill="#DDB87A"/>
<rect x="100" y="20" width="10" height="10" fill="#2D2A24"/>
<rect x="120" y="20" width="10" height="10" fill="#2D2A24" data-kind="hearth"/>
<rect x="140" y="20" width="10" height="x" fill="#2D2A24"/>
<rect fill="#C9A57A" height="30" width="40" y="200" x="300"/>
<rect x="160" y="20" width="12" height="12" fill="#9C8C70" data-kind="well"/>
<rect x="180" y="20" width="12" height="12" fill="url(#garden-stipple)"/>
<rect x="200" y="200" width="50" height="50" fill="url(#oshirasu-sand)" stroke="#5A3F1E"/>
<g data-kind="main gate"><rect x="10" y="150" width="4" height="8"/><rect x="10" y="170" width="4" height="8" fill="#2D2A24"/></g>
<g data-kind="latrine"><rect x="60" y="100" width="8" height="8" fill="#7E726A"/><rect x="70" y="100" width="8" height="8" fill="#000"/></g>
<rect x="80" y="100" width="8" height="8" fill="#7E726A" data-part-of="latrine" data-kind="privy hatch"/>
<path d="M 200 20 L 260 20 L 260 80 L 230 80 L 230 50 L 200 50 Z" fill="url(#vegetable-rows)" id="garden"/>
<path d="M 300 20 H 360 V 80 H 300 Z M 310 30 V 70 H 350 V 30 Z" fill="#E8D2A8"/>
<path d="M 0 0 C 1 1 2 2 3 3" fill="#E8D2A8"/>
<path d="M 0 0 L 5 5 L 0 5 Z" fill="#E8D2A8"/>
<path d="M 0 0 L 5 0" fill="none"/>
<path d="10 10 20 10 20 20 10 20" fill="#E8D2A8"/>
<g id="trees"><circle cx="50" cy="250" r="9"/><circle cx="70" cy="250" r="2"/></g>
<circle cx="90" cy="250" r="7" fill="#7A8C5C"/>
<g fill="#7A8C5C"><circle cx="110" cy="250" r="6"/></g>
<circle cx="130" cy="250" r="5"/>
<circle cx="140" cy="250" r="3"/>
<ellipse cx="150" cy="250" rx="4" ry="2"/>
<g fill="#8FB0C6"><circle cx="160" cy="250" r="3"/><circle cx="170" cy="250" r="3"/></g>
<g stroke="#3F3A30" stroke-width="3"><line x1="10" y1="120" x2="200" y2="120"/></g>
<g stroke="#2D2A24" stroke-width="4" stroke-linecap="square"><line x1="10" y1="10" x2="10" y2="290"/><line x1="10" y1="10" x2="390" y2="12"/></g>
<line x1="390" y1="10" x2="390" y2="290" stroke="#2D2A24" stroke-width="2"/>
<g/>
<g id="fence"><line x1="5" y1="5" x2="5" y2="50"/></g>
<g transform="translate(100, 50)" data-kind="board"><rect x="1" y="2" width="3" height="4" fill="#C9876C"/><line x1="0" y1="0" x2="3" y2="4"/><polyline points="1,1 2,5 3"/><polygon points=""/><path d="m 1 1 l 2 2 H 9 V 7 Q 1 1 4 4 L 5"/></g>
<g transform="translate(3)"><circle cx="1" cy="1" r="1" data-kind="dot"/><ellipse cx="1" cy="1" rx="2" ry="1"/></g>
<text x="50" y="60" font-size="10">Office &amp; Hall</text>
<text x="50" y="80" font-size="12" font-weight="bold" text-anchor="middle">INNER COURT</text>
<text x="50" y="90" font-size="12" font-weight="bold" text-anchor="end" letter-spacing="1.5">Tatsuya's quarters</text>
<text x="50" y="100" font-size="9" font-weight="bold">12 34</text>
<text x="200" y="150" font-size="10"><tspan x="200" dy="0">INNER</tspan><tspan x="200" dy="11.1">COURT</tspan><tspan x="200" dy="0.2">YARD</tspan></text>
<text x="200" y="170" font-size="10"><tspan x="200">one</tspan> <tspan dy="3">two</tspan></text>
<text x="200" y="180" font-size="10"><tspan x="200">one</tspan>tail<tspan x="200">two</tspan></text>
<text x="300" y="150" font-size="10" transform="rotate(90 300 150)">River</text>
<text x="300" y="170" font-size="10" transform="rotate(-90, 300, 170)">River</text>
<text x="300" y="190" font-size="10" transform="rotate(45 300 190)">Askew</text>
<text y="5">no x</text>
<text x="1" y="5">   </text>
<text data-kind="caption" font-size="10">declared</text>
<rectangle x="1" y="1" width="1" height="1" fill="#DDB87A"/><rect/><rect></rect>
<pathology d="M 0 0 H 4 V 4 H 0 Z" fill="#E8D2A8"/>
<circles cx="1" cy="1" r="9" fill="#7A8C5C"/><circle/>
<linear x1="1" y1="1" x2="2" y2="2" stroke="#2D2A24"/>
<g/><g stroke="#2D2A24"/><line x1="0" y1="0" x2="5" y2="0"/>
<g̃ id="trees"><circle cx="5" cy="5" r="5"/></g̃>
<gid="fence"><line x1="5" y1="5" x2="5" y2="50"/></gid>
<g id="fence"><line x1="7" y1="5" x2="7" y2="50"/></g>
<g fill="#7A8C5C" id="trees"><circle cx="9" cy="9" r="9"/></g>
<circle cx="200" cy="280" r="4" fill="#7A8C5C"/><circle cx="210" cy="280" r="4"/><circle cx="220" cy="280" r="3.99" fill="#7A8C5C"/>
<rect x="20" y="260" width="25" height="20" fill="#C9876C"/><rect x="50" y="260" width="24.9" height="20" fill="#C9876C"/>
<rect x="80" y="260" width="25" height="10" fill="#1A1410"/><rect x="110" y="260" width="24.9" height="10" fill="#1A1410"/>
<text x="10" y="200" font-size="10" font-weight="bold">ABCDe</text><text x="10" y="210" font-size="10" font-weight="bold">ABCde</text>
<text x="300" y="210" font-size="10" transform="rotate(89 300 210)">Edge</text><text x="300" y="220" font-size="10" transform="rotate(90.5 300 220)">Edge</text><text x="300" y="230" font-size="10" transform="rotate(91 300 230)">Edge</text>
<g data-kind="grove"><defs data-kind="d"><pattern id="q"><rect x="0" y="0" width="1" height="1"/></pattern></defs></g>
<defs></defs><defsx><circle cx="3" cy="3" r="8" fill="#7A8C5C"/></defsx>
</svg>
"##;

/// The fixtures: a name and a sheet each.
pub const SHEETS: [(&str, &str); 25] = [
    ("full", FULL),
    (
        "non-ascii before the ink",
        "<svg><text x=\"1\" y=\"2\">\u{6c34} \u{91ce}</text><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><g data-kind=\"main gate\"><rect x=\"1\" y=\"1\" width=\"2\" height=\"2\"/></g><g fill=\"#8FB0C6\"><text>\u{6c34}</text><circle cx=\"5\" cy=\"5\" r=\"1\"/></g><g id=\"trees\"><text>\u{91ce}</text><circle cx=\"5\" cy=\"5\" r=\"5\"/></g><circle cx=\"\u{661}\u{662}\" cy=\"1\" r=\"5\"/><text x=\"3\" y=\"4\" font-weight=\"bold\">\u{c9}t\u{e9} \u{2160}</text></svg>",
    ),
    (
        "no precinct",
        "<svg><rect x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/></svg>",
    ),
    ("unbalanced", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/></g></svg>"),
    ("unclosed", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><g>"),
    ("no svg", "<rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/>"),
    ("closing at the top", "</svg>"),
    ("a bad label x", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><text x=\"a\" y=\"1\">t</text></svg>"),
    ("a bad font size", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><text x=\"1\" y=\"1\" font-size=\"12px\">t</text></svg>"),
    ("a bad line drop", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><text x=\"1\" y=\"1\"><tspan x=\"1\">a</tspan><tspan x=\"1\" dy=\"-\">b</tspan></text></svg>"),
    ("a bad rotation", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><text x=\"1\" y=\"1\" transform=\"rotate(90 1.2.3 4)\">t</text></svg>"),
    ("a bad circle", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><circle cx=\"1.2.3\" cy=\"1\" r=\"5\"/></svg>"),
    ("a bad canopy", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><circle r=\"big\" fill=\"#7A8C5C\"/></svg>"),
    ("a path's lone coordinate", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><path d=\"M 1\" fill=\"#fff\"/></svg>"),
    ("a path's letter for a number", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><path d=\"M 1 L 2 3\" fill=\"#fff\"/></svg>"),
    ("a wall line missing its end", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><line x1=\"1\" y1=\"1\" stroke=\"#2D2A24\"/></svg>"),
    ("a wall's bad width", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><line x1=\"1\" y1=\"1\" x2=\"2\" y2=\"2\" stroke=\"#3F3A30\" stroke-width=\"thick\"/></svg>"),
    ("a roofed court missing its width", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><rect x=\"1\" y=\"1\" height=\"2\" fill=\"url(#court-cobbles)\" stroke=\"#5A3F1E\"/></svg>"),
    ("a bad translate", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><g transform=\"translate(.)\"><rect x=\"1\" y=\"1\" width=\"1\" height=\"1\"/></g></svg>"),
    ("a bad tub", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><g fill=\"#8FB0C6\"><circle cx=\"..\" cy=\"1\" r=\"1\"/></g></svg>"),
    ("a bad ellipse", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><ellipse cx=\"1\" cy=\"1\" rx=\".\" ry=\"1\"/></svg>"),
    ("a bad fence line", "<svg><rect id=\"precinct\" x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#fff\"/><g id=\"fence\"><line x1=\"-\" y1=\"1\" x2=\"2\" y2=\"2\"/></g></svg>"),
    // T174: the grid measures on fractional bounds (a float floor division that is not exact), every mask painted; the sized marks of
    // every tag, kind and lineage; and an interior that paints no cell (the Python's division by zero)
    ("measured: the grid measures", GRIDS),
    ("measured: the sized marks", MARKS),
    ("a precinct drawn backwards", "<svg><rect id=\"precinct\" x=\"20\" y=\"20\" width=\"-5\" height=\"9\" fill=\"url(#court-earth)\"/><rect x=\"0\" y=\"0\" width=\"30\" height=\"30\" fill=\"#DDB87A\"/></svg>"),
];

/// The grid measures' sheet (feature 449 T174): a precinct on fractional pixels, two buildings, an open feature, a tree glyph, a divider.
const GRIDS: &str = r##"<svg xmlns="http://www.w3.org/2000/svg">
<rect id="precinct" x="10.5" y="7.25" width="301.3" height="200.9" fill="url(#court-earth)"/>
<rect x="12" y="9" width="60" height="40" fill="#DDB87A" data-kind="hall"/>
<rect x="250.7" y="150.1" width="55" height="50" fill="#C9A57A"/>
<rect x="120" y="100" width="40" height="30" fill="url(#garden-stipple)"/>
<rect x="290" y="9.5" width="20" height="60.3" fill="#DDB87A"/>
<circle cx="200" cy="40" r="8" fill="#7A8C5C"/>
<g stroke="#3F3A30" stroke-width="3"><line x1="10.5" y1="120" x2="311" y2="120"/><line x1="160.2" y1="120" x2="160.2" y2="207"/></g>
</svg>"##;

/// The sized marks' sheet (feature 449 T174): each mark tag, a stroke width inherited with a unit, curves and diagonals (`math.hypot`),
/// a part's lineage, a not-highlighted mark, an untagged one, a caption's kind and a rect with no area.
const MARKS: &str = r#"<svg>
<rect id="precinct" x="0" y="0" width="300" height="300" fill="url(#court-earth)"/>
<g data-kind="road" stroke-width="4.5px"><path d="M 10 10 L 40 50 C 1 2 3 4 70 90 Q 5 5 100 33.3"/><polyline points="0,0 3,4 6,8.5"/></g>
<circle cx="50" cy="50" r="7.3" data-kind="tree"/>
<ellipse cx="80" cy="20" rx="4" ry="2.5" data-kind="tub" stroke-width="0.7"/>
<line x1="1" y1="1" x2="4.4" y2="5.1" data-kind="pole"/>
<polygon points="10,10 20,10 15,18" data-kind="arch" data-part-of="gate"/>
<g data-kind="landing"><rect x="5" y="5" width="9" height="9" data-kind="steps"/><circle cx="1" cy="1" r="1" data-kind="barge"/></g>
<circle cx="1" cy="1" r="1" data-kind="-"/>
<circle cx="2" cy="2" r="1"/>
<text x="1" y="1" data-kind="alcove">alcove</text>
<rect x="1" y="1" width="0" height="4" data-kind="flat"/>
<g data-kind="shrine"><text x="5" y="5">x</text></g>
<g transform="translate(5.5 2)"><line x1="0" y1="0" x2="0.1" y2="0.2" data-kind="peg"/></g>
</svg>"#;
