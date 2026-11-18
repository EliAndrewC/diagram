//! The page writer's cases (feature 449 T150, part A's lockstep): each a function's name and its arguments, once handed to the Python as
//! JSON too, now to the port's [`super::call::call`] alone, its answer held by `super` (pinned to the Python's, or by its outcome). Aimed at every line a pool sheet's page does not reach: the hamlet vocabulary and its card, the hit
//! regions and the keep-clear clip on the pool hamlets' own manifests, the town and city counts on the legacy pool's, the merge's tiles,
//! skips and refusals, the raster's documents and tiles, and the refusals the Python raised.
//!
//! Research: the page writer's lockstep cases - NONE: inputs, deciding nothing about a building

use std::fmt::Write as _;

use serde_json::{json, Value};

/// The pool hamlets, whose manifests and notes the hamlet cases read.
pub const HAMLETS: [&str; 5] = ["inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada"];

/// The legacy pool's maps of every tier the card describes, their manifests and notes read as the hamlets' are.
pub const LEGACY: [&str; 9] = [
    "hamlets/akagahara",
    "villages/hikari-no-sato",
    "villages/hoshigaoka",
    "towns/hirameki",
    "towns/ubame",
    "provincial-cities/minami",
    "provincial-cities/tango",
    "capitals/shiro-daika",
    "hamlets/tanada",
];

fn file(rel: &str) -> Value {
    json!({"file": rel})
}

fn meta(rel: &str) -> Value {
    json!({"file": rel, "key": "meta"})
}

/// `n` same-styled lines spread over cells, `every` of them a cell apart.
fn lines(n: usize, style: &str) -> String {
    let mut s = String::new();
    for i in 0..n {
        let (x, y) = ((i * 37) % 1700, (i * 53) % 900);
        let _ = write!(
            s,
            "<line x1=\"{x}\" y1=\"{y}\" x2=\"{}.5\" y2=\"{}\" {style}/>",
            x + 3,
            y + 2
        );
    }
    s
}

/// The merge's cases: tiles, skips, a blocked bucket, translucent and outlined refusals, and the Python's errors.
fn merges() -> Vec<Value> {
    let blades = lines(230, "stroke=\"#6a5\" stroke-width=\"0.8\"");
    let mut skips = "<line x1=\"0\" y1=\"0\" x2=\"5\" y2=\"5\" stroke=\"#000\"/>".to_owned();
    for i in 0..402 {
        let _ = write!(
            skips,
            "<rect x=\"{}\" y=\"900\" width=\"2\" height=\"2\" fill=\"#111\"/>",
            i * 10
        );
    }
    skips += "<line x1=\"1\" y1=\"1\" x2=\"6\" y2=\"6\" stroke=\"#000\"/>";
    let cases = [
        blades.clone(),
        format!("{}<rect x=\"0\" y=\"0\" width=\"900\" height=\"600\" fill=\"#fff\"/>{}", lines(3, "stroke=\"#000\""), lines(4, "stroke=\"#000\"")),
        skips,
        "<circle cx=\"10\" cy=\"10\" r=\"4\" fill=\"#383\" stroke=\"#121\" stroke-width=\"0.5\"/><circle cx=\"13\" cy=\"10\" r=\"4\" fill=\"#383\" stroke=\"#121\" stroke-width=\"0.5\"/><circle cx=\"40\" cy=\"10\" r=\"4\" fill=\"#383\" stroke=\"#121\" stroke-width=\"0.5\"/>".to_owned(),
        "<circle cx=\"10\" cy=\"10\" r=\"4\" fill=\"#383\" fill-opacity=\"0.85\"/><circle cx=\"12\" cy=\"10\" r=\"4\" fill=\"#383\" fill-opacity=\"0.85\"/><circle cx=\"30\" cy=\"10\" r=\"4\" fill=\"#383\" fill-opacity=\"0.85\"/>".to_owned(),
        "<circle cx=\"-0\" cy=\"5\" r=\"0\" fill=\"#a00\"/><circle cx=\"-0\" cy=\"5\" r=\"0\" fill=\"#a00\"/><ellipse cx=\"5\" cy=\"5\" rx=\"2.5\" ry=\"1.25\" fill=\"#0a0\"/><ellipse cx=\"50\" cy=\"5\" rx=\"2.5\" ry=\"1.25\" fill=\"#0a0\"/>".to_owned(),
        "<circle cx=\"1\" cy=\"1\" r=\"1\" fill=\"#a00\" opacity=\"\" stroke=\"#000\" stroke-width=\"\"/><circle cx=\"1\" cy=\"1\" r=\"1\" fill=\"#a00\" opacity=\"\" stroke=\"#000\" stroke-width=\"\"/>".to_owned(),
        "<path d=\"M1 2\" fill=\"#000\"/><line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke=\"#000\"/><polygon points=\"0,0 9,0 9,9\" fill=\"#999\"/><line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke=\"#000\"/>".to_owned(),
        "<line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke-width=\"x\"/><line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"/>".to_owned(),
        "<circle cx=\"1\" cy=\"1\" fill=\"#000\"/><circle cx=\"5\" cy=\"5\" fill=\"#000\"/>".to_owned(),
        "<line x1=\"inf\" y1=\"0\" x2=\"1\" y2=\"1\"/><line x1=\"inf\" y1=\"0\" x2=\"1\" y2=\"1\"/>".to_owned(),
        "<circle cx=\"1\" cy=\"1\" r=\"1\" opacity=\"half\"/><circle cx=\"1\" cy=\"1\" r=\"1\"/>".to_owned(),
        "<rect x=\"0\" y=\"0\" width=\"1\" height=\"1\"/>".to_owned(),
        "<g/><rect/>".to_owned(),
        "<rect x=\"1\" y=\"1\" width=\"q\" height=\"1\"/><ellipse cx=\"1\" cy=\"1\" rx=\"1\"/><rect x=\"1\" y=\"1\" width=\"1\" height=\"1\" stroke-width=\"bad\"/>".to_owned(),
    ];
    cases.into_iter().map(|s| json!(["merge", s])).collect()
}

