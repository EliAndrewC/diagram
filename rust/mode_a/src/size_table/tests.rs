//! Its unit tests (feature 449 T174).
//!
//! Research:
//!     its tests - NONE: tests, deciding nothing about a building

use super::{gaps, render, table, to_json, Table};

/// A sheet with each form the table reads: definitions skipped, a stroke inherited, collinear walls on both axes and a shift that
/// rounds to the axis, a rotation flagged, a kind past 42 characters, a rect with no area, a negative zero stroke (`CPython` 3.14.4's
/// `size_table.table` and `render` gave every figure below).
const SHEET: &str = r##"<svg xmlns="http://www.w3.org/2000/svg"><defs><rect x="0" y="0" width="9" height="9"/></defs>
<g data-kind="hall" stroke="#2D2A24" stroke-width="6"><rect x="10" y="10" width="60" height="30"/><line x1="0" y1="0" x2="30" y2="0.5"/><line x1="40" y1="0.2" x2="90" y2="0"/></g>
<g transform="translate(5, 7) rotate(3)"><rect x="1" y="1" width="3" height="3" data-kind="a very long kind name that runs past forty-two characters"/></g>
<g transform="translate(100)"><line x1="0" y1="10" x2="0" y2="20" stroke="#000" stroke-width="3"/><line x1="0.4" y1="30" x2="0.4" y2="25" stroke="#000" stroke-width="3"/><line x1="0" y1="0" x2="5" y2="5" stroke="#000"/></g>
<rect x="1" y="1" width="0" height="3"/><rect x="-3.04" y="2" width="1" height="1" stroke-width="-0"/><path d="M 0 0" stroke-width="0"/>
<line x1="-0.3" y1="5" x2="-0.3" y2="9" stroke="#111" stroke-width="1"/><line x1="0.2" y1="12" x2="0.2" y2="20" stroke="#111" stroke-width="1"/>
</svg>"##;

const RENDERED: &str = "size-table: x.svg - 3 px = 1 ft; 3 rects, 3 wall gaps
   w ft   h ft   sq ft  at px         kind (data-kind)                            note
   20.0   10.0     200  10.0,10.0     hall                                        
    1.0    1.0       1  6.0,8.0       a very long kind name that runs past forty  transform not applied
    0.3    0.3       0  -3.0,2.0      (untagged)                                  
wall gaps (openings between collinear segments): 3.3 ft h@0 from 30 (wall 2.0 ft); 1.0 ft v@0 from 9 (wall 0.3 ft); 1.7 ft v@100 from 20 (wall 1.0 ft)
stroke widths in ft (count): -0.0 (2), 0.3 (2), 1.0 (2), 2.0 (3)";

const JSON: &str = r#"{
 "rects": [
  {
   "x_px": 10.0,
   "y_px": 10.0,
   "w_ft": 20.0,
   "h_ft": 10.0,
   "area_sqft": 200,
   "kind": "hall",
   "note": ""
  },
  {
   "x_px": 6.0,
   "y_px": 8.0,
   "w_ft": 1.0,
   "h_ft": 1.0,
   "area_sqft": 1,
   "kind": "a very long kind name that runs past forty-two characters",
   "note": "transform not applied"
  },
  {
   "x_px": -3.0,
   "y_px": 2.0,
   "w_ft": 0.3,
   "h_ft": 0.3,
   "area_sqft": 0,
   "kind": "",
   "note": ""
  }
 ],
 "strokes_ft": {
  "-0.0": 2,
  "0.3": 2,
  "1.0": 2,
  "2.0": 3
 },
 "gaps": [
  {
   "axis": "h",
   "at_px": 0.0,
   "from_px": 30.0,
   "gap_ft": 3.3,
   "wall_ft": 2.0
  },
  {
   "axis": "v",
   "at_px": 0.0,
   "from_px": 9.0,
   "gap_ft": 1.0,
   "wall_ft": 0.3
  },
  {
   "axis": "v",
   "at_px": 100.0,
   "from_px": 20.0,
   "gap_ft": 1.7,
   "wall_ft": 1.0
  }
 ]
}
"#;

#[test]
fn the_table_its_text_and_its_json_are_the_python_s() {
    let data = table(SHEET).unwrap();
    assert_eq!(render("x.svg", &data), RENDERED);
    assert_eq!(to_json(&data), JSON);
    let empty = Table {
        rects: Vec::new(),
        strokes_ft: Vec::new(),
        gaps: Vec::new(),
    };
    assert_eq!(
        render("e.svg", &empty),
        "size-table: e.svg - 3 px = 1 ft; 0 rects, 0 wall gaps\n   w ft   h ft   sq ft  at px         kind (data-kind)                            note\nwall gaps (openings between collinear segments): none found - check gates drawn another way\nstroke widths in ft (count): "
    );
    assert_eq!(
        to_json(&empty),
        "{\n \"rects\": [],\n \"strokes_ft\": {},\n \"gaps\": []\n}\n"
    );
}

#[test]
fn a_figure_past_a_float_is_written_as_json_writes_it() {
    let data = Table {
        rects: Vec::new(),
        strokes_ft: vec![(f64::INFINITY, 1)],
        gaps: gaps(&[
            (0.0, 0.0, 2.0, 0.0, String::new(), f64::INFINITY),
            (5.0, 0.0, 9.0, 0.0, String::new(), f64::INFINITY),
        ])
        .unwrap(),
    };
    let json = to_json(&data);
    assert!(json.contains("\"Infinity\": 1") && json.contains("\"wall_ft\": Infinity"));
    assert!(super::json_float(f64::NAN) == "NaN");
    let neg = Table {
        strokes_ft: vec![(f64::NEG_INFINITY, 1)],
        ..data
    };
    assert!(to_json(&neg).contains("\"-Infinity\": 1"));
}

#[test]
fn what_the_python_refused_is_refused_in_its_order() {
    let refusal = |svg: &str| {
        let e = table(svg).unwrap_err();
        (e.kind, e.message)
    };
    assert_eq!(refusal("<svg><rect").0, crate::etree::PARSE_ERROR);
    assert_eq!(
        refusal("<g/>"),
        ("ValueError", "no <svg> element in the sheet".to_owned())
    );
    // `<_r>` is an element to the XML reader and no start tag to the pattern: the rect's index runs past the start tags
    assert_eq!(
        refusal(r#"<svg><_r/><rect x="1" y="1" width="1" height="1"/></svg>"#),
        ("IndexError", "list index out of range".to_owned())
    );
    let nines = "9".repeat(400);
    assert_eq!(
        refusal(&format!(
            r#"<svg><rect x="1" y="1" width="{nines}" height="1"/></svg>"#
        ))
        .0,
        "OverflowError"
    );
    let far = "9".repeat(308);
    assert_eq!(
        refusal(&format!(
            r#"<svg><line x1="{far}" y1="0" x2="{far}" y2="9"/></svg>"#
        ))
        .0,
        "OverflowError"
    );
}
