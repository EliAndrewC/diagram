//! A change to an engine's drawing code owes the glyph-check of each element it redraws (449 T237), on scratch repositories whose
//! `rust/phases/src/driver/` and `rust/mode_a/src/compound*` hold small engines of the real ones' shape.

use std::path::Path;

use super::super::super::tests::{
    commit, compound, drawn, feature, hamlet, put, repo, sh, started,
};
use super::super::{all_owed, check_declared, Unit};
use super::*;

/// The writer: `kind` names what the marks after it depict, `polygon` and `line` ink, `finish` writes the document with its tile.
const SVG: &str = r###"//! the writer
pub mod ink {
    pub const LAND: &str = "#EFE3C2";
    pub const DRAIN: &str = "#4F7186";
}

const TILE: &str = r##"<pattern id="p">"{"</pattern>"##;

#[derive(Default)]
pub struct Svg {
    body: String,
    kind: String,
}

impl Svg {
    pub fn kind(&mut self, kind: &str) {
        kind.clone_into(&mut self.kind);
    }

    pub fn polygon(&mut self, ring: &[(f64, f64)], fill: &str) {
        let _ = (ring, fill, '{', '\'');
        self.body.push('p');
    }

    pub fn line(&mut self, pts: &[(f64, f64)], stroke: &str) {
        self.polygon(pts, stroke);
    }

    /* the document */
    pub fn finish(&self) -> String {
        format!("<svg><defs>{TILE}</defs>{}</svg>", self.body)
    }

    pub fn unused(&self) {}
}

impl std::fmt::Display for Svg {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.body)
    }
}

#[cfg(test)]
mod tests {
    fn writes() {
        svg.kind("tested");
    }
}
"###;

/// A polder: its stage, a helper and a constant only the sluice's drawing reads, two draw functions (one choosing its kind at run
/// time), and the roll that draws them.
const POLDER: &str = r#"//! a polder
use super::svg::{ink, Svg};

const SLUICE_SPAN_FT: f64 = 20.0;
const SLUICE_FT: f64 = 8.0;

pub struct PolderStage {
    pub sluices: Vec<(f64, f64)>,
    pub plots: Vec<Vec<(f64, f64)>>,
}

struct Frame {
    board: Vec<(f64, f64)>,
}

impl Frame {
    fn span(&self) -> usize {
        self.board.len()
    }
}

fn paddy_kind(i: usize) -> &'static str {
    if i == 0 { "paddy" } else { "wet paddy" }
}

fn polygon(n: usize) -> usize {
    n + 1
}

fn stage_polder(n: usize) -> PolderStage {
    let sluices = (0..polygon(n)).map(|i| (i as f64, 0.0)).collect();
    PolderStage { sluices, plots: Vec::new() }
}

fn sluice_frame(at: (f64, f64)) -> Frame {
    let half = SLUICE_SPAN_FT / 2.0;
    let _whole = SLUICE_SPAN_FT;
    Frame { board: vec![(at.0 - half, at.1), (at.0 + half, at.1)] }
}

fn draw_polder(svg: &mut Svg, s: &PolderStage) {
    for (i, x) in s.plots.iter().enumerate() {
        svg.kind(paddy_kind(i));
        svg.polygon(x, ink::LAND);
    }
    svg.kind("sluice gate");
    let h = SLUICE_FT / 2.0;
    for g in &s.sluices {
        svg.polygon(&[(g.0 - h, g.1)], ink::DRAIN);
    }
}

fn draw_sluices(svg: &mut Svg, s: &PolderStage) {
    svg.kind("sluice gate");
    for &at in &s.sluices {
        // the frame across its channel
        let f = sluice_frame(at);
        svg.polygon(&f.board, ink::DRAIN);
    }
}

fn under(svg: &mut Svg, s: &PolderStage) {
    svg.line(&s.sluices, ink::DRAIN);
}