fn hits() -> Vec<Value> {
    let marks = "<g stroke-width=\"1.4\"><line x1=\"0\" y1=\"0\" x2=\"9\" y2=\"9\" id=\"a\"/><polyline points=\"0,0 4,4\" fill=\"none\" stroke-width=\"0.6\"/><polygon points=\"0,0 4,4 0,4\"/><path d=\"M0,0L5,5\"/><path d=\"M0,0L5,5\" stroke=\"#000\"/><circle cx=\"3\" cy=\"4\" r=\"0.7\"/></g>";
    vec![
        json!(["hit_copies", marks]),
        json!(["hit_copies", marks, [8.0, 12.0, 6.0]]),
        json!(["hit_copies", "<line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"/>"]),
        json!([
            "hit_copies",
            "<g stroke-width=\"1.2.3\"><line x1=\"0\"/></g>"
        ]),
        json!(["hit_copies", "<circle cx=\"1\" cy=\"1\" r=\"1.2.3\"/>"]),
        json!(["wrap", lines(3, "stroke=\"#000\""), "bund"]),
        json!(["wrap", "<circle cx=\"1\" cy=\"1\" r=\"1\"/>", {"planted": "mulberry dike"}]),
        json!(["wrap", "<polygon points=\"0,0 4,4\" fill=\"#5a7\" stroke=\"#333\" stroke-width=\"1\"/>", {"fill": "paddy", "stroke": "bund"}]),
        json!(["wrap", "<g>x</g>", [["karo's house", "<rect/>"], [null, "<text>t</text>"], ["-", "<rect/>"], [{"planted": "well"}, "<circle/>"]]]),
        json!(["wrap", "<rect/>", "-"]),
        json!(["wrap", "<rect/>", null]),
        json!(["wrap", "", "well"]),
        json!(["wrap", "<rect/>", {"planted": "-"}]),
        json!([
            "part_of",
            "<g class=\"f f-well\" data-k=\"well\"><rect/></g>",
            ["kitchen", "karo's house"]
        ]),
        json!(["part_of", "<rect/>", ["kitchen"]]),
        json!(["part_of", "<g class=\"f f-well\" data-k=\"well\"></g>", []]),
        json!([
            "part_of",
            "<g class=\"f f-well\" data-k=\"well\"",
            ["kitchen"]
        ]),
    ]
}

fn census() -> Vec<Value> {
    let mut strings = vec![
        json!("<svg viewBox=\"0 0 10 10\">"),
        json!("<defs><rect/></defs><rect/>"),
        json!("<clipPath id=\"c\"><rect/></clipPath>"),
    ];
    let mut tags = vec![json!("-"), json!(null), json!("well")];
    for i in 0..23 {
        strings.push(json!(format!("<path d=\"M{i},0\"/>")));
        tags.push(json!(null));
    }
    strings.push(json!("<polygon points=\"0,0\"/><g/>"));
    tags.push(json!({"fill": "paddy", "stroke": "bund"}));
    strings.push(json!("<rect/>"));
    tags.push(json!([
        ["kitchen", "<rect/><text>a</text>"],
        [null, "<image/>"]
    ]));
    strings.push(json!("<rect/><rect/>"));
    tags.push(json!({"planted": "well"}));
    strings.push(json!("<rect/>"));
    tags.push(json!("no such kind"));
    vec![
        json!(["census", strings, tags]),
        json!(["present", tags]),
        json!([
            "unregistered",
            [
                ["-", 1],
                ["place", 2],
                ["well", 1],
                ["zzz", 1],
                ["paddy", 3]
            ],
            "hamlet"
        ]),
        json!([
            "unregistered",
            [["well", 1], ["zzz", 1], ["kitchen", 3]],
            "sheet"
        ]),
        json!(["census", ["<rect/>"], ["a", "b"]]),
    ]
}

/// Every key of the hamlet vocabulary the cases light, and their strings.
fn hamlet_page(registry: &[String]) -> (Vec<Value>, Vec<Value>, Vec<Value>) {
    let mut strings = vec![json!("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 400 300\" width=\"400\" height=\"300\">"), json!("<rect x=\"0\" y=\"0\" width=\"400\" height=\"300\" fill=\"#efe6cf\"/>")];
    let mut tags = vec![json!("-"), json!("-")];
    let mut within = vec![json!([]), json!([])];
    for (i, k) in registry.iter().enumerate() {
        let (x, y) = ((i * 23) % 380, (i * 41) % 280);
        strings.push(json!(format!("<rect x=\"{x}\" y=\"{y}\" width=\"12\" height=\"9\" fill=\"#7a6\" stroke=\"#333\" stroke-width=\"0.6\"/><line x1=\"{x}\" y1=\"{y}\" x2=\"{}\" y2=\"{}\" stroke=\"#345\" stroke-width=\"0.5\"/>", x + 9, y + 7)));
        tags.push(json!(k));
        within.push(json!(if i % 7 == 0 {
            vec!["paddy"]
        } else {
            Vec::new()
        }));
    }
    strings.push(json!("<polygon points=\"40,40 90,40 90,80 40,80\" fill=\"#9cf\" stroke=\"#653\" stroke-width=\"1.2\"/>"));
    tags.push(json!({"fill": "wet paddy", "stroke": "bund"}));
    within.push(json!([]));
    strings.push(json!("<g transform=\"translate(5,5)\"><rect x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#a85\"/><text x=\"1\" y=\"8\" font-family=\"serif\" font-size=\"6\">Ho</text></g>"));
    tags.push(json!([
        [
            "farmhouse",
            "<rect x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#a85\"/>"
        ],
        [
            "place",
            "<text x=\"1\" y=\"8\" font-family=\"serif\" font-size=\"6\">Inashiro</text>"
        ]
    ]));
    within.push(json!([]));
    strings.push(json!("<circle cx=\"900\" cy=\"900\" r=\"2\" fill=\"#000\"/><circle cx=\"20\" cy=\"20\" r=\"2\" fill=\"#000\"/>"));
    tags.push(json!({"planted": "copse"}));
    within.push(json!([]));
    strings.push(json!(
        "<text x=\"10\" y=\"290\" font-family=\"serif\" font-size=\"9\">scale</text>"
    ));
    tags.push(json!(null));
    within.push(json!([]));
    strings.push(json!("</svg>"));
    tags.push(json!("-"));
    within.push(json!([]));
    (strings, tags, within)
}

#[expect(
    clippy::too_many_lines,
    reason = "the hamlet vocabulary's cases, one list"
)]
fn hamlet_cases(hamlet_keys: &[String], sheet_keys: &[String]) -> Vec<Value> {
    let mut out = Vec::new();
    let regions: Vec<&str> = [
        "scrub and rough grazing",
        "woodland commons",
        "marsh",
        "windbreak",
        "copse",
        "homestead bamboo",
        "shared bamboo grove",
    ]
    .to_vec();
    let (strings, tags, within) = hamlet_page(hamlet_keys);
    for h in HAMLETS {
        let m = format!("pool/hamlets/{h}/{h}.json");
        let notes = file(&format!("pool/hamlets/{h}/{h}.notes.md"));
        out.push(json!(["hit_regions", file(&m), regions]));
        out.push(json!(["keep_clear", file(&m)]));
        out.push(json!([
            "place_card",
            meta(&m),
            hamlet_keys,
            notes,
            file(&m)
        ]));
        out.push(json!(["explain", hamlet_keys, notes, "hamlet", meta(&m)]));
        out.push(json!([
            "read_notes",
            format!("pool/hamlets/{h}/{h}.notes.md")
        ]));
        for k in ["windbreak", "retirement", "grove"] {
            out.push(json!([k, meta(&m)]));
        }
    }
    let ina = "pool/hamlets/inashiro/inashiro.json";
    let notes = file("pool/hamlets/inashiro/inashiro.notes.md");
    out.push(json!([
        "render",
        strings,
        tags,
        "Inashiro",
        meta(ina),
        file(ina),
        notes,
        true,
        "hamlet",
        null
    ]));
    out.push(json!([
        "render",
        strings,
        tags,
        "Inashiro",
        meta(ina),
        file(ina),
        notes,
        false,
        "hamlet",
        within
    ]));
    let town = json!({"scale": "town", "name": "Ubame", "windward": "NW", "wind_source": "regional", "grove_sides": 3, "settlement_form": "dispersed"});
    out.push(json!(["render", strings, tags, "A Town", town, {"houses": [{"x": 1, "y": 2, "w": 3, "h": 4}]}, "", false, "hamlet", null]));
    out.push(json!([
        "render", strings, tags, "Nothing", null, null, "", false, "hamlet", null
    ]));
    out.push(json!([
        "render",
        [],
        [],
        "Empty",
        null,
        null,
        "",
        true,
        "hamlet",
        null
    ]));
    out.push(json!([
        "render",
        ["<svg>", "</svg>"],
        ["-", "-"],
        "No box",
        null,
        null,
        "",
        true,
        "sheet",
        [[], []]
    ]));
    out.push(json!([
        "render",
        ["<svg viewBox=\"0 0 9 9\">"],
        ["-", "-"],
        "Unzipped",
        null,
        null,
        "",
        false,
        "sheet",
        null
    ]));
    out.push(json!([
        "explain",
        sheet_keys,
        "## Map notes\n\n### Features\n\n- **well**: the map's own well.\n",
        "sheet",
        {}
    ]));
    out.push(json!([
        "explain",
        ["place", "no such kind", "well"],
        "",
        "sheet",
        null
    ]));
    for l in LEGACY {
        let name = l.rsplit('/').next().unwrap_or(l);
        let m = format!("legacy-hand-authored-pool/{l}/{name}.json");
        let notes = file(&format!("legacy-hand-authored-pool/{l}/{name}.notes.md"));
        out.push(json!([
            "place_card",
            meta(&m),
            hamlet_keys,
            notes,
            file(&m)
        ]));
        out.push(json!(["place_card", meta(&m), [], "", file(&m)]));
    }
    out
}

fn place_cases() -> Vec<Value> {
    let place = json!([
        ["district", "Hoshigaoka"],
        ["district direction", "east"],
        ["county", "Hayakawa"],
        ["imperial road", "directly south"],
        ["town", "Hayakawa"],
        ["town direction", "further south"],
        ["also", "A ferry crosses here"]
    ]);
    let bare = json!([
        ["district", "Hoshigaoka"],
        ["town", "Hayakawa"],
        ["also", "Ends."]
    ]);
    let mut out = vec![
        json!(["kinds"]),
        json!(["join", []]),
        json!(["join", ["a"]]),
        json!(["join", ["a", "b"]]),
        json!(["join", ["a", "b", "c"]]),
    ];
    for scale in ["hamlet", "village", "town", "city", "capital"] {
        out.push(json!(["where", scale, place]));
        out.push(json!(["where", scale, bare]));
        out.push(json!(["lane_default", scale, place]));
    }
    out.push(json!(["lane_default", "hamlet", []]));
    out.push(json!([
        "crops",
        [
            "paddy",
            "millet",
            "soy",
            "mulberry dike",
            "fish pond",
            "bund beans"
        ]
    ]));
    out.push(json!(["crops", []]));
    let metas = [
        json!({"households": 70}),
        json!({"households": 66}),
        json!({"households": 70.0}),
        json!({"households": "12"}),
        json!({"households": true}),
        json!({"population": 1200.7}),
        json!({"population": "x"}),
        json!({}),
        json!({"households": null}),
    ];
    for m in &metas {
        for (scale, houses) in [("hamlet", 66), ("village", 0), ("town", 95), ("city", 70)] {
            out.push(json!(["size_sentence", scale, m, houses]));
        }
    }
    for m in [
        json!({"windward": "N", "wind_source": "declared"}),
        json!({"windward": "NW", "wind_source": "regional", "name": "Kuwabata"}),
        json!({"windward": "X", "wind_source": "regional"}),
        json!({"windward": "N"}),
        json!({"windward": null, "wind_source": "regional"}),
        json!({"grove_sides": 4, "settlement_form": "dispersed", "flood_ground": true}),
        json!({"grove_sides": 2.0, "settlement_form": null}),
        json!({"grove_sides": 2}),
        json!({"grove_sides": true, "settlement_form": "linear"}),
        json!({"grove_sides": 5, "settlement_form": "linear"}),
        json!({"family_form": "retirement_house", "retirement_houses": 3, "households": 15, "name": "Sawada"}),
        json!({"family_form": "retirement_house", "retirement_houses": 3.0, "households": 15}),
        json!({"family_form": "retirement_house", "retirement_houses": true, "households": true}),
        json!({"family_form": "retirement_house", "retirement_houses": 0, "households": 15}),
        json!({"family_form": "stem", "retirement_houses": 3, "households": 15}),
    ] {
        for k in ["windbreak", "retirement", "grove"] {
            out.push(json!([k, m]));
        }
    }
    for (m, scale) in [
        (json!({"houses": [1, 2, 3]}), "hamlet"),
        (json!({"houses": "abc"}), "village"),
        (json!({"houses": 3}), "hamlet"),
        (
            json!({"buildings": [{"kind": "samurai"}, {"kind": "shop"}, {"kind": "monk_house"}]}),
            "town",
        ),
        (json!({"buildings": [3]}), "city"),
        (json!({}), "town"),
        (json!({"houses": null}), "hamlet"),
    ] {
        out.push(json!(["dwellings_shown", m, scale]));
    }
    out.push(json!(["place_card", {"scale": "town"}, [], "", {"buildings": 7}]));
    out.push(json!(["place_card", {"scale": "village"}, [], "", {}]));
    out.push(json!(["size_sentence", "capital", {}, 3]));
    out.push(json!(["place_card", {"scale": "hamlet", "households": 5}, ["field grave"], "", {"houses": [1]}]));
    out
}