pub fn roll_polder(n: usize) -> String {
    let s = stage_polder(n);
    let mut svg = Svg::default();
    draw_polder(&mut svg, &s);
    svg.kind("marsh");
    for strip in &s.plots {
        svg.polygon(strip, ink::LAND);
    }
    svg.kind(paddy_kind(1));
    svg.line(&s.sluices, ink::DRAIN);
    draw_sluices(&mut svg, &s);
    svg.kind("-");
    under(&mut svg, &s);
    let doc = svg.finish();
    doc
}

pub fn ground(n: usize) -> String {
    let mut svg = Svg::default();
    svg.line(&[], ink::LAND);
    roll_polder(n)
}

#[cfg(test)]
mod tests {
    fn rolls() {
        let mut svg = Svg::default();
        svg.kind("only tested");
    }
}
"#;

/// The Mode A compound's writer and two of its marks, one tagging a kind of its own and one the kind its caller names; and the sheet.
#[expect(
    clippy::needless_raw_string_hashes,
    reason = "the text holds `\"##`, which two hashes would end on"
)]
const EMIT: &str = r###"//! the compound's marks
pub struct Svg {
    out: String,
}

impl Svg {
    pub fn new() -> Self {
        Self { out: String::new() }
    }

    pub fn rect(&mut self, attrs: &str) {
        self.out.push_str(attrs);
    }

    pub fn finish(self) -> String {
        self.out
    }
}