fn notes_cases() -> Vec<Value> {
    let texts = [
        "# Title\n\n## Map notes\n\n### Place\n\n- **District**: Hoshigaoka\n- **district  direction**: east\n  and a little north\n- not a bullet\n- **county** Hayakawa\n  - nested\n\n### Features\n\n- **Village Lane**: runs south\n  <!-- a comment -->\n  continues\n- **windbreak**:\n- **windbreak**: first wins\n- **windbreak**: second\n#### deeper\n- **well**: under a deeper heading\n## Next\n- **copse**: outside\n",
        "## Map Notes\r\n### Place\r\n- **district**: A\r\n### Features\r\n",
        "no block at all",
        "## map notes\n\n### place\n",
        "## *Map* `notes`\n### Features\n- **`well`**: x\x0c- **pond**: y\n\t- **x**: wrapped tab\n| a | b |\n  * star\n",
        "### Map notes\n- **a**: b\n## Map notes\n### Place\n- **a**: c",
    ];
    let mut out: Vec<Value> = texts.iter().map(|t| json!(["notes", t])).collect();
    out.push(json!(["section", texts[0], "features"]));
    out.push(json!(["section", texts[0], "nowhere"]));
    out.push(json!(["read_notes", "pool/no-such-map.notes.md"]));
    out
}

fn raster_cases() -> Vec<Value> {
    let page = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 60 40\" width=\"60\" height=\"40\">\n<rect width=\"60\" height=\"40\" fill=\"#efe6cf\" stroke=\"#000\" opacity=\"0.5\"/>\n<g class=\"f f-well\" data-k=\"well\"><circle cx=\"10\" cy=\"10\" r=\"5\" fill=\"#36c\" fill-opacity=\"0.5\"/><g><rect x=\"1\" y=\"1\" width=\"2\" height=\"2\" fill=\"url(#p)\"/></g><text x=\"2\" y=\"30\" font-family=\"serif\" font-size=\"8\">W</text></g>\n<g class=\"f f-karo-s-house planted\" data-k=\"karo&#x27;s house\" data-in=\"court\"><path d=\"M20,20L40,30\" stroke=\"#a33\" fill=\"none\"/><path d=\"M20,20L40,30\" fill=\"none\" class=\"hit\" style=\"pointer-events: stroke; stroke-width: 6.0px\"/><circle cx=\"30\" cy=\"5\" r=\"1.5\" fill=\"none\" class=\"hit\" style=\"pointer-events: fill\"/></g>\n<g class=\"f f-scrub\" data-k=\"scrub\"><path class=\"hit\" d=\"M0,0L9,0L9,9Z\" fill-rule=\"evenodd\" fill=\"none\" style=\"pointer-events: fill\"/></g>\n<g class=\"f f-well\" data-k=\"well\"><rect x=\"50\" y=\"30\" width=\"4\" height=\"4\" fill=\"#36c\"/></g>\n<text x=\"40\" y=\"38\" font-size=\"5\">scale</text>\n</svg>";
    let merged = "<g class=\"f f-scrub\" data-k=\"scrub\"><path d=\"M-500,1L-490,2M5,5L7,7M800,1L801,1\" stroke=\"#6a5\"/><path d=\"M-100,5a2,2 0 1 0 4,0a2,2 0 1 0 -4,0M10,10a2,2 0 1 0 4,0\" fill=\"#353\"/><path d=\"M-500,1L-490,2\" fill=\"#000\"/><path d=\"M1 2 C 3 4\" fill=\"#000\"/><circle cx=\"-900\" cy=\"1\" r=\"1\"/><circle r=\"1\" cy=\"1\" cx=\"5\"/><ellipse cx=\"5\" cy=\"5\" rx=\"1\" ry=\"2\"/><ellipse cx=\"5\" ry=\"2\" cy=\"5\" rx=\"1\"/><line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"/><line y1=\"0\" x1=\"0\" x2=\"-900\" y2=\"1\"/><rect x=\"0\" y=\"0\" width=\"1\" height=\"1\"/><rect y=\"0\" x=\"-900\" width=\"1\" height=\"1\"/><polygon points=\"0,0 1,1 2,0\"/><polyline points=\"-900,0 -901,1\"/><polygon points=\"\"/><polygon/><rect x=\"a\" y=\"0\" width=\"1\" height=\"1\"/></g>";
    let vb = json!([0.0, 0.0, 60.0, 40.0]);
    let mut out = vec![
        json!(["viewbox", "<svg viewBox=\" 0, -5 60.5 40 \">"]),
        json!(["viewbox", "<svg>"]),
        json!(["viewbox", "<svg viewBox=\"0 0 1.2.3 4\">"]),
        json!(["drop_offmap", merged, vb]),
        json!(["drop_offmap", "<g transform=\"translate(9,9)\"><circle cx=\"-900\" cy=\"1\" r=\"1\"/></g>", vb]),
        json!(["drop_offmap", "<circle cx=\"1.2.3\" cy=\"1\" r=\"1\"/>", vb]),
        json!(["drop_offmap", "<path d=\"M1,2a\" fill=\"#000\"/>", vb]),
        json!(["drop_offmap", "<path d=\"M-900,0L-901,1\" fill=\"#000\"/> tail", vb]),
        json!(["tile_count", [0.0, 0.0, 3402.0, 3424.0], 2.0]),
        json!(["tile_count", [0.0, 0.0, 60.0, 40.0], 2.0]),
        json!(["tile_count", [0.0, 0.0, -60.0, 40.0], 2.0]),
        json!(["tile_boxes", [10.0, 5.0, 1001.0, 799.0], 3]),
        json!(["tile_boxes", [0.0, 0.0, 2.0, 2.0], 3]),
        json!(["tile_doc", format!("{page}\n{merged}"), [10.0, 0.0, 30.0, 20.0]]),
        json!(["tile_doc", "<svg>no box</svg>", [0.0, 0.0, 1.0, 1.0]]),
        json!(["class_keys", page]),
        json!(["recolor", "<g class=\"f f-x\" data-k=\"x\"><g class=\"hit\" fill=\"none\" style=\"pointer-events: fill\"><rect fill=\"none\"/></g><rect fill=\"#abc\" stroke=\"#123456\"/><rect fill=\"url(#p)\"/></g>", "#040000"]),
        json!(["unpaint", "<rect fill=\"#abc\" stroke=\"#123\"/><rect fill=\"url(#q)\" stroke=\"none\"/>"]),
        json!(["without_text", page]),
        json!(["id_map", page, false]),
        json!(["id_map", page, true]),
        json!(["id_map", "<svg viewBox=\"0 0 9 9\"><g class=\"f f-a\" data-k=\"a\"><g></svg>", false]),
        json!(["picture", page, 2.0, null]),
        json!(["picture", page, 2.0, 2]),
        json!(["picture", page, 1.5, 2]),
        json!(["picture", "<svg width=\"8\" height=\"6\"><rect width=\"8\" height=\"6\" fill=\"#123\"/></svg>", 2.0, null]),
        json!(["data_uri", "image/png", "abcde"]),
        json!(["refuse", 100.0, "1"]),
        json!(["refuse", 2000.0, "1"]),
        json!(["refuse", 2000.0, null]),
        json!(["refuse", 2000.0, ""]),
    ];
    out.extend(
        [1, 2, 63, 64, 127, 4032]
            .iter()
            .map(|i| json!(["palette", i])),
    );
    out
}