pub fn well(s: &mut Svg) {
    s.rect(r##"fill="#9C8C70" data-kind="well""##);
}

pub fn building(s: &mut Svg, k: &str) {
    s.rect(&format!(r#"fill="#E8D2A8" data-kind="{k}""#));
}

fn yard(s: &mut Svg) {
    well(s);
    s.rect(r##"fill="#B8B0A0" data-kind="gate""##);
}
"###;

const COMPOUND: &str = r"//! the compound engine
pub mod emit;

pub fn sheet(k: &str) -> String {
    let mut svg = emit::Svg::new();
    emit::well(&mut svg);
    emit::building(&mut svg, k);
    svg.finish()
}
";

const DRIVER: &str = "rust/phases/src/driver";

/// Two hamlets - the polder Kuwabata and the comb Inashiro - and a generated compound, the engines that draw them, all at the base.
fn world(name: &str) -> l7r_guard::shared::tempdir::Held<std::path::PathBuf> {
    let r = repo(name);
    hamlet(&r, "inashiro", &["paddy", "weir", "marsh"]);
    hamlet(
        &r,
        "kuwabata",
        &["paddy", "wet paddy", "sluice gate", "marsh", "-"],
    );
    compound(&r, "c", &["hall", "well", "-"]);
    put(&r, &format!("{DRIVER}/svg.rs"), SVG);
    put(&r, &format!("{DRIVER}/polder.rs"), POLDER);
    put(
        &r,
        &format!("{DRIVER}/tests.rs"),
        "fn t() { svg.kind(\"x\"); }\n",
    );
    put(&r, "rust/phases/src/driver.rs", "mod polder;\nmod svg;\n");
    put(&r, "rust/mode_a/src/compound.rs", COMPOUND);
    put(&r, "rust/mode_a/src/compound/emit.rs", EMIT);
    commit(&r, "the engines");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    r
}

/// `path`'s text with `from` replaced by `to` (present exactly once).
fn edit(root: &Path, path: &str, from: &str, to: &str) {
    let text = std::fs::read_to_string(root.join(path)).unwrap();
    assert_eq!(text.matches(from).count(), 1, "{from:?} in {path}");
    put(root, path, &text.replacen(from, to, 1));
}

fn polder(root: &Path, from: &str, to: &str) {
    edit(root, &format!("{DRIVER}/polder.rs"), from, to);
}

fn owed(root: &Path) -> Vec<String> {
    all_owed(root).1.iter().map(Unit::slug).collect()
}

/// The undo of every edit: the engines as at the base.
fn reset(root: &Path) {
    sh(root, "git checkout -q -- rust && git clean -qfd rust");
}

/// RED FIRST (449 T237): T234's change - the sluice's span, read only by the helper that frames it, which only the sluice's drawing
/// calls - owed no glyph-check until an Occasions line declared it; it owes the sluice gate's, on the map that draws one.
#[test]
fn a_change_to_the_sluices_drawing_owes_its_glyph_check_undeclared() {
    let r = world("sluice");
    assert!(owed(&r).is_empty());
    polder(
        &r,
        "SLUICE_SPAN_FT: f64 = 20.0",
        "SLUICE_SPAN_FT: f64 = 24.0",
    );
    let (_, units, problems) = all_owed(&r);
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        ["glyph-check--sluice-gate--kuwabata"]
    );
    assert_eq!(
        units[0].occasion,
        "'sluice gate' is redrawn: the hamlet driver's drawing code changed (rust/phases/src/driver/polder.rs SLUICE_SPAN_FT)"
    );
    assert!(problems.is_empty(), "{problems:?}");
    // nothing is refused for it: what it owes is read from the change, so no Occasions line is asked for
    assert!(check_declared(&r).is_none());
    reset(&r);
    polder(
        &r,
        "Frame { board: vec![",
        "Frame { board: vec![(at.0, at.1), ",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    reset(&r);
    polder(
        &r,
        "svg.kind(\"sluice gate\");\n    for &at",
        "svg.kind(\"sluice gate\");\n    svg.kind(\"sluice gate\");\n    for &at",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
}

/// T234 WHOLE: the old square deleted from the polder's drawing (its kind named in the lines deleted) with the constant only it read,
/// the frame drawn by a new function the roll calls: the sluice gate alone is owed, not the legend of every map the driver draws.
#[test]
fn t234s_whole_change_owes_the_sluice_gate_alone() {
    let r = world("t234");
    polder(&r, "const SLUICE_FT: f64 = 8.0;\n", "");
    polder(
        &r,
        "    svg.kind(\"sluice gate\");\n    let h = SLUICE_FT / 2.0;\n    for g in &s.sluices {\n        svg.polygon(&[(g.0 - h, g.1)], ink::DRAIN);\n    }\n",
        "",
    );
    polder(
        &r,
        "Frame { board: vec![",
        "Frame { board: vec![(at.0, at.1), ",
    );
    // and a type new beside it, which only the frame's drawing fills (T234's `SluiceFrame`): a redraw asks no declaration (449 T238,
    // red first: the type, redrawing nothing by itself, was read as placement and refused undeclared)
    polder(
        &r,
        "struct Frame {",
        "struct Posts {\n    n: usize,\n}\n\nstruct Frame {",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    assert!(check_declared(&r).is_none());
    // a line of a draw function above the first kind it names may feed any of its marks
    reset(&r);
    polder(
        &r,
        "for (i, x) in s.plots.iter().enumerate() {",
        "for (i, x) in s.plots.iter().enumerate().skip(1) {",
    );
    assert_eq!(owed(&r).len(), 5);
}

/// A stage's logic, a comment, a type's shape, a test, and a writer method nothing calls redraw no element: nothing owed.
#[test]
fn a_change_to_stage_logic_or_a_comment_owes_nothing() {
    let r = world("logic");
    polder(&r, "(i as f64, 0.0)", "(i as f64, 1.0)");
    assert!(owed(&r).is_empty());
    reset(&r);
    polder(
        &r,
        "// the frame across its channel",
        "// the frame across the channel it shuts",
    );
    edit(
        &r,
        &format!("{DRIVER}/svg.rs"),
        "/* the document */",
        "/* the document, written */",
    );
    assert!(owed(&r).is_empty());
    reset(&r);
    polder(
        &r,
        "board: Vec<(f64, f64)>,",
        "board: Vec<(f64, f64)>,\n    posts: usize,",
    );
    polder(
        &r,
        "svg.kind(\"only tested\");",
        "svg.kind(\"only tested again\");",
    );
    edit(
        &r,
        &format!("{DRIVER}/svg.rs"),
        "pub fn unused(&self) {}",
        "pub fn unused(&self) { let _ = 1; }",
    );
    edit(&r, &format!("{DRIVER}/tests.rs"), "\"x\"", "\"y\"");
    polder(
        &r,
        "use super::svg::{ink, Svg};",
        "use super::svg::{ink, Svg as Svg};",
    );
    polder(&r, "self.board.len()", "self.board.len() + 1");
    // a stage's helper named as a writer method is not that method
    polder(&r, "    n + 1\n", "    n + 2\n");
    assert!(owed(&r).is_empty());
}

/// Where the change's elements cannot be told - a kind chosen at run time, or the writer's document - the whole legend of each map the
/// engine draws is owed, each element once, on the first map that draws it; never `-`.
#[test]
fn where_the_elements_cannot_be_told_the_whole_legend_is_owed() {
    let r = world("whole");
    polder(
        &r,
        "svg.polygon(x, ink::LAND);",
        "svg.polygon(x, ink::DRAIN);",
    );
    let units = all_owed(&r).1;
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        [
            "glyph-check--marsh--inashiro",
            "glyph-check--paddy--inashiro",
            "glyph-check--sluice-gate--kuwabata",
            "glyph-check--weir--inashiro",
            "glyph-check--wet-paddy--kuwabata",
        ]
    );
    assert_eq!(
        units[0].occasion,
        "the hamlet driver's drawing code changed (rust/phases/src/driver/polder.rs draw_polder) and the elements it redraws cannot \
         be told (a kind chosen at run time, or the document every mark is written into), so the whole legend of inashiro is owed"
    );
    // the writer's document, through its tile: every mark is written into it
    reset(&r);
    edit(
        &r,
        &format!("{DRIVER}/svg.rs"),
        "<pattern id=\"p\">",
        "<pattern id=\"q\">",
    );
    assert_eq!(owed(&r).len(), 5);
    // a mark drawn under a kind chosen at run time in the roll
    reset(&r);
    polder(
        &r,
        "svg.line(&s.sluices, ink::DRAIN);\n    draw_sluices",
        "svg.line(&s.sluices, ink::LAND);\n    draw_sluices",
    );
    assert_eq!(owed(&r).len(), 5);
    // a mark after a draw function's call, whose kind the roll no longer knows
    reset(&r);
    polder(
        &r,
        "draw_sluices(&mut svg, &s);",
        "draw_sluices(&mut svg, &s);\n    svg.polygon(&[], ink::LAND);",
    );
    assert_eq!(owed(&r).len(), 5);
    // a mark before any kind is named
    reset(&r);
    edit(
        &r,
        &format!("{DRIVER}/polder.rs"),
        "svg.line(&[], ink::LAND);",
        "svg.line(&[], ink::DRAIN);",
    );
    assert_eq!(owed(&r).len(), 5);
    // a draw function naming no kind of its own draws its caller's: here `-`, so nothing
    reset(&r);
    polder(
        &r,
        "svg.line(&s.sluices, ink::DRAIN);\n}",
        "svg.line(&s.sluices, ink::LAND);\n}",
    );
    assert!(owed(&r).is_empty());
}

/// The roll's own lines: a mark drawn there owes the kind it is drawn under, a draw function's call that function's kinds, and a
/// line that does not touch the writer nothing.
#[test]
fn a_rolls_lines_owe_the_kind_they_are_drawn_under() {
    let r = world("roll");
    polder(
        &r,
        "svg.polygon(strip, ink::LAND);",
        "svg.polygon(strip, ink::DRAIN);",
    );
    assert_eq!(owed(&r), ["glyph-check--marsh--inashiro"]);
    reset(&r);
    polder(
        &r,
        "draw_sluices(&mut svg, &s);",
        "draw_sluices(&mut svg, &stage_polder(2));",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    reset(&r);
    polder(&r, "let doc = svg.finish();\n    doc", "svg.finish()");
    assert!(owed(&r).is_empty());
}

/// A drawing function deleted owes what it drew at the base, and one added what it draws; a file added draws too.
#[test]
fn a_drawing_deleted_or_added_owes_its_kinds() {
    let r = world("added");
    polder(&r, "    draw_sluices(&mut svg, &s);\n", "");
    let body = "fn draw_sluices(svg: &mut Svg, s: &PolderStage) {\n    svg.kind(\"sluice gate\");";
    let text = std::fs::read_to_string(r.join(DRIVER).join("polder.rs")).unwrap();
    let at = text.find(body).unwrap();
    let end = at + text[at..].find("\n}\n").unwrap() + 3;
    put(
        &r,
        &format!("{DRIVER}/polder.rs"),
        &format!("{}{}", &text[..at], &text[end..]),
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    reset(&r);
    put(
        &r,
        &format!("{DRIVER}/weir.rs"),
        "use super::svg::Svg;\n\npub fn draw_weir(svg: &mut Svg) {\n    svg.kind(\"weir\");\n    svg.kind(\"kiln\");\n}\n\n\
         fn roll_weir() -> String {\n    let mut svg = Svg::default();\n    svg.kind(\"weir\");\n    svg.finish()\n}\n",
    );
    // the kiln is drawn on no map: nothing to judge it on
    assert_eq!(owed(&r), ["glyph-check--weir--inashiro"]);
}

/// The Mode A compound engine: a mark tagging its own kind owes that kind's check on the compound, one tagging its caller's owes the
/// whole legend, and the sheet's call of a mark that mark's kinds.
#[test]
fn the_compound_engines_marks_owe_their_kinds_on_the_compound() {
    let r = world("compound");
    edit(&r, "rust/mode_a/src/compound/emit.rs", "#9C8C70", "#9C8C71");
    assert_eq!(owed(&r), ["glyph-check--well--c"]);
    reset(&r);
    edit(&r, "rust/mode_a/src/compound/emit.rs", "#E8D2A8", "#E8D2A9");
    let units = all_owed(&r).1;
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        ["glyph-check--hall--c", "glyph-check--well--c"]
    );
    assert!(units[0].occasion.starts_with("the Mode A compound engine's drawing code changed (rust/mode_a/src/compound/emit.rs building)"));
    reset(&r);
    edit(
        &r,
        "rust/mode_a/src/compound.rs",
        "emit::building(&mut svg, k);",
        "emit::building(&mut svg, \"hall\");",
    );
    assert_eq!(owed(&r), ["glyph-check--hall--c", "glyph-check--well--c"]);
    // a mark that calls another draws what that one draws too
    reset(&r);
    edit(&r, "rust/mode_a/src/compound/emit.rs", "#B8B0A0", "#B8B0A1");
    assert_eq!(owed(&r), ["glyph-check--well--c"]);
    // no size-audit: a redrawn glyph is judged, its size is not new
    reset(&r);
    edit(
        &r,
        "rust/mode_a/src/compound/emit.rs",
        "self.out.push_str(attrs);",
        "self.out.push_str(attrs.trim());",
    );
    assert_eq!(owed(&r), ["glyph-check--hall--c", "glyph-check--well--c"]);
}

/// The legend an element is judged on is the map's drawing now, else (not current: the change itself made it stale) its drawing at
/// the base - so the unit stands whether or not the hamlet was redrawn before the ask.
#[test]
fn a_hamlet_not_current_is_judged_on_its_base_legend() {
    let r = world("stale");
    put(
        &r,
        "pool/hamlets/kuwabata/kuwabata.spec.json",
        "{\"seed\": 2}",
    );
    polder(
        &r,
        "SLUICE_SPAN_FT: f64 = 20.0",
        "SLUICE_SPAN_FT: f64 = 24.0",
    );
    let (_, units, problems) = all_owed(&r);
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        ["glyph-check--sluice-gate--kuwabata"]
    );
    assert_eq!(problems.len(), 1, "{problems:?}");
    // redrawn without the sluice: no longer on the map, nothing to judge
    drawn(&r, "kuwabata", &["paddy"]);
    assert!(owed(&r).is_empty());
}

/// The declared route keeps working, and a declared line and the detection of the same change are one unit.
#[test]
fn a_declared_redraw_and_the_detected_one_are_one_unit() {
    let r = world("declared");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: sluice gate - the frame across its channel\n",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    polder(
        &r,
        "SLUICE_SPAN_FT: f64 = 20.0",
        "SLUICE_SPAN_FT: f64 = 24.0",
    );
    let units = all_owed(&r).1;
    assert_eq!(units.len(), 1);
    let said = &units[0].occasion;
    let want = "SLUICE_SPAN_FT): the frame across its channel";
    assert!(said.ends_with(want), "{said}");
}

/// The item reader: an item left open runs to the file's end, a raw string to its end, and a module's items are read inside it.
#[test]
fn the_item_reader_reads_to_the_end_of_what_is_left_open() {
    let mut out = Vec::new();
    items(
        "mod m {\n    const A: u8 = 1;\n}\nfn open() {\n    let s = r#\"never closed\n",
        "f.rs",
        None,
        &mut out,
    );
    let names: Vec<(&str, Role, usize)> = out
        .iter()
        .map(|i| (i.name.as_str(), i.role, i.lines.len()))
        .collect();
    assert_eq!(names, [("A", Role::Constant, 1), ("open", Role::Helper, 2)]);
}

/// With no commit there is no base to compare with: nothing is owed from the code.
#[test]
fn with_no_base_nothing_is_owed_from_the_code() {
    let empty = super::super::super::tests::dir("redrawn-unborn");
    sh(&empty, "git init -q");
    put(&empty, &format!("{DRIVER}/polder.rs"), POLDER);
    assert!(owed(&empty).is_empty());
}

/// RED FIRST (449 T238): a change to the driver's placement - a stage function, or a line of the roll that hands the stages their
/// ground and does not touch the writer - redraws nothing, so it owes no glyph-check; it was refused nothing either, where the deleted
/// Python's placement code was refused until the feature declared its occasions (T239's seat ring, in `roll_polder`). It is refused
/// undeclared, naming the file; a drawing change beside it still owes its glyph-check; a comment or a test is no change.
#[test]
fn a_change_to_the_drivers_placement_is_refused_until_an_occasion_is_declared() {
    let r = world("placed");
    polder(&r, "(i as f64, 0.0)", "(i as f64, 1.0)");
    assert!(owed(&r).is_empty());
    assert!(check_declared(&r).unwrap().starts_with(
        "drawing or placement code moved (rust/phases/src/driver/polder.rs) and no declaration answers"
    ));
    started(&r, "900-x", "T1");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- none: T1 - the stage's own roll\n",
    );
    assert!(check_declared(&r).is_none());
    sh(&r, "rm -rf specs .specify");
    reset(&r);
    polder(
        &r,
        "let s = stage_polder(n);",
        "let s = stage_polder(n + 1);",
    );
    assert!(owed(&r).is_empty());
    assert!(check_declared(&r).is_some());
    polder(
        &r,
        "SLUICE_SPAN_FT: f64 = 20.0",
        "SLUICE_SPAN_FT: f64 = 24.0",
    );
    assert_eq!(owed(&r), ["glyph-check--sluice-gate--kuwabata"]);
    assert!(check_declared(&r).is_some());
    reset(&r);
    polder(
        &r,
        "// the frame across its channel",
        "// the frame across the channel it shuts",
    );
    polder(
        &r,
        "svg.kind(\"only tested\");",
        "svg.kind(\"only tested again\");",
    );
    edit(&r, &format!("{DRIVER}/tests.rs"), "\"x\"", "\"y\"");
    assert!(check_declared(&r).is_none());
}