/// The hit geometry on synthetic manifests: a lifted class's layer on a stand-in (`HIT_ON_TOP` is empty today), the keep-clear clip's
/// rotations, polygons and skipped records, the regions' roles and covers, and their refusals.
fn geometry() -> Vec<Value> {
    let strings = json!([
        "<line x1=\"0\" y1=\"0\" x2=\"9\" y2=\"9\" stroke-width=\"0.5\"/>",
        "<polygon points=\"0,0 4,4 0,4\" fill=\"none\" stroke=\"#000\" stroke-width=\"1\"/>",
        "<rect/>",
        "<g>x</g>",
        "<path d=\"M0,0L1,1\" fill=\"none\"/>",
        "<line x1=\"7\" y1=\"7\" x2=\"8\" y2=\"8\"/>",
    ]);
    let tags = json!([
        "stream", {"fill": "paddy", "stroke": "bund"}, "bund",
        [["village lane", "<line x1=\"2\" y1=\"2\" x2=\"3\" y2=\"3\"/>"], [null, "<rect/>"], ["-", "<rect/>"]], "zzz", "stream",
    ]);
    let clear = json!({
        "houses": [
            {"x": 1, "y": 2, "w": 3, "h": 4, "rot": 30}, {"x": "5", "y": 5, "w": 2, "h": 2, "rot": null, "poly": [[0, 0], [4, 1], [2, 6]]},
            {"x": 1}, "notadict", {"x": "q", "y": 1, "w": 1, "h": 1}, {"x": 1, "y": 1, "w": 1, "h": 1, "rot": "bad"},
            {"x": 1, "y": 1, "w": 1, "h": 1, "poly": [[0, 0], [1, 1]]}, {"x": 1, "y": 1, "w": null, "h": 1},
        ],
        "pig_sties": [{"x": 0.05, "y": -0.05, "w": 1.25, "h": 0.75, "rot": -90}],
    });
    let regions = json!({
        "commons": [
            {"role": null, "poly": [[0, 0], [1, 1], [2, 0]]}, {"role": "grazing", "poly": [[0, 0], [1, 0], [1, 1]], "cover": []},
            {"role": "woodland", "poly": [[0, 0], [1, 0], [1, 1]]}, {"poly": []}, 7,
            {"role": "commons", "poly": [[0, 0], [1, 0], [1, 1]], "cover": [[[0, 0], [9, 0], [9, 9]], [[2, 2], [3, 3], [2, 3]]]},
        ],
        "marshes": [{"poly": [[0, 0], [3, 0], [3, 3]], "cover": [[[0, 0], [1, 1], [1, 0]]]}, {"poly": [[0, 0], [3.25, 0.05], [3, 3]]}],
        "village_groves": [{"role": "copse", "poly": [[0, 0], [1, 0], [1, 1]]}, {"role": "windbreak", "poly": [[0, 0], [1, 0], [1, 1]]}],
        "bamboo_stands": [{"role": "homestead", "poly": [["1.5", "2"], [3, 4], [5, 6]]}, {"poly": [[1, 1], [2, 2], [3, 1]]}],
    });
    let present = json!([
        "scrub and rough grazing",
        "woodland commons",
        "marsh",
        "windbreak",
        "homestead bamboo",
        "shared bamboo grove"
    ]);
    vec![
        json!(["hit_layer", strings, tags, file("pool/hamlets/inashiro/inashiro.json"), ["pond canal", "zzz", "bund", "village lane", "stream"]]),
        json!(["hit_layer", strings, tags, null, []]),
        json!(["hit_layer", ["<line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke-width=\"1.2.3\"/>"], ["stream"], {}, ["stream"]]),
        json!(["keep_clear", clear]),
        json!(["keep_clear", {"houses": 5}]),
        json!(["keep_clear", {"houses": [{"x": 1, "y": 1, "w": 1, "h": 1, "poly": [[0, 0], [1], [2, 2]]}]}]),
        json!(["keep_clear", {"houses": [{"x": 1, "y": 1, "w": 1, "h": 1, "poly": [[0, 0], ["a", 1], [2, 2]]}]}]),
        json!(["keep_clear", {}]),
        json!(["hit_regions", regions, present]),
        json!(["hit_regions", {"marshes": [{"poly": [[0, 0], [1, 2, 3]]}]}, ["marsh"]]),
        json!(["hit_regions", {"marshes": [{"poly": [[0, 0], [1]]}]}, ["marsh"]]),
        json!(["hit_regions", {"marshes": [{"poly": [5]}]}, ["marsh"]]),
        json!(["hit_regions", {"marshes": [{"poly": [[0, null]]}]}, ["marsh"]]),
        json!(["hit_regions", {"marshes": "ab", "commons": {"k": 1}}, ["marsh"]]),
        json!(["hit_regions", {}, ["marsh"]]),
        json!(["hit_regions", null, ["marsh"]]),
        // an outlined bucket refusing a same-styled circle whose extent cannot be read
        json!(["merge", "<circle cx=\"1\" cy=\"1\" r=\"1\" fill=\"#000\" stroke=\"#000\"/><circle cx=\"9\" cy=\"9\" fill=\"#000\" stroke=\"#000\"/>"]),
        json!(["render", ["<svg viewBox=\"0 0 9 9\">", "<rect/>"], ["-"], "Unzipped", null, null, "", false, "sheet", null]),
        json!(["render", ["<svg viewBox=\"0 0 9 9\">", "<rect/>"], ["-", "-"], "Unzipped", null, null, "", false, "sheet", [[]]]),
        json!(["render", ["<svg viewBox=\"0 0 90 60\" width=\"90\" height=\"60\">", "<rect width=\"9\" height=\"9\"/>", "</svg>"], ["-", "paddy", "-"], "Few", meta("pool/hamlets/sawada/sawada.json"), file("pool/hamlets/sawada/sawada.json"), file("pool/hamlets/sawada/sawada.notes.md"), false, "hamlet", null]),
        // a box wider than the grid's span: kept aside, and asked of every filed extent
        json!(["merge", format!("{}<rect x=\"0\" y=\"0\" width=\"3000\" height=\"10\"/>{}<line x1=\"0\" y1=\"500\" x2=\"3000\" y2=\"500\" stroke=\"#000\"/><line x1=\"0\" y1=\"900\" x2=\"3000\" y2=\"900\" stroke=\"#000\"/>", lines(3, "stroke=\"#000\""), lines(3, "stroke=\"#000\""))]),
        json!(["merge", "<line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke=\"#000\" stroke=\"#111\"/><line x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\" stroke=\"#111\"/>"]),
        json!(["merge", "<circle cx=\"1\" cy=\"1\" r=\"1\" fill=\"#000\" stroke=\"#000\"/><path d=\"M0 0\"/><circle cx=\"9\" cy=\"9\" r=\"1\" fill=\"#000\" stroke=\"#000\"/><circle cx=\"30\" cy=\"9\" r=\"1\" fill=\"#000\" stroke=\"#000\"/>"]),
        json!(["merge", format!("{}<circle cx=\"5\" cy=\"5\" r=\"2\"/><circle cx=\"5\" cy=\"5\" r=\"2\"/>", (0..205).fold(String::new(), |mut s, i| {
            let _ = write!(s, "<circle cx=\"{}\" cy=\"{}\" r=\"1\" fill=\"#0a0\"/>", (i * 97) % 1900, (i * 31) % 800);
            s
        }))]),
    ]
}

/// A synthetic sheet with every form the pieces take: an id reopened, definitions, a part drawn elsewhere, text runs, a ruling.
const SHEET: &str = "<?xml version=\"1.0\"?><!-- a note --><svg viewBox=\"0 0 40 30\" width=\"40\" height=\"30\"><defs><pattern id=\"p\"><rect/></pattern></defs><rect width=\"40\" height=\"30\" fill=\"#eee\" data-kind=\"-\"/><g id=\"court\" transform=\"translate(1,1)\" data-kind=\"inner court\"><rect x=\"0\" y=\"0\" width=\"9\" height=\"9\" fill=\"#ccc\"/><g data-kind=\"kitchen\"><rect x=\"1\" y=\"1\" width=\"3\" height=\"3\"/><circle cx=\"2\" cy=\"2\" r=\"1\" data-kind=\"hearth\"/></g>  text run  <rect data-kind=\"-\"/></g><rect x=\"20\" y=\"1\" width=\"2\" height=\"2\" data-kind=\"genkan\" data-part-of=\"residence\"/><text x=\"1\" y=\"28\">Ochiba's Manor</text></svg>";

/// The parse fixtures the sheet's reader refuses (`fixtures.rs`): their pieces, census and page refused on both sides.
const READER_REFUSALS: [&str; 4] = ["unbalanced", "unclosed", "no svg", "closing at the top"];

/// The cases that SHOULD refuse, each the Python's refusal its input was written to reach: the case's name, a piece of its arguments' JSON
/// that picks it out, and why. Every other case is asserted to succeed on both sides (`check`); a name marked `!` is asserted to refuse.
const REFUSALS: [(&str, &str, &str); 30] = [
    (
        "merge",
        r#"stroke-width=\"x\""#,
        "a line's stroke width that is no number (read outside the Python's try)",
    ),
    (
        "merge",
        r##"<circle cx=\"1\" cy=\"1\" fill=\"#000\"/><circle cx=\"5\""##,
        "merged circles with no radius (the subpath's KeyError)",
    ),
    (
        "merge",
        r#"x1=\"inf\""#,
        "an infinite coordinate's grid cell (int of NaN)",
    ),
    (
        "merge",
        r#"opacity=\"half\""#,
        "an opacity that is no number",
    ),
    (
        "merge",
        r#"stroke-width=\"bad\""#,
        "a rect's stroke width that is no number",
    ),
    (
        "hit_copies",
        "1.2.3",
        "a width or radius `[\\d.]+` took that is no number",
    ),
    (
        "part_of",
        r#"data-k=\"well\"",["kitchen"]"#,
        "an opening that never closes (str.index)",
    ),
    (
        "census",
        r#"["a","b"]"#,
        "more tags than strings (zip strict)",
    ),
    (
        "render",
        "Unzipped",
        "strings, tags and parts of different lengths (zip strict)",
    ),
    (
        "size_sentence",
        r#""hamlet",{"population":"x"}"#,
        "a population that is no integer",
    ),
    (
        "size_sentence",
        r#""village",{"population":"x"}"#,
        "a population that is no integer",
    ),
    (
        "size_sentence",
        r#""city",{"population":"x"}"#,
        "a population that is no integer",
    ),
    (
        "size_sentence",
        r#""capital""#,
        "a tier the card does not describe (KINDS' KeyError)",
    ),
    (
        "dwellings_shown",
        r#"{"houses":3}"#,
        "houses with no length",
    ),
    (
        "dwellings_shown",
        r#"{"buildings":[3]}"#,
        "a building that is no object",
    ),
    (
        "place_card",
        r#"{"buildings":7}"#,
        "buildings that are not a list",
    ),
    ("viewbox", "1.2.3", "a viewBox figure that is no number"),
    (
        "drop_offmap",
        "1.2.3",
        "a fast-read figure that is no number",
    ),
    (
        "drop_offmap",
        r#"M1,2a\""#,
        "an arc with no radius (the Python's IndexError)",
    ),
    ("tile_count", "-60.0", "a negative area's square root"),
    (
        "id_map",
        "<g></svg>",
        "a class group never closed (the Python's assert)",
    ),
    (
        "refuse",
        r#"2000.0,"1""#,
        "a raster past the test bar with the render switch set",
    ),
    (
        "hit_layer",
        "1.2.3",
        "a lifted mark's width that is no number",
    ),
    (
        "keep_clear",
        r#"{"houses":5}"#,
        "records that are not a list",
    ),
    ("keep_clear", "[1],[2,2]", "a polygon point with no y"),
    (
        "keep_clear",
        r#"["a",1]"#,
        "a polygon point that is no number",
    ),
    ("hit_regions", "[1,2,3]", "a ring point of three figures"),
    ("hit_regions", "[[0,0],[1]]", "a ring point of one figure"),
    (
        "hit_regions",
        r#""poly":[5]"#,
        "a ring point that is no pair",
    ),
    ("hit_regions", "[0,null]", "a ring figure that is null"),
];

/// Every case, in order.
#[must_use]
pub fn cases(hamlet_keys: &[String], sheet_keys: &[String], sheets: &[(&str, &str)]) -> Vec<Value> {
    let mut out = vec![json!(["consts"])];
    out.extend(merges());
    out.extend(hits());
    out.extend(census());
    out.extend(hamlet_cases(hamlet_keys, sheet_keys));
    out.extend(place_cases());
    out.extend(notes_cases());
    out.extend(raster_cases());
    out.extend(geometry());
    out.push(json!(["pieces", SHEET]));
    out.push(json!(["sheet_census", SHEET]));
    // each parse fixture's pieces, census and page (no picture); the reader's own refusals refused on both sides
    for (name, s) in sheets {
        let mark = if READER_REFUSALS.contains(name) {
            "!"
        } else {
            ""
        };
        for f in ["pieces", "sheet_census", "sheet_page"] {
            out.push(json!([format!("{mark}{f}"), s]));
        }
    }
    out.push(json!(["!pieces", "<svg><g>"]));
    for p in [
        "pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg",
        "a/b/karo's-house.plan.svg",
        "noext",
        "x/3d-plan.svg",
    ] {
        out.push(json!(["title_of", p]));
    }
    // a raster page with no class group: the picture's image goes before the close
    out.push(json!([
        "render",
        [
            "<svg viewBox=\"0 0 20 10\" width=\"20\" height=\"10\">",
            "<rect width=\"20\" height=\"10\" fill=\"#abc\"/>",
            "</svg>"
        ],
        ["-", "-", "-"],
        "Bare",
        null,
        null,
        "",
        true,
        "sheet",
        null
    ]));
    // the merge's long scatter under a class, through the whole page: its tiles reach the off-map drop and the picture's tiles
    out.push(json!([
        "render",
        [
            "<svg viewBox=\"0 0 1700 900\" width=\"1700\" height=\"900\">",
            lines(230, "stroke=\"#6a5\" stroke-width=\"0.8\""),
            "</svg>"
        ],
        ["-", "scrub and rough grazing", "-"],
        "Scrub",
        null,
        null,
        "",
        true,
        "hamlet",
        null
    ]));
    for case in &mut out {
        let text = case.to_string();
        let refuses = REFUSALS
            .iter()
            .any(|(name, needle, _)| case[0] == *name && text.contains(needle));
        if refuses {
            case[0] = Value::from(format!("!{}", super::text_of(&case[0])));
        }
    }
    // every listed refusal names a case, so the table never outlives what it lists
    for (name, needle, why) in REFUSALS {
        let named = out
            .iter()
            .any(|c| c[0] == format!("!{name}") && c.to_string().contains(needle));
        assert!(named, "{why}");
    }
    out
}
